#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WZB encoding cleanup — four targeted fixes:

1. Historiated initials
   <w> inside <hi rend="initial_historisiert"> are decorative first letters
   of words split across the TEI (e.g. "I" + "n" = "In"). They were
   incorrectly annotated as standalone tokens (DIG/NOM with lemma_2 or
   lemma_13826). Convert them to <seg type="pc">, stripping all annotation
   attributes.

2. Josua.0 — misclassified paratext
   <div xml:id="Josua.0"> sits between <div type="paratext" id="Transition6">
   and <div type="book" id="Josua"> at the body level. It contains 21 words
   of introductory text (opening verses of Joshua placed before the book div).
   wzb-structural-fix.py incorrectly assigned type="chapter" to it (the
   xml:id matches the BookName.N pattern but N=0 is not a chapter).
   Fix: type="paratext", xml:id="JosuaPrologus".

3. <div type="Transition2.1"> — non-standard type
   One div uses an ad-hoc type string instead of the canonical "paratext".
   Fix: type="paratext". The xml:id "Transition2.1" is retained.

4. Unnamed prologus body div — no @type, no @xml:id
   The main prologue text body (914 <w> elements) sits inside
   <div type="prologus" xml:id="Prologus"> with type="" and xml:id="".
   Fix: type="section", xml:id="Prologus.1".

Decision record: git history of docs/features/034-wenzelsbibel-annotation.md
§Encoding Cleanup (doc deleted after #34)
"""

import sys
import argparse
from pathlib import Path
from lxml import etree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"
XML_ID  = f"{{{NS_XML}}}id"
LANG    = f"{{{NS_XML}}}lang"

ANNOTATION_ATTRS = ("lemmaRef", "meaningRef", "wordRef", "pos")


# ---------------------------------------------------------------------------
# Fix 1: Historiated initials → <seg type="pc">
# ---------------------------------------------------------------------------

def convert_to_seg_pc(w: etree._Element, parent: etree._Element) -> None:
    seg = etree.Element(f"{{{NS_TEI}}}seg")
    wid = w.get(XML_ID, "")
    if wid:
        seg.set(XML_ID, wid)
    seg.set("type", "pc")
    seg.text = w.text
    seg.tail = w.tail
    idx = list(parent).index(w)
    parent.remove(w)
    parent.insert(idx, seg)


def fix_historiated_initials(root: etree._Element) -> int:
    """
    Convert <w> inside <hi rend="initial_historisiert"> to <seg type="pc">.
    These are decorative first letters of words, not standalone tokens.
    """
    count = 0
    for hi in root.findall(f".//{{{NS_TEI}}}hi"):
        if hi.get("rend", "") != "initial_historisiert":
            continue
        for w in list(hi.findall(f"{{{NS_TEI}}}w")):
            form = (w.text or "").strip()
            print(f"  initial: form={form!r} (was pos={w.get('pos','')!r})")
            convert_to_seg_pc(w, hi)
            count += 1
    return count


# ---------------------------------------------------------------------------
# Fix 2: Josua.0 → paratext
# ---------------------------------------------------------------------------

def fix_josua0(root: etree._Element) -> bool:
    div = root.find(f".//{{{NS_TEI}}}div[@{XML_ID}='Josua.0']")
    if div is None:
        print("  Josua.0 not found — skipping")
        return False
    old_type = div.get("type", "")
    div.set("type", "paratext")
    div.set(XML_ID, "JosuaPrologus")
    print(f"  Josua.0: type={old_type!r} → 'paratext', xml:id → 'JosuaPrologus'")
    return True


# ---------------------------------------------------------------------------
# Fix 3: Transition2.1 → type="paratext"
# ---------------------------------------------------------------------------

def fix_transition21(root: etree._Element) -> bool:
    div = root.find(f".//{{{NS_TEI}}}div[@{XML_ID}='Transition2.1']")
    if div is None:
        print("  Transition2.1 not found — skipping")
        return False
    old_type = div.get("type", "")
    div.set("type", "paratext")
    print(f"  Transition2.1: type={old_type!r} → 'paratext'")
    return True


# ---------------------------------------------------------------------------
# Fix 4: Unnamed prologus body div → type="section", xml:id="Prologus.1"
# ---------------------------------------------------------------------------

def fix_prologus_body(root: etree._Element) -> bool:
    """
    Find the unnamed div (type='', xml:id='') inside <div type='prologus'>.
    """
    prologus = root.find(f".//{{{NS_TEI}}}div[@type='prologus']")
    if prologus is None:
        print("  prologus div not found — skipping")
        return False

    for child in prologus:
        if (child.tag == f"{{{NS_TEI}}}div"
                and child.get("type", "") == ""
                and child.get(XML_ID, "") == ""):
            ws = len(child.findall(f".//{{{NS_TEI}}}w"))
            child.set("type", "section")
            child.set(XML_ID, "Prologus.1")
            print(f"  unnamed prologus div ({ws} <w>): type='' → 'section', xml:id='' → 'Prologus.1'")
            return True

    print("  unnamed prologus body div not found — already fixed or missing")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="WZB encoding cleanup: historiated initials, div types, Josua.0"
    )
    parser.add_argument("--tei", default="ingest/wzb/WZB.lemma-autofill.tei.xml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tei_path = Path(args.tei)
    print(f"Parsing {tei_path} ...")
    tree = etree.parse(str(tei_path))
    root = tree.getroot()

    print("\n1. Converting historiated initials to <seg type='pc'> ...")
    n_initials = fix_historiated_initials(root)
    print(f"   Converted: {n_initials}")

    print("\n2. Fixing Josua.0 (type='chapter' → 'paratext', xml:id → 'JosuaPrologus') ...")
    fix_josua0(root)

    print("\n3. Fixing Transition2.1 (type='Transition2.1' → 'paratext') ...")
    fix_transition21(root)

    print("\n4. Fixing unnamed prologus body div (type='' → 'section', xml:id → 'Prologus.1') ...")
    fix_prologus_body(root)

    # Summary verification
    print("\nVerification:")
    print(f"  hi rend=initial_historisiert remaining w: "
          f"{sum(len(hi.findall(f'.//{{{NS_TEI}}}w')) for hi in root.findall(f'.//{{{NS_TEI}}}hi') if hi.get('rend') == 'initial_historisiert')}")
    from collections import Counter
    div_types = Counter(d.get("type", "(none)") for d in root.findall(f".//{{{NS_TEI}}}div"))
    for t in ("chapter", "book", "paratext", "prologus", "section", "Transition2.1", "(none)"):
        if t in div_types:
            print(f"  div type={t!r}: {div_types[t]}")

    if args.dry_run:
        print("\nDRY RUN — no file written.")
        return

    tree.write(str(tei_path), encoding="UTF-8", xml_declaration=True)
    print(f"\nWritten to {tei_path}")


if __name__ == "__main__":
    main()
