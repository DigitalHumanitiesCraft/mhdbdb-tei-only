#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216 Punkt 3: wie gross ist die vrouwe-Disambiguierung (Messung, read-only).

Kontext: In #216 haengen die Punkte 2, 4, 5, 6 und 8 an Punkt 3. Die Regel fuer
die Personifikation "Frau Minne" ist als Lemma-Regel formuliert (unmittelbar
vorangehendes Token mit lemmaRef=lemma_7260, Wortform ohne -n), und sie greift
dort nicht, wo das vorangehende vrouwe-Token selbst noch kein Lemma traegt.
Dieses Skript misst, wie gross diese Luecke ist. Es aendert nichts.

Drei Fragen, in dieser Reihenfolge beantwortet:
  1. Wie viele <w> im Korpus sind formal vrouwe und tragen kein @lemmaRef?
  2. Wie viele davon stehen unmittelbar vor einer minne-Form?
  3. Wie viele distinkte Ziel-Lemmata kaemen in Frage, wie viele existieren schon?

## Messvorschrift

**Das Formeninventar wird erhoben, nicht geraten.** "Formal vrouwe" ist die
Menge der MHG-normalisierten Oberflaechenformen aller <w>, die lemma_7260
tragen; Lemma-Ids werden token-genau verglichen (CONTRACTS B.1), nie als
Teilzeichenkette. Eine handgeschriebene Schreibungsliste waere hier der falsche
Weg: #216 (Kommentar vom 31.08.) hat gemessen, dass eine Sechserliste aus HUGO
nur 214 von 633 Stellen deckt und die haeufigste Schreibung ueberhaupt nicht
enthaelt. Dasselbe Inventar wird fuer lemma_7250 (vro "froh") erhoben, weil
sich die beiden ueberschneiden und eine reine Formenregel dort falsche Treffer
erzeugt.

**minne-Formen** nach der Vorschrift aus #216 (Kommentar vom 31.08., 15:38):
^m[iíîy]nn[eè]?$ ueber die Rohform. Das Doppel-n haelt die Possessivformen
min/mine draussen.

**"Unmittelbar" heisst: in der <w>-Folge des <body>, nicht unter den direkten
Kindern der Verszeile.** Das ist der Punkt, an dem sich diese Messung von der
in #216 protokollierten unterscheidet, und der Unterschied ist gross: **am
01.09.2026 gemessen** enthielten 115 der damals 155 gefundenen Paare
mindestens ein <w>, das in einem <hi> steht statt direkt in seinem <l>. Ein
Durchlauf ueber die direkten Kinder fand nur 40 davon. Das Skript weist beide
Zaehlweisen aus, damit die Differenz sichtbar bleibt statt erklaert werden zu
muessen.

**Die Zahl 155 ist ein historischer Stand und nicht mehr das, was ein Lauf
heute ausgibt.** Der Batch ingest/pos-disambig/216-vrouwe155/ hat am
06.09.2026 152 dieser Tokens annotiert; sie tragen jetzt lemma_7260 und fallen
damit aus Frage 1 und Frage 2 heraus, die beide auf "ohne @lemmaRef" prueft.
Ein Lauf gegen den heutigen Korpus findet noch 3 Paare, naemlich die drei
RVBR-Tokens der Schreibung frô, fuer die es unter lemma_7260 keinen
Variantentyp gibt. Das ist kein Defekt der Messung, sondern ihr Zweck: sie
misst eine Luecke, und die Luecke ist kleiner geworden.

Usage:
    python scripts/audit/measure-216-vrouwe-minne.py [--top 25]
"""
import argparse
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from mhg_normalizer import normalize_mhg  # noqa: E402
from corpus_files import corpus_files  # noqa: E402

# Konvention in scripts/audit/ (#329): das Skript druckt Korpusformen, und die
# MHG-Breven liegen ausserhalb von cp1252. Ohne den Wrapper toetet eine
# Windows-Konsole den Lauf an seiner eigenen Ausgabe.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

VROUWE = 'lemma_7260'   # vrouwe, NOM
VRO = 'lemma_7250'      # vrô "froh", ADJ ADV GRA NOM

# Literale statt \u-Escapes: die Zeichen sind sichtbar und stehen so auch im
# Ticket. Das Doppel-n ist die eigentliche Bedingung.
MINNE_RE = re.compile('^m[iíîy]nn[eè]?$', re.IGNORECASE)

# Zeilenartige Container. <lb/> steht bewusst nicht drin: es ist ein Milestone,
# also ein leeres Element, und damit nie Vorfahr eines <w>.
LINEISH = {'%sl' % TEI, '%sp' % TEI, '%shead' % TEI}


def lemma_ids(w):
    """Die Lemma-Ids eines <w>, token-genau (CONTRACTS B.1)."""
    ref = w.get('lemmaRef')
    return [t.split('#')[-1] for t in ref.split()] if ref else []


def form_of(w):
    """Die Oberflaechenform. itertext(), weil <w> Kindelemente tragen kann."""
    return ''.join(w.itertext()).strip()


def wrapper_of(w):
    """Beschreibt, worin das <w> steckt: direktes Kind der Zeile oder <hi>."""
    p = w.getparent()
    if p is None or p.tag in LINEISH:
        return '(direktes Kind)'
    return '%s rend=%s' % (etree.QName(p).localname, p.get('rend') or '-')


def build_inventory(files):
    """Formeninventar von vrouwe und vro, am Bestand erhoben."""
    vrouwe = Counter()
    vro = Counter()
    for fp in files:
        body = etree.parse(str(fp)).find('.//%sbody' % TEI)
        if body is None:
            continue
        for w in body.iter('%sw' % TEI):
            ids = lemma_ids(w)
            if not ids:
                continue
            f = form_of(w)
            if not f:
                continue
            n = normalize_mhg(f)
            if VROUWE in ids:
                vrouwe[n] += 1
            if VRO in ids:
                vro[n] += 1
    return vrouwe, vro


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=25)
    args = ap.parse_args()

    files = corpus_files()
    print('Korpusdateien: %d' % len(files))

    vrouwe_forms, vro_forms = build_inventory(files)
    inventory = set(vrouwe_forms)
    overlap = sorted(inventory & set(vro_forms))

    print('\n== Formeninventar (am Bestand erhoben) ==')
    print('normalisierte Formen mit %s : %4d  (%6d Tokens)'
          % (VROUWE, len(inventory), sum(vrouwe_forms.values())))
    print('normalisierte Formen mit %s : %4d  (%6d Tokens)'
          % (VRO, len(vro_forms), sum(vro_forms.values())))
    print('Schnittmenge der Inventare       : %4d  %s' % (len(overlap), overlap))

    # --- Durchgang ueber den Korpus: Fragen 1 und 2 in einem Lauf ------------
    unann = Counter()                 # normalisierte Form -> Tokens
    unann_raw = Counter()             # Rohform -> Tokens
    unann_sigles = defaultdict(set)
    pos_on_unann = Counter()
    total_w = 0

    pairs = []                        # (sigle, w-id, vrouwe-Rohform, minne-Rohform)
    pair_minne_lemma = Counter()
    pair_forms = Counter()
    pair_sigles = Counter()
    pair_v_wrapper = Counter()
    pair_m_wrapper = Counter()
    pair_minne_capital = Counter()
    pair_pred_ending = Counter()

    # Zaehlweisen-Vergleich (siehe Docstring)
    trav = Counter()

    for fp in files:
        sigle = fp.name.replace('.tei.xml', '')
        body = etree.parse(str(fp)).find('.//%sbody' % TEI)
        if body is None:
            continue
        ws = list(body.iter('%sw' % TEI))
        total_w += len(ws)
        forms = [form_of(w) for w in ws]
        # Die Vorfahren als Objekte halten, nicht als id(): lxml-Elemente sind
        # Proxies, die on demand entstehen und wieder verschwinden. Eine
        # aufgehobene id() zeigt danach auf nichts oder auf einen fremden
        # Proxy, und der Vergleich liefert stillschweigend Unsinn.
        parents = [w.getparent() for w in ws]

        for i, w in enumerate(ws):
            f = forms[i]
            if not f:
                continue
            n = normalize_mhg(f)
            in_inv = n in inventory
            has_lemma = bool(w.get('lemmaRef'))

            if in_inv and not has_lemma:
                unann[n] += 1
                unann_raw[f] += 1
                unann_sigles[n].add(sigle)
                pos_on_unann[w.get('pos') or '(kein @pos)'] += 1

            if i + 1 >= len(ws) or not MINNE_RE.match(forms[i + 1] or ''):
                continue

            # Zaehlweisen-Vergleich ueber alle vrouwe-minne-Paare
            direct = (parents[i] is not None and parents[i].tag in LINEISH
                      and parents[i + 1] is not None and parents[i + 1].tag in LINEISH)
            if VROUWE in lemma_ids(w):
                trav['A_folge'] += 1
                if direct:
                    trav['A_direkte_kinder'] += 1
            elif not has_lemma and in_inv:
                trav['B_folge'] += 1
                if direct:
                    trav['B_direkte_kinder'] += 1

            if has_lemma or not in_inv:
                continue

            m = ws[i + 1]
            pairs.append((sigle, w.get(XMLID, ''), f, forms[i + 1]))
            pair_minne_lemma['|'.join(lemma_ids(m)) or '(ohne lemmaRef)'] += 1
            pair_forms[n] += 1
            pair_sigles[sigle] += 1
            pair_v_wrapper[wrapper_of(w)] += 1
            pair_m_wrapper[wrapper_of(m)] += 1
            pair_minne_capital[forms[i + 1][:1].isupper()] += 1
            pair_pred_ending['mit -n' if n.endswith('n') else 'ohne -n'] += 1

    # --- Frage 1 ------------------------------------------------------------
    print('\n== Frage 1: formal vrouwe, ohne @lemmaRef ==')
    print('<w> im Korpus gesamt                : %d' % total_w)
    print('davon formal vrouwe ohne @lemmaRef  : %d' % sum(unann.values()))
    print('in distinkten normalisierten Formen : %d' % len(unann))
    print('in Sigeln                           : %d'
          % len(set().union(*unann_sigles.values())))
    print('\nnach Form:')
    for n, c in unann.most_common(args.top):
        print('  %-14s %5d  (%d Sigel)' % (n, c, len(unann_sigles[n])))
    print('\n@pos an diesen Tokens:')
    for p, c in pos_on_unann.most_common():
        print('  %-14s %5d' % (p, c))

    # --- Frage 2 ------------------------------------------------------------
    print('\n== Frage 2: davon unmittelbar vor einer minne-Form ==')
    print('Paare                               : %d' % len(pairs))
    print('in distinkten normalisierten Formen : %d' % len(pair_forms))
    print('in Sigeln                           : %d' % len(pair_sigles))
    print('\nnach Sigle:')
    for s, c in pair_sigles.most_common():
        print('  %-6s %4d' % (s, c))
    print('\nwas das minne-Token traegt:')
    for k, c in pair_minne_lemma.most_common():
        print('  %-24s %4d' % (k, c))
    print('\nEndung des vrouwe-Tokens:')
    for k, c in pair_pred_ending.most_common():
        print('  %-24s %4d' % (k, c))

    print('\nZaehlweise (siehe Docstring): <w>-Folge gegen direkte Kinder der Zeile')
    for k in sorted(trav):
        print('  %-22s %4d' % (k, trav[k]))

    print('\nWorin die Tokens stecken, vrouwe-Seite:')
    for k, c in pair_v_wrapper.most_common():
        print('  %-42s %4d' % (k, c))
    print('minne-Seite:')
    for k, c in pair_m_wrapper.most_common():
        print('  %-42s %4d' % (k, c))
    print('minne-Rohform beginnt mit Grossbuchstabe:')
    for k, c in pair_minne_capital.most_common():
        print('  %-42s %4d' % (k, c))

    # --- Frage 3 ------------------------------------------------------------
    print('\n== Frage 3: moegliche Ziel-Lemmata ==', flush=True)
    vtree = etree.parse(str(PROJECT_ROOT / 'authority-files' / 'variants.xml'))
    norm2lemmata = defaultdict(set)
    raw_types = {}
    for entry in vtree.iter('%sentry' % TEI):
        lid = (entry.get('corresp') or '').split('#')[-1]
        if not lid:
            continue
        for form in entry.iter('%sform' % TEI):
            raw = (form.text or '').strip()
            if not raw:
                continue
            norm2lemmata[normalize_mhg(raw)].add(lid)
            raw_types.setdefault((lid, raw), form.get(XMLID, ''))

    ltree = etree.parse(str(PROJECT_ROOT / 'authority-files' / 'lexicon.xml'))
    lemma_pos = {}
    lemma_orth = {}
    for entry in ltree.iter('%sentry' % TEI):
        lid = entry.get(XMLID)
        if not lid:
            continue
        lemma_pos[lid] = sorted({(p.text or '').strip() for p in entry.iter('%spos' % TEI)})
        orth = entry.find('.//%sorth' % TEI)
        lemma_orth[lid] = (orth.text or '').strip() if orth is not None else ''

    per_form = [(n, c, sorted(norm2lemmata.get(n, set()))) for n, c in unann.most_common()]
    cand_all = {l for _, _, cs in per_form for l in cs}
    missing = sorted(l for l in cand_all if l not in lemma_pos)

    print('distinkte Ziel-Lemmata ueber alle Formen : %d' % len(cand_all))
    print('davon in lexicon.xml vorhanden           : %d' % (len(cand_all) - len(missing)))
    print('davon fehlend (muessten gepraegt werden) : %d  %s' % (len(missing), missing))

    buckets = {0: [0, 0], 1: [0, 0], 2: [0, 0]}
    for _, c, cs in per_form:
        k = 0 if not cs else (1 if len(cs) == 1 else 2)
        buckets[k][0] += c
        buckets[k][1] += 1
    print('\nTokens nach Kandidatenlage (Stufe 2, Variantenwoerterbuch):')
    print('  kein Treffer in variants.xml : %6d Tokens in %3d Formen' % tuple(buckets[0]))
    print('  genau ein Lemma              : %6d Tokens in %3d Formen' % tuple(buckets[1]))
    print('  mehrere Lemmata              : %6d Tokens in %3d Formen' % tuple(buckets[2]))

    print('\nje Form:')
    for n, c, cs in per_form[:args.top]:
        desc = ', '.join('%s=%s/%s' % (l, lemma_orth.get(l, '?'),
                                       '|'.join(lemma_pos.get(l, [])) or '?')
                         for l in cs) or '(kein Treffer)'
        print('  %-14s %5d  %s' % (n, c, desc))

    # --- Stoppbedingung -----------------------------------------------------
    # Der Kickoff beendet die Welle, sobald die Umsetzung ein neues Lemma oder
    # einen neuen Variantentyp praegen muesste. Ein neuer Typ wird nur fuer ein
    # @corresp gebraucht, nicht fuer lemmaRef und pos; die Zahl steht hier
    # trotzdem, weil sie die Entscheidung traegt.
    print('\n== Stoppbedingung: neue Variantentypen noetig? ==')
    have_type = 0
    need_new = Counter()
    for raw, c in unann_raw.items():
        cs = norm2lemmata.get(normalize_mhg(raw), set())
        if len(cs) != 1:
            continue
        lid = next(iter(cs))
        if (lid, raw) in raw_types:
            have_type += c
        else:
            need_new[raw] += c
    print('eindeutige Tokens, Rohform schon als <form> am Ziel-Lemma : %d' % have_type)
    print('eindeutige Tokens, Rohform fehlt (neuer Typ noetig)       : %d'
          % sum(need_new.values()))
    for raw, c in need_new.most_common():
        print('   %-16s %d' % (raw, c))

    return 0


if __name__ == '__main__':
    sys.exit(main())
