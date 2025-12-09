#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare a fix task for a specific chunk by identifying missing decisions
and extracting their context from the source chunk.

Usage:
    python scripts/data-wrangling/pos/prepare-fix-task.py temp/disambiguation/ADP.tei-chunk-026.md
"""

import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def get_required_decisions(chunk_file):
    required_ids = set()
    # Store line info to extract context later
    # map id -> line_content
    id_map = {}
    
    pattern = r"^\d+\.\s*([⚠️❓].*?)-\s*([a-zA-Z0-9_\-\.]+)$"
    
    try:
        with open(chunk_file, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(pattern, line.strip())
                if match:
                    xml_id = match.group(2)
                    content = match.group(1)
                    required_ids.add(xml_id)
                    id_map[xml_id] = line.strip()
    except Exception as e:
        print(f"Error reading {chunk_file}: {e}", file=sys.stderr)
        
    return required_ids, id_map

def get_provided_decisions(result_files):
    provided_ids = set()
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
    parser = argparse.ArgumentParser(description="Prepare fix task")
    parser.add_argument("chunk_file", help="Path to the source chunk file")
    
    args = parser.parse_args()
    
    chunk_path = Path(args.chunk_file)
    results_dir = chunk_path.parent
    base_name = chunk_path.name.replace(".md", "")
    
    # Find result files
    result_files = []
    res_file = results_dir / f"{base_name}-result.md"
    if res_file.exists():
        result_files.append(res_file)
    result_files.extend(list(results_dir.glob(f"{base_name}-result_FIX*.md")))
    
    required, id_map = get_required_decisions(chunk_path)
    provided = get_provided_decisions(result_files)
    
    missing = required - provided
    
    if not missing:
        print(f"No missing decisions for {chunk_path.name}!")
        return
    
    # Extract Context Text from chunk file
    context_text = []
    with open(chunk_path, "r", encoding="utf-8") as f:
        in_context = False
        for line in f:
            if "## CONTEXT TEXT" in line:
                in_context = True
                continue
            if "## WORDS TO VALIDATE" in line:
                in_context = False
                break
            if in_context and line.strip():
                context_text.append(line.strip())
    
    print(f"# Fix Task for {chunk_path.name}")
    print(f"Missing {len(missing)} decisions.\n")
    
    print("## CONTEXT TEXT")
    print("\n".join(context_text))
    print("\n## MISSING ITEMS TO VALIDATE")
    
    # Sort missing items by their appearance in the file (using id_map line content to sort? No, IDs roughly sequential)
    # Better: iterate over id_map order if python dict preserves insertion order (it does in 3.7+)
    
    for xml_id, line_content in id_map.items():
        if xml_id in missing:
            print(line_content)

if __name__ == "__main__":
    main()
