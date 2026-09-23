---
name: nacht-a1-252-267
description: Review des zweiten #252-Durchgangs (846 Inline-Lücken) zusammen mit #267 no-print, Nachtlauf 23.09.2026, Commit 8be73c141
metadata:
  type: project
---

Ergänzt [[project_caesura_gap_252]] (erster Durchgang, 10.09.2026). Eigene Datei, weil der Nachtlauf je Spur eine eigene Memory-Datei verlangt.

- Zielmenge 846 in 20 Dateien nach der K11-Regel (Geschwister-pc `(`/`)`, Block mit `<w>` in beliebiger Tiefe), Skript `scripts/ingest/gap-252/migrate-inline-gap.py`. Danach gap 1.940/114 (1.935 in l, 5 in p; 841 in l MIT w), caesura **51.140/218**, Rohmuster-Rest genau 3 (NEIC_6303140_2, NEIR_1205060_1, SJH_4101130_1 = Zeile "Marker plus ein Zeichen").
- **TEI-MODEL.md:263 ist die zweite Kopie der caesura-Zahl und blieb zum zweiten Mal stehen** (Runde 2 am 10.09. dieselbe Falle bei :261). Wer §6.5 aendert, grept `in \d+ files, see 6.5`.
- Header nach #267: `status="restricted"` = `n="no-print"` = 9 Dateien; Standard-availability einzeilig 651 (650 + FR3), 6 umbrochen (DUE ER OVG SAL WGA WVO), WZB eigener Block. `excerpt-only` steht danach nur noch in den `<change>`-Eintraegen der neun.
- Kein Konsument: `n="excerpt-only"`, `status="restricted"`, `@media print` in assets/, playground/, testing/ = 0 Treffer; `@media print` nur in Pruefseiten (examples/review-pages, scripts/audit/*.template.html, scripts/review/review_page.py, ingest/review). build-corpus-index liest nur w/l (iterwalk :192) und Header-XPaths idno/title/author/msIdentifier/keywords, darum kein Rebuild-Diff und kein Bump.
- Diff-Klassifikation in einem Rutsch: `git diff base...HEAD -- tei/ | grep '^+' | sed 's/xml:id="[^"]*"//g; s/when="[^"]*"//g' | sort | uniq -c` zeigt jede eingefuegte Zeilenart mit Anzahl; CR-Zaehlung im Diff ueber `--output=<datei>` und Python, weil der Worktree-Guard `| grep -c $'\r'` und `$(...)` ablehnt.
- sources/linecode-manifest.csv: 306 Zeilen, 199 Sigeln, Spalte `sigle`; MAI und NEI fehlen dort, FR3 = erledigt/fr3.txt.
