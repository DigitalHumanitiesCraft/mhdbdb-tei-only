#!/usr/bin/env python3
"""10-lemma-assign.py: Phase 1a, Auto-Match der Lemmata (BRE, #147).

Vorbild: scripts/ingest/wzb/wzb-auto-match.py. Fuer jedes lexikalische <w> der 18 Zeugen
(nicht in <head>, bre_annot.py) wird die Wortform normalisiert (bre_annot.norm: Faltung der
Fruehdrucke, dann normalize_mhg) und in variants.xml nachgeschlagen, das auf dieselbe Weise
normalisiert ist:
  genau 1 Lemma  -> @lemmaRef (auto-single)
  mehrere        -> phase1/lemma-pending.tsv (Disambiguierung, Phase 1b)
  keines         -> phase1/lemma-unmatched.tsv (frequenzsortiert, fuer das Lexikonteam)
Roemische Zahlzeichen (nur Grossbuchstaben I V X L C M) -> lemma_13826 (DIG), wie in der
Tabelle docs/DATA-MODEL.md -> Structural cleanup ("Roman numerals in the text flow").

Schreibt nichts in lexicon.xml oder variants.xml. Idempotent: ein vorhandenes @lemmaRef bleibt.
Die Einteilung haengt nicht am vorhandenen @lemmaRef: ein in Phase 1b schon entschiedenes Token
bleibt in lemma-pending.tsv (13-lemma-apply.py traegt seine Entscheidung danach wieder ein), ein
abweichendes @lemmaRef an einem eindeutigen Token ist ein harter Fehler.
Stufen der Disambiguierung (Spalte stufe), nach Haeufigkeit der normalisierten Form unter den
mehrdeutigen Tokens: >= 3 bulk (eine Entscheidung je Form, Ausnahmen je xml_id), 2 instance
(je Token), 1 hapax (bewusst zurueckgestellt, DATA-MODEL Phase 1b).

Aufruf: python -P -E scripts/ingest/bre/10-lemma-assign.py [--trocken]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

RE_ROEMISCH = re.compile(r"^[IVXLCM]+$")
LEMMA_ZAHL = "lemma_13826"
PENDING_FELDER = ["xml_id", "zeuge", "text", "form", "norm", "kontext", "anzahl", "stufe",
                  "kandidaten", "resolved_lemma", "decision_type", "confidence", "reviewer",
                  "begruendung"]
UNMATCHED_FELDER = ["norm", "anzahl", "formen", "zeugen", "beispiel_xml_id", "beispiel_kontext"]


def stufe(n):
    return "bulk" if n >= 3 else ("instance" if n == 2 else "hapax")


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true", help="TEI nicht schreiben")
    a = ap.parse_args()

    lemmata, _ = ba.lade_varianten()
    lex = ba.lade_lexikon()
    konzepte = ba.lade_konzepte()
    if LEMMA_ZAHL not in lex or lex[LEMMA_ZAHL]["pos"] != ["DIG"]:
        raise bc.HarterFehler(f"{LEMMA_ZAHL} fehlt oder ist nicht DIG")

    pending, unmatched = [], collections.defaultdict(list)
    stat = collections.Counter()
    je_zeuge = {}
    baeume = []
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        z = collections.Counter()
        for t in ba.tokens(baum):
            if t["head"]:
                z["head"] += 1
                continue
            z["lexikalisch"] += 1
            w = t["w"]
            form = t["form"]
            n = ba.norm(form)
            kand = lemmata.get(n, set())
            eindeutig = LEMMA_ZAHL if RE_ROEMISCH.match(form) else (
                next(iter(kand)) if len(kand) == 1 else None)
            if eindeutig:
                ziel = f"lexicon.xml#{eindeutig}"
                if w.get("lemmaRef") and w.get("lemmaRef") != ziel:
                    raise bc.HarterFehler(f"{t['id']}: @lemmaRef {w.get('lemmaRef')} != {ziel}")
                # Herkunft vor dem Setzen zaehlen, damit ein zweiter Lauf dieselben Zahlen ausgibt
                if eindeutig == LEMMA_ZAHL:
                    z["roemisch"] += 1
                elif n != normalize_mhg(form) and normalize_mhg(form) not in lemmata:
                    z["dank_faltung"] += 1
                if w.get("lemmaRef"):
                    z["schon"] += 1
                    continue
                w.set("lemmaRef", ziel)
                z["eindeutig"] += 1
            elif kand:
                z["mehrdeutig"] += 1
                pending.append({"xml_id": t["id"], "zeuge": zeuge, "text": t["titel"], "form": form,
                                "norm": n, "kontext": t["kontext"],
                                "kandidaten": " | ".join(
                                    f"{ba.lemma_label(l, lex, konzepte)} n={c}"
                                    for l, c in sorted(kand.items(), key=lambda x: (-x[1], x[0])))})
            else:
                z["ohne"] += 1
                unmatched[n].append((form, zeuge, t["id"], t["kontext"]))
        je_zeuge[zeuge] = z
        stat.update(z)
        baeume.append((baum, pfad))

    haeufig = collections.Counter(p["norm"] for p in pending)
    for p in pending:
        p["anzahl"] = haeufig[p["norm"]]
        p["stufe"] = stufe(haeufig[p["norm"]])
    pending.sort(key=lambda p: (-p["anzahl"], p["norm"], p["xml_id"]))
    ba.schreibe_tsv(ba.PHASE1 / "lemma-pending.tsv", PENDING_FELDER, pending)
    um = []
    for n, lst in unmatched.items():
        um.append({"norm": n, "anzahl": len(lst),
                   "formen": " ".join(sorted({f for f, *_ in lst})),
                   "zeugen": " ".join(sorted({z for _, z, *_ in lst})),
                   "beispiel_xml_id": lst[0][2], "beispiel_kontext": lst[0][3]})
    um.sort(key=lambda r: (-r["anzahl"], r["norm"]))
    ba.schreibe_tsv(ba.PHASE1 / "lemma-unmatched.tsv", UNMATCHED_FELDER, um)

    if not a.trocken:
        for baum, pfad in baeume:
            ba.schreibe(baum, pfad)

    print(f"{'Zeuge':6} {'lex. <w>':>9} {'eindeutig':>10} {'mehrdeutig':>11} {'ohne':>6} {'head':>5}")
    for zeuge, z in je_zeuge.items():
        print(f"{zeuge:6} {z['lexikalisch']:9d} {z['eindeutig'] + z['schon']:10d} {z['mehrdeutig']:11d} "
              f"{z['ohne']:6d} {z['head']:5d}")
    lexn = stat["lexikalisch"]
    print(f"gesamt: {lexn} lexikalische <w> ({stat['head']} <w> in <head> nicht lexikalisch)")
    print(f"  eindeutig (@lemmaRef): {ba.prozent(stat['eindeutig'] + stat['schon'], lexn)}, davon "
          f"{stat['schon']} schon vorhanden, {stat['roemisch']} roemische Zahl, "
          f"{stat['dank_faltung']} nur dank Faltung")
    print(f"  mehrdeutig: {ba.prozent(stat['mehrdeutig'], lexn)} in {len(haeufig)} Formen; Stufen: "
          + ", ".join(f"{s} {sum(1 for p in pending if p['stufe'] == s)} Tokens/"
                      f"{sum(1 for n, c in haeufig.items() if stufe(c) == s)} Formen"
                      for s in ("bulk", "instance", "hapax")))
    print(f"  ohne Treffer: {ba.prozent(stat['ohne'], lexn)} in {len(um)} Formen "
          f"(phase1/lemma-unmatched.tsv)")
    print("(trocken: TEI nicht geschrieben)" if a.trocken else "TEI geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
