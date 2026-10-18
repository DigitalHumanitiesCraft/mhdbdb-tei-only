---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python/JS (importlib in-process, Mutationsproben, Scratch-Nachbau, Rebuild-and-Compare, gz/c14n-Vergleich) und wiederkehrende Zählfallen
metadata:
  type: project
---
Verdichtet 18.10.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')`, bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`; `main()` in `redirect_stdout`, SystemExit fangen.
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, FAIL zählen; oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft. Steht die Eingabevalidierung hinter einem Korpuslauf von Minuten, den Block per `src[src.index(a):src.index(b)]` ausschneiden und mit nachgebauten Vorbedingungen `exec`en; die Kontrollvariante ohne Mutation muss durchlaufen.
- **Rebuild-and-Compare ohne Baumkopie:** `build_index()` / `build_corpus_index(jobs=1)` (sonst BrokenProcessPool) geben den Index nur zurück; `save_index(index)` schreibt nach Modul-Global `OUTPUT_FILE`. Modul per importlib, `os.chdir(<wt>)`, `mod.OUTPUT_FILE = <scratch>/fresh.json.gz`, bauen, speichern, dekomprimierte Bytes gegen `data/*.json.gz` halten. `extract-variants.py` ohne `--apply`: `variants.regen.xml` muss gegen `variants.xml` leer diffen, Datum eingeschlossen.
- Apply-Skript reproduzieren: betroffene Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD. Sperrt der Classifier `--apply`, ohne Umgehung: `git archive origin/main tei/ | tar -x -C scratch/alt`, Modul per importlib, auf den Kopien nachfahren.
- **Gates im Worktree mit cwd = Worktree starten** (`env -C <wt> python ...`), solange sie cwd-relativ lesen (Liste in projekt-gates-und-ci): sonst messen sie still den Hauptbaum, grün. Kontrollwert: eine Zahl, die zwischen beiden Bäumen differiert, muss kippen. `count-editorial-notes-and-div-heads.py` braucht `--corpus <wt>/tei` (#493).

**Vergleichen:** gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, JSON-Walk bzw. `json.dumps(sort_keys=True)`. Nach lxml-Serialisierung c14n vergleichen (`remove_blank_text`/`pretty_print` ändern alle 667 Dateien). CRLF-Befund an einer Spec erst mit Probe: JS `$` mit `m`-Flag matcht auch vor `\r`; `node -e` auf einer CRLF-Kopie entkräftet den Fehlalarm.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex (trifft nur einwertige). `@lemmaRef` = `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- `findall` statt `find` (Doppelsiglen); lxml `find('x')` = nur direkte Kinder; `id(elem)` ist keine Identität (Proxies): `tree.getpath()` + Datei.
- JS `Math.round` = `math.floor(x + 0.5)`, nicht Pythons `round()`. Tokens (w+pc) sind nicht Wörter.
- Restsuche nach Katalogzahlen nicht über das Nomen (`tools|modules`): Zahlwörter allein greppen, jede Zeile lesen. Zahlsuche mit `\b`. CSVs oft `;` + BOM (`utf-8-sig`). Leere Suche: Kontrollwert (`type="sigle"` = 667 Dateien).

**JS ohne Browser**
- **Browser-ES-Modul prüfen:** Datei aus `assets/js/lib/` als `.mjs`-Kopie ins Scratch, dynamisch importieren; geht, solange `document`/`window` nur in ungerufenen Funktionen stehen. Unter Node 24 ging der direkte `pathToFileURL`-Import von `assets/js/search/search-engine.js` samt `data/*.json.gz` (gunzipSync) ohne Kopie: `new SearchEngine(auth, corp)`, dann `searchLemma`/`resolveSearchTerm` echt.
- **Alt-gegen-neu der Auflösung nicht über alle Schlüssel** (Volllauf >600 s): Stichprobe (jeder 25. Schlüssel plus alle mit mehreren Lemmata gleicher Ansetzung); Fassungen per `git archive <rev> assets/js/lib assets/js/search | tar -x` ins Temp, `package.json` mit `type: module` daneben. Ohne Baumkopie: `git show origin/main:<datei>`, die relativen Importe per `split/join` auf `pathToFileURL(<wt>/assets/js/lib/)` umschreiben (Ersetzungszahl asserten), als `.mjs` nach Temp.
- **Node-Zeitmessung ist reihenfolgeabhängig** (JIT-Zustand): Fall isoliert und in der Gate-Reihenfolge messen. `ms > budget` ist bei NaN falsch (`--reps 0` gab GRUEN).
- **Zeitgate mit Runner-Budget: lokale Rotzahl ist keine Mutationswirkung** (`benchmark-search.mjs` ist lokal unverändert teilweise rot). Eine Mutation zählt nur auf den Fällen, deren Codepfad sie trifft; immer ein unmutierter Lauf daneben. Mutation ohne Baumänderung: Manager-Kopie mit umgeschriebenen Importen nach Temp, `--manager <kopie.mjs>`. Ein `pull_request`-Lauf prüft den Merge-Commit, `workflow_dispatch` den Zweigkopf.
