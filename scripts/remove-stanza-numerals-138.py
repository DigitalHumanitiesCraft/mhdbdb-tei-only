#!/usr/bin/env python3
"""Strophenziffern als <w pos="DIG"> aus dem Verstext entfernen (#138).

Hintergrund
-----------
In HUG steht die roemische Strophenzahl als Wort-Token am Ende des letzten
Verses der VORIGEN Strophe. Die zugrundeliegende Edition (Hofmeister 2005)
setzt sie dagegen in die linke Randspalte, auf Hoehe des ersten Verses der
Strophe. Bei uns landet die Zahl dadurch mitten im Vers und geht als <w> in
Suche und Index ein. KZW in #138: "das ist Unsinn und wird auch nicht in der
zugrundeliegenden Edition abgebildet. Nimm die in diesem Text alle raus."

Der Randzahl-Ersatz existiert bereits: <lg type="stanza"> traegt @n, und zwar
strikt 1..N pro <div> (verifiziert: 33 divs, 814 Strophen, keine Abweichung).
Die Leseansicht kann die Zahl also aus lg/@n an den Rand setzen.

Was das Skript loescht
----------------------
Ausschliesslich <w> mit @pos="DIG", die

  1. letztes <w> ihres <l> sind,
  2. deren <l> in einem <lg type="stanza"> steht, und
  3. deren xml:id in einem eigenen ID-Block liegt (die Ziffer ist im
     Legacy-Linecode eine eigene Untereinheit, das vorangehende <pc> gehoert
     zum Vers und bleibt stehen).

Bedingung 3 ist der eigentliche Schutz: sie unterscheidet die Randziffer von
einem echten Zahlwort im Verstext, das im ID-Block des Verses saesse. Faellt
ein Token durch eine der drei Bedingungen, bricht das Skript ab, statt zu
raten.

Nicht geloescht wird das vorangehende <pc> (Verssatzzeichen) und nichts
ausserhalb von <lg type="stanza">.

Verwendung
----------
    python -X utf8 scripts/remove-stanza-numerals-138.py --dry-run
    python -X utf8 scripts/remove-stanza-numerals-138.py --apply

Standard ist --dry-run. Ohne --apply wird nichts geschrieben.

Nachgelagert (Data-Change-Lifecycle, docs/DATA-MODEL.md): variants.xml
regenerieren, beide Indexe und die API neu bauen, Versionen heben. Das
Skript macht das NICHT, es fasst nur das TEI an.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML = "http://www.w3.org/XML/1998/namespace"
XML_ID = f"{{{NS_XML}}}id"
W_TAG = f"{{{NS_TEI}}}w"
L_TAG = f"{{{NS_TEI}}}l"
LG_TAG = f"{{{NS_TEI}}}lg"

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "tei" / "HUG.tei.xml"


def id_block(xml_id):
    """Der ID-Block ohne den laufenden Token-Index.

    HUG_30040_9 -> HUG_30040 (Vers 4, Untereinheit 0)
    HUG_30041_0 -> HUG_30041 (Vers 4, Untereinheit 1 = die Randziffer)
    """
    return xml_id.rsplit("_", 1)[0] if xml_id else ""


def sammle_kandidaten(root):
    """(kandidaten, ablehnungen) -- Ablehnungen sind Abbruchgrund, keine Warnung."""
    kandidaten = []
    ablehnungen = []

    for w in root.iter(W_TAG):
        if w.get("pos") != "DIG":
            continue

        l_el = w.getparent()
        if l_el is None or l_el.tag != L_TAG:
            ablehnungen.append((w.get(XML_ID), "Elternelement ist kein <l>"))
            continue

        if [x for x in l_el.iter(W_TAG)][-1] is not w:
            ablehnungen.append((w.get(XML_ID), "nicht das letzte <w> des Verses"))
            continue

        lg = l_el.getparent()
        if lg is None or lg.tag != LG_TAG or lg.get("type") != "stanza":
            ablehnungen.append((w.get(XML_ID), "<l> steht nicht in <lg type='stanza'>"))
            continue

        vorher = w.getprevious()
        if vorher is not None and id_block(vorher.get(XML_ID)) == id_block(w.get(XML_ID)):
            ablehnungen.append((w.get(XML_ID), "im selben ID-Block wie das Vorgaengertoken"))
            continue

        kandidaten.append(w)

    return kandidaten, ablehnungen


def entferne(w):
    """<w> loeschen und die Einrueckung des schliessenden </l> erhalten."""
    eltern = w.getparent()
    vorher = w.getprevious()
    if vorher is not None:
        vorher.tail = w.tail
    else:
        eltern.text = w.tail
    eltern.remove(w)


def serialize(tree, pfad):
    # lxml verschluckt beim Serialisieren den Zeilenumbruch zwischen der
    # letzten Processing Instruction und <TEI>.
    data = etree.tostring(tree, encoding="UTF-8", xml_declaration=True)
    data = data.replace(b"?><TEI ", b"?>\n<TEI ")
    if not data.endswith(b"\n"):
        data += b"\n"
    pfad.write_bytes(data)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--apply", action="store_true",
                   help="Aenderung schreiben (ohne diese Flag nur Bericht)")
    p.add_argument("--dry-run", action="store_true",
                   help="Probelauf, ist ohnehin der Standard (nur zur Deutlichkeit)")
    p.add_argument("--datei", type=Path, default=ZIEL,
                   help=f"TEI-Datei (Standard: {ZIEL.name})")
    args = p.parse_args()

    tree = etree.parse(str(args.datei))
    root = tree.getroot()

    vorher_w = sum(1 for _ in root.iter(W_TAG))
    kandidaten, ablehnungen = sammle_kandidaten(root)

    print(f"Datei:            {args.datei.name}")
    print(f"<w> gesamt:       {vorher_w}")
    print(f"Kandidaten:       {len(kandidaten)}")

    if ablehnungen:
        print()
        print(f"ABBRUCH: {len(ablehnungen)} DIG-Token erfuellen die Bedingungen nicht.")
        for xml_id, grund in ablehnungen[:20]:
            print(f"  {xml_id}: {grund}")
        print()
        print("Diese Faelle sind keine Randziffern oder anders kodiert und muessen")
        print("einzeln angesehen werden. Es wurde nichts geschrieben.")
        return 1

    werte = Counter((w.text or "").strip() for w in kandidaten)
    print(f"verschiedene Ziffern: {len(werte)}")
    print(f"Beispiele:        {', '.join(k for k, _ in werte.most_common(6))}")

    if not args.apply:
        print()
        print("Probelauf, nichts geschrieben. Mit --apply anwenden.")
        return 0

    # Differenziell, nicht absolut: HUG hat einen Vers, der schon im Bestand
    # ohne <w> ist (n=738 enthaelt nur ein <caesura/>). Verboten ist nur, dass
    # die Loeschung einen Vers NEU leert.
    # Die Elemente selbst festhalten, nicht ihre id(): lxml-Proxies werden
    # zwischen Iterationen verworfen und neu erzeugt, id() ist dann ein
    # anderer Wert (siehe docs/DECISIONS.md, Abschnitt zum v4.1.0-Build).
    leer_vorher = [l_el for l_el in root.iter(L_TAG)
                   if not [x for x in l_el.iter(W_TAG)]]

    for w in kandidaten:
        entferne(w)

    nachher_w = sum(1 for _ in root.iter(W_TAG))
    if nachher_w != vorher_w - len(kandidaten):
        print(f"ABBRUCH: <w>-Bilanz stimmt nicht ({vorher_w} - {len(kandidaten)} "
              f"!= {nachher_w}). Nichts geschrieben.")
        return 1

    neu_leer = [l_el.get("n") for l_el in root.iter(L_TAG)
                if not [x for x in l_el.iter(W_TAG)]
                and not any(bekannt is l_el for bekannt in leer_vorher)]
    if neu_leer:
        print(f"ABBRUCH: {len(neu_leer)} Verse wuerden durch die Loeschung "
              f"leer: {neu_leer[:10]}")
        return 1

    if leer_vorher:
        print(f"Hinweis: {len(leer_vorher)} Vers(e) waren schon vorher ohne <w> "
              f"(HUG n=738 traegt nur ein <caesura/>); unveraendert.")

    serialize(tree, args.datei)
    print()
    print(f"{len(kandidaten)} Strophenziffern entfernt, <w> jetzt {nachher_w}.")
    print("Naechste Schritte: variants.xml regenerieren, Indexe + API neu bauen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
