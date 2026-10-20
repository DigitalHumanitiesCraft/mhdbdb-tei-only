#!/usr/bin/env python3
"""
Doku-Health-Check: wann er faellig ist, und welche Doku-Artefakte liegen geblieben sind.

Der Doku-Health-Check (Scorecard im JOURNAL, Playbook docs/playbooks/DOKU-CHECK.md)
war bisher an eine Erinnerung gebunden. Dieses Skript macht die Faelligkeit zu einer
Messung und fasst zwei Arten von Liegengebliebenem mit an:

    a) Faelligkeit: Commits auf den 14 stabilen Docs seit dem letzten Check
       (Markerdatei doc-health-state.json) und Tage seit dessen Datum.
    b) Feature-Docs (docs/features/*.md), deren Issue geschlossen ist: laut
       CLAUDE.md "Temporal Artifacts" leben sie nur, solange das Issue offen ist.
    c) docs/JOURNAL.md ueber der Zeilenschwelle (Verdichten ist Sache von chsteiner).

## Wer was darf

Das Skript liest und meldet. Es aendert keine Datei im Repo, schliesst kein Issue
und stoesst keinen Check an. Schreiben tut es nur mit `--kommentar --apply`, und
dann nur einen Kommentar ins Sammelticket.

## GitHub nur ueber `gh api`

Jeder Zugriff laeuft als Subprozess `gh api` (REST), nie ueber GraphQL, `gh pr`,
`gh issue` oder urllib mit GITHUB_TOKEN. Grund: dasselbe Skript muss auch in einer
Claude-Cloud-Session laufen, deren Proxy nur REST erlaubt und in der GITHUB_TOKEN
ein Platzhalter ist. In der Action liefert GH_TOKEN (github.token) die Rechte.

## Defensiv

Eine unbekannte Eingabe ist ein harter Fehler (Exit 2 mit Meldung), kein stilles
Ueberspringen: fehlendes oder unbekanntes Feld in der Markerdatei, ein Commit, der
nicht in der History liegt (flacher Klon: fetch-depth 0?), eine fehlende stabile
Doc, eine unbekannte .md unter docs/ (so faellt ein 16. Dokument auf), ein
Feature-Doc, dessen erste H1 nicht genau eine Issue-Nummer traegt.

## Kommentar ins Sammelticket

`--kommentar --issue N` postet nur bei Zustandswechsel. Der Zustandsschluessel
(Faelligkeitszustand ohne die laufende Zahl, Menge der Feature-Befunde,
JOURNAL-Hinweis ja/nein) wird gehasht und steht als `<!-- doc-health: HASH -->`
im Kommentar. Gepostet wird, wenn der letzte Kommentar mit diesem Marker einen
anderen Hash traegt oder keiner existiert, und der Zustand nicht ruhig ist. Ist
er ruhig und der letzte markierte Kommentar meldete etwas, geht eine kurze
Entwarnung raus. Ohne `--apply` zeigt der Lauf nur, was gepostet wuerde.

Usage:
    python scripts/audit/check-doc-staleness.py                 # Bericht a) bis c)
    python scripts/audit/check-doc-staleness.py --faellig       # nur a): Statuszeile und Zahlenzeile
    python scripts/audit/check-doc-staleness.py --kommentar --issue 641            # zeigen
    python scripts/audit/check-doc-staleness.py --kommentar --issue 641 --apply    # posten
    python scripts/audit/check-doc-staleness.py --selftest

Exit codes:
    0 = Lauf ist durch (auch bei "faellig"; die Faelligkeit ist ein Befund, kein Fehler)
    1 = nur bei --selftest: ein Fall ist fehlgeschlagen
    2 = harter Fehler in der Eingabe oder beim Zugriff
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO_DIR = Path(__file__).resolve().parents[2]
STATE_FILE = Path(__file__).resolve().parent / 'doc-health-state.json'
REPO = 'DigitalHumanitiesCraft/mhdbdb-tei-only'

# Faelligkeit: entschieden von chsteiner am 20.10.2026. Faellig, sobald EINE der
# beiden Schwellen erreicht ist.
SCHWELLE_COMMITS = 40
SCHWELLE_TAGE = 60

# Schwelle fuer den JOURNAL-Hinweis (Zeilen von docs/JOURNAL.md).
SCHWELLE_JOURNAL = 1500

# Praefix des Kopf-Branches eines offenen Doku-Check-PR.
PR_PRAEFIX = 'claude/doku-check-'

# Die 15 promptotyping-Dokumente aus docs/INDEX.md ohne JOURNAL.md.
STABILE_DOCS = (
    'INDEX', 'DATA-MODEL', 'ARCHITECTURE', 'DESIGN', 'FEATURES', 'DEVELOPMENT',
    'RESEARCH', 'DECISIONS', 'CONTRACTS', 'TEI-MODEL', 'TEI-MODEL-AUTH-FILES',
    'LINECODE', 'POS-TAGSET', 'ROADMAP',
)
# Bekannt ausgenommen: das 15. promptotyping-Dokument und sein Archiv.
AUSGENOMMEN = ('JOURNAL.md', 'journal-archive.md')

STATE_FELDER = ('commit', 'date', 'scorecard', '_comment')
MARKER = re.compile(r'<!-- doc-health: ([0-9a-f]+) -->')


class Fehler(Exception):
    """Harter Fehler in der Eingabe oder beim Zugriff (Exit 2)."""


# ---------------------------------------------------------------- reine Logik

def lade_state(daten):
    """Prueft den Inhalt der Markerdatei; gibt (commit, datum) zurueck."""
    if not isinstance(daten, dict):
        raise Fehler('Markerdatei: oberste Ebene ist kein Objekt')
    fehlt = [f for f in STATE_FELDER if f not in daten]
    if fehlt:
        raise Fehler('Markerdatei ohne Feld ' + ', '.join(repr(f) for f in fehlt))
    unbekannt = sorted(set(daten) - set(STATE_FELDER))
    if unbekannt:
        raise Fehler('Markerdatei mit unbekanntem Feld ' + ', '.join(repr(f) for f in unbekannt))
    for f in STATE_FELDER:
        if not isinstance(daten[f], str) or not daten[f].strip():
            raise Fehler(f'Markerdatei: Feld {f!r} ist kein nichtleerer Text')
    if not re.fullmatch(r'[0-9a-f]{40}', daten['commit']):
        raise Fehler(f"Markerdatei: commit {daten['commit']!r} ist keine volle SHA (40 Hex-Zeichen)")
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', daten['date']):
        raise Fehler(f"Markerdatei: date {daten['date']!r} ist kein ISO-Datum (JJJJ-MM-TT)")
    try:
        datum = date.fromisoformat(daten['date'])
    except ValueError:
        raise Fehler(f"Markerdatei: date {daten['date']!r} ist kein gueltiges Datum")
    return daten['commit'], datum


def ist_faellig(n_commits, tage):
    return n_commits >= SCHWELLE_COMMITS or tage >= SCHWELLE_TAGE


def faelligkeit_zustand(n_commits, tage, pr_nummern):
    """('nein' | 'faellig' | 'pr-offen', Nummer oder None). Ein offener PR gilt nur, wenn faellig."""
    if not ist_faellig(n_commits, tage):
        return 'nein', None
    if pr_nummern:
        return 'pr-offen', min(pr_nummern)
    return 'faellig', None


def statuszeile(zustand, nummer):
    if zustand == 'ja' or zustand == 'faellig':
        return 'FAELLIG: ja'
    if zustand == 'pr-offen':
        return f'FAELLIG: pr-offen #{nummer}'
    return 'FAELLIG: nein'


def zahlenzeile(n_commits, n_docs, sha, datum, tage):
    return (f'{n_commits} Commits an {n_docs} stabilen Docs seit {sha[:9]} ({datum.isoformat()}), '
            f'{tage} Tage; Schwelle {SCHWELLE_COMMITS} Commits oder {SCHWELLE_TAGE} Tage')


def issue_nummer_aus_h1(text, name):
    """Issue-Nummer aus der ersten H1-Zeile (`# ...`); genau ein `#N`, sonst harter Fehler."""
    h1 = None
    for zeile in text.splitlines():
        if re.match(r'# \S', zeile):
            h1 = zeile
            break
    if h1 is None:
        raise Fehler(f'{name}: keine H1-Zeile')
    treffer = re.findall(r'#(\d+)', h1)
    if len(treffer) != 1:
        raise Fehler(f'{name}: erste H1 traegt {len(treffer)} Issue-Nummern statt genau einer: {h1!r}')
    return int(treffer[0])


def pruefe_docs_liste(vorhanden):
    """Harter Fehler bei fehlender stabiler Doc oder unbekannter .md; `vorhanden` = Dateinamen."""
    soll = {f'{n}.md' for n in STABILE_DOCS}
    fehlt = sorted(soll - set(vorhanden))
    if fehlt:
        raise Fehler('stabile Doc fehlt unter docs/: ' + ', '.join(fehlt))
    unbekannt = sorted(set(vorhanden) - soll - set(AUSGENOMMEN))
    if unbekannt:
        raise Fehler('unbekannte .md unter docs/ (weder stabile Doc noch ausgenommen; '
                     'ein 16. Dokument oder eine Ausnahme fehlt in der Liste): ' + ', '.join(unbekannt))


def zustandsschluessel(zustand, feature_befunde, journal_hinweis):
    """Der Teil des Zustands, dessen Wechsel einen neuen Kommentar rechtfertigt."""
    return '|'.join([zustand, ','.join(sorted(feature_befunde)), 'journal' if journal_hinweis else '-'])


def hash_von(schluessel):
    return hashlib.sha1(schluessel.encode('utf-8')).hexdigest()[:12]


def ist_ruhig(zustand, feature_befunde, journal_hinweis):
    return zustand == 'nein' and not feature_befunde and not journal_hinweis


def letzter_hash(kommentare):
    """Hash des letzten Kommentars mit Marker (Reihenfolge der Liste = zeitlich), sonst None."""
    letzter = None
    for k in kommentare:
        m = MARKER.search(k or '')
        if m:
            letzter = m.group(1)
    return letzter


def entscheide(ruhig, neuer_hash, ruhiger_hash, letzter):
    """'melden' | 'entwarnung' | 'nichts'."""
    if ruhig:
        if letzter is None or letzter == ruhiger_hash:
            return 'nichts'
        return 'entwarnung'
    if letzter is None or letzter != neuer_hash:
        return 'melden'
    return 'nichts'


def json_folge(text):
    """Mehrere aneinandergehaengte JSON-Werte (gh --paginate) zu einer flachen Liste."""
    dec = json.JSONDecoder()
    i, n, werte = 0, len(text), []
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        wert, i = dec.raw_decode(text, i)
        if isinstance(wert, list):
            werte.extend(wert)
        else:
            werte.append(wert)
    return werte


# --------------------------------------------------------------- Zugriff (git, gh)

def git(*args):
    try:
        p = subprocess.run(['git', '-C', str(REPO_DIR), *args], capture_output=True,
                           text=True, encoding='utf-8')
    except OSError as exc:
        raise Fehler(f'git nicht aufrufbar: {exc}')
    return p


def gh_api(*args):
    try:
        p = subprocess.run(['gh', 'api', *args], capture_output=True, text=True, encoding='utf-8')
    except OSError as exc:
        raise Fehler(f'gh nicht aufrufbar: {exc}')
    if p.returncode != 0:
        raise Fehler(f'gh api {" ".join(args)} endete mit Exit {p.returncode}: {p.stderr.strip()}')
    return p.stdout


def offene_doku_prs(repo):
    """Nummern offener PRs, deren Kopf-Branch mit PR_PRAEFIX beginnt (nur Lesen, REST)."""
    seiten = json_folge(gh_api('--paginate', f'repos/{repo}/pulls?state=open&per_page=100'))
    nummern = []
    for pr in seiten:
        try:
            ref, nr = pr['head']['ref'], pr['number']
        except (KeyError, TypeError):
            raise Fehler(f'PR-Antwort ohne head.ref oder number: {str(pr)[:200]}')
        if ref.startswith(PR_PRAEFIX):
            nummern.append(int(nr))
    return sorted(nummern)


def issue_status(repo, nummer):
    status = gh_api(f'repos/{repo}/issues/{nummer}', '--jq', '.state').strip()
    if status not in ('open', 'closed'):
        raise Fehler(f'Issue #{nummer}: unbekannter Status {status!r}')
    return status


def lade_state_datei(pfad):
    try:
        daten = json.loads(Path(pfad).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise Fehler(f'Markerdatei nicht lesbar ({pfad}): {exc}')
    return lade_state(daten)


def messe_faelligkeit(repo):
    """Alles fuer Teil a): (sha, datum, n_commits, tage, zustand, nummer, pr_nummern)."""
    sha, datum = lade_state_datei(STATE_FILE)
    if git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
        raise Fehler(f'Commit {sha[:9]} der Markerdatei liegt nicht in der History '
                     '(flacher Klon? fetch-depth 0?)')
    docs_dir = REPO_DIR / 'docs'
    pruefe_docs_liste([p.name for p in docs_dir.glob('*.md')])
    pfade = [f'docs/{n}.md' for n in STABILE_DOCS]
    # --first-parent: ein ohne Squash gemergter Zweig zaehlt als ein Commit
    # (der Merge), nicht mit jedem Einzelcommit; sonst machte ein Doku-Check-PR
    # mit einem Commit je Befund den naechsten Check sofort faellig.
    p = git('log', '--first-parent', '--format=%H', f'{sha}..HEAD', '--', *pfade)
    if p.returncode != 0:
        raise Fehler(f'git log endete mit Exit {p.returncode}: {p.stderr.strip()}')
    n_commits = len([z for z in p.stdout.splitlines() if z.strip()])
    heute = datetime.now(timezone.utc).date()
    tage = (heute - datum).days
    if tage < 0:
        raise Fehler(f'Datum der Markerdatei {datum.isoformat()} liegt in der Zukunft (heute {heute.isoformat()} UTC)')
    prs = offene_doku_prs(repo)
    zustand, nummer = faelligkeit_zustand(n_commits, tage, prs)
    return sha, datum, n_commits, tage, zustand, nummer, prs


def feature_befunde(repo):
    """([Befundzeilen], Anzahl geprueft) fuer Teil b)."""
    ordner = REPO_DIR / 'docs' / 'features'
    dateien = sorted(ordner.glob('*.md')) if ordner.is_dir() else []
    befunde = []
    for d in dateien:
        text = d.read_text(encoding='utf-8')
        nr = issue_nummer_aus_h1(text, d.name)
        if issue_status(repo, nr) == 'closed':
            befunde.append(f'Feature-Doc zu geschlossenem Issue #{nr}: {d.name}')
    return befunde, len(dateien)


def journal_zeilen():
    pfad = REPO_DIR / 'docs' / 'JOURNAL.md'
    try:
        return len(pfad.read_text(encoding='utf-8').splitlines())
    except OSError as exc:
        raise Fehler(f'docs/JOURNAL.md nicht lesbar: {exc}')


# ------------------------------------------------------------------- Berichte

def faellig_modus(repo):
    sha, datum, n, tage, zustand, nummer, _ = messe_faelligkeit(repo)
    print(statuszeile(zustand, nummer))
    print(zahlenzeile(n, len(STABILE_DOCS), sha, datum, tage))
    return 0


def sammle(repo):
    """Alles, was Bericht und Kommentar brauchen."""
    sha, datum, n, tage, zustand, nummer, prs = messe_faelligkeit(repo)
    befunde, geprueft = feature_befunde(repo)
    zeilen = journal_zeilen()
    hinweis = zeilen > SCHWELLE_JOURNAL
    return dict(sha=sha, datum=datum, n=n, tage=tage, zustand=zustand, nummer=nummer, prs=prs,
                befunde=befunde, geprueft=geprueft, journal=zeilen, hinweis=hinweis)


def bericht_text(d):
    heute = datetime.now(timezone.utc).date().isoformat()
    z = [f'Doku-Health-Check, Stand {heute} (UTC)', '']
    z.append(statuszeile(d['zustand'], d['nummer']))
    z.append(zahlenzeile(d['n'], len(STABILE_DOCS), d['sha'], d['datum'], d['tage']))
    if d['zustand'] == 'pr-offen':
        z.append('Offene Doku-Check-PRs: ' + ', '.join(f'#{p}' for p in d['prs'])
                 + f' (Kopf-Branch {PR_PRAEFIX}*)')
    z.append('')
    z.append(f"Feature-Docs: {d['geprueft']} gepruefte Dateien unter docs/features/, "
             f"{len(d['befunde'])} zu geschlossenen Issues")
    for b in d['befunde']:
        z.append(f'  - {b}')
    if d['hinweis']:
        z.append(f"JOURNAL hat {d['journal']} Zeilen (Schwelle {SCHWELLE_JOURNAL}): "
                 'Verdichten ist Sache von chsteiner')
    else:
        z.append(f"JOURNAL: {d['journal']} Zeilen (Schwelle {SCHWELLE_JOURNAL}), kein Hinweis")
    return '\n'.join(z)


def schluessel_von(d):
    return zustandsschluessel(d['zustand'] if d['zustand'] != 'pr-offen' else f"pr-offen #{d['nummer']}",
                              d['befunde'], d['hinweis'])


RUHIGER_SCHLUESSEL = zustandsschluessel('nein', [], False)


def kommentar_text(d, modus, neuer_hash):
    kopf = f'<!-- doc-health: {neuer_hash} -->'
    if modus == 'entwarnung':
        return '\n'.join([kopf, 'Doku-Health: Entwarnung. ' + statuszeile(d['zustand'], d['nummer'])
                          + '; ' + zahlenzeile(d['n'], len(STABILE_DOCS), d['sha'], d['datum'], d['tage'])
                          + f", keine Feature-Docs zu geschlossenen Issues, JOURNAL {d['journal']} Zeilen."])
    zeilen = [kopf, 'Doku-Health meldet:', '', '```', bericht_text(d), '```']
    if d['zustand'] == 'faellig':
        zeilen += ['', 'Naechster Schritt: Doku-Check nach docs/playbooks/DOKU-CHECK.md; der Check-PR '
                       'schreibt scripts/audit/doc-health-state.json fort.']
    return '\n'.join(zeilen)


def kommentar_modus(repo, issue, apply):
    d = sammle(repo)
    print(bericht_text(d))
    print()
    neuer = hash_von(schluessel_von(d))
    ruhig = ist_ruhig(d['zustand'], d['befunde'], d['hinweis'])
    ruhiger_hash = hash_von(RUHIGER_SCHLUESSEL)
    kommentare = [c.get('body') or '' for c in
                  json_folge(gh_api('--paginate', f'repos/{repo}/issues/{issue}/comments?per_page=100'))]
    letzter = letzter_hash(kommentare)
    entscheidung = entscheide(ruhig, neuer, ruhiger_hash, letzter)
    print(f'Zustandshash {neuer} (ruhig: {"ja" if ruhig else "nein"}), letzter Marker in den '
          f'{len(kommentare)} Kommentaren von #{issue}: {letzter or "keiner"}, Entscheidung: {entscheidung}')
    if entscheidung == 'nichts':
        print('Kein Kommentar noetig.')
        return 0
    text = kommentar_text(d, entscheidung, ruhiger_hash if entscheidung == 'entwarnung' else neuer)
    if not apply:
        print(f'Ohne --apply: wuerde in #{issue} posten:')
        print('-' * 60)
        print(text)
        print('-' * 60)
        return 0
    with tempfile.TemporaryDirectory() as t:
        pfad = Path(t) / 'kommentar.md'
        pfad.write_text(text, encoding='utf-8')
        gh_api(f'repos/{repo}/issues/{issue}/comments', '-F', f'body=@{pfad}')
    print(f'Kommentar in #{issue} gepostet ({entscheidung}).')
    return 0


# ------------------------------------------------------------------- Selbsttest

def selftest():
    cases = []

    def wirft(f, teil):
        try:
            f()
        except Fehler as exc:
            return teil in str(exc)
        return False

    # Faelligkeitsregel an den Grenzwerten
    cases.append(('39 Commits, 59 Tage: nicht faellig', not ist_faellig(39, 59)))
    cases.append(('40 Commits, 0 Tage: faellig', ist_faellig(40, 0)))
    cases.append(('0 Commits, 60 Tage: faellig', ist_faellig(0, 60)))
    cases.append(('0 Commits, 59 Tage: nicht faellig', not ist_faellig(0, 59)))
    cases.append(('39 Commits und 60 Tage: faellig (Tage allein genuegen)', ist_faellig(39, 60)))
    cases.append(('faellig ohne PR', faelligkeit_zustand(40, 1, []) == ('faellig', None)))
    cases.append(('faellig mit PR #7 und #3: pr-offen #3', faelligkeit_zustand(40, 1, [7, 3]) == ('pr-offen', 3)))
    cases.append(('nicht faellig mit offenem PR: nein', faelligkeit_zustand(1, 1, [3]) == ('nein', None)))
    cases.append(('Statuszeilen', [statuszeile('faellig', None), statuszeile('nein', None),
                                   statuszeile('pr-offen', 12)]
                  == ['FAELLIG: ja', 'FAELLIG: nein', 'FAELLIG: pr-offen #12']))
    cases.append(('Zahlenzeile traegt Menge, Stand und Schwellen',
                  zahlenzeile(41, 14, 'a' * 40, date(2026, 10, 5), 15)
                  == '41 Commits an 14 stabilen Docs seit aaaaaaaaa (2026-10-05), 15 Tage; '
                     'Schwelle 40 Commits oder 60 Tage'))

    # H1-Parser
    cases.append(('H1 mit einer Nummer', issue_nummer_aus_h1('# Titel (#28)\n\n# 99', 'x.md') == 28))
    cases.append(('H1 ohne Nummer: harter Fehler',
                  wirft(lambda: issue_nummer_aus_h1('# Titel\n\ntext #5', 'x.md'), '0 Issue-Nummern')))
    cases.append(('H1 mit zwei Nummern: harter Fehler',
                  wirft(lambda: issue_nummer_aus_h1('# #1 und #2', 'x.md'), '2 Issue-Nummern')))
    cases.append(('Datei ohne H1: harter Fehler',
                  wirft(lambda: issue_nummer_aus_h1('## nur H2 #4\n', 'x.md'), 'keine H1')))
    cases.append(('nur die erste H1 zaehlt, nicht der Rest der Datei',
                  issue_nummer_aus_h1('Vorspann\n# #118: Titel\n\n# #5 zweite', 'x.md') == 118))

    # Zustandshash und Entscheidung
    ruhig_h = hash_von(RUHIGER_SCHLUESSEL)
    s1 = zustandsschluessel('faellig', [], False)
    s2 = zustandsschluessel('faellig', ['b', 'a'], False)
    cases.append(('Hash ist stabil gegen die Reihenfolge der Befunde',
                  s2 == zustandsschluessel('faellig', ['a', 'b'], False)))
    cases.append(('Hash unterscheidet Befunde, Zustand und JOURNAL-Hinweis',
                  len({hash_von(s1), hash_von(s2), hash_von(zustandsschluessel('nein', [], True)),
                       ruhig_h}) == 4))
    cases.append(('Marker wird gefunden, der letzte zaehlt',
                  letzter_hash(['x', f'<!-- doc-health: {hash_von(s1)} -->', 'y',
                                f'<!-- doc-health: {ruhig_h} -->', 'z']) == ruhig_h
                  and letzter_hash(['x', 'y']) is None))
    cases.append(('unruhig, kein Marker: melden', entscheide(False, 'h1', ruhig_h, None) == 'melden'))
    cases.append(('unruhig, gleicher Hash: nichts', entscheide(False, 'h1', ruhig_h, 'h1') == 'nichts'))
    cases.append(('unruhig, anderer Hash: melden', entscheide(False, 'h2', ruhig_h, 'h1') == 'melden'))
    cases.append(('ruhig, nie etwas gemeldet: nichts', entscheide(True, ruhig_h, ruhig_h, None) == 'nichts'))
    cases.append(('ruhig, letzter Kommentar meldete etwas: Entwarnung',
                  entscheide(True, ruhig_h, ruhig_h, 'h1') == 'entwarnung'))
    cases.append(('ruhig, Entwarnung schon gepostet: nichts', entscheide(True, ruhig_h, ruhig_h, ruhig_h) == 'nichts'))
    cases.append(('ruhig nur ohne Faelligkeit, Feature-Befund und JOURNAL-Hinweis',
                  ist_ruhig('nein', [], False) and not ist_ruhig('faellig', [], False)
                  and not ist_ruhig('pr-offen', [], False) and not ist_ruhig('nein', ['x'], False)
                  and not ist_ruhig('nein', [], True)))

    # gh --paginate: aneinandergehaengte Arrays
    cases.append(('json_folge: zwei Seiten und Objekt',
                  json_folge('[{"a":1},{"a":2}]\n[{"a":3}]\n{"a":4}') == [{'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}]
                  and json_folge('') == [] and json_folge('[]\n[]') == []))

    # Markerdatei
    gut = {'commit': 'a' * 40, 'date': '2026-10-05', 'scorecard': 's', '_comment': 'c'}
    cases.append(('Markerdatei gueltig', lade_state(gut) == ('a' * 40, date(2026, 10, 5))))
    cases.append(('Markerdatei: fehlendes Feld',
                  wirft(lambda: lade_state({k: v for k, v in gut.items() if k != 'scorecard'}), "ohne Feld 'scorecard'")))
    cases.append(('Markerdatei: unbekanntes Feld',
                  wirft(lambda: lade_state(dict(gut, extra='x')), "unbekanntem Feld 'extra'")))
    cases.append(('Markerdatei: Datum nicht ISO (auch das Kompaktformat)',
                  wirft(lambda: lade_state(dict(gut, date='05.10.2026')), 'kein ISO-Datum')
                  and wirft(lambda: lade_state(dict(gut, date='20261005')), 'kein ISO-Datum')))
    cases.append(('Markerdatei: unmoegliches Datum',
                  wirft(lambda: lade_state(dict(gut, date='2026-02-30')), 'kein gueltiges Datum')))
    cases.append(('Markerdatei: kurze SHA',
                  wirft(lambda: lade_state(dict(gut, commit='621bcf749')), 'keine volle SHA')))
    cases.append(('Markerdatei: leeres Feld',
                  wirft(lambda: lade_state(dict(gut, scorecard=' ')), 'nichtleerer Text')))
    cases.append(('Markerdatei: kein Objekt', wirft(lambda: lade_state([]), 'kein Objekt')))

    # Doc-Liste
    alle = [f'{n}.md' for n in STABILE_DOCS] + list(AUSGENOMMEN)
    cases.append(('Doc-Liste: 14 stabile Docs', len(STABILE_DOCS) == 14 and len(set(STABILE_DOCS)) == 14))
    try:
        pruefe_docs_liste(alle)
        ok_voll = True
    except Fehler:
        ok_voll = False
    cases.append(('Doc-Liste vollstaendig ohne Fehler', ok_voll))
    cases.append(('Doc-Liste: fehlende stabile Doc',
                  wirft(lambda: pruefe_docs_liste([a for a in alle if a != 'DESIGN.md']), 'DESIGN.md')))
    cases.append(('Doc-Liste: unbekannte .md faellt auf',
                  wirft(lambda: pruefe_docs_liste(alle + ['ZZZ.md']), 'ZZZ.md')))

    failed = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print(f"  {'OK  ' if ok else 'FAIL'}  {n}")
    if failed:
        print(f'\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}', file=sys.stderr)
        return 1
    print(f'\nSelbsttest bestanden: {len(cases)} Faelle')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Doku-Health-Check: Faelligkeit und liegen gebliebene Doku-Artefakte.')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--faellig', action='store_true', help='nur die Faelligkeit (Status- und Zahlenzeile); Exit 0 bei ja, nein und pr-offen, Exit 2 bei einem Fehler')
    ap.add_argument('--kommentar', action='store_true', help='Bericht und Kommentar ins Sammelticket (mit --issue)')
    ap.add_argument('--issue', type=int, help='Sammelticket fuer --kommentar')
    ap.add_argument('--apply', action='store_true', help='mit --kommentar: wirklich posten')
    ap.add_argument('--repo', default=REPO)
    args = ap.parse_args()
    if sum([args.selftest, args.faellig, args.kommentar]) > 1:
        ap.error('--selftest, --faellig und --kommentar schliessen einander aus')
    if args.kommentar and not args.issue:
        ap.error('--kommentar braucht --issue N')
    if (args.issue or args.apply) and not args.kommentar:
        ap.error('--issue und --apply gehoeren zu --kommentar')
    if args.selftest:
        return selftest()
    try:
        if args.faellig:
            return faellig_modus(args.repo)
        if args.kommentar:
            return kommentar_modus(args.repo, args.issue, args.apply)
        print(bericht_text(sammle(args.repo)))
        return 0
    except Fehler as exc:
        print(f'FEHLER: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
