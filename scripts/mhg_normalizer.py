#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHG (Middle High German) Text Normalizer

CRITICAL: This module MUST produce IDENTICAL normalization results
as assets/js/lib/text-normalizer.js

Any discrepancy will cause search failures between build-time indices
and runtime search.

Parity tests: testing/tests/normalization-parity.spec.js
"""

import sys
import unicodedata
import io

# Force UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def normalize_mhg(text):
    """
    Normalize Middle High German text for consistent search.

    Must match TextNormalizer.normalizeMHG() in assets/js/lib/text-normalizer.js EXACTLY.

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

    # Step 0: Unicode-Komposition (#224). Muss mit .normalize('NFC') in
    # text-normalizer.js uebereinstimmen. Ein "oe" kann als ein Zeichen
    # (U+00F6) oder als o + kombinierendes Trema (U+006F U+0308) kodiert
    # sein; nur die komponierte Form trifft die Umlaut-Regeln unten.
    # Die Authority-Files sind durchgaengig NFC, dieser Schritt aendert die
    # Build-Ausgabe also nicht (verifiziert: Index byte-identisch). Er
    # schuetzt die Laufzeit-Eingabe und kuenftige Ingests.
    normalized = unicodedata.normalize('NFC', text)

    # Step 1: Lowercase (like JavaScript)
    normalized = normalized.lower()

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
