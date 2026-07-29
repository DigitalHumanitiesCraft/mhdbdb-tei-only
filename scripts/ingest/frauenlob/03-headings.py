#!/usr/bin/env python3
"""FR1/FR2/FR3: Ueberschriften-Tokens bereinigen und GA-Zaehlung sichtbar machen.

Issue #236, Punkte C und E.

Ausgangslage: Die roemischen Ordnungszahlen der Toene sind im Legacy-Linecode ueber
die letzte Stelle (`h` = HEADLINE) markiert, wurden beim Ingest aber weder zu `<head>`
noch zu `<hi rend="head">` konvertiert. Sie stehen als gewoehnliche Tokens im Textfluss:
die erste jeweils als loses `<p>` direkt unter `<body>`, alle weiteren am Ende des
*vorangehenden* Tons. Teils tragen sie `@lemmaRef`/`@ana` und landen damit in
Lemmafrequenz und Woerterbuch (derselbe Fehlertyp wie #228).

Dieses Skript:
  1. entfernt diese Tokens ersatzlos (der Inhalt wandert nach 2.),
  2. setzt je `<div type="song">` ein `<head>` mit GA-Nummer und Ton-Namen,
  3. macht bei FR2 die verlorene GA-Ebene XIV in `div/@n` explizit.

Erkennung der Tokens: Der `@xml:id`-Rumpf ist der Linecode ohne fuehrende Nullen,
seine letzte Ziffer ist die `h`-Stelle. `h != 0` heisst Ueberschrift. Das trifft in
FR1 26, in FR2 2 und in FR3 14 Tokens — exakt die im Issue genannten Zahlen.

Idempotent: ein zweiter Lauf findet weder Tokens noch fehlende `<head>`.

    python scripts/ingest/frauenlob/03-headings.py [--dry-run]
"""
import csv
import sys
from pathlib import Path

# Windows-Konsole schreibt sonst cp1252 und stirbt an "ä"/"–".
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed")

REPO = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / "source"
TEI_NS = "http://www.tei-c.org/ns/1.0"
XID = "{http://www.w3.org/XML/1998/namespace}id"

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]

# Die beiden Anhaenge des Supplementbands. Die Herausgeber haben Anhang I als XV.
# und Anhang II als XIV. gezaehlt; die MHDBDB hat sie beim Ingest getauscht, damit
# die Reihenfolge XIII.-XIV.-XV. stimmt (siehe <normalization> in FR3).
FR3_ANHAENGE = {
    "14": "XIV. Minnelieder aus Ettmüllers Ausgabe (Anhang II der Ausgabe)",
    "15": "XV. Sangsprüche aus Ettmüllers Ausgabe (Anhang I der Ausgabe)",
}


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


def load_tonnamen():
    names = {}
    with (SOURCE / "ga-tonnamen.tsv").open(encoding="utf-8") as fh:
        rows = [ln for ln in fh if not ln.startswith("#")]
    for row in csv.DictReader(rows, delimiter="\t"):
        names[row["ga"]] = row["name"]
    return names


def is_heading_token(el):
    """Traegt das Token die h-Stelle des Linecodes (h != 0)?"""
    xid = el.get(XID)
    if not xid or "_" not in xid:
        return False
    stem = xid.split("_")[1]
    return stem.isdigit() and stem[-1] != "0"


def strip_heading_tokens(body):
    """Entfernt die Ordnungszahl-Tokens und leergewordene Huellen."""
    removed = []
    for el in list(body.iter()):
        if el.tag in (q("w"), q("pc")) and is_heading_token(el):
            removed.append((el.get(XID), el.text))
            parent = el.getparent()
            # Tail des Tokens an den Vorgaenger bzw. den Elterntext haengen,
            # damit kein Whitespace-Sprung im Textfluss entsteht.
            prev = el.getprevious()
            if el.tail:
                if prev is not None:
                    prev.tail = (prev.tail or "") + el.tail
                else:
                    parent.text = (parent.text or "") + el.tail
            parent.remove(el)

    # Leergewordene <hi>-Huellen aufloesen.
    for hi in list(body.iter(q("hi"))):
        if len(hi) == 0 and not (hi.text or "").strip():
            parent = hi.getparent()
            prev = hi.getprevious()
            if hi.tail:
                if prev is not None:
                    prev.tail = (prev.tail or "") + hi.tail
                else:
                    parent.text = (parent.text or "") + hi.tail
            parent.remove(hi)

    # Das lose <p> direkt unter <body> faellt weg, sobald es leer ist.
    dropped_p = 0
    for p in list(body):
        if p.tag == q("p") and len(p) == 0 and not (p.text or "").strip():
            body.remove(p)
            dropped_p += 1

    return removed, dropped_p


def set_head(div, text, indent):
    """Setzt bzw. aktualisiert das <head> als erstes Kind eines div."""
    existing = div.find(q("head"))
    if existing is not None:
        if existing.text == text:
            return False
        existing.text = text
        return True
    head = etree.Element(q("head"))
    head.text = text
    head.tail = "\n" + " " * indent
    div.insert(0, head)
    if div.text is None or div.text.strip() == "":
        div.text = "\n" + " " * indent
    return True


def process(sigle, tonnamen, dry_run):
    path = REPO / "tei" / f"{sigle}.tei.xml"
    tree = etree.parse(str(path))
    body = tree.find(f".//{q('body')}")

    removed, dropped_p = strip_heading_tokens(body)
    print(f"=== {sigle} ===")
    print(f"  Ueberschriften-Tokens entfernt: {len(removed)}"
          + (f", loses <p> unter <body>: {dropped_p}" if dropped_p else ""))
    for xid, text in removed:
        print(f"      {xid:<22} {text!r}")

    songs = [d for d in body if d.tag == q("div") and d.get("type") == "song"]
    changed_heads = 0

    if sigle == "FR2":
        # FR2 sind die Lieder der GA XIV. Die Ebene XIV existierte bisher nur als
        # das lose <p>xiv.</p>; sie wandert in div/@n und in ein <head> am Body-Anfang.
        for div in songs:
            n = div.get("n")
            if n and not n.startswith("XIV,"):
                div.set("n", f"XIV,{n}")
        if body.find(q("head")) is None:
            head = etree.Element(q("head"))
            head.text = f"XIV. {tonnamen['XIV']}"
            head.tail = "\n" + " " * 6
            body.insert(0, head)
            if body.text is None or body.text.strip() == "":
                body.text = "\n" + " " * 6
            changed_heads += 1
        print(f"  div/@n -> XIV,1 … XIV,{len(songs)}; <head> am Body-Anfang gesetzt")
    else:
        for div in songs:
            n = div.get("n")
            if sigle == "FR3" and n in FR3_ANHAENGE:
                text = FR3_ANHAENGE[n]
            else:
                roman = ROMAN[int(n)]
                name = tonnamen.get(roman)
                if not name:
                    sys.exit(f"ERROR: kein Ton-Name fuer {sigle} div n={n} (GA {roman})")
                text = f"{roman}. {name}"
            if set_head(div, text, 8):
                changed_heads += 1
                print(f"      div n={n:<4} -> <head>{text}</head>")

    print(f"  <head>-Elemente gesetzt/aktualisiert: {changed_heads}")

    lemma_heads = [x for x, _ in removed]
    if lemma_heads:
        print(f"  (die entfernten Tokens trugen teils @lemmaRef/@ana — vgl. #228)")

    if not dry_run:
        tree.write(str(path), encoding="UTF-8", xml_declaration=True)
        print(f"  geschrieben: {path.relative_to(REPO)}")
    print()
    return len(removed) + changed_heads


def main():
    dry_run = "--dry-run" in sys.argv
    tonnamen = load_tonnamen()
    total = 0
    for sigle in ("FR1", "FR2", "FR3"):
        total += process(sigle, tonnamen, dry_run)
    if dry_run:
        print("--dry-run: nichts geschrieben.")
    print(f"Aenderungen gesamt: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
