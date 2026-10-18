#!/usr/bin/env python3
"""#461 (Lauf 18.10.2026, D3): Koerperkonzept fuer Fantastische Tiere.

KZW 16.10.2026: "Leg ein neues Koerper-Unterkonzept auch bei Fantastischen
Tieren an, wenn es das im Korpus gibt." Konzept-ID und Bezeichnung von der
Koordination am 18.10.2026 bestaetigt (Checkin D3).

- concepts.xml: neues concept_14101100 "Koerper/Gliedmassen von Fantastischen
  Tieren", broader concept_14100000, einsortiert vor concept_14110000. Muster
  der Geschwister: 14011100 (Saeugetiere), 14021100 (Voegel), 14031100 (Fische).
- lexicon.xml: neuer Sense lemma_1958_sense_119200 mit diesem Konzept, nach
  sense_119199 (hoechste Sense-Nummer vorher 119199, gemessen an lexicon.xml).
- tei/: die vier Belege PL3_312606_7 (Drache), VIR_17403_4, VIR_30008_4
  (Drachenkampf) und TRO_37_4 (Phoenix) bekommen @ana auf den neuen Sense.
  Alle vier im Kontext gelesen, keiner meint etwas anderes als ein Fabeltier.

Nichts wird umgehaengt, sense_3004 bleibt unberuehrt.

SCHREIBWEISE wie apply-460-461-rest.py: textuell, Ist-Zustand vorher
verifiziert (nicht idempotent), Zeilenende erhalten, je Datei ein <change>.

Usage:
    python scripts/ingest/pos-disambig/apply-461-fabeltiere.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-461-fabeltiere.py --apply
"""

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
APPLY = '--apply' in sys.argv
DATUM = '2026-10-18'
KONZEPT = 'concept_14101100'
SENSE = 'lemma_1958_sense_119200'
HOECHSTE_SENSENUMMER = 119199
TOKENS = {  # xml:id -> (Form, Ist-@corresp)
    'PL3_312606_7': ('gebeyn', 'variants.xml#type_310837'),
    'VIR_17403_4': ('gebeine', 'variants.xml#type_6602'),
    'VIR_30008_4': ('gebeine', 'variants.xml#type_6602'),
    'TRO_37_4': ('gebeine', 'variants.xml#type_6602'),
}
ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)
SENSE_ENDE = re.compile(
    r'(<sense xml:id="lemma_1958_sense_119199"[^>]*>.*?</sense>)([ \t]*\r?\n)', re.S)
KONZEPT_VOR = re.compile(r'([ \t]*)<category xml:id="concept_14110000">')


def lies(pfad):
    with open(pfad, encoding='utf-8', newline='') as fh:
        return fh.read()


def schreibe(pfad, text):
    with open(pfad, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def main():
    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    konpfad = ROOT / 'authority-files' / 'concepts.xml'
    lexikon, konzepte = lies(lexpfad), lies(konpfad)
    hoechste = max(int(m) for m in re.findall(r'_sense_(\d+)"', lexikon))
    if hoechste != HOECHSTE_SENSENUMMER:
        sys.exit(f'ABBRUCH: hoechste Sense-Nummer {hoechste}, erwartet {HOECHSTE_SENSENUMMER}')
    if f'xml:id="{SENSE}"' in lexikon or f'xml:id="{KONZEPT}"' in konzepte:
        sys.exit('ABBRUCH: Konzept oder Sense steht schon da')
    if len(SENSE_ENDE.findall(lexikon)) != 1 or len(KONZEPT_VOR.findall(konzepte)) != 1:
        sys.exit('ABBRUCH: Anker in lexicon.xml oder concepts.xml nicht genau einmal')
    if 'xml:id="concept_14100000"' not in konzepte:
        sys.exit('ABBRUCH: concept_14100000 fehlt')

    nl = '\r\n' if '\r\n' in konzepte else '\n'
    m = KONZEPT_VOR.search(konzepte)
    e = m.group(1)
    block = nl.join([
        f'{e}<category xml:id="{KONZEPT}">',
        f'{e}  <catDesc>',
        f'{e}    <term xml:lang="de">Körper/Gliedmaßen von Fantastischen Tieren</term>',
        f'{e}    <term xml:lang="en">Body/Limbs of fantastic animals</term>',
        f'{e}    <ptr type="broader" target="#concept_14100000"/>',
        f'{e}  </catDesc>',
        f'{e}</category>', ''])
    konzepte_neu = konzepte[:m.start()] + block + konzepte[m.start():]

    nl = '\r\n' if '\r\n' in lexikon else '\n'
    m = SENSE_ENDE.search(lexikon)
    einzug = '          '
    sense = (f'{einzug}<sense xml:id="{SENSE}">{nl}{einzug}  <ptr target="concepts.xml#{KONZEPT}"/>{nl}'
             f'{einzug}</sense>{nl}')
    lexikon_neu = lexikon[:m.end()] + sense + lexikon[m.end():]

    je_datei = defaultdict(list)
    for wid in TOKENS:
        je_datei[wid.split('_')[0]].append(wid)
    neu = {}
    for sigle, ids in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        text = lies(pfad)
        for wid in ids:
            form, corresp = TOKENS[wid]
            ist = (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#lemma_1958" pos="NOM" '
                   f'corresp="{corresp}">{form}</w>')
            soll = (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#lemma_1958" pos="NOM" '
                    f'ana="lexicon.xml#{SENSE}" corresp="{corresp}">{form}</w>')
            if text.count(ist) != 1:
                sys.exit(f'ABBRUCH: Ist-Zustand von {wid} weicht ab ({text.count(ist)}x gefunden)')
            text = text.replace(ist, soll)
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        enl = '\r\n' if '\r\n' in m.group(3) else '\n'
        eintrag = (f'<change when="{DATUM}" who="#editor">#461 gebeine: {len(ids)} Token'
                   f'{"" if len(ids) == 1 else "s"} (Fabeltier) mit @ana auf {SENSE} gesetzt, '
                   f'neues Körperkonzept {KONZEPT}.</change>')
        text = text[:m.end(2)] + enl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    if APPLY:
        for pfad, text in neu.items():
            schreibe(pfad, text)
        schreibe(lexpfad, lexikon_neu)
        schreibe(konpfad, konzepte_neu)
    print(f'{len(TOKENS)} Tokens in {len(neu)} Dateien, 1 Konzept, 1 Sense'
          + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
