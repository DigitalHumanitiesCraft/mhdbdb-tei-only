#!/usr/bin/env python3
"""
Phase G1: Normalize genre references in works.xml

Replaces denormalized genre <ref> elements (with label text, lang variants,
parent-genre refs) with clean <ptr target="..."/> elements.

IST: 3,422 <ref target="genres.xml#..." xml:lang="..." [type="parent"]>Label</ref>
SOLL: 1 <ptr target="genres.xml#..."/> per unique direct genre-ID

Special cases:
  - work_560, work_197: only have type="parent" refs → keep the parent genre-ID
  - Multiple genres per work → multiple <ptr> elements

Usage:
    python scripts/data-wrangling/tei-model/authority-files/normalize-work-genres.py [--dry-run]
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

WORKS_FILE = Path('authority-files/works.xml')


def normalize_genres(works_file: Path, dry_run: bool) -> dict:
    """Replace genre <ref> with <ptr/> in all <bibl> elements."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(works_file), parser)
    root = tree.getroot()

    stats = {
        'refs_removed': 0,
        'ptrs_added': 0,
        'bibls_changed': 0,
        'parent_only_bibls': [],
    }

    bibls = root.findall(f'.//{TEI}bibl')

    for bibl in bibls:
        genre_refs = bibl.findall(f'{TEI}ref[@target]')
        genre_refs = [r for r in genre_refs if r.get('target', '').startswith('genres.xml#')]

        if not genre_refs:
            continue

        # Collect unique genre IDs, separating direct from parent
        direct_ids = []
        parent_ids = []
        for ref in genre_refs:
            genre_id = ref.get('target')
            if ref.get('type') == 'parent':
                if genre_id not in parent_ids:
                    parent_ids.append(genre_id)
            else:
                if genre_id not in direct_ids:
                    direct_ids.append(genre_id)

        # Special case: only parent refs → use parent IDs as direct
        if not direct_ids and parent_ids:
            work_id = bibl.get(f'{{{TEI_NS.replace(TEI_NS, "")}}}id', bibl.get('{http://www.w3.org/XML/1998/namespace}id', '?'))
            stats['parent_only_bibls'].append(work_id)
            direct_ids = parent_ids

        # Find insertion point: after last <idno>, before <author>
        insert_pos = None
        for i, child in enumerate(bibl):
            tag = etree.QName(child.tag).localname if isinstance(child.tag, str) else ''
            if tag == 'idno':
                insert_pos = i + 1
            elif tag in ('author', 'relatedItem'):
                if insert_pos is None:
                    insert_pos = i
                break

        if insert_pos is None:
            insert_pos = len(bibl)

        if not dry_run:
            # Remove all genre refs
            for ref in genre_refs:
                # Clean up trailing whitespace/newline text
                tail = ref.tail
                prev = ref.getprevious()
                parent = ref.getparent()
                parent.remove(ref)

            # Insert <ptr> elements at the correct position
            for j, genre_target in enumerate(direct_ids):
                ptr = etree.Element(f'{TEI}ptr')
                ptr.set('target', genre_target)
                ptr.tail = '\n          '
                bibl.insert(insert_pos + j, ptr)

        stats['refs_removed'] += len(genre_refs)
        stats['ptrs_added'] += len(direct_ids)
        stats['bibls_changed'] += 1

    if not dry_run:
        tree.write(str(works_file), encoding='UTF-8', xml_declaration=True)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Phase G1: Normalize genre refs in works.xml')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    if not WORKS_FILE.exists():
        logger.error(f'{WORKS_FILE} not found')
        return 1

    stats = normalize_genres(WORKS_FILE, args.dry_run)

    logger.info('')
    logger.info(f'{"Would change" if args.dry_run else "Changed"} {stats["bibls_changed"]} <bibl> elements')
    logger.info(f'  <ref> removed: {stats["refs_removed"]}')
    logger.info(f'  <ptr> added:   {stats["ptrs_added"]}')
    if stats['parent_only_bibls']:
        logger.info(f'  Parent-only bibls (used parent genre): {stats["parent_only_bibls"]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
