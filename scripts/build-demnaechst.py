#!/usr/bin/env python3
"""
Seite "Demnaechst im Korpus" (#537): aus den offenen Issues mit dem Label
`ingest` und einer kleinen Zeitplan-Datei den Abschnittsbereich von
hilfe-demnaechst.html bauen.

Zwei Dateien, zwei Zustaendigkeiten:
  data/demnaechst-issues.json   eingefrorener Stand der offenen ingest-Issues
                                (Nummer, Titel, Labels); schreibt nur dieses Skript
  data/demnaechst-zeitplan.json von Hand gepflegt, eine Freigabeliste (chsteiner,
                                18.10.2026): unter "freigegeben" steht je Issue,
                                das die Seite nennen darf, ein Quartal ("2026-Q4")
                                und/oder ein Titel; ohne Quartal erscheint es mit
                                "Zeitpunkt offen". Unter "nicht_freigegeben" stehen
                                Issues mit Grund (und optional "vorgeschlagen")

Die Seite zeigt nur, was unter "freigegeben" steht. Ein Issue ohne Eintrag
erscheint nicht und wird im Build-Log als "nicht freigegeben: #N" gezaehlt.
Ausgeschlossen bleibt jedes Issue mit dem Label `wait:extern`, auch wenn es
freigegeben ist. Texte mit offener Rechtefrage nennt die Seite erst nach der
Freigabe (KZW, #537, 08.10.2026). Der Grund ist nur fuer die Pflege, die Seite
zeigt ihn nicht.

Ein Ausfall der GitHub-API (Netz, HTTP, Zeitlimit) bricht nichts: das Skript
meldet es, behaelt den alten Stand und endet mit Exit 0. Ein unerwartetes
Antwortformat (fehlendes Feld, falscher Typ) ist ein harter Fehler mit Exit 1.
Eine formal korrekte, leere Issue-Liste ist ein gueltiges Ergebnis. Die Seite
entsteht in jedem Fall aus den Dateien auf der Platte.

Aufruf:
  python scripts/build-demnaechst.py            # Issues abrufen und bauen
  python scripts/build-demnaechst.py --offline  # nur bauen
  python scripts/build-demnaechst.py --check    # Seite gegen die Dateien pruefen
  python scripts/build-demnaechst.py --selftest # Freigabeliste und Antwortformat an Beispielen pruefen
"""

import argparse
import html
import http.client
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
ISSUES = WURZEL / "data" / "demnaechst-issues.json"
ZEITPLAN = WURZEL / "data" / "demnaechst-zeitplan.json"
SEITE = WURZEL / "hilfe-demnaechst.html"
MARKE_AN = "<!-- DEMNAECHST:START -->"
MARKE_AUS = "<!-- DEMNAECHST:END -->"

REPO = "DigitalHumanitiesCraft/mhdbdb-tei-only"
LABEL = "ingest"
AUSSCHLUSS_LABEL = "wait:extern"
ZEITLIMIT = 30
QUARTAL = re.compile(r"^(\d{4})-Q([1-4])$")


class Antwortformat(Exception):
    """Die Antwort der API hat nicht die erwartete Form: harter Fehler, kein Ausfall."""


def normalisieren(stueck):
    """Eine Seite der API-Antwort pruefen und auf die Felder kuerzen, die wir speichern."""
    if not isinstance(stueck, list):
        raise Antwortformat(f"Antwort ist keine Liste, sondern {type(stueck).__name__}")
    ergebnis = []
    for k, i in enumerate(stueck):
        if not isinstance(i, dict):
            raise Antwortformat(f"Eintrag {k} ist kein Objekt")
        if "pull_request" in i:
            continue
        nummer, titel, labels = i.get("number"), i.get("title"), i.get("labels")
        if type(nummer) is not int:
            raise Antwortformat(f"Eintrag {k}: 'number' fehlt oder ist keine Ganzzahl")
        if not isinstance(titel, str):
            raise Antwortformat(f"Issue #{nummer}: 'title' fehlt oder ist kein Text")
        if not isinstance(labels, list) or not all(isinstance(l, dict) and isinstance(l.get("name"), str) for l in labels):
            raise Antwortformat(f"Issue #{nummer}: 'labels' fehlt oder hat nicht die Form [{{name}}]")
        ergebnis.append({"nummer": nummer, "titel": titel, "labels": sorted(l["name"] for l in labels)})
    return ergebnis


def abrufen():
    """Alle offenen Issues mit dem Label, seitenweise. Netzfehler werfen, ein falsches Format wirft Antwortformat."""
    ergebnis = []
    seite = 1
    while True:
        url = (f"https://api.github.com/repos/{REPO}/issues"
               f"?labels={LABEL}&state=open&per_page=100&page={seite}")
        kopf = {"User-Agent": "mhdbdb-tei-only/demnaechst", "Accept": "application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            kopf["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
        with urllib.request.urlopen(urllib.request.Request(url, headers=kopf), timeout=ZEITLIMIT) as antwort:
            if antwort.status != 200:
                raise urllib.error.URLError(f"HTTP {antwort.status}")
            rohtext = antwort.read()
        try:
            stueck = json.loads(rohtext.decode("utf-8"))
        except ValueError as fehler:  # JSONDecodeError und UnicodeDecodeError
            raise Antwortformat(f"Antwort ist kein JSON: {fehler}") from fehler
        # Die Seitenlaenge zaehlt die rohe Antwort, nicht die gekuerzte (Pull Requests fallen weg)
        ergebnis.extend(normalisieren(stueck))
        if len(stueck) < 100:
            break
        seite += 1
    return sorted(ergebnis, key=lambda i: i["nummer"])


def lesen(pfad, leer):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else leer


def aktualisieren(alt):
    try:
        liste = abrufen()
    except (urllib.error.URLError, TimeoutError, socket.error, http.client.HTTPException) as fehler:
        # nur Netz und HTTP (HTTPError ist ein URLError): der alte Stand bleibt liegen
        print(f"::warning::Issues nicht aktualisiert: {type(fehler).__name__}: {fehler}")
        return alt, False
    except Antwortformat as fehler:
        sys.exit(f"Issues: unerwartetes Antwortformat der GitHub-API: {fehler}")
    geaendert = liste != alt.get("issues")
    # Das Abrufdatum aendert sich nur mit dem Inhalt, sonst oeffnete jeder Monat einen PR.
    abgerufen = date.today().isoformat() if geaendert else alt.get("abgerufen", date.today().isoformat())
    return {"abgerufen": abgerufen, "issues": liste}, geaendert


def e(text):
    return html.escape(text, quote=True)


def deutsches_datum(iso):
    return date.fromisoformat(iso).strftime("%d.%m.%Y") if iso else ""


def quartal_text(q):
    treffer = QUARTAL.match(q)
    if not treffer:
        sys.exit(f"Zeitplan: '{q}' ist kein Quartal der Form 2026-Q4")
    return f"{treffer.group(2)}. Quartal {treffer.group(1)}"


def bereinigt(titel):
    return re.sub(r"^(Ingest-Kandidat(en)?( \(Sammel\))?|Ingest):\s*", "", titel)


def zeilen(stand, zeitplan, melden=True):
    """Sichtbare Eintraege: (sortschluessel, titel, zeitangabe). Nur Freigegebenes erscheint."""
    for alt in ("zeitplan", "ausgeschlossen"):
        if alt in zeitplan:
            sys.exit(f"Zeitplan: '{alt}' gilt nicht mehr, die Datei fuehrt 'freigegeben' und 'nicht_freigegeben'")
    frei = zeitplan.get("freigegeben", {})
    nicht = zeitplan.get("nicht_freigegeben", {})
    nummern = {str(i["nummer"]) for i in stand.get("issues", [])}
    for n in list(frei) + list(nicht):
        if melden and n not in nummern:
            print(f"::warning::Zeitplan nennt #{n}, das kein offenes ingest-Issue ist (Eintrag veraltet)")
    for n in frei:
        if n in nicht:
            sys.exit(f"Zeitplan: #{n} steht unter freigegeben und unter nicht_freigegeben")
    ergebnis = []
    for i in stand.get("issues", []):
        n = str(i["nummer"])
        if AUSSCHLUSS_LABEL in i["labels"] and n in frei:
            if melden:
                print(f"::warning::#{n} trägt {AUSSCHLUSS_LABEL} und ist freigegeben: wird nicht gezeigt, Eintrag prüfen")
            continue
        if n not in frei:
            if melden:
                print(f"nicht freigegeben: #{n}")
            continue
        eintrag = frei[n]
        q = eintrag.get("quartal")
        titel = eintrag.get("titel") or bereinigt(i["titel"])
        ergebnis.append(((q or "9999-Q9", titel.casefold()), titel,
                         quartal_text(q) if q else "Zeitpunkt offen"))
    return sorted(ergebnis)


def region_bauen(stand, zeitplan):
    sichtbar = zeilen(stand, zeitplan)
    if sichtbar:
        liste = "\n".join(
            f'<li><p class="pub-titel">{e(titel)}</p><p class="pub-meta">{e(zeit)}</p></li>'
            for _, titel, zeit in sichtbar)
    else:
        liste = '<li class="pub-leer">Zurzeit steht keine Aufnahme fest, die hier genannt werden kann.</li>'
    vorschlag = ""
    if zeitplan.get("vorschlag"):
        vorschlag = ('<p class="text-sm text-slate-600 mb-3"><strong>Vorschlag:</strong> '
                     'Die Quartale sind noch nicht abgestimmt.</p>\n')
    return (f'<section class="mb-10">\n'
            f'<h2 class="text-2xl font-bold text-slate-900 mb-1">Geplante Aufnahmen{f" ({len(sichtbar)})" if sichtbar else ""}</h2>\n'
            f'<p class="text-slate-600 mb-3">Zeitangaben sind Schätzungen und können sich verschieben.</p>\n'
            f'{vorschlag}'
            f'<ul class="pub-liste">\n{liste}\n</ul>\n</section>\n'
            f'<p class="text-sm text-slate-500">Stand: {deutsches_datum(stand.get("abgerufen", ""))}. '
            f'Die Liste wird einmal im Monat aus der Arbeitsplanung des Projekts übernommen.</p>')


def seite_gebaut(stand, zeitplan):
    text = SEITE.read_text(encoding="utf-8")
    i, j = text.find(MARKE_AN), text.find(MARKE_AUS)
    if i < 0 or j < i:
        sys.exit(f"{SEITE.name}: Marken {MARKE_AN} / {MARKE_AUS} fehlen")
    return text[: i + len(MARKE_AN)] + "\n" + region_bauen(stand, zeitplan) + "\n" + text[j:], text


def selftest():
    """Eingebautes Beispiel, ohne Netz: ein Issue ohne Freigabe erscheint nicht."""
    stand = {"abgerufen": "2026-10-18", "issues": [
        {"nummer": 1, "titel": "Ingest: Freigegebener Text", "labels": ["ingest"]},
        {"nummer": 2, "titel": "Ingest: Ausdruecklich gesperrter Text", "labels": ["ingest"]},
        {"nummer": 3, "titel": "Ingest: Neuer Text ohne jeden Eintrag", "labels": ["ingest"]},
        {"nummer": 4, "titel": "Ingest: Freigegeben, aber wartet extern", "labels": ["ingest", "wait:extern"]},
    ]}
    plan = {"freigegeben": {"1": {"quartal": "2027-Q1"}, "4": {}},
            "nicht_freigegeben": {"2": {"grund": "Rechtefrage"}}}
    sichtbar = zeilen(stand, plan, melden=False)
    assert [t for _, t, _ in sichtbar] == ["Freigegebener Text"], sichtbar
    assert sichtbar[0][2] == "1. Quartal 2027", sichtbar
    region = region_bauen(stand, plan)
    for t in ("gesperrter Text", "Neuer Text ohne jeden Eintrag", "wartet extern"):
        assert t not in region, t
    assert "Freigegebener Text" in region
    assert "pub-leer" in region_bauen(stand, {"freigegeben": {}, "nicht_freigegeben": {}})
    # Antwortformat: fehlendes Feld und falscher Typ sind harte Fehler, eine leere Liste ist gueltig
    assert normalisieren([]) == []
    gut = {"number": 5, "title": "x", "labels": [{"name": "ingest"}]}
    assert normalisieren([gut]) == [{"nummer": 5, "titel": "x", "labels": ["ingest"]}]
    for schlecht in ({"title": "x", "labels": []}, {"number": "5", "title": "x", "labels": []},
                     {"number": 5, "labels": []}, {"number": 5, "title": "x", "labels": ["ingest"]},
                     {"number": 5, "title": "x"}):
        try:
            normalisieren([schlecht])
        except Antwortformat:
            continue
        raise AssertionError(f"Format {schlecht} wurde angenommen")
    try:
        normalisieren({"message": "Not Found"})
    except Antwortformat:
        pass
    else:
        raise AssertionError("Objekt statt Liste wurde angenommen")
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="nicht abrufen, nur die Seite bauen")
    ap.add_argument("--check", action="store_true", help="Seite gegen die Dateien pruefen, nichts schreiben")
    ap.add_argument("--selftest", action="store_true", help="Freigabeliste und Antwortformat an Beispielen pruefen")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return

    stand = lesen(ISSUES, {"issues": []})
    zeitplan = lesen(ZEITPLAN, {"freigegeben": {}, "nicht_freigegeben": {}})
    if not args.offline and not args.check:
        stand, geaendert = aktualisieren(stand)
        if geaendert:
            ISSUES.write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
            print("Stand geschrieben:", ISSUES.relative_to(WURZEL))
        else:
            print("Stand unveraendert.")

    neu, alt = seite_gebaut(stand, zeitplan)
    if args.check:
        if neu != alt:
            sys.exit(f"{SEITE.name}: Abschnittsbereich weicht von den Dateien ab, "
                     "python scripts/build-demnaechst.py --offline")
        print(f"OK: {SEITE.name} passt zu den Dateien")
        return
    if neu != alt:
        SEITE.write_text(neu, encoding="utf-8", newline="")
        print("Seite geschrieben:", SEITE.name)
    print(f"{len(zeilen(stand, zeitplan, melden=False))} von {len(stand.get('issues', []))} offenen ingest-Issues freigegeben")


if __name__ == "__main__":
    main()
