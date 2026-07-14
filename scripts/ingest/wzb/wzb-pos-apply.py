#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2b: Apply LLM-resolved @pos values from wzb-pos-pending.tsv back to
the WZB TEI file.

Run wzb-pos-assign.py first to auto-assign single-POS cases and generate
the pending TSV.  After filling in the `resolved_pos` column (LLM or human),
run this script to write the @pos attributes.

Usage:
    py scripts/wzb-pos-apply.py [--dry-run]
    py scripts/wzb-pos-apply.py --pending ingest/wzb/wzb-pos-pending.tsv

Input:
    ingest/wzb/WZB.lemma-autofill.tei.xml
    ingest/wzb/wzb-pos-pending.tsv  (with resolved_pos filled in)

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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_TEI     = PROJECT_ROOT / "ingest" / "wzb" / "WZB.lemma-autofill.tei.xml"
DEFAULT_PENDING = PROJECT_ROOT / "ingest" / "wzb" / "phase2" / "wzb-pos-pending.tsv"

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"

VALID_POS = {
    "PRO", "VRB", "NOM", "ADJ", "ADV", "CNJ", "PRP", "VEX", "POS", "NAM", "NUM",
    "NEG", "GRA", "INJ", "VEM", "IPA", "DET", "DIG",
    # Conjunction subtypes (SKILL.md tagset):
    "SCNJ", "CCNJ",
    # ART removed: articles are DET per SKILL.md tagset
}


def load_resolutions(tsv_path):
    """Return {xml_id: pos_value} for rows with resolved_pos filled in."""
    resolved = {}
    skipped = 0
    invalid = 0
    with tsv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            pos = row.get("resolved_pos", "").strip()
            if not pos:
                skipped += 1
                continue
            # Accept space-separated multi-tags (e.g. "NOM VRB")
            tags = pos.split()
            bad = [t for t in tags if t not in VALID_POS]
            if bad:
                print(f"  WARNING: invalid POS tag(s) {bad} for {row['xml_id']} — skipping row")
                invalid += 1
                continue
            resolved[row["xml_id"]] = pos
    print(f"Loaded {len(resolved)} resolved POS rows ({skipped} still pending, {invalid} invalid tags skipped)")
    return resolved


def apply_pos(tei_path, pending_path, dry_run=False):
    resolutions = load_resolutions(pending_path)
    if not resolutions:
        print("Nothing to apply.")
        return

    print(f"Parsing TEI from {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()

    w_elements = root.findall(f".//{{{NS_TEI}}}w")
    if not w_elements:
        w_elements = root.findall(".//w")
    print(f"  {len(w_elements)} <w> elements found")

    id_index = {w.get(XML_ID, ""): w for w in w_elements if w.get(XML_ID)}

    stats = {"applied": 0, "overwrite": 0, "not_found": 0}
    not_found = []

    for xml_id, pos in resolutions.items():
        w = id_index.get(xml_id)
        if w is None:
            stats["not_found"] += 1
            not_found.append(xml_id)
            continue
        if w.get("pos"):
            stats["overwrite"] += 1
        if not dry_run:
            w.set("pos", pos)
        stats["applied"] += 1

    # Coverage report
    total = len(w_elements)
    has_pos = sum(1 for w in w_elements if w.get("pos"))
    # Overwrites stecken schon in has_pos — sie nochmal zu addieren wies im
    # Dry-Run Coverage >100 % aus (real gesehen: "141.2%", #171 F69).
    will_have = has_pos + (stats["applied"] - stats["overwrite"] if dry_run else 0)

    print(f"\nApplied:       {stats['applied']} (overwrote existing: {stats['overwrite']})")
    print(f"xml_id not found: {stats['not_found']}")
    if not_found:
        for nf in not_found[:10]:
            print(f"  {nf}")
        if len(not_found) > 10:
            print(f"  ... ({len(not_found) - 10} more)")

    if dry_run:
        print(f"\nDRY RUN: would bring @pos coverage to ~{will_have}/{total} ({100*will_have/total:.1f}%)")
        print("No changes written.")
        return

    final_pos = sum(1 for w in w_elements if w.get("pos"))
    print(f"\nFinal @pos coverage: {final_pos}/{total} ({100*final_pos/total:.1f}%)")

    tree.write(str(tei_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"TEI written to {tei_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 2b: apply resolved @pos values to WZB TEI")
    parser.add_argument("--tei",     default=str(DEFAULT_TEI),     help="Path to annotated TEI file")
    parser.add_argument("--pending", default=str(DEFAULT_PENDING), help="Path to pending TSV")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report changes without writing the TEI")
    args = parser.parse_args()

    apply_pos(
        tei_path=Path(args.tei),
        pending_path=Path(args.pending),
        dry_run=args.dry_run,
    )
