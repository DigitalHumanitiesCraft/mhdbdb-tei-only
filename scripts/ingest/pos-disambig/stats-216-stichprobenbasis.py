#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216: Grundgesamtheit der schweren Stichprobe, und die Stichprobe selbst.

Die Zahlen im Provenienz-Log ("2.041 ohne stuetzenden Vorgaenger", und die
Aufgliederung dieser Menge) standen zunaechst ohne Zaehlvorschrift im Text.
Hier ist sie, ausfuehrbar.

Vorschrift: gestuetzt ist ein Fall, wenn das unmittelbar vorangehende <w> ein
@pos aus MARKER_TAGS traegt (Determinierer, Artikel, Praeposition, Possessiv,
Pronomen, Adjektiv, Gradpartikel). Mehrdeutige Tags zaehlen als Marker, sobald
eines davon enthalten ist. Der erste Anlauf filterte statt dessen ueber eine
Wortliste und war unwirksam, weil er die mhd. Schreibvielfalt verfehlte
(di, dîn, sîner, dorch, grozzer): das ist der Grund fuer dieses Skript.

Tokens, die dieser Batch selbst annotiert hat, zaehlen als unannotiert. Die
Frage gilt dem Korpusstand VOR dem Batch, und nur so misst das Skript nach dem
Apply noch dasselbe.

Usage:
    python scripts/ingest/pos-disambig/stats-216-stichprobenbasis.py \
        --diff-liste ingest/pos-disambig/216-minne/diff-liste.csv [--stichprobe]

--stichprobe schreibt stichprobe-schwer-50.csv neu (Seed 21602, 20 VRB und
30 NOM: Verben sind uebergewichtet, weil Imperativ und Konjunktiv ohne overtes
Subjekt dort das Risiko sind).
"""
import argparse
import csv
import random
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

MARKER_TAGS = {"DET", "ART", "PRP", "POS", "PRO", "ADJ", "GRA"}
SEED = 21602


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff-liste", required=True)
    ap.add_argument("--stichprobe", action="store_true")
    args = ap.parse_args()

    with open(REPO / args.diff_liste, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        spalten = reader.fieldnames
        zeilen = [r for r in reader if r["action"] == "ANNOTATE"]

    annotiert = {r["xml_id"] for r in zeilen}
    je_datei = {}
    for r in zeilen:
        je_datei.setdefault(r["file"], set()).add(r["xml_id"])

    # Vorgaenger und Vorvorgaenger jedes Ziel-Tokens einsammeln
    umfeld = {}
    for fname, ids in sorted(je_datei.items()):
        ws = list(etree.parse(str(REPO / "tei" / fname)).iter(W_TAG))
        for i, w in enumerate(ws):
            if w.get(XML_ID) not in ids:
                continue
            def tags(j):
                if j < 0:
                    return None
                if ws[j].get(XML_ID) in annotiert:
                    return set()
                return set((ws[j].get("pos") or "").split())
            umfeld[w.get(XML_ID)] = (
                norm("".join(ws[i - 1].itertext())) if i > 0 else "",
                tags(i - 1), tags(i - 2))

    schwer = []
    stat = Counter()
    for r in zeilen:
        text, vor1, vor2 = umfeld.get(r["xml_id"], ("", None, None))
        if vor1 and vor1 & MARKER_TAGS:
            stat["gestuetzt"] += 1
            continue
        stat["ohne_stuetze"] += 1
        stat["ohne_stuetze:vorgaenger_ohne_pos" if not vor1
             else "ohne_stuetze:vorgaenger_anderes_pos"] += 1
        stat["distanz2_marker" if (vor2 and vor2 & MARKER_TAGS)
             else "distanz2_ohne"] += 1
        r = dict(r)
        r["vorgaenger"] = text
        r["vorgaenger_pos"] = " ".join(sorted(vor1)) if vor1 else "(ohne)"
        schwer.append(r)

    print("ANNOTATE gesamt:", len(zeilen))
    print("  mit stuetzendem Vorgaenger (@pos in %s): %5d"
          % ("/".join(sorted(MARKER_TAGS)), stat["gestuetzt"]))
    print("  ohne stuetzenden Vorgaenger:             %5d" % stat["ohne_stuetze"])
    print("     davon Vorgaenger ganz ohne @pos:      %5d"
          % stat["ohne_stuetze:vorgaenger_ohne_pos"])
    print("     davon Vorgaenger mit anderem @pos:    %5d"
          % stat["ohne_stuetze:vorgaenger_anderes_pos"])
    print("     davon mit Marker auf Distanz 2:       %5d" % stat["distanz2_marker"])
    print("     davon auch dort ohne Marker:          %5d" % stat["distanz2_ohne"])
    print("  Verdict-Verteilung der schweren Faelle:",
          dict(Counter(r["verdict_pos"] for r in schwer)))

    if args.stichprobe:
        rng = random.Random(SEED)
        vrb = [r for r in schwer if r["verdict_pos"] == "VRB"]
        nom = [r for r in schwer if r["verdict_pos"] == "NOM"]
        probe = rng.sample(vrb, min(20, len(vrb))) + rng.sample(nom, min(30, len(nom)))
        rng.shuffle(probe)
        ziel = REPO / "ingest/pos-disambig/216-minne/stichprobe-schwer-50.csv"
        with open(ziel, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=spalten + ["vorgaenger", "vorgaenger_pos"],
                               delimiter=";")
            w.writeheader()
            w.writerows(probe)
        print("geschrieben:", ziel, "|", dict(Counter(r["verdict_pos"] for r in probe)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
