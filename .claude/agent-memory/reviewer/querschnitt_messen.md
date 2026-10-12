---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python/JS (importlib in-process, Mutationsproben, Scratch-Nachbau, Rebuild-and-Compare, gz/c14n-Vergleich, find-mentions-Probe) und wiederkehrende Zählfallen
metadata:
  type: project
---
Verdichtet 08. und 10.10.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')`, bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`; `main()` in `redirect_stdout`, SystemExit fangen.
- Netz: `sys.modules["requests"]` vor dem Import stubben. **find-mentions.py `main()` ohne Netz:** außerdem `fm.zotero_baseline`, `fm.SOURCES`, `fm.zotero_write` ersetzen, `fm.PROBLEME` zwischen Fällen leeren, cwd ins Scratch; Kandidatentitel mit fast disjunkten Wortmengen (>= 85 % Überlappung gilt als bekannt).
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, FAIL zählen; oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft.
- **Rebuild-and-Compare ohne Baumkopie:** `build_index()` / `build_corpus_index(jobs=1)` (sonst BrokenProcessPool) geben den Index nur zurück; `save_index(index)` schreibt nach Modul-Global `OUTPUT_FILE`. Modul per importlib, `os.chdir(<wt>)`, `mod.OUTPUT_FILE = <scratch>/fresh.json.gz`, bauen, speichern, dekomprimierte Bytes gegen `data/*.json.gz` halten. `extract-variants.py` ohne `--apply`: `variants.regen.xml` (gates_und_ci) muss gegen `variants.xml` leer diffen, Datum eingeschlossen.
- Nachbau im Scratch (Builds überschreiben data/): Skript + mhg_normalizer.py, tei_namespaces.py + authority-files, `--allow-dirty`; PROJECT_ROOT hängt an `__file__`; Authority-Build braucht zusätzlich `scripts/build-corpus-index.py` und `data/corpus-index.json.gz`. Ohne Korpuskopie: tei/ als **Hardlinks (`os.link`)**, die mutierte Datei als echte Kopie.
- Apply-Skript reproduzieren: betroffene Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD (bei `parents[3]`-REPO: projekt_526_breve_makron). Sperrt der Classifier `--apply` (querschnitt_umgebung), ohne Umgehung: `git archive origin/main tei/ | tar -x -C scratch/alt`, Modul per importlib, auf den Kopien nachfahren.
- **„Idempotent" heißt: die eigene Ausgabe wird wieder erkannt.** Auf HEAD klassifizieren, nicht dem Marker glauben. Am **Apply-Pfad** messen: Kopie von 2 Dateien, `TEI_DIR`/`PLAN`/`REPO` patchen, `--apply` zweimal.
- **Gates im Worktree mit cwd = Worktree starten** (`env -C <wt> python ...`), solange sie cwd-relativ lesen (Liste in gates_und_ci): sonst messen sie still den Hauptbaum, grün. Kontrollwert: eine Zahl, die zwischen beiden Bäumen differiert, muss kippen. `count-editorial-notes-and-div-heads.py` braucht `--corpus <wt>/tei` (#493).

**Vergleichen**
- gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, JSON-Walk bzw. `json.dumps(sort_keys=True)`.
- Nach lxml-Serialisierung c14n vergleichen (`remove_blank_text`/`pretty_print` ändern alle 667 Dateien).
- **CRLF-Befund an einer Spec erst mit Probe:** JS `$` mit `m`-Flag matcht auch vor `\r`; `node -e` auf einer CRLF-Kopie entkräftet den Fehlalarm.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex (trifft nur einwertige). `@lemmaRef` = `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- `findall` statt `find` (Doppelsiglen); lxml `find('x')` = nur direkte Kinder; `id(elem)` ist keine Identität (Proxies): `tree.getpath()` + Datei.
- JS `Math.round` = `math.floor(x + 0.5)`, nicht Pythons `round()`. Tokens (w+pc) sind nicht Wörter; Messung auf die Feldmenge des Codes bringen.
- Restsuche nach Katalogzahlen nicht über das Nomen (`tools|modules`): Zahlwörter allein greppen, jede Zeile lesen.
- Katalog-/Bereichsende am Rahmen messen, nicht per Zeilenfenster. Zahlsuche mit `\b`. CSVs oft `;` + BOM (`utf-8-sig`). Leere Suche: Kontrollwert (`type="sigle"` = 667 Dateien).

**JS ohne Browser**
- **Browser-ES-Modul prüfen:** Datei aus `assets/js/lib/` als `.mjs`-Kopie ins Scratch, dynamisch importieren (`.js` scheitert ohne `type: module`); geht, solange `document`/`window` nur in ungerufenen Funktionen stehen. Unter Node 24.21 (10.10.) ging der direkte `pathToFileURL`-Import von `assets/js/search/search-engine.js` samt `data/*.json.gz` (gunzipSync) ohne Kopie: `new SearchEngine(auth, corp)`, dann `searchLemma`/`resolveSearchTerm` echt.
- **Leistungsfalle:** `for (k in obj) { break; }` als „ist leer“-Probe ist auf `corpusIndex.lemmaIndex` (Dictionary-Mode, ~42k Schlüssel) O(n), Millisekunden je Aufruf gegen ~0 für den Property-Zugriff. Leerprüfungen auf großen Index-Objekten zeitmessen.
- **Alt-gegen-neu der Auflösung nicht über alle Schlüssel** (jede Auflösung scannt ~44k Lemmata, Volllauf >600 s): Stichprobe (jeder 25. Schlüssel plus alle mit mehreren Lemmata gleicher Ansetzung). Fassungen per `git archive <rev> assets/js/lib assets/js/search | tar -x` ins Temp, Basis in eigenen Unterordner, `package.json` mit `type: module` daneben.
- **Alt/neu eines Browser-Moduls ohne Baumkopie:** `execFileSync('git',['show','origin/main:<datei>'])` im Probeskript, die relativen `'../../../assets/js/lib/'`-Importe per `split/join` auf `pathToFileURL(<wt>/assets/js/lib/)` umschreiben (Ersetzungszahl asserten), als `.mjs` nach Temp, beide importieren. Synthetische Daten mit doppelten IDs, fehlendem `lemma`, Mutationsfolgen; `structuredClone` für zwei gleiche Datensätze.
- **Node-Zeitmessung ist reihenfolgeabhängig:** derselbe Fall ist allein ~3x schneller als im selben Prozess nach anderen Eingaben (JIT-Zustand der geteilten `lib/`-Module; überlebt `gc()` und frische Instanz). Budget aus Einzelmessung x1,5 reicht dann nicht: Fall isoliert und in der Gate-Reihenfolge messen. `ms > budget` ist bei NaN falsch (`--reps 0` gab GRUEN). Probe als `node --expose-gc --input-type=module -e` mit relativen Importen vom Worktree aus.
- **Zeitgate mit Runner-Budget: lokale Rotzahl ist keine Mutationswirkung:** `benchmark-search.mjs` ist lokal unverändert teilweise rot. Eine Mutation zählt nur auf den Fällen, deren Codepfad sie trifft; immer ein unmutierter Lauf daneben. Mutation ohne Baumänderung: Manager-Kopie mit umgeschriebenen Importen nach Temp, `--manager <kopie.mjs>`. Runner-Werte: `gh run view <id> --log`; ein `pull_request`-Lauf prüft den Merge-Commit, `workflow_dispatch` den Zweigkopf.
- **Mutationsprobe ohne Dateiänderung (#463 R5):** im Node-Lauf die Methode an der Instanz überschreiben (`am.getAttestationIndex = () => roh`), dieselbe Eingabe: zeigt, ob die Spec-Erwartung die entfernte Schutzschicht unterscheidet.
