#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Step 1: Auto-assign @ana (and @corresp where possible).

For every <w> with @lemmaRef pointing to a single-sense lexicon entry:
  - Write @ana = "lexicon.xml#{sense_xml_id}"
  - Attempt @corresp: normalise word form, look up in variants.xml,
    intersect candidate type IDs with sense's @ana type list;
    if exactly one match write @corresp = "variants.xml#{type_id}".

Multi-sense lemmata are written to a pending TSV for LLM disambiguation.

Usage:
    py scripts/wzb-sense-assign.py [--dry-run]

Input:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml
    authority-files/lexicon.xml
    authority-files/variants.xml
    authority-files/concepts.xml

Output:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml   (updated in-place, unless --dry-run)
    Wenzelsbibel/phase3/wzb-sense-pending.tsv  (multi-sense rows for LLM review)
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

# mhg_normalizer lives in scripts/ (two levels up after the 2026-05 ingest
# reorg that moved this file into scripts/ingest/wzb/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from mhg_normalizer import normalize_mhg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT  = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_TEI   = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
DEFAULT_LEX   = PROJECT_ROOT / "authority-files" / "lexicon.xml"
DEFAULT_VAR   = PROJECT_ROOT / "authority-files" / "variants.xml"
DEFAULT_CON   = PROJECT_ROOT / "authority-files" / "concepts.xml"
DEFAULT_OUT   = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"

NS_TEI  = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"
XML_ID  = f"{{{NS_XML}}}id"

CONTEXT_WINDOW = 5  # words each side for pending TSV


# ---------------------------------------------------------------------------
# Index builders
# ---------------------------------------------------------------------------

def build_concept_index(con_path):
    """Return {concept_id: 'DE (EN)'} labels from concepts.xml."""
    tree = etree.parse(str(con_path))
    ns = {"tei": NS_TEI, "xml": NS_XML}
    index = {}
    for cat in tree.findall(".//tei:category", ns):
        cid = cat.get(XML_ID, "")
        if not cid:
            continue
        de_terms = cat.findall(f"tei:catDesc/tei:term[@{{{NS_XML}}}lang='de']", ns)
        en_terms = cat.findall(f"tei:catDesc/tei:term[@{{{NS_XML}}}lang='en']", ns)
        de = de_terms[0].text.strip() if de_terms and de_terms[0].text else ""
        en = en_terms[0].text.strip() if en_terms and en_terms[0].text else ""
        label = f"{de} ({en})" if en else de
        index[cid] = label
    return index


def build_lexicon_sense_index(lex_path):
    """Return {lemma_id: [sense_dict, ...]} where sense_dict has:
        sense_id   – xml:id of <sense>
        concept_ids – list of concept IDs (without '#')
        ana_types   – set of type IDs from @ana (without '#')
    """
    tree = etree.parse(str(lex_path))
    ns = {"tei": NS_TEI}
    index = {}
    for entry in tree.findall(".//tei:entry", ns):
        lemma_id = entry.get(XML_ID, "")
        if not lemma_id:
            continue
        senses = []
        for sense in entry.findall("tei:sense", ns):
            sid = sense.get(XML_ID, "")
            concept_ids = []
            for ptr in sense.findall("tei:ptr", ns):
                t = ptr.get("target", "")
                if "concepts.xml#" in t:
                    concept_ids.append(t.split("#")[-1])
            ana_raw = sense.get("ana", "")
            ana_types = set()
            for tok in ana_raw.split():
                tok = tok.lstrip("#")
                if tok:
                    ana_types.add(tok)
            senses.append({
                "sense_id":    sid,
                "concept_ids": concept_ids,
                "ana_types":   ana_types,
            })
        index[lemma_id] = senses
    return index


def build_variant_index(var_path):
    """Return {normalized_form: [(type_id, lemma_id), ...]} from variants.xml.

    type_id = e.g. 'type_42'  (xml:id of <form>)
    lemma_id = e.g. 'lemma_7' (from @corresp)
    """
    tree = etree.parse(str(var_path))
    ns = {"tei": NS_TEI}
    index: dict[str, list] = {}
    for entry in tree.findall(".//tei:entry", ns):
        corresp = entry.get("corresp", "")
        lemma_id = corresp.split("#")[-1] if "#" in corresp else corresp
        for form_el in entry.findall("tei:form", ns):
            type_id = form_el.get(XML_ID, "")
            text = (form_el.text or "").strip()
            if not text or not type_id:
                continue
            norm = normalize_mhg(text.lower())
            index.setdefault(norm, []).append((type_id, lemma_id))
    return index


# ---------------------------------------------------------------------------
# Context helper
# ---------------------------------------------------------------------------

def build_context_list(w_elements):
    return [(w.get(XML_ID, ""), (w.text or "").strip()) for w in w_elements]


def get_context(idx, context_list, window=CONTEXT_WINDOW):
    start = max(0, idx - window)
    end = min(len(context_list), idx + window + 1)
    parts = []
    for i in range(start, end):
        _, text = context_list[i]
        parts.append(f"[{text}]" if i == idx else text)
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Sense label builder
# ---------------------------------------------------------------------------

def sense_label(sense_dict, concept_index):
    """Build human-readable label: 'concept1_DE (EN); concept2_DE (EN)'."""
    labels = [concept_index.get(cid, cid) for cid in sense_dict["concept_ids"]]
    return "; ".join(labels) if labels else sense_dict["sense_id"]


# ---------------------------------------------------------------------------
# wordRef resolver
# ---------------------------------------------------------------------------

def resolve_corresp(form, lemma_id, sense_dict, variant_index):
    """Return corresp type ID (e.g. 'type_42') for variants.xml reference, or None."""
    norm = normalize_mhg(form.lower())
    candidates = variant_index.get(norm, [])
    matches = [
        type_id for type_id, var_lemma_id in candidates
        if var_lemma_id == lemma_id and type_id in sense_dict["ana_types"]
    ]
    if len(matches) == 1:
        return matches[0]
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def assign_senses(tei_path, lex_path, var_path, con_path, pending_path, dry_run=False):
    print(f"Loading concepts from {con_path} ...")
    concept_index = build_concept_index(con_path)
    print(f"  {len(concept_index)} concepts indexed")

    print(f"Loading lexicon senses from {lex_path} ...")
    lex_index = build_lexicon_sense_index(lex_path)
    print(f"  {len(lex_index)} entries indexed")

    print(f"Loading variant forms from {var_path} ...")
    var_index = build_variant_index(var_path)
    print(f"  {len(var_index)} normalized forms indexed")

    print(f"Parsing TEI from {tei_path} ...")
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()
    w_elements = root.findall(f".//{{{NS_TEI}}}w")
    print(f"  {len(w_elements)} <w> elements found")

    context_list = build_context_list(w_elements)

    stats = {
        "auto_meaning":   0,
        "auto_corresp":  0,
        "already_done":   0,
        "multi_sense":    0,
        "zero_sense":     0,
        "no_lemma":       0,
        "lemma_missing":  0,
    }
    pending_rows = []

    for idx, w in enumerate(w_elements):
        xml_id   = w.get(XML_ID, "")
        form     = (w.text or "").strip()
        lemma_ref = w.get("lemmaRef", "")
        pos_val   = w.get("pos", "")

        if w.get("ana"):
            stats["already_done"] += 1
            continue

        if not lemma_ref:
            stats["no_lemma"] += 1
            continue

        lemma_id = lemma_ref.split("#")[-1] if "#" in lemma_ref else lemma_ref

        senses = lex_index.get(lemma_id)
        if senses is None:
            stats["lemma_missing"] += 1
            continue

        if len(senses) == 0:
            stats["zero_sense"] += 1
            continue

        if len(senses) == 1:
            sense = senses[0]
            meaning_val = f"lexicon.xml#{sense['sense_id']}"
            if not dry_run:
                w.set("ana", meaning_val)
            stats["auto_meaning"] += 1

            corresp_type = resolve_corresp(form, lemma_id, sense, var_index)
            if corresp_type:
                if not dry_run:
                    w.set("corresp", f"variants.xml#{corresp_type}")
                stats["auto_corresp"] += 1
            continue

        # Multi-sense: add to pending TSV
        stats["multi_sense"] += 1
        candidate_senses = "|".join(
            f"{s['sense_id']} :: {sense_label(s, concept_index)}"
            for s in senses
        )
        pending_rows.append({
            "xml_id":            xml_id,
            "form":              form,
            "lemmaRef":          lemma_ref,
            "pos":               pos_val,
            "context":           get_context(idx, context_list),
            "candidate_senses":  candidate_senses,
            "resolved_sense":    "",
            "confidence":        "",
            "reviewer":          "",
        })

    # Summary
    total = len(w_elements)
    print(f"\nResults:")
    print(f"  Already had @meaningRef:   {stats['already_done']}")
    print(f"  Auto-assigned @meaningRef: {stats['auto_meaning']}")
    print(f"  Auto-assigned @corresp:    {stats['auto_corresp']}")
    print(f"  Pending (multi-sense):     {stats['multi_sense']}")
    print(f"  Skipped (no @lemmaRef):    {stats['no_lemma']}")
    print(f"  Skipped (0 senses):        {stats['zero_sense']}")
    print(f"  Skipped (lemma not found): {stats['lemma_missing']}")
    done = stats['already_done'] + stats['auto_meaning']
    print(f"\n  @ana coverage: {done}/{total} ({100*done/total:.1f}%)")

    # Write pending TSV
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["xml_id", "form", "lemmaRef", "pos", "context",
                  "candidate_senses", "resolved_sense", "confidence", "reviewer"]
    with pending_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(pending_rows)
    print(f"\nPending TSV written to {pending_path} ({len(pending_rows)} rows)")

    if dry_run:
        print("\nDRY RUN: TEI not modified.")
        return

    tree.write(str(tei_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"TEI written to {tei_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 3 Step 1: auto-assign @ana/@corresp to WZB <w> elements"
    )
    parser.add_argument("--tei",      default=str(DEFAULT_TEI))
    parser.add_argument("--lexicon",  default=str(DEFAULT_LEX))
    parser.add_argument("--variants", default=str(DEFAULT_VAR))
    parser.add_argument("--concepts", default=str(DEFAULT_CON))
    parser.add_argument("--output",   default=str(DEFAULT_OUT))
    parser.add_argument("--dry-run",  action="store_true",
                        help="Report counts and write TSV without modifying TEI")
    args = parser.parse_args()

    assign_senses(
        tei_path=Path(args.tei),
        lex_path=Path(args.lexicon),
        var_path=Path(args.variants),
        con_path=Path(args.concepts),
        pending_path=Path(args.output),
        dry_run=args.dry_run,
    )
