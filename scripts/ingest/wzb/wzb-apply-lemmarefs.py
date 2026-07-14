#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply Phase 1b lemma resolutions from the disambiguation TSV back to the
annotated WZB TEI file.

Phase 1 (wzb-auto-match.py) wrote @lemmaRef for unambiguous single-candidate
matches. Phase 1b (wzb-bulk-resolve.py) resolved the ambiguous and unmatched
rows. This script applies those Phase 1b decisions to the TEI file.

Usage:
    py scripts/wzb-apply-lemmarefs.py [--dry-run] [--overwrite]

    --dry-run   Report changes without writing the output file
    --overwrite Also update <w> elements that already have @lemmaRef
                (use this to correct Phase 1 errors; by default Phase 1
                matches are preserved)

Input:
    ingest/wzb/WZB.lemma-autofill.tei.xml   (Phase 1 output)
    ingest/wzb/wzb-disambiguation.tsv        (Phase 1b resolutions)

Output:
    ingest/wzb/WZB.lemma-autofill.tei.xml   (updated in-place)
"""

import csv
import sys
import argparse
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    print("ERROR: Please install lxml: pip install lxml")
    sys.exit(1)

def uprint(*args, **kwargs):
    text = " ".join(str(a) for a in args) + kwargs.get("end", "\n")
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_TEI  = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
DEFAULT_TSV  = PROJECT_ROOT / "Wenzelsbibel" / "phase1b" / "wzb-disambiguation.tsv"

XML_ID_ATTR  = "{http://www.w3.org/XML/1998/namespace}id"


def load_resolutions(tsv_path):
    """Return {xml_id: lemma_id} for every resolved row."""
    resolved = {}
    skipped = 0
    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            lemma = row.get("resolved_lemma", "").strip()
            if not lemma:
                skipped += 1
                continue
            resolved[row["xml_id"]] = lemma
    uprint(f"Loaded {len(resolved)} resolved rows from TSV ({skipped} still pending)")
    return resolved


def build_id_index(w_elements):
    """Return {xml_id_string: element} for fast lookup.

    Note: w elements whose xml:id the parser dropped (invalid NCName with
    recover=True) are skipped — their rows resolve as not_found.
    """
    index = {}
    for w in w_elements:
        xml_id = w.get(XML_ID_ATTR, "")
        if xml_id:
            index[xml_id] = w
    return index


def apply_lemmarefs(tei_path, tsv_path, dry_run=False, overwrite=False):
    resolutions = load_resolutions(tsv_path)

    tree = etree.parse(str(tei_path))
    ns_tei = "http://www.tei-c.org/ns/1.0"

    root = tree.getroot()
    # Handle both namespaced and bare <w>
    w_elements = root.findall(f".//{{{ns_tei}}}w")
    if not w_elements:
        w_elements = root.findall(".//w")

    id_index = build_id_index(w_elements)
    uprint(f"Indexed {len(id_index)} <w> elements from TEI file")

    stats = {
        "applied":       0,
        "skipped_phase1": 0,
        "not_found":     0,
        "new_lemma":     0,
    }
    not_found_ids = []

    for xml_id, lemma_id in resolutions.items():
        w = id_index.get(xml_id)
        if w is None:
            stats["not_found"] += 1
            not_found_ids.append(xml_id)
            continue

        existing = w.get("lemmaRef", "")
        new_ref = f"lexicon.xml#{lemma_id}"

        if existing and not overwrite:
            stats["skipped_phase1"] += 1
            continue

        if not dry_run:
            w.set("lemmaRef", new_ref)
        stats["applied"] += 1

        if not existing:
            stats["new_lemma"] += 1

    # Summary
    uprint(f"\nResults:")
    uprint(f"  Applied:             {stats['applied']} (new: {stats['new_lemma']}, overwrote: {stats['applied'] - stats['new_lemma']})")
    uprint(f"  Skipped (Phase 1):   {stats['skipped_phase1']}")
    uprint(f"  xml_id not found:    {stats['not_found']}")

    if not_found_ids:
        uprint(f"\n  First 20 missing ids:")
        for nf in not_found_ids[:20]:
            uprint(f"    {nf}")
        if len(not_found_ids) > 20:
            uprint(f"    ... ({len(not_found_ids) - 20} more)")

    if dry_run:
        uprint(f"\nDRY RUN: no changes written.")
        return

    # Count final coverage
    total_w = len(w_elements)
    has_lemma = sum(1 for w in w_elements if w.get("lemmaRef"))
    uprint(f"\nFinal coverage: {has_lemma}/{total_w} <w> elements have @lemmaRef ({100*has_lemma/total_w:.1f}%)")

    # Write back to same path
    tree.write(str(tei_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    uprint(f"Written to {tei_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply Phase 1b lemma resolutions to WZB TEI file")
    parser.add_argument("--tei", default=str(DEFAULT_TEI), help="Path to annotated TEI file")
    parser.add_argument("--tsv", default=str(DEFAULT_TSV), help="Path to disambiguation TSV")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    parser.add_argument("--overwrite", action="store_true",
                        help="Also update <w> elements that already have @lemmaRef")
    args = parser.parse_args()

    apply_lemmarefs(
        Path(args.tei),
        Path(args.tsv),
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )
