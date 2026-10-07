---
name: querschnitt-tests
description: Tests im Review: Einzelspec via run-tests.js, --reporter-Falle, report.json, Port-Konflikt, Proben ohne Spec, Locator-Fallen, Tailwind (mit widerlegtem Falschbefund)
metadata:
  type: project
---
Verdichtet 02.10.2026.

**Läufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet Server selbst, VERDICT TEILLAUF), `npm test -- <spec...>` oder `-- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js`. Die VERDICT-Zeile ist das Ergebnis; im Hintergrund mit Redirect in eine Scratch-Datei.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles grün.
- `testing/test-results/report.json` wird von jedem Einzellauf überschrieben und fehlt, solange `npm test` läuft: Volllaufzahl des Aufrufers (`stats.expected/unexpected`) vorher lesen.
- `node scripts/run-tests.js --list` zählt ohne Server; ein statisches `grep` auf `test(` liegt darunter (Schleifen, generierte Tests).
- **Auch `npx playwright test --list -c testing/playwright.config.js` überschreibt `report.json`** (JSON-Reporter läuft im Listenmodus mit: `expected 0, skipped N`). Am 06.10.2026 so den Volllauf-Beleg des Aufrufers (435/350,5 s) vernichtet, obwohl die Zeile darüber das Lesen vorher verlangt. Vor jedem `--list` oder Einzellauf: `stats` des vorhandenen `report.json` in die Scratch-Datei kopieren.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei). Welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. run-tests.js bricht ab (`KEIN ERGEBNIS`, Exit 2), wenn :8080 ein fremder Baum bedient. Abhilfe `MHDBDB_TEST_PORT=<port> npm.cmd test -- <spec>`: am 02.10.2026 war 8081 ebenfalls fremd belegt, 8097 lief (TEILLAUF GRÜN, 10 Tests 30 s). `netstat -ano | grep LISTEN` findet unter deutscher Konsole nichts (dort ABHÖREN).
- Specs liegen in `testing/tests/`; ein Glob `testing/*.spec.js` läuft still leer.
- **Flaky ist rot, auch bei grünem Retry:** `testing/playwright.config.js` setzt `retries: 1` und `failOnFlakyTests: true`, `scripts/run-tests.js` zählt `stats.flaky` in die ROT-Gründe („Retry zur Diagnose, nicht zum Durchwinken"). Ein TEILLAUF GRUEN der betroffenen Spec danach ersetzt den Volllauf nicht; „npm test grün" heißt VOLLLAUF GRUEN (gemessen 07.10.2026, Frage des Aufrufers in #526 Runde 2).
- Anderer Port ohne Config-Änderung: `MHDBDB_TEST_PORT=8084 node scripts/run-tests.js <spec>`.
- Playwright-Zeilennummern in der Laufausgabe stimmen bei Specs mit Nicht-ASCII-Zeichen nicht mit dem Quelltext überein (B2, 02.10.2026); Zeilen für einen Befund aus `rg -n`.

- **Einzelspec auf einer Kopie, ohne den Worktree zu berühren (Cloud, 04.10.2026):** `git archive <rev> -- $(git ls-tree --name-only <rev> | grep -v '^tei$') | tar -x -C <kopie>`, dazu `git show <rev>:tei/PZ.tei.xml > <kopie>/tei/PZ.tei.xml` (321 MB statt 1,7 GB), `ln -s <worktree>/node_modules <kopie>/node_modules`, dann `MHDBDB_TEST_PORT=8097 node scripts/run-tests.js <spec> [--grep <Titelwort>]` aus der Kopie. Browser liegen in `$PLAYWRIGHT_BROWSERS_PATH` (/opt/pw-browsers), nicht in `~/.cache`. `report.json` des Aufrufers bleibt unangetastet; Mutationsproben mit cp/cmp-Restaurierung je Lauf (dreissiger-buecher.spec.js: 33 s, mit PZ-Rendern bis 76 s).

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`; ca. 1 min. Echter Klick statt `dispatchEvent('mousedown')`: Specs umgehen mouseup/click.
- ESM-Helfer per `file://`-Import gegen eine wörtliche Altkopie vergleichen; `node --check` nimmt ESM; kein JS-Parser in node_modules.

**Locator-Fallen**
- ID-Grep reicht nicht: Textlocator (`button:has-text("...")`) mitsuchen und VOR dem Befund auf der Basis gegen das HTML greppen (kann dort schon tot sein).
- Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt grün und tut nichts.
- Specs können datengebunden sein (Prüfseiten): neuer Datenstand bricht sie ohne Vorlagenänderung.
- `check-doc-inventories.py` hält `testing/tests/*.spec.js` gegen die Spec-Tabelle in DEVELOPMENT.md: neue Spec ohne Zeile ist ein echter Befund.

**Tailwind**
- `assets/css/tailwind-output.css` ist committet, kein Gate, kein Workflow baut CSS. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify` (0,6 s), `cmp`.
- **Klasse im minifizierten CSS nur mit Lookahead `[\s{,:.\[>]` oder mit Kontextausgabe zählen; `rg -c` auf der Ein-Zeilen-Datei liefert nur 0 oder 1.** Absolute Selektorzahlen sind zählweisenabhängig, nur die Mengendifferenz trägt.
- **Widerlegter Falschbefund (#228):** `.flex-shrink-0` steht als gruppierter Selektor `.flex-shrink-0,.shrink-0{...}`; die Regex `\.flex-shrink-0\{` verfehlt jede Gruppe `.a,.b{` (siehe querschnitt_review_fallen).
- **Zwei Specs parallel auf EINER Kopie:** je ein Port (8097/8098), je ein Aufruf von `run-tests.js` im eigenen Bash-Call; Mutationen an verschiedenen TEI-Dateien gleichzeitig anlegen, wenn jede Spec nur ihre liest (04.10.2026, dreissiger 38 s, WH-Einzeltest 16 s). Die Kopfzeile des Fehlers nennt bei Specs mit Umlauten einen falschen Testtitel; die `> NNN |`-Zeile des Asserts stimmt.
