#!/usr/bin/env python3
"""#193 Baustein 3, Vorpruefung: treffen Boreks Belegstellen unsere Verse?

Das ist die Frage, an der das ganze Feature haengt, und sie ist vor jeder
UI-Entscheidung zu beantworten. `arthurianHorses.xml` (TUdatalib 3695, CC0)
zitiert 346 Verse aus fuenf Werken. Alle fuenf liegen im Korpus.

## Die Zaehlweisen

Unsere `<l>` tragen KEIN `xml:id`, nur ein fortlaufendes `@n`. Die zitierbare
Stellenangabe steckt in den `xml:id` der WOERTER, und zwar in drei Varianten:

    WH, PZ   Dreissigerzaehlung   339,24  ->  PZ_33924_*   (Abschnitt*100 + Vers)
    ER       Vers mal 100         4714    ->  ER_471400_*
    ER       Sonderzaehlung       4629,18 ->  ER_462918_*
    IW, TR   fortlaufend          1108    ->  IW_1108_*

Die Erec-Sonderzaehlung ist kein Sonderfall unserer Daten, sondern die
uebliche Zaehlung des Einschubs nach Vers 4629; unsere IDs bilden sie ab
(`ER_462901` bis `ER_462924` existieren).

## Warum die Trefferquote allein nicht reicht

Alle 346 Stellenangaben lassen sich auf eine existierende Wort-ID abbilden.
Das ist noch kein Beweis: eine ID kann existieren und trotzdem auf einen
anderen Vers zeigen, wenn die zitierte Ausgabe anders zaehlt. Das Skript
vergleicht deshalb zusaetzlich den WORTLAUT und sucht den besten Versatz im
Umkreis von vier Versen. Gemessen am 08.08.2026 sitzen 328 von 336 Versen
exakt; im Parzival liegt ein Block von fuenf Versen (339,24 bis 339,28) genau
zwei Verse tiefer. Ohne den Textvergleich waere das unentdeckt geblieben.

## Warum Zeichenkette und nicht Wortmenge

Die erste Fassung verglich normalisierte WORTMENGEN und meldete neun Verse
ohne Entsprechung. Sechs davon waren derselbe Vers in anderer Orthographie:
'unt hetz Lehelin genomn' gegen 'und hetez lehelin genomen', 'ans grales'
gegen 'an sgrales'. Das Maass scheiterte an Schreibung und Worttrennung, nicht
an Textidentitaet, und produzierte damit genau die Zweifelsfaelle, die es
finden sollte. Verglichen wird jetzt die MHD-normalisierte Buchstabenkette
ohne Trennungen (`difflib`), Schwelle 0.75. Uebrig bleiben drei echte Faelle.

Usage:
    python scripts/ingest/horses/02-map-citations.py           # Bericht
    python scripts/ingest/horses/02-map-citations.py --json    # maschinenlesbar
    python scripts/ingest/horses/02-map-citations.py --detail  # je Vers eine Zeile
"""
import argparse
import difflib
import io
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from lxml import etree  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'scripts'))
from mhg_normalizer import normalize_mhg as normalize  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XML = '{http://www.w3.org/XML/1998/namespace}'

QUELLE = ('https://tudatalib.ulb.tu-darmstadt.de/server/api/core/bitstreams/'
          'a64fd7c9-9c58-4446-97bd-885577f2b85c/content')   # hdl:tudatalib/3695

SIGLE = {'Wh.': 'WH', 'Pz.': 'PZ', 'Er.': 'ER', 'Iw.': 'IW', 'Tr.': 'TR'}
# Texte, deren Wort-IDs den Vers mit 100 multiplizieren (Platz fuer die
# Unterzaehlung eines Einschubs). Bei IW und TR steht die Verszahl blank.
MAL100 = {'WH', 'PZ', 'ER'}
UMKREIS = 4
# Ab hier gilt ein Vers als derselbe. Der Wert liegt in den gemessenen Daten
# (08.08.2026) in einer leeren Zone: schwaechste akzeptierte Entsprechung
# 0.84, staerkster verworfener Treffer 0.42, dazwischen nichts. Die Schwelle
# entscheidet hier also nichts, was der Abstand nicht schon entscheidet.
SCHWELLE = 0.75


def stellenkern(n, sigle):
    """Boreks Angabe auf den Verskern unserer Wort-IDs abbilden."""
    if ',' in n:
        a, b = n.split(',')
        return int('%d%02d' % (int(a), int(b)))
    return int(n) * 100 if sigle in MAL100 else int(n)


def kette(s):
    """Ein Vers als vergleichbare Buchstabenkette: MHD-normalisiert, ohne
    Trennungen und Interpunktion. Die Worttrennung faellt bewusst weg, sie
    ist zwischen Ausgaben nicht stabil ('ans grales' / 'an sgrales')."""
    return re.sub(r'[^a-z]', '', normalize(s.lower()))


def aehnlich(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def lade_borek(pfad=None):
    if pfad and pfad.exists():
        baum = etree.parse(str(pfad))
    else:
        with urllib.request.urlopen(QUELLE, timeout=60) as r:
            baum = etree.fromstring(r.read()).getroottree()
    # Je Vers eine LISTE. 346 Stellenangaben entfallen auf 336 Verse: zehn
    # werden von zwei Pferden zitiert, vier davon mit abweichendem Wortlaut
    # ('kam her Walwan geriten' / 'und kam her Walwan geriten'). Ein dict
    # ueberschriebe die eine Fassung mit der anderen, und welche gewinnt,
    # haengt an der Dokumentreihenfolge. Bewertet wird die beste.
    belege = defaultdict(lambda: defaultdict(list))
    for pferd in baum.getroot().iter(TEI + 'horse'):
        pid = pferd.get(XML + 'id')
        for src in pferd.iter(TEI + 'source'):
            werk = (src.get('ref') or '').lstrip('#')
            for l in src.iter(TEI + 'l'):
                belege[werk][l.get('n')].append(
                    (re.sub(r'\s+', ' ', ''.join(l.itertext())).strip(), pid))
    return belege


def main():
    ap = argparse.ArgumentParser(description='#193 Baustein 3: Belegstellen-Mapping.')
    ap.add_argument('--json', action='store_true', dest='as_json')
    ap.add_argument('--detail', action='store_true')
    args = ap.parse_args()

    belege = lade_borek(HERE / 'arthurianHorses.xml')
    ergebnis = {}

    for werk, sigle in SIGLE.items():
        root = etree.parse(str(REPO / 'tei' / ('%s.tei.xml' % sigle))).getroot()
        unser = defaultdict(list)
        for w in root.iter(TEI + 'w'):
            wid = w.get(XML + 'id')
            if wid and w.text:
                unser[int(wid.split('_')[1])].append(w.text)

        versatz, schwach, zeilen = Counter(), [], []
        for n, fassungen in sorted(belege[werk].items()):
            k = stellenkern(n, sigle)
            ketten = [(kette(t), pid) for t, pid in fassungen]
            ketten = [(b, pid) for b, pid in ketten if b]
            if not ketten:
                continue
            quote, _, d, pferd = max(
                (aehnlich(b, kette(' '.join(unser.get(k + d, [])))), -abs(d), d, pid)
                for b, pid in ketten for d in range(-UMKREIS, UMKREIS + 1))
            if quote >= SCHWELLE:
                versatz[d] += 1
            else:
                schwach.append([n, round(quote, 2)])
            zeilen.append([n, '%s_%d' % (sigle, k), pferd, round(quote, 2), d])

        ergebnis[werk] = dict(
            sigle=sigle, belege=len(belege[werk]), versatz=dict(versatz.most_common()),
            schwach=schwach, zeilen=zeilen if args.detail else [],
        )

    if args.as_json:
        print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
        return 0

    gesamt = sum(d['belege'] for d in ergebnis.values())
    exakt = sum(d['versatz'].get(0, 0) for d in ergebnis.values())
    print('Belegstellen-Mapping #193, gemessen gegen tei/ '
          '(Umkreis %d Verse, Schwelle %.2f)\n' % (UMKREIS, SCHWELLE))
    print('  %-5s %-6s %7s  %-26s %s' % ('Werk', 'Sigle', 'Verse', 'Versatz', 'ohne klare Entsprechung'))
    for werk, d in ergebnis.items():
        print('  %-5s %-6s %7d  %-26s %d'
              % (werk, d['sigle'], d['belege'], d['versatz'], len(d['schwach'])))
    print('\n  %d von %d Versen sitzen exakt (%.0f %%).' % (exakt, gesamt, 100 * exakt / gesamt))
    for werk, d in ergebnis.items():
        andere = {k: v for k, v in d['versatz'].items() if k != 0}
        if andere:
            print('  %s: %s Verse mit Versatz, lokal und nicht systematisch.' % (d['sigle'], andere))
        if d['schwach']:
            print('  %s ohne klare Entsprechung: %s'
                  % (d['sigle'], ', '.join('%s (%.2f)' % (n, q) for n, q in d['schwach'][:6])))
    if args.detail:
        print()
        for werk, d in ergebnis.items():
            for n, ziel, pferd, q, dd in d['zeilen']:
                print('  %-5s %-9s -> %-14s %-14s %.2f  Versatz %+d' % (werk, n, ziel, pferd or '', q, dd))
    return 0


if __name__ == '__main__':
    sys.exit(main())
