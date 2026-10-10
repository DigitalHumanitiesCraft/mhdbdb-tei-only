---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python/JS (importlib in-process, Mutationsproben, Scratch-Nachbau, Rebuild-and-Compare, gz/c14n-Vergleich, find-mentions-Probe) und wiederkehrende Zählfallen
metadata:
  type: project
---
Verdichtet 08.10.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')` und bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`; `main()` in `redirect_stdout`, SystemExit fangen.
- Alt/neu: `git show <alt>:<skript> > scratch/old.py`, beide laden, auf frisch geparsten Bäumen anwenden, `etree.tostring` vergleichen (spart 1,4-GB-Kopie).
- Netz: `sys.modules["requests"]` vor dem Import stubben. **find-mentions.py `main()` ohne Netz (<1 s):** zusätzlich `fm.zotero_baseline`, `fm.SOURCES` (Tupel mit einer Funktion, `__name__` setzen), `fm.zotero_write` ersetzen, `fm.PROBLEME` zwischen Fällen leeren, cwd ins Scratch (candidates.json). Kandidatentitel brauchen fast disjunkte Wortmengen (>= 85 % Überlappung gilt als bekannt).
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, FAIL zählen; oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft.
- **Rebuild-and-Compare ohne Baumkopie (#540):** `build_index()` / `build_corpus_index(jobs=1)` (sonst BrokenProcessPool) geben den Index nur zurück; `save_index(index)` schreibt nach Modul-Global `OUTPUT_FILE`. Modul per importlib, `os.chdir(<wt>)`, `mod.OUTPUT_FILE = <scratch>/fresh.json.gz`, bauen, speichern, dekomprimierte Bytes gegen `data/*.json.gz` halten (Authority ~1 min, Korpus ~5 min). `extract-variants.py` ohne `--apply`: `variants.regen.xml` (gates_und_ci) muss gegen `variants.xml` leer diffen, Datum eingeschlossen (der Dry-Run übernimmt das alte Datum bei fünf Nullzählern).
- Nachbau im Scratch (Builds überschreiben data/): Skript + mhg_normalizer.py, tei_namespaces.py + authority-files, `--allow-dirty`; PROJECT_ROOT hängt an `__file__`. Authority-Build braucht zusätzlich `scripts/build-corpus-index.py` und `data/corpus-index.json.gz`.
- Sandkasten ohne Korpuskopie: Scratch-ROOT mit Skript + `scripts/corpus_files.py`, tei/ als **Hardlinks (`os.link`, auf Windows statt Symlink)**, die mutierte Datei als echte Kopie. Cwd-relative Skripte: Kopie unter `scripts/audit/`, Start mit `env -C <scratch>`.
- Apply-Skript reproduzieren: betroffene Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD. Bei `parents[3]`-REPO (projekt_526_breve_makron) muss `--out-dir` unter dem Scratch-REPO liegen (der Pfad steht wörtlich im `<change>`).
- **Skript mit `--apply`-Schalter:** der Classifier sperrte am 30.09. auch den Trockenlauf (#493), am 08.10.2026 lief derselbe als Subagent durch. Je Session probieren. Falls gesperrt, ohne Umgehung: `git archive origin/main tei/ | tar -x -C scratch/alt`, Modul per importlib laden, auf den Kopien nachfahren.
- **„Idempotent" bei einem Ersetzungsskript heißt: die eigene Ausgabe wird wieder erkannt.** Auf HEAD klassifizieren, nicht dem Marker glauben (#493 lief auf seiner Ausgabe in `UnbekannterSatz`). Idempotenz am **Apply-Pfad** messen: Kopie von 2 Dateien ins Scratch, `TEI_DIR`/`PLAN`/`REPO` patchen, `--apply` zweimal.
- **Gates im Worktree mit cwd = Worktree starten** (`env -C <wt> python ...`), solange sie cwd-relativ lesen (Liste in gates_und_ci): sonst messen sie still den Hauptbaum, grün. Kontrollwert: eine Zahl, die zwischen beiden Bäumen differiert, muss kippen. `scripts/audit/count-editorial-notes-and-div-heads.py` braucht dafür `--corpus <wt>/tei` (sonst Hauptbaum, #493).

**Vergleichen**
- gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, rekursiver JSON-Walk bzw. `json.dumps(sort_keys=True)`.
- Nach lxml-Serialisierung c14n vergleichen (`remove_blank_text`/`pretty_print` ändern alle 667 Dateien).
- **CRLF-Befund an einer Spec erst mit Probe:** JS `$` mit `m`-Flag matcht auch vor `\r`; `node -e` auf einer CRLF-Kopie entkräftet den Fehlalarm.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex (trifft nur einwertige). `@lemmaRef` = `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- Schema nie aus `items[0].keys()`: optionale Felder stehen nur an Trägern, Counter über alle.
- `findall` statt `find` (Doppelsiglen); lxml `find('x')` = nur direkte Kinder.
- lxml `id(elem)` ist keine Identität (Proxies teilen Adressen): `tree.getpath()` + Datei.
- Rundung wie das Modul: JS `Math.round` = `math.floor(x + 0.5)`, nicht Pythons `round()`.
- Tokens (w+pc) sind nicht Wörter. Zahl hängt an der Feldmenge: Messung auf die Feldmenge des Codes bringen. Umlaut-Regex mit `[äöüÄÖÜ]`.
- Restsuche nach Katalogzahlen nicht über das Nomen (`tools|modules`): die Explorer heißen in FEATURES „controlled vocabularies" (:143, „six"), Werkzeuge auch „the other ten". Zahlwörter allein greppen und jede Zeile lesen (#451 R2, zwei Runden übersehen).
- Katalog-/Bereichsende am Rahmen messen, nicht per Zeilenfenster. Zahlsuche mit `\b`. CSVs im Repo oft `;` + BOM (`utf-8-sig`). Leere Suche: Kontrollwert mitmessen (`type="sigle"` = 667 Dateien).
- **Browser-ES-Modul ohne Browser prüfen:** Datei aus `assets/js/lib/` als `.mjs`-Kopie ins Scratch, dynamisch importieren (ein `.js`-Import scheitert ohne `type: module`); geht, solange `document`/`window` nur in ungerufenen Funktionen stehen.
