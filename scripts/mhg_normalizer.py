#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHG (Middle High German) Text Normalizer

CRITICAL: This module MUST produce IDENTICAL normalization results
as playground/js/utils/text-normalizer.js

Any discrepancy will cause search failures between build-time indices
and runtime search.

Parity tests: testing/tests/normalization-parity.spec.js
"""

import sys
import io

# Force UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def normalize_mhg(text):
    """
    Normalize Middle High German text for consistent search.

    Must match TextNormalizer.normalizeMHG() in text-normalizer.js EXACTLY.

    Transformations:
    - Long vowels → short: â→a, ê→e, î→i, ô→o, û→u (and ā,ē,ī,ō,ū variants)
    - Umlauts → digraphs: ä→ae, ö→oe, ü→ue
    - Ligatures: æ→ae, œ→oe
    - Special: ǒ→o
    - Lowercase all

    Args:
        text (str): Text to normalize

    Returns:
        str: Normalized text (lowercase, special chars replaced)
    """
    if not text:
        return ''

    # Must match JavaScript order and replacements EXACTLY
    # JavaScript: text.toLowerCase().replace(/[âā]/g, 'a').replace(...)

    # Step 1: Lowercase FIRST (like JavaScript)
    normalized = text.lower()

    # Step 2: Replace long vowels with circumflex and macron
    normalized = normalized.replace('â', 'a').replace('ā', 'a')
    normalized = normalized.replace('ê', 'e').replace('ē', 'e')
    normalized = normalized.replace('î', 'i').replace('ī', 'i')
    normalized = normalized.replace('ô', 'o').replace('ō', 'o')
    normalized = normalized.replace('û', 'u').replace('ū', 'u')

    # Step 3: Umlauts → digraphs
    normalized = normalized.replace('ä', 'ae')
    normalized = normalized.replace('ö', 'oe')
    normalized = normalized.replace('ü', 'ue')

    # Step 4: Ligatures
    normalized = normalized.replace('æ', 'ae')
    normalized = normalized.replace('œ', 'oe')

    # Step 5: Other special characters
    normalized = normalized.replace('ǒ', 'o')

    return normalized


def matches_normalized(text, search_term):
    """
    Check if text contains search term (with normalization).

    Args:
        text (str): Text to search in
        search_term (str): Term to search for

    Returns:
        bool: True if normalized text contains normalized search term
    """
    if not text or not search_term:
        return False

    normalized_text = normalize_mhg(text)
    normalized_search = normalize_mhg(search_term)

    return normalized_search in normalized_text


def exact_match_normalized(text, search_term):
    """
    Check for exact match (with normalization).

    Args:
        text (str): Text to compare
        search_term (str): Term to match exactly

    Returns:
        bool: True if normalized texts are identical
    """
    if not text or not search_term:
        return False

    return normalize_mhg(text) == normalize_mhg(search_term)


def starts_with_normalized(text, search_term):
    """
    Check if text starts with search term (with normalization).

    Args:
        text (str): Text to check
        search_term (str): Term to check for at start

    Returns:
        bool: True if normalized text starts with normalized search term
    """
    if not text or not search_term:
        return False

    normalized_text = normalize_mhg(text)
    normalized_search = normalize_mhg(search_term)

    return normalized_text.startswith(normalized_search)


# Test cases for validation
TEST_CASES = [
    # (input, expected_output)
    ('brôt', 'brot'),
    ('BRÔT', 'brot'),
    ('wîn', 'win'),
    ('vriunt', 'vriunt'),
    ('schône', 'schone'),  # ô→o (CORRECTED: ô not ö!)
    ('schöne', 'schoene'),  # ö→oe (added test with actual umlaut)
    ('Âventiure', 'aventiure'),  # Â→â→a
    ('mære', 'maere'),  # æ→ae
    ('âne', 'ane'),
    ('fröude', 'froeude'),  # ö→oe
    ('müede', 'mueede'),  # ü→ue, original has 'e' already → mueede (CORRECTED from 'muede')
    ('ûzer', 'uzer'),
    ('ōre', 'ore'),  # ō→o
    ('sǒne', 'sone'),  # ǒ→o
    ('cæsar', 'caesar'),  # æ→ae
    ('œnologie', 'oenologie'),  # œ→oe
    ('', ''),
    (None, ''),
]


def run_self_test():
    """
    Run self-test to validate normalization logic.
    Returns number of failures.
    """
    print("Running MHG normalizer self-test...")
    failures = 0

    for input_text, expected in TEST_CASES:
        result = normalize_mhg(input_text)
        if result != expected:
            print(f"[FAIL] normalize_mhg({input_text!r}) = {result!r}, expected {expected!r}")
            failures += 1
        else:
            print(f"[PASS] normalize_mhg({input_text!r}) = {result!r}")

    if failures == 0:
        print(f"\n[SUCCESS] All {len(TEST_CASES)} tests passed!")
    else:
        print(f"\n[FAILURE] {failures}/{len(TEST_CASES)} tests failed")

    return failures


if __name__ == '__main__':
    import sys

    # Run self-test when executed directly
    failures = run_self_test()
    sys.exit(1 if failures > 0 else 0)
