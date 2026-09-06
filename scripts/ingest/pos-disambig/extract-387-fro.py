#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#387: die kontextpflichtigen fro-Tokens fuer die Disambiguierung extrahieren.

Der mechanische Teil von #387 liegt als ingest/pos-disambig/387-vrouwe/. Was
dort zurueckgestellt wurde, weil es eine Kontextentscheidung braucht, ist die
Schreibung fro (mit und ohne Zirkumflex): am 06.09.2026 gemessen 390 Tokens in
61 Sigeln, mehrdeutig zwischen

    lemma_7260   vrouwe   NOM                  Herrin, Frau
    lemma_7250   vrô      ADJ ADV GRA NOM      froh

Das ist der Kern des Tickets. @wachauers Entscheidung vom 01.09.2026
("Jedesmal Frau Minne") galt der Anrede unmittelbar vor minne und ist
ausdruecklich NICHT auf diese Belege uebertragbar; die betroffenen Stellen
sind ohnehin schon in #216 abgearbeitet.

## Zwei Entscheidungen je Fall, nicht eine

Anders als bei minne oder stat reicht das Lemma nicht. Faellt das Urteil auf
lemma_7250, ist die Wortart offen, denn das Lemma fuehrt vier: ADJ, ADV, GRA
und NOM. Faellt es auf lemma_7260, ist sie es nicht, das Lemma fuehrt nur NOM.

GRA wird nie vergeben (POS-TAGSET §3 und §6.3d), auch nicht, wenn das
Ziel-Lemma den Tag fuehrt. Dieselbe Regel wie im Breve-Lauf zu #235.

## Was das Skript liefert

cases.json in der Form, die apply-homograph.py erwartet, plus ein
Kontextfenster: im Vers der Zielvers mit Vorgaenger- und Folgevers, in Prosa
ein Fenster von +-15 Tokens innerhalb des Blockelements. Zusaetzlich das
unmittelbar folgende Token als eigenes Feld: die Anrede steht typischerweise
vor einem Titel oder Namen ("fro minne", "frov kuenegin"), und das ist das
staerkste Einzelsignal, das ohne Lektuere zu haben ist.

Ausserdem @rend des Elternelements. @wachauer hat am 01.09.2026 in #216
festgehalten, dass rend="upper_case_first_letter" nicht zwingend die
Personifikation markiert, aber ein brauchbares Indiz ist, sobald Frau und
Titel zusammenstehen. Wichtig dabei: die Majuskel der Edition steht im Markup,
nicht im Zeichenbestand des Tokens, eine Pruefung auf den ersten Buchstaben
findet null Faelle.

Das Skript entscheidet nichts. Es schreibt keine actions.json.

Nur lesend am Korpus, deterministisch (corpus_files-Reihenfolge, Dokumentordnung).

Usage:
    python scripts/ingest/pos-disambig/extract-387-fro.py \
        --out-dir ingest/pos-disambig/387-fro
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from corpus_files import corpus_files  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
PC_TAG = "{" + TEI_NS + "}pc"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

ZIELFORM = "fro"          # MHG-normalisiert; trifft fro und frô
PROSA_FENSTER = 15
BLOCK_LOCAL = {"p", "head", "div", "lg", "body"}


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def token_text(el):
    return norm("".join(el.itertext()))


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out = Path(args.out_dir)
    if not out.is_absolute():
        out = REPO / out

    faelle = []
    formen, sigel = Counter(), Counter()
    for fp in corpus_files():
        root = etree.parse(str(fp)).getroot()
        body = root.find(".//{%s}body" % TEI_NS)
        if body is None:
            continue
        # pc mitnehmen, damit das Kontextfenster die Interpunktion zeigt: bei
        # einer Anrede steht dort oft ein Komma, und das ist ein Signal.
        knoten = [e for e in body.iter() if e.tag in (W_TAG, PC_TAG)]
        ws = [e for e in knoten if e.tag == W_TAG]
        for idx, w in enumerate(ws):
            if w.get("lemmaRef"):
                continue
            txt = token_text(w)
            if normalize_mhg(txt) != ZIELFORM:
                continue

            vers = vers_von(w)
            eltern = w.getparent()
            fall = {
                "file": fp.name,
                "xml_id": w.get(XML_ID),
                "form": txt,
                "sigle": fp.name.split(".")[0],
                "pos_prior": w.get("pos") or "",
                "rend": (eltern.get("rend") or "") if eltern is not None else "",
                "next_token": token_text(ws[idx + 1]) if idx + 1 < len(ws) else "",
            }
            if vers is not None:
                nach = list(vers.itersiblings(L_TAG))
                vor = list(vers.itersiblings(L_TAG, preceding=True))
                fall["context_mode"] = "verse"
                fall["verse_n"] = vers.get("n") or ""
                fall["prev_verse"] = render(
                    [e for e in vor[0].iter() if e.tag in (W_TAG, PC_TAG)]) if vor else ""
                fall["verse"] = render(
                    [e for e in vers.iter() if e.tag in (W_TAG, PC_TAG)], mark=w)
                fall["next_verse"] = render(
                    [e for e in nach[0].iter() if e.tag in (W_TAG, PC_TAG)]) if nach else ""
                fall["context"] = ""
            else:
                blk = block_von(w)
                umfeld = [e for e in (blk if blk is not None else body).iter()
                          if e.tag in (W_TAG, PC_TAG)]
                j = umfeld.index(w)
                fall["context_mode"] = "prose"
                fall["verse_n"] = ""
                fall["prev_verse"] = fall["verse"] = fall["next_verse"] = ""
                fall["context"] = render(
                    umfeld[max(0, j - PROSA_FENSTER):j + PROSA_FENSTER + 1], mark=w)
            faelle.append(fall)
            formen[txt] += 1
            sigel[fall["sigle"]] += 1

    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json").write_text(
        json.dumps(faelle, ensure_ascii=False, indent=1), encoding="utf-8")

    print("Faelle: %d in %d Sigeln" % (len(faelle), len(sigel)))
    print("Schreibungen:", dict(formen))
    print("Kontextmodus:", dict(Counter(f["context_mode"] for f in faelle)))
    print("mit @rend am Elternelement:",
          dict(Counter(f["rend"] for f in faelle if f["rend"])))
    print("groesste Sigel:", dict(sigel.most_common(12)))
    print("geschrieben:", out / "cases.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
