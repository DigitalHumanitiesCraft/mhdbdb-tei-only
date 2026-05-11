#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add a new lemma entry to authority-files/lexicon.xml.

Auto-assigns the next lemma ID and sense ID (max existing + 20, matching
the WZB Phase 1b addition convention).  The new <entry> is inserted
immediately after the current highest-ID lemma in the lexicon.

Usage:
    py scripts/wzb-add-lemma.py --orth <form> --pos <POS> --concept <ID> [...]
    py scripts/wzb-add-lemma.py --orth weise --pos NOM --concept concept_23112700
    py scripts/wzb-add-lemma.py --orth zipper --pos NOM \
        --concept concept_23305330 --concept concept_14012000 \
        --ana type_12345 type_67890

Options:
    --orth TEXT         Orthographic (lemma) form (required)
    --pos TAG           POS tag — one of the 19 valid MHDBDB tags (required)
    --concept ID [...]  concept_XXXXXXXX IDs (repeatable, at least one required)
    --ana TYPE [...]    type_XXXXX IDs for the <sense @ana> attribute (optional)
    --dry-run           Print the new <entry> XML without modifying any file
    --lexicon PATH      Override lexicon.xml path
    --concepts PATH     Override concepts.xml path
"""

import re
import sys
import argparse
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed — run: pip install lxml")

NS_TEI  = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"
XML_ID  = f"{{{NS_XML}}}id"

VALID_POS = {
    "PRO", "VRB", "NOM", "ADJ", "ADV", "DET", "CNJ", "SCNJ", "CCNJ",
    "PRP", "VEX", "POS", "NAM", "NUM", "NEG", "INJ", "VEM", "IPA", "DIG",
}

PROJECT_ROOT  = Path(__file__).parent.parent
DEFAULT_LEX   = PROJECT_ROOT / "authority-files" / "lexicon.xml"
DEFAULT_CON   = PROJECT_ROOT / "authority-files" / "concepts.xml"
ENTRY_INDENT  = "        "   # 8 spaces — matches existing lexicon indentation
CHILD_INDENT  = "          " # 10 spaces


def next_lemma_id(doc) -> int:
    ids = [
        int(m.group(1))
        for e in doc.iter(f"{{{NS_TEI}}}entry")
        if (xid := e.get(XML_ID, "")) and (m := re.fullmatch(r"lemma_(\d+)", xid))
    ]
    return max(ids) + 20


def next_sense_id(doc) -> int:
    ids = [
        int(m.group(1))
        for s in doc.iter(f"{{{NS_TEI}}}sense")
        if (xid := s.get(XML_ID, "")) and (m := re.search(r"_sense_(\d+)$", xid))
    ]
    return max(ids) + 20


def validate_concepts(concept_ids: list[str], con_path: Path) -> list[str]:
    """Return list of concept IDs not found in concepts.xml."""
    con_doc = etree.parse(str(con_path))
    known = {
        e.get(XML_ID, "")
        for e in con_doc.iter(f"{{{NS_TEI}}}category")
    }
    return [c for c in concept_ids if c not in known]


def build_entry(lemma_num: int, sense_num: int, orth: str, pos: str,
                concept_ids: list[str], ana_types: list[str]) -> etree._Element:
    lemma_id = f"lemma_{lemma_num}"
    sense_id = f"{lemma_id}_sense_{sense_num}"

    entry = etree.Element(f"{{{NS_TEI}}}entry")
    entry.set(XML_ID, lemma_id)
    entry.text = f"\n{CHILD_INDENT}"

    form = etree.SubElement(entry, f"{{{NS_TEI}}}form")
    form.set("type", "lemma")
    form.text = f"\n{CHILD_INDENT}  "
    orth_el = etree.SubElement(form, f"{{{NS_TEI}}}orth")
    orth_el.text = orth
    orth_el.tail = f"\n{CHILD_INDENT}"
    form.tail = f"\n{CHILD_INDENT}"

    gramGrp = etree.SubElement(entry, f"{{{NS_TEI}}}gramGrp")
    gramGrp.text = f"\n{CHILD_INDENT}  "
    pos_el = etree.SubElement(gramGrp, f"{{{NS_TEI}}}pos")
    pos_el.text = pos
    pos_el.tail = f"\n{CHILD_INDENT}"
    gramGrp.tail = f"\n{CHILD_INDENT}"

    sense = etree.SubElement(entry, f"{{{NS_TEI}}}sense")
    sense.set(XML_ID, sense_id)
    if ana_types:
        sense.set("ana", " ".join(f"#{t}" for t in ana_types))
    sense.text = f"\n{CHILD_INDENT}  "
    for i, cid in enumerate(concept_ids):
        ptr = etree.SubElement(sense, f"{{{NS_TEI}}}ptr")
        ptr.set("target", f"concepts.xml#{cid}")
        ptr.tail = f"\n{CHILD_INDENT}  " if i < len(concept_ids) - 1 else f"\n{CHILD_INDENT}"
    sense.tail = f"\n{ENTRY_INDENT}"

    entry.tail = f"\n{ENTRY_INDENT}"
    return entry


def find_insertion_point(doc) -> tuple:
    """Return (parent_element, index_after_which_to_insert) for the max-id entry."""
    max_id, max_entry = max(
        (
            (int(m.group(1)), e)
            for e in doc.iter(f"{{{NS_TEI}}}entry")
            if (xid := e.get(XML_ID, "")) and (m := re.fullmatch(r"lemma_(\d+)", xid))
        ),
        key=lambda x: x[0],
    )
    parent = max_entry.getparent()
    idx = list(parent).index(max_entry)
    return parent, idx, max_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new lemma entry to lexicon.xml")
    parser.add_argument("--orth", required=True, help="Orthographic (lemma) form")
    parser.add_argument("--pos",  required=True, help=f"POS tag ({', '.join(sorted(VALID_POS))})")
    parser.add_argument("--concept", required=True, action="append", dest="concepts",
                        metavar="CONCEPT_ID", help="concept_XXXXXXXX ID (repeatable)")
    parser.add_argument("--ana", nargs="+", default=[], metavar="TYPE_ID",
                        help="type_XXXXX IDs for <sense @ana> (optional)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lexicon",  default=str(DEFAULT_LEX))
    parser.add_argument("--concepts", default=str(DEFAULT_CON))
    args = parser.parse_args()

    # --- validate POS ---
    if args.pos not in VALID_POS:
        sys.exit(f"ERROR: '{args.pos}' is not a valid POS tag.\nValid: {', '.join(sorted(VALID_POS))}")

    lex_path = Path(args.lexicon)
    con_path = Path(args.concepts)
    if not lex_path.exists():
        sys.exit(f"ERROR: lexicon not found: {lex_path}")
    if not con_path.exists():
        sys.exit(f"ERROR: concepts not found: {con_path}")

    # --- validate concepts exist ---
    missing = validate_concepts(args.concepts, con_path)
    if missing:
        sys.exit(f"ERROR: concept ID(s) not found in concepts.xml: {missing}")

    print(f"Parsing {lex_path.name} ...")
    doc = etree.parse(str(lex_path))

    lemma_num = next_lemma_id(doc)
    sense_num = next_sense_id(doc)
    print(f"  Next lemma ID : lemma_{lemma_num}")
    print(f"  Next sense ID : lemma_{lemma_num}_sense_{sense_num}")

    entry = build_entry(lemma_num, sense_num, args.orth, args.pos, args.concepts, args.ana)
    entry_xml = etree.tostring(entry, encoding="unicode", pretty_print=False)
    print(f"\nNew entry XML:\n{entry_xml}\n")

    if args.dry_run:
        print("DRY RUN — no changes written.")
        sys.exit(0)

    parent, idx, prev_max_id = find_insertion_point(doc)
    print(f"Inserting after lemma_{prev_max_id} (position {idx} in parent) ...")
    parent.insert(idx + 1, entry)

    doc.write(str(lex_path), encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"Written to {lex_path}")

    # --- post-write sanity check ---
    from pathlib import Path as _P
    sys.path.insert(0, str(Path(__file__).parent / "audit"))
    import importlib.util, types
    spec = importlib.util.spec_from_file_location(
        "check_senses", Path(__file__).parent / "audit" / "check-lexicon-senses.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    violations = mod.check(lex_path)
    if violations:
        print(f"\nWARNING: post-write check found entries without <sense>:")
        for v in violations:
            print(v)
    else:
        print("Post-write check: OK — all entries have <sense>")
