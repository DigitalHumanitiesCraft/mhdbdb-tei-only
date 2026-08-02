#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Naming-Index Konsistenz-Check (#152) — CI-Gate + lokaler Pre-Push-Check.

Prueft data/naming-index.json.gz offline auf zwei Invarianten:
  1. source.commit-Provenienz vorhanden (ohne sie ist der Index nicht aus
     seinem Quellstand reproduzierbar und der Freshness-Vergleich in
     data-integrity.yml unmoeglich; mit --require-commit rebuilden).
  2. Jede works[].sigle existiert als tei/<SIG>.tei.xml — ein Sigle-Rename
     ohne naming-Anpassung braeche den Reader-Link im Playground sonst
     still als No-op.

Extrahiert aus dem frueheren Inline-Heredoc in data-integrity.yml (Review
PR #155): als Skript ist der Check lokal VOR dem Push ausfuehrbar und hat
via scripts/audit/** seinen eigenen Workflow-Trigger (Review #146).

Usage:
    python scripts/audit/check-naming-index.py                       # Konsistenz-Check
    python scripts/audit/check-naming-index.py --print-source-commit # nur Pin ausgeben

--print-source-commit dient den Workflows (data-integrity.yml Freshness-
Step, naming-index-update.yml Quell-Commit-Steps) als einzige Quelle der
Pin-Extraktion — vorher existierte der gzip/json-Einzeiler dreifach inline.

Exit codes: 0 = ok, 1 = Invariante verletzt / Index fehlt.
"""

import gzip
import io
import json
import sys
from pathlib import Path

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252,
# und Audit-Skripte geben Korpus- und Lexikonformen aus. Die MHG-Breven ŏ
# und ŭ liegen ausserhalb von cp1252, ein Treffer wuerde das Skript also an
# seiner eigenen Ausgabe toeten. Der Wrapper steht deshalb einheitlich in
# allen Skripten, die etwas ausgeben, statt pro Datei abgewogen zu werden.
# Er deckt nur stdout; wer ueber stderr meldet, braucht ihn dort ebenso.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX = PROJECT_ROOT / 'data' / 'naming-index.json.gz'
TEI_DIR = PROJECT_ROOT / 'tei'


def load_index():
    if not INDEX.exists():
        sys.exit(f'::error file=data/naming-index.json.gz::naming-index fehlt '
                 f'({INDEX}).')
    with gzip.open(INDEX, 'rt', encoding='utf-8') as f:
        return json.load(f)


def main():
    idx = load_index()
    commit = idx.get('source', {}).get('commit', '')

    if '--print-source-commit' in sys.argv:
        print(commit)
        return 0

    ok = True
    if not commit:
        print('::error file=data/naming-index.json.gz::naming-index ohne '
              'source.commit — Provenienz verloren. Mit '
              'scripts/ingest/naming/01-fetch-and-build-index.py '
              '--require-commit rebuilden (#152).')
        ok = False
    works = idx.get('works', [])
    for work in works:
        sigle = work.get('sigle', '')
        if not (TEI_DIR / f'{sigle}.tei.xml').exists():
            print(f'::error file=data/naming-index.json.gz::naming-index '
                  f'referenziert Sigle "{sigle}", aber tei/{sigle}.tei.xml '
                  f'existiert nicht — Sigle-Rename ohne naming-Anpassung? '
                  f'Der Reader-Link im Playground braeche sonst still (#152).')
            ok = False
    if ok:
        print(f'naming-index OK: source.commit={commit[:12]}, '
              f'{len(works)} Werke, alle Sigles im Korpus.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
