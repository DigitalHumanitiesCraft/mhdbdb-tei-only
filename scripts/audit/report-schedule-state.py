#!/usr/bin/env python3
"""
Zustandswechsel eines Zeitplanlaufs ins Sammelticket melden (#653).

Die Zeitplanlaeufe auf main (nightly-tests.yml, link-check.yml, data-integrity.yml)
brauchen kein Modell und erreichen sonst niemanden, wenn sie rot werden:
issue-matrix.yml war 15 Tage in Folge rot, ohne dass es jemand bemerkt hat. Dieses
Skript ist der gemeinsame Meldeweg. Es kommentiert in #653, aber nur bei einem
Zustandswechsel (gruen nach rot, rot nach gruen), nach dem Muster von
check-doc-staleness.py --kommentar (Marker mit Hash im Kommentar).

## Marker

`<!-- zeitplan: NAME STATE HASH -->`. NAME ist der Lauf (z. B. `nightly-tests`),
STATE `gruen` oder `rot`, HASH die ersten 12 Zeichen von sha1("NAME|STATE"). Der
Hash schuetzt gegen einen von Hand getippten Marker: stimmt er nicht zum Rest der
Zeile, ist das ein harter Fehler. Massgeblich ist der letzte Kommentar mit einem
Marker desselben NAME; andere Laeufe im selben Ticket stoeren sich nicht.

## Entscheidung

    kein Marker, neuer Zustand rot     -> melden
    kein Marker, neuer Zustand gruen   -> nichts (es gab nie etwas zu entwarnen)
    letzter Marker gleich dem neuen    -> nichts
    letzter Marker rot, neu gruen      -> Entwarnung
    letzter Marker gruen, neu rot      -> melden

Ohne --apply zeigt der Lauf nur, was gepostet wuerde. Das Skript aendert keine
Datei im Repo.

## Nur main meldet

`--ref` (Vorgabe: GITHUB_REF) muss `refs/heads/main` sein, sonst meldet das Skript
nichts und sagt es in einer Logzeile. Gemessen: 12 von 12 workflow_dispatch-Laeufen
auf data-integrity.yml liefen auf Zweigen, darunter absichtlich rote Proben. Die
Workflows pruefen den Ref ebenfalls (Vorbild check-runtime-budget.py); das Skript
sichert es ein zweites Mal ab.

## GitHub nur ueber `gh api`

Wie check-doc-staleness.py (dessen gh_api, json_folge und Fehler hier mitbenutzt
werden): REST ueber Subprozess, in der Action liefert GH_TOKEN die Rechte.

Usage:
    python scripts/audit/report-schedule-state.py --name nightly-tests --state rot \\
        --detail-file detail.txt --run-url URL --issue 653            # zeigen
    python scripts/audit/report-schedule-state.py ... --apply         # posten
    python scripts/audit/report-schedule-state.py --selftest

Exit codes:
    0 = Lauf ist durch (auch wenn nichts zu melden war)
    1 = nur bei --selftest: ein Fall ist fehlgeschlagen
    2 = harter Fehler in der Eingabe oder beim Zugriff
"""
import argparse
import hashlib
import importlib.util
import io
import os
import re
import sys
import tempfile
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)


def _lade_staleness():
    """check-doc-staleness.py hat einen Bindestrich im Namen, also per importlib laden."""
    pfad = Path(__file__).resolve().parent / 'check-doc-staleness.py'
    spec = importlib.util.spec_from_file_location('check_doc_staleness', pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


_ds = _lade_staleness()
Fehler = _ds.Fehler
gh_api = _ds.gh_api
json_folge = _ds.json_folge
REPO = _ds.REPO

ZUSTAENDE = ('gruen', 'rot')
MELDE_REF = 'refs/heads/main'
NAME_MUSTER = re.compile(r'[a-z0-9][a-z0-9-]*')
MARKER = re.compile(r'<!-- zeitplan: (\S+) (\S+) (\S+) -->')
# Ein Kommentar ist keine Aktenablage: laengere Ausgaben werden gekappt.
DETAIL_MAX_ZEICHEN = 3000


# ---------------------------------------------------------------- reine Logik

def hash_von(name, zustand):
    return hashlib.sha1(f'{name}|{zustand}'.encode('utf-8')).hexdigest()[:12]


def marker_zeile(name, zustand):
    return f'<!-- zeitplan: {name} {zustand} {hash_von(name, zustand)} -->'


def pruefe_name(name):
    if not NAME_MUSTER.fullmatch(name or ''):
        raise Fehler(f'--name {name!r}: erlaubt sind Kleinbuchstaben, Ziffern und Bindestrich')


def letzter_zustand(kommentare, name):
    """Zustand des letzten Kommentars mit Marker fuer `name` (Reihenfolge = zeitlich), sonst None."""
    letzter = None
    for k in kommentare:
        for m in MARKER.finditer(k or ''):
            n, zustand, h = m.groups()
            if n != name:
                continue
            if zustand not in ZUSTAENDE or h != hash_von(n, zustand):
                raise Fehler(f'Marker mit unbekanntem Zustand oder falschem Hash: {m.group(0)!r}')
            letzter = zustand
    return letzter


def entscheide(neu, letzter):
    """'melden' | 'entwarnung' | 'nichts'."""
    if neu not in ZUSTAENDE:
        raise Fehler(f'unbekannter Zustand {neu!r}')
    if letzter is None:
        return 'melden' if neu == 'rot' else 'nichts'
    if letzter == neu:
        return 'nichts'
    return 'melden' if neu == 'rot' else 'entwarnung'


def kappe(detail):
    detail = detail.strip()
    if len(detail) <= DETAIL_MAX_ZEICHEN:
        return detail
    return detail[:DETAIL_MAX_ZEICHEN].rstrip() + f'\n[gekappt bei {DETAIL_MAX_ZEICHEN} von {len(detail)} Zeichen]'


def kommentar_text(name, neu, entscheidung, detail, run_url):
    kopf = marker_zeile(name, neu)
    if entscheidung == 'entwarnung':
        zeilen = [kopf, f'Zeitplanlauf `{name}`: wieder gruen.']
    else:
        zeilen = [kopf, f'Zeitplanlauf `{name}`: rot.']
    if detail:
        zeilen += ['', '```', kappe(detail), '```']
    if run_url:
        zeilen += ['', f'Lauf: {run_url}']
    return '\n'.join(zeilen)


# --------------------------------------------------------------------- Ablauf

def meldet_fuer_ref(ref):
    """Nur ein Lauf auf main darf melden: ein dispatch auf einem Zweig (auch eine absichtlich rote Probe) ist kein Zustand von main."""
    return ref == MELDE_REF


def melde(repo, issue, name, neu, detail, run_url, apply, ref=MELDE_REF):
    pruefe_name(name)
    if not meldet_fuer_ref(ref):
        print(f'{name}: Ref {ref or "<leer>"} ist nicht {MELDE_REF}: nichts melden.')
        return 0
    kommentare = [c.get('body') or '' for c in
                  json_folge(gh_api('--paginate', f'repos/{repo}/issues/{issue}/comments?per_page=100'))]
    letzter = letzter_zustand(kommentare, name)
    entscheidung = entscheide(neu, letzter)
    print(f'{name}: neuer Zustand {neu}, letzter Marker in den {len(kommentare)} Kommentaren '
          f'von #{issue}: {letzter or "keiner"}, Entscheidung: {entscheidung}')
    if entscheidung == 'nichts':
        print('Kein Kommentar noetig.')
        return 0
    text = kommentar_text(name, neu, entscheidung, detail, run_url)
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

    rot, gruen = marker_zeile('a', 'rot'), marker_zeile('a', 'gruen')
    cases.append(('Marker traegt Name, Zustand und Hash',
                  rot == f"<!-- zeitplan: a rot {hash_von('a', 'rot')} -->" and hash_von('a', 'rot') != hash_von('a', 'gruen')))
    cases.append(('kein Marker, rot: melden', entscheide('rot', None) == 'melden'))
    cases.append(('kein Marker, gruen: nichts', entscheide('gruen', None) == 'nichts'))
    cases.append(('rot nach rot: nichts', entscheide('rot', 'rot') == 'nichts'))
    cases.append(('gruen nach gruen: nichts', entscheide('gruen', 'gruen') == 'nichts'))
    cases.append(('gruen nach rot: melden', entscheide('rot', 'gruen') == 'melden'))
    cases.append(('rot nach gruen: Entwarnung', entscheide('gruen', 'rot') == 'entwarnung'))
    cases.append(('unbekannter Zustand: harter Fehler', wirft(lambda: entscheide('gelb', None), 'unbekannter Zustand')))
    cases.append(('letzter Marker zaehlt, fremder Name stoert nicht',
                  letzter_zustand(['x', rot, marker_zeile('b', 'gruen'), 'y'], 'a') == 'rot'
                  and letzter_zustand([rot, 'text', gruen], 'a') == 'gruen'
                  and letzter_zustand(['x'], 'a') is None))
    cases.append(('falscher Hash im Marker: harter Fehler',
                  wirft(lambda: letzter_zustand(['<!-- zeitplan: a rot 000000000000 -->'], 'a'), 'falschem Hash')))
    cases.append(('unbekannter Zustand im Marker: harter Fehler',
                  wirft(lambda: letzter_zustand(['<!-- zeitplan: a gelb 000000000000 -->'], 'a'), 'unbekanntem Zustand')))
    cases.append(('Name wird geprueft',
                  wirft(lambda: pruefe_name('Nightly Tests'), '--name') and pruefe_name('nightly-tests') is None))
    lang = 'z' * (DETAIL_MAX_ZEICHEN + 10)
    cases.append(('lange Ausgabe wird gekappt und nennt die Menge',
                  kappe(lang).endswith(f'[gekappt bei {DETAIL_MAX_ZEICHEN} von {len(lang)} Zeichen]')
                  and kappe('kurz ') == 'kurz'))
    text = kommentar_text('a', 'rot', 'melden', 'VERDICT: ROT', 'https://x/run/1')
    cases.append(('Kommentar: Marker in der ersten Zeile, Detail und Link',
                  text.splitlines()[0] == rot and 'VERDICT: ROT' in text and 'Lauf: https://x/run/1' in text))
    cases.append(('Ref: nur refs/heads/main meldet',
                  meldet_fuer_ref('refs/heads/main') and not meldet_fuer_ref('refs/heads/claude/x')
                  and not meldet_fuer_ref('refs/pull/1/merge') and not meldet_fuer_ref('')))
    # Ein anderer Ref kehrt vor jedem Zugriff zurueck: mit unerreichbarem gh darf nichts passieren.
    def ohne_zugriff():
        try:
            return melde('x/y', 653, 'a', 'rot', '', '', True, ref='refs/heads/zweig') == 0
        except Fehler:
            return False  # der gh-Zugriff wurde versucht

    cases.append(('Ref ausserhalb main: Exit 0 ohne gh-Zugriff', ohne_zugriff()))
    cases.append(('Entwarnung ohne Detail',
                  'wieder gruen' in kommentar_text('a', 'gruen', 'entwarnung', '', '')))

    failed = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print(f"  {'OK  ' if ok else 'FAIL'}  {n}")
    if failed:
        print(f'\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}', file=sys.stderr)
        return 1
    print(f'\nSelbsttest bestanden: {len(cases)} Faelle')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Zustandswechsel eines Zeitplanlaufs ins Sammelticket melden.')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--name', help='Name des Laufs, z. B. nightly-tests')
    ap.add_argument('--state', choices=ZUSTAENDE, help='Zustand dieses Laufs')
    ap.add_argument('--detail-file', help='Datei mit der Ausgabe, die in den Kommentar kommt')
    ap.add_argument('--run-url', default='')
    ap.add_argument('--ref', default=os.environ.get('GITHUB_REF', MELDE_REF),
                    help='Ref des Laufs (Vorgabe: GITHUB_REF, sonst main); ein anderer Ref als refs/heads/main meldet nichts')
    ap.add_argument('--issue', type=int, default=653)
    ap.add_argument('--apply', action='store_true', help='wirklich posten')
    ap.add_argument('--repo', default=REPO)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.name or not args.state:
        ap.error('--name und --state sind Pflicht')
    try:
        detail = ''
        if args.detail_file:
            try:
                detail = Path(args.detail_file).read_text(encoding='utf-8')
            except OSError as exc:
                raise Fehler(f'--detail-file nicht lesbar: {exc}')
        return melde(args.repo, args.issue, args.name, args.state, detail, args.run_url, args.apply, args.ref)
    except Fehler as exc:
        print(f'FEHLER: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
