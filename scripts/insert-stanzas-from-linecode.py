#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert <lg type="stanza" n="N"> wrappers around <l>-sequences.

Issue: #23 (Fehlende Stanza-Auszeichnung, 100 Texte nach KZW-Cleanup)

For each sigle in the #23 list:
  1. Look up the Linecode template in docs/data/linecode-templates.csv
     (column LINECODE). The template marks each structural slot with
     a letter (a, c, d, p, s, ...). Position(s) of `s` = STANZA.
  2. Read the raw Linecode source `<SIG>.txt` from Julia's handover
     OneDrive folder. For each line, extract the stanza counter from
     the `s`-positions. Detect transitions (counter value changes
     between consecutive lines).
  3. For each detected stanza, find all consecutive <l>-elements in
     the TEI whose xml:ids fall in that stanza's range, and wrap
     them in <lg type="stanza" n="N">. N is assigned sequentially
     (1, 2, 3, ...) per KZW-decision (#23, 2026-05-11) — not the
     raw Linecode value.

Usage:
  python scripts/insert-stanzas-from-linecode.py \\
      --linecode-dir "C:/Users/chstn/Downloads/Linecode2TEI/Linecode2TEI/OUTDATED-Texte-mit-Linecode" \\
      [--dry-run] [--sigles GEG,KVH,JSG]

KZW-Decisions (#23, 2026-05-11):
  - <lg type="stanza"> bekommt grundsaetzlich @n (fortlaufend ab 1)
  - KVM ist Prosa, gehoert zu #44 (raus)
  - MUG, SUB haben bereits <lg type="stanza"> (skip, no overwrite)
  - MSF fehlt im Korpus (no TEI file)
"""

import argparse
import csv
import sys
from pathlib import Path
from lxml import etree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"
NS = {"tei": NS_TEI}

L_TAG = f"{{{NS_TEI}}}l"
LG_TAG = f"{{{NS_TEI}}}lg"
W_TAG = f"{{{NS_TEI}}}w"

# Sigles per #23 minus KZW-Cleanup (KVM Prosa) and audit (MUG/SUB done, MSF absent).
SIGLES_23 = (
    "GEG GOL GVE GVN GVS GVV "
    "HAW HDM HHP HHW HMU HSB HVM HVS HVW HWI "
    "JSG "
    "KCJ KK KOL KU KVH KVL "
    "LVS "
    "PUL "
    "RAB RDJ RDS RDV RLS ROA ROD RUB RUR RVB RVR "
    "SA SAL SDG SDT SES SG SGO SHF SHR SHS SHT SIG SJH SJR SJT SJW "
    "SKL SKO SKT SMT SOT SP SRK SST ST STA STE SUS SVE SVL SVW "
    "SWH SWI SWK SWT SZK "
    "TA TIT TUS "
    "UVL UVW UWL "
    "VBU VDK VIR VOB VSA VSB VST VSU VWI "
    "WDA WDB WDD WEL WME WND WVB WVG WVH WVK WVM WVP WVV"
).split()


def load_templates(csv_path: Path) -> dict[str, str]:
    """Return {sigle: linecode-template} from docs/data/linecode-templates.csv."""
    templates = {}
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            sig = row["ID"].strip()
            tpl = row["LINECODE"].strip()
            if sig and tpl:
                templates[sig] = tpl
    return templates


def stanza_positions_in_file(template: str, file_width: int) -> list[int]:
    """Return list of file-Linecode positions where 's' appears in template.

    Templates are 19-char-aligned; file Linecodes are right-aligned (offset
    = len(template) - file_width). Positions in template before the offset
    are dropped.
    """
    offset = len(template) - file_width
    return [i - offset for i, ch in enumerate(template) if ch == "s" and i - offset >= 0]


def find_stanza_anchors(linecode_path: Path, s_positions: list[int],
                        max_candidates: int = 12) -> list[tuple[str, list[str]]]:
    """Return [(stanza_value, [xml_id_numeric_candidates])] per stanza-block.

    Per stanza we collect up to `max_candidates` linecodes — needed for texts
    like WVV where the first linecode of a stanza-block is a section header
    (rendered as <head>/<supplied>, not <l>), and the actual first verse
    sits a few lines later. The wrapper tries candidates in order until one
    finds an <l>-ancestor.

    Skips the initial '00' / all-zero stanza value (typically the head/title).
    """
    anchors = []  # list of (stanza_val, [xml_id_candidates])
    prev_stanza = None
    with linecode_path.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split(None, 1)
            if not parts or not parts[0].isdigit():
                continue
            lc = parts[0]
            stanza = "".join(lc[p] for p in s_positions)
            xml_id_numeric = lc.lstrip("0") or "0"
            if stanza != prev_stanza:
                if int(stanza) > 0:
                    anchors.append((stanza, [xml_id_numeric]))
                prev_stanza = stanza
            elif anchors and len(anchors[-1][1]) < max_candidates:
                anchors[-1][1].append(xml_id_numeric)
    return anchors


def find_first_l_for_anchor(root, sigle: str, xml_id_candidates):
    """Try each candidate xml:id; return the first <l>-ancestor found.

    `xml_id_candidates` may be a single string (legacy) or a list (post #110).
    """
    if isinstance(xml_id_candidates, str):
        xml_id_candidates = [xml_id_candidates]
    for xml_id_numeric in xml_id_candidates:
        for suffix in ("_0", "_1", "_2"):
            target_id = f"{sigle}_{xml_id_numeric}{suffix}"
            for w in root.xpath(f".//tei:w[@xml:id='{target_id}']", namespaces=NS):
                cur = w
                while cur is not None and cur.tag != L_TAG:
                    cur = cur.getparent()
                if cur is not None:
                    return cur
    return None


def wrap_stanza(first_l, last_l, stanza_n: int) -> bool:
    """Wrap [first_l, last_l] (inclusive sibling range) into <lg type='stanza' n='N'>.

    Returns True on success. Both must share the same parent. Returns False
    (without modifying the tree) if the range contains an Element that is
    not <l> (e.g. a stray <hi rend="initial"> or free <w> — WVV section-wechsel
    pattern). <lg> requires <l>-only content per tei_all.rng.
    """
    parent = first_l.getparent()
    if parent is None or last_l.getparent() is not parent:
        return False

    # Pre-check: only <l> children allowed inside the range
    sib = first_l
    while sib is not None:
        if isinstance(sib.tag, str) and sib.tag != L_TAG:
            return False
        if sib is last_l:
            break
        sib = sib.getnext()

    lg = etree.Element(LG_TAG, attrib={"type": "stanza", "n": str(stanza_n)})
    # Mirror indentation: lg.tail takes first_l's tail; first_l's leading
    # whitespace (parent.text or prev sibling's tail) becomes lg.tail context.
    parent.insert(list(parent).index(first_l), lg)

    # Move children: from first_l to last_l (inclusive)
    moving = []
    sib = first_l
    while sib is not None:
        moving.append(sib)
        if sib is last_l:
            break
        sib = sib.getnext()

    for el in moving:
        lg.append(el)  # detaches from parent, appends to lg

    return True


def insert_stanzas_for_text(sigle: str, tei_path: Path, linecode_path: Path,
                            template: str, dry_run: bool) -> dict:
    """Process one text. Returns stats dict."""
    stats = {
        "sigle": sigle,
        "anchors": 0,
        "wrapped": 0,
        "skipped_existing_lg": False,
        "missing_anchors": [],
        "wrap_failed": [],
    }

    # Skip if TEI already has any <lg type="stanza">
    with tei_path.open(encoding="utf-8") as f:
        head = f.read(50000)
    if '<lg type="stanza"' in head:
        stats["skipped_existing_lg"] = True
        return stats

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()

    file_width = None
    with linecode_path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if parts and parts[0].isdigit():
                file_width = len(parts[0])
                break
    if file_width is None:
        return stats

    s_positions = stanza_positions_in_file(template, file_width)
    if not s_positions:
        return stats

    anchors = find_stanza_anchors(linecode_path, s_positions)
    stats["anchors"] = len(anchors)
    if not anchors:
        return stats

    # For each anchor, find its first <l>; then the next stanza's first <l>
    # is the boundary. The last stanza's range goes to the parent's last <l>.
    first_ls = []
    for stanza_val, candidates in anchors:
        l = find_first_l_for_anchor(root, sigle, candidates)
        if l is None:
            stats["missing_anchors"].append((candidates[0], stanza_val))
            first_ls.append(None)
        else:
            first_ls.append(l)

    # Build (first_l, last_l) ranges. last_l = sibling immediately before next first_l.
    for idx, ((stanza_val, candidates), first_l) in enumerate(zip(anchors, first_ls)):
        if first_l is None:
            continue
        if idx + 1 < len(anchors) and first_ls[idx + 1] is not None:
            next_first = first_ls[idx + 1]
            # Walk back from next_first to find the previous <l> sibling
            sib = next_first.getprevious()
            last_l = None
            while sib is not None:
                if sib.tag == L_TAG:
                    last_l = sib
                    break
                sib = sib.getprevious()
            if last_l is None:
                # Fallback: first_l itself
                last_l = first_l
        else:
            # Last stanza: walk forward to find the last <l> sibling
            last_l = first_l
            sib = first_l.getnext()
            while sib is not None:
                if sib.tag == L_TAG:
                    last_l = sib
                sib = sib.getnext()

        # Both must share parent. If walk-back from next_first landed in a
        # different container (e.g. next stanza is in a separate <p>/<div>
        # because a section boundary fell between them — see WVV 1242→2223),
        # fall back to walk-forward in first_l's own parent.
        if first_l.getparent() is not last_l.getparent():
            last_l = first_l
            sib = first_l.getnext()
            while sib is not None:
                if sib.tag == L_TAG:
                    last_l = sib
                sib = sib.getnext()
            if first_l.getparent() is not last_l.getparent():
                stats["wrap_failed"].append((candidates[0], "parent mismatch"))
                continue

        if wrap_stanza(first_l, last_l, idx + 1):
            stats["wrapped"] += 1
        else:
            stats["wrap_failed"].append((candidates[0], "wrap_stanza returned False"))

    if not dry_run and stats["wrapped"] > 0:
        # lxml drops the newline between <?xml-model?> and <TEI> on serialize.
        data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
        data = data.replace(b"?><TEI ", b"?>\n<TEI ")
        if not data.endswith(b"\n"):
            data += b"\n"
        tei_path.write_bytes(data)
    return stats


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--linecode-dir", required=True,
                    help="Path to OUTDATED-Texte-mit-Linecode folder")
    ap.add_argument("--templates",
                    default="docs/data/linecode-templates.csv",
                    help="Path to linecode-templates.csv (default: docs/data/...)")
    ap.add_argument("--tei-dir", default="tei",
                    help="TEI folder (default: tei)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would be wrapped without writing")
    ap.add_argument("--sigles", default="",
                    help="Comma-separated subset (default: all 100 from #23)")
    args = ap.parse_args()

    linecode_dir = Path(args.linecode_dir)
    tei_dir = Path(args.tei_dir)
    templates_path = Path(args.templates)

    if not linecode_dir.is_dir():
        print(f"ERROR: linecode-dir not found: {linecode_dir}", file=sys.stderr)
        return 1
    if not tei_dir.is_dir():
        print(f"ERROR: tei-dir not found: {tei_dir}", file=sys.stderr)
        return 1
    if not templates_path.is_file():
        print(f"ERROR: templates csv not found: {templates_path}", file=sys.stderr)
        return 1

    templates = load_templates(templates_path)
    print(f"Loaded {len(templates)} templates from {templates_path}")

    subset = set(s.strip() for s in args.sigles.split(",") if s.strip())
    sigles = sorted(subset) if subset else sorted(SIGLES_23)
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print(f"Texts: {len(sigles)}")
    print()
    print(f"{'SIG':5}  {'TPL':22}  {'anchors':>7}  {'wrapped':>7}  {'note':<30}")
    print("-" * 80)

    total = {"anchors": 0, "wrapped": 0, "skipped": 0, "tei_missing": 0,
             "lc_missing": 0, "no_template": 0}
    for sigle in sigles:
        tpl = templates.get(sigle)
        tei_path = tei_dir / f"{sigle}.tei.xml"
        lc_path = linecode_dir / f"{sigle}.txt"

        if not tpl:
            print(f"{sigle:5}  {'(no template)':22}")
            total["no_template"] += 1
            continue
        if not tei_path.exists():
            print(f"{sigle:5}  {tpl:22}  -  -  TEI MISSING")
            total["tei_missing"] += 1
            continue
        if not lc_path.exists():
            print(f"{sigle:5}  {tpl:22}  -  -  LINECODE MISSING")
            total["lc_missing"] += 1
            continue

        stats = insert_stanzas_for_text(sigle, tei_path, lc_path, tpl, args.dry_run)
        note = ""
        if stats["skipped_existing_lg"]:
            note = "skipped (already has <lg>)"
            total["skipped"] += 1
        elif stats["missing_anchors"]:
            note = f"missing-anchors: {len(stats['missing_anchors'])}"
        elif stats["wrap_failed"]:
            note = f"wrap-failed: {len(stats['wrap_failed'])}"

        print(f"{sigle:5}  {tpl:22}  {stats['anchors']:>7}  "
              f"{stats['wrapped']:>7}  {note:<30}")
        total["anchors"] += stats["anchors"]
        total["wrapped"] += stats["wrapped"]

    print("-" * 80)
    print(f"{'TOTAL':5}  {' '*22}  {total['anchors']:>7}  {total['wrapped']:>7}")
    print(f"  skipped (already has lg): {total['skipped']}")
    print(f"  TEI missing:              {total['tei_missing']}")
    print(f"  Linecode missing:         {total['lc_missing']}")
    print(f"  No template:              {total['no_template']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
