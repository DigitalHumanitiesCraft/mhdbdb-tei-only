#!/usr/bin/env python3
"""
Phase B2: Migrate @wordRef → @corresp with URI transformation

7,406,166 occurrences across all 666 base files (+ disamb files).
Attribute rename PLUS value transformation:

  IST:  wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"
  SOLL: corresp="variants.xml#type_8717"

  IST:  wordRef="lexicon.xml#type_117145"
  SOLL: corresp="variants.xml#type_117145"

Extraction: find 'type_' + digits (or negative) → 'variants.xml#type_{id}'

No JS impact (no code reads @wordRef).

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/migrate-wordref.py [--dry-run]
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

TEI_DIR = Path('tei')

TYPE_RE = re.compile(r'type_(-?\d+)')


def transform_uri(wordref_val: str) -> str:
    """Extract type ID and build variants.xml URI.

    'lexicon.xml#lemma_2598_sense_77615_type_8717' → 'variants.xml#type_8717'
    'lexicon.xml#type_117145'                      → 'variants.xml#type_117145'
    'lexicon.xml#type_-7'                          → 'variants.xml#type_-7'
    """
    m = TYPE_RE.search(wordref_val)
    if m:
        return f'variants.xml#type_{m.group(1)}'
    return None


def migrate_file(tei_file: Path, dry_run: bool) -> tuple:
    """Migrate @wordRef → @corresp in one file. Returns (migrated, skipped)."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    migrated = 0
    skipped = 0

    for elem in root.iter():
        val = elem.get('wordRef')
        if val is not None:
            new_val = transform_uri(val)
            if new_val:
                if not dry_run:
                    del elem.attrib['wordRef']
                    elem.set('corresp', new_val)
                migrated += 1
            else:
                logger.warning(f'  Cannot transform wordRef="{val}"')
                skipped += 1

    if migrated and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return migrated, skipped


def main():
    parser = argparse.ArgumentParser(description='Phase B2: @wordRef → @corresp')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    logger.info(f'Processing {len(tei_files)} TEI files...')

    total_migrated = 0
    total_skipped = 0
    files_changed = 0

    for i, tei_file in enumerate(tei_files):
        migrated, skipped = migrate_file(tei_file, args.dry_run)
        if migrated:
            files_changed += 1
            total_migrated += migrated
        total_skipped += skipped
        if (i + 1) % 50 == 0:
            logger.info(f'  {i + 1}/{len(tei_files)} files processed...')

    logger.info('')
    logger.info(f'{"Would migrate" if args.dry_run else "Migrated"} {total_migrated:,} @wordRef → @corresp in {files_changed} files')
    if total_skipped:
        logger.warning(f'Skipped {total_skipped} values (no type_ pattern found)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
