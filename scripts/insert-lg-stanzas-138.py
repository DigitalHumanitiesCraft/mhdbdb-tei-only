#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert <lg type="stanza"> wrappers into HUG songs from the linecode export.

Issue: #138 Punkt 5 (HUG-Strophen, @wachauer 2026-06-12: "Ja, mach das.")

Quelle / Mechanik:
  KZWs HUG.txt-Linecode-Export enthaelt 814 roemische Strophenziffern als
  Kommentarzeilen (Flag-Ziffer 1 im 4-stelligen Zeilen-Code; Verse haben
  Flag 0). Pro Lied eroeffnet jede Marker-Zeile eine Strophe; die folgenden
  Verse gehoeren dazu bis zum naechsten Marker.

  Im TEI sind die Strophen IMPLIZIT: 33 der 40 Lieder sind stanzaisch.
  - Strophe I jedes Marker-Lieds ist ein freistehendes
    <ab><hi rend="upper_case"><w>i</w></hi></ab> am Lied-Anfang (= die 33
    standalone <ab>/<hi>).
  - Strophen II+ sind als Trailing-<w pos="DIG">ii/iii/...</w> am ENDE der
    letzten <l> der Vorstrophe eingebettet (die Marker-Tokens sitzen also
    physisch in der Vorzeile und duerfen NICHT verschoben werden).

  Deshalb gruppiert dieses Skript ganze <l> nach ihrem Erst-Token-Linecode
  in Strophen und wrappt jeden Lauf in <lg type="stanza" n>. Eingebettete
  Marker-Tokens reiten in ihrer <l> mit. Das <ab> der Strophe I bleibt vor
  dem ersten <lg> (ein <ab> ist als <lg>-Direktkind nicht TEI-valide).
  7 Lieder ohne Marker (1,2,4,5,14,21,25) bleiben unangetastet.

Invarianten (werden geprueft, Abbruch bei Verletzung):
  - <w>/<pc>-Sequenz (ids in Dokumentreihenfolge) vor/nach identisch
    (Positionszaehlung CONTRACTS Paragraph B bleibt unberuehrt).
  - Elementzahlen l/w/pc/hi/ab unveraendert; lg: 0 -> Summe der Marker (814).
  - Strophenzahl je Lied == Marker-Zahl im Linecode-Export; Strophenfolge
    1..N aufsteigend; kein Vers vor dem ersten Marker.

Usage:
  python scripts/insert-lg-stanzas-138.py --hug-linecode <HUG.txt> [--dry-run]
"""

import argparse
import re
import sys
from bisect import bisect_right
from pathlib import Path
from collections import defaultdict, Counter
from lxml import etree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"
NS = {"tei": NS_TEI}

LG_TAG = f"{{{NS_TEI}}}lg"
L_TAG = f"{{{NS_TEI}}}l"
AB_TAG = f"{{{NS_TEI}}}ab"

MARKER_RE = re.compile(r'^(\d{13})\s+([IVXLC]+)\.?\s*$')


def token_id_sequence(root):
    """Alle <w>/<pc>-ids in Dokumentreihenfolge (Paritaets-Invariante)."""
    w = f"{{{NS_TEI}}}w"
    pc = f"{{{NS_TEI}}}pc"
    return [el.get(XML_ID) for el in root.iter(w, pc)]


def element_counts(root, *localnames):
    return {ln: len(root.findall(f".//tei:{ln}", NS)) for ln in localnames}


def serialize(tree, tei_path: Path):
    # lxml drops the newline between <?xml-model?> and <TEI> on serialize.
    data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
    data = data.replace(b"?><TEI ", b"?>\n<TEI ")
    if not data.endswith(b"\n"):
        data += b"\n"
    tei_path.write_bytes(data)


def parse_marker_boundaries(linecode_path: Path) -> dict:
    """song:int -> sorted list[int] der Marker-Zeilen-Codes (Flag 1)."""
    boundaries = defaultdict(list)
    with linecode_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = MARKER_RE.match(line)
            if not m:
                continue
            code = m.group(1)
            song = int(code[7:9])
            lc = int(code[9:13])
            boundaries[song].append(lc)
    for song, codes in boundaries.items():
        if codes != sorted(codes):
            raise SystemExit(f"HUG: Marker-Codes Lied {song} nicht aufsteigend: {codes[:6]}")
    return dict(boundaries)


def l_linecode(l_el, song: int) -> int:
    """Erst-Token-Linecode einer <l> als int (numerischer id-Teil ohne Song-Praefix)."""
    prefix = str(song)
    for tok in l_el.iter():
        tid = tok.get(XML_ID)
        if tid and tid.startswith("HUG_"):
            num = tid.split("_")[1]
            if not num.startswith(prefix):
                raise SystemExit(f"HUG: Token {tid} passt nicht zu Lied {song}")
            return int(num[len(prefix):])
    raise SystemExit(f"HUG: <l> ohne Token-id in Lied {song}")


def wrap_stanzas(tei_path: Path, boundaries: dict, dry_run: bool) -> dict:
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()

    before_tokens = token_id_sequence(root)
    before_counts = element_counts(root, "l", "w", "pc", "hi", "ab", "lg")
    if before_counts["lg"] != 0:
        raise SystemExit(f"HUG: erwartet 0 <lg> vorab, gefunden {before_counts['lg']}")

    body = root.find(".//tei:body", NS)
    divs = body.findall("tei:div[@type='song']", NS)

    # Standard-Trennzeichen aus der bestehenden Struktur ableiten (robust statt hartkodiert).
    child_indent = body[0].text if body[0].text and body[0].text.strip() == "" else "\n        "
    # child_indent ist die Einrueckung der div-Kinder (= Ebene <ab>/<l>); <lg> sitzt gleichauf.
    div_close_indent = "\n      "  # </div> auf 6 Spaces

    total_stanzas = 0
    per_song = {}
    for div in divs:
        song = int(div.get("n"))
        mc = boundaries.get(song)
        if not mc:
            per_song[song] = 0  # kein Marker -> unveraendert
            continue

        children = list(div)
        ls = [c for c in children if c.tag == L_TAG]
        # Strophen-Index je <l> bestimmen (bisect: Anzahl Marker <= Linecode).
        groups = []  # list[list[<l>]]
        stanza_seq = []
        for l_el in ls:
            code = l_linecode(l_el, song)
            st = bisect_right(mc, code)  # 1-based Strophe
            if st < 1:
                raise SystemExit(f"HUG: Lied {song}, <l> code {code} vor erstem Marker {mc[0]}")
            if not stanza_seq or stanza_seq[-1] != st:
                stanza_seq.append(st)
                groups.append([])
            groups[-1].append(l_el)

        expected = list(range(1, len(mc) + 1))
        if stanza_seq != expected:
            raise SystemExit(f"HUG: Lied {song} Strophenfolge {stanza_seq[:8]}... "
                             f"!= 1..{len(mc)}")

        # Position des ersten <l> im div merken (dort kommen die <lg> hin).
        first_l = groups[0][0]
        insert_pos = children.index(first_l)

        new_lgs = []
        for i, group in enumerate(groups):
            lg = etree.Element(LG_TAG, attrib={"type": "stanza", "n": str(i + 1)})
            lg.text = child_indent
            for l_el in group:
                div.remove(l_el)
                lg.append(l_el)
                l_el.tail = child_indent  # zwischen <l> und vor </lg>
            lg.tail = child_indent
            new_lgs.append(lg)
        # letztes <lg> schliesst die div -> </div> auf 6 Spaces
        new_lgs[-1].tail = div_close_indent

        for off, lg in enumerate(new_lgs):
            div.insert(insert_pos + off, lg)

        per_song[song] = len(new_lgs)
        total_stanzas += len(new_lgs)

    after_tokens = token_id_sequence(root)
    after_counts = element_counts(root, "l", "w", "pc", "hi", "ab", "lg")

    if before_tokens != after_tokens:
        raise SystemExit("HUG: Token-Sequenz veraendert - Abbruch, nichts geschrieben.")
    expected_counts = dict(before_counts)
    expected_counts["lg"] = total_stanzas
    if after_counts != expected_counts:
        raise SystemExit(f"HUG: Elementzahlen unerwartet: {after_counts} != {expected_counts}")
    if total_stanzas != sum(len(v) for v in boundaries.values()):
        raise SystemExit(f"HUG: Strophensumme {total_stanzas} != Marker "
                         f"{sum(len(v) for v in boundaries.values())}")

    if not dry_run:
        serialize(tree, tei_path)
    return {"songs_wrapped": sum(1 for v in per_song.values() if v),
            "stanzas": total_stanzas, "lg": after_counts["lg"],
            "l": after_counts["l"], "per_song": per_song}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hug-linecode", required=True,
                    help="Pfad zu KZWs HUG.txt-Export (Issue #138)")
    ap.add_argument("--tei", default="tei/HUG.tei.xml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    boundaries = parse_marker_boundaries(Path(args.hug_linecode))
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print(f"Linecode: {len(boundaries)} Lieder mit Markern, "
          f"{sum(len(v) for v in boundaries.values())} Strophen total")

    stats = wrap_stanzas(Path(args.tei), boundaries, args.dry_run)
    print(f"HUG  songs_wrapped={stats['songs_wrapped']} stanzas={stats['stanzas']} "
          f"lg={stats['lg']} l={stats['l']}")
    anomalies = {s: n for s, n in sorted(stats["per_song"].items())}
    print("Strophen je Lied:", anomalies)


if __name__ == "__main__":
    main()
