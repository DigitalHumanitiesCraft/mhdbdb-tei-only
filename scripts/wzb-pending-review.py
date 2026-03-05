#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a per-form pending-review TSV from the disambiguation TSV.

One row per unique (form, candidate_lemmas) combination, with:
- count of occurrences
- one sample context
- empty resolved_lemma / confidence / note columns for filling in

Output: Wenzelsbibel/wzb-pending-review.tsv

Usage:
    py scripts/wzb-pending-review.py [--tsv <path>] [--out <path>]
"""

import csv
import argparse
from pathlib import Path
from collections import defaultdict

DEFAULT_TSV = "Wenzelsbibel/wzb-disambiguation.tsv"
DEFAULT_OUT = "Wenzelsbibel/wzb-pending-review.tsv"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv", default=DEFAULT_TSV)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--match-type", default="ambiguous",
                        choices=["ambiguous", "unmatched", "all"],
                        help="Which rows to include (default: ambiguous)")
    args = parser.parse_args()

    tsv_path = Path(args.tsv)
    out_path = Path(args.out)

    # Collect: key=(form, candidate_lemmas) -> {count, sample_context}
    data = defaultdict(lambda: {"count": 0, "sample_context": ""})

    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # Skip already resolved
            if row.get("resolved_lemma", "").strip():
                continue
            mt = row.get("match_type", "")
            if args.match_type != "all" and mt != args.match_type:
                continue
            key = (row["form"], row.get("candidate_lemmas", ""), mt)
            entry = data[key]
            entry["count"] += 1
            if not entry["sample_context"]:
                entry["sample_context"] = row.get("context", "")

    # Sort by count descending
    sorted_data = sorted(data.items(), key=lambda x: -x[1]["count"])

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["form", "match_type", "count", "candidate_lemmas", "sample_context",
                         "resolved_lemma", "confidence", "note"])
        for (form, candidates, mt), entry in sorted_data:
            writer.writerow([form, mt, entry["count"], candidates,
                             entry["sample_context"], "", "", ""])

    print(f"Written {len(sorted_data)} unique forms to {out_path}")
