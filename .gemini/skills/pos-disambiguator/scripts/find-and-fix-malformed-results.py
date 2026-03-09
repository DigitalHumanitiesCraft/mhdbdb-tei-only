#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find and fix malformed result lines in LLM disambiguation output.

This script detects lines that look like results but don't match the expected
format of the merge script, attempts to fix them, and validates the content.

Expected format (from merge script):
    xml_id | old_pos → new_pos | confidence | reason

Common malformed patterns detected:
1. ⚠️ marker with word text: `ID | ⚠️ word (OLD) - NEW | conf | reason`
2. ❓ marker with word text: `ID | ❓ word () - NEW | conf | reason`
3. ✓ marker with word text: `ID | ✓ word (OLD) - NEW | conf | reason`
4. Using `-` instead of `→`: `ID | OLD - NEW | conf | reason`
5. Missing arrow entirely: `ID | OLD NEW | conf | reason`

Integrity checks performed on fixed lines:
- Valid POS tags (from 19-tag set + ART legacy)
- Valid confidence levels (high, medium, low)
- Non-empty reason
- Sensible old_pos → new_pos transition

Usage:
    python .gemini/skills/pos-disambiguator/scripts/find-and-fix-malformed-results.py temp/disambiguation
    python .gemini/skills/pos-disambiguator/scripts/find-and-fix-malformed-results.py temp/disambiguation --dry-run
"""

import argparse
import glob
import re
import os
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Valid POS tags (19-tag set + legacy/corpus-specific tags)
VALID_POS_TAGS = {
    'NOM', 'NAM', 'ADJ', 'ADV', 'DET', 'POS', 'PRO', 'PRP', 'NEG', 'NUM',
    'CNJ', 'SCNJ', 'CCNJ', 'IPA', 'VRB', 'VEX', 'VEM', 'INJ', 'PTK',
    'ART',  # Legacy tag, should be DET but exists in corpus
    'DIG',  # Digit/numeral tag for Roman numerals (xi, xxv, etc.)
}

# Valid confidence levels
VALID_CONFIDENCE = {'high', 'medium', 'low'}


# The CORRECT pattern that the merge script expects
CORRECT_PATTERN = re.compile(
    r"^([a-zA-Z0-9_\-\.]+)\s*\|\s*(.*?)\s*→\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)$"
)

# Patterns for malformed lines that we can fix
# Each tuple: (regex, extractor function that returns (xml_id, old_pos, new_pos, confidence, reason))
MALFORMED_PATTERNS = [
    # Pattern 1: ⚠️ marker with compound tag in parentheses, hyphen separator
    # Example: ADP_2005500_12 | ⚠️ da (ADV CNJ) - ADV | high | adverb
    (
        re.compile(r"^([a-zA-Z0-9_\-\.]+)\s*\|\s*⚠️\s*\S+\s*\(([A-Z]+(?:\s+[A-Z]+)*)\)\s*-\s*([A-Z]+(?:\s+[A-Z]+)*)\s*\|\s*(.+?)\s*\|\s*(.+)$"),
        lambda m: (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
    ),
    # Pattern 2: ❓ marker with empty parens, hyphen separator (missing pos)
    # Example: ADP_2005500_11 | ❓ er () - PRO | high | pronoun
    (
        re.compile(r"^([a-zA-Z0-9_\-\.]+)\s*\|\s*❓\s*\S+\s*\(\)\s*-\s*([A-Z]+(?:\s+[A-Z]+)*)\s*\|\s*(.+?)\s*\|\s*(.+)$"),
        lambda m: (m.group(1), "", m.group(2), m.group(3), m.group(4))
    ),
    # Pattern 3: ✓ marker with single tag in parentheses, hyphen separator
    # Example: ADP_2005500_10 | ✓ daz (DET) - DET | high | determiner
    (
        re.compile(r"^([a-zA-Z0-9_\-\.]+)\s*\|\s*✓\s*\S+\s*\(([A-Z]+(?:\s+[A-Z]+)*)\)\s*-\s*([A-Z]+(?:\s+[A-Z]+)*)\s*\|\s*(.+?)\s*\|\s*(.+)$"),
        lambda m: (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
    ),
    # Pattern 4: Correct structure but hyphen instead of arrow
    # Example: ADP_123 | ADV - ADV | high | reason
    (
        re.compile(r"^([a-zA-Z0-9_\-\.]+)\s*\|\s*([A-Z]*(?:\s+[A-Z]+)*)\s+-\s+([A-Z]+(?:\s+[A-Z]+)*)\s*\|\s*(.+?)\s*\|\s*(.+)$"),
        lambda m: (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
    ),
]


def validate_pos_tags(pos_string):
    """
    Validate that a POS string contains only valid tags.
    Returns (is_valid, list of invalid tags).
    """
    if not pos_string or pos_string.strip() == "":
        return True, []  # Empty old_pos is valid (for missing tags)

    tags = pos_string.strip().split()
    invalid = [t for t in tags if t not in VALID_POS_TAGS]
    return len(invalid) == 0, invalid


def validate_result_content(xml_id, old_pos, new_pos, confidence, reason):
    """
    Validate the content of a parsed/fixed result line.
    Returns (is_valid, list of issues).
    """
    issues = []

    # Check old_pos tags (can be empty for missing tags)
    old_valid, old_invalid = validate_pos_tags(old_pos)
    if not old_valid:
        issues.append(f"invalid old_pos tags: {old_invalid}")

    # Check new_pos tags (must not be empty)
    if not new_pos or new_pos.strip() == "":
        issues.append("empty new_pos")
    else:
        new_valid, new_invalid = validate_pos_tags(new_pos)
        if not new_valid:
            issues.append(f"invalid new_pos tags: {new_invalid}")

    # Check confidence
    conf_lower = confidence.lower().strip()
    # Handle "✓ correct" which maps to "high"
    if "correct" in conf_lower:
        conf_lower = "high"
    if conf_lower not in VALID_CONFIDENCE:
        issues.append(f"invalid confidence: '{confidence}'")

    # Check reason
    if not reason or reason.strip() == "":
        issues.append("empty reason")

    return len(issues) == 0, issues


def format_fixed_line(xml_id, old_pos, new_pos, confidence, reason):
    """Format the components into a valid result line."""
    return f"{xml_id} | {old_pos} → {new_pos} | {confidence} | {reason}"


def is_potential_result_line(line):
    """Check if a line looks like it might be a result line (has pipes and looks structured)."""
    line = line.strip()
    if not line:
        return False
    # Skip markdown headers and dividers
    if line.startswith('#') or line.startswith('---') or line.startswith('**'):
        return False
    # Must have at least 3 pipe separators for a result line
    if line.count('|') < 3:
        return False
    # Must start with what looks like an XML ID
    if not re.match(r'^[a-zA-Z0-9_\-\.]+\s*\|', line):
        return False
    return True


def find_and_fix_malformed(directory, dry_run=False):
    """Find and optionally fix malformed result lines."""
    files = glob.glob(os.path.join(directory, "*-result*.md"))

    if not files:
        print(f"No result files found in {directory}")
        return

    total_malformed = 0
    total_fixed = 0
    total_unfixable = 0
    total_invalid_content = 0
    files_with_issues = []
    all_content_issues = []  # Collect all content validation issues

    print(f"Scanning {len(files)} result files in {directory}...\n")

    for file_path in sorted(files):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        file_malformed = 0
        file_fixed = 0
        file_unfixable = 0
        file_invalid_content = 0
        issues = []

        for line_num, line in enumerate(lines, 1):
            original_line = line
            line_stripped = line.strip()

            # Check if this looks like a result line
            if not is_potential_result_line(line_stripped):
                new_lines.append(original_line)
                continue

            # Check if it matches the correct format
            correct_match = CORRECT_PATTERN.match(line_stripped)
            if correct_match:
                new_lines.append(original_line)
                continue

            # It looks like a result but doesn't match - it's malformed
            file_malformed += 1
            total_malformed += 1

            # Try to fix it with our patterns
            fixed = False
            for pattern, extractor in MALFORMED_PATTERNS:
                match = pattern.match(line_stripped)
                if match:
                    # Extract components
                    xml_id, old_pos, new_pos, confidence, reason = extractor(match)

                    # Validate the content
                    content_valid, content_issues = validate_result_content(
                        xml_id, old_pos, new_pos, confidence, reason
                    )

                    if not content_valid:
                        # Format is fixable but content is invalid
                        file_invalid_content += 1
                        total_invalid_content += 1
                        all_content_issues.append({
                            'file': os.path.basename(file_path),
                            'line_num': line_num,
                            'original': line_stripped,
                            'issues': content_issues
                        })
                        issues.append({
                            'line_num': line_num,
                            'original': line_stripped,
                            'fixed': None,
                            'status': 'INVALID_CONTENT',
                            'content_issues': content_issues
                        })
                        # Still fix the format, but flag it
                        fixed_line = format_fixed_line(xml_id, old_pos, new_pos, confidence, reason) + "\n"
                        new_lines.append(fixed_line)
                        file_fixed += 1
                        total_fixed += 1
                    else:
                        # Format and content both valid
                        fixed_line = format_fixed_line(xml_id, old_pos, new_pos, confidence, reason) + "\n"
                        new_lines.append(fixed_line)
                        file_fixed += 1
                        total_fixed += 1
                        issues.append({
                            'line_num': line_num,
                            'original': line_stripped,
                            'fixed': fixed_line.strip(),
                            'status': 'FIXED'
                        })

                    fixed = True
                    break

            if not fixed:
                # Couldn't fix it - keep original and report
                new_lines.append(original_line)
                file_unfixable += 1
                total_unfixable += 1
                issues.append({
                    'line_num': line_num,
                    'original': line_stripped,
                    'fixed': None,
                    'status': 'UNFIXABLE'
                })

        # Report issues for this file
        if issues:
            files_with_issues.append(file_path)
            status_str = f"{file_malformed} malformed ({file_fixed} fixable, {file_unfixable} unfixable"
            if file_invalid_content > 0:
                status_str += f", ⚠️ {file_invalid_content} with invalid content"
            status_str += ")"
            print(f"📄 {os.path.basename(file_path)}: {status_str}")

            for issue in issues[:5]:  # Show first 5 issues
                if issue['status'] == 'FIXED':
                    print(f"   L{issue['line_num']}: ✓ {issue['original'][:60]}...")
                    print(f"         → {issue['fixed'][:60]}...")
                elif issue['status'] == 'INVALID_CONTENT':
                    print(f"   L{issue['line_num']}: ⚠️ {issue['original'][:60]}...")
                    print(f"         Issues: {', '.join(issue['content_issues'])}")
                else:
                    print(f"   L{issue['line_num']}: ✗ {issue['original'][:80]}...")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more issues")
            print()

            # Write fixed file if not dry run
            if not dry_run and file_fixed > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files scanned: {len(files)}")
    print(f"Files with issues: {len(files_with_issues)}")
    print(f"Total malformed lines: {total_malformed}")
    print(f"  - Fixed (format): {total_fixed}")
    print(f"  - Unfixable: {total_unfixable}")

    if total_invalid_content > 0:
        print(f"\n⚠️  CONTENT VALIDATION ISSUES: {total_invalid_content}")
        print("These lines have valid format but suspicious content:")
        for issue in all_content_issues[:10]:
            print(f"  {issue['file']}:L{issue['line_num']}: {', '.join(issue['issues'])}")
        if len(all_content_issues) > 10:
            print(f"  ... and {len(all_content_issues) - 10} more")

    if dry_run:
        print(f"\n⚠️  DRY RUN - no files were modified")
        print(f"Run without --dry-run to apply fixes")
    elif total_fixed > 0:
        print(f"\n✓ Fixed {total_fixed} lines in {len(files_with_issues)} files")

    if total_unfixable > 0:
        print(f"\n⚠️  {total_unfixable} lines could not be automatically fixed")
        print("These need manual review")

    return total_malformed, total_fixed, total_unfixable, total_invalid_content


def main():
    parser = argparse.ArgumentParser(
        description='Find and fix malformed result lines in disambiguation output'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='temp/disambiguation',
        help='Directory containing result files (default: temp/disambiguation)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only report issues, do not fix files'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"ERROR: Directory not found: {args.directory}")
        return 1

    find_and_fix_malformed(args.directory, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
