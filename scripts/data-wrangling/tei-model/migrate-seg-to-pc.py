#!/usr/bin/env python3
"""
Phase C1: Migrate <seg type="pc"> → <pc join="...">

1,370,191 occurrences across 666 base files (+ disamb).

Transformation:
  <seg xml:id="X" type="pc">.</seg>  →  <pc xml:id="X" join="left">.</pc>

Join direction based on content:
  join="right": opening punctuation — ( < «
  join="left":  everything else — . , ; : ! ? ) > » ' and elided forms

xml:id is preserved when present.

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/migrate-seg-to-pc.py [--dry-run]
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

TEI_DIR = Path('tei')

# Characters that join to the right (opening punctuation)
RIGHT_JOIN = frozenset(['(', '<', '\u00ab'])  # ( < «


def get_join(text: str) -> str:
    """Determine join direction from punctuation content."""
    stripped = text.strip() if text else ''
    if stripped in RIGHT_JOIN:
        return 'right'
    return 'left'


def migrate_file(tei_file: Path, dry_run: bool) -> int:
    """Migrate <seg type="pc"> → <pc> in one file. Returns count."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    count = 0
    for seg in root.findall(f'.//{TEI}seg[@type="pc"]'):
        text_content = etree.tostring(seg, method='text', encoding='unicode')
        if not dry_run:
            # Change element tag
            seg.tag = f'{TEI}pc'
            # Remove type="pc", add join
            del seg.attrib['type']
            seg.set('join', get_join(text_content))
        count += 1

    if count and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return count


def main():
    parser = argparse.ArgumentParser(description='Phase C1: <seg type="pc"> → <pc>')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    logger.info(f'Processing {len(tei_files)} TEI files...')

    total = 0
    files_changed = 0

    for i, tei_file in enumerate(tei_files):
        count = migrate_file(tei_file, args.dry_run)
        if count:
            files_changed += 1
            total += count
        if (i + 1) % 50 == 0:
            logger.info(f'  {i + 1}/{len(tei_files)} files processed...')

    logger.info('')
    logger.info(f'{"Would migrate" if args.dry_run else "Migrated"} {total:,} <seg type="pc"> → <pc> in {files_changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
