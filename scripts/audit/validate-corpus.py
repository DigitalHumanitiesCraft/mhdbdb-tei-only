#!/usr/bin/env python3
"""Full two-stage RelaxNG validation for the MHDBDB corpus + authority files.

Runs each file against:
  Stage 1: tei_all.rng            (TEI P5 conformance)
  Stage 2: mhdbdb.rng              (corpus files only)
           mhdbdb-authority.rng    (authority files only)
           — whichever matches the file's location.

Python-native via lxml.etree.RelaxNG — no jing/java dependency. The
former version of this script only did structural Python assertions
because it was written before we knew lxml could handle RELAX NG
natively, and before we had the .rng files generated via rnc2rng.
Those assertions are now redundant with mhdbdb.rng itself, so they
are retired.

## Removed structural Python checks (history)

The pre-2026-04-15 version of this script performed these custom
Python-level assertions in addition to a well-formedness check:

  * Non-standard attributes: `@meaningRef` / `@wordRef` on `<w>`
  * `div/@type` whitelist (chapter, section, number, song, parallel,
    colophon, recipe)
  * `<suppplied>` typo detection (should be `<supplied>`)
  * `<seg type="pc">` forbidden (should be `<pc>`)
  * `<l>` forbidden in the 18 prose files listed in PROSE_SIGLES

All five checks are now enforced by schema/mhdbdb.rnc itself:

  * Non-standard attributes — excluded from the `w` pattern
  * `div/@type` — Enum in the `div` pattern
  * `<supplied>` — element is explicitly named (a typo-variant would
    fail the Stage-1 tei_all check as an unknown element)
  * `<pc>` — explicit element, no `seg type="pc"` accepted
  * Prose files — structurally enforced via the mixed-content model
    plus the GAP comments in mhdbdb.rnc

If a future migration reintroduces any of these patterns and fails to
update the schema, the existing Stage-2 validation will catch it.
Adding a parallel Python-only "strict mode" would duplicate logic and
drift over time. If a new invariant is discovered that RelaxNG cannot
express (e.g., a cross-file constraint like `@lemmaRef` pointing at a
real lemma in lexicon.xml), that should become a Stage-3 check — not
something bolted onto this validator. See docs/DECISIONS.MD ADR-013
for the "Daten vor Schema" policy and docs/features/032-schema-followup.md
P3 section for Schematron candidates.

Usage:
    python scripts/audit/validate-corpus.py                      # all 667 + 8
    python scripts/audit/validate-corpus.py --sample ABG PUC     # specific sigles
    python scripts/audit/validate-corpus.py --corpus-only        # skip authority
    python scripts/audit/validate-corpus.py --authority-only     # skip corpus
    python scripts/audit/validate-corpus.py --fail-fast          # stop on first fail

Exit code: 0 if no Stage-2 failures, 1 otherwise. Stage-1 failures
count against the known #30-baseline (docs/TEI-MODEL.md §10) and do
NOT fail the run by themselves — that baseline is documented and
represents deliberate GAP patterns the custom schema accepts.
"""
import argparse
import glob
import io
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from lxml import etree

SCHEMA_TEI_ALL = 'schema/tei_all.rng'
SCHEMA_MHDBDB = 'schema/mhdbdb.rng'
SCHEMA_MHDBDB_AUTH = 'schema/mhdbdb-authority.rng'

# Known #30-baseline: 30 corpus files that are intentionally not
# strict-tei_all-valid because they contain patterns documented as
# GAPs in mhdbdb.rnc. They are listed in TEI-MODEL.md §10.
KNOWN_TEI_ALL_BASELINE_COUNT = 30


def load_schemas():
    tei_all = etree.RelaxNG(etree.parse(SCHEMA_TEI_ALL))
    mhdbdb = etree.RelaxNG(etree.parse(SCHEMA_MHDBDB))
    auth = etree.RelaxNG(etree.parse(SCHEMA_MHDBDB_AUTH))
    return tei_all, mhdbdb, auth


def validate_one(path, tei_all, stage2_schema, stage2_name):
    """Return (ok_s1, ok_s2, stage2_err_string_or_None)."""
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError as e:
        return False, False, f'NOT WELL-FORMED: {e}'
    ok1 = tei_all.validate(tree)
    ok2 = stage2_schema.validate(tree)
    err = None
    if not ok2:
        err = '; '.join(str(e)[:200] for e in list(stage2_schema.error_log)[:2])
    return ok1, ok2, err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', nargs='+', help='limit to specific sigles')
    ap.add_argument('--corpus-only', action='store_true', help='skip authority-files/')
    ap.add_argument('--authority-only', action='store_true', help='skip tei/')
    ap.add_argument('--fail-fast', action='store_true', help='stop on first stage-2 fail')
    args = ap.parse_args()

    print('Loading schemas...')
    try:
        tei_all, mhdbdb, auth = load_schemas()
    except Exception as e:
        print(f'ERROR loading schemas: {e}', file=sys.stderr)
        sys.exit(2)

    # Build the work list
    files = []  # list of (path, stage2_schema, stage2_label)
    if args.sample:
        for s in args.sample:
            p_corpus = Path(f'tei/{s}.tei.xml')
            p_auth = Path(f'authority-files/{s}.xml')
            if p_corpus.exists():
                files.append((p_corpus, mhdbdb, 'mhdbdb'))
            elif p_auth.exists():
                files.append((p_auth, auth, 'mhdbdb-authority'))
            else:
                print(f'  MISSING: {s}')
    else:
        if not args.authority_only:
            for f in sorted(glob.glob('tei/*.tei.xml')):
                files.append((Path(f), mhdbdb, 'mhdbdb'))
        if not args.corpus_only:
            for f in sorted(glob.glob('authority-files/*.xml')):
                files.append((Path(f), auth, 'mhdbdb-authority'))

    if not files:
        print('Nothing to validate.', file=sys.stderr)
        sys.exit(2)

    print(f'Validating {len(files)} file(s)...')

    n_ok = 0
    n_s1_fail = 0
    n_s2_fail = 0
    s2_fails = []  # (path, stage2_name, err)
    s1_fail_files = []
    t0 = time.time()

    for i, (path, s2_schema, s2_name) in enumerate(files, 1):
        if i % 100 == 0:
            print(f'  {i}/{len(files)} (elapsed {time.time() - t0:.0f}s)')
        ok1, ok2, err = validate_one(path, tei_all, s2_schema, s2_name)
        if ok1 and ok2:
            n_ok += 1
        if not ok1:
            n_s1_fail += 1
            s1_fail_files.append(path.name)
        if not ok2:
            n_s2_fail += 1
            s2_fails.append((path.name, s2_name, err))
            if args.fail_fast:
                break

    elapsed = time.time() - t0
    print()
    print(f'DONE in {elapsed:.0f}s')
    print(f'  Fully valid:        {n_ok}/{len(files)}')
    print(f'  Stage-1 fails:      {n_s1_fail}  (known baseline: {KNOWN_TEI_ALL_BASELINE_COUNT} corpus files)')
    print(f'  Stage-2 fails:      {n_s2_fail}')

    # Baseline check only makes sense for the full corpus run — on a
    # --sample or --corpus-only/--authority-only subset the number
    # naturally differs and a warning would be noise.
    is_full_run = not (args.sample or args.corpus_only or args.authority_only)
    if is_full_run and n_s1_fail != KNOWN_TEI_ALL_BASELINE_COUNT:
        delta = n_s1_fail - KNOWN_TEI_ALL_BASELINE_COUNT
        marker = 'ABOVE baseline' if delta > 0 else 'below baseline'
        print(f'  WARN: stage-1 count {marker} by {abs(delta)}')
        if s1_fail_files:
            print(f'  s1-fail files: {s1_fail_files[:20]}')

    if s2_fails:
        print()
        print('Stage-2 failures (these break the build):')
        for name, stage, err in s2_fails[:20]:
            print(f'  {name}  ({stage})')
            if err:
                print(f'    {err}')

    sys.exit(1 if n_s2_fail > 0 else 0)


if __name__ == '__main__':
    main()
