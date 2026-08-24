#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stichproben fuer die Durchsicht einer Homographie-Serie ziehen (POS-TAGSET §6.3).

Gate 3 verlangt 50 zufaellige Faelle je Batch. Eine reine Zufallsstichprobe
misst aber vor allem den leichten Fall: wo ein Artikel oder eine Praeposition
unmittelbar vor dem Token steht, ist die Wortart schon syntaktisch entschieden.
Serie 1 (#216) hat das gezeigt, dort trafen 45 von 50 Zufallsfaellen auf eine
solche Konstellation. Deshalb werden hier zwei Stichproben gezogen:

  stichprobe-50.csv         50 zufaellige ANNOTATE-Faelle (Gate 3 woertlich)
  stichprobe-schwer-50.csv  50 zufaellige ANNOTATE-Faelle, bei denen das
                            unmittelbar vorangehende <w> KEIN Marker-Tag
                            traegt, die Entscheidung also aus Syntax und
                            Semantik kommen musste

Marker-Tags sind die Wortarten, die ein folgendes Substantiv bereits selbst
anzeigen (Determinativ, Praeposition, Possessiv, Attribut). Die Liste steht als
MARKER_TAGS im Code und ist Teil der Zaehlvorschrift: wer die Zahl nachrechnen
will, muss sie kennen.

Der Seed haengt an der Ticketnummer, damit derselbe Aufruf dieselbe Stichprobe
zieht. Achtung: die Stichprobe ist nur so stabil wie die Grundgesamtheit. Wird
die diff-liste neu erzeugt und faellt dabei ein Fall weg oder kommt einer dazu,
verschiebt sich die Auswahl.

Usage:
    python scripts/ingest/pos-disambig/stichproben-homograph.py \
        --diff-liste ingest/pos-disambig/369-stat/diff-liste.csv \
        --out-dir ingest/pos-disambig/369-stat --seed 369
"""
import argparse
import csv
import random
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

# Wortarten, die ein folgendes Substantiv selbst anzeigen. ART und GRA sind
# Altbestand (POS-TAGSET §5), stehen aber noch im Korpus und zaehlen mit.
MARKER_TAGS = {"DET", "ART", "PRP", "POS", "PRO", "ADJ", "GRA"}


def ist_marker(pos_wert):
    """Traegt das Token eine Wortart, die ein folgendes Substantiv anzeigt?

    Geprueft wird je Tag, nicht am ganzen Attributwert: das Korpus fuehrt
    Mehrfachtags als whitespace-getrennte Liste ('ART NUM', 'ADJ ADV'), und ein
    Vergleich des vollen Werts gegen die Menge wuerde genau die Faelle als
    schwer zaehlen, in denen der Artikel danebensteht.
    """
    return any(t in MARKER_TAGS for t in pos_wert.split())

W_RE = re.compile(r'<w\b[^>]*>')
XMLID_RE = re.compile(r'xml:id="([^"]+)"')
POS_RE = re.compile(r'\bpos="([^"]+)"')


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def vorgaenger_pos(text, ziel_ids):
    """Zu jeder xml:id das @pos des unmittelbar vorangehenden <w> im Dokument."""
    aus = {}
    vorher = None
    for m in W_RE.finditer(text):
        tag = m.group(0)
        mid = XMLID_RE.search(tag)
        if not mid:
            vorher = tag
            continue
        if mid.group(1) in ziel_ids:
            mp = POS_RE.search(vorher) if vorher else None
            aus[mid.group(1)] = mp.group(1) if mp else ""
        vorher = tag
    return aus


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff-liste", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=50)
    args = ap.parse_args()

    with open(pfad(args.diff_liste), encoding="utf-8-sig", newline="") as f:
        zeilen = [r for r in csv.DictReader(f, delimiter=";")
                  if r["action"] == "ANNOTATE"]
    if not zeilen:
        sys.exit("FEHLER: keine ANNOTATE-Faelle in der diff-liste")

    je_datei = {}
    for z in zeilen:
        je_datei.setdefault(z["file"], set()).add(z["xml_id"])

    vor = {}
    for fname, ids in sorted(je_datei.items()):
        text = (TEI_DIR / fname).read_text(encoding="utf-8", newline="")
        vor.update(vorgaenger_pos(text, ids))

    fehlend = [z["xml_id"] for z in zeilen if z["xml_id"] not in vor]
    if fehlend:
        sys.exit("FEHLER: %d Faelle im TEI nicht gefunden (erster: %s)"
                 % (len(fehlend), fehlend[0]))

    for z in zeilen:
        z["vorgaenger_pos"] = vor[z["xml_id"]]
        z["schwer"] = "nein" if ist_marker(vor[z["xml_id"]]) else "ja"

    schwer = [z for z in zeilen if z["schwer"] == "ja"]
    print("ANNOTATE-Faelle:", len(zeilen), "| davon schwer:", len(schwer),
          "(%.1f %%)" % (len(schwer) / len(zeilen) * 100))
    print("Vorgaenger-Tags:",
          dict(Counter(z["vorgaenger_pos"] or "(ohne)" for z in zeilen)
               .most_common(10)))

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spalten = list(zeilen[0].keys()) + ["pruefung", "anmerkung"]
    for name, grund, s in (("stichprobe-%d.csv" % args.n, zeilen, args.seed),
                           ("stichprobe-schwer-%d.csv" % args.n, schwer,
                            args.seed + 1)):
        n = min(args.n, len(grund))
        auswahl = random.Random(s).sample(sorted(grund,
                                                 key=lambda z: z["xml_id"]), n)
        # Sortiert schreiben, damit die Datei unabhaengig von der Reihenfolge
        # der Ziehung byte-identisch reproduzierbar ist.
        auswahl.sort(key=lambda z: z["xml_id"])
        with open(out / name, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=spalten, delimiter=";")
            w.writeheader()
            for z in auswahl:
                w.writerow(dict(z, pruefung="", anmerkung=""))
        print("geschrieben:", out / name, "(%d Faelle)" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
