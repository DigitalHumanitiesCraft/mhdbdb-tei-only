#!/usr/bin/env python3
"""
Em-Dash-Gate: user-sichtbare Texte dürfen keine Em-Dashes (—) tragen.

Hausregel des Projekts: in Prosa, die Nutzende oder Leserinnen sehen, steht
statt eines Em-Dashes ein Doppelpunkt, ein Komma, eine Klammer oder ein
eigener Satz. Ein En-Dash (–) mit Leerzeichen ist erlaubt.

Der Anlass ist wiederkehrend: KZW hat am 28.07. zum wiederholten Mal einen
Em-Dash im Frontend gemeldet (Issue #140, diesmal im Hapax-Werkzeug). Sieben
Fundstellen steckten damals in `assets/js/` und `playground/js/`, keine davon
wäre in einem Review aufgefallen, weil sie in Template-Literalen und
title-Attributen sitzen.

Bewusst NICHT geprüft:
  - Code-Kommentare (`//`, `/* */`, `#`, `<!-- -->`) — dort sind Em-Dashes
    laut Hausregel ausdrücklich erlaubt
  - docs/**, publications/**, README — Autorentext, kein UI
  - tei/**, authority-files/** — Quelldaten, editorisch gewollt
  - assets/vendor/** und node_modules — Fremdcode

Geprüft werden:
  - alle committeten *.html im Repo-Wurzelbereich und in playground/
  - String- und Template-Literale in assets/js/** und playground/js/**

Usage:
    python scripts/audit/check-no-em-dash.py            # Report + Exit-Code
    python scripts/audit/check-no-em-dash.py --quiet    # nur Exit-Code

Exit 0 = sauber, Exit 1 = Em-Dash in user-sichtbarem Text gefunden.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

EM_DASH = '—'

# Achtung: nur auf der OBERSTEN Ebene ausschliessen. Ein Test mit
# `part in SKIP_DIRS for part in ...parts` uebersieht ausgerechnet
# playground/js/ui/tei/, weil dort ein Verzeichnis ebenfalls `tei` heisst.
TOP_LEVEL_SKIP = {'tei', 'data', 'docs', 'publications', 'schema', 'testing',
                  'proposals', 'node_modules', '.git', 'test-results'}
# Diese duerfen auf jeder Ebene fehlen.
SKIP_ANYWHERE = {'node_modules', 'vendor', '_archived', 'test-results', '.git'}

# Em-Dash innerhalb eines Quoted- oder Template-Literals: nur solche Treffer
# landen im DOM. Ein Em-Dash in einer Kommentarzeile ist erlaubt.
IN_STRING = re.compile(
    '(`[^`]*' + EM_DASH + '[^`]*`)'
    "|('[^']*" + EM_DASH + "[^']*')"
    '|("[^"]*' + EM_DASH + '[^"]*")'
)

COMMENT_START = ('//', '*', '/*', '<!--', '#')


def relevante_dateien():
    for muster in ('*.html', 'assets/js/**/*.js', 'playground/**/*.js',
                   'playground/**/*.html', 'lemma/**/*.html', 'api/*.html'):
        for pfad in REPO.glob(muster):
            teile = pfad.relative_to(REPO).parts
            if teile[0] in TOP_LEVEL_SKIP:
                continue
            if any(t in SKIP_ANYWHERE for t in teile):
                continue
            yield pfad


def pruefe(pfad: Path):
    """Liefert (Zeilennummer, Zeileninhalt) je Fundstelle."""
    treffer = []
    try:
        text = pfad.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return treffer
    ist_html = pfad.suffix == '.html'
    for nr, zeile in enumerate(text.split('\n'), 1):
        gestrippt = zeile.strip()
        if EM_DASH not in gestrippt:
            continue
        if gestrippt.startswith(COMMENT_START):
            continue
        # In HTML ist jeder Nicht-Kommentar-Treffer sichtbarer Text oder
        # Attributwert; in JS nur, was in einem Literal steht.
        if ist_html or IN_STRING.search(zeile):
            treffer.append((nr, gestrippt[:160]))
    return treffer


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--quiet', action='store_true', help='nur Exit-Code, keine Ausgabe')
    args = ap.parse_args()

    fundstellen = []
    for pfad in sorted(set(relevante_dateien())):
        for nr, zeile in pruefe(pfad):
            fundstellen.append((pfad.relative_to(REPO).as_posix(), nr, zeile))

    if not fundstellen:
        if not args.quiet:
            print('Em-Dash-Gate: keine Em-Dashes in user-sichtbarem Text.')
        return 0

    if not args.quiet:
        print(f'Em-Dash-Gate: {len(fundstellen)} Fundstelle(n) in user-sichtbarem Text.')
        print('Hausregel: Doppelpunkt, Komma, Klammer oder eigener Satz statt Em-Dash.')
        print()
        for pfad, nr, zeile in fundstellen:
            print(f'::error file={pfad},line={nr}::Em-Dash in user-sichtbarem Text')
            print(f'  {pfad}:{nr}')
            print(f'    {zeile}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
