#!/usr/bin/env python3
"""16-sense-assign.py: Phase 3, Auto-Assign der Bedeutung (BRE, #147), Vorbild wzb-sense-assign.py.

Fuer jedes <w> mit @lemmaRef (nicht in <head>), nie @ana ohne @lemmaRef:
  Lemma mit genau 1 Sense  -> @ana = lexicon.xml#<sense> (auto-single)
  mehrere Senses           -> phase3/sense-pending.tsv, Kandidaten "sense_id :: Konzeptlabel DE (EN)";
                              Gruppe = Lemma (bulk ab 3 Tokens, 2 instance, 1 hapax zurueckgestellt)
  kein Sense               -> phase3/sense-ohne.tsv (redaktionelle Liste, kein @ana)
@corresp setzt erst 18-corresp.py, wenn alle @ana stehen. Idempotent.

Aufruf: python -P -E scripts/ingest/bre/16-sense-assign.py [--trocken]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

FELDER = ["xml_id", "zeuge", "text", "form", "lemma_id", "gruppe", "lemma", "kontext", "anzahl",
          "stufe", "kandidaten", "resolved_sense", "decision_type", "confidence", "reviewer",
          "begruendung"]
OHNE_FELDER = ["lemma_id", "lemma", "anzahl", "beispiel_xml_id"]


def stufe(n):
    return "bulk" if n >= 3 else ("instance" if n == 2 else "hapax")


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    lex = ba.lade_lexikon()
    konzepte = ba.lade_konzepte()
    pending, ohne, stat = [], collections.defaultdict(list), collections.Counter()
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        for t in ba.tokens(baum):
            w = t["w"]
            if t["head"]:
                if w.get("ana"):
                    raise bc.HarterFehler(f"{t['id']}: @ana in <head>")
                continue
            if not w.get("lemmaRef"):
                if w.get("ana"):
                    raise bc.HarterFehler(f"{t['id']}: @ana ohne @lemmaRef")
                continue
            stat["mit_lemma"] += 1
            lid = w.get("lemmaRef").split("#")[-1]
            senses = lex[lid]["senses"]
            ana = w.get("ana")
            if ana and ana.split("#")[-1] not in {s["id"] for s in senses}:
                raise bc.HarterFehler(f"{t['id']}: @ana {ana} gehoert nicht zu {lid}")
            if len(senses) == 1:
                if ana:
                    stat["schon"] += 1
                else:
                    w.set("ana", f"lexicon.xml#{senses[0]['id']}")
                    stat["auto"] += 1
            elif not senses:
                stat["ohne"] += 1
                ohne[lid].append(t["id"])
            else:
                stat["mehrdeutig"] += 1
                kand = " | ".join(
                    f"{s['id']} :: " + ("; ".join(konzepte.get(c, c) for c in s["konzepte"]) or "(ohne Konzept)")
                    for s in senses)
                pending.append({"xml_id": t["id"], "zeuge": zeuge, "text": t["titel"], "form": t["form"],
                                "lemma_id": lid, "gruppe": lid, "lemma": ba.lemma_label(lid, lex),
                                "kontext": t["kontext"], "kandidaten": kand})
        if not a.trocken:
            ba.schreibe(baum, pfad)
    h = collections.Counter(p["gruppe"] for p in pending)
    for p in pending:
        p["anzahl"] = h[p["gruppe"]]
        p["stufe"] = stufe(h[p["gruppe"]])
    pending.sort(key=lambda p: (-p["anzahl"], p["gruppe"], p["xml_id"]))
    ba.schreibe_tsv(ba.PHASE3 / "sense-pending.tsv", FELDER, pending)
    ba.schreibe_tsv(ba.PHASE3 / "sense-ohne.tsv", OHNE_FELDER, sorted(
        ({"lemma_id": l, "lemma": ba.lemma_label(l, lex), "anzahl": len(x), "beispiel_xml_id": x[0]}
         for l, x in ohne.items()), key=lambda r: (-r["anzahl"], r["lemma_id"])))
    n = stat["mit_lemma"]
    print(f"<w> mit @lemmaRef: {n}")
    print(f"  @ana auto (genau ein Sense): {ba.prozent(stat['auto'] + stat['schon'], n)}, "
          f"davon schon vorhanden {stat['schon']}")
    print(f"  mehrdeutig: {ba.prozent(stat['mehrdeutig'], n)} in {len(h)} Lemmata; Stufen: "
          + ", ".join(f"{s} {sum(1 for p in pending if p['stufe'] == s)} Tokens/"
                      f"{sum(1 for c in h.values() if stufe(c) == s)} Lemmata"
                      for s in ("bulk", "instance", "hapax")))
    print(f"  Lemma ohne Sense: {stat['ohne']} Tokens in {len(ohne)} Lemmata (phase3/sense-ohne.tsv)")
    print("(trocken: TEI nicht geschrieben)" if a.trocken else "TEI geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
