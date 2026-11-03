---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python und JS (importlib in-process, Mutationsproben, Rebuild-and-Compare, Ausfallproben für urllib, gz- und c14n-Vergleich) und wiederkehrende Zählfallen
metadata:
  type: project
---
Verdichtet 03.11.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')`, bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`. `main()` in `redirect_stdout`, SystemExit fangen.
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft. Liegt die Stelle hinter einem minutenlangen Lauf: Block per `src[src.index(a):src.index(b)]` ausschneiden und `exec`en, die Kontrollvariante ohne Mutation muss durchlaufen.
- **Rebuild-and-Compare:** `build_index()` bzw. `build_corpus_index(jobs=1)` (sonst BrokenProcessPool) geben den Index zurück, `save_index` schreibt nach `OUTPUT_FILE`. `mod.OUTPUT_FILE = <scratch>/fresh.json.gz`, dekomprimiert gegen `data/*.json.gz` halten.
- Apply-Skript reproduzieren: Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD. Sperrt der Classifier `--apply`: ohne Umgehung per importlib auf `git archive`-Kopien.
- **Gates im Worktree mit `env -C <wt>` starten**, solange sie cwd-relativ lesen (projekt-gates-und-ci), sonst messen sie still den Hauptbaum. Kontrollwert: eine Zahl, die zwischen den Bäumen differiert, muss kippen.

**Ausfallproben für urllib-Skripte:** `mod.urllib.request.urlopen` durch eine Attrappe ersetzen (Kontextmanager mit `status`, `headers`, `read()`), nur die Abruffunktion rufen, `SystemExit` gegen Rückgabe halten. `http.client.IncompleteRead`/`BadStatusLine` sind `HTTPException`, weder `OSError` noch `URLError` noch `ValueError`. `int(HTTPMessage()["fehlt"])` ist TypeError. `RemoteDisconnected`, `ssl.SSLError` sind OSError, `socket.error` ist `OSError` (fängt auch `URLError`).

**Vergleichen:** gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, `json.dumps(sort_keys=True)`. Nach lxml-Serialisierung c14n vergleichen. CRLF-Befund an einer Spec erst proben: JS `$` mit `m`-Flag matcht auch vor `\r`.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex. `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- `findall` statt `find` (Doppelsiglen), lxml `find('x')` = nur direkte Kinder, `id(elem)` ist keine Identität: `tree.getpath()` plus Datei.
- JS `Math.round` = `math.floor(x + 0.5)`, nicht `round()`. Tokens (w+pc) sind nicht Wörter.
- Restsuche nach Katalogzahlen über die Zahlwörter mit `\b`, nicht über das Nomen. CSVs oft `;` plus BOM (`utf-8-sig`). Leere Suche: Kontrollwert (`type="sigle"` trifft jede Korpusdatei).
- **Treffer über Lemmata verlieren die unannotierten Formen** (rund ein Fünftel der `<w>` ohne `@lemmaRef`, 18.10.2026), „hintereinander" über annotierte Tokens springt Wörter. Gegenprobe über alle `<w>`.

**JS ohne Browser**
- Browser-ES-Modul aus `assets/js/lib/` als `.mjs`-Kopie dynamisch importieren (geht, solange `document`/`window` nur in ungerufenen Funktionen stehen). `assets/js/search/search-engine.js` ging unter Node 24 direkt per `pathToFileURL` samt `data/*.json.gz` (gunzipSync).
- Alt gegen neu der Auflösung per Stichprobe (Volllauf >600 s), Fassungen per `git archive <rev> assets/js/lib assets/js/search` mit `package.json` (`type: module`) ins Temp, oder `git show` mit umgeschriebenen relativen Importen (Ersetzungszahl asserten).
- Node-Zeitmessung ist reihenfolgeabhängig (JIT). `ms > budget` ist bei NaN falsch. Lokales Rot eines Zeitgates mit Runner-Budget ist keine Mutationswirkung: immer ein unmutierter Lauf daneben. Ein `pull_request`-Lauf prüft den Merge-Commit, `workflow_dispatch` den Zweigkopf.
