#!/usr/bin/env python3
"""13-lemma-apply.py: Phase 1b anwenden (BRE, #147), Vorbild wzb-apply-lemmarefs.py.

Liest phase1/lemma-pending.tsv und die Entscheidungen phase1/lemma-bulk.tsv (je Form) und
phase1/lemma-patch.tsv (je xml_id, geht vor). Schreibt @lemmaRef in die Zeugen und traegt die
Entscheidung je Token in die Spalten resolved_lemma, decision_type, confidence, reviewer,
begruendung der Pending-TSV ein (Audit-Trail). abstain und Hapaxe bleiben ohne @lemmaRef.

Additiv: ein <w>, das schon ein @lemmaRef traegt, wird nicht ueberschrieben (harter Fehler, wenn
die Entscheidung abweicht). Jede Entscheidung muss ein Kandidat des Tokens sein.

Aufruf: python -P -E scripts/ingest/bre/13-lemma-apply.py [--trocken]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

PENDING_FELDER = ["xml_id", "zeuge", "text", "form", "norm", "kontext", "anzahl", "stufe",
                  "kandidaten", "resolved_lemma", "decision_type", "confidence", "reviewer",
                  "begruendung"]


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    pending = ba.lies_tsv(ba.PHASE1 / "lemma-pending.tsv", PENDING_FELDER)
    bulk = {b["schluessel"]: b for b in ba.lies_tsv(ba.PHASE1 / "lemma-bulk.tsv")}
    patch = {p["xml_id"]: p for p in ba.lies_tsv(ba.PHASE1 / "lemma-patch.tsv")}
    ziel = {}
    stat = collections.Counter()
    lexikon = set(ba.lade_lexikon())
    for z in pending:
        e = patch.get(z["xml_id"])
        if e is None and z["stufe"] == "bulk":
            e = bulk.get(z["norm"])
        if e is None:
            stat["offen_" + z["stufe"]] += 1
            continue
        ba.pruefe_entscheidung(e, f"{z['xml_id']}")
        kand = set(re.findall(r"\b(lemma_\d+)\b", z["kandidaten"]))
        if e["resolved"] and e["resolved"] not in kand:
            # zulaessig nur markiert, mit low und mit einem Lemma aus lexicon.xml (12-entscheidungen.py)
            if not (e["begruendung"].startswith("[außerhalb der Kandidaten]") and e["confidence"] == "low"
                    and e["resolved"] in lexikon):
                raise bc.HarterFehler(f"{z['xml_id']}: {e['resolved']} ist kein Kandidat ({sorted(kand)})")
            stat["ausserhalb"] += 1
        if e["decision_type"] == "abstain":
            if z["xml_id"] in patch or "SPLIT" not in e["begruendung"]:
                stat["abstain"] += 1
            else:
                stat["offen_split"] += 1
        else:
            ziel[z["xml_id"]] = e["resolved"]
            stat[e["decision_type"]] += 1
        z["resolved_lemma"] = e["resolved"]
        for k in ("decision_type", "confidence", "reviewer", "begruendung"):
            z[k] = e[k]
    unbenutzt = set(patch) - {z["xml_id"] for z in pending}
    if unbenutzt:
        raise bc.HarterFehler(f"{len(unbenutzt)} Patch-Zeilen ohne Pending-Token, z.B. {sorted(unbenutzt)[:3]}")

    gesetzt = 0
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        geaendert = False
        for w in baum.getroot().iter(ba.T + "w"):
            lid = ziel.get(w.get(ba.XML_ID))
            if lid is None:
                continue
            alt = w.get("lemmaRef")
            if alt:
                if alt != f"lexicon.xml#{lid}":
                    raise bc.HarterFehler(f"{w.get(ba.XML_ID)} traegt schon {alt}, Entscheidung {lid}")
                stat["schon"] += 1
                continue
            w.set("lemmaRef", f"lexicon.xml#{lid}")
            gesetzt += 1
            geaendert = True
        if geaendert and not a.trocken:
            ba.schreibe(baum, pfad)
    if gesetzt + stat["schon"] != len(ziel):
        raise bc.HarterFehler(f"{gesetzt} gesetzt + {stat['schon']} schon != {len(ziel)} Entscheidungen")
    if not a.trocken:
        ba.schreibe_tsv(ba.PHASE1 / "lemma-pending.tsv", PENDING_FELDER, pending)
    n = len(pending)
    print(f"mehrdeutige Tokens: {n}")
    print(f"  @lemmaRef gesetzt: {ba.prozent(len(ziel), n)} (bulk-llm {stat['bulk-llm']}, "
          f"instance-llm {stat['instance-llm']}), davon schon vorhanden {stat['schon']}, "
          f"Lemma ausserhalb der Kandidaten (low, markiert) {stat['ausserhalb']}")
    print(f"  abstain: {stat['abstain']}; offen: hapax {stat['offen_hapax']}, ohne Entscheidung "
          f"bulk {stat['offen_bulk']} instance {stat['offen_instance']}, SPLIT ohne Token-Entscheidung "
          f"{stat['offen_split']}")
    print("(trocken: nichts geschrieben)" if a.trocken else "TEI und lemma-pending.tsv geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
