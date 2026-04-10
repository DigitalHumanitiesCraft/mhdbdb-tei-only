#!/usr/bin/env python3
"""
Merge disambiguated POS tags from .disamb.tei.xml into base .tei.xml files.

The 9 disamb files have better POS annotations:
- POS tags for ALL <w> elements (base files have gaps)
- Corrected POS tags where the LLM disambiguator improved them

Strategy: For each <w> matched by @xml:id, copy @pos from disamb → base.
Then delete the disamb file (base becomes the single source of truth).

Scope: 9 disamb files in tei/

Usage:
    python scripts/data-wrangling/tei-model/merge-disamb.py [--dry-run]
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
XML = f'{{{XML_NS}}}'

TEI_DIR = Path('tei')


def merge_file(base_file: Path, disamb_file: Path, dry_run: bool) -> dict:
    """Merge @pos from disamb into base. Returns stats dict."""
    parser = etree.XMLParser(remove_blank_text=False)
    base_tree = etree.parse(str(base_file), parser)
    disamb_tree = etree.parse(str(disamb_file), parser)

    # Build lookup: xml:id → @pos from disamb
    disamb_pos = {}
    for w in disamb_tree.findall(f'.//{TEI}w'):
        xml_id = w.get(f'{XML}id')
        pos = w.get('pos')
        if xml_id and pos:
            disamb_pos[xml_id] = pos

    # Also collect @reason attributes (compound POS tags)
    disamb_reason = {}
    for w in disamb_tree.findall(f'.//{TEI}w'):
        xml_id = w.get(f'{XML}id')
        reason = w.get('reason')
        if xml_id and reason:
            disamb_reason[xml_id] = reason

    # Apply to base
    stats = {'pos_added': 0, 'pos_changed': 0, 'pos_unchanged': 0, 'reason_added': 0, 'unmatched': 0}

    for w in base_tree.findall(f'.//{TEI}w'):
        xml_id = w.get(f'{XML}id')
        if not xml_id or xml_id not in disamb_pos:
            continue

        old_pos = w.get('pos')
        new_pos = disamb_pos[xml_id]

        if old_pos is None:
            stats['pos_added'] += 1
        elif old_pos != new_pos:
            stats['pos_changed'] += 1
        else:
            stats['pos_unchanged'] += 1
            continue  # No change needed

        if not dry_run:
            w.set('pos', new_pos)
            # Also copy @reason if present
            if xml_id in disamb_reason:
                w.set('reason', disamb_reason[xml_id])
                stats['reason_added'] += 1

    # Check for disamb entries not in base
    base_ids = {w.get(f'{XML}id') for w in base_tree.findall(f'.//{TEI}w')}
    stats['unmatched'] = len(set(disamb_pos.keys()) - base_ids)

    if (stats['pos_added'] or stats['pos_changed']) and not dry_run:
        base_tree.write(str(base_file), encoding='UTF-8', xml_declaration=True)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Merge disamb POS tags into base files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    parser.add_argument('--keep', action='store_true',
                        help='Keep disamb files after merge (default: delete)')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    disamb_files = sorted(TEI_DIR.glob('*.disamb.tei.xml'))
    logger.info(f'Found {len(disamb_files)} disamb files')

    total_added = 0
    total_changed = 0

    for disamb_file in disamb_files:
        sigle = disamb_file.name.replace('.disamb.tei.xml', '')
        base_file = TEI_DIR / f'{sigle}.tei.xml'

        if not base_file.exists():
            logger.warning(f'{sigle}: base file not found, skipping')
            continue

        stats = merge_file(base_file, disamb_file, args.dry_run)
        total_added += stats['pos_added']
        total_changed += stats['pos_changed']

        logger.info(f'  {sigle}: +{stats["pos_added"]} added, ~{stats["pos_changed"]} changed, '
                     f'={stats["pos_unchanged"]} unchanged'
                     + (f', {stats["reason_added"]} @reason' if stats['reason_added'] else '')
                     + (f', {stats["unmatched"]} unmatched' if stats['unmatched'] else ''))

        # Delete disamb file
        if not args.dry_run and not args.keep:
            disamb_file.unlink()
            logger.info(f'  {sigle}: deleted {disamb_file.name}')

    logger.info('')
    logger.info(f'{"Would merge" if args.dry_run else "Merged"} {total_added:,} POS added + {total_changed:,} POS changed')
    if not args.dry_run and not args.keep:
        logger.info(f'Deleted {len(disamb_files)} disamb files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
