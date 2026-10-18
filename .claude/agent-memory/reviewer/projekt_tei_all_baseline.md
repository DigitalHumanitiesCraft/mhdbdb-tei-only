---
name: projekt-tei-all-baseline
description: Wo die tei_all-Baselinezahl (validate-corpus.py) ueberall steht und warum ein Englisch-Grep und --corpus-only sie nicht vollstaendig pruefen
metadata:
  type: project
---

Die Zahl der tei_all-Baseline (`KNOWN_TEI_ALL_BASELINE` in `scripts/audit/validate-corpus.py`) steht auch in deutscher Prosa: `schema/README.md` (Stufe-1-Absatz, dort auch "Ein N+1. Fail wuerde als WARN") und `hilfe-daten-beitragen.html` ("Baseline von N toleranten GAP-Files"), neben TEI-MODEL.md §10 und DECISIONS.md. Ein Grep nach englischen Mustern ("34 corpus files", "baseline of 34") verfehlt beide; am 18.10.2026 (Zweig claude/zedolne-reason, 34 auf 35) blieben sie so stehen.

**Why:** jede Datei mit ihrem ersten `@reason` auf `<w>` waechst die Baseline um eins (POS-TAGSET.md, Absatz nach der Fusionstabelle); das passiert bei jeder Fusionsentscheidung wieder.

**How to apply:** bei jeder Baseline-Aenderung `git grep -n -E "\b<alt>\b" -- '*.md' '*.html' schema/` und nach Kontext filtern, nicht nach Phrase. Dazu: `validate-corpus.py --corpus-only` (und `--sample`) ueberspringt den NEW/GONE-Namensabgleich (Zeilen um 251-270); nur der Lauf ohne Filter belegt, dass die Menge stimmt, nicht nur die Zahl (~140 s lokal mit 8 Workern).
