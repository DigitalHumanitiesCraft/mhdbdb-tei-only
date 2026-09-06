#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#387: die eindeutigen vrouwe-Tokens ohne @lemmaRef extrahieren.

Schwesterskript zu extract-216-vrouwe155.py, mit derselben Bauart und einer
engeren Menge. Dort ging es um die 155 Tokens unmittelbar vor einer
minne-Form, hier um den Rest, den @wachauer am 01.09.2026 als eigenes Ticket
verlangt hat.

**Dieses Skript nimmt ausschliesslich die mechanisch bestimmten Faelle.** Die
kontextpflichtigen bleiben liegen und werden nicht einmal als Fall
ausgegeben, damit niemand sie versehentlich durch die Pipeline schiebt: sie
sind die eigentliche Arbeit von #387 und brauchen eine philologische
Entscheidung, die @wachauer ausdruecklich NICHT vorweggenommen hat (seine
Antwort vom 01.09. gilt der Anrede vor minne und nicht den uebrigen Belegen).

## Auswahlregel

Ein Fall ist ein <w> im <body>, das

  1. KEIN @lemmaRef traegt,
  2. formal vrouwe ist, und
  3. dessen normalisierte Schreibung im gesamten Korpus nur ein einziges
     Lemma traegt, naemlich lemma_7260 (vrouwe), das genau eine Wortart fuehrt.

Punkt 3 ist die Stelle, an der dieses Skript strenger ist als eine
Kandidatenabfrage im Variantenwoerterbuch. Beide Quellen sagen ueber diesen
Bestand dasselbe, aber sie sind nicht dasselbe: variants.xml ist korpus-
abgeleitet und kann hinter dem Korpus herhinken. Gemessen wird deshalb am
Korpus, und die Menge der Lemmata je Form wird ueber ALLE Lemmata gebildet,
nicht gegen eine Liste erwarteter Konkurrenten (die Lehre aus dem
Vorgaengerskript, siehe dessen Docstring).

**Formal vrouwe wird am Bestand erhoben, nicht geraten.** Es ist die Menge der
MHG-normalisierten Oberflaechenformen aller <w> mit lemma_7260. Eine
handgeschriebene Schreibungsliste waere hier nachweislich falsch: #216
(Kommentar vom 31.08.2026) hat gemessen, dass eine Sechserliste aus HUGO nur
214 von 633 Stellen deckt und die haeufigste Schreibung nicht enthaelt.

## Was ausdruecklich NICHT hierher gehoert

- Die mehrdeutigen Formen (Stand 06.09.2026: fro mit 390 Tokens, froewen mit
  6, vroewe mit 1). Das Skript zaehlt sie und legt sie als offene-faelle.csv
  ab, ohne cases.json-Eintrag.
- Tokens, deren Rohform unter lemma_7260 keinen Variantentyp hat. Sie kaemen
  sonst bei apply-homograph als "kein-typ" in den Review; das Skript meldet
  sie vorher, damit die Zahl im Batch-Log steht statt im Rueckstand.

Nur lesend am Korpus, deterministisch (corpus_files-Reihenfolge, Dokumentordnung).

Usage:
    python scripts/ingest/pos-disambig/extract-387-vrouwe.py \
        --out-dir ingest/pos-disambig/387-vrouwe
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from corpus_files import corpus_files  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

LEMMA_VROUWE = "lemma_7260"
VARIANTS = REPO / "authority-files" / "variants.xml"

PROSA_FENSTER = 15
BLOCK_LOCAL = {"p", "head", "div", "lg", "body"}


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def token_text(el):
    return norm("".join(el.itertext()))


def lemma_ids(el):
    """Token-genaue Menge der Lemma-Ids eines @lemmaRef (CONTRACTS.md B.1)."""
    return {v.split("#")[-1] for v in (el.get("lemmaRef") or "").split()}


def vers_von(w):
    for a in w.iterancestors():
        if a.tag == L_TAG:
            return a
    return None


def block_von(w):
    for a in w.iterancestors():
        if etree.QName(a).localname in BLOCK_LOCAL:
            return a
    return None


def render(tokens, mark=None):
    teile = []
    for t in tokens:
        txt = token_text(t)
        if not txt:
            continue
        teile.append("**" + txt + "**" if t is mark else txt)
    return " ".join(teile)


def typen_am_lemma():
    """Rohform -> type_id fuer alle <form> unter lemma_7260 in variants.xml."""
    root = etree.parse(str(VARIANTS)).getroot()
    treffer = {}
    for e in root.findall(".//{%s}entry" % TEI_NS):
        if (e.get("corresp") or "").split("#")[-1] != LEMMA_VROUWE:
            continue
        for f in e.findall("{%s}form" % TEI_NS):
            treffer[(f.text or "").strip()] = f.get(XML_ID)
    return treffer


def sammle_formen_lemmata(dateien):
    """Je normalisierter Oberflaechenform die Menge ALLER Lemmata am Bestand."""
    form2lemmata = defaultdict(set)
    for fp in dateien:
        root = etree.parse(str(fp)).getroot()
        for w in root.iter(W_TAG):
            ids = lemma_ids(w)
            if not ids:
                continue
            txt = token_text(w)
            if txt:
                form2lemmata[normalize_mhg(txt)] |= ids
        root.clear()
    return form2lemmata


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out = Path(args.out_dir)
    if not out.is_absolute():
        out = REPO / out

    dateien = list(corpus_files())
    print("Korpusdateien: %d" % len(dateien))

    form2lemmata = sammle_formen_lemmata(dateien)
    inventar = {f for f, ls in form2lemmata.items() if LEMMA_VROUWE in ls}
    eindeutig = {f for f in inventar if form2lemmata[f] == {LEMMA_VROUWE}}
    print("Formeninventar lemma_7260: %d Formen, davon %d ausschliesslich"
          % (len(inventar), len(eindeutig)))
    print("  mit weiteren Lemmata: %s"
          % sorted((f, sorted(form2lemmata[f] - {LEMMA_VROUWE}))
                   for f in inventar - eindeutig))

    typen = typen_am_lemma()

    faelle, aktionen, offen = [], [], []
    formen_ok, formen_offen, ohne_typ = Counter(), Counter(), Counter()
    for fp in dateien:
        root = etree.parse(str(fp)).getroot()
        body = root.find(".//{%s}body" % TEI_NS)
        if body is None:
            continue
        ws = list(body.iter(W_TAG))
        txt = [token_text(w) for w in ws]
        for i, w in enumerate(ws):
            if w.get("lemmaRef"):
                continue
            nf = normalize_mhg(txt[i])
            if nf not in inventar:
                continue
            xid = w.get(XML_ID)
            vers = vers_von(w)

            grund = ""
            if nf not in eindeutig:
                grund = "mehrdeutig: auch %s" % ", ".join(
                    sorted(form2lemmata[nf] - {LEMMA_VROUWE}))
            elif txt[i] not in typen:
                grund = "kein Variantentyp unter %s fuer die Rohform" % LEMMA_VROUWE

            prev_v = ziel_v = next_v = ""
            if vers is not None:
                geschw = list(vers.itersiblings(L_TAG))
                vorher = list(vers.itersiblings(L_TAG, preceding=True))
                prev_v = render(list(vorher[0].iter(W_TAG))) if vorher else ""
                ziel_v = render(list(vers.iter(W_TAG)), mark=w)
                next_v = render(list(geschw[0].iter(W_TAG))) if geschw else ""
                kontext = " / ".join(x for x in (prev_v, ziel_v, next_v) if x)
                modus, vers_n = "verse", (vers.get("n") or "")
            else:
                blk = block_von(w)
                nachbarn = list(blk.iter(W_TAG)) if blk is not None else ws
                j = nachbarn.index(w)
                kontext = render(nachbarn[max(0, j - PROSA_FENSTER):
                                          j + PROSA_FENSTER + 1], mark=w)
                modus, vers_n = "prose", ""

            if grund:
                offen.append({"file": fp.name, "xml_id": xid, "form": txt[i],
                              "sigle": fp.name.split(".")[0],
                              "pos_prior": w.get("pos") or "",
                              "grund": grund, "vers": vers_n,
                              "kontext": kontext})
                (ohne_typ if grund.startswith("kein Variantentyp")
                 else formen_offen)[txt[i]] += 1
                continue

            faelle.append({"file": fp.name, "xml_id": xid, "form": txt[i],
                           "sigle": fp.name.split(".")[0],
                           "pos_prior": w.get("pos") or "",
                           "context_mode": modus, "verse_n": vers_n,
                           "context": kontext,
                           "prev_verse": prev_v, "verse": ziel_v,
                           "next_verse": next_v})
            aktionen.append({
                "xml_id": xid, "lemma": LEMMA_VROUWE, "pos": "NOM",
                "confidence": "high", "herkunft": "mechanisch",
                "begruendung": (
                    "Die MHG-normalisierte Schreibung traegt im gesamten Korpus "
                    "nur lemma_7260, und lemma_7260 fuehrt genau eine Wortart "
                    "(NOM). Keine Kontextentscheidung noetig."),
            })
            formen_ok[txt[i]] += 1

    # Eine Wache gegen genau den Fehler, den das Vorgaengerskript hatte: die
    # Begruendung oben behauptet Eindeutigkeit ueber ALLE Lemmata. Wenn diese
    # Menge je einen mehrdeutigen Fall enthielte, stuende sie falsch im Log.
    if any(normalize_mhg(f["form"]) not in eindeutig for f in faelle):
        sys.exit("FEHLER: ein Fall der mechanischen Menge traegt eine "
                 "mehrdeutige Schreibung. Das darf nicht vorkommen.")

    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json").write_text(
        json.dumps(faelle, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "actions.json").write_text(
        json.dumps(aktionen, ensure_ascii=False, indent=1), encoding="utf-8")
    if offen:
        with open(out / "offene-faelle.csv", "w", encoding="utf-8-sig",
                  newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(offen[0].keys()),
                                delimiter=";")
            wr.writeheader()
            wr.writerows(offen)

    # Die corresp-Tabelle fuer die config.json aus dem Bestand, nicht von Hand.
    corresp = {"%s|%s" % (form.lower(), LEMMA_VROUWE): typen[form]
               for form in sorted(formen_ok)}
    print("\nMechanisch: %d Tokens in %d Sigeln, %d Schreibungen"
          % (len(faelle), len({f['sigle'] for f in faelle}), len(formen_ok)))
    print("  je Schreibung:", dict(formen_ok.most_common()))
    print("  Kontextmodus:", dict(Counter(f["context_mode"] for f in faelle)))
    print("\nZurueckgestellt: %d Tokens" % len(offen))
    print("  mehrdeutige Schreibung:", dict(formen_offen.most_common()))
    print("  ohne Variantentyp     :", dict(ohne_typ.most_common()))
    print("\ncorresp fuer die config.json:")
    print(json.dumps(corresp, ensure_ascii=False, indent=2))
    print("\ngeschrieben:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
