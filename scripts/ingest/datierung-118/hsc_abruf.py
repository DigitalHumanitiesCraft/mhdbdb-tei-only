#!/usr/bin/env python3
"""Handschriftencensus-Abruf fuer die Datierung der Werke (#118).

Liest die Werke aus den TEI-Headern (msIdentifier/@corresp = works.xml#work_...)
und ihre HSC-Werk-ID aus works.xml (idno type="handschriftencensus", beide
URL-Formen http://www.handschriftencensus.de/werke/N und
https://handschriftencensus.de/werke/N). Die Aufloesung Sigle -> Werk geht nur
ueber @corresp, nie ueber die Sigle (CONTRACTS.md F.4).

Drei Stufen je Werk, alles in einen Cache (Dateiname = Schema unten):
  1. werke/N          (HTML)  -> werke_N.html   Handschrift-IDs aus href="/NNNN"
  2. werke/N.json             -> werke_N.json   Titel, vlverweis
  3. NNNN.json (je Handschrift, ueber alle Werke dedupliziert) -> NNNN.json

Gegenprobe: gnd[].werk_id der Handschrift muss das Werk enthalten, ueber das sie
erreicht wurde. Fehlt es, bricht das Skript nicht ab, sondern fuehrt das Paar
(werk_id, hs_id) in gegenprobe_fehlt und zaehlt es (Sammelhandschriften).

Schreibt nichts ausser in den Cache. Unbekannte Struktur (Schluessel
entstehungszeit, schreibsprache, gnd fehlt), 0 Handschrift-Links oder ein
Cache-Fehltreffer im --offline-Lauf sind harte Fehler.

Aufruf:
  python scripts/ingest/datierung-118/hsc_abruf.py --nur-zaehlen
  python scripts/ingest/datierung-118/hsc_abruf.py [--cache-dir temp/hsc-cache]
      [--offline] [--limit K] [--werk N]
"""
import argparse
import collections
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
USER_AGENT = ("MHDBDB-Datierung/0.1 (+https://github.com/DigitalHumanitiesCraft/"
              "mhdbdb-tei-only/issues/118)")
BASIS = "https://handschriftencensus.de"
MIN_ABSTAND = 1.0
VERSUCHE = 3

RE_CORRESP = re.compile(r'<msIdentifier\b[^>]*\bcorresp="works\.xml#([^"]+)"')
RE_SIGLE = re.compile(r'<idno\s+type="sigle"\s*>([^<]+)</idno>')
RE_HSC = re.compile(r'handschriftencensus\.de/werke/(\d+)\s*$')
RE_HS_LINK = re.compile(r'href="/(\d+)"')


class HarterFehler(Exception):
    """Abbruch mit Meldung; main() gibt sie aus und beendet mit Exit 1."""


def lese_tei_header(pfad):
    """Header-Text bis </teiHeader>, in Bloecken gelesen."""
    text = ""
    with open(pfad, "r", encoding="utf-8") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            text += block
            if "</teiHeader>" in text:
                return text.split("</teiHeader>")[0]
    raise HarterFehler(f"kein </teiHeader> in {pfad}")


def lade_works_hsc(repo=REPO):
    """work_xml_id -> HSC-Werk-ID (int), nur Werke mit handschriftencensus-idno."""
    from lxml import etree
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    xml_id = "{http://www.w3.org/XML/1998/namespace}id"
    baum = etree.parse(str(repo / "authority-files" / "works.xml"))
    ergebnis = {}
    for bibl in baum.iterfind(".//t:bibl", ns):
        wid = bibl.get(xml_id)
        if not wid or not wid.startswith("work_"):
            continue
        ids = set()
        for idno in bibl.iterfind("t:idno[@type='handschriftencensus']", ns):
            m = RE_HSC.search((idno.text or "").strip())
            if not m:
                raise HarterFehler(f"unbekannte HSC-URL in works.xml bei {wid}: {idno.text!r}")
            ids.add(int(m.group(1)))
        if len(ids) > 1:
            raise HarterFehler(f"mehrere HSC-IDs bei {wid}: {sorted(ids)}")
        if ids:
            ergebnis[wid] = ids.pop()
    return ergebnis


def lade_texte(repo=REPO):
    """Liste (sigle, work_xml_id) je TEI-Datei, aus dem Header (@corresp)."""
    texte = []
    for pfad in sorted((repo / "tei").glob("*.tei.xml")):
        kopf = lese_tei_header(pfad)
        corr = RE_CORRESP.findall(kopf)
        if len(corr) != 1:
            raise HarterFehler(f"{pfad}: {len(corr)} msIdentifier/@corresp statt 1")
        teil = kopf[kopf.index("<msIdentifier"):]
        teil = teil[:teil.index("</msIdentifier>")]
        sig = RE_SIGLE.findall(teil)
        if len(sig) != 1:
            raise HarterFehler(f"{pfad}: {len(sig)} idno type=sigle im msIdentifier statt 1")
        texte.append((sig[0].strip(), corr[0]))
    return texte


def werkliste(repo=REPO):
    """-> (werke, texte).

    werke: HSC-Werk-ID -> {"work_xml_ids": [...], "siglen": [...]}, sortiert
    numerisch nach HSC-ID. texte: Liste (sigle, work_xml_id, hsc_id oder None).
    """
    works = lade_works_hsc(repo)
    texte = []
    werke = {}
    for sigle, wid in lade_texte(repo):
        hsc = works.get(wid)
        texte.append((sigle, wid, hsc))
        if hsc is None:
            continue
        w = werke.setdefault(hsc, {"work_xml_ids": [], "siglen": []})
        if wid not in w["work_xml_ids"]:
            w["work_xml_ids"].append(wid)
        w["siglen"].append(sigle)
    return dict(sorted(werke.items())), texte


class Cache:
    """Datei-Cache mit hoeflichem Abruf; jede Datei wird hoechstens einmal geladen."""

    def __init__(self, verzeichnis, offline):
        self.verz = Path(verzeichnis)
        self.offline = offline
        self.letzte = 0.0
        self.anfragen = 0
        self.abgerufen = set()  # Dateinamen, die in diesem Lauf aus dem Netz kamen

    def pfad(self, name):
        return self.verz / name

    def hole(self, name, url):
        pfad = self.pfad(name)
        if pfad.is_file():
            return pfad.read_bytes()
        if self.offline:
            raise HarterFehler(f"Cache-Fehltreffer (--offline): {pfad}  (URL {url})")
        daten = self._netz(url)
        self.verz.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(daten)
        self.abgerufen.add(name)
        return daten

    def _netz(self, url):
        letzter = None
        for versuch in range(VERSUCHE):
            warte = self.letzte + MIN_ABSTAND * (2 ** versuch) - time.monotonic()
            if warte > 0:
                time.sleep(warte)
            self.letzte = time.monotonic()
            self.anfragen += 1
            if self.anfragen % 50 == 0:
                print(f"  ... {self.anfragen} Anfragen", file=sys.stderr)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    if r.status == 200:
                        return r.read()
                    letzter = f"HTTP {r.status}"
            except urllib.error.HTTPError as e:
                letzter = f"HTTP {e.code}"
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                letzter = repr(e)
        raise HarterFehler(f"Abruf fehlgeschlagen nach {VERSUCHE} Versuchen: {url} ({letzter})")


def lade_json(daten, pfad, pflicht):
    try:
        obj = json.loads(daten.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HarterFehler(f"kein gueltiges JSON: {pfad} ({e})")
    if not isinstance(obj, dict):
        raise HarterFehler(f"JSON ist kein Objekt: {pfad}")
    fehlt = [k for k in pflicht if k not in obj]
    if fehlt:
        raise HarterFehler(f"unbekannte Struktur, Schluessel fehlt {fehlt}: {pfad}")
    return obj


def werk_stufe12(cache, werk_id):
    """-> (liste der Handschrift-IDs in Reihenfolge, werk-json)."""
    name = f"werke_{werk_id}.html"
    html = cache.hole(name, f"{BASIS}/werke/{werk_id}")
    ids = []
    for m in RE_HS_LINK.findall(html.decode("utf-8")):
        if m not in ids:
            ids.append(m)
    if not ids:
        raise HarterFehler(f"Werk {werk_id}: kein Handschrift-Link in {cache.pfad(name)}")
    name_j = f"werke_{werk_id}.json"
    wj = lade_json(cache.hole(name_j, f"{BASIS}/werke/{werk_id}.json"),
                   cache.pfad(name_j), ["titel", "vlverweis"])
    return [int(i) for i in ids], wj


def hs_stufe3(cache, hs_id):
    name = f"{hs_id}.json"
    return lade_json(cache.hole(name, f"{BASIS}/{hs_id}.json"), cache.pfad(name),
                     ["entstehungszeit", "schreibsprache", "gnd"])


def gnd_werk_ids(hs):
    """Menge der werk_id aus gnd[] (leer bei null/Liste ohne Eintraege)."""
    gnd = hs["gnd"] or []
    return {int(g["werk_id"]) for g in gnd if isinstance(g, dict) and g.get("werk_id") is not None}


def lauf(werke, cache):
    """Ruft alle Stufen fuer die gegebenen Werke ab.

    -> dict mit werk_hss (werk -> [hs_id]), werk_json, hs_json, gegenprobe_fehlt,
    werke_netz (Werke, fuer die mindestens eine Datei aus dem Netz kam).
    """
    werk_hss, werk_json, werke_netz = {}, {}, set()
    for wid in werke:
        vorher = set(cache.abgerufen)
        werk_hss[wid], werk_json[wid] = werk_stufe12(cache, wid)
        if cache.abgerufen - vorher:
            werke_netz.add(wid)
    hs_json = {}
    for wid in werke:
        for hid in werk_hss[wid]:
            if hid not in hs_json:
                hs_json[hid] = hs_stufe3(cache, hid)
    gegenprobe_fehlt = []
    for wid in werke:
        for hid in werk_hss[wid]:
            if wid not in gnd_werk_ids(hs_json[hid]):
                gegenprobe_fehlt.append((wid, hid))
    return {"werk_hss": werk_hss, "werk_json": werk_json, "hs_json": hs_json,
            "gegenprobe_fehlt": gegenprobe_fehlt, "werke_netz": werke_netz}


def waehle_werke(werke, limit, werk):
    ids = list(werke)
    if werk is not None:
        if werk not in werke:
            raise HarterFehler(f"HSC-Werk {werk} kommt in den TEI-Header-Werken nicht vor")
        return [werk]
    if limit is not None:
        return ids[:limit]
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser(description="Handschriftencensus-Abruf (#118)")
    ap.add_argument("--cache-dir", default=str(REPO / "temp" / "hsc-cache"))
    ap.add_argument("--offline", action="store_true", help="kein Netz, Cache-Fehltreffer = Abbruch")
    ap.add_argument("--limit", type=int, help="nur die ersten K Werke (numerisch nach HSC-ID)")
    ap.add_argument("--werk", type=int, help="nur dieses HSC-Werk")
    ap.add_argument("--nur-zaehlen", action="store_true", help="nur die Werkliste zaehlen")
    a = ap.parse_args(argv)
    try:
        werke, texte = werkliste()
        mit = sum(1 for t in texte if t[2] is not None)
        if a.nur_zaehlen:
            print(f"Werke mit HSC-ID: {len(werke)} (aus {mit} Texten mit HSC-Werk "
                  f"von {len(texte)} Texten, {len(texte) - mit} ohne)")
            return 0
        auswahl = waehle_werke(werke, a.limit, a.werk)
        cache = Cache(a.cache_dir, a.offline)
        erg = lauf(auswahl, cache)
    except HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1
    alle = [h for w in auswahl for h in erg["werk_hss"][w]]
    mehrfach = sum(1 for n in collections.Counter(alle).values() if n > 1)
    netz = len(erg["werke_netz"])
    print(f"Werke: {len(auswahl)} (abgerufen {netz} + Cache {len(auswahl) - netz}), "
          f"Handschriften: {len(erg['hs_json'])} (davon {mehrfach} in mehreren Werken), "
          f"Gegenprobe fehlt: {len(erg['gegenprobe_fehlt'])} (von {len(alle)} Paaren), "
          f"Parsefehler: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
