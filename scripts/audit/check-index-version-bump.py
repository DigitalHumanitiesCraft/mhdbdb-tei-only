#!/usr/bin/env python3
"""Version-Bump-Gate fuer corpus-/authority-index (#154).

Schliesst die Luecke, die Rebuild-and-Compare (#125) und
check-index-versions.py offen lassen: ein Daten-PR, der die Indexe
korrekt rebuildet, aber den Drei-Stellen-Versions-Bump (CONTRACTS §E)
vergisst, passiert beide Gates gruen — committeter und frisch gebauter
Index tragen dann beide die alte Version. Folge: der Dexie-Cache
(MHDBDBMainSite) invalidiert nicht, wiederkehrende Nutzer behalten bis
zu 30 Tage den alten Index, waehrend die Leseansicht seit #151 sofort
aktualisiert.

Regel: Hat sich der DEKOMPRIMIERTE Index-Inhalt gegenueber der Base
geaendert, MUSS sich auch der eingebettete version-String geaendert
haben. (Umgekehrt ist ein Bump ohne Inhaltsaenderung erlaubt — z.B.
reiner Cache-Flush — und wird nur als Hinweis gemeldet.)

Der naming-index ist bewusst NICHT Gegenstand dieses Gates: er hat
keinen Versions-Kanal im Loader (lazy fetch ohne IndexedDB-Cache, #59)
und damit keine Bump-Pflicht.

Usage:
    python scripts/audit/check-index-version-bump.py --base <git-rev>

    <git-rev> muss lokal aufloesbar sein (in CI vorher fetchen, siehe
    data-integrity.yml "Diff-Base bestimmen").

Exit codes:
    0 = ok (Inhalt unveraendert, oder geaendert + gebumpt; Base-seitig
        fehlende Datei zaehlt als neu -> ok)
    1 = Inhalt geaendert, aber version-String identisch (Bump vergessen),
        oder Vorbedingung verletzt (Base nicht aufloesbar, version-String
        nicht extrahierbar)
"""
import argparse
import gzip
import io
import re
import subprocess
import sys
from pathlib import Path

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252,
# und Audit-Skripte geben Korpus- und Lexikonformen aus. Die MHG-Breven ŏ
# und ŭ liegen ausserhalb von cp1252, ein Treffer wuerde das Skript also an
# seiner eigenen Ausgabe toeten. Der Wrapper steht deshalb einheitlich in
# den Skripten, die Korpus- oder Lexikonformen ausgeben, nicht in allen 22.
# Wer eines ergaenzt, das solche Formen druckt, braucht ihn ebenfalls.
# Er deckt nur stdout; wer ueber stderr meldet, braucht ihn dort ebenso.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INDEX_FILES = ('data/corpus-index.json.gz', 'data/authority-index.json.gz')

# Der version-String steht build-bedingt am JSON-Anfang (json.dumps eines
# Dicts mit 'version' als erstem Key) — Regex auf den Kopf reicht und
# erspart das Parsen der bis zu mehreren 100 MB grossen Indexe.
VERSION_RE = re.compile(rb'"version"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"')


def extract_version(data, label):
    m = VERSION_RE.search(data[:1000])
    if not m:
        sys.exit(f'::error title=Index version bump gate::Kein version-String '
                 f'im Kopf von {label} gefunden. Index-Format hat sich evtl. '
                 f'geaendert — Regex in check-index-version-bump.py anpassen.')
    return m.group(1).decode('ascii')


def git_show(base, path):
    """Blob von <base>:<path> oder None, wenn die Datei dort nicht existiert.

    Fail-open bei JEDEM git-Fehler (nicht nur "Pfad fehlt in Base") — die
    Base selbst ist vorher via rev-parse verifiziert, andere Fehlerarten
    sind hier nicht unterscheidbar ohne stderr-Parsing.
    """
    result = subprocess.run(
        ['git', 'show', f'{base}:{path}'],
        cwd=PROJECT_ROOT, capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout


def main():
    parser = argparse.ArgumentParser(
        description='Inhalts-Aenderung ohne Versions-Bump erkennen (#154).')
    parser.add_argument('--base', required=True,
                        help='Git-Rev des Vergleichsstands (z.B. origin/main)')
    args = parser.parse_args()

    probe = subprocess.run(['git', 'rev-parse', '--verify', f'{args.base}^{{commit}}'],
                           cwd=PROJECT_ROOT, capture_output=True, text=True)
    if probe.returncode != 0:
        sys.exit(f'::error title=Index version bump gate::Base "{args.base}" ist '
                 f'lokal nicht aufloesbar. In CI vorher fetchen (data-integrity.yml).')
    base_sha = probe.stdout.strip()
    print(f'Vergleiche gegen Base {base_sha[:12]} ({args.base})')

    failed = False
    for rel_path in INDEX_FILES:
        new_raw = (PROJECT_ROOT / rel_path).read_bytes()
        new = gzip.decompress(new_raw)
        new_version = extract_version(new, rel_path)

        old_raw = git_show(base_sha, rel_path)
        if old_raw is None:
            print(f'{rel_path}: in Base nicht vorhanden (neue Datei) — OK')
            continue
        old = gzip.decompress(old_raw)
        old_version = extract_version(old, f'{args.base}:{rel_path}')

        if old == new:
            print(f'{rel_path}: Inhalt unveraendert (Version {new_version}) — OK')
        elif old_version != new_version:
            print(f'{rel_path}: Inhalt geaendert, Version {old_version} -> '
                  f'{new_version} gebumpt — OK')
        else:
            failed = True
            print(f'::error file={rel_path}::{rel_path}: Inhalt hat sich gegenueber '
                  f'{args.base} geaendert, aber der version-String ist unveraendert '
                  f'({new_version}). Drei-Stellen-Bump vergessen (CONTRACTS §E): '
                  f'Version im Build-Skript UND in assets/js/lib/corpus-loader.js '
                  f'bumpen, Index rebuilden, mitcommitten — sonst behalten '
                  f'wiederkehrende Nutzer bis zu 30 Tage den alten Index (#154).')

    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
