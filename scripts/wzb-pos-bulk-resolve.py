#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply bulk POS resolutions to the Phase 2 pending TSV (wzb-pos-pending.tsv).

Mirrors wzb-bulk-resolve.py but targets resolved_pos instead of resolved_lemma,
and supports matching on lemma_id as well as form.

Resolution file format (TSV with header):
    lemma_id    form    resolved_pos    confidence    note
    lemma_5432  *       VEX             high          sin = copula/aux
    lemma_7489  wirt    VEX             high          werden future/passive
    lemma_1517  er      PRO             high          personal pronoun

  - lemma_id: required; restricts which rows are affected
  - form:     use * to match any form under that lemma_id
  - resolved_pos: MHDBDB POS tag (or space-separated multi-tag)

Rows that already have resolved_pos set are skipped (never overwritten).

Usage:
    py scripts/wzb-pos-bulk-resolve.py --resolutions <file> [--dry-run]
    py scripts/wzb-pos-bulk-resolve.py --resolutions <file> --tsv Wenzelsbibel/wzb-pos-pending.tsv
"""

import csv
import sys
import argparse
from pathlib import Path
from collections import defaultdict

def uprint(*args, **kwargs):
    text = " ".join(str(a) for a in args) + kwargs.get("end", "\n")
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))

DEFAULT_TSV = "Wenzelsbibel/wzb-pos-pending.tsv"
REVIEWER    = "claude"

VALID_POS = {
    "PRO", "VRB", "NOM", "ADJ", "ADV", "ART", "CNJ", "PRP", "VEX", "POS", "NAM", "NUM",
    "NEG", "GRA", "INJ", "VEM", "IPA", "DET", "DIG",
}


def load_resolutions(res_path):
    """Return list of (lemma_id, form_or_star, resolved_pos, confidence, note)."""
    resolutions = []
    with res_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            pos = row["resolved_pos"].strip()
            tags = pos.split()
            bad = [t for t in tags if t not in VALID_POS]
            if bad:
                uprint(f"  WARNING: invalid POS tag(s) {bad} in resolution for {row['lemma_id']}/{row['form']} — skipping")
                continue
            resolutions.append((
                row["lemma_id"].strip(),
                row["form"].strip(),
                pos,
                row.get("confidence", "high").strip(),
                row.get("note", "").strip(),
            ))
    return resolutions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk-apply POS resolutions to wzb-pos-pending.tsv")
    parser.add_argument("--resolutions", "-r", required=True, help="TSV file with resolutions")
    parser.add_argument("--tsv", "-t", default=DEFAULT_TSV, help="Pending POS TSV to update")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    res_path = Path(args.resolutions)
    tsv_path = Path(args.tsv)

    if not res_path.exists():
        uprint(f"ERROR: resolutions file not found: {res_path}")
        sys.exit(1)
    if not tsv_path.exists():
        uprint(f"ERROR: TSV file not found: {tsv_path}")
        sys.exit(1)

    resolutions = load_resolutions(res_path)
    uprint(f"Loaded {len(resolutions)} resolution rules")
    for lid, form, pos, conf, note in resolutions:
        uprint(f"  {lid} / {'*' if form == '*' else repr(form):12s} -> {pos} ({conf}){' — ' + note if note else ''}")

    # Build lookup: (lemma_id, form_lower) -> (pos, conf) and (lemma_id, '*') -> ...
    exact_lookup   = {}  # (lemma_id, form_lower) -> (pos, conf)
    wildcard_lookup = {}  # lemma_id -> (pos, conf)
    for lid, form, pos, conf, _ in resolutions:
        if form == "*":
            wildcard_lookup[lid] = (pos, conf)
        else:
            exact_lookup[(lid, form.lower())] = (pos, conf)

    # Read and update TSV
    rows = []
    stats = defaultdict(lambda: {"updated": 0, "skipped": 0})

    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            lid   = row.get("lemma_id", "").strip()
            form  = row.get("form", "").strip()

            # Already resolved?
            if row.get("resolved_pos", "").strip():
                rows.append(row)
                continue

            key = (lid, form.lower())
            if key in exact_lookup:
                pos, conf = exact_lookup[key]
                rule_key = f"{lid}/{form}"
            elif lid in wildcard_lookup:
                pos, conf = wildcard_lookup[lid]
                rule_key = f"{lid}/*"
            else:
                rows.append(row)
                continue

            stats[rule_key]["updated"] += 1
            if not args.dry_run:
                row["resolved_pos"] = pos
                row["confidence"]   = conf
                row["reviewer"]     = REVIEWER
            rows.append(row)

    # Report
    total_updated = sum(s["updated"] for s in stats.values())
    uprint(f"\nResults:")
    for rule_key, s in sorted(stats.items()):
        uprint(f"  {rule_key:35s}: {s['updated']} updated")
    uprint(f"\nTotal: {total_updated} rows would be {'updated' if args.dry_run else 'updated'}")

    if args.dry_run:
        uprint("DRY RUN: no changes written.")
        sys.exit(0)

    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    uprint(f"Written to {tsv_path}")
