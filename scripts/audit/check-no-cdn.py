#!/usr/bin/env python3
"""
No-CDN-Gate: committete HTML-Seiten dürfen keine externen <script src>
tragen — alle Runtime-Bibliotheken sind vendored (assets/vendor/,
pako/dexie seit 2026-07, Prism seit #78).

Fängt doppelte, einfache und fehlende Quotes sowie protokoll-relative
URLs (//cdn...). Gegenstück zum lokalen Playwright-Guard
testing/tests/vendor.spec.js; dieses Skript ist das CI-Gate in
data-integrity.yml (Playwright läuft dort nicht).

Exit 0 = sauber, Exit 1 = externe script-src gefunden.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
# Nur auf der OBERSTEN Ebene ausschliessen. Ein Test ueber ALLE Pfadteile
# (so stand es hier bis 28.07.) uebersieht Verzeichnisse, die zufaellig
# genauso heissen wie eine Datenwurzel: playground/js/ui/tei/ waere
# wegen 'tei' stillschweigend ungeprueft geblieben. Aktuell liegt dort
# kein HTML, der Fehler war also wirkungslos, aber es ist dieselbe Falle,
# in die check-no-em-dash.py zuerst getappt ist (#140).
TOP_LEVEL_SKIP = {'tei', 'data', 'node_modules', '.git', 'test-results'}
SKIP_ANYWHERE = {'node_modules', '.git', 'test-results'}

EXTERNAL_SCRIPT_SRC = re.compile(
    r'<script[^>]+src\s*=\s*["\']?\s*(?:https?:)?//', re.IGNORECASE
)


def html_files(root: Path):
    for path in root.rglob('*.html'):
        teile = path.relative_to(root).parts
        if teile[0] in TOP_LEVEL_SKIP:
            continue
        if any(t in SKIP_ANYWHERE for t in teile):
            continue
        yield path


def main() -> int:
    offenders = []
    for path in html_files(REPO):
        text = path.read_text(encoding='utf-8', errors='replace')
        for match in EXTERNAL_SCRIPT_SRC.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            offenders.append(f'{path.relative_to(REPO)}:{line}: {match.group(0)}...')

    if offenders:
        print('❌ Externe <script src> gefunden (CDN-Verbot, vendored unter assets/vendor/):')
        for o in offenders:
            print(f'   {o}')
        return 1

    print('✅ No-CDN-Check: keine externen <script src> in committeten HTML-Seiten')
    return 0


if __name__ == '__main__':
    sys.exit(main())
