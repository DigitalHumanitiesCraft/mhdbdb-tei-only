#!/usr/bin/env python3
"""15-apply.py: Entscheidungen von Phase 2 (@pos) oder Phase 3 (@ana) anwenden (BRE, #147).

Vorbild wzb-pos-apply.py und wzb-sense-apply.py. Liest <phase>-pending.tsv und die
Entscheidungen <phase>-bulk.tsv (je Gruppe) und <phase>-patch.tsv (je xml_id, geht vor), schreibt
das Attribut in die Zeugen und traegt die Entscheidung je Token in die Pending-TSV ein (Audit-Trail).
abstain und Hapaxe bleiben ohne Attribut.

Pruefungen: jede Entscheidung ist ein Kandidat des Tokens; @pos aus dem 19er-Set; @ana gehoert
zum @lemmaRef des Tokens (nie @ana ohne @lemmaRef); additiv (ein vorhandener, abweichender Wert
ist ein harter Fehler).

Aufruf: python -P -E scripts/ingest/bre/15-apply.py --phase pos|sense [--trocken]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

PHASEN = {
    # phase -> (Ordner, Ergebnisspalte, Attribut, Wert aus Entscheidung)
    "pos": (ba.PHASE2, "resolved_pos", "pos", lambda r: r),
    "sense": (ba.PHASE3, "resolved_sense", "ana", lambda r: f"lexicon.xml#{r}"),
}


def kandidaten(phase, text):
    if phase == "pos":
        return ba.pos_kandidaten(text)
    return set(re.findall(r"\b(lemma_\d+_sense_\d+)\b", text))


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=list(PHASEN), required=True)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    ordner, spalte, attr, wert = PHASEN[a.phase]
    pfad_p = ordner / f"{a.phase}-pending.tsv"
    pending = ba.lies_tsv(pfad_p)
    felder = list(pending[0].keys()) if pending else []
    bulk = {b["schluessel"]: b for b in ba.lies_tsv(ordner / f"{a.phase}-bulk.tsv")}
    patch = {p["xml_id"]: p for p in ba.lies_tsv(ordner / f"{a.phase}-patch.tsv")}
    ziel, stat = {}, collections.Counter()
    for z in pending:
        e = patch.get(z["xml_id"])
        if e is None and z["stufe"] == "bulk":
            e = bulk.get(z["gruppe"])
        if e is None:
            stat["offen_" + z["stufe"]] += 1
            continue
        ba.pruefe_entscheidung(e, z["xml_id"])
        if e["decision_type"] == "abstain":
            stat["abstain" if (z["xml_id"] in patch or "SPLIT" not in e["begruendung"]) else "offen_split"] += 1
        else:
            if e["resolved"] not in kandidaten(a.phase, z["kandidaten"]):
                raise bc.HarterFehler(f"{z['xml_id']}: {e['resolved']} ist kein Kandidat")
            if a.phase == "pos" and e["resolved"] not in ba.VALID_POS:
                raise bc.HarterFehler(f"{z['xml_id']}: {e['resolved']} nicht im 19er-Set")
            if a.phase == "sense" and not e["resolved"].startswith(z["lemma_id"] + "_sense_"):
                raise bc.HarterFehler(f"{z['xml_id']}: {e['resolved']} gehoert nicht zu {z['lemma_id']}")
            ziel[z["xml_id"]] = (z["lemma_id"], wert(e["resolved"]))
            stat[e["decision_type"]] += 1
        z[spalte] = e["resolved"]
        for k in ("decision_type", "confidence", "reviewer", "begruendung"):
            z[k] = e[k]
    gesetzt = 0
    for _, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        geaendert = False
        for w in baum.getroot().iter(ba.T + "w"):
            x = ziel.get(w.get(ba.XML_ID))
            if x is None:
                continue
            lid, v = x
            if w.get("lemmaRef") != f"lexicon.xml#{lid}":
                raise bc.HarterFehler(f"{w.get(ba.XML_ID)}: @lemmaRef {w.get('lemmaRef')} != {lid}")
            if w.get(attr):
                if w.get(attr) != v:
                    raise bc.HarterFehler(f"{w.get(ba.XML_ID)}: @{attr} {w.get(attr)} != {v}")
                stat["schon"] += 1
                continue
            w.set(attr, v)
            gesetzt += 1
            geaendert = True
        if geaendert and not a.trocken:
            ba.schreibe(baum, pfad)
    if gesetzt + stat["schon"] != len(ziel):
        raise bc.HarterFehler(f"{gesetzt} + {stat['schon']} != {len(ziel)} Entscheidungen")
    if not a.trocken:
        ba.schreibe_tsv(pfad_p, felder, pending)
    n = len(pending)
    print(f"mehrdeutige Tokens ({a.phase}): {n}")
    print(f"  @{attr} gesetzt: {ba.prozent(len(ziel), n)} (bulk-llm {stat['bulk-llm']}, instance-llm "
          f"{stat['instance-llm']}), davon schon vorhanden {stat['schon']}")
    print(f"  abstain: {stat['abstain']}; offen: hapax {stat['offen_hapax']}, ohne Entscheidung bulk "
          f"{stat['offen_bulk']} instance {stat['offen_instance']}, SPLIT ohne Token-Entscheidung "
          f"{stat['offen_split']}")
    print("(trocken: nichts geschrieben)" if a.trocken else "TEI und Pending-TSV geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
