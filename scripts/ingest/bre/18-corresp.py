#!/usr/bin/env python3
"""18-corresp.py: Phase 3, @corresp (Variantentyp) setzen (BRE, #147), Algorithmus wie
wzb-sense-assign.py.resolve_corresp und docs/DATA-MODEL.md -> Phase 3.

Fuer jedes <w> mit @lemmaRef und @ana:
    typen = Typen aus variants.xml, deren Form normalisiert gleich der Wortform ist und die zum
            @lemmaRef gehoeren, geschnitten mit der Typliste im @ana des Senses (lexicon.xml)
    genau 1 Treffer -> @corresp = variants.xml#type_K
    0 Treffer       -> Form fehlt in variants.xml fuer diesen Sense (gezaehlt)
    >1 Treffer      -> nicht gesetzt (gezaehlt, phase3/corresp-mehrdeutig.tsv)

Welche Form zaehlt (Hinweis vom 2026-11-08 in #147): die aufgeloeste Form, ''.join(w.itertext()),
also mit dem Text von <expan>, <add> und <hi>. Die Graphie der Abkuerzung selbst ist nicht
ueberliefert: das Wiki schreibt nur die Aufloesung in Klammern, Stufe 0 macht daraus <expan>
ohne <abbr>. Es gibt im TEI also keine andere Form als die aufgeloeste, und extract-variants.py,
build-corpus-index.py und die Suche lesen ebenfalls itertext. Ausgenommen sind Woerter mit
<supplied>: deren ergaenzte Buchstaben stehen nicht in der Handschrift, die Form waere eine
Form des Herausgebers, keine Variante des Schreibers. Begruendung auch im README.

Aufruf: python -P -E scripts/ingest/bre/18-corresp.py [--trocken]
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

MEHR_FELDER = ["xml_id", "form", "lemma_id", "sense_id", "typen"]


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trocken", action="store_true")
    a = ap.parse_args()
    lex = ba.lade_lexikon()
    sense_typen = {s["id"]: s["typen"] for e in lex.values() for s in e["senses"]}
    _, typen = ba.lade_varianten()
    stat, mehr = collections.Counter(), []
    for _, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        for t in ba.tokens(baum):
            w = t["w"]
            if not (w.get("lemmaRef") and w.get("ana")):
                continue
            stat["mit_ana"] += 1
            # Einteilung unabhaengig vom vorhandenen @corresp, damit ein zweiter Lauf dieselben
            # Zahlen ausgibt; ein vorhandener Wert, der der Einteilung widerspricht, ist ein Fehler
            if w.find(f".//{ba.T}supplied") is not None:
                if w.get("corresp"):
                    raise bc.HarterFehler(f"{t['id']}: @corresp auf einem Wort mit <supplied>")
                stat["supplied"] += 1
                continue
            lid = w.get("lemmaRef").split("#")[-1]
            sid = w.get("ana").split("#")[-1]
            treffer = sorted({tid for tid, tl, _ in typen.get(ba.norm(t["form"]), [])
                              if tl == lid and tid in sense_typen.get(sid, set())})
            ziel = f"variants.xml#{treffer[0]}" if len(treffer) == 1 else None
            if w.get("corresp") and w.get("corresp") != ziel:
                raise bc.HarterFehler(f"{t['id']}: @corresp {w.get('corresp')} != {ziel}")
            if ziel:
                if w.get("corresp"):
                    stat["schon"] += 1
                else:
                    w.set("corresp", ziel)
                    stat["gesetzt"] += 1
                if w.find(f".//{ba.T}expan") is not None:
                    stat["gesetzt_expan"] += 1
            elif treffer:
                stat["mehrdeutig"] += 1
                mehr.append({"xml_id": t["id"], "form": t["form"], "lemma_id": lid, "sense_id": sid,
                             "typen": " ".join(treffer)})
            else:
                stat["kein"] += 1
        if not a.trocken:
            ba.schreibe(baum, pfad)
    ba.schreibe_tsv(ba.PHASE3 / "corresp-mehrdeutig.tsv", MEHR_FELDER, mehr)
    n = stat["mit_ana"]
    print(f"<w> mit @lemmaRef und @ana: {n}")
    print(f"  @corresp gesetzt: {ba.prozent(stat['gesetzt'] + stat['schon'], n)}, davon schon vorhanden "
          f"{stat['schon']}, mit <expan> im Wort {stat['gesetzt_expan']}")
    print(f"  kein Typ (Form fuer diesen Sense nicht in variants.xml): {stat['kein']}")
    print(f"  mehrere Typen (nicht gesetzt, phase3/corresp-mehrdeutig.tsv): {stat['mehrdeutig']}")
    print(f"  ausgenommen, <supplied> im Wort: {stat['supplied']}")
    print("(trocken: TEI nicht geschrieben)" if a.trocken else "TEI geschrieben")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
