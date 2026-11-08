#!/usr/bin/env python3
"""#461 (2026-11-08): die zwei Ochsen-Belege in JEW auf den Saeugetier-Sense.

JEW_556900000_3 und JEW_557800000_0 meinen die mageren Ochsen in Pharaos
Traum, wie JEW_566800000_5, der seit dem 2026-10-10 auf
lemma_1958_sense_119196 (concept_14011100, Saeugetiere) steht. Die Tabelle
vom 10.10. fuehrte die beiden als "menschlich"; berichtigt im Nachtrag vom
18.10. in ingest/review/461-gebeine/README.md, dort aber nicht umgehaengt.

Grundlage: chsteiner 2026-10-10 in #461, die Saeugetier-Belege bekommen den
neuen Sense; chsteiner 2026-11-08, die beiden Ochsen jetzt umhaengen. Die
Frage nach einem eigenen Sense fuer die lebenden Gebeine (12 plus 3 mit
Zweifel) bleibt bei KZW und wird hier nicht beruehrt.

Aenderung: nur @ana an zwei Tokens, @lemmaRef und @corresp bleiben. Dazu ein
<change> in JEW und die Spalten Entscheidung und Quelle in belege.tsv.

SCHREIBWEISE wie apply-461-fabeltiere.py: textuell, Ist-Zustand vorher
verifiziert (nicht idempotent), Zeilenende erhalten.

Usage:
    python scripts/ingest/pos-disambig/apply-461-ochsen.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-461-ochsen.py --apply
"""

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
APPLY = '--apply' in sys.argv
DATUM = '2026-11-08'
VORHER = 'lemma_1958_sense_3004'
SENSE = 'lemma_1958_sense_119196'
VORBILD = 'JEW_566800000_5'
TOKENS = ['JEW_556900000_3', 'JEW_557800000_0']
CORRESP = 'variants.xml#type_6601'
FORM = 'gebein'
ENTSCHEIDUNG = (f'{SENSE} (Ochsen in Pharaos Traum, wie {VORBILD}); '
                f'vorher {VORHER}, verliert damit concept_21030000 und concept_21104000')
QUELLE = 'chsteiner 2026-10-10 und 2026-11-08, Kommentare in #461'
ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def lies(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return fh.read()


def schreibe(pfad, text):
    with open(pfad, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def w(wid, sense):
    return (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#lemma_1958" pos="NOM" '
            f'ana="lexicon.xml#{sense}" corresp="{CORRESP}">{FORM}</w>')


def main():
    lexikon = lies(ROOT / 'authority-files' / 'lexicon.xml')
    if lexikon.count(f'xml:id="{SENSE}"') != 1:
        sys.exit(f'ABBRUCH: {SENSE} steht nicht genau einmal in lexicon.xml')

    pfad = ROOT / 'tei' / 'JEW.tei.xml'
    text = lies(pfad)
    if text.count(w(VORBILD, SENSE)) != 1:
        sys.exit(f'ABBRUCH: Vorbild {VORBILD} steht nicht wie erwartet auf {SENSE}')
    for wid in TOKENS:
        ist, soll = w(wid, VORHER), w(wid, SENSE)
        if text.count(ist) != 1:
            sys.exit(f'ABBRUCH: Ist-Zustand von {wid} weicht ab ({text.count(ist)}x gefunden)')
        text = text.replace(ist, soll)
    m = ANKER.search(text)
    if not m:
        sys.exit('ABBRUCH: kein revisionDesc-Anker in JEW')
    enl = '\r\n' if '\r\n' in m.group(3) else '\n'
    eintrag = (f'<change when="{DATUM}" who="#editor">#461 gebeine: 2 Tokens (die Ochsen '
               f'in Pharaos Traum, wie {VORBILD}) von {VORHER} auf {SENSE} umgehängt.</change>')
    text = text[:m.end(2)] + enl + m.group(1) + eintrag + text[m.end(2):]

    tsvpfad = ROOT / 'ingest' / 'review' / '461-gebeine' / 'belege.tsv'
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
        schreibe(pfad, text)
        schreibe(tsvpfad, tnl.join(zeilen))
    print(f'{len(TOKENS)} Tokens in 1 Datei, {getroffen} Zeilen in belege.tsv'
          + ('' if APPLY else '  [Trockenlauf]'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
