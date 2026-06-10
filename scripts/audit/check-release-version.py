#!/usr/bin/env python3
"""Konsistenz-Check der Release-Version gegen CITATION.cff und .zenodo.json.

Hintergrund (#91, 2026-06-10): Zenodo zieht die Record-Metadaten beim
Release aus .zenodo.json. Steht dort ein hartkodiertes "version"-Feld,
das beim Taggen nicht mitgebumpt wurde, zeigt der Zenodo-Record still
eine falsche Version an -- kein Fehler, keine Warnung. Deshalb:

  1. .zenodo.json darf KEIN "version"-Feld enthalten. Fehlt es, nimmt
     Zenodo automatisch den Tag-Namen als Version -> der Git-Tag ist
     die Single Source of Truth.
  2. CITATION.cff -> version: "X.Y.Z" muss dem Tag (ohne fuehrendes "v")
     entsprechen. Die CFF speist das GitHub-Widget "Cite this repository";
     eine veraltete Version dort produziert falsche Zitationen.

Schlaegt der Check beim Tag-Push fehl: Tag wieder loeschen
(git push --delete origin vX.Y.Z; git tag -d vX.Y.Z), CITATION.cff
fixen, neu taggen. Solange noch kein GitHub-Release publiziert wurde,
hat Zenodo nichts gesehen -- der Webhook feuert erst beim Release.

Usage:
    python scripts/audit/check-release-version.py v1.1.0   # Tag explizit
    python scripts/audit/check-release-version.py          # Tag aus $GITHUB_REF_NAME (CI)

Exit codes:
    0 = konsistent
    1 = drift (CFF-Version != Tag, oder "version"-Feld in .zenodo.json)
    2 = parse error / kein Tag ermittelbar
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CITATION_CFF = PROJECT_ROOT / 'CITATION.cff'
ZENODO_JSON = PROJECT_ROOT / '.zenodo.json'

CFF_VERSION_PATTERN = re.compile(r'^version:\s*"([^"]+)"', re.MULTILINE)


def main():
    parser = argparse.ArgumentParser(
        description="Check Release-Tag gegen CITATION.cff und .zenodo.json.")
    parser.add_argument('tag', nargs='?', default=os.environ.get('GITHUB_REF_NAME'),
                        help="Release-Tag (z.B. v1.1.0). Default: $GITHUB_REF_NAME.")
    args = parser.parse_args()

    if not args.tag:
        sys.exit("::error title=Release version audit::Kein Tag uebergeben und $GITHUB_REF_NAME ist leer. Usage: check-release-version.py v1.1.0")

    expected = args.tag.lstrip('v')
    errors = []

    # 1. CITATION.cff: version muss dem Tag entsprechen
    try:
        cff_text = CITATION_CFF.read_text(encoding='utf-8')
    except FileNotFoundError:
        sys.exit(f"::error title=Release version audit::File not found: {CITATION_CFF}")

    m = CFF_VERSION_PATTERN.search(cff_text)
    if not m:
        sys.exit(
            "::error title=Release version audit::Kein version-Feld in CITATION.cff gefunden. "
            "File-Format-Drift? Regex in check-release-version.py anpassen."
        )
    cff_version = m.group(1)
    cff_lineno = cff_text.count('\n', 0, m.start()) + 1
    if cff_version != expected:
        errors.append(
            f"::error file=CITATION.cff,line={cff_lineno}::CITATION.cff version ({cff_version}) "
            f"!= Release-Tag {args.tag} (erwartet: {expected}). Vor dem Taggen version + date-released bumpen."
        )

    # 2. .zenodo.json: darf kein version-Feld haben (Tag ist SSoT)
    try:
        zenodo = json.loads(ZENODO_JSON.read_text(encoding='utf-8'))
    except FileNotFoundError:
        sys.exit(f"::error title=Release version audit::File not found: {ZENODO_JSON}")
    except json.JSONDecodeError as e:
        sys.exit(f"::error file=.zenodo.json::JSON parse error: {e}")

    if 'version' in zenodo:
        errors.append(
            f"::error file=.zenodo.json::.zenodo.json enthaelt ein hartkodiertes version-Feld "
            f"(\"{zenodo['version']}\"). Entfernen -- ohne das Feld nimmt Zenodo automatisch den "
            f"Tag-Namen als Version und es kann nichts driften."
        )

    if not errors:
        print(f"Release version consistent: Tag {args.tag} == CITATION.cff {cff_version}, "
              f".zenodo.json ohne version-Feld (Tag ist SSoT).")
        return 0

    print(f"Release version drift detected (Tag: {args.tag}):", file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)
    print("", file=sys.stderr)
    print("Fix: Tag loeschen, Dateien korrigieren, neu taggen -- solange kein "
          "GitHub-Release publiziert wurde, hat der Zenodo-Webhook nichts gesehen.", file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
