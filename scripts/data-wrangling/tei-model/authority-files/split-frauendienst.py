#!/usr/bin/env python3
"""
Phase I2: Split Frauendienst (work_6) from Frauenbuch (work_7)

All 7 sigles were incorrectly lumped under work_7 ("Frauenbuch").
Frauendienst and Frauenbuch are two separate works by Ulrich von Liechtenstein.

Moves to work_6 (Frauendienst):
  - Sigles: FD, FDS, FH, FLD, FP
  - Corresponding <relatedItem>/<biblStruct> entries (matched by @key)
  - Genre: genre_88b5cae2 (Liebesroman und Abenteuerroman)
  - Wikidata: Q1451651

Stays at work_7 (Frauenbuch):
  - Sigles: FB, FBS
  - Their biblStruct entries
  - Existing genres and identifiers

Source: Katharina (2026-04-10), Handschriftencensus, GND, Wikidata.

Usage:
    python scripts/data-wrangling/tei-model/authority-files/split-frauendienst.py [--dry-run]
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
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

WORKS_FILE = Path('authority-files/works.xml')

# Sigles that belong to Frauendienst (work_6)
FRAUENDIENST_SIGLES = {'FD', 'FDS', 'FH', 'FLD', 'FP'}


def main():
    parser = argparse.ArgumentParser(description='Phase I2: Split Frauendienst/Frauenbuch')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    xml_parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(WORKS_FILE), xml_parser)
    root = tree.getroot()

    # Find work_6 and work_7
    work_6 = root.find(f'.//{TEI}bibl[@{XML_ID}="work_6"]')
    work_7 = root.find(f'.//{TEI}bibl[@{XML_ID}="work_7"]')

    if work_6 is None or work_7 is None:
        logger.error('Could not find work_6 and/or work_7')
        return 1

    logger.info(f'work_6: {work_6.find(f"{TEI}title").text}')
    logger.info(f'work_7: {work_7.find(f"{TEI}title").text}')

    # --- 1. Move sigles from work_7 to work_6 ---
    sigles_moved = []
    for idno in list(work_7.findall(f'{TEI}idno[@type="sigle"]')):
        if idno.text and idno.text.strip() in FRAUENDIENST_SIGLES:
            sigles_moved.append(idno.text.strip())
            if not args.dry_run:
                work_7.remove(idno)
                # Insert after last idno in work_6, before ptr/author
                insert_pos = 0
                for i, child in enumerate(work_6):
                    if isinstance(child.tag, str) and etree.QName(child.tag).localname == 'idno':
                        insert_pos = i + 1
                idno.tail = '\n          '
                work_6.insert(insert_pos, idno)

    logger.info(f'Sigles moved to work_6: {sigles_moved}')

    # --- 2. Move biblStruct/relatedItem entries ---
    biblstructs_moved = []
    for ri in list(work_7.findall(f'{TEI}relatedItem')):
        bs = ri.find(f'{TEI}biblStruct')
        if bs is not None:
            key = bs.get('key', '')
            if key in FRAUENDIENST_SIGLES:
                biblstructs_moved.append(key)
                if not args.dry_run:
                    work_7.remove(ri)
                    ri.tail = '\n        '
                    work_6.append(ri)

    logger.info(f'biblStruct entries moved to work_6: {biblstructs_moved}')

    # --- 3. Add genre ptr to work_6 ---
    existing_ptrs = [p.get('target', '') for p in work_6.findall(f'{TEI}ptr')]
    genre_target = 'genres.xml#genre_88b5cae2'
    if genre_target not in existing_ptrs:
        if not args.dry_run:
            # Insert after idnos, before author
            insert_pos = 0
            for i, child in enumerate(work_6):
                if isinstance(child.tag, str):
                    localname = etree.QName(child.tag).localname
                    if localname == 'idno':
                        insert_pos = i + 1
                    elif localname in ('ptr', 'author', 'relatedItem'):
                        if localname != 'ptr':
                            insert_pos = i
                        break
            ptr = etree.Element(f'{TEI}ptr')
            ptr.set('target', genre_target)
            ptr.tail = '\n          '
            work_6.insert(insert_pos, ptr)
        logger.info(f'Added genre ptr: {genre_target}')
    else:
        logger.info(f'Genre ptr already exists: {genre_target}')

    # --- 4. Add Wikidata to work_6 ---
    existing_wikidata = work_6.find(f'{TEI}idno[@type="wikidata"]')
    if existing_wikidata is None:
        if not args.dry_run:
            # Insert after last idno
            insert_pos = 0
            for i, child in enumerate(work_6):
                if isinstance(child.tag, str) and etree.QName(child.tag).localname == 'idno':
                    insert_pos = i + 1
            wikidata = etree.Element(f'{TEI}idno')
            wikidata.set('type', 'wikidata')
            wikidata.text = 'http://www.wikidata.org/entity/Q1451651'
            wikidata.tail = '\n          '
            work_6.insert(insert_pos, wikidata)
        logger.info('Added Wikidata Q1451651 to work_6')
    else:
        logger.info(f'Wikidata already exists: {existing_wikidata.text}')

    # --- 5. Write ---
    if not args.dry_run:
        tree.write(str(WORKS_FILE), encoding='UTF-8', xml_declaration=True)

    logger.info('')
    logger.info('Summary:')
    logger.info(f'  work_6 (Frauendienst): +{len(sigles_moved)} sigles, +{len(biblstructs_moved)} biblStructs, +genre, +wikidata')
    logger.info(f'  work_7 (Frauenbuch): -{len(sigles_moved)} sigles, -{len(biblstructs_moved)} biblStructs')
    logger.info('')
    logger.info('NOTE: work_7 genres may need review — genre_88b5cae2 (Liebesroman) was')
    logger.info('      probably assigned because of the Frauendienst sigles. Ask Katharina.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
