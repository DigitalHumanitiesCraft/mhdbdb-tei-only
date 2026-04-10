#!/usr/bin/env python3
"""
Phase A5: Add <langUsage> to all TEI headers

All corpus texts are Middle High German. Currently no file has <langUsage>.
This script adds:

  <langUsage>
    <language ident="gmh">Mittelhochdeutsch</language>
  </langUsage>

Inserted into <profileDesc>, before <particDesc>.

Scope: all *.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/enrich-headers.py [--dry-run]
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


def migrate_file(tei_file: Path, dry_run: bool) -> bool:
    """Add langUsage to one file. Returns True if changed."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    # Check if langUsage already exists
    existing = root.find(f'.//{TEI}langUsage')
    if existing is not None:
        return False

    # Find profileDesc
    profile_desc = root.find(f'.//{TEI}profileDesc')
    if profile_desc is None:
        logger.warning(f'  No <profileDesc> in {tei_file.name}')
        return False

    if dry_run:
        return True

    # Build <langUsage><language ident="gmh">Mittelhochdeutsch</language></langUsage>
    lang_usage = etree.Element(f'{TEI}langUsage')
    language = etree.SubElement(lang_usage, f'{TEI}language')
    language.set('ident', 'gmh')
    language.text = 'Mittelhochdeutsch'

    # Insert as first child of profileDesc (before particDesc)
    profile_desc.insert(0, lang_usage)

    tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)
    return True


def main():
    parser = argparse.ArgumentParser(description='Phase A5: Add langUsage to TEI headers')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    logger.info(f'Processing {len(tei_files)} TEI files...')

    added = 0
    skipped = 0

    for tei_file in tei_files:
        if migrate_file(tei_file, args.dry_run):
            added += 1
        else:
            skipped += 1

    logger.info('')
    logger.info(f'{"Would add" if args.dry_run else "Added"} <langUsage> to {added} files, {skipped} already had it')
    return 0


if __name__ == '__main__':
    sys.exit(main())
