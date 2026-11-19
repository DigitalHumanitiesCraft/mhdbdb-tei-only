#!/usr/bin/env python3
"""
#262: den toten ETC-Link in den TEI-Headern durch das Textarchiv des
Mittelhochdeutschen Woerterbuchs ersetzen.

Festlegung von chsteiner am 18.11.2026 in #262 (Kommentar 6987321260): der
Link <ref target="http://etext.lib.virginia.edu/german/mhg"/> wird durch
https://mhdwb-online.de/textarchiv.php ersetzt. Anlass: Ute Recker-Hamm
(MWB Trier) hatte angemerkt, dass der ETC-Link nicht mehr funktioniert; die
MHGTA-Website ist im Textarchiv auf mhdwb-online.de aufgegangen.

Was ersetzt wird und was nicht (gemessen am 19.11.2026):

  73 Dateien enthalten etext.lib.virginia.edu, in zwei Formen:
  - 71 Dateien tragen genau einmal das leere <ref target="..."/> im
    bibl type="digitalIntermediary". Das wird ersetzt.
  - 5 Dateien (BDK BGM BRZ DL1 DL2) nennen die URL als Text am Ende der
    <note> im biblStruct, drei davon (BGM BRZ DL2) zusaetzlich mit <ref>.
    Diese <note> wird NICHT angefasst: sie ist der Bibliographievermerk aus
    Zotero (Kette Zotero -> works.xml -> TEI-Header, works.xml traegt
    dieselben 5 Zeilen), und sync_tei_headers.py --works --check haelt den
    Header-biblStruct gegen works.xml. Eine Aenderung nur hier waere rot,
    eine in works.xml wuerde beim naechsten Zotero-Lauf zurueckgeschrieben.
    Zudem zitiert der Vermerk die Quelle mit ihrem damaligen Wortlaut.

Je geaenderte Datei ein <change> in der revisionDesc, wie bei #267.

Kein Build liest den <ref> im Header (belegt im PR-Body mit grep ueber
scripts/ und assets/), es aendert sich also kein Index.

Aufruf:
    python scripts/ingest/etc-link-262/replace-etc-link.py            # Trockenlauf
    python scripts/ingest/etc-link-262/replace-etc-link.py --apply    # schreiben
"""

import argparse
import io
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / 'tei'
DATUM = '2026-11-19'

ALT = '<ref target="http://etext.lib.virginia.edu/german/mhg"/>'
NEU = '<ref target="https://mhdwb-online.de/textarchiv.php"/>'
HOST = 'etext.lib.virginia.edu'

# Die URL als Text in der Zotero-<note>; bleibt stehen (siehe Docstring).
NOTE_FORM = 'http://etext.lib.virginia.edu/german/mhg</note>'
NOTE_DATEIEN = ['BDK', 'BGM', 'BRZ', 'DL1', 'DL2']

ERWARTET_REF = 71
ERWARTET_HOST = 73

ANKER = re.compile(r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>', re.S)

EINTRAG = ('<change when="%s" who="#editor">#262: Toten Link des Electronic Text Center '
           '(etext.lib.virginia.edu) in der elektronischen Zwischenstufe durch das Textarchiv '
           'des Mittelhochdeutschen Wörterbuchs (mhdwb-online.de) ersetzt, in dem das MHGTA '
           'aufgegangen ist.</change>' % DATUM)


def mit_change(text, name):
    m = ANKER.search(text)
    if m is None:
        sys.exit('FEHLER: %s: kein <change>-Anker vor </revisionDesc>' % name)
    nl = '\r\n' if '\r\n' in m.group(3) else '\n'
    return text[:m.end(2)] + nl + m.group(1) + EINTRAG + text[m.end(2):]


def main():
    p = argparse.ArgumentParser(description='#262 ETC-Link')
    p.add_argument('--apply', action='store_true', help='schreiben statt nur pruefen')
    args = p.parse_args()

    mit_host, mit_ref, nur_note = [], [], []
    neu = {}
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        if HOST not in text:
            continue
        sigle = pfad.name.split('.')[0]
        mit_host.append(sigle)
        n_ref = text.count(ALT)
        n_note = text.count(NOTE_FORM)
        n_host = text.count(HOST)
        # Jede Fundstelle des Hosts muss einer der beiden bekannten Formen gehoeren.
        if n_ref + n_note != n_host:
            sys.exit('FEHLER: %s: %d Treffer fuer %s, davon nur %d bekannt (ref %d, note %d)'
                     % (sigle, n_host, HOST, n_ref + n_note, n_ref, n_note))
        if n_ref > 1:
            sys.exit('FEHLER: %s: <ref> steht %d-mal, erwartet hoechstens 1' % (sigle, n_ref))
        if n_ref == 0:
            nur_note.append(sigle)
            print('%-6s ref 0  note %d  (nicht angefasst)' % (sigle, n_note))
            continue
        mit_ref.append(sigle)
        t = text.replace(ALT, NEU)
        neu[pfad] = mit_change(t, sigle)
        print('%-6s ref %d  note %d' % (sigle, n_ref, n_note))

    if len(mit_host) != ERWARTET_HOST:
        sys.exit('FEHLER: %d Dateien mit %s, erwartet %d' % (len(mit_host), HOST, ERWARTET_HOST))
    if len(mit_ref) != ERWARTET_REF:
        sys.exit('FEHLER: %d Dateien mit <ref>, erwartet %d' % (len(mit_ref), ERWARTET_REF))
    note_ist = sorted(s for s in mit_host if NOTE_FORM in (TEI_DIR / (s + '.tei.xml')).read_text(encoding='utf-8'))
    if note_ist != NOTE_DATEIEN:
        sys.exit('FEHLER: <note>-Form in %s, erwartet %s' % (note_ist, NOTE_DATEIEN))
    if not neu:
        sys.exit('FEHLER: null Treffer')

    print('\nDateien mit %s: %d (%d mit <ref> + %d nur <note>: %s)'
          % (HOST, len(mit_host), len(mit_ref), len(nur_note), ' '.join(nur_note)))
    print('<note>-Form, nicht angefasst: %d Dateien (%s)' % (len(note_ist), ' '.join(note_ist)))

    for pfad, text in neu.items():
        if args.apply:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
    print('%s: %d Dateien' % ('geschrieben' if args.apply else 'Trockenlauf, wuerde schreiben', len(neu)))
    if not args.apply:
        print('Nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
