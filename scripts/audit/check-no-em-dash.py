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

Die schlichte Regel trifft alle real vorhandenen Fälle und ist in fünf
Zeilen nachvollziehbar. Ihr bekannter blinder Fleck: eine Prosazeile
innerhalb eines Template-Literals, die mit `*` oder `//` beginnt, würde
für einen Kommentar gehalten. Im Bestand kommt das nicht vor, und wenn es
je vorkommt, ist die Zeile ohnehin verdächtig formatiert.

In HTML wird jeder Em-Dash außerhalb eines `<!-- -->`-Kommentars geflaggt;
dort ist er entweder sichtbarer Text oder ein Attributwert.

Geprüft werden die ausgelieferten HTML-Seiten sowie die JS-Verzeichnisse
`assets/js/`, `playground/` und `lemma/`. Nicht geprüft: `docs/`,
`publications/`, `tei/`, `authority-files/`, `schema/`, `testing/` und
Fremdcode unter `vendor/`.

Usage:
    python scripts/audit/check-no-em-dash.py            # Report + Exit-Code
    python scripts/audit/check-no-em-dash.py --quiet    # nur Exit-Code

Exit 0 = sauber, Exit 1 = Em-Dash in user-sichtbarem Text gefunden.
"""

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

EM_DASH = '—'

# Auch die Umschreibungen fangen. Im Bestand gibt es davon aktuell null
# Vorkommen; die Erweiterung kostet also nichts und schliesst die Tuer,
# bevor jemand die Gotcha in CLAUDE.md als Zeichen- statt Typografie-Regel
# liest und zur Entity greift.
EM_FORMEN = (EM_DASH, '&mdash;', '&#8212;', '&#x2014;', chr(92) + 'u2014')

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
)

KOMMENTAR_PRAEFIXE = ('//', '*', '/*', '<!--')


def relevante_dateien():
    for muster in GLOBS:
        for pfad in REPO.glob(muster):
            teile = pfad.relative_to(REPO).parts
            if teile[0] in TOP_LEVEL_SKIP:
                continue
            if any(t in SKIP_ANYWHERE for t in teile):
                continue
            yield pfad


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
        sichtbar = []
        while rest:
            if im_kommentar:
                ende = rest.find('-->')
                if ende == -1:
                    rest = ''
                    break
                rest = rest[ende + 3:]
                im_kommentar = False
                continue
            start = rest.find('<!--')
            if start == -1:
                sichtbar.append(rest)
                rest = ''
                break
            sichtbar.append(rest[:start])
            rest = rest[start + 4:]
            im_kommentar = True
        sichtbarer_text = ''.join(sichtbar)
        if sichtbarer_text.lstrip().startswith(('//', '*')):
            continue
        pos = _fund(sichtbarer_text)
        if pos == -1:
            continue
        treffer.append((nr, _ausschnitt(zeile, zeile.find(sichtbarer_text.strip()[:20]))))
    return treffer


SELBSTTEST = [
    # (Name, Endung, Quelltext, erwartete Zeilennummern)
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
    ('HTML-Entity statt Literal', '.html',
     '<p>Hinweis &mdash; sichtbar</p>\n', [1]),
    ('JS-Escape statt Literal', '.js',
     "const s = 'Hinweis " + chr(92) + "u2014 sichtbar';\n", [1]),
]


def selbsttest():
    fehler = 0
    for name, endung, quelle, erwartet in SELBSTTEST:
        scan = scanne_html if endung == '.html' else scanne_js
        ist = [nr for nr, _ in scan(quelle)]
        ok = ist == erwartet
        print(f'  [{"PASS" if ok else "FAIL"}] {name}: erwartet {erwartet}, bekommen {ist}')
        if not ok:
            fehler += 1
    print()
    print(f'Selbsttest: {len(SELBSTTEST) - fehler}/{len(SELBSTTEST)} bestanden')
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

    fundstellen = []
    for pfad in sorted(set(relevante_dateien())):
        try:
            text = pfad.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        if EM_DASH not in text:
            continue
        scan = scanne_html if pfad.suffix == '.html' else scanne_js
        rel = pfad.relative_to(REPO).as_posix()
        for nr, zeile in scan(text):
            fundstellen.append((rel, nr, zeile))

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
