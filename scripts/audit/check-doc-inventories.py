#!/usr/bin/env python3
"""
Inventar-Gate: jede Datei eines Verzeichnisses steht in der zugehörigen
Aufstellung, und die Aufstellung nennt keine Datei, die es nicht gibt.

Drei Inventare in zwei Dateien:

    ### Test File Inventory      <-  testing/tests/     (Playwright-Specs)
    ### Audit Scripts Reference  <-  scripts/audit/     (Diagnosen und Gates)
    ## Verzeichnisstruktur       <-  scripts/ und die drei flachen Unterordner
                                     audit/, sync/, _archived/ (scripts/README.md)

Anlass war #329: die Spec-Tabelle listete 20 von 30 Dateien, zusammen 86 der
276 Tests. Beim Nachziehen zeigte der Review, dass die Skript-Tabelle zwei
Abschnitte tiefer denselben Zustand hatte, 11 von 22, darunter zwei aktive
CI-Gates. Deshalb ist das Skript nicht auf Specs zugeschnitten: der Drift-Typ
ist der Tabelle egal.

Das dritte Inventar kam am 2026-08-06 dazu, aus genau demselben Befund eine
Ebene weiter. `scripts/audit/check-file-sizes.py` (#350) stand in
DEVELOPMENT.md und im Workflow, aber nicht im Verzeichnisbaum von
scripts/README.md: 24 gelistet, 25 vorhanden. Zwei Inventare derselben Sache,
eines gegatet und eines nicht, ist die Konstellation, aus der still ein
falscher zweiter Katalog wird, und der ungegatete gewinnt, weil er näher am
Code liegt und deshalb zuerst gelesen wird.

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
BAUM_DOC = REPO / 'scripts' / 'README.md'


class Inventar:
    """Ein Verzeichnis und die Tabelle, die es vollständig auflisten muss.

    `endung` ist ein Regex-Fragment ohne Anker und entscheidet allein, welche
    Datei mitzählt. Geprüft wird nur die Endung, nie der ganze Name: eine
    Zeichenklasse für den Namensteil wäre ein Fail-open, weil eine Datei mit
    Umlaut oder Leerzeichen still aus dem Scan fiele und trotzdem existierte.

    Aus demselben Fragment entsteht das Zeilenmuster, damit Dateiscan und
    Tabellenzeile dieselben Namen durchlassen. Ließe der Scan einen Namen zu,
    den die Tabelle nicht aufnehmen kann, bliebe das Gate rot ohne einen Weg,
    es grün zu bekommen. Bis auf Backtick und Pipe: die kann eine
    Markdown-Tabellenzelle nicht eindeutig führen, eine so benannte Datei wäre
    also unauflösbar rot. Unter Linux ist das erlaubt, im Repo kommt es nicht
    vor, und die Alternative wäre, solche Namen stillschweigend zu übergehen.
    """

    def __init__(self, titel, verzeichnis, endung, was, wozu, doc=DOC):
        self.titel = titel
        self.verzeichnis = REPO / verzeichnis
        self.doc = doc
        self.was = was
        self.wozu = wozu
        # Geklammert eingesetzt, nicht roh. Die zwei heutigen Fragmente sind
        # auf oberster Ebene alternationsfrei, ein künftiges `\.py|\.sh` wäre
        # es nicht: `\.py|\.sh$` verankerte nur den zweiten Zweig, und
        # "foo.python.txt" zählte als Treffer. Ein Fail-open in genau der
        # Erweiterung, für die es diese Klasse gibt.
        muster = f'(?:{endung})'
        self.endung = re.compile(muster + r'$')
        # Erste Spalte einer Tabellenzeile: | `name.py` | Zweck |
        # Nicht-gierig, damit der Match in Spalte 1 bleibt; umgebender
        # Leerraum wird getrimmt, Backticks sind optional. group(1) ist die
        # äußere Klammer, weil sie zuerst öffnet: auch dann stabil, wenn ein
        # künftiges Fragment eigene Gruppen mitbringt.
        self.zeile = re.compile(r'^\|\s*`?([^|`]+?' + muster + r')`?\s*\|')
        self.muster = muster

    def im_dateisystem(self) -> set:
        """Bezeichner ist der Pfad relativ zum Verzeichnis. Solange dieses flach
        ist, ist das der Dateiname; liegt eine Datei je in einem Unterordner,
        steht der Pfad in der Tabelle und bleibt eindeutig."""
        return {p.relative_to(self.verzeichnis).as_posix()
                for p in self.verzeichnis.rglob('*')
                if p.is_file() and self.endung.search(p.name)}

    def bereich(self, text: str) -> str:
        return abschnitt(text, self.titel, self.doc.name)

    def in_tabelle(self, abschnitt_text: str) -> set:
        return {m.group(1)
                for m in (self.zeile.match(z) for z in abschnitt_text.splitlines())
                if m}


class BaumInventar(Inventar):
    """Ein Verzeichnisbaum in einem Code-Block statt einer Markdown-Tabelle.

    Zwei Unterschiede zur Tabellenfassung, beide erzwungen durch die Form:

    Der Abschnitt ist der Code-Block selbst, nicht der Text um ihn herum. Das
    ist das Gegenteil dessen, was `abschnitt()` tut, und aus demselben Grund
    richtig: dort sind die Blöcke Beispiele und dürfen nicht zählen, hier IST
    der Block das Inventar. Ein Name in der Prosa darunter zählt bewusst nicht,
    sonst wäre eine Datei gelistet, weil sie irgendwo erwähnt wird.

    Und der Baum listet mehrere flache Verzeichnisse mit blossem Dateinamen,
    ohne Pfad. Deshalb wird nicht rekursiv gescannt: `_archived/wzb/` und die
    sechs `ingest/`-Ordner stehen im Baum als Ordner und fuehren ihre Dateien
    absichtlich nicht einzeln auf. Kollidieren zwei Basisnamen ueber die
    Verzeichnisse hinweg, kann der Baum sie nicht auseinanderhalten; dann ist
    das Gate rot, statt einen der beiden stillschweigend als abgedeckt zu
    zaehlen. Heute kollidiert keiner, und genau deshalb faellt es sonst nie auf.
    """

    def __init__(self, titel, verzeichnisse, endung, was, wozu, doc):
        super().__init__(titel, verzeichnisse[0], endung, was, wozu, doc)
        self.verzeichnisse = [REPO / v for v in verzeichnisse]
        # Alles vor dem Kommentar, am Zeilenende verankert: so zaehlt weder ein
        # Dateiname im Kommentar noch ein Ordner-Eintrag (`ingest/`).
        self.eintrag = re.compile(r'([^\s│├└─/]+' + self.muster + r')$')

    def im_dateisystem(self) -> set:
        namen = {}
        for verzeichnis in self.verzeichnisse:
            for p in sorted(verzeichnis.glob('*')):
                if p.is_file() and self.endung.search(p.name):
                    namen.setdefault(p.name, []).append(
                        p.relative_to(REPO).as_posix())
        doppelt = {n: pfade for n, pfade in namen.items() if len(pfade) > 1}
        if doppelt:
            raise SystemExit(
                'FEHLER: gleicher Dateiname in mehreren Verzeichnissen, der '
                'Baum kann sie nicht unterscheiden: '
                + '; '.join(f'{n} ({", ".join(p)})' for n, p in sorted(doppelt.items()))
            )
        return set(namen)

    def bereich(self, text: str) -> str:
        return codeblock(text, self.titel, self.doc.name)

    def in_tabelle(self, abschnitt_text: str) -> set:
        namen = set()
        for zeile in abschnitt_text.splitlines():
            treffer = self.eintrag.search(zeile.split('#', 1)[0].rstrip())
            if treffer:
                namen.add(treffer.group(1))
        return namen


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
    # Der Baum fuehrt Python und Node gemeinsam: `run-tests.js` und
    # `build-corpus-index.py` stehen als Nachbarn darin, und eine Endung, die
    # nur eines von beiden kennt, liesse die Haelfte des Wurzelverzeichnisses
    # ungeprueft.
    BaumInventar('## Verzeichnisstruktur',
                 ('scripts', 'scripts/audit', 'scripts/sync', 'scripts/_archived'),
                 r'\.py|\.js',
                 'Skripte in scripts/ und den drei flachen Unterordnern',
                 'die Zeile im Baum, mit einem Kommentar, wofuer das Skript da ist',
                 BAUM_DOC),
]


def abschnitt(text: str, titel: str, doc_name: str = DOC.name) -> str:
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

    Eine nicht geschlossene Fence verwirft alles ab ihrer Zeile. Fail-closed in
    beiden Lagen, aber mit verschiedenen Meldungen: steht sie hinter der
    Überschrift, fehlen die Dateien darunter im Ergebnis und werden gemeldet;
    steht sie davor, verschwindet die Überschrift mit, und es gibt den
    SystemExit oben statt einer Fehlenden-Liste.

    Die Code-Blöcke fallen deshalb weg, BEVOR die Überschrift gesucht wird,
    nicht erst danach. Sonst könnte eine Überschrift, die weiter oben als
    Beispiel in einem Block steht, den Scan an der falschen Stelle beginnen
    lassen; der Fence-Zähler startete dann mitten im Block und der Rest des
    Dokuments zählte als Code. Das Beispiel-Muster ist in diesen Docstrings
    üblich, oben in dieser Datei steht es selbst.

    Der Öffner wird gemerkt, Zeichen und Länge, statt jede Fence-Zeile als
    Umschalter zu nehmen. Verschachtelung ist die übliche Schreibweise, um
    Markdown in Markdown zu zeigen (~~~ außen und ``` innen, oder vier
    Backticks außen und drei innen), und ein blinder Umschalter kippte am
    inneren Marker heraus: die Beispielzeile dazwischen zählte dann als
    Tabelleneintrag. Fail-open, dieselbe Klasse wie das ungeklammerte
    Endungs-Fragment weiter oben, nur eine Ebene tiefer versteckt.
    """
    fence = re.compile(r'^\s*(`{3,}|~{3,})')
    ausserhalb = []
    offen = None  # (Zeichen, Länge) des öffnenden Markers

    for zeile in text.splitlines():
        treffer = fence.match(zeile)
        if treffer:
            marker = treffer.group(1)
            if offen is None:
                offen = (marker[0], len(marker))
            elif marker[0] == offen[0] and len(marker) >= offen[1]:
                offen = None
            # Ein andersartiger oder kürzerer Marker im Block ist Inhalt.
            continue
        if offen is None:
            ausserhalb.append(zeile)

    try:
        start = ausserhalb.index(titel)
    except ValueError:
        raise SystemExit(
            f'FEHLER: Überschrift "{titel}" steht nicht in {doc_name} '
            '(außerhalb eines Codeblocks). Wurde sie umbenannt? '
            'Dann INVENTARE hier mitziehen.'
        )

    behalten = []
    for zeile in ausserhalb[start + 1:]:
        if zeile.startswith(('# ', '## ', '### ')):
            break
        behalten.append(zeile)
    return '\n'.join(behalten)


def codeblock(text: str, titel: str, doc_name: str) -> str:
    """Der erste Code-Block unter einer Überschrift, ohne die Fence-Zeilen.

    Die genaue Umkehrung von `abschnitt()`, und aus demselben Grund richtig:
    dort sind Blöcke Beispiele und dürfen nicht zählen, hier ist der Block das
    Inventar und alles ausserhalb ist Prosa. Beide Fassungen nebeneinander sind
    kein Widerspruch, sondern der Unterschied zwischen einer Tabelle, die im
    Text steht, und einem Baum, der nur als Block darstellbar ist.

    Die Überschrift wird nur ausserhalb einer Fence gesucht, sonst begönne der
    Block an einem Beispiel. Verschachtelte Marker gelten wie oben als Inhalt,
    nicht als Umschalter.

    Fail-closed in allen drei Fehlerlagen, mit unterscheidbaren Meldungen:
    Überschrift weg, kein Block darunter, Block nicht geschlossen. Ein leeres
    Ergebnis zurückzugeben hiesse, jede Datei des Verzeichnisses als fehlend zu
    melden, statt zu sagen, dass die Aufstellung nicht gefunden wurde.
    """
    fence = re.compile(r'^\s*(`{3,}|~{3,})')
    offen = None
    nach_titel = False
    inhalt = None

    for zeile in text.splitlines():
        treffer = fence.match(zeile)
        if treffer:
            marker = (treffer.group(1)[0], len(treffer.group(1)))
            if offen is None:
                offen = marker
                if nach_titel and inhalt is None:
                    inhalt = []
                continue
            if marker[0] == offen[0] and marker[1] >= offen[1]:
                offen = None
                if inhalt is not None:
                    return '\n'.join(inhalt)
                continue
            # Ein andersartiger oder kürzerer Marker im Block ist Inhalt.
        if offen is None:
            if zeile == titel:
                nach_titel = True
        elif inhalt is not None:
            inhalt.append(zeile)

    if not nach_titel:
        raise SystemExit(
            f'FEHLER: Überschrift "{titel}" steht nicht in {doc_name} '
            '(außerhalb eines Codeblocks). Wurde sie umbenannt? '
            'Dann INVENTARE hier mitziehen.'
        )
    if inhalt is None:
        raise SystemExit(
            f'FEHLER: unter "{titel}" in {doc_name} steht kein Code-Block. '
            'Der Verzeichnisbaum ist das Inventar und muss einer sein.'
        )
    raise SystemExit(
        f'FEHLER: der Code-Block unter "{titel}" in {doc_name} ist nicht '
        'geschlossen.'
    )


def pruefe(vorhanden: set, gelistet: set) -> tuple:
    """(fehlt in der Tabelle, in der Tabelle ohne Datei)"""
    return sorted(vorhanden - gelistet), sorted(gelistet - vorhanden)


def _wirft(fn) -> bool:
    """Wirft der Aufruf SystemExit? Die Fail-closed-Lagen werden belegt und
    nicht zugesichert: eine Meldung, die niemand ausgelöst hat, ist eine
    Behauptung."""
    try:
        fn()
    except SystemExit:
        return True
    return False


def selbsttest() -> int:
    spec, skript, baum = INVENTARE

    baum_doc = (
        'Vorspann.\n'
        '\n'
        f'{baum.titel}\n'
        '\n'
        '```\n'
        'scripts/\n'
        '├── build-api.py                 # Statische JSON-API (#45)\n'
        '├── run-tests.js                 # Wrapper fuer npm test\n'
        '│\n'
        '├── ingest/                      # Korpus-Ingest je Vorhaben\n'
        '│   └── wzb/                     # Wenzelsbibel\n'
        '│\n'
        '├── audit/\n'
        '│   ├── check-no-cdn.py          # ein Gate\n'
        '│   └── lexicon-baseline.json    # Referenzmenge, keine Datei mit Endung\n'
        '│\n'
        '└── _archived/                   # Referenz, nicht ausfuehren\n'
        '    └── tei-transformation.py    # Original-Migration\n'
        '```\n'
        '\n'
        'Prosa darunter nennt phantom.py, das zaehlt nicht als gelistet.\n'
    )

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
        # Die Überschrift wird gesucht, nachdem die Blöcke weg sind. Sonst
        # begänne der Scan an der Beispielzeile, der Fence-Zähler stünde
        # mitten im Block, und der Rest des Dokuments zählte als Code.
        ('Eine Überschrift im Codeblock beginnt den Abschnitt nicht',
         spec.in_tabelle(abschnitt(
             '```markdown\n'
             f'{spec.titel}\n'
             '| `falsch.spec.js` | X | nur ein Beispiel |\n'
             '```\n'
             '\n'
             f'{spec.titel}\n'
             '\n'
             '| `richtig.spec.js` | X | die echte Tabelle |\n',
             spec.titel)) == {'richtig.spec.js'}),
        # Ein alternierendes Fragment darf nicht nur seinen letzten Zweig
        # verankern. Ungeklammert wäre "foo.python.txt" hier ein Treffer.
        ('Alternation im Endungs-Fragment bleibt verankert',
         (lambda i: i.endung.search('a.sh') is not None
          and i.endung.search('a.py') is not None
          and i.endung.search('foo.python.txt') is None
          )(Inventar('### X', 'scripts/audit', r'\.py|\.sh', 'x', 'y'))),
        # Verschachtelte Fences: mit einem blinden Umschalter schlösse der
        # innere Marker den äußeren Block, und die Beispielzeile dazwischen
        # zählte als Eintrag. Beide üblichen Schreibweisen geprüft.
        ('Ein Block mit ~~~ außen und ``` innen zählt ganz als Code',
         spec.in_tabelle(abschnitt(
             f'{spec.titel}\n'
             '~~~\n'
             '```\n'
             '| `falsch.spec.js` | X | nur ein Beispiel |\n'
             '```\n'
             '~~~\n'
             '| `richtig.spec.js` | X | die echte Tabelle |\n',
             spec.titel)) == {'richtig.spec.js'}),
        ('Ein Block mit vier Backticks außen und drei innen ebenso',
         spec.in_tabelle(abschnitt(
             f'{spec.titel}\n'
             '````markdown\n'
             '```\n'
             '| `falsch.spec.js` | X | nur ein Beispiel |\n'
             '```\n'
             '````\n'
             '| `richtig.spec.js` | X | die echte Tabelle |\n',
             spec.titel)) == {'richtig.spec.js'}),
        # --- Baum-Inventar: der Block IST das Inventar -------------------
        ('Baum: Eintraege mit Baumglyphen werden erkannt, .py und .js',
         baum.in_tabelle(codeblock(baum_doc, baum.titel, 'test.md'))
         == {'build-api.py', 'run-tests.js', 'check-no-cdn.py',
             'tei-transformation.py'}),
        # Die Kehrseite von abschnitt(): dort ist der Block Beispiel und zaehlt
        # nicht, hier ist alles ausserhalb Prosa und zaehlt nicht.
        ('Baum: Nennung in der Prosa unter dem Block zaehlt nicht',
         'phantom.py' not in baum.in_tabelle(
             codeblock(baum_doc, baum.titel, 'test.md'))),
        ('Baum: Ordner-Eintrag zaehlt nicht',
         baum.in_tabelle('├── ingest/    # Korpus-Ingest') == set()),
        ('Baum: Dateiname im Kommentar zaehlt nicht',
         baum.in_tabelle('├── run-tests.js   # ersetzt run-old.py') == {'run-tests.js'}),
        ('Baum: andere Endungen zaehlen nicht',
         baum.in_tabelle('│   └── lexicon-baseline.json  # X') == set()
         and baum.in_tabelle('│   └── TEXT_DATA_TABLE.xlsx  # X') == set()),
        ('Baum: fehlende Datei wird gemeldet',
         pruefe({'build-api.py', 'neu.py'},
                baum.in_tabelle(codeblock(baum_doc, baum.titel, 'test.md')))[0]
         == ['neu.py']),
        ('Baum: geloeschte Datei wird als verwaist gemeldet',
         pruefe({'build-api.py'},
                baum.in_tabelle('├── build-api.py\n├── weg.py'))[1] == ['weg.py']),
        ('Baum: eine Ueberschrift im Codeblock beginnt den Block nicht',
         baum.in_tabelle(codeblock(
             '```markdown\n'
             f'{baum.titel}\n'
             '├── falsch.py   # nur ein Beispiel\n'
             '```\n'
             '\n'
             f'{baum.titel}\n'
             '```\n'
             '├── richtig.py  # der echte Baum\n'
             '```\n',
             baum.titel, 'test.md')) == {'richtig.py'}),
        ('Baum: verschachtelte Fences beenden den Block nicht',
         baum.in_tabelle(codeblock(
             f'{baum.titel}\n'
             '~~~\n'
             '├── a.py\n'
             '```\n'
             '├── b.py\n'
             '```\n'
             '├── c.py\n'
             '~~~\n'
             '├── danach.py  # ausserhalb\n',
             baum.titel, 'test.md')) == {'a.py', 'b.py', 'c.py'}),
        # Fail-closed, jede Lage mit eigener Meldung: sonst meldete das Gate
        # nach einer Umbenennung jede Datei einzeln als fehlend.
        ('Baum: fehlende Ueberschrift ist ein Fehler, kein leeres Ergebnis',
         _wirft(lambda: codeblock('nur Prosa\n', baum.titel, 'test.md'))),
        ('Baum: Ueberschrift ohne Block ist ein Fehler',
         _wirft(lambda: codeblock(f'{baum.titel}\nnur Prosa\n', baum.titel, 'test.md'))),
        ('Baum: nicht geschlossener Block ist ein Fehler',
         _wirft(lambda: codeblock(f'{baum.titel}\n```\n├── a.py\n', baum.titel, 'test.md'))),
        # Der Baum fuehrt blosse Dateinamen. Zwei gleiche Namen in zwei
        # Verzeichnissen waeren im Set eine Datei, und die zweite gaelte
        # stillschweigend als abgedeckt: Fail-open. Dasselbe Verzeichnis
        # zweimal ist der billigste echte Fall dieser Lage.
        ('Baum: kollidierende Basisnamen sind ein Fehler',
         _wirft(lambda: BaumInventar(
             '### X', ('scripts/audit', 'scripts/audit'), r'\.py',
             'x', 'y', BAUM_DOC).im_dateisystem())),
        ('Baum: scannt nicht rekursiv (ingest/ und _archived/wzb/ bleiben aussen)',
         'wzb_roman.py' not in baum.im_dateisystem()
         and 'wzb-fix-pronoun-in.py' not in baum.im_dateisystem()),
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

    quelle = {}
    drift = set()

    for inv in INVENTARE:
        if inv.doc not in quelle:
            quelle[inv.doc] = inv.doc.read_text(encoding='utf-8')
        vorhanden = inv.im_dateisystem()
        gelistet = inv.in_tabelle(inv.bereich(quelle[inv.doc]))
        fehlen, verwaist = pruefe(vorhanden, gelistet)

        print(f'{inv.titel.lstrip("#").strip()}: {len(vorhanden)} {inv.was}, '
              f'{len(gelistet)} in {inv.doc.name}')

        if fehlen:
            drift.add(inv.doc)
            print(f'  Fehlt in der Aufstellung ({len(fehlen)}):')
            for name in fehlen:
                print(f'    {name}')
        if verwaist:
            drift.add(inv.doc)
            print(f'  Genannt, aber nicht vorhanden ({len(verwaist)}):')
            for name in verwaist:
                print(f'    {name}')
        if fehlen or verwaist:
            print(f'  Nachzutragen ist: {inv.wozu}.')

    if drift:
        for doc in sorted(drift):
            print(f'\nBitte {doc.relative_to(REPO).as_posix()} nachziehen.')
        return 1

    print('Keine Drift.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
