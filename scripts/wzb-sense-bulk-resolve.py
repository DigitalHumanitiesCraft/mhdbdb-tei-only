#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Step 2a: Apply bulk sense resolutions to wzb-sense-pending.tsv.

Two resolution modes (select with --by):
  lemma  (default) — match all unresolved rows sharing the same @lemmaRef;
                     one resolution line per lemma covers all its tokens
  xml_id           — match individual rows by xml_id (patch mode for
                     minority exceptions)

Resolution file format (TSV, with header):
  lemma mode:   lemmaRef  resolved_sense  confidence  note
  xml_id mode:  xml_id    resolved_sense  confidence  note

Only rows with an empty resolved_sense are updated (never overwrites).

Usage:
    py scripts/wzb-sense-bulk-resolve.py --resolutions <file> [--by lemma|xml_id] [--dry-run]
    py scripts/wzb-sense-bulk-resolve.py -r Wenzelsbibel/phase3/resolutions/wzb-sense-batch01.tsv
"""

import csv
import sys
import argparse
from pathlib import Path

def uprint(*args, **kwargs):
    text = " ".join(str(a) for a in args) + kwargs.get("end", "\n")
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_PENDING = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"
REVIEWER = "claude"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 3: bulk-apply sense resolutions to wzb-sense-pending.tsv"
    )
    parser.add_argument("--resolutions", "-r", required=True, help="TSV file with resolutions")
    parser.add_argument("--pending", "-t", default=str(DEFAULT_PENDING), help="Pending TSV to update")
    parser.add_argument("--by", choices=["lemma", "xml_id"], default="lemma",
                        help="Match key: 'lemma' (bulk) or 'xml_id' (per-instance patch)")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    res_path     = Path(args.resolutions)
    pending_path = Path(args.pending)
    key_col      = "lemmaRef" if args.by == "lemma" else "xml_id"

    if not res_path.exists():
        uprint(f"ERROR: resolutions file not found: {res_path}")
        sys.exit(1)
    if not pending_path.exists():
        uprint(f"ERROR: pending TSV not found: {pending_path}")
        sys.exit(1)

    # Load resolutions
    resolutions = {}
    with res_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            key = row.get(key_col, "").strip()
            sense = row.get("resolved_sense", "").strip()
            if key and sense:
                resolutions[key] = (sense, row.get("confidence", "high"), row.get("note", ""))
    uprint(f"Loaded {len(resolutions)} resolutions (key={key_col})")

    # Read pending TSV
    rows = []
    fieldnames = None
    with pending_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Apply
    stats = {k: {"updated": 0, "skipped": 0} for k in resolutions}
    unmatched_keys = set(resolutions.keys())

    for row in rows:
        key = row.get(key_col, "").strip()
        if key not in resolutions:
            continue
        unmatched_keys.discard(key)
        resolved_sense, confidence, _ = resolutions[key]
        if row.get("resolved_sense", "").strip():
            stats[key]["skipped"] += 1
        else:
            if not args.dry_run:
                row["resolved_sense"] = resolved_sense
                row["confidence"]     = confidence
                row["reviewer"]       = REVIEWER
            stats[key]["updated"] += 1

    # Report
    total_updated = 0
    for key, s in stats.items():
        sense, conf, note = resolutions[key]
        uprint(f"  {key:<35} -> {sense} ({conf}): {s['updated']} updated, {s['skipped']} already resolved")
        total_updated += s["updated"]

    if unmatched_keys:
        uprint(f"\nWARNING: {len(unmatched_keys)} resolution key(s) not found in pending TSV:")
        for k in sorted(unmatched_keys)[:10]:
            uprint(f"  {k}")

    if args.dry_run:
        uprint(f"\nDRY RUN: would update {total_updated} rows (no changes written)")
        sys.exit(0)

    # Write back
    with pending_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    uprint(f"\nUpdated {total_updated} rows in {pending_path}")

    # Coverage summary
    resolved_total = sum(1 for r in rows if r.get("resolved_sense", "").strip())
    uprint(f"Resolved so far: {resolved_total}/{len(rows)} ({100*resolved_total/len(rows):.1f}%)")
