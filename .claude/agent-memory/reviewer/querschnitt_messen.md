---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python und JS, Zählfallen
metadata:
  type: project
---
**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')`, bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`. `main()` in `redirect_stdout`, SystemExit fangen.
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft. Liegt die Stelle hinter einem minutenlangen Lauf: Block per `src[src.index(a):src.index(b)]` ausschneiden und `exec`en, die Kontrollvariante ohne Mutation muss durchlaufen.
- Test-Suite, die ihr Modul per `spec_from_file_location` lädt (z. B. `scripts/ingest/bre/test_bre.py`): Wrapper im Scratch patcht `importlib.util.spec_from_file_location` auf die mutierte Kopie, `sys.path.insert(0, <echter Skriptordner>)`, dann `runpy.run_path(<echte Suite>, run_name="__main__")`. Working Tree bleibt unberührt, Kontrolle ohne Mutation daneben.
- **Determinismus eines Messskripts:** nicht „zweimal laufen", sondern mit `PYTHONHASHSEED=0`, `1`, `12345` je einen in-process-Lauf mit `mod.AUSGABE = <scratch>` und Bytevergleich gegen die committete Ausgabe. Eine Klasse, die der Caller „strukturell 0" nennt, vor der Vorrang-Subtraktion nachrechnen.
- **Rebuild-and-Compare:** `build_index()` bzw. `build_corpus_index(jobs=1)` (sonst BrokenProcessPool) geben den Index zurück, `mod.OUTPUT_FILE = <scratch>/fresh.json.gz`, dekomprimiert gegen `data/*.json.gz` halten.
- **„Die einzige Änderung unter X" an einem Lauf mit Protokoll-TSV:** erst die geänderten `<w>` aus `git diff -U0 <basis>...<ziel> -- tei/` (xml:id, +/- verglichen) gegen die Protokoll-IDs halten. Erst wenn beide Mengen gleich sind, trägt ein Filter im Protokoll die Allaussage.
- Apply-Skript reproduzieren: Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD. Sperrt der Classifier `--apply`: ohne Umgehung per importlib auf `git archive`-Kopien.
- Korpusvolle Audit-Skripte mit zwei Pässen über `tei/` laufen über 3 Minuten: gleich im Hintergrund mit `--out <scratch>` und stdout in eine Scratch-Datei, dann `cmp` gegen die committete CSV.

**Isolation über einen Temp-Worktree prüfen** (`ci-lokal.py`, #726, 25.11.2026): zwei Proben an einem Fixture-Repo im Scratch, `main(['--repo', <fixture>], tabelle=...)` in-process.
- Kill statt Ctrl-C: der Schritt selbst ist `taskkill //F //PID $KILLPID`, der Treiber setzt `os.environ['KILLPID'] = str(os.getpid())` (nur der eigene Prozess). Danach `git worktree list` im Fixture: `finally` läuft nicht, der Worktree bleibt registriert, `worktree prune` im nächsten Lauf räumt ihn nicht, weil der Ordner noch da ist. Den Rest selbst wegräumen (`worktree remove --force`, Runner-Temp `ci-lokal-*`). Seit `claude/726-nachtrag` (25.11.2026, falls gemergt) räumt der nächste Lauf einen Rest mit toter PID selbst (`raeume_reste`), nachmessen.
- Fehlerpfad eines Statusprogramms (tasklist, ps) per `mock.patch.object(cl.subprocess, 'run', ...)` nur für `cmd[0] == 'tasklist'` einspeisen, Rest mit `os.getpid()` (lebt) anlegen, Lauf fahren: zeigt in Sekunden, ob ein Fehler als „tot" gelesen wird. Echte Fehlerform vorher messen (`tasklist /FI "PID eq -5"`: rc 1, stdout leer, `FEHLER:` in stderr; kein Treffer: rc 0, lokalisierte `INFORMATION:`-Zeile).
- Halter im Rest (Windows): `subprocess.Popen([python, '-c', 'f=open("a.txt","rb"); time.sleep(120)'], cwd=wt)`, dann `entferne_worktree`. Gemessen 25.11.2026 an `939e371` (mit `prune`) und `2e65b94` (ohne) gleich: der Ordner bleibt mit `a.txt`, der Eintrag ist ausgetragen, `.git` und Admin-Ordner weg, und der nächste `raeume_reste` meldet nichts. Ein verwaister Temp-Ordner ist also kein neuer Befund eines Diffs, der nur `prune` streicht: erst gegen die Vorfassung fahren.
- Rennen: eine Funktion zwischen dem Lesen von HEAD und `worktree add` per `mock.patch.object` ersetzen, die im Fixture committet. Liest das Skript HEAD mehrfach statt einmal als SHA, laufen Plan und Schritte auf zwei Commits. Ein fremder Commit als Kind des Start-Commits unterscheidet `merge-base <basis> HEAD` nicht von `merge-base <basis> <sha>` (Mutation bleibt grün, Runde 3 #726): dafür braucht es ein `reset` oder einen Branch-Wechsel im Mock.
- Für Proben an einem einzelnen Skript samt Test `git archive <sha> <skript> <test> | tar -x -C <scratch>` statt `init` plus `fetch` des ganzen Repos (lief über 120 s).
- Was ein Pfad in `ci-lokal.py` auslöst, ohne Clone und ohne Commit: `cl.plane(cl.lade_workflows(cl.workflow_texte(W, None, REV)), cl.KLASSEN, REV, [pfad], opt)` je Pfad und Ereignis, `opt` mit `workflow, ohne_filter, lang, ereignis, branch, runner_temp`, dann die `zeilen` mit Art `lang` zählen. Am 25.11.2026 so gefunden: `docs/FEATURES.md` und `docs/TEI-MODEL.md` lösen über `measured-counts.yml` einen `lokal-lang`-Schritt aus.
- `git status --porcelain -z` zählt eine gestagte Umbenennung als zwei Einträge (`R  neu\0alt\0`).

**Ausfallproben für urllib-Skripte:** `mod.urllib.request.urlopen` durch einen Mock ersetzen (Kontextmanager mit `status`, `headers`, `read()`), nur die Abruffunktion rufen, `SystemExit` gegen Return Value halten. `http.client.IncompleteRead`/`BadStatusLine` sind `HTTPException`, weder `OSError` noch `URLError` noch `ValueError`. `RemoteDisconnected`, `ssl.SSLError`, `socket.error` sind OSError (fängt auch `URLError`).

**Vergleichen:** gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, `json.dumps(sort_keys=True)`. Nach lxml-Serialisierung c14n vergleichen. CRLF-Befund an einer Spec erst proben: JS `$` mit `m`-Flag matcht auch vor `\r`.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex. `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- `findall` statt `find` (Doppelsiglen), lxml `find('x')` = nur direkte Kinder, `id(elem)` ist keine Identität: `tree.getpath()` plus Datei.
- JS `Math.round` = `math.floor(x + 0.5)`, nicht `round()`. Tokens (w+pc) sind nicht Wörter.
- Restsuche nach Katalogzahlen über die Zahlwörter mit `\b`, nicht über das Nomen. CSVs oft `;` plus BOM (`utf-8-sig`). Leere Suche: Control (`type="sigle"` trifft jede Korpusdatei).
- Treffer über Lemmata verlieren die unannotierten Formen (rund ein Fünftel der `<w>` ohne `@lemmaRef`, Stand Oktober 2026), „hintereinander" über annotierte Tokens springt Wörter. Gegenprobe über alle `<w>`.

**JS ohne Browser**
- Browser-ES-Modul aus `assets/js/lib/` als `.mjs`-Kopie dynamisch importieren (geht, solange `document`/`window` nur in ungerufenen Funktionen stehen). `assets/js/search/search-engine.js` geht unter Node direkt per `pathToFileURL` samt `data/*.json.gz` (gunzipSync).
- Alt gegen neu der Auflösung per Stichprobe (Volllauf >600 s), Fassungen per `git archive <rev> assets/js/lib assets/js/search` mit `package.json` (`type: module`) ins Temp.
- Modul mit DOM-Importen (z. B. `playground/js/ui/core/router.js`): einzelne Funktion per Klammerzählung aus dem Quelltext schneiden und mit `new Function` und Fake-`window` laufen lassen, alt gegen neu. Die Zählung beim `) {` beginnen, nicht beim ersten `{`: ein Default `params = {}` bricht sie sonst.
- Node-Zeitmessung ist reihenfolgeabhängig (JIT). `ms > budget` ist bei NaN falsch. Lokales Rot eines Zeitgates mit Runner-Budget ist keine Mutationswirkung: immer ein unmutierter Lauf daneben.
