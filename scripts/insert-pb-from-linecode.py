#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert <pb/> milestones into 14 TEI files using Julia's Linecode handover.

Issue: #26 (Fehlende page/pb-Auszeichnung)

For each text in TEMPLATES: parse the Linecode .txt to find lines where the
page value (template letters `p` and optionally `v`) changes. Insert a
<pb n="N"/> (or <pb n="Nr"/Nv"/> if recto/verso digit present) before the
line element containing the first <w> of the new page.

Linecode templates come from Julia's TEXT_DATA_TABLE.csv (handover folder).
Templates are 19 chars wide; file Linecodes are either 13 or 19 chars.
File codes are right-aligned against the template: a 13-char file Linecode
maps to template positions 7-19, with the leading 6 template positions
(always-zero padding) dropped.

Insertion convention:
  - Verse texts (<l n="..">): insert <pb> as previous sibling of <l>.
  - Prose texts (<lb n=".."/>): insert <pb> as previous sibling of <lb>.
  - Combine ppp+v as n="Nr"/n="Nv" without @type (matches WZB precedent).

Usage:
  python scripts/insert-pb-from-linecode.py \\
      --linecode-dir "C:/Users/chstn/Downloads/Linecode2TEI/Linecode2TEI/OUTDATED-Texte-mit-Linecode" \\
      [--dry-run] [--sigles APO,ARB,...]
"""

import argparse
import sys
from pathlib import Path
from lxml import etree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"

# Linecode templates per text (from Julia's TEXT_DATA_TABLE.csv).
# All 19 chars wide. 'p' = page (PAGE), 'v' = recto/verso (HANDWRITINGSHEETPAGE).
# DIS (no page positions) and BDK (no Linecode file, plus already has 24 pb)
# are intentionally excluded.
TEMPLATES = {
    "APO":  "000000000000pppv--h",
    "ARB":  "00000000000000pp--h",
    "ATF":  "0000000000zzpppv--h",
    "DIO":  "00000000000000ppp--",
    "DL2":  "000000tpppcccuaa--k",
    "ESB":  "000000000000000pp--",
    "MBS1": "0000000000000zppv--",
    "MBS5": "000000000czzpppv--h",
    "MBS7": "000000000000zpppv--",
    "MNA":  "0000000000000pppa--",
    "MR1":  "0000000zzpppv----hk",
    "MR2":  "00000zzpppvl----ukh",
    "MSP":  "000000000000pppv--h",
    "REG":  "00000000000000pv--h",
}


def decode_page_label(linecode: str, template: str) -> str | None:
    """Decode page label from a Linecode string given the text's template.

    Returns 'N' for plain page, 'Nr' / 'Nv' for recto/verso, or None if
    the resulting page number is 0 (uninitialized).
    """
    offset = len(template) - len(linecode)  # template positions dropped from front
    page_digits = []
    recto_verso = None
    for i, ch in enumerate(template):
        file_pos = i - offset
        if file_pos < 0:
            continue
        if ch == "p":
            page_digits.append(linecode[file_pos])
        elif ch == "v":
            recto_verso = linecode[file_pos]
    if not page_digits:
        return None
    page = int("".join(page_digits))
    if page == 0:
        return None
    label = str(page)
    if recto_verso == "1":
        label += "r"
    elif recto_verso == "2":
        label += "v"
    return label


def find_page_anchors(linecode_path: Path, template: str):
    """Yield (xml_id_numeric, page_label) for each page transition."""
    prev_label = None
    with linecode_path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split(None, 1)
            if not parts or not parts[0].isdigit():
                continue
            lc = parts[0]
            label = decode_page_label(lc, template)
            if label is None:
                prev_label = None
                continue
            if label != prev_label:
                stripped = lc.lstrip("0") or "0"
                yield stripped, label
                prev_label = label


def find_target_w(root, sigle: str, xml_id_numeric: str):
    """Find the first <w> matching SIG_<id>_0 (or _1 if _0 absent)."""
    for suffix in ("_0", "_1", "_2"):
        target_id = f"{sigle}_{xml_id_numeric}{suffix}"
        elems = root.xpath(
            f".//tei:w[@xml:id='{target_id}']",
            namespaces={"tei": NS_TEI},
        )
        if elems:
            return elems[0]
    return None


BLOCK_TAGS = {f"{{{NS_TEI}}}{t}" for t in ("p", "div", "body", "lg", "head", "l")}
WRAPPER_TAGS = {f"{{{NS_TEI}}}{t}" for t in ("hi", "supplied", "add", "unclear", "note")}
TOKEN_TAGS = {f"{{{NS_TEI}}}{t}" for t in ("w", "pc", "caesura")}
PB_TAG = f"{{{NS_TEI}}}pb"
LB_TAG = f"{{{NS_TEI}}}lb"
L_TAG = f"{{{NS_TEI}}}l"


def find_insertion_point(w_elem):
    """Return the element before which to insert <pb>, or None if a <pb>
    already sits at that position.

    Logic:
      1. Bubble out of phrase-level wrappers (<hi>, <supplied>, <add>,
         <unclear>, <note>) so the target sits as a child of a block
         container (<p>, <div>, <lg>, <l>, <head>, <body>).
      2. Inspect the target's preceding siblings until we hit a token
         (<w>/<pc>) or a line marker (<lb>) or another <pb>:
           - <pb> hit first → already marked, skip.
           - <lb> hit first → line-aligned page break: insert before <lb>.
           - <w>/<pc> hit first → mid-line page break: insert before target.
      3. No preceding tokens at all: target is start of its block.
           - If parent is <l>: insert before <l> (verse line-start convention).
           - Otherwise: insert before target.
    """
    target = w_elem
    while target.getparent() is not None and target.getparent().tag in WRAPPER_TAGS:
        target = target.getparent()

    parent = target.getparent()
    if parent is None or parent.tag not in BLOCK_TAGS:
        # Unexpected: target sits outside our recognized container set.
        return target  # best-effort

    prev_sib = target.getprevious()
    if prev_sib is not None:
        if prev_sib.tag == PB_TAG:
            return None
        if prev_sib.tag == LB_TAG:
            return prev_sib
        return target  # mid-block: insert inline before target

    # No preceding sibling → target is first child of its block.
    if parent.tag == L_TAG:
        return parent
    return target


# Backwards-compat name used in stats reporting.
find_line_element = find_insertion_point


def insert_pb_for_text(sigle: str, tei_path: Path, linecode_path: Path,
                      template: str, dry_run: bool) -> dict:
    """Insert <pb/> elements for one text. Returns stats dict."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()

    anchors = list(find_page_anchors(linecode_path, template))
    stats = {
        "sigle": sigle,
        "anchors": len(anchors),
        "inserted": 0,
        "missing_w": [],
        "missing_line": [],
        "already_has_pb": 0,
    }

    for xml_id_numeric, page_label in anchors:
        w = find_target_w(root, sigle, xml_id_numeric)
        if w is None:
            stats["missing_w"].append((xml_id_numeric, page_label))
            continue
        insertion_point = find_insertion_point(w)
        if insertion_point is None:
            # A <pb> already sits immediately before this anchor.
            stats["already_has_pb"] += 1
            continue
        if insertion_point.getparent() is None:
            stats["missing_line"].append((xml_id_numeric, page_label))
            continue

        pb = etree.Element(f"{{{NS_TEI}}}pb")
        pb.set("n", page_label)
        insertion_point.addprevious(pb)
        # Make the inserted <pb> sit on its own line at the same indentation
        # as the element it was placed before. The leading whitespace that
        # previously preceded insertion_point now precedes <pb>; we mirror it
        # into pb.tail so insertion_point keeps its indentation too.
        prev = pb.getprevious()
        if prev is not None and prev.tail is not None:
            pb.tail = prev.tail
        else:
            parent = pb.getparent()
            if parent is not None and parent.text is not None:
                pb.tail = parent.text
        stats["inserted"] += 1

    if not dry_run and stats["inserted"] > 0:
        # lxml drops the newline between sibling PIs (e.g. <?xml-model?>) and
        # the root element on serialization. Post-process the bytes to put it
        # back, preserving the file's original on-disk shape.
        data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
        data = data.replace(b"?><TEI ", b"?>\n<TEI ")
        if not data.endswith(b"\n"):
            data += b"\n"
        tei_path.write_bytes(data)
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--linecode-dir", required=True,
                    help="Path to OUTDATED-Texte-mit-Linecode folder")
    ap.add_argument("--tei-dir", default="tei",
                    help="Path to TEI folder (default: tei)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would be inserted without writing files")
    ap.add_argument("--sigles", default="",
                    help="Comma-separated subset to process (default: all)")
    args = ap.parse_args()

    linecode_dir = Path(args.linecode_dir)
    tei_dir = Path(args.tei_dir)

    if not linecode_dir.is_dir():
        print(f"ERROR: linecode-dir not found: {linecode_dir}", file=sys.stderr)
        return 1
    if not tei_dir.is_dir():
        print(f"ERROR: tei-dir not found: {tei_dir}", file=sys.stderr)
        return 1

    subset = set(s.strip() for s in args.sigles.split(",") if s.strip())
    sigles = sorted(subset) if subset else sorted(TEMPLATES.keys())

    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print(f"Texts: {len(sigles)}")
    print()
    print(f"{'SIG':5}  {'TPL':22}  {'anchors':>7}  {'inserted':>8}  {'has_pb':>6}  {'miss_w':>6}  {'miss_l':>6}")
    print("-" * 80)

    grand_total = {"anchors": 0, "inserted": 0, "missing_w": 0, "missing_line": 0, "already_has_pb": 0}
    for sigle in sigles:
        if sigle not in TEMPLATES:
            print(f"{sigle:5}  (no template)")
            continue
        template = TEMPLATES[sigle]
        tei_path = tei_dir / f"{sigle}.tei.xml"
        lc_path = linecode_dir / f"{sigle}.txt"
        if not tei_path.exists():
            print(f"{sigle:5}  TEI MISSING")
            continue
        if not lc_path.exists():
            print(f"{sigle:5}  LINECODE MISSING")
            continue

        stats = insert_pb_for_text(sigle, tei_path, lc_path, template, args.dry_run)
        print(f"{sigle:5}  {template:22}  {stats['anchors']:>7}  "
              f"{stats['inserted']:>8}  {stats['already_has_pb']:>6}  "
              f"{len(stats['missing_w']):>6}  {len(stats['missing_line']):>6}")
        grand_total["anchors"] += stats["anchors"]
        grand_total["inserted"] += stats["inserted"]
        grand_total["missing_w"] += len(stats["missing_w"])
        grand_total["missing_line"] += len(stats["missing_line"])
        grand_total["already_has_pb"] += stats["already_has_pb"]

        if stats["missing_w"] and args.dry_run:
            print(f"        missing <w> examples: {stats['missing_w'][:3]}")
        if stats["missing_line"] and args.dry_run:
            print(f"        missing <l>/<lb> examples: {stats['missing_line'][:3]}")

    print("-" * 80)
    print(f"{'TOTAL':5}  {'':22}  {grand_total['anchors']:>7}  "
          f"{grand_total['inserted']:>8}  {grand_total['already_has_pb']:>6}  "
          f"{grand_total['missing_w']:>6}  {grand_total['missing_line']:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
