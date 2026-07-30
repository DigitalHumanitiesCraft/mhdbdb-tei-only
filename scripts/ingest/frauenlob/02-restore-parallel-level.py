#!/usr/bin/env python3
"""FR3: Parallelueberlieferungs-Ebene wiederherstellen (Issue #236, Vorschlag D).

Ausgangslage: Beim Ingest wurde die `u`-Stelle des Legacy-Linecodes
(`0000000uddaaass---h`, u = PARALLELUEBERLIEFERUNG) abgeflacht. Ergebnis sind
23 gleichrangige `<div type="song">` mit mehrfach vergebenem `@n`; 28 (Ton,
Strophe)-Paare sind mehrfach belegt und keine Stelle ist eindeutig zitierbar.

Dieses Skript fuehrt die Toene gleicher Nummer zusammen und haengt jeden
zusaetzlichen Zeugen als `<div type="parallel">` unter die betroffene Strophe:

    div[@type=song @n=5]
      div[@type=section @n=205]
        p > lg ...                      <- u=1, unveraendert
        div[@type=parallel @n=1]        <- u=2
          p > lg ...

`parallel/@n` folgt der Zaehlung der Edition (u=2 -> "Parallelueberlieferung 1"),
nicht der u-Ziffer. Die u-Ziffer bleibt ueber die `@xml:id`s der Tokens erhalten.

Kein Token, kein `<l>` und kein `@xml:id` wird veraendert — ausschliesslich die
Verschachtelung. Idempotent: ein zweiter Lauf findet nichts mehr zu tun.

    python scripts/ingest/frauenlob/02-restore-parallel-level.py [--dry-run]
"""
import sys
import collections
from pathlib import Path

# Windows-Konsole schreibt sonst cp1252 und stirbt an "ä"/"–".
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed")

# Schreibt und stellt die Prolog-Umbrueche wieder her, die
# tree.write(xml_declaration=True) verschluckt (siehe _tei_io.py).
from _tei_io import write_tei

REPO = Path(__file__).resolve().parents[3]
TEI_PATH = REPO / "tei" / "FR3.tei.xml"
TEI_NS = "http://www.tei-c.org/ns/1.0"
XID = "{http://www.w3.org/XML/1998/namespace}id"


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


def u_of(div):
    """u-Ziffer eines song-div aus dem xml:id des ersten Tokens."""
    first_w = div.find(f".//{q('w')}")
    if first_w is None:
        return None
    return int(first_w.get(XID).split("_")[1].zfill(12)[0])


def shift_indent(elem, spaces="  "):
    """Erhoeht die Einrueckung eines Teilbaums um `spaces`.

    Fasst ausschliesslich Whitespace-only-Text an. Mixed Content (der Textfluss
    in <l>, <w>, <pc>, <hi>) bleibt garantiert unberuehrt.
    """
    for node in elem.iter():
        for attr in ("text", "tail"):
            val = getattr(node, attr)
            if val and val.strip() == "" and "\n" in val:
                setattr(node, attr, val.replace("\n", "\n" + spaces))


def main():
    dry_run = "--dry-run" in sys.argv

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(TEI_PATH), parser)
    body = tree.find(f".//{q('body')}")

    song_divs = [d for d in body if d.tag == q("div") and d.get("type") == "song"]
    if not song_divs:
        sys.exit("ERROR: keine song-divs gefunden")

    # Nach Ton gruppieren, Reihenfolge der u=1-Toene bestimmt die Zielreihenfolge.
    by_ton = collections.OrderedDict()
    for div in song_divs:
        u = u_of(div)
        if u is None:
            sys.exit(f"ERROR: song-div n={div.get('n')} enthaelt kein <w>")
        by_ton.setdefault(div.get("n"), {})[u] = div

    already = body.findall(f".//{q('div')}[@type='parallel']")
    if already:
        print(f"Nichts zu tun: {len(already)} <div type=\"parallel\"> bereits vorhanden.")
        return 0

    print(f"Vorher: {len(song_divs)} song-divs, {len(by_ton)} verschiedene Toene")
    print()

    moved_sections = 0
    moved_lines = 0
    removed_divs = []

    for ton, per_u in by_ton.items():
        if 1 not in per_u:
            sys.exit(f"ERROR: Ton {ton} hat keinen u=1-Zeugen — Zielstruktur nicht bestimmbar")
        base = per_u[1]
        base_sections = {s.get("n"): s for s in base if s.tag == q("div")}

        for u in sorted(k for k in per_u if k != 1):
            other = per_u[u]
            for section in list(other):
                if section.tag != q("div"):
                    continue
                strophe = section.get("n")
                target = base_sections.get(strophe)
                if target is None:
                    sys.exit(
                        f"ERROR: Ton {ton}, Strophe {strophe} existiert in u={u}, "
                        f"aber nicht in u=1 — bitte haendisch pruefen")

                # Einrueckungstiefe: body(4) > song(6) > section(8) > parallel(10)
                indent_self = "\n" + " " * 10
                indent_close = "\n" + " " * 8

                prev = target[-1] if len(target) else None

                parallel = etree.SubElement(target, q("div"))
                parallel.set("type", "parallel")
                # Zaehlung der Edition: u=2 ist "Parallelueberlieferung 1".
                parallel.set("n", str(u - 1))

                # Inhalt des Zeugen umhaengen, Reihenfolge erhalten.
                parallel.text = section.text
                for child in list(section):
                    parallel.append(child)

                # Whitespace-only-Tails so setzen, dass die neue Ebene korrekt
                # eingerueckt steht. Nicht-Whitespace wird nie angefasst.
                if prev is not None and (prev.tail or "").strip() == "":
                    prev.tail = indent_self
                elif target.text is not None and target.text.strip() == "":
                    target.text = indent_self
                parallel.tail = indent_close

                n_lines = len(parallel.findall(f".//{q('l')}"))
                moved_lines += n_lines
                moved_sections += 1
                shift_indent(parallel)
                print(f"  Ton {ton:>3}, Strophe {strophe:>4}: u={u} -> "
                      f"<div type=\"parallel\" n=\"{u - 1}\"> ({n_lines} Verse)")

            removed_divs.append(other)

    # Die nun leeren Zusatz-Toene entfernen.
    for div in removed_divs:
        body.remove(div)

    remaining = [d for d in body if d.tag == q("div") and d.get("type") == "song"]
    total_l = len(body.findall(f".//{q('l')}"))
    total_w = len(body.findall(f".//{q('w')}"))
    n_parallel = len(body.findall(f".//{q('div')}[@type='parallel']"))

    print()
    print(f"  song-divs      {len(song_divs)} -> {len(remaining)}")
    print(f"  parallel-divs  0 -> {n_parallel}")
    print(f"  umgehaengte Strophen: {moved_sections} ({moved_lines} Verse)")
    print(f"  Gesamtbestand: {total_l} <l>, {total_w} <w>")

    # Eindeutigkeit der Adressen pruefen — das eigentliche Ziel des Umbaus.
    pairs = collections.Counter()
    for div in remaining:
        for sub in div:
            if sub.tag == q("div"):
                pairs[(div.get("n"), sub.get("n"))] += 1
    dupes = {k: v for k, v in pairs.items() if v > 1}
    if dupes:
        sys.exit(f"ERROR: (Ton, Strophe) weiterhin mehrfach belegt: {dupes}")
    print(f"  (Ton, Strophe)-Adressen: {len(pairs)}, alle eindeutig")

    if dry_run:
        print("\n--dry-run: nichts geschrieben.")
        return 0

    write_tei(tree, TEI_PATH)
    print(f"\nGeschrieben: {TEI_PATH.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
