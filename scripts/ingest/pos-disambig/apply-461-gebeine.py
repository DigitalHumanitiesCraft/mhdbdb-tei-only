#!/usr/bin/env python3
"""#461: gebeine (lemma_1958) bekommt einen Sense fuer Saeugetierknochen.

Freigabe Christian 10.10.2026 im Ticket (Kommentar "Entschieden von @chsteiner
am 10.10.2026"): lemma_1958 bekommt einen neuen Sense mit concept_14011100
(Koerper/Gliedmassen von Saeugetieren), die 21 Saeugetier-Belege erhalten ihn
als @ana, alles andere bleibt. Die Arbeitsliste ist
ingest/review/461-gebeine/belege.tsv: 207 Tokens, je Token am Kontext
eingestuft; "tierisch" sind 27, davon 21 Saeugetiere. Die uebrigen sechs
(Hahn, Fisch, Phoenix, drei Drachen) gehen mit den 9 offenen Belegen als Frage
an KZW und bleiben unberuehrt.

SENSE
-----
Neu: lemma_1958_sense_119196 mit genau einem concept-ptr, concept_14011100.
Hoechste Sense-Nummer am 10.10.2026: 119195 (lemma_3036_sense_119195, #357),
gemessen an lexicon.xml auf origin/main 87c54acbf. Kein @ana am neuen Sense:
die Typlisten dort sind Migrationsbestand, wie bei lemma_9644_sense_119194.

@ana AN TOKENS
--------------
Die 21 Tokens tragen vorher kein @ana (16) oder lemma_1958_sense_3004 (5); beide
Faelle werden zu lemma_1958_sense_119196. @lemmaRef, @pos und @corresp bleiben,
Token-Text, Reihenfolge und xml:id bleiben byte-identisch. Auf variants.xml
wirkt das nicht (kein @corresp geaendert).

SCHREIBWEISE
------------
Wie apply-460-jagat.py: gefunden mit lxml, geschrieben textuell, Ist-Zustand
vorher verifiziert (nicht idempotent), das Zeilenende jeder Datei bleibt
erhalten. Je Datei ein <change> in der revisionDesc.

Usage:
    python scripts/ingest/pos-disambig/apply-461-gebeine.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-461-gebeine.py --apply
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

LISTE = ROOT / 'ingest' / 'review' / '461-gebeine' / 'belege.tsv'
LEMMA = 'lemma_1958'
ALTE_SENSES = (None, 'lemma_1958_sense_3004')
NEUER_SENSE = 'lemma_1958_sense_119196'
KONZEPT = 'concept_14011100'
HOECHSTE_SENSENUMMER = 119195
ERWARTET = {'menschlich': 131, 'Reliquie/Heilige': 40, 'tierisch': 27,
            'übertragen/sonstig': 5, 'unklar': 4}
# Die sechs Tierbelege ohne Saeugetier (Ticket #461, Vorab-Messung 10.10.2026)
KEIN_SAEUGETIER = {'AMI_972_3', 'FLG1_4135180940_2', 'TRO_37_4',
                   'PL3_312606_7', 'VIR_17403_4', 'VIR_30008_4'}
ERWARTET_SAEUGETIERE = 21
ERWARTET_DATEIEN = 15

DATUM = '2026-10-10'
ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)
SENSE_ENDE = re.compile(
    r'(<sense xml:id="lemma_1958_sense_49690"[^>]*>.*?</sense>)([ \t]*\r?\n)', re.S)


def frag(wert):
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def lies_liste():
    with open(LISTE, encoding='utf-8', newline='') as fh:
        zeilen = list(csv.DictReader(fh, delimiter='\t'))
    zaehlung = defaultdict(int)
    for z in zeilen:
        zaehlung[z['Einstufung']] += 1
    if dict(zaehlung) != ERWARTET or len(zeilen) != 207:
        sys.exit(f'ABBRUCH: Einstufungen {dict(zaehlung)}, erwartet {ERWARTET}')
    tiere = {z['xml:id'] for z in zeilen if z['Einstufung'] == 'tierisch'}
    if not KEIN_SAEUGETIER <= tiere:
        sys.exit(f'ABBRUCH: nicht tierisch eingestuft: {sorted(KEIN_SAEUGETIER - tiere)}')
    return [z for z in zeilen
            if z['Einstufung'] == 'tierisch' and z['xml:id'] not in KEIN_SAEUGETIER]


def neues_ana(tag):
    """tag: das oeffnende <w ...>; ana wird gesetzt oder ersetzt, Reihenfolge lemmaRef pos ana corresp."""
    ana = f'ana="lexicon.xml#{NEUER_SENSE}"'
    if re.search(r'\bana="', tag):
        return re.sub(r'\bana="[^"]*"', ana, tag, count=1)
    return re.sub(r'(\bpos="[^"]*")', r'\1 ' + ana, tag, count=1)


def main():
    tiere = lies_liste()
    ids = [z['xml:id'] for z in tiere]
    if len(ids) != ERWARTET_SAEUGETIERE or len(set(ids)) != len(ids):
        sys.exit(f'ABBRUCH: {len(ids)} Saeugetier-Belege, erwartet {ERWARTET_SAEUGETIERE}')
    je_datei = defaultdict(list)
    for z in tiere:
        je_datei[z['Sigle']].append(z)
    if len(je_datei) != ERWARTET_DATEIEN:
        sys.exit(f'ABBRUCH: {len(je_datei)} Dateien, erwartet {ERWARTET_DATEIEN}')

    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    with open(lexpfad, encoding='utf-8', newline='') as fh:
        lexikon = fh.read()
    hoechste = max(int(m) for m in re.findall(r'_sense_(\d+)"', lexikon))
    if hoechste != HOECHSTE_SENSENUMMER:
        sys.exit(f'ABBRUCH: hoechste Sense-Nummer {hoechste}, erwartet {HOECHSTE_SENSENUMMER}')
    if f'xml:id="{NEUER_SENSE}"' in lexikon:
        sys.exit(f'ABBRUCH: {NEUER_SENSE} steht schon in lexicon.xml')
    konzepte = (ROOT / 'authority-files' / 'concepts.xml').read_text(encoding='utf-8')
    if f'xml:id="{KONZEPT}"' not in konzepte:
        sys.exit(f'ABBRUCH: {KONZEPT} fehlt in concepts.xml')
    ms = SENSE_ENDE.findall(lexikon)
    if len(ms) != 1:
        sys.exit(f'ABBRUCH: Sense-Anker in lexicon.xml {len(ms)}x')

    fehler = []
    for sigle, eintraege in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        gefunden = {w.get(XMLID): w for w in etree.parse(str(pfad)).iter(f'{TEI_NS}w')}
        for z in eintraege:
            wid = z['xml:id']
            w = gefunden.get(wid)
            if w is None:
                fehler.append(f'{wid}: nicht gefunden')
                continue
            form = ''.join(w.itertext()).strip()
            if form != z['Form']:
                fehler.append(f"{wid}: Form {form!r}, erwartet {z['Form']!r}")
            if frag(w.get('lemmaRef')) != LEMMA or w.get('pos') != 'NOM':
                fehler.append(f"{wid}: lemmaRef/pos {w.get('lemmaRef')} {w.get('pos')}")
            if frag(w.get('ana')) not in ALTE_SENSES:
                fehler.append(f"{wid}: ana {w.get('ana')}")
            if set(w.attrib) - {XMLID, 'lemmaRef', 'pos', 'ana', 'corresp'}:
                fehler.append(f'{wid}: weitere Attribute {sorted(w.attrib)}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand aller {len(ids)} Tokens in {len(je_datei)} Dateien wie erwartet.')

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
                lambda m: neues_ana(m.group(0)[:m.group(0).index('>') + 1])
                + m.group(1) + '</w>', text)
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        nl = '\r\n' if '\r\n' in m.group(3) else '\n'
        revision = (f'#461 gebeine: {len(eintraege)} Token{"" if len(eintraege) == 1 else "s"} '
                    f'mit Säugetierknochen auf den neuen Sense {NEUER_SENSE} '
                    f'({KONZEPT}) gesetzt.')
        eintrag = f'<change when="{DATUM}" who="#editor">{revision}</change>'
        text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    nl = '\r\n' if '\r\n' in lexikon else '\n'
    m = SENSE_ENDE.search(lexikon)
    einzug = '          '
    sense = (f'{einzug}<sense xml:id="{NEUER_SENSE}">{nl}'
             f'{einzug}  <ptr target="concepts.xml#{KONZEPT}"/>{nl}'
             f'{einzug}</sense>{nl}')
    lexikon_neu = lexikon[:m.end()] + sense + lexikon[m.end():]

    if APPLY:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        with open(lexpfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(lexikon_neu)
    print(f'{len(ids)} Tokens in {len(neu)} Dateien auf {NEUER_SENSE}; lexicon.xml: neuer Sense'
          + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
