#!/usr/bin/env python3
"""
Seite "Demnaechst im Korpus" (#537): aus den offenen Issues mit dem Label
`ingest` und einer kleinen Zeitplan-Datei den Abschnittsbereich von
hilfe-demnaechst.html bauen.

Zwei Dateien, zwei Zustaendigkeiten:
  data/demnaechst-issues.json   eingefrorener Stand der offenen ingest-Issues
                                (Nummer, Titel, Labels); schreibt nur dieses Skript
  data/demnaechst-zeitplan.json von Hand gepflegt: je Issue ein Quartal
                                ("2026-Q4") oder ein Ausschluss mit Grund; ein
                                Issue ohne Eintrag erscheint mit "Zeitpunkt offen"

Ausgeschlossen ist ohne Eintrag jedes Issue mit dem Label `wait:extern` (die
Rechtefrage ist dort offen, #537). Arbeit an Texten, die schon im Korpus
stehen, und Issues ohne neuen Text stehen mit Grund unter "ausgeschlossen" in
der Zeitplan-Datei. Der Grund ist nur fuer die Pflege, die Seite zeigt ihn nicht.

Ein Ausfall der GitHub-API bricht nichts: das Skript meldet es, behaelt den
alten Stand und endet mit Exit 0. Die Seite entsteht in jedem Fall aus den
Dateien auf der Platte.

Aufruf:
  python scripts/build-demnaechst.py            # Issues abrufen und bauen
  python scripts/build-demnaechst.py --offline  # nur bauen
  python scripts/build-demnaechst.py --check    # Seite gegen die Dateien pruefen
"""

import argparse
import html
import json
import os
import re
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


def abrufen():
    """Alle offenen Issues mit dem Label, seitenweise. Wirft bei jedem Fehler."""
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
                raise RuntimeError(f"HTTP {antwort.status}")
            stueck = json.loads(antwort.read().decode("utf-8"))
        if not isinstance(stueck, list):
            raise RuntimeError("unerwartete Antwort")
        ergebnis.extend(i for i in stueck if "pull_request" not in i)
        if len(stueck) < 100:
            break
        seite += 1
    return sorted(({"nummer": i["number"], "titel": i["title"],
                    "labels": sorted(l["name"] for l in i["labels"])} for i in ergebnis),
                  key=lambda i: i["nummer"])


def lesen(pfad, leer):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else leer


def aktualisieren(alt):
    try:
        liste = abrufen()
        if not liste:
            raise RuntimeError("leere Antwort")
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError) as fehler:
        print(f"::warning::Issues nicht aktualisiert: {fehler}")
        return alt, False
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


def zeilen(stand, zeitplan):
    """Sichtbare Eintraege: (sortschluessel, titel, zeitangabe). Meldet unbekannte Issues im Plan."""
    plan = zeitplan.get("zeitplan", {})
    aus = zeitplan.get("ausgeschlossen", {})
    nummern = {str(i["nummer"]) for i in stand.get("issues", [])}
    for n in list(plan) + list(aus):
        if n not in nummern:
            print(f"::warning::Zeitplan nennt #{n}, das kein offenes ingest-Issue ist (Eintrag veraltet)")
    for n in plan:
        if n in aus:
            sys.exit(f"Zeitplan: #{n} steht unter zeitplan und unter ausgeschlossen")
    ergebnis = []
    for i in stand.get("issues", []):
        n = str(i["nummer"])
        if n in aus or (AUSSCHLUSS_LABEL in i["labels"] and n not in plan):
            continue
        eintrag = plan.get(n, {})
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
        liste = '<li class="pub-leer">Zurzeit ist keine Aufnahme geplant.</li>'
    vorschlag = ""
    if zeitplan.get("vorschlag"):
        vorschlag = ('<p class="text-sm text-slate-600 mb-3"><strong>Vorschlag:</strong> '
                     'Die Quartale sind noch nicht abgestimmt.</p>\n')
    return (f'<section class="mb-10">\n'
            f'<h2 class="text-2xl font-bold text-slate-900 mb-1">Geplante Aufnahmen ({len(sichtbar)})</h2>\n'
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="nicht abrufen, nur die Seite bauen")
    ap.add_argument("--check", action="store_true", help="Seite gegen die Dateien pruefen, nichts schreiben")
    args = ap.parse_args()

    stand = lesen(ISSUES, {"issues": []})
    zeitplan = lesen(ZEITPLAN, {"zeitplan": {}, "ausgeschlossen": {}})
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
    print(f"Sichtbar: {len(zeilen(stand, zeitplan))} von {len(stand.get('issues', []))} offenen ingest-Issues")


if __name__ == "__main__":
    main()
