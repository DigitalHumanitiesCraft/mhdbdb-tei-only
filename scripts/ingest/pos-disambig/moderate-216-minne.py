#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216: dokumentierter Moderations-Pass auf actions.json.

Nach dem Muster des Piloten #189 (dort wurden 4 Instrumenten-Faelle nach
Lexikon-Pruefung von low auf high gehoben) haelt dieses Skript die
Hand-Eingriffe fest, statt actions.json still zu editieren. Jeder Eintrag
nennt Fall, Richtung und Grund; das Skript ist idempotent und meldet, wenn
ein Eingriff bereits angewendet ist.

Eingriffe dieses Batches (alle in Richtung VORSICHT, keiner hebt an):

1. GWTK_125210733600_0: 'ir soelten bilich schowen / minne junckfrowen, /
   due edel ist und da by guett'. Das Relativpronomen im Folgevers steht im
   Singular, die Lesart ist also 'mîne juncfrouwen' (Possessiv), nicht
   'Minne-Jungfrauen'. GWTK schreibt das Possessiv sonst 'mine' (113x),
   'minne' kommt dort nur 22x vor; sechs weitere GWTK-Faelle hatte bereits
   die Disambiguierung selbst als Possessiv-Verdacht auf low gesetzt.
   high -> low, damit der Fall ins menschliche Review geht.

Usage:
    python scripts/ingest/pos-disambig/moderate-216-minne.py \
        --actions ingest/pos-disambig/216-minne/actions.json [--apply]
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# xml_id -> (erwartete alte confidence, neue confidence, Zusatz zur Begruendung)
EINGRIFFE = {
    "GWTK_125210733600_0": (
        "high", "low",
        " [Moderation 2026-08-24: Folgevers 'due edel ist' im Singular,"
        " daher wohl Possessiv 'mîne juncfrouwen'; zurueckgehalten.]",
    ),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--actions", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    path = REPO / args.actions
    actions = json.loads(path.read_text(encoding="utf-8"))
    by_id = {a["xml_id"]: a for a in actions}

    geaendert = 0
    for xid, (alt, neu, zusatz) in EINGRIFFE.items():
        a = by_id.get(xid)
        if a is None:
            sys.exit(f"FEHLER: {xid} steht nicht in {args.actions}")
        if a["confidence"] == neu and zusatz in a["begruendung"]:
            print(f"  {xid}: bereits angewendet ({neu})")
            continue
        if a["confidence"] != alt:
            sys.exit(f"FEHLER: {xid}: confidence ist {a['confidence']!r},"
                     f" erwartet {alt!r} — Eingriff passt nicht zum Stand")
        a["confidence"] = neu
        a["begruendung"] = a["begruendung"] + zusatz
        geaendert += 1
        print(f"  {xid}: {alt} -> {neu}")

    print(f"Eingriffe: {len(EINGRIFFE)}, davon anzuwenden: {geaendert}")
    if args.apply and geaendert:
        path.write_text(json.dumps(actions, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8", newline="")
        print(f"geschrieben: {path}")
    elif not args.apply:
        print("(Dry-Run, --apply zum Schreiben)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
