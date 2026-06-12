#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert editorial <div> wrappers for HUG (songs) and MBS1/2/5/7 (recipes).

Issue: #138 (Editorische <div>-Hülle, Follow-up zu #30)

KZW-Decisions (#138, 2026-06-09):
  - HUG: Linecode-Template `0000000000000dd---k` — `dd` = Liednummer,
    "Von daher wäre eine song-Hülle sinnvoll." → <div type="song" n>
  - MBS1/2/7: "mach jeweils eine <div type='recipe'>-Hülle pro Rezept."
  - KLA: keine Hülle (keine Lieder), PL1-3: kein Substruktur-Signal im
    Linecode (t-Zähler konstant 1/2/3 = die Datei selbst) — beide skip.
  - MBS5 ergänzt (gleicher Defekt): <div type="recipe" n="2"> enthält
    real die Rezepte 2-22 und wird an den lb-n=1-Resets aufgeteilt.

Mechanik:
  HUG  — Songnummer ist deterministisch aus jeder w-id ableitbar:
         numerischer id-Teil minus die letzten 4 Stellen (3 Zeilen-
         Digits + 1 Kommentar-Flag) = Songzähler. Die Direktkinder des
         Mega-<p> (5009 <l> + 33 standalone <hi> mit römischen
         Strophenziffern) werden gruppiert und je Song in
         <div type="song" n> verschoben; das Mega-<p> entfällt
         (Verstext gehört nicht in <p>).
  MBS  — Rezeptgrenze = <lb n="1"> (Zeilenzähler-Reset im Linecode).
         Inhalt je Rezept wandert in <div type="recipe" n> mit innerem
         <p> (Muster: bestehende MBS5-Rezept-divs). Ein <pb>
         unmittelbar vor dem Reset gehört zum neuen Rezept.

Invarianten (werden geprüft, Abbruch bei Verletzung):
  - <w>/<pc>-Sequenz (ids in Dokumentreihenfolge) ist vor/nach
    identisch — Positionszählung (CONTRACTS §B) bleibt unberührt.
  - Elementzahlen l/lb/pb/hi/supplied unverändert.

Usage:
  python scripts/insert-div-wrappers-138.py --hug-linecode <HUG.txt> [--dry-run]
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
NS = {"tei": NS_TEI}

DIV_TAG = f"{{{NS_TEI}}}div"
P_TAG = f"{{{NS_TEI}}}p"
AB_TAG = f"{{{NS_TEI}}}ab"
HI_TAG = f"{{{NS_TEI}}}hi"
LB_TAG = f"{{{NS_TEI}}}lb"
PB_TAG = f"{{{NS_TEI}}}pb"
W_TAG = f"{{{NS_TEI}}}w"
PC_TAG = f"{{{NS_TEI}}}pc"


def token_id_sequence(root):
    """Alle <w>/<pc>-ids in Dokumentreihenfolge (Paritäts-Invariante)."""
    return [el.get(XML_ID) for el in root.iter(W_TAG, PC_TAG)]


def element_counts(root, *localnames):
    return {ln: len(root.findall(f".//tei:{ln}", NS)) for ln in localnames}


def serialize(tree, tei_path: Path):
    # lxml drops the newline between <?xml-model?> and <TEI> on serialize.
    data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
    data = data.replace(b"?><TEI ", b"?>\n<TEI ")
    if not data.endswith(b"\n"):
        data += b"\n"
    tei_path.write_bytes(data)


def first_token_numeric(el, sigle: str):
    """Numerischer id-Teil des ersten Nachfahren mit xml:id (w/pc/caesura...)."""
    for tok in el.iter():
        tid = tok.get(XML_ID)
        if tid and tid.startswith(sigle + "_"):
            return tid.split("_")[1]
    return None


# ---------------------------------------------------------------- HUG

def wrap_hug_songs(tei_path: Path, linecode_path: Path, dry_run: bool) -> dict:
    """40 <div type="song" n> aus dem dd-Songzähler des Linecodes."""
    # Erwartete Songmenge aus dem Linecode (Validierungsreferenz)
    songs_in_linecode = []
    with linecode_path.open(encoding="utf-8") as f:
        for raw in f:
            parts = raw.strip().split(None, 1)
            if parts and parts[0].isdigit() and len(parts[0]) == 13:
                song = int(parts[0][7:9])
                if not songs_in_linecode or songs_in_linecode[-1] != song:
                    songs_in_linecode.append(song)
    expected = list(range(1, len(songs_in_linecode) + 1))
    if songs_in_linecode != expected:
        raise SystemExit(f"HUG: Songfolge im Linecode nicht 1..N aufsteigend: "
                         f"{songs_in_linecode[:10]}...")

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()
    before_tokens = token_id_sequence(root)
    before_counts = element_counts(root, "l", "hi", "w")

    body = root.find(".//tei:body", NS)
    if body.find("tei:div", NS) is not None:
        return {"skipped": "hat bereits <div>"}
    mega_p = body.find("tei:p", NS)

    # Direktkinder nach Songnummer gruppieren.
    # Songnummer = numerischer id-Teil ohne die letzten 4 Stellen.
    groups = []  # list[(song:int, [children])]
    for child in mega_p:
        num = first_token_numeric(child, "HUG")
        if num is None or len(num) <= 4:
            raise SystemExit(f"HUG: Kind ohne ableitbare Songnummer: "
                             f"{etree.tostring(child)[:120]}")
        song = int(num[:-4])
        if not groups or groups[-1][0] != song:
            groups.append((song, []))
        groups[-1][1].append(child)

    got = [g[0] for g in groups]
    if got != expected:
        raise SystemExit(f"HUG: TEI-Songfolge {got[:10]}... != Linecode {expected[:10]}...")

    indent_div = "\n      "
    indent_child = "\n        "
    divs = []
    for song, children in groups:
        div = etree.Element(DIV_TAG, attrib={"type": "song", "n": str(song)})
        div.text = indent_child
        appended = []
        for el in children:
            if el.tag == HI_TAG:
                # Freistehende <hi> (römische Strophenziffern) sind als
                # div-Direktkind nicht tei_all-valide -> <ab>-Hülle.
                ab = etree.Element(AB_TAG)
                ab.tail = el.tail
                ab.text = indent_child + "  "
                div.append(ab)
                ab.append(el)
                el.tail = indent_child
                appended.append(ab)
            else:
                div.append(el)
                appended.append(el)
        appended[-1].tail = indent_div
        div.tail = indent_div
        divs.append(div)
    divs[-1].tail = "\n    "

    body.remove(mega_p)
    body.text = indent_div
    for div in divs:
        body.append(div)

    after_tokens = token_id_sequence(root)
    after_counts = element_counts(root, "l", "hi", "w")
    if before_tokens != after_tokens:
        raise SystemExit("HUG: Token-Sequenz verändert — Abbruch, nichts geschrieben.")
    if before_counts != after_counts:
        raise SystemExit(f"HUG: Elementzahlen verändert: {before_counts} -> {after_counts}")

    if not dry_run:
        serialize(tree, tei_path)
    return {"songs": len(divs), "l": after_counts["l"], "hi": after_counts["hi"]}


# ---------------------------------------------------------------- MBS

def split_at_lb_resets(container, sigle: str):
    """Direktkinder von `container` an <lb n='1'> in Rezept-Chunks teilen.

    Ein <pb> (ggf. mehrere) unmittelbar vor dem Reset wandert in den
    neuen Chunk (Muster MBS5 Rezept 1: <pb/> vor <lb n='1'/>).
    """
    chunks = [[]]
    children = list(container)
    for i, child in enumerate(children):
        if child.tag == LB_TAG and child.get("n") == "1" and chunks[-1]:
            chunks.append([])
            # vorangehende pb in den neuen Chunk ziehen
            while chunks[-2] and chunks[-2][-1].tag == PB_TAG:
                chunks[-1].append(chunks[-2].pop())
        chunks[-1].append(child)
    return [c for c in chunks if c]


def wrap_mbs_recipes(tei_path: Path, sigle: str, dry_run: bool) -> dict:
    """<div type="recipe" n> pro lb-n=1-Reset; inneres <p> wie MBS5-Muster."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()
    before_tokens = token_id_sequence(root)
    before_counts = element_counts(root, "lb", "pb", "hi", "supplied", "w")

    body = root.find(".//tei:body", NS)

    # MBS5: bestehendes <div type="recipe" n="2"> enthält Rezepte 2-22 und
    # wird selbst gesplittet; bei MBS1/2/7 ist das Mega-<p> der Container.
    existing_divs = body.findall("tei:div", NS)
    if sigle == "MBS5":
        target_div = existing_divs[-1]
        container = target_div.find("tei:p", NS)
        n_start = int(target_div.get("n"))
        insert_parent, insert_pos = body, list(body).index(target_div)
    else:
        if existing_divs:
            return {"skipped": "hat bereits <div>"}
        container = body.find("tei:p", NS)
        n_start = 1
        insert_parent, insert_pos = body, list(body).index(container)

    chunks = split_at_lb_resets(container, sigle)

    indent_div = "\n      "
    indent_p = "\n        "
    indent_child = "\n          "
    new_divs = []
    for i, chunk in enumerate(chunks):
        div = etree.Element(DIV_TAG, attrib={"type": "recipe", "n": str(n_start + i)})
        div.text = indent_p
        p = etree.SubElement(div, P_TAG)
        p.text = indent_child
        for el in chunk:
            p.append(el)
        chunk[-1].tail = indent_p
        p.tail = indent_div
        div.tail = indent_div
        new_divs.append(div)

    if sigle == "MBS5":
        body.remove(target_div)
    else:
        body.remove(container)
    for off, div in enumerate(new_divs):
        insert_parent.insert(insert_pos + off, div)
    new_divs[-1].tail = "\n    " if new_divs[-1] is list(body)[-1] else indent_div

    after_tokens = token_id_sequence(root)
    after_counts = element_counts(root, "lb", "pb", "hi", "supplied", "w")
    if before_tokens != after_tokens:
        raise SystemExit(f"{sigle}: Token-Sequenz verändert — Abbruch, nichts geschrieben.")
    if before_counts != after_counts:
        raise SystemExit(f"{sigle}: Elementzahlen verändert: {before_counts} -> {after_counts}")

    if not dry_run:
        serialize(tree, tei_path)
    return {"recipes": len(new_divs), "n_range": f"{n_start}-{n_start + len(new_divs) - 1}",
            "lb": after_counts["lb"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hug-linecode", required=True,
                    help="Pfad zu KZWs HUG.txt-Export (Issue #138)")
    ap.add_argument("--tei-dir", default="tei")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sigles", default="HUG,MBS1,MBS2,MBS5,MBS7",
                    help="Teilmenge (Default: alle fünf)")
    args = ap.parse_args()

    tei_dir = Path(args.tei_dir)
    sigles = [s.strip() for s in args.sigles.split(",") if s.strip()]
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")

    for sigle in sigles:
        tei_path = tei_dir / f"{sigle}.tei.xml"
        if not tei_path.is_file():
            print(f"{sigle:5}  ERROR: {tei_path} fehlt")
            continue
        if sigle == "HUG":
            stats = wrap_hug_songs(tei_path, Path(args.hug_linecode), args.dry_run)
        else:
            stats = wrap_mbs_recipes(tei_path, sigle, args.dry_run)
        print(f"{sigle:5}  {stats}")


if __name__ == "__main__":
    main()
