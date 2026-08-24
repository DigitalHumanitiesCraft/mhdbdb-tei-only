#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216 Serie 1: Neu-Annotation der nackten minne-Tokens (korpusweit).

Kontext (Issue #216, Verfahren wie Pilot #189/fix-189-gwtk-rot-junc.py):
6.982 Tokens der Oberflaechenform "minne" ohne @lemmaRef in 262 Texten wurden
kontext-disambiguiert (LLM-Batch nach POS-TAGSET.md §6.3; Provenienz-Log unter
ingest/pos-disambig/216-minne/). Kandidaten: lemma_4130 minne (NOM) und
lemma_4133 minnen (VRB); Personifikation "Frau Minne" als lemma_4130 + pos NAM.

Anwendungsregeln (konservativ, Entscheidungen chsteiner 2026-08-24):

  ANNOTATE nur wenn ALLE drei gelten:
    - confidence == high
    - pos-Verdict != NAM        (NAM-Frage geht komplett ins Review, KZW)
    - kein pos_prior-Konflikt   (326 Tokens tragen @pos aus einer Altannotation
                                 ohne Lemma; weicht das Verdict davon ab -> Review)
  sonst REVIEW: Token bleibt byte-identisch, Fall geht in review-faelle.csv
  (Spalte review_grund: confidence | nam | prior-konflikt).

Beide (Form, Lemma)-Paare haben Bestands-Typen in variants.xml; neue Typen
werden NICHT gepraegt (das Skript bricht ab, falls doch eines fehlt).
Tokens mit pos_prior tragen bereits pos="...", sonst sind sie nackt; in beiden
Faellen aendert sich nur das oeffnende <w>-Tag, Token-Text, Reihenfolge und
xml:id bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4).

@ana (Sense-Referenz) wird bewusst NICHT gesetzt — kuratorisch (wie #189/#198).

Usage:
    python scripts/ingest/pos-disambig/fix-216-minne.py \
        --actions ingest/pos-disambig/216-minne/actions.json \
        --cases ingest/pos-disambig/216-minne/cases.json \
        --out-dir ingest/pos-disambig/216-minne [--apply]

Ohne --apply: Dry-Run (prueft alle Matches, schreibt nur die Review-Artefakte).
Achtung: nicht idempotent — ein Replay setzt den Korpus-Stand VOR dem Batch
voraus (Parent-Commit), weil das Skript verifiziert, dass die Ziel-Tokens
noch unannotiert sind, bevor es schreibt.
"""
import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

VALID_LEMMAS = {
    "lemma_4130": "minne (NOM; Personifikation NAM)",
    "lemma_4133": "minnen (VRB)",
}
VALID_POS = {"NOM", "VRB", "NAM"}

# Bestands-Typen aus authority-files/variants.xml (Stand 2026-08-24) fuer die
# Form "minne" unter beiden Kandidaten-Lemmata. Vollstaendig: neue Typen darf
# dieser Batch nicht praegen.
CORRESP_KNOWN = {
    ("minne", "lemma_4130"): "type_14385",
    ("minne", "lemma_4133"): "type_38651",
}

# xml:id zuerst, dann optional pos="..." (326 Altannotations-Tokens in
# ADP 183, FLG 128, ABG 15), kein weiteres Attribut (gemessen 2026-08-24).
W_TEMPLATE = r'<w xml:id="{xid}"(?: pos="(?P<oldpos>[A-Z]+)")?>(?P<form>[^<]*)</w>'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--actions", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    actions = {a["xml_id"]: a for a in json.load(open(args.actions, encoding="utf-8"))}
    cases = {c["xml_id"]: c for c in json.load(open(args.cases, encoding="utf-8"))}
    if set(actions) != set(cases):
        missing = set(cases) - set(actions)
        extra = set(actions) - set(cases)
        sys.exit(f"FEHLER: Aktionen decken Faelle nicht exakt ab (fehlend: {len(missing)}, fremd: {len(extra)})")

    by_file = {}
    for xid, c in cases.items():
        by_file.setdefault(c["file"], []).append(xid)

    diff_rows = []
    stats = Counter()
    for fname in sorted(by_file):
        fp = TEI_DIR / fname
        # newline="" beim Lesen UND Schreiben: Zeilenenden bleiben byte-identisch
        text = fp.read_text(encoding="utf-8", newline="")
        changed = False
        for xid in by_file[fname]:
            a = actions[xid]
            c = cases[xid]
            if a["lemma"] not in VALID_LEMMAS:
                sys.exit(f"FEHLER: {xid}: unbekanntes Lemma {a['lemma']!r}")
            if a["pos"] not in VALID_POS:
                sys.exit(f"FEHLER: {xid}: unerwarteter pos-Tag {a['pos']!r}")
            m = re.search(W_TEMPLATE.format(xid=re.escape(xid)), text)
            if not m:
                sys.exit(f"FEHLER: {fname}: <w xml:id={xid}> nicht unannotiert gefunden")
            if m.group("form").strip() != c["form"]:
                sys.exit(f"FEHLER: {xid}: Tokentext {m.group('form')!r} != erwartete Form {c['form']!r}")
            if (m.group("oldpos") or "") != c.get("pos_prior", ""):
                sys.exit(f"FEHLER: {xid}: @pos im Bestand {m.group('oldpos')!r} != pos_prior {c.get('pos_prior')!r}")

            prior = c.get("pos_prior", "")
            if a["confidence"] != "high":
                action, grund = "REVIEW", "confidence"
            elif a["pos"] == "NAM" or prior == "NAM":
                action, grund = "REVIEW", "nam"
            elif prior and prior != a["pos"]:
                action, grund = "REVIEW", "prior-konflikt"
            else:
                action, grund = "ANNOTATE", ""
            stats[action] += 1

            new_lemma = new_pos = new_corresp = ""
            if action == "ANNOTATE":
                pair = (c["form"].lower(), a["lemma"])
                if pair not in CORRESP_KNOWN:
                    sys.exit(f"FEHLER: {xid}: kein Bestands-Typ fuer {pair!r}")
                new_lemma = f"lexicon.xml#{a['lemma']}"
                new_pos = a["pos"]
                new_corresp = f"variants.xml#{CORRESP_KNOWN[pair]}"
                new_tag = (
                    f'<w xml:id="{xid}" lemmaRef="{new_lemma}" pos="{new_pos}"'
                    f' corresp="{new_corresp}">{m.group("form")}</w>'
                )
                text = text[:m.start()] + new_tag + text[m.end():]
                changed = True

            diff_rows.append({
                "file": fname, "xml_id": xid, "form": c["form"],
                "vers": c.get("verse_n", ""),
                "action": action, "review_grund": grund,
                "geaendert": "ja" if action == "ANNOTATE" else "nein",
                "alt_pos": prior, "neu_pos": new_pos,
                "alt_lemmaRef": "", "neu_lemmaRef": new_lemma,
                "alt_corresp": "", "neu_corresp": new_corresp,
                "verdict_lemma": a["lemma"], "verdict_pos": a["pos"],
                "confidence": a["confidence"],
                "begruendung": a["begruendung"],
                # Vers-Faelle mit Nachbarversen, damit die CSV ohne Rueckgriff
                # auf das TEI pruefbar ist: mehrere Begruendungen berufen sich
                # auf Material, das im blossen Zielvers nicht steht (Stichproben-
                # Review 2026-08-24, z. B. das 'swer' zu KWL_15004_1).
                "kontext": (
                    " / ".join(x for x in (c.get("prev_verse"), c.get("verse"),
                                           c.get("next_verse")) if x)
                    if c.get("context_mode") == "verse" else c.get("context", "")
                ),
            })
        if changed and args.apply:
            fp.write_text(text, encoding="utf-8", newline="")
            stats["dateien_geaendert"] += 1

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    def write_csv(path, rows):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(diff_rows[0].keys()), delimiter=";")
            writer.writeheader()
            writer.writerows(rows)

    write_csv(out_dir / "diff-liste.csv", diff_rows)
    applied = [r for r in diff_rows if r["action"] == "ANNOTATE"]
    review = [r for r in diff_rows if r["action"] == "REVIEW"]
    write_csv(out_dir / "review-faelle.csv", review)
    rng = random.Random(216)
    write_csv(out_dir / "stichprobe-50.csv", rng.sample(applied, min(50, len(applied))))

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] {len(diff_rows)} Faelle verarbeitet: {dict(stats)}")
    verdicts = Counter(f"{r['verdict_lemma']}/{r['verdict_pos']}" for r in applied)
    print(f"Verdict-Verteilung (nur ANNOTATE): {dict(verdicts)}")
    gruende = Counter(r["review_grund"] for r in review)
    print(f"Review-Gruende (erste zutreffende Regel): {dict(gruende)}")
    # Die Regeln greifen in fester Reihenfolge, deshalb verdeckt 'confidence'
    # die NAM- und Prior-Faelle, die ohnehin nicht high sind. Zweite Sicht auf
    # dieselbe Menge, damit das Review-Paket beziffert werden kann:
    print("Review-Merkmale (Mehrfachnennung moeglich):")
    print(f"  Verdict NAM:      {sum(1 for r in review if r['verdict_pos'] == 'NAM')}")
    print(f"  pos_prior NAM:    {sum(1 for r in review if r['alt_pos'] == 'NAM')}")
    print(f"  confidence < high:{sum(1 for r in review if r['confidence'] != 'high')}")
    print(f"  pos_prior-Konflikt:{sum(1 for r in review if r['alt_pos'] and r['alt_pos'] != r['verdict_pos'])}")
    print(f"Artefakte: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
