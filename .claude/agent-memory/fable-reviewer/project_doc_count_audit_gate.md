---
name: doc-count-audit-gate
description: Wie doc-count-audit.py zu pruefen ist: Altstand ohne tei/ nachfahren, INTENTIONALLY_SILENT ist nur Selbstpruefung, Baumzeilen sind ungegatet (Review fix/doc-count-corpus-scope, 2026-09-18)
metadata:
  type: project
---

`scripts/audit/doc-count-audit.py` laesst sich fuer einen alten Stand ohne das
Korpus nachfahren: `git archive <sha> docs/... README.md playground/readme.md
hilfe-playground.html playground/js/ui playground/index.html
scripts/audit/doc-count-audit.py | tar -x -C <scratch>`, dann ein
importlib-Treiber mit `sys.path.insert(0, <repo>/scripts)` (fuer
`mhg_normalizer`, `corpus_files`), `os.chdir(<scratch>)`, und nur
`collect_code_counts()` + `find_stale_wordcounts` ueber `CODE_DOC_TARGETS`
aufrufen. `collect_counts()` parst tei/ und braucht das ganze Korpus; fuer
`check_anchor_coverage` reicht ein Platzhalter-Dict mit grossen Werten, weil
dort nur die Untergrenze zaehlt. Missing-file-Gaps aus dem Scratch ignorieren.

**Why:** Am 18.09.2026 hiess es in Commit-Message, fehlerjournal.md und
Auftrag „sechs Stellen in drei Dateien"; der Altstand meldet 11 Treffer in 9
(Datei,Key)-Paaren ueber 5 Dateien (DESIGN.md und playground/readme.md waren
nicht mitgelesen). Die Zahl war aus der abgeschnittenen Ausgabe gelesen.

**How to apply:**
- `INTENTIONALLY_SILENT` wird nur in `check_anchor_coverage` gelesen (Zeilen
  ~840/851) und nie im Drift-Scan; der Exit-Code haengt allein an
  `total_drift`. Ein Eintrag dort gatet nichts ab und sein Entfernen gatet
  nichts neu; „silent-obsolet" ist eine Meldung ohne Exit-Wirkung.
- `TREE_LINE_RE` ueberspringt Baumzeilen (`│├└`), und „fourteen files" hat
  keinen Anker: die Dateizahl von `playground/js/ui/tei/` in
  ARCHITECTURE.md (Baum ~:205, Prosa ~:230) und die Klammer in DESIGN.md:162
  sind ungegatet und driften bei jedem Hilfsmodul ohne Einstiegspunkt
  (corpus-scope.js seit #204). Bei jeder Aenderung an NON_TOOL_MODULES dort
  nachsehen.
- Einstiegspunkt eines tei/-Moduls messen: Import in
  `playground/js/playground-main.js`, Route in `playground/js/ui/core/router.js`,
  Button in `playground/index.html`; Kontrollwert `hapax-legomena` trifft an
  allen drei Stellen.
- Zeilenenden nie am Arbeitsbaum messen: `core.autocrlf=true` und
  `*.md text=auto` (.gitattributes:10) machen aus einem LF-Blob eine
  CRLF-Kopie (`git ls-files --eol` zeigt `i/lf w/crlf`). Was committet ist,
  sagt `git show HEAD:<datei>`; am 18.09.2026 hiess es „420 CRLF", der Blob
  hatte 0 CRLF und 420 LF (Runde 2).
- Mutationsprobe fuer einen Anker: `find_stale_wordcounts(doc, wert+1, key)`
  bzw. `find_stale_numbers(doc, 240000, 'variants_normalized')` in-process;
  DECISIONS.md:1256/:1288 binden `234,245` und werden beim naechsten
  Mapping-Wechsel gemeldet, obwohl DEVELOPMENT.md:271 datierte ADR-Zahlen
  ausnimmt.
