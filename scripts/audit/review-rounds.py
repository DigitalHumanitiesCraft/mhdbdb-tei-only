#!/usr/bin/env python3
"""Zählt die Review-Runden pro gemergtem PR (Wirkungsmessung für den lokalen Reviewer).

Hintergrund: seit dem 02.08.2026 läuft vor dem ersten Push ein lokaler
Reviewer (`fable-reviewer`, Fable 5, mit Bash), und der Prompt der CI-Action
weist den Bot an, bestehende Kommentare zu lesen und ab der dritten Runde nur
noch Verhaltensbefunde zu melden. Ob das wirkt, ist eine empirische Frage.
Dieses Skript liefert die Zahl dafür, damit die Nachher-Messung nicht in einer
Shell-History endet.

MESSVORSCHRIFT: Gezählt werden die Konversationskommentare von `claude[bot]`
an einem PR (`issues/<nr>/comments`), nicht Inline-Kommentare und nicht formale
Reviews: die Action postet ausschließlich Konversationskommentare, `reviews`
und `pulls/<nr>/comments` sind für alle Baseline-PRs leer (gemessen). Zwei
Spalten, weil sie Verschiedenes messen:

  Läufe     jeder Kommentar des Bots, also ein Workflow-Lauf.
  Reviews   nur Kommentare, die mit `**Claude finished` beginnen.

Die Differenz sind Fortschritts-Stubs abgebrochener Läufe: `track_progress`
postet den Kommentar beim Start, und wenn der nächste Push den Lauf über die
Concurrency-Group abbricht, bleibt der Stub stehen. In der Baseline betrifft
das drei PRs (#335, #337, #338), zusammen vier Stubs. Für die Frage „wie oft
hat der Bot gearbeitet" ist `Läufe` richtig, für „wie oft gab es ein Ergebnis
zu triagieren" `Reviews`.

Beide Zahlen hängen daran, dass `use_sticky_comment` in
`.github/workflows/claude-code-review.yml` AUS bleibt: sonst überschreibt jeder
Lauf denselben Kommentar und beide Spalten messen etwas anderes. Ebenso daran,
dass die Action der einzige LLM-Kommentator bleibt.

BASELINE (gemessen 2026-08-02, PRs #324 bis #338, Stand VOR dem neuen Setup):
siehe --baseline. Die Läufe sind dabei keine unabhängige Größe, sondern die
Zahl der Push-Ereignisse plus eins, weil jeder Push einen Lauf auslöst. Eine
sinkende Zahl heißt also nicht zwingend „der Bot findet weniger", sondern
zuerst „es wurde seltener nachgeschoben".

Usage:
    python scripts/audit/review-rounds.py
    python scripts/audit/review-rounds.py --limit 20 --baseline

Read-only, braucht `gh` mit Repo-Leserecht. Keine Korpus- oder Index-Änderung.
"""
import argparse
import json
import statistics
import subprocess
import sys

BOT = 'claude[bot]'
FERTIG_PRAEFIX = '**Claude finished'

# PR-Titel tragen Umlaute, die Windows-Konsole fährt cp1252: ohne das hier
# zerbröselt "prüft" im Output zu Fragezeichen (JOURNAL 2026-07-31).
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Der Stand vor dem neuen Setup, je PR (Läufe, abgeschlossene Reviews).
# Erhoben mit genau diesem Skript am 2026-08-02.
BASELINE = {324: (9, 9), 328: (12, 12), 330: (5, 5), 332: (7, 7), 333: (6, 6),
            334: (2, 2), 335: (3, 2), 336: (4, 4), 337: (11, 10), 338: (4, 2)}


def gh(args):
    res = subprocess.run(['gh'] + args, capture_output=True, text=True,
                         encoding='utf-8', errors='replace')
    if res.returncode != 0:
        sys.exit(f'gh {" ".join(args)} fehlgeschlagen:\n{res.stderr.strip()}')
    return res.stdout


def kennzahlen(werte):
    return (statistics.median(werte), max(werte), min(werte),
            statistics.mean(werte), sum(werte))


def zeile(titel, werte):
    med, hoch, tief, mittel, summe = kennzahlen(werte)
    return (f'{titel}: Median {med}, Maximum {hoch}, Minimum {tief}, '
            f'Mittelwert {mittel:.1f}, Summe {summe}')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--limit', type=int, default=10,
                   help='Zahl der zuletzt gemergten PRs (Vorgabe 10)')
    p.add_argument('--author', default=BOT,
                   help=f'Kommentar-Autor (Vorgabe {BOT})')
    p.add_argument('--baseline', action='store_true',
                   help='die eingebaute Vorher-Messung danebenstellen')
    args = p.parse_args()

    repo = json.loads(gh(['repo', 'view', '--json', 'nameWithOwner']))['nameWithOwner']

    # `gh pr list` sortiert nach Erstellungsdatum, nicht nach Merge-Datum:
    # #338 steht dort vor #337, obwohl #337 zwei Stunden später gemergt wurde.
    # Deshalb ein großzügiges Fenster holen, nach mergedAt sortieren und erst
    # dann zuschneiden. Rest-Risiko: ein PR, der länger offen lag als das
    # Fenster breit ist, fällt trotzdem heraus; bei gesättigtem Fenster warnt
    # die Ausgabe unten.
    fenster = max(60, args.limit * 6)
    prs = json.loads(gh(['pr', 'list', '--state', 'merged', '--limit',
                         str(fenster), '--json', 'number,title,mergedAt']))
    if not prs:
        sys.exit('Keine gemergten PRs gefunden.')
    naiv = {pr['number'] for pr in prs[:args.limit]}   # so haette gh sortiert
    prs = sorted(prs, key=lambda x: x['mergedAt'], reverse=True)[:args.limit]
    verschoben = len({pr['number'] for pr in prs} - naiv)

    zeilen, laeufe, reviews = [], [], []
    for pr in prs:
        nr = pr['number']
        kommentare = json.loads(gh([
            'api', f'repos/{repo}/issues/{nr}/comments', '--paginate']))
        eigene = [k for k in kommentare
                  if (k.get('user') or {}).get('login') == args.author]
        fertig = sum(1 for k in eigene
                     if (k.get('body') or '').startswith(FERTIG_PRAEFIX))
        laeufe.append(len(eigene))
        reviews.append(fertig)
        zeilen.append((nr, pr['mergedAt'][:10], len(eigene), fertig,
                       pr['title'][:52]))

    breite = max(len(z[4]) for z in zeilen)
    print(f'Review-Runden ({args.author}), {len(zeilen)} zuletzt gemergte PRs '
          f'in {repo}\n')
    print(f'  {"PR":>5}  {"gemergt":<10}  {"Läufe":>5}  {"Reviews":>7}  Titel')
    for nr, datum, n, fertig, titel in zeilen:
        print(f'  {nr:>5}  {datum:<10}  {n:>5}  {fertig:>7}  {titel:<{breite}}')

    print()
    print('  ' + zeile('Läufe  ', laeufe))
    print('  ' + zeile('Reviews', reviews))

    if verschoben:
        print(f'\n  Hinweis: {verschoben} PR(s) in dieser Auswahl hätte die '
              f'Sortierung von `gh pr list` (nach Erstellung) verfehlt.')

    if args.baseline:
        bl = [v[0] for v in BASELINE.values()]
        br = [v[1] for v in BASELINE.values()]
        print(f'\n  Baseline 2026-08-02 (PRs {min(BASELINE)} bis '
              f'{max(BASELINE)}, vor dem neuen Setup):')
        print('  ' + zeile('Läufe  ', bl))
        print('  ' + zeile('Reviews', br))
        ueberlappung = sorted(set(BASELINE) & {z[0] for z in zeilen})
        if ueberlappung:
            print(f'\n  Achtung: {len(ueberlappung)} der oben gelisteten PRs '
                  f'gehören noch zur Baseline selbst ({ueberlappung}). '
                  f'Der Vergleich trägt erst, wenn keiner mehr dabei ist.')


if __name__ == '__main__':
    main()
