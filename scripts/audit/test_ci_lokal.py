#!/usr/bin/env python3
"""
Tests fuer ci-lokal.py (#726). Jeder Test faehrt main() am echten Pfad gegen ein
winziges Git-Repo mit Workflow-Fixtures in einem Temp-Verzeichnis; die
Klassifikationstabelle wird je Test uebergeben.

Aufruf:
    python scripts/audit/test_ci_lokal.py

Braucht git, PyYAML und Git Bash (wie ci-lokal.py selbst).
"""
import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


def eintrag(run, klasse='lokal', name='Schritt A', datei='t.yml', job='j', wenn='', nl=True, **extra):
    # `run: |` im YAML endet auf einen Zeilenumbruch, `run: text` in einer Zeile nicht
    return cl.E(datei, job, name, cl.schritt_hash(run + ('\n' if nl else ''), wenn, ''),
                klasse, 'Testgrund', **extra)


class Basis(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='ci-lokal-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def repo(self, workflows, geaendert=('docs/x.md',)):
        """Git-Repo mit den Workflows im ersten Commit; `geaendert` liegt danach untracked da."""
        wfdir = self.tmp / '.github' / 'workflows'
        wfdir.mkdir(parents=True)
        for name, text in workflows.items():
            (wfdir / name).write_text(text, encoding='utf-8', newline='\n')
        (self.tmp / 'README.md').write_text('x\n', encoding='utf-8')
        for args in (['init', '-q'], ['config', 'user.email', 't@t'], ['config', 'user.name', 't'],
                     ['add', '-A'], ['commit', '-q', '-m', 'basis']):
            subprocess.run(['git', '-C', str(self.tmp), *args], check=True, capture_output=True)
        for d in geaendert:
            (self.tmp / d).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / d).write_text('neu\n', encoding='utf-8')
        return self.tmp

    def lauf(self, tabelle, *argumente):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cl.main(['--repo', str(self.tmp), '--basis', 'HEAD', *argumente], tabelle=tabelle)
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
        code, out = self.lauf([eintrag('echo alt')])
        self.assertEqual(code, 2, out)
        self.assertIn('run-Text geaendert', out)

    def test_unveraenderter_schritt_laeuft(self):
        self.repo({'t.yml': wf('echo hallo')})
        code, out = self.lauf([eintrag('echo hallo')])
        self.assertEqual(code, 0, out)
        self.assertIn('1 von 1 gelaufen (davon 0 rot)', out)


class Pfadfilter(Basis):
    def test_filter_greift(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['docs/x.md'])
        code, out = self.lauf([eintrag('echo hallo')])
        self.assertEqual(code, 0, out)
        self.assertNotIn('nicht betroffen', out)
        self.assertIn('[1/1]', out)

    def test_filter_greift_nicht(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['src/y.txt'])
        code, out = self.lauf([eintrag('echo hallo')])
        self.assertEqual(code, 0, out)
        self.assertIn('nicht betroffen: t.yml', out)
        self.assertNotIn('[1/', out)

    def test_working_tree_abschaltbar(self):
        self.repo({'t.yml': wf('echo hallo')}, geaendert=['docs/x.md'])
        code, out = self.lauf([eintrag('echo hallo')], '--ohne-working-tree')
        self.assertIn('nicht betroffen: t.yml', out)

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
        code, out = self.lauf([eintrag('exit 3')])
        self.assertEqual(code, 1, out)
        self.assertIn('ROT', out)
        self.assertIn('(davon 1 rot)', out)

    def test_ersetzung_github_event_name(self):
        run = 'test "${{ github.event_name }}" = "pull_request"'
        self.repo({'t.yml': wf(run)})
        code, out = self.lauf([eintrag(run)])
        self.assertEqual(code, 0, out)
        self.assertIn('Ersetzung: ${{ github.event_name }} -> pull_request', out)

    def test_nicht_ersetzbarer_ausdruck_ohne_klasse_ausgelassen(self):
        run = 'echo ${{ github.sha }}'
        self.repo({'t.yml': wf(run)})
        code, out = self.lauf([eintrag(run, 'lokal')])
        self.assertEqual(code, 2, out)
        self.assertIn('nicht ersetzbarer Ausdruck', out)
        code, out = self.lauf([eintrag(run, 'ausgelassen')])
        self.assertEqual(code, 0, out)
        self.assertIn('1 ausgelassen', out)

    def test_lokal_lang_nur_mit_flag(self):
        self.repo({'t.yml': wf('exit 3')})
        tab = [eintrag('exit 3', 'lokal-lang')]
        code, out = self.lauf(tab)
        self.assertEqual(code, 0, out)
        self.assertIn('1 lokal-lang nicht gelaufen (--lang)', out)
        code, out = self.lauf(tab, '--lang')
        self.assertEqual(code, 1, out)

    def test_ersetzt_liefert_ausgaben_fuer_spaetere_schritte(self):
        zwei = (WF_KOPF + "      - name: Basis\n        id: base\n        run: echo egal\n"
                          "      - name: Folge\n        run: test -n \"${{ steps.base.outputs.sha }}\"\n")
        self.repo({'t.yml': zwei})
        tab = [eintrag('echo egal', 'ersetzt', name='Basis', nl=False),
               eintrag('test -n "${{ steps.base.outputs.sha }}"', 'lokal', name='Folge', nl=False)]
        code, out = self.lauf(tab)
        self.assertEqual(code, 0, out)
        self.assertIn('1 ersetzt', out)


class Ereignis(Basis):
    PUSH = ("name: P\non:\n  push:\n    branches:\n      - main\njobs:\n  j:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - name: Schritt A\n        run: |\n          echo hallo\n")

    def test_push_only_workflow_nur_im_modus_push(self):
        self.repo({'p.yml': self.PUSH})
        tab = [eintrag('echo hallo', datei='p.yml')]
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
        code, out = self.lauf([eintrag('echo hallo', datei='p.yml')], '--ereignis', 'push')
        self.assertIn('nicht betroffen: p.yml', out)

    def test_event_name_folgt_dem_modus(self):
        run = 'test "${{ github.event_name }}" = "push"'
        both = WF_KOPF.replace('  pull_request:', '  push:\n    branches: [main]\n  pull_request:') + \
            "      - name: Schritt A\n        run: |\n          " + run + "\n"
        self.repo({'t.yml': both})
        code, out = self.lauf([eintrag(run)], '--ereignis', 'push')
        self.assertEqual(code, 0, out)
        code, out = self.lauf([eintrag(run)])
        self.assertEqual(code, 1, out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
