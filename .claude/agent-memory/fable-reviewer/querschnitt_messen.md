---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python/JS (importlib in-process, Mutationsproben, Scratch-Nachbau, gz/c14n-Vergleich, find-mentions-Probe) und wiederkehrende Zählfallen
metadata:
  type: project
---
Verdichtet 02.10.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')` und bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`; `main()` in `redirect_stdout`, SystemExit fangen.
- Alt/neu: `git show <alt>:<skript> > scratch/old.py`, beide laden, auf frisch geparsten Bäumen anwenden, `etree.tostring` vergleichen (spart 1,4-GB-Kopie).
- Netz: `sys.modules["requests"]` vor dem Import stubben. **find-mentions.py `main()` ohne Netz (<1 s):** zusätzlich `fm.zotero_baseline`, `fm.SOURCES` (Tupel mit einer Funktion, `__name__` setzen), `fm.zotero_write` ersetzen, `fm.PROBLEME` zwischen Fällen leeren, cwd ins Scratch (candidates.json). Kandidatentitel brauchen fast disjunkte Wortmengen (>= 85 % Überlappung gilt als bekannt): `f"MHDBDB zq{i:02d}ab zq{i:02d}cd zq{i:02d}ef"`. Exit 1 im Schreibpfad jenseits PROBLEME: Zotero-Ablehnung, Kappung, fehlender ZOTERO_API_KEY; candidates.json trägt immer alle Kandidaten, Zotero nur MAX_NEU.
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, FAIL zählen; oder `inspect.getsource` + replace + `exec`. Vorher sichern, dass die Probe die Stelle trifft.
- `build-corpus-index.py` in-process: `build_corpus_index(jobs=1)` (sonst BrokenProcessPool), mehrere Minuten. Builds überschreiben data/: nie im Baum laufen lassen; Nachbau im Scratch (Skript + mhg_normalizer.py, tei_namespaces.py + authority-files, `--allow-dirty`; PROJECT_ROOT hängt an `__file__`).
- Sandkasten ohne Korpuskopie: Scratch-ROOT mit Skript + `scripts/corpus_files.py`, tei/ als **Hardlinks (`os.link`, auf Windows statt Symlink)**; die mutierte Datei als echte Kopie. Für cwd-relative Skripte (validate-corpus.py) Skriptkopie unter `scripts/audit/`, Start mit `env -C <scratch>`.
- Apply-Skript reproduzieren: betroffene Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD.
- **Gates im Worktree mit cwd = Worktree starten** (`env -C <wt> python ...`): `doc-count-audit.py` und `validate-corpus.py` lesen cwd-relativ und messen sonst still den Hauptbaum, grün. Kontrollwert: eine Zahl, die zwischen beiden Bäumen differiert, muss kippen.

**Vergleichen**
- gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, rekursiver JSON-Walk bzw. `json.dumps(sort_keys=True)`.
- Nach lxml-Serialisierung c14n vergleichen (`remove_blank_text`/`pretty_print` ändern alle 667 Dateien).
- Byte-Block über Revisionen: sha1 + Länge + Nachbarüberschrift je Rev.

**Zählfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex (trifft nur einwertige). `@lemmaRef` = `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- Schema nie aus `items[0].keys()`: optionale Felder stehen nur an Trägern, Counter über alle.
- `findall` statt `find` (Doppelsiglen); lxml `find('x')` = nur direkte Kinder.
- lxml `id(elem)` ist keine Identität (Proxies teilen Adressen): `tree.getpath()` + Datei.
- Rundung wie das Modul: JS `Math.round` = `math.floor(x + 0.5)`, nicht Pythons `round()`.
- Tokens (w+pc) sind nicht Wörter. Zahl hängt an der Feldmenge: Messung auf die Feldmenge des Codes bringen. Umlaut-Regex mit `[äöüÄÖÜ]`.
- Katalog-/Bereichsende am Rahmen messen, nicht per Zeilenfenster. Zahlsuche mit `\b`. CSVs im Repo oft `;` + BOM (`utf-8-sig`). Leere Suche: Kontrollwert mitmessen (`type="sigle"` = 667 Dateien).
- **Browser-ES-Modul ohne Browser prüfen:** Datei aus `assets/js/lib/` als `.mjs`-Kopie ins Scratch, dynamisch importieren (ein `.js`-Import scheitert ohne `type: module`); geht, solange `document`/`window` nur in ungerufenen Funktionen stehen. Bei `Promise.all`-Arbeiterschleifen laufen die anderen Worker nach einem Wurf weiter und rufen den Callback noch: mit setTimeout-Promises nachbauen.
- **Skript mit `--apply`-Schalter: der Classifier sperrt auch den Trockenlauf** (#493, „Irreversible Local Destruction"). Weg ohne Umgehung: `git archive origin/main tei/ | tar -x -C scratch/alt` (je ~1 min), Modul per importlib laden, auf den Kopien nachfahren.- **„Idempotent" bei einem Ersetzungsskript heißt: die eigene Ausgabe wird wieder erkannt.** Auf HEAD klassifizieren, nicht dem Marker glauben (#493 lief auf seiner Ausgabe in 559 `UnbekannterSatz`). Idempotenz am **Apply-Pfad** messen, nicht am Trockenlauf: Kopie von 2 Dateien ins Scratch, `TEI_DIR`/`PLAN`/`REPO` patchen, `--apply` zweimal (der zweite kürzte die Plan-CSV auf die Kopfzeile).
- **CRLF-Befund an einer Spec erst mit Probe:** JS `$` mit `m`-Flag matcht auch vor `\r`; `node -e` auf einer CRLF-Kopie entkräftet den Fehlalarm. `git ls-files --eol <datei>` zeigt, was im Baum liegt.
