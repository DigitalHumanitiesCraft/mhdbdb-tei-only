#!/usr/bin/env python3
"""
Phase A4: Decode HZU/HZU2 date notes

HZU and HZU2 have encoded date notes:
  <note type="date" n="224"/> → <note type="date" n="24. Februar"/>

Encoding: last 2 digits = day, remaining prefix = month number.
  224  → month 2,  day 24 → "24. Februar"
  810  → month 8,  day 10 → "10. August"
  1012 → month 10, day 12 → "12. Oktober"

Year notes (<note type="year" n="1293"/>) are already human-readable
and remain unchanged.

Scope: HZU.tei.xml and HZU2.tei.xml only

Usage:
    python scripts/data-wrangling/tei-model/decode-hzu-dates.py [--dry-run]
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

MONTHS = {
    1: 'Jänner', 2: 'Februar', 3: 'März', 4: 'April',
    5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember',
}

TARGET_FILES = ['HZU.tei.xml', 'HZU2.tei.xml']


def decode_date(encoded: str) -> str:
    """Decode '224' → '24. Februar', '1012' → '12. Oktober'."""
    if not encoded or not encoded.isdigit() or len(encoded) < 3:
        return None
    day = int(encoded[-2:])
    month = int(encoded[:-2])
    if month < 1 or month > 12 or day < 1 or day > 31:
        return None
    return f'{day}. {MONTHS[month]}'


def migrate_file(tei_file: Path, dry_run: bool) -> int:
    """Decode date notes in one file. Returns count of decoded notes."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    decoded = 0
    errors = 0

    for note in root.findall(f'.//{TEI}note[@type="date"]'):
        encoded = note.get('n', '')
        result = decode_date(encoded)
        if result:
            if not dry_run:
                note.set('n', result)
            decoded += 1
        else:
            logger.warning(f'  Cannot decode date n="{encoded}"')
            errors += 1

    if decoded and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    if errors:
        logger.warning(f'  {errors} date(s) could not be decoded')

    return decoded


def main():
    parser = argparse.ArgumentParser(description='Phase A4: Decode HZU date notes')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    total = 0
    for filename in TARGET_FILES:
        tei_file = TEI_DIR / filename
        if not tei_file.exists():
            logger.warning(f'{filename} not found, skipping')
            continue

        decoded = migrate_file(tei_file, args.dry_run)
        sigle = filename.replace('.tei.xml', '')
        logger.info(f'  {sigle}: {decoded} dates decoded')
        total += decoded

    logger.info('')
    logger.info(f'{"Would decode" if args.dry_run else "Decoded"} {total} date notes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
