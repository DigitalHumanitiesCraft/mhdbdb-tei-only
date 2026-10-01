#!/usr/bin/env python3
"""#459: sieben WZB-Tokens `lenden` meinen die Lende, nicht das Verb.

Sie tragen lemma_3702 lenden ("anlanden, enden") mit pos="VRB" und kommen auf
lemma_3701 lende (NOM). Freigabe Christian 01.10.2026 in der Session.

SENSE
-----
lemma_3701 hat zwei Senses. _sense_5861 traegt beide Koerperkonzepte
(concept_14011100 Saeugetiere, concept_21030000 Menschen) gemeinsam, also
bekommen alle sieben diesen Sense: die zwei Menschenstellen (35va, 64vb) und
die fuenf Levitikus-Stellen ueber das Opfertier gleichermassen.
_sense_5862 (concept_12010000, concept_31500000) ist nicht gemeint.

TYP
---
Regel aus #367: neue Nummer praegen, nie eine bestehende umhaengen.
type_12871 ist `lenden` unter lemma_3702 und behaelt die uebrigen 38 Tokens
des Verbs. Hoechste vergebene Nummer am 01.10.2026: type_372391 (gemessen an
variants.xml auf origin/main 652815547). Gepraegt wird type_372392 fuer
`lenden` unter lemma_3701.

SCHREIBWEISE
------------
Wie apply-387-418-464.py: gefunden mit lxml, geschrieben textuell mit
re.subn, nur das oeffnende <w>-Tag aendert sich, CRLF bleibt erhalten. Der
Ist-Zustand jedes Tokens wird vorher verifiziert; das Skript ist deshalb
nicht idempotent.

Usage:
    python scripts/ingest/pos-disambig/apply-459-lende.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-459-lende.py --apply
"""

import io
import re
import sys
from pathlib import Path

from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
APPLY = '--apply' in sys.argv

NEUER_TYP = 'type_372392'
FORM = 'lenden'
IST = ('lemma_3702', 'VRB', 'lemma_3702_sense_5863', 'type_12871', None)
SOLL = ('lemma_3701', 'NOM', 'lemma_3701_sense_5861', NEUER_TYP, None)

IDS = [
    'WZB_35va_29_1',
    'WZB_64vb_28_7',
    'WZB_100rb_36_2',
    'WZB_100va_31_1',
    'WZB_100vb_15_7',
    'WZB_101rb_10_0',
    'WZB_104rb_3_3',
]

REVISION = ('#459 lenden: 7 Tokens meinen die Lende und stehen jetzt auf lemma_3701 lende '
            '(NOM, lemma_3701_sense_5861) statt auf dem Verb lemma_3702; neu gepraegter '
            'Variantentyp type_372392 nach der Regel aus #367.')
DATUM = '2026-10-01'

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def frag(wert):
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def neues_tag(wid):
    lemma, pos, ana, corresp, _ = SOLL
    return (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#{lemma}" pos="{pos}" '
            f'ana="lexicon.xml#{ana}" corresp="variants.xml#{corresp}">')


def main():
    if len(IDS) != 7 or len(set(IDS)) != 7:
        sys.exit('ABBRUCH: erwartet 7 verschiedene xml:id')

    varianten = (ROOT / 'authority-files' / 'variants.xml').read_text(encoding='utf-8')
    hoechster = max(int(m) for m in re.findall(r'xml:id="type_(\d+)"', varianten))
    if hoechster != 372391:
        sys.exit(f'ABBRUCH: hoechste Typnummer {hoechster}, erwartet 372391')

    lexikon = (ROOT / 'authority-files' / 'lexicon.xml').read_text(encoding='utf-8')
    if f'xml:id="{SOLL[2]}"' not in lexikon:
        sys.exit(f'ABBRUCH: {SOLL[2]} fehlt in lexicon.xml')

    pfad = ROOT / 'tei' / 'WZB.tei.xml'
    gefunden = {}
    for w in etree.parse(str(pfad)).iter(f'{TEI_NS}w'):
        wid = w.get(XMLID)
        if wid in IDS:
            gefunden[wid] = (''.join(w.itertext()).strip(),
                             (frag(w.get('lemmaRef')), w.get('pos'), frag(w.get('ana')),
                              frag(w.get('corresp')), w.get('reason')))
    fehler = []
    for wid in IDS:
        if wid not in gefunden:
            fehler.append(f'{wid}: nicht gefunden')
            continue
        form, wert = gefunden[wid]
        if form != FORM:
            fehler.append(f'{wid}: Form {form!r}, erwartet {FORM!r}')
        if wert != IST:
            fehler.append(f'{wid}: ist {wert}, erwartet {IST}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand aller {len(IDS)} Tokens wie erwartet.')

    with open(pfad, encoding='utf-8', newline='') as fh:
        text = fh.read()
    for wid in IDS:
        muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
        treffer = muster.findall(text)
        if len(treffer) != 1 or treffer[0].strip() != FORM:
            sys.exit(f'ABBRUCH: {wid} textuell {len(treffer)}x, Form {treffer!r}')
        text, n = muster.subn(lambda m, t=neues_tag(wid): t + m.group(1) + '</w>', text)
        if n != 1:
            sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')

    m = ANKER.search(text)
    if not m:
        sys.exit('ABBRUCH: kein revisionDesc-Anker in WZB')
    nl = '\r\n' if '\r\n' in m.group(3) else '\n'
    eintrag = f'<change when="{DATUM}" who="#editor">{REVISION}</change>'
    text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]

    if APPLY:
        with open(pfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
    print(f'WZB.tei.xml: {len(IDS)} Tokens auf {SOLL[0]} {SOLL[1]} {SOLL[2]} {NEUER_TYP}'
          + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
