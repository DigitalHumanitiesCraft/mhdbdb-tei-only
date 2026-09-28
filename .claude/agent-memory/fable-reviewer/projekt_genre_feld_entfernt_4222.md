---
name: genre-feld-entfernt-4222
description: Review des Aufraeum-Commits nach dem Nachtlauf (Korpus-Index 4.2.22, genre-Feld weg, CSV-Quellenangabe #420): Leser-Historie per git log -S, In-Process-Rebuild-Fallen, Feldnamen der Fremdindizes
metadata:
  type: project
---

Korpus-Index 4.2.22 (Branch `claude/aufraeumen-nachtlauf`, Runde 1 am 28.09.2026) entfernt `text.genre`.

**Leser-Historie ist eine Zuschreibung und wird per `git log -S` gemessen, nicht aus dem Kommentar uebernommen.**
`git log --oneline -S"text.genre" -- assets/js playground/js` zeigt: der letzte Leser des Korpusfelds fiel mit #314
(3ba9ddf9e, 2026-08-01, Upload-Pfad des Playgrounds: `genre: text.genre || ''`). #433 (28a5bffda, 2026-09-23)
entfernte dagegen die Kette `getGenre(text.workRef)` -> `work.genre` im **Authority**-Index. Commit-Message und
build-corpus-index.py:137 schrieben "seit #433 kein Leser" und zeigten auf search-engine.js, das seit #433 gar keine
Gattung mehr aufloest; die Gattung je Werk laeuft ueber `work.genres` (tei-text-reader.js:306) und
`maps.genreToWorks` (app.js:322, genre-tree.js).

**Why:** Zwei Issues, zwei Felder gleichen Namens (`text.genre` im Korpus-Index, `work.genre` im Authority-Index);
wer "genre" greppt, sieht beide Ketten als eine.

**How to apply:** Bei jeder "seit #N kein Leser"-Behauptung den Feldpfad mit `-S"<objekt>.<feld>"` einzeln loggen
und das Datum des Treffers mit dem genannten Issue vergleichen.

Weitere Messpunkte dieser Runde:
- `term[@type="genre"]` in tei/: 0 von 667 Dateien (`git grep -c 'type="genre"' -- tei/ | wc -l`, Kontrollwert
  `type="sigle"` = 667). Der Header traegt Gattungen stattdessen als `classDecl/taxonomy/category/gloss`, das liest
  tei-text-reader.js:383 direkt aus dem TEI, nicht aus dem Index.
- check-index-versions.py gatet fuenf Dateien, aber nur vier tragen die Korpusversion (build-authority-index.py
  traegt nur die Authority-Version): "vier Stellen" beim Korpus-Bump ist richtig.
- In-Process-Rebuild von build-corpus-index.py per importlib bricht mit `BrokenProcessPool`, weil die Worker
  `process_tei_file` aus einem nicht importierbaren Modul nicht picklen koennen: `build_corpus_index(jobs=1)` nehmen
  und mehrere Minuten einplanen. Vergleich auf JSON-Ebene (`json.dumps(sort_keys=True)`), nie auf gz-Bytes.
- Fremdindizes schreiben die Lizenz verschieden: naming-index `source.license` + `citation` "(v0.3.0-beta)",
  horses-index `source.licence`. Code, der beide anfasst, muss beide Schreibweisen treffen.
- `testing/fixtures/sample-corpus-index.json` traegt `"genre": "test"` und hat 0 Konsumenten (`git grep
  sample-corpus-index` leer): tote Fixture, kein Gate haengt daran.
- Linda Beutel-Thurows Zustimmung zur Quellenangabe im Dateinamen steht in #420 am 2026-09-24T06:37Z
  (api.github.com/repos/.../issues/420/comments, 200 ohne Token).

Runde 2 (28.09.2026, Fix-Commit 89d04997a): alle drei Zeiger per `git -C <worktree> grep -n` bestaetigt
(work.genres tei-text-reader.js:306, maps.genreToWorks app.js:323 + genre-tree.js:20-27), Fixture 0x "genre",
JSON parst, 0 Konsumenten. Der Guard liess `git -C "<pfad mit Projekte-Git-mhdbdb>"` durch, obwohl aeltere Notizen
ein Verbot fuer "Git" im Pfad melden: der Bindestrich-Pfad im Scratchpad-Worktree ist offenbar nicht betroffen.
