#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find missing decisions in PoS validation results.

This script compares source chunk files (containing ⚠️ and ❓ items)
with the generated result files to identify items that were skipped by the Agent.

It outputs a JSON report mapping chunk files to missing xml_ids.

Usage:
    python scripts/data-wrangling/pos/find-missing-decisions.py temp/disambiguation [SIGLE]
"""

import argparse
import re
import sys
import json
from pathlib import Path
import glob

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def get_required_decisions(chunk_file):
    """Extract xml_ids that require validation from source chunk file."""
    required_ids = set()
    
    # Regex to find lines like: "1. ⚠️ word (POS POS) - XML_ID" or "2. ❓ word () - XML_ID"
    # We look for the indicators ⚠️ or ❓
    pattern = r"^\d+\.\s*[⚠️❓].*?-\s*([a-zA-Z0-9_\-\.]+)$"
    
    try:
        with open(chunk_file, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(pattern, line.strip())
                if match:
                    required_ids.add(match.group(1))
    except Exception as e:
        print(f"Error reading {chunk_file}: {e}", file=sys.stderr)
        
    return required_ids

def get_provided_decisions(result_files):
    """Extract xml_ids that have decisions in result/fix files."""
    provided_ids = set()
    
    # Regex for result line: xml_id | old -> new | ...
    pattern = r"^([a-zA-Z0-9_\-\.]+)\s*|.*"
    
    for file_path in result_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(pattern, line.strip())
                    if match:
                        provided_ids.add(match.group(1))
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            
    return provided_ids

def main():
    parser = argparse.ArgumentParser(description="Find skipped PoS validation items")
    parser.add_argument("results_dir", help="Directory containing chunk and result files")
    parser.add_argument("sigle", nargs="?", help="Optional SIGLE to filter files (e.g. ADP)")
    parser.add_argument("--json", action="store_true", help="Output valid JSON only")
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        if args.json: print("[]"); return 1
        print(f"Error: Directory {results_dir} not found")
        return 1
        
    # Find source chunk files (excluding result files)
    pattern = "*-chunk-*.md"
    if args.sigle:
        pattern = f"{args.sigle}*{pattern}"
        
    all_files = list(results_dir.glob(pattern))
    source_files = [f for f in all_files if "-result" not in f.name]
    
    if not source_files:
        if args.json: print("[]"); return 0
        print(f"No source chunk files found matching '{pattern}'")
        return 0
        
    report = []
    
    if not args.json:
        print(f"Analyzing {len(source_files)} chunk files...")
    
    for source_file in source_files:
        # Construct expected result filenames
        base_name = source_file.name.replace(".md", "")
        result_file = results_dir / f"{base_name}-result.md"
        fix_files = list(results_dir.glob(f"{base_name}-result_FIX*.md"))
        
        all_result_files = []
        if result_file.exists():
            all_result_files.append(result_file)
        all_result_files.extend(fix_files)
        
        # Get sets of IDs
        required = get_required_decisions(source_file)
        provided = get_provided_decisions(all_result_files)
        
        if "016" in source_file.name:
            print(f"DEBUG: {source_file.name} - Required: {len(required)}, Provided: {len(provided)}", file=sys.stderr)
            # Check specifically for the missing ID
            if "ADP_806900_1" in required:
                print("DEBUG: ADP_806900_1 is in REQUIRED", file=sys.stderr)
            else:
                print("DEBUG: ADP_806900_1 is NOT in REQUIRED", file=sys.stderr)

        missing = required - provided
        
        if missing:
            report.append({
                "chunk_file": source_file.name,
                "chunk_path": str(source_file),
                "missing_count": len(missing),
                "missing_ids": sorted(list(missing))
            })
            
    # Sort by missing count (descending)
    report.sort(key=lambda x: x["missing_count"], reverse=True)
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "=" * 80)
        print(f"MISSING DECISIONS REPORT ({args.sigle or 'ALL'})")
        print("=" * 80)
        print(f"{ 'Chunk File':<40} | { 'Missing Count':<15}")
        print("-" * 80)
        
        total_missing = 0
        for item in report[:20]: # Show top 20
            print(f"{item['chunk_file']:<40} | {item['missing_count']:<15}")
            total_missing += item["missing_count"]
            
        if len(report) > 20:
            print(f"... and {len(report) - 20} more files")
            
        total_missing = sum(item["missing_count"] for item in report)
        print("-" * 80)
        print(f"TOTAL MISSING DECISIONS: {total_missing}")
        print("=" * 80)

if __name__ == "__main__":
    main()
