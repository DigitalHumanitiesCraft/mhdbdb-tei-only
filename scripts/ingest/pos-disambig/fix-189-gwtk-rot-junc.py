#!/usr/bin/env python3
"""#189: GWTK-Pilot — Neu-Annotation der nackten rot/jung-Tokens.

Kontext (Issue #189): In GWTK tragen 278 Tokens der homographie-ambigen
Oberflaechenformen rott/rotten/rotte/roten (139) und jungen/junger (139)
weder @lemmaRef noch @pos — sie wurden bei der Alt-MHDBDB-Annotation nie
disambiguiert. Alle 278 Faelle wurden kontext-disambiguiert (LLM-Batch nach
POS-TAGSET.md §6.3; Provenienz-Log unter ingest/pos-disambig/189-gwtk-rot-junc/).

Anders als beim Schwester-Batch #198 (fix-198-habe-nom.py: Umhaengen bereits
annotierter Tokens) ist dies eine NEU-Annotation nackter Tokens
(<w xml:id="...">form</w>). Die Aktionsdatei traegt pro Token lemma + pos +
confidence; angewendet wird konservativ:

  confidence=high            -> ANNOTATE: lemmaRef + pos + corresp einfuegen
  confidence=medium|low      -> REVIEW: Token bleibt byte-identisch,
                                Fall geht an das menschliche Review

@ana (Sense-Referenz) wird bewusst NICHT gesetzt — die Sense-Zuordnung ist
kuratorisch (gleiche Regel wie bei den #198-MOVEs). @corresp zeigt auf den
variants-Typ der Form unter dem Ziel-Lemma; fuer (Form, Lemma)-Paare ohne
Bestands-Typ praegt das Skript deterministisch neue IDs ab NEXT_TYPE_ID
(fortlaufend, sortiert nach Lemma-Nummer und Form). Die Typen materialisieren
sich beim anschliessenden variants.xml-Rebuild (scripts/sync/extract-variants.py
liest sie aus den Token-@corresp — der Korpus fuehrt).

Nur das oeffnende <w>-Tag aendert sich; Token-Text, Reihenfolge und xml:id
bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4).

Usage:
    python scripts/ingest/pos-disambig/fix-189-gwtk-rot-junc.py \
        --actions ingest/pos-disambig/189-gwtk-rot-junc/actions.json \
        --cases ingest/pos-disambig/189-gwtk-rot-junc/cases.json \
        --out-dir ingest/pos-disambig/189-gwtk-rot-junc [--apply]

Ohne --apply: Dry-Run (prueft alle Matches, schreibt nur die Review-Artefakte).
Achtung: nicht idempotent — ein Replay setzt den Korpus-Stand VOR dem Batch
voraus (Parent-Commit), weil das Skript verifiziert, dass die Ziel-Tokens
noch nackt sind, bevor es schreibt.
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
    "lemma_4954": "rôt (ADJ, Farbe)",
    "lemma_4978": "rote (NOM Schar / VRB sich rotten)",
    "lemma_10840": "roete (NOM Roete)",
    "lemma_11330": "Rot (NAM)",
    "lemma_3157": "junc (ADJ; substantiviert NOM)",
    "lemma_3162": "jungen (VRB verjuengen)",
    "lemma_3163": "jünger (NOM discipulus)",
}
VALID_POS = {"ADJ", "NOM", "VRB", "NAM"}

# Bestands-Typen aus authority-files/variants.xml (Stand 2026-07-12) fuer die
# (form.lower(), lemma)-Paare der Zielformen. Fehlende Paare werden ab
# NEXT_TYPE_ID neu gepraegt.
CORRESP_KNOWN = {
    ("rott", "lemma_4954"): "type_194575",
    ("rott", "lemma_4978"): "type_75564",
    ("rott", "lemma_10840"): "type_264305",
    ("rotten", "lemma_4978"): "type_17204",
    ("rotte", "lemma_4978"): "type_17203",
    ("roten", "lemma_4954"): "type_80222",
    ("roten", "lemma_4978"): "type_17202",
    ("roten", "lemma_11330"): "type_40920",
    ("jungen", "lemma_3157"): "type_10830",
    ("jungen", "lemma_3162"): "type_77810",
    ("junger", "lemma_3157"): "type_10831",
    ("junger", "lemma_3163"): "type_10867",
}
# Hoechste vergebene type-Nummer in variants.xml (== Korpus-Maximum, da nach
# #115 alle Korpus-@corresp-Typen aufloesen): naechste freie ID.
NEXT_TYPE_ID = 372361

BARE_W_TEMPLATE = r'<w xml:id="{xid}">(?P<form>[^<]*)</w>'


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

    # Neue variants-Typen deterministisch praegen: alle high-Faelle ohne
    # Bestands-Typ, sortiert nach (Lemma-Nummer, Form), fortlaufend ab NEXT_TYPE_ID.
    new_pairs = sorted({
        (cases[xid]["form"].lower(), a["lemma"])
        for xid, a in actions.items()
        if a["confidence"] == "high"
        and (cases[xid]["form"].lower(), a["lemma"]) not in CORRESP_KNOWN
    }, key=lambda p: (int(p[1].split("_")[1]), p[0]))
    corresp_map = dict(CORRESP_KNOWN)
    for offset, pair in enumerate(new_pairs):
        corresp_map[pair] = f"type_{NEXT_TYPE_ID + offset}"

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
            m = re.search(BARE_W_TEMPLATE.format(xid=re.escape(xid)), text)
            if not m:
                sys.exit(f"FEHLER: {fname}: <w xml:id={xid}> nicht als nacktes Token gefunden")
            if m.group("form").strip() != c["form"]:
                sys.exit(f"FEHLER: {xid}: Tokentext {m.group('form')!r} != erwartete Form {c['form']!r}")

            annotate = a["confidence"] == "high"
            action = "ANNOTATE" if annotate else "REVIEW"
            stats[action] += 1
            new_lemma = new_pos = new_corresp = ""
            if annotate:
                new_lemma = f"lexicon.xml#{a['lemma']}"
                new_pos = a["pos"]
                new_corresp = f"variants.xml#{corresp_map[(c['form'].lower(), a['lemma'])]}"
                new_tag = (
                    f'<w xml:id="{xid}" lemmaRef="{new_lemma}" pos="{new_pos}"'
                    f' corresp="{new_corresp}">{m.group("form")}</w>'
                )
                text = text[:m.start()] + new_tag + text[m.end():]
                changed = True

            diff_rows.append({
                "file": fname, "xml_id": xid, "form": c["form"], "vers": c["verse_n"],
                "action": action, "geaendert": "ja" if annotate else "nein",
                "alt_pos": "", "neu_pos": new_pos,
                "alt_lemmaRef": "", "neu_lemmaRef": new_lemma,
                "alt_corresp": "", "neu_corresp": new_corresp,
                "verdict_lemma": a["lemma"], "verdict_pos": a["pos"],
                "confidence": a["confidence"],
                "begruendung": a["begruendung"],
                "kontext": c["verse"],
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
    rng = random.Random(189)
    write_csv(out_dir / "stichprobe-50.csv", rng.sample(applied, min(50, len(applied))))

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] {len(diff_rows)} Faelle verarbeitet: {dict(stats)}")
    verdicts = Counter(f"{r['verdict_lemma']}/{r['verdict_pos']}" for r in applied)
    print(f"Verdict-Verteilung (nur ANNOTATE): {dict(verdicts)}")
    if new_pairs:
        print("Neu gepraegte variants-Typen:")
        for pair in new_pairs:
            print(f"  {corresp_map[pair]} = Form {pair[0]!r} unter {pair[1]} ({VALID_LEMMAS[pair[1]]})")
    print(f"Artefakte: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
