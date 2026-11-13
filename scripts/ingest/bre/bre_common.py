"""bre_common.py: gemeinsame Konstanten und Helfer des BRE-Ingests (Weingruesse, #147).

Quelle: Brevitas-Wiki (MediaWiki), Transkriptionen von Silvan Wagner.
Rohtext nur ueber die API (der Renderer verschluckt die Spitzklammern der
editorischen Ergaenzungen).
"""
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO / "temp" / "bre-wiki"
INGEST_DIR = REPO / "ingest" / "bre"
MANIFEST = INGEST_DIR / "revisionen.tsv"
SEGMENTIERUNG = INGEST_DIR / "segmentierung.tsv"

API = "https://wiki.brevitas.org/mediawiki_1_43/api.php"
WIKI_BASIS = "https://wiki.brevitas.org/mediawiki_1_43/index.php"
USER_AGENT = ("MHDBDB-Ingest/0.1 (+https://github.com/DigitalHumanitiesCraft/"
              "mhdbdb-tei-only/issues/147)")
MIN_ABSTAND = 2.0
VERSUCHE = 3

DOKU_TITEL = "Dokumentation Edition Weingrüße"
LISTE_MARKE = "=====Einzelne Weingrüße====="

# Hauptseite: Abschnitt "Überlieferung" (Überlieferungsbeschreibung je Zeuge) ist fuer die
# Werkzuordnung massgeblich (Silvan Wagner ueber KZW, #147, 2026-11-12). HAUPT_REVID ist die
# Revision, mit der ein Manifest ohne Hauptseite ergaenzt wird (31127 vom 2026-11-11; der
# Abschnitt "Überlieferung" ist mit Revision 30019 vom 2026-06-15 wortgleich, gemessen
# 2026-11-13: beide Revisionen unterscheiden sich nur in der Kopfzeile der Seite).
HAUPT_TITEL = "Kategorie:Quelle Weingruß"
HAUPT_REVID = 31127

# Editionssigle -> (Transkriptionsseite ohne Praefix "Weingrüße ", MHDBDB-Sigle).
# Vorlaeufig (Koordination, #147).
ZEUGEN = {
    "B": ("Cgm 713", "BRE_CGM713"),
    "B1": ("Mgq 2370", "BRE_MGQ2370"),
    "B2": ("Mgq 495", "BRE_MGQ495"),
    "C": ("MS Ger. 74", "BRE_MSGER74"),
    "D": ("Mscr. M 50", "BRE_MSCRM50"),
    "F": ("5339a", "BRE_HS5339A"),
    "H1": ("Cpg 98", "BRE_CPG98"),
    "L": ("Ms. 1590", "BRE_MS1590"),
    "M1": ("Cgm 216", "BRE_CGM216"),
    "N2": ("Merkel 2° 966", "BRE_MERKEL966"),
    "R": ("Cod. 29.6 Aug. 4°", "BRE_GUELF296"),
    "S": ("Cod. 13711", "BRE_COD13711"),
    "U": ("Georg. 150.8°", "BRE_GEORG1508"),
    "W": ("Cod. Quart 564", "BRE_QUART564"),
    "W1": ("Cod. Oct 145", "BRE_OCT145"),
    "d1": ("GW M43176 (d1)", "BRE_D1"),
    "d2": ("VD16 ZV 32099 (d2)", "BRE_D2"),
    "d3": ("VD16 ZV 29685 (d3)", "BRE_D3"),
    "d4": ("VD16 ZV 15959 (d4)", "BRE_D4"),
    "d5": ("VD16 R 439 (d5)", "BRE_D5"),
    "d6": ("VD16 ZV 30224 (d6)", "BRE_D6"),
}
TRANSKRIPTIONS_PRAEFIX = "Weingrüße "

# Vorspann: Zeilen vor dem ersten Textanfang der Segmentierung, je Zeuge ausdruecklich
# (bereinigter Text wie bre_wikitext.vergleichstext, exakter Vergleich). Jede Abweichung
# ist ein harter Fehler, auch ein Vorspann bei einem Zeugen, der hier nicht steht.
#   reihentitel          -> <head> des aeusseren <div> (der Reihe)
#   text_ohne_einzelseite-> eigenes <div type="section">, erste Zeile = <head>
#   fragment             -> eigenes <div type="section"> ohne <head>
# (Gemessen 2026-10-23 an den gepinnten Revisionen, Koordination #147.)
VORSPANN = {
    "S": ("reihentitel", ["Wein grüs pier grüs und met grüs"]),
    "d1": ("reihentitel", ["Ein schoner spruch vom wein met und bier"]),
    "d2": ("reihentitel", ["Ain schöner Spruch von Lobung Wein, Met und Byer"]),
    "d3": ("reihentitel", ["Raͤbhaͤnszlin"]),
    "d4": ("reihentitel", ["Ein hübscher spruch von dem edlen weyn"]),
    "d5": ("reihentitel", ["Rebhenßlins segen"]),
    "d6": ("reihentitel", ["Rebhenssleins Grus und Segen"]),
    "N2": ("text_ohne_einzelseite", [
        "Ain spruch vom rebhänßlin",
        "Gott hatt geschaff(e)n mich so rechtt",
        "Mich lobtt der herr und auch der knecht",
        "Die lame(n) krippel mach ich dantz(e)n",
        "Fechtt(e)n \\auch mit feüchtt(e)n lantz(e)n/",
    ]),
    "R": ("fragment", [
        "Du seist pey fraue(n) oder pey man(n)en",
        "So kum her wider pey rechten zeiten",
        "Wen(n) ich den mu(n)d offt in dy swem(m) muß reite(n)",
    ]),
}
VORSPANN_NOTIZ = {
    "text_ohne_einzelseite": "Keiner Einzeltextseite im Brevitas-Wiki zugeordnet.",
    # {werk}: bre_common.VORSPANN_WERK. Die Hauptseite fuehrt R unter "Weinsegen Allerliebster
    # Trost (nur die letzten drei Verse)"; in der Synopse der Einzeltextseite fehlt R.
    "fragment": "Fragment von {werk}: nur die letzten drei Verse. Zuordnung nach der "
                "Überlieferungsbeschreibung der Hauptseite (Brevitas-Wiki, Abschnitt Überlieferung).",
}

# Zeuge -> Einzeltext (Seitentitel ohne Autorzusatz), dessen Text der Vorspann ist, wo die
# Hauptseite das ausdruecklich sagt. R: Hauptseite, Abschnitt Ueberlieferung, R: "Weinsegen
# Allerliebster Trost (nur die letzten drei Verse)" (Revision 31127; wortgleich in 30019).
VORSPANN_WERK = {"R": "Weinsegen Allerliebster Trost"}

# Abweichungen zwischen der Hauptseite (Liste unter ";Sigle") und der Segmentierung, die
# geprueft sind: (Zeuge, art, Text, bisher, laut Hauptseite) -> Befund, der Schluessel ist
# bre_hauptseite.schluessel() und traegt den Inhalt der Abweichung (Anzahl, bei einer anderen
# Reihenfolge die Stellen und Folgen). Eine andere Abweichung der gleichen Art, etwa eine
# zusaetzliche Vertauschung, ist ein anderer Schluessel und bricht 02-convert-wiki-to-mhdbdb.py
# ab. Der Eintrag erklaert die Abweichung oder haelt sie als offene Frage fest, er korrigiert
# nichts. Gemessen 2026-11-13 gegen Revision 31127 (03-hauptseite-abgleich.py).
_KLAMMER = ("eigener Abschnitt", "in Klammern (kein eigener Text)")
ABWEICHUNG_ERKLAERT = {
    ("B2", "nur_bisher", "Weinsegen Allerliebster Trost", "1x", "fehlt"):
        "offen: Fehlansatz (2 Verse, 3 gestrichene) vor dem Weingruss Allerliebster Trunck; die "
        "Einzeltextseite fuehrt ihn als 'falscher Eintrag', Hauptseite (Liste und Uebersicht) kennt "
        "18 Texte, der Satz dort nennt 19",
    ("B2", "reihenfolge", "",
     "ab Stelle 15: Weinsegen Allerliebster Trost > Weingruß Allerliebster Trunck",
     "ab Stelle 15: Weingruß Allerliebster Trunck > Weinsegen Allerliebster Trost"):
        "offen: Folge des Fehlansatzes, er steht vor dem Weingruss Allerliebster Trunck, der Weinsegen "
        "Allerliebster Trost der Hauptseite danach",
    ("N2", "nur_bisher", "Pseudo-Weingruß Noes Pau", "1x", "fehlt"):
        "erklaert: Hauptseite nennt ihn im Fliesstext (S. 113v, 'nicht mehr als Weingruss zu zaehlen')",
    ("W1", "nur_bisher", "Pseudo-Weingruß Her Fein", "1x", "fehlt"):
        "erklaert: Hauptseite nennt ihn im Fliesstext als siebten Text des ersten Teils",
    ("d4", "reihenfolge", "",
     "ab Stelle 2: Weingruß Edels Getranck > Weinsegen Edle Leibsalb",
     "ab Stelle 2: Weinsegen Edle Leibsalb > Weingruß Edels Getranck"):
        "offen: Liste der Hauptseite fuehrt Edle Leibsalb vor Edels Getranck, die Uebersicht der "
        "Hauptseite (Stellung 2 und 3) und die Synopsen fuehren Edels Getranck zuerst; der Fliesstext "
        "sagt, die ersten Verspaare beider seien vertauscht",
    ("d5", "nur_bisher", "Weingruß Süsser Geschmack", "1x", "fehlt"):
        "erklaert: Liste der Hauptseite unvollstaendig (19 Eintraege, Satz nennt 20 Weingruesse und "
        "den Vorspruch); die Uebersicht fuehrt ihn als Stellung 19",
    ("d5", "nur_bisher", "Weinsegen Ein Kron", "1x", "fehlt"):
        "erklaert: wie Suesser Geschmack, Uebersicht Stellung 20",
    ("d6", "klammer_aber_abschnitt", "Weingruß Allerliebster Trunck") + _KLAMMER:
        "offen: Hauptseite setzt sechs Texte in Klammern (rudimentaer in Edles Abkuelen assimiliert, "
        "keine eigenen Texte); die Segmentierung schneidet davon drei als eigene Abschnitte",
    ("d6", "klammer_aber_abschnitt", "Weinsegen Allerliebster Trost") + _KLAMMER:
        "offen: wie Allerliebster Trunck",
    ("d6", "klammer_aber_abschnitt", "Weinsegen Ein Kron") + _KLAMMER:
        "offen: wie Allerliebster Trunck",
}

# Faltung NUR fuer den Vergleich erster Vers <-> Transkriptionszeile, nie fuer die Ausgabe.
# Jede Anwendung wird ausgegeben (Erratum an Silvan Wagner).
FALTUNG = {"ů": "uͦ"}  # ů (U+016F) ~ uͦ (u + U+0366)


class HarterFehler(Exception):
    """Abbruch mit Meldung; main() gibt sie aus und beendet mit Exit 1."""


def transkriptions_titel(sigle):
    if sigle not in ZEUGEN:
        raise HarterFehler(f"unbekannte Editionssigle {sigle!r}; bekannt: {', '.join(ZEUGEN)}")
    return TRANSKRIPTIONS_PRAEFIX + ZEUGEN[sigle][0]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cache_pfad(revid):
    return CACHE_DIR / f"rev_{int(revid)}.json"


def api_abruf(params, letzter=[0.0]):
    """Ein API-Aufruf mit Hoeflichkeitsabstand und Wiederholung bei Netzfehlern."""
    url = API + "?" + urllib.parse.urlencode(params)
    letzter_fehler = None
    for versuch in range(VERSUCHE):
        warte = MIN_ABSTAND - (time.monotonic() - letzter[0])
        if warte > 0:
            time.sleep(warte)
        letzter[0] = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            letzter_fehler = e
            time.sleep(2.0 * (versuch + 1))
    raise HarterFehler(f"API-Abruf fehlgeschlagen nach {VERSUCHE} Versuchen: {url}: {letzter_fehler}")


def seite_aus_antwort(antwort, erwartet):
    """Aus einer query-Antwort genau eine Seite mit genau einer Revision; sonst harter Fehler."""
    if "error" in antwort:
        raise HarterFehler(f"API-Fehler fuer {erwartet}: {antwort['error']}")
    seiten = antwort.get("query", {}).get("pages", [])
    if len(seiten) != 1:
        raise HarterFehler(f"{erwartet}: {len(seiten)} Seiten in der Antwort statt 1")
    s = seiten[0]
    if s.get("missing"):
        raise HarterFehler(f"Seite fehlt im Wiki: {erwartet}")
    revs = s.get("revisions", [])
    if len(revs) != 1:
        raise HarterFehler(f"{erwartet}: {len(revs)} Revisionen in der Antwort statt 1")
    r = revs[0]
    for feld in ("revid", "timestamp", "user"):
        if feld not in r:
            raise HarterFehler(f"{erwartet}: Feld {feld} fehlt in der Revision")
    try:
        inhalt = r["slots"]["main"]["content"]
    except KeyError:
        raise HarterFehler(f"{erwartet}: slots.main.content fehlt")
    if not isinstance(inhalt, str) or not inhalt.strip():
        raise HarterFehler(f"{erwartet}: Inhalt leer")
    return {
        "titel": s["title"], "pageid": s["pageid"], "revid": r["revid"],
        "timestamp": r["timestamp"], "user": r["user"], "inhalt": inhalt,
    }


def lade_manifest():
    """titel -> dict(pageid, revid, timestamp, user, sha256). Harter Fehler, wenn es fehlt."""
    if not MANIFEST.exists():
        raise HarterFehler(f"Manifest fehlt: {MANIFEST} (erst 00-fetch-wiki.py ausfuehren)")
    zeilen = MANIFEST.read_text(encoding="utf-8").splitlines()
    kopf = zeilen[0].split("\t")
    erwartet = ["titel", "pageid", "revid", "timestamp", "user", "sha256"]
    if kopf != erwartet:
        raise HarterFehler(f"Manifest-Kopf {kopf} != {erwartet}")
    m = {}
    for i, z in enumerate(zeilen[1:], 2):
        if not z.strip():
            continue
        f = z.split("\t")
        if len(f) != 6:
            raise HarterFehler(f"Manifest Zeile {i}: {len(f)} Felder statt 6")
        m[f[0]] = dict(zip(erwartet[1:], f[1:]))
    return m


def lade_seite(titel):
    """Gepinnte Seite aus dem Cache laden (Manifest + Cache, sha256 geprueft)."""
    m = lade_manifest()
    if titel not in m:
        raise HarterFehler(f"Seite nicht im Manifest: {titel}")
    e = m[titel]
    p = cache_pfad(e["revid"])
    if not p.exists():
        raise HarterFehler(f"Cache fehlt fuer {titel} (rev {e['revid']}): {p}; 00-fetch-wiki.py ausfuehren")
    seite = json.loads(p.read_text(encoding="utf-8"))
    if sha256_text(seite["inhalt"]) != e["sha256"]:
        raise HarterFehler(f"sha256-Abweichung im Cache fuer {titel} (rev {e['revid']})")
    return seite


def einzeltext_titel(doku_inhalt):
    """Die Titel der Einzeltextseiten aus dem Rohtext der Dokumentationsseite.

    Liest die Wikilinks hinter der Marke bis zur naechsten Ueberschrift.
    """
    if LISTE_MARKE not in doku_inhalt:
        raise HarterFehler(f"Marke {LISTE_MARKE!r} nicht in {DOKU_TITEL}")
    rest = doku_inhalt.split(LISTE_MARKE, 1)[1]
    m = re.search(r"^=+[^=\n]+=+\s*$", rest, re.M)
    if m:
        rest = rest[:m.start()]
    titel = []
    for z in rest.splitlines():
        if not z.strip():
            continue
        links = re.findall(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]", z)
        if not links:
            raise HarterFehler(f"Zeile in der Einzeltext-Liste ohne Wikilink: {z!r}")
        titel.extend(l.strip() for l in links)
    if len(set(titel)) != len(titel):
        raise HarterFehler("doppelte Titel in der Einzeltext-Liste")
    return titel


def ausgabe_utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
