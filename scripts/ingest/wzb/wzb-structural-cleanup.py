#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WZB structural cleanup — implements paratext encoding decisions (Issue #66).

Operations performed (in order):

1. Book headers (fw elements)
   - Strip @lemmaRef, @pos, @meaningRef, @wordRef from all <w> inside <fw>
   - These are structural running headers, not lexical tokens

2. Surplus elements
   - Strip the same annotation attributes from <w> inside <surplus>

3. CAPITULUM + adjacent Roman numeral <w> → <head type="chapter">
   - Finds each <w>CAPITULUM</w> in the text flow
   - Collects adjacent <w> siblings in the same parent that are Roman numerals
   - Replaces them with a single <head type="chapter" n="N">CAPITULUM X</head>
   - The numeral is normalised (U→V) for the @n attribute

4. Scribal marks and section initials → <seg type="pc">
   - Covers: ł, -, ̃, ჻, =, ؞, ׀, ⫶, ; and similar non-linguistic marks
   - Single-letter section initials: a, A, s, S, O, o (by context)
   - Replaces <w xml:id="...">mark</w> with <seg xml:id="..." type="pc">mark</seg>

Decision record: git history of docs/features/034-wenzelsbibel-annotation.md
§Paratext (doc deleted after #34; policy now in docs/DATA-MODEL.md → Ingest-Verfahren)
"""

import argparse
import re
import sys
from pathlib import Path
from lxml import etree

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"

ANNOTATION_ATTRS = ("lemmaRef", "meaningRef", "wordRef", "pos")

# Roman numeral characters used in WZB (U stands for V)
ROMAN_CHARS = set("IVXLCDUM")

# Scribal marks that are never linguistic tokens
SCRIBAL_MARK_FORMS = {
    "ł",        # Polish stroke-L used as paragraph marker
    "჻",        # Georgian paragraph separator
    "=",        # equals sign used as section marker
    "-",        # hyphen used as word-break / continuation mark
    "̃",        # combining tilde (standalone)
    "̄",        # combining macron (standalone)
    "̣",        # combining dot below (standalone)
    "؞",        # Arabic triple dot
    "׀",        # Hebrew punctuation paseq
    "⫶",        # triple colon operator (used decoratively)
    ";",        # semicolon used as scribal mark (context-specific)
}

# Single-letter section initials (only treated as scribal when NOT inside fw/surplus,
# no lemmaRef, and form is exactly one character)
SECTION_INITIAL_FORMS = {"a", "A", "s", "S", "O", "o"}


def is_roman_numeral(text: str) -> bool:
    """Return True if text consists entirely of Roman numeral chars (WZB: U=V)."""
    t = text.strip()
    return bool(t) and len(t) <= 10 and all(c in ROMAN_CHARS for c in t)


def roman_to_arabic(text: str) -> int:
    """Convert Roman numeral string (U=V) to integer. Returns 0 on failure."""
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000, "U": 5}
    t = text.strip()
    result, prev = 0, 0
    for ch in reversed(t):
        v = vals.get(ch, 0)
        result = result - v if v < prev else result + v
        prev = v
    return result


def strip_annotation_attrs(element):
    """Remove all annotation attributes from a <w> element."""
    for attr in ANNOTATION_ATTRS:
        element.attrib.pop(attr, None)


def process_fw_and_surplus(root):
    """Strip annotation attributes from all <w> inside <fw> and <surplus>."""
    count = 0
    for container_tag in ("fw", "surplus"):
        for container in root.findall(f".//{{{NS_TEI}}}{container_tag}"):
            for w in container.findall(f".//{{{NS_TEI}}}w"):
                had_attrs = any(w.get(a) for a in ANNOTATION_ATTRS)
                strip_annotation_attrs(w)
                if had_attrs:
                    count += 1
    return count


def collect_capitulum_group(cap_w, parent):
    """
    Given a <w>CAPITULUM</w> element and its parent, return the set of
    sibling <w> elements that form the chapter heading group:
    - the CAPITULUM element itself
    - adjacent <w> siblings (within 4 positions) whose text is a Roman numeral
    Returns (group_elements, numeral_text, insert_position_in_parent).
    """
    children = list(parent)
    cap_pos = children.index(cap_w)

    # Collect only <w> siblings and their positions in children list
    w_siblings = [(i, c) for i, c in enumerate(children) if c.tag == f"{{{NS_TEI}}}w"]
    cap_w_idx = next(j for j, (i, c) in enumerate(w_siblings) if c is cap_w)

    group = {cap_pos: cap_w}  # pos_in_children -> element
    numeral_parts = []  # (offset_from_cap, text)

    # Look ±4 w-siblings
    for dist in range(-4, 5):
        if dist == 0:
            continue
        sibling_idx = cap_w_idx + dist
        if sibling_idx < 0 or sibling_idx >= len(w_siblings):
            continue
        pos_in_children, sibling_w = w_siblings[sibling_idx]
        form = (sibling_w.text or "").strip()
        if is_roman_numeral(form):
            group[pos_in_children] = sibling_w
            numeral_parts.append((dist, form))

    # Build numeral string in order (negatives = before CAPITULUM, positives = after)
    before = " ".join(f for d, f in sorted(numeral_parts) if d < 0)
    after = " ".join(f for d, f in sorted(numeral_parts) if d > 0)
    numeral_text = (before + " " if before else "") + (after if after else "")
    numeral_text = numeral_text.strip()

    # Arabic chapter number for @n attribute
    arabic_n = roman_to_arabic(numeral_text) if numeral_text else 0

    # Head text: "CAPITULUM <numeral>" (after-position style) or "<numeral> CAPITULUM"
    if before and not after:
        head_text = f"{before} CAPITULUM"
    elif after:
        head_text = f"CAPITULUM {after}"
    else:
        head_text = "CAPITULUM"

    # Insert position = position of the first group element in children
    insert_pos = min(group.keys())

    return group, head_text, arabic_n, insert_pos


def process_capitulum(root):
    """Replace CAPITULUM + adjacent Roman numeral <w> elements with <head type='chapter'>."""
    count = 0
    w_list = root.findall(f".//{{{NS_TEI}}}w")

    for w in w_list:
        if (w.text or "").strip() != "CAPITULUM":
            continue
        parent = w.getparent()
        if parent is None:
            continue
        # Only process <w> in structural content (not inside fw/surplus — already handled)
        anc_tags = set()
        el = parent
        while el is not None:
            anc_tags.add(el.tag.split("}")[-1])
            el = el.getparent()
        if "fw" in anc_tags or "surplus" in anc_tags:
            continue

        group, head_text, arabic_n, insert_pos = collect_capitulum_group(w, parent)

        # Build <head type="chapter"> element
        head_el = etree.Element(f"{{{NS_TEI}}}head")
        head_el.set("type", "chapter")
        if arabic_n > 0:
            head_el.set("n", str(arabic_n))
        head_el.text = head_text

        # Remove group elements from parent, insert head at earliest position
        children = list(parent)
        # Remove in reverse order so indices stay valid
        for pos in sorted(group.keys(), reverse=True):
            el_to_remove = children[pos]
            # Preserve tail text (spacing)
            tail = el_to_remove.tail or ""
            parent.remove(el_to_remove)

        # Re-read children after removals
        children = list(parent)
        # Clamp insert_pos
        insert_pos = min(insert_pos, len(children))
        parent.insert(insert_pos, head_el)

        count += 1

    return count


def is_section_initial(w, parent_tag):
    """Return True if this single-letter <w> is a scribal section initial."""
    form = (w.text or "").strip()
    if form not in SECTION_INITIAL_FORMS:
        return False
    if parent_tag in ("fw", "surplus", "hi"):
        return False
    if w.get("lemmaRef", ""):
        return False  # already resolved — keep it
    return True


def convert_to_seg_pc(w, parent):
    """Replace a <w> element with <seg type='pc'> in-place."""
    seg = etree.Element(f"{{{NS_TEI}}}seg")
    wid = w.get(XML_ID, "")
    if wid:
        seg.set(XML_ID, wid)
    seg.set("type", "pc")
    seg.text = w.text
    seg.tail = w.tail

    children = list(parent)
    idx = children.index(w)
    parent.remove(w)
    parent.insert(idx, seg)


def process_scribal_marks(root):
    """Convert scribal mark and section initial <w> elements to <seg type='pc'>."""
    count = 0
    # Collect first (can't modify while iterating)
    to_convert = []
    for w in root.findall(f".//{{{NS_TEI}}}w"):
        parent = w.getparent()
        if parent is None:
            continue
        parent_tag = parent.tag.split("}")[-1]
        form = (w.text or "").strip()

        if form in SCRIBAL_MARK_FORMS:
            to_convert.append(w)
        elif is_section_initial(w, parent_tag):
            to_convert.append(w)

    for w in to_convert:
        parent = w.getparent()
        if parent is not None:
            convert_to_seg_pc(w, parent)
            count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="WZB paratext structural cleanup (Issue #66)")
    parser.add_argument("--tei", default="Wenzelsbibel/WZB.lemma-autofill.tei.xml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tei_path = Path(args.tei)
    print(f"Parsing {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()

    w_before = len(root.findall(f".//{{{NS_TEI}}}w"))
    print(f"  <w> elements before: {w_before}")

    print("\n1. Stripping annotation attrs from <fw> and <surplus> words ...")
    n_fw = process_fw_and_surplus(root)
    print(f"   Stripped: {n_fw} elements")

    print("\n2. Converting CAPITULUM + Roman numerals to <head type='chapter'> ...")
    n_cap = process_capitulum(root)
    print(f"   Chapter heads created: {n_cap}")

    print("\n3. Converting scribal marks and section initials to <seg type='pc'> ...")
    n_scribal = process_scribal_marks(root)
    print(f"   Converted: {n_scribal} elements")

    w_after = len(root.findall(f".//{{{NS_TEI}}}w"))
    seg_after = len(root.findall(f".//{{{NS_TEI}}}seg[@type='pc']"))
    head_after = len(root.findall(f".//{{{NS_TEI}}}head[@type='chapter']"))

    print(f"\nSummary:")
    print(f"  <w> before:            {w_before}")
    print(f"  <w> after:             {w_after}  (delta: {w_after - w_before})")
    print(f"  <head type='chapter'>: {head_after}")
    print(f"  <seg type='pc'>:       {seg_after}")

    if args.dry_run:
        print("\nDRY RUN — no file written.")
        return

    tree.write(str(tei_path), encoding="UTF-8", xml_declaration=True)
    print(f"\nWritten to {tei_path}")


if __name__ == "__main__":
    main()
