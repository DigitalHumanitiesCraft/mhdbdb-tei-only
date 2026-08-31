#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#367: Entscheidungsvorlage fuer 'waeren' als Adjektiv statt Verb.

Sammelt die Faelle, in denen die Schreibfamilie von 'wâren' unter lemma_7505
(wesen, VRB) unmittelbar vor der Wortform 'minne' steht, also die belegte
attributive Lesart 'der/die wâren minne'. Schreibt eine CSV mit Vorvers,
Zielvers und Folgevers, damit die philologische Entscheidung ohne Blick ins
TEI moeglich ist.

Zaehlvorschrift, die dieselbe ist wie im Ticket: @lemmaRef traegt lemma_7505
UND die Form passt auf ^w.{1,2}ren$. NICHT ueber einen einzelnen Variantentyp,
denn 'wæren' und 'woren' tragen eigene Typen und fielen sonst heraus.

Zusaetzlich wird ausgegeben, welche Formen im Korpus bereits unter lemma_7338
(wâr, ADJ) annotiert sind: davon haengt ab, ob eine Umannotation bestehende
Variantentypen wiederverwenden kann oder neue praegt.

Usage:
    python scripts/ingest/pos-disambig/extract-367-waeren.py [--out DATEI]
"""
import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from corpus_files import corpus_files  # noqa: E402
from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

LEMMA_VRB = "lemma_7505"   # wesen
LEMMA_ADJ = "lemma_7338"   # wâr, das Ziel-Lemma der attributiven Lesart
FAMILIE = re.compile(r"^w.{1,2}ren$")
ZIEL_FOLGEWORT = "minne"


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def vers_text(el, mark_id=None):
    if el is None:
        return ""
    teile = []
    for w in el.iter(W_TAG):
        t = norm("".join(w.itertext()))
        teile.append("**%s**" % t if w.get(XML_ID) == mark_id else t)
    return " ".join(teile)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ingest/pos-disambig/367-waeren/faelle.csv")
    args = ap.parse_args()

    faelle = []
    adj_formen = Counter()
    adj_typen = Counter()

    for f in corpus_files():
        tree = etree.parse(str(f))
        ws = list(tree.iter(W_TAG))
        for i, w in enumerate(ws):
            lemmata = {c.split("#")[-1] for c in (w.get("lemmaRef") or "").split()}
            form = norm("".join(w.itertext()))

            if LEMMA_ADJ in lemmata:
                adj_formen[form.lower()] += 1
                adj_typen.update({c.split("#")[-1]
                                  for c in (w.get("corresp") or "").split()} or {"-"})

            if LEMMA_VRB not in lemmata or not FAMILIE.match(form.lower()):
                continue
            if i + 1 >= len(ws):
                continue
            if norm("".join(ws[i + 1].itertext())).lower() != ZIEL_FOLGEWORT:
                continue

            xid = w.get(XML_ID)
            vers = w.getparent()
            while vers is not None and vers.tag != L_TAG:
                vers = vers.getparent()
            vorher = nachher = None
            if vers is not None:
                alle = list(tree.iter(L_TAG))
                j = alle.index(vers)
                vorher = alle[j - 1] if j > 0 else None
                nachher = alle[j + 1] if j + 1 < len(alle) else None

            faelle.append({
                "file": f.name,
                "xml_id": xid,
                "form": form,
                "corresp": w.get("corresp") or "",
                "vers_n": vers.get("n") if vers is not None else "",
                "vorvers": vers_text(vorher),
                "vers": vers_text(vers, xid),
                "folgevers": vers_text(nachher),
                "entscheidung": "",
                "anmerkung": "",
            })

    ziel = REPO / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with open(ziel, "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(faelle[0].keys()), delimiter=";")
        wr.writeheader()
        wr.writerows(faelle)

    print("Faelle 'w?ren' + minne unter %s: %d" % (LEMMA_VRB, len(faelle)))
    # split("_", 1)[0], nicht rsplit("_", 2)[0]: siehe sigle() in
    # extract-cases-by-id.py. Hier steuert die Ableitung nur diese
    # Diagnosezeile und keine Dateiauswahl, im schlechtesten Fall stuende also
    # WZB_1ra statt WZB in einer Ausgabe. Trotzdem mitgezogen, damit die
    # Fehlerklasse nicht an einer dritten Stelle liegen bleibt.
    print("  Siglen:", dict(sorted(Counter(
        x["xml_id"].split("_", 1)[0] for x in faelle).items())))
    print("  Schreibungen:", dict(Counter(x["form"].lower() for x in faelle)))
    print("  geschrieben:", ziel)
    print()
    print("Bestand unter %s (waer, ADJ) im Korpus: %d Tokens, %d Formen"
          % (LEMMA_ADJ, sum(adj_formen.values()), len(adj_formen)))
    print("  haeufigste Formen:", dict(adj_formen.most_common(12)))
    print("  Variantentypen:", dict(adj_typen.most_common(12)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
