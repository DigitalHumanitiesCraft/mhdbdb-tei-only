#!/usr/bin/env python3
"""#198: haben (NOM) — Batch-Korrektur der ambigen habe/hab/hawe-Tokens unter lemma_2598.

Kontext (Issue #198, Scoping-Kommentar 2026-07-10): lemma_2598 *haben* vermengt
Verb- und Nomen-Belege. Alle 714 habe/hab/hawe-Tokens unter lemma_2598 wurden
kontext-disambiguiert (LLM-Batch nach POS-TAGSET.md §6.3; Provenienz-Log unter
ingest/pos-disambig/198-habe-nom/). Die Aktionsdatei traegt pro Token eine von
vier Entscheidungen:

  MOVE   -> Substantiv *habe* (Besitz): lemmaRef="lexicon.xml#lemma_2593",
            pos="NOM", @ana entfaellt (Sense-Zuordnung folgt in Schritt 2 des
            Issue-Plans beim KZW-Sense-Review; Alt-Wert steht in der Diff-Liste),
            @corresp auf den variants-Typ der Form unter lemma_2593
            (habe->type_8699, hab->type_80494).
  STRIP  -> verbal (Konjunktiv/Indikativ/Imperativ/Hilfsverb): NOM wird aus dem
            Compound-@pos gestrichen; lemmaRef/ana/corresp unveraendert.
  REVIEW -> Aenderung zurueckgehalten (houwe-Verdacht oder Konfidenz < high);
            Token bleibt byte-identisch, Fall geht an das menschliche Review.
  KEEP   -> verbal ohne NOM im @pos: nichts zu tun.

Nur @lemmaRef/@pos/@ana/@corresp aendern sich; Token-Text, Reihenfolge und
xml:id bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4).

Usage:
    python scripts/fix-198-habe-nom.py --actions <actions.json> --cases <cases.json> \
        --out-dir ingest/pos-disambig/198-habe-nom [--apply]

Ohne --apply: Dry-Run (prueft alle Matches, schreibt nur die Diff-Liste).
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEI_DIR = REPO / "tei"

TARGET_LEMMA_OLD = "lexicon.xml#lemma_2598"
TARGET_LEMMA_NEW = "lexicon.xml#lemma_2593"
# Bestehende variants-Typen der Zielformen unter lemma_2593 (Korpus-Belege, #198)
CORRESP_NEW = {
    "habe": "variants.xml#type_8699",
    "hab": "variants.xml#type_80494",
}

W_RE_TEMPLATE = (
    r'<w xml:id="{xid}" lemmaRef="(?P<lemmaRef>[^"]*)" pos="(?P<pos>[^"]*)"'
    r'(?: ana="(?P<ana>[^"]*)")?(?: corresp="(?P<corresp>[^"]*)")?>'
)


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
        # newline="" beim Lesen UND Schreiben: Zeilenenden (LF/CRLF gemischt im
        # Korpus, z. B. WZB=CRLF) bleiben byte-identisch erhalten
        text = fp.read_text(encoding="utf-8", newline="")
        changed = False
        for xid in by_file[fname]:
            a = actions[xid]
            c = cases[xid]
            m = re.search(W_RE_TEMPLATE.format(xid=re.escape(xid)), text)
            if not m:
                sys.exit(f"FEHLER: {fname}: <w xml:id={xid}> nicht im erwarteten Attributmuster gefunden")
            old_lemma, old_pos = m.group("lemmaRef"), m.group("pos")
            old_ana, old_corresp = m.group("ana"), m.group("corresp")
            if old_lemma != TARGET_LEMMA_OLD:
                sys.exit(f"FEHLER: {xid}: lemmaRef ist {old_lemma}, erwartet {TARGET_LEMMA_OLD}")

            new_lemma, new_pos, new_ana, new_corresp = old_lemma, old_pos, old_ana, old_corresp
            if a["action"] == "MOVE":
                new_lemma, new_pos, new_ana = TARGET_LEMMA_NEW, "NOM", None
                new_corresp = CORRESP_NEW[c["form"].lower()]
            elif a["action"] == "STRIP":
                new_pos = " ".join(t for t in old_pos.split() if t != "NOM")
                if not new_pos:
                    sys.exit(f"FEHLER: {xid}: pos waere leer (alt: {old_pos!r})")
            stats[a["action"]] += 1

            token_changed = (new_lemma, new_pos, new_ana, new_corresp) != (old_lemma, old_pos, old_ana, old_corresp)
            if token_changed:
                new_tag = f'<w xml:id="{xid}" lemmaRef="{new_lemma}" pos="{new_pos}"'
                if new_ana:
                    new_tag += f' ana="{new_ana}"'
                if new_corresp:
                    new_tag += f' corresp="{new_corresp}"'
                new_tag += ">"
                text = text[:m.start()] + new_tag + text[m.end():]
                changed = True

            diff_rows.append({
                "file": fname, "xml_id": xid, "form": c["form"],
                "action": a["action"], "geaendert": "ja" if token_changed else "nein",
                "alt_pos": old_pos, "neu_pos": new_pos,
                "alt_lemmaRef": old_lemma, "neu_lemmaRef": new_lemma,
                "alt_ana": old_ana or "", "neu_ana": new_ana or "",
                "alt_corresp": old_corresp or "", "neu_corresp": new_corresp or "",
                "verdict": a["verdict"], "confidence": a["confidence"],
                "begruendung": a["begruendung"], "hinweis": a.get("note", ""),
                "kontext": (c.get("line") or "").strip(),
            })
        if changed and args.apply:
            fp.write_text(text, encoding="utf-8", newline="")
            stats["dateien_geaendert"] += 1

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "diff-liste.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(diff_rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(diff_rows)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] {len(diff_rows)} Faelle verarbeitet: {dict(stats)}")
    print(f"Diff-Liste: {out_dir / 'diff-liste.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
