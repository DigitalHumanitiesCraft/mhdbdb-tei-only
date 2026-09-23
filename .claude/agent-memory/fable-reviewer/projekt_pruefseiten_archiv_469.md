---
name: pruefseiten-archiv-469
description: Review-Lehren zu PR #469 (archivierte Pruefseiten, Generatoren build-review-364/klaus, Specs review-364/klaus): Testlauf im Worktree, --reporter-Falle, Generator-Laufzeit, eingebetteter Fremd-Commit
metadata:
  type: project
---

Gemessen am 23.09.2026, Runde 1 auf #469 (Worktree mhdbdb-wt-469, Basis 15e26bf9f).

- **Testlauf in einem Worktree ohne cd:** `npm.cmd --prefix <worktree> test -- review-364.spec.js review-klaus.spec.js` liefert `VERDICT: TEILLAUF GRUEN (7 Tests aus 2 Datei(en))`, Exit 0; node_modules dort ist eine Junction auf den Hauptbaum.
- **`--reporter=line` auf der Kommandozeile ersetzt die Reporter-Liste aus `testing/playwright.config.js:62-65`**, damit fehlt `report.json`, und `scripts/run-tests.js:203` hat den alten vorher geloescht: Ausgabe "7 passed", aber `VERDICT: KEIN ERGEBNIS`, Exit 2. Der Satz in `docs/INDEX.md` dazu ist gemessen wahr.
- **`build-review-364.py` braucht ueber 10 Minuten und 1,6 GB**: Regex-Scan ueber alle 667 TEI, dann lxml-Parse der Treffer (nach 10 min 21 Dateien). Nie im Vordergrund mit `| tail` starten (Ausgabe kommt erst am Ende); `--extract <scratchpad>/x.json > log 2>&1` als Hintergrundlauf. Beide Generatoren brechen per assert ab, wenn der Issue-Umfang nicht mehr 35/66/29 (364) bzw. 39/264/22 (Klaus) ist: "regenerate and replace the archived example" geht nur, solange die Issues nicht abgearbeitet sind.
- **Die archivierten Beispiele tragen `"commit": "6e36a659..."`, und dieser Commit existiert in diesem Repo nicht** (`git branch -a --contains` -> no such commit): KZWs lokaler Stand. Eine Regeneration embedded HEAD und heutiges Datum, die Tabellenspalte "Data snapshot" in INDEX.md (2026-09-17 / 2026-09-21) wandert mit.
- **Specs sind datengebunden**, nicht nur vorlagengebunden: 66 decisions, 6 Karten in lemma_79408, 24 nav-Buttons, 110 Optionen, "108 Belege uebernommen", Gruppe lemma_1164_sense_16760 mit 109; 286 Karten im Klaus-Bericht. Ein neuer Datenstand bricht sie auch ohne Vorlagenaenderung.
- **Bot-Review ohne WebFetch:** `gh pr view 469 --repo DigitalHumanitiesCraft/mhdbdb-tei-only --json comments` gibt den vollen Bot-Kommentar am Laptop. Ohne gh geht `curl api.github.com/repos/.../issues/469/comments` ohne Token (200, 23.09.2026); die Bot-Runden sind dort die `claude[bot]`-Eintraege.
- **Runde 4 (d0faf2581, theme-Feld):** `build-review-klaus.py:181-182` liest die 364-Vorlage nur fuer den `<style>`-Block (`re.search(r'<style>(.*?)</style>')`), Skriptaenderungen an der 364-Vorlage erreichen die Klaus-Seite nie. Vorlage gegen Archivbeispiel vergleichen: beide Dateien zeilenweise per difflib, nur die Zeile mit `id="review-data"` ausgeblendet; seit d0faf2581 weichen genau Z. 33 und Z. 72 ab, alles andere ist identisch. Der `state` der 364-Vorlage wird nur ueber `state.reviewer`, `state.answers`, `state=validate(...)`, `state=next` gelesen (grep `state\.[a-z]+`), ein entferntes Feld hat keinen Leser.

**Why:** Die Fragen des Aufrufers (Uebersetzungstreue, Tabellenzeilen, "regenerate"-Satz) haengen alle an diesen Messungen, und die Laufzeit des Generators haette die Runde beinahe gesprengt.
**How to apply:** Bei jeder Folgerunde auf #469 oder an den Pruefseiten zuerst die Generatoren im Hintergrund starten, dann lesen.
