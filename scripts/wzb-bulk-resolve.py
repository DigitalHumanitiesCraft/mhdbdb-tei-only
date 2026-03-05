#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply bulk lemma resolutions to the disambiguation TSV.

Reads a resolutions file (TSV: form, resolved_lemma, confidence, note)
and updates matching rows in the main disambiguation TSV where
resolved_lemma is not yet set.

Usage:
    py scripts/wzb-bulk-resolve.py --resolutions <file> [--tsv <file>] [--dry-run]

Resolutions file format (TSV, with header):
    form  resolved_lemma  confidence  note
    der   lemma_1119      high        definite article

Skips rows that already have a resolved_lemma (never overwrites).
"""

import csv
import sys
import argparse
from pathlib import Path

DEFAULT_TSV = "Wenzelsbibel/wzb-disambiguation.tsv"
REVIEWER = "claude"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk-apply lemma resolutions to disambiguation TSV")
    parser.add_argument("--resolutions", "-r", required=True, help="TSV file with resolutions")
    parser.add_argument("--tsv", "-t", default=DEFAULT_TSV, help="Disambiguation TSV to update")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    res_path = Path(args.resolutions)
    tsv_path = Path(args.tsv)

    if not res_path.exists():
        print(f"ERROR: resolutions file not found: {res_path}")
        sys.exit(1)
    if not tsv_path.exists():
        print(f"ERROR: TSV file not found: {tsv_path}")
        sys.exit(1)

    # Load resolutions: {form: (resolved_lemma, confidence, note)}
    resolutions = {}
    with res_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            resolutions[row["form"]] = (row["resolved_lemma"], row["confidence"], row.get("note", ""))
    print(f"Loaded {len(resolutions)} resolutions: {', '.join(resolutions.keys())}")

    # Read and update TSV
    rows = []
    stats = {form: {"updated": 0, "skipped_already_resolved": 0} for form in resolutions}

    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            form = row["form"]
            if form in resolutions:
                resolved_lemma, confidence, _ = resolutions[form]
                if row.get("resolved_lemma", "").strip():
                    stats[form]["skipped_already_resolved"] += 1
                else:
                    if not args.dry_run:
                        row["resolved_lemma"] = resolved_lemma
                        row["confidence"] = confidence
                        row["reviewer"] = REVIEWER
                    stats[form]["updated"] += 1
            rows.append(row)

    # Report
    total_updated = 0
    for form, s in stats.items():
        lemma, conf, note = resolutions[form]
        print(f"  {form!r:12s} -> {lemma} ({conf}): {s['updated']} updated, {s['skipped_already_resolved']} already resolved")
        total_updated += s["updated"]

    if args.dry_run:
        print(f"\nDRY RUN: would update {total_updated} rows (no changes written)")
        sys.exit(0)

    # Write back
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {total_updated} rows in {tsv_path}")
