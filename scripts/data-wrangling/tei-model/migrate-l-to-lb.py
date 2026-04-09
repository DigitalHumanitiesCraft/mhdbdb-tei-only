#!/usr/bin/env python3
"""
Phase C2: Migrate <l> → <lb/> in 18 prose files

TEI P5 defines <l> as verse line. 18 prose texts misuse it for typographic
line breaks. Migration: <l n="X">content</l> → <lb n="X"/>content

The container element becomes a milestone element. All children of <l>
are moved to the parent element, positioned after the new <lb/>.

Only the 18 files listed in TEI-MODEL.md Section 8.1 are affected.

Usage:
    python scripts/data-wrangling/tei-model/migrate-l-to-lb.py [--dry-run]
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

# 18 prose files from TEI-MODEL.md Section 8.1
TARGET_SIGLES = [
    'PL1', 'PL2', 'PL3',           # Prosa-Lancelot
    'FLG1',                          # Fliessende Licht
    'VTC', 'NBU', 'PUC', 'ESB',     # Chroniken
    'LUU', 'EHB', 'EB1', 'EB2',     # Baemler 1476
    'MSP', 'PRJ', 'REG',            # Baemler 1476
    'ATF', 'SPH', 'WGI',            # Sonstige
]


def migrate_file(tei_file: Path, dry_run: bool) -> int:
    """Convert <l> → <lb/> in one file. Returns count."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    # Collect all <l> elements (iterate in reverse to avoid index issues)
    l_elems = root.findall(f'.//{TEI}l')
    if not l_elems:
        return 0

    if dry_run:
        return len(l_elems)

    for l_elem in l_elems:
        parent = l_elem.getparent()

        # Create <lb/> with same @n
        lb = etree.Element(f'{TEI}lb')
        n = l_elem.get('n')
        if n is not None:
            lb.set('n', n)

        # Insert <lb/> right before <l>
        l_elem.addprevious(lb)

        # The <lb/> tail gets the <l>'s text (content before first child)
        lb.tail = l_elem.text

        # Move children of <l> to parent, right after <lb/>
        # We insert in reverse after lb, so order is preserved
        children = list(l_elem)
        anchor = lb
        for child in children:
            anchor.addnext(child)
            anchor = child

        # The last child (or lb if no children) gets <l>'s tail appended
        if children:
            last = children[-1]
            last.tail = (last.tail or '') + (l_elem.tail or '')
        else:
            lb.tail = (lb.tail or '') + (l_elem.tail or '')

        # Remove the now-empty <l>
        parent.remove(l_elem)

    tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)
    return len(l_elems)


def main():
    parser = argparse.ArgumentParser(description='Phase C2: <l> → <lb/> in prose files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    total = 0
    files_changed = 0

    for sigle in TARGET_SIGLES:
        tei_file = TEI_DIR / f'{sigle}.tei.xml'
        if not tei_file.exists():
            logger.warning(f'{sigle}: file not found, skipping')
            continue

        count = migrate_file(tei_file, args.dry_run)
        if count:
            logger.info(f'  {sigle}: {count} <l> → <lb/>')
            files_changed += 1
            total += count

    logger.info('')
    logger.info(f'{"Would migrate" if args.dry_run else "Migrated"} {total:,} <l> → <lb/> in {files_changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
