#!/usr/bin/env python3
"""Add <?xml-model?> PIs to all 666 tei/*.tei.xml files (P2-15).

Inserts two processing instructions directly after the <?xml?>-
declaration so XML editors (oXygen, VS Code Scholarly XML, Emacs
nxml-mode) get Live-Validation + Code-Completion against both our
custom schema and tei_all.rng without running jing manually.

Target shape (first 4 lines of each file):

    <?xml version='1.0' encoding='UTF-8'?>
    <?xml-model href="../schema/mhdbdb.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
    <?xml-model href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="...">

Authority-Files und Examples haben diese PIs bereits (Commit 9cda50c44).
Hier geht es um die 666 Korpus-Dateien.

Usage:
    python scripts/add-xml-model-pi.py --dry-run            # scan + report
    python scripts/add-xml-model-pi.py --sample ABG PUC     # limit to sigles
    python scripts/add-xml-model-pi.py                      # apply to all

Idempotency: skips files that already contain an `xml-model` PI (sub-
string check). A second run is a no-op.

After successful run + verification: move to scripts/_archived/.
"""
import argparse
import glob
import io
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

PI1 = '<?xml-model href="../schema/mhdbdb.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
PI2 = '<?xml-model href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"?>'


def process_file(path, dry_run=False):
    """Return one of 'added', 'skipped', 'error' after processing.

    Reads + writes in BINARY mode so no newline translation happens —
    on Windows, the default Path.write_text() converts \\n to \\r\\n,
    which changes every line of the file and produces a 14M-line diff
    instead of the expected 2-lines-per-file change.
    """
    try:
        raw = path.read_bytes()
    except Exception as e:
        print(f'  ERROR reading {path.name}: {e}')
        return 'error'

    if b'xml-model' in raw:
        return 'skipped'  # idempotent — already has the PI

    # Detect the native newline byte sequence used in THIS file.
    # TEI corpus files here use LF (\n), but we detect dynamically so
    # the script stays portable to any line-ending convention.
    if b'\r\n' in raw:
        newline = b'\r\n'
    else:
        newline = b'\n'

    # Find end of the <?xml ?> declaration line (up to and including its
    # newline). Insert the two PI lines directly after.
    nl_idx = raw.find(newline)
    if nl_idx < 0:
        print(f'  ERROR: {path.name} has no line break after <?xml ?>')
        return 'error'

    first_line = raw[: nl_idx + len(newline)]
    if not first_line.lstrip().startswith(b'<?xml '):
        print(f'  ERROR: {path.name} does not start with <?xml ?>: {first_line[:80]!r}')
        return 'error'

    insert = PI1.encode('utf-8') + newline + PI2.encode('utf-8') + newline
    new_raw = first_line + insert + raw[nl_idx + len(newline):]

    if dry_run:
        return 'added'  # would be added

    path.write_bytes(new_raw)
    return 'added'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='scan + report, no changes')
    ap.add_argument('--sample', nargs='+', help='limit to given sigles (without .tei.xml)')
    args = ap.parse_args()

    if args.sample:
        files = [Path(f'tei/{s}.tei.xml') for s in args.sample]
        files = [f for f in files if f.exists()]
    else:
        files = [Path(f) for f in sorted(glob.glob('tei/*.tei.xml'))]

    print(f'{"DRY-RUN" if args.dry_run else "APPLY"}: processing {len(files)} file(s)')

    n_added = 0
    n_skipped = 0
    n_error = 0
    for f in files:
        result = process_file(f, dry_run=args.dry_run)
        if result == 'added':
            n_added += 1
        elif result == 'skipped':
            n_skipped += 1
        else:
            n_error += 1

    verb = 'would add' if args.dry_run else 'added'
    print(f'Done. {verb} PIs to {n_added} file(s), skipped {n_skipped}, errors {n_error}.')


if __name__ == '__main__':
    main()
