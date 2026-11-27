#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legt fuer Eintraege aus der Zotero-Sammlung "Eigene Publikationen" (WB4HTUGC)
Zenodo-ENTWUERFE an: ein Stub-Record pro Eintrag, mit Vollzitat im
Beschreibungsfeld und in der Datei zitation_<id>.txt, in der Community mhdbdb.

    python scripts/sync/zotero-zu-zenodo.py                   # Trockenlauf
    python scripts/sync/zotero-zu-zenodo.py --write           # legt Entwuerfe an
    python scripts/sync/zotero-zu-zenodo.py --bericht temp/zenodo.md

Veroeffentlicht wird NIE hier. Eine DOI laesst sich nicht zurueckholen; die
Entwuerfe prueft und veroeffentlicht ein Mensch in der Zenodo-Oberflaeche.

Aussenwirkung
-------------
Das Skript fasst weder `tei/` noch `authority-files/` an und erzeugt keine
abgeleiteten Daten, loest also KEINEN Index-Rebuild aus. Einziges Schreibziel
sind neue, unveroeffentlichte Zenodo-Entwuerfe. Bestehende Records und Zotero
bleiben unveraendert. MAX_NEU deckelt einen Lauf.

Zugangsdaten (nur aus der Umgebung, nie aus einer Datei im Repo)
    ZENODO_TOKEN   Pflicht, auch im Trockenlauf (die Entwuerfe sind nur mit
                   Token lesbar). Fuer --write genuegt deposit:write, das
                   Recht deposit:actions wird NICHT gebraucht.
Zotero wird nur gelesen; die Gruppe ist ohne Schluessel lesbar, ein optionaler
ZOTERO_API_KEY wird mitgeschickt, falls gesetzt.

Was als "schon vorhanden" gilt
------------------------------
Ein Zotero-Eintrag hat schon einen Record, wenn (1) irgendein Record im Konto
seinen Zotero-Schluessel im Feld "Notes" traegt ("Zotero-Schluessel: ABCD1234",
das schreibt dieses Skript selbst), oder (2) seine DOI in einem Record als
verwandte Kennung steht, oder (3) ein VEROEFFENTLICHTER Record der Community
denselben Titel hat. Unveroeffentlichte Entwuerfe ohne Schluessel zaehlen nie:
sonst verdeckt jeder Altentwurf, dass etwas fehlt.

Was nicht angelegt wird (und im Bericht steht)
----------------------------------------------
- Eintraege mit dem Vermerk "Automatisch gefunden" im Feld Extra: sie kommen
  aus find-mentions.py und sind nicht gegen die Quelle geprueft. Der Vermerk
  muss in Zotero erst entfernt werden.
- Eintraege, deren Zenodo-DOI auf einen eigenen Record mit demselben Titel
  zeigt (born-Zenodo): sie haben ihren Record schon.
- Eintraege, deren Angaben dem DOI-Register widersprechen (Autor:innen oder
  Datum). Das ist kein Schoenheitsfehler: Zotero hatte zum Beispiel bei einem
  Blogpost ein falsches Datum und bei dreien falsch befuellte Autorenfelder.
  Zurueckgehalten wird, bis Zotero stimmt.

Exit-Status
-----------
0 nur, wenn nichts offen blieb. Steht etwas in PROBLEME, wurde etwas
zurueckgehalten (Abweichung zum DOI-Register) oder hat MAX_NEU Eintraege
abgeschnitten, endet der Lauf mit 1: die unbeaufsichtigte Routine sieht nur den
Status. Eine leere Ergebnisliste heisst nur dann "nichts Neues", wenn PROBLEME
leer ist. Gleiches Prinzip wie in find-mentions.py: eine Abfrage, die nicht
geantwortet hat, ist ein Problem und kein Nullbefund.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

# find-mentions.py liefert get() (Wiederholung, None bei Nichtantwort) und clean_doi()
_spec = importlib.util.spec_from_file_location(
    "find_mentions", Path(__file__).with_name("find-mentions.py"))
FM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FM)

COL_EIGENE = "WB4HTUGC"              # Eigene Publikationen
COMMUNITY = "mhdbdb"
ZENODO = "https://zenodo.org/api"
MAX_NEU = 10
ABRUF = None                          # Datum des Laufs, in main() gesetzt

PROBLEME = []                         # macht den Lauf unvollstaendig (Exit 1)
ABWEICHUNGEN = []                     # zurueckgehaltene Eintraege (Exit 1)

MONATE = ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

# Bekannte Personen mit ORCID und Affiliation (beides oeffentlich, vom Team
# so gewuenscht). Schluessel ist die Anzeigeform "Vorname Nachname".
PERSONEN = {
    "Katharina Zeppezauer-Wachauer": {
        "orcid": "0000-0001-9310-9029", "affiliation": "University of Salzburg"},
}

TYP_PUBLIKATION = {
    "journalArticle": "article", "bookSection": "section", "book": "book",
    "thesis": "thesis", "conferencePaper": "conferencepaper",
    "preprint": "preprint", "report": "report",
}
SPRACHEN = {"de": "deu", "en": "eng", "fr": "fra", "it": "ita", "es": "spa"}
TEILCHEN = {"van", "von", "de", "der", "den", "del", "di", "da", "zu", "zur"}
# Nur Arbeiten dieser Personen werden angelegt (Teilzeichenkette der Anzeigeform,
# kleingeschrieben). "christian steiner" voll ausgeschrieben, weil es in der
# Gruppe auch eine Elisabeth Steiner gibt.
TEAM = ("zeppezauer", "wachauer", "van beek", "hintersteiner",
        "christian steiner", "beutel-thurow")
SEIT = "2024-01-01"                   # aelter wird nicht automatisch angelegt
ZENODO_DOI = re.compile(r"^10\.5281/zenodo\.(\d+)$")
SCHLUESSEL = re.compile(r"Zotero-Schluessel:\s*([A-Z0-9]{8})")


def norm(s):
    return FM.norm(s or "")


def kennung(s):
    """Normalform einer verwandten Kennung: DOIs ohne Praefix, URLs unveraendert
    (nur kleingeschrieben, ohne Schlussschraegstrich)."""
    s = (s or "").strip()
    d = FM.clean_doi(s)
    return d if re.match(r"^10\.\d{4,9}/", d) else s.lower().rstrip("/")


def doi_aus(item):
    d = FM.clean_doi(item.get("DOI") or "")
    if d:
        return d
    m = re.search(r"10\.\d{4,9}/[^\s\"<>,;]+", item.get("extra") or "")
    return FM.clean_doi(m.group(0)) if m else ""


# ------------------------------------------------------------------ Zotero
def zotero_eigene():
    """Alle Top-Level-Eintraege der Sammlung. Gegenprobe der gelesenen Anzahl
    gegen Total-Results; faellt etwas aus, ist die Liste lueckenhaft."""
    kopfzeilen = {"Zotero-API-Version": "3", **FM.UA}
    if os.environ.get("ZOTERO_API_KEY"):
        kopfzeilen["Zotero-API-Key"] = os.environ["ZOTERO_API_KEY"]
    eintraege, start, erwartet = [], 0, None
    while True:
        antwort = FM.get(
            f"https://api.zotero.org/groups/{FM.GROUP}/collections/{COL_EIGENE}"
            f"/items/top?format=json&limit=100&start={start}",
            headers=kopfzeilen, kopf=True)
        if antwort is None:
            PROBLEME.append(f"Zotero: Seite ab Eintrag {start} nicht abrufbar, "
                            "die Liste ist lueckenhaft.")
            return eintraege, False
        daten, kopf = antwort
        if erwartet is None:
            try:
                erwartet = int(kopf["Total-Results"])
            except (KeyError, ValueError):
                erwartet = None
        if not daten:
            break
        eintraege += [d["data"] for d in daten]
        start += 100
    if erwartet is None:
        PROBLEME.append("Zotero: Gesamtzahl der Sammlung nicht abrufbar, die "
                        "Vollstaendigkeit ist ungeprueft.")
        return eintraege, False
    if len(eintraege) != erwartet:
        PROBLEME.append(f"Zotero: {len(eintraege)} von {erwartet} Eintraegen gelesen.")
        return eintraege, False
    return eintraege, True


# ------------------------------------------------------------------ Zenodo
def zenodo_konto(token):
    """Alle Records und Entwuerfe des Kontos (Legacy-API). Gibt eine Liste von
    Verzeichnissen mit Schluessel, DOIs, Titel, Status zurueck, oder None."""
    kopf = {"Authorization": f"Bearer {token}"}
    ergebnis, seite = [], 1
    while True:
        daten = FM.get(f"{ZENODO}/deposit/depositions?size=100&page={seite}"
                       "&sort=mostrecent", headers=kopf)
        if daten is None:
            PROBLEME.append(f"Zenodo: Konto-Liste Seite {seite} nicht abrufbar.")
            return None
        if not daten:
            break
        for d in daten:
            m = d.get("metadata", {})
            notiz = re.sub(r"<[^>]+>", " ", m.get("notes") or "")
            s = SCHLUESSEL.search(notiz)
            dois = {kennung(r.get("identifier", ""))
                    for r in (m.get("related_identifiers") or [])}
            if d.get("doi"):
                dois.add(FM.clean_doi(d["doi"]))
            comm = {c.get("identifier") for c in (m.get("communities") or [])}
            ergebnis.append({
                "id": d["id"], "veroeffentlicht": bool(d.get("submitted")),
                "titel": norm(m.get("title", "")), "schluessel": s.group(1) if s else "",
                "dois": dois, "community": COMMUNITY in comm})
        seite += 1
        if seite > 50:
            PROBLEME.append("Zenodo: Blaetter-Obergrenze erreicht, Rest ungelesen.")
            return None
    return ergebnis


def schon_da(item, konto):
    """Grund, warum der Eintrag schon einen Record hat, sonst ''."""
    doi = doi_aus(item)
    for k in konto:
        if k["schluessel"] == item["key"]:
            return f"Schluessel in Record {k['id']}"
    for kenn in (doi, kennung(item.get("url", ""))):
        if kenn:
            for k in konto:
                if kenn in k["dois"]:
                    return f"Kennung in Record {k['id']}"
    t = norm(item.get("title", ""))
    for k in konto:
        if k["veroeffentlicht"] and k["community"] and k["titel"] == t:
            return f"gleicher Titel, veroeffentlicht, Record {k['id']}"
    return ""


# ------------------------------------------------------------- Aufbereitung
def de_datum(iso):
    j, m, t = iso.split("-")
    return f"{int(t)}. {MONATE[int(m)]} {j}"


def iso_datum(s):
    """Zotero-Datum als YYYY-MM-DD; nur ein Jahr wird zu YYYY-01-01."""
    m = re.match(r"^\[?(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?", (s or "").strip())
    if not m:
        return ""
    return f"{m.group(1)}-{int(m.group(2) or 1):02d}-{int(m.group(3) or 1):02d}"


def ganzer_datumsteil(s):
    return bool(re.match(r"^\[?\d{4}-\d{1,2}-\d{1,2}", (s or "").strip()))


def anzeige(c):
    if c.get("name"):
        return c["name"].strip()
    return f"{c.get('firstName', '').strip()} {c.get('lastName', '').strip()}".strip()


def inversform(c):
    """'Nachname, Vorname'; Namensteilchen wie 'van' gehoeren zum Nachnamen."""
    if c.get("name"):
        return c["name"].strip()
    vor, nach = c.get("firstName", "").strip().split(), c.get("lastName", "").strip()
    while vor and vor[-1].lower() in TEILCHEN:
        nach = f"{vor.pop()} {nach}"
    return f"{nach}, {' '.join(vor)}".strip(", ")


def personen(item, typen):
    return [c for c in item.get("creators", []) if c.get("creatorType") in typen]


def ist_team(item):
    return any(t in anzeige(c).lower() for c in personen(item, ("author", "presenter"))
               for t in TEAM)


def mehrere_personen_in_einem_feld(item):
    """Gibt die Angabe zurueck, wenn ein Zotero-Personenfeld mehr als eine
    Person enthaelt ("A und B C"). Ein Registerabgleich allein findet das nicht:
    der Nachname steckt dann trotzdem in der Verfasserzeile. Reine Namensfelder
    (Institutionen) sind davon ausgenommen, solange sie kein "und" enthalten."""
    for c in personen(item, ("author", "presenter", "editor")):
        s = anzeige(c)
        if FM.KEINE_PERSON.search(s) or ";" in s or s.count(",") > 1:
            return s[:80]
        if not c.get("name") and len((c.get("firstName", "") + " " + c.get("lastName", "")).split()) > 5:
            return s[:80]
    return ""


def behaelter(item):
    t = item["itemType"]
    for feld in ("blogTitle", "publicationTitle", "encyclopediaTitle",
                 "websiteTitle", "proceedingsTitle", "forumTitle", "meetingName"):
        if item.get(feld):
            return item[feld]
    if t in ("book", "thesis", "report", "document"):
        return item.get("publisher") or item.get("university") or item.get("institution") or ""
    return ""


def vollzitat(item, url):
    aut = personen(item, ("author", "presenter"))
    iso = iso_datum(item.get("date"))
    wann = de_datum(iso) if ganzer_datumsteil(item.get("date")) else iso[:4]
    titel = item["title"].strip()
    titel = titel if titel[-1] in ".?!" else titel + "."
    kopf = f"{', '.join(anzeige(c) for c in aut)} ({wann}). {titel}"
    if item["itemType"] == "bookSection":
        hrsg = [anzeige(c) for c in personen(item, ("editor",))]
        teil = "In " + (", ".join(hrsg) + " (Hrsg.), " if hrsg else "") + item.get("bookTitle", "")
        if item.get("pages"):
            teil += f" (S. {item['pages'].replace('-', '–')})"
        teil += "."
        if item.get("publisher"):
            teil += f" {item['publisher']}."
        mitte = f" {teil}"
    else:
        b = behaelter(item)
        mitte = f" {b}." if b else ""
    return f"{kopf}{mitte} Abgerufen am {ABRUF} von {url}"


def stub_metadaten(item, url, zit, teil_von):
    aut = personen(item, ("author", "presenter"))
    creators = []
    for c in aut:
        e = {"name": inversform(c)}
        e.update(PERSONEN.get(anzeige(c), {}))
        creators.append(e)
    typ = TYP_PUBLIKATION.get(item["itemType"], "other")
    meta = {
        "upload_type": "presentation" if item["itemType"] == "presentation" else "publication",
        "title": item["title"].strip(),
        "description": ("<p>Bibliographischer Eintrag aus der MHDBDB-Sekundärliteratur "
                        "(Zotero-Sammlung).</p><p>" + zit.replace(url, f'<a href="{url}">{url}</a>') + "</p>"),
        "publication_date": iso_datum(item.get("date")),
        "creators": creators,
        "access_right": "open",
        "license": "cc-by-4.0",
        "communities": [{"identifier": COMMUNITY}],
        "notes": f"Zotero-Schluessel: {item['key']}",
    }
    if meta["upload_type"] == "publication":
        meta["publication_type"] = typ
    lang = SPRACHEN.get((item.get("language") or "")[:2].lower())
    if lang:
        meta["language"] = lang
    doi = doi_aus(item)
    if doi:
        meta["related_identifiers"] = [{
            "identifier": doi, "scheme": "doi",
            "relation": "isPartOf" if teil_von else "isAlternateIdentifier"}]
    elif item.get("url"):
        meta["related_identifiers"] = [{
            "identifier": item["url"], "scheme": "url", "relation": "isAlternateIdentifier"}]
    hrsg = personen(item, ("editor",))
    if hrsg:
        meta["contributors"] = [{"name": inversform(c), "type": "Editor"} for c in hrsg]
    return meta


# -------------------------------------------------------------- Gegenprobe
def doi_register(doi):
    """CSL-Metadaten aus dem DOI-Register, None bei Nichtantwort."""
    for versuch in range(3):
        try:
            r = requests.get(f"https://doi.org/{doi}", timeout=60,
                             headers={"Accept": "application/vnd.citationstyles.csl+json", **FM.UA})
            if r.status_code == 404:
                return {}
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if versuch == 2:
                print(f"  ! doi.org/{doi}: {e}", file=sys.stderr)
                return None
            time.sleep(5 * (versuch + 1))


def abweichung(item, reg):
    """Liste von Widerspruechen zwischen Zotero und dem DOI-Register."""
    fehler = []
    teile = (reg.get("issued") or {}).get("date-parts") or [[]]
    if teile[0] and ganzer_datumsteil(item.get("date")):
        zot = iso_datum(item["date"])
        regd = "-".join(f"{int(x):02d}" if i else str(x) for i, x in enumerate(teile[0]))
        if len(teile[0]) == 3 and zot != regd:
            fehler.append(f"Datum: Zotero {zot}, DOI-Register {regd}")
    blob = norm(" ".join(
        (a.get("given", "") + " " + a.get("family", "")) if "family" in a else a.get("literal", "")
        for a in reg.get("author", [])))
    if blob:
        for c in personen(item, ("author", "presenter")):
            nach = norm(c.get("lastName") or c.get("name", ""))
            if nach and nach not in blob:
                fehler.append(f"Autor:in {anzeige(c)}: nicht im DOI-Register ({blob[:80]})")
        zahl = len(personen(item, ("author", "presenter")))
        # Hat das Register viele einzelne Personen, muss Zotero nicht weniger haben.
        if len(reg.get("author", [])) > 1 and "family" in reg["author"][0] and zahl < len(reg["author"]):
            fehler.append(f"Autor:innen: Zotero {zahl}, DOI-Register {len(reg['author'])}")
    return fehler


def zenodo_titel(zid):
    r = FM.get(f"{ZENODO}/records/{zid}")
    return None if r is None else (r.get("metadata", {}).get("title") or "")


# ------------------------------------------------------------------- Anlegen
def anlegen(meta, text, token):
    kopf = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(f"{ZENODO}/deposit/depositions", headers=kopf, timeout=90,
                      data=json.dumps({"metadata": meta}, ensure_ascii=False).encode("utf-8"))
    if r.status_code not in (200, 201):
        return None, f"HTTP {r.status_code}: {r.text[:300]}"
    dep = r.json()
    r2 = requests.put(f"{dep['links']['bucket']}/zitation_{dep['id']}.txt",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/octet-stream"},
                      data=(text + "\n").encode("utf-8"), timeout=90)
    if r2.status_code not in (200, 201):
        return dep["id"], f"Entwurf {dep['id']} angelegt, Datei abgelehnt: HTTP {r2.status_code}"
    return dep["id"], ""


# ----------------------------------------------------------------------- Lauf
def main():
    global ABRUF
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--bericht", help="Markdown-Bericht in diese Datei schreiben")
    ap.add_argument("--seit", default=SEIT,
                    help=f"nur Eintraege ab diesem Datum (Standard {SEIT})")
    args = ap.parse_args()

    from datetime import date
    ABRUF = de_datum(date.today().isoformat())
    token = os.environ.get("ZENODO_TOKEN", "")
    if not token:
        print("FEHLER: ZENODO_TOKEN nicht gesetzt (auch der Trockenlauf braucht ihn).")
        sys.exit(1)

    print(f"Zotero -> Zenodo, Stand {date.today().isoformat()}\n")
    items, zotero_ok = zotero_eigene()
    print(f"Zotero 'Eigene Publikationen': {len(items)} Eintraege")
    konto = zenodo_konto(token)
    if konto is None:
        konto = []
    pub = sum(1 for k in konto if k["veroeffentlicht"])
    print(f"Zenodo-Konto: {len(konto)} Records/Entwuerfe, davon {pub} veroeffentlicht, "
          f"{len(konto) - pub} unveroeffentlicht (davon "
          f"{sum(1 for k in konto if not k['veroeffentlicht'] and k['schluessel'])} mit Zotero-Schluessel)\n")

    neu, uebersprungen = [], {}
    for it in items:
        if it.get("itemType") in ("attachment", "note") or not it.get("title"):
            continue
        titel = it["title"][:70]
        if not ist_team(it) or (iso_datum(it.get("date")) or "0") < args.seit:
            uebersprungen.setdefault(f"ausserhalb Team oder vor {args.seit}", []).append(titel)
            continue
        grund = schon_da(it, konto)
        if grund:
            uebersprungen.setdefault("hat schon einen Record", []).append(f"{titel} ({grund})")
            continue
        if "automatisch gefunden" in (it.get("extra") or "").lower():
            uebersprungen.setdefault("wartet auf Kuration (Vermerk 'Automatisch gefunden' in Extra)", []).append(titel)
            continue
        mehr = mehrere_personen_in_einem_feld(it)
        if mehr:
            ABWEICHUNGEN.append((it["key"], titel, [f"Autorenfeld enthaelt mehrere Personen: {mehr}"]))
            continue
        doi = doi_aus(it)
        teil_von = False
        m = ZENODO_DOI.match(doi)
        if m:
            zt = zenodo_titel(m.group(1))
            if zt is None:
                PROBLEME.append(f"Zenodo-Record {m.group(1)} nicht abrufbar: {titel}")
                continue
            if norm(zt) == norm(it["title"]):
                uebersprungen.setdefault("eigener Zenodo-Record (born-Zenodo)", []).append(titel)
                continue
            teil_von = True       # DOI gehoert zu einem Sammelband o. ae.
        elif doi:
            reg = doi_register(doi)
            if reg is None:
                PROBLEME.append(f"DOI-Register nicht erreichbar: {doi} ({titel})")
                continue
            fehler = abweichung(it, reg) if reg else [f"DOI {doi} im Register nicht gefunden"]
            if fehler:
                ABWEICHUNGEN.append((it["key"], titel, fehler))
                continue
        if not personen(it, ("author", "presenter")):
            ABWEICHUNGEN.append((it["key"], titel, ["keine Autor:innen in Zotero"]))
            continue
        if not iso_datum(it.get("date")):
            ABWEICHUNGEN.append((it["key"], titel, ["kein Datum in Zotero"]))
            continue
        url = f"https://doi.org/{doi}" if doi else it.get("url", "")
        if not url:
            ABWEICHUNGEN.append((it["key"], titel, ["weder DOI noch URL in Zotero"]))
            continue
        zit = vollzitat(it, url)
        neu.append({"item": it, "meta": stub_metadaten(it, url, zit, teil_von), "zit": zit})

    for gruppe, liste in uebersprungen.items():
        print(f"Nicht angelegt, {gruppe}: {len(liste)}")
        if gruppe.startswith(("wartet", "eigener")):
            for t in liste:
                print(f"    - {t}")
    print(f"\n{len(neu)} neue Entwuerfe:\n")
    for n in neu:
        print(f"- {n['meta']['publication_date']} | {n['meta']['title'][:80]}")
        print(f"    {n['zit']}")
    if ABWEICHUNGEN:
        print(f"\nZURUECKGEHALTEN, {len(ABWEICHUNGEN)} Eintraege (Zotero korrigieren, dann naechster Lauf):")
        for key, t, f in ABWEICHUNGEN:
            print(f"  - [{key}] {t}")
            for x in f:
                print(f"      {x}")

    angelegt = []
    gekappt = len(neu) > MAX_NEU
    if args.write and zotero_ok and konto:
        if gekappt:
            print(f"\nACHTUNG: {len(neu)} Entwuerfe, es werden nur {MAX_NEU} angelegt.")
        for n in neu[:MAX_NEU]:
            zid, fehler = anlegen(n["meta"], n["zit"], token)
            if fehler:
                PROBLEME.append(f"{n['meta']['title'][:50]}: {fehler}")
            if zid:
                angelegt.append((zid, n["meta"]["title"]))
                print(f"  Entwurf angelegt: https://zenodo.org/uploads/{zid}")
            time.sleep(1)
    elif args.write:
        print("\nFEHLER: Abgleichsbasis unvollstaendig (Zotero oder Zenodo), es wird "
              "nichts geschrieben. Gegen eine lueckenhafte Basis gilt Vorhandenes als neu.")
        PROBLEME.append("--write verweigert wegen unvollstaendiger Abgleichsbasis")

    if args.bericht:
        zeilen = ["## Zotero nach Zenodo", ""]
        zeilen += [f"- Entwuerfe angelegt: {len(angelegt)}", f"- Neue Kandidaten: {len(neu)}",
                   f"- Zurueckgehalten: {len(ABWEICHUNGEN)}", ""]
        if angelegt:
            zeilen += ["| Entwurf | Titel |", "|---|---|"]
            zeilen += [f"| [{z}](https://zenodo.org/uploads/{z}) | {t[:90]} |" for z, t in angelegt]
        for key, t, f in ABWEICHUNGEN:
            zeilen.append(f"- Zurueckgehalten `{key}` {t}: {'; '.join(f)}")
        Path(args.bericht).parent.mkdir(parents=True, exist_ok=True)
        Path(args.bericht).write_text("\n".join(zeilen) + "\n", encoding="utf-8")

    offen = bool(PROBLEME or ABWEICHUNGEN or gekappt)
    if PROBLEME:
        print("\n" + "=" * 70 + "\nLAUF UNVOLLSTAENDIG:")
        for p in PROBLEME:
            print(f"  - {p}")
        print("=" * 70)
    if not args.write:
        print("\n(Trockenlauf, nichts geschrieben. Mit --write Entwuerfe anlegen.)")
    if offen:
        print("\nDieser Lauf hat etwas offen gelassen, Exit-Status 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
