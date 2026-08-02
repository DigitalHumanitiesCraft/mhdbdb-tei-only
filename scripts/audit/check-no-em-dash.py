#!/usr/bin/env python3
"""
Em-Dash-Gate: user-sichtbare Texte dürfen keine Em-Dashes (—) tragen.

Hausregel des Projekts: in Prosa, die Nutzende sehen, steht statt eines
Em-Dashes ein Doppelpunkt, ein Komma, eine Klammer oder ein eigener Satz.
Ein En-Dash (–) mit Leerzeichen ist erlaubt, ebenso Em-Dashes in
Code-Kommentaren.

Anlass ist wiederkehrend: KZW hat am 28.07. zum wiederholten Mal einen
Em-Dash im Frontend gemeldet (#140, diesmal im Hapax-Werkzeug).

## Die Regel, und warum sie so schlicht ist

Geflaggt wird ein Em-Dash in einer Zeile, die **nicht wie eine
Kommentarzeile aussieht** und in der **vor dem Em-Dash kein `//` steht**.

Zwei Anläufe davor sind gescheitert, beide an derselben Sorte Ehrgeiz:

1. „Em-Dash zwischen zwei Anführungszeichen in derselben Zeile" ist
   wertlos, weil fast die gesamte UI-Prosa dieses Projekts in
   MEHRZEILIGEN Template-Literalen lebt, deren Textzeilen weder Backtick
   noch Quote enthalten. Vier live sichtbare Em-Dashes sind so entgangen.
2. Ein Zustandsautomat über String-, Template- und Kommentarzustände
   verliert die Spur an Regex-Literalen (`/[",\\n\\r]/` in `app.js` öffnet
   über das `"` einen String). Mit Regex-Erkennung nachgerüstet wurde es
   nicht besser, nur schwerer zu prüfen: 27 Fundstellen, die Mehrzahl
   Kommentarzeilen.

Ein dritter Weg wurde erwogen und verworfen: **Totalverbot** von U+2014 in
den Auslieferungsverzeichnissen, Kommentare eingeschlossen. Das Skript
schrumpfte auf gut 15 Zeilen ohne Zustand und ohne Kommentar-Erkennung, und
die gesamte Fehlerklasse dieses Gates wäre weg statt geflickt: alle
gefundenen Fail-opens saßen ausnahmslos in der Kommentar-Ausnahme. Dagegen
spricht, dass die Hausregel Em-Dashes in Code-Kommentaren ausdrücklich
erlaubt; eine repo-lokale Verschärfung nur für dieses Verzeichnis wäre eine
Regeländerung und keine Entscheidung, die ein Audit-Skript treffen darf.
Wenn die Kommentar-Ausnahme je fällt, ist das hier die einfachere Lösung.

Der Selbsttest ist gegen Mutationen abgesichert: mehrere Änderungen am
Scanner (Reihenfolgebedingung `k < pos` entfernen, sichtbaren Text vor einem
öffnenden Kommentar verwerfen, Kodierungsfehler still überspringen) haben
eine frühere Fassung der Fälle vollständig bestanden und waren trotzdem
Fail-opens. Wer hier Fälle ergänzt, prüfe sie so: Mutation einbauen, Fälle
laufen lassen. Ein Fall, der jede Mutation überlebt, prüft nichts.

Die schlichte Regel trifft alle real vorhandenen Fälle und ist in fünf
Zeilen nachvollziehbar. Sie hat zwei bekannte blinde Flecken, beide zum
Fail-open hin, beide im Bestand aktuell unbelegt:

1. Eine Prosazeile innerhalb eines Template-Literals, die mit `*` oder
   `//` beginnt, gilt als Kommentar. Wenn das je vorkommt, ist die Zeile
   ohnehin verdächtig formatiert.
2. Die `//`-Ausnahme fragt nicht, ob sie in JS-Code steht. In den
   Dokuseiten (`api/index.html`, `hilfe-daten-beitragen.html`,
   `hilfe-schema.html`) stehen Code-Beispiele als sichtbarer Seitentext
   in `<pre>`/`<code>`; ein Em-Dash hinter dem `//` eines solchen
   Beispiels wäre lesbar und liefe durch. Das sauber zu trennen hieße,
   `<script>`- und `<pre>`-Bereiche über Zeilengrenzen mitzuführen, also
   genau die Zustandsverfolgung, an der Anlauf 2 gescheitert ist und die
   in diesem Skript bisher jedes Mal einen neuen Fail-open erzeugt hat.
   Bewusst nicht gebaut. Der Bestand ist ausgezählt: 15 HTML-Zeilen
   tragen ein `//`, 14 davon in echten `<script>`-Blöcken (404.html,
   hilfe-schema.html, index.html), genau eine als sichtbarer
   Seitentext (`api/index.html`, das `console.log`-Beispiel), und die
   trägt keinen Em-Dash. Wer hier einen Em-Dash einbaut, muss ihn
   selbst sehen; das Gate sagt nichts dazu.

In HTML wird jeder Em-Dash außerhalb eines `<!-- -->`-Kommentars geflaggt;
dort ist er entweder sichtbarer Text oder ein Attributwert.

CSS bekommt einen eigenen Zweig (`scanne_css`), weil die Präfixregel sonst
am Universalselektor scheitert: `*, ::before { … }` sähe aus wie eine
Kommentarfortsetzung. Ein Zustandsautomat ist dort im Gegensatz zu JS
unbedenklich, weil CSS nur `/* */` kennt und weder Template- noch
Regex-Literale hat.

Geprüft werden die ausgelieferten HTML-Seiten, die JS-Verzeichnisse
`assets/js/`, `playground/` und `lemma/` sowie `assets/css/`, weil
`content:`-Deklarationen als sichtbarer Text rendern. Ausgenommen davon
ist `tailwind-output.css`: generiert, minifiziert, und über
`tailwind-input.css` plus die HTML-Klassen ohnehin mitgeprüft. Nicht
geprüft: `docs/`, `publications/`, `tei/`, `authority-files/`, `schema/`,
`testing/` und Fremdcode unter `vendor/`.

Wenn ein Em-Dash einmal als DATEN gebraucht wird und nicht als Typografie
(Normalisierungstabelle, Interpunktions-Regex, Platzhalter-Glyphe), dann ist
der vorgesehene Weg `String.fromCharCode(0x2014)` beziehungsweise in Python
`chr(0x2014)`, nicht ein weiterer Eintrag in `SKIP_DATEIEN`. Eine ganze
Datei blindzuschalten, um ein Zeichen zu erlauben, ist der teuerste
denkbare Tausch. Ein nachgestelltes `// erlaubt` hilft nicht: die Ausnahme
verlangt das `//` VOR dem Fund.

Usage:
    python scripts/audit/check-no-em-dash.py            # Report + Exit-Code
    python scripts/audit/check-no-em-dash.py --quiet    # nur Exit-Code

Exit 0 = sauber, Exit 1 = Em-Dash in user-sichtbarem Text gefunden.
"""

import argparse
import io
import sys
from pathlib import Path

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252, und
# Audit-Skripte geben Korpusinhalte aus. Hier ist der Fall konkret: das Gate
# druckt unten die rohe Fundzeile, und hilfe-korpussuche.html sowie
# hilfe-playground.html führen die MHG-Breven ŏ und ŭ, die cp1252 nicht kann.
# Käme in eine solche Zeile je ein Em-Dash, stürbe das Gate lokal an seiner
# eigenen Fundmeldung, also ausgerechnet im roten Fall, in dem man die Ausgabe
# braucht. Der Wrapper deckt nur stdout; dieses Skript meldet auch nur dorthin.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parent.parent.parent

EM_DASH = '—'

# Auch die Umschreibungen fangen. Im Bestand gibt es davon aktuell null
# Vorkommen; die Erweiterung kostet also nichts und schliesst die Tuer,
# bevor jemand die Gotcha in CLAUDE.md als Zeichen- statt Typografie-Regel
# liest und zur Entity greift.
# Die beiden CSS-Escapes stehen mit dabei, seit assets/css/ im Umfang ist:
# `content: "\2014"` rendert denselben Strich wie das Literalzeichen.
EM_FORMEN = (EM_DASH, '&mdash;', '&#8212;', '&#x2014;', chr(92) + 'u2014',
             chr(92) + '2014', chr(92) + '002014')

# Sicherheitsnetz fuer kuenftige Globs, aktuell ohne Wirkung: die Liste in
# GLOBS beginnt durchgaengig mit einem konkreten Segment, der erste Pfadteil
# eines Fundes ist also nie `tei`, `data` oder `docs`. Wer hier spaeter ein
# `**/*.js` einfuehrt, braucht den Filter, und dann gilt: nur auf der
# OBERSTEN Ebene ausschliessen. Ein Test ueber alle Pfadteile uebersaehe
# ausgerechnet playground/js/ui/tei/, weil dort ein Verzeichnis ebenfalls
# `tei` heisst. Das war der erste Fehler dieses Gates.
TOP_LEVEL_SKIP = {'tei', 'data', 'docs', 'publications', 'schema', 'testing',
                  'proposals', 'node_modules', '.git', 'test-results'}
SKIP_ANYWHERE = {'node_modules', 'vendor', '_archived', 'test-results', '.git'}

# Generierte Artefakte gehoeren nicht in ein Gate, das auf handgeschriebene
# Prosa zielt: die Quelle (tailwind-input.css und die HTML-Klassen) wird
# gescannt, das Kompilat braucht es nicht, und ein Fund dort waere ohnehin
# nicht dort zu beheben.
#
# Die Datei war vorher zusaetzlich unsichtbar, weil sie minifiziert ist und
# als eine einzige Zeile mit fuehrendem `*` an der JS-Praefixregel durchfiel.
# Diese Ursache ist mit `scanne_css` weg; der Ausschluss bleibt trotzdem, aber
# jetzt aus dem einen Grund, der ihn traegt, statt als Symptomkur.
SKIP_DATEIEN = {'assets/css/tailwind-output.css'}

# `*.html` ist bewusst nicht rekursiv: die ausgelieferten Seiten liegen im
# Wurzelverzeichnis, in playground/, lemma/, api/ und includes/. Ein
# kuenftiger HTML-Unterordner braucht hier einen eigenen Eintrag.
GLOBS = (
    '*.html',
    'playground/**/*.html',
    'lemma/**/*.html',
    'api/*.html',
    'includes/*.html',
    'assets/js/**/*.js',
    'playground/**/*.js',
    'lemma/**/*.js',
    'assets/css/**/*.css',
)

KOMMENTAR_PRAEFIXE = ('//', '*', '/*', '<!--')


def relevante_dateien(wurzel=None):
    wurzel = wurzel or REPO
    for muster in GLOBS:
        for pfad in wurzel.glob(muster):
            teile = pfad.relative_to(wurzel).parts
            if teile[0] in TOP_LEVEL_SKIP:
                continue
            if any(t in SKIP_ANYWHERE for t in teile):
                continue
            if pfad.relative_to(wurzel).as_posix() in SKIP_DATEIEN:
                continue
            yield pfad


def scanne_verzeichnis(wurzel=None):
    """Alle relevanten Dateien unter `wurzel` pruefen.

    Bewusst als eigene Funktion mit Wurzel-Parameter: die Fehler dieses
    Gates sassen zweimal von dreimal NICHT im Scanner, sondern in der
    Schicht davor, also in der Frage, welche Dateien und welche Bytes der
    Scanner ueberhaupt zu sehen bekommt. Nur so laesst sich diese Schicht
    im Selbsttest ueber ein temporaeres Verzeichnis mitpruefen.
    """
    wurzel = wurzel or REPO
    fundstellen = []
    for pfad in sorted(set(relevante_dateien(wurzel))):
        rel = pfad.relative_to(wurzel).as_posix()
        try:
            text = pfad.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # NICHT ueberspringen. Ein stiller `continue` war ein Fail-open
            # genau in der Schicht, die schon zwei Fehler dieses Gates trug:
            # eine Datei mit einem einzigen Fremd-Byte fiele samt aller
            # korrekt kodierten Em-Dashes aus dem Scan. Der realistische Fall
            # ist ausgerechnet der hier gesuchte: Copy-Paste aus Word liefert
            # CP-1252, und dort IST 0x97 der Em-Dash. UTF-8 ist ohnehin harte
            # Projektvorgabe, also wird das gemeldet statt geschluckt.
            fundstellen.append((rel, 1, 'Datei ist nicht UTF-8 und konnte '
                                        'nicht geprueft werden'))
            continue
        except OSError:
            continue
        # Vorfilter ueber ALLE Schreibweisen. Ein Filter nur auf das
        # Literalzeichen verwirft genau den Fall, fuer den die Entity-
        # Erkennung gebaut ist: eine Datei mit `&mdash;` und ohne Strich.
        if not any(f in text for f in EM_FORMEN):
            continue
        scan = scanner_fuer(pfad.suffix)
        for nr, zeile in scan(text):
            fundstellen.append((rel, nr, zeile))
    return fundstellen


def kommentar_beginn(zeile):
    """Index des ersten `//`, das kein Teil von `://` ist, sonst -1.

    Bewusste Annahme: protokollrelative Links (`href="//example.org"`) vor
    einem Em-Dash derselben Zeile wuerden die Zeile faelschlich als
    Kommentar werten. Im Bestand kommt das nicht vor.
    """
    such = 0
    while True:
        idx = zeile.find('//', such)
        if idx == -1:
            return -1
        if idx > 0 and zeile[idx - 1] == ':':
            such = idx + 2
            continue
        return idx


def _fund(text):
    """Index des ersten Em-Dash in irgendeiner Schreibweise, sonst -1."""
    treffer = [text.find(f) for f in EM_FORMEN]
    treffer = [t for t in treffer if t != -1]
    return min(treffer) if treffer else -1


def _ausschnitt(zeile, pos):
    """Fenster um die Fundstelle statt eines Praefixes.

    Ein reines `[:160]` schneidet den Em-Dash aus langen Zeilen heraus, und
    dann hilft die Konsolenausgabe beim Suchen nicht mehr.
    """
    gestrippt = zeile.strip()
    versatz = len(zeile) - len(zeile.lstrip())
    pos = max(0, pos - versatz)
    if len(gestrippt) <= 160:
        return gestrippt
    start = max(0, pos - 60)
    ende = min(len(gestrippt), start + 160)
    vorn = '…' if start > 0 else ''
    hinten = '…' if ende < len(gestrippt) else ''
    return vorn + gestrippt[start:ende] + hinten


def scanne_js(text):
    treffer = []
    for nr, zeile in enumerate(text.split('\n'), 1):
        pos = _fund(zeile)
        if pos == -1:
            continue
        if zeile.lstrip().startswith(KOMMENTAR_PRAEFIXE):
            continue
        k = kommentar_beginn(zeile)
        if k != -1 and k < pos:
            continue
        treffer.append((nr, _ausschnitt(zeile, pos)))
    return treffer


def scanne_css(text):
    """Em-Dashes ausserhalb von `/* */`, die ueber Zeilengrenzen halten.

    Eigener Zweig statt der JS-Praefixregel, weil die in CSS am haeufigsten
    gebrauchten Selektoren mit `*` beginnen (`*, ::before { … }`), und
    `scanne_js` haelt eine solche Zeile fuer eine Kommentarfortsetzung. Der
    Scan waere damit ausgerechnet gegen die uebliche Selektorform blind.

    Der Zustandsautomat ist hier vertretbar, obwohl er es in JS nicht war:
    CSS kennt genau eine Kommentarform und weder Template-Literale noch
    Regex-Literale, also keine der Mehrdeutigkeiten, an denen Anlauf 2
    gescheitert ist. Strings (`content: "…"`) muessen nicht verfolgt werden,
    denn deren Inhalt ist genau das, was gesucht wird.

    Bekannte Restluecke, im Bestand unbelegt: ein `/*` INNERHALB eines
    Strings (`content: "/*"`) oeffnet einen Kommentar, den es nicht gibt,
    und verschluckt den Rest bis zum naechsten `*/`. Das zu schliessen
    hiesse Stringzustaende mitzufuehren, also genau den Schritt, der die
    Einfachheit dieses Zweigs aufgeben wuerde.
    """
    treffer = []
    im_kommentar = False
    for nr, zeile in enumerate(text.split('\n'), 1):
        rest = zeile
        versatz = 0
        sichtbar = []
        while rest:
            if im_kommentar:
                ende = rest.find('*/')
                if ende == -1:
                    break
                rest = rest[ende + 2:]
                versatz += ende + 2
                im_kommentar = False
                continue
            start = rest.find('/*')
            if start == -1:
                sichtbar.append((rest, versatz))
                break
            sichtbar.append((rest[:start], versatz))
            rest = rest[start + 2:]
            versatz += start + 2
            im_kommentar = True
        pos = -1
        for stueck, start in sichtbar:
            p = _fund(stueck)
            if p != -1:
                pos = start + p
                break
        if pos == -1:
            continue
        treffer.append((nr, _ausschnitt(zeile, pos)))
    return treffer


def scanner_fuer(endung):
    if endung == '.html':
        return scanne_html
    if endung == '.css':
        return scanne_css
    return scanne_js


def scanne_html(text):
    """Em-Dashes ausserhalb von <!-- -->; die halten ueber Zeilengrenzen.

    Reihenfolge ist wichtig: erst den Kommentar-Zustand fortschreiben, DANN
    die JS-Kommentar-Ausnahme auf den sichtbaren Rest anwenden. Andersherum
    kann eine mit `//` oder `*` beginnende Zeile ein schliessendes `-->`
    verschlucken; `im_kommentar` bliebe dauerhaft True und der gesamte Rest
    der Datei liefe ungeprueft durch (fail open). Genau dieser Fall steckt
    im Selbsttest.

    Inline-<script>-Bloecke enthalten JS-Kommentare, fuer die dieselbe
    Ausnahme gilt wie in .js-Dateien (hilfe-schema.html traegt einen).
    """
    treffer = []
    im_kommentar = False
    for nr, zeile in enumerate(text.split('\n'), 1):
        rest = zeile
        versatz = 0          # Position von `rest` in `zeile`
        sichtbar = []        # (Text, Startindex in zeile)
        while rest:
            if im_kommentar:
                ende = rest.find('-->')
                if ende == -1:
                    break
                rest = rest[ende + 3:]
                versatz += ende + 3
                im_kommentar = False
                continue
            start = rest.find('<!--')
            if start == -1:
                sichtbar.append((rest, versatz))
                break
            sichtbar.append((rest[:start], versatz))
            rest = rest[start + 4:]
            versatz += start + 4
            im_kommentar = True
        # Position der Fundstelle in der ORIGINALZEILE mitfuehren, statt sie
        # hinterher per find() zu suchen: bei einer Zeile, die ein Kommentar
        # zerteilt, ist der zusammengesetzte sichtbare Text kein
        # zusammenhaengender Teilstring mehr.
        sichtbarer_text = ''.join(s for s, _ in sichtbar)
        # `/*` gehoert dazu: Inline-<script>- und <style>-Bloecke tragen
        # Blockkommentare, und ohne diesen Praefix meldete das Gate eine ganz
        # normale `/* ... */`-Kommentarzeile darin als Fehlalarm.
        if sichtbarer_text.lstrip().startswith(('//', '*', '/*')):
            continue
        # Nachgestellte JS-Kommentare im Inline-<script> genauso exempieren
        # wie in .js-Dateien. Entscheidend ist der Geltungsbereich: sowohl
        # der Em-Dash als auch das `//` muessen im SELBEN sichtbaren Stueck
        # gesucht werden. Ein kommentar_beginn() auf der Rohzeile liesse ein
        # `//` aus dem Kommentarinhalt den sichtbaren Rest stillschalten:
        # `<!-- x // y --> <p>Hinweis - sichtbar</p>` waere durchgerutscht.
        pos = -1
        for stueck, start in sichtbar:
            p = _fund(stueck)
            if p == -1:
                continue
            k = kommentar_beginn(stueck)
            if k != -1 and k < p:
                break      # ab hier ist der Rest der Zeile JS-Kommentar
            pos = start + p
            break
        if pos == -1:
            continue
        treffer.append((nr, _ausschnitt(zeile, pos)))
    return treffer


SELBSTTEST = [
    # (Name, Endung, Quelltext, erwartete Zeilennummern)
    #
    # Die naechsten vier Faelle nageln die REIHENFOLGE fest und sind
    # nachtraeglich entstanden: ein Mutationstest hat gezeigt, dass drei
    # Aenderungen am Scanner alle bis dahin vorhandenen Faelle bestanden und
    # trotzdem Fail-opens waren. Ohne sie darf man `k < pos` durch `k != -1`
    # ersetzen (jede Zeile mit irgendeinem `//` waere exempt) oder in
    # `scanne_html` den sichtbaren Text VOR einem oeffnenden `<!--` verwerfen.
    # Gemeinsamer Nenner: kein Fall hatte die Reihenfolge "Em-Dash zuerst,
    # Kommentar danach", obwohl genau das die haeufigste Form im Bestand ist.
    ('Em-Dash im String, Kommentar erst danach', '.js',
     "const s = 'x " + EM_DASH + " y'; // Hinweis\n", [1]),
    ('Em-Dash im Inline-Script, Kommentar danach', '.html',
     '<script>\n  const s = "x ' + EM_DASH + ' y"; // Hinweis\n</script>\n', [2]),
    ('sichtbarer Text, danach oeffnet ein HTML-Kommentar', '.html',
     '<p>x ' + EM_DASH + ' y</p> <!-- ok -->\n', [1]),
    ('CSS: content-String, danach oeffnet ein Kommentar', '.css',
     'a::after { content: "' + EM_DASH + '"; } /* ok */\n', [1]),
    # Gegenrichtung zum vorletzten Fall: derselbe Zeilenbau, aber der Em-Dash
    # steht IM mittig geoeffneten Kommentar und darf nicht gemeldet werden.
    ('Em-Dash im mittig geoeffneten HTML-Kommentar', '.html',
     '<p>sichtbar</p> <!-- Anmerkung ' + EM_DASH + ' erlaubt -->\n', []),
    # Blockkommentar in einem Inline-<script>: haeufige Form, war ein
    # Fehlalarm, solange der HTML-Zweig nur `//` und `*` als Praefix kannte.
    ('Blockkommentar im Inline-Script', '.html',
     '<script>\n/* Hinweis ' + EM_DASH + ' erlaubt */\n</script>\n', []),
    # CSS-Zweig: der erste Fall faellt unter scanne_js durch (Zeile beginnt
    # mit dem Universalselektor `*`, den die Praefixregel fuer einen Kommentar
    # haelt) und ist damit der Grund, warum es scanne_css gibt.
    ('Universalselektor, Em-Dash im content-String', '.css',
     '*, ::before { content: "x ' + EM_DASH + ' y"; }\n', [1]),
    ('CSS-Blockkommentar ueber mehrere Zeilen', '.css',
     '/* Hinweis\n   Fortsetzung ' + EM_DASH + ' erlaubt\n*/\na { color: red; }\n', []),
    ('Text nach dem Kommentarende derselben Zeile', '.css',
     '/* x */ a::after { content: "' + EM_DASH + '"; }\n', [1]),
    ('mehrzeiliges Template-Literal', '.js',
     'const html = `\n  <p>Hinweis ' + EM_DASH + ' sichtbar</p>\n`;\n', [2]),
    ('JSDoc-Fortsetzungszeile', '.js',
     '/**\n * Erlaeuterung ' + EM_DASH + ' erlaubt\n */\nconst a = 1;\n', []),
    ('Inline-Kommentar hinter Code', '.js',
     "const a = 1; // Grund " + EM_DASH + " erlaubt\n", []),
    ('URL im String, Em-Dash danach', '.js',
     "const s = 'https://x.org ' + '" + EM_DASH + " sichtbar';\n", [1]),
    ('HTML-Kommentar ueber Zeilengrenzen', '.html',
     '<!--\n  Notiz ' + EM_DASH + ' erlaubt\n-->\n<p>sauber</p>\n', []),
    ('Kommentarende auf //-Zeile, danach sichtbarer Text', '.html',
     '<!--\n// Notiz -->\n<p>Hinweis ' + EM_DASH + ' sichtbar</p>\n', [3]),
    # Alle sieben Eintraege aus EM_FORMEN einmal durchspielen. Vorher waren nur
    # drei davon getestet (Literal, &mdash;, —); die beiden numerischen
    # Entities und die beiden CSS-Escapes liessen sich aus EM_FORMEN loeschen,
    # ohne dass ein einziger Fall rot wurde. Fail-open-Richtung, deshalb je ein
    # Fall. Befund aus dem Review zu diesem PR.
    ('HTML-Entity statt Literal', '.html',
     '<p>Hinweis &mdash; sichtbar</p>\n', [1]),
    ('numerische Entity, dezimal', '.html',
     '<p>Hinweis &#8212; sichtbar</p>\n', [1]),
    ('numerische Entity, hexadezimal', '.html',
     '<p>Hinweis &#x2014; sichtbar</p>\n', [1]),
    ('JS-Escape statt Literal', '.js',
     "const s = 'Hinweis " + chr(92) + "u2014 sichtbar';\n", [1]),
    ('CSS-Escape, vierstellig', '.css',
     'a::after { content: "' + chr(92) + '2014"; }\n', [1]),
    ('CSS-Escape, sechsstellig', '.css',
     'a::after { content: "' + chr(92) + '002014"; }\n', [1]),
    ('nachgestellter Kommentar im Inline-Script', '.html',
     '<script>\n  laden();  // Grund ' + EM_DASH + ' nur intern\n</script>\n', []),
    # Geltungsbereich: ein // IM HTML-Kommentar darf den sichtbaren Rest
    # derselben Zeile nicht stillschalten (Fail-open aus Runde 4).
    ('// im HTML-Kommentar, sichtbarer Text danach', '.html',
     '<!-- x // y --> <p>Hinweis ' + EM_DASH + ' sichtbar</p>\n', [1]),
    ('mehrzeiliger Kommentar mit // schliesst, Text danach', '.html',
     '<!--\n  x // y --> <p>Hinweis ' + EM_DASH + ' sichtbar</p>\n', [2]),
]

# Zweite Ebene: welche DATEIEN sieht der Scanner ueberhaupt. Zwei von drei
# Fehlern dieses Gates sassen hier, nicht in der Zeilenlogik.
SELBSTTEST_DATEIEN = [
    # (relativer Pfad, Inhalt, wird erwartet?)
    ('nur-entity.html', '<p>Hinweis &mdash; sichtbar</p>\n', True),
    ('assets/js/a.js', "const s = 'x " + EM_DASH + " y';\n", True),
    ('playground/js/b.js', "const s = 'x " + EM_DASH + " y';\n", True),
    ('lemma/c.js', "const s = 'x " + EM_DASH + " y';\n", True),
    ('includes/_d.html', '<p>x ' + EM_DASH + ' y</p>\n', True),
    # Regressionstest zum ERSTEN Fehler dieses Gates: `any(part in SKIP_DIRS)`
    # ueber alle Pfadteile verschluckte playground/js/ui/tei/, weil dort ein
    # Verzeichnis `tei` heisst. Drei der sieben Fundstellen dieses PRs lagen
    # genau dort. Die beiden Faelle darunter (docs/, tei/) nageln das NICHT
    # fest, sie fallen schon durch die nicht-rekursiven HTML-Globs heraus.
    ('playground/js/ui/tei/h.js', "const s = 'x " + EM_DASH + " y';\n", True),
    ('assets/css/i.css', 'a::after { content: "x ' + EM_DASH + ' y"; }\n', True),
    # Die drei HTML-Globs ausserhalb des Wurzelverzeichnisses waren ungetestet:
    # `api/*.html`, `lemma/**/*.html` und `playground/**/*.html` liessen sich
    # einzeln aus GLOBS loeschen, ohne dass ein Fall rot wurde, obwohl unter
    # api/ und playground/ ausgelieferte Seiten liegen. Befund aus dem Review.
    ('api/index.html', '<p>x ' + EM_DASH + ' y</p>\n', True),
    ('playground/index.html', '<p>x ' + EM_DASH + ' y</p>\n', True),
    ('lemma/lemma_1/index.html', '<p>x ' + EM_DASH + ' y</p>\n', True),
    # Die drei Faelle darunter schliessen zwei Luecken auf einmal (zweite
    # Review-Runde, wieder per Mutation nachgewiesen):
    #
    # (a) REKURSIVITAET. `assets/js/**/*.js`, `playground/**/*.html` und
    #     `assets/css/**/*.css` liessen sich auf die nicht-rekursive Form
    #     verkuerzen, ohne dass ein Fall rot wurde: alle bisherigen Dateien
    #     liegen im Wurzel ihres Teilbaums. Real liegen 10 von 13 JS-Dateien
    #     unter assets/js/ in Unterordnern (lib/, search/, rendering/,
    #     storage/). `playground/**/*.js` war als einziges schon gedeckt,
    #     naemlich durch playground/js/ui/tei/h.js.
    #
    # (b) VORFILTER. Vor dem Scan steht ein `any(f in text for f in
    #     EM_FORMEN)`. Die Zeilen-Faelle rufen den Scanner direkt auf und
    #     umgehen ihn; auf Dateiebene trug bis hierher jeder Fall das
    #     Literalzeichen oder `&mdash;`. Der Vorfilter liess sich also auf
    #     diese zwei Formen verengen, und eine Datei mit ausschliesslich
    #     `—`, `&#8212;` oder einem CSS-Escape waere still uebersprungen
    #     worden: genau der Fail-open, den die Zeilen-Faelle eine Ebene
    #     hoeher schliessen sollten. Deshalb tragen die drei Faelle je eine
    #     NICHT-literale Schreibweise.
    ('assets/js/lib/k.js',
     "const s = 'x " + chr(92) + "u2014 y';\n", True),
    ('playground/sub/x.html', '<p>x &#8212; y</p>\n', True),
    ('assets/css/sub/m.css',
     'a::after { content: "' + chr(92) + '2014"; }\n', True),
    # Kaputte Kodierung: 0x97 ist in CP-1252 selbst ein Em-Dash. Frueher fiel
    # so eine Datei still aus dem Scan, jetzt wird sie gemeldet.
    ('assets/js/j.js', b"const s = 'a \x97 b';\n", True),
    # Der Fall prueft NUR den Ausschluss: ohne SKIP_DATEIEN wird die Datei
    # gemeldet, mit nicht. (Die urspruengliche Begruendung hier, eine Zeile mit
    # fuehrendem `*` falle ohnehin an der Praefixregel durch, gilt seit
    # scanne_css nicht mehr; CSS wird jetzt korrekt gelesen.)
    ('assets/css/tailwind-output.css',
     'a::after { content: "x ' + EM_DASH + ' y"; }\n', False),
    ('docs/e.html', '<p>x ' + EM_DASH + ' y</p>\n', False),
    ('tei/f.html', '<p>x ' + EM_DASH + ' y</p>\n', False),
    ('scripts/g.js', "const s = 'x " + EM_DASH + " y';\n", False),
]


def selbsttest():
    fehler = 0
    for name, endung, quelle, erwartet in SELBSTTEST:
        scan = scanner_fuer(endung)
        ist = [nr for nr, _ in scan(quelle)]
        ok = ist == erwartet
        print(f'  [{"PASS" if ok else "FAIL"}] {name}: erwartet {erwartet}, bekommen {ist}')
        if not ok:
            fehler += 1

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        wurzel = Path(tmp)
        for rel, inhalt, _ in SELBSTTEST_DATEIEN:
            ziel = wurzel / rel
            ziel.parent.mkdir(parents=True, exist_ok=True)
            # bytes statt str erlaubt einen Fall mit kaputter Kodierung
            if isinstance(inhalt, bytes):
                ziel.write_bytes(inhalt)
            else:
                ziel.write_text(inhalt, encoding='utf-8')
        gemeldet = {p for p, _, _ in scanne_verzeichnis(wurzel)}
        for rel, _, erwartet in SELBSTTEST_DATEIEN:
            ok = (rel in gemeldet) == erwartet
            zustand = 'gemeldet' if rel in gemeldet else 'nicht gemeldet'
            soll = 'gemeldet' if erwartet else 'nicht gemeldet'
            print(f'  [{"PASS" if ok else "FAIL"}] Datei-Umfang {rel}: {zustand}, erwartet {soll}')
            if not ok:
                fehler += 1

    gesamt = len(SELBSTTEST) + len(SELBSTTEST_DATEIEN)
    print()
    print(f'Selbsttest: {gesamt - fehler}/{gesamt} bestanden')
    return fehler


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--quiet', action='store_true', help='nur Exit-Code, keine Ausgabe')
    ap.add_argument('--selftest', action='store_true',
                    help='Scanner gegen eingebaute Faelle pruefen, Repo nicht anfassen')
    args = ap.parse_args()

    if args.selftest:
        return 1 if selbsttest() else 0

    fundstellen = scanne_verzeichnis()

    if not fundstellen:
        if not args.quiet:
            print('Em-Dash-Gate: keine Em-Dashes in user-sichtbarem Text.')
        return 0

    if not args.quiet:
        print(f'Em-Dash-Gate: {len(fundstellen)} Fundstelle(n) in user-sichtbarem Text.')
        print('Hausregel: Doppelpunkt, Komma, Klammer oder eigener Satz statt Em-Dash.')
        print()
        for pfad, nr, zeile in fundstellen:
            print(f'::error file={pfad},line={nr}::Em-Dash in user-sichtbarem Text')
            print(f'  {pfad}:{nr}')
            print(f'    {zeile}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
