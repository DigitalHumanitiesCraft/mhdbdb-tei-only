#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute majority-sense baseline from the annotated MHDBDB corpus.

For every lemma that appears in wzb-sense-pending.tsv, this script:
  1. Scans all tei/*.xml files for <w @lemmaRef @meaningRef> pairs
  2. Counts sense frequency per lemma in the corpus
  3. Determines the majority sense (most frequent in corpus)
  4. Computes the theoretical accuracy if we applied majority-sense to all
     unresolved pending tokens

Output:
  Wenzelsbibel/phase3/wzb-sense-majority-baseline.tsv
    lemma_id | majority_sense_id | majority_count | total_count | majority_pct

Usage:
    py scripts/wzb-sense-baseline.py [--dry-run]
"""

import csv
import sys
import argparse
from pathlib import Path
from collections import Counter, defaultdict

try:
    from lxml import etree
except ImportError:
    print("ERROR: pip install lxml")
    sys.exit(1)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_TEI_DIR = PROJECT_ROOT / "tei"
DEFAULT_PENDING = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"
DEFAULT_OUT     = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-majority-baseline.tsv"

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"


def scan_corpus(tei_dir: Path) -> dict[str, Counter]:
    """Return {lemma_id: Counter(sense_id)} from all annotated corpus files."""
    lemma_sense_counts: dict[str, Counter] = defaultdict(Counter)
    files = sorted(tei_dir.glob("*.xml"))
    print(f"Scanning {len(files)} corpus files in {tei_dir} ...")

    for i, fpath in enumerate(files):
        if i % 100 == 0:
            print(f"  {i}/{len(files)} files ...", end="\r")
        try:
            tree = etree.parse(str(fpath))
        except Exception:
            continue
        for w in tree.findall(f".//{{{NS_TEI}}}w"):
            lemma_ref   = w.get("lemmaRef", "")
            meaning_ref = w.get("meaningRef", "")
            if not lemma_ref or not meaning_ref:
                continue
            lemma_id = lemma_ref.split("#")[-1]  if "#" in lemma_ref   else lemma_ref
            sense_id = meaning_ref.split("#")[-1] if "#" in meaning_ref else meaning_ref
            lemma_sense_counts[lemma_id][sense_id] += 1

    print(f"  {len(files)}/{len(files)} files done.    ")
    return lemma_sense_counts


def load_pending_lemmata(pending_path: Path) -> dict[str, list[str]]:
    """Return {lemma_id: [xml_ids]} for unresolved pending rows."""
    lemmata: dict[str, list[str]] = defaultdict(list)
    with pending_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("resolved_sense", "").strip():
                continue  # already resolved
            lemma_ref = row.get("lemmaRef", "")
            lemma_id  = lemma_ref.split("#")[-1] if "#" in lemma_ref else lemma_ref
            lemmata[lemma_id].append(row["xml_id"])
    return lemmata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute majority-sense baseline from annotated MHDBDB corpus"
    )
    parser.add_argument("--tei-dir",  default=str(DEFAULT_TEI_DIR))
    parser.add_argument("--pending",  default=str(DEFAULT_PENDING))
    parser.add_argument("--output",   default=str(DEFAULT_OUT))
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    corpus_counts = scan_corpus(Path(args.tei_dir))
    print(f"Corpus: {len(corpus_counts)} unique lemmata with sense annotations")

    pending_lemmata = load_pending_lemmata(Path(args.pending))
    print(f"Pending: {len(pending_lemmata)} unique lemmata, "
          f"{sum(len(v) for v in pending_lemmata.values())} tokens")

    # Build baseline output rows
    out_rows = []
    baseline_correct = 0
    baseline_total   = 0
    no_corpus_data   = 0

    for lemma_id, xml_ids in sorted(pending_lemmata.items(),
                                    key=lambda x: -len(x[1])):
        counts = corpus_counts.get(lemma_id)
        n_pending = len(xml_ids)
        if not counts:
            no_corpus_data += 1
            out_rows.append({
                "lemma_id":         lemma_id,
                "majority_sense_id": "",
                "majority_count":    0,
                "total_count":       0,
                "majority_pct":      "",
                "pending_tokens":    n_pending,
                "note":             "no corpus data",
            })
            continue

        majority_sense, majority_count = counts.most_common(1)[0]
        total = sum(counts.values())
        pct   = majority_count / total * 100

        out_rows.append({
            "lemma_id":          lemma_id,
            "majority_sense_id": majority_sense,
            "majority_count":    majority_count,
            "total_count":       total,
            "majority_pct":      f"{pct:.1f}",
            "pending_tokens":    n_pending,
            "note":              f"{len(counts)} senses in corpus",
        })

        # Theoretical baseline accuracy: assume majority sense correct for all pending
        baseline_total   += n_pending
        baseline_correct += n_pending  # optimistic upper bound if majority sense applies

    # Realistic baseline: weighted by corpus majority_pct
    weighted_correct = sum(
        r["pending_tokens"] * float(r["majority_pct"]) / 100
        for r in out_rows if r["majority_pct"]
    )
    weighted_total = sum(r["pending_tokens"] for r in out_rows if r["majority_pct"])

    print(f"\n=== Majority-Sense Baseline Estimate ===")
    print(f"Pending tokens with corpus data: {weighted_total}")
    print(f"Pending tokens without corpus data: "
          f"{sum(r['pending_tokens'] for r in out_rows if not r['majority_pct'])}")
    print(f"Lemmata with no corpus annotations: {no_corpus_data}")
    print(f"\nWeighted majority-sense accuracy (upper bound): "
          f"{weighted_correct:.0f}/{weighted_total} = "
          f"{100*weighted_correct/weighted_total:.1f}% (if corpus distribution holds in WZB)")
    print("Note: this is an overestimate — corpus genre mix != WZB biblical prose")

    if args.dry_run:
        print("\nDRY RUN: no output written.")
        sys.exit(0)

    fieldnames = ["lemma_id", "majority_sense_id", "majority_count",
                  "total_count", "majority_pct", "pending_tokens", "note"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"\nBaseline TSV written to {args.output} ({len(out_rows)} rows)")
