#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2: Auto-assign @pos to <w> elements in WZB.lemma-autofill.tei.xml.

For <w> elements whose @lemmaRef points to a single-POS lexicon entry the
@pos attribute is written directly.  Multi-POS lemmas and words without
@lemmaRef are collected in a pending TSV for LLM/human review.

Usage:
    py scripts/wzb-pos-assign.py [--dry-run]

Input:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml
    authority-files/lexicon.xml

Output:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml   (updated in-place, unless --dry-run)
    Wenzelsbibel/wzb-pos-pending.tsv           (rows needing LLM disambiguation)
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

# ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_TEI  = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
DEFAULT_LEX  = PROJECT_ROOT / "authority-files" / "lexicon.xml"
DEFAULT_OUT  = PROJECT_ROOT / "Wenzelsbibel" / "phase2" / "wzb-pos-pending.tsv"

NS_TEI  = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"
XML_ID  = f"{{{NS_XML}}}id"

VALID_POS = {
    "PRO", "VRB", "NOM", "ADJ", "ADV", "CNJ", "PRP", "VEX", "POS", "NAM", "NUM",
    # Additional tags found in lexicon.xml:
    "NEG", "GRA", "INJ", "VEM", "IPA", "DET", "DIG",
    # Conjunction subtypes (SKILL.md tagset):
    "SCNJ", "CCNJ",
    # ART removed: articles are DET per SKILL.md tagset
}
CONTEXT_WINDOW = 5  # words each side


# ---------------------------------------------------------------------------
# Lexicon index
# ---------------------------------------------------------------------------

# Tagset normalisation: old lexicon tags → SKILL.md canonical tags.
# Applied at index-build time so stale lexicon entries never leak into TEI output.
_LEGACY_TAG_MAP = {
    "GRA": "ADV",   # grammatical particle → treated as ADV throughout
    "ART": "DET",   # article → DET (SKILL.md tagset)
    # CNJ stays CNJ in the index; context resolver outputs CCNJ/SCNJ
}


def _normalise_pos(tag: str) -> str:
    return _LEGACY_TAG_MAP.get(tag, tag)


def build_lexicon_index(lex_path):
    """Return {lemma_id: [pos_value, ...]} for every entry in lexicon.xml.

    Legacy tags (GRA, ART) are normalised to the SKILL.md canonical tagset
    at read time so they never appear in TEI @pos output.
    """
    tree = etree.parse(str(lex_path))
    ns = {"tei": NS_TEI}
    index = {}
    for entry in tree.findall(".//tei:entry", ns):
        lemma_id = entry.get(XML_ID, "")
        if not lemma_id:
            continue
        pos_els = entry.findall(".//tei:gramGrp/tei:pos", ns)
        raw = [p.text.strip() for p in pos_els if p.text and p.text.strip()]
        # Normalise and deduplicate while preserving order
        seen, pos_values = set(), []
        for tag in raw:
            normalised = _normalise_pos(tag)
            if normalised not in seen:
                seen.add(normalised)
                pos_values.append(normalised)
        index[lemma_id] = pos_values
    return index


# ---------------------------------------------------------------------------
# Context helper
# ---------------------------------------------------------------------------

def build_context_list(w_elements):
    """Return a flat list of (xml_id, form_text) for context lookup."""
    result = []
    for w in w_elements:
        xml_id = w.get(XML_ID, "")
        text = (w.text or "").strip()
        result.append((xml_id, text))
    return result


def get_context(idx, context_list, window=CONTEXT_WINDOW):
    """Return a string of ±window words around position idx."""
    start = max(0, idx - window)
    end = min(len(context_list), idx + window + 1)
    parts = []
    for i in range(start, end):
        xml_id, text = context_list[i]
        if i == idx:
            parts.append(f"[{text}]")
        else:
            parts.append(text)
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def assign_pos(tei_path, lex_path, pending_path, dry_run=False):
    print(f"Loading lexicon from {lex_path} ...")
    lex = build_lexicon_index(lex_path)
    print(f"  {len(lex)} entries indexed")

    print(f"Parsing TEI from {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()

    w_elements = root.findall(f".//{{{NS_TEI}}}w")
    if not w_elements:
        w_elements = root.findall(".//w")
    print(f"  {len(w_elements)} <w> elements found")

    context_list = build_context_list(w_elements)

    stats = {
        "auto_assigned":  0,
        "already_has_pos": 0,
        "multi_pos":      0,
        "no_lemma":       0,
        "lemma_missing":  0,  # lemmaRef present but ID not in lexicon
    }
    pending_rows = []

    for idx, w in enumerate(w_elements):
        xml_id = w.get(XML_ID, "")
        form   = (w.text or "").strip()

        # Skip if already annotated
        if w.get("pos"):
            stats["already_has_pos"] += 1
            continue

        lemma_ref = w.get("lemmaRef", "")

        # --- No lemmaRef: flag for LLM ---
        if not lemma_ref:
            stats["no_lemma"] += 1
            pending_rows.append({
                "xml_id":        xml_id,
                "form":          form,
                "context":       get_context(idx, context_list),
                "lemma_id":      "",
                "candidate_pos": "",
                "resolved_pos":  "",
                "confidence":    "",
                "reviewer":      "",
            })
            continue

        # Extract "lemma_NNNN" from "lexicon.xml#lemma_NNNN"
        lemma_id = lemma_ref.split("#", 1)[-1] if "#" in lemma_ref else lemma_ref

        pos_list = lex.get(lemma_id)
        if pos_list is None:
            stats["lemma_missing"] += 1
            pending_rows.append({
                "xml_id":        xml_id,
                "form":          form,
                "context":       get_context(idx, context_list),
                "lemma_id":      lemma_id,
                "candidate_pos": "",
                "resolved_pos":  "",
                "confidence":    "",
                "reviewer":      "",
            })
            continue

        # --- Single POS: auto-assign ---
        if len(pos_list) == 1:
            if not dry_run:
                w.set("pos", pos_list[0])
            stats["auto_assigned"] += 1
            continue

        # --- Multi POS: flag for LLM ---
        stats["multi_pos"] += 1
        pending_rows.append({
            "xml_id":        xml_id,
            "form":          form,
            "context":       get_context(idx, context_list),
            "lemma_id":      lemma_id,
            "candidate_pos": "|".join(pos_list),
            "resolved_pos":  "",
            "confidence":    "",
            "reviewer":      "",
        })

    # Summary
    total = len(w_elements)
    print(f"\nAuto-assigned:          {stats['auto_assigned']}")
    print(f"Already had @pos:       {stats['already_has_pos']}")
    print(f"Pending (multi-POS):    {stats['multi_pos']}")
    print(f"Pending (no lemmaRef):  {stats['no_lemma']}")
    print(f"Pending (lemma missing):{stats['lemma_missing']}")
    print(f"Pending total:          {len(pending_rows)}")
    final_pos = stats["already_has_pos"] + (stats["auto_assigned"] if not dry_run else 0)
    print(f"\nEstimated @pos after run: {final_pos + stats['auto_assigned'] if dry_run else final_pos}/{total} "
          f"({100 * (final_pos + stats['auto_assigned'] if dry_run else final_pos) / total:.1f}%)")

    # Write pending TSV
    fieldnames = ["xml_id", "form", "context", "lemma_id", "candidate_pos",
                  "resolved_pos", "confidence", "reviewer"]
    with pending_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(pending_rows)
    print(f"\nPending TSV written to {pending_path} ({len(pending_rows)} rows)")

    if dry_run:
        print("\nDRY RUN: TEI not modified.")
        return

    # Write updated TEI
    tree.write(str(tei_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"TEI written to {tei_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 2: auto-assign @pos to WZB <w> elements")
    parser.add_argument("--tei",     default=str(DEFAULT_TEI), help="Path to annotated TEI file")
    parser.add_argument("--lexicon", default=str(DEFAULT_LEX), help="Path to lexicon.xml")
    parser.add_argument("--output",  default=str(DEFAULT_OUT), help="Path for pending TSV output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report counts and write TSV without modifying the TEI")
    args = parser.parse_args()

    assign_pos(
        tei_path=Path(args.tei),
        lex_path=Path(args.lexicon),
        pending_path=Path(args.output),
        dry_run=args.dry_run,
    )
