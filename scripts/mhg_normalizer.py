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
    # Der Schritt aendert die Build-Ausgabe an genau drei Datensaetzen
    # (person_1052, person_1332, work_435 tragen ein zerlegtes ue); der
    # Authority-Index geht dadurch auf 1.6.2, drei api/-Dateien aendern sich.
    # Lemmata und Varianten-Schluessel bleiben unveraendert. Kuenftige Ingests
    # sind damit gegen dieselbe Falle abgesichert.
    # Siehe docs/CONTRACTS.md Contract A, Schritt 0.
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
    # Breve ueber o/u ist in der Wenzelsbibel das Umlautzeichen, nicht ein
    # eigener Laut (#224, bestaetigt an 469 lemmatisierten WZB-Tokens:
    # bo+breve+ses -> lemma_788 boese, scho+breve+ne -> lemma_5280 schoene,
    # wu+breve+nschet -> wuenschet). Greift nach Schritt 0, weil NFC das
    # kombinierende Breve (U+0306) auf o/u zu U+014F/U+016D zusammenzieht.
    # Breve auf w/n/y/z (WZB, 130 Tokens) hat KEINE praekomponierte Form,
    # bleibt also unangetastet: dort ist es kein Umlautzeichen.
    normalized = normalized.replace('ŏ', 'oe')
    normalized = normalized.replace('ŭ', 'ue')

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
    # Schritt 0, NFC (#224): zerlegte Umlaute muessen wie komponierte
    # normalisieren. Ohne die NFC-Komposition bleibt das kombinierende Trema
    # stehen und die Umlaut-Regeln greifen nicht.
    # Escapes statt Literale: ein Editor mit Auto-Normalisierung wuerde die
    # zerlegte Form still zu NFC zusammenziehen und den Test entwerten.
    ('bo\u0308ses', 'boeses'),        # o + kombinierendes Trema statt ö
    ('Mu\u0308hldorf', 'muehldorf'),  # dito mit ü und Grossbuchstabe
    # Breve-Umlaute (#224, WZB). Escapes wie oben.
    ('bo\u0306ses', 'boeses'),     # zerlegt: NFC zieht zu o-Breve zusammen
    ('b\u014fses', 'boeses'),      # praekomponiert
    ('w\u016dnschet', 'wuenschet'),
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
