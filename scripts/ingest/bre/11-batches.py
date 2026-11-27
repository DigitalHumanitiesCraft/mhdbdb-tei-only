#!/usr/bin/env python3
"""11-batches.py: Batches fuer die LLM-Disambiguierung (BRE, #147), Vorbild wzb-split-tsv.py.

Liest die Pending-TSV einer Phase und schreibt Arbeitsdateien nach temp/bre-batches/ (gitignoriert,
nicht versioniert: versioniert sind die Entscheidungen, siehe README). Je Zeile:

  bulk      eine Zeile je Form (Phase 1) oder je Lemma (Phase 2 und 3), mit allen Belegen bis
            MAX_BELEGE, darueber eine Stichprobe mit festem Seed (147)
  instance  eine Zeile je Token

Batches zu BATCH Zeilen. Der Seed macht die Stichprobe reproduzierbar.

Aufruf:
  python -P -E scripts/ingest/bre/11-batches.py --phase lemma --stufe bulk
  python -P -E scripts/ingest/bre/11-batches.py --phase lemma --stufe instance [--nur-norm a,b]

--offen: nur was die Pending-TSV noch ohne Entscheidung fuehrt (nach dem Apply-Skript sind die
entschiedenen Zeilen dort eingetragen). Fuer neu hinzugekommene Zeugen, wenn die Entscheidungen
der uebrigen schon stehen. Bei bulk nur Gruppen, in denen keine Zeile entschieden ist; bei
instance die Tokens der Stufe instance; bei --stufe split die Tokens ohne Entscheidung in
SPLIT-Gruppen (Ausgabe lemma-split-NN.tsv, Format wie instance). Danach 12-entscheidungen.py
--ergaenzen.
"""
import argparse
import collections
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

BATCH = 50
MAX_BELEGE = 12
SEED = 147
ZIEL = bc.REPO / "temp" / "bre-batches"
PHASEN = {
    # phase -> (pending-TSV, Gruppierungsschluessel fuer bulk, Kandidatenspalte)
    "lemma": (ba.PHASE1 / "lemma-pending.tsv", "norm", "kandidaten"),
    "pos": (ba.PHASE2 / "pos-pending.tsv", "gruppe", "kandidaten"),
    "sense": (ba.PHASE3 / "sense-pending.tsv", "gruppe", "kandidaten"),
}


def beleg(z):
    return f"{z['xml_id']} ({z['zeuge']}, {z['text']}): {z['kontext']}"


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=list(PHASEN), required=True)
    ap.add_argument("--stufe", choices=["bulk", "instance", "split"], required=True)
    ap.add_argument("--offen", action="store_true", help="nur Zeilen ohne Entscheidung (siehe oben)")
    ap.add_argument("--nur", default="", help="nur diese Gruppenschluessel (kommagetrennt), "
                    "bei instance: alle Tokens dieser Gruppen unabhaengig von ihrer Stufe")
    ap.add_argument("--praefix", default="", help="Namenspraefix der Batchdateien")
    a = ap.parse_args()
    pfad, schluessel, kandspalte = PHASEN[a.phase]
    zeilen = ba.lies_tsv(pfad)
    if a.stufe == "split" and not a.offen:
        raise bc.HarterFehler("--stufe split nur mit --offen")
    ergebnis = {"lemma": "resolved_lemma", "pos": "resolved_pos", "sense": "resolved_sense"}[a.phase]
    if a.offen:
        entschieden = {z["xml_id"] for z in zeilen if z[ergebnis] or z["decision_type"]}
        if a.stufe == "bulk":
            teils = {z[schluessel] for z in zeilen if z["xml_id"] in entschieden}
            zeilen = [z for z in zeilen if z[schluessel] not in teils]
        elif a.stufe == "split":
            bulkpfad = pfad.parent / f"{a.phase}-bulk.tsv"
            split = {b["schluessel"] for b in ba.lies_tsv(bulkpfad)
                     if b["decision_type"] == "abstain" and b["begruendung"].startswith("SPLIT")}
            patchpfad = pfad.parent / f"{a.phase}-patch.tsv"
            mit_patch = {p["xml_id"] for p in ba.lies_tsv(patchpfad)}
            # die Apply-Skripte tragen bei SPLIT ohne Token-Entscheidung abstain in die Pending-TSV ein
            zeilen = [z for z in zeilen if z["xml_id"] not in mit_patch and z["stufe"] == "bulk"
                      and z[schluessel] in split]
        else:
            zeilen = [z for z in zeilen if z["xml_id"] not in entschieden]
    nur = {x for x in a.nur.split(",") if x}
    rng = random.Random(SEED)
    out = []
    if a.stufe == "bulk":
        gruppen = collections.OrderedDict()
        for z in zeilen:
            if z["stufe"] == "bulk" and (not nur or z[schluessel] in nur):
                gruppen.setdefault(z[schluessel], []).append(z)
        for k, zs in gruppen.items():
            probe = zs if len(zs) <= MAX_BELEGE else sorted(rng.sample(zs, MAX_BELEGE),
                                                           key=lambda z: z["xml_id"])
            out.append({"schluessel": k, "form": zs[0]["form"] if a.phase == "lemma" else
                        " ".join(sorted({z["form"] for z in zs}))[:200],
                        "lemma": zs[0].get("lemma", ""),
                        "anzahl": len(zs), "kandidaten": zs[0][kandspalte],
                        "belege": " ¶ ".join(beleg(z) for z in probe)})
        felder = ["schluessel", "form", "lemma", "anzahl", "kandidaten", "belege"]
    else:
        for z in zeilen:
            if (z[schluessel] in nur) if nur else (a.stufe == "split" or z["stufe"] == "instance"):
                out.append({"xml_id": z["xml_id"], "form": z["form"], "lemma": z.get("lemma", ""),
                            "zeuge": z["zeuge"], "text": z["text"], "kontext": z["kontext"],
                            "kandidaten": z[kandspalte]})
        felder = ["xml_id", "form", "lemma", "zeuge", "text", "kontext", "kandidaten"]
    ZIEL.mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(0, len(out), BATCH):
        n += 1
        ba.schreibe_tsv(ZIEL / f"{a.praefix}{a.phase}-{a.stufe}-{n:02d}.tsv", felder, out[i:i + BATCH])
    print(f"{len(out)} Zeilen in {n} Batches nach {ZIEL} ({a.phase}, {a.stufe})")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
