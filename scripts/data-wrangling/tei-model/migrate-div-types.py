#!/usr/bin/env python3
"""
Phase A1: Migrate div/@type values to SOLL-Modell

Renames div/@type values per TEI-MODEL.md Section 3 decisions:

  deed      → number    (HZU, HZU2)
  sermon    → number    (ADP, ECK + 10 further)
  sigil     → number    (BOP)
  paragraph → number    (BDK)
  part      → section   (DL2, EHB + further)
  subsection→ section   (KVM)
  §         → section   (KVM)
  volume    → section   (FLG, FLG1)

LZT special case:
  <div type="stanza"> → <lg type="stanza">  (element change, not just rename)

Scope: all *.tei.xml and *.disamb.tei.xml in tei/

Usage:
    python scripts/data-wrangling/tei-model/migrate-div-types.py [--dry-run]
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

# Simple renames: old_type → new_type
RENAMES = {
    'deed':       'number',
    'sermon':     'number',
    'sigil':      'number',
    'paragraph':  'number',
    'part':       'section',
    'subsection': 'section',
    '§':          'section',
    'volume':     'section',
}


def migrate_file(tei_file: Path, dry_run: bool) -> dict:
    """Migrate a single TEI file. Returns change counts."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_file), parser)
    root = tree.getroot()

    counts = {}
    changed = False

    # --- Simple renames ---
    for old_type, new_type in RENAMES.items():
        divs = root.findall(f'.//{TEI}div[@type="{old_type}"]')
        if divs:
            counts[f'{old_type}→{new_type}'] = len(divs)
            if not dry_run:
                for div in divs:
                    div.set('type', new_type)
            changed = True

    # --- LZT special case: <div type="stanza"> → <lg type="stanza"> ---
    stanza_divs = root.findall(f'.//{TEI}div[@type="stanza"]')
    if stanza_divs:
        counts['div.stanza→lg.stanza'] = len(stanza_divs)
        if not dry_run:
            for div in stanza_divs:
                # Change tag from div to lg, keep all attributes
                div.tag = f'{TEI}lg'
                # type="stanza" stays as-is
        changed = True

    if changed and not dry_run:
        tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)

    return counts


def main():
    parser = argparse.ArgumentParser(description='Phase A1: Migrate div/@type values')
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
    logger.info(f'{"Would change" if args.dry_run else "Changed"} {files_changed} files')
    for migration, count in sorted(total_counts.items()):
        logger.info(f'  {migration}: {count}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
