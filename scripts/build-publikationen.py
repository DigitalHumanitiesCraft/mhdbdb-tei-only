#!/usr/bin/env python3
"""
Publikationen-Seite (#417): Zotero-Sammlungen in einen eingefrorenen Stand
schreiben und daraus den Abschnittsbereich von hilfe-publikationen.html bauen.

Quelle: die oeffentliche Zotero-Gruppe 5043625 (Mittelhochdeutsche
Begriffsdatenbank), ohne Schluessel lesbar. Zwei Sammlungen, je ein Abschnitt:
  WB4HTUGC  Eigene Publikationen
  Z2N4SWWI  Erwaehnende Publikationen

Der Stand liegt in data/zotero-publikationen.json. Das ist der eingefrorene
Stand (KZW 10.09.2026: "Wir frieren einen Stand ein und ziehen ihn 1x pro Monat
automatisiert nach"); die Seite entsteht nur aus ihm, nie live. Ein monatlicher
Lauf (.github/workflows/monatslauf-seiten.yml) ruft dieses Skript auf und
oeffnet einen PR, wenn sich der Stand aendert.

Ein Zotero-Ausfall bricht nichts: antwortet die API nicht, mit einem Fehler
oder mit weniger als der Haelfte der bisherigen Eintraege, bleibt der alte
Stand liegen, das Skript meldet es und endet mit Exit 0. Die Seite wird in
jedem Fall aus dem Stand auf der Platte gebaut.

Aufruf:
  python scripts/build-publikationen.py            # abrufen und bauen
  python scripts/build-publikationen.py --offline  # nur bauen
  python scripts/build-publikationen.py --check    # Seite gegen Stand pruefen
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
STAND = WURZEL / "data" / "zotero-publikationen.json"
SEITE = WURZEL / "hilfe-publikationen.html"
MARKE_AN = "<!-- PUBLIKATIONEN:START -->"
MARKE_AUS = "<!-- PUBLIKATIONEN:END -->"

GRUPPE = "5043625"
ABSCHNITTE = [
    ("WB4HTUGC", "Eigene Publikationen",
     "Veröffentlichungen aus dem Projekt und seinem Umfeld."),
    ("Z2N4SWWI", "Erwähnende Publikationen",
     "Arbeiten, die die MHDBDB nennen oder nutzen."),
]
SEITENGROESSE = 100
# Weniger als dieser Anteil der bisherigen Eintraege gilt als misslungener Abruf
MINDESTANTEIL = 0.5
ZEITLIMIT = 30
AUSGESCHLOSSEN = {"attachment", "note"}


class AbrufAusgefallen(RuntimeError):
    """Der Abruf lief, lieferte aber erkennbar keinen brauchbaren Bestand (HTTP-Status, leer, Einbruch): alter Stand bleibt."""


def abrufen(sammlung):
    """Alle Eintraege oberster Ebene einer Sammlung, seitenweise. Wirft bei jedem Fehler."""
    eintraege = []
    start = 0
    gesamt = None
    while gesamt is None or start < gesamt:
        url = (f"https://api.zotero.org/groups/{GRUPPE}/collections/{sammlung}/items/top"
               f"?format=json&v=3&limit={SEITENGROESSE}&start={start}")
        anfrage = urllib.request.Request(url, headers={"User-Agent": "mhdbdb-tei-only/publikationen"})
        with urllib.request.urlopen(anfrage, timeout=ZEITLIMIT) as antwort:
            if antwort.status != 200:
                raise AbrufAusgefallen(f"{sammlung}: HTTP {antwort.status}")
            if antwort.headers.get("Total-Results") is None:
                raise RuntimeError(f"{sammlung}: Kopf Total-Results fehlt")
            gesamt = int(antwort.headers["Total-Results"])
            seite = json.loads(antwort.read().decode("utf-8"))
        if not seite:
            break
        eintraege.extend(seite)
        start += len(seite)
    if len(eintraege) != gesamt:
        raise RuntimeError(f"{sammlung}: {len(eintraege)} Eintraege gelesen, {gesamt} gemeldet")
    return eintraege


def jahr(datum):
    treffer = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", datum or "")
    return int(treffer.group(1)) if treffer else None


def autoren(creators):
    namen = [c.get("lastName") or c.get("name") or "" for c in creators
             if c.get("creatorType") in ("author", "editor", "contributor") or "name" in c]
    namen = [n for n in namen if n]
    if len(namen) > 3:
        return ", ".join(namen[:3]) + " u. a."
    return ", ".join(namen)


def normalisieren(eintrag):
    d = eintrag["data"]
    doi = (d.get("DOI") or "").strip()
    return {
        "key": d["key"],
        "typ": d["itemType"],
        "titel": " ".join((d.get("title") or "").split()),
        "autoren": autoren(d.get("creators", [])),
        "jahr": jahr(d.get("date")),
        "doi": doi,
        "url": (d.get("url") or "").strip(),
    }


def sortiert(liste):
    # neueste zuerst; ohne Jahr ans Ende; dann alphabetisch
    return sorted(liste, key=lambda e: (-(e["jahr"] or 0), e["titel"].casefold(), e["key"]))


def stand_lesen():
    if not STAND.exists():
        return {"abschnitte": {}}
    return json.loads(STAND.read_text(encoding="utf-8"))


def aktualisieren(alt):
    """Neuen Stand abrufen; je Abschnitt bei Fehler oder Einbruch den alten behalten."""
    neu = {"quelle": f"https://www.zotero.org/groups/{GRUPPE}/mittelhochdeutsche_begriffsdatenbank/library",
           "abschnitte": {}}
    for sammlung, titel, _ in ABSCHNITTE:
        vorher = alt.get("abschnitte", {}).get(sammlung)
        try:
            roh = abrufen(sammlung)
            liste = sortiert([normalisieren(x) for x in roh if x["data"]["itemType"] not in AUSGESCHLOSSEN])
            if not liste:
                raise AbrufAusgefallen("leere Antwort")
            if vorher and len(liste) < MINDESTANTEIL * len(vorher["eintraege"]):
                raise AbrufAusgefallen(f"nur {len(liste)} Eintraege gegen bisher {len(vorher['eintraege'])}")
            # Das Datum gehoert zum Abschnitt: es wandert nur mit seinem Inhalt, sonst oeffnete jeder
            # Monat einen PR, und ein ausgefallener Abschnitt behaelt sein altes Datum.
            heute = date.today().isoformat()
            if vorher and vorher["eintraege"] == liste:
                abgerufen = vorher.get("abgerufen") or alt.get("abgerufen") or heute
            else:
                abgerufen = heute
            neu["abschnitte"][sammlung] = {"titel": titel, "abgerufen": abgerufen, "eintraege": liste}
        except (urllib.error.URLError, TimeoutError, OSError, AbrufAusgefallen) as fehler:  # nur Netz und HTTP (HTTPError ist URLError, socket-Fehler sind OSError) lassen den alten Stand liegen; ein unerwartetes Format ist ein harter Fehler
            print(f"::warning::Zotero-Sammlung {sammlung} ({titel}) nicht aktualisiert: {type(fehler).__name__}: {fehler}")
            if vorher is None:
                print(f"  kein bisheriger Stand fuer {sammlung}: Abschnitt bleibt leer")
                continue
            neu["abschnitte"][sammlung] = vorher
    inhalt_alt = json.dumps(alt.get("abschnitte", {}), ensure_ascii=False, sort_keys=True)
    inhalt_neu = json.dumps(neu["abschnitte"], ensure_ascii=False, sort_keys=True)
    return neu, inhalt_alt != inhalt_neu


def e(text):
    return html.escape(text, quote=True)


def deutsches_datum(iso):
    return date.fromisoformat(iso).strftime("%d.%m.%Y") if iso else ""


DOI_VORSATZ = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
DOI_FORM = re.compile(r"^10\.\d{4,9}/\S+$")
WEB = re.compile(r"^https?://\S+$", re.I)


def ziel_von(eintrag):
    """(href, Beschriftung) oder None. Das DOI-Feld in Zotero ist Freitext: auch eine volle
    doi.org-Adresse, eine andere Web-Adresse oder eine URN kommen darin vor."""
    doi = DOI_VORSATZ.sub("", eintrag["doi"]).strip()
    if DOI_FORM.match(doi):
        return f"https://doi.org/{doi}", f"DOI {doi}"
    if WEB.match(eintrag["doi"]):
        return eintrag["doi"], "Link"
    if WEB.match(eintrag["url"]):
        return eintrag["url"], "Link"
    return None


def eintrag_html(eintrag):
    ziel = ziel_von(eintrag)
    if ziel:
        ziel = (f'<a href="{e(ziel[0])}" class="text-brand-600 hover:text-brand-700 font-medium" '
                f'target="_blank" rel="noopener">{e(ziel[1])}</a>')
    else:
        ziel = "kein Link hinterlegt"
    zusatz = ", ".join(x for x in (e(eintrag["autoren"]) if eintrag["autoren"] else "",
                                   str(eintrag["jahr"]) if eintrag["jahr"] else "o. J.") if x)
    # Das Em-Dash-Gate (check-no-em-dash.py) gilt fuer die Seite; der Stand behaelt den Titel wie in Zotero.
    titel = " ".join(eintrag["titel"].replace(chr(0x2014), " - ").split())
    return (f'<li><p class="pub-titel">{e(titel)}</p>'
            f'<p class="pub-meta">{zusatz} &middot; {ziel}</p></li>')


def aeltester_stand(stand):
    """Das aelteste Abschnittsdatum: ein ausgefallener Abschnitt soll die Seite nicht frischer machen."""
    daten = [a.get("abgerufen") or stand.get("abgerufen") or "" for a in stand.get("abschnitte", {}).values()]
    return min((d for d in daten if d), default="")


def region_bauen(stand):
    teile = []
    for sammlung, titel, erklaerung in ABSCHNITTE:
        abschnitt = stand.get("abschnitte", {}).get(sammlung)
        eintraege = abschnitt["eintraege"] if abschnitt else []
        liste = "\n".join(eintrag_html(x) for x in eintraege) if eintraege else \
            '<li class="pub-leer">Zurzeit ist hier nichts aufgeführt.</li>'
        teile.append(
            f'<section class="mb-10" id="{e(sammlung.lower())}">\n'
            f'<h2 class="text-2xl font-bold text-slate-900 mb-1">{e(titel)} ({len(eintraege)})</h2>\n'
            f'<p class="text-slate-600 mb-3">{e(erklaerung)}</p>\n'
            f'<ul class="pub-liste">\n{liste}\n</ul>\n</section>')
    teile.append(
        f'<p class="text-sm text-slate-500">Stand der Bibliothek: {deutsches_datum(aeltester_stand(stand))}. '
        f'Die Liste wird einmal im Monat aus der <a href="{e(stand.get("quelle", ""))}" '
        f'class="text-brand-600 hover:text-brand-700 font-medium" target="_blank" rel="noopener">'
        f'Zotero-Bibliothek der MHDBDB</a> übernommen.</p>')
    return "\n".join(teile)


def seite_gebaut(stand):
    text = SEITE.read_text(encoding="utf-8")
    i, j = text.find(MARKE_AN), text.find(MARKE_AUS)
    if i < 0 or j < i:
        sys.exit(f"{SEITE.name}: Marken {MARKE_AN} / {MARKE_AUS} fehlen")
    return text[: i + len(MARKE_AN)] + "\n" + region_bauen(stand) + "\n" + text[j:], text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="nicht abrufen, nur die Seite bauen")
    ap.add_argument("--check", action="store_true", help="Seite gegen den Stand pruefen, nichts schreiben")
    args = ap.parse_args()

    stand = stand_lesen()
    if not args.offline and not args.check:
        stand, geaendert = aktualisieren(stand)
        if geaendert or not STAND.exists():
            STAND.write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
            print("Stand geschrieben:", STAND.relative_to(WURZEL))
        else:
            print("Stand unveraendert.")

    neu, alt = seite_gebaut(stand)
    if args.check:
        if neu != alt:
            sys.exit(f"{SEITE.name}: Abschnittsbereich weicht vom Stand ab, "
                     "python scripts/build-publikationen.py --offline")
        print(f"OK: {SEITE.name} passt zum Stand")
        return
    if neu != alt:
        SEITE.write_text(neu, encoding="utf-8", newline="")
        print("Seite geschrieben:", SEITE.name)
    for sammlung, titel, _ in ABSCHNITTE:
        n = len(stand.get("abschnitte", {}).get(sammlung, {}).get("eintraege", []))
        print(f"{titel}: {n} Eintraege ({sammlung})")


if __name__ == "__main__":
    main()
