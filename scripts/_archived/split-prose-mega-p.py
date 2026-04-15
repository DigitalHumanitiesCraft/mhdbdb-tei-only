#!/usr/bin/env python3
"""Split mega-<p> elements in prose files at <pb/> milestones.

One-shot data consolidation. Background: PL1/PL2/PL3 (Prosa-Lancelot)
carry the entire body in a single <p> with 240,000–404,000 direct
children, which pushes lxml.etree.RelaxNG into 51s–339s per file.
Files with a single <p> of <= 100k children validate in under 10s.

Policy — "Daten vor Schema" (CLAUDE.md Hard Constraints): we fix the
data structure instead of loosening schema/mhdbdb.rnc. Splitting at
<pb/> is semantically natural for prose manuscripts: one <p> per
manuscript page.

Usage:
    python scripts/split-prose-mega-p.py --dry-run           # scan + report
    python scripts/split-prose-mega-p.py --dry-run --all     # also report subcritical
    python scripts/split-prose-mega-p.py --sample PL1        # limit to one file
    python scripts/split-prose-mega-p.py                     # apply to all over threshold

Idempotency: after a run, the mega-<p> is gone (replaced by N small
<p>s), so a second run finds nothing to do and exits cleanly.

After successful run + validation, move this script to scripts/_archived/
analogous to the #32-migration scripts.
"""
import argparse
import glob
import io
import sys
from pathlib import Path
from lxml import etree

# Windows default console is cp1252; force UTF-8 so non-ASCII chars print.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
NS = {'t': TEI_NS}

# Threshold for "critical" mega-<p> — above this, validation slows down
# dramatically. Based on empirical profiling 2026-04-15:
#   OVG   98,595 children → 7.5s  (acceptable)
#   PL3  239,393 children → 51s   (too slow)
#   PL2  370,830 children → 306s  (catastrophic)
#   PL1  403,981 children → 339s  (catastrophic)
CRITICAL_THRESHOLD = 100_000

# Report threshold — for the --all dry-run flag, list all <p> over this
# many children so we see the full picture.
REPORT_THRESHOLD = 1_000


def find_mega_ps(tree, threshold):
    """Return list of <p> elements with more than `threshold` direct children."""
    return [p for p in tree.iter(TEI + 'p') if len(p) > threshold]


def split_at_pb(big_p):
    """Split one big <p> into multiple <p>s at <pb/> milestones.

    Returns the number of new <p>s created, or 0 if the split could not
    be performed (no <pb/> found).

    The split inserts the new <p>s as siblings of the original, at the
    same position in the parent, then removes the original <p>. All
    child elements and their tails are moved (not copied), so no data
    is lost.

    Each new <p>:
      - inherits the original's attributes (except @n, which is set from
        the <pb/>'s @n value)
      - starts with its triggering <pb/> as the first child
      - contains all children up to (but not including) the next <pb/>

    Content before the first <pb/> (including the original <p>'s text
    node) becomes the first new <p>, without an @n attribute.
    """
    TEI_P = TEI + 'p'
    TEI_PB = TEI + 'pb'

    parent = big_p.getparent()
    if parent is None:
        return 0

    children = list(big_p)
    pb_indices = [i for i, c in enumerate(children) if c.tag == TEI_PB]
    if not pb_indices:
        return 0

    original_text = big_p.text
    original_tail = big_p.tail
    original_attrs = dict(big_p.attrib)
    original_index = list(parent).index(big_p)

    # Strip <p>'s children from the tree first so we can rebuild
    # cleanly. Children are still referenced in `children` list.
    for c in children:
        big_p.remove(c)

    # Build segments
    # Segment 0 (optional): text + children before first <pb/>
    # Segment i (1..n): starts with <pb/>, runs until next <pb/> or end
    segments = []  # each: (pb_n_or_None, text_or_None, list_of_elements)
    first_pb_i = pb_indices[0]
    if first_pb_i > 0 or (original_text and original_text.strip()):
        segments.append((None, original_text, children[:first_pb_i]))
    for idx, pb_i in enumerate(pb_indices):
        next_pb_i = pb_indices[idx + 1] if idx + 1 < len(pb_indices) else len(children)
        pb_elem = children[pb_i]
        pb_n = pb_elem.get('n')
        seg_children = children[pb_i:next_pb_i]
        segments.append((pb_n, None, seg_children))

    # Create and insert new <p>s
    new_ps = []
    for pb_n, text, seg_children in segments:
        new_p = etree.SubElement(parent, TEI_P)
        # copy original attrs except @n (we overwrite with pb @n)
        for k, v in original_attrs.items():
            if k != 'n':
                new_p.set(k, v)
        if pb_n:
            new_p.set('n', pb_n)
        if text is not None:
            new_p.text = text
        for c in seg_children:
            new_p.append(c)
        new_ps.append(new_p)

    # SubElement inserted at the end; move the new_ps to the right place
    # (original_index) and remove big_p.
    parent.remove(big_p)
    # Move new_ps into the right slot: remove + re-insert in order.
    for np in reversed(new_ps):
        parent.remove(np)
    for i, np in enumerate(new_ps):
        parent.insert(original_index + i, np)

    # Preserve the tail of the original <p>
    if original_tail is not None and new_ps:
        new_ps[-1].tail = original_tail

    return len(new_ps)


def process_file(tei_file, dry_run=False):
    """Process one TEI file. Returns (n_split, n_new_ps) for the split count."""
    try:
        tree = etree.parse(tei_file)
    except etree.XMLSyntaxError as e:
        print(f'  PARSE ERROR: {e}')
        return 0, 0

    mega = find_mega_ps(tree, CRITICAL_THRESHOLD)
    if not mega:
        return 0, 0

    n_split = 0
    n_new = 0
    for big_p in mega:
        n_children = len(big_p)
        if dry_run:
            pb_count = sum(1 for c in big_p if c.tag == TEI + 'pb')
            print(f'  WOULD SPLIT: <p> with {n_children:,} children, {pb_count} <pb/> inside')
            n_split += 1
            n_new += pb_count + 1  # estimate
            continue
        new_count = split_at_pb(big_p)
        if new_count == 0:
            print(f'  SKIP: <p> with {n_children:,} children has no <pb/> — cannot split')
            continue
        print(f'  SPLIT: <p>({n_children:,} children) → {new_count} new <p>')
        n_split += 1
        n_new += new_count

    if n_split > 0 and not dry_run:
        tree.write(tei_file, encoding='UTF-8', xml_declaration=True)
    return n_split, n_new


def report_all(tei_file):
    """Dry-run-extra: report any <p> over REPORT_THRESHOLD (not just critical)."""
    try:
        tree = etree.parse(tei_file)
    except etree.XMLSyntaxError:
        return []
    hits = []
    for p in tree.iter(TEI + 'p'):
        if len(p) > REPORT_THRESHOLD:
            pb_count = sum(1 for c in p if c.tag == TEI + 'pb')
            hits.append((len(p), pb_count))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='scan + report, do not modify')
    ap.add_argument('--sample', nargs='+', help='limit to specific sigles (without .tei.xml)')
    ap.add_argument('--all', action='store_true', help='with --dry-run: report all <p> over 1k children')
    args = ap.parse_args()

    if args.sample:
        files = [f'tei/{s}.tei.xml' for s in args.sample]
        files = [f for f in files if Path(f).exists()]
        if not files:
            print('No matching files.', file=sys.stderr)
            sys.exit(1)
    else:
        files = sorted(glob.glob('tei/*.tei.xml'))

    print(f'{"DRY-RUN" if args.dry_run else "APPLY"}: processing {len(files)} file(s), '
          f'threshold = {CRITICAL_THRESHOLD:,} children per <p>')
    print()

    # Optional: report all files with subcritical mega-<p>s
    if args.dry_run and args.all:
        print('=== All files with any <p> over report threshold ===')
        subcritical = []
        for f in files:
            hits = report_all(f)
            for n_children, n_pb in hits:
                subcritical.append((n_children, n_pb, Path(f).name))
        subcritical.sort(reverse=True)
        for n_children, n_pb, name in subcritical:
            marker = ' ← CRITICAL' if n_children > CRITICAL_THRESHOLD else ''
            print(f'  {n_children:>10,} children / {n_pb:>5} <pb/>  {name}{marker}')
        print()
        print(f'=== Critical files (> {CRITICAL_THRESHOLD:,}) ===')

    total_split = 0
    total_new = 0
    total_files = 0
    for f in files:
        name = Path(f).name
        n_split, n_new = process_file(f, dry_run=args.dry_run)
        if n_split > 0:
            total_files += 1
            print(f'{name}: {n_split} mega-<p>(s), {n_new} new <p>(s)')
            total_split += n_split
            total_new += n_new

    print()
    verb = 'would split' if args.dry_run else 'split'
    print(f'Done. {verb} {total_split} mega-<p>(s) across {total_files} file(s) '
          f'into {total_new} new <p>(s).')


if __name__ == '__main__':
    main()
