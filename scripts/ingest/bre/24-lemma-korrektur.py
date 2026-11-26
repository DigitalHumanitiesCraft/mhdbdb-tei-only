#!/usr/bin/env python3
"""24-lemma-korrektur.py: bestaetigte Lemma-Korrekturen in die Zeugen uebernehmen (BRE, #147).

Liest ingest/bre/pruefung/lemma-korrekturen.tsv (je xml_id eine Zeile: alt, neu) und ersetzt in
ingest/bre/BRE_*.tei.xml das @lemmaRef von alt auf neu. Anders als 13-lemma-apply.py ueberschreibt
dieses Skript bewusst ein vorhandenes @lemmaRef, aber nur, wenn es genau dem Altwert der Zeile
entspricht (sonst harter Fehler) und das neue Lemma in lexicon.xml steht.

@pos, @ana und @corresp des Tokens haengen am alten Lemma und werden entfernt; die Tokens muessen
danach durch Phase 2 und 3 (und 18-corresp.py) neu laufen. Die Liste steht auf der Konsole mit
der Zahl je Attribut. Dasselbe Skript zweimal gestartet: harter Fehler beim zweiten Lauf (alt steht
nicht mehr da), damit nichts doppelt wirkt.

Aufruf: python -P -E scripts/ingest/bre/24-lemma-korrektur.py [--trocken]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

TSV = bc.REPO / "ingest" / "bre" / "pruefung" / "lemma-korrekturen.tsv"
FELDER = ["xml_id", "wort", "zeuge", "nr", "alt", "neu", "neu_form", "quelle", "notiz"]
ABHAENGIG = ("pos", "ana", "corresp")


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    zeilen = ba.lies_tsv(TSV, FELDER)
    ziel = {}
    for z in zeilen:
        if z["xml_id"] in ziel:
            raise bc.HarterFehler(f"{z['xml_id']} doppelt in {TSV.name}")
        if z["alt"] == z["neu"]:
            raise bc.HarterFehler(f"{z['xml_id']}: alt gleich neu")
        ziel[z["xml_id"]] = z
    lexikon = set(ba.lade_lexikon())
    for z in zeilen:
        if z["neu"] not in lexikon:
            raise bc.HarterFehler(f"{z['xml_id']}: {z['neu']} fehlt in lexicon.xml")
    gefunden = set()
    entfernt = collections.Counter()
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        geaendert = False
        for w in baum.getroot().iter(ba.T + "w"):
            z = ziel.get(w.get(ba.XML_ID))
            if z is None:
                continue
            if w.get("lemmaRef") != f"lexicon.xml#{z['alt']}":
                raise bc.HarterFehler(f"{z['xml_id']}: @lemmaRef ist {w.get('lemmaRef')}, erwartet lexicon.xml#{z['alt']}")
            w.set("lemmaRef", f"lexicon.xml#{z['neu']}")
            for att in ABHAENGIG:
                if att in w.attrib:
                    del w.attrib[att]
                    entfernt[att] += 1
            gefunden.add(z["xml_id"])
            geaendert = True
        if geaendert and not a.trocken:
            ba.schreibe(baum, pfad)
    fehlt = set(ziel) - gefunden
    if fehlt:
        raise bc.HarterFehler(f"{len(fehlt)} xml_id nicht in den Zeugen, z.B. {sorted(fehlt)[:3]}")
    print(f"Korrekturen: {len(zeilen)} Tokens, @lemmaRef ersetzt: {len(gefunden)}")
    print("entfernt (haengt am alten Lemma): " + ", ".join(f"@{k} {entfernt[k]}" for k in ABHAENGIG))
    print("(trocken: nichts geschrieben)" if a.trocken else "Zeugen geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
