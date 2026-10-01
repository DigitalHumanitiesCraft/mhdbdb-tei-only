---
name: querschnitt-messen
description: Mess- und Probenrezepte in Python (importlib in-process, Mutationsproben, Scratch-Nachbau, gz/c14n-Vergleich) und wiederkehrende Zaehlfallen
metadata:
  type: project
---
Stand 28.09.2026.

**In-process statt Baum anfassen**
- `importlib.util.spec_from_file_location`, vorher `sys.path.insert(0, '<repo>/scripts')` (corpus_files) und bei cwd-relativen Pfaden `os.chdir`. Patchen: `mod.corpus_files = lambda: [kopien]`, `mod.LEXICON = <scratch>`, `sys.argv`; `main()` in `redirect_stdout`, SystemExit fangen. Sekunden statt Minuten.
- Alt/neu: `git show <alt>:<skript> > scratch/old.py`, beide laden, auf frisch geparsten Baeumen anwenden, `etree.tostring` vergleichen (spart 1,4-GB-Kopie).
- Netz: `sys.modules["requests"]` vor dem Import stubben.
- Mutationsprobe: Quelle lesen, `str.replace` mit `count == 1`-Assert, Scratch-Datei, laufen, FAIL zaehlen; oder `inspect.getsource` + replace + `exec` im Modulnamensraum. Vorher sichern, dass die Probe die Stelle trifft.
- `build-corpus-index.py` in-process: `build_corpus_index(jobs=1)` (sonst BrokenProcessPool), mehrere Minuten. Builds haben keine Output-Option und ueberschreiben data/: nie im Baum laufen lassen; Nachbau im Scratch (Skript + Hilfsmodule wie mhg_normalizer.py, tei_namespaces.py + authority-files, `--allow-dirty`; PROJECT_ROOT haengt an `__file__`/`parents[N]`).
- Sandkasten ohne Korpuskopie: Scratch-ROOT mit Skript + `scripts/corpus_files.py`, tei/ als Symlinks, geaenderte Dateien per `git show` als echte Kopie.
- Apply-Skript reproduzieren: betroffene Dateien per `git show origin/main:` ins Scratch, Skript in gleicher Verzeichnistiefe, `--apply`, Bytevergleich gegen HEAD.
- Generierte Seite bitidentisch: Zielpfad (z.B. `ZIEL`) auf $TEMP biegen, `main()`.
- **Gates im Worktree mit cwd = Worktree starten** (`env -C <wt> python ...`): `doc-count-audit.py` und `validate-corpus.py` lesen cwd-relativ und messen sonst still den Hauptbaum, gruen. Kontrollwert: eine Zahl, die zwischen beiden Baeumen differiert, muss kippen.

**Vergleichen**
- gz nie auf Bytes (lokales zlib != Runner): dekomprimieren, rekursiver JSON-Walk bzw. `json.dumps(sort_keys=True)`.
- Nach lxml-Serialisierung c14n vergleichen, nicht Repo-Bytes (`remove_blank_text`/`pretty_print` aendern alle 667 Dateien).
- Byte-Block ueber Revisionen: sha1 + Laenge + Nachbarueberschrift je Rev.

**Zaehlfallen**
- @ana, @corresp, @lemmaRef per `split()`, nie per `attr="#id"`-Regex (trifft nur einwertige). `@lemmaRef` = `lexicon.xml#lemma_N`: `split('#')[-1]`, nicht `lstrip('#')`.
- Schema nie aus `items[0].keys()`: optionale Felder stehen nur an Traegern, Counter ueber alle.
- `findall` statt `find` (erste Sigle allein verfehlt Doppelsiglen); lxml `find('x')` = nur direkte Kinder.
- lxml `id(elem)` ist keine Identitaet (Proxies teilen Adressen): `tree.getpath()` + Datei.
- Grosse Listen: Index-Dict statt `list.index`.
- Umlaut-Regex mit `[äöüÄÖÜ]`; Zahl haengt an der Feldmenge: Messung auf die Feldmenge des Codes (Getter) bringen.
- Rundung wie das Modul: JS `Math.round` = `math.floor(x + 0.5)`, nicht Pythons `round()` (Banker).
- Tokens (w+pc) sind nicht Woerter.
- Katalog-/Bereichsende am Rahmen messen, nicht per Zeilenfenster.
- Zahlsuche mit `\b` (ingest/wzb-Koordinaten wie `1051,986`).
- CSVs im Repo: oft `;` + BOM (`utf-8-sig`).
- Leere Suche: Kontrollwert mitmessen (z.B. `type="sigle"` = 667 Dateien).
- **Browser-ES-Modul ohne Browser pruefen (30.09., #448):** Datei aus `assets/js/lib/` per `fs` als `.mjs`-Kopie ins Scratch, dynamisch importieren (package.json ohne `type: module`, ein `.js`-Import scheitert). Geht, solange `document`/`window` nur in ungerufenen Funktionen stehen. XLSX aus `toXlsx`: `zipfile.testzip()` (None = alle CRC ok) + `infolist()` fuer Offsets, dann openpyxl 3.1.5 (`font.b`, `freeze_panes`, Zelltyp, Spalte AD fuer columnName). Umlaute in der Konsole als `�` sind cp1252, kein Datenbefund.
- **Arbeiter-Schleife mit `Promise.all`:** wirft ein Worker, laufen die anderen weiter und rufen den Fortschritts-Callback noch; im Scratch mit setTimeout-Promises nachbauen, 8 Dateien, eine wirft, Statusobjekt nach 300 ms lesen. Am 30.09. in multi-lemma-export.js gemessen (Fehlertext durch `Lade Texte … 7 / 8` ersetzt).
- **Repo-Skript mit `--apply`-Schalter: der Classifier sperrt auch den Trockenlauf** (30.09., #493, "Irreversible Local Destruction"). Weg ohne Umgehung: `git archive origin/main tei/ | tar -x -C scratch/alt` und dasselbe fuer HEAD (je ~1 min fuer 667 Dateien), Modul per importlib laden, `neuer_satz`/`zaehle` auf den Kopien nachfahren. Liefert nebenbei die Zieltabelle des alten Baums und die Idempotenzprobe auf dem neuen.
- **"Idempotent" bei einem Satz-Ersetzungsskript heisst: die eigene Ausgabe wird wieder erkannt.** Auf HEAD klassifizieren, nicht dem Marker glauben: #493 lief auf seiner Ausgabe in 559 `UnbekannterSatz` (Regex kannte "semantisch disambiguiert" nicht), der Marker-Zweig war damit tot.
- **Idempotenz am Apply-Pfad messen, nicht am Trockenlauf** (30.09., #493 Runde 2): Kopie von 2 Dateien ins Scratch, `TEI_DIR`/`PLAN`/`REPO` patchen, `--apply` zweimal. Der Trockenlauf war sauber (572 stimmt schon), der zweite `--apply` kuerzte die committete Plan-CSV auf die Kopfzeile (`open("w")` ohne Rueckfrage bei 0 Aenderungen) und der `<change>`-Ersatz verliert den Originalwortlaut im "Vorher". Fuer die Fangfrage "erkennt EIGEN einen Altsatz falsch": alle 572 Altsaetze aus `git archive origin/main` per `fullmatch` pruefen, plus Kontrollwert "semantisch" in irgendeinem Altsatz (0).
- **CRLF-Befund an einer Playwright-Spec erst mit Probe:** JS `$` mit `m`-Flag matcht auch vor `\r` (ECMAScript-LineTerminator umfasst CR), `/^...$/m` auf CRLF-Text trifft also. Am 29.09. fast als A gemeldet; `node -e` auf einer `sed 's/$/\r/'`-Kopie im Scratch entkraeftet es in Sekunden. `git ls-files --eol <datei>` zeigt, was im Baum liegt (hier `*.md text=auto` + autocrlf=true: w/crlf), ein Build-Skript, das LF schreibt, bleibt trotzdem `git status`-sauber.
