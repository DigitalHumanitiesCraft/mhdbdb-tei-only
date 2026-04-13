#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WZB structural fix — two operations:

1. Add @type="chapter" to unnamed chapter divs (xml:id like "Genesis.1").
   The WB-DEA transformation left these divs with type="" even though they
   represent biblical chapters. This makes them indistinguishable from
   anonymous wrapper divs.

2. Move <head type="chapter"> from inside <l>/<p> to first child of its
   target <div type="chapter">, replacing the inline position with a
   <milestone unit="chapter" n="N"/> to preserve text-flow information.

   The scribal CAPITULUM markers (now encoded as <head type="chapter">) were
   placed by wzb-structural-cleanup.py at their position in the text flow —
   inside <l> elements. TEI P5 does not allow <head> as a child of <l>.
   The correct encoding is:
     - <head type="chapter" n="N"> as first child of <div type="chapter">
     - <milestone unit="chapter" n="N"/> inline in the <l> to record position

   The arabic chapter number (@n) is recomputed from the head text using a
   space-tolerant roman_to_arabic() that handles "I X" → IX = 9 correctly.

Decision record: docs/features/034-wenzelsbibel-annotation.md §Structural Fix
"""

import re
import sys
import argparse
from pathlib import Path
from lxml import etree

# ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"
XML_ID  = f"{{{NS_XML}}}id"

# e.g. "Genesis.1", "Exodus.12", "Josua.24" — BookName.ChapterNumber
CHAPTER_ID_RE = re.compile(r"^[A-Z][a-z]+\.\d+$")


# ---------------------------------------------------------------------------
# Roman numeral helpers
# ---------------------------------------------------------------------------

def roman_to_arabic(text: str) -> int:
    """Convert Roman numeral string (U=V; spaces between letters ignored)."""
    vals = {"I": 1, "V": 5, "X": 10, "L": 50,
            "C": 100, "D": 500, "M": 1000, "U": 5}
    t = text.strip().replace(" ", "")   # "I X" → "IX"
    if not t:
        return 0
    result, prev = 0, 0
    for ch in reversed(t):
        v = vals.get(ch, 0)
        result = result - v if v < prev else result + v
        prev = v
    return result


def chapter_n_from_head_text(head_text: str) -> int:
    """Extract arabic chapter number from text like 'II CAPITULUM' or 'CAPITULUM X'."""
    remaining = head_text.strip().replace("CAPITULUM", "").strip()
    return roman_to_arabic(remaining) if remaining else 0


# ---------------------------------------------------------------------------
# Operation 1: add @type="chapter" to unnamed chapter divs
# ---------------------------------------------------------------------------

def fix_div_types(root) -> int:
    """Add @type='chapter' to divs with xml:id matching BookName.N pattern."""
    count = 0
    for div in root.findall(f".//{{{NS_TEI}}}div"):
        if div.get("type", "") == "":
            xid = div.get(XML_ID, "")
            if CHAPTER_ID_RE.match(xid):
                div.set("type", "chapter")
                count += 1
    return count


# ---------------------------------------------------------------------------
# Operation 2: move <head type="chapter"> to target div
# ---------------------------------------------------------------------------

def build_chapter_map(root: etree._Element) -> dict:
    """
    Return {book_xml_id: {chapter_int: div_element}} for all
    <div type="book"> → <div type="chapter"> pairs.
    Requires fix_div_types() to have run first.
    """
    book_chapter_map: dict = {}
    for book_div in root.findall(f".//{{{NS_TEI}}}div[@type='book']"):
        book_id = book_div.get(XML_ID, "")
        chapter_map: dict = {}
        for ch_div in book_div.findall(f"{{{NS_TEI}}}div[@type='chapter']"):
            xid = ch_div.get(XML_ID, "")
            try:
                n = int(xid.rsplit(".", 1)[-1])
                chapter_map[n] = ch_div
            except (ValueError, IndexError):
                pass
        book_chapter_map[book_id] = chapter_map
    return book_chapter_map


def ancestor_div_of_type(el: etree._Element, type_val: str):
    """Walk up tree to find nearest ancestor <div @type=type_val>."""
    el = el.getparent()
    while el is not None:
        if el.tag == f"{{{NS_TEI}}}div" and el.get("type") == type_val:
            return el
        el = el.getparent()
    return None


def next_chapter_div_sibling(chapter_div: etree._Element):
    """Return the first <div type='chapter'> sibling after chapter_div."""
    parent = chapter_div.getparent()
    if parent is None:
        return None
    siblings = list(parent)
    idx = siblings.index(chapter_div)
    for sib in siblings[idx + 1:]:
        if (sib.tag == f"{{{NS_TEI}}}div"
                and sib.get("type") == "chapter"):
            return sib
    return None


def move_chapter_heads(root: etree._Element, book_chapter_map: dict) -> tuple:
    """
    Move each <head type='chapter'> found inside <l> or <p> to the first-child
    position of its target <div type='chapter'>, replacing its former position
    with <milestone unit='chapter' n='N'/>.

    Returns (moved_count, skipped_count).
    """
    # Collect all heads currently inside l or p (not already div children)
    heads_to_move = []
    for head in root.findall(f".//{{{NS_TEI}}}head[@type='chapter']"):
        parent = head.getparent()
        if parent is not None and parent.tag in (
            f"{{{NS_TEI}}}l",
            f"{{{NS_TEI}}}p",
        ):
            heads_to_move.append(head)

    moved, skipped = 0, 0

    for head in heads_to_move:
        head_text = (head.text or "").strip()
        n_val = chapter_n_from_head_text(head_text)

        containing_book    = ancestor_div_of_type(head, "book")
        containing_chapter = ancestor_div_of_type(head, "chapter")

        if containing_book is None:
            print(f"  SKIP (no book ancestor): {head_text!r}")
            skipped += 1
            continue

        book_id      = containing_book.get(XML_ID, "")
        chapter_map  = book_chapter_map.get(book_id, {})

        # Determine target div: prefer match by chapter number, else next sibling,
        # else fall back to the containing chapter div itself (e.g. last chapter)
        target_div = None
        if n_val > 0 and n_val in chapter_map:
            target_div = chapter_map[n_val]
        elif containing_chapter is not None:
            target_div = next_chapter_div_sibling(containing_chapter)
            if target_div is None:
                # Last chapter: no next sibling, use containing div
                target_div = containing_chapter

        if target_div is None:
            print(f"  SKIP (no target div found): {head_text!r} n={n_val}")
            skipped += 1
            continue

        # Build <milestone unit="chapter" n="N"/> to mark text-flow position
        milestone = etree.Element(f"{{{NS_TEI}}}milestone")
        milestone.set("unit", "chapter")
        if n_val > 0:
            milestone.set("n", str(n_val))
        milestone.tail = head.tail  # preserve trailing whitespace

        # Replace head with milestone in its current parent (l or p)
        parent = head.getparent()
        children = list(parent)
        idx = children.index(head)
        parent.remove(head)
        parent.insert(idx, milestone)

        # Update @n to recomputed value (fixes Roman numeral parsing bugs)
        if n_val > 0:
            head.set("n", str(n_val))
        else:
            head.attrib.pop("n", None)

        head.tail = "\n          "  # indent inside div

        # Insert head as first child of target div
        target_div.insert(0, head)

        target_xid = target_div.get(XML_ID, "")
        print(f"  moved: {head_text!r} (n={n_val}) -> <div xml:id='{target_xid}'>")
        moved += 1

    return moved, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="WZB structural fix: div @type + head placement (Issue #66)"
    )
    parser.add_argument("--tei", default="Wenzelsbibel/WZB.lemma-autofill.tei.xml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tei_path = Path(args.tei)
    print(f"Parsing {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()

    # --- Operation 1 ---
    print("\n1. Adding @type='chapter' to unnamed chapter divs ...")
    n_divs = fix_div_types(root)
    print(f"   Updated: {n_divs} divs")

    # Build chapter map AFTER fixing div types
    book_chapter_map = build_chapter_map(root)
    total_chapters = sum(len(v) for v in book_chapter_map.values())
    print(f"   Chapter map: {len(book_chapter_map)} books, {total_chapters} chapters indexed")

    # --- Operation 2 ---
    print("\n2. Moving <head type='chapter'> out of <l>/<p> ...")
    n_moved, n_skipped = move_chapter_heads(root, book_chapter_map)
    print(f"\n   Moved: {n_moved}  Skipped: {n_skipped}")

    # --- Verification counts ---
    heads_in_div = sum(
        1 for h in root.findall(f".//{{{NS_TEI}}}head[@type='chapter']")
        if h.getparent() is not None
        and h.getparent().tag == f"{{{NS_TEI}}}div"
    )
    heads_still_inline = sum(
        1 for h in root.findall(f".//{{{NS_TEI}}}head[@type='chapter']")
        if h.getparent() is not None
        and h.getparent().tag != f"{{{NS_TEI}}}div"
    )
    milestones = len(root.findall(f".//{{{NS_TEI}}}milestone[@unit='chapter']"))

    print(f"\nSummary:")
    print(f"  <div type='chapter'> added:           {n_divs}")
    print(f"  <head type='chapter'> now in <div>:   {heads_in_div}")
    print(f"  <head type='chapter'> still inline:   {heads_still_inline}")
    print(f"  <milestone unit='chapter'> created:   {milestones}")

    if args.dry_run:
        print("\nDRY RUN — no file written.")
        return

    tree.write(str(tei_path), encoding="UTF-8", xml_declaration=True)
    print(f"\nWritten to {tei_path}")


if __name__ == "__main__":
    main()
