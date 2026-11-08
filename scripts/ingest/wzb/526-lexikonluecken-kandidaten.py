#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#526: Lexikonluecken der WZB-Breve-Faelle, nur MESSEN.

Frage (chsteiner 08.10.): Wie viele der 109 Zeilen mit review_grund=
lemma-kein-treffer in ingest/wzb/526-breve/review-faelle.csv gehoeren zu einem
vorhandenen Lemma mit anderer Schreibung? Das Skript annotiert nichts, aendert
weder tei/ noch authority-files/ und entscheidet nichts. Es legt je Zeile
Kandidaten vor, die ein Mensch liest.

FESTE REGEL (steht auch als Kopfkommentar in der Ausgabe-CSV):
  Basis: normalize_mhg (scripts/mhg_normalizer.py; Breve o/u -> oe/ue, n/w-Breve
  getilgt). Danach werden beide Seiten kanonisiert, in dieser Reihenfolge:
    sch->sh, cz->z, ck->k, kk->k, ey->ei, y->i, oe->o, v->u, f->u
  (Aequivalenzen mit Kosten 0: o/oe, kk=ck=k, v=f=u, y=i, ey=ei, cz=z, sch=sh).
  Klasse "distanz": Levenshtein-Distanz <= 1 (Einfuegen, Loeschen, Ersetzen je
  Kosten 1) zwischen den kanonisierten Formen.
  Klasse "flexion-moeglich": ein Kandidat (normalisiert, ohne weitere
  Kanonisierung, mindestens 3 Zeichen) ist echtes Praefix der normalisierten
  Form, der Rest ist eines von e en er es em n s t et est.
  Kandidatenquellen: alle <orth> in authority-files/lexicon.xml (Lemma =
  entry/@xml:id) und alle <form> in authority-files/variants.xml (Lemma =
  entry/@corresp).
Einstufung je Zeile:
  kandidat-eindeutig   Distanzklasse trifft genau ein Lemma
  kandidat-mehrdeutig  Distanzklasse trifft mehrere Lemmata
  nur-flexion          nur, wenn die Distanzklasse leer ist und die Flexionsklasse
                       trifft (heute 0 Zeilen; Flexionstreffer neben einem
                       Distanzkandidaten stehen nicht in der Ausgabe)
  kein-kandidat        beides leer
Eine Einstufung ist ein Kandidatenhinweis, keine Zuordnung: Praezision liest
der Mensch an der Fundstelle.

Harte Fehler: Summe der Zeilen ungleich 109, ein Token fehlt im TEI oder traegt
inzwischen @lemmaRef, ein lexicon-entry ohne xml:id, ein variants-entry ohne
@corresp/@lemmaRef, ein Kandidat ohne Eintrag in lexicon.xml. Ein mehrteiliges
@corresp wird in Tokens zerlegt, alle Lemmata zaehlen.

Usage:
    python scripts/ingest/wzb/526-lexikonluecken-kandidaten.py
"""
import csv
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
from mhg_normalizer import normalize_mhg  # noqa: E402
from lxml import etree  # noqa: E402

TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
QUELLE = REPO / "ingest" / "wzb" / "526-breve" / "review-faelle.csv"
AUSGABE = REPO / "ingest" / "wzb" / "526-breve" / "lexikonluecken-kandidaten.csv"
WZB = REPO / "tei" / "WZB.tei.xml"
LEXICON = REPO / "authority-files" / "lexicon.xml"
VARIANTS = REPO / "authority-files" / "variants.xml"
ERWARTET = 109
GRUND = "lemma-kein-treffer"
ENDUNGEN = ("e", "en", "er", "es", "em", "n", "s", "t", "et", "est")
MIN_PRAEFIX = 3

REGEL = ("Regel: normalize_mhg, dann kanonisiert sch>sh cz>z ck>k kk>k ey>ei y>i "
         "oe>o v>u f>u; distanz = Levenshtein <= 1 auf kanonisierter Form; "
         "flexion-moeglich = Kandidat (normalisiert, >= 3 Zeichen) ist echtes "
         "Praefix, Rest in e en er es em n s t et est")
KANON = (("sch", "sh"), ("cz", "z"), ("ck", "k"), ("kk", "k"), ("ey", "ei"),
         ("y", "i"), ("oe", "o"), ("v", "u"), ("f", "u"))


def kanon(s):
    for a, b in KANON:
        s = s.replace(a, b)
    return s


def nfc(s):
    return unicodedata.normalize("NFC", s or "").strip()


def nachbarn(s, alphabet):
    """Alle Zeichenketten mit Distanz <= 1 zu s (inklusive s)."""
    aus = {s}
    for i in range(len(s) + 1):
        for c in alphabet:
            aus.add(s[:i] + c + s[i:])
        if i < len(s):
            aus.add(s[:i] + s[i + 1:])
            for c in alphabet:
                aus.add(s[:i] + c + s[i + 1:])
    return aus


def lade_kandidatenquellen():
    """-> (normalisiert -> {lemma}), (kanonisiert -> {lemma}), lemma -> orth."""
    norm = defaultdict(set)
    orth_von = {}
    for entry in etree.parse(str(LEXICON)).iter("{%s}entry" % TEI):
        lid = entry.get(XML_ID)
        if not lid:
            sys.exit("FEHLER: lexicon.xml: entry ohne xml:id (Zeile %s)" % entry.sourceline)
        for o in entry.iter("{%s}orth" % TEI):
            if o.text and o.text.strip():
                norm[normalize_mhg(o.text.strip())].add(lid)
                orth_von.setdefault(lid, nfc(o.text))
    for entry in etree.parse(str(VARIANTS)).iter("{%s}entry" % TEI):
        ref = entry.get("corresp") or entry.get("lemmaRef")
        if not ref or not ref.strip():
            sys.exit("FEHLER: variants.xml: entry ohne @corresp/@lemmaRef (Zeile %s)"
                     % entry.sourceline)
        lids = {t.split("#")[-1] for t in ref.split()}
        for f in entry.iter("{%s}form" % TEI):
            if f.text and f.text.strip():
                norm[normalize_mhg(f.text.strip())] |= lids
    kan = defaultdict(set)
    for k, ls in norm.items():
        kan[kanon(k)] |= ls
    return norm, kan, orth_von


def lade_faelle():
    with open(QUELLE, encoding="utf-8-sig", newline="") as fh:
        zeilen = list(csv.DictReader(fh, delimiter=";"))
    return [z for z in zeilen if z["review_grund"] == GRUND]


def pruefe_tei(faelle):
    ids = {z["xml_id"] for z in faelle}
    gefunden = {}
    for w in etree.parse(str(WZB)).iter("{%s}w" % TEI):
        xid = w.get(XML_ID)
        if xid in ids:
            gefunden[xid] = w.get("lemmaRef")
    fehlt = sorted(ids - set(gefunden))
    mit_ref = sorted(x for x, r in gefunden.items() if r)
    if fehlt or mit_ref:
        sys.exit("FEHLER: Token nicht im TEI %s oder inzwischen mit @lemmaRef %s"
                 % (fehlt[:5], mit_ref[:5]))


def main():
    faelle = lade_faelle()
    pruefe_tei(faelle)
    norm, kan, orth_von = lade_kandidatenquellen()
    alphabet = sorted({c for k in kan for c in k})
    norm_schluessel = [k for k in norm if len(k) >= MIN_PRAEFIX]

    cache = {}

    def kandidaten(normalisiert):
        if normalisiert in cache:
            return cache[normalisiert]
        dist = set()
        for n in nachbarn(kanon(normalisiert), alphabet):
            dist |= kan.get(n, set())
        flex = set()
        for k in norm_schluessel:
            if len(k) < len(normalisiert) and normalisiert.startswith(k) \
                    and normalisiert[len(k):] in ENDUNGEN:
                flex |= norm[k]
        flex -= dist
        cache[normalisiert] = (dist, flex)
        return cache[normalisiert]

    def lemma_nr(l):
        return int(l.split("_")[-1]) if l.split("_")[-1].isdigit() else 0

    def fmt(ls):
        fehlt = sorted(l for l in ls if l not in orth_von)
        if fehlt:
            sys.exit("FEHLER: Kandidat ohne Eintrag in lexicon.xml: %s" % fehlt[:5])
        return "|".join("%s:%s" % (l, orth_von[l]) for l in sorted(ls, key=lemma_nr))

    ausgabe = []
    for z in faelle:
        form = nfc(z["form"])
        n = normalize_mhg(form)
        dist, flex = kandidaten(n)
        if len(dist) == 1:
            klasse, kand = "kandidat-eindeutig", dist
        elif dist:
            klasse, kand = "kandidat-mehrdeutig", dist
        elif flex:
            klasse, kand = "nur-flexion", flex
        else:
            klasse, kand = "kein-kandidat", set()
        ausgabe.append((z["xml_id"], form, n, klasse, fmt(kand)))
    ausgabe.sort()

    summe = len(ausgabe)
    formen = len({a[1] for a in ausgabe})
    formen_norm = len({a[2] for a in ausgabe})
    if summe != ERWARTET:
        sys.exit("FEHLER: %d Zeilen statt %d" % (summe, ERWARTET))

    with open(AUSGABE, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("# %s\n" % REGEL)
        w = csv.writer(fh, delimiter=";", lineterminator="\n")
        w.writerow(["xml_id", "form", "normalisiert", "klasse", "kandidaten", "regel"])
        for a in ausgabe:
            w.writerow(list(a) + ["distanz<=1" if a[3].startswith("kandidat") else
                                  ("flexion-moeglich" if a[3] == "nur-flexion" else "")])

    for k in ("kandidat-eindeutig", "kandidat-mehrdeutig", "nur-flexion", "kein-kandidat"):
        zl = [a for a in ausgabe if a[3] == k]
        print("%s: %d Zeilen (%d Schreibungen, %d normalisiert)"
              % (k, len(zl), len({a[1] for a in zl}), len({a[2] for a in zl})))
    print("Gesamt: %d Zeilen (%d Schreibungen, %d normalisiert)" % (summe, formen, formen_norm))


if __name__ == "__main__":
    main()
