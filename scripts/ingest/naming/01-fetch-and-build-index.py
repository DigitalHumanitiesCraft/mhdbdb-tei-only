"""01-fetch-and-build-index.py

Holt Linda Beutel-Thurows kuratierte Naming-analysis-Daten von GitHub und
baut daraus den vorgebauten Index `data/naming-index.json.gz` für das
Playground-Modul "Erweiterte Figurenbezeichnungen" (Issue #59).

Quelle: https://github.com/lindabeutel/Naming-analysis (CC BY-NC-SA 4.0)
  - data/<Buch>/categorization_<Buch>.json   (primäre Datenquelle, 4 Werke;
    Linda 2026-03-04: buchspezifische Dateien verwenden, NICHT die globale
    lemma_categories.json — Kategorien sind kontextabhängig)
  - data/lemma_normalization.json            (kanonischer Name → Varianten;
    Alias-Quelle für die Eigenname-Klassifikation)

Dazu kommt eine werkspezifische Alias-Ergänzung auf unserer Seite:
  - scripts/ingest/naming/alias-overrides.json

lemma_normalization.json normalisiert werkübergreifend. Ein Alias, der nur in
einem Werk gilt, wäre dort semantisch falsch, deshalb liegt er hier statt in
Lindas Repo (Linda, #59-Kommentar 2026-07-28: „passt sehr gut"). Bisher genau
ein Eintrag: „Alexander" als Deckname des Paris im Trojanerkrieg.

Jeder Override nennt seine Kategorie: "deck" (Deckname, eigene vierte
Kategorie) oder "eig" (echter Eigenname, der nur in lemma_normalization.json
fehlt). Linda am 2026-08-10 zu Alexander: „Der Name sollte in dem Fall nicht
als 'Eigenname', sondern als 'Deckname' gelabelt werden." Ein Deckname
benennt die Figur wie ein Name, ist aber nicht ihrer — die Kategorie liegt
zwischen Eigenname und Antonomasie und darf in keiner der beiden aufgehen.

Datenmodell der categorization-Records (Excel-Erbe, pandas-Export):
  - Genau eines von drei Feld-Mustern trägt die Nennphrase:
      "Erzähler" befüllt                          → Erzähler nennt
      "Bezeichnung" + "Nennende Figur" befüllt    → Figurenrede
      "Eigennennung" befüllt                      → Selbstnennung
  - "Bezeichnung 1-4": Einzellemmata der Nennung. Eigenname, wenn das Lemma
    den Figurennamen trifft (case-insensitiv exakt oder Alias aus
    lemma_normalization.json — repliziert Lindas match_name_to_lemma aus
    naming_analysis/shared.py), Deckname bei einem "deck"-Override, sonst
    Antonomasie.
  - "Epitheta 1-5": bereits als Epitheta kategorisiert (Linda 2026-03-05).
  - "Vers": Float; Dezimalstellen sind echte Editions-Verszählungen (z.B.
    17.02 im Eneasroman). Die Zählung folgt Lindas Editionsgrundlagen und
    weicht teils von der MHDBDB-TEI-Zählung ab (nur ROL weitgehend
    deckungsgleich) — deshalb baut das Modul KEINE Reader-Deep-Links.

Bekannte Quirks, die dieses Skript bereinigt:
  - Literale NaN-Tokens im JSON (pandas) — JS JSON.parse würde scheitern.
  - NBSP (\\xa0) statt Leerzeichen in den Rolandslied-Werten (~1.029 Werte).
  - Figurennamen mit Unterstrichen im Rolandslied ("Gott_(christlich)").

Verwendung:
    python scripts/ingest/naming/01-fetch-and-build-index.py
        [--ref master] [--source-dir <lokale Kopie statt GitHub-Fetch>]
        [--require-commit]   # CI: hart failen statt Build-Zeit-Fallback (#152)

Kein Versions-Kanal in corpus-loader.js: das Modul lädt den Index lazy per
fetch+pako ohne IndexedDB-Cache (klein genug), daher gibt es hier keinen
Cache-Invalidierungs-Bump wie bei corpus-/authority-index (#94).

Der Build ist deterministisch (generatedAt = Committer-Datum des Quell-
Commits, gzip ohne mtime): gleicher Quellstand → byte-identischer Output.
Darauf baut der wöchentliche Auto-Update-Workflow
.github/workflows/naming-index-update.yml (rebuild → git diff → PR).
"""

import argparse
import gzip
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = PROJECT_ROOT / "data" / "naming-index.json.gz"
OVERRIDES_FILE = Path(__file__).resolve().parent / "alias-overrides.json"
JS_MODUL = PROJECT_ROOT / "playground" / "js" / "ui" / "tei" / "naming-explorer.js"

REPO = "lindabeutel/Naming-analysis"
RAW_BASE = "https://raw.githubusercontent.com/" + REPO

# Lindas Buchnamen → MHDBDB-Sigles (Cross-Reference verifiziert in #59,
# Kommentar 2026-05-16: alle 4 existieren im Korpus)
BOOKS = {
    "Iwein": "IW",
    "Eneasroman": "ENE",
    "Rolandslied": "ROL",
    "Trojanerkrieg": "TRO",
}

BEZEICHNUNG_COLS = ["Bezeichnung 1", "Bezeichnung 2", "Bezeichnung 3", "Bezeichnung 4"]
EPITHETA_COLS = ["Epitheta 1", "Epitheta 2", "Epitheta 3", "Epitheta 4", "Epitheta 5"]

# Kategorien im Index-Record, in Anzeigereihenfolge des Playgrounds.
CATS = ["eig", "deck", "ant", "epi"]

# Kategorien, die ein Override vergeben darf. "ant" waere sinnlos (das ist der
# Default ohne Override), "epi" kommt aus eigenen Spalten der Quelle.
OVERRIDE_CATS = {"eig", "deck"}

# Lindas Instanztypologie, Typname -> Marker, nach data/instance_types.json
# (schema_version 1.0). Dieselbe Liste steht als MARKER_KLASSEN im Frontend
# (playground/js/ui/tei/naming-explorer.js) und wird dort zur Legende.
#
# Der Guard unten haelt beide Seiten zusammen. Er ist noetig, weil das Repo
# woechentlich automatisch nachgezogen wird (naming-index-update.yml): ein
# neunter Typ oder ein neuer Marker kaeme sonst stumm in den Index, und die
# Legende erklaerte ihn nicht, ohne dass irgendetwas rot wird. Die Marker
# stehen hier als Zeichen, nicht als Regex: Lindas pattern-Felder sind
# Python-Syntax mit uneinheitlicher Verankerung und taugen nicht als
# gemeinsamer Vertrag zwischen Python und JS.
BEKANNTE_INSTANZTYPEN = {
    "Individual": None,
    "Collective": "[",
    "Role figure": "<",
    "Collective member": "<",
    "Group": " & ",
    "Non-figure": "{",
    "Quoted": "#",
    "Immaterial": "°",
}

# Zeichen, mit denen ein markierter Wert beginnen darf. Ein Wert, der mit
# einem anderen Sonderzeichen anfaengt, traegt einen Marker, den weder dieses
# Skript noch das Frontend kennt.
BEKANNTE_ANFANGSMARKER = {"[", "<", "{", "#", "°"}

# Zitierter Quellstand. Beide Werte muessen zu dem Ref passen, aus dem gebaut
# wird, und werden dagegen geprueft (pruefe_zitation). Getrennt von SOURCE_META
# stehen sie nur, damit die Pruefung sie nicht aus einem Satz herausparsen muss;
# in den Index geht weiterhin ausschliesslich SOURCE_META, unveraendert im
# Wortlaut, damit der Byte-Vergleich des Freshness-Gates gueltig bleibt.
QUELL_VERSION = "v0.2.1-beta"
QUELL_DOI = "10.5281/zenodo.21916576"

SOURCE_META = {
    "repo": "https://github.com/" + REPO,
    "doi": QUELL_DOI,
    "citation": f"Beutel-Thurow, L. (2026). Naming-analysis ({QUELL_VERSION}).",
    "license": "CC BY-NC-SA 4.0",
}


def filled(value):
    """True wenn das Feld inhaltlich befüllt ist (NaN/None/'' zählen nicht)."""
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    return str(value).strip() != ""


def clean(value):
    """NBSP → Leerzeichen, Whitespace kollabieren, strip."""
    s = str(value).replace("\xa0", " ")
    return " ".join(s.split())


def clean_figure_name(raw):
    """Anzeigename: Rolandslied-Unterstriche zu Leerzeichen."""
    return clean(raw).replace("_", " ")


def serialize_verse(value):
    """Float-Vers kompakt: 803.0 → '803', 17.02 → '17.02'."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return repr(value)
    return clean(value)


def classify(figure_name, lemma, aliases, deck_aliases):
    """Kategorie eines Bezeichnungs-Lemmas: 'eig', 'deck' oder 'ant'.

    Eigenname ist Lindas match_name_to_lemma (shared.py): case-insensitiv
    exakt oder Alias. Der Deckname wird zuerst geprueft: er ist die
    werkspezifische, einzeln begruendete Aussage und schlaegt deshalb den
    werkuebergreifenden Alias, falls ein Lemma beides traefe.
    """
    norm_lemma = lemma.lower().strip()
    if norm_lemma in deck_aliases:
        return "deck"
    if norm_lemma == figure_name.lower().strip() or norm_lemma in aliases:
        return "eig"
    return "ant"


def load_overrides():
    """alias-overrides.json → {buch: {figur_lowercase: {kategorie: {alias, ...}}}}.

    Schluessel unterhalb von "_readme" sind Buchnamen wie in BOOKS. Ein
    unbekannter Buch- oder Figurenname wuerde stumm wirkungslos bleiben,
    deshalb prueft build_index beide gegen die Daten.

    "category" ist Pflicht: der Unterschied zwischen einem Decknamen und einem
    schlicht fehlenden Eigennamen-Alias ist eine philologische Aussage, keine
    Voreinstellung, die ein neuer Eintrag stillschweigend erben darf.
    """
    raw = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    out = {}
    for book, figures in raw.items():
        if book.startswith("_"):
            continue
        out[book] = {}
        for name, entry in figures.items():
            cat = entry.get("category")
            if cat not in OVERRIDE_CATS:
                sys.exit(f"FEHLER: alias-overrides.json, {book}/{name}: "
                         f"category={cat!r} ist nicht erlaubt. Zulaessig sind "
                         f"{sorted(OVERRIDE_CATS)}.")
            out[book][name.lower()] = {cat: {a.lower() for a in entry["aliases"]}}
    return out


def pruefe_zitation(ref, source_dir):
    """Guard gegen eine Zitation, die nicht zum gebauten Quellstand passt.

    Der Index traegt Version und DOI der Quelle fest verdrahtet. Laufen sie
    auseinander, bricht nichts: die Seite laedt, die Tests laufen, die Daten
    stimmen. Nur die Angabe, worauf sie beruhen, ist falsch, und genau das ist
    die Klasse von Fehler, die still bleibt (JOURNAL 2026-07-31, "die vierte
    Stelle, die niemand pflegt"). Eine Pflegenotiz reicht dagegen messbar
    nicht, ein Abbruch schon.

    Anders als pruefe_instanztypen ist die Pruefung **symmetrisch**, und das
    ist kein Widerspruch: die Zitation muss zu ihrem Ref passen, in beide
    Richtungen. Ein alter Ref hat eine alte CITATION.cff, und dann ist die
    alte Angabe die richtige.

    Praktische Folge, beabsichtigt: sobald Linda ein Release macht, faellt der
    naechste Lauf gegen master, bis QUELL_VERSION und QUELL_DOI nachgezogen
    sind. Der Auto-Update-PR vom Montag kommt damit nicht mit neuen Daten
    unter alter Zitation durch, sondern gar nicht.
    """
    try:
        cff = fetch("CITATION.cff", ref, source_dir)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            sys.exit(f"FEHLER: CITATION.cff nicht abrufbar (HTTP {exc.code}). "
                     f"Das ist eine Stoerung, kein alter Quellstand.")
        print("   CITATION.cff: am Quellstand nicht vorhanden (404), "
              "Zitations-Vergleich uebersprungen")
        return
    except FileNotFoundError:
        print("   CITATION.cff: in der lokalen Quellkopie nicht vorhanden, "
              "Zitations-Vergleich uebersprungen")
        return

    def feld(name):
        """Wert eines Top-Level-Schluessels. Kein YAML-Parser, aber tolerant
        gegen die Schreibweisen, die CFF legal zulaesst: beide Anfuehrungs-
        zeichen und ein Kommentar am Zeilenende.

        Bewusst auf Spalte 0 verankert (`^` mit re.M): ein eingerueckter
        `version:`-Schluessel steht in einem `preferred-citation:`-Block und
        meint etwas anderes. Ebenso matcht `cff-version:` nicht auf `version`.
        """
        treffer = re.search(rf'^{name}:[ \t]*(.+?)[ \t]*$', cff, re.M)
        if not treffer:
            return None
        wert = re.sub(r'\s+#.*$', '', treffer.group(1)).strip()
        if len(wert) >= 2 and wert[0] == wert[-1] and wert[0] in "\"'":
            wert = wert[1:-1]
        return wert

    ihre_version, ihr_doi = feld("version"), feld("doi")
    if ihre_version is None or ihr_doi is None:
        sys.exit(f"FEHLER: CITATION.cff hat keine version- oder doi-Zeile auf "
                 f"oberster Ebene (version={ihre_version!r}, doi={ihr_doi!r}). "
                 f"Stehen sie eingerueckt, etwa in einem identifiers- oder "
                 f"preferred-citation-Block, muss diese Pruefung angepasst "
                 f"werden; QUELL_VERSION nachzuziehen hilft dann nicht.")

    if (ihre_version, ihr_doi) != (QUELL_VERSION, QUELL_DOI):
        sys.exit(f"FEHLER: Die Zitation passt nicht zum gebauten Quellstand.\n"
                 f"  CITATION.cff: {ihre_version} / {ihr_doi}\n"
                 f"  hier fest:    {QUELL_VERSION} / {QUELL_DOI}\n"
                 f"QUELL_VERSION und QUELL_DOI nachziehen. Der Index wuerde "
                 f"sonst neue Daten unter alter Zitation ausliefern.")

    print(f"   CITATION.cff: {ihre_version}, DOI passt")


def pruefe_instanztypen(ref, source_dir):
    """Drift-Guard gegen Lindas data/instance_types.json (#59).

    **Die Pruefung ist absichtlich asymmetrisch**, und das ist keine Nachlaes-
    sigkeit, sondern die Bedingung dafuer, dass sie ueberhaupt laufen kann.
    Dieses Skript wird an zwei Stellen mit gegenlaeufigen Erwartungen
    aufgerufen:

      - der Montags-Workflow baut mit --ref master, will also den NEUESTEN
        Quellstand gegen den heutigen Code pruefen;
      - das Freshness-Gate in data-integrity.yml baut mit --ref <Pin des
        ausgelieferten Index>, will also einen HISTORISCHEN Quellstand mit
        heutigem Code reproduzieren.

    Eine symmetrische Pruefung waere im zweiten Fall garantiert rot, sobald
    Linda die Typologie erweitert: der alte Quellstand kennt den neuen Typ
    naturgemaess nicht. Deshalb ist nur die eine Richtung ein Fehler:

      - Die Quelle kennt einen Typ, den wir nicht kennen  -> HART. Nur so
        herum geht der Legende etwas verloren, und es kann nur bei einem
        frischen Build passieren.
      - Wir kennen einen Typ, den die Quelle (noch) nicht hat -> Hinweis.
        Die Legende zeigt ihn schlicht nie, weil kein Wert seinen Marker
        traegt.
      - Ein Typ steht auf beiden Seiten, traegt aber einen anderen Marker
        -> HART, in beide Richtungen. Das ist echte Drift und keine Frage
        des Alters.

    Fehlt die Datei ganz, ist der Quellstand aelter als die Typologie (sie
    kam am 2026-08-11 dazu, der zuletzt ausgelieferte Index haengt an
    b7cc0585 vom 2026-08-10 und liefert dort HTTP 404). Das ist ein Hinweis,
    kein Fehler; pruefe_marker_in_werten laeuft unabhaengig davon weiter und
    schuetzt die Daten selbst.

    example_values wird bewusst nicht geprueft: Linda erklaert die Listen in
    note_on_scope ausdruecklich als illustrativ und nicht gepflegt ("code must
    not treat them as a closed vocabulary").
    """
    try:
        roh = json.loads(fetch("data/instance_types.json", ref, source_dir))
    except urllib.error.HTTPError as exc:
        # NUR 404 heisst "an diesem Quellstand gibt es die Datei noch nicht".
        # 429, 500 und 503 sind Stoerungen und duerfen den harten Teil des
        # Guards nicht stillschweigend abschalten: die uebrigen Fetches
        # koennen dabei gelingen, der Index waere gebaut und der Montags-PR
        # eroeffnet, ohne dass die Typologie je verglichen wurde.
        if exc.code != 404:
            sys.exit(f"FEHLER: data/instance_types.json nicht abrufbar "
                     f"(HTTP {exc.code}). Das ist kein alter Quellstand, "
                     f"sondern eine Stoerung. Lauf wiederholen.")
        print("   instance_types.json: am Quellstand nicht vorhanden (404), "
              "Typologie-Vergleich uebersprungen")
        return
    except FileNotFoundError:
        print("   instance_types.json: in der lokalen Quellkopie nicht "
              "vorhanden, Typologie-Vergleich uebersprungen")
        return
    except Exception as exc:                      # noqa: BLE001
        sys.exit(f"FEHLER: data/instance_types.json nicht lesbar ({exc}). "
                 f"Ohne sie ist nicht pruefbar, ob die Marker-Legende im "
                 f"Frontend noch zur Quelle passt.")

    ihre = {t.get("name"): t.get("marker") for t in roh.get("types", [])}
    if not ihre:
        sys.exit("FEHLER: data/instance_types.json enthaelt keine types[].")
    if None in ihre:
        sys.exit("FEHLER: data/instance_types.json hat einen types[]-Eintrag "
                 "ohne 'name'. Ohne Namen ist er nicht zuordenbar.")

    neu = sorted(set(ihre) - set(BEKANNTE_INSTANZTYPEN))
    if neu:
        sys.exit(f"FEHLER: Die Quelle kennt Instanztypen, die dieser Build "
                 f"nicht kennt: {neu}. BEKANNTE_INSTANZTYPEN hier und "
                 f"MARKER_KLASSEN in playground/js/ui/tei/naming-explorer.js "
                 f"nachziehen, dann die Legende pruefen.")

    # Ihr Marker-Feld schreibt das Fuellzeichen mit ("[…]", "#…"); verglichen
    # wird deshalb der Anfang, nicht der ganze String. Group traegt " & " ohne
    # Fuellzeichen und faellt damit auf Gleichheit zurueck.
    for name, unser in BEKANNTE_INSTANZTYPEN.items():
        if name not in ihre:
            continue
        ihr = ihre[name]
        if unser is None:
            if ihr is not None:
                sys.exit(f"FEHLER: Typ {name!r} traegt jetzt den Marker {ihr!r}, "
                         f"hier gilt er als markerlos.")
        elif ihr is None or not ihr.startswith(unser):
            sys.exit(f"FEHLER: Typ {name!r} hat den Marker {ihr!r}, erwartet "
                     f"wurde ein Marker beginnend mit {unser!r}.")

    fehlend = sorted(set(BEKANNTE_INSTANZTYPEN) - set(ihre))
    hinweis = f", {len(fehlend)} hier bekannte fehlen dort ({fehlend})" if fehlend else ""
    print(f"   instance_types.json: {len(ihre)} Typen, Marker unveraendert{hinweis}")


def pruefe_frontend_paritaet():
    """Haelt MARKER_KLASSEN im Frontend und BEKANNTE_INSTANZTYPEN zusammen.

    Ohne diese Pruefung stehen drei Listen derselben Typologie im Repo (hier,
    im JS-Modul und im Playwright-Spec), und nur eine davon haengt an einem
    Gate. Der Ausfall waere genau der, den der Typologie-Guard verhindern
    soll: Linda fuehrt einen Typ ein, der Build failt und nennt beide Stellen,
    jemand zieht nur die Python-Seite nach, und danach ist der Build gruen,
    der Index traegt die neuen Marker und die Legende kennt sie nicht.

    Verglichen wird ueber die **Marker**, nicht ueber die Namen: 'Role figure'
    und 'Collective member' teilen sich '<' und stehen im Frontend bewusst in
    einer Zeile, es muss also je Marker mindestens eine Klasse geben.
    """
    text = JS_MODUL.read_text(encoding="utf-8")
    block = re.search(r"const MARKER_KLASSEN = \[(.*?)\];", text, re.S)
    if not block:
        sys.exit(f"FEHLER: MARKER_KLASSEN nicht in {JS_MODUL.name} gefunden. "
                 f"Wurde die Konstante umbenannt, muss diese Pruefung mit.")
    js_ids = set(re.findall(r"id:\s*'([^']+)'", block.group(1)))

    unbekannt = sorted(js_ids - set(BEKANNTE_INSTANZTYPEN))
    if unbekannt:
        sys.exit(f"FEHLER: {JS_MODUL.name} kennt Klassen, die hier keinen Typ "
                 f"haben: {unbekannt}.")

    je_marker = {}
    for name, marker in BEKANNTE_INSTANZTYPEN.items():
        if marker is not None:
            je_marker.setdefault(marker, []).append(name)
    fehlend = sorted(m for m, typen in je_marker.items() if not set(typen) & js_ids)
    if fehlend:
        sys.exit(f"FEHLER: Fuer die Marker {fehlend} fuehrt "
                 f"{JS_MODUL.name} keine Klasse. Die Legende wuerde Werte mit "
                 f"diesem Marker nicht erklaeren. MARKER_KLASSEN nachziehen.")

    print(f"   Frontend-Paritaet: {len(js_ids)} Klassen, alle Marker abgedeckt")


def pruefe_figuren_markerfrei(werte):
    """Lindas Invariante an der benannten Figur: dort steht nie ein Marker.

    "markers qualify an entity's role as a naming instance, not the entity
    itself" (instance_types.json), und die Legende sagt das dem Nutzer
    woertlich zu. Eine Zusage, die die Ansicht macht, muss der Build pruefen,
    sonst liefe ein '[X]' als eigener Figurname neben 'X' ins Auswahlfeld,
    ohne dass etwas rot wird.

    Geprueft wird gegen die **bekannten Marker**, nicht gegen jedes
    Sonderzeichen. Ein Figurname darf mit einem Anfuehrungszeichen oder einer
    Klammer beginnen, ohne dass das die woechentliche Pipeline anhaelt; die
    Invariante spricht von Markern und nicht von Interpunktion.
    """
    verdaechtig = sorted({w for w in werte if w and w[0] in BEKANNTE_ANFANGSMARKER})
    if verdaechtig:
        sys.exit(f"FEHLER: {len(verdaechtig)} benannte Figuren tragen einen "
                 f"Marker: {verdaechtig[:10]}. Mit Linda klaeren, ob die "
                 f"Invariante noch gilt, bevor hier etwas nachgezogen wird.")


def pruefe_marker_in_werten(werte, feld, erlaubt, hinweis):
    """Unbekannte Marker in den Werten der nennenden Instanz.

    Die Typologie kann unveraendert sein und trotzdem ein Zeichen auftauchen,
    das keine Klasse abdeckt. Geprueft wird der Wortanfang.

    **Bekannte Luecke, bewusst offen gelassen:** ein Marker im Wortinneren
    faellt hier nicht auf. Die heutigen Innen-Marker sind Klammern
    ('[rechen] des Eneas') und damit ueber ihr oeffnendes Zeichen erfasst,
    aber ' & ' fuer Gruppen widerlegt die bequeme Verallgemeinerung "innen
    heisst Klammer": es steht per Konstruktion in der Mitte und ist keine.
    Ein kuenftiger Separator-Marker nach demselben Muster rutscht also durch
    beide Haelften des Guards.

    Nicht geschlossen, weil die Alternative teurer waere als der Fall: ein
    Test auf beliebige Sonderzeichen im Wortinneren schlaegt bei Apostrophen,
    Bindestrichen und den Qualifier-Klammern '(heidnisch)' an, also bei
    regulaeren Daten. Und die Luecke greift nur, wenn Linda einen solchen
    Marker einfuehrt, OHNE ihn in instance_types.json zu deklarieren; tut sie
    es dort, faengt ihn pruefe_instanztypen.
    """
    verdaechtig = sorted({
        w for w in werte
        if w and not w[0].isalnum() and w[0] not in erlaubt
    })
    if verdaechtig:
        sys.exit(f"FEHLER: {len(verdaechtig)} {feld} beginnen mit einem "
                 f"unbekannten Marker: {verdaechtig[:10]}. {hinweis}")


def fetch(path, ref, source_dir):
    if source_dir:
        return (source_dir / path).read_text(encoding="utf-8")
    url = f"{RAW_BASE}/{ref}/{path}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def resolve_commit(ref, require=False):
    """Provenienz: Commit-SHA + Committer-Datum des Refs.

    Ohne require=True best effort (interaktiv/lokal). Mit require=True
    (CI, #152) harter Fehler: ein stiller Fallback auf Build-Zeit machte
    den Build nicht-deterministisch und verlor die Provenienz (leerer PR
    ohne source.commit).

    Nutzt GITHUB_TOKEN aus der Umgebung, wenn gesetzt: unauthentifizierte
    api.github.com-Calls von GitHub-Runnern teilen sich das IP-Rate-Limit
    und schlagen sporadisch mit 403 fehl — genau die Flakiness, die das
    harte Gate nicht haben darf.
    """
    url = f"https://api.github.com/repos/{REPO}/commits/{ref}"
    try:
        headers = {"Accept": "application/vnd.github+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {"sha": data["sha"], "date": data["commit"]["committer"]["date"]}
    except Exception as exc:  # noqa: BLE001 — Provenienz optional, ausser require
        if require:
            sys.exit(f"FEHLER (--require-commit): Commit für Ref '{ref}' nicht "
                     f"auflösbar ({exc}). Ohne aufgelösten Commit wäre der Build "
                     f"nicht-deterministisch (generatedAt = Build-Zeit) und die "
                     f"Provenienz (source.commit) ginge verloren (#152).")
        print(f"   (Commit nicht auflösbar: {exc})")
        return None


def build_record(row, figure_name, aliases, deck_aliases):
    """Ein categorization-Record → kompakter Index-Record (oder None)."""
    if filled(row.get("Bezeichnung")) and filled(row.get("Nennende Figur")):
        who, by = "fig", clean(row["Nennende Figur"])
        phrase = clean(row["Bezeichnung"])
    elif filled(row.get("Erzähler")):
        who, by = "erz", None
        phrase = clean(row["Erzähler"])
    elif filled(row.get("Eigennennung")):
        who, by = "self", None
        phrase = clean(row["Eigennennung"])
    elif filled(row.get("Bezeichnung")):
        # Figurenrede ohne erfasste nennende Figur (3x im Iwein)
        who, by = "fig", None
        phrase = clean(row["Bezeichnung"])
    else:
        return None

    buckets = {cat: [] for cat in CATS}
    for col in BEZEICHNUNG_COLS:
        val = row.get(col)
        if not filled(val):
            continue
        lemma = clean(val)
        buckets[classify(figure_name, lemma, aliases, deck_aliases)].append(lemma)

    buckets["epi"] = [clean(row[col]) for col in EPITHETA_COLS if filled(row.get(col))]

    record = {"v": serialize_verse(row.get("Vers")), "ph": phrase, "who": who}
    if by:
        record["by"] = by
    for cat in CATS:
        if buckets[cat]:
            record[cat] = buckets[cat]
    return record


def build_index(ref, source_dir):
    pruefe_zitation(ref, source_dir)
    pruefe_instanztypen(ref, source_dir)
    pruefe_frontend_paritaet()
    normalization = json.loads(fetch("data/lemma_normalization.json", ref, source_dir))
    # Alias-Lookup: kanonischer Name (lowercase) → Set lowercased Varianten
    alias_map = {
        clean_figure_name(k).lower(): {clean(v).lower() for v in variants}
        for k, variants in normalization.items()
    }

    overrides = load_overrides()
    unbekannt = set(overrides) - set(BOOKS)
    if unbekannt:
        sys.exit(f"FEHLER: alias-overrides.json nennt unbekannte Werke: "
                 f"{sorted(unbekannt)}. Bekannt sind {sorted(BOOKS)}.")

    works = []
    totals = {"records": 0, **{cat: 0 for cat in CATS}}
    namer_werte = set()
    figur_werte = set()

    for book_name, sigle in BOOKS.items():
        raw = json.loads(fetch(f"data/{book_name}/categorization_{book_name}.json", ref, source_dir))
        buch_overrides = overrides.get(book_name, {})
        figures = {}
        skipped = 0
        for row in raw:
            if not filled(row.get("Benannte Figur")):
                skipped += 1
                continue
            if filled(row.get("Nennende Figur")):
                namer_werte.add(clean(row["Nennende Figur"]))
            figure_name = clean_figure_name(row["Benannte Figur"])
            figur_werte.add(figure_name)
            aliases = alias_map.get(figure_name.lower(), set())
            extra = buch_overrides.get(figure_name.lower(), {})
            aliases = aliases | extra.get("eig", set())
            record = build_record(row, figure_name, aliases, extra.get("deck", set()))
            if record is None:
                skipped += 1
                continue
            figures.setdefault(figure_name, []).append(record)
            totals["records"] += 1
            for cat in CATS:
                totals[cat] += len(record.get(cat, []))

        # Ein vertippter Figurenname im Override bliebe sonst stumm wirkungslos:
        # der Eintrag stuende in der Datei, die Klassifikation liefe unveraendert.
        fehlend = sorted(set(buch_overrides) - {n.lower() for n in figures})
        if fehlend:
            sys.exit(f"FEHLER: alias-overrides.json nennt fuer {book_name} "
                     f"Figuren, die dort nicht vorkommen: {fehlend}")

        works.append({
            "sigle": sigle,
            "bookName": book_name,
            "figures": {name: figures[name] for name in sorted(figures, key=str.lower)},
        })
        print(f"   {sigle:4s} ({book_name}): {sum(len(v) for v in figures.values())} Records, "
              f"{len(figures)} Figuren, {skipped} übersprungen")

    pruefe_marker_in_werten(
        namer_werte, "Werte der nennenden Instanz", BEKANNTE_ANFANGSMARKER,
        "Entweder ist es ein neuer Instanztyp (dann BEKANNTE_INSTANZTYPEN und "
        "MARKER_KLASSEN nachziehen) oder ein Datenfehler bei Linda.")
    pruefe_figuren_markerfrei(figur_werte)
    return works, totals


def main():
    parser = argparse.ArgumentParser(
        description="Naming-analysis-Daten fetchen und data/naming-index.json.gz bauen (#59)")
    parser.add_argument("--ref", default="master",
                        help="Git-Ref im Quell-Repo (Default: master)")
    parser.add_argument("--source-dir", type=Path, default=None,
                        help="Lokale Repo-Kopie statt GitHub-Fetch (offline/reproduzierbar)")
    parser.add_argument("--require-commit", action="store_true",
                        help="Harter Fehler statt Build-Zeit-Fallback, wenn der "
                             "Quell-Commit nicht auflösbar ist (CI, #152)")
    args = parser.parse_args()
    if args.require_commit and args.source_dir:
        parser.error("--require-commit ist mit --source-dir nicht kombinierbar "
                     "(lokale Kopie hat keinen auflösbaren Quell-Commit)")

    print("=" * 60)
    print("MHDBDB Naming Index Builder (#59)")
    print("=" * 60)
    src = args.source_dir or f"GitHub {REPO}@{args.ref}"
    print(f"\nQuelle: {src}")

    commit = None
    if not args.source_dir:
        commit = resolve_commit(args.ref, require=args.require_commit)
        if commit:
            print(f"   Commit: {commit['sha']} ({commit['date']})")

    print("\nBaue Index...")
    # Fetch unter dem RESOLVIERTEN SHA, nicht unter dem beweglichen Ref:
    # zwischen resolve_commit und den raw-Fetches kann das Quell-Repo einen
    # Push erhalten (bzw. der raw-CDN cached Branch-Refs ~5 min) — dann
    # truege der Index source.commit=X bei Inhalt=Y, und das Freshness-Gate
    # (data-integrity.yml) meldet spaeter falschen Drift (Review PR #155).
    fetch_ref = commit["sha"] if commit else args.ref
    works, totals = build_index(fetch_ref, args.source_dir)

    # generatedAt = Committer-Datum des Quell-Commits, nicht Build-Zeit:
    # zwei Builds desselben Quellstands sind dadurch byte-identisch (#125-
    # Prinzip), was den git-diff-Check in naming-index-update.yml trägt.
    # Fallback Build-Zeit nur offline/--source-dir (dann kein Auto-Diff).
    generated_at = (commit or {}).get("date") or \
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    index = {
        "version": "1.0.0",
        "generatedAt": generated_at,
        "source": {**SOURCE_META, "ref": args.ref,
                   **({"commit": commit["sha"]} if commit else {})},
        "works": works,
    }

    print(f"\nGesamt: {totals['records']} Records | "
          f"Eigennamen-Lemmata: {totals['eig']} | "
          f"Decknamen-Lemmata: {totals['deck']} | "
          f"Antonomasien-Lemmata: {totals['ant']} | "
          f"Epitheta: {totals['epi']}")

    json_data = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    uncompressed = len(json_data.encode("utf-8"))
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    # mtime=0: kein Zeitstempel im gzip-Header, sonst wäre jeder Build
    # byte-verschieden und der Workflow-Diff immer dirty.
    with gzip.GzipFile(OUTPUT_FILE, mode="wb", mtime=0) as f:
        f.write(json_data.encode("utf-8"))
    compressed = OUTPUT_FILE.stat().st_size

    print(f"\nGespeichert: {OUTPUT_FILE}")
    print(f"   Unkomprimiert: {uncompressed / 1024:.0f} KB")
    print(f"   Komprimiert:   {compressed / 1024:.0f} KB")


if __name__ == "__main__":
    main()
