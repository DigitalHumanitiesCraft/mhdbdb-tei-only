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
ganz oben zwischen `PERSONEN` die Listen je Person; zwischen `MATRIX` Quick
Stats, Verteilung nach Bereich, "Wer ist am Zug" (bei uns, Frage fehlt, die
Zeile fuer Externe) und je eine Tabelle pro Autonomiestufe.

Von Hand bleibt alles ausserhalb der Marker: die Legende des Schemas, die
Arbeitsregeln und die Befundliste. Das ist Urteil und keine Zaehlung.

## Das Label-Schema, gegen das geprueft wird

Drei Achsen mit genau einem Label je Achse und Ticket:

    auto:full | auto:brief | auto:checkin | auto:pair | auto:blocked
              | auto:frozen
    area:data | area:frontend | area:playground | area:pipeline
              | area:docs | area:orga
    effort:small | effort:medium | effort:large

Dazu die Flags `ingest` und `evergreen` sowie, nur an `auto:blocked`, ein oder
mehrere `wait:*` (kzw, julia, linda, extern). Mehrere sind erlaubt und
richtig: #315 wartet auf KZW *und* Julia.

`auto:frozen` ist am 21.09.2026 dazugekommen und trennt zwei Zustaende, die
vorher beide `auto:blocked` hiessen: "wartet auf eine Antwort" und "wartet
auf einen Termin". Der Anlass ist #271, bis Juni 2027 stillgelegt nach einer
Entscheidung von KZW vom 10.09. (Vorschlag 15:24, Jahreszahl bestaetigt
16:41; ihr Kommentar vom 11.09. betrifft die NEIM-Konkordanz und nicht das
Einfrieren). Weil das Schema keinen Wert dafuer hatte,
trug der Vorgang weiter `wait:kzw` und stand taeglich in ihrer Ping-Liste,
obwohl sie geantwortet hatte. Das war im Vorgang selbst vermerkt, statt es zu
beheben, und wurde am 17.09. in #406 zu Recht geruegt. Ein eingefrorener
Vorgang traegt deshalb **kein** `wait:*`: niemand schuldet etwas, und die
Listen je Person bleiben Listen der Schulden.

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

Umgekehrt gilt: `auto:blocked` ohne `wait:*` macht die Listen je Person
unvollstaendig, und ein `wait:*` an einem nicht blockierten Ticket macht sie
falsch. Beides ist ein Fehler und kein Hinweis.

## MESSVORSCHRIFT: zwei Daten, die verschiedene Fragen beantworten

**In den Tabellen** steht die letzte Wortmeldung im Ticket, gleich von wem,
ersatzweise das Anlegedatum. Nicht `updatedAt`, obwohl das billiger zu holen
waere: dieses Feld springt bei jeder Label-Aenderung auf heute. Beim Aufbau
des Schemas am 05.08. standen dadurch schlagartig alle 52 Tickets auf
demselben Datum, und die Sortierung "aeltestes zuerst" war wertlos.

**In der Ping-Liste** stand bis zum 09.10.2026 das Datum der letzten
Wortmeldung **der erwarteten Person**; seither gibt es sie nur noch fuer
Externe, fuer die Personen gilt "wer ist am Zug" (unten). Die Frage dort lautet "wie lange schweigt KZW zu
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

## MESSVORSCHRIFT: wer ist am Zug

Seit dem 09.10.2026 steht ganz oben in #44, zwischen eigenen Markern
(`PERSONEN`), je eine Liste fuer Katharina, Julia und Linda: nur das, was
gerade bei ihnen liegt. Anlass ist die Ruege von KZW vom 17.09. in #406:
"Bereits beantwortete Fragen duerfen nicht erneut als Entscheidungsrueckstand
bei mir erscheinen", und dazu "benenne die konkrete unbeantwortete Frage".
Die Labels koennen das nicht leisten: sie werden von Hand gepflegt, und wenn
KZW antwortet, bleibt `wait:kzw` stehen.

Darum wird nicht gespeichert, wer am Zug ist, sondern gerechnet, je Vorgang
und je `wait:<person>`:

- Eine **Frage an sie** ist ein Kommentar von uns (`WIR`), dessen erste
  Zeile mit `Frage:` oder `Abnahme:` beginnt (fett oder nicht, auch nach
  fuehrenden @-Erwaehnungen), oder der eine Zeile `@<konto> Frage:` traegt.
  Eine erste Zeile, die nur an andere adressiert ist, fragt sie nicht.
- **Ball bei uns**, wenn der letzte Kommentar der Person juenger ist als
  unsere letzte Frage an sie. Bots zaehlen auf keiner Seite, und unsere
  Statusmeldungen ohne Anfangswort zaehlen nicht: sonst schaltete ein
  "Label korrigiert" nach ihrer Antwort die Frist ab.
  Das gilt auch, wenn wir sie nie gefragt haben und sie irgendwann
  geschrieben hat.
- Sonst liegt der Ball bei der Person, und unsere letzte Frage sagt, was
  sie tun soll. Gibt es keine und hat sie nie geschrieben, steht der
  Vorgang bei uns unter "Frage fehlt" und in keiner Personenliste.

Das Anfangswort ist gemessen und nicht Geschmack: am 09.10. lagen nach der
reinen Regel "wer zuletzt schrieb" 47 der 51 `wait:kzw` bei KZW, aber unser
letzter Kommentar war dort meist eine Statusmeldung ("Umgesetzt in PR 553",
"Label korrigiert", "Stand 06.09.") und keine Frage; vier Vorgaenge hatten
gar keinen. Ihre Liste waere wieder voll von Dingen gewesen, die sie nichts
fragen. Ein zweiter Hinweis auf Abnahmen, ein gemergter PR mit Verweis auf
den Vorgang, schlug bei 35 von 51 an und ist deshalb nicht drin; geblieben
ist nur der Live-Link (`LIVE`), als Hinweis "vermutlich Abnahme".

Eine Abnahme, die Julia und KZW zugleich meint, steht nur in Julias Liste:
einfache Abnahmen gehen seit dem 09.10. zuerst an Julia (KZW in #378). Eine
offene Frage an KZW und eine nur an KZW gerichtete Abnahme bleiben davon
unberuehrt. Hat KZW geantwortet, zaehlt jede juengere Abnahme an Julia als
unsere Reaktion; schreibt KZW danach noch einmal, liegt es bei uns. Der
Vorrang gilt nur fuer KZW und vergleicht Zeilen, nicht Kommentare: eine
eigene Zeile `@wachauer Abnahme:` neben einer an Julia bleibt bei KZW. Der
Selbsttest prueft ueber seine Lebenslauf-Faelle, unabhaengig von dieser
Regel, dass keine offene Frage an KZW unsichtbar wird.

Liegt etwas laenger als `FRIST_TAGE` bei uns, wird der Lauf rot wie bei
einer Label-Luecke, und der Body sagt es. Abstellen laesst sich das nur mit
einer neuen Frage an sie oder mit anderen Labels.

Usage:
    python scripts/audit/build-issue-matrix.py             # Vorschau auf stdout
    python scripts/audit/build-issue-matrix.py --apply     # #44 aktualisieren
    python scripts/audit/build-issue-matrix.py --check     # Gate: Drift = rot
    python scripts/audit/build-issue-matrix.py --selftest  # ohne Netz pruefen

Exit codes:
    0 = alles konsistent (bei --check zusaetzlich: Body ist aktuell)
    1 = Label-Luecke, Ball laenger als FRIST_TAGE bei uns, oder bei --check
        ein veralteter Body
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
from datetime import date, timedelta
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

MATRIX_ISSUE = 44
BEGIN = '<!-- MATRIX:BEGIN (generiert von scripts/audit/build-issue-matrix.py, nicht von Hand aendern) -->'
END = '<!-- MATRIX:END -->'
# Zweites Markerpaar ganz oben im Body: die Listen fuer Menschen. Eigene
# Marker, damit der handgepflegte Text dazwischen (Legende, Schema) bleibt.
PBEGIN = '<!-- PERSONEN:BEGIN (generiert von scripts/audit/build-issue-matrix.py, nicht von Hand aendern) -->'
PEND = '<!-- PERSONEN:END -->'

# Reihenfolge ist Absicht: von "sofort machbar" nach "wartet auf einen
# Menschen". Wer die Matrix liest, um Arbeit zu finden, liest von oben.
AUTO_STUFEN = [
    ('auto:full', 'sofort machbar, keine offene Frage'),
    ('auto:brief', 'kurze Klaerung vorab, dann am Stueck durchziehbar'),
    ('auto:checkin', 'semiautonom, Zwischenentscheidungen unterwegs'),
    ('auto:pair', 'nur gemeinsam mit Chris in einer Session'),
    ('auto:blocked', 'wartet auf einen Menschen, nicht auf Arbeit'),
    ('auto:frozen', 'bewusst stillgelegt bis zu einem Termin, wartet auf '
                    'niemanden'),
]

# `auto:frozen` steht bewusst unter `auto:blocked` und nicht daneben: es ist
# die einzige Stufe, bei der niemand etwas schuldet. Wer die Matrix von oben
# nach Arbeit liest, hat hier nichts mehr zu holen.
FROZEN = 'auto:frozen'
AREAS = ['area:data', 'area:frontend', 'area:playground', 'area:pipeline',
         'area:docs', 'area:orga']
EFFORTS = ['effort:small', 'effort:medium', 'effort:large']
# Sortierschluessel innerhalb einer Stufe: der kleinste Brocken zuerst.
EFFORT_RANG = {e: i for i, e in enumerate(EFFORTS)}

# Die drei Achsen mit ihrem erlaubten Vokabular. Die Anzahl allein genuegt
# nicht: ein Label, das dem Praefix folgt und dem Skript unbekannt ist, zaehlt
# als "genau eins" und faellt aus jeder Zaehlung, die ueber die Konstanten
# oben laeuft, waehrend der Tageslauf gruen bleibt.
#
# Was das heisst, ist je Achse verschieden, gemessen am erzeugten Block und
# als Selbsttest festgehalten: ein fremdes `auto:` erscheint in keiner
# Tabelle, weil die Tabellen nach Autonomiestufe gebildet werden. Ein fremdes
# `area:` oder `effort:` bekommt dagegen seine Zeile und zeigt den Rohwert in
# der Zelle, weil zeile() den ersten Treffer ungefiltert nimmt. Die Kopfzahl
# zaehlt das Ticket in allen drei Faellen weiter mit.
#
# Der erste Fall waere beim Einfuehren von `auto:frozen` eingetreten, haette
# jemand das Label auf GitHub vor diesem Skript angelegt.
ACHSEN = [
    ('auto:', 'Autonomiestufe', [n for n, _ in AUTO_STUFEN]),
    ('area:', 'Bereich', AREAS),
    ('effort:', 'Aufwand', EFFORTS),
]

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

# Wer "wir" ist, wenn es darum geht, wer am Zug ist: nur das Konto, unter dem
# Christian und alle Sessions schreiben. Die Bots aus UNSERE_SEITE fehlen
# absichtlich: ein Review-Kommentar stellt keine Frage und beantwortet keine.
WIR = ('chsteiner',)
# Wie die Personen in den Listen oben heissen. Die Reihenfolge ist die der
# Abschnitte im Body.
PERSONEN = {
    'wait:kzw': 'Katharina',
    'wait:julia': 'Julia',
    'wait:linda': 'Linda',
}
# Personen, deren Abschnitt auch leer erscheint. Linda erscheint nur, wenn
# etwas bei ihr liegt.
IMMER_SICHTBAR = ('wait:kzw', 'wait:julia')
ANFANG = re.compile(r'(?:@[\w-]+[\s,:]*)*(?:\*\*)?(Frage|Abnahme):')
LIVE = 'dhcraft.org/mhdbdb-tei-only'
FRIST_TAGE = 7


def abbruch(meldung):
    """Mit Exit 2 aussteigen: Werkzeug- oder Datenfehler, keine Label-Luecke.

    Nicht `sys.exit(<string>)`: das liefert Exit-Code 1 und ist damit von
    einer Label-Luecke nicht mehr zu unterscheiden. Der Unterschied traegt
    die Aussage des Workflows: rot mit 1 heisst "Body geschrieben, aber ein
    Ticket ist unvollstaendig gelabelt", rot mit 2 heisst "nichts passiert".
    """
    print(f'::error::{meldung}', file=sys.stderr)
    sys.exit(2)


class ListeGesaettigt(RuntimeError):
    """Eine Issue-Liste hat ihr Limit ausgeschoepft und ist moeglicherweise
    abgeschnitten.

    Eigene Ausnahme und kein abbruch(), weil der Aufrufer entscheiden muss:
    bei den OFFENEN Issues ist eine abgeschnittene Liste ein Abbruchgrund,
    der Body haengt an ihnen. Bei den geschlossenen betrifft sie nur die
    ROADMAP-Pruefung, und die ist ausdruecklich Warnung und kein Fehler.

    Der Umweg ueber abbruch() hat genau diese Unterscheidung gekostet: er
    endet in sys.exit(2), und gh() tut das bei einem Rate Limit oder einem
    abgelaufenen Token auch. Ein `except SystemExit` haette den einen Fall
    nicht vom anderen trennen koennen und einen echten gh-Ausfall als
    "Limit erhoehen" gemeldet, bei gruenem Job (CI-Review-Bot, PR #396).
    """


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
        raise ListeGesaettigt(
            f'gh issue list --state {state} hat das Limit von {limit} '
            f'ausgeschoepft ({len(roh)} Eintraege). Die Liste ist '
            f'moeglicherweise abgeschnitten, und jede Auswertung darauf '
            f'waere still unvollstaendig. Limit in issue_liste() erhoehen.')
    return roh


def hole_issues():
    # Hier bleibt die Saettigung ein Abbruch: der Body von #44 wird aus diesen
    # Issues gebaut, und eine abgeschnittene Liste hiesse ein stiller
    # Teil-Body. Bei den geschlossenen entscheidet main() anders, siehe dort.
    try:
        roh = issue_liste('open', 'number,title,labels,createdAt,comments', 300)
    except ListeGesaettigt as exc:
        abbruch(str(exc))
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


def letzte_wortmeldung(issue, ausser=None):
    """Datum des letzten Kommentars, ersatzweise das Anlegedatum.

    Mit `ausser` zaehlen alle Kommentare ausser denen der genannten Logins:
    die Zeile fuer Externe braucht das ("wann kam zuletzt etwas von
    aussen"), die Tabellen nicht ("wann hat hier zuletzt jemand
    geschrieben").

    Warum das nicht dasselbe ist und was die Verwechslung gekostet hat:
    Messvorschrift im Modul-Docstring. Sie steht dort und nur dort, damit
    das gemessene Datum darin nicht an zwei Stellen wahr gehalten werden
    muss.
    """
    kommentare = issue.get('comments') or []
    if ausser:
        kommentare = [k for k in kommentare if konto_von(k) not in ausser]
    if kommentare:
        return max(k['createdAt'] for k in kommentare)[:10]
    return issue['createdAt'][:10]


def achse(issue, praefix):
    """Alle Labels eines Praefix an diesem Issue."""
    return [l for l in issue['labels'] if l.startswith(praefix)]


def letzter_kommentar(issue, konten):
    """Der juengste Kommentar eines der genannten Konten, sonst None."""
    treffer = [k for k in issue.get('comments') or [] if konto_von(k) in konten]
    return max(treffer, key=lambda k: k['createdAt']) if treffer else None


def erste_zeile(kommentar, konto=None):
    """Die Zeile, die fuer diese Person zaehlt.

    Gibt es eine Zeile, die mit `@konto` und einem Anfangswort beginnt, ist es
    diese: so traegt ein Kommentar an zwei Personen zwei verschiedene Fragen
    (#526, 09.10.: Grundsatzfrage an KZW, Pruefseite an Julia). Sonst die
    erste nicht leere Zeile, ausser sie ist an jemand anderen adressiert: dann
    ist es keine Frage an diese Person, sonst stuende eine `@juliahin Frage:`
    auch in Katharinas Liste (Opus-Review 09.10., die Fehlerklasse aus #406).
    """
    zeilen = [z.strip() for z in (kommentar.get('body') or '').splitlines()
              if z.strip()]
    erste = zeilen[0] if zeilen else ''
    if konto:
        for z in zeilen:
            if (z.startswith(f'@{konto} ') or z.startswith(f'@{konto},')) \
                    and ANFANG.match(z):
                return z
        an = re.match(r'(?:@[\w-]+[\s,:]*)+', erste)
        if an and f'@{konto}' not in re.findall(r'@[\w-]+', an.group(0)):
            return ''
    return erste


def art(kommentar, konto=None):
    """'frage', 'abnahme' oder 'ohne': was unser letzter Kommentar verlangt.

    Nur der Zeilenanfang zaehlt. "Das ist noch keine Abnahme: ..." mitten im
    Satz darf nicht treffen, sonst passiert hier, was GitHub mit "Kein
    Closes: #235" gemacht hat (CLAUDE.md, Git Rules).
    """
    if not kommentar:
        return 'ohne'
    m = ANFANG.match(erste_zeile(kommentar, konto))
    return m.group(1).lower() if m else 'ohne'


def letzte_frage(issue, konto):
    """Unser juengster Kommentar, der `konto` etwas fragt, sonst None.

    Statusmeldungen ohne Anfangswort zaehlen nicht: sie legen den Ball
    weder zu ihr noch nehmen sie ihn uns ab.
    """
    unsere = [k for k in issue.get('comments') or [] if konto_von(k) in WIR]
    for k in sorted(unsere, key=lambda k: k['createdAt'], reverse=True):
        if art(k, konto) != 'ohne':
            return k
    return None


def frage_text(kommentar, konto=None):
    """Die Zeile nach dem Anfangswort bis zum ersten Fragezeichen.

    Nicht bis zum ersten Punkt: "z. B.", "1,85 Mio." und "29.07." schnitten
    am 09.10. vier von 46 Fragen vor dem Fragezeichen ab, eine davon ganz.
    """
    text = ANFANG.sub('', erste_zeile(kommentar, konto), count=1)
    text = re.sub(r'[*_`#>]', '', text)
    text = ' '.join(text.split())
    text = text.split('?', 1)[0] + '?' if '?' in text else text
    if len(text) > 140:
        text = text[:139] + '…'
    # Eckige Klammern wuerden den Linktext beenden, in dem der Satz steht.
    return entschaerfe(text).replace('[', '(').replace(']', ')') or '(ohne Text)'


def einordnen(issues):
    """Jeden Vorgang mit wait:<person> einer Stelle zuordnen.

    Liefert ein dict: 'person' -> {wait: {'abnahme': [...], 'frage': [...]}},
    'bei_uns' -> [(issue, wait, ihr_kommentar)], 'fehlt' -> [(issue, wait,
    unser_letzter_kommentar_oder_None)]. Die Listen der Personen tragen
    (issue, unser_kommentar). Messvorschrift im Modul-Docstring.
    """
    person = {w: {'abnahme': [], 'frage': []} for w in PERSONEN}
    bei_uns, fehlt = [], []

    for i in issues:
        if 'evergreen' in i['labels']:
            continue
        for wait in PERSONEN:
            if wait not in i['labels']:
                continue
            konto = WAIT_KONTEN[wait]
            ihr = letzter_kommentar(i, (konto,))
            # Gemessen wird gegen unsere letzte *Frage* an sie, nicht gegen
            # unseren letzten Kommentar: sonst schaltet ein Statuskommentar
            # nach ihrer Antwort die Frist ab, und der Vorgang steht auf keiner
            # Liste mehr (Opus-Review 09.10., #397).
            unser = letzte_frage(i, konto)
            if ihr and (not unser or ihr['createdAt'] > unser['createdAt']):
                stelle = 'bei_uns'
            elif not unser:
                stelle = 'fehlt'
            else:
                stelle = art(unser, konto)
            # Julia zuerst (KZW in #378, 09.10.), nur fuer KZW. Gibt es eine
            # Abnahme von uns an Julia, wird KZW uebersprungen, wenn
            # - wir KZW nie gefragt haben und sie nie geschrieben hat,
            # - unsere letzte Abnahme an KZW dieselbe Zeile ist wie die an
            #   Julia (eine eigene Zeile oder ein eigener Kommentar nur an
            #   KZW bleibt bei ihr: komplexe Abnahmen, Runden 4 und 5),
            # - oder der Ball nach KZWs Antwort bei uns laege und eine
            #   juengere Abnahme an Julia unsere Reaktion ist (Frage an KZW,
            #   sie antwortet, wir setzen um, Abnahme an Julia mit cc).
            # Eine offene Frage an KZW wird nie uebersprungen.
            if wait == 'wait:kzw' and 'wait:julia' in i['labels']:
                julia = WAIT_KONTEN['wait:julia']
                abnahmen = [k['createdAt'] for k in i.get('comments') or []
                            if konto_von(k) in WIR
                            and art(k, julia) == 'abnahme']
                if abnahmen and (
                        stelle == 'fehlt'
                        or (stelle == 'abnahme' and art(unser, julia) ==
                            'abnahme' and erste_zeile(unser, konto) ==
                            erste_zeile(unser, julia))
                        or (stelle == 'bei_uns'
                            and max(abnahmen) > ihr['createdAt'])):
                    continue
            if stelle == 'bei_uns':
                bei_uns.append((i, wait, ihr))
            elif stelle == 'fehlt':
                fehlt.append((i, wait, letzter_kommentar(i, WIR)))
            else:
                person[wait][stelle].append((i, unser))
    for wait in person:
        for liste in person[wait].values():
            liste.sort(key=lambda t: (t[1]['createdAt'], t[0]['number']))
    bei_uns.sort(key=lambda t: (t[2]['createdAt'], t[0]['number']))
    fehlt.sort(key=lambda t: t[0]['number'])
    return {'person': person, 'bei_uns': bei_uns, 'fehlt': fehlt}


def ueberfaellig(eingeordnet, heute):
    """Vorgaenge, die laenger als FRIST_TAGE bei uns liegen."""
    grenze = (heute - timedelta(days=FRIST_TAGE)).isoformat()
    return [(i, wait, k) for i, wait, k in eingeordnet['bei_uns']
            if k['createdAt'][:10] < grenze]


def kurztitel(issue, laenge=70):
    titel = issue['title']
    if len(titel) > laenge:
        titel = titel[:laenge - 1] + '…'
    return entschaerfe(titel)


def baue_personen(issues):
    """Der Block ganz oben in #44: was bei wem liegt, fuer Menschen lesbar."""
    eingeordnet = einordnen(issues)
    aus = ['## Wer ist gerade dran?\n',
           'Hier steht nur, was gerade bei dir liegt, mit der Frage selbst als '
           'Link. Hast du geantwortet, verschwindet der Punkt beim nächsten '
           'täglichen Lauf von selbst. Erzeugt von '
           '`scripts/audit/build-issue-matrix.py`.\n']
    for wait, name in PERSONEN.items():
        listen = eingeordnet['person'][wait]
        if wait not in IMMER_SICHTBAR and not any(listen.values()):
            continue
        aus.append(f'### Für {name}\n')
        # Ohne diese Zeile stuende bei leeren Listen "Derzeit nichts", obwohl
        # Vorgaenge auf die Person warten, deren Frage nur noch nicht in der
        # neuen Form gestellt ist. Am 09.10. waren das 47 bei Katharina.
        offen = sum(1 for _, w, _ in eingeordnet['fehlt'] if w == wait)
        if offen:
            aus.append(f'_Dazu kommen {offen} ältere Vorgänge, bei denen wir '
                       f'die Frage an dich noch nicht in dieser Form gestellt '
                       f'haben. Sie kommen nach und nach hierher; bis dahin '
                       f'musst du dort nichts tun._\n')
        for was, kopf in (('abnahme', 'Abnehmen'), ('frage', 'Entscheiden')):
            eintraege = listen[was]
            aus.append(f'**{kopf} ({len(eintraege)})**, älteste zuerst\n')
            if not eintraege:
                aus.append('Derzeit nichts.\n')
                continue
            for i, k in eintraege:
                aus.append(f'- [{frage_text(k, WAIT_KONTEN[wait])}]({k["url"]}) · '
                           f'#{i["number"]} {kurztitel(i)} · '
                           f'seit {k["createdAt"][:10]}')
            aus.append('')
    return '\n'.join(aus).rstrip() + '\n'


def pruefe(issues):
    """Label-Luecken finden. Liefert eine Liste von Klartext-Meldungen."""
    fehler = []
    for i in issues:
        nr = i['number']
        if 'evergreen' in i['labels']:
            # Die Matrix selbst wird gepflegt, nicht abgearbeitet.
            continue
        for praefix, name, erlaubt in ACHSEN:
            treffer = achse(i, praefix)
            if len(treffer) != 1:
                gefunden = ', '.join(treffer) if treffer else 'keins'
                fehler.append(f'#{nr}: {name} muss genau ein Label sein, '
                              f'gefunden: {gefunden}')
            fremd = [t for t in treffer if t not in erlaubt]
            if fremd:
                fehler.append(f'#{nr}: unbekanntes {name}-Label: '
                              f'{", ".join(fremd)}. Das Skript kennt nur '
                              f'{", ".join(erlaubt)}')
        wartet = achse(i, 'wait:')
        blockiert = 'auto:blocked' in i['labels']
        if blockiert and not wartet:
            fehler.append(f'#{nr}: auto:blocked ohne wait:*, steht deshalb '
                          f'unter "Wer ist am Zug" nirgends')
        if wartet and not blockiert:
            fehler.append(f'#{nr}: {", ".join(wartet)} an einem Ticket ohne '
                          f'auto:blocked')
        unbekannt = [w for w in wartet if w not in WAIT_NAMEN]
        if unbekannt:
            fehler.append(f'#{nr}: unbekanntes wait-Label: {", ".join(unbekannt)}')
    return fehler


ROADMAP = 'docs/ROADMAP.md'
# Gelesen wird an der Repo-Wurzel dieses Skripts, nicht am cwd (fehlerjournal.md
# 104). Im sparse Checkout von issue-matrix.yml ist das dieselbe Stelle wie vorher.
REPO = Path(__file__).resolve().parents[2]


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
    pfad = REPO / ROADMAP
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
    for marker in ('MATRIX:BEGIN', 'MATRIX:END', 'PERSONEN:BEGIN', 'PERSONEN:END'):
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


def baue(issues, heute=None):
    """Den generierten Block als Markdown. `heute` nur fuer den Selbsttest."""
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
    # fehlt unter "Wer ist am Zug", dessen Kopfzahl es mitzaehlt.
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
        eingeordnet = einordnen(zaehlbar)
        spaet = {(i['number'], wait) for i, wait, _ in
                 ueberfaellig(eingeordnet, heute or date.today())}
        if spaet:
            nummern = ', '.join(f'#{nr}' for nr, _ in sorted(spaet))
            aus.append(f'> **{len(spaet)} Wartesache(n) liegen laenger als '
                       f'{FRIST_TAGE} Tage bei uns:** {nummern}. Die Person '
                       f'hat geantwortet, und niemand hat reagiert.\n')
        aus.append('### Wer ist am Zug\n')
        aus.append(f'{len(blockierte)} Tickets warten auf einen Menschen. Was '
                   f'bei Katharina, Julia oder Linda liegt, steht ganz oben '
                   f'im Body; hier steht, was bei uns liegt. Messvorschrift '
                   f'im Docstring des Skripts.\n')
        bei_uns = eingeordnet['bei_uns']
        aus.append(f'**Ball bei uns ({len(bei_uns)})**: die Person hat nach '
                   f'unserer letzten Frage an sie geschrieben. Neu fragen, '
                   f'umlabeln oder schliessen; ein Statuskommentar allein '
                   f'nimmt den Vorgang nicht von hier.\n')
        for i, wait, k in bei_uns:
            frist = (f' **seit mehr als {FRIST_TAGE} Tagen**'
                     if (i['number'], wait) in spaet else '')
            aus.append(f'- #{i["number"]} {kurztitel(i)}: {PERSONEN[wait]} am '
                       f'{k["createdAt"][:10]} ([Antwort]({k["url"]})){frist}')
        if bei_uns:
            aus.append('')
        fehlt = eingeordnet['fehlt']
        aus.append(f'**Frage fehlt ({len(fehlt)})**: wartet auf eine Person, '
                   f'aber kein Kommentar von uns fragt sie mit `Frage:` oder '
                   f'`Abnahme:`. Steht deshalb in keiner Liste oben. '
                   f'Beheben mit einem Kommentar, der die Frage stellt, oder '
                   f'mit anderen Labels, wenn nichts mehr gebraucht wird.\n')
        for i, wait, k in fehlt:
            seit = k['createdAt'][:10] if k else 'keiner'
            hinweis = (', vermutlich Abnahme (Live-Link)'
                       if k and LIVE in (k.get('body') or '') else '')
            aus.append(f'- #{i["number"]} {kurztitel(i)} ({PERSONEN[wait]}), '
                       f'unser letzter Kommentar: {seit}{hinweis}')
        if fehlt:
            aus.append('')
        # Externe haben kein Konto, an dem sich messen liesse, wer am Zug ist.
        # Fuer sie bleibt eine Zeile mit der laengsten Stille zuerst.
        extern = [(letzte_wortmeldung(i, UNSERE_SEITE), i)
                  for i in blockierte if 'wait:extern' in i['labels']]
        if extern:
            extern.sort(key=lambda t: (t[0], t[1]['number']))
            liste = ', '.join(f'#{i["number"]} ({seit})' for seit, i in extern)
            aus.append(f'**{WAIT_NAMEN["wait:extern"]} ({len(extern)})**, '
                       f'laengste Stille zuerst; das Datum ist der letzte '
                       f'Kommentar, der nicht von uns stammt: {liste}\n')

    for stufe, was in AUTO_STUFEN:
        treffer = [i for i in zaehlbar if stufe in i['labels']]
        aus.append(f'### `{stufe}` ({len(treffer)}): {was}\n')
        if not treffer:
            aus.append('Derzeit keins.\n')
            continue
        aus.append(tabelle(treffer))
        aus.append('')

    return '\n'.join(aus).rstrip() + '\n'


def ersetze(body, block, begin=BEGIN, end=END):
    """Den Bereich zwischen den Markern austauschen.

    Zwei Markerpaare stehen im Body (MATRIX und PERSONEN), jeder Aufruf
    ersetzt genau eines und laesst das andere als Handtext stehen.

    Die Reihenfolgepruefung ist kein Formalismus: steht END vor BEGIN, ist
    `partition(END)` hinter BEGIN leer, und der gesamte handgepflegte Fuss
    faellt stillschweigend weg. `--check` wuerde in diesem Zustand Drift
    melden und zu genau dem `--apply` auffordern, das den Verlust schreibt.
    Deshalb hier Exit 2 statt einer Reparatur auf Verdacht.
    """
    if begin not in body or end not in body:
        abbruch(f'In #{MATRIX_ISSUE} fehlen die Marker. Erwartet wird eine '
                f'Zeile "{begin}" und spaeter "{end}".')
    if body.index(begin) > body.index(end):
        abbruch(f'In #{MATRIX_ISSUE} steht der END-Marker vor dem '
                f'BEGIN-Marker ({begin}). In dieser Reihenfolge wuerde der '
                f'Text nach BEGIN verloren gehen; bitte die Marker im Body '
                f'ordnen.')
    kopf, _, rest = body.partition(begin)
    _, _, fuss = rest.partition(end)
    return f'{kopf}{begin}\n\n{block}\n{end}{fuss}'


def ersetze_beide(body, block, personen):
    return ersetze(ersetze(body, block), personen, PBEGIN, PEND)


def hole_body():
    return json.loads(gh(['issue', 'view', str(MATRIX_ISSUE),
                          '--json', 'body']))['body']


def selftest():
    """Zaehlung, Sortierung, Pruefung und Marker-Ersatz an erfundenen Daten."""
    def iss(nr, labels, titel='T', datum='2026-08-01', kommentare=None):
        # kommentare: Liste aus 'JJJJ-MM-TT', ('JJJJ-MM-TT', 'login') oder
        # ('JJJJ-MM-TT', 'login', 'Text')
        def komm(n, k):
            k = (k, 'chsteiner') if isinstance(k, str) else k
            datum_, konto, text = (k + ('',))[:3]
            return {'createdAt': datum_ + 'T00:00:00Z',
                    'author': {'login': konto}, 'body': text,
                    'url': f'https://x/{nr}#c{n}'}
        roh = {'number': nr, 'title': titel, 'labels': sorted(labels),
               'createdAt': datum + 'T00:00:00Z',
               'comments': [komm(n, k) for n, k in
                            enumerate(kommentare or [])]}
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
    faelle.append(('Wartesache ohne unseren Kommentar steht unter Frage fehlt',
                   '**Frage fehlt (1)**' in block
                   and '- #2 T (Katharina), unser letzter Kommentar: keiner'
                   in block))

    # `auto:frozen` muss beides koennen: eine eigene Tabelle bekommen, damit
    # der Vorgang nicht stumm aus der Matrix faellt, und aus "Wer ist am Zug"
    # herausbleiben, weil dort Schulden stehen und kein Termin. Ohne wait:*
    # darf es dabei keine Luecke melden: das ist die Ausnahme, die der
    # gesamte Eintrag ausmacht.
    frozen = iss(271, [FROZEN, 'area:data', 'effort:large'], titel='Eingefroren')
    faelle.append(('auto:frozen ohne wait:* ist keine Luecke',
                   pruefe([frozen]) == []))
    kalt = baue(sauber + [frozen])
    faelle.append(('auto:frozen bekommt eine eigene Tabelle',
                   f'`{FROZEN}` (1)' in kalt and '#271' in kalt))
    # Die Kopfzahl und nicht die Nennung: ein eingefrorener Vorgang traegt
    # kein wait:*, faellt also ohnehin durch jede Liste je Person. Was
    # falsch wuerde, ist ihr Zaehler darueber. Die erste Fassung dieses
    # Falles prueft auf "#271" und war damit stumm, gemessen an einer
    # Mutation, die `blockierte` um FROZEN erweitert: Selbsttest blieb gruen.
    faelle.append(('auto:frozen zaehlt nicht als wartend',
                   '1 Tickets warten auf einen Menschen' in kalt))
    faelle.append(('auto:frozen zaehlt in der Kopfzahl mit',
                   '**3 offene Issues**' in kalt))
    # Gegenprobe zur vorigen Zeile: mit wait:* ist es weiterhin ein Fehler,
    # sonst wuerde die neue Stufe die Listen je Person zum Schweigen bringen.
    faelle.append(('wait:* an auto:frozen faellt weiter auf', any(
        'ohne auto:blocked' in f for f in
        pruefe([iss(272, [FROZEN, 'area:data', 'effort:small', 'wait:kzw'])]))))

    # Wer ist am Zug (Messvorschrift im Docstring). Jeder Fall prueft beide
    # Seiten: wo der Vorgang steht UND wo er nicht stehen darf, denn ein
    # Vorgang in der falschen Liste ist genau KZWs Ruege aus #406.
    W = ['auto:blocked', 'area:data', 'effort:small']
    heute = date(2026, 10, 9)

    gesehen = []

    def wo(i, ganz=False):
        # Nur der Abschnitt "Wer ist am Zug" und der Kasten davor: die
        # Tabellen darunter nennen jeden blockierten Vorgang ohnehin, ein
        # "#N not in" gegen den ganzen Block waere also stumm.
        gesehen.append(i)
        m = baue([i], heute)
        if not ganz:
            m = m.partition('### `auto:')[0]
        return baue_personen([i]), m

    # Sie hat nach unserer Frage geantwortet: bei uns, nicht in ihrer Liste.
    p, m = wo(iss(60, W + ['wait:kzw'], kommentare=[
        ('2026-10-01', 'chsteiner', 'Frage: Soll X?'),
        ('2026-10-05', 'wachauer', 'Ja.')]))
    faelle.append(('Ihre Antwort legt den Ball zu uns', '**Ball bei uns (1)**'
                   in m and '#60' in m and '#60' not in p))

    # Wir fragen danach neu: wieder bei ihr, mit dem neuen Satz.
    p, m = wo(iss(61, W + ['wait:kzw'], kommentare=[
        ('2026-10-01', 'wachauer', 'Ja.'),
        ('2026-10-02', 'chsteiner', 'Frage: Gilt das auch fuer Y? Rest.')]))
    faelle.append(('Unsere Frage legt den Ball zu ihr, mit dem ersten Satz',
                   '**Entscheiden (1)**' in p
                   and '[Gilt das auch fuer Y?](https://x/61#c1)' in p
                   and 'seit 2026-10-02' in p and '#61' not in m))

    # Abnahme, fett und nach einer Erwaehnung.
    p, _ = wo(iss(62, W + ['wait:kzw'], kommentare=[
        ('2026-10-03', 'chsteiner', '@wachauer **Abnahme:** Bitte X pruefen.')]))
    faelle.append(('Abnahme fett nach @-Erwaehnung wird erkannt',
                   '**Abnehmen (1)**' in p and 'Bitte X pruefen.' in p))

    # Das Anfangswort zaehlt nur am Anfang.
    p, m = wo(iss(63, W + ['wait:kzw'], kommentare=[
        ('2026-10-03', 'chsteiner', 'Das ist noch keine Abnahme: erst morgen.')]))
    faelle.append(('Abnahme: mitten im Satz trifft nicht', '#63' not in p
                   and '**Frage fehlt (1)**' in m))
    faelle.append(('Frage fehlt wird in ihrer Liste mitgezaehlt, statt '
                   '"Derzeit nichts" stehen zu lassen',
                   'Dazu kommen 1 ältere' in p.partition('### Für Julia')[0]))

    # Statusmeldung ohne Anfangswort: Frage fehlt, mit Live-Hinweis.
    p, m = wo(iss(64, W + ['wait:kzw'], kommentare=[
        ('2026-10-03', 'chsteiner',
         'Umgesetzt, live: https://dhcraft.org/mhdbdb-tei-only/')]))
    faelle.append(('Statusmeldung steht unter Frage fehlt, mit Live-Hinweis',
                   '#64' not in p and 'vermutlich Abnahme' in m))

    # Ein Bot nach ihrer Antwort legt den Ball nicht zurueck.
    p, m = wo(iss(65, W + ['wait:kzw'], kommentare=[
        ('2026-10-01', 'chsteiner', 'Frage: Soll X?'),
        ('2026-10-05', 'wachauer', 'Ja.'),
        ('2026-10-06', 'claude', 'Frage: Review-Kommentar')]))
    faelle.append(('Bot-Kommentar legt den Ball nicht zurueck',
                   '**Ball bei uns (1)**' in m and '#65' not in p))

    # Julia zuerst: eine Abnahme mit beiden Labels steht nur bei Julia.
    # Auch nicht als "Frage fehlt" oder "bei uns" fuer KZW, obwohl sie frueher
    # im Thread geschrieben hat und keine Zeile an sie geht.
    p, m = wo(iss(66, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'wachauer', 'Bitte Julia vorreihen.'),
        ('2026-10-04', 'chsteiner',
         '@juliahin **Abnahme:** Bitte pruefen?\ncc @wachauer')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Julia-Abnahme steht nur bei Julia, bei KZW nirgends',
                   '#66' in jul and '#66' not in kat and '#66' not in m
                   and 'Dazu kommen' not in kat))
    # Der uebliche Lebenslauf: Frage an KZW, sie antwortet, wir setzen um,
    # Abnahme an Julia mit cc. KZW steht danach nirgends, auch nicht rot.
    p, m = wo(iss(77, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@wachauer Frage: Soll X?'),
        ('2026-09-02', 'wachauer', 'Ja.'),
        ('2026-10-04', 'chsteiner',
         '@juliahin **Abnahme:** Bitte pruefen?\ncc @wachauer')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Abnahme an Julia nach KZWs Antwort: KZW nirgends',
                   '#77' in jul and '#77' not in kat and '#77' not in m
                   and 'laenger als' not in m))
    # Gegenprobe: schreibt KZW nach der Abnahme an Julia, liegt es bei uns.
    _, m = wo(iss(78, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@juliahin Abnahme: Bitte pruefen?'),
        ('2026-09-02', 'wachauer', 'Moment, da fehlt noch was.')]))
    faelle.append(('KZW nach der Abnahme an Julia: Ball bei uns',
                   '**Ball bei uns (1)**' in m and '#78' in m))
    # Offene Frage an KZW, danach eine getrennte Abnahme an Julia: die Frage
    # bleibt in KZWs Liste (Runde 3; der Vorrang darf nichts verschlucken).
    p, m = wo(iss(80, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@wachauer Frage: Soll X so bleiben?'),
        ('2026-09-05', 'chsteiner',
         '@juliahin Abnahme: Bitte Y pruefen?\ncc @wachauer')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Offene KZW-Frage bleibt trotz spaeterer Julia-Abnahme',
                   'Soll X so bleiben?' in kat and '#80' in jul))
    # Abnahme an Julia nach KZWs Antwort, danach eine Frage an Julia: die
    # Abnahme bleibt unsere Reaktion, KZW nicht bei uns.
    _, m = wo(iss(81, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@wachauer Frage: Soll X?'),
        ('2026-09-02', 'wachauer', 'Ja.'),
        ('2026-09-10', 'chsteiner', '@juliahin Abnahme: Bitte pruefen?'),
        ('2026-09-20', 'chsteiner', '@juliahin Frage: Noch was?')]))
    faelle.append(('Spaetere Frage an Julia macht KZW nicht rot',
                   '#81' not in m))
    # Frage an KZW und Abnahme an Julia im selben Kommentar: beide Zeilen.
    p, _ = wo(iss(82, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner', '@wachauer Frage: Gilt Z?\n\n'
         '@juliahin Abnahme: Bitte Y pruefen?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Frage an KZW und Abnahme an Julia in einem Kommentar',
                   'Gilt Z?' in kat and 'Bitte Y pruefen?' in jul
                   and 'Bitte Y' not in kat))
    # Eine nur an KZW gerichtete Abnahme bleibt bei ihr, auch wenn Julia
    # frueher eine eigene, beantwortete Abnahme hatte (Runde 4).
    p, m = wo(iss(83, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@juliahin Abnahme: Einfach?'),
        ('2026-09-03', 'juliahin', 'passt'),
        ('2026-09-20', 'chsteiner', '@wachauer Abnahme: Komplexe Sache Z?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('An KZW gerichtete Abnahme bleibt bei KZW',
                   'Komplexe Sache Z?' in kat and 'Komplexe' not in jul))
    # Der Vorrang gilt nicht fuer Linda: ihre Antwort bleibt bei uns.
    _, m = wo(iss(84, W + ['wait:linda', 'wait:julia'], kommentare=[
        ('2026-09-01', 'chsteiner', '@lindabeutel Frage: Lieferst du X?'),
        ('2026-09-02', 'lindabeutel', 'Ja, naechste Woche.'),
        ('2026-09-05', 'chsteiner', '@juliahin Abnahme: Bitte Y pruefen?')]))
    faelle.append(('Julia-Abnahme verdeckt Lindas Antwort nicht',
                   '#84 ' in m and 'Linda am 2026-09-02' in m))
    # Nie gefragt, aber sie hat geschrieben: bei uns, nicht "Frage fehlt".
    _, m = wo(iss(79, W + ['wait:kzw'], kommentare=[
        ('2026-09-01', 'wachauer', 'Hier meine Antwort.'),
        ('2026-09-05', 'chsteiner', 'Umgesetzt in PR 553.')]))
    faelle.append(('Ohne Frage, aber mit ihrer Antwort: Ball bei uns',
                   '**Ball bei uns (1)**' in m and '**Frage fehlt (0)**' in m))
    # Dasselbe ohne Adressierung: die Abnahme gilt fuer beide, steht aber
    # nur bei Julia.
    p, m = wo(iss(76, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner', 'Abnahme: Bitte pruefen?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Unadressierte Abnahme mit beiden Labels nur bei Julia',
                   '#76' in jul and '#76' not in kat and '#76' not in m))
    # Zwei Personen, zwei Fragen in einem Kommentar: jede bekommt ihre Zeile.
    p, _ = wo(iss(72, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner',
         '@wachauer Frage: Duerfen wir neue Lemmata anlegen?\nGrund.\n\n'
         '@juliahin Frage: Welches Lemma gehoert zu den 19 Woertern?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Je Person die an sie adressierte Zeile',
                   'neue Lemmata' in kat and '19 Woertern' not in kat
                   and '19 Woertern' in jul and 'neue Lemmata' not in jul))
    # Eine erste Zeile an die eine Person steht nicht bei der anderen.
    p, m = wo(iss(73, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner', '@wachauer Frage: Nur an KZW gerichtet?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('An eine Person adressierte Frage fehlt bei der anderen',
                   'Nur an KZW' in kat and 'Nur an KZW' not in jul
                   and '#73 T (Julia)' in m))
    # Ihre Antwort, danach nur ein Statuskommentar von uns: der Ball bleibt
    # bei uns, und die Frist laeuft weiter (#397: der Status darf den Alarm
    # nicht abschalten).
    p, m = wo(iss(74, W + ['wait:kzw'], kommentare=[
        ('2026-09-01', 'chsteiner', 'Frage: X?'),
        ('2026-09-02', 'wachauer', 'Ja.'),
        ('2026-09-03', 'chsteiner', 'Label korrigiert.')]))
    faelle.append(('Status nach ihrer Antwort laesst den Ball bei uns',
                   '**Ball bei uns (1)**' in m and 'laenger als' in m
                   and '**Frage fehlt (0)**' in m and '#74' not in p))
    # Abkuerzungen und Daten schneiden die Frage nicht ab.
    p, _ = wo(iss(75, W + ['wait:kzw'], kommentare=[
        ('2026-10-03', 'chsteiner',
         'Frage: Gilt z. B. die Regel vom 29.07. auch hier? Rest.')]))
    faelle.append(('Punkte vor dem Fragezeichen kuerzen die Frage nicht',
                   '[Gilt z. B. die Regel vom 29.07. auch hier?]' in p))
    # Gegenprobe: eine Frage mit beiden Labels steht bei beiden.
    p, _ = wo(iss(67, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner', 'Frage: Wer von euch?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Eine Frage an beide steht bei beiden', '#67' in jul
                   and '#67' in kat))

    # Frist: genau die Grenze ist noch nicht ueberfaellig, ein Tag mehr schon.
    for tage, soll in ((FRIST_TAGE, False), (FRIST_TAGE + 1, True)):
        tag = (heute - timedelta(days=tage)).isoformat()
        _, m = wo(iss(68, W + ['wait:kzw'], kommentare=[
            ('2026-09-01', 'chsteiner', 'Frage: X?'), (tag, 'wachauer', 'Ja.')]))
        faelle.append((f'Antwort vor {tage} Tagen: ueberfaellig={soll}',
                       ('laenger als' in m) == soll))

    # Linda erscheint nur, wenn etwas bei ihr liegt; Katharina und Julia immer.
    leer = baue_personen([iss(69, ['auto:full', 'area:docs', 'effort:small'])])
    faelle.append(('Leere Personenliste: Katharina und Julia stehen, Linda nicht',
                   '### Für Katharina' in leer and '### Für Julia' in leer
                   and 'Linda' not in leer))

    # Eckige Klammern im Satz duerfen den Link nicht beenden.
    p, _ = wo(iss(70, W + ['wait:kzw'], kommentare=[
        ('2026-10-03', 'chsteiner', 'Frage: Gilt [X] auch?')]))
    faelle.append(('Eckige Klammern im Fragesatz bleiben im Link',
                   '[Gilt (X) auch?](https://x/70#c0)' in p))

    # Die Tabellen behalten die letzte Wortmeldung, gleich von wem.
    faelle.append(('In der Tabelle steht weiter die letzte Wortmeldung',
                   '| 2026-10-05 |' in wo(iss(71, W + ['wait:kzw'], kommentare=[
                       ('2026-10-05', 'wachauer', 'Ja.')]), ganz=True)[1]))

    # Zwei Abnahme-Zeilen in einem Kommentar: die an KZW bleibt bei ihr
    # (Runde 5: verglichen wird die Zeile, nicht der Kommentar).
    p, _ = wo(iss(85, W + ['wait:kzw', 'wait:julia'], kommentare=[
        ('2026-10-04', 'chsteiner', '@juliahin Abnahme: Seite Y?\n'
         '@wachauer Abnahme: Grundsatzpruefung Z?')]))
    kat, _, jul = p.partition('### Für Julia')
    faelle.append(('Zwei Abnahme-Zeilen: die an KZW bleibt bei KZW',
                   'Grundsatzpruefung Z?' in kat and 'Seite Y?' in jul
                   and 'Seite Y?' not in kat))

    # Invarianten ueber alle Faelle oben, unabhaengig von der Skip-Logik
    # (Runde 5: die erste Fassung hing an derselben Herleitung wie der Skip
    # und blieb bei jedem Mutanten gruen).
    # 1. Kein wait:<person> steht an zwei Stellen.
    # 2. Ist unsere letzte Frage an KZW unbeantwortet, steht sie in KZWs
    #    Liste, ausser es ist eine Abnahme in genau derselben Zeile wie die
    #    an Julia. Das ist die Fehlerklasse aus #406, umgekehrt.
    def stellen(e, nr, wait):
        n = sum(1 for was in ('abnahme', 'frage')
                for i, _ in e['person'][wait][was] if i['number'] == nr)
        return n + sum(1 for i, w, _ in e['bei_uns'] + e['fehlt']
                       if i['number'] == nr and w == wait)
    kzw, jul_k = WAIT_KONTEN['wait:kzw'], WAIT_KONTEN['wait:julia']
    luecken, offen_geprueft = [], 0
    for i in gesehen:
        e = einordnen([i])
        for wait in PERSONEN:
            if wait in i['labels'] and stellen(e, i['number'], wait) > 1:
                luecken.append(f'#{i["number"]} {wait} doppelt')
        if 'wait:kzw' not in i['labels']:
            continue
        u = letzte_frage(i, kzw)
        ihr = letzter_kommentar(i, (kzw,))
        if not u or (ihr and ihr['createdAt'] > u['createdAt']):
            continue
        if ('wait:julia' in i['labels'] and art(u, kzw) == 'abnahme'
                and erste_zeile(u, kzw) == erste_zeile(u, jul_k)):
            continue
        offen_geprueft += 1
        gelistet = [k for i2, k in e['person']['wait:kzw'][art(u, kzw)]
                    if i2['number'] == i['number']]
        if gelistet != [u]:
            luecken.append(f'#{i["number"]} offene Frage an KZW fehlt')
    faelle.append((f'Kein Vorgang doppelt, keine offene KZW-Frage '
                   f'unsichtbar ({len(gesehen)} Faelle, davon '
                   f'{offen_geprueft} mit offener Frage; Luecken: '
                   f'{luecken or "keine"})',
                   not luecken and offen_geprueft > 10))

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

    # WAIT_NAMEN, WAIT_KONTEN und PERSONEN kodieren dieselbe Personenliste
    # dreimal. Fehlt ein neues wait:<person> in PERSONEN, faellt der Vorgang
    # still aus jeder Liste; fehlt das Konto, bricht einordnen() ab.
    faelle.append(('Jede benannte Person hat ein Konto und eine Liste, nur '
                   'Externe nicht',
                   set(WAIT_NAMEN) - set(WAIT_KONTEN) == {'wait:extern'}
                   and set(WAIT_NAMEN) - {'wait:extern'} == set(PERSONEN)))
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
                   'Wer-ist-am-Zug zu fallen', '#97: auto:blocked ohne wait' in stumm
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

    # Der fuenfte Fehlermodus, und der einzige, den die Anzahlpruefung allein
    # nicht sieht: ein Label, das dem Praefix folgt und dem Skript fremd ist.
    fremd_auto = pruefe([iss(11, ['auto:sometime', 'area:data', 'effort:small'])])
    faelle.append(('Unbekannte Autonomiestufe faellt auf', any(
        'unbekanntes Autonomiestufe-Label' in f for f in fremd_auto)))
    faelle.append(('...und nicht als Anzahlfehler, denn es ist genau eines',
                   not any('muss genau ein Label sein' in f for f in fremd_auto)))
    faelle.append(('Unbekannter Bereich faellt auf', any(
        'unbekanntes Bereich-Label' in f for f in
        pruefe([iss(12, ['auto:full', 'area:datenbank', 'effort:small'])]))))
    # Was ein fremder Wert im erzeugten Block anrichtet, ist je Achse
    # verschieden. Der Kommentar ueber ACHSEN behauptet das, diese zwei Faelle
    # halten ihn fest: die erste Fassung sagte "faellt aus jeder Tabelle" fuer
    # alle drei Achsen, und das stimmt nur fuer auto:.
    fremd_block = baue([iss(1, ['auto:full', 'area:docs', 'effort:small']),
                        iss(11, ['auto:sometime', 'area:data', 'effort:small'])])
    faelle.append(('Fremdes auto: erscheint in keiner Tabelle',
                   '| #11 |' not in fremd_block
                   and 'unbekanntes Autonomiestufe-Label' in fremd_block))
    area_block = baue([iss(1, ['auto:full', 'area:docs', 'effort:small']),
                       iss(12, ['auto:full', 'area:datenbank', 'effort:small'])])
    faelle.append(('Fremdes area: bekommt seine Zeile, mit dem Rohwert',
                   '| #12 |' in area_block and '| datenbank |' in area_block))

    # Haelt AUTO_STUFEN und ACHSEN zusammen: wer eine Stufe nur an einer der
    # beiden Stellen eintraegt, macht die eigene Matrix rot.
    faelle.append(('Jede Stufe aus AUTO_STUFEN ist erlaubtes Vokabular',
                   all(pruefe([iss(13, [name, 'area:data', 'effort:small']
                                   + (['wait:kzw'] if name == 'auto:blocked'
                                      else []))]) == []
                       for name, _ in AUTO_STUFEN)))

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

    # Zwei Markerpaare: jedes wird ersetzt, der Handtext dazwischen bleibt.
    zwei = f'{PBEGIN}\nP\n{PEND}\nmitte\n{BEGIN}\nM\n{END}\nunten'
    beide = ersetze_beide(zwei, 'NEU-M\n', 'NEU-P\n')
    faelle.append(('Beide Markerpaare werden je fuer sich ersetzt',
                   beide.index('NEU-P') < beide.index(PEND) < beide.index('mitte')
                   < beide.index(BEGIN) < beide.index('NEU-M') < beide.index(END)
                   and '\nP\n' not in beide and '\nM\n' not in beide
                   and beide.endswith('unten')))
    faelle.append(('Ersatz beider Paare ist idempotent',
                   ersetze_beide(beide, 'NEU-M\n', 'NEU-P\n') == beide))
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            ersetze_beide(f'oben\n{BEGIN}\nM\n{END}\nunten', 'N\n', 'N\n')
        ohne_p = False
    except SystemExit as exc:
        ohne_p = exc.code == 2
    faelle.append(('Fehlendes PERSONEN-Paar steigt mit 2 aus', ohne_p))

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
    # ist von der ROADMAP unabhaengig. Eng gefangen wird nur ListeGesaettigt:
    # ein echter gh-Ausfall (Rate Limit, abgelaufenes Token) soll weiterhin mit
    # Exit 2 rot werden, statt als "Limit erhoehen" durchzugehen.
    try:
        roadmap_treffer = pruefe_roadmap(hole_geschlossene())
    except FileNotFoundError:
        roadmap_treffer = []
        print(f'::warning::{ROADMAP} ist unter {REPO} nicht '
              f'vorhanden, die ROADMAP-Pruefung ist ausgefallen. Im Workflow '
              f'gehoert die Datei in die sparse-checkout-Liste.',
              file=sys.stderr)
    except ListeGesaettigt as exc:
        roadmap_treffer = []
        print(f'::warning::Die ROADMAP-Pruefung ist ausgefallen: {exc} Der '
              f'Body wird trotzdem geschrieben, er haengt an den offenen '
              f'Issues.', file=sys.stderr)

    for zeile_nr, nr in roadmap_treffer:
        print(f'::warning file={ROADMAP},line={zeile_nr}::#{nr} steht in '
              f'{ROADMAP} als Eintrag, ist aber nicht mehr offen. Zeile '
              f'streichen oder mit dem neuen Stand weiterfuehren.',
              file=sys.stderr)

    block = baue(issues)
    personen = baue_personen(issues)

    # Liegt etwas zu lange bei uns, ist das ein Fehler wie eine Label-Luecke:
    # der Body wird geschrieben und sagt es, der Lauf wird rot.
    for i, wait, k in ueberfaellig(einordnen(issues), date.today()):
        fehler.append(f'#{i["number"]}')
        print(f'::error title=Ball bei uns::#{i["number"]}: {PERSONEN[wait]} '
              f'hat am {k["createdAt"][:10]} geantwortet, seitdem keine neue '
              f'Frage von uns ({k["url"]})', file=sys.stderr)

    if args.check:
        aktuell = hole_body()
        neu = ersetze_beide(aktuell, block, personen)
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
        neu = ersetze_beide(hole_body(), block, personen)
        gh(['issue', 'edit', str(MATRIX_ISSUE), '--body', neu])
        zaehlbar = sum(1 for i in issues if 'evergreen' not in i['labels'])
        print(f'#{MATRIX_ISSUE} aktualisiert: {zaehlbar} Issues gelistet, '
              f'{len(issues)} geprueft.')
        return 1 if fehler else 0

    print(personen)
    print(block)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
