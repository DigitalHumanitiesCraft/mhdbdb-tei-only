#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Static JSON API

Emits a static, deterministic JSON API into api/ from the two pre-built
indexes (data/authority-index.json.gz + data/corpus-index.json.gz).
Frontend-only project: the "API" is plain files served by GitHub Pages,
there is no backend.

Output tree:
  api/index.json                  Root manifest (collections + source versions)
  api/lemmata/index.json          Full lemma records as one bundle (43k+ records,
                                  no individual files — the bundle IS the API)
  api/<coll>/index.json           Summary list (persons, works, concepts,
                                  genres, names, texts)
  api/<coll>/{id}.json            Full individual record + license key

Transformations:
  - persons: 'works' comma-string → JSON array ("work_4,work_36" → [...])
  - texts: heavy keys (words, lemmata, lineStarts, lineEnds) stripped
  - every emitted file carries "license": "CC BY-NC-SA 4.0"

Determinismus (#125-Prinzip): keine Zeitstempel, keine Randomness, Iteration
strikt in Index-Listen-Reihenfolge, kompaktes json.dumps — gleicher Index-
Stand → byte-identischer Output. Vor dem Schreiben werden ALLE api/**/*.json
gelöscht (Orphan-Schutz); Nicht-JSON-Dateien wie api/index.html bleiben
unangetastet.

Usage:
    python scripts/build-api.py [--allow-dirty]
"""

import argparse
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
API_DIR = PROJECT_ROOT / 'api'
AUTHORITY_INDEX_FILE = DATA_DIR / 'authority-index.json.gz'
CORPUS_INDEX_FILE = DATA_DIR / 'corpus-index.json.gz'

LICENSE = 'CC BY-NC-SA 4.0'
CONTACT = 'mhdbdb@plus.ac.at'

# ID-Muster: Windows-FS ist case-insensitiv, deshalb zusätzlich der
# Eindeutigkeits-Check in assert_ids() — zwei IDs, die sich nur in
# Groß-/Kleinschreibung unterscheiden, würden dieselbe Datei überschreiben.
# Bindestrich erlaubt: 3 Werke tragen UUID-IDs aus der RDF-Migration
# (work_f1576278-..., work_c7da236c-..., work_b4cc20a0-...); FS-/URL-sicher.
AUTHORITY_ID_RE = re.compile(r'^[a-z]+_[A-Za-z0-9-]+$')  # work_WZB ist gültig
TEXT_ID_RE = re.compile(r'^[A-Z0-9]+$')

# Schwere Korpus-Felder, die nicht in die per-Text-API gehören
TEXT_STRIP_KEYS = ('words', 'lemmata', 'lineStarts', 'lineEnds')


def check_working_tree(directory, allow_dirty):
    """Pre-flight check (Muster #100, wie build-authority-index.py):
    data/ muss sauber sein — modifizierte ODER untracked Index-Dateien
    würden sonst still in die API einfließen."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', '--', str(directory)],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  git status check skipped: {e}")
        return

    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    if not lines:
        return

    untracked = [ln for ln in lines if ln.startswith('??')]
    modified = [ln for ln in lines if not ln.startswith('??')]

    print(f"⚠️  Working tree under {directory}/ is not clean:")
    print(f"   {len(untracked)} untracked, {len(modified)} modified/staged")
    for ln in lines[:10]:
        print(f"     {ln}")
    if len(lines) > 10:
        print(f"     ... +{len(lines) - 10} more")

    if allow_dirty:
        print("   --allow-dirty set, continuing anyway.")
    else:
        sys.exit(
            "Refusing to build the API from a possibly-inconsistent index state.\n"
            "Commit/stash the changes above, or pass --allow-dirty for local tests."
        )


def load_index(path):
    """Load a pre-built .json.gz index."""
    if not path.exists():
        sys.exit(f"❌ ERROR: {path} not found — run the index builders first.")
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def clean_api_dir():
    """Orphan-Schutz: alle bestehenden JSON-Dateien unter api/ löschen,
    damit gelöschte Records keine Datei-Leichen hinterlassen. Nicht-JSON
    (api/index.html etc.) bleibt unangetastet.
    Symlinks werden übersprungen (expliziter Guard; Python-3.13-rglob
    traversiert keine Symlink-Dirs, aber Files könnten Symlinks sein).
    Nach dem Löschen werden leere Unterverzeichnisse bottom-up entfernt,
    damit umbenannte/weggefallene Collections keine leeren Dirs
    hinterlassen."""
    if not API_DIR.exists():
        return 0
    removed = 0
    for json_file in sorted(API_DIR.rglob('*.json')):
        if json_file.is_symlink():
            continue
        json_file.unlink()
        removed += 1
    # leere Unterverzeichnisse bottom-up (rmdir wirft bei nicht-leer)
    for subdir in sorted(API_DIR.rglob('*'), reverse=True):
        if subdir.is_symlink() or not subdir.is_dir():
            continue
        try:
            subdir.rmdir()
        except OSError:
            pass
    return removed


def assert_ids(collection_name, ids, pattern):
    """ID-Validierung: Muster + case-insensitive Eindeutigkeit
    (Windows-FS-Kollisionsschutz)."""
    for record_id in ids:
        if not pattern.match(record_id):
            print(f"❌ ERROR: invalid id in {collection_name}: {record_id!r} "
                  f"(expected pattern {pattern.pattern})")
            sys.exit(1)
    seen = {}
    for record_id in ids:
        lowered = record_id.lower()
        if lowered in seen:
            print(f"❌ ERROR: case-insensitive id collision in {collection_name}: "
                  f"{seen[lowered]!r} vs {record_id!r} (would collide on Windows)")
            sys.exit(1)
        seen[lowered] = record_id


def record_id(rec, coll):
    """ID eines Records mit klarer Fehlermeldung statt nacktem KeyError."""
    if 'id' not in rec:
        sys.exit(f"❌ ERROR: record in {coll!r} missing 'id' key: {rec!r}")
    return rec['id']


def validate_all_ids(authority, corpus):
    """Wipe-Safety: Alle Collections vollständig validieren BEVOR
    clean_api_dir() läuft — ein ungültiger ID darf das bestehende api/
    nicht erst zerstören und dann abbrechen."""
    for coll in ('lemmata', 'persons', 'works', 'concepts', 'genres', 'names'):
        assert_ids(coll, [record_id(rec, coll) for rec in authority[coll]], AUTHORITY_ID_RE)
    assert_ids('texts', [record_id(rec, 'texts') for rec in corpus['texts']], TEXT_ID_RE)


def write_json(path, obj):
    """Write compact deterministic JSON, return byte count."""
    data = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    path.write_bytes(data)
    return len(data)


def parse_person_works(value):
    """persons.works: Komma-String oder null → JSON-Array.
    "work_4,work_36" → ["work_4","work_36"], null/leer → []."""
    if not value:
        return []
    return [w for w in (part.strip() for part in value.split(',')) if w]


def write_collection(name, records, summarize, transform=None):
    """Write api/<name>/{id}.json per record + api/<name>/index.json.
    Records werden als neue Dicts gebaut — der geladene Index wird nie
    mutiert. ID-Validierung passiert vorab in validate_all_ids() (vor dem
    Wipe). License wird immer hier gesetzt, unabhängig vom transform —
    transform-Autoren müssen nicht daran denken.
    Returns (file_count, byte_count)."""
    coll_dir = API_DIR / name
    coll_dir.mkdir(parents=True, exist_ok=True)

    files = 0
    total_bytes = 0
    summaries = []
    for rec in records:
        base = transform(rec) if transform else dict(rec)
        out = {**base, 'license': LICENSE}
        total_bytes += write_json(coll_dir / f"{rec['id']}.json", out)
        files += 1
        summaries.append(summarize(rec))

    total_bytes += write_json(coll_dir / 'index.json',
                              {'license': LICENSE, 'items': summaries})
    files += 1
    return files, total_bytes


def build_api(authority, corpus):
    """Build the full api/ tree. Returns per-collection stats."""
    # Explizites mkdir, damit der Root-Manifest-Write nicht vom
    # mkdir-Side-Effect einer anderen Section abhängt (z.B. frischer Clone).
    API_DIR.mkdir(exist_ok=True)

    stats = {}  # collection → (files, bytes)

    # --- lemmata: nur Bundle, keine Einzeldateien (43k+ Records) ---
    lemmata = authority['lemmata']
    lemmata_dir = API_DIR / 'lemmata'
    lemmata_dir.mkdir(parents=True, exist_ok=True)
    n = write_json(lemmata_dir / 'index.json',
                   {'license': LICENSE, 'items': lemmata})
    stats['lemmata'] = (1, n)
    print(f"   lemmata:  1 file (bundle, {len(lemmata):,} records)")

    # --- persons (mit works-Normalisierung) ---
    stats['persons'] = write_collection(
        'persons', authority['persons'],
        summarize=lambda r: {'id': r['id'], 'preferredName': r['preferredName']},
        transform=lambda r: {**r, 'works': parse_person_works(r.get('works'))},
    )
    print(f"   persons:  {stats['persons'][0]} files")

    # --- works ---
    stats['works'] = write_collection(
        'works', authority['works'],
        summarize=lambda r: {'id': r['id'], 'title': r['title'], 'sigle': r.get('sigle')},
    )
    print(f"   works:    {stats['works'][0]} files")

    # --- concepts, genres, names (gleiches Summary-Schema) ---
    for coll in ('concepts', 'genres', 'names'):
        stats[coll] = write_collection(
            coll, authority[coll],
            summarize=lambda r: {'id': r['id'], 'termDE': r['termDE'],
                                 'termEN': r.get('termEN')},
        )
        print(f"   {coll + ':':9s} {stats[coll][0]} files")

    # --- texts (Korpus-Index, schwere Felder gestrippt) ---
    stats['texts'] = write_collection(
        'texts', corpus['texts'],
        summarize=lambda r: {'id': r['id'], 'title': r['title'],
                             'author': r['author'], 'wordCount': r['wordCount']},
        transform=lambda r: {k: v for k, v in r.items() if k not in TEXT_STRIP_KEYS},
    )
    print(f"   texts:    {stats['texts'][0]} files")

    # --- Root-Manifest ---
    collections = {}
    for coll in ('lemmata', 'persons', 'works', 'concepts', 'genres', 'names'):
        collections[coll] = {'href': f'{coll}/index.json',
                             'count': len(authority[coll])}
    collections['texts'] = {'href': 'texts/index.json', 'count': len(corpus['texts'])}

    manifest = {
        'project': 'MHDBDB',
        'license': LICENSE,
        'contact': CONTACT,
        'documentation': 'index.html',
        'sources': {
            'authorityIndex': authority['version'],
            'corpusIndex': corpus['version'],
        },
        'collections': collections,
    }
    n = write_json(API_DIR / 'index.json', manifest)
    stats['root'] = (1, n)
    print(f"   root:     1 file (manifest)")

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build static JSON API in api/ from the pre-built indexes")
    parser.add_argument(
        '--allow-dirty', action='store_true',
        help="Build even if data/ has untracked or modified files (use for local tests)."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MHDBDB Static API Builder")
    print("=" * 60)

    check_working_tree(DATA_DIR.relative_to(PROJECT_ROOT), args.allow_dirty)

    try:
        print(f"\n📖 Loading {AUTHORITY_INDEX_FILE.name}...")
        authority = load_index(AUTHORITY_INDEX_FILE)
        print(f"   Version {authority['version']}")
        print(f"📖 Loading {CORPUS_INDEX_FILE.name}...")
        corpus = load_index(CORPUS_INDEX_FILE)
        print(f"   Version {corpus['version']}, {corpus['totalTexts']} texts")

        # Wipe-Safety: Alle IDs validieren VOR dem Wipe — ein Validierungs-
        # fehler darf das bestehende api/ nicht erst zerstören.
        print(f"\n🔍 Validating IDs (pre-wipe)...")
        validate_all_ids(authority, corpus)
        print(f"   IDs OK")

        removed = clean_api_dir()
        if removed:
            print(f"\n🧹 Removed {removed} existing JSON files under api/")

        print(f"\n🔨 Writing API to {API_DIR}...")
        stats = build_api(authority, corpus)

        total_files = sum(f for f, _ in stats.values())
        total_bytes = sum(b for _, b in stats.values())
        print(f"\n📊 Summary:")
        for coll, (files, nbytes) in stats.items():
            print(f"   {coll:9s} {files:5d} files  {nbytes / 1024:10.1f} KB")
        print(f"   {'TOTAL':9s} {total_files:5d} files  {total_bytes / (1024 * 1024):8.2f} MB")
        print(f"\n✅ Static API built successfully!")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
