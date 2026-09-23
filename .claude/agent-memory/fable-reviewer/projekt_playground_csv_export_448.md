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

**Why:** Die Zahlen im Commit („4 Texte mit Komma") und in der Hilfe („50 oder 100 Zeilen") sind genau die Klasse-B-Kandidaten, die eine Folgerunde sonst neu misst.
**How to apply:** Bei Folgerunden zu #448 oder neuen Exporten die Grenzen und die minne-Zahlen von hier nehmen und nur bei Indexwechsel neu messen.
