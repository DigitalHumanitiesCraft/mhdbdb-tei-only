#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entscheidungsvorlage aus einer vorgegebenen Liste von Token-IDs bauen.

extract-367-waeren.py sammelt seine Faelle selbst ueber eine Zaehlvorschrift.
Hier ist die Auswahl schon getroffen, meist von einem Menschen im Issue-Thread,
und gebraucht wird nur noch die Aufbereitung: je Fall Sigle, xml:id, Schreibung,
aktueller Variantentyp, Versnummer sowie Vorvers, Zielvers und Folgevers mit
fett markiertem Zielwort. Format und Spalten wie faelle.csv aus #367, damit die
Vorlage ohne Blick ins TEI ausfuellbar ist.

Eingabe ist eine Textdatei, eine Zeile je Fall:

    SL_851_3;eindeutig
    TIT_50020_2;zu-lesen

Der Teil nach dem Semikolon ist frei und landet in der Spalte 'kategorie';
fehlt er, bleibt die Spalte leer. Zeilen, die mit # beginnen, und Leerzeilen
werden uebersprungen.

Das Skript prueft, dass jede ID genau einmal im Korpus vorkommt, und bricht ab,
wenn eine fehlt: eine Liste aus einem Issue ist eine Behauptung, keine Messung.
Zusaetzlich wird der Ist-Zustand jedes Tokens mitgeschrieben (lemmaRef, pos,
ana), damit im Review sichtbar ist, wovon aus umannotiert wird.

Usage:
    python scripts/ingest/pos-disambig/extract-cases-by-id.py \
        --ids ingest/pos-disambig/<ordner>/ids.txt \
        --out ingest/pos-disambig/<ordner>/faelle.csv
"""
import argparse
import csv
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

SPALTEN = ["file", "xml_id", "form", "corresp", "vers_n", "vorvers", "vers",
           "folgevers", "ist_lemmaRef", "ist_pos", "ist_ana", "kategorie",
           "entscheidung", "anmerkung"]


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def sigle(xid):
    """Sigle einer Token-ID: alles vor dem ERSTEN Unterstrich.

    Nicht von hinten abschneiden. Bis zum 2026-08-31 stand hier
    rsplit("_", 2)[0], was genau zwei Unterstriche voraussetzt. Die WZB hat
    mehr (WZB_1ra_2_1 ergab WZB_1ra), damit wurde tei/WZB.tei.xml
    uebersprungen und das Skript meldete, die ID sei nicht im Korpus: das
    Gegenteil des Sachverhalts, und ausgerechnet fuer den groessten aktiven
    Ingest. Gemessen am 2026-08-31: 149.165 <w>-IDs mit drei und mehr
    Unterstrichen, davon 149.130 mit genau drei und 35 mit vier
    (etwa WZB_56va_1_0_1), alle in WZB.tei.xml. Keine der 667 Korpusdateien
    traegt einen Unterstrich im Namen, und bis zu zwei Unterstrichen liefern
    beide Ableitungen dasselbe. Die Ableitung von vorn ist damit fuer jede
    Sigle korrekt und fuer die uebrigen 666 Texte aequivalent zur alten.
    """
    return xid.split("_", 1)[0]


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
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    reihenfolge = []
    kategorie = {}
    for zeile in pfad(args.ids).read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#"):
            continue
        xid, _, kat = zeile.partition(";")
        xid = xid.strip()
        if xid in kategorie:
            sys.exit("FEHLER: ID doppelt in der Eingabeliste: %s" % xid)
        reihenfolge.append(xid)
        kategorie[xid] = kat.strip()

    # Nur die Dateien parsen, deren Sigle in der Liste vorkommt.
    siglen = {sigle(x) for x in reihenfolge}
    gefunden = {}
    for fp in corpus_files():
        if fp.name.split(".")[0] not in siglen:
            continue
        tree = etree.parse(str(fp))
        alle_l = list(tree.iter(L_TAG))
        for w in tree.iter(W_TAG):
            xid = w.get(XML_ID)
            if xid not in kategorie:
                continue
            if xid in gefunden:
                sys.exit("FEHLER: xml:id %s kommt mehrfach im Korpus vor" % xid)
            vers = w.getparent()
            while vers is not None and vers.tag != L_TAG:
                vers = vers.getparent()
            vor = nach = None
            if vers is not None and vers in alle_l:
                j = alle_l.index(vers)
                vor = alle_l[j - 1] if j > 0 else None
                nach = alle_l[j + 1] if j + 1 < len(alle_l) else None
            gefunden[xid] = {
                "file": fp.name,
                "xml_id": xid,
                "form": norm("".join(w.itertext())),
                "corresp": w.get("corresp") or "",
                "vers_n": vers.get("n") if vers is not None else "",
                "vorvers": vers_text(vor),
                "vers": vers_text(vers, xid),
                "folgevers": vers_text(nach),
                "ist_lemmaRef": w.get("lemmaRef") or "",
                "ist_pos": w.get("pos") or "",
                "ist_ana": w.get("ana") or "",
                "kategorie": kategorie[xid],
                "entscheidung": "",
                "anmerkung": "",
            }

    fehlend = [x for x in reihenfolge if x not in gefunden]
    if fehlend:
        sys.exit("FEHLER: %d von %d IDs nicht im Korpus gefunden: %s"
                 % (len(fehlend), len(reihenfolge), ", ".join(fehlend)))

    ziel = pfad(args.out)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with open(ziel, "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=SPALTEN, delimiter=";")
        wr.writeheader()
        wr.writerows(gefunden[x] for x in reihenfolge)

    print("Faelle: %d, alle im Korpus belegt" % len(reihenfolge))
    print("  Siglen:", dict(sorted(Counter(
        sigle(x) for x in reihenfolge).items())))
    print("  Schreibungen:", dict(Counter(gefunden[x]["form"] for x in reihenfolge)))
    print("  Ist-lemmaRef:", dict(Counter(gefunden[x]["ist_lemmaRef"] for x in reihenfolge)))
    print("  Ist-pos:", dict(Counter(gefunden[x]["ist_pos"] for x in reihenfolge)))
    print("  mit @ana:", sum(1 for x in reihenfolge if gefunden[x]["ist_ana"]))
    print("  Kategorien:", dict(Counter(kategorie.values())))
    print("  geschrieben:", ziel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
