#!/usr/bin/env python3
"""
Tests fuer ci-lokal.py (#726). Jeder Test faehrt main() am echten Pfad gegen ein
winziges Git-Repo mit Workflow-Fixtures in einem Temp-Verzeichnis; die
Klassifikationstabelle wird je Test uebergeben. Das Repo hat zwei Commits: die
Basis (Workflows, README) und die "Aenderung" (die Dateien, gegen die der
paths-Filter laeuft). Geprueft wird nur HEAD.

Aufruf:
    python scripts/audit/test_ci_lokal.py

Braucht git, PyYAML und Git Bash (wie ci-lokal.py selbst).
"""
import contextlib
import importlib.util
import io
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HIER = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('ci_lokal', HIER / 'ci-lokal.py')
cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cl)

WF_KOPF = """name: T
on:
  pull_request:
    paths:
      - 'docs/**'
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
"""


def wf(run, name='Schritt A', kopf=WF_KOPF, extra=''):
    eingerueckt = ''.join('          ' + z + '\n' for z in run.splitlines())
    return f"{kopf}      - name: {name}\n{extra}        run: |\n{eingerueckt}"


def eintrag(yaml_text, name='Schritt A', klasse='lokal', datei='t.yml', **extra):
    """Eintrag mit dem Hash, den ci-lokal.py fuer genau diesen Workflow-Text ausrechnet."""
    for w in cl.lade_workflows({datei: yaml_text}):
        for s in w.schritte:
            if s.schluessel == name:
                return cl.E(datei, s.job, name, s.hash, klasse, 'Testgrund', **extra)
    raise AssertionError(f'Schritt {name!r} nicht im Fixture')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout


class Basis(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='ci-lokal-test-'))
        self.addCleanup(self.aufraeumen)

    def aufraeumen(self):
        subprocess.run(['git', '-C', str(self.tmp), 'worktree', 'prune'], capture_output=True)
        # Git-Objekte sind schreibgeschuetzt, unter Windows scheitert rmtree sonst still
        shutil.rmtree(self.tmp, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))

    def repo(self, workflows, geaendert=('docs/x.md',), extra_basis=None):
        """Git-Repo: Commit 1 = Workflows und README, Commit 2 = `geaendert`."""
        wfdir = self.tmp / '.github' / 'workflows'
        wfdir.mkdir(parents=True)
        for name, text in workflows.items():
            (wfdir / name).write_text(text, encoding='utf-8', newline='\n')
        (self.tmp / 'README.md').write_text('x\n', encoding='utf-8')
        for pfad, inhalt in (extra_basis or {}).items():
            (self.tmp / pfad).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / pfad).write_text(inhalt, encoding='utf-8')
        for args in (['init', '-q'], ['config', 'user.email', 't@t'], ['config', 'user.name', 't'],
                     ['config', 'core.autocrlf', 'false'], ['add', '-A'], ['commit', '-q', '-m', 'basis']):
            git(self.tmp, *args)
        for d in geaendert:
            (self.tmp / d).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / d).write_text('neu\n', encoding='utf-8')
        git(self.tmp, 'add', '-A')
        git(self.tmp, 'commit', '-q', '--allow-empty', '-m', 'aenderung')
        return self.tmp

    def lauf(self, tabelle, *argumente):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cl.main(['--repo', str(self.tmp), '--basis', 'HEAD~1', *argumente], tabelle=tabelle)
        return code, out.getvalue()


class Klassifikation(Basis):
    def test_unklassifizierter_schritt_ist_harter_fehler(self):
        self.repo({'t.yml': wf('echo hallo')})
        code, out = self.lauf([])
        self.assertEqual(code, 2, out)
        self.assertIn('nicht klassifiziert', out)
        self.assertNotIn('[1/', out, 'bei einem harten Fehler darf nichts laufen')

    def test_geaenderter_run_text_ist_harter_fehler(self):
        self.repo({'t.yml': wf('echo neu')})
        code, out = self.lauf([eintrag(wf('echo alt'))])
        self.assertEqual(code, 2, out)
        self.assertIn('run-Text geaendert', out)
        self.assertIn("'?', '?'", out, 'der Vorschlag soll die Klasse offen lassen')

    def test_geaenderte_env_ist_harter_fehler(self):
        alt = wf('echo hallo')
        neu = wf('echo hallo', extra='        env:\n          X: "1"\n')
        self.repo({'t.yml': neu})
        code, out = self.lauf([eintrag(alt)])
        self.assertEqual(code, 2, out)
        self.assertIn('run-Text geaendert', out)

    def test_geaendertes_working_directory_ist_harter_fehler(self):
        alt = wf('echo hallo')
        neu = wf('echo hallo', extra='        working-directory: sub\n')
        self.repo({'t.yml': neu})
        code, out = self.lauf([eintrag(alt)])
        self.assertEqual(code, 2, out)

    def test_geaendertes_defaults_run_ist_harter_fehler(self):
        alt = wf('echo hallo')
        neu = wf('echo hallo', kopf=WF_KOPF.replace('    runs-on: ubuntu-latest\n',
                                                    '    runs-on: ubuntu-latest\n    defaults:\n      run:\n        shell: bash\n'))
        self.repo({'t.yml': neu})
        code, out = self.lauf([eintrag(alt)])
        self.assertEqual(code, 2, out)

    def test_unveraenderter_schritt_laeuft(self):
        self.repo({'t.yml': wf('echo hallo')})
        code, out = self.lauf([eintrag(wf('echo hallo'))])
        self.assertEqual(code, 0, out)
        self.assertIn('1 von 1 gelaufen (davon 0 rot)', out)


class Pfadfilter(Basis):
    def test_filter_greift(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['docs/x.md'])
        code, out = self.lauf([eintrag(wf('echo hallo'))])
        self.assertEqual(code, 0, out)
        self.assertNotIn('nicht betroffen', out)
        self.assertIn('[1/1]', out)

    def test_filter_greift_nicht(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['src/y.txt'])
        code, out = self.lauf([eintrag(wf('echo hallo'))])
        self.assertEqual(code, 0, out)
        self.assertIn('nicht betroffen: t.yml', out)
        self.assertNotIn('[1/', out)

    def test_nur_head_zaehlt_nicht_der_working_tree(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['src/y.txt'])
        (self.tmp / 'docs').mkdir()
        (self.tmp / 'docs' / 'fremd.md').write_text('untracked\n', encoding='utf-8')
        code, out = self.lauf([eintrag(wf('echo hallo'))])
        self.assertIn('nicht betroffen: t.yml', out, 'eine fremde untracked Datei darf den Workflow nicht ausloesen')
        self.assertIn('WARNUNG: 1 uncommittete oder untracked Eintraege', out)

    def test_gestagte_umbenennung_zaehlt_einmal(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['src/y.txt'])
        git(self.tmp, 'mv', 'README.md', 'README2.md')
        self.assertEqual(cl.ungepruefte_aenderungen(self.tmp), 1)
        code, out = self.lauf([eintrag(wf('echo hallo'))])
        self.assertIn('WARNUNG: 1 uncommittete oder untracked Eintraege', out)

    def test_glob_und_negation(self):
        self.assertTrue(cl.pfad_trifft(['**.md'], 'README.md'))
        self.assertTrue(cl.pfad_trifft(['**.md'], 'docs/a/b.md'))
        self.assertTrue(cl.pfad_trifft(['**/*.html'], 'index.html'))
        self.assertFalse(cl.pfad_trifft(['assets/js/*'], 'assets/js/a/b.js'))
        self.assertTrue(cl.pfad_trifft(['api/**', '!api/index.html'], 'api/a.json'))
        self.assertFalse(cl.pfad_trifft(['api/**', '!api/index.html'], 'api/index.html'))


class Ausfuehren(Basis):
    def test_roter_schritt_gibt_exit_1(self):
        self.repo({'t.yml': wf('exit 3')})
        code, out = self.lauf([eintrag(wf('exit 3'))])
        self.assertEqual(code, 1, out)
        self.assertIn('ROT', out)
        self.assertIn('(davon 1 rot)', out)

    def test_ersetzung_github_event_name(self):
        run = 'test "${{ github.event_name }}" = "pull_request"'
        self.repo({'t.yml': wf(run)})
        code, out = self.lauf([eintrag(wf(run))])
        self.assertEqual(code, 0, out)
        self.assertIn('Ersetzung: ${{ github.event_name }} -> pull_request', out)

    def test_nicht_ersetzbarer_ausdruck_ohne_klasse_ausgelassen(self):
        run = 'echo ${{ github.sha }}'
        self.repo({'t.yml': wf(run)})
        code, out = self.lauf([eintrag(wf(run), klasse='lokal')])
        self.assertEqual(code, 2, out)
        self.assertIn('nicht ersetzbarer Ausdruck', out)
        code, out = self.lauf([eintrag(wf(run), klasse='ausgelassen')])
        self.assertEqual(code, 0, out)
        self.assertIn('1 ausgelassen', out)

    def test_lokal_lang_nur_mit_flag(self):
        self.repo({'t.yml': wf('exit 3')})
        tab = [eintrag(wf('exit 3'), klasse='lokal-lang')]
        code, out = self.lauf(tab)
        self.assertEqual(code, 0, out)
        self.assertIn('1 lokal-lang nicht gelaufen (--lang)', out)
        code, out = self.lauf(tab, '--lang')
        self.assertEqual(code, 1, out)

    def test_ersetzt_liefert_ausgaben_fuer_spaetere_schritte(self):
        zwei = (WF_KOPF + "      - name: Basis\n        id: base\n        run: echo egal\n"
                          "      - name: Folge\n        run: test -n \"${{ steps.base.outputs.sha }}\"\n")
        self.repo({'t.yml': zwei})
        tab = [eintrag(zwei, 'Basis', 'ersetzt'), eintrag(zwei, 'Folge', 'lokal')]
        code, out = self.lauf(tab)
        self.assertEqual(code, 0, out)
        self.assertIn('1 ersetzt', out)

    def test_working_directory_aus_defaults_run_wird_angewandt(self):
        kopf = WF_KOPF.replace('    runs-on: ubuntu-latest\n',
                               '    runs-on: ubuntu-latest\n    defaults:\n      run:\n        working-directory: sub\n')
        text = wf('test -f marker.txt', kopf=kopf)
        self.repo({'t.yml': text}, extra_basis={'sub/marker.txt': 'm\n'})
        code, out = self.lauf([eintrag(text)])
        self.assertEqual(code, 0, out)


class Isolation(Basis):
    def test_schritte_laufen_im_temporaeren_worktree_nicht_im_repo(self):
        run = 'echo x > geschrieben.txt\npwd'
        text = wf(run)
        self.repo({'t.yml': text})
        vorher = git(self.tmp, 'status', '--porcelain')
        code, out = self.lauf([eintrag(text)], '-v')
        self.assertEqual(code, 0, out)
        self.assertEqual(git(self.tmp, 'status', '--porcelain'), vorher, 'das Repo des Aufrufers wurde veraendert')
        self.assertEqual(git(self.tmp, 'status', '--porcelain'), '')
        self.assertFalse((self.tmp / 'geschrieben.txt').exists())
        self.assertEqual(len(git(self.tmp, 'worktree', 'list').strip().splitlines()), 1,
                         'der temporaere Worktree ist nicht entfernt')
        self.assertIn(f'Worktree von HEAD ({git(self.tmp, "rev-parse", "HEAD").strip()[:12]}) fuer den Lauf:', out)

    def test_git_im_repo_des_aufrufers_nimmt_keine_optionalen_locks(self):
        self.repo({'t.yml': wf('echo hallo')})
        echt, gesehen = subprocess.run, []

        def spion(cmd, *a, **kw):
            gesehen.append((cmd, (kw.get('env') or {}).get('GIT_OPTIONAL_LOCKS')))
            return echt(cmd, *a, **kw)
        with mock.patch.object(cl.subprocess, 'run', spion):
            cl.ungepruefte_aenderungen(self.tmp)
        status = [e for c, e in gesehen if 'status' in c]
        self.assertEqual(status, ['0'])

    def test_fremder_commit_waehrend_des_laufs_aendert_nichts(self):
        """Ein anderer Commit zwischen Start und Schritten: Plan und Schritte bleiben auf der Start-SHA."""
        run = 'git rev-parse HEAD > gesehen.txt\ntest -f docs/x.md'
        text = wf(run)
        self.repo({'t.yml': text})
        start = git(self.tmp, 'rev-parse', 'HEAD').strip()
        basis = git(self.tmp, 'rev-parse', 'HEAD~1').strip()
        tab = [eintrag(text)]
        echt = cl.loese_head

        def mit_fremdem_commit(repo):
            sha = echt(repo)
            # eine andere Session: loescht die geaenderte Datei und aendert den Workflow
            git(self.tmp, 'rm', '-q', 'docs/x.md')
            (self.tmp / '.github/workflows/t.yml').write_text(text.replace('git rev-parse', 'echo fremd'),
                                                              encoding='utf-8', newline='\n')
            git(self.tmp, 'add', '-A')
            git(self.tmp, 'commit', '-q', '-m', 'fremder Commit')
            return sha
        out = io.StringIO()
        with mock.patch.object(cl, 'loese_head', mit_fremdem_commit), contextlib.redirect_stdout(out):
            code = cl.main(['--repo', str(self.tmp), '--basis', basis, '-v'], tabelle=tab)
        self.assertNotEqual(git(self.tmp, 'rev-parse', 'HEAD').strip(), start, 'der fremde Commit fehlt')
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn('[1/1]', out.getvalue(), 'Workflow nicht betroffen: die Dateiliste kam aus dem neuen HEAD')
        self.assertIn(f'HEAD beim Start: {start[:12]}', out.getvalue())
        self.assertIn(f'Worktree von HEAD ({start[:12]})', out.getvalue())

    def test_worktree_wird_auch_bei_abbruch_entfernt(self):
        text = wf('echo hallo')
        self.repo({'t.yml': text})
        with mock.patch.object(cl, 'fahre', side_effect=KeyboardInterrupt):
            code, out = self.lauf([eintrag(text)])
        self.assertEqual(code, 130, out)
        self.assertEqual(len(git(self.tmp, 'worktree', 'list').strip().splitlines()), 1)

    def test_trocken_legt_keinen_worktree_an(self):
        text = wf('echo hallo')
        self.repo({'t.yml': text})
        with mock.patch.object(cl, 'lege_worktree_an', side_effect=AssertionError('Worktree bei --trocken')):
            code, out = self.lauf([eintrag(text)], '--trocken')
        self.assertEqual(code, 0, out)


def toter_pid():
    p = subprocess.Popen([sys.executable, '-c', 'pass'])
    p.wait()
    return p.pid


class Reste(Basis):
    """Worktrees `ci-lokal-wt-*` aus einem hart abgebrochenen Lauf (#726, Nachtrag)."""

    def setUp(self):
        super().setUp()
        self.text = wf('echo hallo')
        self.repo({'t.yml': self.text})
        self.tab = [eintrag(self.text)]

    def rest(self, pid):
        wt = cl.lege_worktree_an(self.tmp, 'HEAD')
        self.addCleanup(cl.entferne_worktree, self.tmp, wt)
        cl.pid_datei(Path(wt)).write_text(str(pid), encoding='ascii')
        return Path(wt).as_posix()  # so nennt `git worktree list` den Pfad

    def anzahl(self):
        return len(git(self.tmp, 'worktree', 'list').strip().splitlines())

    def test_toter_rest_wird_entfernt(self):
        wt = self.rest(toter_pid())
        code, out = self.lauf(self.tab)
        self.assertEqual(code, 0, out)
        self.assertIn(f'Rest eines abgebrochenen Laufs entfernt: {wt}', out)
        self.assertFalse(os.path.exists(wt))
        self.assertEqual(self.anzahl(), 1)

    def test_rest_mit_lebender_pid_bleibt_und_wird_gemeldet(self):
        wt = self.rest(os.getpid())
        code, out = self.lauf(self.tab)
        self.assertEqual(code, 0, out)
        self.assertIn(f'(PID {os.getpid()}), nicht entfernt: {wt}', out)
        self.assertNotIn('entfernt: ' + wt, out.replace('nicht entfernt: ' + wt, ''))
        self.assertTrue(os.path.exists(wt))
        self.assertEqual(self.anzahl(), 2)

    def test_unlesbare_pid_datei_wird_nur_gemeldet(self):
        wt = self.rest(toter_pid())
        cl.pid_datei(Path(wt)).unlink()
        code, out = self.lauf(self.tab)
        self.assertIn(f'PID-Datei nicht lesbar, nicht entfernt: {wt}', out)
        self.assertTrue(os.path.exists(wt))

    def test_fremder_worktree_ohne_praefix_bleibt_unberuehrt(self):
        temp_wt = tempfile.mkdtemp(prefix='anderer-wt-')
        unter_repo = self.tmp / 'ci-lokal-wt-nicht-im-temp-root'
        for wt in (temp_wt, str(unter_repo)):
            git(self.tmp, 'worktree', 'add', '--detach', wt, 'HEAD')
            self.addCleanup(cl.entferne_worktree, self.tmp, wt)
            cl.pid_datei(Path(wt)).write_text(str(toter_pid()), encoding='ascii')
        code, out = self.lauf(self.tab)
        self.assertEqual(code, 0, out)
        self.assertNotIn('Rest eines', out)
        self.assertTrue(os.path.exists(temp_wt) and unter_repo.exists())
        self.assertEqual(self.anzahl(), 3)

    def test_trocken_meldet_aber_entfernt_nicht(self):
        wt = self.rest(toter_pid())
        code, out = self.lauf(self.tab, '--trocken')
        self.assertEqual(code, 0, out)
        self.assertIn(f'--trocken entfernt nicht: {wt}', out)
        self.assertTrue(os.path.exists(wt))
        self.assertEqual(self.anzahl(), 2)

    def test_eigener_lauf_schreibt_seine_pid(self):
        wt = cl.lege_worktree_an(self.tmp, 'HEAD')
        self.addCleanup(cl.entferne_worktree, self.tmp, wt)
        self.assertEqual(cl.pid_datei(Path(wt)).read_text(encoding='ascii'), str(os.getpid()))
        self.assertEqual(git(wt, 'status', '--porcelain'), '', 'die PID-Datei darf nicht im Worktree stehen')


class LangWarnung(Basis):
    TEXT = wf('echo hallo')

    def warnung(self, pfad):
        self.repo({'t.yml': self.TEXT}, geaendert=[pfad])
        code, out = self.lauf([eintrag(self.TEXT)])
        self.assertEqual(code, 0, out)
        self.assertIn('WARNUNG: der Diff aendert tei/, authority-files/ oder schema/ und --lang fehlt', out)
        self.assertIn('im Hintergrund fahren', out)
        self.assertNotIn(';', [z for z in out.splitlines() if 'Pflicht ist --lang' in z][0])

    def test_warnung_bei_tei_ohne_lang(self):
        self.warnung('tei/a.xml')

    def test_warnung_bei_authority_files_ohne_lang(self):
        self.warnung('authority-files/b.xml')

    def test_warnung_bei_schema_ohne_lang(self):
        self.warnung('schema/c.rnc')

    def test_keine_warnung_mit_lang_oder_ohne_diese_pfade(self):
        self.repo({'t.yml': self.TEXT}, geaendert=['tei/a.xml'])
        code, out = self.lauf([eintrag(self.TEXT)], '--lang')
        self.assertNotIn('--lang fehlt', out)
        code, out = self.lauf([eintrag(self.TEXT)], '--trocken')
        self.assertIn('--lang fehlt', out, '--trocken warnt auch')

    def test_keine_warnung_fuer_andere_pfade(self):
        self.repo({'t.yml': self.TEXT}, geaendert=['docs/x.md', 'scripts/teilnehmer.py'])
        code, out = self.lauf([eintrag(self.TEXT)])
        self.assertNotIn('--lang fehlt', out)


class Umgebung(Basis):
    def test_pyyaml_fehlt_ist_exit_2(self):
        self.repo({'t.yml': wf('echo hallo')})
        with mock.patch.dict(sys.modules, {'yaml': None}):
            code, out = self.lauf([])
        self.assertEqual(code, 2, out)
        self.assertIn('PyYAML', out)

    def test_bash_fehlt_ist_exit_2(self):
        text = wf('echo hallo')
        self.repo({'t.yml': text})
        with mock.patch.dict(os.environ, {'CI_LOKAL_BASH': str(self.tmp / 'gibt-es-nicht.exe')}), \
                mock.patch.object(cl, 'lege_worktree_an', side_effect=AssertionError('Worktree trotz fehlender Bash')):
            code, out = self.lauf([eintrag(text)])
        self.assertEqual(code, 2, out)
        self.assertIn('CI_LOKAL_BASH', out)
        self.assertEqual(len(git(self.tmp, 'worktree', 'list').strip().splitlines()), 1)


class Ereignis(Basis):
    PUSH = ("name: P\non:\n  push:\n    branches:\n      - main\njobs:\n  j:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - name: Schritt A\n        run: |\n          echo hallo\n")

    def test_push_only_workflow_nur_im_modus_push(self):
        self.repo({'p.yml': self.PUSH})
        tab = [eintrag(self.PUSH, datei='p.yml')]
        code, out = self.lauf(tab)
        self.assertEqual(code, 0, out)
        self.assertIn('nicht betroffen: p.yml (kein pull_request-Trigger)', out)
        self.assertNotIn('[1/', out)
        code, out = self.lauf(tab, '--ereignis', 'push')
        self.assertEqual(code, 0, out)
        self.assertIn('[1/1]', out)

    def test_schritt_nur_im_anderen_modus_braucht_trotzdem_eine_klasse(self):
        self.repo({'p.yml': self.PUSH})
        code, out = self.lauf([])
        self.assertEqual(code, 2, out)
        self.assertIn('nicht klassifiziert: p.yml', out)

    def test_push_filter_branch_und_tags(self):
        tags = self.PUSH.replace('branches:\n      - main', 'tags:\n      - "v*"')
        self.repo({'p.yml': tags})
        code, out = self.lauf([eintrag(tags, datei='p.yml')], '--ereignis', 'push')
        self.assertIn('nicht betroffen: p.yml', out)

    def test_event_name_folgt_dem_modus(self):
        run = 'test "${{ github.event_name }}" = "push"'
        both = WF_KOPF.replace('  pull_request:', '  push:\n    branches: [main]\n  pull_request:') + \
            "      - name: Schritt A\n        run: |\n          " + run + "\n"
        self.repo({'t.yml': both})
        code, out = self.lauf([eintrag(both)], '--ereignis', 'push')
        self.assertEqual(code, 0, out)
        code, out = self.lauf([eintrag(both)])
        self.assertEqual(code, 1, out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
