#!/usr/bin/env python3
"""
Inventar-Gate für docs/DEVELOPMENT.md: jede Datei eines Verzeichnisses steht in
der zugehörigen Tabelle, und die Tabelle nennt keine Datei, die es nicht gibt.

Zwei Inventare, beide in derselben Datei:

    ### Test File Inventory      <-  testing/tests/     (Playwright-Specs)
    ### Audit Scripts Reference  <-  scripts/audit/     (Diagnosen und Gates)

Anlass war #329: die Spec-Tabelle listete 20 von 30 Dateien, zusammen 86 der
276 Tests. Beim Nachziehen zeigte der Review, dass die Skript-Tabelle zwei
Abschnitte tiefer denselben Zustand hatte, 11 von 22, darunter zwei aktive
CI-Gates. Deshalb ist das Skript nicht auf Specs zugeschnitten: der Drift-Typ
ist der Tabelle egal.

Er fällt nicht auf, weil sein Veralten nichts kaputt macht. Genau das ist der
Grund, ihn zu gaten: die Tabellen sind der einzige Ort, an dem steht, WOFÜR
eine Datei da ist, und ein unvollständiges Inventar ist schlimmer als keines,
weil es Vollständigkeit behauptet.

## Warum die Prüfung nur den jeweiligen Abschnitt liest

Ein `grep <name> docs/DEVELOPMENT.md` über das ganze Dokument wäre die
naheliegende Fassung und wäre falsch. `vendor.spec.js` etwa stand seit #328 in
der Blindstellen-Tabelle weiter oben und hätte den Test bestanden, ohne je im
Inventar aufzutauchen: gemessen am 01.08.2026 meldet der Ganzdokument-Vergleich
neun Fehlende, der Abschnitts-Vergleich zehn. Die Zahl, die zählt, ist zehn.

Die Blindstellen-Tabelle ist zudem absichtlich unvollständig, sie listet nur
die Nicht-JS-Abhängigkeiten. Jeder Abschnitt wird deshalb an seiner Überschrift
abgegrenzt, von der Überschrift bis zur nächsten derselben oder einer höheren
Ebene.

## Selbsttest

Beide Richtungen werden an künstlichen Eingaben belegt, nicht zugesichert. Der
Grund steht im JOURNAL zum 31.07.: ein Gate, das jahrelang grün läuft, sagt
nichts, solange niemand den Fehler einbaut, den es fangen soll. Zwei der Fälle
unten spiegeln genau die beiden Fehlermodi, die dieses Skript rechtfertigen:
eine neue Datei, die niemand einträgt, und ein Dateiname, der außerhalb der
Tabelle vorkommt.

Usage:
    python scripts/audit/check-doc-inventories.py             # Bericht + Exit-Code
    python scripts/audit/check-doc-inventories.py --selftest  # Scanner prüfen
"""
import argparse
import io
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / 'docs' / 'DEVELOPMENT.md'


class Inventar:
    """Ein Verzeichnis und die Tabelle, die es vollständig auflisten muss.

    `endung` ist ein Regex-Fragment ohne Anker und entscheidet allein, welche
    Datei mitzählt. Geprüft wird nur die Endung, nie der ganze Name: eine
    Zeichenklasse für den Namensteil wäre ein Fail-open, weil eine Datei mit
    Umlaut oder Leerzeichen still aus dem Scan fiele und trotzdem existierte.

    Aus demselben Fragment entsteht das Zeilenmuster, damit Dateiscan und
    Tabellenzeile garantiert dieselben Namen durchlassen. Ließe der Scan einen
    Namen zu, den die Tabelle nicht aufnehmen kann, bliebe das Gate rot ohne
    einen Weg, es grün zu bekommen.
    """

    def __init__(self, titel, verzeichnis, endung, was, wozu):
        self.titel = titel
        self.verzeichnis = REPO / verzeichnis
        self.was = was
        self.wozu = wozu
        self.endung = re.compile(endung + r'$')
        # Erste Spalte einer Tabellenzeile: | `name.py` | Zweck |
        # Nicht-gierig, damit der Match in Spalte 1 bleibt; umgebender
        # Leerraum wird getrimmt, Backticks sind optional.
        self.zeile = re.compile(r'^\|\s*`?([^|`]+?' + endung + r')`?\s*\|')

    def im_dateisystem(self) -> set:
        """Bezeichner ist der Pfad relativ zum Verzeichnis. Solange dieses flach
        ist, ist das der Dateiname; liegt eine Datei je in einem Unterordner,
        steht der Pfad in der Tabelle und bleibt eindeutig."""
        return {p.relative_to(self.verzeichnis).as_posix()
                for p in self.verzeichnis.rglob('*')
                if p.is_file() and self.endung.search(p.name)}

    def in_tabelle(self, abschnitt_text: str) -> set:
        return {m.group(1)
                for m in (self.zeile.match(z) for z in abschnitt_text.splitlines())
                if m}


INVENTARE = [
    # Was Playwright tatsächlich einsammelt, nicht was heute zufällig dort
    # liegt: testing/playwright.config.js setzt nur testDir und kein testMatch,
    # es gilt also der Default `**/*.@(spec|test).?(c|m)[jt]s?(x)`, rekursiv und
    # auch *.test.js. Ein engerer Glob wäre ein Fail-open, weil eine Spec in
    # einem künftigen Unterordner in der Suite mitliefe und hier grün wäre.
    Inventar('### Test File Inventory', 'testing/tests',
             r'\.(?:spec|test)\.(?:[cm]?[jt]sx?)',
             'Playwright-Specs in testing/tests/',
             'Kategorie plus einen Satz, wofür die Spec da ist'),
    Inventar('### Audit Scripts Reference', 'scripts/audit',
             r'\.py',
             'Skripte in scripts/audit/',
             'einen Satz, was das Skript tut, und ob ein Workflow es ruft'),
]


def abschnitt(text: str, titel: str) -> str:
    """Der Bereich unter einer Überschrift bis zur nächsten derselben oder einer
    höheren Ebene.

    Fehlt die Überschrift, ist das ein Fehler und kein leeres Ergebnis: sonst
    meldete das Gate nach einer Umbenennung der Überschrift jede einzelne Datei
    als fehlend, statt zu sagen, dass es die Tabelle nicht mehr findet.

    Code-Blöcke werden ganz verworfen, aus zwei Gründen in dieser Reihenfolge.
    Der erste: eine Zeile wie `# python scripts/…` darin zählte sonst als
    Überschrift und schnitte die Tabelle vorzeitig ab; das Muster ist in diesen
    Docstrings üblich, und die Abschnitte tragen bereits Prosa, wachsen also.
    Der zweite folgt aus dem ersten: sobald ein Code-Block im Abschnitt möglich
    ist, kann darin eine Beispiel-Tabellenzeile stehen, und die zählte als
    Eintrag. Eine Datei wäre dann gelistet, weil jemand sie als Beispiel
    hingeschrieben hat. Die Zeilen nur für die Überschriftenerkennung zu
    ignorieren und sie trotzdem zurückzugeben, wäre also ein Fail-open.

    Eine nicht geschlossene Fence verwirft den Rest des Dokuments. Das ist
    fail-closed: die Dateien darunter fehlen dann im Ergebnis und werden
    gemeldet.
    """
    zeilen = text.splitlines()
    try:
        start = zeilen.index(titel)
    except ValueError:
        raise SystemExit(
            f'FEHLER: Überschrift "{titel}" steht nicht in {DOC.name}. '
            'Wurde sie umbenannt? Dann INVENTARE hier mitziehen.'
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


def pruefe(vorhanden: set, gelistet: set) -> tuple:
    """(fehlt in der Tabelle, in der Tabelle ohne Datei)"""
    return sorted(vorhanden - gelistet), sorted(gelistet - vorhanden)


def selbsttest() -> int:
    spec, skript = INVENTARE

    tabelle = (
        f'{spec.titel}\n'
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
    gelistet = spec.in_tabelle(abschnitt(tabelle, spec.titel))

    mit_codeblock = (
        f'{spec.titel}\n'
        '\n'
        '```bash\n'
        '# python scripts/audit/check-doc-inventories.py\n'
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
        ('Fehlende Datei wird gemeldet',
         pruefe({'a.spec.js', 'b.spec.js', 'neu.spec.js'}, gelistet)[0] == ['neu.spec.js']),
        ('Gelöschte Datei wird gemeldet',
         pruefe({'a.spec.js'}, gelistet)[1] == ['b.spec.js']),
        ('Deckungsgleich ist grün',
         pruefe({'a.spec.js', 'b.spec.js'}, gelistet) == ([], [])),
        ('Backticks sind optional',
         spec.in_tabelle('| x.spec.js | Main site | ohne Backticks |') == {'x.spec.js'}),
        ('Namensnennung in der Beschreibungsspalte zählt nicht',
         spec.in_tabelle('| `a.spec.js` | X | Gegenstück zu b.spec.js |') == {'a.spec.js'}),
        # Die folgenden decken ab, was Playwright per Default noch einsammelt
        # und ein Glob auf *.spec.js im Wurzelverzeichnis nicht:
        ('*.test.js zählt mit',
         bool(spec.endung.search('x.test.js'))
         and spec.in_tabelle('| `x.test.js` | X | Y |') == {'x.test.js'}),
        ('TypeScript- und Modul-Varianten zählen mit',
         all(spec.endung.search(n) for n in ('a.spec.ts', 'b.test.mjs', 'c.spec.cjs', 'd.test.tsx'))),
        # Dateiscan und Tabellenzeile müssen dieselben Namen durchlassen, sonst
        # ließe sich eine gefundene Datei nicht eintragen.
        ('Name mit Umlaut oder Leerzeichen zählt beidseitig mit',
         spec.endung.search('wörterbuch prüfung.spec.js') is not None
         and spec.in_tabelle('| `wörterbuch prüfung.spec.js` | X | Y |')
             == {'wörterbuch prüfung.spec.js'}),
        ('Nicht-Spec zählt nicht',
         not spec.endung.search('util.js') and not spec.endung.search('fixture.spec.xml')),
        # Zwei Wirkungen in einer Eingabe: ohne Codeblock-Erkennung schnitte
        # die Kommentarzeile darin die Tabelle ab und a.spec.js fehlte; würden
        # die Blockzeilen nur für die Überschriftensuche ignoriert und trotzdem
        # zurückgegeben, zählte die Beispielzeile als Eintrag.
        ('Ein Codeblock beendet die Tabelle nicht und zählt selbst nicht mit',
         spec.in_tabelle(abschnitt(mit_codeblock, spec.titel)) == {'a.spec.js'}),
        # Prosa in Spalte 1 ist die Kehrseite davon, Leerzeichen zuzulassen,
        # und fail-closed: das Phantom taucht als "genannt, aber nicht
        # vorhanden" auf und macht Exit 1.
        ('Prosa in Spalte 1 wird als verwaister Eintrag gemeldet',
         pruefe(set(), spec.in_tabelle('| Ersatz für a.spec.js | X | Y |'))[1]
         == ['Ersatz für a.spec.js']),
        # Das zweite Inventar hat eine andere Endung und eine zweispaltige
        # Tabelle. Beides darf sich nicht vermischen.
        ('Skript-Inventar liest .py',
         skript.in_tabelle('| `check-no-cdn.py` | ein Gate |') == {'check-no-cdn.py'}),
        ('Die beiden Inventare greifen nicht ineinander',
         skript.in_tabelle('| `a.spec.js` | X |') == set()
         and spec.in_tabelle('| `doc-count-audit.py` | X | Y |') == set()),
        ('Nicht-Python zählt im Skript-Inventar nicht',
         not skript.endung.search('lexicon-baseline.json')
         and not skript.endung.search('TEXT_DATA_TABLE.xlsx')
         and not skript.endung.search('modul.pyc')),
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

    text = DOC.read_text(encoding='utf-8')
    drift = False

    for inv in INVENTARE:
        vorhanden = inv.im_dateisystem()
        gelistet = inv.in_tabelle(abschnitt(text, inv.titel))
        fehlen, verwaist = pruefe(vorhanden, gelistet)

        print(f'{inv.titel[4:]}: {len(vorhanden)} {inv.was}, '
              f'{len(gelistet)} in der Tabelle')

        if fehlen:
            drift = True
            print(f'  Fehlt in der Tabelle ({len(fehlen)}):')
            for name in fehlen:
                print(f'    {name}')
        if verwaist:
            drift = True
            print(f'  Genannt, aber nicht vorhanden ({len(verwaist)}):')
            for name in verwaist:
                print(f'    {name}')
        if fehlen or verwaist:
            print(f'  Nachzutragen ist: {inv.wozu}.')

    if drift:
        print(f'\nBitte {DOC.relative_to(REPO).as_posix()} nachziehen.')
        return 1

    print('Keine Drift.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
