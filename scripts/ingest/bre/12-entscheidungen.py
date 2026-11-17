#!/usr/bin/env python3
"""12-entscheidungen.py: LLM-Entscheidungen einer Phase uebernehmen (BRE, #147).

Liest die Ausgaben der LLM-Batches (temp/bre-entscheidungen/<phase>-bulk-*.tsv und
<phase>-instance-*.tsv, Format in den Anleitungen temp/bre-batches/ANLEITUNG-<phase>.md) und
schreibt die versionierten Entscheidungstabellen der Phase:

  <phaseN>/<phase>-bulk.tsv   eine Zeile je Form (Phase 1) oder Lemma (2, 3)
  <phaseN>/<phase>-patch.tsv  eine Zeile je xml_id: Ausnahmen zu bulk, instance, SPLIT-Gruppen

Harte Pruefungen: jede Bulk-Gruppe und jedes Instance-Token der Pending-TSV genau einmal
entschieden (oder bewusst offen: Gruppen mit SPLIT muessen vollstaendig in instance stehen),
jede Entscheidung ist ein Kandidat der Zeile oder abstain, confidence aus high/medium/low.
Verworfene Batches (--verwerfen) zaehlen als nicht entschieden.

Aufruf: python -P -E scripts/ingest/bre/12-entscheidungen.py --phase lemma --reviewer llm:claude-sonnet-5-5
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

QUELLE = bc.REPO / "temp" / "bre-entscheidungen"
PHASEN = {
    # phase -> (Pending, Ausgabeordner, Gruppenschluessel, Ergebnisspalte, Kandidaten-Muster)
    "lemma": (ba.PHASE1 / "lemma-pending.tsv", ba.PHASE1, "norm", "resolved_lemma",
              re.compile(r"\b(lemma_\d+)\b")),
    "pos": (ba.PHASE2 / "pos-pending.tsv", ba.PHASE2, "gruppe", "resolved_pos",
            re.compile(r"\b([A-Z]{2,4})\b")),
    "sense": (ba.PHASE3 / "sense-pending.tsv", ba.PHASE3, "gruppe", "resolved_sense",
              re.compile(r"\b(lemma_\d+_sense_\d+)\b")),
}
BULK_FELDER = ["schluessel", "anzahl", "resolved", "decision_type", "confidence", "reviewer",
               "begruendung"]
PATCH_FELDER = ["xml_id", "form", "resolved", "decision_type", "confidence", "reviewer",
                "begruendung", "quelle"]


AUSSERHALB = "[außerhalb der Kandidaten] "
LEMMATA = None  # nur Phase lemma: Lemma-IDs aus lexicon.xml


def zulassen(phase, res, kand, conf, begr, ort):
    """Prueft eine Entscheidung gegen die Kandidaten -> (confidence, begruendung).

    Phase lemma: eine Lemma-ID ausserhalb der Kandidaten ist zulaessig, wenn sie in lexicon.xml
    steht (variants.xml fuehrt die Form fuer dieses Lemma nur nicht, z.B. "grus" fuer grüeʒen).
    Sie wird auf confidence=low gesetzt und markiert, landet also sicher im Pruefpaket.
    Phase pos und sense: nur Kandidaten (ein Sense eines anderen Lemmas braeche @ana/@lemmaRef).
    """
    if res == "abstain" or res in kand:
        if res != "abstain" and conf not in ba.CONFIDENCE:
            raise bc.HarterFehler(f"{ort}: confidence {conf!r}")
        return conf, begr
    if phase == "lemma" and res in LEMMATA:
        return "low", AUSSERHALB + begr
    if phase != "lemma" and (res in ba.VALID_POS or re.fullmatch(r"lemma_\d+_sense_\d+", res)):
        # ein gueltiger Wert, aber nicht unter den Kandidaten (z.B. PRO fuer ein Lemma, das nur
        # DET/NUM fuehrt): nicht geschrieben, als abstain mit dem verworfenen Wert gefuehrt
        print(f"verworfen (kein Kandidat): {ort} {res}")
        return None, f"[verworfen: {res} ist kein Kandidat] " + begr
    raise bc.HarterFehler(f"{ort}: {res!r} ist kein Kandidat ({sorted(kand)})")


def kandidaten(text, muster):
    if muster.pattern.startswith(r"\b([A-Z]"):
        return ba.pos_kandidaten(text)
    return set(muster.findall(text))


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=list(PHASEN), required=True)
    ap.add_argument("--reviewer", required=True, help="llm:<modell>")
    ap.add_argument("--verwerfen", default="", help="Batchdateien, die verworfen werden (kommagetrennt)")
    a = ap.parse_args()
    if not ba.RE_REVIEWER.match(a.reviewer):
        raise bc.HarterFehler(f"--reviewer {a.reviewer!r} ist nicht llm:<modell>")
    pending_pfad, ziel, schl, spalte, muster = PHASEN[a.phase]
    global LEMMATA
    if a.phase == "lemma":
        LEMMATA = set(ba.lade_lexikon())
    pending = ba.lies_tsv(pending_pfad)
    verworfen = {x.strip() for x in a.verwerfen.split(",") if x.strip()}
    gruppen, token = {}, {}
    for z in pending:
        gruppen.setdefault(z[schl], []).append(z)
        token[z["xml_id"]] = z

    bulk, patch, split = {}, {}, set()
    for p in sorted(QUELLE.glob(f"{a.phase}-bulk-*.tsv")):
        if p.name in verworfen:
            print(f"verworfen: {p.name}")
            continue
        for i, r in enumerate(ba.lies_tsv(p, ["schluessel", spalte, "confidence", "ausnahmen",
                                               "begruendung"]), 2):
            ort = f"{p.name}:{i}"
            k = r["schluessel"]
            if k not in gruppen and a.phase == "pos" and " " in k:
                # Schluessel "lemma_N form": ein Modell schreibt die normalisierte Form manchmal
                # mit Umlaut zurueck ("süesser" statt "sueesser"); normalisiert ist sie eindeutig
                lid, _, f = k.partition(" ")
                if f"{lid} {ba.norm(f)}" in gruppen:
                    print(f"Schluessel normalisiert: {ort} {k!r} -> {lid} {ba.norm(f)!r}")
                    k = f"{lid} {ba.norm(f)}"
            if k not in gruppen or gruppen[k][0]["stufe"] != "bulk":
                raise bc.HarterFehler(f"{ort}: {k!r} ist keine Bulk-Gruppe der Pending-TSV")
            if k in bulk or k in split:
                raise bc.HarterFehler(f"{ort}: {k!r} doppelt entschieden")
            kand = kandidaten(gruppen[k][0]["kandidaten"], muster)
            res = r[spalte].strip()
            if res == "SPLIT":
                split.add(k)
                bulk[k] = {"schluessel": k, "anzahl": len(gruppen[k]), "resolved": "",
                           "decision_type": "abstain", "confidence": "", "reviewer": a.reviewer,
                           "begruendung": "SPLIT: je Token entschieden (patch, quelle split)"}
                continue
            conf, begr = zulassen(a.phase, res, kand, r["confidence"], r["begruendung"].strip(), ort)
            if conf is None:
                res = "abstain"
            bulk[k] = {"schluessel": k, "anzahl": len(gruppen[k]),
                       "resolved": "" if res == "abstain" else res,
                       "decision_type": "abstain" if res == "abstain" else "bulk-llm",
                       "confidence": "" if res == "abstain" else conf,
                       "reviewer": a.reviewer, "begruendung": begr}
            for aus in filter(None, (x.strip() for x in r["ausnahmen"].split(";"))):
                xid, _, lres = aus.partition("=")
                xid, lres = xid.strip(), lres.strip()
                if xid not in token or token[xid][schl] != k:
                    raise bc.HarterFehler(f"{ort}: Ausnahme {xid!r} gehoert nicht zu {k!r}")
                aconf, abegr = zulassen(a.phase, lres, kand, r["confidence"],
                                        "Ausnahme zur Bulk-Entscheidung", f"{ort} Ausnahme {xid}")
                if aconf is None:
                    lres = "abstain"
                patch[xid] = {"xml_id": xid, "form": token[xid]["form"],
                              "resolved": "" if lres == "abstain" else lres,
                              "decision_type": "abstain" if lres == "abstain" else "instance-llm",
                              "confidence": "" if lres == "abstain" else aconf,
                              "reviewer": a.reviewer, "begruendung": abegr,
                              "quelle": "bulk-ausnahme"}
    for p in sorted(QUELLE.glob(f"{a.phase}-instance-*.tsv")) + sorted(QUELLE.glob(f"{a.phase}-split-*.tsv")):
        if p.name in verworfen:
            print(f"verworfen: {p.name}")
            continue
        quelle = "split" if "-split-" in p.name else "instance"
        for i, r in enumerate(ba.lies_tsv(p, ["xml_id", spalte, "confidence", "begruendung"]), 2):
            ort = f"{p.name}:{i}"
            xid = r["xml_id"]
            if xid not in token:
                raise bc.HarterFehler(f"{ort}: {xid!r} nicht in der Pending-TSV")
            g = token[xid][schl]
            if quelle == "instance" and token[xid]["stufe"] != "instance":
                raise bc.HarterFehler(f"{ort}: {xid} ist nicht Stufe instance")
            if quelle == "split" and g not in split:
                raise bc.HarterFehler(f"{ort}: {xid} gehoert zu keiner SPLIT-Gruppe ({g!r})")
            if xid in patch and patch[xid]["quelle"] != "bulk-ausnahme":
                raise bc.HarterFehler(f"{ort}: {xid} doppelt entschieden")
            kand = kandidaten(token[xid]["kandidaten"], muster)
            res = r[spalte].strip()
            conf, begr = zulassen(a.phase, res, kand, r["confidence"], r["begruendung"].strip(), ort)
            if conf is None:
                res = "abstain"
            patch[xid] = {"xml_id": xid, "form": token[xid]["form"],
                          "resolved": "" if res == "abstain" else res,
                          "decision_type": "abstain" if res == "abstain" else "instance-llm",
                          "confidence": "" if res == "abstain" else conf,
                          "reviewer": a.reviewer, "begruendung": begr,
                          "quelle": quelle}

    # Vollstaendigkeit
    fehlen_bulk = [k for k, zs in gruppen.items() if zs[0]["stufe"] == "bulk" and k not in bulk]
    fehlen_inst = [x for x, z in token.items() if z["stufe"] == "instance" and x not in patch]
    fehlen_split = [x for x, z in token.items() if z[schl] in split and x not in patch]
    print(f"Bulk-Gruppen: {len(bulk)} entschieden, davon SPLIT {len(split)}, abstain "
          f"{sum(1 for b in bulk.values() if b['decision_type'] == 'abstain') - len(split)}; "
          f"nicht entschieden {len(fehlen_bulk)}")
    print(f"Patch-Zeilen: {len(patch)} (bulk-ausnahme "
          f"{sum(1 for p in patch.values() if p['quelle'] == 'bulk-ausnahme')}, instance "
          f"{sum(1 for p in patch.values() if p['quelle'] == 'instance')}, split "
          f"{sum(1 for p in patch.values() if p['quelle'] == 'split')}); instance offen "
          f"{len(fehlen_inst)}, SPLIT-Tokens offen {len(fehlen_split)}")
    if fehlen_split:
        print("SPLIT-Gruppen ohne vollstaendige Token-Entscheidung: "
              + ",".join(sorted({token[x][schl] for x in fehlen_split})))
    ba.schreibe_tsv(ziel / f"{a.phase}-bulk.tsv", BULK_FELDER,
                    sorted(bulk.values(), key=lambda b: (-b["anzahl"], b["schluessel"])))
    ba.schreibe_tsv(ziel / f"{a.phase}-patch.tsv", PATCH_FELDER,
                    sorted(patch.values(), key=lambda p: p["xml_id"]))
    print(f"geschrieben: {ziel / (a.phase + '-bulk.tsv')}, {ziel / (a.phase + '-patch.tsv')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
