#!/usr/bin/env python3
"""
Phase E2: Corpus Validation

Two-stage validation:
  Stage 1: Well-formedness (lxml parse)
  Stage 2: Structural checks (Python assertions based on TEI-MODEL.md)

Note: Full RELAX NG validation (tei_all.rng + mhdbdb.rng) requires
jing (Java) or trang to convert RNC→RNG. This script performs the
structural validation that matters most for MHDBDB conformance.

Usage:
    python scripts/data-wrangling/tei-model/validate-corpus.py [--sample N]
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

TEI_DIR = Path('tei')

# Allowed div/@type values (TEI-MODEL.md Section 3)
ALLOWED_DIV_TYPES = {
    'chapter', 'section', 'number', 'song',
    'parallel', 'colophon', 'recipe',
}

# 18 prose files that should NOT have <l> (migrated to <lb/>)
PROSE_SIGLES = {
    'PL1', 'PL2', 'PL3', 'FLG1', 'VTC', 'NBU', 'PUC', 'ESB',
    'LUU', 'EHB', 'EB1', 'EB2', 'MSP', 'PRJ', 'REG', 'ATF', 'SPH', 'WGI',
}


def validate_file(tei_file: Path) -> list:
    """Validate one TEI file. Returns list of error strings."""
    errors = []
    sigle = tei_file.stem.replace('.tei', '').replace('.disamb', '')

    try:
        tree = etree.parse(str(tei_file))
    except etree.XMLSyntaxError as e:
        return [f'NOT WELL-FORMED: {e}']

    root = tree.getroot()

    # --- Check 1: No non-standard attributes on <w> ---
    for w in root.iter(f'{TEI}w'):
        for attr in w.attrib:
            if attr in ('meaningRef', 'wordRef'):
                errors.append(f'Non-standard attribute @{attr} on <w>')
                break  # one error per type is enough
        if errors:
            break

    # --- Check 2: div/@type values ---
    for div in root.findall(f'.//{TEI}div'):
        dtype = div.get('type')
        if dtype and dtype not in ALLOWED_DIV_TYPES:
            errors.append(f'Invalid div/@type="{dtype}"')

    # --- Check 3: No <suppplied> typo ---
    if root.findall(f'.//{TEI}suppplied'):
        errors.append('<suppplied> typo found')

    # --- Check 4: No <seg type="pc"> (should be <pc>) ---
    for seg in root.findall(f'.//{TEI}seg[@type="pc"]'):
        errors.append('<seg type="pc"> found (should be <pc>)')
        break

    # --- Check 5: langUsage exists ---
    if root.find(f'.//{TEI}langUsage') is None:
        errors.append('Missing <langUsage>')

    # --- Check 6: monogr author before title ---
    for monogr in root.findall(f'.//{TEI}monogr'):
        children = [c.tag.replace(TEI, '') for c in monogr]
        if 'author' in children and 'title' in children:
            if children.index('author') > children.index('title'):
                errors.append('<monogr>: <author> after <title>')

    # --- Check 7: Prose files should not have <l> ---
    if sigle in PROSE_SIGLES:
        ls = root.findall(f'.//{TEI}l')
        if ls:
            errors.append(f'Prose file has {len(ls)} <l> elements (should use <lb/>)')

    # --- Check 8: <pc> has @join ---
    for pc in root.findall(f'.//{TEI}pc'):
        if pc.get('join') is None:
            errors.append('<pc> missing @join attribute')
            break

    return errors


def main():
    parser = argparse.ArgumentParser(description='Phase E2: Corpus validation')
    parser.add_argument('--sample', type=int, default=0,
                        help='Validate only N random files (0=all)')
    args = parser.parse_args()

    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
    if args.sample:
        import random
        tei_files = random.sample(tei_files, min(args.sample, len(tei_files)))

    logger.info(f'Validating {len(tei_files)} TEI files...')

    total_errors = 0
    files_with_errors = 0

    for i, tei_file in enumerate(tei_files):
        errors = validate_file(tei_file)
        if errors:
            sigle = tei_file.stem.replace('.tei', '')
            files_with_errors += 1
            for err in errors:
                logger.error(f'  {sigle}: {err}')
                total_errors += 1
        if (i + 1) % 100 == 0:
            logger.info(f'  {i + 1}/{len(tei_files)} files validated...')

    logger.info('')
    if total_errors == 0:
        logger.info(f'ALL {len(tei_files)} files VALID')
    else:
        logger.error(f'{total_errors} errors in {files_with_errors} files')

    return 1 if total_errors else 0


if __name__ == '__main__':
    sys.exit(main())
