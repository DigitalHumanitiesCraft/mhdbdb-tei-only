#!/usr/bin/env python3
"""
Drop dead @corresp="variants.xml#type_-N" attributes from <w> elements (Issue #115).

The negative type-IDs are legacy MHDBDB punctuation type-codes, not orthographic
variants, and are not defined in variants.xml (they resolve to nothing):

    type_-7  -> '-'   (Trennstrich)     6,369 refs
    type_-10 -> '«'                      1,630 refs
    type_-11 -> '»'                      1,629 refs
    type_-15 -> '/'   (Virgel)           5,267 refs

These tokens carry no @lemmaRef, so removing them is irrelevant to position
counting. We strip only the dangling @corresp attribute; the <w>, its @xml:id,
@pos and text content stay (schema-valid: @corresp is optional on <w>, see
schema/mhdbdb.rnc).

Implementation note: byte-level regex replacement (no lxml round-trip) so that
line endings, attribute order and formatting stay byte-exact — only the matched
attribute disappears, keeping diffs minimal. The pattern requires the *whole*
@corresp value to be a single negative type-ID (closing quote right after the
digits); space-separated multi-value corresp would not match and is reported.

Usage:
    python scripts/audit/drop-negative-variant-corresp.py            # dry-run
    python scripts/audit/drop-negative-variant-corresp.py --apply    # write changes
"""

import io
import re
import sys
from collections import Counter
from pathlib import Path

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from corpus_files import TEI_DIR, corpus_files  # noqa: E402

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252,
# und Audit-Skripte geben Korpus- und Lexikonformen aus. Die MHG-Breven ŏ
# und ŭ liegen ausserhalb von cp1252, ein Treffer wuerde das Skript also an
# seiner eigenen Ausgabe toeten. Der Wrapper steht deshalb einheitlich in
# den Skripten, die Korpus- oder Lexikonformen ausgeben, nicht in allen 22.
# Wer eines ergaenzt, das solche Formen druckt, braucht ihn ebenfalls.
# Er deckt nur stdout; wer ueber stderr meldet, braucht ihn dort ebenso.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# ' corresp="variants.xml#type_-<digits>"' — leading space + whole-value match.
PATTERN = re.compile(rb' corresp="variants\.xml#type_-\d+"')
# Sanity guard: negative type-ID appearing inside a multi-value list (would be skipped).
MULTI_GUARD = re.compile(rb'corresp="[^"]*variants\.xml#type_-\d+[^"]*"')


def main():
    apply = '--apply' in sys.argv
    # Kein "run from repo root"-Guard mehr (#287): TEI_DIR haengt jetzt am
    # PROJECT_ROOT, das Skript ist damit CWD-unabhaengig.
    if not TEI_DIR.exists():
        print(f'Error: {TEI_DIR} not found')
        return 1

    files = corpus_files()
    total = 0
    touched = []
    skipped_multi = Counter()

    for fp in files:
        data = fp.read_bytes()
        # Detect multi-value occurrences that the strict pattern would not remove.
        multi = len(MULTI_GUARD.findall(data)) - len(PATTERN.findall(data))
        if multi > 0:
            skipped_multi[fp.name] += multi

        new, n = PATTERN.subn(b'', data)
        if n:
            total += n
            touched.append((fp.name, n))
            if apply:
                fp.write_bytes(new)

    mode = 'APPLIED' if apply else 'DRY-RUN (no files written)'
    print('=' * 60)
    print(f'Drop negative-type @corresp on <w>  [{mode}]')
    print('=' * 60)
    print(f'Files touched:        {len(touched)}')
    print(f'Attributes removed:   {total:,}')
    print()
    print('Top 12 files by removals:')
    for name, n in sorted(touched, key=lambda x: -x[1])[:12]:
        print(f'  {name:16} {n:>6}')

    if skipped_multi:
        print('\n!! WARNING: multi-value @corresp containing a negative type-ID '
              '(NOT removed — needs manual review):')
        for name, c in skipped_multi.most_common():
            print(f'  {name:16} {c:>6}')
    else:
        print('\nNo multi-value @corresp with negative type-IDs (clean single-value set).')

    if not apply:
        print('\nDry-run only. Re-run with --apply to write changes.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
