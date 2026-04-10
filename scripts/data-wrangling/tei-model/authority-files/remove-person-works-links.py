#!/usr/bin/env python3
"""
Phase H1: Remove denormalized works links from persons.xml

Removes <listBibl> elements from <person> entries. These contain
bidirectional links to works.xml that are redundant — the build script
derives person→work relationships from works.xml <author> refs.

IST: 209 <listBibl><bibl corresp="works.xml#work_N"/></listBibl> in <person>
SOLL: removed

Usage:
    python scripts/data-wrangling/tei-model/authority-files/remove-person-works-links.py [--dry-run]
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

PERSONS_FILE = Path('authority-files/persons.xml')


def remove_works_links(persons_file: Path, dry_run: bool) -> int:
    """Remove all <listBibl> from <person> elements. Returns count removed."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(persons_file), parser)
    root = tree.getroot()

    list_bibls = root.findall(f'.//{TEI}person/{TEI}listBibl')
    count = len(list_bibls)

    if not dry_run:
        for lb in list_bibls:
            lb.getparent().remove(lb)
        tree.write(str(persons_file), encoding='UTF-8', xml_declaration=True)

    return count


def main():
    parser = argparse.ArgumentParser(description='Phase H1: Remove works links from persons.xml')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    if not PERSONS_FILE.exists():
        logger.error(f'{PERSONS_FILE} not found')
        return 1

    count = remove_works_links(PERSONS_FILE, args.dry_run)
    logger.info(f'{"Would remove" if args.dry_run else "Removed"} {count} <listBibl> elements')

    return 0


if __name__ == '__main__':
    sys.exit(main())
