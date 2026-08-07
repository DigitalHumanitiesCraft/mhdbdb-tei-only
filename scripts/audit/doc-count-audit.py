#!/usr/bin/env python3
"""Korpus- und Authority-File-Zaehlungen aus den Daten extrahieren und mit
den in der Doku verankerten Zahlen abgleichen.

Hintergrund: bei jeder Korpus-Aenderung (z.B. WZB-Aufnahme 2026-05-08
hat das Korpus von 666 auf 667 Dateien gebracht) muessen mehrere Stellen
in docs/TEI-MODEL.md, docs/INDEX.md und docs/ROADMAP.md mitwandern,
sonst driftet die Doku schnell. Dieser Audit zeigt den aktuellen Stand
plus die Stellen in den Docs, wo die Zahlen NICHT mehr stimmen.

Es ist explizit kein Auto-Fixer: das Script meldet Drift, aendert aber
keine Doku. Die Begruendung ("WZB +1") gehoert in den Commit, nicht in
eine generische Markdown-Edit.

Usage:
    python scripts/audit/doc-count-audit.py             # default: full report
    python scripts/audit/doc-count-audit.py --check     # exit non-zero bei drift
"""
import argparse
import glob
import io
import re
import sys
from pathlib import Path
from lxml import etree

# scripts/ auf den Pfad, damit der Parity-Normalizer und die gemeinsame
# Korpusauswahl (#287) importierbar sind
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mhg_normalizer import normalize_mhg
from corpus_files import corpus_files

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)


def count_xml_elements(path: str, xpath: str) -> int:
    """Count elements matching xpath in path (TEI namespace assumed)."""
    tree = etree.parse(path)
    return len(tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))


def count_variants_normalized(path: str) -> int:
    """Distinct normalized forms in variants.xml — die Zahl, gegen die die
    Suche tatsächlich prüft (Variants-Dictionary dedupliziert nach
    MHG-Normalisierung, siehe CONTRACTS.md). Muss mit dem JS-Build der
    Runtime-Map übereinstimmen; Parity haengt an normalize_mhg()."""
    tree = etree.parse(path)
    orth_tag = '{http://www.tei-c.org/ns/1.0}orth'
    normed = set()
    for form in tree.xpath('//tei:form[@xml:id]',
                           namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        orth = form.find(orth_tag)
        text = orth.text if orth is not None else form.text
        if text and text.strip():
            normed.add(normalize_mhg(text.strip()))
    return len(normed)


def collect_counts() -> dict:
    counts = {}
    counts['corpus_files'] = len(corpus_files())
    counts['authority_files'] = len(glob.glob('authority-files/*.xml'))
    counts['lexicon_entries'] = count_xml_elements('authority-files/lexicon.xml', '//tei:entry[@xml:id]')
    counts['variants_entries'] = count_xml_elements('authority-files/variants.xml', '//tei:entry[@corresp]')
    counts['variants_forms'] = count_xml_elements('authority-files/variants.xml', '//tei:form[@xml:id]')
    counts['variants_normalized'] = count_variants_normalized('authority-files/variants.xml')
    counts['persons'] = count_xml_elements('authority-files/persons.xml', '//tei:person[@xml:id]')
    counts['works'] = count_xml_elements('authority-files/works.xml', '//tei:bibl[@xml:id]')
    counts['concepts'] = count_xml_elements('authority-files/concepts.xml', '//tei:category[@xml:id]')
    counts['genres'] = count_xml_elements('authority-files/genres.xml', '//tei:category[@xml:id]')
    counts['names'] = count_xml_elements('authority-files/names.xml', '//tei:category[@xml:id]')
    counts['contributors_persons'] = count_xml_elements('authority-files/contributors.xml', '//tei:person[@xml:id]')
    counts['contributors_orgs'] = count_xml_elements('authority-files/contributors.xml', '//tei:org[@xml:id]')
    return counts


# Zahl unterhalb derer der Ziffern-Scan (find_stale_numbers) gar nicht erst
# laeuft: zu viele False Positives aus Tabellen-Indizes, Prozenten,
# Abschnitts- und Versionsnummern. Als Konstante, damit die Anker-
# Selbstpruefung dieselbe Schwelle melden kann statt sie zu verschweigen.
NUMERIC_SCAN_MIN = 100

# Ausnahmen von NUMERIC_SCAN_MIN (#297 Punkt 1). Die 100er-Schwelle schuetzt
# gegen Tabellenindizes, Prozente und Abschnittsnummern; sie macht das Audit
# aber blind fuer jede Datenzahl darunter. names.xml war die erste
# doc-gepruefte Authority-Datei unter der Schwelle (90 Kategorien) und stand
# damit still in docs/TEI-MODEL.md; contributors.xml (52) kam 2026-08-02 aus
# demselben Grund dazu. Zulaessig ist die Absenkung nur bei einem
# Key, dessen Anker die Zahl eng bindet und dessen Drift-Fenster klein bleibt:
# bei 90 sind das +-2, es werden also nur 88 bis 92 mit direkt folgendem
# "Kategorien" oder "Namen" gemeldet.
#
# Die Absenkung gilt KEY-GLOBAL, nicht pro (Datei, Key): kommt der Key spaeter
# in einem zahlenreichen Target dazu (INDEX.md, ROADMAP.md), waechst die
# Fehlalarmflaeche still mit. Dann pro Target entscheiden statt hier absenken.
SCAN_MIN_OVERRIDE = {'names': 50, 'contributors_persons': 50}

# min_digits (find_stale_numbers) koppelt die Stellenzahl an diese Schwelle
# und kennt nur zwei- oder dreistellig. Ein Override unter 10 waere still
# wirkungslos: der Scan liefe, das Muster faende die einstellige Zahl nie,
# und die Selbstpruefung meldete nichts, weil weder Schwelle noch Anker
# verletzt sind. Genau das Muster 'konfiguriert, gruen, prueft nichts'.
if SCAN_MIN_OVERRIDE and min(SCAN_MIN_OVERRIDE.values()) < 10:
    # raise statt assert: ein assert verschwindet unter python -O, und diese
    # Pruefung soll auch dort halten.
    raise SystemExit('SCAN_MIN_OVERRIDE unter 10 braucht zuerst ein '
                     'einstelliges Ziffernmuster in find_stale_numbers')


def scan_min_for(key: str) -> int:
    return SCAN_MIN_OVERRIDE.get(key, NUMERIC_SCAN_MIN)


# (Datei, Key)-Paare, die BEWUSST keine Zahl fuehren (#297 Punkt 4). Ohne
# diese Liste meldet die Selbstpruefung sie als Abdeckungsluecke, obwohl sie
# das Gegenteil sind: eine Entscheidung. Das Target bleibt konfiguriert, damit
# eine spaeter doch eingesetzte Zahl sofort gegatet ist.
INTENTIONALLY_SILENT = {
    ('README.md', 'entry_points'):
        'nennt sechs Explorer und zwoelf Werkzeuge einzeln, nie die Summe',
    ('docs/ARCHITECTURE.md', 'entry_points'):
        'nennt die Werkzeuge einzeln in der Routing-Tabelle, nie als Summe',
    ('docs/ARCHITECTURE.md', 'tei_tools'):
        'nennt die Werkzeuge einzeln in der Routing-Tabelle, nie als Summe',
    ('docs/INDEX.md', 'entry_points'):
        'verweist seit #316 auf FEATURES.md, statt den Katalog samt Zahlen zu wiederholen',
    ('docs/INDEX.md', 'tei_tools'):
        'verweist seit #316 auf FEATURES.md, statt den Katalog samt Zahlen zu wiederholen',
    # Die folgenden fuenf sind mit #342 dazugekommen, nicht weil sich die
    # Dokumente geaendert haetten, sondern weil die Selbstpruefung seither die
    # Zahlbindung verlangt statt blossem Vorkommen des Ankerworts. Jede
    # Begruendung ist gemessen: die Ist-Zahl kommt in der Datei nicht vor.
    ('docs/ARCHITECTURE.md', 'corpus_files'):
        'beschreibt Komponenten und Datenfluss, nennt die Korpusgroesse nirgends',
    ('docs/ARCHITECTURE.md', 'variants_forms'):
        'nennt den Varianten-Mechanismus, nie die Zahl der Formen',
    ('docs/ARCHITECTURE.md', 'variants_normalized'):
        'nennt den Varianten-Mechanismus, nie die Zahl der Mappings',
    # ('docs/DECISIONS.md', 'lexicon_entries') stand hier bis 2026-08-07 mit der
    # Begruendung "ADRs begruenden Entscheidungen; die Lexikongroesse fuehren
    # TEI-MODEL und DATA-MODEL". ADR-018 nennt die Zahl jetzt selbst (als
    # Nenner: 1 von 43.879 Lemmata ist kuratiert), also greift der Anker und
    # die Ausnahme waere eine Luecke statt einer Feststellung. Die
    # Selbstpruefung hat den Eintrag im selben Lauf als veraltet gemeldet.
    ('docs/DECISIONS.md', 'variants_normalized'):
        'ADR-015 nennt nur die historischen Formzahlen der Regenerierung, nie die Mappings',
    # Mit #316 dazu, und die Uebersetzung hat hier nichts kaputtgemacht,
    # sondern etwas sichtbar: die bisherige Bindung traf "43.879 Eintraege",
    # also die Lexikonzahl, und wurde nur vom Drift-Fenster verworfen. Von
    # variants.xml nennt die Datei die Zahl der Formen (Zeile 169), nie die
    # der Eintraege.
    ('docs/DATA-MODEL.md', 'variants_entries'):
        'nennt von variants.xml nur die Formenzahl, nie die Zahl der Eintraege',
}


# Explizite Ausnahme-Mengen statt -1/-2-Offsets (Review PR #222): beim
# naechsten Werkzeug-Zuwachs hier pflegen, nicht in Zaehl-Magie suchen.
NON_TOOL_MODULES = {'tei-ui.js'}                 # Router, kein Werkzeug
MODAL_MODULES = {'multi-lemma-search.js'}        # folgt dem DESIGN-Pattern nicht
PRE_DESCRIBED_TOOLS = {                          # in hilfe-playground vorab
    'multi-lemma-search.js',                     # beschrieben; §5 zaehlt den
    'verse-position-search.js',                  # Rest als "weitere Werkzeuge"
}


def collect_code_counts() -> dict:
    """Code-abgeleitete Counts (Carearbeit-Lehre 2026-07-13: Drift-Klasse
    Nr. 1 sind Werkzeug-/Entry-Point-Zahlen, nicht Datenzahlen).

    Ableitungen folgen den Doku-Konventionen:
    - TEI-Werkzeuge = Module in playground/js/ui/tei/ minus NON_TOOL_MODULES
      (multi-lemma-search.js zaehlt als Werkzeug Nr. 1)
    - Pattern-Module (DESIGN.md) = Werkzeuge minus MODAL_MODULES
    - Authority-Explorer = die sechs show*Btn-Buttons der Authority-Sidebar
    - Entry Points = Explorer + Werkzeuge
    - "weitere Werkzeuge" (hilfe-playground §5) = Werkzeuge minus
      PRE_DESCRIBED_TOOLS
    - UI-Module = alle .js unter playground/js/ui/ (Gesamtzahl des
      Modulbaums in ARCHITECTURE.md §UI Layer, #276)"""
    counts = {}
    counts['ui_modules'] = len(glob.glob('playground/js/ui/**/*.js', recursive=True))
    module_names = {Path(m).name for m in glob.glob('playground/js/ui/tei/*.js')}
    known = NON_TOOL_MODULES | MODAL_MODULES | PRE_DESCRIBED_TOOLS
    missing = known - module_names
    if missing:
        sys.exit(f'FEHLER: Ausnahme-Mengen nennen nicht existierende Module: {sorted(missing)} '
                 f'— NON_TOOL_MODULES/MODAL_MODULES/PRE_DESCRIBED_TOOLS pflegen.')
    tools_set = module_names - NON_TOOL_MODULES
    counts['tei_tools'] = len(tools_set)
    counts['pattern_modules'] = len(tools_set - MODAL_MODULES)
    counts['tei_tools_weitere'] = len(tools_set - PRE_DESCRIBED_TOOLS)
    html = Path('playground/index.html').read_text(encoding='utf-8')
    counts['authority_explorers'] = len(re.findall(
        r'id="show(?:Authors|Works|Lemmata|Concepts|Genres|Names)Btn"', html))
    counts['entry_points'] = counts['authority_explorers'] + counts['tei_tools']
    return counts


# (label, key, formatted-as-found-in-docs)
LABELS = [
    ('Korpus-Dateien (tei/)', 'corpus_files'),
    ('Authority-Dateien (authority-files/)', 'authority_files'),
    ('lexicon.xml — Lemmata', 'lexicon_entries'),
    ('variants.xml — Eintraege', 'variants_entries'),
    ('variants.xml — Formen', 'variants_forms'),
    ('variants.xml — normalisiert dedupliziert', 'variants_normalized'),
    ('persons.xml — Personen', 'persons'),
    ('works.xml — Werke', 'works'),
    ('concepts.xml — Kategorien', 'concepts'),
    ('genres.xml — Kategorien', 'genres'),
    ('names.xml — Kategorien', 'names'),
    ('contributors.xml — Personen', 'contributors_persons'),
    ('contributors.xml — Organisationen', 'contributors_orgs'),
]

# Doc paths to scan for drift. Each entry is (path, keys-that-should-match).
# Patterns search for any occurrence of the count number that is NOT the
# actual current value — when found, that means the doc is stale.
DOC_TARGETS = [
    ('docs/TEI-MODEL.md', ['corpus_files', 'lexicon_entries', 'works', 'persons',
                            'concepts', 'genres', 'names', 'variants_entries', 'variants_forms',
                            'contributors_persons']),
    ('docs/INDEX.md', ['corpus_files']),
    ('docs/ROADMAP.md', ['corpus_files']),
    # Beide tragen undatierte Ist-Angaben zu variants.xml und standen bis
    # 2026-07-28 nicht im Audit; sie blieben deshalb bei 256.761 stehen.
    ('docs/DATA-MODEL.md', ['variants_forms', 'variants_entries', 'variants_normalized',
                            'works']),  # works: #293 hat die 584 in Prosa gebracht
    ('docs/TEI-MODEL-AUTH-FILES.md', ['variants_forms', 'variants_entries',
                                       'contributors_persons']),
    # CONTRACTS.md:315 beschreibt den Ist-Aufbau des Variants-Dictionary; der
    # Datumsstempel dort macht die Zeile nicht historisch.
    ('docs/CONTRACTS.md', ['variants_forms', 'variants_normalized']),
    # ARCHITECTURE.md und DECISIONS.md standen bis 2026-07-31 in KEINER
    # Datenzahl-Liste (#276, Luecke 1): ARCHITECTURE.md nur in
    # CODE_DOC_TARGETS, DECISIONS.md ueberhaupt nirgends. Dadurch konnte in
    # ARCHITECTURE.md "~257k mappings" stehenbleiben, waehrend das Runtime-
    # Dictionary 234.243 Eintraege hat. ARCHITECTURE.md beschreibt Stufe 2
    # der Lemma-Aufloesung und den Woerterbuch-Registeraufbau, DECISIONS.md
    # traegt in ADR-005/ADR-013/ADR-014 Korpus- und Varianten-Zahlen.
    ('docs/ARCHITECTURE.md', ['corpus_files', 'lexicon_entries',
                              'variants_forms', 'variants_normalized']),
    # Achtung ADR-Eigenart: ADRs nennen bewusst historische Zahlen
    # ("On the day of the decision ... 13 modules", "192,472 -> 256,759
    # variant forms"). Stumm bleiben die aus drei verschiedenen Gruenden,
    # nicht aus einem: "256,759 variant forms" haelt der Pfeil-Skip in
    # find_stale_numbers, "13 modules" der HISTORICAL_MARKERS-Skip in
    # find_stale_wordcounts, "64,287 variant forms" allein die Fenster-
    # Distanz zum Ist-Wert (der Fenster-Check laeuft vor dem Anker-Abgleich,
    # die Zahl faellt also raus, obwohl ihr Anker bindet; Probe: auf 250.000
    # gesetzt wird sie gemeldet). Ohne die ersten beiden produziert dieses Target
    # Dauer-Fehlalarme und wird abgeschaltet.
    ('docs/DECISIONS.md', ['corpus_files', 'lexicon_entries',
                           'variants_forms', 'variants_normalized']),
    # CLAUDE.md is intentionally vague ("~670 TEI texts"), no exact check.
    # User-facing HTML-Seiten (#192): hartkodierte Kennzahlen driften mit
    # jedem Ingest. Konvention (erklaert auf hilfe-daten.html):
    # variants_forms = rohe orthographische Varianten,
    # variants_normalized = dedupliziert — die Zahl, die Suche/Playground zeigen.
    #
    # docs/ARCHITECTURE.md und docs/DECISIONS.md fuehren fuer
    # variants_normalized seit #279/#294 KEINE Zahl mehr, sondern verweisen
    # auf CONTRACTS §C. Ihr Target bleibt trotzdem stehen, aber mit einer
    # ehrlicheren Erwartung als "Ratsche" (Review PR #305): gefangen wird
    # nur eine AUSGESCHRIEBENE Wiedereinsetzung ("234.244 Mappings").
    #
    # Ausgerechnet die Form, die dort vorher stand, faellt durch: "~257k"
    # matcht das Ziffernmuster nicht (zwischen 7 und k liegt keine
    # Wortgrenze), und selbst "~257.000" faengt der Rundungs-Skip ab. Das
    # ist kein Versehen, sondern die Grenze des Verfahrens: eine gerundete
    # Angabe ist per Konvention erlaubt, und ob sie sich auf die richtige
    # Groesse bezieht, kann ein Ziffern-Scan nicht wissen. Genau daran ist
    # #279 aufgefallen, und zwar per Hand, nicht per Gate.
    ('README.md', ['corpus_files', 'lexicon_entries']),
    # schema/README.md mit #356. Die Datei fuehrt die Bestandstabelle der acht
    # Authority Files ein zweites Mal, stand aber in keiner Target-Liste: am
    # 2026-08-06 waren fuenf ihrer Zahlen veraltet (lexicon 43.750, variants
    # 192.472 Formen und 39.282 Gruppen, works 583, contributors 51), waehrend
    # dieselben Werte in den gegateten Dateien stimmten. Genau der Mechanismus,
    # den dieses Skript verhindern soll, nur eine Datei ausserhalb seiner Liste.
    # Die 2 Organisationen bleiben ungegatet: einstellige Zahlen liegen unter
    # der Scan-Untergrenze, und ein Override darunter waere still wirkungslos.
    ('schema/README.md', ['corpus_files', 'lexicon_entries', 'variants_forms',
                          'variants_entries', 'works', 'persons', 'concepts',
                          'genres', 'names', 'contributors_persons']),
    # index.html traegt den Stats-Block der Startseite (TEI-Texte, Lemmata,
    # rohe Varianten-Formen). Fehlte bis 2026-07-28 im Audit, deshalb blieb
    # dort 256.761 stehen, waehrend #138 alle anderen Seiten auf 256.760 zog.
    ('index.html', ['corpus_files', 'lexicon_entries', 'variants_forms']),
    ('hilfe-daten.html', ['corpus_files', 'lexicon_entries',
                          'variants_forms', 'variants_normalized',
                          'contributors_persons']),
    ('hilfe-korpussuche.html', ['variants_normalized']),
    ('hilfe-playground.html', ['variants_normalized']),
    ('hilfe-daten-beitragen.html', ['variants_forms']),
    ('playground/index.html', ['variants_normalized']),
]

CODE_LABELS = [
    ('Playground — UI-Module gesamt (js/ui/)', 'ui_modules'),
    ('Playground — TEI-Analyse-Werkzeuge', 'tei_tools'),
    ('Playground — davon "weitere" (hilfe §5)', 'tei_tools_weitere'),
    ('Playground — Pattern-Module (DESIGN)', 'pattern_modules'),
    ('Playground — Authority-Explorer', 'authority_explorers'),
    ('Playground — Search Entry Points', 'entry_points'),
]

# Kleine, code-abgeleitete Counts stehen in den Docs meist als Zahlwort
# ("zwoelf TEI-Analysewerkzeuge", "Twelve analysis tools") oder kleine
# Ziffer ("all 18 entry points") — der numerische Scan oben greift dafuer
# nicht (Untergrenze 100). Eigener Wortzahl-Scan mit engen Ankern.
CODE_DOC_TARGETS = [
    ('README.md', ['tei_tools', 'authority_explorers', 'entry_points']),
    ('docs/INDEX.md', ['tei_tools', 'entry_points']),
    ('docs/FEATURES.md', ['tei_tools', 'entry_points']),
    ('docs/ARCHITECTURE.md', ['tei_tools', 'pattern_modules', 'entry_points',
                              'ui_modules']),
    ('docs/DESIGN.md', ['pattern_modules']),
    # #276 Luecke 1: DECISIONS.md wurde von keinem der beiden Scans beruehrt.
    # ADR-002 haelt die Modulzahl (historisch markiert, siehe oben).
    ('docs/DECISIONS.md', ['ui_modules']),
    ('hilfe-playground.html', ['tei_tools', 'tei_tools_weitere', 'authority_explorers']),
    # playground/readme.md mit #356. Die Datei fuehrte bis dahin genau EINES
    # der zwoelf TEI-Werkzeuge auf und nannte an dritter Stelle "11 search
    # types"; der Katalog ist jetzt ein Verweis auf FEATURES.md, die beiden
    # Summen bleiben und werden deshalb hier gebunden.
    ('playground/readme.md', ['tei_tools', 'authority_explorers']),
]

NUMBER_WORDS = {
    'fuenf': 5, 'fünf': 5, 'sechs': 6, 'sieben': 7, 'acht': 8, 'neun': 9,
    'zehn': 10, 'elf': 11, 'zwoelf': 12, 'zwölf': 12, 'dreizehn': 13,
    'vierzehn': 14, 'fuenfzehn': 15, 'fünfzehn': 15, 'sechzehn': 16,
    'siebzehn': 17, 'achtzehn': 18, 'neunzehn': 19, 'zwanzig': 20,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20,
}

CODE_ANCHORS = {
    'tei_tools': r'(?:TEI-Analyse-?[Ww]erkzeuge|TEI-Analysewerkzeuge|(?:TEI[- ])?analysis tools|Analyse-Werkzeuge|Werkzeuge)',
    'tei_tools_weitere': r'weitere\s+Werkzeuge',
    # Beide Sprachen: die Docs stellen auf Englisch um (#316), DESIGN.md
    # traegt den Count noch deutsch. Ohne die englische Variante ging die
    # Bindung in ARCHITECTURE.md still verloren, als "die elf Analyse-Module"
    # zu "The eleven analysis modules" wurde.
    'pattern_modules': r'(?:Analyse-Module|analysis\s+modules)',
    # #276 Luecke 2: die Gesamtzahl der Module unter playground/js/ui/ stand
    # an drei Stellen in drei verschiedenen falschen Auspraegungen, ohne dass
    # es dafuer ueberhaupt einen Count gab. Der Anker greift bewusst nur das
    # blanke "Module(n)"/"modules" — qualifizierte Fuegungen wie
    # "11 analysis modules" gehoeren zu pattern_modules und matchen hier
    # nicht, weil der Anker unmittelbar hinter der Zahl stehen muss.
    'ui_modules': r'(?:UI-)?[Mm]odule[ns]?\b',
    # Englische Variante mit #356, aus demselben Grund wie bei
    # 'pattern_modules': playground/readme.md ist englisch geschrieben und
    # haette mit den deutschen Alternativen allein keine Bindung.
    'authority_explorers': r'(?:Authority-File-(?:Explorer|Einstiegspunkte)|Authority-Explorer|[Aa]uthority(?:[- ][Ff]ile)?[- ][Ee]xplorers?)',
    'entry_points': r'(?:[Ss]earch\s+)?[Ee]ntry\s+[Pp]oints',
}

# Zeilen im Modul-/Verzeichnisbaum zaehlen Unterverzeichnisse ("├── core/
# # Core utilities (3 modules)"), nie die Gesamtzahl. Ohne diesen Skip
# meldet der ui_modules-Anker jede Baumzeile als Drift.
# Nebenwirkung, bewusst in Kauf genommen: die Baumzeile "13 files: router +
# modal + 11 analysis modules" in ARCHITECTURE.md wird damit auch fuer
# pattern_modules nicht mehr geprueft. Dieselbe Angabe steht im Fliesstext
# darunter ("The eleven analysis modules"), Drift bleibt sichtbar.
TREE_LINE_RE = re.compile(r'^\s*[│├└]')

# ADRs und Retrospektiven nennen bewusst den Stand von damals. Der
# Chronikzeilen-Skip (Datum, Haekchen) greift dort nicht, weil ADR-Fliesstext
# das Datum in der Ueberschrift traegt, nicht in der Zeile. Marker auf der
# ganzen Zeile, analog zum hist_ctx-Skip in find_stale_numbers.
# Zweisprachig seit #316: die englischen Marker sind die woertlichen
# Entsprechungen der deutschen daneben, keine neue Klasse. Ohne sie meldete
# das Audit die bewusst historischen ADR-002-Zahlen ("13 modules") als Drift,
# sobald der Absatz uebersetzt war.
HISTORICAL_MARKERS = re.compile(
    r'Tag der Entscheidung|Entscheidungszeitpunkt|damals|seinerzeit|seither'
    r'|historisch|urspr(?:ü|ue)nglich|zum Zeitpunkt|Stand von|at the time'
    r'|day of the decision|since then|historical(?:ly)?|originally')


# Was zwischen Zahl und Anker stehen darf: Whitespace-Laeufe, begrenzte
# HTML-Tags (Stat-Karten haben Zahl und Label in getrennten <p>) und
# Auszeichnungszeichen (Backticks, Anfuehrungszeichen, Fettschrift) —
# "43.879 `lemmata`-Eintraege" ist dieselbe Aussage wie "43.879 Lemmata".
ANCHOR_SEP = r'(?:\s+|[`"„“»«*_]|</?[a-zA-Z][^>]{0,80}>){0,8}'

# Strong keyword anchors (must appear right after the number; in HTML
# duerfen begrenzt Tags dazwischenliegen, z. B. Stat-Karten
# "<p>256.759</p><p>orthographische Varianten</p>").
# Modulweit statt lokal in find_stale_numbers, damit die Anker-
# Selbstpruefung (#276 Luecke 4) dieselben Muster benutzt.
NEAR_KEYWORDS = {
    # F25 (#171): auch "NNN Dateien", "NNN TEI-Dateien" (Bindestrich) und
    # "NNN Files" matchen — die dominanten Schreibweisen in den Docs.
    # Bare "Dateien"/"Files" ist vertretbar, weil der Drift-Window-Check
    # (±2 %) und der Rundungs-/Arrow-Skip False Positives abfangen.
    # Mit #342 nachgetragen: "TEI-codierte Texte" (das alte Muster verlangte
    # "TEI" direkt vor "Texte") und "[Cc]orpus", das gar nicht vorkam. Beide
    # Formen stehen im Bestand unmittelbar hinter der 667, README.md Zeile 21
    # und ROADMAP.md Zeile 118; die Selbstpruefung meldete die zwei Dateien
    # deshalb als ungeprueft, obwohl sie die Zahl fuehren.
    'corpus_files': r'(?:TEI(?:-XML)?[-\s](?:files?|Dateien|Texte)|TEI-[a-zäöüß]+e\s+Texte|Korpus(?:-?[Dd]ateien)?|(?:mittelhochdeutsche\s+)?TEI-Texte|[Cc]orpus\b|Dateien|[Ff]iles)',
    # Kleinschreibung, weil ARCHITECTURE.md die Zahl als "43,879 `lemmata`
    # entries" fuehrt (Code-Bezeichner im Fliesstext); "records", weil
    # dieselbe Zahl dort als Groesse des API-Lemmata-Bundles auftaucht
    # ("43,879 records", ARCHITECTURE.md §Static JSON API).
    'lexicon_entries': r'(?:[Ll]emmata|[Rr]ecords)',
    # Zweisprachig seit #316: DATA-MODEL.md schreibt die 584 seit der
    # Uebersetzung als "584 works". TEI-MODEL.md ist noch deutsch und haelt
    # die Form "Werke", beide Zielorte brauchen ihre Variante.
    'works': r'(?:Werke|[Ww]orks)',
    # "variant entries" kam mit #316 dazu und ist bewusst zusammengesetzt: ein
    # blankes "[Ee]ntries" traefe in docs/DATA-MODEL.md die Lexikonzahl
    # ("43,879 entries"). Das Drift-Fenster verwirft die zwar (+-852 um
    # 42.627), die Anker-Abdeckungspruefung kennt es aber nicht und meldete
    # den INTENTIONALLY_SILENT-Eintrag der Datei faelschlich als veraltet.
    # "Lemma-Gruppen" mit #356: schema/README.md nennt die Eintragszahl so,
    # und der Anker muss unmittelbar hinter der Zahl stehen. Zusammengesetzt
    # und deshalb kollisionsfrei zu 'lexicon_entries'.
    'variants_entries': r'(?:Variant|Eintr[äa]ge|[Vv]ariant\s+entries|Lemma-Gruppen)',
    # Satzanfang und Karten-Labels schreiben das Adjektiv gross
    # ("Orthographische Varianten" im Stats-Block der Startseite); ohne
    # die Grossschreib-Variante lief der Anker dort ins Leere und
    # index.html blieb auf 256.761 stehen, waehrend #138 alle anderen
    # Seiten auf 256.760 zog.
    # DATA-MODEL.md und CONTRACTS.md schreiben die Formenzahl englisch
    # ("variant forms", "raw forms"); ohne diese Alternativen greift dort
    # kein Anker und der DOC_TARGETS-Eintrag bliebe wirkungslos.
    # Das blanke "[Ff]orms" kam mit #316 dazu (die Tabellen in TEI-MODEL.md
    # und TEI-MODEL-AUTH-FILES.md schreiben "256,760 forms" ohne Beiwort) und
    # macht die zwei zusammengesetzten Varianten nicht ueberfluessig: ANCHOR_SEP
    # laesst zwischen Zahl und Anker kein Wort zu, "256,760 variant forms"
    # braucht also weiterhin seine eigene Alternative.
    # "Wortformen" mit #356 (schema/README.md). Das blanke "Formen" traegt
    # es nicht: ANCHOR_SEP laesst zwischen Zahl und Anker kein Wort und auch
    # keinen Wortbestandteil zu, der Anker beginnt also am W.
    'variants_forms': r'(?:Formen|Wortformen|[Oo]rthographische\w*\s+Varianten|(?:[Vv]ariant|[Rr]aw)\s+forms|[Ff]orms)',
    # #276 Luecke 3: CONTRACTS.md fuehrt die deduplizierte Zahl als
    # "Varianten-Schluessel" (Schluessel der Runtime-Map). Ohne diese
    # Alternative blieb die Stelle jahrelang ungeprueft.
    # "variant mappings" ist die englische Entsprechung von
    # "Varianten-Schluessel": beim Umstellen von CONTRACTS.md auf Englisch
    # (#316) verlor CONTRACTS.md Zeile 90 sonst ihre einzige Bindung, weil
    # ANCHOR_SEP zwischen Zahl und Anker kein Wort zulaesst und "[Mm]appings"
    # damit erst hinter "variant" beginnt.
    'variants_normalized': r'(?:[Nn]ormalisierte\w*\s+(?:Schreibvarianten|Varianten)|[Ee]indeutige\s+Zuordnungen|[Nn]ormalized\s+entries|[Vv]arianten-Schl[üu]ssel|[Vv]ariant\s+mappings|[Mm]appings)',
    # Englische Alternativen seit #316: die Bestandstabellen in TEI-MODEL.md
    # (Paragraph 10) und TEI-MODEL-AUTH-FILES.md (Paragraph 1) schreiben
    # "211 persons", "567 categories", "615 categories", "90 categories".
    # "Kategorien"/"categories" ist fuer drei Keys derselbe Anker; getrennt
    # halten sie die Drift-Fenster (+-11 um 567, +-12 um 615, +-2 um 90).
    'persons': r'(?:Personen|[Pp]ersons)',
    # Die drei zusammengesetzten Alternativen kamen mit #356 dazu, alle aus
    # schema/README.md, alle so eng geschnitten, dass sie sich untereinander
    # nicht treffen koennen: "semantische Konzepte" (567), "Gattungskategorien"
    # (615), "Namensformen" (90). Das blanke "Kategorien" bleibt der geteilte
    # Anker der drei Keys, auseinandergehalten von den Drift-Fenstern.
    'concepts': r'(?:Konzepte|Begriffe|Kategorien|[Cc]ategories|semantische\s+Konzepte)',
    'genres': r'(?:Gattungen|Kategorien|[Cc]ategories|Gattungskategorien)',
    'names': r'(?:Namen|Kategorien|[Cc]ategories|Namensformen)',
    # Der Wert wurde schon berechnet, war aber in keinem DOC_TARGETS-Eintrag
    # eingetragen: docs/TEI-MODEL.md stand deshalb still auf 51, waehrend
    # TEI-MODEL-AUTH-FILES.md 52 fuehrte (#315 Punkt 4). Kollision mit dem
    # gleichnamigen Anker von 'persons' (211) gibt es nicht: das Drift-Fenster
    # ist +-2 um 52.
    # "MHDBDB-Mitwirkende" mit #356 (schema/README.md). Praefix und Bindestrich
    # machen die Alternative kollisionsfrei zu 'persons'.
    'contributors_persons': r'(?:Personen|[Pp]ersons|MHDBDB-Mitwirkende)',
}


def find_stale_wordcounts(doc_path: str, current: int, key: str) -> list:
    """Zahlwort- und Kleinziffern-Drift fuer code-abgeleitete Counts.

    Gleiche Anker-Idee wie find_stale_numbers (Keyword direkt hinter der
    Zahl, begrenzt Markup dazwischen), aber: Zahlwoerter statt grosser
    Ziffern, KEIN Drift-Fenster (jede Abweichung vom Ist-Wert zaehlt),
    und ein Skip fuer datierte Chronik-Zeilen (Milestones/Changelogs mit
    "(20YY-" oder Haekchen-Marker), deren Zahlen bewusst historisch sind.
    Ordinale ("Zehntes Werkzeug") matchen dank \\b-Grenzen nicht."""
    if not Path(doc_path).exists():
        return []
    keywords = CODE_ANCHORS.get(key)
    if not keywords:
        return []
    anchor = re.compile(ANCHOR_SEP + keywords)
    words = '|'.join(sorted(NUMBER_WORDS, key=len, reverse=True))
    num_re = re.compile(rf'\b((?i:{words})|\d{{1,2}})\b')
    content = Path(doc_path).read_text(encoding='utf-8')

    findings = []
    for m in num_re.finditer(content):
        raw = m.group(1)
        num = NUMBER_WORDS.get(raw.lower(), None)
        if num is None:
            try:
                num = int(raw)
            except ValueError:
                continue
        if num == current:
            continue
        if not anchor.match(content[m.end():m.end() + 300]):
            continue
        # Datierte Chronik-Zeilen (INDEX-Milestones, ROADMAP-Log) sind
        # bewusst historisch: "damit 8 TEI-Analyse-Werkzeuge (2026-05-15)".
        line_start = content.rfind('\n', 0, m.start()) + 1
        line_end = content.find('\n', m.end())
        line = content[line_start:line_end if line_end != -1 else len(content)]
        if re.search(r'\(20\d\d-|✅|✓', line):
            continue
        # Modulbaum-Zeilen zaehlen Unterverzeichnisse, nicht Gesamtzahlen
        # ("├── authority/  # Authority file exploration (7 modules)").
        if TREE_LINE_RE.match(line):
            continue
        # ADR-Fliesstext mit explizitem Damals-Marker (#276).
        if HISTORICAL_MARKERS.search(line):
            continue
        line_no = content[:m.start()].count('\n') + 1
        ctx = content[max(0, m.start() - 25):m.end() + 40].replace('\n', ' ').strip()
        findings.append((line_no, raw, ctx[:80]))
    return findings


def find_stale_numbers(doc_path: str, current: int, key: str) -> list:
    """Look for stale counts in the doc.

    Strategy: tight drift window (±2 absolute, or ±2% relative for large
    numbers) plus a strong keyword anchor immediately after the number.
    This catches the common case "WZB ingest bumped 666 -> 667 but doc
    still says 666" without flagging arbitrary numbers near generic
    words like "TEI" or "files".

    Counts below the key's threshold (scan_min_for: NUMERIC_SCAN_MIN, oder
    ein Eintrag in SCAN_MIN_OVERRIDE) are not scanned: too many false
    positives from table indices, percentages, section numbers, version
    strings."""
    if not Path(doc_path).exists() or current < scan_min_for(key):
        return []

    keywords = NEAR_KEYWORDS.get(key)
    if not keywords:
        return []
    # Begrenzt HTML-Tags plus Whitespace-Läufe zwischen Zahl und Anker
    # erlauben (Stat-Karten: Zahl und Label in getrennten, eingerückten <p>).
    anchor = re.compile(ANCHOR_SEP + keywords)

    # Drift window: 2 absolute or 2% relative (whichever is larger). Die
    # fruehere 50er-Kappung machte das Audit blind fuer jeden Backfill/Ingest
    # >50 Eintraege (der +125-Lemma-Backfill #115 passierte unbemerkt, Review
    # PR #156). Gegen Fehlalarme wie "100 Lemmata" schuetzt nicht die Kappung,
    # sondern der strikte Keyword-Anchor plus die relative Distanz.
    # Die Varianten-Zahlen haben hochpraezise Anker („orthographische
    # Varianten", „normalisierte Schreibvarianten") — dort darf das Fenster
    # weit sein, sonst bleibt Drift wie 175.910 → 256.759 (#192, -31 %)
    # unsichtbar. Fuer generische Anker bleibt das enge 2 %-Fenster.
    rel = 0.5 if key in ('variants_forms', 'variants_normalized') else 0.02
    window_size = max(2, int(current * rel))
    content = Path(doc_path).read_text(encoding='utf-8')

    findings = []
    # Mindeststellenzahl haengt an der Schwelle (#297): das Muster fand bisher
    # nur Zahlen ab drei Stellen, ein abgesenktes SCAN_MIN_OVERRIDE allein
    # blieb deshalb wirkungslos. Zweistellig wird nur gesucht, wo die Schwelle
    # das ausdruecklich erlaubt; Schutz gegen Fehlalarme ist dort das enge
    # Drift-Fenster (bei 90 sind es +-2) plus der direkt folgende Anker.
    min_digits = 2 if scan_min_for(key) < 100 else 3
    for m in re.finditer(rf'\b(\d{{1,3}}(?:[.,]\d{{3}})+|\d{{{min_digits},7}})\b', content):
        raw = m.group(1)
        try:
            num = int(raw.replace('.', '').replace(',', ''))
        except ValueError:
            continue
        if num == current or abs(num - current) > window_size:
            continue
        # Bewusst gerundete Angaben („~257.000 Formen", „rund 257.000") sind
        # kein Drift — ueberspringen. Ebenso historische Von-nach-Angaben
        # („675→666 corpus files" aus der #32-Migrationshistorie), erkennbar
        # am Pfeil unmittelbar vor der Zahl (F25, #171).
        prefix = content[max(0, m.start() - 8):m.start()]
        if re.search(r'(?:~|rund\s|ca\.\s|etwa\s|über\s|(?:→|->)\s*)$', prefix):
            continue
        # Historische Kontexte (Audit-Snapshots, Migrationsstaende wie
        # "Korpus zum Audit-Zeitpunkt ... 666 Dateien" oder "initial 666
        # Files am 2026-04-15") sind bewusst alt und kein Drift: Marker im
        # Nahkontext vor der Zahl (gleiche Zeile, max. 120 Zeichen) skippen.
        line_start = content.rfind('\n', 0, m.start()) + 1
        hist_ctx = content[max(line_start, m.start() - 120):m.start()]
        # Zweisprachig seit #316, woertliche Entsprechungen der deutschen
        # Marker daneben: TEI-MODEL.md fuehrt die 666 des #32-Audits jetzt als
        # "Corpus at the time of the audit ... in 666 files". Ohne die
        # englischen Marker meldete das Audit sie als Drift gegen 667, weil
        # 666 im Fenster (+-13) liegt und "files" der Anker ist.
        if re.search(r'(?:Audit-Zeitpunkt|zum Audit|Audit:|vor WZB|initial|historisch'
                     r'|time of the audit|before WZB)', hist_ctx):
            continue
        # Derselbe Fall, aber mit dem Vermerk HINTER der Zahl (#297): in
        # docs/CONTRACTS.md steht "234,244 is the state of v1.6.2, not
        # today's" -- der Satz erklaert die Zahl also genau so, wie das Audit
        # es verlangt, und wurde trotzdem gemeldet, weil der Marker
        # nachgestellt ist. Bewusst eng: nur der explizite
        # Stand-von-Version-Vermerk und die woertliche Abgrenzung, nicht
        # irgendein Vorkommen von "Stand"/"state".
        # Zweisprachig seit #316: die deutsche Fassung des Satzes bleibt
        # stehen, weil andere Docs noch nicht uebersetzt sind.
        line_end = content.find('\n', m.end())
        line_end = len(content) if line_end == -1 else line_end
        # Auf 120 Zeichen gekappt wie hist_ctx: ohne die Kappung schirmt ein
        # nachgestellter Vermerk auf einer langen Zeile jede Zahl links von
        # sich ab, auch die, auf die er sich nicht bezieht.
        fwd_ctx = content[m.end():min(line_end, m.end() + 120)]
        if re.search(r"(?:sind|ist)\s+der\s+Stand\s+von\s+v\d|nicht\s+der\s+heutige"
                     r"|(?:is|are)\s+the\s+state\s+of\s+v\d|not\s+today'?s",
                     fwd_ctx):
            continue
        # Keyword must appear right after the number (bounded markup allowed).
        suffix = content[m.end():m.end() + 300]
        if anchor.match(suffix):
            line_no = content[:m.start()].count('\n') + 1
            # Show a bit of context centered on the match
            ctx_start = max(0, m.start() - 25)
            ctx = content[ctx_start:m.end() + 30].replace('\n', ' ').strip()
            findings.append((line_no, raw, ctx[:80]))
    return findings


def number_pattern_for(key: str, numeric: bool) -> re.Pattern:
    """Das Zahlmuster, mit dem der jeweilige Scan im Dokument sucht.

    Wortgleich zu den beiden Scans, damit die Selbstpruefung unten nicht
    grosszuegiger wird als das, was sie zusichert: find_stale_numbers sucht
    grosse Ziffern mit Tausendertrennung, find_stale_wordcounts Zahlwoerter
    und zweistellige Ziffern.
    """
    if numeric:
        min_digits = 2 if scan_min_for(key) < 100 else 3
        return re.compile(rf'\b(\d{{1,3}}(?:[.,]\d{{3}})+|\d{{{min_digits},7}})\b')
    words = '|'.join(sorted(NUMBER_WORDS, key=len, reverse=True))
    return re.compile(rf'\b((?i:{words})|\d{{1,2}})\b')


def anchor_binds_number(content: str, pattern: str, num_re: re.Pattern) -> bool:
    """Steht im Dokument irgendwo eine Zahl unmittelbar vor dem Anker?

    Die Selbstpruefung fragte bis #342 nur, ob das Anker-Wort ueberhaupt
    vorkommt. Beide Scans verlangen aber mehr: die Zahl muss direkt davor
    stehen, ANCHOR_SEP laesst dazwischen nur Whitespace und etwas Markup zu.
    Kommt das Wort nur in Prosa vor ("and the TEI analysis tools, from ..."),
    laeuft der Scan ins Leere, waehrend die Selbstpruefung Abdeckung meldet.
    Gemessen betraf das acht Paare: zwei liessen sich beheben, weil der Anker
    die im Bestand verwendete Formulierung nicht kannte, sechs stehen seither
    begruendet in INTENTIONALLY_SILENT (#342).

    Die Skip-Regeln der Scans (z. B. datierte Chronik-Zeilen, Modulbaum-Zeilen,
    Rundungs- und Pfeil-Praefixe, das Drift-Fenster selbst) sind hier bewusst
    NICHT nachgebildet. Sie nehmen einzelne
    Fundstellen aus, nicht die Pruefbarkeit der Stelle an sich: eine
    Datei, in der die Zahl nur in einer Chronik-Zeile steht, wuerde sonst als
    ungeprueft gelten, obwohl der Scan dort anschlaegt, sobald jemand die
    Zahl ausserhalb der Chronik nennt.
    """
    anchor = re.compile(ANCHOR_SEP + pattern)
    return any(anchor.match(content[m.end():m.end() + 300])
               for m in num_re.finditer(content))


def check_anchor_coverage(counts: dict, code_counts: dict) -> list:
    """Selbstpruefung: welches konfigurierte (Datei, Key)-Paar prueft nichts?

    Hintergrund (#276 Luecke 4): docs/ARCHITECTURE.md stand mit drei Keys in
    CODE_DOC_TARGETS, und keiner der drei Anker hatte einen einzigen Treffer
    in der Datei. Das Target war sauber konfiguriert, das Audit meldete gruen,
    und geprueft wurde nichts. Das ist kein Fehler — eine Datei darf ueber
    einen Count schweigen — aber es darf nicht unsichtbar bleiben, sonst
    zaehlt man Targets und haelt sie fuer Abdeckung.

    Nachtrag #342: die Pruefung hatte selbst denselben blinden Fleck. Sie
    fragte nur, ob das Anker-Wort im Dokument vorkommt, waehrend beide Scans
    eine Zahl unmittelbar davor verlangen. Ein Anker in reiner Prosa erfuellte
    also die Selbstpruefung, ohne dass der Scan je haette anschlagen koennen.
    Betroffen waren acht Paare. Zwei davon liessen sich beheben, indem der
    corpus_files-Anker die real verwendeten Formulierungen lernte; die
    restlichen sechs stehen jetzt begruendet in INTENTIONALLY_SILENT.

    Gemeldet werden sechs Zustaende:
      missing-file  Pfad existiert nicht (Umbenennung, Tippfehler)
      no-anchor     kein Anker-Muster fuer den Key hinterlegt
      below-min     Ist-Wert unter der Schwelle des Keys (scan_min_for),
                    der Ziffern-Scan laeuft dort nie
      no-hit        der Scan kann hier nichts finden, aus einem von zwei
                    Gruenden: das Anker-Wort fehlt ganz, oder es steht nur
                    in Prosa, nie hinter einer Zahl. Beides steht als
                    Diagnose in der Meldung (#342)
      silent        wie no-hit, aber als bewusste Entscheidung hinterlegt
                    (INTENTIONALLY_SILENT) und damit kein offener Punkt
      silent-obsolet  als silent hinterlegt, aber der Anker trifft doch:
                    der Eintrag gehoert entfernt
    """
    gaps = []
    scans = [(DOC_TARGETS, NEAR_KEYWORDS, counts, True),
             (CODE_DOC_TARGETS, CODE_ANCHORS, code_counts, False)]
    for targets, anchors, values, numeric in scans:
        for doc_path, keys in targets:
            path = Path(doc_path)
            if not path.exists():
                for key in keys:
                    gaps.append((doc_path, key, 'missing-file', ''))
                continue
            content = path.read_text(encoding='utf-8')
            for key in keys:
                pattern = anchors.get(key)
                if not pattern:
                    gaps.append((doc_path, key, 'no-anchor',
                                 'kein Anker-Muster hinterlegt'))
                    continue
                if numeric and values[key] < scan_min_for(key):
                    gaps.append((doc_path, key, 'below-min',
                                 f'Ist-Wert {values[key]} < {scan_min_for(key)}'))
                    continue
                num_re = number_pattern_for(key, numeric)
                if not anchor_binds_number(content, pattern, num_re):
                    reason = INTENTIONALLY_SILENT.get((doc_path, key))
                    # Zwei Wege in denselben Zustand, mit verschiedener
                    # Behebung: fehlt das Wort ganz, gehoert der Count in die
                    # Datei oder das Target weg. Steht es nur in Prosa, reicht
                    # es, die Zahl an derselben Stelle zu nennen.
                    diagnose = ('Anker kommt im Dokument nicht vor'
                                if not re.search(pattern, content) else
                                'Anker kommt nur in Prosa vor, nie hinter einer Zahl')
                    gaps.append((doc_path, key,
                                 'silent' if reason else 'no-hit',
                                 reason or diagnose))
                elif (doc_path, key) in INTENTIONALLY_SILENT:
                    # Seit #342 heisst "trifft" hier: der Anker steht hinter
                    # einer Zahl. Ein Eintrag wird also erst dann obsolet
                    # gemeldet, wenn die Datei wirklich wieder zaehlt, und
                    # nicht schon, wenn das Wort in einem Fliesstext auftaucht.
                    # Der Anker trifft, der Eintrag behauptet das Gegenteil:
                    # tote Config mit inzwischen falscher Begruendung. Ohne
                    # diese Meldung altert INTENTIONALLY_SILENT genauso still
                    # wie die Luecken, gegen die es gebaut wurde.
                    gaps.append((doc_path, key, 'silent-obsolet',
                                 'Anker trifft inzwischen, Eintrag aus '
                                 'INTENTIONALLY_SILENT entfernen'))
    return gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='exit code 1 if any stale numbers found in docs')
    args = ap.parse_args()

    counts = collect_counts()
    code_counts = collect_code_counts()

    print('=== Current corpus + authority counts ===')
    print()
    print('| Position | Aktueller Wert |')
    print('|----------|----------------|')
    for label, key in LABELS:
        print(f'| {label} | {counts[key]:,} |')
    for label, key in CODE_LABELS:
        print(f'| {label} | {code_counts[key]} |')
    print()

    print('=== Doc drift scan ===')
    print()
    total_drift = 0
    for doc_path, keys in DOC_TARGETS:
        if not keys:
            continue
        for key in keys:
            findings = find_stale_numbers(doc_path, counts[key], key)
            if findings:
                print(f'  {doc_path} — expected {counts[key]:,} for {key}:')
                for line_no, raw, ctx in findings[:5]:
                    print(f'    L{line_no}: "{raw}" near "{ctx}"')
                if len(findings) > 5:
                    print(f'    ... +{len(findings) - 5} more')
                total_drift += len(findings)

    for doc_path, keys in CODE_DOC_TARGETS:
        for key in keys:
            findings = find_stale_wordcounts(doc_path, code_counts[key], key)
            if findings:
                print(f'  {doc_path} — expected {code_counts[key]} for {key}:')
                for line_no, raw, ctx in findings[:5]:
                    print(f'    L{line_no}: "{raw}" near "{ctx}"')
                if len(findings) > 5:
                    print(f'    ... +{len(findings) - 5} more')
                total_drift += len(findings)

    if total_drift == 0:
        print('  No drift detected against scanned docs + user-facing HTML pages')
        print('  (data counts + code-derived playground counts).')
        print('  NB: Zahlwort-Scan deckt Werkzeug-/Explorer-/Entry-Point-Claims ab;')
        print('      datierte Chronik-Zeilen (Milestones/Changelogs) sind ausgenommen.')
    else:
        print()
        print(f'  Total potential drift hits: {total_drift}')
        print('  Note: heuristic scan; review manually before editing.')

    print()
    print('=== Anker-Abdeckung (Selbstpruefung) ===')
    print()
    gaps = check_anchor_coverage(counts, code_counts)
    # Bewusst stille Paare (#297) getrennt ausweisen: sie in dieselbe Zahl zu
    # werfen wie echte Luecken macht die Meldung zu Rauschen, das jeder Lauf
    # wiederholt und niemand mehr liest.
    silent = [g for g in gaps if g[2] == 'silent']
    # silent-obsolet gehoert in keinen der beiden Toepfe: dort TRIFFT der
    # Anker, das Paar prueft also potenziell etwas, nur ist die hinterlegte
    # Begruendung veraltet. Es unter "prueft derzeit nichts" zu zaehlen waere
    # dieselbe Ungenauigkeit, gegen die die Selbstpruefung gebaut ist.
    obsolet = [g for g in gaps if g[2] == 'silent-obsolet']
    open_gaps = [g for g in gaps if g[2] not in ('silent', 'silent-obsolet')]
    if not open_gaps:
        print('  Kein konfiguriertes (Datei, Key)-Paar ohne Anker-Treffer.')
    else:
        for doc_path, key, kind, detail in open_gaps:
            suffix = f' — {detail}' if detail else ''
            print(f'  [{kind}] {doc_path} / {key}{suffix}')
        print()
        print(f'  {len(open_gaps)} konfigurierte Paare pruefen derzeit nichts.')
        print('  Kein Fehler und kein Exit-Code: eine Datei darf ueber einen Count')
        print('  schweigen. Aber ein Target ohne Anker-Treffer ist derselbe blinde')
        print('  Fleck wie ein fehlendes Target, nur schwerer zu sehen (#276).')
    if obsolet:
        print()
        print('  Veraltete Ausnahme, bitte entfernen:')
        for doc_path, key, _kind, detail in obsolet:
            print(f'    {doc_path} / {key}: {detail}')
    if silent:
        print()
        print('  Bewusst ohne Zahl (INTENTIONALLY_SILENT, #297 Punkt 4):')
        for doc_path, key, _kind, detail in silent:
            print(f'    {doc_path} / {key} — {detail}')
        print('  Das Target bleibt konfiguriert, damit eine spaeter doch')
        print('  eingesetzte Zahl sofort gegatet ist.')

    if args.check and total_drift > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
