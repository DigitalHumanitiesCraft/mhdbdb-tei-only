#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#255: Wie stark verzerrt die Parallelueberlieferung die Zahlen der Werkzeuge?

KZW hat am 2026-07-30 im Ticket keine Umsetzung bestellt, sondern eine Messung:
"Erstelle mir eine Liste von Tools, wo es wirklich anders behandelt werden
sollte." Dieses Skript ist die Grundlage dieser Liste. Es aendert nichts, es
rechnet jede Kennzahl aus CONTRACTS §H zweimal: einmal wie heute, einmal ohne
die Tokens, die in einem <div type="parallel"> liegen. Die Differenz ist die
Verzerrung.

WARUM DAS NICHT EINE ZAHL IST
-----------------------------
`<div type="parallel">` traegt im Korpus zwei unvereinbare Bedeutungen, und
welche gemeint ist, steht nur im @n:

  Klasse HANDSCHRIFT  @n ist ein Handschriften- oder Werkname
                      ("Jenaer Liederhandschrift", "Codex Manesse").
                      Der Text BESTEHT aus diesen Zeugen, es gibt keinen
                      Basiszeugen daneben. In BRW und DL1 liegen 100 % der
                      indexierten Tokens in solchen divs.

  Klasse ZAEHLER      @n ist eine laufende Nummer (1, 2, 3).
                      Der div haengt neben einem Basistext, meist als
                      Geschwister eines <p>. Das ist der Fall, den #255
                      beschreibt.

Ein Filter "Tokens in parallel-divs nicht mitzaehlen" wuerde BRW und DL1
vollstaendig aus dem Korpus loeschen. Die Unterscheidung ist deshalb keine
Feinheit des Berichts, sondern die Vorbedingung jeder Umsetzung, und sie
gehoert vor jede Werkzeugentscheidung.

Deshalb rechnet das Skript beide Szenarien, und der Unterschied zwischen ihnen
ist der eigentliche Befund:

  all       jeder parallel-div faellt heraus. Das ist die naive Umsetzung von
            "Zeugenvarianten nicht mitzaehlen".
  zaehler   nur die Klasse ZAEHLER faellt heraus, also der Fall, den #255
            beschreibt. HANDSCHRIFT-Bloecke bleiben Text.

MESSVORSCHRIFT
--------------
Ohne sie sind die Zahlen unten nicht reproduzierbar (Regel 11 des
Issue-Playbooks: Zahlen in Doku und Kommentaren altern mit den Daten).

  Position        §B-Position: laufende Nummer des <w> mit nicht-leerem
                  @lemmaRef und nicht-leerem Textinhalt, in Dokumentordnung
                  ueber <body>, ab 0. Identisch zu build-corpus-index.py.
  parallel-Token  eine Position, deren <w> einen Vorfahren
                  div[@type="parallel"] hat, der zum Szenario gehoert.
  Basis-Token     jede andere Position desselben Textes.
  Block           der parallel-div, in dem die Position liegt, sonst der
                  Basistext. Bloecke sind die Einheiten, zwischen denen eine
                  Naht liegt; im Szenario "zaehler" bilden HANDSCHRIFT-divs
                  weiterhin eigene Bloecke, weil auch sie verschiedene Zeugen
                  sind, nur eben keine, die herausgerechnet werden sollen.
  Naht            zwei im Index benachbarte Verse (lineEnds[k], lineEnds[k+1])
                  bzw. zwei Positionen im Abstand <= 10, deren Bloecke
                  verschieden sind.
  "ohne"          dieselbe Kennzahl, gerechnet ueber die Basis-Tokens allein.

Der Positionslauf wird gegen text.wordCount und len(text.lineEnds) aus dem
gebauten Index geprueft und bricht bei Abweichung ab: eine Messung auf einer
anderen Zaehlung als der des Index waere lautlos falsch.

Usage:
    python scripts/audit/parallel-witness-bias.py
    python scripts/audit/parallel-witness-bias.py --csv out.csv
    python scripts/audit/parallel-witness-bias.py --proximity 10

Read-only. Kein schreibender Korpus-, Index- oder Schema-Zugriff.
"""
import argparse
import csv
import gzip
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from corpus_files import corpus_files  # noqa: E402

TEI_NS = 'http://www.tei-c.org/ns/1.0'
W = f'{{{TEI_NS}}}w'
L = f'{{{TEI_NS}}}l'
BODY = f'{{{TEI_NS}}}body'
DIV = f'{{{TEI_NS}}}div'

CORPUS_INDEX = PROJECT_ROOT / 'data' / 'corpus-index.json.gz'
AUTHORITY_INDEX = PROJECT_ROOT / 'data' / 'authority-index.json.gz'

# Signifikanzschwellen der Keyness-Spalte, df = 1 (CONTRACTS §H.1). Nur 10.83
# wird in der UI hervorgehoben, 3.84 steht der Vollstaendigkeit halber dabei.
LL_STRONG = 10.83
LL_WEAK = 3.84


def classify_n(value):
    """HANDSCHRIFT oder ZAEHLER, entschieden am @n des parallel-div.

    Eine reine Zahl ist eine laufende Nummer innerhalb eines Abschnitts, alles
    andere ein Zeugenname. Das ist eine Heuristik am Datenbestand, keine
    Zusicherung des Schemas: mhdbdb.rnc schreibt fuer @n nichts vor. Sie wird
    im Bericht je Text mit den tatsaechlichen @n-Werten ausgewiesen, damit sie
    nachpruefbar bleibt, statt unbesehen zu wirken.
    """
    if value is None:
        return 'OHNE-N'
    return 'ZAEHLER' if value.strip().isdigit() else 'HANDSCHRIFT'


def scan_text(path):
    """Positionen, Verse und Ueberlieferungsbloecke eines Korpustextes.

    Ein einziger Durchlauf mit iterwalk, wie build-corpus-index.py, damit
    Positionszaehlung und <l>-Grenzen aus derselben Traversierung stammen.
    """
    tree = etree.parse(str(path))
    body = tree.find(f'.//{BODY}')
    if body is None:
        return None

    # Der Stack traegt die gerade offenen parallel-divs. Im Korpus sind sie
    # nicht geschachtelt (gemessen: 0 Faelle), der Stack setzt das aber nicht
    # voraus, sondern haelt es aus.
    #
    # Der Blockschluessel ist ein eigener Zaehler, NICHT id(el): lxml gibt
    # Proxy-Objekte pro Zugriff neu aus, und sobald der Proxy eingesammelt
    # wird, vergibt CPython dieselbe id() erneut. Eine Fassung dieses Skripts,
    # die id(el) nahm, zaehlte fuer FR3 16 statt 36 divs, und zwar erst,
    # nachdem eine unbeteiligte Aufraeumung die letzte Referenz auf das
    # Element entfernt hatte. Playbook §2.1 Regel 10, docs/DECISIONS.md:858.
    par_stack = []
    next_key = 0
    blocks = {}          # block-key -> {'n', 'klasse', 'tokens'}
    block_of = []        # je Position der block-key (None = Basistext)
    line_ends = []
    line_block = []      # Block des Verses, gemessen am letzten indexierten Wort
    lines_par = 0
    lines_total = 0

    pos = 0
    cur_line_last = None
    in_line = False

    for event, el in etree.iterwalk(body, events=('start', 'end'),
                                    tag=(W, L, DIV)):
        tag = el.tag
        if tag == DIV:
            if el.get('type') != 'parallel':
                continue
            if event == 'start':
                key = next_key
                next_key += 1
                n = el.get('n')
                blocks[key] = {'n': n, 'klasse': classify_n(n), 'tokens': 0}
                par_stack.append(key)
            else:
                par_stack.pop()
            continue

        if tag == L:
            if event == 'start':
                in_line = True
                cur_line_last = None
                lines_total += 1
                if par_stack:
                    lines_par += 1
            else:
                in_line = False
                # CONTRACTS §H.2a: ein lineEnds-Eintrag entsteht nur fuer <l>
                # mit mindestens einem indexierten Wort.
                if cur_line_last is not None:
                    line_ends.append(cur_line_last)
                    line_block.append(block_of[cur_line_last])
            continue

        # tag == W
        if event != 'start':
            continue
        if not el.get('lemmaRef'):
            continue
        if not ''.join(el.itertext()).strip():
            continue
        key = par_stack[-1] if par_stack else None
        block_of.append(key)
        if key is not None:
            blocks[key]['tokens'] += 1
        if in_line:
            cur_line_last = pos
        pos += 1

    return {
        'word_count': pos,
        'block_of': block_of,
        'blocks': blocks,
        'line_ends': line_ends,
        'line_block': line_block,
        'lines_total': lines_total,
        'lines_par': lines_par,
    }


def log_likelihood(a, b, c, d):
    """Signierte Log-Likelihood, Zeile fuer Zeile wie CONTRACTS §H.1."""
    if c <= 0 or d <= 0 or (a + b) <= 0:
        return 0.0
    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    ll = 0.0
    if a > 0 and e1 > 0:
        ll += a * math.log(a / e1)
    if b > 0 and e2 > 0:
        ll += b * math.log(b / e2)
    ll *= 2
    return ll if (a / c) >= ((a + b) / (c + d)) else -ll


def band(ll):
    """Das Signifikanzband, in dem die UI einen Keyness-Wert liest."""
    m = abs(ll)
    if m >= LL_STRONG:
        return 'stark'
    if m >= LL_WEAK:
        return 'schwach'
    return 'keine'


def rhymes_with(a, b):
    """CONTRACTS §H.3, graphemisches Reimkriterium auf normalisierten Formen."""
    if not a or not b:
        return False
    if a[-3:] == b[-3:]:
        return True
    return len(a) <= 4 and len(b) <= 4 and a[-2:] == b[-2:]


def length_matched_ttr(text, target_len, seeds=(255, 1, 2, 3, 4)):
    """TTR eines gleich langen Zufallsausschnitts aus dem VOLLEN Text.

    Die Vergleichsgroesse zur Spalte "TTR ohne". Gezogen werden target_len
    Positionen ohne Zuruecklegen, die Typenzahl darueber ist die Zahl der
    Lemmata mit mindestens einer gezogenen Position. Gemittelt ueber mehrere
    Seeds, weil eine Einzelziehung um mehrere Prozent streut. Die Seeds stehen
    fest, damit der Lauf reproduzierbar bleibt.
    """
    wc = text['wordCount']
    if not wc or target_len <= 0 or target_len >= wc:
        return None
    lemma_of = {}
    for lemma_id, positions in text['lemmata'].items():
        for p in positions:
            lemma_of.setdefault(p, set()).add(lemma_id)
    werte = []
    for seed in seeds:
        rng = random.Random(seed)
        gezogen = rng.sample(range(wc), target_len)
        typen = set()
        for p in gezogen:
            typen.update(lemma_of.get(p, ()))
        werte.append(len(typen) / target_len)
    return sum(werte) / len(werte)


def excluded_positions(scan, scope):
    """Die Positionen, die das Szenario herausrechnet."""
    if scope == 'all':
        return {i for i, b in enumerate(scan['block_of']) if b is not None}
    return {i for i, b in enumerate(scan['block_of'])
            if b is not None and scan['blocks'][b]['klasse'] == 'ZAEHLER'}


def report_scope(scope, scans, index, texts_by_id, normalized, args):
    """Abschnitte 2 bis 6 fuer ein Szenario."""
    par_positions = {s: excluded_positions(sc, scope) for s, sc in scans.items()}
    betroffen = {s for s, p in par_positions.items() if p}

    print()
    print('=' * 78)
    print(f'SZENARIO "{scope}": '
          + ('jeder parallel-div faellt heraus'
             if scope == 'all'
             else 'nur die Klasse ZAEHLER faellt heraus'))
    print(f'betroffene Texte: {", ".join(sorted(betroffen)) or "(keine)"}')
    print('=' * 78)

    if not betroffen:
        print('Nichts herauszurechnen, das Szenario ist gegenstandslos.')
        return {}

    # ------------------------------------------------------- H.1 Keyness
    print()
    print('-' * 78)
    print('H.1 KEYNESS (Hauptseite, sortierbare Spalte)')
    print('-' * 78)
    corpus_word_total = sum(t['wordCount'] for t in index['texts'])
    entfernt = sum(len(p) for p in par_positions.values())
    corpus_word_total_ohne = corpus_word_total - entfernt
    print(f'  corpusWordTotal  mit  {corpus_word_total:>12,}')
    print(f'  corpusWordTotal  ohne {corpus_word_total_ohne:>12,}'
          f'   ({entfernt / corpus_word_total * 100:.3f} % weniger)')

    lemma_total = Counter()
    lemma_par = Counter()
    for t in index['texts']:
        parset = par_positions.get(t['id'])
        for lemma_id, positions in t['lemmata'].items():
            lemma_total[lemma_id] += len(positions)
            if parset:
                n_par = sum(1 for p in positions if p in parset)
                if n_par:
                    lemma_par[lemma_id] += n_par

    probe = set()
    for sigle in betroffen:
        t = texts_by_id[sigle]
        top = sorted(t['lemmata'].items(), key=lambda kv: -len(kv[1]))[:args.keyness_top]
        probe.update(k for k, _ in top)
    print(f'  Probe: {len(probe)} Lemmata (je betroffenem Text die '
          f'{args.keyness_top} haeufigsten), gerechnet ueber alle '
          f'{len(index["texts"])} Zeilen.')

    band_wechsel = []
    entfallene_zeilen = 0
    verschiebungen = []
    vorzeichen = 0
    for lemma_id in probe:
        cm = lemma_total[lemma_id]
        cm_ohne = cm - lemma_par.get(lemma_id, 0)
        for t in index['texts']:
            sigle = t['id']
            positions = t['lemmata'].get(lemma_id)
            if not positions:
                continue
            a = len(positions)
            c = t['wordCount']
            ll_mit = log_likelihood(a, cm - a, c, corpus_word_total - c)
            parset = par_positions.get(sigle)
            if parset:
                a_o = sum(1 for p in positions if p not in parset)
                c_o = c - len(parset)
            else:
                a_o, c_o = a, c
            if c_o <= 0:
                entfallene_zeilen += 1
                continue
            ll_ohne = log_likelihood(a_o, cm_ohne - a_o, c_o,
                                     corpus_word_total_ohne - c_o)
            shift = abs(ll_ohne - ll_mit)
            verschiebungen.append((shift, sigle, lemma_id, ll_mit, ll_ohne))
            if band(ll_mit) != band(ll_ohne):
                band_wechsel.append((shift, sigle, lemma_id, ll_mit, ll_ohne))
            if (ll_mit >= 0) != (ll_ohne >= 0):
                vorzeichen += 1

    in_betroffen = sum(1 for r in band_wechsel if r[1] in betroffen)
    print()
    print(f'  Werte, deren Zeile ganz entfaellt (Text wird leer): '
          f'{entfallene_zeilen:,}')
    print(f'  Werte, die das Signifikanzband wechseln: {len(band_wechsel):,}')
    print(f'    in den betroffenen Texten selbst: {in_betroffen:,}')
    print(f'    in allen uebrigen Texten:         {len(band_wechsel) - in_betroffen:,}')
    print(f'  Werte, die das Vorzeichen wechseln:      {vorzeichen:,}')
    if verschiebungen:
        verschiebungen.sort(reverse=True)
        s, sg, lm, x, y = verschiebungen[0]
        print(f'  Groesste Verschiebung insgesamt: {s:.1f} '
              f'({sg}, {lm}: {x:.1f} -> {y:.1f})')
        aussen = [v for v in verschiebungen if v[1] not in betroffen]
        if aussen:
            s, sg, lm, x, y = aussen[0]
            print(f'  Groesste Verschiebung ausserhalb: {s:.3f} '
                  f'({sg}, {lm}: {x:.3f} -> {y:.3f})')

    # ------------------------------------------------------- H.2 Hapax
    print()
    print('-' * 78)
    print('H.2 HAPAXLEGOMENA (korpusweit)')
    print('-' * 78)
    counts_ohne = {k: v - lemma_par.get(k, 0) for k, v in lemma_total.items()}
    print(f'{"Schwelle":<12}{"mit":>10}{"ohne":>10}{"Differenz":>12}')
    for lvl in (1, 2, 3):
        mit = sum(1 for c in lemma_total.values() if 0 < c <= lvl)
        ohne = sum(1 for c in counts_ohne.values() if 0 < c <= lvl)
        print(f'  <= {lvl:<8}{mit:>10,}{ohne:>10,}{ohne - mit:>+12,}')
    weg = sum(1 for c in counts_ohne.values() if c == 0)
    neu = sum(1 for k, v in counts_ohne.items() if 0 < v <= 1 < lemma_total[k])
    print()
    print(f'  Lemmata nur in Parallelueberlieferung belegt (fallen ganz weg): {weg:,}')
    print(f'  Lemmata, die erst ohne die Zeugen zum Hapax werden:            {neu:,}')

    # ------------------------------------------------------- H.4 Verse
    print()
    print('-' * 78)
    print('H.4 VERSENDEN-PROFIL und REIM-DRUCK')
    print('-' * 78)
    verse_mit = sum(len(t['lineEnds']) for t in index['texts'] if t['lineEnds'])
    verse_par = 0
    for sigle, scan in scans.items():
        parset = par_positions[sigle]
        verse_par += sum(1 for p in scan['line_ends'] if p in parset)
    print(f'  verseCount (Bereich Korpus)  mit  {verse_mit:>10,}')
    print(f'  verseCount (Bereich Korpus)  ohne {verse_mit - verse_par:>10,}'
          f'   ({verse_par / verse_mit * 100:.3f} % weniger)')

    # ------------------------------------------------------- Die Naht
    print()
    print('-' * 78)
    print(f'DIE NAHT: Reim-Woerterbuch (H.3) und Naehesuche (§C.2.2)')
    print('-' * 78)
    print('  Fehlerklasse: nicht Doppelzaehlung, sondern eine Verbindung ueber')
    print('  die Grenze zweier Fassungen desselben Verses hinweg.')
    print()
    print(f'{"Sigle":<7}{"Verspaare":>11}{"ueber Naht":>12}{"davon reimen":>14}'
          f'{"Reimquote sonst":>17}{"Tokenpaare <= " + str(args.proximity):>19}')
    summe = {'paare': 0, 'naht': 0, 'reim': 0, 'prox': 0,
             'innen': 0, 'innen_reim': 0}
    per_text = {}
    for sigle, scan in sorted(scans.items()):
        lb = scan['line_block']
        le = scan['line_ends']
        paare = max(0, len(le) - 1)
        naht = sum(1 for k in range(paare) if lb[k] != lb[k + 1])
        # Wie viele der Nahtpaare meldet das Reim-Woerterbuch tatsaechlich als
        # Reim? Nur die zaehlen als falsche Ausgabe. Partnerseite ueber
        # words[pos] wie in H.3.
        #
        # Die Kontrollzahl daneben ist Pflicht, nicht Zierde: eine 0 bei
        # "davon reimen" ist ohne sie nicht von einem kaputten
        # Normalisierungs-Lookup zu unterscheiden. Sie misst dieselbe Groesse
        # auf den Verspaaren INNERHALB eines Blocks, wo Reime vorkommen
        # muessen.
        t = texts_by_id[sigle]
        words = t['words']
        reim = 0
        innen = 0
        innen_reim = 0
        for k in range(paare):
            a = normalized.get(words[le[k]], '')
            b = normalized.get(words[le[k + 1]], '')
            if lb[k] != lb[k + 1]:
                if rhymes_with(a, b):
                    reim += 1
            else:
                innen += 1
                if rhymes_with(a, b):
                    innen_reim += 1
        bo = scan['block_of']
        n = len(bo)
        prox = 0
        for i in range(n):
            bi = bo[i]
            for j in range(i + 1, min(n, i + args.proximity + 1)):
                if bo[j] != bi:
                    prox += 1
        quote = f'{innen_reim / innen * 100:.1f}%' if innen else 'n/a'
        print(f'{sigle:<7}{paare:>11,}{naht:>12,}{reim:>14,}{quote:>17}'
              f'{prox:>19,}')
        per_text[sigle] = {'verspaare': paare, 'naht': naht, 'reim': reim,
                           'prox': prox}
        summe['paare'] += paare
        summe['naht'] += naht
        summe['reim'] += reim
        summe['prox'] += prox
        summe['innen'] += innen
        summe['innen_reim'] += innen_reim
    quote = (f'{summe["innen_reim"] / summe["innen"] * 100:.1f}%'
             if summe['innen'] else 'n/a')
    print(f'{"Summe":<7}{summe["paare"]:>11,}{summe["naht"]:>12,}'
          f'{summe["reim"]:>14,}{quote:>17}{summe["prox"]:>19,}')
    print()
    print('  "ueber Naht" sind benachbarte lineEnds-Eintraege aus verschiedenen')
    print('  Bloecken, "davon reimen" die Teilmenge, die H.3 auch wirklich als')
    print('  Reimpaar ausgibt. Nur diese Zahl ist eine falsche Ausgabe, die')
    print('  erste ist ihre Obergrenze.')
    print('  "Reimquote sonst" ist dieselbe Rechnung auf den Verspaaren')
    print('  INNERHALB eines Blocks. Sie ist die Kontrollzahl: liegt sie bei')
    print('  0, misst nicht die Naht nichts, sondern das Skript.')

    # ------------------------------------------------------- H.5
    print()
    print('-' * 78)
    print('H.5 NORMIERTE GROESSEN je betroffenem Text')
    print('-' * 78)
    print(f'{"Sigle":<7}{"wordCount mit":>15}{"ohne":>11}{"Typen mit":>11}'
          f'{"ohne":>8}{"TTR mit":>10}{"TTR ohne":>10}{"Aenderung":>11}'
          f'{"laengengleich":>15}')
    ergebnis = {}
    for sigle in sorted(betroffen):
        t = texts_by_id[sigle]
        parset = par_positions[sigle]
        wc = t['wordCount']
        wc_o = wc - len(parset)
        typen = len(t['lemmata'])
        typen_o = sum(1 for positions in t['lemmata'].values()
                      if any(p not in parset for p in positions))
        ttr = typen / wc if wc else 0.0
        if wc_o:
            ttr_o = typen_o / wc_o
            aend = f'{(ttr_o - ttr) / ttr * 100:+.1f}%'
            ttr_o_txt = f'{ttr_o:.4f}'
            # Kontrolle gegen das Laengenartefakt: TTR faellt mit der Textlaenge,
            # aus rechnerischen und nicht aus stilistischen Gruenden (§H.5
            # Punkt 1). Ein Ausschnitt derselben Laenge aus dem VOLLEN Text
            # sagt, wie viel der Aenderung allein daher kommt, dass der Text
            # kuerzer geworden ist. Ohne diese Spalte laese sich ein Artefakt
            # als Entzerrung.
            ttr_len = length_matched_ttr(t, wc_o)
            len_txt = f'{ttr_len:.4f}' if ttr_len is not None else 'n/a'
        else:
            ttr_o = None
            aend = 'Text leer'
            ttr_o_txt = 'n/a'
            len_txt = 'n/a'
        print(f'{sigle:<7}{wc:>15,}{wc_o:>11,}{typen:>11,}{typen_o:>8,}'
              f'{ttr:>10.4f}{ttr_o_txt:>10}{aend:>11}{len_txt:>15}')
        ergebnis[sigle] = {
            'wordcount_ohne': wc_o, 'typen_mit': typen, 'typen_ohne': typen_o,
            'ttr_mit': round(ttr, 5),
            'ttr_ohne': round(ttr_o, 5) if ttr_o is not None else '',
            'ttr_laengengleich': len_txt,
            **{f'{k}_{scope}': v for k, v in per_text.get(sigle, {}).items()},
        }
    print()
    print('  "laengengleich" ist die TTR eines gleich langen Zufallsausschnitts')
    print('  aus dem vollen Text (Mittel ueber 5 feste Seeds). Liegt "TTR ohne"')
    print('  auf diesem Wert, ist die Aenderung ein Laengenartefakt und keine')
    print('  Entzerrung: die TTR steigt, wenn ein Text kuerzer wird, aus')
    print('  rechnerischen und nicht aus stilistischen Gruenden (§H.5 Punkt 1).')
    print('  wordCount ohne = 0 heisst, der Text besteht vollstaendig aus')
    print('  Parallelueberlieferung und faellt aus jeder Auswertung heraus.')
    return ergebnis


def main():
    ap = argparse.ArgumentParser(
        description='#255: Verzerrung durch Parallelueberlieferung, je Werkzeug',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', help='Ergebnistabelle je Text zusaetzlich als CSV')
    ap.add_argument('--proximity', type=int, default=10,
                    help='Fensterbreite der Naehesuche in annotierten Tokens '
                         '(Vorgabe der UI: 10)')
    ap.add_argument('--keyness-top', type=int, default=50,
                    help='Wie viele Lemmata je betroffenem Text die '
                         'Keyness-Probe durchrechnet (Vorgabe 50)')
    args = ap.parse_args()

    for path in (CORPUS_INDEX, AUTHORITY_INDEX):
        if not path.exists():
            sys.exit(f'FEHLER: {path} fehlt. Erst die Indexe bauen.')

    with gzip.open(CORPUS_INDEX, 'rt', encoding='utf-8') as fh:
        index = json.load(fh)
    with gzip.open(AUTHORITY_INDEX, 'rt', encoding='utf-8') as fh:
        authority = json.load(fh)
    texts_by_id = {t['id']: t for t in index['texts']}
    normalized = {e['id']: (e.get('normalized') or '') for e in authority['lemmata']}

    print('=' * 78)
    print('#255  Verzerrung durch Parallelueberlieferung, je Werkzeug gemessen')
    print('=' * 78)
    print(f'Korpus-Index {index.get("version")}, Authority-Index '
          f'{authority.get("version")}, {len(index["texts"])} Texte')
    print(f'Naehe-Fenster: {args.proximity} annotierte Tokens')

    scans = {}
    for path in corpus_files():
        if b'type="parallel"' not in path.read_bytes():
            continue
        scan = scan_text(path)
        if scan is not None:
            scans[path.name.replace('.tei.xml', '')] = scan

    if not scans:
        print('Kein Text mit <div type="parallel"> gefunden. Nichts zu messen.')
        return 0

    # Paritaetspruefung gegen den gebauten Index. Ohne sie misst das Skript
    # womoeglich eine andere Grundgesamtheit, als die Werkzeuge lesen.
    for sigle, scan in sorted(scans.items()):
        t = texts_by_id.get(sigle)
        if t is None:
            sys.exit(f'FEHLER: Text {sigle} steht nicht im Korpus-Index.')
        if t['wordCount'] != scan['word_count']:
            sys.exit(f'FEHLER: Positionszaehlung weicht ab fuer {sigle}: '
                     f'Index {t["wordCount"]}, hier {scan["word_count"]}.')
        if len(t['lineEnds']) != len(scan['line_ends']):
            sys.exit(f'FEHLER: lineEnds weichen ab fuer {sigle}: '
                     f'Index {len(t["lineEnds"])}, hier {len(scan["line_ends"])}.')
    print(f'Paritaet gegen den Index geprueft: {len(scans)} Texte, wordCount '
          'und lineEnds stimmen ueberein.')

    # ------------------------------------------------------- 1. Struktur
    print()
    print('-' * 78)
    print('1. STRUKTUR: wo die Parallelueberlieferung liegt und was sie bedeutet')
    print('-' * 78)
    print()
    print(f'{"Sigle":<7}{"divs":>5}{"Klasse":>26}{"Tokens":>9}{"davon par.":>11}'
          f'{"Anteil":>9}{"Verse":>8}{"par.":>7}')
    rows = {}
    for sigle, scan in sorted(scans.items()):
        par_tokens = sum(1 for b in scan['block_of'] if b is not None)
        total = scan['word_count']
        klassen = sorted({b['klasse'] for b in scan['blocks'].values()})
        klasse = '+'.join(klassen) if klassen else '-'
        share = par_tokens / total * 100 if total else 0.0
        print(f'{sigle:<7}{len(scan["blocks"]):>5}{klasse:>26}{total:>9,}'
              f'{par_tokens:>11,}{share:>8.1f}%{scan["lines_total"]:>8,}'
              f'{scan["lines_par"]:>7,}')
        rows[sigle] = {
            'sigle': sigle, 'divs': len(scan['blocks']), 'klasse': klasse,
            'tokens': total, 'tokens_parallel': par_tokens,
            'anteil_prozent': round(share, 2), 'verse': scan['lines_total'],
            'verse_parallel': scan['lines_par'],
        }

    print()
    print('Die @n-Werte je Text, damit die Klassifikation nachpruefbar ist:')
    for sigle, scan in sorted(scans.items()):
        counted = Counter((b['n'], b['klasse']) for b in scan['blocks'].values())
        parts = [f'{n!r} [{k}]' + (f' x{c}' if c > 1 else '')
                 for (n, k), c in counted.most_common()]
        print(f'  {sigle:<6} {", ".join(parts)}')

    print()
    print('LESART: Klasse HANDSCHRIFT heisst, der div traegt einen Zeugennamen')
    print('und der Text besteht aus solchen Bloecken. Ein Filter, der sie')
    print('herausrechnet, loescht diese Texte, statt sie zu entzerren.')

    ergebnisse = {}
    for scope in ('all', 'zaehler'):
        ergebnisse[scope] = report_scope(scope, scans, index, texts_by_id,
                                         normalized, args)

    if args.csv:
        out = Path(args.csv)
        for scope, erg in ergebnisse.items():
            for sigle, values in erg.items():
                for k, v in values.items():
                    rows[sigle][f'{k}__{scope}' if not k.endswith(scope) else k] = v
        fields = ['sigle', 'divs', 'klasse', 'tokens', 'tokens_parallel',
                  'anteil_prozent', 'verse', 'verse_parallel']
        extra = sorted({k for r in rows.values() for k in r} - set(fields))
        fields += extra
        with out.open('w', encoding='utf-8-sig', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter=';')
            writer.writeheader()
            for sigle in sorted(rows):
                writer.writerow({k: rows[sigle].get(k, '') for k in fields})
        print()
        print(f'CSV geschrieben: {out}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
