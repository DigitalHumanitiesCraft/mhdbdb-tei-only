#!/usr/bin/env python3
"""
Spec-Inventar-Gate: jede Playwright-Spec steht in der Tabelle
"Test File Inventory" in docs/DEVELOPMENT.md, und die Tabelle nennt keine
Spec, die es nicht gibt.

Anlass ist #329: die Tabelle listete 20 von 30 Specs. Die zehn fehlenden
gehörten alle zu Features aus Mai bis Juli 2026, zusammen 86 der 276 Tests.
Das ist der Drift-Typ, den niemand bemerkt, weil sein Veralten nichts kaputt
macht: die Tabelle ist der einzige Ort, an dem steht, WOFÜR eine Spec da ist
(Kategorie plus ein Satz), und genau deshalb lohnt sie sich nur gepflegt.

## Warum die Prüfung nur die eine Tabelle liest

Ein `grep <name> docs/DEVELOPMENT.md` über das ganze Dokument wäre die
naheliegende Fassung und wäre falsch. `vendor.spec.js` etwa stand seit #328 in
der Blindstellen-Tabelle weiter oben und hätte den Test bestanden, ohne je im
Inventar aufzutauchen: gemessen am 01.08.2026 meldet der Ganzdokument-Vergleich
neun Fehlende, der Tabellen-Vergleich zehn. Die Zahl, die zählt, ist zehn.

Dieselbe Datei enthält außerdem eine zweite Spec-Tabelle (die Blindstellen von
`test:changed`), die absichtlich unvollständig ist: sie listet nur die
Nicht-JS-Abhängigkeiten. Sie darf nicht mitgezählt werden. Die Tabelle wird
deshalb über ihre Überschrift abgegrenzt, von `### Test File Inventory` bis zur
nächsten Überschrift derselben oder einer höheren Ebene.

## Selbsttest

Beide Richtungen werden an künstlichen Eingaben belegt, nicht zugesichert. Der
Grund steht im JOURNAL zum 31.07.: ein Gate, das jahrelang grün läuft, sagt
nichts, solange niemand den Fehler einbaut, den es fangen soll. Zwei der Fälle
unten spiegeln genau die beiden Fehlermodi, die dieses Skript rechtfertigen:
eine neue Spec, die niemand einträgt, und ein Spec-Name, der außerhalb der
Tabelle vorkommt.

Usage:
    python scripts/audit/check-test-inventory.py             # Bericht + Exit-Code
    python scripts/audit/check-test-inventory.py --selftest  # Scanner prüfen
"""
import argparse
import io
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO / 'testing' / 'tests'
DOC = REPO / 'docs' / 'DEVELOPMENT.md'
TABELLEN_TITEL = '### Test File Inventory'

# Was Playwright tatsächlich einsammelt, nicht was heute zufällig dort liegt.
# testing/playwright.config.js setzt nur testDir und kein testMatch, es gilt
# also der Default `**/*.@(spec|test).?(c|m)[jt]s?(x)`: rekursiv und auch
# *.test.js. Heute ist das Verzeichnis flach und enthält nur *.spec.js, ein
# engerer Glob wäre aber ein Fail-open: eine Spec in einem künftigen
# Unterordner liefe in der Suite mit und wäre hier grün.
#
# Geprüft wird nur die Endung, nicht der ganze Name. Eine Zeichenklasse für den
# Namensteil wäre die zweite Sorte Fail-open: eine Datei mit Umlaut oder
# Leerzeichen im Namen fiele still aus dem Scan, liefe in der Suite aber mit.
ENDUNG = re.compile(r'\.(?:spec|test)\.(?:[cm]?[jt]sx?)$')

# Erste Spalte einer Tabellenzeile: | `name.spec.js` | Kategorie | Text |
# Der Name darf alles außer Pipe und Backtick sein, Leerzeichen eingeschlossen.
# Enger wäre hier zwar fail-closed und nicht fail-open, aber genauso kaputt:
# eine Datei, die ENDUNG oben akzeptiert, muss sich auch eintragen lassen,
# sonst bliebe das Gate rot ohne einen Weg, es grün zu bekommen. Der Match ist
# nicht-gierig, damit er in Spalte 1 bleibt; umgebender Leerraum wird getrimmt.
ZEILE = re.compile(r'^\|\s*`?([^|`]+?\.(?:spec|test)\.(?:[cm]?[jt]sx?))`?\s*\|')


def tabellen_abschnitt(text: str) -> str:
    """Der Bereich unter der Inventar-Überschrift bis zur nächsten Überschrift
    gleicher oder höherer Ebene.

    Fehlt die Überschrift, ist das ein Fehler und kein leeres Ergebnis: sonst
    meldete das Gate nach einer Umbenennung der Überschrift jede einzelne Spec
    als fehlend, statt zu sagen, dass es die Tabelle nicht mehr findet.

    Code-Blöcke werden ganz verworfen, aus zwei Gründen in dieser Reihenfolge.
    Der erste: eine Zeile wie `# python scripts/…` darin zählte sonst als
    Überschrift und schnitte die Tabelle vorzeitig ab; das Muster ist in diesen
    Docstrings üblich, und der Abschnitt trägt bereits Prosa, wird also wachsen.
    Der zweite folgt aus dem ersten: sobald ein Code-Block im Abschnitt möglich
    ist, kann darin eine Beispiel-Tabellenzeile stehen, und die zählte als
    Eintrag. Eine Spec wäre dann gelistet, weil jemand sie als Beispiel
    hingeschrieben hat. Die Zeilen nur für die Überschriftenerkennung zu
    ignorieren und sie trotzdem zurückzugeben, wäre also ein Fail-open.

    Eine nicht geschlossene Fence verwirft den Rest des Dokuments. Das ist
    fail-closed: die Specs darunter fehlen dann im Ergebnis und werden gemeldet.
    """
    zeilen = text.splitlines()
    try:
        start = zeilen.index(TABELLEN_TITEL)
    except ValueError:
        raise SystemExit(
            f'FEHLER: Überschrift "{TABELLEN_TITEL}" steht nicht in {DOC.name}. '
            'Wurde sie umbenannt? Dann TABELLEN_TITEL hier mitziehen.'
        )
    behalten = []
    im_codeblock = False
    for zeile in zeilen[start + 1:]:
        if zeile.lstrip().startswith(('```', '~~~')):
            im_codeblock = not im_codeblock
            continue
        if im_codeblock:
            continue
        if zeile.startswith(('# ', '## ', '### ')):
            break
        behalten.append(zeile)
    return '\n'.join(behalten)


def specs_im_dateisystem() -> set:
    """Bezeichner ist der Pfad relativ zu testing/tests/. Solange das
    Verzeichnis flach ist, ist das der Dateiname; liegt eine Spec je in einem
    Unterordner, steht der Pfad in der Tabelle und bleibt eindeutig."""
    return {p.relative_to(SPEC_DIR).as_posix()
            for p in SPEC_DIR.rglob('*')
            if p.is_file() and ENDUNG.search(p.name)}


def specs_in_tabelle(abschnitt: str) -> set:
    return {m.group(1) for m in (ZEILE.match(z) for z in abschnitt.splitlines()) if m}


def pruefe(vorhanden: set, gelistet: set) -> tuple:
    """(fehlt in der Tabelle, in der Tabelle ohne Datei)"""
    return sorted(vorhanden - gelistet), sorted(gelistet - vorhanden)


def selbsttest() -> int:
    tabelle = (
        f'{TABELLEN_TITEL}\n'
        '\n'
        '| File | Category | What it tests |\n'
        '|------|----------|--------------|\n'
        '| `a.spec.js` | Main site | Erste |\n'
        '| `b.spec.js` | Playground | Zweite |\n'
        '\n'
        '### CI: Data Integrity\n'
        '\n'
        'Hier steht c.spec.js außerhalb der Tabelle.\n'
    )
    gelistet = specs_in_tabelle(tabellen_abschnitt(tabelle))

    mit_codeblock = (
        f'{TABELLEN_TITEL}\n'
        '\n'
        '```bash\n'
        '# python scripts/audit/check-test-inventory.py\n'
        '| `beispiel.spec.js` | X | so sieht eine Zeile aus |\n'
        '```\n'
        '\n'
        '| `a.spec.js` | Main site | Erste |\n'
        '\n'
        '### Naechster Abschnitt\n'
        '\n'
        '| `d.spec.js` | X | darf nicht mitzaehlen |\n'
    )

    faelle = [
        ('Tabelle endet an der nächsten Überschrift',
         'c.spec.js' not in gelistet),
        ('Nennung außerhalb der Tabelle zählt nicht als gelistet',
         pruefe({'a.spec.js', 'b.spec.js', 'c.spec.js'}, gelistet)[0] == ['c.spec.js']),
        ('Fehlende Spec wird gemeldet',
         pruefe({'a.spec.js', 'b.spec.js', 'neu.spec.js'}, gelistet)[0] == ['neu.spec.js']),
        ('Gelöschte Spec wird gemeldet',
         pruefe({'a.spec.js'}, gelistet)[1] == ['b.spec.js']),
        ('Deckungsgleich ist grün',
         pruefe({'a.spec.js', 'b.spec.js'}, gelistet) == ([], [])),
        ('Backticks sind optional',
         specs_in_tabelle('| x.spec.js | Main site | ohne Backticks |') == {'x.spec.js'}),
        ('Namensnennung in der Beschreibungsspalte zählt nicht',
         specs_in_tabelle('| `a.spec.js` | X | Gegenstück zu b.spec.js |') == {'a.spec.js'}),
        # Die folgenden decken ab, was Playwright per Default noch einsammelt
        # und ein Glob auf *.spec.js im Wurzelverzeichnis nicht:
        ('*.test.js zählt mit',
         bool(ENDUNG.search('x.test.js')) and specs_in_tabelle('| `x.test.js` | X | Y |') == {'x.test.js'}),
        ('TypeScript- und Modul-Varianten zählen mit',
         all(ENDUNG.search(n) for n in ('a.spec.ts', 'b.test.mjs', 'c.spec.cjs', 'd.test.tsx'))),
        # Beide Regexe müssen dieselben Namen durchlassen. Ließe der Dateiscan
        # einen Namen zu, den die Tabellenzeile nicht aufnehmen kann, bliebe
        # das Gate rot ohne einen Weg, es grün zu bekommen.
        ('Name mit Umlaut oder Leerzeichen zählt beidseitig mit',
         ENDUNG.search('wörterbuch prüfung.spec.js') is not None
         and specs_in_tabelle('| `wörterbuch prüfung.spec.js` | X | Y |')
             == {'wörterbuch prüfung.spec.js'}),
        ('Nicht-Spec zählt nicht',
         not ENDUNG.search('util.js') and not ENDUNG.search('fixture.spec.xml')),
        # Zwei Wirkungen in einer Eingabe: ohne Codeblock-Erkennung schnitte
        # die Kommentarzeile darin die Tabelle ab und a.spec.js fehlte; würden
        # die Blockzeilen nur für die Überschriftensuche ignoriert und trotzdem
        # zurückgegeben, zählte die Beispielzeile als Eintrag.
        ('Ein Codeblock beendet die Tabelle nicht und zählt selbst nicht mit',
         specs_in_tabelle(tabellen_abschnitt(mit_codeblock)) == {'a.spec.js'}),
        # Die gelockerte ZEILE nimmt auch Prosa in Spalte 1 an. Das ist die
        # Kehrseite davon, Leerzeichen zuzulassen, und fail-closed: das Phantom
        # taucht als "genannt, aber nicht vorhanden" auf und macht Exit 1.
        ('Prosa in Spalte 1 wird als verwaister Eintrag gemeldet',
         pruefe(set(), specs_in_tabelle('| Ersatz für a.spec.js | X | Y |'))[1]
         == ['Ersatz für a.spec.js']),
    ]

    for name, ok in faelle:
        print(f'  {"OK  " if ok else "FAIL"} {name}')
    gescheitert = [name for name, ok in faelle if not ok]
    if gescheitert:
        print(f'\nSelbsttest fehlgeschlagen: {len(gescheitert)} von {len(faelle)}')
        return 1
    print(f'\nSelbsttest bestanden: {len(faelle)} von {len(faelle)}')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true',
                    help='Scanner an künstlichen Eingaben prüfen, Repo nicht anfassen')
    args = ap.parse_args()

    if args.selftest:
        return selbsttest()

    vorhanden = specs_im_dateisystem()
    gelistet = specs_in_tabelle(tabellen_abschnitt(DOC.read_text(encoding='utf-8')))
    fehlen, verwaist = pruefe(vorhanden, gelistet)

    print(f'{len(vorhanden)} Specs in testing/tests/, {len(gelistet)} in der Inventar-Tabelle')

    if fehlen:
        print(f'\nFehlt in der Tabelle "{TABELLEN_TITEL[4:]}" ({len(fehlen)}):')
        for name in fehlen:
            print(f'  {name}')
    if verwaist:
        print(f'\nIn der Tabelle genannt, aber nicht in testing/tests/ ({len(verwaist)}):')
        for name in verwaist:
            print(f'  {name}')

    if fehlen or verwaist:
        print(f'\nBitte {DOC.relative_to(REPO).as_posix()} nachziehen: '
              'Kategorie plus einen Satz, wofür die Spec da ist.')
        return 1

    print('Keine Drift.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
