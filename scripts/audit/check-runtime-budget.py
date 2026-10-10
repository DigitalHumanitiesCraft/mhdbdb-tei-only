#!/usr/bin/env python3
"""
Laufzeitbudget der CI-Schritte (#564): rot, wenn ein Schritt deutlich laenger
braucht als sein Budget.

Bis hierher gab es in diesen Workflows nur `timeout-minutes` (5, 20 bzw. 45
Minuten je Workflow) als Abbruch und nichts, was rot wurde, wenn ein Schritt
langsamer wurde. Eine Verlangsamung fiel erst auf, wenn jemand wartete.

## Wie es laeuft

Als LETZTER Schritt in jedem Job der PR-Workflows. Das Skript liest ueber die
Actions-API die schon fertigen Schritte des EIGENEN Jobs (Dauer =
completed_at minus started_at) und haelt sie gegen `runtime-budget.json`.
Das Ergebnis ist damit derselbe Check am PR wie der Job selbst; ein
workflow_run-Workflow liefe im Kontext von main, wuerde das Budget nicht aus
dem PR lesen und waere erst nach dem Merge testbar.

## Die Regel (Entscheidung chsteiner, 10.10.2026, #564)

- Grenze = Budget mal 1,5. Checkout-Schritte: Budget mal 1,3.
- Ein Schritt mit Budget unter 10 s hat die feste Grenze 10 s. Ein Schritt ohne
  Eintrag hat sie auch: er darf bis 10 s laufen, darueber ist er rot ("kein
  Budget"), bis jemand einen Eintrag mit Begruendung schreibt.
- Der LLM-Review-Schritt ist nicht im Gate (`excluded`; der Workflow selbst
  traegt das Gate nicht, siehe unten).
- Rot auf einem PR heisst: kein Merge, bis die Verlangsamung behoben oder das
  Budget im SELBEN PR erhoeht ist, mit einer Begruendungszeile in der
  Budgetdatei. Ein Neustart wegen Runner-Rauschen ist einmal erlaubt.
- Auf push, schedule und dispatch wird nichts rot. Dort geht eine Ueberschreitung
  als Kommentar ins Sammelticket (`collector_issue`), und nur auf main.

## Was das Skript nicht rot faerbt

Ein Job, der schon rot ist: dann ist die Ueberschreitung eine Warnung. Der
Budget-Schritt soll die eigentliche Ursache weder verdecken noch verdoppeln.

## Was es rot faerbt, obwohl nichts ueberschritten ist

Auf einem PR jede Messung, die nicht moeglich war: API nicht erreichbar, Job
nicht gefunden, kein fertiger Schritt, Budgetdatei unbrauchbar. Keine Daten
sind rot, nicht gruen. Bei einem PR aus einem Fork liefert das Token weniger
Rechte; fehlt dort der Lesezugriff auf die Actions-API, endet der Schritt
also rot und nicht als stilles Gruen.

## Warum nicht claude-code-review.yml

Die Action prueft, dass die Workflow-Datei der auf main gleicht, und bricht
sonst ab. Ein Schritt in dieser Datei haengt das Review eines jeden PR, der
ihn einfuehrt. Der Review-Schritt ist ohnehin ausgenommen.

## Grundmenge der Budgets

Die Werte stehen mit Datum, Anzahl Laeufe und Messvorschrift in der Budgetdatei
(`basis`). `--measure` rechnet sie aus der API nach. Regel der Koordination:
p90 der erfolgreichen Laeufe. Zeitraum: bei einem Schritt, den eine Beschleunigung
veraendert hat (Checkout nach E1), nur Laeufe seit deren Merge; sonst die letzten
25. Gibt es weniger als 10 Laeufe, steht das mit "n unter 10, vorlaeufig" in
`basis`, und die Nachkalibrierung folgt.

Usage:
    python scripts/audit/check-runtime-budget.py --selftest
    python scripts/audit/check-runtime-budget.py --check --repo R --run-id N --attempt A \\
        --workflow no-cdn-check.yml --job check --event pull_request --job-status success
    python scripts/audit/check-runtime-budget.py --check ... --jobs-json antwort.json
        # statt der API eine gespeicherte Antwort (Wiederholung und Mutationsproben)
    python scripts/audit/check-runtime-budget.py --measure --repo R --workflow data-integrity.yml \\
        --since 2026-10-10T00:00:00Z --max-runs 25

Exit codes:
    0 = alles im Budget, oder Ueberschreitung ohne Wirkung (kein PR, Job schon rot)
    1 = auf einem PR mindestens ein Schritt ueber der Grenze; bei --selftest ein Fall
    2 = Messung auf einem PR nicht moeglich
"""
import argparse
import io
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO_DIR = Path(__file__).resolve().parents[2]
BUDGET_FILE = Path(__file__).resolve().parent / 'runtime-budget.json'

# Schritte, die der Runner selbst einfuegt (kein Workflow-Inhalt, nicht budgetierbar);
# dazu alle "Post ..."-Schritte der Actions, die erst nach dem Gate-Schritt laufen
RUNNER_SCHRITTE = ('Set up job', 'Complete job')


class MessungFehlt(Exception):
    """Die Messung war nicht moeglich (API, Job, Budgetdatei)."""


def zeit(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def sekunden(schritt, jetzt=None):
    """Dauer eines erfolgreichen Schritts in Sekunden, sonst None.

    Ein Schritt, den die Jobs-API noch als `in_progress` fuehrt, zaehlt mit
    `jetzt` als Ende (der Start des Gate-Skripts, nicht der Moment der Auswertung).
    Das ist der Schritt unmittelbar vor diesem Gate: beim
    ersten PR-Lauf (#575) meldete die API ihn noch nicht als abgeschlossen, und
    ohne diese Regel fehlte in jedem Job genau der letzte, oft groesste Schritt.
    """
    if schritt.get('status') == 'in_progress' and jetzt is not None:
        a = schritt.get('started_at')
        return (jetzt - zeit(a)).total_seconds() if a else None
    if schritt.get('conclusion') != 'success':
        return None
    a, b = schritt.get('started_at'), schritt.get('completed_at')
    if not a or not b:
        return None
    return (zeit(b) - zeit(a)).total_seconds()


def lade_budget(pfad):
    try:
        cfg = json.loads(Path(pfad).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise MessungFehlt(f'Budgetdatei nicht lesbar: {exc}')
    for feld in ('factor', 'checkout_factor', 'floor_s', 'collector_issue', 'excluded', 'steps'):
        if feld not in cfg:
            raise MessungFehlt(f'Budgetdatei ohne Feld {feld!r}')
    for feld in ('factor', 'checkout_factor', 'floor_s'):
        if not isinstance(cfg[feld], (int, float)) or cfg[feld] < 0:
            raise MessungFehlt(f'Budgetdatei: {feld} ist keine Zahl ab 0')
    if not isinstance(cfg['collector_issue'], int):
        raise MessungFehlt('Budgetdatei: collector_issue ist keine Issue-Nummer')
    for schluessel, eintrag in cfg['steps'].items():
        if '/' not in schluessel:
            raise MessungFehlt(f'Budgetdatei: Schluessel {schluessel!r} ohne "<workflow>/<schritt>"')
        for feld in ('budget_s', 'n', 'date', 'basis', 'reason'):
            if feld not in eintrag or eintrag[feld] in ('', None):
                raise MessungFehlt(f'Budgetdatei: {schluessel!r} ohne {feld!r}')
        if not isinstance(eintrag['budget_s'], (int, float)) or eintrag['budget_s'] <= 0:
            raise MessungFehlt(f'Budgetdatei: {schluessel!r}: budget_s ist keine positive Zahl')
    return cfg


def grenze(workflow, name, cfg):
    """(Grenze in s, Budget in s oder None, Faktor) fuer einen Schritt."""
    eintrag = cfg['steps'].get(f'{workflow}/{name}')
    if eintrag is None:
        return cfg['floor_s'], None, None
    budget = eintrag['budget_s']
    if budget < cfg['floor_s']:
        return cfg['floor_s'], budget, None
    faktor = cfg['checkout_factor'] if name.startswith('Checkout') else cfg['factor']
    return budget * faktor, budget, faktor


def bewerte(schritte, workflow, cfg, eigener_schritt=None, jetzt=None):
    """[(name, dauer, grenze, budget, faktor, ueber)] fuer alle messbaren Schritte."""
    zeilen = []
    for s in schritte:
        name = s['name']
        if name == eigener_schritt or f'{workflow}/{name}' in cfg['excluded']:
            continue
        if name in RUNNER_SCHRITTE or name.startswith('Post '):
            continue
        dauer = sekunden(s, jetzt)
        if dauer is None:
            continue
        g, budget, faktor = grenze(workflow, name, cfg)
        zeilen.append((name, dauer, g, budget, faktor, dauer > g))
    return zeilen


def zeile_text(name, dauer, g, budget, faktor):
    if budget is None:
        return f'{name}: {dauer:.0f} s gegen die feste Grenze {g:g} s (kein Budget eingetragen)'
    if faktor is None:
        return f'{name}: {dauer:.0f} s gegen die feste Grenze {g:g} s (Budget {budget:g} s liegt darunter)'
    return f'{name}: {dauer:.0f} s gegen Grenze {g:.0f} s (Budget {budget:g} s mal {faktor:g})'


def hole_jobs(repo, run_id, attempt, token):
    api = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
    url = f'{api}/repos/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.urlopen(req, timeout=30) as antwort:
            return json.loads(antwort.read().decode('utf-8'))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise MessungFehlt(f'Actions-API nicht lesbar ({url}): {exc}')


def vor_dem_gate(schritte, eigener_schritt):
    """Die Schritte vor dem eigenen, ohne Runner-Schritte; ohne eigenen Schritt alle."""
    liste = []
    for s in schritte:
        if s['name'] == eigener_schritt:
            break
        if s['name'] in RUNNER_SCHRITTE or s['name'].startswith('Post '):
            continue
        liste.append(s)
    return liste


def offene_schritte(schritte, eigener_schritt):
    """Schritte vor dem Gate, die die API weder fertig noch laufend mit Startzeit fuehrt."""
    return [s for s in vor_dem_gate(schritte, eigener_schritt)
            if s.get('status') != 'completed'
            and not (s.get('status') == 'in_progress' and s.get('started_at'))]


def eigene_schritte(antwort, job_name):
    jobs = [j for j in antwort.get('jobs', []) if j.get('name') == job_name]
    if len(jobs) != 1:
        raise MessungFehlt(f'Job {job_name!r} kommt {len(jobs)}-mal in der API-Antwort vor, erwartet genau einmal')
    return jobs[0].get('steps', [])


def kommentiere(repo, nummer, text, token):
    api = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
    req = urllib.request.Request(
        f'{api}/repos/{repo}/issues/{nummer}/comments', data=json.dumps({'body': text}).encode('utf-8'),
        method='POST', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
                                'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as antwort:
        antwort.read()


def pruefe(args, cfg, antwort, kommentar=None):
    """Kernlogik; gibt den Exit-Code zurueck. `kommentar(text)` nimmt den Sammelticket-Kommentar."""
    erzwingend = args.event == 'pull_request'
    job_rot = args.job_status not in ('success', '')
    try:
        schritte = eigene_schritte(antwort, args.job)
        zeilen = bewerte(schritte, args.workflow, cfg, eigener_schritt=args.self_step,
                         jetzt=getattr(args, 'jetzt', None) or datetime.now(timezone.utc))
        if not zeilen:
            raise MessungFehlt(f'Job {args.job!r}: kein fertiger Schritt messbar')
        gemessen = {z[0] for z in zeilen}
        fehlt = [s for s in vor_dem_gate(schritte, args.self_step)
                 if s['name'] not in gemessen and f'{args.workflow}/{s["name"]}' not in cfg['excluded']
                 and s.get('conclusion') != 'skipped']
        for s in fehlt:
            print(f'  nicht gemessen: {s["name"]} (status {s.get("status")}, conclusion {s.get("conclusion")})')
        if fehlt and erzwingend and not job_rot:
            raise MessungFehlt(f'{len(fehlt)} Schritt(e) vor dem Gate nicht messbar: '
                               + ', '.join(s['name'] for s in fehlt))
    except MessungFehlt as exc:
        if erzwingend and not job_rot:
            print(f'::error title=Laufzeitbudget::Messung nicht moeglich: {exc}', file=sys.stderr)
            return 2
        print(f'::warning title=Laufzeitbudget::Messung nicht moeglich: {exc}')
        return 0

    ueber = [z for z in zeilen if z[5]]
    ohne_budget = [z for z in ueber if z[3] is None]
    print(f'Laufzeitbudget {args.workflow}, Job {args.job}: {len(zeilen)} Schritte gemessen, '
          f'{len(ueber)} ueber der Grenze ({len(ohne_budget)} davon ohne Eintrag), '
          f'Ereignis {args.event or "unbekannt"}, Job {args.job_status or "unbekannt"}.')
    laengster = max(zeilen, key=lambda z: z[1])
    print(f'  laengster Schritt: {laengster[0]}: {laengster[1]:.0f} s')
    if not ueber:
        return 0

    for name, dauer, g, budget, faktor, _ in ueber:
        text = zeile_text(name, dauer, g, budget, faktor)
        if erzwingend and not job_rot:
            print(f'::error title=Laufzeitbudget::{args.workflow} {text}. Beheben oder das Budget in '
                  f'scripts/audit/runtime-budget.json im selben PR erhoehen (mit Begruendung).', file=sys.stderr)
        else:
            print(f'::warning title=Laufzeitbudget::{args.workflow} {text}')
    if erzwingend and not job_rot:
        return 1
    if kommentar and not erzwingend and args.ref == 'refs/heads/main':
        koerper = [f'Laufzeitbudget ueberschritten, `{args.workflow}`, Job `{args.job}`, Ereignis `{args.event}`, '
                   f'[Lauf {args.run_id}]({args.run_url}):', '']
        koerper += [f'- {zeile_text(n, d, g, b, f)}' for n, d, g, b, f, _ in ueber]
        koerper += ['', 'Rot blockiert auf main nichts. Ursache suchen oder, wenn die Verlangsamung gewollt ist, '
                    'das Budget in `scripts/audit/runtime-budget.json` mit Begruendung erhoehen.']
        try:
            kommentar('\n'.join(koerper))
        except (urllib.error.URLError, OSError) as exc:
            print(f'::warning title=Laufzeitbudget::Kommentar im Sammelticket nicht moeglich: {exc}')
    return 0


def p90(werte):
    v = sorted(werte)
    return v[min(len(v) - 1, math.ceil(0.9 * len(v)) - 1)]


def messen(args, cfg_floor):
    """Vorschlag fuer die Budgets aus den letzten erfolgreichen Laeufen eines Workflows."""
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or ''
    api = os.environ.get('GITHUB_API_URL', 'https://api.github.com')

    def get(pfad):
        req = urllib.request.Request(f'{api}/{pfad}', headers={
            'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(req, timeout=60) as antwort:
            return json.loads(antwort.read().decode('utf-8'))

    q = f'repos/{args.repo}/actions/workflows/{args.workflow}/runs?status=success&per_page=100'
    if args.since:
        q += '&created=' + urllib.request.quote('>=' + args.since)
    runs = get(q)['workflow_runs']
    if args.branch:
        runs = [r for r in runs if r['head_branch'] == args.branch]
    runs = runs[:args.max_runs]
    dauern = {}
    for r in runs:
        for j in get(f'repos/{args.repo}/actions/runs/{r["id"]}/jobs?per_page=100')['jobs']:
            if j.get('conclusion') != 'success':
                continue
            for s in j['steps']:
                d = sekunden(s)
                if d is not None:
                    dauern.setdefault(s['name'], []).append(d)
    out = {'workflow': args.workflow, 'laeufe': len(runs), 'schritte': {}}
    for name, v in sorted(dauern.items()):
        out['schritte'][name] = {'n': len(v), 'p90': p90(v), 'median': sorted(v)[len(v) // 2], 'max': max(v)}
    return out


def selftest():
    cfg = {'factor': 1.5, 'checkout_factor': 1.3, 'floor_s': 10, 'collector_issue': 1,
           'excluded': ['w.yml/Run Claude Code Review'],
           'steps': {
               'w.yml/Checkout': {'budget_s': 100, 'n': 1, 'date': 'd', 'basis': 'b', 'reason': 'r'},
               'w.yml/Bauen': {'budget_s': 100, 'n': 1, 'date': 'd', 'basis': 'b', 'reason': 'r'},
               'w.yml/Klein': {'budget_s': 5, 'n': 1, 'date': 'd', 'basis': 'b', 'reason': 'r'},
               'w.yml/Freshness Indexe — Rebuild': {'budget_s': 80, 'n': 1, 'date': 'd', 'basis': 'b', 'reason': 'r'},
           }}

    def schritt(name, dauer, conclusion='success', mit_zeit=True):
        s = {'name': name, 'conclusion': conclusion}
        if mit_zeit:
            s['started_at'] = '2026-10-10T12:00:00Z'
            s['completed_at'] = f'2026-10-10T12:{int(dauer) // 60:02d}:{int(dauer) % 60:02d}Z'
        return s

    def ueber(schritte, **kw):
        return [z[0] for z in bewerte(schritte, 'w.yml', kw.get('cfg', cfg), kw.get('eigener'), kw.get('jetzt')) if z[5]]

    cases = []
    cases.append(('Schritt im Budget ist ok', ueber([schritt('Bauen', 150)]) == []))
    cases.append(('Schritt ueber Budget mal 1,5 ist rot', ueber([schritt('Bauen', 151)]) == ['Bauen']))
    cases.append(('Checkout hat Faktor 1,3: 131 s ist rot, derselbe Wert bei anderem Schritt ok',
                  ueber([schritt('Checkout', 131), schritt('Bauen', 131)]) == ['Checkout']))
    cases.append(('Budget unter 10 s: feste Grenze 10 s, 10 s ok', ueber([schritt('Klein', 10)]) == []))
    cases.append(('Budget unter 10 s: 11 s rot', ueber([schritt('Klein', 11)]) == ['Klein']))
    cases.append(('Schritt ohne Eintrag: 10 s ok', ueber([schritt('Neu', 10)]) == []))
    cases.append(('Schritt ohne Eintrag: 11 s rot (kein Budget)', ueber([schritt('Neu', 11)]) == ['Neu']))
    cases.append(('ausgenommener Schritt zaehlt nie', ueber([schritt('Run Claude Code Review', 9999)]) == []))
    cases.append(('eigener Schritt zaehlt nie', ueber([schritt('Laufzeitbudget', 9999)], eigener='Laufzeitbudget') == []))
    cases.append(('fehlgeschlagener Schritt wird nicht bewertet', ueber([schritt('Bauen', 9999, conclusion='failure')]) == []))
    cases.append(('Schritt ohne Zeitstempel wird nicht bewertet', ueber([schritt('Bauen', 0, mit_zeit=False)]) == []))
    cases.append(('Schluessel mit Gedankenstrich im Schrittnamen findet sein Budget',
                  ueber([schritt('Freshness Indexe — Rebuild', 121)]) == ['Freshness Indexe — Rebuild']
                  and ueber([schritt('Freshness Indexe — Rebuild', 120)]) == []))
    laufend = {'name': 'Bauen', 'status': 'in_progress', 'conclusion': None,
               'started_at': '2026-10-10T12:00:00Z'}
    jetzt = zeit('2026-10-10T12:03:00Z')
    cases.append(('laufender Schritt zaehlt mit jetzt als Ende: 180 s gegen Grenze 150 s ist rot',
                  ueber([laufend], jetzt=jetzt) == ['Bauen']))
    cases.append(('laufender Schritt im Budget (120 s) ist ok',
                  ueber([laufend], jetzt=zeit('2026-10-10T12:02:00Z')) == []))
    cases.append(('laufender Schritt ohne jetzt wird nicht bewertet',
                  ueber([laufend]) == []))
    cases.append(('wartender Schritt (pending) wird nicht bewertet',
                  ueber([{'name': 'Bauen', 'status': 'pending', 'conclusion': None}], jetzt=jetzt) == []))
    offen_pending = [{'name': 'Vor', 'status': 'completed', 'conclusion': 'success'},
                     {'name': 'Bauen', 'status': 'queued', 'conclusion': None},
                     {'name': 'Laufzeitbudget', 'status': 'in_progress', 'conclusion': None, 'started_at': 'x'},
                     {'name': 'Spaeter', 'status': 'pending', 'conclusion': None}]
    cases.append(('offener Schritt vor dem Gate wird erkannt, spaetere nicht',
                  [s['name'] for s in offene_schritte(offen_pending, 'Laufzeitbudget')] == ['Bauen']))
    cases.append(('laufender Schritt mit Startzeit ist nicht offen',
                  offene_schritte([laufend], 'Laufzeitbudget') == []))
    streng = dict(cfg, factor=0, checkout_factor=0, floor_s=0)
    cases.append(('Mutation: Faktor 0 und Untergrenze 0 macht jeden Schritt ab 1 s rot',
                  ueber([schritt('Bauen', 1), schritt('Klein', 1)], cfg=streng) == ['Bauen', 'Klein']))

    class A:
        pass

    def args(**kw):
        a = A()
        a.event, a.job_status, a.job, a.workflow, a.self_step = 'pull_request', 'success', 'check', 'w.yml', 'Laufzeitbudget'
        a.ref, a.run_id, a.run_url = 'refs/heads/main', 1, 'u'
        for k, v in kw.items():
            setattr(a, k, v)
        return a

    def antwort(*schritte):
        return {'jobs': [{'name': 'check', 'steps': list(schritte)}]}

    gut = antwort(schritt('Bauen', 100))
    laufend_neu = {'name': 'Neu', 'status': 'in_progress', 'conclusion': None, 'started_at': '2026-10-10T12:00:00Z'}
    schlecht = antwort(schritt('Bauen', 200))
    stumm = io.StringIO()
    alt_out, alt_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = stumm
    try:
        r_ok = pruefe(args(), cfg, gut)
        r_pr = pruefe(args(), cfg, schlecht)
        r_push = pruefe(args(event='push'), cfg, schlecht)
        r_rot = pruefe(args(job_status='failure'), cfg, schlecht)
        r_keinjob = pruefe(args(job='gibt-es-nicht'), cfg, gut)
        r_leer = pruefe(args(), cfg, antwort())
        r_keinjob_push = pruefe(args(event='push', job='gibt-es-nicht'), cfg, gut)
        r_fehlt_rot = pruefe(args(job_status='failure', job='gibt-es-nicht'), cfg, gut)
        r_ungemessen = pruefe(args(), cfg, antwort(schritt('Bauen', 100), {'name': 'Haengt', 'status': 'queued', 'conclusion': None},
                                                   {'name': 'Laufzeitbudget', 'status': 'in_progress', 'conclusion': None, 'started_at': 'x'}))
        gesendet2 = []
        r_push_ungemessen = pruefe(args(event='push'), cfg, antwort(schritt('Bauen', 200), {'name': 'Haengt', 'status': 'queued', 'conclusion': None},
                                                                    {'name': 'Laufzeitbudget', 'status': 'in_progress', 'conclusion': None, 'started_at': 'x'}),
                                   kommentar=gesendet2.append)
        # laufender Schritt, Start 12:00:00, jetzt 12:00:05: 5 s gegen die Grenze 10 s ist ok, auch wenn die Uhr weiterlaeuft
        r_jetzt = pruefe(args(jetzt=zeit('2026-10-10T12:00:05Z'), job='lauf'), cfg,
                         {'jobs': [{'name': 'lauf', 'steps': [laufend_neu, {'name': 'Laufzeitbudget', 'status': 'in_progress', 'conclusion': None, 'started_at': '2026-10-10T12:00:05Z'}]}]})
        r_uebersprungen = pruefe(args(), cfg, antwort(schritt('Bauen', 100), {'name': 'Bedingt', 'status': 'completed', 'conclusion': 'skipped'}))
        gesendet = []
        pruefe(args(event='push'), cfg, schlecht, kommentar=gesendet.append)
        pruefe(args(event='push', ref='refs/heads/anderer'), cfg, schlecht, kommentar=gesendet.append)
        pruefe(args(event='pull_request'), cfg, schlecht, kommentar=gesendet.append)
    finally:
        sys.stdout, sys.stderr = alt_out, alt_err
    cases.append(('PR im Budget: Exit 0', r_ok == 0))
    cases.append(('PR ueber Grenze: Exit 1', r_pr == 1))
    cases.append(('push ueber Grenze: Exit 0, nichts wird rot', r_push == 0))
    cases.append(('PR mit schon rotem Job: Exit 0, keine zweite Rotfaerbung', r_rot == 0))
    cases.append(('PR, Job nicht in der API-Antwort: Exit 2 (keine Daten ist rot)', r_keinjob == 2))
    cases.append(('PR, Job ohne fertigen Schritt: Exit 2', r_leer == 2))
    cases.append(('push, Job nicht gefunden: nur Warnung, Exit 0', r_keinjob_push == 0))
    cases.append(('PR mit rotem Job und fehlender Messung: Exit 0 (verdeckt nichts)', r_fehlt_rot == 0))
    cases.append(('PR, ein Schritt vor dem Gate nicht messbar: Exit 2', r_ungemessen == 2))
    cases.append(('push, ein Schritt nicht messbar: Bericht und Kommentar bleiben',
                  r_push_ungemessen == 0 and len(gesendet2) == 1 and 'Bauen' in gesendet2[0]))
    cases.append(('Wartezeit zaehlt nicht: args.jetzt zu Beginn, spaetere Auswertung aendert nichts',
                  r_jetzt == 0))
    cases.append(('PR, ein Schritt wegen if uebersprungen (skipped): Exit 0', r_uebersprungen == 0))
    cases.append(('Kommentar ins Sammelticket nur bei Ueberschreitung auf push in main',
                  len(gesendet) == 1 and 'Bauen' in gesendet[0]))

    for kaputt, text in (
            ({k: v for k, v in cfg.items() if k != 'floor_s'}, 'fehlendes Feld floor_s'),
            (dict(cfg, steps={'w.yml/X': {'budget_s': 5}}), 'Eintrag ohne Begruendung'),
            (dict(cfg, steps={'ohne-schraegstrich': cfg['steps']['w.yml/Bauen']}), 'Schluessel ohne Workflow'),
            (dict(cfg, collector_issue='574'), 'Sammelticket keine Zahl')):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'b.json'
            p.write_text(json.dumps(kaputt), encoding='utf-8')
            try:
                lade_budget(p)
                ok = False
            except MessungFehlt:
                ok = True
        cases.append((f'Budgetdatei wird abgelehnt: {text}', ok))
    cases.append(('p90 von 25 Werten ist der 23. Wert', p90(list(range(1, 26))) == 23))

    echt = lade_budget(BUDGET_FILE) if BUDGET_FILE.exists() else None
    cases.append(('die echte Budgetdatei ist gueltig', echt is not None))

    failed = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print(f"  {'OK  ' if ok else 'FAIL'}  {n}")
    if failed:
        print(f'\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}', file=sys.stderr)
        return 1
    print(f'\nSelbsttest bestanden: {len(cases)} Faelle')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Laufzeitbudget der CI-Schritte (#564).')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--measure', action='store_true')
    ap.add_argument('--budget', default=str(BUDGET_FILE))
    ap.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY', ''))
    ap.add_argument('--run-id', default=os.environ.get('GITHUB_RUN_ID', ''))
    ap.add_argument('--attempt', default=os.environ.get('GITHUB_RUN_ATTEMPT', '1'))
    ap.add_argument('--workflow', default='')
    ap.add_argument('--job', default=os.environ.get('GITHUB_JOB', ''))
    ap.add_argument('--event', default=os.environ.get('GITHUB_EVENT_NAME', ''))
    ap.add_argument('--ref', default=os.environ.get('GITHUB_REF', ''))
    ap.add_argument('--job-status', default='success')
    ap.add_argument('--self-step', default='Laufzeitbudget (#564)')
    ap.add_argument('--run-url', default='')
    ap.add_argument('--jobs-json', help='gespeicherte API-Antwort statt der API')
    ap.add_argument('--since', default='')
    ap.add_argument('--branch', default='')
    ap.add_argument('--max-runs', type=int, default=25)
    args = ap.parse_args()
    # Der Start dieses Skripts ist die obere Schranke fuer das Ende des Schritts
    # davor; die Wartezeit der Wiederholungen unten gehoert nicht zu ihm.
    args.jetzt = datetime.now(timezone.utc)

    if args.selftest:
        return selftest()
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or ''
    if args.measure:
        print(json.dumps(messen(args, 10), indent=2, ensure_ascii=True))
        return 0
    if not args.check:
        ap.error('--check, --measure oder --selftest angeben')
    if not args.workflow:
        ap.error('--workflow fehlt')
    erzwingend = args.event == 'pull_request'
    try:
        cfg = lade_budget(args.budget)
        if args.jobs_json:
            try:
                antwort = json.loads(Path(args.jobs_json).read_text(encoding='utf-8'))
            except (OSError, ValueError) as exc:
                raise MessungFehlt(f'API-Antwort nicht lesbar: {exc}')
        else:
            if not (args.repo and args.run_id and token):
                raise MessungFehlt('Repository, Lauf-Nummer oder Token fehlen')
            for versuch in range(6):
                antwort = hole_jobs(args.repo, args.run_id, args.attempt, token)
                try:
                    offen = offene_schritte(eigene_schritte(antwort, args.job), args.self_step)
                except MessungFehlt:
                    break
                if not offen:
                    break
                time.sleep(2)
    except MessungFehlt as exc:
        if erzwingend and args.job_status in ('success', ''):
            print(f'::error title=Laufzeitbudget::Messung nicht moeglich: {exc}', file=sys.stderr)
            return 2
        print(f'::warning title=Laufzeitbudget::Messung nicht moeglich: {exc}')
        return 0
    kommentar = (lambda text: kommentiere(args.repo, cfg['collector_issue'], text, token)) if token else None
    return pruefe(args, cfg, antwort, kommentar)


if __name__ == '__main__':
    sys.exit(main())
