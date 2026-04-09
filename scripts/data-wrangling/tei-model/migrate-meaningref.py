#!/usr/bin/env python3
"""
Phase B1: Migrate @meaningRef → @ana

5,852,223 occurrences across all 666 base files (+ disamb files).
Pure attribute rename — values stay identical.

@meaningRef is non-standard TEI and blocks tei_all.rng validation.
@ana (att.global.analytic) is the TEI P5 standard equivalent.

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/migrate-meaningref.py [--dry-run]
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

TEI_DIR = Path('tei')


def migrate_file(tei_file: Path, dry_run: bool) -> int:
    """Rename @meaningRef → @ana in one file. Returns count."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    count = 0
    for elem in root.iter():
        val = elem.get('meaningRef')
        if val is not None:
            if not dry_run:
                del elem.attrib['meaningRef']
                elem.set('ana', val)
            count += 1

    if count and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return count


def main():
    parser = argparse.ArgumentParser(description='Phase B1: @meaningRef → @ana')
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
    logger.info(f'{"Would rename" if args.dry_run else "Renamed"} {total:,} @meaningRef → @ana in {files_changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
