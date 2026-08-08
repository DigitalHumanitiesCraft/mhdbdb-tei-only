#!/usr/bin/env python3
"""#193 Baustein 3, Vorpruefung: treffen Boreks Belegstellen unsere Verse?

Das ist die Frage, an der das ganze Feature haengt, und sie war vor jeder
UI-Entscheidung zu beantworten. `arthurianHorses.xml` (TUdatalib 3695, CC0)
traegt 346 Stellenangaben aus fuenf Werken, verteilt auf 336 Verse. Alle
fuenf Werke liegen im Korpus.

Dieses Skript berichtet, es baut nichts. Die Auflegungslogik steht in
`mapping.py` und wird vom Index-Bau (`03-build-index.py`) mitbenutzt, damit
Bericht und Index nicht auseinanderlaufen. Warum der Wortlaut und nicht die
Verszahl entscheidet, steht dort im Kopf.

Ergebnis vom 08.08.2026, je VERS gezaehlt: 328 exact, 5 shifted, 3 distant,
0 unresolved. Der Index zaehlt je BELEG und meldet deshalb 338 exact.

Usage:
    python scripts/ingest/horses/02-map-citations.py           # Bericht
    python scripts/ingest/horses/02-map-citations.py --json    # maschinenlesbar
    python scripts/ingest/horses/02-map-citations.py --detail  # je Vers eine Zeile
"""
import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapping  # noqa: E402

HERE = Path(__file__).resolve().parent
QUELLE = ('https://tudatalib.ulb.tu-darmstadt.de/server/api/core/bitstreams/'
          'a64fd7c9-9c58-4446-97bd-885577f2b85c/content')   # hdl:tudatalib/3695


def main():
    ap = argparse.ArgumentParser(description='#193 Baustein 3: Belegstellen-Mapping.')
    ap.add_argument('--json', action='store_true', dest='as_json')
    ap.add_argument('--detail', action='store_true')
    ap.add_argument('--quelle', type=Path, default=HERE / 'arthurianHorses.xml',
                    help='lokale Kopie; fehlt sie, wird sie geholt (%s)' % QUELLE)
    args = ap.parse_args()

    if not args.quelle.exists():
        import urllib.request
        print('hole %s' % QUELLE)
        args.quelle.write_bytes(urllib.request.urlopen(QUELLE, timeout=60).read())

    belege = mapping.lade_borek(args.quelle)
    ergebnis = {}

    for werk, sigle in mapping.SIGLE.items():
        _, verskette = mapping.lade_verse(sigle)
        art, versatz, fern, offen, zeilen = Counter(), Counter(), [], [], []
        for n, fassungen in sorted(belege[werk].items()):
            r = mapping.aufloesen(n, sigle, fassungen, verskette)
            art[r['match']] += 1
            if r['match'] == 'shifted':
                versatz[r['versatz']] += 1
            elif r['match'] == 'distant':
                fern.append([n, r['target'], r['score']])
            elif r['match'] == 'unresolved':
                offen.append([n, r['score']])
            zeilen.append([n, r['target'], r['match'], r['score'], r['versatz']])

        ergebnis[werk] = dict(
            sigle=sigle, belege=len(belege[werk]), art=dict(art),
            versatz=dict(versatz.most_common()), fern=fern, offen=offen,
            zeilen=zeilen if args.detail else [],
        )

    if args.as_json:
        print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
        return 0

    gesamt = sum(d['belege'] for d in ergebnis.values())
    exakt = sum(d['art'].get('exact', 0) for d in ergebnis.values())
    offen = sum(d['art'].get('unresolved', 0) for d in ergebnis.values())
    print('Belegstellen-Mapping #193, gemessen gegen tei/ '
          '(Umkreis %d Verse, Schwelle %.2f)\n' % (mapping.UMKREIS, mapping.SCHWELLE))
    print('  %-5s %-6s %7s  %-22s %6s %s'
          % ('Werk', 'Sigle', 'Verse', 'verschoben', 'fern', 'offen'))
    for werk, d in ergebnis.items():
        print('  %-5s %-6s %7d  %-22s %6d %d'
              % (werk, d['sigle'], d['belege'], d['versatz'] or '',
                 len(d['fern']), len(d['offen'])))
    print('\n  %d von %d Versen sitzen exakt (%.0f %%), %d bleiben offen.'
          % (exakt, gesamt, 100 * exakt / gesamt, offen))
    for werk, d in ergebnis.items():
        if d['versatz']:
            print('  %s: %s Verse verschoben, lokal und nicht systematisch.'
                  % (d['sigle'], d['versatz']))
        for n, ziel, q in d['fern']:
            print('  %s %s liegt ausserhalb des Umkreises bei %s (%.2f).'
                  % (d['sigle'], n, ziel, q))
        for n, q in d['offen']:
            print('  %s %s ohne Entsprechung (bester Treffer %.2f).'
                  % (d['sigle'], n, q))
    if args.detail:
        print()
        for werk, d in ergebnis.items():
            for n, ziel, art, q, dd in d['zeilen']:
                print('  %-5s %-9s -> %-14s %-10s %.2f  %s'
                      % (werk, n, ziel or '(keins)', art, q,
                         'Versatz %+d' % dd if dd else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
