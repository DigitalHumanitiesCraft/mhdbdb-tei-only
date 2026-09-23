#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sucht Publikationen, die die MHDBDB erwaehnen, und legt sie in Zotero ab.

Fragt Zenodo, OpenAlex, OpenAIRE, Crossref und Semantic Scholar ab, verwirft
alles, was in der Zotero-Gruppe 5043625 schon irgendwo liegt, und legt den Rest
in der Sammlung "Zu pruefen (automatisch gefunden)" (NHIA2I6N) unterhalb von
"Erwaehnende Publikationen" an. Die Entscheidung bleibt kuratorisch: was nicht
einschlaegig ist, wandert nach "Geprueft: nicht einschlaegig" (IPQ3XNMT) und
wirkt von dort als Sperrliste. Wer einen Fehlgriff stattdessen loescht, bekommt
ihn im naechsten Lauf wieder vorgelegt.

    python scripts/sync/find-mentions.py                  # Trockenlauf
    python scripts/sync/find-mentions.py --write          # legt in Zotero an
    python scripts/sync/find-mentions.py --since 2023-01-01

Aussenwirkung
-------------
Das Skript fasst weder `tei/` noch `authority-files/` an und erzeugt keine
abgeleiteten Daten. Es loest deshalb KEINEN Index-Rebuild aus und beruehrt die
Data-Change-Lifecycle-Schrittfolge nicht. Einziges Schreibziel ist die
Zotero-Gruppe, und dort ausschliesslich das Anlegen neuer Eintraege in
NHIA2I6N; bestehende Eintraege werden nie geaendert oder geloescht. MAX_NEU
deckelt einen Lauf zusaetzlich auf 30 Neuanlagen.

Abhaengigkeiten und Zugangsdaten
--------------------------------
Ausser der Standardbibliothek nur `requests`, wie schon in
`enhance_works_with_zotero.py`. Bewusst NICHT in `requirements.txt`: die Datei
pinnt die Build-Kette fuer byte-identische Rebuilds (#125), und dieses Skript
gehoert nicht dazu.

Zugangsdaten kommen aus der Umgebung, nie aus einer Datei im Repo:

    ZOTERO_API_KEY     Pflicht fuer --write, Schreibrecht auf Gruppe 5043625
    OPENALEX_API_KEY   optional, aber dringend empfohlen

Zu OpenAlex: seit 13.02.2026 ist ein Schluessel Pflicht (kostenlos unter
openalex.org/settings/api), der alte "polite pool" per mailto ist abgeschafft.
Ohne Schluessel bleiben 100 Abrufe am Tag, und danach antwortet der Dienst mit
HTTP 200 und count=0, also "keine Treffer" statt "gedrosselt". Genau davor
schuetzt die Kanarienvogel-Abfrage in `src_openalex()`: ein leeres Ergebnis auf
das Token "MHDBDB" gilt als Ausfall und nicht als Befund, und der Lauf meldet
sich am Ende ausdruecklich als unvollstaendig. Ein stiller Nullbefund waere die
gefaehrlichste Fehlerart dieses Skripts, weil er wie "nichts Neues erschienen"
aussieht.

Abgleichsbasis
--------------
Verglichen wird gegen alle Top-Level-Eintraege der Gruppe. Faellt beim Blaettern
eine Seite aus, ist die Basis lueckenhaft, und lueckenhaft heisst hier: Bekanntes
gilt als neu. Deshalb zaehlt `zotero_baseline()` die gelesenen Eintraege gegen
die serverseitige Gesamtzahl (Kopfzeile Total-Results), und `--write` verweigert
die Arbeit, sobald die Probe nicht aufgeht. Dasselbe Prinzip gilt fuer die
Quellen: eine Abfrage, die nicht geantwortet hat, landet in PROBLEME und nicht
im Schweigen.

Exit-Status
-----------
0 nur, wenn der Lauf vollstaendig war. Steht etwas in PROBLEME oder hat Zotero
eine Neuanlage abgelehnt, endet der Lauf mit 1, im Trockenlauf wie beim
Schreiben. Fuer einen Lauf am Terminal ist das nebensaechlich, weil der Text
gelesen wird; fuer die unbeaufsichtigte Monatsroutine ist der Status das
einzige Signal, und ohne ihn sieht ein Lauf mit vier ausgefallenen Quellen
genauso aus wie einer ohne Neuigkeiten.

Praezision vor Vollstaendigkeit: ein Treffer zaehlt nur, wenn der Projektname
in Titel, Abstract oder Beschreibung steht oder wenn er aus der Suche nach
einem eindeutigen Token stammt. Ohne diese Huerde liefert die Suche nach
"Middle High German Conceptual Database" alles, was irgendwo "conceptual" und
"database" enthaelt, von Ernaehrungsstudien bis Bluthochdruck-Leitlinien.
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata
from datetime import date
from urllib.parse import quote

import requests

GROUP = "5043625"
COL_PRUEFEN = "NHIA2I6N"          # Zu pruefen (automatisch gefunden)
COL_ABGELEHNT = "IPQ3XNMT"        # Geprueft: nicht einschlaegig (Sperrliste)
MAIL = "mhdbdb@plus.ac.at"
UA = {"User-Agent": f"MHDBDB-mention-scan/1.0 (mailto:{MAIL})"}

# (Suchbegriff, ist_eindeutiges_Token)
# Die Projektadresse mhdbdb.sbg.ac.at wird von allen Suchmaschinen in
# "mhdbdb / sbg / ac / at" zerlegt. Bei Crossref liefert das Wechselrichter
# ("AC"), die Satellitenmission SBG-TIR und Salzburger Landesrecht ("Sbg");
# davor schuetzt TOKEN_QUELLEN. Bei OpenAlex holt dieselbe Abfrage dagegen
# Arbeiten herein, die die Adresse im Literaturverzeichnis fuehren.
QUERIES = [
    ("MHDBDB", True),
    ("mhdbdb.sbg.ac.at", True),
    ("Mittelhochdeutsche Begriffsdatenbank", False),
    ("Middle High German Conceptual Database", False),
]

# Quellen, deren Index Abstract oder Volltext umfasst: nur bei diesen ist ein
# Treffer auf das Token "MHDBDB" fuer sich schon ein Beleg. Crossref sucht nur
# unscharf ueber Titelfelder und braucht daher immer den Namensnachweis.
TOKEN_QUELLEN = {"OpenAlex", "Zenodo", "OpenAIRE", "SemanticScholar"}

NAME = re.compile(
    r"mhdbdb|begriffsdatenbank|middle high german conceptual database", re.I
)

MAX_NEU = 30  # Sicherheitsnetz: mehr als das pro Lauf nie anlegen

# Sammelt alles, was den Lauf unvollstaendig macht. Ein leeres Ergebnis ohne
# Eintrag hier heisst "nichts Neues gefunden", mit Eintrag heisst es "nicht
# zuverlaessig gesucht".
PROBLEME = []

# Das MHDBDB-Team. Arbeiten dieser Personen gehoeren in "Eigene Publikationen",
# nicht zu den erwaehnenden. Sie werden trotzdem in der Pruefablage angelegt,
# aber als solche gekennzeichnet.
TEAM = [
    "zeppezauer", "wachauer", "schmidt", "springeth", "weichselbaumer",
    "hinkelmanns", "van beek", "vanbeek", "hintersteiner", "beutel",
]

# Woerter, die fuer den Titelvergleich nichts hergeben
STOPP = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "eines",
    "und", "oder", "aber", "als", "auf", "aus", "bei", "fur", "fuer", "mit",
    "nach", "von", "vom", "vor", "zum", "zur", "uber", "ueber", "unter", "im",
    "in", "an", "am", "the", "and", "for", "with", "from", "into", "eine",
    "zwischen", "durch", "gegen", "ohne", "ist", "sind", "werden", "wird",
}


# ------------------------------------------------------------------ Helfer
def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def entdiakritisiert(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def stamm(w):
    """Sehr grobe deutsche Grundform: 'Oswalds' -> 'oswald',
    'mittelhochdeutschen' -> 'mittelhochdeutsch'."""
    for endung in ("ischen", "lichen", "enden", "ungen", "en", "er", "es", "e", "n", "s"):
        if len(w) > len(endung) + 3 and w.endswith(endung):
            return w[: -len(endung)]
    return w


def woerter(titel):
    """Wortmenge eines Titels fuer den Aehnlichkeitsvergleich."""
    roh = re.split(r"[^a-z0-9]+", entdiakritisiert(titel))
    return {stamm(w) for w in roh if len(w) > 2 and w not in STOPP}


def ueberlappung(a, b):
    """Anteil der kleineren Wortmenge, der in der groesseren steckt."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


JAHR = re.compile(r"\b(1\d{3}|20\d{2})\b")


def jahr_aus(s):
    """Erste vierstellige Jahreszahl einer Datumsangabe. Zotero-Datumsfelder
    sind Freitext ("Mai 2024", "2024-05-01", "o.J."), deshalb wird gesucht und
    nicht die erste vier Zeichen abgeschnitten."""
    m = JAHR.search(str(s or ""))
    return m.group(0) if m else ""


def nachname(n):
    """Nachname einer Namensangabe, entdiakritisiert und ohne Beiwerk."""
    n = entdiakritisiert(n).strip()
    if not n:
        return ""
    if "," in n:
        n = n.split(",")[0]
    teile = n.split()
    return re.sub(r"[^a-z-]", "", teile[-1]) if teile else ""


def nachnamen(namen):
    """Menge der Nachnamen, fuer den titelunabhaengigen Abgleich."""
    return {k for k in (nachname(n) for n in namen or []) if len(k) > 2}


def clean_doi(d):
    if not d:
        return ""
    d = str(d).lower().strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d.rstrip(".")


def get(url, tries=4, headers=None, kopf=False):
    """Eine GET-Anfrage mit Wiederholung. Gibt None zurueck, wenn nicht
    geantwortet wurde, sonst die geparste Antwort, mit `kopf=True` als Paar
    (Antwort, Kopfzeilen)."""
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=headers or UA, timeout=60)
            if r.status_code in (429, 503):
                time.sleep(20 * (attempt + 1))
                continue
            r.raise_for_status()
            return (r.json(), r.headers) if kopf else r.json()
        except Exception as e:
            if attempt == tries - 1:
                print(f"  ! {url[:80]}: {e}", file=sys.stderr)
                return None
            time.sleep(6 * (attempt + 1))
    return None


def unabstract(inv):
    if not inv:
        return ""
    words = [(p, w) for w, ps in inv.items() for p in ps]
    return " ".join(w for _, w in sorted(words))


# Die Wortgrenzen stehen pro Alternative, nicht um die Gruppe: nach "u.a."
# folgt ein Punkt, und zwischen Punkt und Zeilenende gibt es keine Wortgrenze.
# Mit \b hinter der Gruppe war die Abkuerzung deshalb nicht gesperrt.
KEINE_PERSON = re.compile(r"\bund\b|\band\b|\bet\s+al\b|u\.\s*a\.|&", re.I)


def split_name(n):
    """'Zeppezauer-Wachauer, Katharina' oder 'Katharina Zeppezauer-Wachauer'.

    Gibt None zurueck, wenn die Angabe keine einzelne Person sein kann. Grund:
    manche Quellen liefern die ganze Verfasserzeile als einen Namen. Bei
    OpenAlex geschah das mit 10.58079/16jkg, und weil hier stumpf am letzten
    Leerzeichen getrennt wurde, stand in Zotero (Eintrag 2VJQBB2M) danach der
    Autor "Alan van Beek und Julia Hintersteiner Katharina Zeppezauer-Wachauer".
    Lieber kein Autor als ein erfundener: die Rohangabe wandert stattdessen als
    Notiz nach `extra`, wo sie kuratorisch aufzuloesen ist.
    """
    n = (n or "").strip().strip(",;")
    if not n:
        return None
    if KEINE_PERSON.search(n):
        return None
    if ";" in n or n.count(",") > 1:
        return None
    if len(n.replace(",", " ").split()) > 4:
        return None
    if "," in n:
        last, _, first = n.partition(",")
        return {"creatorType": "author", "firstName": first.strip(),
                "lastName": last.strip()}
    parts = n.split()
    if len(parts) == 1:
        return {"creatorType": "author", "name": n}
    return {"creatorType": "author", "firstName": " ".join(parts[:-1]),
            "lastName": parts[-1]}


# ------------------------------------------------------------ Zotero-Basis
def zotero_gesamtzahl():
    """Serverseitige Anzahl der Top-Level-Eintraege aus der Kopfzeile
    Total-Results. None, wenn die Auskunft nicht zu bekommen war.

    Laeuft ueber `get()` und damit mit demselben Wiederholungsbudget wie die
    Seitenabrufe. Vorher war ausgerechnet dieser Aufruf der einzige ohne
    Wiederholung, und an ihm haengt die ganze Schreibsperre.
    """
    antwort = get(f"https://api.zotero.org/groups/{GROUP}/items/top"
                  "?format=json&limit=1", kopf=True)
    if antwort is None:
        return None
    try:
        return int(antwort[1]["Total-Results"])
    except (KeyError, TypeError, ValueError) as e:
        print(f"  ! Kopfzeile Total-Results unbrauchbar: {e}", file=sys.stderr)
        return None


def zotero_baseline():
    """Alle Eintraege der Gruppe als Abgleichsbasis, inklusive Sperrliste.

    Gibt (eintraege, dois, vollstaendig) zurueck. Titelgleichheit auf's Zeichen
    reicht nicht: 'Neidhart in der MHDBDB' und 'Neidhart in der MHDBDB:
    Sachregister' sind dieselbe Arbeit. Deshalb wird zusaetzlich die Wortmenge
    jedes Titels vorgehalten, dazu Jahr und Nachnamen als titelunabhaengige
    Merkmale fuer `schon_bekannt()`.

    Eine fehlgeschlagene Seite ist kein Listenende. Wuerde sie wie eines
    behandelt, waere die Basis stillschweigend kuerzer, und eine kurze Basis
    macht Bekanntes zu Neuem: mit --write entstuenden daraus Dubletten. Deshalb
    wird der Abbruchgrund unterschieden und die Zahl der gelesenen Eintraege
    gegen die serverseitige Gesamtzahl gegengeprueft.
    """
    eintraege, dois = [], set()
    vollstaendig = True
    erwartet = zotero_gesamtzahl()
    gelesen, start = 0, 0
    while True:
        data = get(f"https://api.zotero.org/groups/{GROUP}/items/top"
                   f"?format=json&limit=100&start={start}")
        if data is None:
            PROBLEME.append(
                f"Zotero-Abgleichsbasis: Seite ab Eintrag {start} nicht "
                "abrufbar. Die Basis ist lueckenhaft."
            )
            vollstaendig = False
            break
        if not data:
            break
        gelesen += len(data)
        for it in data:
            d = it.get("data", {})
            t = d.get("title")
            if t:
                eintraege.append({
                    "titel": t,
                    "woerter": woerter(t),
                    "jahr": jahr_aus(d.get("date")),
                    "autoren": nachnamen(
                        [c.get("lastName") or c.get("name", "")
                         for c in (d.get("creators") or [])]),
                })
            for field in (d.get("DOI"), d.get("extra"), d.get("url")):
                if field:
                    for m in re.finditer(r"10\.\d{4,9}/[^\s\"<>,;]+", str(field)):
                        dois.add(clean_doi(m.group(0)))
        start += 100
        if start > 20000:
            PROBLEME.append("Zotero-Abgleichsbasis: Blaetter-Obergrenze von "
                            "20000 Eintraegen erreicht, Rest ungelesen.")
            vollstaendig = False
            break
    # Ohne Gegenprobe keine Freigabe. Faellt die Gesamtzahl aus, ist die Basis
    # nicht laenger geprueft, und ungeprueft ist hier dasselbe wie lueckenhaft:
    # `if not data: break` allein kann eine Seite, die mit HTTP 200 und leerer
    # Liste zurueckkommt, nicht vom Listenende unterscheiden. Die fruehere
    # Fassung liess die Pruefung in genau diesem Fall ersatzlos entfallen und
    # schaltete die Schreibsperre damit aus, statt sie einzuschalten.
    if erwartet is None:
        PROBLEME.append("Zotero-Abgleichsbasis: Gesamtzahl der Gruppe nicht "
                        "abrufbar, die Vollstaendigkeit ist ungeprueft.")
        vollstaendig = False
    elif gelesen != erwartet:
        PROBLEME.append(f"Zotero-Abgleichsbasis: {gelesen} von {erwartet} "
                        "Eintraegen gelesen.")
        vollstaendig = False
    return eintraege, dois, vollstaendig


def zweitmerkmal(kandidat, eintrag):
    """Ein vom Titel unabhaengiger Beleg dafuer, dass zwei Eintraege dieselbe
    Arbeit sind: ein gemeinsamer Nachname oder, ersatzweise, dasselbe Jahr.
    Gibt die Begruendung zurueck, sonst den leeren String.

    Das Jahr allein ist schwach, weil dieser Bestand sich auf wenige Jahre und
    ein Fachgebiet ballt. Es zaehlt deshalb nur, solange es der Autorenlage
    nicht widerspricht: kennen beide Seiten ihre Verfasser und teilen keinen,
    ist das ein Unterschied und kein fehlendes Merkmal. Gemessen am 23.09.2026
    an den 1848 Titeln der Gruppe: das Jahr trug 4 von 397 Urteilen, und zwei
    davon waren falsch ("Visual Text Analysis in Digital Humanities" verschluckt
    von "Digital Humanities", beide 2017).
    """
    kn = nachnamen(kandidat.get("authors"))
    en = eintrag.get("autoren", set())
    gemeinsam = kn & en
    if gemeinsam:
        return f"Autor {sorted(gemeinsam)[0]}"
    if kn and en:
        return ""
    kj, ej = jahr_aus(kandidat.get("date")), eintrag.get("jahr", "")
    if kj and ej and kj == ej:
        return f"Jahr {kj}"
    return ""


def schon_bekannt(kandidat, eintraege, dois):
    """Gibt zurueck: ('bekannt'|'verdacht'|'neu', passender Zoterotitel).

    Kurze Titel sind gefaehrlich, in beide Richtungen. Nach oben, weil
    "Quantifizierende historische Semantik" zwei Woerter mit einem
    Galloromania-Band teilt und sonst als Dublette gaelte. Nach unten, weil die
    Ueberlappung im Teilmengenfall rechnerisch immer 1,0 ist: steckt die
    Wortmenge des Kandidaten ganz in der eines Bestandstitels, ist jede
    Prozenthuerde wirkungslos. So verschwand jeder kurze Titel, der in einem
    laengeren Bestandstitel steckt. Gemessen am 23.09.2026: "Mittelhochdeutsche
    Begriffsdatenbank" galt als bekannt, weil "Die Mittelhochdeutsche
    Begriffsdatenbank als Werkzeug der Editionsphilologie" im Bestand liegt,
    und ein Bestandstitel aus einem einzigen Wort schluckte jeden Kandidaten,
    der dieses Wort enthaelt: 248 der 1848 Bestandstitel sind genau das
    ("Tristan", "Parzival", "Minnesang"). Haelt man jeden Bestandstitel einmal
    als hypothetischen Neufund gegen den restlichen Bestand, waeren nach der
    alten Regel 149 von 1848 still verschwunden, acht Prozent, darunter
    "Tristan als moench" hinter "Tristan".

    Der Teilmengenfall mit weniger als drei gemeinsamen Woertern braucht daher
    ein zweites, vom Titel unabhaengiges Merkmal (Autor oder Jahr, siehe
    `zweitmerkmal()`). Fehlt es, wird der Fund vorgelegt und als
    Dublettenverdacht markiert, statt still verworfen zu werden: ein
    ueberfluessiger Eintrag in der Pruefablage kostet einen Klick, ein
    verschwundener Fund ist unsichtbar.
    """
    if kandidat["doi"] and kandidat["doi"] in dois:
        return "bekannt", f"DOI {kandidat['doi']}"
    kw = woerter(kandidat["title"])
    if len(kw) < 2:                      # zu kurz fuer einen Wortvergleich
        kw = None
    bester, bestwert, bestschnitt = None, 0.0, 0
    belegt = None
    for e in eintraege:
        if kw is None:
            if entdiakritisiert(e["titel"]) == entdiakritisiert(kandidat["title"]):
                return "bekannt", e["titel"]
            continue
        wert = ueberlappung(kw, e["woerter"])
        schnitt = len(kw & e["woerter"])
        # Entschieden wird ueber Wert UND Schnittgroesse. Deshalb genuegt es
        # nicht, nur den hoechsten Wert mitzufuehren: im Teilmengenfall tragen
        # viele Eintraege denselben Wert 1,0, und ob geurteilt werden darf,
        # entscheidet ein anderes Merkmal als das, wonach sortiert wird. Gesucht
        # wird daher zweierlei: der aehnlichste Eintrag ueberhaupt (fuer die
        # Verdachtsmeldung) und der erste, der wirklich traegt.
        if (wert, schnitt) > (bestwert, bestschnitt):
            bester, bestwert, bestschnitt = e, wert, schnitt
        if belegt is None and wert >= 0.85:
            if schnitt >= 3:
                belegt = (e, "")
            else:
                beleg = zweitmerkmal(kandidat, e)
                if beleg:
                    belegt = (e, beleg)

    if belegt is not None:
        e, beleg = belegt
        return "bekannt", (f"{e['titel']} [{beleg}]" if beleg else e["titel"])
    if bester is None:
        return "neu", ""
    mit_jahr = f"{bester['titel']} ({bester['jahr']})" if bester["jahr"] else bester["titel"]
    if bestwert >= 0.85:
        return "verdacht", f"{mit_jahr}, Titelteilmenge ohne zweites Merkmal"
    if bestwert >= 0.6 and bestschnitt >= 3:
        return "verdacht", mit_jahr
    return "neu", ""


def ist_team(autoren):
    zeile = entdiakritisiert(" ; ".join(autoren or []))
    return [n for n in TEAM if n in zeile]


# ----------------------------------------------------------------- Quellen
# Konvention fuer alle Quellen: `get()` gibt None zurueck, wenn die Abfrage
# nicht beantwortet wurde, und eine leere Struktur, wenn sie beantwortet wurde
# und nichts enthielt. Nur das Erste ist ein Ausfall und gehoert in PROBLEME,
# sonst meldet sich ein Lauf als vollstaendig, in dem vier von fuenf Quellen
# geschwiegen haben. Drosselung schlaegt hier als 429 oder 503 durch und wird
# damit zu None; nur OpenAlex antwortet darauf mit HTTP 200 und count=0, und
# genau dafuer gibt es dort zusaetzlich den Kanarienvogel.
def src_zenodo():
    out = []
    for q, token in QUERIES:
        data = get(f"https://zenodo.org/api/records?q={quote(q)}&size=25&sort=newest")
        time.sleep(1)
        if data is None:
            PROBLEME.append(f"Zenodo: Abfrage \"{q}\" fehlgeschlagen.")
            continue
        if not data:
            continue
        for h in data.get("hits", {}).get("hits", []):
            m = h.get("metadata", {})
            out.append({
                "title": m.get("title", ""),
                "text": re.sub(r"<[^>]+>", " ", m.get("description") or "")[:3000],
                "date": str(m.get("publication_date", ""))[:10],
                "doi": clean_doi(h.get("doi", "")),
                "type": (m.get("resource_type") or {}).get("type", ""),
                "url": (h.get("links") or {}).get("self_html", ""),
                "authors": [c.get("name", "") for c in (m.get("creators") or [])],
                "venue": "Zenodo",
                "src": "Zenodo", "q": q, "token": token,
            })
    return out


def openalex_abfrage(q, seite=100):
    """Eine OpenAlex-Suche. Gibt None zurueck, wenn die Antwort unbrauchbar ist."""
    schluessel = os.environ.get("OPENALEX_API_KEY", "")
    url = ("https://api.openalex.org/works?search=" + quote(q)
           + f"&filter=from_publication_date:{SINCE}"
           + f"&per-page={seite}&mailto={MAIL}"
           + (f"&api_key={schluessel}" if schluessel else ""))
    return get(url)


def src_openalex():
    """OpenAlex antwortet beim Drosseln mit HTTP 200 und count=0 statt mit einem
    Fehler. Ein leeres Ergebnis ist deshalb nicht vertrauenswuerdig. Die Suche
    nach "MHDBDB" hat nachweislich Treffer; liefert sie null, ist die Quelle
    stumm und nicht leer."""
    for versuch in range(4):
        probe = openalex_abfrage("MHDBDB", seite=5)
        if probe and probe.get("meta", {}).get("count", 0) > 0:
            break
        wartezeit = 30 * (versuch + 1)
        print(f"    OpenAlex antwortet leer, warte {wartezeit}s "
              f"(Versuch {versuch + 1} von 4)", file=sys.stderr)
        time.sleep(wartezeit)
    else:
        PROBLEME.append(
            "OpenAlex lieferte auch nach vier Versuchen keine Treffer auf "
            "\"MHDBDB\". Die Quelle war gedrosselt, nicht leer. Dieser Lauf "
            "ist unvollstaendig."
        )
        return []

    out = []
    for q, token in QUERIES:
        data = openalex_abfrage(q)
        time.sleep(6)
        if data is None:
            PROBLEME.append(f"OpenAlex: Abfrage \"{q}\" fehlgeschlagen.")
            continue
        if not data.get("results"):
            PROBLEME.append(f"OpenAlex: Abfrage \"{q}\" kam leer zurueck.")
            continue
        for w in data.get("results", []):
            loc = (w.get("primary_location") or {}).get("source") or {}
            out.append({
                "title": w.get("title") or "",
                "text": unabstract(w.get("abstract_inverted_index"))[:3000],
                "date": w.get("publication_date", ""),
                "doi": clean_doi(w.get("doi", "")),
                "type": w.get("type", ""),
                "url": w.get("id", ""),
                "authors": [(a.get("author") or {}).get("display_name", "")
                            for a in (w.get("authorships") or [])][:12],
                "venue": loc.get("display_name", "") or "",
                "src": "OpenAlex", "q": q, "token": token,
            })
    return out


def src_openaire():
    out = []
    for q, token in QUERIES[:3]:
        data = get("https://api.openaire.eu/search/publications"
                   "?format=json&size=50&keywords=" + quote(q))
        time.sleep(1)
        if data is None:
            PROBLEME.append(f"OpenAIRE: Abfrage \"{q}\" fehlgeschlagen.")
            continue
        if not data:
            continue
        results = (data.get("response", {}).get("results") or {}).get("result") or []
        if isinstance(results, dict):
            results = [results]
        for r in results:
            try:
                meta = r["metadata"]["oaf:entity"]["oaf:result"]
            except (KeyError, TypeError):
                continue

            def flat(v):
                if isinstance(v, list):
                    v = v[0] if v else ""
                return v.get("$", "") if isinstance(v, dict) else str(v or "")

            pid = meta.get("pid") or []
            if isinstance(pid, dict):
                pid = [pid]
            doi = ""
            for p in pid:
                if isinstance(p, dict) and p.get("@classid") == "doi":
                    doi = clean_doi(p.get("$", ""))
            creators = meta.get("creator") or []
            if isinstance(creators, dict):
                creators = [creators]
            out.append({
                "title": flat(meta.get("title")),
                "text": flat(meta.get("description"))[:3000],
                "date": flat(meta.get("dateofacceptance"))[:10],
                "doi": doi, "type": "publication",
                "url": f"https://doi.org/{doi}" if doi else "",
                "authors": [flat(c) for c in creators][:12],
                "venue": "",
                "src": "OpenAIRE", "q": q, "token": token,
            })
    return out


def src_crossref():
    out = []
    for q, token in QUERIES:
        data = get("https://api.crossref.org/works?query.bibliographic=" + quote(q)
                   + f"&filter=from-pub-date:{SINCE}&rows=40&mailto={MAIL}")
        time.sleep(1)
        if data is None:
            PROBLEME.append(f"Crossref: Abfrage \"{q}\" fehlgeschlagen.")
            continue
        if not data:
            continue
        for it in data.get("message", {}).get("items", []):
            parts = (it.get("issued") or {}).get("date-parts") or [[]]
            auth = []
            for a in it.get("author") or []:
                auth.append(" ".join(x for x in [a.get("given"), a.get("family")] if x))
            out.append({
                "title": re.sub(r"<[^>]+>", "", " ".join(it.get("title") or [])),
                "text": re.sub(r"<[^>]+>", " ", it.get("abstract") or "")[:3000],
                "date": "-".join(str(x) for x in parts[0] if x is not None),
                "doi": clean_doi(it.get("DOI", "")),
                "type": it.get("type", ""),
                "url": f"https://doi.org/{it.get('DOI', '')}",
                "authors": auth[:12],
                "venue": " ".join(it.get("container-title") or []),
                "src": "Crossref", "q": q, "token": token,
            })
    return out


def src_semanticscholar():
    out = []
    for q, token in QUERIES[:2]:
        data = get("https://api.semanticscholar.org/graph/v1/paper/search?query="
                   + quote(q) + "&limit=50&fields=title,abstract,year,venue,"
                   "authors,externalIds,publicationTypes,url", tries=2)
        time.sleep(4)
        if data is None:
            # Der haeufigste Fall: unauthentifiziert antwortet Semantic Scholar
            # oft mit 429, und `tries=2` gibt dann schnell auf.
            PROBLEME.append(f"SemanticScholar: Abfrage \"{q}\" fehlgeschlagen.")
            continue
        if not data:
            continue
        for p in data.get("data") or []:
            ext = p.get("externalIds") or {}
            out.append({
                "title": p.get("title", ""),
                "text": (p.get("abstract") or "")[:3000],
                "date": str(p.get("year") or ""),
                "doi": clean_doi(ext.get("DOI", "")),
                "type": ",".join(p.get("publicationTypes") or []),
                "url": p.get("url", ""),
                "authors": [a.get("name", "") for a in (p.get("authors") or [])][:12],
                "venue": p.get("venue", "") or "",
                "src": "SemanticScholar", "q": q, "token": token,
            })
    return out


SOURCES = (src_zenodo, src_openalex, src_openaire, src_crossref, src_semanticscholar)


# -------------------------------------------------------- Zotero schreiben
TYPMAP = {
    "book-chapter": "bookSection", "bookSection": "bookSection",
    "book": "book", "monograph": "book", "edited-book": "book",
    "journal-article": "journalArticle", "article": "journalArticle",
    "JournalArticle": "journalArticle", "review": "journalArticle",
    "conference-paper": "conferencePaper", "proceedings-article": "conferencePaper",
    "Conference": "conferencePaper",
    "dataset": "dataset", "software": "computerProgram",
    "presentation": "presentation", "poster": "presentation",
    "posted-content": "preprint", "preprint": "preprint",
    "dissertation": "thesis", "thesis": "thesis",
    "report": "report", "publication": "document", "other": "document",
}
DOI_FELD = {"journalArticle", "conferencePaper", "preprint", "dataset", "report"}


def zotero_item(c, heute):
    typ = TYPMAP.get(c["type"], "document")
    herkunft = (f"Automatisch gefunden am {heute} | Quelle: {c['src']} | "
                f"Suche: \"{c['q']}\" | Evidenz: {c['evidenz']}")
    extra = [herkunft]
    if c.get("verdacht"):
        extra.append(f"ACHTUNG moegliche Dublette zu: {c['verdacht']}")
    if c.get("team"):
        extra.append("Gehoert vermutlich zu 'Eigene Publikationen' "
                     f"(Autor aus dem MHDBDB-Team: {', '.join(c['team'])})")
    # Was `split_name()` nicht als Person erkennt, wird nicht geraten, sondern
    # unzerlegt notiert: ein fehlender Autor ist korrigierbar, ein erfundener
    # sieht aus wie eine Angabe.
    creators, unklar = [], []
    for a in c.get("authors") or []:
        person = split_name(a)
        if person:
            creators.append(person)
        elif str(a).strip():
            unklar.append(str(a).strip())
    if unklar:
        extra.append("Verfasserangabe nicht zerlegbar, bitte pruefen: "
                     + " | ".join(unklar[:5]))
    it = {
        "itemType": typ,
        "title": c["title"][:500],
        "creators": creators,
        "date": c.get("date") or "",
        "url": c.get("url", "") or (f"https://doi.org/{c['doi']}" if c["doi"] else ""),
        "collections": [COL_PRUEFEN],
        "tags": [{"tag": "auto-fund"}, {"tag": f"auto-fund {heute[:7]}"}],
    }
    if c.get("verdacht"):
        it["tags"].append({"tag": "moegliche-dublette"})
    if c.get("team"):
        it["tags"].append({"tag": "eigene-publikation?"})
    if c["doi"]:
        if typ in DOI_FELD:
            it["DOI"] = c["doi"]
        else:
            extra.append(f"DOI: {c['doi']}")
    venue = c.get("venue") or ""
    if venue:
        feld = {"journalArticle": "publicationTitle", "bookSection": "bookTitle",
                "conferencePaper": "proceedingsTitle"}.get(typ)
        if feld:
            it[feld] = venue[:300]
        else:
            extra.append(f"Erschienen in: {venue}")
    it["extra"] = "\n".join(extra)
    return it


def zotero_write(cands, key, heute):
    kopf = {"Zotero-API-Key": key, "Content-Type": "application/json"}
    angelegt, fehler = 0, []
    for i in range(0, len(cands), 25):          # Zotero nimmt max. 50 pro Aufruf
        block = [zotero_item(c, heute) for c in cands[i:i + 25]]
        r = requests.post(
            f"https://api.zotero.org/groups/{GROUP}/items",
            headers=kopf,
            data=json.dumps(block, ensure_ascii=False).encode("utf-8"),
            timeout=90,
        )
        if r.status_code not in (200, 201):
            fehler.append(f"HTTP {r.status_code}: {r.text[:300]}")
            continue
        antwort = r.json()
        angelegt += len(antwort.get("successful", {}))
        for k, v in (antwort.get("failed") or {}).items():
            fehler.append(f"{block[int(k)]['title'][:60]}: {v}")
        time.sleep(2)
    return angelegt, fehler


# -------------------------------------------------------------------- Lauf
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2024-01-01")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    global SINCE
    SINCE = args.since
    heute = date.today().isoformat()

    print(f"MHDBDB-Erwaehnungssuche, Stand {heute}, Zeitfenster ab {SINCE}\n")

    eintraege, dois, basis_ok = zotero_baseline()
    print(f"Zotero-Abgleichsbasis: {len(eintraege)} Titel, {len(dois)} DOIs")

    found = []
    for fn in SOURCES:
        try:
            got = fn()
            print(f"  {fn.__name__:22s} {len(got):4d} Rohtreffer")
            found += got
        except Exception as e:
            print(f"  {fn.__name__:22s} FEHLER: {e}")
            PROBLEME.append(f"{fn.__name__} abgebrochen: {e}")

    seen, cands, unspezifisch, bekannt = set(), [], 0, 0
    for f in found:
        if not f["title"]:
            continue
        if NAME.search(f["title"] + " " + f.get("text", "")):
            f["evidenz"] = "Projektname in Titel oder Abstract"
        elif f["token"] and f["src"] in TOKEN_QUELLEN:
            f["evidenz"] = f"Index-Treffer auf \"{f['q']}\""
        else:
            unspezifisch += 1
            continue
        key = f["doi"] or norm(f["title"])[:80]
        if key in seen:
            continue
        seen.add(key)

        stand, treffer = schon_bekannt(f, eintraege, dois)
        if stand == "bekannt":
            bekannt += 1
            continue
        f["verdacht"] = treffer if stand == "verdacht" else ""
        f["team"] = ist_team(f.get("authors"))
        cands.append(f)
        # Damit zwei Fassungen derselben Arbeit im selben Lauf nicht doppelt
        # angelegt werden, zaehlt der neue Kandidat ab jetzt zur Basis.
        eintraege.append({"titel": f["title"], "woerter": woerter(f["title"]),
                          "jahr": jahr_aus(f.get("date")),
                          "autoren": nachnamen(f.get("authors"))})

    # `or ""`, weil ein Feld, das die Quelle mit null liefert, aus `.get()` als
    # None zurueckkommt. Der Vergleich str gegen None wuerde den Lauf hier
    # beenden, nach allen Netzabfragen und vor candidates.json.
    cands.sort(key=lambda x: x["date"] or "", reverse=True)
    print(f"\n{unspezifisch} als unspezifisch verworfen, {bekannt} schon in Zotero.")
    print(f"{len(cands)} neue Kandidaten:\n")
    for c in cands:
        ziel = f"https://doi.org/{c['doi']}" if c["doi"] else c["url"]
        marken = []
        if c["team"]:
            marken.append("EIGENE?")
        if c["verdacht"]:
            marken.append("DUBLETTE?")
        kopf = (" ".join(marken) + " ") if marken else ""
        print(f"- {c['date'] or 'o.J.':10s} | {c['src']:15s} | {kopf}{c['title'][:90]}")
        print(f"    {ziel}   [{c['evidenz']}]")
        if c["verdacht"]:
            print(f"    aehnlich zu: {c['verdacht']}")

    with open("candidates.json", "w", encoding="utf-8") as fh:
        json.dump(cands, fh, ensure_ascii=False, indent=1)

    if PROBLEME:
        print("\n" + "=" * 70)
        print("LAUF UNVOLLSTAENDIG. Es wurde nicht ueberall zuverlaessig "
              "gesucht oder abgeglichen:")
        for p in PROBLEME:
            print(f"  - {p}")
        print("Eine leere oder kurze Liste bedeutet hier NICHT, dass es nichts")
        print("Neues gibt. Lauf spaeter wiederholen.")
        print("=" * 70)
    else:
        print("\nAlle Quellen haben geantwortet, der Lauf ist vollstaendig.")

    if not args.write:
        print("\n(Trockenlauf, nichts geschrieben. Mit --write in Zotero anlegen.)")
        sys.exit(1 if PROBLEME else 0)

    if not basis_ok:
        print("\nFEHLER: Die Zotero-Abgleichsbasis ist unvollstaendig (siehe oben).")
        print("Gegen eine lueckenhafte Basis gilt Bekanntes als neu, und --write")
        print("legt daraus Dubletten an. Es wird nichts geschrieben.")
        sys.exit(1)

    if len(cands) > MAX_NEU:
        print(f"\nACHTUNG: {len(cands)} Kandidaten, es werden nur die "
              f"{MAX_NEU} neuesten angelegt. Rest siehe Liste oben.")
        cands = cands[:MAX_NEU]
    if not cands:
        print("\nNichts Neues, in Zotero bleibt alles unveraendert.")
        sys.exit(1 if PROBLEME else 0)

    key = os.environ.get("ZOTERO_API_KEY", "")
    if not key:
        print("\nFEHLER: ZOTERO_API_KEY nicht gesetzt.")
        sys.exit(1)
    angelegt, fehler = zotero_write(cands, key, heute)
    print(f"\n{angelegt} Eintraege in 'Zu pruefen (automatisch gefunden)' angelegt.")
    for f in fehler:
        print(f"  ! {f}")
    if PROBLEME or fehler:
        print("\nDieser Lauf war nicht vollstaendig, Exit-Status 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
