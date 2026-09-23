#!/usr/bin/env python3
"""
#267: den Marker excerpt-only auf no-print umstellen und den Lizenzsatz
korrigieren; FR3 bekommt das Standard-<availability>.

Zehn Header trugen <availability status="restricted"> mit
<ab type="display" n="excerpt-only"/> und dem Satz "Eine vollstaendige
Lesefassung kann daher nicht angeboten werden." Die Leseansicht zeigt alle
zehn vollstaendig, und das ist gewollt. Entscheidungen von KZW in #267:

  10.09.2026, 11:27  Den Text nicht am Lesen hindern, aber den Buchkauf nicht
                     ersetzen: von diesen Texten keine ausdruckbaren PDFs.
  10.09.2026, 14:35  Neuer Satz: "Eine vollstaendige Fassung der Edition inkl.
                     Apparat kann daher nicht angeboten werden."
  10.09.2026, 14:59  FR3 ist von der Ausnahmeregel befreit (25-Jahres-Frist nach
                     § 76b UrhG-AT abgelaufen).

Daraus, wie in der Zusammenfassung vom 10.09.2026, 15:52 im selben Thread:

  neun Header (HUB1 HUB2 MAI MML MRL MRS MSB1 NEI RLS):
      n="excerpt-only" -> n="no-print", alter Satz -> neuer Satz,
      status="restricted" bleibt
  FR3:
      das ganze <availability> wird das der 657 uebrigen Texte: kein @status,
      kein <ab>, der Standardabsatz

Bedeutung von no-print: docs/TEI-MODEL.md, Abschnitt 2.1.

Kein Build liest <availability>, es aendert sich also kein Index.

Aufruf:
    python scripts/ingest/no-print-267/apply-no-print.py            # Trockenlauf
    python scripts/ingest/no-print-267/apply-no-print.py --apply    # schreiben
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
DATUM = '2026-09-23'

NEUN = ['HUB1', 'HUB2', 'MAI', 'MML', 'MRL', 'MRS', 'MSB1', 'NEI', 'RLS']
FREI = 'FR3'

SATZ_ALT = 'Eine vollständige Lesefassung kann daher nicht angeboten werden.'
SATZ_NEU = 'Eine vollständige Fassung der Edition inkl. Apparat kann daher nicht angeboten werden.'
AB_ALT = '<ab type="display" n="excerpt-only"/>'
AB_NEU = '<ab type="display" n="no-print"/>'

# Der Standardabsatz der uebrigen Texte. Er wird nicht hier abgeschrieben,
# sondern aus dem Korpus gelesen und muss dort in genau einer Fassung stehen.
# Gemessen am 23.09.2026: 650 Header tragen ihn einzeilig, sechs (DUE ER OVG
# SAL WGA WVO) denselben Wortlaut umbrochen und mit abweichendem <licence>-Text,
# WZB gar keinen. Genommen wird die einzeilige Fassung samt ihrem <licence>.
STANDARD_P = re.compile(r'<availability>\s*(<licence [^>]*>[^<\n]*</licence>)\s*(<p>[^<\n]*</p>)\s*</availability>')
BLOCK = re.compile(r'<availability status="restricted">.*?</availability>', re.S)

ANKER = re.compile(r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>', re.S)

EINTRAG_NEUN = ('<change when="%s" who="#editor">#267: Anzeigemarker excerpt-only in no-print '
                'umbenannt und den Lizenzsatz korrigiert, nach den Entscheidungen von KZW vom '
                '10.09.2026. Der Text wird vollständig zum Lesen angeboten, von ihm werden aber '
                'keine ausdruckbaren Fassungen erzeugt.</change>' % DATUM)
EINTRAG_FR3 = ('<change when="%s" who="#editor">#267: Nutzungsbeschränkung aufgehoben, nach der '
               'Entscheidung von KZW vom 10.09.2026 (Schutzfrist der Edition nach § 76b UrhG-AT '
               'abgelaufen). availability entspricht jetzt dem der übrigen Texte.</change>' % DATUM)


def standardabsatz():
    gefunden = {}
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        kopf = pfad.read_text(encoding='utf-8')[:20000]
        m = STANDARD_P.search(kopf)
        if m:
            gefunden.setdefault(m.groups(), []).append(pfad.name)
    if len(gefunden) != 1:
        sys.exit('FEHLER: Standardabsatz nicht eindeutig, %d Fassungen' % len(gefunden))
    (lizenz, absatz), dateien = gefunden.popitem()
    print('Standard-<availability>: %d Header' % len(dateien))
    return lizenz, absatz


def mit_change(text, eintrag, name):
    m = ANKER.search(text)
    if m is None:
        sys.exit('FEHLER: %s: kein <change>-Anker vor </revisionDesc>' % name)
    nl = '\r\n' if '\r\n' in m.group(3) else '\n'
    return text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]


def genau_einmal(text, alt, neu, name):
    n = text.count(alt)
    if n != 1:
        sys.exit('FEHLER: %s: %r steht %d-mal, erwartet 1' % (name, alt, n))
    return text.replace(alt, neu)


def main():
    p = argparse.ArgumentParser(description='#267 no-print')
    p.add_argument('--apply', action='store_true', help='schreiben statt nur pruefen')
    args = p.parse_args()

    # Die Menge der markierten Texte muss genau die erwartete sein.
    markiert = sorted(pf.name.split('.')[0] for pf in TEI_DIR.glob('*.tei.xml')
                      if 'n="excerpt-only"' in pf.read_text(encoding='utf-8'))
    if markiert != sorted(NEUN + [FREI]):
        sys.exit('FEHLER: markiert sind %s, erwartet %s' % (markiert, sorted(NEUN + [FREI])))

    lizenz_std, p_std = standardabsatz()
    print('  %s\n  %s' % (lizenz_std, p_std))

    neu = {}
    for sigle in NEUN:
        pfad = TEI_DIR / (sigle + '.tei.xml')
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        t = genau_einmal(text, AB_ALT, AB_NEU, sigle)
        t = genau_einmal(t, SATZ_ALT, SATZ_NEU, sigle)
        neu[pfad] = mit_change(t, EINTRAG_NEUN, sigle)

    pfad = TEI_DIR / (FREI + '.tei.xml')
    with open(pfad, encoding='utf-8', newline='') as fh:
        text = fh.read()
    bloecke = BLOCK.findall(text)
    if len(bloecke) != 1:
        sys.exit('FEHLER: FR3: %d restricted-Bloecke, erwartet 1' % len(bloecke))
    alt = bloecke[0]
    if AB_ALT not in alt or SATZ_ALT not in alt:
        sys.exit('FEHLER: FR3: Block hat nicht den erwarteten Altzustand')
    # Einrueckung und Zeilenende aus dem Block selbst nehmen.
    nl = '\r\n' if '\r\n' in alt else '\n'
    zeilen = alt.split(nl)
    einr_innen = re.match(r'\s*', zeilen[1]).group(0)
    einr_ende = re.match(r'\s*', zeilen[-1]).group(0)
    lizenz = re.search(r'<licence [^>]*>[^<]*</licence>', alt).group(0)
    if lizenz != lizenz_std:
        sys.exit('FEHLER: FR3: <licence> weicht vom Standard ab: %r' % lizenz)
    ersatz = nl.join(['<availability>', einr_innen + lizenz, einr_innen + p_std,
                      einr_ende + '</availability>'])
    t = genau_einmal(text, alt, ersatz, FREI)
    neu[pfad] = mit_change(t, EINTRAG_FR3, FREI)

    for pfad, text in neu.items():
        print('%s %s' % ('geschrieben' if args.apply else 'Trockenlauf', pfad.name))
        if args.apply:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
    if not args.apply:
        print('\nNichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
