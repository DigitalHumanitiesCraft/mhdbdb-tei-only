#!/usr/bin/env python3
"""21-abdeckung.py: Abdeckung und Pruefungen nach Phase 1 bis 3 (BRE, #147).

Je Zeuge und gesamt: Anteil der lexikalischen <w> (nicht in <head>) mit @lemmaRef, @pos, @ana,
@corresp, jeweils mit Nenner. Dazu die Pruefungen aus docs/DATA-MODEL.md -> Coverage reference
values and QA, als harte Fehler (Exit 1):
  - jedes @lemmaRef und jedes @ana zeigt auf eine ID in lexicon.xml, jedes @corresp auf einen Typ
    in variants.xml, der zum @lemmaRef gehoert
  - jedes @pos ist aus dem 19er-Set
  - kein @ana ohne @lemmaRef, kein @ana eines anderen Lemmas, keine Annotation in <head>
  - jede Datei validiert gegen schema/mhdbdb.rng

Aufruf: python -P -E scripts/ingest/bre/21-abdeckung.py [--markdown]
"""
import argparse
import collections
import sys
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_annot as ba  # noqa: E402
import bre_common as bc  # noqa: E402

ATTR = ["lemmaRef", "pos", "ana", "corresp"]


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--markdown", action="store_true", help="Tabelle als Markdown ausgeben")
    a = ap.parse_args()
    lex = ba.lade_lexikon()
    senses = {s["id"]: lid for lid, e in lex.items() for s in e["senses"]}
    typ_lemma = {}
    for _, e in etree.iterparse(str(ba.VARIANTEN), tag=ba.T + "entry"):
        lid = (e.get("corresp") or "").split("#")[-1]
        for f in e.findall(ba.T + "form"):
            typ_lemma[f.get(ba.XML_ID)] = lid
        e.clear()
    rng = etree.RelaxNG(etree.parse(str(bc.REPO / "schema" / "mhdbdb.rng")))
    fehler = []
    zeilen = []
    gesamt = collections.Counter()
    for zeuge, pfad in ba.zeugen_dateien():
        baum = ba.lies(pfad)
        if not rng.validate(baum):
            fehler.append(f"{pfad.name}: Schema: {rng.error_log[0].message}")
        z = collections.Counter()
        for w in baum.getroot().iter(ba.T + "w"):
            xid = w.get(ba.XML_ID)
            if ba.in_head(w):
                if any(w.get(x) for x in ATTR):
                    fehler.append(f"{xid}: Annotation in <head>")
                continue
            z["w"] += 1
            lr, pos, ana, cor = (w.get(x) for x in ATTR)
            lid = lr.split("#")[-1] if lr else None
            if lr:
                z["lemmaRef"] += 1
                if not lr.startswith("lexicon.xml#") or lid not in lex:
                    fehler.append(f"{xid}: @lemmaRef {lr} nicht in lexicon.xml")
            if pos:
                z["pos"] += 1
                if pos not in ba.VALID_POS:
                    fehler.append(f"{xid}: @pos {pos} nicht im 19er-Set")
            if ana:
                z["ana"] += 1
                sid = ana.split("#")[-1]
                if not lr:
                    fehler.append(f"{xid}: @ana ohne @lemmaRef")
                elif senses.get(sid) != lid:
                    fehler.append(f"{xid}: @ana {sid} gehoert nicht zu {lid}")
            if cor:
                z["corresp"] += 1
                tid = cor.split("#")[-1]
                if not cor.startswith("variants.xml#") or typ_lemma.get(tid) != lid:
                    fehler.append(f"{xid}: @corresp {cor} gehoert nicht zu {lid}")
        zeilen.append((zeuge, pfad.name[:-8], z))
        gesamt.update(z)
    zeilen.append(("gesamt", "", gesamt))
    if a.markdown:
        print("| Zeuge | Datei | lexikalische `<w>` | `@lemmaRef` | `@pos` | `@ana` | `@corresp` |")
        print("|---|---|--:|--:|--:|--:|--:|")
        for zeuge, name, z in zeilen:
            print(f"| {zeuge} | {name} | {z['w']} | " + " | ".join(
                f"{z[x]} ({100 * z[x] / z['w']:.1f} %)" for x in ATTR) + " |")
    else:
        print(f"{'Zeuge':7} {'Datei':15} {'<w>':>6} " + " ".join(f"{x:>17}" for x in ATTR))
        for zeuge, name, z in zeilen:
            print(f"{zeuge:7} {name:15} {z['w']:6d} " + " ".join(
                f"{z[x]:6d} ({100 * z[x] / z['w']:5.1f} %)" for x in ATTR))
    print(f"Pruefungen: {len(fehler)} Fehler")
    for f in fehler[:30]:
        print("  " + f)
    return 1 if fehler else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(1)
