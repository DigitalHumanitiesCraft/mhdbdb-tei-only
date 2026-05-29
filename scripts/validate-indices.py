#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate Generated Indices

Validates structure and content of:
- data/authority-index.json.gz
- data/corpus-index.json.gz

Checks:
- File exists and readable
- JSON structure valid
- Required fields present
- Data types correct
- Version matches expected
- Statistics reasonable

Exit code: 0 = success, 1 = validation failed
"""

import json
import gzip
import sys
import io
from pathlib import Path

# Force UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
AUTHORITY_INDEX = DATA_DIR / 'authority-index.json.gz'
CORPUS_INDEX = DATA_DIR / 'corpus-index.json.gz'

# Expected versions are derived from the loader constants (single source of
# truth), not hardcoded — otherwise this gate silently goes stale on every
# index bump (it sat at '1.0.0' while the indexes reached 4.1.3 / 1.4.0).
import re

_LOADER = PROJECT_ROOT / 'assets' / 'js' / 'lib' / 'corpus-loader.js'


def _loader_const(name):
    try:
        m = re.search(rf"const {name} = '([^']+)'", _LOADER.read_text(encoding='utf-8'))
        return m.group(1) if m else None
    except OSError:
        return None


EXPECTED_AUTHORITY_VERSION = _loader_const('AUTHORITY_INDEX_VERSION')
EXPECTED_CORPUS_VERSION = _loader_const('INDEX_VERSION')


def validate_authority_index():
    """Validate authority index structure and content."""
    print("[CHECK] Validating authority-index.json.gz...")

    if not AUTHORITY_INDEX.exists():
        print(f"[FAIL] File not found: {AUTHORITY_INDEX}")
        return False

    try:
        with gzip.open(AUTHORITY_INDEX, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FAIL] Cannot parse JSON: {e}")
        return False

    # Check required fields
    required_fields = ['version', 'generatedAt', 'lemmata', 'persons', 'works', 'variants']
    for field in required_fields:
        if field not in data:
            print(f"[FAIL] Missing field: {field}")
            return False

    # Check version
    if EXPECTED_AUTHORITY_VERSION and data['version'] != EXPECTED_AUTHORITY_VERSION:
        print(f"[WARN] Version mismatch: {data['version']} (loader expects {EXPECTED_AUTHORITY_VERSION})")

    # Check data types
    if not isinstance(data['lemmata'], list):
        print(f"[FAIL] 'lemmata' must be a list")
        return False

    if not isinstance(data['variants'], dict):
        print(f"[FAIL] 'variants' must be a dict")
        return False

    # Check statistics
    num_lemmata = len(data['lemmata'])
    num_variants = len(data['variants'])
    num_persons = len(data['persons'])
    num_works = len(data['works'])

    print(f"   Lemmata: {num_lemmata:,}")
    print(f"   Variants: {num_variants:,}")
    print(f"   Persons: {num_persons:,}")
    print(f"   Works: {num_works:,}")

    # Sanity checks
    if num_lemmata < 10000:
        print(f"[WARN] Expected >10,000 lemmata, found {num_lemmata}")

    if num_variants < 50000:
        print(f"[WARN] Expected >50,000 variants, found {num_variants}")

    # Check lemma structure
    if num_lemmata > 0:
        sample_lemma = data['lemmata'][0]
        required_lemma_fields = ['id', 'lemma', 'normalized']
        for field in required_lemma_fields:
            if field not in sample_lemma:
                print(f"[FAIL] Lemma missing field: {field}")
                return False

    print("[PASS] Authority index valid")
    return True


def validate_corpus_index():
    """Validate corpus index structure and content."""
    print("\n[CHECK] Validating corpus-index.json.gz...")

    if not CORPUS_INDEX.exists():
        print(f"[FAIL] FAIL: File not found: {CORPUS_INDEX}")
        return False

    try:
        with gzip.open(CORPUS_INDEX, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FAIL] FAIL: Cannot parse JSON: {e}")
        return False

    # Check required fields
    required_fields = ['version', 'generatedAt', 'totalTexts', 'totalLemmata', 'texts', 'lemmaIndex']
    for field in required_fields:
        if field not in data:
            print(f"[FAIL] FAIL: Missing field: {field}")
            return False

    # Check version
    if EXPECTED_CORPUS_VERSION and data['version'] != EXPECTED_CORPUS_VERSION:
        print(f"[WARN] WARNING: Version mismatch: {data['version']} (loader expects {EXPECTED_CORPUS_VERSION})")

    # Check data types
    if not isinstance(data['texts'], list):
        print(f"[FAIL] FAIL: 'texts' must be a list")
        return False

    if not isinstance(data['lemmaIndex'], dict):
        print(f"[FAIL] FAIL: 'lemmaIndex' must be a dict")
        return False

    # Check statistics
    num_texts = len(data['texts'])
    num_lemmata = len(data['lemmaIndex'])
    declared_texts = data['totalTexts']
    declared_lemmata = data['totalLemmata']

    print(f"   Total texts: {num_texts:,} (declared: {declared_texts:,})")
    print(f"   Total unique lemmata: {num_lemmata:,} (declared: {declared_lemmata:,})")

    # Check consistency
    if num_texts != declared_texts:
        print(f"[FAIL] FAIL: Text count mismatch: {num_texts} != {declared_texts}")
        return False

    if num_lemmata != declared_lemmata:
        print(f"[FAIL] FAIL: Lemma count mismatch: {num_lemmata} != {declared_lemmata}")
        return False

    # Sanity checks
    if num_texts < 600:
        print(f"[WARN] WARNING: Expected ~667 texts, found {num_texts}")

    if num_lemmata < 10000:
        print(f"[WARN] WARNING: Expected >10,000 unique lemmata, found {num_lemmata}")

    # Check text structure
    if num_texts > 0:
        sample_text = data['texts'][0]
        required_text_fields = ['id', 'filename', 'title', 'wordCount', 'lemmata']
        for field in required_text_fields:
            if field not in sample_text:
                print(f"[FAIL] FAIL: Text missing field: {field}")
                return False

        # Check lemmata structure
        if not isinstance(sample_text['lemmata'], dict):
            print(f"[FAIL] FAIL: Text lemmata must be a dict")
            return False

        # Check lemma positions
        for lemma_id, positions in sample_text['lemmata'].items():
            if not isinstance(positions, list):
                print(f"[FAIL] FAIL: Lemma positions must be a list")
                return False
            if len(positions) > 0 and not isinstance(positions[0], int):
                print(f"[FAIL] FAIL: Lemma positions must be integers")
                return False
            break  # Just check first one

    # Check lemmaIndex structure
    if num_lemmata > 0:
        sample_lemma_id = list(data['lemmaIndex'].keys())[0]
        sample_text_ids = data['lemmaIndex'][sample_lemma_id]
        if not isinstance(sample_text_ids, list):
            print(f"[FAIL] FAIL: LemmaIndex values must be lists")
            return False

    print("[PASS] PASS: Corpus index valid")
    return True


def main():
    """Main validation entry point."""
    print("=" * 60)
    print("MHDBDB Index Validation")
    print("=" * 60)
    print()

    all_valid = True

    # Validate authority index
    if not validate_authority_index():
        all_valid = False

    # Validate corpus index
    if not validate_corpus_index():
        all_valid = False

    print()
    print("=" * 60)
    if all_valid:
        print("[PASS] All indices valid!")
        return 0
    else:
        print("[FAIL] Validation failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
