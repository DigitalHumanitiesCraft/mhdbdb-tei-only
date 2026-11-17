#!/usr/bin/env python3
"""14-pos-assign.py: Phase 2, Auto-Inherit der Wortart (BRE, #147), Vorbild wzb-pos-assign.py.

Fuer jedes <w> mit @lemmaRef (nicht in <head>): Wortarten des Lemmas aus lexicon.xml
(gramGrp/pos, auf das 19er-Set abgebildet in bre_annot.lade_lexikon: ART -> DET, GRA faellt weg
nach docs/POS-TAGSET.md §3, ein Lemma nur mit GRA wird ADJ; wzb-pos-assign.py bildet GRA -> ADV ab):
  genau 1  -> @pos (auto-single)
  mehrere  -> phase2/pos-pending.tsv, Gruppe = Lemma und normalisierte Form (bulk ab 3 Tokens,
              2 instance, 1 hapax zurueckgestellt, wie Phase 1)
  keine    -> gezaehlt und gemeldet, kein @pos
Jeder geschriebene Tag ist aus dem 19er-Set (harter Fehler sonst). Idempotent: ein zweiter Lauf nach
15-apply.py --phase pos teilt gleich ein, 15 fuellt die Aufloesungsspalten wieder.

Aufruf: python -P -E scripts/ingest/bre/14-pos-assign.py [--trocken]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

FELDER = ["xml_id", "zeuge", "text", "form", "lemma_id", "gruppe", "lemma", "kontext", "anzahl",
          "stufe", "kandidaten", "resolved_pos", "decision_type", "confidence", "reviewer",
          "begruendung"]


def stufe(n):
    return "bulk" if n >= 3 else ("instance" if n == 2 else "hapax")


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    lex = ba.lade_lexikon()
    pending, stat, je_zeuge = [], collections.Counter(), {}
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        z = collections.Counter()
        for t in ba.tokens(baum):
            w = t["w"]
            if t["head"] or not w.get("lemmaRef"):
                continue
            z["mit_lemma"] += 1
            lid = w.get("lemmaRef").split("#")[-1]
            if lid not in lex:
                raise bc.HarterFehler(f"{t['id']}: {lid} fehlt in lexicon.xml")
            pos = lex[lid]["pos19"]
            fremd = [p for p in pos if p not in ba.VALID_POS]
            if fremd:
                raise bc.HarterFehler(f"{lid}: Wortart(en) {fremd} nicht im 19er-Set")
            # Ein schon gesetztes @pos kommt bei genau einer Wortart von hier (also genau diese),
            # sonst von 15-apply.py, das auch CCNJ und SCNJ setzt, wenn das Lemma CNJ traegt
            erlaubt = set(pos) if len(pos) == 1 else ba.pos_kandidaten(" | ".join(pos))
            if w.get("pos") and w.get("pos") not in erlaubt:
                raise bc.HarterFehler(f"{t['id']}: @pos {w.get('pos')} nicht unter {sorted(erlaubt)} von {lid}")
            if len(pos) == 1:
                if w.get("pos"):
                    z["schon"] += 1
                else:
                    w.set("pos", pos[0])
                    z["auto"] += 1
            elif not pos:
                z["ohne_pos"] += 1
            else:
                # bleibt in der Pending-TSV, auch wenn 15-apply.py @pos schon gesetzt hat
                z["mehrdeutig"] += 1
                pending.append({"xml_id": t["id"], "zeuge": zeuge, "text": t["titel"],
                                "form": t["form"], "lemma_id": lid,
                                "gruppe": f"{lid} {ba.norm(t['form'])}",
                                "lemma": ba.lemma_label(lid, lex), "kontext": t["kontext"],
                                "kandidaten": " | ".join(pos)})
        je_zeuge[zeuge] = z
        stat.update(z)
        if not a.trocken:
            ba.schreibe(baum, pfad)
    h = collections.Counter(p["gruppe"] for p in pending)
    for p in pending:
        p["anzahl"] = h[p["gruppe"]]
        p["stufe"] = stufe(h[p["gruppe"]])
    pending.sort(key=lambda p: (-p["anzahl"], p["gruppe"], p["xml_id"]))
    ba.schreibe_tsv(ba.PHASE2 / "pos-pending.tsv", FELDER, pending)
    n = stat["mit_lemma"]
    print(f"<w> mit @lemmaRef: {n}")
    print(f"  @pos geerbt (genau eine Wortart): {ba.prozent(stat['auto'] + stat['schon'], n)}, "
          f"davon schon vorhanden {stat['schon']}")
    print(f"  mehrdeutig: {ba.prozent(stat['mehrdeutig'], n)} in {len(h)} Gruppen (Lemma+Form); Stufen: "
          + ", ".join(f"{s} {sum(1 for p in pending if p['stufe'] == s)} Tokens/"
                      f"{sum(1 for c in h.values() if stufe(c) == s)} Gruppen"
                      for s in ("bulk", "instance", "hapax")))
    print(f"  Lemma ohne Wortart im Lexikon: {stat['ohne_pos']}")
    print("(trocken: TEI nicht geschrieben)" if a.trocken else "TEI geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
