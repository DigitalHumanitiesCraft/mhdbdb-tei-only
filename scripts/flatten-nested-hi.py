#!/usr/bin/env python3
"""Flatten nested <hi>/<hi> in 143 TEI files.

Why: the schema's inline.model allows <hi> recursively, which contrib-
utes to non-linear RelaxNG matching on large mixed-content <p>-elements
(see split-prose-mega-p.py for the PL1/PL2/PL3 case). By eliminating
every nested <hi> in the data, we can tighten mhdbdb.rnc so that <hi>
can no longer contain another <hi>, removing the recursion.

Policy: "Daten vor Schema" (CLAUDE.md Hard Constraints).

The corpus has 36,924 nested-<hi> instances across 143 files (scan
2026-04-15). They fall into two groups:

  SIMPLE (36,498): <hi rend="A"><hi rend="B">X</hi></hi>
    → <hi rend="A B">X</hi>                       (in-place merge)

  COMPLEX (426):   <hi rend="A">[lb/pb/content + inner-<hi> + more]</hi>
    → extract milestones, then distribute outer rend over each child

Distribution strategy (complex case):
  - <lb/>, <pb/>, <cb/> children (empty milestones) are moved OUT of the
    outer as preceding siblings. They have no content, so a <hi> wrap
    around them is semantically meaningless.
  - For the remaining non-milestone children, the outer <hi> is dissolved:
    - Each child <hi rend="B"> gets its rend merged to "A B" and replaces
      the nesting.
    - Each <w>/<pc> child gets wrapped in a fresh <hi rend="A">.
  - The outer <hi> itself disappears; its children become siblings of
    each other at the outer's former position in the parent.

Semantic equivalence:
  <hi rend="initial">                  <lb/>
    <lb/>                     →        <hi rend="initial upper_case">X</hi>
    <hi rend="upper_case">X</hi>       <hi rend="initial">Y</hi>
    <w>Y</w>                           <hi rend="initial">Z</hi>
    <w>Z</w>
  </hi>

Both forms render X with BOTH 'initial' and 'upper_case', Y and Z with
'initial' alone — identical visual semantics.

Usage:
    python scripts/flatten-nested-hi.py --dry-run
    python scripts/flatten-nested-hi.py

Idempotency: a second run finds no nested <hi> and exits cleanly.

After successful run + validation: move to scripts/_archived/.
"""
import argparse
import glob
import io
import sys
from collections import Counter
from pathlib import Path
from lxml import etree

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'

MILESTONE_TAGS = {TEI + 'lb', TEI + 'pb', TEI + 'cb'}


def find_nested_hi(tree):
    """Return list of outer <hi> elements that contain at least one <hi> child."""
    return [hi for hi in tree.iter(TEI + 'hi') if hi.find(TEI + 'hi') is not None]


def is_flattenable(outer_hi):
    """Check whether the outer <hi> has exactly one element-child (the
    inner <hi>) and no significant text. Returns the inner <hi> or None."""
    if outer_hi.text and outer_hi.text.strip():
        return None
    children = list(outer_hi)
    if len(children) != 1:
        return None
    inner = children[0]
    if inner.tag != TEI + 'hi':
        return None
    if inner.tail and inner.tail.strip():
        return None
    return inner


def merge_rend(outer_rend, inner_rend):
    """Merge two @rend values into a whitespace-separated list, dedup'd."""
    a = outer_rend.split() if outer_rend else []
    b = inner_rend.split() if inner_rend else []
    merged = []
    for v in a + b:
        if v and v not in merged:
            merged.append(v)
    return ' '.join(merged)


def flatten_simple(outer_hi):
    """Simple in-place merge: <hi A><hi B>X</hi></hi> → <hi "A B">X</hi>.

    Returns True on success, False if outer is not simple-flattenable.
    """
    inner = is_flattenable(outer_hi)
    if inner is None:
        return False

    # Merge rends onto the outer (keeps parent/position/tail/namespace
    # context intact — no need to re-insert into parent).
    outer_rend = outer_hi.get('rend') or ''
    inner_rend = inner.get('rend') or ''
    outer_hi.set('rend', merge_rend(outer_rend, inner_rend))

    # Copy any non-rend attributes from inner that outer lacks
    for k, v in inner.attrib.items():
        if k == 'rend':
            continue
        if k not in outer_hi.attrib:
            outer_hi.set(k, v)

    # Move inner's content into outer, then drop inner
    outer_hi.text = inner.text
    outer_hi.remove(inner)
    for c in list(inner):
        outer_hi.append(c)
    return True


def flatten_complex(outer_hi):
    """Complex case: outer <hi> has >1 children or mixed content.

    Strategy:
      1. Milestone children (lb/pb/cb) are moved OUT of the outer as
         preceding siblings — they have no content and wrapping them
         in <hi> is semantically meaningless.
      2. For the remaining content:
         - If exactly one remains and it is a <hi>, do a simple merge
           (same effect as flatten_simple).
         - Otherwise, dissolve the outer: each child takes the outer's
           rend, distributed as follows:
             <hi rend="B"> children → merge rend to "A B", keep element
             <w>/<pc>/other  → wrap in new <hi rend="A">
         The outer <hi> is removed from the parent, and its new
         "children" become siblings at the outer's former position.

    Returns number of elements that replaced the outer (>=1), or 0 if
    the outer could not be processed (e.g., has significant text).
    """
    parent = outer_hi.getparent()
    if parent is None:
        return 0

    # If outer has significant text content, we cannot safely dissolve
    # (text would lose its <hi> wrap). Not observed in the current
    # corpus, but guard anyway.
    if outer_hi.text and outer_hi.text.strip():
        return 0

    outer_rend = outer_hi.get('rend') or ''
    outer_tail = outer_hi.tail
    outer_index = list(parent).index(outer_hi)

    # Detach all children from outer so we can reparent them cleanly
    children = list(outer_hi)
    for c in children:
        outer_hi.remove(c)

    # Partition into milestones vs content
    milestones = [c for c in children if c.tag in MILESTONE_TAGS]
    content = [c for c in children if c.tag not in MILESTONE_TAGS]

    # Clear tails on milestones since they'll sit at a new position;
    # the tails were whitespace between outer's children, not meaningful.
    for ms in milestones:
        ms.tail = None

    # Build the replacement element list
    new_elements = list(milestones)

    if len(content) == 0:
        # Only milestones inside — outer was just a decorative wrapper
        # around empty markers. Drop outer, keep milestones.
        pass
    elif len(content) == 1 and content[0].tag == TEI + 'hi':
        # After milestone extraction: simple merge into the single inner
        inner = content[0]
        inner_rend = inner.get('rend') or ''
        inner.set('rend', merge_rend(outer_rend, inner_rend))
        for k, v in list(inner.attrib.items()):
            pass  # already set
        inner.tail = None
        new_elements.append(inner)
    else:
        # Distribute outer rend over each content child
        for c in content:
            c.tail = None  # reset: was inter-child whitespace
            if c.tag == TEI + 'hi':
                inner_rend = c.get('rend') or ''
                c.set('rend', merge_rend(outer_rend, inner_rend))
                new_elements.append(c)
            else:
                # Wrap in a new <hi rend="outer_rend">
                new_hi = etree.Element(TEI + 'hi')
                new_hi.set('rend', outer_rend)
                new_hi.append(c)
                new_elements.append(new_hi)

    # Remove the now-empty outer and insert the new elements at its spot
    parent.remove(outer_hi)
    for i, el in enumerate(new_elements):
        parent.insert(outer_index + i, el)

    # Preserve outer's tail on the last new element so the document-flow
    # whitespace survives the edit.
    if new_elements and outer_tail is not None:
        new_elements[-1].tail = outer_tail

    return len(new_elements)


def process_file(tei_file, dry_run=False):
    """Process one file. Returns (n_found, n_simple, n_complex, n_skipped)."""
    try:
        tree = etree.parse(tei_file)
    except etree.XMLSyntaxError as e:
        print(f'  PARSE ERROR: {e}')
        return 0, 0, 0, 0

    if dry_run:
        nested = find_nested_hi(tree)
        if not nested:
            return 0, 0, 0, 0
        n_found = len(nested)
        n_simple = sum(1 for outer in nested if is_flattenable(outer) is not None)
        n_complex = n_found - n_simple
        return n_found, n_simple, n_complex, 0

    # Apply mode: gather all nested once, process each independently.
    # At depth 2 (the only depth currently observed) every nested case
    # is structurally isolated from every other, so a single pass
    # suffices and avoids the O(n²) cost of re-scanning the tree.
    # A small post-pass handles any residuals (depth > 2 safety).
    n_found = 0
    n_simple = 0
    n_complex = 0
    n_skip = 0

    def process_targets(targets):
        nonlocal n_found, n_simple, n_complex, n_skip
        for target in targets:
            # target might have been moved/removed by earlier processing
            # of an ancestor — skip if it no longer has nested children
            if target.find(TEI + 'hi') is None:
                continue
            n_found += 1
            if flatten_simple(target):
                n_simple += 1
                continue
            added = flatten_complex(target)
            if added > 0:
                n_complex += 1
                continue
            # Genuinely stuck — last-resort unwrap
            rend = target.get('rend')
            kids = [etree.QName(c.tag).localname for c in target]
            text = (target.text or '').strip()[:50]
            print(f'  SKIP (unhandled): <hi rend="{rend}"> with children {kids}, text="{text}"', flush=True)
            n_skip += 1
            parent = target.getparent()
            if parent is not None:
                idx = list(parent).index(target)
                ch = list(target)
                for c in ch:
                    target.remove(c)
                parent.remove(target)
                for i, c in enumerate(ch):
                    parent.insert(idx + i, c)

    # First pass: pick innermost first so depth-3 cases (if any) work
    initial = find_nested_hi(tree)
    innermost = [o for o in initial if o.find(TEI + 'hi').find(TEI + 'hi') is None]
    other = [o for o in initial if o not in innermost]
    process_targets(innermost + other)

    # Safety pass: any residuals (depth > 2) are picked up now
    residual_passes = 0
    while True:
        residuals = find_nested_hi(tree)
        if not residuals:
            break
        residual_passes += 1
        if residual_passes > 10:
            print(f'  WARNING: residual pass limit reached, {len(residuals)} nested left', flush=True)
            break
        process_targets(residuals)

    if (n_simple + n_complex) > 0:
        tree.write(tei_file, encoding='UTF-8', xml_declaration=True)
    return n_found, n_simple, n_complex, n_skip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='scan + report, no changes')
    ap.add_argument('--sample', nargs='+', help='limit to specific sigles')
    args = ap.parse_args()

    if args.sample:
        files = [f'tei/{s}.tei.xml' for s in args.sample]
        files = [f for f in files if Path(f).exists()]
    else:
        files = sorted(glob.glob('tei/*.tei.xml'))

    print(f'{"DRY-RUN" if args.dry_run else "APPLY"}: processing {len(files)} file(s)')
    print()

    total_found = 0
    total_simple = 0
    total_complex = 0
    total_skip = 0
    affected = 0
    for f in files:
        name = Path(f).stem.replace('.tei', '')
        n_found, n_simple, n_complex, n_skip = process_file(f, dry_run=args.dry_run)
        if n_found > 0:
            affected += 1
            label = f'{name}:'
            bits = [f'found={n_found}', f'simple={n_simple}', f'complex={n_complex}']
            if n_skip:
                bits.append(f'SKIP={n_skip}')
            print(f'{label:10s} ' + ' '.join(bits))
            total_found += n_found
            total_simple += n_simple
            total_complex += n_complex
            total_skip += n_skip

    print()
    verb = 'would process' if args.dry_run else 'processed'
    print(f'Done. {verb} {total_found} nested-<hi>(s) across {affected} file(s): '
          f'{total_simple} simple, {total_complex} complex, {total_skip} unhandled.')


if __name__ == '__main__':
    main()
