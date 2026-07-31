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

Seit #307 werden zusaetzlich die zwei Doku-Stellen geprueft:

  4. docs/TEI-MODEL.md   Paragraph 11, Versionstabelle (Source of Truth laut eigener Ansage)
  5. docs/INDEX.md       Project Status, Klammerzusatz mit beiden Versionen

Die driften anders und unauffaelliger: sie brechen nichts, also faellt es
niemandem auf. Belegfall: der INDEX.md-Satz stand am 2026-07-31 zwei
Minor-Versionen zurueck (v4.2.0/v1.7.0 statt v4.2.1/v1.8.0), obwohl die
Pflegeanweisung in TEI-MODEL.md Paragraph 11 genau diese Stelle nennt.
Eine Doku-Notiz mehr haette das nicht verhindert, ein Gate tut es.

Usage:
    python scripts/audit/check-index-versions.py            # exit non-zero bei drift, prints report
    python scripts/audit/check-index-versions.py --quiet    # exit only, no output on success

Exit codes:
    0 = alle Versions-Strings konsistent
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
TEI_MODEL = PROJECT_ROOT / 'docs' / 'TEI-MODEL.md'
DOCS_INDEX = PROJECT_ROOT / 'docs' / 'INDEX.md'

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
    # Doku-Stellen (#307). Die Regexes sind bewusst an die konkrete Formulierung
    # gebunden: wird sie umformuliert, ist Exit 2 (Format-Drift) das richtige
    # Signal, nicht stilles Durchwinken.
    {
        'key': 'tei_model_corpus',
        'path': TEI_MODEL,
        'pattern': re.compile(r"\|\s*Corpus Index\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|"),
        'role': 'corpus',
    },
    {
        'key': 'tei_model_authority',
        'path': TEI_MODEL,
        'pattern': re.compile(r"\|\s*Authority Index\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|"),
        'role': 'authority',
    },
    {
        'key': 'docs_index_corpus',
        'path': DOCS_INDEX,
        'pattern': re.compile(r"Corpus Index v([0-9]+\.[0-9]+\.[0-9]+)"),
        'role': 'corpus',
    },
    {
        'key': 'docs_index_authority',
        'path': DOCS_INDEX,
        'pattern': re.compile(r"Authority Index v([0-9]+\.[0-9]+\.[0-9]+)"),
        'role': 'authority',
    },
]

# Menschenlesbare Namen fuer den Drift-Report.
LABELS = {
    'corpus_build': 'build-skript',
    'authority_build': 'build-skript',
    'loader_corpus': 'loader',
    'loader_authority': 'loader',
    'tei_model_corpus': 'TEI-MODEL.md',
    'tei_model_authority': 'TEI-MODEL.md',
    'docs_index_corpus': 'INDEX.md',
    'docs_index_authority': 'INDEX.md',
}

# Welche Targets gehoeren zu welcher Rolle, in Report-Reihenfolge. Die
# Build-Version fuehrt: sie steht im Artefakt und ist damit die Wahrheit.
ROLE_KEYS = {
    'corpus': ['corpus_build', 'loader_corpus', 'tei_model_corpus', 'docs_index_corpus'],
    'authority': ['authority_build', 'loader_authority', 'tei_model_authority', 'docs_index_authority'],
}


def extract(target):
    """Extract version string + line number from a target. Returns (version, lineno)
    or raises SystemExit(2) on parse failure."""
    try:
        text = target['path'].read_text(encoding='utf-8')
    except FileNotFoundError:
        # sys.exit(<string>) waere immer Exit-Code 1 — Parse-/Format-Fehler
        # sollen laut Docstring als 2 von Drift (1) unterscheidbar sein (#171 F95).
        print(f"::error title=Index version audit::File not found: {target['path']}", file=sys.stderr)
        sys.exit(2)

    m = target['pattern'].search(text)
    if not m:
        print(
            f"::error title=Index version audit::Pattern not found in {target['path'].relative_to(PROJECT_ROOT)}. "
            f"File format may have drifted from what this script expects. Update the regex in check-index-versions.py.",
            file=sys.stderr,
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

    # Pro Rolle fuehrt die Build-Version: sie landet im Artefakt und ist damit
    # die einzige Angabe, die nicht behaupten, sondern sein kann.
    drift = {}
    for role, keys in ROLE_KEYS.items():
        truth = results[keys[0]]['version']
        off = [k for k in keys[1:] if results[k]['version'] != truth]
        if off:
            drift[role] = (truth, off)

    if not drift:
        if not args.quiet:
            print("Index versions consistent:")
            for role, keys in ROLE_KEYS.items():
                places = ', '.join(LABELS[k] for k in keys)
                print(f"  {role:9s} = {results[keys[0]]['version']}  ({places})")
        return 0

    # Drift report. Use GitHub Actions ::error annotations so the CI log
    # surfaces the exact files + lines.
    print("Index version drift detected:", file=sys.stderr)
    print("", file=sys.stderr)
    for role, (truth, off) in drift.items():
        head = ROLE_KEYS[role][0]
        print(f"  {role.upper()}:", file=sys.stderr)
        print(f"    {LABELS[head]:14s} {truth}  ({results[head]['path']}:{results[head]['lineno']})  <- fuehrend", file=sys.stderr)
        for k in off:
            r = results[k]
            print(f"    {LABELS[k]:14s} {r['version']}  ({r['path']}:{r['lineno']})", file=sys.stderr)
            if k.startswith('loader'):
                fix = ("Bump the loader constant so cache-invalidate triggers for users "
                       "with an old cached index.")
            else:
                fix = ("Doku-Stelle nachziehen. Sie bricht nichts, deshalb faellt der "
                       "Rueckstand sonst niemandem auf.")
            print(
                f"::error file={r['path']},line={r['lineno']}::{role} index version "
                f"{r['version']} does not match the build-skript version {truth} in "
                f"{results[head]['path']}:{results[head]['lineno']}. {fix}",
                file=sys.stderr,
            )
    print("", file=sys.stderr)
    print("Fix: alle Stellen auf die Build-Skript-Version ziehen, commit, push.", file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
