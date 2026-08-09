#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Dreissiger-Gliederung des Willehalm als <div type="chapter"> kodieren.

Issue: #358

## Der Befund

Der Willehalm wird nach Dreissigern zitiert (`Wh. 77,14`), aber diese
Gliederung stand nicht als Gliederung im TEI. Die 14.002 <l> hingen in
EINEM <p>, und die Abschnittsnummer existierte nur an zwei Stellen:

  1. in den Wort-IDs   WH_7714_*   = Abschnitt 77, Vers 14
  2. als <pb n="77"/>  vor dem ersten Vers des Abschnitts

Der Parzival, derselbe Autor und dieselbe Konvention, kodiert genau das
als <div type="chapter" n="77"> und hat KEIN einziges <pb>. Dasselbe
Phaenomen war also in zwei Dateien zweimal verschieden kodiert worden.

## Warum das <pb> hier nicht bleibt

Es behauptet einen Seitenanfang, und das ist es nicht. Gezaehlt werden
im Folgenden <l>-ELEMENTE: 465 der 467 Abschnitte haben exakt 30, die
beiden anderen 28 (Abschnitt 57) und 24 (Abschnitt 467, der letzte).
Wer stattdessen die tokentragenden Verse zaehlt, kommt beim letzten auf
23, weil sein <l n="24"> nur eine <caesura> enthaelt: zwei richtige
Zahlen fuer zwei Fragen. Eine Handschriftenseite mit 465 mal exakt 30
Zeilen gibt es nicht, ein Dreissiger schon.

Zum Vergleich derselbe Test an DIO, dessen 212 <pb> #26 im Mai
nachweislich aus Julias Linecode-Seitenangaben eingefuegt hat: dort
haben 210 der 212 Einheiten je 45 Verse (die restlichen 35 und 9), und
das sind echte Seiten. WH stand nicht in der #26-Sigle-Liste, seine <pb>
stammen aus der Ursprungstransformation.

Die Umkodierung ist verlustfrei: das <pb> traegt nur @n, dieselbe Zahl
steht danach am <div>, an derselben Stelle im Dokument.

## Invarianten (Abbruch bei Verletzung, es wird nichts geschrieben)

  - <w>/<pc>-Sequenz in Dokumentreihenfolge unveraendert. Das ist die
    Positionszaehlung aus CONTRACTS Paragraph B, an der Python und JS
    exakt uebereinstimmen muessen
  - Zahl der <l>, <w>, <hi>, <supplied> unveraendert
  - je Abschnitt: die Nummer am neuen <div> ist dieselbe wie die aus der
    ersten Wort-ID des Abschnitts abgeleitete. Das ist die eigentliche
    Pruefung, denn sie vergleicht die beiden Quellen der Nummer
    miteinander, statt einer von beiden zu glauben
  - <pb> 467 -> 0 und <div> 0 -> 467, beides exakt

Usage:
  python scripts/insert-div-chapters-358.py [--sigles WH] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

from lxml import etree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = "{%s}id" % NS_XML
NS = {"tei": NS_TEI}

DIV_TAG = "{%s}div" % NS_TEI
L_TAG = "{%s}l" % NS_TEI
PB_TAG = "{%s}pb" % NS_TEI
W_TAG = "{%s}w" % NS_TEI
PC_TAG = "{%s}pc" % NS_TEI

# Nur Werke, fuer die der Befund gemessen ist. DIO, FB, WLE, FP tragen
# ebenfalls ihre Abschnittsnummer nur in den Wort-IDs, sind aber NICHT
# derselbe Fall: DIO und FB sind regelmaessige Seiten (45 bzw. 32 Verse),
# WLE und FP unregelmaessig. Das ist eine philologische Frage und liegt
# als Rueckfrage an #358.
WERKE = ("WH",)


def token_id_sequence(root):
    """Alle <w>/<pc>-ids in Dokumentreihenfolge (Paritaets-Invariante)."""
    return [el.get(XML_ID) for el in root.iter(W_TAG, PC_TAG)]


def element_counts(root, *localnames):
    return {ln: len(root.findall(".//tei:%s" % ln, NS)) for ln in localnames}


def serialize(tree, tei_path):
    # lxml verliert beim Serialisieren den Umbruch zwischen <?xml-model?>
    # und <TEI> (uebernommen aus insert-div-wrappers-138.py).
    data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
    data = data.replace(b"?><TEI ", b"?>\n<TEI ")
    if not data.endswith(b"\n"):
        data += b"\n"
    tei_path.write_bytes(data)


def abschnitt_aus_wortid(l_el, sigle):
    """Abschnittsnummer aus der ersten Wort-ID eines <l>: WH_7714_0 -> 77."""
    for tok in l_el.iter(W_TAG, PC_TAG):
        tid = tok.get(XML_ID)
        if tid and tid.startswith(sigle + "_"):
            teil = tid.split("_")[1]
            if teil.isdigit():
                return int(teil) // 100
    return None


def wrap_chapters(tei_path, sigle, dry_run):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(tei_path), parser)
    root = tree.getroot()

    before_tokens = token_id_sequence(root)
    before_counts = element_counts(root, "l", "w", "hi", "supplied")
    before_pb = len(root.findall(".//tei:pb", NS))

    body = root.find(".//tei:body", NS)
    if body.find("tei:div", NS) is not None:
        return {"uebersprungen": "hat bereits <div>"}
    container = body.find("tei:p", NS)
    if container is None:
        return {"uebersprungen": "kein <p> im body"}

    kinder = [k for k in container if isinstance(k.tag, str)]
    fremd = {etree.QName(k).localname for k in kinder} - {"pb", "l"}
    if fremd:
        raise SystemExit("%s: <p> enthaelt ausser pb/l auch %s — nicht "
                         "vorgesehen, Abbruch." % (sigle, sorted(fremd)))
    if not kinder or kinder[0].tag != PB_TAG:
        raise SystemExit("%s: erstes Kind des <p> ist kein <pb> — dann faengt "
                         "der erste Abschnitt nicht am Textanfang an." % sigle)

    # An jedem <pb> einen neuen Abschnitt beginnen; das <pb> selbst geht auf,
    # seine Nummer wird die des <div>.
    gruppen = []   # [(nummer, [<l>, ...])]
    for kind in kinder:
        if kind.tag == PB_TAG:
            n = kind.get("n")
            if not (n and n.isdigit()):
                raise SystemExit("%s: <pb> ohne numerisches @n." % sigle)
            gruppen.append((int(n), []))
        else:
            gruppen[-1][1].append(kind)

    leer = [n for n, ls in gruppen if not ls]
    if leer:
        raise SystemExit("%s: Abschnitte ohne Verse: %s" % (sigle, leer))

    # Die eigentliche Pruefung: stimmen die beiden Quellen der Nummer ueberein?
    for n, ls in gruppen:
        aus_id = abschnitt_aus_wortid(ls[0], sigle)
        if aus_id != n:
            raise SystemExit(
                "%s: Abschnitt %d beginnt mit einem Vers, dessen Wort-ID auf "
                "Abschnitt %s zeigt. Die beiden Quellen widersprechen sich, "
                "Abbruch." % (sigle, n, aus_id))

    folge = [n for n, _ in gruppen]
    if folge != list(range(1, len(folge) + 1)):
        raise SystemExit("%s: Abschnittsfolge nicht 1..N aufsteigend: %s..."
                         % (sigle, folge[:8]))

    # Einrueckung: das <div> tritt an die Stelle des <p>, die <l> behalten
    # ihre eigene. So bleibt der Diff auf die Huellen beschraenkt und die
    # 14.002 Verszeilen werden nicht angefasst.
    # body.text ist die Einrueckung VOR dem <p>, also die, auf der die neuen
    # <div> stehen. container.tail ist die davor liegende Ebene (vor </body>)
    # und taugt nur fuer das letzte <div>.
    einzug_div = body.text or "\n      "
    einzug_kind = kinder[0].tail or "\n        "

    divs = []
    for n, ls in gruppen:
        div = etree.Element(DIV_TAG, attrib={"type": "chapter", "n": str(n)})
        div.text = einzug_kind
        for el in ls:
            div.append(el)
        ls[-1].tail = einzug_div
        div.tail = einzug_div
        divs.append(div)
    divs[-1].tail = container.tail

    pos = list(body).index(container)
    body.remove(container)
    for off, div in enumerate(divs):
        body.insert(pos + off, div)

    after_tokens = token_id_sequence(root)
    after_counts = element_counts(root, "l", "w", "hi", "supplied")
    if before_tokens != after_tokens:
        raise SystemExit("%s: Token-Sequenz veraendert — Abbruch, nichts "
                         "geschrieben." % sigle)
    if before_counts != after_counts:
        raise SystemExit("%s: Elementzahlen veraendert: %s -> %s"
                         % (sigle, before_counts, after_counts))
    nach_pb = len(root.findall(".//tei:pb", NS))
    nach_div = len(root.findall(".//tei:div", NS))
    if nach_pb != 0 or nach_div != before_pb:
        raise SystemExit("%s: erwartet %d <div> und 0 <pb>, gezaehlt %d und %d"
                         % (sigle, before_pb, nach_div, nach_pb))

    if not dry_run:
        serialize(tree, tei_path)
    return {"abschnitte": len(divs), "pb_aufgeloest": before_pb,
            "verse": after_counts["l"],
            "verse_je_abschnitt_haeufigster": max(
                {len(ls) for _, ls in gruppen},
                key=lambda k: sum(1 for _, ls in gruppen if len(ls) == k))}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tei-dir", default="tei")
    ap.add_argument("--sigles", default=",".join(WERKE))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Modus: %s" % ("DRY-RUN" if args.dry_run else "SCHREIBEN"))
    for sigle in [s.strip() for s in args.sigles.split(",") if s.strip()]:
        pfad = Path(args.tei_dir) / ("%s.tei.xml" % sigle)
        if not pfad.is_file():
            print("%-5s FEHLER: %s fehlt" % (sigle, pfad))
            continue
        print("%-5s %s" % (sigle, wrap_chapters(pfad, sigle, args.dry_run)))


if __name__ == "__main__":
    main()
