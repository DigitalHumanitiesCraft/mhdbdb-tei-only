#!/usr/bin/env python3
"""
Phase A2: Fix monogr element order

TEI P5 content model for <monogr>:
  (author|editor|meeting|respStmt)*, title+,
  (idno|editor|edition|sponsor|funder|respStmt)*,
  (note|biblScope)*, imprint*

Problem: 131 files have <author> AFTER <title> in <monogr>.

SOLL order: author*, title, editor*, idno*, edition?, imprint*

This script reorders <monogr> children to match the SOLL model.

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/fix-monogr-order.py [--dry-run]
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

# SOLL order: elements sorted into these groups, in this sequence
ORDER_GROUPS = ['author', 'title', 'editor', 'idno', 'edition', 'imprint']


def sort_key(elem):
    """Sort key for monogr children based on SOLL order."""
    local = elem.tag.replace(TEI, '')
    try:
        return ORDER_GROUPS.index(local)
    except ValueError:
        # Unknown elements go to the end
        return len(ORDER_GROUPS)


def migrate_file(tei_file: Path, dry_run: bool) -> int:
    """Fix monogr order in one file. Returns number of monogrs fixed."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    fixed = 0
    for monogr in root.findall(f'.//{TEI}monogr'):
        children = list(monogr)
        local_names = [c.tag.replace(TEI, '') for c in children]

        # Check if author appears after title
        if 'author' in local_names and 'title' in local_names:
            if local_names.index('author') > local_names.index('title'):
                if not dry_run:
                    # Detach all children, sort, re-attach
                    for child in children:
                        monogr.remove(child)
                    for child in sorted(children, key=sort_key):
                        monogr.append(child)
                fixed += 1

    if fixed and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return fixed


def main():
    parser = argparse.ArgumentParser(description='Phase A2: Fix monogr element order')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    logger.info(f'Processing {len(tei_files)} TEI files...')

    total_fixed = 0
    files_changed = 0

    for tei_file in tei_files:
        fixed = migrate_file(tei_file, args.dry_run)
        if fixed:
            sigle = tei_file.stem.replace('.tei', '')
            logger.info(f'  {sigle}: {fixed} monogr(s) reordered')
            files_changed += 1
            total_fixed += fixed

    logger.info('')
    logger.info(f'{"Would fix" if args.dry_run else "Fixed"} {total_fixed} monogr(s) in {files_changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
