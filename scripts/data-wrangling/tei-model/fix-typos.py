#!/usr/bin/env python3
"""
Phase A3: Fix element name typos

Known typos:
  <suppplied> → <supplied>  (1 occurrence in corpus)

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/fix-typos.py [--dry-run]
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

# Typo corrections: wrong_tag → correct_tag
TYPOS = {
    f'{TEI}suppplied': f'{TEI}supplied',
}


def migrate_file(tei_file: Path, dry_run: bool) -> dict:
    """Fix typos in one file. Returns {typo: count}."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    counts = {}
    changed = False

    for wrong_tag, correct_tag in TYPOS.items():
        elems = root.findall(f'.//{wrong_tag}')
        if elems:
            local_wrong = wrong_tag.replace(TEI, '')
            local_correct = correct_tag.replace(TEI, '')
            counts[f'{local_wrong}→{local_correct}'] = len(elems)
            if not dry_run:
                for elem in elems:
                    elem.tag = correct_tag
            changed = True

    if changed and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return counts


def main():
    parser = argparse.ArgumentParser(description='Phase A3: Fix element name typos')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    logger.info(f'Processing {len(tei_files)} TEI files...')

    total_counts = {}
    files_changed = 0

    for tei_file in tei_files:
        counts = migrate_file(tei_file, args.dry_run)
        if counts:
            sigle = tei_file.stem.replace('.tei', '')
            logger.info(f'  {sigle}: {counts}')
            files_changed += 1
            for k, v in counts.items():
                total_counts[k] = total_counts.get(k, 0) + v

    logger.info('')
    logger.info(f'{"Would fix" if args.dry_run else "Fixed"} typos in {files_changed} files')
    for typo, count in sorted(total_counts.items()):
        logger.info(f'  {typo}: {count}')

    if not total_counts:
        logger.info('  No typos found.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
