#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216 Serie 1: Extraktion der nackten minne-Tokens fuer die Kontext-Disambiguierung.

Zieht alle <w> mit Oberflaechenform "minne" (case-insensitiv, NFC) OHNE @lemmaRef
aus dem gesamten Korpus (667 Dateien via corpus_files) und schreibt sie als
cases.json nach ingest/pos-disambig/216-minne/ (Muster: 189-gwtk-rot-junc).

Zwei Kontext-Modi, weil 1.016 der Faelle ausserhalb von <l> stehen (Prosa):
  - verse: Zielvers (Token mit ** markiert) + Vorgaengervers + 2 Folgeverse,
    wie im Piloten #189
  - prose: Fenster von +-15 Tokens um das Ziel innerhalb des Blockelements
    (<p>, <head>, ...), Ziel ebenfalls mit ** markiert

Zusatzfeld pos_prior: 326 der Faelle tragen bereits @pos ohne @lemmaRef
(ADP 183, FLG 128, ABG 15; darunter 16x NAM = Frau-Minne-Kandidaten). Das @pos
geht als Vorinformation in den Prompt; die Anwendungsregel dazu steht im
Batch-README (Konflikt LLM-Verdict vs. pos_prior -> Review, pos=NAM -> Review).

Nur lesend am Korpus; deterministisch (corpus_files-Reihenfolge, Dokumentordnung).

Usage:
    python scripts/ingest/pos-disambig/extract-216-minne.py
"""
import json
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from corpus_files import corpus_files  # noqa: E402

from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
PC_TAG = "{" + TEI_NS + "}pc"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

TARGET = "minne"
PROSE_WINDOW = 15  # Tokens je Seite

# Blockelemente, in denen Prosa-Faelle haengen (gemessen 2026-08-24:
# p 962, head 29, hi 14, supplied 10, div 1 — hi/supplied sind Inline und
# werden zum naechsten Blockeltern hochgereicht)
BLOCK_LOCAL = {"p", "head", "div", "lg", "body"}


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def token_text(el):
    return norm("".join(el.itertext()))


def render(tokens, mark=None):
    """Tokens (w/pc-Elemente) als Text, das mark-Element mit ** markiert."""
    parts = []
    for t in tokens:
        txt = token_text(t)
        if not txt:
            continue
        parts.append("**" + txt + "**" if t is mark else txt)
    return " ".join(parts)


def block_ancestor(w):
    for a in w.iterancestors():
        if etree.QName(a).localname in BLOCK_LOCAL:
            return a
    return None


def main():
    cases = []
    for f in corpus_files():
        sigle = f.name.replace(".tei.xml", "")
        tree = etree.parse(str(f))

        verses = list(tree.iter(L_TAG))
        verse_index = {id(l): i for i, l in enumerate(verses)}
        verse_tokens = [[t for t in l.iterdescendants(W_TAG, PC_TAG)] for l in verses]

        for w in tree.iter(W_TAG):
            if w.get("lemmaRef"):
                continue
            if token_text(w).lower() != TARGET:
                continue

            case = {
                "file": f.name,
                "xml_id": w.get(XML_ID),
                "form": token_text(w),
                "sigle": sigle,
            }
            if w.get("pos"):
                case["pos_prior"] = w.get("pos")

            anc_l = next((a for a in w.iterancestors() if a.tag == L_TAG), None)
            if anc_l is not None:
                i = verse_index[id(anc_l)]
                case["context_mode"] = "verse"
                case["verse_n"] = anc_l.get("n")
                case["prev_verse"] = render(verse_tokens[i - 1]) if i > 0 else ""
                case["verse"] = render(verse_tokens[i], mark=w)
                case["next_verse"] = render(verse_tokens[i + 1]) if i + 1 < len(verses) else ""
                case["next2_verse"] = render(verse_tokens[i + 2]) if i + 2 < len(verses) else ""
            else:
                block = block_ancestor(w)
                tokens = list(block.iterdescendants(W_TAG, PC_TAG)) if block is not None else [w]
                pos = tokens.index(w)
                lo = max(0, pos - PROSE_WINDOW)
                hi = pos + PROSE_WINDOW + 1
                case["context_mode"] = "prose"
                case["block"] = etree.QName(block).localname if block is not None else "?"
                case["context"] = render(tokens[lo:hi], mark=w)
            cases.append(case)

    out_dir = REPO / "ingest" / "pos-disambig" / "216-minne"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "cases.json"
    out.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="")

    n_verse = sum(1 for c in cases if c["context_mode"] == "verse")
    n_prior = sum(1 for c in cases if "pos_prior" in c)
    print("Faelle:", len(cases), "| verse:", n_verse, "| prose:", len(cases) - n_verse,
          "| mit pos_prior:", n_prior)
    print("geschrieben:", out)


if __name__ == "__main__":
    main()
