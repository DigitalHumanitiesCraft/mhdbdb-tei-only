#!/usr/bin/env python3
"""
Ueberlieferungsluecken von '( caesura )' auf <gap/> migrieren (#252).

Auslassungen der Edition stehen im Korpus als Interpunktion plus Zaesur:

    <l n="32">
      <pc xml:id="FR3_107203020320_0" join="right">(</pc>
      <caesura xml:id="FR3_107203020320_1"/>
      <pc xml:id="FR3_107203020320_2" join="left">)</pc>
    </l>

<caesura/> bezeichnet in TEI einen metrischen Einschnitt, keine Textluecke;
dafuer gibt es <gap/>. Ausserdem ist die Luecke so nicht auffindbar: man muesste
ein dreiteiliges Serialisierungsmuster suchen statt eines Elements.

KZW hat am 29.07.2026 entschieden, dass echte Auslassungen <gap/> werden und
<caesura/> der bewussten Zaesur im Vers bleibt, und am 10.09.2026 bestaetigt,
dass die Verallgemeinerung von den 324 an der Linecode-Vorlage geprueften
Faellen auf die ganze Menge traegt.

ZIELMENGE, gemessen am 2026-09-10:

    <l> mit <caesura/> und ohne <w>          1.144
      A  gar kein sichtbarer Text              972   ->  wird migriert
      B  sichtbar genau "( )"                  122   ->  wird migriert
      B' sichtbar andere Zeichen                38   ->  bleibt
      C  sichtbarer Text mit Buchstaben         12   ->  bleibt
                                              ----
                                  migriert    1.094  in 103 Dateien

C ist der Grund, warum dieses Skript nicht nach "leer" fragt, sondern nach
Buchstaben. Die 12 liegen in 8 Dateien; darunter steht FDS "(folgen Lied 34
bis Lied 37)", eine Herausgeberangabe, und in EIL, GWTK und FR1 echter, nur
unlemmatisierter Wortlaut. Eine Migration nach dem Kriterium "kein <w>"
haette den geloescht.

B' bleibt, weil dort Zeichen stehen, die nicht Teil des Markers sind. Die 38
zerfallen in vier Gruppen:

    22  nur Redezeichen (< oder >, eines davon mit Punkt).
         In GWTK und BRF sind das Anfuehrungszeichen, keine Klammern.
     5  nur ein Komma oder ein Doppelpunkt.
     8  eine einzelne Klammer. Sie bilden vier Paare ueber mehrere Verse:
         SJH lg179 n=6/7, SUS lg61 n=6/10, SUS lg127 n=7/8, SVW lg6 n=6/7.
         Bei SUS lg61 liegen drei jetzt migrierte Zeilen dazwischen.
     3  der vollstaendige Marker plus EIN Zeichen: NEIC lg3 n=14 "< ( )",
         NEIR lg5 n=6 "( ) ," und SJH lg168 n=13 "( ) !". Das sind die
         Kandidaten fuer eine Korrektur von Hand.

Das Skript druckt alle 38 mit ihrem Inhalt aus, damit sie nachgesehen werden
koennen statt nur gezaehlt zu sein.

WAS DIESES SKRIPT NICHT ANFASST, alles am 2026-09-10 nach dem Lauf gemessen:

  838 in 17 Dateien  "( caesura )" INNERHALB einer Zeile zwischen Woertern
                     (FR1 518, FR3 176, MSG 56, BRW 38, NEIC 22, NEIR 10,
                     NEIM 5, SKL 3, MML 2, dazu acht Dateien mit je einem)
    5 in 3 Dateien   dasselbe Muster in <p>-Prosa (HUB2 1, PL1 1, SUB1 3)
    2 in MUG         <l><hi><caesura/></hi></l>, also die Zaesur nicht als
                     direktes Kind. Das Skript sieht sie deshalb nicht;
                     ob das <hi> mitentfernt werden soll, ist eine
                     Entscheidung und keine Skriptkorrektur

Sie sind vermutlich dieselbe Sache, aber das ist eine philologische Aussage
ueber Stellen mit Text ringsum und keine mechanische. Offen in #252.

WARUM TEXTUELL UND NICHT UEBER LXML: ein lxml-Round-Trip formatiert die ganze
Datei neu und macht aus 1.094 Aenderungen einen Diff ueber 103 Dateien. Die
Zielmenge wird deshalb mit lxml BESTIMMT und mit einer Regex GESCHRIEBEN, und
vor jedem Schreiben wird der Altzustand geprueft (Muster wie in
scripts/ingest/pos-disambig/apply-homograph.py).

Die 1.339 xml:id in den betroffenen <l> fallen dabei weg. Das ist geprueft und
nicht angenommen: keine davon kommt in data/corpus-index.json.gz, in
data/authority-index.json.gz oder in einer der 2.742 Dateien unter api/ vor.
<gap/> traegt im Schema kein xml:id (schema/mhdbdb.rnc), es wird also auch
keines gesetzt.

KEIN INDEX-REBUILD NOETIG: die betroffenen <l> tragen kein <w>, gehen also
weder in die Positionszaehlung noch in lineStarts/lineEnds ein. Der Docstring
von build-corpus-index.py sagt es selbst: "Same length as the number of <l>
elements with at least one indexed word."

Aufruf:
    python scripts/migrate-caesura-to-gap-252.py            # Trockenlauf
    python scripts/migrate-caesura-to-gap-252.py --apply    # schreiben
"""

import argparse
import io
import re
import sys
from collections import Counter
from pathlib import Path

import lxml.etree as ET

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parent.parent
TEI_DIR = REPO / 'tei'
T = '{http://www.tei-c.org/ns/1.0}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

# Buchstaben einschliesslich der MHG-Sonderzeichen. Wer hier nur [A-Za-z]
# prueft, uebersieht 'ʒ' und die Umlaute und migriert Text weg.
BUCHSTABE = re.compile(r'[A-Za-zÀ-ÿʒ]')

# Der Auslassungsmarker der Vorlage ist die runde Klammer um die Zaesur,
# entstanden aus %(...)% und Verwandten. Sichtbar bleibt davon im TEI genau
# "()" und sonst nichts.
#
# Die erste Fassung dieses Skripts prueft hier auf [()<>[]] und hat damit 27
# <pc> geloescht, die nicht zum Marker gehoerten, darunter 24 Redezeichen.
# In GWTK und BRF sind < und > Anfuehrungszeichen (GWTK traegt 970 bzw. 963
# davon im ganzen Text): GWTK n="35" oeffnet die Rede "< nun wol uff , helede",
# n="36" war "|| >", also Luecke plus Redeschluss, und waere zu einem blossen
# <gap/> geworden. Die Rede haette nie geschlossen.
#
# Die Regel dahinter ist dieselbe, die B' stehen laesst: ein Zeichen, das
# nicht Teil des Markers ist, gehoert zum Text und wird nicht mitentfernt.
# Gefunden im lokalen Review, Runde 1.
NUR_RUNDE_KLAMMERN = re.compile(r'^\(\s*\)$')


def zielmenge():
    """Die zu migrierenden <l> bestimmen, je Datei und mit ihrer Anker-Id.

    Anker ist die erste xml:id im Inneren des <l>. Sie ist innerhalb der Datei
    eindeutig und ueberlebt, anders als die Position, jede Umsortierung.
    """
    treffer = {}
    ausgelassen = Counter()
    uebrig = []
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        try:
            baum = ET.parse(str(pfad))
        except ET.XMLSyntaxError as fehler:
            sys.exit('FEHLER: %s laesst sich nicht parsen: %s' % (pfad.name, fehler))
        for zeile in baum.iter(T + 'l'):
            if zeile.find(T + 'caesura') is None:
                continue
            if zeile.find(T + 'w') is not None:
                continue
            sichtbar = ''.join(zeile.itertext()).strip()
            if sichtbar and BUCHSTABE.search(sichtbar):
                ausgelassen['C: sichtbarer Text mit Buchstaben'] += 1
                continue
            if sichtbar and not NUR_RUNDE_KLAMMERN.match(' '.join(sichtbar.split())):
                ausgelassen["B': sichtbare Zeichen, die nicht der Marker sind"] += 1
                uebrig.append((pfad.name, zeile.get('n'), sichtbar))
                continue
            anker = next((e.get(XML_ID) for e in zeile.iter()
                          if e is not zeile and e.get(XML_ID)), None)
            if anker is None:
                sys.exit('FEHLER: %s: <l n=%r> ohne xml:id im Inneren, kein Anker'
                         % (pfad.name, zeile.get('n')))
            treffer.setdefault(pfad.name, []).append(anker)
    return treffer, ausgelassen, uebrig


def bloecke(text):
    """Alle <l>...</l> der Datei als (start, ende, innen) liefern."""
    for m in re.finditer(r'<l\b[^>]*>(.*?)</l>', text, re.DOTALL):
        yield m.start(), m.end(), m.group(1), m.group(0)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('--apply', action='store_true',
                   help='Aenderungen schreiben statt nur zaehlen')
    args = p.parse_args()

    treffer, ausgelassen, uebrig = zielmenge()
    gesamt = sum(len(v) for v in treffer.values())
    print('Zielmenge: %d Stellen in %d Texten' % (gesamt, len(treffer)))
    for grund, n in sorted(ausgelassen.items()):
        print('  bewusst ausgelassen, %s: %d' % (grund, n))
    if uebrig:
        print('\n  Die ausgelassenen Zeilen mit sichtbaren Zeichen, zum Nachsehen:')
        for name, nr, sichtbar in uebrig:
            print('    %-10s n=%-8s %r' % (name, nr, ' '.join(sichtbar.split())))
    print()

    geschrieben = 0
    dateien = 0
    for name in sorted(treffer):
        pfad = TEI_DIR / name
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        offen = set(treffer[name])
        neu = []
        letztes = 0
        for start, ende, innen, ganz in bloecke(text):
            anker = re.search(r'xml:id="([^"]+)"', innen)
            if anker is None or anker.group(1) not in offen:
                continue
            # Altzustand pruefen, bevor geschrieben wird.
            if '<w ' in innen or '<w>' in innen:
                sys.exit('FEHLER: %s: Block um %s traegt ein <w>'
                         % (name, anker.group(1)))
            if '<caesura' not in innen:
                sys.exit('FEHLER: %s: Block um %s traegt keine <caesura/>'
                         % (name, anker.group(1)))
            offen.discard(anker.group(1))
            kopf = re.match(r'<l\b[^>]*>', ganz).group(0)
            neu.append(text[letztes:start])
            neu.append(kopf + '<gap reason="lost"/></l>')
            letztes = ende
            geschrieben += 1
        if offen:
            sys.exit('FEHLER: %s: %d Anker nicht im Text gefunden: %s'
                     % (name, len(offen), sorted(offen)[:3]))
        neu.append(text[letztes:])
        ergebnis = ''.join(neu)
        if ergebnis != text:
            dateien += 1
            if args.apply:
                with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(ergebnis)

    print('%s: %d Stellen in %d Dateien'
          % ('Geschrieben' if args.apply else 'Trockenlauf', geschrieben, dateien))
    if geschrieben != gesamt:
        sys.exit('FEHLER: %d Stellen bestimmt, %d geschrieben' % (gesamt, geschrieben))
    if not args.apply:
        print('\nNichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
