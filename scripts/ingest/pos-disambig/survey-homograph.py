#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sondierung fuer eine Homographie-Serie (#216 ff.): lohnt sich der Batch?

Beantwortet vor jeder neuen Serie die immer gleichen fuenf Fragen zu einer
Wortform:

  1. Wie viele Tokens dieser Form sind unannotiert (kein @lemmaRef)?
  2. Auf wie viele Texte verteilen sie sich?
  3. Welche Lemmata traegt die Form dort, wo sie annotiert IST? Das ist die
     Kandidatenmenge fuer die Disambiguierung, und sie kommt aus dem Korpus,
     nicht aus dem Lexikon: massgeblich ist die geuebte Praxis.
  4. Welche Variantentypen sind damit schon vergeben (praegt der Batch neue)?
  5. Wie viele der unannotierten Tokens tragen bereits ein @pos als Prior?

Die Form wird als Regex gegen den kleingeschriebenen Tokentext gematcht, damit
die mittelhochdeutsche Schreibvielfalt hineinpasst. Eine Wortliste taugt dafuer
nicht, das war der Fehler des ersten Stichprobenfilters in #216.

Usage:
    python scripts/ingest/pos-disambig/survey-homograph.py --form "^stat$"
    python scripts/ingest/pos-disambig/survey-homograph.py --form "^st[aâáàäăa]t$"
"""
import argparse
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


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def esc(s):
    """Escaped ausgeben, immer.

    Die Windows-Konsole laeuft unter cp1252: sie wirft bei 'ă' einen
    UnicodeEncodeError und ersetzt 'â' still durch '?'. An genau dieser stillen
    Ersetzung wurde in #216 eine Schreibung falsch abgelesen und die Zahl
    landete im Provenienz-Log. Deshalb geht hier nichts Unescaptes hinaus.
    """
    return s.encode("unicode_escape").decode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", required=True, help="Regex gegen den Tokentext (lower)")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    muster = re.compile(args.form)

    offen_formen = Counter()
    offen_dateien = Counter()
    offen_prior = Counter()
    offen_vers = Counter()
    annot_lemma = Counter()
    annot_typ = Counter()
    annot_formen = Counter()
    lemma_pos = Counter()
    # (Schreibung, Lemma) -> Variantentyp: genau diese Zuordnung braucht das
    # Anwendungs-Skript einer Serie, um @corresp setzen zu koennen.
    zuordnung = Counter()

    for f in corpus_files():
        for w in etree.parse(str(f)).iter(W_TAG):
            form = norm("".join(w.itertext()))
            if not muster.match(form.lower()):
                continue
            lemmata = [c.split("#")[-1] for c in (w.get("lemmaRef") or "").split()]
            if lemmata:
                for lid in lemmata:
                    annot_lemma[lid] += 1
                    lemma_pos[(lid, w.get("pos") or "-")] += 1
                annot_formen[form.lower()] += 1
                typen = [c.split("#")[-1] for c in (w.get("corresp") or "").split()]
                for c in typen:
                    annot_typ[c] += 1
                for lid in lemmata:
                    zuordnung[(form.lower(), lid, "|".join(typen) or "-")] += 1
                continue
            offen_formen[form.lower()] += 1
            offen_dateien[f.name] += 1
            offen_prior[w.get("pos") or "(ohne)"] += 1
            el = w.getparent()
            while el is not None and el.tag != L_TAG:
                el = el.getparent()
            offen_vers["vers" if el is not None else "prosa"] += 1

    offen = sum(offen_formen.values())
    print("Muster:", esc(args.form))
    print()
    print("UNANNOTIERT (kein @lemmaRef): %d Tokens in %d Texten"
          % (offen, len(offen_dateien)))
    print("  Schreibungen:")
    for fo, n in offen_formen.most_common(args.top):
        print("     %-16s %6d" % (esc(fo), n))
    print("  Vers/Prosa:", dict(offen_vers))
    print("  @pos als Prior:", dict(offen_prior.most_common(8)))
    print("  groesste Texte:", dict(offen_dateien.most_common(8)))
    print()
    print("ANNOTIERT: %d Tokens, %d Schreibungen" % (sum(annot_formen.values()),
                                                     len(annot_formen)))
    print("  Lemma-Kandidaten (die Praxis im Korpus):")
    for lid, n in annot_lemma.most_common(args.top):
        posse = {p: c for (l_, p), c in lemma_pos.items() if l_ == lid}
        print("     %-16s %6d   pos: %s" % (lid, n, posse))
    print("  Variantentypen:", dict(annot_typ.most_common(args.top)))
    print()
    print("ZUORDNUNG (Schreibung, Lemma) -> Variantentyp, so wie das Korpus sie uebt:")
    for (fo, lid, typ), n in zuordnung.most_common(args.top * 2):
        print("     %-14s %-14s %-16s %6d" % (esc(fo), lid, typ, n))
    mehrdeutig = {}
    for (fo, lid, typ), n in zuordnung.items():
        mehrdeutig.setdefault((fo, lid), set()).add(typ)
    strittig = {k: v for k, v in mehrdeutig.items() if len(v) > 1}
    print("  Paare mit mehr als einem Typ (muessen vor dem Batch geklaert werden):",
          len(strittig))
    for (fo, lid), typen in list(strittig.items())[:8]:
        print("     %-14s %-14s %s" % (esc(fo), lid, sorted(typen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
