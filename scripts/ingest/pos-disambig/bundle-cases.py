#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Faelle aus cases.json in Bundles fuer die LLM-Laeufe zerlegen.

POS-TAGSET §6.3 begrenzt, wie viel ein Lauf sehen darf. Ein Bundle ist die
Arbeitseinheit eines Agenten: klein genug, dass jeder Fall einzeln beurteilt
wird, gross genug, dass der Overhead nicht ueberwiegt. Serie 1 (#216) lief mit
60 Faellen je Bundle durch 118 Bundles.

Die Zerlegung folgt der Reihenfolge in cases.json (corpus_files-Reihenfolge,
Dokumentordnung) und ist damit deterministisch: derselbe Korpusstand ergibt
dieselben Bundles. Die Bundles gehoeren NICHT ins Repository, sie sind
Zwischenmaterial; im Repository stehen cases.json (Eingang) und actions.json
(Ausgang), aus denen sie sich jederzeit neu erzeugen lassen.

Usage:
    python scripts/ingest/pos-disambig/bundle-cases.py \
        --cases ingest/pos-disambig/369-stat/cases.json \
        --out-dir <scratchpad>/369-stat/bundles [--size 60]
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--size", type=int, default=60)
    args = ap.parse_args()

    pfad = Path(args.cases)
    if not pfad.is_absolute():
        pfad = REPO / pfad
    cases = json.loads(pfad.read_text(encoding="utf-8"))

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(0, len(cases), args.size):
        teil = cases[i:i + args.size]
        ziel = out / ("bundle-%03d.json" % n)
        ziel.write_text(json.dumps(teil, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
        n += 1

    print("Faelle:", len(cases), "| Bundles:", n, "| je", args.size)
    print("Ordner:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
