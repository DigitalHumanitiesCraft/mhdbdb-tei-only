#!/usr/bin/env python3
"""
ci-lokal.py: die Pruefschritte der CI vor dem Push lokal fahren (#726).

Anlass: ein CI-Gate, das vor dem Push nicht lokal lief, hat viermal eine
Pipeline-Runde gekostet (fehlerjournal.md, Fehler 9, 103, 115, 118; zweimal
check-doc-inventories.py, einmal check-author-refs.py). Die Ursache war jedes
Mal dieselbe: die Session zog die Gates aus einer Liste im Kopf. Dieses Skript
liest die Workflows selbst, waehlt die aus, die bei einem PR liefen, und fuehrt
deren `run:`-Schritte lokal aus. Die Liste im Kopf entfaellt.

## Was es tut

1. Es nimmt jeden Workflow, der auf `pull_request` triggert, und wertet dessen
   `paths`/`paths-ignore` gegen die geaenderten Dateien aus: `git diff
   --name-only <basis>...HEAD`, dazu uncommittete und untracked Dateien des
   Working Trees (`--ohne-working-tree` schaltet das ab). Was der Filter nicht
   trifft, steht als "nicht betroffen" in der Ausgabe.
2. Jeder `run:`-Schritt jedes PR-Workflows muss in der Tabelle KLASSEN stehen
   (auch in einem Workflow, der gerade nicht betroffen ist). Schluessel ist
   Workflow-Datei, Job und Schrittname (ohne Namen `run:<hash>`), dazu ein Hash
   aus run-Text, Schritt-`if` und Job-`if`. Ein Schritt ohne Eintrag und ein
   Schritt, dessen Hash nicht mehr passt, sind ein HARTER FEHLER (Exit 2, nichts
   laeuft). Das ist der Zweck: ein neuer oder geaenderter CI-Schritt darf nicht
   still durchrutschen. Verwaiste Eintraege (Schritt gibt es nicht mehr) werden
   nur gemeldet.
3. Klassen: `lokal` (wird gefahren), `lokal-lang` (ueber etwa eine Minute,
   laeuft nur mit `--lang`), `ersetzt` (das Skript liefert die Ausgaben des
   Schritts selbst, hier der Diff-Base-Schritt), `ausgelassen` (mit Grund).
   Ein `lokal`-Schritt darf keinen `${{ }}`-Ausdruck behalten, der sich nicht
   ersetzen laesst: das ist ein harter Fehler, die Klasse muss dann
   `ausgelassen` sein. Ersetzt werden `github.event_name` (immer
   `pull_request`), `runner.temp` und `steps.<id>.outputs.<name>` eines
   `ersetzt`-Schritts (`sha` ist der merge-base mit der Basis, `naming_changed`
   wird aus den geaenderten Dateien gerechnet). Jede Ersetzung steht in der
   Ausgabe.
4. Die Schritte laufen in Git Bash (`bash -e <datei>`, wie der GitHub-Default),
   mit der `env` aus Workflow, Job und Schritt. Je Schritt eine Zeile, am Ende
   eine Summe mit Nenner. Exit 1, sobald ein Schritt rot ist.

## Aufruf

    python scripts/audit/ci-lokal.py --trocken       # nur auflisten, nichts fahren
    python scripts/audit/ci-lokal.py                 # alles ausser lokal-lang
    python scripts/audit/ci-lokal.py --lang          # auch die Langlaeufer
    python scripts/audit/ci-lokal.py --workflow no-cdn-check
    python scripts/audit/ci-lokal.py --basis origin/main --ohne-filter
    python scripts/audit/ci-lokal.py --ereignis push # direkter Push auf main ohne PR (push-Trigger,
                                                     # branches- und paths-Filter); Default pull_request

Tests: python scripts/audit/test_ci_lokal.py

## Grenzen (bewusst)

- Die Schritte schreiben ins Working Tree, wie in der CI (Freshness-Schritte:
  Rebuild, dann `git diff` gegen den Index). Ein rotes Freshness-Gate heisst
  dann: das Ergebnis des Rebuilds ist jetzt im Working Tree und gehoert in den
  Commit. Uncommittete Quellaenderungen sieht ein solches Gate gegen den Index,
  nicht gegen den PR-Stand: vor dem Lauf committen.
- Abhaengigkeiten (lxml, rnc2rng aus requirements.txt) werden nie installiert.
  Fehlt eine, ist der Schritt rot mit der Fehlermeldung des Schritts.
- `npm test` hat in CLAUDE.md eine eigene Pflicht und steht in keinem
  PR-Workflow. Kaeme ein solcher Schritt dazu, gehoert er in `lokal-lang`.
- Braucht PyYAML (steht in der Python-Installation). Fehlt es: Meldung, Exit 2,
  kein pip install. Dann entscheidet die aufrufende Session, ob ein minimaler
  eigener Leser gebaut wird.
"""
import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Klassifikation
# ---------------------------------------------------------------------------
#
# (datei, job, schluessel, hash, klasse, grund, extra)
# `schluessel` ist der Schrittname, ohne Namen `run:<hash12 des run-Texts>`.
# `hash` ist ein Fingerabdruck aus run-Text, Schritt-if und Job-if. Aendert
# sich einer davon, ist der Schritt neu zu klassifizieren. Neue Zeilen liefert
# der harte Fehler selbst (er druckt den Eintrag zum Einfuegen).
# `extra`: {'ersatz': '<bash>'} fuehrt statt des run-Texts diesen Befehl aus.

Eintrag = namedtuple('Eintrag', 'datei job schluessel hash klasse grund extra')


def E(datei, job, schluessel, hash_, klasse, grund, **extra):
    return Eintrag(datei, job, schluessel, hash_, klasse, grund, extra)


KLASSEN_WERTE = ('lokal', 'lokal-lang', 'ersetzt', 'ausgelassen')

EM = '\u2014'  # die Schrittnamen in data-integrity.yml tragen einen Em-Dash

KLASSEN = []  # wird unten gefuellt (siehe TABELLE am Dateiende)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def git(repo, *args, check=True):
    res = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if check and res.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)} ist fehlgeschlagen: '
                           f'{res.stderr.decode("utf-8", "replace").strip()}')
    return res


def glob_regex(muster):
    """GitHub-Glob (paths-Filter) als Regex: `*` ohne `/`, `**` mit, `**/` auch leer."""
    i, out = 0, []
    while i < len(muster):
        c = muster[i]
        if muster.startswith('**/', i):
            out.append('(?:.*/)?')
            i += 3
        elif muster.startswith('**', i):
            out.append('.*')
            i += 2
        elif c == '*':
            out.append('[^/]*')
            i += 1
        elif c == '?':
            # GitHub: null oder ein Vorkommen des vorigen Zeichens
            if out:
                out[-1] = f'(?:{out[-1]})?'
            i += 1
        elif c == '[' and muster.find(']', i + 1) > i:
            j = muster.find(']', i + 1)
            inhalt = muster[i + 1:j]
            if inhalt.startswith('!'):
                inhalt = '^' + inhalt[1:]
            out.append(f'[{inhalt}]')
            i = j + 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile('^' + ''.join(out) + '$')


def pfad_trifft(muster_liste, pfad):
    """Reihenfolge zaehlt: ein spaeteres `!`-Muster nimmt einen Treffer wieder weg."""
    treffer = False
    for m in muster_liste:
        neg = m.startswith('!')
        if glob_regex(m[1:] if neg else m).match(pfad):
            treffer = not neg
    return treffer


def ref_greift(filt, ereignis, branch):
    """Nur fuer push: greift der branches/tags-Filter fuer einen Push auf `branch`?"""
    if ereignis != 'push' or not filt:
        return True
    if 'branches' in filt:
        return any(glob_regex(m).match(branch) for m in filt['branches'])
    if 'branches-ignore' in filt:
        return not any(glob_regex(m).match(branch) for m in filt['branches-ignore'])
    # nur tags/tags-ignore: ein Branch-Push loest den Workflow nicht aus
    return not ('tags' in filt or 'tags-ignore' in filt)


def filter_greift(filt, dateien):
    """(greift, Beispieltreffer). Ohne Pfadfilter laeuft der Workflow immer."""
    if not filt or not ('paths' in filt or 'paths-ignore' in filt):
        return True, []
    if 'paths' in filt:
        treffer = [d for d in dateien if pfad_trifft(filt['paths'], d)]
    else:
        treffer = [d for d in dateien if not pfad_trifft(filt['paths-ignore'], d)]
    return bool(treffer), treffer


def schritt_hash(run, wenn, job_wenn):
    roh = f'{run}\n--if--\n{wenn or ""}\n--job-if--\n{job_wenn or ""}'
    return hashlib.sha256(roh.encode('utf-8')).hexdigest()[:12]


AUSDRUCK = re.compile(r'\$\{\{(.*?)\}\}', re.S)


def ersetze(text, ctx):
    """(neuer Text, [(Ausdruck, Wert)], [nicht ersetzbare Ausdruecke])."""
    ersetzt, offen = [], []

    def sub(m):
        ausdruck = ' '.join(m.group(1).split())
        if ausdruck in ctx:
            ersetzt.append((ausdruck, ctx[ausdruck]))
            return ctx[ausdruck]
        offen.append(ausdruck)
        return m.group(0)

    return AUSDRUCK.sub(sub, text), ersetzt, offen


class NichtAuswertbar(Exception):
    pass


def wertet_aus(ausdruck, ctx):
    """Kleine Auswertung fuer `if:`: always(), success(), A == 'x', A != 'x', && und ||.

    Klammern und alles andere sind NichtAuswertbar; das ist ein harter Fehler
    bei einem Schritt, der laufen soll, nie ein stilles Wahr.
    """
    text = ausdruck.strip()
    m = re.fullmatch(r'\$\{\{(.*)\}\}', text, re.S)
    if m:
        text = m.group(1).strip()
    if '(' in text.replace('always()', '').replace('success()', ''):
        raise NichtAuswertbar(f'Klammern in if: {ausdruck!r}')
    for oder in text.split('||'):
        if all(_atom(a.strip(), ctx) for a in oder.split('&&')):
            return True
    return False


def _atom(a, ctx):
    if a in ('always()', 'success()', 'true'):
        return True
    if a == 'false':
        return False
    m = re.fullmatch(r"([\w.\-]+)\s*(==|!=)\s*'([^']*)'", a)
    if m and m.group(1) in ctx:
        gleich = ctx[m.group(1)] == m.group(3)
        return gleich if m.group(2) == '==' else not gleich
    raise NichtAuswertbar(f'if-Teil {a!r}')


# ---------------------------------------------------------------------------
# Workflows lesen
# ---------------------------------------------------------------------------

@dataclass
class Schritt:
    datei: str
    job: str
    nr: int
    name: str
    stepid: str
    run: str
    env: dict
    wenn: str
    job_wenn: str
    shell: str
    wd: str
    weiter: bool
    wf_env: dict = field(default_factory=dict)
    job_env: dict = field(default_factory=dict)

    @property
    def hash(self):
        return schritt_hash(self.run, self.wenn, self.job_wenn)

    @property
    def schluessel(self):
        return self.name or 'run:' + hashlib.sha256(self.run.encode('utf-8')).hexdigest()[:12]


@dataclass
class Workflow:
    datei: str
    name: str
    filt: dict
    schritte: list


def lade_yaml():
    try:
        import yaml
    except ImportError:
        sys.exit('ci-lokal: PyYAML (import yaml) fehlt. Kein pip install: die aufrufende Session '
                 'entscheidet, ob ein minimaler eigener Workflow-Leser gebaut wird.')
    return yaml


EREIGNISSE = ('pull_request', 'push')
FILTER_SCHLUESSEL = ('paths', 'paths-ignore', 'branches', 'branches-ignore', 'tags', 'tags-ignore')


def ereignis_filter(doc, ereignis):
    """(hat_ereignis, Filter oder None). PyYAML liest den Schluessel `on` als True."""
    on = doc.get('on', doc.get(True))
    if on is None:
        return False, None
    if isinstance(on, str):
        return on == ereignis, None
    if isinstance(on, list):
        return ereignis in on, None
    if ereignis not in on:
        return False, None
    cfg = on[ereignis] or {}
    filt = {k: [str(x) for x in cfg[k]] for k in FILTER_SCHLUESSEL if cfg.get(k)}
    return True, (filt or None)


def lade_workflows(verz):
    """Alle Workflows mit pull_request- ODER push-Trigger; die Klassifikation gilt fuer beide."""
    yaml = lade_yaml()
    out = []
    for pfad in sorted(Path(verz).glob('*.yml')):
        doc = yaml.safe_load(pfad.read_text(encoding='utf-8'))
        filt = {e: ereignis_filter(doc, e) for e in EREIGNISSE}
        if not any(hat for hat, _ in filt.values()):
            continue
        wf_env = {k: str(v) for k, v in (doc.get('env') or {}).items()}
        wf_shell = ((doc.get('defaults') or {}).get('run') or {}).get('shell')
        schritte = []
        for jobname, job in (doc.get('jobs') or {}).items():
            job_shell = ((job.get('defaults') or {}).get('run') or {}).get('shell') or wf_shell
            job_env = {k: str(v) for k, v in (job.get('env') or {}).items()}
            for nr, st in enumerate(job.get('steps') or [], 1):
                if 'run' not in st:
                    continue
                schritte.append(Schritt(
                    datei=pfad.name, job=jobname, nr=nr,
                    name=str(st['name']) if st.get('name') is not None else '',
                    stepid=str(st.get('id') or ''), run=str(st['run']),
                    env={k: str(v) for k, v in (st.get('env') or {}).items()},
                    wenn=str(st['if']) if 'if' in st else '',
                    job_wenn=str(job['if']) if 'if' in job else '',
                    shell=str(st.get('shell') or job_shell or ''),
                    wd=str(st.get('working-directory') or ''),
                    weiter=bool(st.get('continue-on-error')),
                    wf_env=wf_env, job_env=job_env))
        out.append(Workflow(pfad.name, str(doc.get('name') or pfad.stem), filt, schritte))
    return out


# ---------------------------------------------------------------------------
# Geaenderte Dateien und Basis
# ---------------------------------------------------------------------------

def geaenderte_dateien(repo, basis, working_tree=True):
    """(merge-base-SHA, sortierte Pfade). Fehler als RuntimeError."""
    if git(repo, 'rev-parse', '--verify', '--quiet', f'{basis}^{{commit}}', check=False).returncode != 0:
        raise RuntimeError(f'Basis "{basis}" gibt es nicht (git fetch origin?)')
    mb = git(repo, 'merge-base', basis, 'HEAD').stdout.decode().strip()
    pfade = set()
    quellen = [('diff', '--name-only', '-z', '--no-renames', '--no-ext-diff', f'{basis}...HEAD')]
    if working_tree:
        quellen.append(('diff', '--name-only', '-z', '--no-renames', '--no-ext-diff', 'HEAD'))
        quellen.append(('ls-files', '-z', '--others', '--exclude-standard'))
    for q in quellen:
        pfade.update(p for p in git(repo, *q).stdout.decode('utf-8', 'replace').split('\0') if p)
    return mb, sorted(pfade)


# ---------------------------------------------------------------------------
# Planung
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    fehler: list = field(default_factory=list)
    warnungen: list = field(default_factory=list)
    nicht_betroffen: list = field(default_factory=list)  # (datei, Grund)
    zeilen: list = field(default_factory=list)           # Aktionen in Reihenfolge
    nenner: int = 0


def vorschlag_zeile(s, klasse='?', grund='?'):
    return (f"E({s.datei!r}, {s.job!r}, {s.schluessel!r}, {s.hash!r}, {klasse!r}, {grund!r}),")


def plane(workflows, tabelle, mb, dateien, optionen):
    """Entscheidet je Schritt: lauf, lang, aus, ersetzt, skip, und sammelt harte Fehler."""
    plan = Plan()
    index = {(e.datei, e.job, e.schluessel): e for e in tabelle}
    gesehen = set()
    rt = optionen['runner_temp']
    naming = any(d == 'data/naming-index.json.gz' or d.startswith('scripts/ingest/naming/')
                 for d in dateien)
    basis_ctx = {'sha': mb, 'naming_changed': 'true' if naming else 'false'}

    # 1. Klassifikation aller PR-Workflows, betroffen oder nicht
    klasse_von = {}
    for wf in workflows:
        schluessel_je_job = {}
        for s in wf.schritte:
            k = (s.datei, s.job, s.schluessel)
            gesehen.add(k)
            if k in schluessel_je_job:
                plan.fehler.append(f'{s.datei}/{s.job}: Schrittname "{s.schluessel}" kommt zweimal vor, '
                                   'der Schluessel ist nicht eindeutig')
            schluessel_je_job[k] = True
            e = index.get(k)
            if e is None:
                plan.fehler.append(f'nicht klassifiziert: {s.datei} / {s.job} / {s.schluessel}\n'
                                   f'      Eintrag in KLASSEN ergaenzen, etwa: {vorschlag_zeile(s)}')
            elif e.klasse not in KLASSEN_WERTE:
                plan.fehler.append(f'{s.datei} / {s.job} / {s.schluessel}: unbekannte Klasse {e.klasse!r}')
            elif e.hash != s.hash:
                plan.fehler.append(f'run-Text geaendert (Hash {e.hash} -> {s.hash}): {s.datei} / {s.job} / '
                                   f'{s.schluessel}\n      Neu klassifizieren, etwa: '
                                   f'{vorschlag_zeile(s, e.klasse, e.grund)}')
            else:
                klasse_von[k] = e
    for k in sorted(set(index) - gesehen):
        plan.warnungen.append(f'verwaister Eintrag in KLASSEN (Schritt gibt es nicht mehr): {" / ".join(k)}')

    # 2. Auswahl
    gewaehlt = []
    for wf in workflows:
        if optionen['workflow'] and optionen['workflow'] not in (wf.datei, Path(wf.datei).stem, wf.name):
            plan.nicht_betroffen.append((wf.datei, 'nicht gewaehlt (--workflow)'))
            continue
        ereignis = optionen['ereignis']
        hat, filt = wf.filt[ereignis]
        if not hat:
            plan.nicht_betroffen.append((wf.datei, f'kein {ereignis}-Trigger'))
        elif not ref_greift(filt, ereignis, optionen['branch']):
            plan.nicht_betroffen.append((wf.datei, f'{ereignis}-Filter nennt "{optionen["branch"]}" nicht: {filt}'))
        elif optionen['ohne_filter']:
            gewaehlt.append(wf)
        else:
            greift, treffer = filter_greift(filt, dateien)
            if greift:
                gewaehlt.append(wf)
            else:
                plan.nicht_betroffen.append((wf.datei, f'Pfadfilter greift nicht {filt}'))

    # 3. Aktionen
    steps_ctx = {}  # Ausgaben der ersetzt-Schritte: (stepid) -> dict
    for wf in gewaehlt:
        for s in wf.schritte:
            e = klasse_von.get((s.datei, s.job, s.schluessel))
            if e is None:
                continue
            plan.nenner += 1
            if e.klasse == 'ausgelassen':
                plan.zeilen.append(('aus', s, e, [], None))
                continue
            if e.klasse == 'ersetzt':
                if s.stepid:
                    steps_ctx[(s.datei, s.job, s.stepid)] = basis_ctx
                plan.zeilen.append(('ersetzt', s, e, [(f'steps.{s.stepid}.outputs.*', 'aus Basis und Dateiliste')], None))
                continue
            plan.zeilen.append(_plane_lokal(plan, s, e, steps_ctx, rt, optionen))
    return plan


def _plane_lokal(plan, s, e, steps_ctx, rt, optionen):
    ctx = {'github.event_name': optionen['ereignis'], 'runner.temp': rt}
    for (d, j, sid), ausgaben in steps_ctx.items():
        if d == s.datei and j == s.job:
            for n, v in ausgaben.items():
                ctx[f'steps.{sid}.outputs.{n}'] = v
    name = f'{s.datei} / {s.job} / {s.schluessel}'
    if s.shell and s.shell.split()[0] not in ('bash', 'sh'):
        plan.fehler.append(f'{name}: shell "{s.shell}" laeuft lokal nicht, Klasse muss ausgelassen sein')
        return ('fehler', s, e, [], None)
    try:
        if s.job_wenn and not wertet_aus(s.job_wenn, ctx):
            return ('skip', s, e, [], f'Job-if falsch: {s.job_wenn}')
        if s.wenn and not wertet_aus(s.wenn, ctx):
            return ('skip', s, e, [], f'if falsch: {s.wenn}')
    except NichtAuswertbar as ex:
        plan.fehler.append(f'{name}: if nicht auswertbar ({ex}), Klasse muss ausgelassen sein')
        return ('fehler', s, e, [], None)
    text = e.extra.get('ersatz', s.run)
    ersetzungen = []
    text, ers, offen = ersetze(text, ctx)
    ersetzungen += ers
    env = {}
    for quelle in (s.wf_env, s.job_env, s.env):
        for k, v in quelle.items():
            v2, ers, off2 = ersetze(v, ctx)
            ersetzungen += ers
            offen += off2
            env[k] = v2
    wd, ers, off3 = ersetze(s.wd, ctx) if s.wd else ('', [], [])
    offen += off3
    if offen:
        plan.fehler.append(f'{name}: nicht ersetzbarer Ausdruck {sorted(set(offen))} in einem Schritt der '
                           f'Klasse {e.klasse}; Klasse muss ausgelassen sein')
        return ('fehler', s, e, ersetzungen, None)
    ersetzungen = list(dict.fromkeys(ersetzungen))
    if e.klasse == 'lokal-lang' and not optionen['lang']:
        return ('lang', s, e, ersetzungen, None)
    env.setdefault('GITHUB_EVENT_NAME', optionen['ereignis'])
    return ('lauf', s, e, ersetzungen, {'text': text, 'env': env, 'wd': wd})


# ---------------------------------------------------------------------------
# Ausfuehren
# ---------------------------------------------------------------------------

def finde_bash():
    """Git Bash, nie das WSL-bash aus System32 oder WindowsApps."""
    if os.environ.get('CI_LOKAL_BASH'):
        return os.environ['CI_LOKAL_BASH']
    for kandidat in (r'C:\Program Files\Git\bin\bash.exe', r'C:\Program Files\Git\usr\bin\bash.exe'):
        if os.path.exists(kandidat):
            return kandidat
    gefunden = shutil.which('bash')
    if gefunden and not re.search(r'(?i)system32|windowsapps', gefunden):
        return gefunden
    sys.exit('ci-lokal: keine Git Bash gefunden (CI_LOKAL_BASH setzen).')


def fahre(s, aktion, repo, rt, nr, timeout):
    """(gruen: bool, Dauer, Ausgabe)."""
    skript = Path(rt) / f'schritt{nr}.sh'
    skript.write_text(aktion['text'], encoding='utf-8', newline='\n')
    env = os.environ.copy()
    env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                'GITHUB_EVENT_NAME': 'pull_request', 'RUNNER_TEMP': Path(rt).as_posix(),
                'GITHUB_OUTPUT': (Path(rt) / 'github_output').as_posix(),
                'GITHUB_ENV': (Path(rt) / 'github_env').as_posix(),
                'GITHUB_STEP_SUMMARY': (Path(rt) / 'step_summary').as_posix()})
    env.update(aktion['env'])
    cwd = Path(repo) / aktion['wd'] if aktion['wd'] else Path(repo)
    start = time.time()
    try:
        res = subprocess.run([finde_bash(), '-e', skript.as_posix()], cwd=str(cwd), env=env,
                             capture_output=True, timeout=timeout)
        ausgabe = (res.stdout + res.stderr).decode('utf-8', 'replace')
        return res.returncode == 0, time.time() - start, ausgabe
    except subprocess.TimeoutExpired:
        return False, time.time() - start, f'Timeout nach {timeout} s'


def sek(x):
    return f'{x:.1f}'.replace('.', ',') + ' s'


def melde_fehler(plan):
    print(f'HARTER FEHLER: {len(plan.fehler)} Befund(e), nichts wurde gefahren.')
    for f in plan.fehler:
        print(f'  - {f}')


def bericht(plan, trocken, repo, timeout, rt, verbose):
    zaehler = {'lauf': 0, 'rot': 0, 'aus': 0, 'ersetzt': 0, 'lang': 0, 'skip': 0}
    gesamt = len(plan.zeilen)
    for i, (art, s, e, ers, aktion) in enumerate(plan.zeilen, 1):
        kopf = f'{s.datei[:-4]}/{s.job}  {s.schluessel}'
        if art == 'aus':
            zaehler['aus'] += 1
            print(f'  ausgelassen  {kopf}\n               Grund: {e.grund}')
        elif art == 'ersetzt':
            zaehler['ersetzt'] += 1
            print(f'  ersetzt      {kopf}\n               {e.grund}')
        elif art == 'skip':
            zaehler['skip'] += 1
            print(f'  uebersprungen {kopf} ({aktion})')
        elif art == 'lang':
            zaehler['lang'] += 1
            print(f'  lang-fehlt   {kopf}  (laeuft nur mit --lang; {e.grund})')
        elif trocken:
            zaehler['lauf'] += 1
            zusatz = f'  [{e.klasse}]' + (' (Ersatzbefehl)' if 'ersatz' in e.extra else '')
            print(f'  lokal        {kopf}{zusatz}')
            for a, w in ers:
                print(f'               Ersetzung: ${{{{ {a} }}}} -> {w}')
        else:
            print(f'  [{i}/{gesamt}] {kopf} ...', end='', flush=True)
            gruen, dauer, ausgabe = fahre(s, aktion, repo, rt, i, timeout)
            zaehler['lauf'] += 1
            ist_rot = (not gruen) and not s.weiter
            if not gruen:
                zaehler['rot'] += 1 if ist_rot else 0
            print(f' {"OK" if gruen else ("ROT" if ist_rot else "rot, continue-on-error")} ({sek(dauer)})')
            for a, w in ers:
                print(f'               Ersetzung: ${{{{ {a} }}}} -> {w}')
            if (not gruen) or verbose:
                zeilen = ausgabe.rstrip().splitlines()
                for z in (zeilen if verbose else zeilen[-30:]):
                    print(f'               | {z}')
    n = plan.nenner
    verb = 'wuerden laufen' if trocken else 'gelaufen'
    teile = [f'{zaehler["lauf"]} von {n} {verb}' + ('' if trocken else f' (davon {zaehler["rot"]} rot)')]
    teile.append(f'{zaehler["aus"]} ausgelassen')
    teile.append(f'{zaehler["ersetzt"]} ersetzt')
    teile.append(f'{zaehler["lang"]} lokal-lang nicht gelaufen (--lang)')
    teile.append(f'{zaehler["skip"]} per if uebersprungen')
    print('Summe: ' + ', '.join(teile))
    return zaehler


def main(argv=None, tabelle=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--basis', default='origin/main', help='Vergleichsstand (Default origin/main)')
    p.add_argument('--trocken', action='store_true', help='nur auflisten, nichts fahren')
    p.add_argument('--lang', action='store_true', help='auch die Schritte der Klasse lokal-lang fahren')
    p.add_argument('--workflow', help='nur diesen Workflow (Dateiname, Stamm oder name:)')
    p.add_argument('--ereignis', choices=EREIGNISSE, default='pull_request',
                   help='pull_request (Default) oder push: direkter Push auf --push-branch, ohne PR')
    p.add_argument('--push-branch', default='main', help=argparse.SUPPRESS)
    p.add_argument('--ohne-filter', action='store_true', help='paths-Filter ignorieren, alle Workflows des Ereignisses nehmen')
    p.add_argument('--ohne-working-tree', action='store_true',
                   help='uncommittete und untracked Dateien nicht in die Dateiliste nehmen')
    p.add_argument('--timeout', type=int, default=1800, help='Sekunden je Schritt (Default 1800)')
    p.add_argument('-v', '--ausfuehrlich', action='store_true', help='Ausgabe auch gruener Schritte zeigen')
    p.add_argument('--repo', default=str(REPO), help=argparse.SUPPRESS)
    p.add_argument('--workflows', default=None, help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    tabelle = KLASSEN if tabelle is None else tabelle
    repo = Path(args.repo)
    wfdir = Path(args.workflows) if args.workflows else repo / '.github' / 'workflows'

    workflows = lade_workflows(wfdir)
    try:
        mb, dateien = geaenderte_dateien(repo, args.basis, not args.ohne_working_tree)
    except RuntimeError as ex:
        print(f'HARTER FEHLER: {ex}')
        return 2
    rt = tempfile.mkdtemp(prefix='ci-lokal-')
    try:
        opt = {'workflow': args.workflow, 'ohne_filter': args.ohne_filter, 'lang': args.lang,
               'ereignis': args.ereignis, 'branch': args.push_branch,
               'runner_temp': Path(rt).as_posix()}
        plan = plane(workflows, tabelle, mb, dateien, opt)
        print(f'Basis {args.basis} (merge-base {mb[:12]}), {len(dateien)} geaenderte Datei(en)'
              + ('' if not args.ohne_working_tree else ' (ohne Working Tree)'))
        for w in plan.warnungen:
            print(f'WARNUNG: {w}')
        if plan.fehler:
            melde_fehler(plan)
            return 2
        for datei, grund in plan.nicht_betroffen:
            print(f'  nicht betroffen: {datei} ({grund})')
        zaehler = bericht(plan, args.trocken, repo, args.timeout, rt, args.ausfuehrlich)
        return 1 if zaehler['rot'] else 0
    finally:
        shutil.rmtree(rt, ignore_errors=True)


# ---------------------------------------------------------------------------
# Tabelle (Stand der Workflows in diesem Repo; Schluessel und Hash siehe oben)
# ---------------------------------------------------------------------------

KLASSEN.extend([
    E('data-integrity.yml', 'validate', 'Install dependencies', '2a030a1b5d62',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('data-integrity.yml', 'validate', 'Index version consistency (#47.3)', '7e8b986ffa46',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Dokumentierte Zahlen gegen die Daten (#382/#398)', 'b6a341b93785',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Werk-Identifier und Editionsnachweis gegen works.xml (#399/#486)', '3466a678fb62',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Regenerate RNG from RNC (P2-14 drift check)', '4cdc376514c0',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Fail if committed .rng differs from regenerated .rng', '07a7476d7e56',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Verify TEI P5 version pin', '5171003490d2',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Personennamen im Header gegen persons.xml (#228/#308)', '51e03d315253',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Gattungen im Header gegen works.xml (#495)', '22552db4c476',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Struktur der committeten Indexe (validate-indices.py,', 'ef0734e3328c',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Validate corpus and authority files (P2-13)', 'eb80c6dfea63',
      'lokal-lang', 'RelaxNG-Validierung aller Korpusdateien, in der CI median 212 s'),
    E('data-integrity.yml', 'validate', 'Laufzeitbudget (#564)', '065094f82e50',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('data-integrity.yml', 'freshness', 'Diff-Base bestimmen (#154/#152)', '118c1329753c',
      'ersetzt', 'Diff-Base: HEAD^1 des Merge-Refs gibt es lokal nicht; ci-lokal setzt sha = merge-base mit der Basis und rechnet naming_changed aus der Dateiliste'),
    E('data-integrity.yml', 'freshness', 'Install dependencies', '2a030a1b5d62',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('data-integrity.yml', 'freshness', 'Index-Versions-Bump-Gate (#154)', 'dd602e780f83',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Variants-Flip-Gate (#378, ADR-021)', 'bd124dfe1d36',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Index-Budget Selbsttest (#111)', '2aa603e4051d',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Index-Budget (#111)', '52b5ea415417',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness variants.xml (#125)', 'f0b7f2a7d0b6',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness API (#45)', '92af7ed15553',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness Begriffshilfe (#498)', 'ead27c95ab39',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness lemma-pos (#462)', '0eba4fc4b226',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness Indexe \u2014 Rebuild-and-Compare (#125)', '34265d837028',
      'lokal-lang', 'baut beide Indexe neu, in der CI median 74 s; schreibt data/*.json.gz'),
    E('data-integrity.yml', 'freshness', 'Naming-Index Konsistenz (#152)', '448d1afbc679',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness naming-index \u2014 Rebuild-and-Compare (#152)', 'ce6ce03033dc',
      'ausgelassen', 'braucht github.token und einen Abruf an lindabeutel/Naming-analysis; bei Aenderung am naming-Index von Hand: 01-fetch-and-build-index.py'),
    E('data-integrity.yml', 'freshness', 'Authority cross-reference integrity (#44/#115/#152)', 'a48a3320d203',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Laufzeitbudget (#564)', 'cf3174432ce8',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('data-integrity.yml', 'melden', 'Zustandswechsel melden (#653)', 'd7904ab427d5',
      'ausgelassen', 'Job laeuft nur auf schedule/workflow_dispatch auf main und meldet in #653; github.*-Kontext, kein Gate am PR'),
    E('doc-health.yml', 'doc-health', 'Doku-Health Selbsttest (#641)', '8754faa5aa8d',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('doc-health.yml', 'doc-health', 'Doku-Health Bericht (#641)', '29ed769aff8d',
      'ausgelassen', 'braucht github.token und die Actions/Issue-API; am PR ohne --apply, kein Gate'),
    E('doc-health.yml', 'doc-health', 'Laufzeitbudget (#564)', 'afc324ed78c0',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('file-size-check.yml', 'check', 'Groessenwaechter Selbsttest (#350)', '160d6a6d3ab3',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('file-size-check.yml', 'check', 'Baum mit Groessen aus der API (#564)', 'fdaf09bf482f',
      'ausgelassen', 'holt den Baum ueber die GitHub-Trees-API (github.token); der lokale Lauf misst ohne API'),
    E('file-size-check.yml', 'check', 'Keine committete Datei nahe GitHubs 100-MiB-Wand (#350)', '5f244420a7ca',
      'lokal', 'Ersatzbefehl: ohne --github-tree, das Skript liest lokal git ls-tree', ersatz='python3 scripts/audit/check-file-sizes.py'),
    E('file-size-check.yml', 'check', 'Laufzeitbudget (#564)', '4b4d5ffed79f',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('link-check.yml', 'link-check', 'Link-Check Selbsttest (#653)', 'fb34be0a845a',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Selbsttest der Meldung (#653)', 'a75b0503d3a1',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Links einsammeln (PR)', 'ee5801264eb4',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Externe Links pruefen (#653)', 'b70a458da74e',
      'ausgelassen', 'fragt das Netz ab und laeuft nur ausserhalb des PR (if); am PR ersetzt es der Schritt "Links einsammeln"'),
    E('link-check.yml', 'melden', 'Zustandswechsel melden (#653)', '42ae2274d1de',
      'ausgelassen', 'Job laeuft nur auf schedule/workflow_dispatch auf main und meldet in #653; github.*-Kontext, kein Gate am PR'),
    E('measured-counts.yml', 'measured-counts', 'Install dependencies', '2a030a1b5d62',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('measured-counts.yml', 'measured-counts', 'Gemessene Zahlen gegen ihre Fundstellen (#414)', 'fa202a81054e',
      'lokal-lang', 'parst alle Korpusdateien, rund 263 s (gemessen 10.10.2026, laut Workflow-Kopf)'),
    E('measured-counts.yml', 'measured-counts', 'Laufzeitbudget (#564)', '343a2ed62ba6',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('no-cdn-check.yml', 'check', 'Arbeitsbaum vollstaendig ausser tei/*.tei.xml und data/*.json.gz (#564)', '111aaeeb9117',
      'ausgelassen', 'Kontrollwert fuer den sparse-Checkout der CI; lokal ist der Baum voll'),
    E('no-cdn-check.yml', 'check', 'Diff-Base bestimmen (#292)', 'fc1e1895d189',
      'ersetzt', 'Diff-Base: HEAD^1 des Merge-Refs gibt es lokal nicht; ci-lokal setzt sha = merge-base mit der Basis und rechnet naming_changed aus der Dateiliste'),
    E('no-cdn-check.yml', 'check', 'No external script src or link href in committed HTML (stdlib only)', 'a67d44c1b036',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Em-Dash-Gate Selbsttest (#140/#292)', 'c5ba14510383',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Keine Em-Dashes in HTML/JS/CSS und neuer Markdown-Prosa (#140/#292)', 'c51179832a95',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Inventar-Gate Selbsttest (#329)', 'ac31dfa1dde4',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Laufzeitbudget Selbsttest (#564)', '9fe2ca4d1251',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Specs und Audit-Skripte stehen in ihren Inventaren (#329)', '4de00b0a6c50',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Hilfe-Unterseiten gegen ihre Stände (#417/#537)', '8e9f7af555dc',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Seitenchrome und SEO-Block gegen includes/ und die Seiten (build-pages --check)', 'e151e994d213',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'tei/-Dateinamen fuer doc-count-audit (#564)', '7938597e2558',
      'ausgelassen', 'ZERSTOERT lokal die Korpusdateien: leert alle tei/*.tei.xml (Platzhalter fuer den sparse-Baum der CI); der naechste Schritt laeuft lokal ohne Platzhalter'),
    E('no-cdn-check.yml', 'check', 'Dokumentierte Zahlen gegen die Daten (#382/#398)', 'fd38f967ad76',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Laufzeitbudget (#564)', 'aaced77400fe',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('search-benchmark.yml', 'benchmark', 'Node-Version', '439306f69f71',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('search-benchmark.yml', 'benchmark', 'Aufloesung gegen Budget (#564)', 'bd7bb956bcb2',
      'ausgelassen', 'Zeitbudget, auf die CI-Runner kalibriert: lokal waren 12 von 24 Faellen ueber Budget '
      '(gemessen bei der Erstellung von ci-lokal.py), ohne dass der Code etwas getan haette. '
      'Nach einer Aenderung unter assets/js/search, assets/js/lib oder playground/js/data '
      'von Hand: node scripts/audit/benchmark-search.mjs'),
    E('release-version-check.yml', 'check', 'Check release version consistency', '8be4fc34da97',
      'ausgelassen', 'laeuft nur beim Tag-Push (v*), braucht GITHUB_REF_NAME; weder PR noch Push auf main'),
])

if __name__ == '__main__':
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.exit(main())
