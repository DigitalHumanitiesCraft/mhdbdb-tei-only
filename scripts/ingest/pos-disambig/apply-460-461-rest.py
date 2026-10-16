#!/usr/bin/env python3
"""#460 und #461, Rest nach KZWs Antworten vom 15.10.2026.

Freigabe: Kickoff `docs/playbooks/kickoffs/2026-10-16-kickoff-daten.md` (A1 bis
A3), Grundlage KZWs Kommentare vom 15.10.2026 in #460 und #461.

#460 (A1)
---------
WH_28126_1 (jaget) und JT_43134000_4 (jagennes) sind Verbformen (KZW: "Verb")
und kommen von lemma_3103 jagat (NOM) auf lemma_3102 jagen (VRB), @ana entfaellt,
wie bei den 145 aus PR #565. WVW_6542_4 ("Nomen") bleibt unveraendert,
AXU_18452_5 und JT_48611000_4 ("brauche mehr Kontext") ebenfalls.
Typen nach der Regel aus #367: fuer jaget gibt es unter lemma_3102 schon
type_372855 (aus #565, wird wiederverwendet), fuer jagennes wird type_372858
gepraegt (hoechste vergebene Nummer 372857, gemessen an variants.xml). Der alte
Typ type_319550 verliert seinen einzigen Beleg; variants.xml wird mit
extract-variants.py --apply regeneriert.

#461 (A2, A3)
-------------
- A3: zwei neue Senses an lemma_1958 mit je einem vorhandenen Koerperkonzept:
  lemma_1958_sense_119198 (concept_14021100, Voegel) fuer AMI_972_3 (Hahn),
  lemma_1958_sense_119199 (concept_14031100, Fische) fuer FLG1_4135180940_2.
  Hoechste Sense-Nummer vorher 119197 (lemma_79829_sense_119197, gemessen an
  lexicon.xml), also fortlaufend 119198 und 119199.
- A2: die 9 offenen Belege kommen nach KZWs Regel ("Bei unklaren Gebeinen
  haengen wir sie an die menschlichen Gebeine dran") an lemma_1958_sense_49690.
  NAR_9400900_3 traegt ihn schon; die uebrigen 8 bekommen ihn (JSG_410_1 wechselt
  von sense_3004 und verliert damit das Tod-Konzept 21104000).

SCHREIBWEISE
------------
Wie apply-460-jagat.py und apply-461-gebeine.py: gefunden mit lxml, geschrieben
textuell, Ist-Zustand vorher verifiziert (nicht idempotent), Zeilenende
erhalten, je Datei ein <change> in der revisionDesc.

Usage:
    python scripts/ingest/pos-disambig/apply-460-461-rest.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-460-461-rest.py --apply
"""

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
DATUM = '2026-10-16'

HOECHSTE_TYPNUMMER = 372857
HOECHSTE_SENSENUMMER = 119197

# (xml:id, Form, Ist-@lemmaRef, Ist-@pos, Ist-@ana, Ist-@corresp)
# -> Soll (lemma, pos, ana, corresp)
JAGEN = {
    'WH_28126_1': ('jaget', ('lemma_3103', 'NOM', 'lemma_3103_sense_4930', 'type_10674'),
                   ('lemma_3102', 'VRB', None, 'type_372855')),
    'JT_43134000_4': ('jagennes', ('lemma_3103', 'NOM', 'lemma_3103_sense_4930', 'type_319550'),
                      ('lemma_3102', 'VRB', None, 'type_372858')),
}

NEUE_SENSES = {
    'lemma_1958_sense_119198': 'concept_14021100',
    'lemma_1958_sense_119199': 'concept_14031100',
}
# xml:id -> (Form, Ist-@ana, Soll-@ana)
S3004 = 'lemma_1958_sense_3004'
S49690 = 'lemma_1958_sense_49690'
GEBEINE = {
    'AMI_972_3': ('gebeine', None, 'lemma_1958_sense_119198'),
    'FLG1_4135180940_2': ('gebeine', None, 'lemma_1958_sense_119199'),
    'HTR_201620_3': ('gebeine', None, S49690),
    'DRE_177_1': ('gepain', None, S49690),
    'DRE_180_1': ('gepain', None, S49690),
    'DRE_181_2': ('gepain', None, S49690),
    'NAR_9303540_3': ('gbeyn', None, S49690),
    'ROL_4345_1': ('gebaines', None, S49690),
    'JSG_410_1': ('gebein', S3004, S49690),
    'IW_5852_4': ('gebeine', None, S49690),
}

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)
SENSE_ENDE = re.compile(
    r'(<sense xml:id="lemma_1958_sense_119196"[^>]*>.*?</sense>)([ \t]*\r?\n)', re.S)


def frag(wert):
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def sigle_von(wid):
    return wid.split('_')[0]


def setze_ana(tag, ana):
    neu = f'ana="lexicon.xml#{ana}"'
    if re.search(r'\bana="', tag):
        return re.sub(r'\bana="[^"]*"', neu, tag, count=1)
    return re.sub(r'(\bpos="[^"]*")', r'\1 ' + neu, tag, count=1)


def main():
    varianten = (ROOT / 'authority-files' / 'variants.xml').read_text(encoding='utf-8')
    hoechster = max(int(m) for m in re.findall(r'xml:id="type_(\d+)"', varianten))
    if hoechster != HOECHSTE_TYPNUMMER:
        sys.exit(f'ABBRUCH: hoechste Typnummer {hoechster}, erwartet {HOECHSTE_TYPNUMMER}')
    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    with open(lexpfad, encoding='utf-8', newline='') as fh:
        lexikon = fh.read()
    hoechste = max(int(m) for m in re.findall(r'_sense_(\d+)"', lexikon))
    if hoechste != HOECHSTE_SENSENUMMER:
        sys.exit(f'ABBRUCH: hoechste Sense-Nummer {hoechste}, erwartet {HOECHSTE_SENSENUMMER}')
    for sid in NEUE_SENSES:
        if f'xml:id="{sid}"' in lexikon:
            sys.exit(f'ABBRUCH: {sid} steht schon in lexicon.xml')
    for lid in ('lemma_3102', 'lemma_3103'):
        if f'<entry xml:id="{lid}">' not in lexikon:
            sys.exit(f'ABBRUCH: {lid} fehlt in lexicon.xml')
    konzepte = (ROOT / 'authority-files' / 'concepts.xml').read_text(encoding='utf-8')
    for kid in NEUE_SENSES.values():
        if f'xml:id="{kid}"' not in konzepte:
            sys.exit(f'ABBRUCH: {kid} fehlt in concepts.xml')
    if len(SENSE_ENDE.findall(lexikon)) != 1:
        sys.exit('ABBRUCH: Sense-Anker sense_119196 nicht genau einmal in lexicon.xml')

    je_datei = defaultdict(list)
    for wid in list(JAGEN) + list(GEBEINE):
        je_datei[sigle_von(wid)].append(wid)

    # Phase 1: Ist-Zustand pruefen
    fehler = []
    for sigle, ids in sorted(je_datei.items()):
        gefunden = {w.get(XMLID): w
                    for w in etree.parse(str(ROOT / 'tei' / f'{sigle}.tei.xml')).iter(f'{TEI_NS}w')}
        for wid in ids:
            w = gefunden.get(wid)
            if w is None:
                fehler.append(f'{wid}: nicht gefunden')
                continue
            form = ''.join(w.itertext()).strip()
            if wid in JAGEN:
                f_soll, (l, p, a, c), _ = JAGEN[wid]
                ist = (frag(w.get('lemmaRef')), w.get('pos'), frag(w.get('ana')), frag(w.get('corresp')))
                if form != f_soll or ist != (l, p, a, c):
                    fehler.append(f'{wid}: Form {form!r}, ist {ist}')
                if set(w.attrib) != {XMLID, 'lemmaRef', 'pos', 'ana', 'corresp'}:
                    fehler.append(f'{wid}: Attribute {sorted(w.attrib)}')
            else:
                f_soll, ana_ist, _ = GEBEINE[wid]
                if form != f_soll or frag(w.get('lemmaRef')) != 'lemma_1958' or w.get('pos') != 'NOM' \
                        or frag(w.get('ana')) != ana_ist:
                    fehler.append(f"{wid}: Form {form!r}, lemmaRef {w.get('lemmaRef')}, "
                                  f"pos {w.get('pos')}, ana {w.get('ana')}")
                if set(w.attrib) - {XMLID, 'lemmaRef', 'pos', 'ana', 'corresp'}:
                    fehler.append(f'{wid}: weitere Attribute {sorted(w.attrib)}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand aller {len(JAGEN) + len(GEBEINE)} Tokens in {len(je_datei)} Dateien wie erwartet.')

    # Phase 2: textuell ersetzen
    neu = {}
    for sigle, ids in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        teile = []
        for wid in ids:
            muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
            treffer = muster.findall(text)
            if len(treffer) != 1:
                sys.exit(f'ABBRUCH: {wid} textuell {len(treffer)}x')
            if wid in JAGEN:
                _, _, (l, p, _a, c) = JAGEN[wid]
                tag = (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#{l}" pos="{p}" '
                       f'corresp="variants.xml#{c}">')
                text, n = muster.subn(lambda m, t=tag: t + m.group(1) + '</w>', text)
                teile.append(('460', wid))
            else:
                soll = GEBEINE[wid][2]
                text, n = muster.subn(
                    lambda m, s=soll: setze_ana(m.group(0)[:m.group(0).index('>') + 1], s)
                    + m.group(1) + '</w>', text)
                teile.append(('461', wid))
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        nl = '\r\n' if '\r\n' in m.group(3) else '\n'
        saetze = []
        n460 = sum(1 for t, _ in teile if t == '460')
        n461 = len(teile) - n460
        if n460:
            saetze.append(f'#460 jagen: {n460} Token als Verbform gelesen (KZW 2026-10-15), von '
                          f'lemma_3103 jagât (NOM) auf lemma_3102 jagen (VRB) umgehängt, @ana entfällt.')
        if n461:
            saetze.append(f'#461 gebeine: {n461} Token{"" if n461 == 1 else "s"} nach KZWs Antwort '
                          f'vom 2026-10-15 mit @ana auf ihren Sense gesetzt.')
        eintrag = f'<change when="{DATUM}" who="#editor">{" ".join(saetze)}</change>'
        text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    nl = '\r\n' if '\r\n' in lexikon else '\n'
    m = SENSE_ENDE.search(lexikon)
    einzug = '          '
    bloecke = ''.join(
        f'{einzug}<sense xml:id="{sid}">{nl}{einzug}  <ptr target="concepts.xml#{kid}"/>{nl}{einzug}</sense>{nl}'
        for sid, kid in NEUE_SENSES.items())
    lexikon_neu = lexikon[:m.end()] + bloecke + lexikon[m.end():]

    if APPLY:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        with open(lexpfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(lexikon_neu)
    print(f'{len(JAGEN)} Tokens auf lemma_3102, {len(GEBEINE)} Tokens mit neuem @ana, '
          f'{len(neu)} Dateien, lexicon.xml: {len(NEUE_SENSES)} neue Senses'
          + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
