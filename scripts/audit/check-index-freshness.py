#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Freshness-Gate: sind die abgeleiteten Artefakte mit dem Quellstand synchron?

Schwester von `check-index-versions.py`. Dort wird geprueft, ob die Versions-
*Konstanten* zueinander passen. Hier wird geprueft, ob die abgeleitete Schicht
(Indexe + korpus-abgeleitetes variants.xml) ueberhaupt aus dem *aktuellen*
Quellstand gebaut wurde. Beide Checks sind noetig: die Konstanten koennen
konsistent sein, waehrend der Index-Inhalt veraltet ist (Quelle editiert,
Rebuild vergessen) -- genau die stille Drift aus #44/#115.

Operationalisiert den Data-Change-Lifecycle (DATA-MODEL.md). Abhaengigkeiten:

    tei/*.tei.xml ----+--> data/corpus-index.json.gz
                      +--> authority-files/variants.xml  (korpus-abgeleitet)
    authority-files/{lexicon,persons,works,concepts,genres,names}.xml
                      +--> data/authority-index.json.gz
    authority-files/variants.xml --> data/authority-index.json.gz

Methode (rein topologisch, kein Timestamp-Verlass -> CI-stabil):
  Fuer jedes Artefakt A mit Quellen S gilt A als VERALTET, wenn eine Quelle in
  einem Commit geaendert wurde, der *nach* dem letzten A-Build-Commit liegt
  (`git diff <build-commit>..HEAD -- <quellen>` ist nicht leer). Der
  lifecycle-konforme Commit (Quelle + Rebuild zusammen) faellt damit korrekt
  durch (Diff ueber den offenen Bereich schliesst den Build-Commit selbst aus).

Zusaetzlich Working-Tree-Check: uncommittete Quelländerungen ohne mitgebautes,
gestagtes Artefakt -> Pre-Commit-Warnung.

Read-only. Exit 0 = frisch, 1 = veraltet, 2 = kein git / Setup-Fehler.
Lokales Advisory, v.a. fuer den Working-Tree-Check vor dem Commit (den CI
nicht sehen kann). Das harte CI-Gate ist seit #125 der Rebuild-and-Compare-
Step in .github/workflows/data-integrity.yml. Die Erkennung hier bleibt
quelldatei-granular und ueber-flaggt Quelländerungen, die kein indexiertes
Feld betreffen (z.B. reine @corresp-Entfernung) -- vor einem Rebuild also
Index-Relevanz pruefen.

Usage:
    python scripts/audit/check-index-freshness.py
    python scripts/audit/check-index-freshness.py --quiet
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Abgeleitetes Artefakt -> (Quell-Pathspecs, Klartext-Name). Die Reihenfolge
# spiegelt den Lifecycle: erst variants.xml regenerieren, dann die Indexe.
DERIVED = [
    {
        'artifact': 'authority-files/variants.xml',
        'sources': ['tei'],
        'label': 'variants.xml (korpus-abgeleitet)',
        'rebuild': 'python scripts/sync/extract-variants.py',
    },
    {
        'artifact': 'data/corpus-index.json.gz',
        'sources': ['tei'],
        'label': 'Corpus-Index',
        'rebuild': 'python scripts/build-corpus-index.py',
    },
    {
        'artifact': 'data/authority-index.json.gz',
        # contributors.xml ist KEIN Index-Input (nur @ref-Register) -> ausgelassen.
        'sources': [
            'authority-files/lexicon.xml', 'authority-files/persons.xml',
            'authority-files/works.xml', 'authority-files/concepts.xml',
            'authority-files/genres.xml', 'authority-files/names.xml',
            'authority-files/variants.xml',
        ],
        'label': 'Authority-Index',
        'rebuild': 'python scripts/build-authority-index.py',
    },
    {
        'artifact': 'api/',
        'sources': [
            'data/corpus-index.json.gz', 'data/authority-index.json.gz',
        ],
        'label': 'Statische JSON-API (#45)',
        'rebuild': 'python scripts/build-api.py',
    },
]


def git(*args):
    """Run a git command in the repo root; return stdout (stripped) or ''."""
    res = subprocess.run(['git', *args], cwd=str(PROJECT_ROOT),
                         capture_output=True, text=True, encoding='utf-8')
    if res.returncode != 0:
        return None
    return res.stdout.strip()


def last_build_commit(artifact):
    """Hash of the most recent committed change to the artifact, or None."""
    out = git('rev-list', '-1', 'HEAD', '--', artifact)
    return out or None


def sources_changed_since(build_commit, sources):
    """Source files that differ between build_commit and HEAD (exclusive of
    build_commit). Empty == artifact still in sync with committed sources."""
    out = git('diff', '--name-only', f'{build_commit}..HEAD', '--', *sources)
    return [l for l in (out or '').splitlines() if l.strip()]


def working_tree_changed(pathspecs):
    """Files with uncommitted changes (staged or unstaged) under pathspecs."""
    out = git('status', '--porcelain', '--', *pathspecs)
    files = []
    for line in (out or '').splitlines():
        # porcelain: XY <path>  (rename: ' -> ')
        path = line[3:].strip()
        if ' -> ' in path:
            path = path.split(' -> ', 1)[1]
        if path:
            files.append(path)
    return files


def main():
    parser = argparse.ArgumentParser(
        description='Freshness-Gate fuer Indexe + variants.xml gegen den Quellstand.')
    parser.add_argument('--quiet', action='store_true',
                        help='Keine Ausgabe bei Erfolg (nur Exit-Code).')
    args = parser.parse_args()

    if git('rev-parse', '--is-inside-work-tree') != 'true':
        print('::error title=Index freshness::Kein git-Repository -- Check uebersprungen.',
              file=sys.stderr)
        return 2

    stale = []          # (label, artifact, [offending sources], rebuild)
    pending = []        # (label, artifact, rebuild) -- working-tree only

    for d in DERIVED:
        artifact = d['artifact']
        build_commit = last_build_commit(artifact)

        # 1) Commit-History-Staleness.
        if build_commit:
            changed = sources_changed_since(build_commit, d['sources'])
            if changed:
                stale.append((d['label'], artifact, changed, d['rebuild']))
        # (Kein build_commit -> Artefakt nie committet; das ist ein anderes
        #  Problem als Drift und wird hier nicht als "stale" gewertet.)

        # 2) Working-Tree-Staleness: Quellen dirty, Artefakt aber nicht.
        src_dirty = working_tree_changed(d['sources'])
        art_dirty = working_tree_changed([artifact])
        if src_dirty and not art_dirty:
            pending.append((d['label'], artifact, d['rebuild'], src_dirty))

    if not stale and not pending:
        if not args.quiet:
            print('Index-Freshness OK: Corpus-Index, Authority-Index und '
                  'variants.xml sind mit dem Quellstand synchron.')
        return 0

    # --- Drift-Report (GitHub-Actions ::error Annotations) ---
    print('Index-/variants-Drift erkannt:', file=sys.stderr)
    print('', file=sys.stderr)
    for label, artifact, changed, rebuild in stale:
        print(f'  VERALTET: {label} ({artifact})', file=sys.stderr)
        print(f'    Quellen seit dem letzten Build geaendert ({len(changed)}):',
              file=sys.stderr)
        for f in changed[:12]:
            print(f'      - {f}', file=sys.stderr)
        if len(changed) > 12:
            print(f'      ... und {len(changed) - 12} weitere', file=sys.stderr)
        print(f'    Fix: {rebuild}  (danach committen)', file=sys.stderr)
        print(f'::error file={artifact}::{label} ist veraltet: '
              f'{len(changed)} Quelldatei(en) wurden nach dem letzten Build '
              f'geaendert. Rebuild: {rebuild}', file=sys.stderr)
    for label, artifact, rebuild, src_dirty in pending:
        print(f'  AUSSTEHEND (Working Tree): {label} ({artifact})', file=sys.stderr)
        print(f'    Uncommittete Quelländerungen ohne mitgebautes Artefakt '
              f'({len(src_dirty)}). Fix: {rebuild}', file=sys.stderr)
    print('', file=sys.stderr)
    print('Hinweis: Die Erkennung ist quelldatei-granular. Ein Flag bedeutet '
          '"eine Quelle hat sich seit dem letzten Build geaendert". Pruefe, ob '
          'die Aenderung ein indexiertes Feld betrifft (lemmaRef, <l>/<lg>, '
          'Tokentext), bevor ein Rebuild als zwingend gilt. Reine @corresp/@ana/'
          '@pos-, Header- oder Kommentar-Aenderungen beeinflussen den '
          'Corpus-Index nicht.', file=sys.stderr)
    print('', file=sys.stderr)
    print('Lifecycle: Quelle aendern, dann variants.xml regenerieren, dann '
          'Indexe rebuilden, dann Versions-Konstanten bumpen, alles in EINEM '
          'Commit. Siehe DATA-MODEL.md (Data-Change-Lifecycle).', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
