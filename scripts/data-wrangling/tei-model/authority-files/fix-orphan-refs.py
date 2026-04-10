#!/usr/bin/env python3
"""
Phase I1: Remove orphaned references in variants.xml and lexicon.xml

1. variants.xml: Remove <entry> elements whose @corresp points to non-existent lemmata
   in lexicon.xml (154 entries)
2. lexicon.xml: Remove <ptr> elements whose @target points to non-existent concepts
   in concepts.xml (61 ptrs)
3. lexicon.xml: Remove <seg> elements whose @corresp points to non-existent lemmata
   in lexicon.xml (10 segs, etymology cross-refs)

Usage:
    python scripts/data-wrangling/tei-model/authority-files/fix-orphan-refs.py [--dry-run]
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from lxml import etree

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

AUTH_DIR = Path('authority-files')


def collect_ids(tree, tag_filter=None):
    """Collect all xml:id values from a tree, optionally filtered by tag."""
    ids = set()
    root = tree.getroot()
    for elem in root.iter():
        eid = elem.get(XML_ID)
        if eid:
            if tag_filter is None or etree.QName(elem.tag).localname == tag_filter:
                ids.add(eid)
    return ids


def fix_variants(variants_file, lemma_ids, dry_run):
    """Remove <entry> elements with @corresp pointing to non-existent lemmata."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(variants_file), parser)
    root = tree.getroot()

    orphans = []
    for entry in root.findall(f'.//{TEI}entry[@corresp]'):
        corresp = entry.get('corresp', '')
        # Extract lemma ID: "lexicon.xml#lemma_123" → "lemma_123"
        m = re.match(r'lexicon\.xml#(.+)', corresp)
        if m and m.group(1) not in lemma_ids:
            orphans.append((entry, corresp))

    if not dry_run:
        for entry, corresp in orphans:
            entry.getparent().remove(entry)
        tree.write(str(variants_file), encoding='UTF-8', xml_declaration=True)

    return len(orphans)


def fix_lexicon_concepts(lexicon_file, concept_ids, dry_run):
    """Remove <ptr> elements with @target pointing to non-existent concepts."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(lexicon_file), parser)
    root = tree.getroot()

    orphan_ptrs = []
    for ptr in root.findall(f'.//{TEI}ptr[@target]'):
        target = ptr.get('target', '')
        m = re.match(r'concepts\.xml#(.+)', target)
        if m and m.group(1) not in concept_ids:
            orphan_ptrs.append((ptr, target))

    orphan_segs = []
    # Collect lemma IDs from this file
    lemma_ids = collect_ids(tree, 'entry')
    for seg in root.findall(f'.//{TEI}seg[@corresp]'):
        corresp = seg.get('corresp', '')
        m = re.match(r'lexicon\.xml#(.+)', corresp)
        if m and m.group(1) not in lemma_ids:
            orphan_segs.append((seg, corresp))

    if not dry_run:
        for ptr, target in orphan_ptrs:
            ptr.getparent().remove(ptr)
        for seg, corresp in orphan_segs:
            seg.getparent().remove(seg)
        tree.write(str(lexicon_file), encoding='UTF-8', xml_declaration=True)

    return len(orphan_ptrs), len(orphan_segs)


def main():
    parser = argparse.ArgumentParser(description='Phase I1: Fix orphaned references')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    variants_file = AUTH_DIR / 'variants.xml'
    lexicon_file = AUTH_DIR / 'lexicon.xml'
    concepts_file = AUTH_DIR / 'concepts.xml'

    # Load reference ID sets
    logger.info('Loading lexicon IDs...')
    lexicon_tree = etree.parse(str(lexicon_file))
    lemma_ids = collect_ids(lexicon_tree, 'entry')
    logger.info(f'  {len(lemma_ids)} lemma IDs loaded')

    logger.info('Loading concept IDs...')
    concepts_tree = etree.parse(str(concepts_file))
    concept_ids = collect_ids(concepts_tree, 'category')
    logger.info(f'  {len(concept_ids)} concept IDs loaded')

    # Fix variants.xml
    logger.info('Fixing variants.xml...')
    variants_count = fix_variants(variants_file, lemma_ids, args.dry_run)
    logger.info(f'  {"Would remove" if args.dry_run else "Removed"} {variants_count} orphaned entries')

    # Fix lexicon.xml
    logger.info('Fixing lexicon.xml...')
    ptr_count, seg_count = fix_lexicon_concepts(lexicon_file, concept_ids, args.dry_run)
    logger.info(f'  {"Would remove" if args.dry_run else "Removed"} {ptr_count} orphaned concept ptrs')
    logger.info(f'  {"Would remove" if args.dry_run else "Removed"} {seg_count} orphaned etymology segs')

    logger.info('')
    logger.info(f'Total: {variants_count + ptr_count + seg_count} orphaned references {"would be " if args.dry_run else ""}removed')

    return 0


if __name__ == '__main__':
    sys.exit(main())
