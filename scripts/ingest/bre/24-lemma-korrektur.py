#!/usr/bin/env python3
"""24-lemma-korrektur.py: bestaetigte Lemma-Korrekturen in die Zeugen uebernehmen (BRE, #147).

Liest ingest/bre/pruefung/lemma-korrekturen.tsv (je xml_id eine Zeile: alt, neu) und ersetzt in
ingest/bre/BRE_*.tei.xml das @lemmaRef von alt auf neu. Anders als 13-lemma-apply.py ueberschreibt
dieses Skript bewusst ein vorhandenes @lemmaRef, aber nur, wenn es genau dem Altwert der Zeile
entspricht (sonst harter Fehler) und das neue Lemma in lexicon.xml steht.

@pos, @ana und @corresp des Tokens haengen am alten Lemma und werden entfernt. Ebenso die Zeilen
dieser xml_id in phase2/pos-patch.tsv und phase3/sense-patch.tsv: beide sind nur nach xml_id
geschluesselt, und 15-apply.py wuerde sie sonst nach dem Neulauf auf das neue Lemma anwenden
(abstain ohne Pruefung, ein Wert, wenn er unter den neuen Kandidaten steht). phase1/lemma-patch.tsv
bleibt unberuehrt: Phase 1 laeuft in der Wiederaufbau-Reihenfolge vor diesem Skript und setzt das
Altlemma, das hier geprueft und ersetzt wird.

Die Tokens muessen danach durch 14, 15 --phase pos, 16, 15 --phase sense und 18-corresp.py neu
laufen. Dasselbe Skript zweimal gestartet: harter Fehler beim zweiten Lauf (alt steht nicht mehr
da), damit nichts doppelt wirkt.

Aufruf: python -P -E scripts/ingest/bre/24-lemma-korrektur.py [--trocken] [--patches-behalten]

--patches-behalten gehoert in jeden Wiederaufbau nach dem ersten Lauf: sobald Phase 2 und 3 neu gelaufen sind,
stehen in den Patch-Tabellen Zeilen zum NEUEN Lemma, die nicht geloescht werden duerfen.
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
PATCHES = (ba.PHASE2 / "pos-patch.tsv", ba.PHASE3 / "sense-patch.tsv")
PATCH_FELDER = ["xml_id", "form", "resolved", "decision_type", "confidence", "reviewer", "begruendung",
                "quelle"]  # wie 12-entscheidungen.py


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    ap.add_argument("--patches-behalten", action="store_true",
                    help="Wiederaufbau nach neu gelaufener Phase 2 und 3: die Patch-Tabellen enthalten dann Zeilen "
                         "zum neuen Lemma und bleiben unberuehrt (nur TEI)")
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
    # Patch-Dateien vor dem ersten Schreiben lesen: fehlt eine oder stimmt der Kopf nicht, bricht das Skript
    # ab, bevor etwas geschrieben ist (sonst stuende die TEI korrigiert neben alten Patch-Zeilen)
    patches = {pfad: ba.lies_tsv(pfad, PATCH_FELDER) for pfad in PATCHES}
    baeume = []  # erst alles pruefen, dann schreiben: ein harter Fehler laesst nichts halb geschrieben zurueck
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
        if geaendert:
            baeume.append((baum, pfad))
    fehlt = set(ziel) - gefunden
    if fehlt:
        raise bc.HarterFehler(f"{len(fehlt)} xml_id nicht in den Zeugen, z.B. {sorted(fehlt)[:3]}")
    for pfad, alle in patches.items():
        rest = alle if a.patches_behalten else [z for z in alle if z["xml_id"] not in ziel]
        entfernt[pfad.name] = len(alle) - len(rest)
        if not a.trocken:
            ba.schreibe_tsv(pfad, PATCH_FELDER, rest)
    if not a.trocken:
        for baum, pfad in baeume:
            ba.schreibe(baum, pfad)
    print(f"Korrekturen: {len(zeilen)} Tokens, @lemmaRef ersetzt: {len(gefunden)}")
    print("entfernt (haengt am alten Lemma): " + ", ".join(f"@{k} {entfernt[k]}" for k in ABHAENGIG))
    print("Patch-Zeilen entfernt: " + ", ".join(f"{p.name} {entfernt[p.name]}" for p in PATCHES))
    print("(trocken: nichts geschrieben)" if a.trocken else "Zeugen und Patch-TSV geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
