#!/usr/bin/env python3
"""#460: 145 Tokens `jaget`/`jeit`/`jait` sind Verbformen und stehen auf dem
Substantivlemma lemma_3103 jagât. Sie kommen auf lemma_3102 jagen (VRB).

Freigabe Christian 10.10.2026 im Ticket (Kommentar "Entschieden von @chsteiner
am 10.10.2026"). Die Arbeitsliste ingest/pos-disambig/460-jagat/belege.tsv
traegt die Einstufung je Token am Kontext: 145 Verb, 35 Substantiv, 5 unklar.
Umgehaengt werden nur die Zeilen "Verb"; die 35 Substantive und die 5 unklaren
bleiben unberuehrt.

SENSE
-----
Die Tokens trugen @ana auf lemma_3103_sense_4930. Das Attribut entfaellt, wie
beim Grossteil des Bestands unter lemma_3102 (1.247 von 1.406 Tokens ohne
@ana, gemessen am 10.10.2026); eine Sense-Wahl am Kontext waere ein eigener
Auftrag.

TYP
---
Regel aus #367: neue Nummer praegen, nie eine bestehende umhaengen. Die Typen
type_10674 (jaget), type_10676 (jeit) und type_115155 (jait) gehoeren zu
lemma_3103 und behalten ihre Nummern. Hoechste vergebene Nummer am 10.10.2026:
type_372854 (gemessen an variants.xml auf origin/main eeaff69d8). Gepraegt
werden unter lemma_3102 type_372855 (jaget), type_372856 (jeit), type_372857
(jait). variants.xml wird anschliessend mit extract-variants.py --apply
regeneriert; das Skript legt die Typen dort nicht selbst an.

SCHREIBWEISE
------------
Wie apply-459-lende.py: gefunden mit lxml, geschrieben textuell mit re.subn,
nur das oeffnende <w>-Tag aendert sich, das Zeilenende der Datei bleibt
erhalten. Der Ist-Zustand jedes Tokens wird vorher verifiziert; das Skript ist
deshalb nicht idempotent. Je Datei kommt ein <change> in die revisionDesc.

Usage:
    python scripts/ingest/pos-disambig/apply-460-jagat.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-460-jagat.py --apply
"""

import csv
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
APPLY = '--apply' in sys.argv

LISTE = ROOT / 'ingest' / 'pos-disambig' / '460-jagat' / 'belege.tsv'
HOECHSTE_TYPNUMMER = 372854
NEUE_TYPEN = {'jaget': 'type_372855', 'jeit': 'type_372856', 'jait': 'type_372857'}
ALT_TYP = {'jaget': 'type_10674', 'jeit': 'type_10676', 'jait': 'type_115155'}
ERWARTET = {'Verb': 145, 'Substantiv': 35, 'unklar': 5}
ERWARTET_DATEIEN = 51

ALT = ('lemma_3103', 'NOM', 'lemma_3103_sense_4930')
SOLL_LEMMA, SOLL_POS = 'lemma_3102', 'VRB'

DATUM = '2026-10-10'
ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def frag(wert):
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def neues_tag(wid, form):
    return (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#{SOLL_LEMMA}" pos="{SOLL_POS}" '
            f'corresp="variants.xml#{NEUE_TYPEN[form]}">')


def lies_liste():
    with open(LISTE, encoding='utf-8', newline='') as fh:
        zeilen = list(csv.DictReader(fh, delimiter='\t'))
    zaehlung = defaultdict(int)
    for z in zeilen:
        zaehlung[z['Einstufung']] += 1
    if dict(zaehlung) != ERWARTET:
        sys.exit(f'ABBRUCH: Einstufungen {dict(zaehlung)}, erwartet {ERWARTET}')
    return [z for z in zeilen if z['Einstufung'] == 'Verb']


def main():
    verben = lies_liste()
    ids = [z['xml:id'] for z in verben]
    if len(set(ids)) != len(ids):
        sys.exit('ABBRUCH: xml:id doppelt in der Liste')
    je_datei = defaultdict(list)
    for z in verben:
        if z['Form'] not in NEUE_TYPEN:
            sys.exit(f"ABBRUCH: unbekannte Form {z['Form']!r} bei {z['xml:id']}")
        je_datei[z['Sigle']].append(z)
    if len(je_datei) != ERWARTET_DATEIEN:
        sys.exit(f'ABBRUCH: {len(je_datei)} Dateien, erwartet {ERWARTET_DATEIEN}')

    varianten = (ROOT / 'authority-files' / 'variants.xml').read_text(encoding='utf-8')
    hoechster = max(int(m) for m in re.findall(r'xml:id="type_(\d+)"', varianten))
    if hoechster != HOECHSTE_TYPNUMMER:
        sys.exit(f'ABBRUCH: hoechste Typnummer {hoechster}, erwartet {HOECHSTE_TYPNUMMER}')
    lexikon = (ROOT / 'authority-files' / 'lexicon.xml').read_text(encoding='utf-8')
    for lid in (SOLL_LEMMA, ALT[0]):
        if f'<entry xml:id="{lid}">' not in lexikon:
            sys.exit(f'ABBRUCH: {lid} fehlt in lexicon.xml')

    # Phase 1: Ist-Zustand aller Tokens pruefen, nichts schreiben
    fehler = []
    for sigle, eintraege in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        gefunden = {}
        for w in etree.parse(str(pfad)).iter(f'{TEI_NS}w'):
            wid = w.get(XMLID)
            gefunden[wid] = w
        for z in eintraege:
            wid = z['xml:id']
            w = gefunden.get(wid)
            if w is None:
                fehler.append(f'{wid}: nicht gefunden')
                continue
            form = ''.join(w.itertext()).strip()
            ist = (frag(w.get('lemmaRef')), w.get('pos'), frag(w.get('ana')),
                   frag(w.get('corresp')), sorted(w.attrib))
            soll = (ALT[0], ALT[1], ALT[2], ALT_TYP[z['Form']],
                    sorted(['lemmaRef', 'pos', 'ana', 'corresp', XMLID]))
            if form != z['Form']:
                fehler.append(f"{wid}: Form {form!r}, erwartet {z['Form']!r}")
            if ist != soll:
                fehler.append(f'{wid}: ist {ist}, erwartet {soll}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand aller {len(ids)} Tokens in {len(je_datei)} Dateien wie erwartet.')

    # Phase 2: textuell ersetzen
    neu = {}
    for sigle, eintraege in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for z in eintraege:
            wid = z['xml:id']
            muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
            treffer = muster.findall(text)
            if len(treffer) != 1 or treffer[0].strip() != z['Form']:
                sys.exit(f'ABBRUCH: {wid} textuell {len(treffer)}x, Form {treffer!r}')
            text, n = muster.subn(
                lambda m, t=neues_tag(wid, z['Form']): t + m.group(1) + '</w>', text)
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        nl = '\r\n' if '\r\n' in m.group(3) else '\n'
        revision = (f'#460 jagen: {len(eintraege)} Token{"" if len(eintraege) == 1 else "s"} '
                    f'als Verbform gelesen, von lemma_3103 jagât (NOM) auf {SOLL_LEMMA} jagen '
                    f'({SOLL_POS}) umgehängt, @ana entfällt; neu geprägte Variantentypen '
                    f'nach der Regel aus #367.')
        eintrag = f'<change when="{DATUM}" who="#editor">{revision}</change>'
        text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    if APPLY:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
    je_form = defaultdict(int)
    for z in verben:
        je_form[z['Form']] += 1
    print(f'{len(ids)} Tokens ({dict(je_form)}) in {len(neu)} Dateien auf {SOLL_LEMMA} {SOLL_POS}, '
          f'Typen {NEUE_TYPEN}' + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
