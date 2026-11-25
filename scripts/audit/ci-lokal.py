#!/usr/bin/env python3
"""
ci-lokal.py: die Pruefschritte der CI vor dem Push lokal fahren (#726).

Anlass: ein CI-Gate, das vor dem Push nicht lokal lief, hat wiederholt eine
Pipeline-Runde gekostet (fehlerjournal.md, Fehler 9, 103, 115, 118). Die Session
zog die Gates aus einer Liste im Kopf, oder rief eines ohne seinen `--check`
auf. Dieses Skript liest die Workflows selbst, waehlt die aus, die beim
gewaehlten Ereignis liefen, und fuehrt deren `run:`-Schritte lokal aus. Die
Liste im Kopf entfaellt.

## Was es tut

1. Es nimmt jeden Workflow, der auf das Ereignis triggert (`--ereignis
   pull_request`, Default, oder `push` fuer einen direkten Push auf `main`
   ohne PR), und wertet dessen `paths`/`paths-ignore` (bei `push` auch
   `branches`/`tags`) gegen die geaenderten Dateien aus: `git diff
   --name-only <merge-base>...<sha>`. Geprueft wird der Commit, auf dem HEAD
   beim Start steht, genau das, was gepusht wird: HEAD wird einmal zur SHA
   aufgeloest, Workflows, Dateiliste und Worktree arbeiten alle auf ihr, auch
   wenn eine andere Session dazwischen committet. Was der Filter nicht trifft, steht als "nicht betroffen" in
   der Ausgabe.
2. Jeder `run:`-Schritt jedes Workflows mit `pull_request`- oder `push`-Trigger
   muss in der Tabelle KLASSEN stehen (auch in einem Workflow, der gerade nicht
   betroffen ist, und auch, wenn er nur in einem der beiden Modi vorkommt).
   Schluessel ist Workflow-Datei, Job und Schrittname (ohne Namen
   `run:<hash>`), dazu ein Hash aus run-Text, Schritt-`env`, Job-`env`,
   `if` von Schritt und Job, `shell`, `working-directory`,
   `continue-on-error` und `defaults.run` von Workflow und Job. Ein Schritt
   ohne Eintrag und ein Schritt, dessen Hash nicht mehr passt, sind ein HARTER
   FEHLER (Exit 2, nichts laeuft). Das ist der Zweck: ein neuer oder
   geaenderter CI-Schritt darf nicht still durchrutschen. Verwaiste Eintraege
   (Schritt gibt es nicht mehr) werden nur gemeldet.
3. Klassen: `lokal` (wird gefahren), `lokal-lang` (ueber etwa eine Minute,
   laeuft nur mit `--lang`), `ersetzt` (das Skript liefert die Ausgaben des
   Schritts selbst, hier der Diff-Base-Schritt), `ausgelassen` (mit Grund).
   Ein `lokal`-Schritt darf keinen `${{ }}`-Ausdruck behalten, der sich nicht
   ersetzen laesst: das ist ein harter Fehler, die Klasse muss dann
   `ausgelassen` sein. Ersetzt werden `github.event_name` (der Wert von
   `--ereignis`), `runner.temp` und `steps.<id>.outputs.<name>` eines
   `ersetzt`-Schritts (`sha` ist der merge-base mit der Basis, `naming_changed`
   wird aus den geaenderten Dateien gerechnet). Jede Ersetzung steht in der
   Ausgabe.
4. Jeder Lauf ohne `--trocken` legt mit `git worktree add --detach` einen
   eigenen Worktree des Commits, auf dem HEAD beim Start steht, unter
   `tempfile.mkdtemp()` an, meldet Pfad und SHA am Anfang und faehrt alle
   Schritte dort. Am Ende wird er wieder entfernt, auch
   bei Fehler und bei Ctrl-C. Das Repo des Aufrufers bleibt unberuehrt: die
   Freshness-Schritte schreiben (Rebuild, dann `git diff`), und im Main
   Worktree teilen sich parallele Sessions den Working Tree.
   Ein Kill oder ein Timeout der Harness laesst den Worktree trotzdem zurueck
   (registriert, unter %TEMP%). Deshalb liest jeder Lauf gleich nach dem
   Aufloesen der SHA, vor Workflows und Plan (auch ein Lauf, der danach mit
   Exit 2 endet), `git worktree list --porcelain`, meldet jeden Eintrag
   `ci-lokal-wt-*` direkt unter `tempfile.gettempdir()` und entfernt ihn
   (`worktree remove --force`, `rmtree`, bleibt der Eintrag stehen, nur sein
   eigener Admin-Ordner unter `<git-common-dir>/worktrees/`; nie ein globales
   `worktree prune`) mit der Zeile `Rest eines abgebrochenen Laufs entfernt:
   <pfad>`. Schutz vor dem Entfernen eines Worktrees, den eine
   andere Session gerade nutzt: jeder Lauf schreibt seine PID in
   `ci-lokal.pid` im Git-Verzeichnis seines Worktrees
   (`<repo>/.git/worktrees/<name>/`), nicht in den Worktree, wo sie als
   untracked Datei in `git status` und `git diff` der Freshness-Schritte
   stuende. Entfernt wird nur, wenn die PID eindeutig tot ist (`tasklist` mit rc 0 und
   ohne Zeile fuer die PID, unter POSIX `ProcessLookupError`). Lebt sie, ist
   ihr Status unklar (rc ungleich 0, Exception, Timeout) oder ist die Datei
   nicht lesbar, wird nur gemeldet, bei unklarem Status mit Grund. `--trocken`
   meldet, entfernt nie. Andere Worktrees fasst es nicht an.
   Bleibt eine PID nach einem Absturz einem fremden Prozess zugeteilt, bleibt
   der Rest liegen und wird bei jedem Lauf gemeldet.
5. Trifft die Dateiliste `tei/`, `authority-files/` oder `schema/` und fehlt
   `--lang`, steht eine Zeile `WARNUNG` davor (Pflicht ist `--lang`, im
   Hintergrund, CLAUDE.md, #726). Der Exit-Code aendert sich nicht, die Summe
   nennt die fehlenden `lokal-lang`-Schritte wie sonst.
6. Die Schritte laufen in Git Bash (`bash -e <datei>`, wie der GitHub-Default),
   mit der `env` aus Workflow, Job und Schritt. Je Schritt eine Zeile, am Ende
   eine Summe mit Nenner. Exit 1, sobald ein Schritt rot ist, Exit 2 bei
   hartem Fehler (auch: PyYAML oder Git Bash fehlen).

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

- Geprueft wird nur, was committet ist. Uncommittete oder untracked Dateien im
  Working Tree des Aufrufers werden nicht geprueft, eine Warnzeile sagt das.
  Ein roter Freshness-Schritt heisst: im eigenen Tree den Rebuild fahren und
  committen, wie es die Meldung des Schritts sagt.
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
import json
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
# `hash` ist ein Fingerabdruck aus allem, was die Ausfuehrung bestimmt (siehe
# Schritt.hash: run, env, if, shell, working-directory, continue-on-error,
# defaults.run). Aendert sich einer davon, ist der Schritt neu zu klassifizieren.
# Neue Zeilen liefert der harte Fehler selbst (er druckt den Eintrag mit `?`).
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
    # GIT_OPTIONAL_LOCKS=0: `git status` im Repo des Aufrufers nimmt sonst index.lock
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    res = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, env=env)
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


def schritt_hash(teile):
    """Fingerabdruck eines Schritts aus allem, was seine Ausfuehrung bestimmt (dict, sortiert)."""
    roh = json.dumps(teile, sort_keys=True, ensure_ascii=True)
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
    wf_defaults: dict = field(default_factory=dict)   # defaults.run des Workflows (roh)
    job_defaults: dict = field(default_factory=dict)  # defaults.run des Jobs (roh)
    shell_schritt: str = ''                           # shell, wie im Schritt selbst geschrieben
    wd_schritt: str = ''                              # working-directory, wie im Schritt geschrieben

    @property
    def hash(self):
        return schritt_hash({
            'run': self.run, 'env': self.env, 'job_env': self.job_env, 'wf_env': self.wf_env,
            'if': self.wenn, 'job_if': self.job_wenn, 'shell': self.shell_schritt,
            'wd': self.wd_schritt, 'continue_on_error': self.weiter,
            'wf_defaults': self.wf_defaults, 'job_defaults': self.job_defaults})

    @property
    def schluessel(self):
        return self.name or 'run:' + hashlib.sha256(self.run.encode('utf-8')).hexdigest()[:12]


@dataclass
class Workflow:
    datei: str
    name: str
    filt: dict
    schritte: list


class HartFehler(Exception):
    """Eingabe oder Umgebung unbrauchbar: Exit 2, nie Exit 1 (das heisst "Schritt rot")."""


def lade_yaml():
    try:
        import yaml
    except ImportError:
        raise HartFehler('PyYAML (import yaml) fehlt. Kein pip install: die aufrufende Session '
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


def workflow_texte(repo, verz=None, rev='HEAD'):
    """{Dateiname: Text}. Ohne `verz` aus den Blobs von `rev`, also das, was gepusht wird."""
    if verz:
        return {p.name: p.read_text(encoding='utf-8') for p in sorted(Path(verz).glob('*.yml'))}
    namen = git(repo, 'ls-tree', '-r', '--name-only', '-z', rev, '--', '.github/workflows/')
    out = {}
    for n in sorted(x for x in namen.stdout.decode('utf-8').split('\0') if x.endswith('.yml')):
        out[Path(n).name] = git(repo, 'show', f'{rev}:{n}').stdout.decode('utf-8')
    return out


def lade_workflows(texte):
    """Alle Workflows mit pull_request- ODER push-Trigger; die Klassifikation gilt fuer beide."""
    yaml = lade_yaml()
    out = []
    for dateiname, text in sorted(texte.items()):
        pfad = Path(dateiname)
        doc = yaml.safe_load(text)
        filt = {e: ereignis_filter(doc, e) for e in EREIGNISSE}
        if not any(hat for hat, _ in filt.values()):
            continue
        wf_env = {k: str(v) for k, v in (doc.get('env') or {}).items()}
        wf_def = (doc.get('defaults') or {}).get('run') or {}
        schritte = []
        for jobname, job in (doc.get('jobs') or {}).items():
            job_def = (job.get('defaults') or {}).get('run') or {}
            job_shell = job_def.get('shell') or wf_def.get('shell')
            job_wd = job_def.get('working-directory') or wf_def.get('working-directory')
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
                    wd=str(st.get('working-directory') or job_wd or ''),
                    weiter=bool(st.get('continue-on-error')),
                    wf_env=wf_env, job_env=job_env,
                    wf_defaults=dict(wf_def), job_defaults=dict(job_def),
                    shell_schritt=str(st.get('shell') or ''),
                    wd_schritt=str(st.get('working-directory') or '')))
        out.append(Workflow(pfad.name, str(doc.get('name') or pfad.stem), filt, schritte))
    return out


# ---------------------------------------------------------------------------
# Geaenderte Dateien und Basis
# ---------------------------------------------------------------------------

def loese_head(repo):
    """HEAD einmal zur SHA aufloesen. Alles Weitere arbeitet auf dieser SHA: committet eine
    andere Session waehrenddessen, bleiben Plan und Schritte auf demselben Commit."""
    res = git(repo, 'rev-parse', '--verify', '--quiet', 'HEAD^{commit}', check=False)
    if res.returncode != 0:
        raise HartFehler('HEAD ist nicht aufloesbar (Repo ohne Commit?)')
    return res.stdout.decode().strip()


def geaenderte_dateien(repo, basis, rev):
    """(merge-base-SHA, sortierte Pfade) von `<merge-base>...<rev>`. Nur `rev`, nie der Working Tree."""
    if git(repo, 'rev-parse', '--verify', '--quiet', f'{basis}^{{commit}}', check=False).returncode != 0:
        raise HartFehler(f'Basis "{basis}" gibt es nicht (git fetch origin?)')
    mb = git(repo, 'merge-base', basis, rev).stdout.decode().strip()
    res = git(repo, 'diff', '--name-only', '-z', '--no-renames', '--no-ext-diff', f'{mb}...{rev}')
    return mb, sorted(p for p in res.stdout.decode('utf-8', 'replace').split('\0') if p)


def ungepruefte_aenderungen(repo):
    """Anzahl uncommitteter und untracked Eintraege im Working Tree des Aufrufers.

    Mit -z steht bei einer Umbenennung oder Kopie (Status R oder C) der Quellpfad als
    eigenes Feld hinter dem Eintrag: es wird uebersprungen, sonst zaehlte sie doppelt."""
    res = git(repo, 'status', '--porcelain', '-z', '--untracked-files=all')
    felder = [x for x in res.stdout.decode('utf-8', 'replace').split('\0') if x]
    n, i = 0, 0
    while i < len(felder):
        n += 1
        i += 2 if ('R' in felder[i][:2] or 'C' in felder[i][:2]) else 1
    return n


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
                                   f'{s.schluessel}\n      Neu klassifizieren (bisher {e.klasse}), etwa: '
                                   f'{vorschlag_zeile(s)}')
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
        if not os.path.exists(os.environ['CI_LOKAL_BASH']):
            raise HartFehler(f'CI_LOKAL_BASH zeigt auf {os.environ["CI_LOKAL_BASH"]}, das gibt es nicht')
        return os.environ['CI_LOKAL_BASH']
    for kandidat in (r'C:\Program Files\Git\bin\bash.exe', r'C:\Program Files\Git\usr\bin\bash.exe'):
        if os.path.exists(kandidat):
            return kandidat
    gefunden = shutil.which('bash')
    if gefunden and not re.search(r'(?i)system32|windowsapps', gefunden):
        return gefunden
    raise HartFehler('keine Git Bash gefunden (CI_LOKAL_BASH setzen)')


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
    p.add_argument('--timeout', type=int, default=1800, help='Sekunden je Schritt (Default 1800)')
    p.add_argument('-v', '--ausfuehrlich', action='store_true', help='Ausgabe auch gruener Schritte zeigen')
    p.add_argument('--repo', default=str(REPO), help=argparse.SUPPRESS)
    p.add_argument('--workflows', default=None, help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    tabelle = KLASSEN if tabelle is None else tabelle
    repo = Path(args.repo)
    try:
        return _lauf(args, repo, tabelle)
    except (HartFehler, RuntimeError) as ex:
        print(f'HARTER FEHLER: {ex}')
        return 2
    except KeyboardInterrupt:
        print('\nabgebrochen')
        return 130


WT_PRAEFIX = 'ci-lokal-wt-'
PID_DATEI = 'ci-lokal.pid'
LANG_PFADE = ('tei/', 'authority-files/', 'schema/')


def lege_worktree_an(repo, rev):
    wt = tempfile.mkdtemp(prefix=WT_PRAEFIX)
    res = git(repo, 'worktree', 'add', '--detach', wt, rev, check=False)
    if res.returncode != 0:
        shutil.rmtree(wt, ignore_errors=True)
        raise HartFehler('git worktree add ist fehlgeschlagen: ' + res.stderr.decode('utf-8', 'replace').strip())
    schreibe_pid(wt)
    return wt


def pid_datei(wt):
    """Die PID-Datei liegt im Git-Verzeichnis des Worktrees (`<repo>/.git/worktrees/<name>/`),
    nicht im Worktree: dort stuende sie als untracked Datei in `git status` und `git diff` der
    Freshness-Schritte. `git worktree remove` und `prune` raeumen sie mit weg."""
    res = git(wt, 'rev-parse', '--absolute-git-dir', check=False)
    if res.returncode != 0:
        return None
    return Path(res.stdout.decode('utf-8', 'replace').strip()) / PID_DATEI


def schreibe_pid(wt):
    pfad = pid_datei(wt)
    if pfad is not None:
        pfad.write_text(str(os.getpid()), encoding='ascii')


def pid_status(pid):
    """('lebt' | 'tot' | 'unklar', Grund). Tot ist eine PID nur bei eindeutiger Antwort: `tasklist`
    mit rc 0 ohne CSV-Zeile `"<pid>"` (der Kein-Treffer-Fall liefert rc 0 und eine lokalisierte
    INFORMATION-Zeile), unter POSIX `ProcessLookupError`. Alles andere ist unklar, und unklar
    entfernt nichts."""
    if sys.platform == 'win32':
        try:
            res = subprocess.run(['tasklist', '/FI', f'PID eq {pid}', '/NH', '/FO', 'CSV'],
                                 capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as ex:
            return 'unklar', f'tasklist nicht lauffaehig: {type(ex).__name__}'
        if res.returncode != 0:
            return 'unklar', f'tasklist endete mit rc {res.returncode}'
        if f'"{pid}"' in res.stdout.decode('utf-8', 'replace'):
            return 'lebt', ''
        return 'tot', ''
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return 'tot', ''
    except PermissionError:
        return 'unklar', 'keine Berechtigung fuer os.kill'
    except Exception as ex:
        return 'unklar', f'os.kill: {type(ex).__name__}'
    return 'lebt', ''


def worktree_pfade(repo):
    res = git(repo, 'worktree', 'list', '--porcelain', check=False)
    return [z[len('worktree '):] for z in res.stdout.decode('utf-8', 'replace').splitlines()
            if z.startswith('worktree ')]


def raeume_reste(repo, trocken):
    """Reste abgebrochener Laeufe: registrierte Worktrees `ci-lokal-wt-*` direkt unter dem Temp-Ordner.

    Entfernt wird nur, wenn die PID-Datei lesbar ist und die PID eindeutig tot ist. Lebt sie, ist ihr
    Status unklar oder ist die Datei nicht lesbar, wird nur gemeldet. Mit `trocken` wird nie entfernt.
    Andere Worktrees (ohne das Praefix oder ausserhalb des Temp-Ordners) fasst es nicht an."""
    temp = os.path.normcase(os.path.realpath(tempfile.gettempdir()))
    for pfad in worktree_pfade(repo):
        p = Path(pfad)
        if not p.name.startswith(WT_PRAEFIX) or os.path.normcase(os.path.realpath(p.parent)) != temp:
            continue
        pid = None
        datei = pid_datei(p) if p.exists() else None
        try:
            pid = int(datei.read_text(encoding='ascii').strip())
        except (OSError, ValueError, AttributeError):
            pass
        if pid is None:
            print(f'Rest eines Laufs, PID-Datei nicht lesbar, nicht entfernt: {pfad}')
        else:
            status, grund = pid_status(pid)
            if status == 'lebt':
                print(f'Worktree eines laufenden Laufs (PID {pid}), nicht entfernt: {pfad}')
            elif status == 'unklar':
                print(f'Rest eines Laufs, Status der PID {pid} unklar ({grund}), nicht entfernt: {pfad}')
            elif trocken:
                print(f'Rest eines abgebrochenen Laufs (PID {pid} tot), --trocken entfernt nicht: {pfad}')
            else:
                entferne_worktree(repo, pfad)
                print(f'Rest eines abgebrochenen Laufs entfernt: {pfad}')


def entferne_worktree(repo, wt):
    """Entfernt genau diesen Worktree. Kein globales `git worktree prune`: es truege fremde
    Worktrees mit fehlendem Ordner still aus. Bleibt der Eintrag nach `remove` und `rmtree`
    stehen, wird nur sein eigener Admin-Ordner unter `<git-common-dir>/worktrees/` entfernt."""
    admin = None
    res = git(wt, 'rev-parse', '--absolute-git-dir', check=False) if os.path.isdir(wt) else None
    common = git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir', check=False)
    if res is not None and res.returncode == 0 and common.returncode == 0:
        kandidat = Path(res.stdout.decode('utf-8', 'replace').strip())
        wurzel = Path(common.stdout.decode('utf-8', 'replace').strip()) / 'worktrees'
        if os.path.normcase(os.path.realpath(kandidat.parent)) == os.path.normcase(os.path.realpath(wurzel)):
            admin = kandidat
    git(repo, 'worktree', 'remove', '--force', wt, check=False)
    shutil.rmtree(wt, ignore_errors=True)
    ziel = os.path.normcase(os.path.realpath(wt))
    if admin is not None and any(os.path.normcase(os.path.realpath(x)) == ziel for x in worktree_pfade(repo)):
        shutil.rmtree(admin, ignore_errors=True)


def _lauf(args, repo, tabelle):
    rev = loese_head(repo)
    raeume_reste(repo, args.trocken)
    texte = workflow_texte(repo, args.workflows, rev)
    workflows = lade_workflows(texte)
    mb, dateien = geaenderte_dateien(repo, args.basis, rev)
    if not args.trocken:
        finde_bash()  # fehlt Git Bash, endet der Lauf vor dem Worktree mit Exit 2
    rt = tempfile.mkdtemp(prefix='ci-lokal-')
    wt = None
    try:
        opt = {'workflow': args.workflow, 'ohne_filter': args.ohne_filter, 'lang': args.lang,
               'ereignis': args.ereignis, 'branch': args.push_branch,
               'runner_temp': Path(rt).as_posix()}
        plan = plane(workflows, tabelle, mb, dateien, opt)
        print(f'HEAD beim Start: {rev[:12]}. Basis {args.basis} (merge-base {mb[:12]}), '
              f'{len(dateien)} geaenderte Datei(en) zwischen merge-base und diesem Commit, '
              f'Ereignis {args.ereignis}')
        n = ungepruefte_aenderungen(repo)
        if n:
            print(f'WARNUNG: {n} uncommittete oder untracked Eintraege im Working Tree werden nicht '
                  'geprueft (geprueft wird HEAD)')
        if not args.lang and any(d.startswith(LANG_PFADE) for d in dateien):
            print('WARNUNG: der Diff aendert tei/, authority-files/ oder schema/ und --lang fehlt: '
                  'Pflicht ist --lang (CLAUDE.md, #726), im Hintergrund fahren')
        for w in plan.warnungen:
            print(f'WARNUNG: {w}')
        if plan.fehler:
            melde_fehler(plan)
            return 2
        for datei, grund in plan.nicht_betroffen:
            print(f'  nicht betroffen: {datei} ({grund})')
        if not args.trocken:
            wt = lege_worktree_an(repo, rev)
            print(f'Worktree von HEAD ({rev[:12]}) fuer den Lauf: {wt} (wird am Ende entfernt)')
        zaehler = bericht(plan, args.trocken, wt or repo, args.timeout, rt, args.ausfuehrlich)
        return 1 if zaehler['rot'] else 0
    finally:
        if wt:
            entferne_worktree(repo, wt)
        shutil.rmtree(rt, ignore_errors=True)


# ---------------------------------------------------------------------------
# Tabelle (Stand der Workflows in diesem Repo; Schluessel und Hash siehe oben)
# ---------------------------------------------------------------------------

KLASSEN.extend([
    E('data-integrity.yml', 'validate', 'Install dependencies', '0d62f8ea7c59',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('data-integrity.yml', 'validate', 'Index version consistency (#47.3)', '1421c781f48d',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Dokumentierte Zahlen gegen die Daten (#382/#398)', '4cd8d1c317e5',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Werk-Identifier und Editionsnachweis gegen works.xml (#399/#486)', 'd3fb7780ec0a',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Regenerate RNG from RNC (P2-14 drift check)', '6a1b344c91c3',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Fail if committed .rng differs from regenerated .rng', 'ec12a24dfa8c',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Verify TEI P5 version pin', 'b6e726b2454e',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Personennamen im Header gegen persons.xml (#228/#308)', '394d5a9bd9ea',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Gattungen im Header gegen works.xml (#495)', 'dddb7c6253cb',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Struktur der committeten Indexe (validate-indices.py,', '020b98c22ae4',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'validate', 'Validate corpus and authority files (P2-13)', '614bb2dd52d9',
      'lokal-lang', 'RelaxNG-Validierung aller Korpusdateien, in der CI median 212 s (data-integrity.yml:10)'),
    E('data-integrity.yml', 'validate', 'Laufzeitbudget (#564)', '3ce47fd1cfc9',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('data-integrity.yml', 'freshness', 'Diff-Base bestimmen (#154/#152)', '8ce7780a3815',
      'ersetzt', 'Diff-Base: HEAD^1 des Merge-Refs gibt es lokal nicht; ci-lokal setzt sha = merge-base mit der Basis und rechnet naming_changed aus der Dateiliste'),
    E('data-integrity.yml', 'freshness', 'Install dependencies', '0d62f8ea7c59',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('data-integrity.yml', 'freshness', 'Index-Versions-Bump-Gate (#154)', '51658f86ce86',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Variants-Flip-Gate (#378, ADR-021)', '5dd94d395270',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Index-Budget Selbsttest (#111)', 'a1d2b2dfc7e3',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Index-Budget (#111)', '11c637f15950',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness variants.xml (#125)', 'd916ceaa3361',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness API (#45)', '7ade901abe98',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness Begriffshilfe (#498)', '77726a5157aa',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness lemma-pos (#462)', '7939c03ea360',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness Indexe \u2014 Rebuild-and-Compare (#125)', 'b707af070a34',
      'lokal-lang', 'baut beide Indexe neu, in der CI median 74 s (data-integrity.yml:10); schreibt data/*.json.gz'),
    E('data-integrity.yml', 'freshness', 'Naming-Index Konsistenz (#152)', 'dec4ef59e33f',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Freshness naming-index \u2014 Rebuild-and-Compare (#152)', 'cf803142361f',
      'ausgelassen', 'braucht github.token und einen Abruf an lindabeutel/Naming-analysis; bei Aenderung am naming-Index von Hand: 01-fetch-and-build-index.py'),
    E('data-integrity.yml', 'freshness', 'Authority cross-reference integrity (#44/#115/#152)', '5a07320ce7a3',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('data-integrity.yml', 'freshness', 'Laufzeitbudget (#564)', '0142c82dd8ad',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('data-integrity.yml', 'melden', 'Zustandswechsel melden (#653)', 'e74d63a9b132',
      'ausgelassen', 'Job laeuft nur auf schedule/workflow_dispatch auf main und meldet in #653; github.*-Kontext, kein Gate am PR'),
    E('doc-health.yml', 'doc-health', 'Doku-Health Selbsttest (#641)', '92fddcc05961',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('doc-health.yml', 'doc-health', 'Doku-Health Bericht (#641)', '44a77cf0a7ca',
      'ausgelassen', 'braucht github.token und die Actions/Issue-API; am PR ohne --apply, kein Gate'),
    E('doc-health.yml', 'doc-health', 'Laufzeitbudget (#564)', '549306303718',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('file-size-check.yml', 'check', 'Groessenwaechter Selbsttest (#350)', '2ad135c339a9',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('file-size-check.yml', 'check', 'Baum mit Groessen aus der API (#564)', 'd8e4cdb71693',
      'ausgelassen', 'holt den Baum ueber die GitHub-Trees-API (github.token); der lokale Lauf misst ohne API'),
    E('file-size-check.yml', 'check', 'Keine committete Datei nahe GitHubs 100-MiB-Wand (#350)', '143647a81b00',
      'lokal', 'Ersatzbefehl: ohne --github-tree, das Skript liest lokal git ls-tree', ersatz='python3 scripts/audit/check-file-sizes.py'),
    E('file-size-check.yml', 'check', 'Laufzeitbudget (#564)', '78b6267c19f5',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('link-check.yml', 'link-check', 'Link-Check Selbsttest (#653)', '8928e09761c5',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Selbsttest der Meldung (#653)', 'a01b2e8b9a83',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Links einsammeln (PR)', 'b36b63b51020',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('link-check.yml', 'link-check', 'Externe Links pruefen (#653)', '2d06d9823091',
      'ausgelassen', 'fragt das Netz ab und laeuft nur ausserhalb des PR (if); am PR ersetzt es der Schritt "Links einsammeln"'),
    E('link-check.yml', 'melden', 'Zustandswechsel melden (#653)', 'e6ad7ca0b441',
      'ausgelassen', 'Job laeuft nur auf schedule/workflow_dispatch auf main und meldet in #653; github.*-Kontext, kein Gate am PR'),
    E('measured-counts.yml', 'measured-counts', 'Install dependencies', '0d62f8ea7c59',
      'ausgelassen', 'pip install: Abhaengigkeiten werden lokal nie installiert (requirements.txt gilt als vorhanden)'),
    E('measured-counts.yml', 'measured-counts', 'Gemessene Zahlen gegen ihre Fundstellen (#414)', '33cf882bc9b2',
      'lokal-lang', 'parst alle Korpusdateien, rund 263 s (gemessen 10.10.2026, measured-counts.yml:6)'),
    E('measured-counts.yml', 'measured-counts', 'Laufzeitbudget (#564)', 'b6ca3c740bcb',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('no-cdn-check.yml', 'check', 'Arbeitsbaum vollstaendig ausser tei/*.tei.xml und data/*.json.gz (#564)', '4e054cf635fb',
      'ausgelassen', 'Kontrollwert fuer den sparse-Checkout der CI; lokal ist der Baum voll'),
    E('no-cdn-check.yml', 'check', 'Diff-Base bestimmen (#292)', '11f87ebc25ab',
      'ersetzt', 'Diff-Base: HEAD^1 des Merge-Refs gibt es lokal nicht; ci-lokal setzt sha = merge-base mit der Basis und rechnet naming_changed aus der Dateiliste'),
    E('no-cdn-check.yml', 'check', 'No external script src or link href in committed HTML (stdlib only)', 'ab022306dac8',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Em-Dash-Gate Selbsttest (#140/#292)', '0254103d6d74',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Keine Em-Dashes in HTML/JS/CSS und neuer Markdown-Prosa (#140/#292)', 'e8c3f5459c83',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Inventar-Gate Selbsttest (#329)', 'f4563578b63f',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Laufzeitbudget Selbsttest (#564)', 'dae7c11483e0',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Specs und Audit-Skripte stehen in ihren Inventaren (#329)', '3360cbf95db7',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Hilfe-Unterseiten gegen ihre Stände (#417/#537)', '653e0c14d156',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Seitenchrome und SEO-Block gegen includes/ und die Seiten (build-pages --check)', '7572777f2b91',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'tei/-Dateinamen fuer doc-count-audit (#564)', '6a0c67c90d9a',
      'ausgelassen', 'ZERSTOERT lokal die Korpusdateien: leert alle tei/*.tei.xml (Platzhalter fuer den sparse-Baum der CI); der naechste Schritt laeuft lokal ohne Platzhalter'),
    E('no-cdn-check.yml', 'check', 'Dokumentierte Zahlen gegen die Daten (#382/#398)', '7f224629d901',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('no-cdn-check.yml', 'check', 'Laufzeitbudget (#564)', '12d9ee596ddb',
      'ausgelassen', 'Laufzeitbudget liest die Dauern der CI-Schritte ueber die Actions-API (github.token, job.status); lokal ohne Gegenstueck'),
    E('search-benchmark.yml', 'benchmark', 'Node-Version', '0e19ab2576be',
      'lokal', 'Pruefschritt, laeuft in Git Bash'),
    E('search-benchmark.yml', 'benchmark', 'Aufloesung gegen Budget (#564)', 'e2133371973b',
      'ausgelassen', 'Zeitbudget, auf die CI-Runner kalibriert und lokal nicht vergleichbar: lokal waren 12 von 24 '
      'Faellen ueber Budget, ohne Code-Aenderung (gemessen 25.11.2026 auf main, '
      '"BENCHMARK: ROT (12 ueber Budget, 0 ohne Budget oder Fall, von 24 Faellen)"). '
      'Nach einer Aenderung unter assets/js/search, assets/js/lib oder playground/js/data '
      'von Hand: node scripts/audit/benchmark-search.mjs'),
    E('release-version-check.yml', 'check', 'Check release version consistency', 'b86995921b05',
      'ausgelassen', 'laeuft nur beim Tag-Push (v*), braucht GITHUB_REF_NAME; weder PR noch Push auf main'),
])

if __name__ == '__main__':
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.exit(main())
