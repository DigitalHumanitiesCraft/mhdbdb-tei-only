#!/usr/bin/env python3
"""Konsistenz-Check der Index-Versions-Konstanten.

Hintergrund (Lehre aus 2026-05-12, #47.3): der Corpus-Index wird durch
drei Stellen versioniert, die alle synchron sein muessen, sonst greift
die Cache-Invalidate-Logik im Frontend nicht.

  1. scripts/build-corpus-index.py        -> 'version': '4.1.3'
  2. scripts/build-authority-index.py     -> 'version': '1.3.0'
  3. assets/js/lib/corpus-loader.js
        INDEX_VERSION             = '4.1.3'
        AUTHORITY_INDEX_VERSION   = '1.3.0'

Wenn diese auseinanderlaufen, cached der Loader den neuen Index mit
der alten Version-Konstante und gibt ihn beim naechsten Load auch wieder
heraus, weil sein Versions-Vergleich (cached.version vs. Loader-Konstante)
match liefert. Production-User bekommen den neuen Index nie zu sehen.

Usage:
    python scripts/audit/check-index-versions.py            # exit non-zero bei drift, prints report
    python scripts/audit/check-index-versions.py --quiet    # exit only, no output on success

Exit codes:
    0 = alle vier Versions-Strings konsistent
    1 = drift (mindestens eine Stelle aus der Reihe)
    2 = parse error (regex hat eine Stelle nicht gefunden -> nicht meine Schuld, sondern File-Format-Drift)
"""
import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BUILD_CORPUS = PROJECT_ROOT / 'scripts' / 'build-corpus-index.py'
BUILD_AUTHORITY = PROJECT_ROOT / 'scripts' / 'build-authority-index.py'
LOADER = PROJECT_ROOT / 'assets' / 'js' / 'lib' / 'corpus-loader.js'

# Regex-Targets: jeweils die erste Fundstelle, die das interessante Pattern matched.
TARGETS = [
    {
        'key': 'corpus_build',
        'path': BUILD_CORPUS,
        'pattern': re.compile(r"'version'\s*:\s*'([0-9]+\.[0-9]+\.[0-9]+)'"),
        'role': 'corpus',
    },
    {
        'key': 'authority_build',
        'path': BUILD_AUTHORITY,
        'pattern': re.compile(r"'version'\s*:\s*'([0-9]+\.[0-9]+\.[0-9]+)'"),
        'role': 'authority',
    },
    {
        'key': 'loader_corpus',
        'path': LOADER,
        'pattern': re.compile(r"const\s+INDEX_VERSION\s*=\s*'([0-9]+\.[0-9]+\.[0-9]+)'"),
        'role': 'corpus',
    },
    {
        'key': 'loader_authority',
        'path': LOADER,
        'pattern': re.compile(r"const\s+AUTHORITY_INDEX_VERSION\s*=\s*'([0-9]+\.[0-9]+\.[0-9]+)'"),
        'role': 'authority',
    },
]


def extract(target):
    """Extract version string + line number from a target. Returns (version, lineno)
    or raises SystemExit(2) on parse failure."""
    try:
        text = target['path'].read_text(encoding='utf-8')
    except FileNotFoundError:
        # sys.exit(<string>) waere immer Exit-Code 1 — Parse-/Format-Fehler
        # sollen laut Docstring als 2 von Drift (1) unterscheidbar sein (#171 F95).
        print(f"::error title=Index version audit::File not found: {target['path']}")
        sys.exit(2)

    m = target['pattern'].search(text)
    if not m:
        print(
            f"::error title=Index version audit::Pattern not found in {target['path'].relative_to(PROJECT_ROOT)}. "
            f"File format may have drifted from what this script expects. Update the regex in check-index-versions.py."
        )
        sys.exit(2)

    # Find line number of the match
    lineno = text.count('\n', 0, m.start()) + 1
    return m.group(1), lineno


def main():
    parser = argparse.ArgumentParser(description="Check Index-Version-Konstanten auf Konsistenz.")
    parser.add_argument('--quiet', action='store_true', help="Keine Ausgabe bei Erfolg (nur Exit-Code).")
    args = parser.parse_args()

    results = {}
    for t in TARGETS:
        version, lineno = extract(t)
        results[t['key']] = {
            'version': version,
            'lineno': lineno,
            'path': t['path'].relative_to(PROJECT_ROOT),
            'role': t['role'],
        }

    corpus_build = results['corpus_build']['version']
    loader_corpus = results['loader_corpus']['version']
    authority_build = results['authority_build']['version']
    loader_authority = results['loader_authority']['version']

    corpus_match = corpus_build == loader_corpus
    authority_match = authority_build == loader_authority

    if corpus_match and authority_match:
        if not args.quiet:
            print(f"Index versions consistent:")
            print(f"  corpus    = {corpus_build}  (build-skript + loader)")
            print(f"  authority = {authority_build}  (build-skript + loader)")
        return 0

    # Drift report. Use GitHub Actions ::error annotations so the CI log
    # surfaces the exact files + lines.
    print("Index version drift detected:", file=sys.stderr)
    print("", file=sys.stderr)
    if not corpus_match:
        cb, lc = results['corpus_build'], results['loader_corpus']
        print(f"  CORPUS:", file=sys.stderr)
        print(f"    build-skript:  {cb['version']}  ({cb['path']}:{cb['lineno']})", file=sys.stderr)
        print(f"    loader:        {lc['version']}  ({lc['path']}:{lc['lineno']})", file=sys.stderr)
        print(f"::error file={lc['path']},line={lc['lineno']}::INDEX_VERSION ({lc['version']}) does not match build-skript version ({cb['version']}) in {cb['path']}:{cb['lineno']}. Bump the loader constant so cache-invalidate triggers for users with an old cached index.", file=sys.stderr)
    if not authority_match:
        ab, la = results['authority_build'], results['loader_authority']
        print(f"  AUTHORITY:", file=sys.stderr)
        print(f"    build-skript:  {ab['version']}  ({ab['path']}:{ab['lineno']})", file=sys.stderr)
        print(f"    loader:        {la['version']}  ({la['path']}:{la['lineno']})", file=sys.stderr)
        print(f"::error file={la['path']},line={la['lineno']}::AUTHORITY_INDEX_VERSION ({la['version']}) does not match build-skript version ({ab['version']}) in {ab['path']}:{ab['lineno']}. Bump the loader constant so cache-invalidate triggers for users with an old cached index.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Fix: bump the loader constant to match the build-skript version, commit, push.", file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
