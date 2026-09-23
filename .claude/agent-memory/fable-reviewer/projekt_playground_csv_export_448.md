---
name: projekt-playground-csv-export-448
description: Review-Lehren zum CSV-Export der Playground-Werkzeuge (#448, 23.09.2026): Helfer-Probe per file://-Import, Tailwind-Zaehlung, Messwerte minne/PZ-ERB, Horses ohne Klappzeilen
metadata:
  type: project
---

Review Runde 1 von #448 (claude/nacht-b4-448, dfa5c8a0a gegen 905a771c6), 23.09.2026.

**Messwerte, die wieder gebraucht werden:**
- `minne` loest auf genau lemma_4130 auf (einziges Lemma mit lemma == 'minne', Suche nimmt Stage 1 auf `normalized`); 338 Texte, davon 4 mit Komma in Titel/Autor (FR1, FR2, HVM, PL1), 0 mit Anfuehrungszeichen. Skript: corpus-index.json.gz laden, `texts[].lemmata` keys pruefen.
- Textvergleich PZ/ERB: 4.512 / 1.756 Lemmata, beide 1.350, nur PZ 3.162, nur ERB 406 (TOP_N_DEFAULT 100 kappt also).
- Anzeigegrenzen: word-frequency 50, verse-ending 50, cooccurrence 50, text-comparison 100, rhyme MAX_VISIBLE_PARTNERS 200.
- horses-explorer.js hat KEINE aufklappbaren Zeilen (grep expanded = 0); nur naming-explorer.js hat expandedTerms. FEATURES.md behauptete es fuer beide.
- Alter app.js-BOM (905a771c6:1443) und neuer Helfer (csv-export.js:37) tragen beide das literale Zeichen EF BB BF; `od -c` auf `git show <sha>:pfad | grep` zeigt es.

**Verfahren:**
- ESM-Helfer ohne Browser pruefen: `.mjs` in $TEMP mit `import ... from 'file:///C:/.../assets/js/lib/csv-export.js'`, alte Funktion woertlich daneben kopieren und ueber eine Probenliste vergleichen. Node 24: `node --check` akzeptiert ESM-Dateien direkt.
- Tailwind-Klassen im gepurgten CSS zaehlen: Python-Regex `\.` + escaped Klasse (`:` -> `\:`, `.` -> `\.`) + Lookahead `[\s{,:.\[>]`, sonst trifft `.flex` auch `.flex-wrap`.
- Worktree-Guard lehnt Verbundkommandos mit `cd` und dem Pfadwort „Git" ab; `git -C <worktree-pfad>` und einfache relative Kommandos gehen durch.
- Inventar-Gate heisst `scripts/audit/check-doc-inventories.py` (Plural); DEVELOPMENT.md:202 nennt ihn richtig, das Spec-Inventar zaehlt 40/40, lib-README 8/8.

**Runde 2 (23.09.2026, 372ca69ed gegen 3a5ff3158, nach Rebase):**
- Rebase-Probe: `git range-diff <alte-basis>..<alter-zweig> <neue-basis>..<neuer-zweig>`; die vier Code/Test/Doku-Commits kamen als `=`, nur der Memory-Commit als neu (MEMORY.md-Konflikt). Ob der Konflikt sauber geloest ist, zeigt `git diff --stat <alt> <neu> -- <b4-dateien>` leer.
- Multi-Lemma-Suche: `fetch` steht NICHT in multi-lemma-search.js (importiert nur router.js), sondern in ui-helpers.js:379-395 (Click auf `.result-summary`, erstes Aufklappen) und :441 (`enrichFileResults`). Ein grep auf `fetch` in der Werkzeugdatei liefert 0 und widerlegt den JOURNAL-Satz nicht.
- `playground/js/ui/tei` = 15 Dateien per `git ls-files`; 13 Werkzeuge ohne corpus-scope.js und tei-ui.js; 9 mit csvButton (naming 2 Aufrufe), 1 Hapax (Semikolon, `_lastFiltered` = alle Seiten), 3 ohne (concept-distribution, lemma-distribution, multi-lemma-search).
- Issue #448 hatte am 23.09. abends 0 Kommentare und 0 PRs mit head claude/nacht-b4-448 (`api.github.com/.../issues/448/comments`, `/pulls?head=Org:zweig&state=all`); JOURNAL-Saetze ueber Statuskommentar und PR-Body sind Bedingungen, keine Messungen.
- Lizenzen: Linda CC BY-NC-SA 4.0 steht in DATA-MODEL.md:371, Borek CC0 1.0 in :410; Seiten-Attribution naming-explorer.js:1140, horses-explorer.js:383.
- Gates laufen im Worktree mit relativem Pfad (`python -X utf8 scripts/audit/check-no-em-dash.py --diff-base origin/main`), der cwd-Reset stellt das Worktree wieder her.

**Runde 3 (23.09.2026, 4fcdf945d gegen d166fa4b1, Cherry-pick nach B3-Merge):**
- Nullprobe fuer den Neuaufbau: `git diff <alter JOURNAL-Commit> HEAD --stat` zeigt nur die Dateien, die main seither brachte (B3 + Kickoff-Zeile + Memory); B4-Code taucht nicht auf. Dateimengen B3/B4 disjunkt bis auf JOURNAL.md und MEMORY.md, beide reine Anhaenge (JOURNAL-Hunk `@@ -777,3 +777,24 @@` ohne Minus-Zeilen).
- Werkzeugzaehlung in der Landing: `<button id="...Btn">` in playground/index.html per awk ueber Zeilen 245-470: 19 = 6 (Korpusanalysen) + 6 (Normdaten, dazwischen) + 7 (Weitere Korpusanalysen); die 13 des Kommentars sind 6 + 7.
- „bis zu 50 Fundstellen je Karte" der Multi-Lemma-Suche sitzt in tei-ui.js:200 (`fileResults.slice(0, 50)`), nicht in ui-helpers.js oder multi-lemma-search.js; `\b50\b` trifft dort nur Tailwind-Farben.
- Textvergleich-Kopf ist dynamisch (`PZ (A)`, `ERB (B)`), der Kommentar paraphrasiert ihn als „Anzahl in A/B"; Versposition ebenso (`Treffer am ${positionLabel}`).
- Guard lehnt `cd /dev/null; W=...; git -C "$W"` ab; plain `git ...; git ...` mit relativen Pfaden in einer Kette geht durch.

**Why:** Die Zahlen im Commit („4 Texte mit Komma") und in der Hilfe („50 oder 100 Zeilen") sind genau die Klasse-B-Kandidaten, die eine Folgerunde sonst neu misst.
**How to apply:** Bei Folgerunden zu #448 oder neuen Exporten die Grenzen und die minne-Zahlen von hier nehmen und nur bei Indexwechsel neu messen.
