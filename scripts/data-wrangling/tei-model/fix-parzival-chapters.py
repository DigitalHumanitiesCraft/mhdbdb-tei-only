#!/usr/bin/env python3
"""
Issue #60: Reconstruct chapter structure in Parzival (PZ)

The PZ TEI file has 24,812 <l> elements in a flat <p> with no chapter divisions.
Chapter boundaries are encoded in the xml:id pattern of <w> elements:

    xml:id="PZ_{CV}_{t}"
    CV = chapter*100 + verse  (e.g. 129 = chapter 1, verse 29)

This script groups <l> elements by chapter number and wraps them in
<div type="chapter" n="{chapter}"> elements.

Before: <body><p><l>...<l>...<l>...</p></body>
After:  <body><div type="chapter" n="1"><l>...</l>...</div>
              <div type="chapter" n="2"><l>...</l>...</div>...</body>

Usage:
    python scripts/data-wrangling/tei-model/fix-parzival-chapters.py [--dry-run]
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from lxml import etree

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

PZ_FILE = Path('tei/PZ.tei.xml')


def get_chapter_from_line(l_el):
    """Extract chapter number from first <w> xml:id in a <l> element."""
    for w in l_el.iter(f'{TEI}w'):
        wid = w.get(XML_ID, '')
        m = re.match(r'PZ_(\d+)_\d+', wid)
        if m:
            cv = int(m.group(1))
            return cv // 100
    return None


def main():
    parser = argparse.ArgumentParser(description='Issue #60: Fix Parzival chapter structure')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    xml_parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(PZ_FILE), xml_parser)
    root = tree.getroot()

    body = root.find(f'.//{TEI}body')
    p = body.find(f'{TEI}p')

    if p is None:
        logger.error('No <p> found in body')
        return 1

    lines = p.findall(f'{TEI}l')
    logger.info(f'Found {len(lines)} <l> elements in <p>')

    # Group lines by chapter
    chapters = {}
    for l in lines:
        ch = get_chapter_from_line(l)
        if ch is None:
            logger.warning(f'Could not determine chapter for <l>, skipping')
            continue
        if ch not in chapters:
            chapters[ch] = []
        chapters[ch].append(l)

    logger.info(f'Found {len(chapters)} chapters (Dreißiger {min(chapters)}-{max(chapters)})')

    # Show stats
    verse_counts = {ch: len(ls) for ch, ls in chapters.items()}
    avg_verses = sum(verse_counts.values()) / len(verse_counts)
    logger.info(f'Average verses per chapter: {avg_verses:.1f}')
    logger.info(f'Min: {min(verse_counts.values())}, Max: {max(verse_counts.values())}')

    if args.dry_run:
        logger.info(f'Would create {len(chapters)} <div type="chapter"> elements')
        return 0

    # Build new body content: <div type="chapter" n="N"> per chapter
    # Remove the <p> and replace with divs
    body.remove(p)

    indent_div = '\n        '
    indent_l = '\n          '

    for ch_num in sorted(chapters.keys()):
        div = etree.SubElement(body, f'{TEI}div')
        div.set('type', 'chapter')
        div.set('n', str(ch_num))
        div.text = indent_l

        ch_lines = chapters[ch_num]
        for i, l in enumerate(ch_lines):
            l.tail = indent_l if i < len(ch_lines) - 1 else indent_div
            div.append(l)

        div.tail = indent_div

    tree.write(str(PZ_FILE), encoding='UTF-8', xml_declaration=True)

    logger.info(f'Created {len(chapters)} <div type="chapter"> elements')
    logger.info(f'Total <l> elements: {sum(len(ls) for ls in chapters.values())}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
