#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Step 3: Write @ana (and @corresp where resolvable) to TEI.

Reads wzb-sense-pending.tsv — rows with a resolved_sense value are applied.
Already-set @ana attributes are never overwritten.

@corresp auto-resolution: normalise word form → look up in variants.xml →
intersect candidate type IDs with sense's @ana list → assign if exactly one
match.

Usage:
    py scripts/wzb-sense-apply.py [--dry-run]

Input:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml
    Wenzelsbibel/phase3/wzb-sense-pending.tsv   (with resolved_sense filled in)
    authority-files/lexicon.xml
    authority-files/variants.xml

Output:
    Wenzelsbibel/WZB.lemma-autofill.tei.xml   (updated in-place, unless --dry-run)
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

sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT  = Path(__file__).parent.parent
DEFAULT_TEI   = PROJECT_ROOT / "Wenzelsbibel" / "WZB.lemma-autofill.tei.xml"
DEFAULT_PEND  = PROJECT_ROOT / "Wenzelsbibel" / "phase3" / "wzb-sense-pending.tsv"
DEFAULT_LEX   = PROJECT_ROOT / "authority-files" / "lexicon.xml"
DEFAULT_VAR   = PROJECT_ROOT / "authority-files" / "variants.xml"

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"


# ---------------------------------------------------------------------------
# Index builders (same logic as wzb-sense-assign.py)
# ---------------------------------------------------------------------------

def build_sense_ana_index(lex_path):
    """Return {sense_id: set_of_type_ids} from lexicon.xml @ana attributes."""
    tree = etree.parse(str(lex_path))
    ns = {"tei": NS_TEI}
    index = {}
    for sense in tree.findall(".//tei:sense", ns):
        sid = sense.get(XML_ID, "")
        ana_raw = sense.get("ana", "")
        ana_types = set()
        for tok in ana_raw.split():
            tok = tok.lstrip("#")
            if tok:
                ana_types.add(tok)
        if sid:
            index[sid] = ana_types
    return index


def build_variant_index(var_path):
    """Return {normalized_form: [(type_id, lemma_id), ...]} from variants.xml."""
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


def resolve_corresp(form, lemma_id, sense_id, sense_ana_index, variant_index):
    """Return corresp type ID (e.g. type_42) or None."""
    ana_types = sense_ana_index.get(sense_id, set())
    if not ana_types:
        return None
    norm = normalize_mhg(form.lower())
    candidates = variant_index.get(norm, [])
    matches = [
        type_id for type_id, var_lemma_id in candidates
        if var_lemma_id == lemma_id and type_id in ana_types
    ]
    if len(matches) == 1:
        return matches[0]   # just 'type_42', caller prepends 'variants.xml#'
    return None


# ---------------------------------------------------------------------------
# Load resolutions from pending TSV
# ---------------------------------------------------------------------------

def load_resolutions(pending_path):
    """Return {xml_id: {sense_id, lemma_id, form}} for resolved rows.

    Rows with resolved_sense=ABSTAIN are counted separately and excluded
    from TEI output — they represent principled abstentions where context
    does not permit disambiguation.
    """
    resolved = {}
    skipped = 0
    abstained = 0
    with pending_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            sense = row.get("resolved_sense", "").strip()
            if not sense:
                skipped += 1
                continue
            if sense.upper() == "ABSTAIN":
                abstained += 1
                continue
            xml_id   = row["xml_id"]
            lemma_ref = row.get("lemmaRef", "")
            lemma_id  = lemma_ref.split("#")[-1] if "#" in lemma_ref else lemma_ref
            resolved[xml_id] = {
                "sense_id": sense,
                "lemma_id": lemma_id,
                "form":     row.get("form", ""),
            }
    print(f"Loaded {len(resolved)} resolved rows "
          f"({skipped} still pending, {abstained} abstained)")
    return resolved


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def apply_senses(tei_path, pending_path, lex_path, var_path, dry_run=False):
    print(f"Loading sense @ana index from {lex_path} ...")
    sense_ana = build_sense_ana_index(lex_path)
    print(f"  {len(sense_ana)} senses indexed")

    print(f"Loading variant forms from {var_path} ...")
    var_index = build_variant_index(var_path)
    print(f"  {len(var_index)} normalized forms indexed")

    resolutions = load_resolutions(pending_path)
    if not resolutions:
        print("Nothing to apply.")
        return

    print(f"Parsing TEI from {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()
    w_elements = root.findall(f".//{{{NS_TEI}}}w")
    print(f"  {len(w_elements)} <w> elements found")

    id_index = {w.get(XML_ID, ""): w for w in w_elements if w.get(XML_ID)}

    stats = {"meaning_applied": 0, "word_ref_applied": 0, "already_set": 0, "not_found": 0}
    not_found = []

    for xml_id, info in resolutions.items():
        w = id_index.get(xml_id)
        if w is None:
            stats["not_found"] += 1
            not_found.append(xml_id)
            continue

        if w.get("ana"):
            stats["already_set"] += 1
            continue

        sense_id = info["sense_id"]
        lemma_id = info["lemma_id"]
        form     = info["form"]

        meaning_val = f"lexicon.xml#{sense_id}"
        if not dry_run:
            w.set("ana", meaning_val)
        stats["meaning_applied"] += 1

        word_frag = resolve_word_ref(form, lemma_id, sense_id, sense_ana, var_index)
        if word_frag:
            if not dry_run:
                w.set("corresp", f"variants.xml#{word_frag}")
            stats["word_ref_applied"] += 1

    # Final coverage
    total = len(w_elements)
    has_meaning = sum(1 for w in w_elements if w.get("ana"))
    projected   = has_meaning + (stats["meaning_applied"] if dry_run else 0)

    print(f"\nApplied @meaningRef:  {stats['meaning_applied']}")
    print(f"Applied @corresp:     {stats['word_ref_applied']}")
    print(f"Already had @ana (skipped): {stats['already_set']}")
    print(f"xml_id not found:    {stats['not_found']}")
    if not_found:
        for nf in not_found[:10]:
            print(f"  {nf}")

    # Decision-type breakdown (for scientific reporting)
    if "decision_type" in (list(resolutions.values())[0].keys() if resolutions else {}):
        pass  # handled below via pending TSV re-read

    if dry_run:
        print(f"\nDRY RUN: @ana coverage would be "
              f"{projected}/{total} ({100*projected/total:.1f}%)")
        print("No changes written.")
        return

    final_meaning = sum(1 for w in w_elements if w.get("ana"))
    final_word    = sum(1 for w in w_elements if w.get("corresp"))
    print(f"\nFinal @ana: {final_meaning}/{total} ({100*final_meaning/total:.1f}%)")
    print(f"Final @corresp:  {final_word}/{total} ({100*final_word/total:.1f}%)")

    tree.write(str(tei_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"TEI written to {tei_path}")


def report_decision_breakdown(pending_path: Path):
    """Print @ana coverage broken down by decision_type."""
    from collections import Counter
    import csv as _csv
    counts: Counter = Counter()
    total = 0
    with pending_path.open(encoding="utf-8") as f:
        for row in _csv.DictReader(f, delimiter="\t"):
            total += 1
            sense = row.get("resolved_sense", "").strip()
            dt    = row.get("decision_type", "").strip() or "unresolved"
            if not sense:
                dt = "unresolved"
            elif sense.upper() == "ABSTAIN":
                dt = "abstain"
            counts[dt] += 1
    print(f"\n=== Decision-type breakdown ({total} pending rows) ===")
    for dt, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {dt:<20}: {n:>6} ({100*n/total:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 3 Step 3: apply resolved @ana/@corresp to WZB TEI"
    )
    parser.add_argument("--tei",      default=str(DEFAULT_TEI))
    parser.add_argument("--pending",  default=str(DEFAULT_PEND))
    parser.add_argument("--lexicon",  default=str(DEFAULT_LEX))
    parser.add_argument("--variants", default=str(DEFAULT_VAR))
    parser.add_argument("--dry-run",  action="store_true",
                        help="Report changes without modifying TEI")
    args = parser.parse_args()

    apply_senses(
        tei_path=Path(args.tei),
        pending_path=Path(args.pending),
        lex_path=Path(args.lexicon),
        var_path=Path(args.variants),
        dry_run=args.dry_run,
    )
