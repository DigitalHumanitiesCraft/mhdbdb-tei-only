#!/usr/bin/env python3
"""
Zweiter Durchgang #252: '( caesura )' INNERHALB eines Blocks mit Woertern
wird <gap reason="lost"/>.

Der erste Durchgang (scripts/migrate-caesura-to-gap-252.py, PR #426) hat nur
Verse ohne ein einziges <w> migriert und die Stellen zwischen Woertern
ausdruecklich offen gelassen. KZW hat sie am 22.09.2026 in #252 freigegeben:

    "Ja, das eingeklammerte Auslassungsmuster bezeichnet auch innerhalb einer
    Textzeile eine Luecke ... Ich trage die Verallgemeinerung auf die
    genannten 846 Faelle mit. Bitte nur dieses Muster ersetzen und
    umliegenden Text sowie Satz- und Redezeichen erhalten. Die fuenf
    Komma-/Doppelpunktfaelle sind damit nicht freigegeben."

ZAEHLREGEL, woertlich aus dem Kommentar vom 14.09.2026 in #252: ein Treffer
ist ein <caesura/>, dessen unmittelbares Geschwisterelement links ein <pc> mit
dem Text '(' und rechts ein <pc> mit dem Text ')' ist, und in dessen
umgebendem Blockelement mindestens ein <w> steht, auf beliebiger Tiefe.

Freigegeben sind genau 846. Weicht die Zaehlung ab, bricht das Skript ab,
statt eine andere Menge zu schreiben: die Freigabe gilt der Menge, nicht der
Regel.

Die fuenf Komma-/Doppelpunktfaelle (GWTK V. 2723, 8380, 20191, 24998, RVBR
V. 17224) tragen keine Klammer und fallen schon durch die Regel heraus. Sie
bleiben offen in #252.

GESCHRIEBEN wird textuell (lxml bestimmt, Regex schreibt, wie im ersten
Durchgang): ersetzt wird genau die Folge

    <pc xml:id="A" join="right">(</pc>WS<caesura xml:id="B"/>WS<pc xml:id="C" join="left">)</pc>

durch <gap reason="lost"/>. Der Leerraum davor und danach bleibt, damit auch
das Zeilenende der Datei (LF oder CRLF) unberuehrt bleibt. Die drei xml:id
fallen weg; <gap/> traegt im Schema keine. Vor dem Schreiben wird geprueft,
dass keine davon in data/ oder api/ vorkommt.

KEIN <w> wird angefasst, also keine Position, keine Zeilengrenze mit Wort,
kein Index. Ob trotzdem ein Bump faellig ist, entscheidet
scripts/audit/check-index-version-bump.py, nicht dieses Skript.

Je Datei ein <change> in der revisionDesc.

Aufruf:
    python scripts/ingest/gap-252/migrate-inline-gap.py            # Trockenlauf
    python scripts/ingest/gap-252/migrate-inline-gap.py --apply    # schreiben
"""

import argparse
import gzip
import io
import re
import sys
from collections import Counter
from pathlib import Path

import lxml.etree as ET

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / 'tei'
T = '{http://www.tei-c.org/ns/1.0}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
BLOCK = {T + 'l', T + 'p', T + 'ab', T + 'head', T + 'item', T + 'seg'}

FREIGEGEBEN = 846
DATUM = '2026-09-23'

ANKER = re.compile(r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>', re.S)


def ist_pc(e, zeichen):
    return e is not None and e.tag == T + 'pc' and (e.text or '').strip() == zeichen


def zielmenge():
    """Je Datei die Liste der (id_links, id_caesura, id_rechts)."""
    treffer = {}
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        baum = ET.parse(str(pfad))
        for c in baum.iter(T + 'caesura'):
            links, rechts = c.getprevious(), c.getnext()
            if not (ist_pc(links, '(') and ist_pc(rechts, ')')):
                continue
            block = c.getparent()
            while block is not None and block.tag not in BLOCK:
                block = block.getparent()
            if block is None:
                sys.exit('FEHLER: %s: Muster um %s ausserhalb jedes Blockelements'
                         % (pfad.name, c.get(XML_ID)))
            if block.find('.//' + T + 'w') is None:
                continue
            ids = (links.get(XML_ID), c.get(XML_ID), rechts.get(XML_ID))
            if None in ids:
                sys.exit('FEHLER: %s: Muster ohne vollstaendige xml:id: %r' % (pfad.name, ids))
            treffer.setdefault(pfad.name, []).append(ids)
    return treffer


def ids_nirgends_referenziert(alle_ids):
    """Keine der wegfallenden xml:id darf in data/ oder api/ stehen."""
    muster = re.compile('|'.join(re.escape(i) for i in sorted(alle_ids, key=len, reverse=True)))
    gelesen = 0
    for pfad in sorted((REPO / 'data').glob('*.json.gz')):
        with gzip.open(pfad, 'rt', encoding='utf-8') as fh:
            inhalt = fh.read()
        gelesen += 1
        m = muster.search(inhalt)
        if m:
            sys.exit('FEHLER: %s referenziert %s' % (pfad.name, m.group(0)))
    for pfad in sorted((REPO / 'api').rglob('*.json')):
        inhalt = pfad.read_text(encoding='utf-8')
        gelesen += 1
        m = muster.search(inhalt)
        if m:
            sys.exit('FEHLER: %s referenziert %s' % (pfad.relative_to(REPO), m.group(0)))
    return gelesen


def eintrag(n):
    return ('<change when="%s" who="#editor">#252 zweiter Durchgang: %d %s des '
            'Auslassungsmusters ( caesura ) innerhalb einer Zeile mit Wortlaut auf '
            '&lt;gap reason="lost"/&gt; migriert, nach der Freigabe von KZW vom '
            '22.09.2026. Nur das Muster ersetzt, umliegender Text sowie Satz- und '
            'Redezeichen unverändert.</change>'
            % (DATUM, n, 'Stelle' if n == 1 else 'Stellen'))


def main():
    p = argparse.ArgumentParser(description='#252 zweiter Durchgang')
    p.add_argument('--apply', action='store_true', help='schreiben statt nur zaehlen')
    args = p.parse_args()

    treffer = zielmenge()
    gesamt = sum(len(v) for v in treffer.values())
    je = Counter({k.split('.')[0]: len(v) for k, v in treffer.items()})
    print('Zielmenge: %d Stellen in %d Dateien' % (gesamt, len(treffer)))
    print('  ' + ', '.join('%s %d' % kv for kv in je.most_common()))
    if gesamt != FREIGEGEBEN:
        sys.exit('FEHLER: %d gezaehlt, freigegeben sind %d. Nichts geschrieben.'
                 % (gesamt, FREIGEGEBEN))

    alle_ids = {i for v in treffer.values() for t in v for i in t}
    gelesen = ids_nirgends_referenziert(alle_ids)
    print('Wegfallende xml:id: %d, in keiner von %d Dateien unter data/ und api/ referenziert'
          % (len(alle_ids), gelesen))

    geschrieben = 0
    for name in sorted(treffer):
        pfad = TEI_DIR / name
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        neu = text
        for links, mitte, rechts in treffer[name]:
            folge = re.compile(
                r'<pc xml:id="%s" join="right">\(</pc>\s*<caesura xml:id="%s"/>\s*'
                r'<pc xml:id="%s" join="left">\)</pc>'
                % (re.escape(links), re.escape(mitte), re.escape(rechts)))
            neu, n = folge.subn('<gap reason="lost"/>', neu)
            if n != 1:
                sys.exit('FEHLER: %s: Folge um %s %d-mal gefunden, erwartet 1' % (name, mitte, n))
            geschrieben += 1
        m = ANKER.search(neu)
        if m is None:
            sys.exit('FEHLER: %s: kein <change>-Anker vor </revisionDesc>' % name)
        nl = '\r\n' if '\r\n' in m.group(3) else '\n'
        neu = neu[:m.end(2)] + nl + m.group(1) + eintrag(len(treffer[name])) + neu[m.end(2):]
        if args.apply:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(neu)

    print('%s: %d Stellen in %d Dateien, je Datei ein <change>'
          % ('Geschrieben' if args.apply else 'Trockenlauf', geschrieben, len(treffer)))
    if geschrieben != FREIGEGEBEN:
        sys.exit('FEHLER: %d geschrieben, freigegeben %d' % (geschrieben, FREIGEGEBEN))
    if not args.apply:
        print('\nNichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
