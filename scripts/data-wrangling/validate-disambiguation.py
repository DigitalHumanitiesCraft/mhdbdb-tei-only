#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate disambiguation TEI files against their originals.

Checks that .disamb.tei.xml files only differ from originals in:
1. pos attribute values (must be single tags, not compound)
2. Addition of <change> entry in <revisionDesc>

Reports problems if:
- Any other content changed
- Any pos attributes still contain compound tags (spaces)
- Any pos attributes are empty
- Structure differs (elements added/removed)
"""

from lxml import etree
import glob
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def has_compound_tag(pos_value):
    """Check if pos attribute contains compound tag (has space)."""
    if not pos_value:
        return False
    return ' ' in pos_value.strip()

def has_empty_tag(pos_value):
    """Check if pos attribute is empty."""
    return pos_value is None or pos_value.strip() == ''

import unicodedata

def normalize_text(text):
    """Normalize whitespace and Unicode for comparison."""
    if text is None:
        return None
    # Normalize Unicode (NFC = canonical composition)
    normalized = unicodedata.normalize('NFC', text)
    # Normalize whitespace
    return ' '.join(normalized.split())

def compare_elements(orig_el, disamb_el, path="", ignore_change_entry=False):
    """
    Recursively compare two XML elements.
    Returns list of differences (excluding allowed changes).
    """
    differences = []

    # Check tag names match
    if orig_el.tag != disamb_el.tag:
        differences.append(f"{path}: Tag changed from {orig_el.tag} to {disamb_el.tag}")
        return differences

    # Skip comparison of <change> entries in <revisionDesc>
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    if orig_el.tag == f"{{{ns['tei']}}}change" and ignore_change_entry:
        return differences

    # Check attributes (excluding pos)
    orig_attrs = {k: v for k, v in (orig_el.attrib or {}).items() if k != 'pos'}
    disamb_attrs = {k: v for k, v in (disamb_el.attrib or {}).items() if k != 'pos'}

    if orig_attrs != disamb_attrs:
        differences.append(f"{path}: Non-pos attributes changed")

    # Check text content
    orig_text = normalize_text(orig_el.text)
    disamb_text = normalize_text(disamb_el.text)
    if orig_text != disamb_text:
        differences.append(f"{path}: Text content changed FROM:\n {orig_text} \nTO:\n {disamb_text}")

    # Check tail content
    orig_tail = normalize_text(orig_el.tail)
    disamb_tail = normalize_text(disamb_el.tail)
    if orig_tail != disamb_tail:
        differences.append(f"{path}: Tail content changed")

    # Check children count
    orig_children = list(orig_el)
    disamb_children = list(disamb_el)

    # If we're in revisionDesc, allow extra <change> entries
    if orig_el.tag.endswith('revisionDesc'):
        # Filter out extra change entries in disamb
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        orig_changes = [c for c in orig_children if c.tag == f"{{{ns['tei']}}}change"]
        disamb_changes = [c for c in disamb_children if c.tag == f"{{{ns['tei']}}}change"]

        # Should have exactly one more change entry
        if len(disamb_changes) != len(orig_changes) + 1:
            differences.append(f"{path}: Expected exactly one additional <change> entry")

        # Compare children excluding the extra change entry
        for i, orig_child in enumerate(orig_children):
            if i < len(disamb_children):
                child_path = f"{path}/{orig_child.tag.split('}')[-1]}[{i}]"
                differences.extend(compare_elements(orig_child, disamb_children[i], child_path, ignore_change_entry=True))
    else:
        if len(orig_children) != len(disamb_children):
            differences.append(f"{path}: Number of child elements changed ({len(orig_children)} -> {len(disamb_children)})")
            return differences

        # Compare children recursively
        for i, (orig_child, disamb_child) in enumerate(zip(orig_children, disamb_children)):
            child_path = f"{path}/{orig_child.tag.split('}')[-1]}[{i}]"
            differences.extend(compare_elements(orig_child, disamb_child, child_path))

    return differences

def validate_file_pair(orig_path, disamb_path):
    """
    Validate a disambiguation file against its original.
    Returns tuple (has_problems, problems_list).
    """
    problems = []

    try:
        # Parse both files
        orig_tree = etree.parse(str(orig_path))
        disamb_tree = etree.parse(str(disamb_path))

        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        # Check for compound tags in disamb file (check ALL <w> elements)
        disamb_words = disamb_tree.xpath('//tei:w', namespaces=ns)
        compound_tags = []
        empty_tags = []

        for word in disamb_words:
            pos = word.get('pos')
            word_id = word.get("{http://www.w3.org/XML/1998/namespace}id", "unknown")

            if has_empty_tag(pos):
                empty_tags.append(word_id)
            elif has_compound_tag(pos):
                compound_tags.append(f"{word_id}: pos='{pos}'")

        if compound_tags:
            problems.append(f"Still has {len(compound_tags)} compound PoS tag(s):")
            problems.extend(f"  - {tag}" for tag in compound_tags[:5])  # Show first 5
            if len(compound_tags) > 5:
                problems.append(f"  ... and {len(compound_tags) - 5} more")

        if empty_tags:
            problems.append(f"Has {len(empty_tags)} empty PoS tag(s):")
            problems.extend(f"  - {tag}" for tag in empty_tags[:5])
            if len(empty_tags) > 5:
                problems.append(f"  ... and {len(empty_tags) - 5} more")

        # Compare structure and content (excluding pos attributes and change entries)
        orig_root = orig_tree.getroot()
        disamb_root = disamb_tree.getroot()

        differences = compare_elements(orig_root, disamb_root, "root")

        if differences:
            problems.append(f"Unexpected changes found:")
            problems.extend(f"  - {diff}" for diff in differences[:10])  # Show first 10
            if len(differences) > 10:
                problems.append(f"  ... and {len(differences) - 10} more")

    except Exception as e:
        problems.append(f"Error validating: {e}")

    return len(problems) > 0, problems

def main():
    """Find and validate all disambiguation file pairs in tei/ folder."""
    tei_dir = Path(__file__).parent.parent.parent / 'tei'

    # Find all .disamb.tei.xml files
    disamb_files = sorted(tei_dir.glob('*.disamb.tei.xml'))

    if not disamb_files:
        print("No disambiguation files found in tei/ folder")
        return

    all_ok = True

    for disamb_path in disamb_files:
        # Find corresponding original file
        orig_filename = disamb_path.name.replace('.disamb.tei.xml', '.tei.xml')
        orig_path = tei_dir / orig_filename

        if not orig_path.exists():
            print(f"\nProblems found in {disamb_path.name}:")
            print(f"  - Original file not found: {orig_filename}")
            all_ok = False
            continue

        # Validate the pair
        has_problems, problems = validate_file_pair(orig_path, disamb_path)

        if has_problems:
            print(f"\nProblems found in {disamb_path.name}:")
            print()
            for problem in problems:
                print(problem)
                print()
            all_ok = False

    if all_ok:
        print("ALL OK")
        print(f"✓ Validated {len(disamb_files)} disambiguation file(s)")

if __name__ == '__main__':
    main()
