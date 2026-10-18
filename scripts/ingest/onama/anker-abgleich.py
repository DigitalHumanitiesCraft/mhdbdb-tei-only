#!/usr/bin/env python3
"""ONAMA-Anker-Abgleich (#609, Paket O1).

Liest onamaObjects.ttl (ONAMA-Korpus) und prueft jede Textpassage gegen die
xml:id-Werte im MHDBDB-TEI. Das Skript aendert nichts an tei/ oder
authority-files/; es schreibt nur den Bericht.

Reproduktionsprinzip (Manifest 16.10.2026, Abschnitt 8):
  1. Turtle mit rdflib lesen (Abhaengigkeit: rdflib, nicht in requirements.txt,
     weil die nur die Build-Kette pinnt; gemessen mit 7.6.0).
  2. Alle Ressourcen mit rdf:type onama:TextPassage (Namensraum
     http://onama.sbg.ac.at/ontology#), je fromToken und toToken.
  3. TEI-Datei aus der Sigle (Teil vor dem ersten "_"), exakter xml:id-Treffer
     auf <w> oder <pc> im <body>. Keine Leerzeichen entfernt, keine IDs
     ergaenzt, nichts repariert.
  4. Elementtyp und Dokumentreihenfolge; Umrechnung in MHDBDB-Wortpositionen
     nur ueber <w> mit nicht-leerem @lemmaRef und nicht-leerem Text
     (CONTRACTS.md Abschnitt B, build-corpus-index.py extract_word_data).

Statusklassen (je Spanne genau eine, in dieser Rangfolge):
  nicht_gefunden  mindestens ein Endpunkt ist kein exakter xml:id-Treffer
  umgekehrt       beide gefunden, aber der Endpunkt liegt vor dem Startpunkt
  nichtwort_anker mindestens ein Endpunkt ist kein <w> (<pc>, <caesura>, ...)
  wortanker       beide Endpunkte sind <w> in richtiger Reihenfolge
Ob ein <w> von der Positionszaehlung gezaehlt wird (lemmaRef und Text), steht
quer dazu im Endpunkt ("wortposition": null = nicht gezaehlt) und im Bericht
unter mit_ungezaehltem_wort_als_endpunkt.
Die Platzhalter-Aussage (fromToken/toToken auf einer Ressource, die keine
TextPassage ist, etwa Q67 mit AXU_XXXX) steht in eigener Liste "ausserhalb".

Aufruf (Quelle in ein eigenes leeres Verzeichnis ausserhalb des Repos laden):
  python scripts/ingest/onama/anker-abgleich.py --ttl <pfad>/onamaObjects.ttl \\
      --ttl-commit b87468b96e49a8899f15efc8ccb281ac11bb7e07 \\
      --out playground/data/onama/anker-abgleich.json
"""
import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

import rdflib
from lxml import etree

REPO = Path(__file__).resolve().parents[3]
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ONAMA = rdflib.Namespace("http://onama.sbg.ac.at/ontology#")
TEI_DIR = REPO / "tei"


def lade_tei(sigle, cache):
    """xml:id -> (dokumentindex, tag, wortposition oder None) fuer <w>/<pc> im body.

    Die Wortposition zaehlt wie build-corpus-index.py: nur <w> mit lemmaRef und Text.
    Zusaetzlich naechste_pos[i]: Position des ersten gezaehlten Wortes ab Index i
    (sonst None), vorige_pos[i]: des letzten gezaehlten Wortes bis Index i.
    """
    if sigle in cache:
        return cache[sigle]
    pfad = TEI_DIR / f"{sigle}.tei.xml"
    if not pfad.is_file():
        cache[sigle] = None
        return None
    baum = etree.parse(str(pfad))
    body = baum.find(f".//{{{TEI_NS}}}body")
    ids = {}
    doppelt = set()
    pos_je_index = []
    wortzahl = 0
    for el in body.iter("*"):
        idx = len(pos_je_index)
        wortpos = None
        if el.tag == f"{{{TEI_NS}}}w":
            if el.get("lemmaRef") and "".join(el.itertext()).strip():
                wortpos = wortzahl
                wortzahl += 1
        pos_je_index.append(wortpos)
        xid = el.get(XML_ID)
        if xid:
            if xid in ids:
                doppelt.add(xid)
            ids[xid] = (idx, etree.QName(el).localname, wortpos)
    vorige = []
    letzte = None
    for p in pos_je_index:
        if p is not None:
            letzte = p
        vorige.append(letzte)
    naechste = [None] * len(pos_je_index)
    kommende = None
    for i in range(len(pos_je_index) - 1, -1, -1):
        if pos_je_index[i] is not None:
            kommende = pos_je_index[i]
        naechste[i] = kommende
    cache[sigle] = {"ids": ids, "doppelt": doppelt, "vorige": vorige,
                    "naechste": naechste, "woerter": wortzahl}
    return cache[sigle]


def anker(token, cache):
    """Ein Endpunkt -> Beschreibung; nichts wird repariert."""
    sigle = token.split("_", 1)[0]
    info = lade_tei(sigle, cache)
    out = {"original": token, "sigle": sigle, "gefunden": False}
    if info is None:
        out["grund"] = "keine TEI-Datei zur Sigle"
        return out
    treffer = info["ids"].get(token)
    if treffer is None:
        out["grund"] = "kein exakter xml:id-Treffer"
        return out
    idx, tag, wortpos = treffer
    out.update(gefunden=True, element=tag, index=idx, wortposition=wortpos)
    if token in info["doppelt"]:
        out["warnung"] = "xml:id kommt mehrfach vor"
    return out


def klassifiziere(von, bis, cache):
    if not (von["gefunden"] and bis["gefunden"]):
        return "nicht_gefunden", None
    if von["sigle"] != bis["sigle"]:
        return "nicht_gefunden", "Endpunkte in verschiedenen Texten"
    if bis["index"] < von["index"]:
        return "umgekehrt", None
    if von["element"] != "w" or bis["element"] != "w":
        return "nichtwort_anker", None
    return "wortanker", None


def wortspanne(von, bis, cache):
    """Umrechnung in MHDBDB-Wortpositionen (inklusive Grenzen).

    Wortanker: die eigenen Positionen. Nichtwort-Anker: Start rueckt auf das
    naechste gezaehlte Wort danach, Ende auf das letzte gezaehlte Wort davor.
    """
    info = cache[von["sigle"]]
    ab = von["wortposition"]
    if ab is None:
        ab = info["naechste"][von["index"]]
    bis_pos = bis["wortposition"]
    if bis_pos is None:
        bis_pos = info["vorige"][bis["index"]]
    if ab is None or bis_pos is None or bis_pos < ab:
        return None
    return [ab, bis_pos]


def git_kopf():
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ttl", required=True, type=Path)
    ap.add_argument("--ttl-commit", required=True, help="Commit des onama-corpus, aus dem die Datei stammt")
    ap.add_argument("--mhdbdb-commit", default=None, help="Standard: HEAD dieses Repos")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    g = rdflib.Graph()
    g.parse(str(args.ttl), format="turtle")
    passagen = set(g.subjects(rdflib.RDF.type, ONAMA.TextPassage))
    von_bis = {}
    for s in set(g.subjects(ONAMA.fromToken, None)) | set(g.subjects(ONAMA.toToken, None)):
        von = list(g.objects(s, ONAMA.fromToken))
        bis = list(g.objects(s, ONAMA.toToken))
        if len(von) != 1 or len(bis) != 1:
            sys.exit(f"harter Fehler: {s} hat {len(von)} fromToken und {len(bis)} toToken")
        von_bis[s] = (str(von[0]), str(bis[0]))
    if not passagen <= set(von_bis):
        sys.exit("harter Fehler: TextPassage ohne fromToken/toToken")

    cache = {}
    eintraege = []
    ausserhalb = []
    for s in sorted(von_bis, key=str):
        von = anker(von_bis[s][0], cache)
        bis = anker(von_bis[s][1], cache)
        realisierungen = sorted(str(r) for r in g.subjects(ONAMA.hasTextPassage, s))
        typen = sorted(str(t).split("#")[-1] for t in g.objects(s, rdflib.RDF.type))
        eintrag = {"uri": str(s), "typen": typen, "realisierungen": realisierungen,
                   "von": von, "bis": bis}
        if s in passagen:
            status, notiz = klassifiziere(von, bis, cache)
            eintrag["status"] = status
            if notiz:
                eintrag["notiz"] = notiz
            if status in ("wortanker", "nichtwort_anker"):
                eintrag["wortspanne"] = wortspanne(von, bis, cache)
            eintraege.append(eintrag)
        else:
            eintrag["status"] = "ausserhalb_textpassage"
            eintrag["label"] = sorted(str(x) for x in g.objects(s, rdflib.RDFS.label))
            ausserhalb.append(eintrag)

    summe = collections.Counter(e["status"] for e in eintraege)
    # Gegenprobe: die Summe der Klassen muss die Menge der Passagen sein.
    assert sum(summe.values()) == len(passagen), (summe, len(passagen))
    nichtwort_arten = collections.Counter(
        a["element"] for e in eintraege if e["status"] == "nichtwort_anker"
        for a in (e["von"], e["bis"]) if a["element"] != "w")
    # Woerter als Endpunkt, die die Positionszaehlung nicht zaehlt (ohne lemmaRef).
    ungezaehlt = collections.Counter(
        e["status"] for e in eintraege if e["status"] in ("wortanker", "nichtwort_anker")
        and any(a["element"] == "w" and a["wortposition"] is None for a in (e["von"], e["bis"])))
    visuell = [e["uri"] for e in eintraege if "VisualRealisation" in
               {str(t).split("#")[-1] for r in e["realisierungen"]
                for t in g.objects(rdflib.URIRef(r), rdflib.RDF.type)}]

    bericht = {
        "eingaben": {
            "onama_corpus_commit": args.ttl_commit,
            "onama_datei": args.ttl.name,
            "mhdbdb_commit": args.mhdbdb_commit or git_kopf(),
            "tripel": len(g),
        },
        "zaehlung": {
            "textpassagen": len(passagen),
            "klassen": dict(sorted(summe.items())),
            "nichtwort_endpunkte_je_element": dict(nichtwort_arten),
            "mit_ungezaehltem_wort_als_endpunkt": dict(ungezaehlt),
            "von_bis_aussagen_gesamt": len(von_bis),
            "ausserhalb_textpassage": len(ausserhalb),
            "passagen_an_visueller_realisierung": visuell,
        },
        "passagen": eintraege,
        "ausserhalb": ausserhalb,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bericht, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Tripel {len(g)}, Textpassagen {len(passagen)}, "
          f"von/bis-Aussagen {len(von_bis)} ({len(passagen)}+{len(ausserhalb)})")
    for k, v in sorted(summe.items()):
        print(f"  {k}: {v}/{len(passagen)}")
    print(f"  Nichtwort-Endpunkte je Element: {dict(nichtwort_arten)}")
    print(f"  mit Wort ohne lemmaRef/Text als Endpunkt (ungezaehlt): {dict(ungezaehlt)}")


if __name__ == "__main__":
    main()
