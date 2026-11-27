#!/usr/bin/env python3
"""#461 (2026-11-27): die 12 lebenden Gebeine von sense_3004 auf sense_49690.

Die 12 Belege mit Einstufung "lebend" (ohne Fragezeichen) in
ingest/review/461-gebeine/sense3004-lebend.tsv meinen einen lebenden
menschlichen Koerper. Sie wechseln von lemma_1958_sense_3004 (Mensch + Tod)
nach lemma_1958_sense_49690 (nur Mensch). Die 3 "lebend?" (HTR_214570_5,
JEW_2330900000_1, ROL_3841_3) bleiben unveraendert.

Grundlage: KZWs Antwort in #461, Entscheidung chsteiner 2026-11-27.

Aenderung: nur @ana an 12 Tokens in 8 Dateien; lemmaRef, pos, corresp und
Wortlaut bleiben. Dazu je Datei ein <change> und die Spalten Entscheidung und
Quelle in belege.tsv.

SCHREIBWEISE wie apply-461-ochsen.py: textuell, Ist-Zustand vorher verifiziert
(nicht idempotent), Zeilenende erhalten. Die Tokenliste wird gegen die TSV
geprueft und bei Abweichung abgebrochen.

Usage:
    python scripts/ingest/pos-disambig/apply-461-lebend.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-461-lebend.py --apply
"""

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
APPLY = '--apply' in sys.argv
DATUM = '2026-11-27'
VORHER = 'lemma_1958_sense_3004'
SENSE = 'lemma_1958_sense_49690'
TOKENS = ['ADP_4117900_4', 'ADP_4122600_12', 'HTR_78950_6', 'HTR_207990_5',
          'JEW_393000000_5', 'JEW_1002900000_8', 'JEW_1270500000_4',
          'OVW_1021020260_2', 'RSP_1926_5', 'SLG_8770_5', 'TRY_11371_4',
          'WL_227_3']
ENTSCHEIDUNG = (f'{SENSE} (lebender menschlicher Koerper); vorher {VORHER}, '
                f'verliert damit concept_21030000 und concept_21104000')
QUELLE = 'KZW und chsteiner 2026-11-27, Kommentare in #461'
ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def lies(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return fh.read()


def schreibe(pfad, text):
    with open(pfad, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def main():
    lexikon = lies(ROOT / 'authority-files' / 'lexicon.xml')
    for s in (VORHER, SENSE):
        if lexikon.count(f'xml:id="{s}"') != 1:
            sys.exit(f'ABBRUCH: {s} steht nicht genau einmal in lexicon.xml')

    tsvdir = ROOT / 'ingest' / 'review' / '461-gebeine'
    # Tokenliste gegen die Einstufungstabelle pruefen
    lebend = []
    for zeile in lies(tsvdir / 'sense3004-lebend.tsv').splitlines()[1:]:
        f = zeile.split('\t')
        if f[4] == 'lebend':
            lebend.append(f[0])
    if sorted(lebend) != sorted(TOKENS):
        sys.exit(f'ABBRUCH: Tokenliste weicht von der TSV ab: {sorted(set(lebend) ^ set(TOKENS))}')

    nach_datei = defaultdict(list)
    for wid in TOKENS:
        nach_datei[wid.split('_')[0]].append(wid)

    neu = {}
    for sigle, ids in nach_datei.items():
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        text = lies(pfad)
        for wid in ids:
            pat = re.compile(
                r'(<w xml:id="' + re.escape(wid) + r'" lemmaRef="lexicon\.xml#lemma_1958" pos="NOM" '
                r'ana="lexicon\.xml#)' + re.escape(VORHER) + r'(" corresp="variants\.xml#type_\d+">[^<]*</w>)')
            treffer = pat.findall(text)
            if len(treffer) != 1:
                sys.exit(f'ABBRUCH: Ist-Zustand von {wid} weicht ab ({len(treffer)}x gefunden)')
            text = pat.sub(lambda m: m.group(1) + SENSE + m.group(2), text)
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        enl = '\r\n' if '\r\n' in m.group(3) else '\n'
        eintrag = (f'<change when="{DATUM}" who="#editor">#461 gebeine: {len(ids)} Tokens '
                   f'(lebender menschlicher Körper) von {VORHER} auf {SENSE} umgehängt.</change>')
        text = text[:m.end(2)] + enl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    tsvpfad = tsvdir / 'belege.tsv'
    tsv = lies(tsvpfad)
    tnl = '\r\n' if '\r\n' in tsv else '\n'
    zeilen = tsv.split(tnl)
    kopf = zeilen[0].split('\t')
    i_ent, i_que = kopf.index('Entscheidung'), kopf.index('Quelle')
    getroffen = 0
    for n, zeile in enumerate(zeilen):
        felder = zeile.split('\t')
        if felder[0] in TOKENS:
            if len(felder) != len(kopf) or felder[i_ent] or felder[i_que]:
                sys.exit(f'ABBRUCH: belege.tsv-Zeile {felder[0]} nicht leer oder falsch breit')
            felder[i_ent], felder[i_que] = ENTSCHEIDUNG, QUELLE
            zeilen[n] = '\t'.join(felder)
            getroffen += 1
    if getroffen != len(TOKENS):
        sys.exit(f'ABBRUCH: {getroffen} von {len(TOKENS)} Zeilen in belege.tsv gefunden')

    if APPLY:
        for pfad, text in neu.items():
            schreibe(pfad, text)
        schreibe(tsvpfad, tnl.join(zeilen))
    print(f'{len(TOKENS)} Tokens in {len(neu)} Dateien, {getroffen} Zeilen in belege.tsv'
          + ('' if APPLY else '  [Trockenlauf]'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
