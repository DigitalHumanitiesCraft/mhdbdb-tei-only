#!/usr/bin/env python3
"""
No-CDN-Gate: committete HTML-Seiten dürfen keine externen <script src>
tragen — alle Runtime-Bibliotheken sind vendored (assets/vendor/,
pako/dexie seit 2026-07, Prism seit #78).

Fängt doppelte, einfache und fehlende Quotes sowie protokoll-relative
URLs (//cdn...). Gegenstück zum lokalen Playwright-Guard
testing/tests/vendor.spec.js; dieses Skript ist das CI-Gate in
no-cdn-check.yml (Playwright läuft in keinem Workflow).

Bis August 2026 stand hier data-integrity.yml. Das war nie richtig: der
Aufruf lag von Anfang an in no-cdn-check.yml, dem leichten Workflow ohne
Index-Rebuild. Aufgefallen ist es, als docs/DEVELOPMENT.md eine Zeile für
dieses Skript bekam, die aus dem Docstring gelesen wurde (#329).

Exit 0 = sauber, Exit 1 = externe script-src gefunden.
"""

import io
import re
import sys
from pathlib import Path

# Ohne diesen Wrapper stirbt das Skript unter Windows an seiner eigenen
# Erfolgsmeldung: die Konsole läuft dort auf cp1252, und das Häkchen im
# print() ist U+2705. In der CI fällt das nie auf (Linux, UTF-8), lokal war
# der Check damit unbenutzbar, und zwar ausgerechnet im grünen Fall.
#
# Die zwei Zeilen stehen seit #329 einheitlich in allen Audit-Skripten, die
# etwas ausgeben. Der Auslöser ist nicht nur dieses Häkchen: Audit-Skripte
# drucken Korpus- und Lexikonformen, und die MHG-Breven ŏ und ŭ liegen
# ebenfalls außerhalb von cp1252.
#
# Zwei Fallen für den nächsten Leser. Erstens ist cp1252 nicht ASCII: es
# enthält Latin-1 samt Umlauten plus 0x80 bis 0x9F, also auch — – „ " •.
# Ein Umlaut in der Ausgabe ist deshalb kein Anlass. Zweitens tauscht der
# Wrapper nur sys.stdout; wer über stderr meldet, braucht ihn dort ebenso.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

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
