#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle-Verdicts zu einer actions.json zusammenfuehren und pruefen.

Zwischen den LLM-Laeufen und dem Schreiben ins Korpus steht genau eine Frage:
deckt das Ergebnis die Faelle exakt ab? In Serie 1 fehlten nach den Wellen
sechs Verdicts und eine xml:id war vertippt; beides faellt hier auf, bevor ein
Anwendungslauf startet.

Geprueft wird:
  - jede xml:id aus cases.json kommt genau einmal vor
  - keine fremde xml:id
  - jedes Verdict traegt lemma, pos und confidence aus den erlaubten Mengen
  - die Form im Verdict stimmt mit der in cases.json ueberein

Die Ausgabe folgt der Reihenfolge von cases.json, nicht der Bundle-Reihenfolge:
actions.json ist damit unabhaengig davon, in welchen Wellen gearbeitet wurde.

Usage:
    python scripts/ingest/pos-disambig/assemble-actions.py \
        --cases ingest/pos-disambig/369-stat/cases.json \
        --verdicts <scratchpad>/369-stat/verdicts \
        --config ingest/pos-disambig/369-stat/config.json \
        --out ingest/pos-disambig/369-stat/actions.json
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CONFIDENCE = {"high", "medium", "low"}


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--erlaube-luecken", action="store_true",
                    help="unvollstaendige Abdeckung nur melden, nicht abbrechen")
    args = ap.parse_args()

    cfg = json.loads(pfad(args.config).read_text(encoding="utf-8"))
    valid_lemmas, valid_pos = set(cfg["lemmas"]), set(cfg["pos"])

    cases = json.loads(pfad(args.cases).read_text(encoding="utf-8"))
    formen = {c["xml_id"]: c["form"] for c in cases}

    gefunden = {}
    doppelt = []
    dateien = sorted(pfad(args.verdicts).glob("verdict-*.json"))
    for f in dateien:
        for e in json.loads(f.read_text(encoding="utf-8")):
            xid = e.get("xml_id")
            if xid in gefunden:
                doppelt.append((xid, f.name))
            gefunden[xid] = e

    fehlend = [x for x in formen if x not in gefunden]
    fremd = [x for x in gefunden if x not in formen]
    fehler = []
    for xid, e in gefunden.items():
        if xid in fremd:
            continue
        if e.get("lemma") not in valid_lemmas:
            fehler.append("%s: Lemma %r" % (xid, e.get("lemma")))
        if e.get("pos") not in valid_pos:
            fehler.append("%s: pos %r" % (xid, e.get("pos")))
        if e.get("confidence") not in CONFIDENCE:
            fehler.append("%s: confidence %r" % (xid, e.get("confidence")))
        if e.get("form") and e["form"] != formen[xid]:
            fehler.append("%s: Form %r != %r" % (xid, e.get("form"), formen[xid]))

    print("Bundle-Dateien:", len(dateien))
    print("Faelle laut cases.json:", len(formen), "| Verdicts gefunden:", len(gefunden))
    print("  fehlend:", len(fehlend), "| fremd:", len(fremd), "| doppelt:", len(doppelt))
    for x in fehlend[:10]:
        print("     fehlend:", x)
    for x in fremd[:10]:
        print("     fremd:", x)
    for x, d in doppelt[:10]:
        print("     doppelt:", x, "in", d)
    print("  Formfehler und ungueltige Werte:", len(fehler))
    for x in fehler[:10]:
        print("    ", x)

    if fehler or fremd or doppelt:
        sys.exit("ABBRUCH: Verdicts sind nicht sauber.")
    if fehlend and not args.erlaube_luecken:
        sys.exit("ABBRUCH: %d Faelle ohne Verdict (--erlaube-luecken zum Fortfahren)."
                 % len(fehlend))

    aus = [gefunden[c["xml_id"]] for c in cases if c["xml_id"] in gefunden]
    pfad(args.out).write_text(json.dumps(aus, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8", newline="")
    print()
    print("Verdicts:", dict(Counter(e["lemma"] + "/" + e["pos"] for e in aus)))
    print("Konfidenz:", dict(Counter(e["confidence"] for e in aus)))
    print("geschrieben:", pfad(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
