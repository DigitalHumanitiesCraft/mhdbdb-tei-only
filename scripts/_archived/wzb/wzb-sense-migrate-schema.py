#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-time migration: add decision_type and model_id columns to wzb-sense-pending.tsv.

Existing resolved rows → decision_type=bulk-llm, model_id=claude-sonnet-4-6
Existing unresolved rows → both columns empty

Run once, then delete this script (or keep for documentation).

Usage:
    py scripts/wzb-sense-migrate-schema.py [--dry-run]
"""

import csv
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_PENDING = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"
BACKFILL_MODEL = "claude-sonnet-4-6"
BACKFILL_TYPE  = "bulk-llm"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pending", default=str(DEFAULT_PENDING))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = Path(args.pending)
    rows = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        old_fields = reader.fieldnames
        for row in reader:
            rows.append(row)

    if "decision_type" in old_fields:
        print("Columns already migrated — nothing to do.")
        sys.exit(0)

    new_fields = old_fields + ["decision_type", "model_id"]
    backfilled = 0
    for row in rows:
        if row.get("resolved_sense", "").strip():
            row["decision_type"] = BACKFILL_TYPE
            row["model_id"]      = BACKFILL_MODEL
            backfilled += 1
        else:
            row["decision_type"] = ""
            row["model_id"]      = ""

    print(f"Rows: {len(rows)}, backfilled {backfilled} resolved rows -> "
          f"decision_type={BACKFILL_TYPE}, model_id={BACKFILL_MODEL}")

    if args.dry_run:
        print("DRY RUN: no changes written.")
        sys.exit(0)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written to {path}")
