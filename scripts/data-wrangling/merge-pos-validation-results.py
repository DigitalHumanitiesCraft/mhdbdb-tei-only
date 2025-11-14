#!/usr/bin/env python3
"""
Merge LLM validation results from markdown files back into TEI file.

This script reads markdown result files produced by the LLM and applies
the PoS tag changes to create a disambiguated TEI file.

Usage:
    python scripts/merge-validation-results.py temp/disambiguation ABG.tei tei/ABG.tei.xml
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime
from lxml import etree

# TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def parse_result_line(line):
    """
    Parse a result line in format:
    xml_id | old_pos → new_pos | confidence | reason

    Returns dict with parsed data or None if line doesn't match format.
    """
    # Match pattern: xml_id | old_pos → new_pos | confidence | reason
    # Also handle: xml_id | pos → pos | ✓ correct | reason (no change)
    pattern = r'^([A-Z_0-9]+)\s*\|\s*(.+?)\s*→\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)$'
    match = re.match(pattern, line.strip())

    if not match:
        return None

    xml_id, old_pos, new_pos, confidence, reason = match.groups()

    # Clean up fields
    xml_id = xml_id.strip()
    old_pos = old_pos.strip()
    new_pos = new_pos.strip()
    confidence = confidence.strip().replace('✓ correct', 'high')
    reason = reason.strip()

    # Determine if this is a change
    is_change = old_pos != new_pos

    return {
        'xml_id': xml_id,
        'old_pos': old_pos,
        'new_pos': new_pos,
        'confidence': confidence,
        'reason': reason,
        'is_change': is_change
    }

def load_validation_results(results_dir, sigle):
    """Load all result markdown files and parse decisions."""
    results_dir = Path(results_dir)
    # Files are named like "ABG.tei-chunk-001-result.md"
    # Try with .tei extension first, then without
    result_files = sorted(results_dir.glob(f"{sigle}.tei-chunk-*-result.md"))
    if not result_files:
        result_files = sorted(results_dir.glob(f"{sigle}-chunk-*-result.md"))

    if not result_files:
        print(f"ERROR: No result files found matching {sigle}.tei-chunk-*-result.md or {sigle}-chunk-*-result.md in {results_dir}")
        return None

    print(f"Found {len(result_files)} result files")

    decisions = {}

    for result_file in result_files:
        print(f"  Reading {result_file.name}...")

        with open(result_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Look for lines matching the result format
        for line in lines:
            result = parse_result_line(line)
            if result:
                decisions[result['xml_id']] = result

    print(f"\nParsed {len(decisions)} validation decisions")
    return decisions

def update_tei_file(original_file, decisions):
    """Update TEI file with validation results."""
    parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
    tree = etree.parse(original_file, parser)
    root = tree.getroot()

    changes_made = 0
    low_confidence_count = 0
    change_log = []

    # Update <w> elements
    for w in root.xpath('.//tei:w', namespaces=NS):
        xml_id = w.get('{http://www.w3.org/XML/1998/namespace}id')

        if xml_id in decisions:
            decision = decisions[xml_id]
            old_pos = decision['old_pos']
            new_pos = decision['new_pos']

            if decision['is_change']:
                w.set('pos', new_pos)
                changes_made += 1

                # Add comment for low-confidence decisions
                if 'low' in decision['confidence'].lower():
                    low_confidence_count += 1
                    comment = etree.Comment(
                        f' LOW CONFIDENCE: Changed pos="{old_pos}" to pos="{new_pos}" ({decision["reason"]}) '
                    )
                    parent = w.getparent()
                    parent.insert(parent.index(w), comment)

                # Log change
                change_log.append({
                    'xml_id': xml_id,
                    'word': w.text or '',
                    'old_pos': old_pos,
                    'new_pos': new_pos,
                    'reason': decision['reason'],
                    'confidence': decision['confidence']
                })

    # Update <revisionDesc>
    revision_desc = root.find('.//tei:revisionDesc', namespaces=NS)
    if revision_desc is not None:
        today = datetime.now().strftime('%Y-%m-%d')
        change_entry = etree.Element('change')
        change_entry.set('when', today)
        change_entry.set('who', '#claude')
        change_entry.text = f'PoS validation: LLM-based validation and disambiguation of {changes_made} tags'

        # Insert as first child
        revision_desc.insert(0, change_entry)

    return tree, change_log, changes_made, low_confidence_count

def save_disambiguation_report(change_log, sigle, output_file, total_changes, low_conf_count, total_validated):
    """Generate detailed markdown report."""
    today = datetime.now().strftime('%Y-%m-%d')

    compound_tags = sum(1 for c in change_log if ' ' in c['old_pos'])
    single_tags = total_changes - compound_tags

    report = f"""# PoS Validation Report: {sigle}.tei.xml

**Date:** {today}
**File:** tei/{sigle}.tei.xml → tei/{sigle}.disamb.tei.xml
**Total Validated:** {total_validated} words
**Total Changes:** {total_changes}
**Method:** LLM-based context analysis with chunked processing

---

## Changes Made

"""

    for i, change in enumerate(change_log, 1):
        conf_flag = ' [LOW CONFIDENCE]' if 'low' in change['confidence'].lower() else ''
        report += f"{i}. **{change['xml_id']}** `{change['word']}`: `{change['old_pos']}` → `{change['new_pos']}` - {change['reason']}{conf_flag}\n"

    report += f"""
---

## Summary

- Compound tags resolved: {compound_tags}
- Single tags corrected: {single_tags}
- Low-confidence decisions: {low_conf_count}
- Total words validated: {total_validated}

---

**Generated by:** Claude Code PoS Validator (Markdown Workflow)
**Model:** Claude Sonnet 4.5
**Workflow:** Chunked markdown → LLM analysis → Merged results
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    parser = argparse.ArgumentParser(description='Merge validation results from markdown into TEI file')
    parser.add_argument('results_dir', help='Directory with result markdown files (e.g., temp/disambiguation)')
    parser.add_argument('sigle', help='SIGLE identifier (e.g., ABG.tei)')
    parser.add_argument('original_tei', help='Path to original TEI file (e.g., tei/ABG.tei.xml)')
    parser.add_argument('--output', help='Output TEI file (default: tei/{SIGLE}.disamb.tei.xml)')
    parser.add_argument('--report', help='Output report file (default: tei/{SIGLE}.disambiguation-report.md)')

    args = parser.parse_args()

    # Clean SIGLE (remove .tei extension if present)
    sigle = args.sigle.replace('.tei', '')

    # Load validation results
    print(f"Loading validation results for {sigle}...")
    decisions = load_validation_results(args.results_dir, sigle)

    if decisions is None:
        return 1

    # Determine output paths
    original_path = Path(args.original_tei)
    output_tei = args.output or original_path.parent / f"{sigle}.disamb.tei.xml"
    output_report = args.report or original_path.parent / f"{sigle}.disambiguation-report.md"

    # Update TEI file
    print(f"\nUpdating {original_path}...")
    tree, change_log, total_changes, low_conf_count = update_tei_file(args.original_tei, decisions)

    # Save updated TEI
    tree.write(output_tei, encoding='utf-8', xml_declaration=True, pretty_print=False)
    print(f"[OK] Saved {output_tei}")
    print()

    # Save report
    total_validated = len(decisions)
    save_disambiguation_report(change_log, sigle, output_report, total_changes, low_conf_count, total_validated)
    print(f"[OK] Saved {output_report}")
    print()

    # Summary
    print("=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Total words validated: {total_validated}")
    print(f"Total changes: {total_changes}")
    print(f"Low-confidence decisions: {low_conf_count}")
    print()
    print("Output files:")
    print(f"  - {output_tei}")
    print(f"  - {output_report}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
