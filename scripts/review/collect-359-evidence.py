#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#359: Belegstellen mit Kontext fuer Boreks Verdachts- und Klassifikationsfaelle.

Die Pruefseite aus #443 zeigt Belege, keine Stichwoerter. Dieses Skript holt
die Belege aus dem Korpus, damit ein Vorschlag aus dem Gelesenen entstehen kann
und nicht aus dem Lemmanamen. Der Fall, gegen den das geschrieben ist, steht in
CLAUDE.md: `Alanya` wurde am 10.09.2026 aus dem Stichwort heraus fuer einen
tuerkischen Ortsnamen gehalten, waehrend die sieben Belege sechsmal
"der kuenc von alanye" lesen.

## Die zwei Klassen, und warum sie verschieden gesucht werden

`verdacht` (25 Paare): die Schreibung ist ueber das Varianten-Woerterbuch
gelaufen, das Lemma lautet aber voellig anders. Die Behauptung dahinter ist,
dass irgendwo im Korpus ein <w> mit GENAU DIESER Schreibung GENAU DIESES Lemma
traegt. Gesucht wird deshalb nach dem Paar: normalisierte Wortform gleich
normalisierter Borek-Form UND @lemmaRef enthaelt das Lemma. Findet die Suche
nichts, ist das ein harter Fehler und kein leeres Ergebnis: dann stimmt die
Behauptung des Reports nicht mehr, und niemand darf das stillschweigend
uebergehen.

`klassifikation` (15 Paare plus die 5 Koerperteile): das Lemma ist richtig
getroffen und traegt kein einschlaegiges Konzept. Zu beurteilen ist der
Gebrauch des Lemmas, nicht einer Schreibung. Gesucht wird deshalb nach allen
Tokens des Lemmas, unabhaengig von der Schreibung.

## Kontext

Der Beleg ist die Verszeile und nicht ein Wortfenster. Ausgegeben werden die
Zeile davor, die Trefferzeile in drei Teilen (davor, Treffer, danach) und die
Zeile danach. Steht das Token nicht in einem <l> (Prosa), faellt die Ausgabe
auf ein Wortfenster zurueck und sagt das im Feld `kontextart`.

Usage:
    python scripts/review/collect-359-evidence.py --counts
    python scripts/review/collect-359-evidence.py --write
"""
import argparse
import gzip
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / 'scripts'))
from corpus_files import corpus_files  # noqa: E402
from mhg_normalizer import normalize_mhg as normalize  # noqa: E402
from tei_namespaces import TEI_NS_URI  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI = '{%s}' % TEI_NS_URI
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

AUTH_INDEX = REPO / 'data' / 'authority-index.json.gz'
# Alles Borek-Material dieses Laufs liegt unter diesem Pfad. `ingest/horses/`
# wird nur gelesen: es gehoert dem Vorgang #193 und nicht dieser Pruefseite.
OUT_DIR = REPO / 'ingest' / 'review' / '359-borek'
CROSSCHECK = OUT_DIR / 'crosscheck.json'

# Wortfenster fuer Prosa, in Tokens je Seite.
PROSA_FENSTER = 20

# Verszeilen je Seite um die Trefferzeile. Zwei statt einer: bei `celder` in
# ROT_28700_1 und bei `irhancte` in ROT_27720_3 entscheidet erst der Satz
# darueber oder darunter, ob von einem Pferd die Rede ist, und wer nur die
# Nachbarzeile sieht, raet.
VERS_FENSTER = 2

# Obergrenze der GESAMMELTEN Belege je Fall. Sie ist bewusst hoch: dieses
# Skript liefert die Lesegrundlage, und wer einen Vorschlag aus Belegen bildet,
# braucht sie vollstaendig, solange sie lesbar ist. Wie viele davon in der
# Pruefseite ERSCHEINEN, entscheidet der Seitengenerator und nicht diese Zahl.
# Die gezaehlte Menge bleibt von beidem unberuehrt und steht als
# `tokens_gesamt` daneben: eine Seite, die 12 von 1.406 Belegen zeigt, muss
# beides sagen, sonst liest sie sich als vollstaendig.
BELEG_CAP = 250


def token_text(el):
    return ''.join(el.itertext()).strip()


def lemma_ids(w):
    """Die Lemma-IDs eines Tokens, tokengenau (CONTRACTS.md B.1).

    Nie als Teilzeichenkette pruefen: `#lemma_308` darf `#lemma_3089` nicht
    treffen.
    """
    ref = w.get('lemmaRef')
    if not ref:
        return []
    return [t.split('#')[-1] for t in ref.split()]


def lade_faelle():
    """Die Faelle aus dem Crosscheck-Report, nicht aus dem Ticket-Body.

    Der Body von #359 zeigt 13 der 25 Verdachtsformen und 5 der 15
    Klassifikationskandidaten, ohne zu sagen, dass das eine Auswahl ist.
    Gemessen am 21.09.2026.
    """
    if not CROSSCHECK.exists():
        sys.exit('%s fehlt. Erzeugen mit:\n'
                 '  python scripts/ingest/horses/01-wordlist-crosscheck.py --json > %s'
                 % (CROSSCHECK, CROSSCHECK))
    with CROSSCHECK.open(encoding='utf-8') as fh:
        report = json.load(fh)

    erwartet = ['wl-pferdetypen', 'wl-koerperteile', 'wl-gangarten']
    fehlend = [n for n in erwartet if n not in report]
    if fehlend:
        sys.exit('Listen fehlen im Report: %s' % ', '.join(fehlend))

    faelle = []
    for liste in erwartet:
        d = report[liste]
        for feld in ('offen', 'verdacht'):
            if feld not in d:
                sys.exit('Feld %s fehlt bei %s' % (feld, liste))
        for row in d['verdacht']:
            form, how, lid, lemma, concepts, homogr = row
            faelle.append(dict(klasse='verdacht', liste=liste, form=form,
                               aufloesung=how, lemma_id=lid, lemma=lemma,
                               concept_ids=concepts, homographen=homogr))
        for row in d['offen']:
            form, how, lid, lemma, concepts, homogr = row
            klasse = ('koerperteil' if liste == 'wl-koerperteile'
                      else 'klassifikation')
            faelle.append(dict(klasse=klasse, liste=liste, form=form,
                               aufloesung=how, lemma_id=lid, lemma=lemma,
                               concept_ids=concepts, homographen=homogr))
    return faelle


def lade_authority():
    """Lemma- und Konzeptnamen, damit die Seite nicht nur IDs zeigt."""
    with gzip.open(AUTH_INDEX, 'rb') as fh:
        idx = json.loads(fh.read())
    lemmata = {l['id']: l for l in idx['lemmata']}
    concepts = {c['id']: c for c in idx['concepts']}
    return idx.get('version', '?'), lemmata, concepts


def zeilen_karte(body):
    """(Liste der <l> in Dokumentreihenfolge, {id(w): index des <l>})."""
    ls = list(body.iter(TEI + 'l'))
    w_zu_l = {}
    for i, l in enumerate(ls):
        for w in l.iter(TEI + 'w'):
            w_zu_l[id(w)] = i
    return ls, w_zu_l


def zeilen_text(l, ausser=None):
    """Der Wortlaut einer Verszeile. `ausser` blendet das Treffertoken aus."""
    teile = []
    for el in l.iter():
        if el.tag not in (TEI + 'w', TEI + 'pc'):
            continue
        if ausser is not None and el is ausser:
            continue
        t = token_text(el)
        if t:
            teile.append(t)
    return ' '.join(teile)


def zeile_geteilt(l, treffer):
    """Die Trefferzeile in (davor, Treffer, danach)."""
    davor, danach, gesehen = [], [], False
    for el in l.iter():
        if el.tag not in (TEI + 'w', TEI + 'pc'):
            continue
        if el is treffer:
            gesehen = True
            continue
        t = token_text(el)
        if not t:
            continue
        (danach if gesehen else davor).append(t)
    return ' '.join(davor), token_text(treffer), ' '.join(danach)


def beleg(w, i, alle_texte, ls, w_zu_l, sigle, meta):
    """Ein Beleg mit Kontext. Verszeile, wo es eine gibt, sonst Wortfenster."""
    li = w_zu_l.get(id(w))
    gemeinsam = dict(
        sigle=sigle,
        titel=meta.get('titel', ''),
        autor=meta.get('autor', ''),
        xml_id=w.get(XML_ID) or '',
        form=token_text(w),
        pos=w.get('pos') or '',
        lemma_ref=w.get('lemmaRef') or '',
        ana=w.get('ana') or '',
    )
    if li is None:
        lo, hi = max(0, i - PROSA_FENSTER), i + PROSA_FENSTER + 1
        gemeinsam.update(
            kontextart='prosa',
            zeile_n='',
            zeilen_davor=[],
            treffer_davor=' '.join(t for t in alle_texte[lo:i] if t),
            treffer=alle_texte[i],
            treffer_danach=' '.join(t for t in alle_texte[i + 1:hi] if t),
            zeilen_danach=[],
        )
        return gemeinsam
    davor, tr, danach = zeile_geteilt(ls[li], w)
    gemeinsam.update(
        kontextart='vers',
        zeile_n=ls[li].get('n') or '',
        zeilen_davor=[dict(n=ls[j].get('n') or '', text=zeilen_text(ls[j]))
                      for j in range(max(0, li - VERS_FENSTER), li)],
        treffer_davor=davor,
        treffer=tr,
        treffer_danach=danach,
        zeilen_danach=[dict(n=ls[j].get('n') or '', text=zeilen_text(ls[j]))
                       for j in range(li + 1, min(len(ls), li + 1 + VERS_FENSTER))],
    )
    return gemeinsam


def scan(faelle, nur_zaehlen):
    """Ein Durchlauf ueber den Korpus fuer alle Faelle gemeinsam."""
    # Verdacht: Paar aus normalisierter Form und Lemma.
    paar_gesucht = defaultdict(set)   # norm_form -> {lemma_id}
    for f in faelle:
        if f['klasse'] == 'verdacht':
            paar_gesucht[normalize(f['form'])].add(f['lemma_id'])
    # Klassifikation und Koerperteile: nur das Lemma.
    lemma_gesucht = {f['lemma_id'] for f in faelle if f['klasse'] != 'verdacht'}

    paar_tokens = Counter()
    paar_texte = defaultdict(set)
    paar_belege = defaultdict(list)
    lemma_tokens = Counter()
    lemma_texte = defaultdict(set)
    lemma_formen = defaultdict(Counter)
    lemma_belege = defaultdict(list)

    parser = etree.XMLParser(no_network=True, load_dtd=False, resolve_entities=False)
    for fp in corpus_files():
        baum = etree.parse(str(fp), parser)
        wurzel = baum.getroot()
        body = wurzel.find('.//%sbody' % TEI)
        if body is None:
            continue
        sigle = fp.name.split('.')[0]
        titel_el = wurzel.find('.//%stitleStmt/%stitle' % (TEI, TEI))
        autor_el = wurzel.find('.//%stitleStmt/%sauthor' % (TEI, TEI))
        meta = dict(
            titel=(''.join(titel_el.itertext()).strip() if titel_el is not None else ''),
            autor=(''.join(autor_el.itertext()).strip() if autor_el is not None else ''),
        )

        ws = list(body.iter(TEI + 'w'))
        texte = [token_text(w) for w in ws]
        ls, w_zu_l = ([], {}) if nur_zaehlen else zeilen_karte(body)

        for i, w in enumerate(ws):
            lids = lemma_ids(w)
            if not lids:
                continue
            norm = normalize(texte[i]) if texte[i] else ''
            kandidaten = paar_gesucht.get(norm)
            for lid in lids:
                if kandidaten and lid in kandidaten:
                    schluessel = (norm, lid)
                    paar_tokens[schluessel] += 1
                    paar_texte[schluessel].add(sigle)
                    if not nur_zaehlen and len(paar_belege[schluessel]) < BELEG_CAP:
                        paar_belege[schluessel].append(
                            beleg(w, i, texte, ls, w_zu_l, sigle, meta))
                if lid in lemma_gesucht:
                    lemma_tokens[lid] += 1
                    lemma_texte[lid].add(sigle)
                    lemma_formen[lid][texte[i]] += 1
                    if not nur_zaehlen and len(lemma_belege[lid]) < BELEG_CAP:
                        lemma_belege[lid].append(
                            beleg(w, i, texte, ls, w_zu_l, sigle, meta))

    return dict(paar_tokens=paar_tokens, paar_texte=paar_texte, paar_belege=paar_belege,
                lemma_tokens=lemma_tokens, lemma_texte=lemma_texte,
                lemma_formen=lemma_formen, lemma_belege=lemma_belege)


def main():
    ap = argparse.ArgumentParser(description='#359: Belegstellen mit Kontext sammeln.')
    ap.add_argument('--counts', action='store_true',
                    help='Nur Umfang messen, keine Belege sammeln, nichts schreiben.')
    ap.add_argument('--write', action='store_true',
                    help='Belege nach ingest/review/359-borek/evidence.json schreiben.')
    args = ap.parse_args()
    if not args.counts and not args.write:
        ap.error('entweder --counts oder --write')

    faelle = lade_faelle()
    auth_version, lemmata, concepts = lade_authority()

    erg = scan(faelle, nur_zaehlen=args.counts)

    ohne_beleg = []
    for f in faelle:
        if f['klasse'] == 'verdacht':
            k = (normalize(f['form']), f['lemma_id'])
            f['tokens_gesamt'] = erg['paar_tokens'].get(k, 0)
            f['texte_gesamt'] = len(erg['paar_texte'].get(k, ()))
            f['belege'] = erg['paar_belege'].get(k, [])
            f['belegregel'] = 'Schreibung und Lemma gemeinsam'
        else:
            lid = f['lemma_id']
            f['tokens_gesamt'] = erg['lemma_tokens'].get(lid, 0)
            f['texte_gesamt'] = len(erg['lemma_texte'].get(lid, ()))
            f['formen'] = erg['lemma_formen'].get(lid, Counter()).most_common(15)
            f['belege'] = erg['lemma_belege'].get(lid, [])
            f['belegregel'] = 'alle Tokens des Lemmas'
        lem = lemmata.get(f['lemma_id'])
        f['lemma_normalisiert'] = lem.get('normalized', '') if lem else ''
        f['konzepte'] = [
            dict(id=c, term=(concepts.get(c) or {}).get('termDE', ''))
            for c in f['concept_ids']
        ]
        if f['tokens_gesamt'] == 0:
            ohne_beleg.append(f)

    # Defensiv: ein Verdachtsfall ohne Beleg widerlegt die Behauptung des
    # Reports. Das ist ein harter Fehler, kein stilles Ueberspringen.
    verdacht_ohne_beleg = [f for f in ohne_beleg if f['klasse'] == 'verdacht']

    for klasse in ('verdacht', 'klassifikation', 'koerperteil'):
        teil = [f for f in faelle if f['klasse'] == klasse]
        print('=' * 78)
        print('%s: %d Faelle' % (klasse, len(teil)))
        print('=' * 78)
        for f in sorted(teil, key=lambda x: -x['tokens_gesamt']):
            print('  %-12s %-14s %-16s %6d Tokens in %4d Texten'
                  % (f['form'], f['lemma_id'], f['lemma'],
                     f['tokens_gesamt'], f['texte_gesamt']))
        summe = sum(f['tokens_gesamt'] for f in teil)
        print('  Summe: %d Tokens' % summe)
        print()

    if verdacht_ohne_beleg:
        print('FEHLER: %d Verdachtsfaelle ohne einen einzigen Beleg im Korpus.'
              % len(verdacht_ohne_beleg))
        for f in verdacht_ohne_beleg:
            print('  %s -> %s (%s)' % (f['form'], f['lemma_id'], f['lemma']))
        print('Der Crosscheck-Report behauptet fuer jeden Verdachtsfall ein <w>')
        print('mit dieser Schreibung und diesem Lemma. Trifft das nicht zu, ist')
        print('der Report oder der Korpus seit seiner Messung veraendert worden.')
        return 1

    if args.counts:
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ziel = OUT_DIR / 'evidence.json'
    nutzlast = dict(
        erzeugt_von='scripts/review/collect-359-evidence.py',
        authority_index_version=auth_version,
        beleg_cap=BELEG_CAP,
        faelle=faelle,
    )
    with ziel.open('w', encoding='utf-8') as fh:
        json.dump(nutzlast, fh, ensure_ascii=False, indent=2)
    print('geschrieben: %s (%d Faelle, Authority-Index %s)'
          % (ziel, len(faelle), auth_version))
    return 0


if __name__ == '__main__':
    sys.exit(main())
