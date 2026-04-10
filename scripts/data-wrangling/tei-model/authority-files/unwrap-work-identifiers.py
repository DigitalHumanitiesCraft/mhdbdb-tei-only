#!/usr/bin/env python3
"""
Phase G2+G3: Unwrap external identifiers and fix GND casing in works.xml

1. Unwrap <note type="identifiers">: move child <idno> elements up into <bibl>
2. Fix GND casing: type="gnd" → type="GND"
3. Enforce SOLL child order in <bibl>: title* → idno* → ptr* → author* → relatedItem*

IST: <note type="identifiers"><idno type="gnd">...</idno><idno type="handschriftencensus">...</idno></note>
SOLL: <idno type="GND">...</idno><idno type="handschriftencensus">...</idno> (direct children of <bibl>)

Dependency: Run AFTER normalize-work-genres.py (G1), since <ptr> must exist for ordering.

Usage:
    python scripts/data-wrangling/tei-model/authority-files/unwrap-work-identifiers.py [--dry-run]
"""

import argparse
import logging
import sys
from pathlib import Path
from lxml import etree

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML_NS = 'http://www.w3.org/XML/1998/namespace'

WORKS_FILE = Path('authority-files/works.xml')

# SOLL order for <bibl> children
TAG_ORDER = ['title', 'idno', 'ptr', 'author', 'relatedItem']


def tag_rank(element):
    """Return sort rank for a bibl child element."""
    localname = etree.QName(element.tag).localname if isinstance(element.tag, str) else ''
    try:
        return TAG_ORDER.index(localname)
    except ValueError:
        return len(TAG_ORDER)  # unknown tags go last


def unwrap_and_reorder(works_file: Path, dry_run: bool) -> dict:
    """Unwrap identifier notes, fix GND casing, reorder bibl children."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(works_file), parser)
    root = tree.getroot()

    stats = {
        'notes_unwrapped': 0,
        'idnos_moved': 0,
        'gnd_fixed': 0,
        'bibls_reordered': 0,
    }

    bibls = root.findall(f'.//{TEI}bibl')

    for bibl in bibls:
        # --- Step 1: Unwrap <note type="identifiers"> ---
        notes = bibl.findall(f'{TEI}note[@type="identifiers"]')
        for note in notes:
            idnos = list(note)
            if not dry_run:
                # Insert idnos before the note's position
                note_index = list(bibl).index(note)
                for i, idno in enumerate(idnos):
                    idno.tail = '\n          '
                    bibl.insert(note_index + i, idno)
                bibl.remove(note)
            stats['notes_unwrapped'] += 1
            stats['idnos_moved'] += len(idnos)

        # --- Step 2: Fix GND casing (search all descendant idnos for dry-run accuracy) ---
        for idno in bibl.iter(f'{TEI}idno'):
            if idno.get('type') == 'gnd':
                if not dry_run:
                    idno.set('type', 'GND')
                stats['gnd_fixed'] += 1

        # --- Step 3: Enforce child order (G3) ---
        children = [c for c in bibl if isinstance(c.tag, str)]
        ranks = [tag_rank(c) for c in children]
        if ranks != sorted(ranks):
            if not dry_run:
                # Preserve text/tail formatting
                sorted_children = sorted(children, key=tag_rank)
                for child in children:
                    bibl.remove(child)
                indent = '\n          '
                for i, child in enumerate(sorted_children):
                    child.tail = indent
                    bibl.append(child)
                # Last child before closing tag
                if sorted_children:
                    sorted_children[-1].tail = '\n        '
            stats['bibls_reordered'] += 1

    if not dry_run:
        tree.write(str(works_file), encoding='UTF-8', xml_declaration=True)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Phase G2+G3: Unwrap identifiers, fix GND casing, reorder bibl children')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    if not WORKS_FILE.exists():
        logger.error(f'{WORKS_FILE} not found')
        return 1

    # Verify G1 ran first
    tree = etree.parse(str(WORKS_FILE))
    genre_refs = tree.findall(f'.//{{{TEI_NS}}}ref[@target]')
    genre_refs = [r for r in genre_refs if r.get('target', '').startswith('genres.xml#')]
    if genre_refs:
        logger.error(f'Found {len(genre_refs)} genre <ref> elements — run normalize-work-genres.py (G1) first!')
        return 1

    stats = unwrap_and_reorder(WORKS_FILE, args.dry_run)

    logger.info('')
    logger.info(f'{"Would change" if args.dry_run else "Changed"}:')
    logger.info(f'  <note> unwrapped:  {stats["notes_unwrapped"]}')
    logger.info(f'  <idno> moved up:   {stats["idnos_moved"]}')
    logger.info(f'  gnd → GND:         {stats["gnd_fixed"]}')
    logger.info(f'  <bibl> reordered:  {stats["bibls_reordered"]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
