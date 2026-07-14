"""wzb-convert-seg-pc.py
Convert <seg type="pc"> elements to <pc join="left|right"> in WZB.tei.xml.

Join direction rule:
  - join="left"  — a preceding non-whitespace token exists in the same parent
                   (a <w>, <pc>, or non-whitespace text/tail, ignoring <lb>/<cb>)
  - join="right" — the seg appears at the start of its content block (no such predecessor)

Usage:
    python scripts/wzb-convert-seg-pc.py [--dry-run]
"""

import argparse
import re
import sys
from lxml import etree

TEI = "http://www.tei-c.org/ns/1.0"
INPUT = "ingest/wzb/WZB.tei.xml"

SKIP_TAGS = {
    f"{{{TEI}}}lb",
    f"{{{TEI}}}cb",
    f"{{{TEI}}}pb",
}


def has_text(s: str | None) -> bool:
    return bool(s and s.strip())


def determine_join(seg: etree._Element) -> str:
    """Return 'left' or 'right' based on what precedes the seg in its parent."""
    parent = seg.getparent()
    children = list(parent)
    idx = children.index(seg)

    # Check parent's leading text (before any child element)
    if idx == 0:
        if has_text(parent.text):
            return "left"
        return "right"

    # Walk backwards through siblings, skipping lb/cb/pb
    for i in range(idx - 1, -1, -1):
        prev = children[i]
        if prev.tag in SKIP_TAGS:
            # Still check the tail of the skip element for non-whitespace text
            if has_text(prev.tail):
                return "left"
            continue
        # Found a real preceding element (w, pc, hi, seg, …)
        return "left"

    # Only skip elements preceded us — check parent.text
    if has_text(parent.text):
        return "left"

    return "right"


def convert(tree: etree._ElementTree, dry_run: bool) -> int:
    root = tree.getroot()
    segs = root.findall(f".//{{{TEI}}}seg[@type='pc']")

    counts = {"left": 0, "right": 0}

    for seg in segs:
        join = determine_join(seg)
        counts[join] += 1

        if not dry_run:
            pc = etree.Element(f"{{{TEI}}}pc")
            pc.set("join", join)
            # Copy @xml:id if present
            xml_id = seg.get(f"{{{seg.nsmap.get('xml', 'http://www.w3.org/XML/1998/namespace')}}}id")
            if xml_id is None:
                # Try the Clark-notation key directly
                for attr_key in seg.attrib:
                    if attr_key.endswith("}id") and "xml" in attr_key:
                        xml_id = seg.attrib[attr_key]
                        break
            if xml_id:
                pc.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)
            pc.text = seg.text
            pc.tail = seg.tail

            parent = seg.getparent()
            idx = list(parent).index(seg)
            parent.remove(seg)
            parent.insert(idx, pc)

    total = counts["left"] + counts["right"]
    print(f"{'[DRY RUN] ' if dry_run else ''}Converted {total} <seg type=\"pc\"> elements")
    print(f"  join=left:  {counts['left']}")
    print(f"  join=right: {counts['right']}")
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing")
    args = parser.parse_args()

    parser_obj = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(INPUT, parser_obj)

    convert(tree, dry_run=args.dry_run)

    if not args.dry_run:
        tree.write(
            INPUT,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=False,  # preserve original whitespace structure
        )
        print(f"Written: {INPUT}")


if __name__ == "__main__":
    main()
