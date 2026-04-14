#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch specific xml_id rows in the disambiguation TSV with correct lemma assignments.
Used for split-form cases where bulk-resolve assigns the dominant reading,
and minority rows need individual correction.

Usage:
    py scripts/wzb-patch-rows.py --patches <file> [--tsv <file>] [--dry-run]

Patches file format (TSV, with header):
    xml_id  resolved_lemma  confidence  note

Always overwrites existing resolved_lemma and reviewer for matching xml_ids.
"""

import csv
import sys
import argparse
from pathlib import Path

def uprint(*args, **kwargs):
    text = " ".join(str(a) for a in args) + kwargs.get("end", "\n")
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))

DEFAULT_TSV = "Wenzelsbibel/phase1b/wzb-disambiguation.tsv"
REVIEWER = "claude"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch individual rows in disambiguation TSV by xml_id")
    parser.add_argument("--patches", "-p", required=True, help="TSV file with per-row patches")
    parser.add_argument("--tsv", "-t", default=DEFAULT_TSV, help="Disambiguation TSV to update")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    patches_path = Path(args.patches)
    tsv_path = Path(args.tsv)

    if not patches_path.exists():
        print(f"ERROR: patches file not found: {patches_path}")
        sys.exit(1)
    if not tsv_path.exists():
        print(f"ERROR: TSV file not found: {tsv_path}")
        sys.exit(1)

    # Load patches: {xml_id: (resolved_lemma, confidence, note)}
    patches = {}
    with patches_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            patches[row["xml_id"]] = (row["resolved_lemma"], row["confidence"], row.get("note", ""))
    uprint(f"Loaded {len(patches)} patches")

    rows = []
    updated = 0
    not_found = list(patches.keys())

    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            xml_id = row["xml_id"]
            if xml_id in patches:
                lemma, conf, note = patches[xml_id]
                old = row.get("resolved_lemma", "")
                if not args.dry_run:
                    row["resolved_lemma"] = lemma
                    row["confidence"] = conf
                    row["reviewer"] = REVIEWER
                uprint(f"  {xml_id}: {old!r} -> {lemma} ({conf})")
                updated += 1
                if xml_id in not_found:
                    not_found.remove(xml_id)
            rows.append(row)

    if not_found:
        uprint(f"\nWARNING: {len(not_found)} xml_ids not found in TSV: {', '.join(not_found)}")

    if args.dry_run:
        uprint(f"\nDRY RUN: would update {updated} rows (no changes written)")
        sys.exit(0)

    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    uprint(f"\nPatched {updated} rows in {tsv_path}")
