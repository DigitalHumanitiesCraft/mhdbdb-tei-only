#!/usr/bin/env python3
"""
Test script to verify we're extracting all available data from Zotero API.

Compares what's in the Zotero cache vs what we generate in biblStruct elements.
"""

import json
import sys
import io
from collections import defaultdict
from lxml import etree

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import the conversion functions
sys.path.insert(0, 'scripts/data-wrangling')
from enhance_works_with_zotero import api_item_to_biblstruct, convert_to_title_case

def load_zotero_cache():
    """Load the Zotero cache file."""
    with open('scripts/data-wrangling/.zotero_cache.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def test_data_extraction():
    """Test if all Zotero data is being extracted."""
    print("=" * 80)
    print("Zotero Data Extraction Test")
    print("=" * 80)

    cache = load_zotero_cache()
    items = cache['items']

    # Build notes map
    notes_map = {}
    for item in items:
        data = item.get('data', {})
        if data.get('itemType') == 'note':
            parent_key = data.get('parentItem')
            if parent_key:
                if parent_key not in notes_map:
                    notes_map[parent_key] = []
                notes_map[parent_key].append(data.get('note', ''))

    # Test a sample of different item types
    test_items = {
        'book': 'AXS',  # Lamprechts Alexander (has author + editor)
        'bookSection': 'TKA',  # Abriss (has editor)
        'book_with_volume': 'WUT',  # Willehalm (has volume)
        'book_with_edition': 'AT',  # Alpharts Tod (has edition field)
        'journalArticle_no_editor': 'ASG',  # Article without editor (new test!)
        'journalArticle': None,  # Will find first one with editor
    }

    # Find journal article
    for item in items:
        data = item.get('data', {})
        if data.get('itemType') == 'journalArticle' and data.get('callNumber'):
            test_items['journalArticle'] = data.get('callNumber')
            break

    print(f"\nTesting {len(test_items)} sample items:\n")

    all_passed = True

    for test_name, call_number in test_items.items():
        if not call_number:
            continue

        print(f"\n{'-' * 80}")
        print(f"Testing: {test_name} (callNumber: {call_number})")
        print(f"{'-' * 80}")

        # Find the item
        zotero_item = None
        for item in items:
            data = item.get('data', {})
            if data.get('callNumber') == call_number:
                zotero_item = item
                break

        if not zotero_item:
            print(f"  [FAIL] Item not found in cache")
            all_passed = False
            continue

        item_data = zotero_item['data']
        item_key = zotero_item['key']
        item_notes = notes_map.get(item_key, [])

        # Generate biblStruct (always returns a biblStruct now)
        biblstruct = api_item_to_biblstruct(item_data, call_number, item_notes)

        # Convert to string for inspection
        biblstruct_xml = etree.tostring(biblstruct, encoding='unicode', pretty_print=True)

        # Check key fields
        checks = []

        # Check creators (authors/editors)
        creators = item_data.get('creators', [])
        authors = [c for c in creators if c.get('creatorType') == 'author']
        editors = [c for c in creators if c.get('creatorType') == 'editor']

        print(f"\n  Creators in Zotero:")
        print(f"    Authors: {len(authors)}")
        for author in authors:
            name = author.get('name', f"{author.get('firstName', '')} {author.get('lastName', '')}").strip()
            print(f"      - {name}")

            # Check for either:
            # 1. Full name as single string (for 'name' field)
            # 2. First and last name separately (for 'firstName'/'lastName' fields)
            first_name = author.get('firstName', '')
            last_name = author.get('lastName', '')

            found = False
            if 'name' in author:
                # Single name field - search for exact match
                found = author['name'] in biblstruct_xml
            elif first_name and last_name:
                # Separate fields - check if both are present
                found = first_name in biblstruct_xml and last_name in biblstruct_xml
            else:
                # Fallback to full name search
                found = name in biblstruct_xml

            if found:
                print(f"        [OK] Found in biblStruct")
                checks.append(('author', name, True))
            else:
                print(f"        [FAIL] NOT found in biblStruct")
                checks.append(('author', name, False))
                all_passed = False

        print(f"    Editors: {len(editors)}")
        for editor in editors:
            name = editor.get('name', f"{editor.get('firstName', '')} {editor.get('lastName', '')}").strip()
            print(f"      - {name}")

            # Check for either:
            # 1. Full name as single string (for 'name' field)
            # 2. First and last name separately (for 'firstName'/'lastName' fields)
            first_name = editor.get('firstName', '')
            last_name = editor.get('lastName', '')

            found = False
            if 'name' in editor:
                # Single name field - search for exact match
                found = editor['name'] in biblstruct_xml
            elif first_name and last_name:
                # Separate fields - check if both are present
                found = first_name in biblstruct_xml and last_name in biblstruct_xml
            else:
                # Fallback to full name search
                found = name in biblstruct_xml

            if found:
                print(f"        [OK] Found in biblStruct")
                checks.append(('editor', name, True))
            else:
                print(f"        [FAIL] NOT found in biblStruct")
                checks.append(('editor', name, False))
                all_passed = False

        # Check key fields
        # Note: titles are converted to Title Case, so we need to check the converted version
        title_fields = {'title', 'bookTitle', 'publicationTitle', 'series'}

        fields_to_check = {
            'title': item_data.get('title'),
            'bookTitle': item_data.get('bookTitle'),
            'publicationTitle': item_data.get('publicationTitle'),
            'place': item_data.get('place'),
            'publisher': item_data.get('publisher'),
            'date': item_data.get('date'),
            'pages': item_data.get('pages'),
            'volume': item_data.get('volume'),
            'issue': item_data.get('issue'),
            'ISBN': item_data.get('ISBN'),
            'series': item_data.get('series'),
            'seriesNumber': item_data.get('seriesNumber'),
            'edition': item_data.get('edition'),
        }

        print(f"\n  Key Fields:")
        for field_name, field_value in fields_to_check.items():
            if field_value:
                # For title fields, check the Title Case version
                if field_name in title_fields:
                    expected_value = convert_to_title_case(str(field_value))
                else:
                    expected_value = str(field_value)

                if expected_value in biblstruct_xml:
                    print(f"    [OK] {field_name}: {field_value}")
                    checks.append((field_name, field_value, True))
                else:
                    print(f"    [FAIL] {field_name}: {field_value} (Expected Title Case: {expected_value}) (NOT IN biblStruct)")
                    checks.append((field_name, field_value, False))
                    all_passed = False

        # Check notes
        if item_notes:
            print(f"\n  Notes: {len(item_notes)} note(s)")
            for i, note in enumerate(item_notes, 1):
                note_snippet = note[:60] + "..." if len(note) > 60 else note
                if note in biblstruct_xml:
                    print(f"    [OK] Note {i}: {note_snippet}")
                    checks.append((f'note_{i}', note_snippet, True))
                else:
                    print(f"    [FAIL] Note {i}: {note_snippet} (NOT IN biblStruct)")
                    checks.append((f'note_{i}', note_snippet, False))
                    all_passed = False

        # Summary for this item
        failed_checks = [c for c in checks if not c[2]]
        if failed_checks:
            print(f"\n  [FAIL] {len(failed_checks)} field(s) missing from biblStruct")
        else:
            print(f"\n  [OK] All fields present in biblStruct")

    # Final summary
    print(f"\n{'=' * 80}")
    if all_passed:
        print("[PASS] ALL TESTS PASSED - All Zotero data is being extracted")
    else:
        print("[FAIL] SOME TESTS FAILED - Some Zotero data is NOT being extracted")
    print(f"{'=' * 80}\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(test_data_extraction())
