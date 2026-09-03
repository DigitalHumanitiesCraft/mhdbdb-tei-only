#!/usr/bin/env python3
"""Baut den abzaehlbaren Teil der Triage-Matrix (#44) aus den Issue-Labels.

## Warum es dieses Skript gibt

#44 ist die Triage-Matrix des Projekts und macht Aussagen ueber alle offenen
Issues gleichzeitig. Genau deshalb veraltet der Body schneller als jede andere
Datei: jede Ticket-Aenderung kann ihn falsch machen, ohne ihn anzufassen. Am
05.08.2026 wurde er innerhalb einer einzigen Sitzung zweimal unwahr, einmal
durch das Schliessen von #114 und einmal durch eine eigene Passage ueber drei
angeblich tote Codepfade, die es laengst nicht mehr gab. Ein Ticket auf diesen
Befund waere reine Selbstbeschaeftigung gewesen.

Die Diagnose dazu stammt von chsteiner: "die staleness von #44 ist ein
dauerzustand und schadet viel mehr als der body inhalt hilft". Also wird der
Teil, der sich abzaehlen laesst, nicht mehr von Hand gepflegt. Die Labels sind
die belastbarere Quelle, weil sie am Ticket haengen und nicht an einem Absatz.

## Was generiert wird und was nicht

Generiert (zwischen den Markern, jeder Handstand darin wird ueberschrieben):
Quick Stats, Verteilung nach Bereich, die Ping-Liste aus `wait:*` und je eine
Tabelle pro Autonomiestufe.

Von Hand bleibt alles ausserhalb der Marker: die Legende des Schemas, die
Arbeitsregeln und die Befundliste. Das ist Urteil und keine Zaehlung.

## Das Label-Schema, gegen das geprueft wird

Drei Achsen mit genau einem Label je Achse und Ticket:

    auto:full | auto:brief | auto:checkin | auto:pair | auto:blocked
    area:data | area:frontend | area:playground | area:pipeline
              | area:docs | area:orga
    effort:small | effort:medium | effort:large

Dazu die Flags `ingest` und `evergreen` sowie, nur an `auto:blocked`, ein oder
mehrere `wait:*` (kzw, julia, linda, extern). Mehrere sind erlaubt und
richtig: #315 wartet auf KZW *und* Julia.

`evergreen` ist die einzige Ausnahme von der Achsenpflicht. #44 traegt kein
`auto:*` und kein `effort:*`, weil es nicht abgearbeitet, sondern gepflegt
wird. Es faellt deshalb aus allen Zaehlungen heraus.

## Warum das Skript bei Label-Luecken rot wird

Ein fehlendes `auto:*` ist kein Schoenheitsfehler, sondern der Zustand, aus
dem die alte Label-Landschaft entstanden ist: vergeben beim Anlegen, nie
nachgezogen, bis die Labels nichts mehr aussagten (gemessen am 05.08.2026
unmittelbar vor dem Umbau: 28 Labels, davon vier fuer denselben Sachverhalt).
Wer ein Ticket anlegt und die Achsen nicht setzt, soll das im Gate sehen und
nicht in vier Wochen.

Umgekehrt gilt: `auto:blocked` ohne `wait:*` macht die Ping-Liste
unvollstaendig, und ein `wait:*` an einem nicht blockierten Ticket macht sie
falsch. Beides ist ein Fehler und kein Hinweis.

## MESSVORSCHRIFT: zwei Daten, die verschiedene Fragen beantworten

**In den Tabellen** steht die letzte Wortmeldung im Ticket, gleich von wem,
ersatzweise das Anlegedatum. Nicht `updatedAt`, obwohl das billiger zu holen
waere: dieses Feld springt bei jeder Label-Aenderung auf heute. Beim Aufbau
des Schemas am 05.08. standen dadurch schlagartig alle 52 Tickets auf
demselben Datum, und die Sortierung "aeltestes zuerst" war wertlos.

**In der Ping-Liste** steht das Datum der letzten Wortmeldung **der
erwarteten Person**. Die Frage dort lautet "wie lange schweigt KZW zu
diesem Ticket" und nicht "wann hat hier zuletzt jemand geschrieben". Der
Unterschied ist am selben 05.08. teuer geworden: sieben Tickets bekamen an
einem Nachmittag einen Nachmess-Kommentar, und die Ping-Liste zeigte sie
danach als frisch. #115 wartet seit dem 29.05. auf eine Antwort von KZW und
stand ploetzlich auf dem heutigen Datum. Das ist derselbe Fehlermodus wie `updatedAt`, nur
subtiler, weil die eigene Betriebsamkeit diesmal wie Fortschritt aussieht.

Ausnahme `wait:extern`: Carina, Silvan, Alan und Gloning haben keinen
GitHub-Account, ihre Antworten trudeln ueber KZW ein. Es gibt dort also kein
Konto, dessen Schweigen man messen koennte. Gezaehlt wird deshalb der letzte
Kommentar, der **nicht von unserer Seite** stammt (`UNSERE_SEITE`, Bots
eingeschlossen). Ohne diese zweite Haelfte des Fixes traefe dieselbe
Uhr-Ruecksetzung ein: #92 und #147 sprangen am 05.08. auf das Tagesdatum,
weil sie einen Nachmess-Kommentar bekamen. Gemessen steht #92 jetzt auf
2026-05-07, dem Anlegedatum, weil dort ueberhaupt noch nie jemand ausser
uns geschrieben hat, und #147 auf 2026-07-10.

Beide Daten kommen aus demselben `gh issue list`-Aufruf, das kostet rund
drei Sekunden fuer den ganzen Bestand.

Usage:
    python scripts/audit/build-issue-matrix.py             # Vorschau auf stdout
    python scripts/audit/build-issue-matrix.py --apply     # #44 aktualisieren
    python scripts/audit/build-issue-matrix.py --check     # Gate: Drift = rot
    python scripts/audit/build-issue-matrix.py --selftest  # ohne Netz pruefen

Exit codes:
    0 = alles konsistent (bei --check zusaetzlich: Body ist aktuell)
    1 = Label-Luecke, oder bei --check ein veralteter Body
    2 = gh nicht nutzbar, Marker fehlen oder stehen verkehrt herum,
        Issue nicht lesbar

Der Unterschied zwischen 1 und 2 ist die Aussage des Workflow-Laufs: bei 1
steht der Body, aber ein Ticket ist unvollstaendig gelabelt; bei 2 ist
nichts geschrieben worden. Deshalb steigen alle Fehlerpfade ueber
`abbruch()` aus und nicht ueber `sys.exit(<string>)`, das 1 liefern wuerde.
"""
import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

MATRIX_ISSUE = 44
BEGIN = '<!-- MATRIX:BEGIN (generiert von scripts/audit/build-issue-matrix.py, nicht von Hand aendern) -->'
END = '<!-- MATRIX:END -->'

# Reihenfolge ist Absicht: von "sofort machbar" nach "wartet auf einen
# Menschen". Wer die Matrix liest, um Arbeit zu finden, liest von oben.
AUTO_STUFEN = [
    ('auto:full', 'sofort machbar, keine offene Frage'),
    ('auto:brief', 'kurze Klaerung vorab, dann am Stueck durchziehbar'),
    ('auto:checkin', 'semiautonom, Zwischenentscheidungen unterwegs'),
    ('auto:pair', 'nur gemeinsam mit Chris in einer Session'),
    ('auto:blocked', 'wartet auf einen Menschen, nicht auf Arbeit'),
]
AREAS = ['area:data', 'area:frontend', 'area:playground', 'area:pipeline',
         'area:docs', 'area:orga']
EFFORTS = ['effort:small', 'effort:medium', 'effort:large']
# Sortierschluessel innerhalb einer Stufe: der kleinste Brocken zuerst.
EFFORT_RANG = {e: i for i, e in enumerate(EFFORTS)}

WAIT_NAMEN = {
    'wait:kzw': 'KZW (`wachauer`)',
    'wait:julia': 'Julia (`juliahin`)',
    'wait:linda': 'Linda (`lindabeutel`)',
    'wait:extern': 'Externe',
}

# Wessen Schweigen die Wartezeit misst. Fuer `wait:extern` gibt es keinen
# GitHub-Account: Carina, Silvan, Alan und Gloning kommentieren nicht selbst,
# ihre Antworten trudeln ueber KZW ein. Dort zaehlt deshalb der letzte
# Kommentar, der nicht von unserer Seite stammt.
WAIT_KONTEN = {
    'wait:kzw': 'wachauer',
    'wait:julia': 'juliahin',
    'wait:linda': 'lindabeutel',
}

# Wer bei `wait:extern` nicht als Antwort zaehlt. Bots stehen mit drin,
# damit ein Review-Kommentar die Uhr ebenfalls nicht zuruecksetzt.
#
# Ohne `[bot]`-Suffix, und das ist keine Nachlaessigkeit: `gh issue list
# --json comments` laeuft ueber GraphQL und liefert Bot-Logins nackt
# ("claude"), die REST-API dagegen mit Suffix ("claude[bot]"). `konto_von()`
# schneidet das Suffix ab, damit beide Formate hier treffen. Die erste
# Fassung dieser Liste trug das Suffix und war damit toter Code, inklusive
# eines gruenen Selbsttests, der dasselbe falsche Format prueft.
UNSERE_SEITE = ('chsteiner', 'claude', 'github-actions')


def abbruch(meldung):
    """Mit Exit 2 aussteigen: Werkzeug- oder Datenfehler, keine Label-Luecke.

    Nicht `sys.exit(<string>)`: das liefert Exit-Code 1 und ist damit von
    einer Label-Luecke nicht mehr zu unterscheiden. Der Unterschied traegt
    die Aussage des Workflows: rot mit 1 heisst "Body geschrieben, aber ein
    Ticket ist unvollstaendig gelabelt", rot mit 2 heisst "nichts passiert".
    """
    print(f'::error::{meldung}', file=sys.stderr)
    sys.exit(2)


def gh(args):
    """`gh` aufrufen und stdout zurueckgeben, sonst mit Exit 2 aussteigen."""
    try:
        res = subprocess.run(['gh'] + args, capture_output=True, text=True,
                             encoding='utf-8', errors='replace')
    except OSError as exc:
        abbruch(f'gh nicht aufrufbar: {exc}')
    if res.returncode != 0:
        abbruch(f'gh {" ".join(args)} fehlgeschlagen: {res.stderr.strip()}')
    return res.stdout


def issue_liste(state, felder, limit):
    """`gh issue list` mit einer Obergrenze, die sich meldet, wenn sie greift.

    `--limit` ist eine Obergrenze, keine Seitengroesse: `gh` paginiert intern
    und schneidet bei N still ab, mit Exit 0. Eine Abfrage, die genau N Zeilen
    liefert, ist deshalb nicht als vollstaendig zu lesen, und ein Gate auf einer
    abgeschnittenen Liste beruhigt, ohne zu decken: es meldet einfach nichts
    mehr. Darum hier Abbruch statt Warnung. Er kostet einmal eine Zeile im
    Skript und ist die einzige Stelle, an der die Saettigung ueberhaupt
    sichtbar wird.
    """
    roh = json.loads(gh(['issue', 'list', '--state', state,
                         '--limit', str(limit), '--json', felder]))
    if len(roh) >= limit:
        abbruch(f'gh issue list --state {state} hat das Limit von {limit} '
                f'ausgeschoepft ({len(roh)} Eintraege). Die Liste ist '
                f'moeglicherweise abgeschnitten, und jede Auswertung darauf '
                f'waere still unvollstaendig. Limit in issue_liste() erhoehen.')
    return roh


def hole_issues():
    roh = issue_liste('open', 'number,title,labels,createdAt,comments', 300)
    for i in roh:
        i['labels'] = sorted(l['name'] for l in i['labels'])
        i['still_seit'] = letzte_wortmeldung(i)
    return sorted(roh, key=lambda i: i['number'])


def konto_von(kommentar):
    """Login des Kommentators, ohne `[bot]`-Suffix.

    GraphQL (`gh issue list --json comments`) liefert Bot-Logins nackt,
    REST mit Suffix. Beide muessen gegen dieselbe Liste treffen.
    """
    login = ((kommentar.get('author') or {}).get('login') or '')
    return login[:-5] if login.endswith('[bot]') else login


def letzte_wortmeldung(issue, konto=None, ausser=None):
    """Datum des letzten Kommentars, ersatzweise das Anlegedatum.

    Genau einer der beiden Filter greift, nie beide: mit `konto` zaehlen
    nur die Kommentare dieser Person, mit `ausser` alle ausser denen der
    genannten Logins, und `konto` hat Vorrang. Die Ping-Liste braucht den
    ersten Modus ("wie lange schweigt KZW zu diesem Ticket"), die Tabellen
    keinen ("wann hat hier zuletzt jemand geschrieben").

    Warum das nicht dasselbe ist und was die Verwechslung gekostet hat:
    Messvorschrift im Modul-Docstring. Sie steht dort und nur dort, damit
    das gemessene Datum darin nicht an zwei Stellen wahr gehalten werden
    muss.
    """
    kommentare = issue.get('comments') or []
    if konto:
        kommentare = [k for k in kommentare if konto_von(k) == konto]
    elif ausser:
        kommentare = [k for k in kommentare if konto_von(k) not in ausser]
    if kommentare:
        return max(k['createdAt'] for k in kommentare)[:10]
    return issue['createdAt'][:10]


def achse(issue, praefix):
    """Alle Labels eines Praefix an diesem Issue."""
    return [l for l in issue['labels'] if l.startswith(praefix)]


def pruefe(issues):
    """Label-Luecken finden. Liefert eine Liste von Klartext-Meldungen."""
    fehler = []
    for i in issues:
        nr = i['number']
        if 'evergreen' in i['labels']:
            # Die Matrix selbst wird gepflegt, nicht abgearbeitet.
            continue
        for praefix, name in (('auto:', 'Autonomiestufe'), ('area:', 'Bereich'),
                              ('effort:', 'Aufwand')):
            treffer = achse(i, praefix)
            if len(treffer) != 1:
                gefunden = ', '.join(treffer) if treffer else 'keins'
                fehler.append(f'#{nr}: {name} muss genau ein Label sein, '
                              f'gefunden: {gefunden}')
        wartet = achse(i, 'wait:')
        blockiert = 'auto:blocked' in i['labels']
        if blockiert and not wartet:
            fehler.append(f'#{nr}: auto:blocked ohne wait:*, die Ping-Liste '
                          f'bleibt unvollstaendig')
        if wartet and not blockiert:
            fehler.append(f'#{nr}: {", ".join(wartet)} an einem Ticket ohne '
                          f'auto:blocked')
        unbekannt = [w for w in wartet if w not in WAIT_NAMEN]
        if unbekannt:
            fehler.append(f'#{nr}: unbekanntes wait-Label: {", ".join(unbekannt)}')
    return fehler


ROADMAP = 'docs/ROADMAP.md'


def hole_geschlossene():
    """Die Nummern der geschlossenen Issues. Bewusst nicht 'alles, was nicht
    offen ist': Issues und PRs teilen sich bei GitHub den Nummernraum, und
    `gh issue list` liefert keine PRs. Gegen 'nicht offen' zu pruefen meldet
    daher jede PR-Nummer, und die ROADMAP fuehrt eine Merge-Tabelle, deren
    erste Spalte aus PR-Nummern besteht. Beim ersten Lauf hat genau das die
    gemergten #245 und #246 gemeldet."""
    return {i['number'] for i in issue_liste('closed', 'number', 1000)}


def pruefe_roadmap(geschlossene):
    """Geschlossene Issues finden, die in docs/ROADMAP.md noch als Eintrag stehen.

    Anlass (Health-Check 02.09.): sechs Eintraege kuendigten Arbeit oder eine
    Antwort an, obwohl die Issues geschlossen waren, und fuenf davon waren es
    schon, als die Datei zuletzt bearbeitet wurde (07.08.). Eine Ermahnung reicht
    dagegen erkennbar nicht.

    Erkannt wird NUR eine Nummer in der ersten Spalte einer Tabellenzeile, also
    der Eintrag selbst. Das ist gemessen und nicht geschaetzt: gegen den Stand
    vor den Korrekturen des 02.09. meldet diese Variante 6 Zeilen, und alle
    sechs sind echt (#106, #111, #129, #140, #172, #224); gegen den Stand danach
    meldet sie 0. Jede `#N` im Dokument zu pruefen haette 45 gemeldet, weil die
    Datei PR-Nummern und Rueckblicke auf erledigte Arbeit im Fliesstext fuehrt.
    Ein Gate, das beim ersten Lauf 45 Zeilen meldet, wird abgeschaltet statt
    beachtet. Auch Aufzaehlungszeilen mitzunehmen kostet schon einen Fehlalarm
    (#187 steht als datierter Rueckblick da, nicht als offener Punkt).

    Der Preis dieser Enge ist ein blinder Fleck: ein Eintrag, der spaeter als
    Aufzaehlung statt als Tabellenzeile geschrieben wird, faellt heraus. Die
    beiden anderen sind geschlossen: eine abgeschnittene Issue-Liste faengt
    issue_liste() ab, und eine fehlende ROADMAP.md wirft hier.

    Der Wurf statt einer leeren Trefferliste ist die Lehre aus dem ersten Tag
    dieses Gates. Es stand hier ein stilles `return []`, mit der Begruendung,
    das Fehlen der Datei falle in diesem Repositorium selbst auf. Im einzigen
    automatischen Aufrufer fiel es nicht auf: issue-matrix.yml checkte
    `scripts/audit` sparse aus, docs/ROADMAP.md war nie vorhanden, und das Gate
    meldete taeglich gruen, ohne je eine Zeile gelesen zu haben. Damit war es
    genau das, wogegen es gebaut wurde: konfiguriert, gruen, prueft nichts.
    Gefunden hat es der CI-Review-Bot auf PR #396 am 02.09.2026; drei lokale
    Reviewrunden hatten den Zweig gesehen und die Checkout-Konfiguration nicht
    aufgemacht.

    Warnung, kein Fehler: ein geschlossenes Issue in der ROADMAP ist ein
    Pflegerueckstand und kein kaputter Build. Das gilt auch fuer den Ausfall
    dieser Pruefung selbst, siehe main().
    """
    pfad = Path(ROADMAP)
    if not pfad.exists():
        raise FileNotFoundError(pfad)
    treffer = []
    for zeile_nr, zeile in enumerate(
            pfad.read_text(encoding='utf-8').splitlines(), start=1):
        m = re.match(r'\|\s*#(\d+)\s*\|', zeile)
        if m and int(m.group(1)) in geschlossene:
            treffer.append((zeile_nr, int(m.group(1))))
    return treffer


def entschaerfe(titel):
    """Einen Issue-Titel in eine Tabellenzelle zwingen.

    Vier Dinge, jedes aus einem echten Fall im Bestand:

    `MATRIX:*` im Titel waere kumulativ zerstoererisch. Der Marker landet
    im generierten Block, und ab dem zweiten Lauf findet `partition(END)`
    den inneren Marker zuerst; der Body waechst dann taeglich um einen
    Blockrest, still und ohne Obergrenze.

    Spitze Klammern verschluckt GitHubs HTML-Sanitizer beim Rendern. Das
    trifft dieses Projekt haeufiger als andere, weil TEI-Elemente in
    Ticket-Titeln stehen: #252 verloere ohne diese Zeile sein `<gap/>` und
    damit das Subjekt des Satzes, #228 sein `<note n=...>`, und das `<div>`
    aus #138 wuerde als Block-Element in die Zelle gerendert. Das `&` muss
    zuerst weg, sonst maskiert der zweite Schritt die eigenen Entities.

    Ein Pipe wuerde die Zelle teilen, ein Zeilenumbruch die ganze Zeile.
    """
    for marker in ('MATRIX:BEGIN', 'MATRIX:END'):
        titel = titel.replace(marker, marker.replace(':', ': '))
    titel = titel.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return titel.replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')


def zeile(issue):
    """Eine Tabellenzeile: Nummer, Titel, Bereich, Aufwand, Flag, Datum."""
    area = (achse(issue, 'area:') or ['?'])[0].replace('area:', '')
    eff = (achse(issue, 'effort:') or ['?'])[0].replace('effort:', '')
    flag = '`ingest`' if 'ingest' in issue['labels'] else ''
    # Erst kuerzen, dann maskieren: die 78 sollen sichtbare Zeichen zaehlen
    # und nicht Entities, und ein Schnitt mitten in `&lt;` kann so nicht
    # entstehen, weil es zum Zeitpunkt des Schnitts noch `<` ist.
    titel = issue['title']
    if len(titel) > 78:
        titel = titel[:77] + '…'
    titel = entschaerfe(titel)
    return (f'| #{issue["number"]} | {titel} | {area} | {eff} | {flag} | '
            f'{issue["still_seit"]} |')


def tabelle(issues):
    kopf = ('| # | Titel | Bereich | Aufwand | Flag | letzte Wortmeldung |\n'
            '|---|-------|---------|---------|------|--------------------|')
    sortiert = sorted(issues, key=lambda i: (
        EFFORT_RANG.get((achse(i, 'effort:') or [''])[0], 9), i['number']))
    return '\n'.join([kopf] + [zeile(i) for i in sortiert])


def baue(issues):
    """Den generierten Block als Markdown."""
    zaehlbar = [i for i in issues if 'evergreen' not in i['labels']]
    gesamt = len(zaehlbar)
    aus = []

    aus.append(f'**{gesamt} offene Issues** (ohne den Evergreen #44). '
               f'Alles zwischen den Markern ist aus den Labels erzeugt, '
               f'siehe `scripts/audit/build-issue-matrix.py`.\n')

    # Jede Label-Luecke verzerrt die Matrix, und zwar sichtbar erst hier
    # unten: ein Ticket ohne auto:* faellt aus allen Tabellen, waehrend die
    # Kopfzahl es mitzaehlt; eins mit zwei auto:* erscheint in beiden
    # Tabellen, und die erste Fundstelle einer Sitzung ist dann womoeglich
    # "sofort machbar" fuer etwas Blockiertes; ein auto:blocked ohne wait:*
    # fehlt in jeder Zeile der Ping-Liste, deren Kopfzahl es mitzaehlt.
    # Der rote Lauf allein hilft nicht: er steht in der Actions-Historie
    # und nicht dort, wo gelesen wird. Deshalb traegt der Body dieselben
    # Meldungen, die `pruefe()` ausgibt, statt einzelner Sonderfaelle.
    luecken = pruefe(zaehlbar)
    if luecken:
        aus.append(f'> **{len(luecken)} Label-Luecke(n): solange sie stehen, '
                   f'passen Kopfzahlen und Tabellen unten nicht zusammen.**')
        for meldung in luecken:
            aus.append(f'> - {meldung}')
        aus.append('>\n> Behoben, sobald die Labels stimmen; dieser Kasten '
                   'verschwindet dann von selbst.\n')

    aus.append('### Quick Stats\n')
    aus.append('| Autonomiestufe | Anzahl | Anteil | heisst |')
    aus.append('|---|---:|---:|---|')
    for stufe, was in AUTO_STUFEN:
        n = sum(1 for i in zaehlbar if stufe in i['labels'])
        anteil = f'{round(100 * n / gesamt)} %' if gesamt else '0 %'
        aus.append(f'| `{stufe}` | {n} | {anteil} | {was} |')

    verteilung = [(a.replace('area:', ''),
                   sum(1 for i in zaehlbar if a in i['labels'])) for a in AREAS]
    verteilung = [f'`{a}` {n}' for a, n in
                  sorted(verteilung, key=lambda x: -x[1]) if n]
    mit_ingest = sum(1 for i in zaehlbar if 'ingest' in i['labels'])
    aus.append(f'\nNach Bereich: {", ".join(verteilung)}. '
               f'Mit `ingest` markiert: {mit_ingest}.\n')

    blockierte = [i for i in zaehlbar if 'auto:blocked' in i['labels']]
    if blockierte:
        aus.append('### Ping-Liste: worauf gewartet wird\n')
        aus.append(f'{len(blockierte)} Tickets warten auf einen Menschen. '
                   f'Laengste Stille zuerst. Das Datum ist die letzte '
                   f'Wortmeldung **der erwarteten Person**, damit ein '
                   f'Nachfassen von unserer Seite die Uhr nicht '
                   f'zuruecksetzt; bei Externen ohne GitHub-Konto der '
                   f'letzte Kommentar, der nicht von uns stammt.\n')
        for wait, name in WAIT_NAMEN.items():
            konto = WAIT_KONTEN.get(wait)
            treffer = [(letzte_wortmeldung(i, konto, UNSERE_SEITE), i)
                       for i in blockierte if wait in i['labels']]
            if not treffer:
                continue
            treffer.sort(key=lambda t: (t[0], t[1]['number']))
            liste = ', '.join(f'#{i["number"]} ({seit})' for seit, i in treffer)
            aus.append(f'- **{name}**, {len(treffer)}: {liste}')
        aus.append('')

    for stufe, was in AUTO_STUFEN:
        treffer = [i for i in zaehlbar if stufe in i['labels']]
        aus.append(f'### `{stufe}` ({len(treffer)}): {was}\n')
        if not treffer:
            aus.append('Derzeit keins.\n')
            continue
        aus.append(tabelle(treffer))
        aus.append('')

    return '\n'.join(aus).rstrip() + '\n'


def ersetze(body, block):
    """Den Bereich zwischen den Markern austauschen.

    Die Reihenfolgepruefung ist kein Formalismus: steht END vor BEGIN, ist
    `partition(END)` hinter BEGIN leer, und der gesamte handgepflegte Fuss
    faellt stillschweigend weg. `--check` wuerde in diesem Zustand Drift
    melden und zu genau dem `--apply` auffordern, das den Verlust schreibt.
    Deshalb hier Exit 2 statt einer Reparatur auf Verdacht.
    """
    if BEGIN not in body or END not in body:
        abbruch(f'In #{MATRIX_ISSUE} fehlen die Marker. Erwartet wird eine '
                f'Zeile "{BEGIN}" und spaeter "{END}".')
    if body.index(BEGIN) > body.index(END):
        abbruch(f'In #{MATRIX_ISSUE} steht der END-Marker vor dem '
                f'BEGIN-Marker. In dieser Reihenfolge wuerde der Text nach '
                f'BEGIN verloren gehen; bitte die Marker im Body ordnen.')
    kopf, _, rest = body.partition(BEGIN)
    _, _, fuss = rest.partition(END)
    return f'{kopf}{BEGIN}\n\n{block}\n{END}{fuss}'


def hole_body():
    return json.loads(gh(['issue', 'view', str(MATRIX_ISSUE),
                          '--json', 'body']))['body']


def selftest():
    """Zaehlung, Sortierung, Pruefung und Marker-Ersatz an erfundenen Daten."""
    def iss(nr, labels, titel='T', datum='2026-08-01', kommentare=None):
        # kommentare: Liste aus 'JJJJ-MM-TT' oder ('JJJJ-MM-TT', 'login')
        def komm(k):
            datum_, konto = (k, 'chsteiner') if isinstance(k, str) else k
            return {'createdAt': datum_ + 'T00:00:00Z',
                    'author': {'login': konto}}
        roh = {'number': nr, 'title': titel, 'labels': sorted(labels),
               'createdAt': datum + 'T00:00:00Z',
               'comments': [komm(k) for k in (kommentare or [])]}
        roh['still_seit'] = letzte_wortmeldung(roh)
        return roh

    faelle = []

    sauber = [
        iss(1, ['auto:full', 'area:docs', 'effort:small']),
        iss(2, ['auto:blocked', 'area:data', 'effort:large', 'wait:kzw', 'ingest']),
        iss(44, ['evergreen', 'area:docs']),
    ]
    faelle.append(('Sauberer Satz erzeugt keine Meldung', pruefe(sauber) == []))
    faelle.append(('Evergreen ist von der Achsenpflicht ausgenommen',
                   not any('#44' in f for f in pruefe(sauber))))

    block = baue(sauber)
    faelle.append(('Der Evergreen faellt aus der Gesamtzahl',
                   '**2 offene Issues**' in block))
    faelle.append(('ingest-Flag steht in der Zeile', '`ingest`' in block))
    faelle.append(('Leere Stufe wird benannt statt weggelassen',
                   '`auto:pair` (0)' in block and 'Derzeit keins.' in block))
    faelle.append(('Ping-Liste nennt Person und Datum',
                   'KZW (`wachauer`)' in block and '#2 (2026-08-01)' in block))

    # Der teuerste Fehlermodus dieser Liste: eigenes Nachfassen sieht aus
    # wie Bewegung. Gemessen werden muss das Schweigen der erwarteten
    # Person, nicht die Betriebsamkeit im Ticket.
    nachgefasst = iss(50, ['auto:blocked', 'area:data', 'effort:small',
                           'wait:kzw'], datum='2026-01-01',
                      kommentare=[('2026-06-01', 'wachauer'),
                                  ('2026-08-05', 'chsteiner')])
    ping = baue([nachgefasst])
    faelle.append(('Eigenes Nachfassen setzt die Ping-Uhr nicht zurueck',
                   '#50 (2026-06-01)' in ping and '#50 (2026-08-05)' not in ping))
    faelle.append(('In der Tabelle steht weiter die letzte Wortmeldung',
                   '| 2026-08-05 |' in ping))

    # Wer nie geantwortet hat, wartet seit dem Anlegen und nicht seit dem
    # letzten Zuruf.
    nie = iss(51, ['auto:blocked', 'area:data', 'effort:small', 'wait:julia'],
              datum='2026-02-02', kommentare=[('2026-08-05', 'chsteiner')])
    faelle.append(('Ohne Antwort zaehlt das Anlegedatum',
                   '#51 (2026-02-02)' in baue([nie])))

    # Bei Externen gibt es kein Konto zu filtern, also faellt unsere eigene
    # Seite heraus. Das eigene Nachfassen darf die Uhr auch hier nicht stellen.
    extern = iss(52, ['auto:blocked', 'area:data', 'effort:small',
                      'wait:extern'], datum='2026-01-01',
                 kommentare=[('2026-05-16', 'wachauer'),
                             ('2026-08-05', 'chsteiner')])
    faelle.append(('Bei Externen zaehlt der letzte Kommentar von aussen',
                   '#52 (2026-05-16)' in baue([extern])))
    # gh liefert Bot-Logins nackt, REST mit Suffix: beide muessen treffen.
    for nr, login in ((53, 'claude'), (54, 'claude[bot]')):
        stumm = iss(nr, ['auto:blocked', 'area:data', 'effort:small',
                         'wait:extern'], datum='2026-03-03',
                    kommentare=[('2026-08-05', login)])
        faelle.append((f'Bot-Kommentar als "{login}" zaehlt nicht als '
                       f'Antwort von aussen',
                       f'#{nr} (2026-03-03)' in baue([stumm])))

    # WAIT_NAMEN und WAIT_KONTEN kodieren dieselbe Personenliste zweimal.
    # Ein neuer Eintrag ohne Konto faellt stumm auf die Extern-Regel zurueck,
    # womit jeder fremde Kommentar als Antwort der erwarteten Person zaehlt.
    faelle.append(('Jede benannte Person hat ein Konto, nur Externe nicht',
                   set(WAIT_NAMEN) - set(WAIT_KONTEN) == {'wait:extern'}))
    faelle.append(('Ohne Luecke kein Luecken-Kasten',
                   'Label-Luecke(n)' not in block))

    # Keine der vier Luecken-Arten darf sich still auf die Matrix auswirken.
    # Alle drei unten verzerren sie auf verschiedene Weise, und alle drei
    # muessen im Body stehen und nicht nur im Actions-Log.
    ohne = baue(sauber + [iss(99, ['area:docs', 'effort:small'])])
    faelle.append(('Ticket ohne auto:* wird im Block benannt',
                   '#99: Autonomiestufe' in ohne))
    faelle.append(('Die Kopfzahl zaehlt das ungelabelte Ticket weiter mit',
                   '**3 offene Issues**' in ohne))

    doppelt = baue(sauber + [iss(98, ['auto:full', 'auto:blocked', 'area:docs',
                                      'effort:small', 'wait:kzw'])])
    faelle.append(('Zwei auto:*, das Ticket steht in zwei Tabellen und der '
                   'Block sagt es', '#98: Autonomiestufe' in doppelt
                   and doppelt.count('| #98 |') == 2))

    stumm = baue(sauber + [iss(97, ['auto:blocked', 'area:docs',
                                    'effort:small'])])
    faelle.append(('auto:blocked ohne wait:* wird benannt, statt aus der '
                   'Ping-Liste zu fallen', '#97: auto:blocked ohne wait' in stumm
                   and '| #97 |' in stumm))

    # Die vier Fehlermodi, die dieses Gate rechtfertigen.
    faelle.append(('Fehlendes auto:* faellt auf', any(
        'Autonomiestufe' in f for f in
        pruefe([iss(5, ['area:docs', 'effort:small'])]))))
    faelle.append(('Zwei effort-Labels fallen auf', any(
        'Aufwand' in f for f in
        pruefe([iss(6, ['auto:full', 'area:docs', 'effort:small', 'effort:large'])]))))
    faelle.append(('auto:blocked ohne wait faellt auf', any(
        'ohne wait' in f for f in
        pruefe([iss(7, ['auto:blocked', 'area:data', 'effort:small'])]))))
    faelle.append(('wait ohne auto:blocked faellt auf', any(
        'ohne auto:blocked' in f for f in
        pruefe([iss(8, ['auto:full', 'area:data', 'effort:small', 'wait:kzw'])]))))
    faelle.append(('Unbekanntes wait-Label faellt auf', any(
        'unbekanntes wait-Label' in f for f in
        pruefe([iss(9, ['auto:blocked', 'area:data', 'effort:small', 'wait:bob'])]))))

    # Sortierung: klein vor gross, bei Gleichstand nach Nummer.
    gemischt = [iss(30, ['auto:full', 'area:docs', 'effort:large']),
                iss(20, ['auto:full', 'area:docs', 'effort:small']),
                iss(10, ['auto:full', 'area:docs', 'effort:large'])]
    reihenfolge = [z.split('|')[1].strip() for z in
                   tabelle(gemischt).split('\n')[2:]]
    faelle.append(('Kleinster Brocken zuerst, dann nach Nummer',
                   reihenfolge == ['#20', '#10', '#30']))

    # Ein Pipe im Titel darf die Tabelle nicht sprengen.
    roh = zeile(iss(11, ['auto:full', 'area:docs', 'effort:small'], 'a|b'))
    faelle.append(('Pipe im Titel wird maskiert', 'a\\|b' in roh))

    # TEI-Elemente stehen in diesem Projekt regelmaessig in Ticket-Titeln:
    # ohne Maskierung frisst GitHubs Sanitizer sie aus der Anzeige.
    tei = zeile(iss(13, ['auto:full', 'area:data', 'effort:small'],
                    'Luecken als <gap/> statt <caesura/>'))
    faelle.append(('Spitze Klammern bleiben sichtbar',
                   '&lt;gap/&gt;' in tei and '<gap/>' not in tei))
    amp = zeile(iss(14, ['auto:full', 'area:docs', 'effort:small'], 'A &amp; B'))
    faelle.append(('Kaufmanns-Und wird vor den Klammern maskiert',
                   '&amp;amp;' in amp))
    umbruch = zeile(iss(15, ['auto:full', 'area:docs', 'effort:small'], 'a\nb'))
    faelle.append(('Zeilenumbruch spaltet die Tabellenzeile nicht',
                   umbruch.count('\n') == 0 and 'a b' in umbruch))

    # Die Kuerzung zaehlt sichtbare Zeichen, nicht Entities: ein Titel aus
    # 78 spitzen Klammern darf nicht auf sieben angezeigte schrumpfen.
    lang = zeile(iss(16, ['auto:full', 'area:docs', 'effort:small'], '<' * 90))
    faelle.append(('Gekuerzt wird vor dem Maskieren',
                   lang.count('&lt;') == 77))

    # Marker-Ersatz: Handschrift ausserhalb bleibt, innen wird ersetzt.
    body = f'oben\n{BEGIN}\nALT\n{END}\nunten'
    neu = ersetze(body, 'NEU\n')
    faelle.append(('Ersatz haelt Kopf und Fuss', neu.startswith('oben')
                   and neu.endswith('unten') and 'ALT' not in neu
                   and 'NEU' in neu))
    faelle.append(('Ersatz ist idempotent',
                   ersetze(neu, 'NEU\n') == neu))

    # Die drei Wege, auf denen der handgepflegte Teil verloren gehen koennte.
    # Alle drei muessen mit Exit 2 enden und nicht mit einem stillen Ergebnis.
    def steigt_mit_2_aus(text):
        # stderr stumm: die ::error-Zeilen gehoeren zum erwarteten Verhalten
        # und saehen im Testlauf wie echte Fehler aus.
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                ersetze(text, 'NEU\n')
        except SystemExit as exc:
            return exc.code == 2
        return False

    faelle.append(('END vor BEGIN steigt aus, statt den Fuss zu schlucken',
                   steigt_mit_2_aus(f'{END}\n{BEGIN}\nhandschrift danach')))
    faelle.append(('Fehlender BEGIN-Marker steigt aus',
                   steigt_mit_2_aus(f'oben\n{END}\nunten')))
    faelle.append(('Fehlender END-Marker steigt aus',
                   steigt_mit_2_aus(f'oben\n{BEGIN}\nunten')))

    # Ein Titel mit Marker-String waere sonst kumulativ zerstoererisch.
    giftig = iss(12, ['auto:full', 'area:docs', 'effort:small'],
                 f'Bug in {END} beim Rendern')
    einmal = ersetze(f'oben\n{BEGIN}\nALT\n{END}\nunten', tabelle([giftig]) + '\n')
    zweimal = ersetze(einmal, tabelle([giftig]) + '\n')
    faelle.append(('Marker im Issue-Titel laesst den Body nicht wachsen',
                   einmal.count(END) == 1 and zweimal.count(END) == 1
                   and zweimal.endswith('unten')))

    schlecht = [name for name, ok in faelle if not ok]
    for name, ok in faelle:
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}")
    if schlecht:
        print(f'\nSelbsttest fehlgeschlagen: {len(schlecht)} von {len(faelle)}',
              file=sys.stderr)
        return 1
    print(f'\nSelbsttest bestanden: {len(faelle)} Faelle')
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--apply', action='store_true',
                   help=f'den Body von #{MATRIX_ISSUE} schreiben')
    p.add_argument('--check', action='store_true',
                   help='nur pruefen, ob der Body dem Label-Stand entspricht')
    p.add_argument('--selftest', action='store_true',
                   help='ohne Netz an erfundenen Daten pruefen')
    args = p.parse_args()

    if args.selftest:
        return selftest()

    issues = hole_issues()
    if not issues:
        print('::error::gh lieferte keine offenen Issues.', file=sys.stderr)
        return 2

    fehler = pruefe(issues)
    for f in fehler:
        print(f'::error title=Label-Luecke::{f}', file=sys.stderr)

    # Beide Ausfaelle dieser Pruefung sind Warnungen und duerfen den Hauptzweck
    # nicht abbrechen: das Schreiben des Bodys haengt an den OFFENEN Issues und
    # ist von der ROADMAP unabhaengig. SystemExit faengt den Saettigungs-Abbruch
    # aus issue_liste(), der sonst vor baue() greifen wuerde, obwohl er nur die
    # geschlossenen betrifft (CI-Review-Bot, PR #396).
    try:
        roadmap_treffer = pruefe_roadmap(hole_geschlossene())
    except FileNotFoundError:
        roadmap_treffer = []
        print(f'::warning::{ROADMAP} ist im Arbeitsverzeichnis nicht '
              f'vorhanden, die ROADMAP-Pruefung ist ausgefallen. Im Workflow '
              f'gehoert die Datei in die sparse-checkout-Liste.',
              file=sys.stderr)
    except SystemExit:
        roadmap_treffer = []
        print('::warning::Die Liste der geschlossenen Issues ist an ihrem '
              'Limit angekommen, die ROADMAP-Pruefung ist ausgefallen. Limit '
              'in hole_geschlossene() erhoehen. Der Body wird trotzdem '
              'geschrieben.', file=sys.stderr)

    for zeile_nr, nr in roadmap_treffer:
        print(f'::warning file={ROADMAP},line={zeile_nr}::#{nr} steht in '
              f'{ROADMAP} als Eintrag, ist aber nicht mehr offen. Zeile '
              f'streichen oder mit dem neuen Stand weiterfuehren.',
              file=sys.stderr)

    block = baue(issues)

    if args.check:
        aktuell = hole_body()
        neu = ersetze(aktuell, block)
        if aktuell.strip() != neu.strip():
            print(f'::error::Der Body von #{MATRIX_ISSUE} ist nicht auf dem '
                  f'Label-Stand. Beheben mit: python '
                  f'scripts/audit/build-issue-matrix.py --apply',
                  file=sys.stderr)
            return 1
        if fehler:
            return 1
        zaehlbar = sum(1 for i in issues if 'evergreen' not in i['labels'])
        print(f'#{MATRIX_ISSUE} ist auf dem Label-Stand, '
              f'{zaehlbar} Issues gelistet, {len(issues)} geprueft.')
        return 0

    if args.apply:
        neu = ersetze(hole_body(), block)
        gh(['issue', 'edit', str(MATRIX_ISSUE), '--body', neu])
        zaehlbar = sum(1 for i in issues if 'evergreen' not in i['labels'])
        print(f'#{MATRIX_ISSUE} aktualisiert: {zaehlbar} Issues gelistet, '
              f'{len(issues)} geprueft.')
        return 1 if fehler else 0

    print(block)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
