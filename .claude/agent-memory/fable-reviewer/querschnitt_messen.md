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
