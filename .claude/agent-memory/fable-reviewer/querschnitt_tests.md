---
name: querschnitt-tests
description: Tests im Review: Einzelspec via run-tests.js, --reporter-Falle, report.json, Port-Konflikt, Proben ohne Spec, Locator-Fallen, Tailwind, warmer Worker-Context (#488)
metadata:
  type: project
---
Verdichtet 08.10.2026.

**Läufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet Server selbst, VERDICT TEILLAUF), `npm test -- <spec...>` oder `-- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js`. Die VERDICT-Zeile ist das Ergebnis; im Hintergrund mit Redirect in eine Scratch-Datei.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles grün.
- `testing/test-results/report.json` wird von jedem Einzellauf überschrieben und fehlt, solange `npm test` läuft: Volllaufzahl des Aufrufers (`stats.expected/unexpected`) vorher lesen. **Auch `npx playwright test --list -c testing/playwright.config.js` überschreibt sie** (JSON-Reporter läuft im Listenmodus mit: `expected 0, skipped N`); so wurde einmal der Volllauf-Beleg des Aufrufers vernichtet. Vor jedem `--list` oder Einzellauf `stats` in eine Scratch-Datei kopieren. `node scripts/run-tests.js --list` zählt ohne Server; ein statisches `grep` auf `test(` liegt darunter.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei). Welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. run-tests.js bricht mit `KEIN ERGEBNIS`, Exit 2 ab, wenn :8080 ein fremder Baum bedient. Abhilfe `MHDBDB_TEST_PORT=<port> node scripts/run-tests.js <spec>`. `netstat -ano | grep LISTEN` findet unter deutscher Konsole nichts (dort ABHÖREN).
- **Flaky ist rot, auch bei grünem Retry:** `testing/playwright.config.js` setzt `retries: 1` und `failOnFlakyTests: true`, `run-tests.js` zählt `stats.flaky` in die ROT-Gründe. Ein TEILLAUF GRUEN ersetzt den Volllauf nicht; „npm test grün" heißt VOLLLAUF GRUEN.
- Bei Specs mit Nicht-ASCII-Zeichen stimmen Zeilennummern und Testtitel der Laufausgabe nicht; Zeilen aus `rg -n`, die `> NNN |`-Zeile des Asserts stimmt.
- **Einzelspec auf einer Kopie, ohne den Worktree zu berühren:** `git archive <rev> -- $(git ls-tree --name-only <rev> | grep -v '^tei$') | tar -x -C <kopie>`, dazu `git show <rev>:tei/PZ.tei.xml > <kopie>/tei/PZ.tei.xml` (321 MB statt 1,7 GB), `ln -s <worktree>/node_modules <kopie>/node_modules`, dann `MHDBDB_TEST_PORT=8097 node scripts/run-tests.js <spec> [--grep <Titelwort>]` aus der Kopie. Mutationsproben mit cp/cmp-Restaurierung je Lauf. Zwei Specs parallel auf EINER Kopie: je ein Port, je ein Aufruf in eigenem Bash-Call, Mutationen an verschiedenen TEI-Dateien.

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`; ca. 1 min. Echter Klick statt `dispatchEvent('mousedown')`: Specs umgehen mouseup/click.
- Bei belegtem 8080 (Volllauf des Aufrufers): die `.mjs` startet selbst `spawn(process.execPath, [<wt>/node_modules/http-server/bin/http-server, <wt>, '-p','8097','-s'])`, pollt per `fetch` bis 200, `server.kill()` im `finally`; berührt weder `run-tests.js` noch `report.json`. Sieben Werkzeuge mit Suche, Leeren, „Neu berechnen", Wiederanhaken: ca. 1,5 min. Ausgabe in eine Datei umleiten, `| tail` frisst die ersten Datensätze.
- ESM-Helfer per `file://`-Import gegen eine wörtliche Altkopie vergleichen; `node --check` nimmt ESM; kein JS-Parser in node_modules.

**Locator-Fallen**
- ID-Grep reicht nicht: Textlocator (`button:has-text("...")`) mitsuchen und VOR dem Befund auf der Basis gegen das HTML greppen (kann dort schon tot sein).
- Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt grün und tut nichts.

**Tailwind**
- `assets/css/tailwind-output.css` ist committet, kein Gate, kein Workflow baut CSS. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify` (0,6 s), `cmp`.
- **Klasse im minifizierten CSS nur mit Lookahead `[\s{,:.\[>]` oder mit Kontextausgabe zählen; `rg -c` auf der Ein-Zeilen-Datei liefert nur 0 oder 1.** Absolute Selektorzahlen sind zählweisenabhängig, nur die Mengendifferenz trägt.
- **Widerlegter Falschbefund (#228):** `.flex-shrink-0` steht als gruppierter Selektor `.flex-shrink-0,.shrink-0{...}`; die Regex `\.flex-shrink-0\{` verfehlt jede Gruppe `.a,.b{`.

**Warmer Worker-Context (#488, `testing/warm-page.js`, gemessen an Playwright 1.55.1, bei Update neu prüfen)**
- Auto-Fixtures laufen vor den vom Test genannten; `_setupContextOptions` setzt die gemergten `use`-Optionen und `_defaultContextTimeout = actionTimeout || 0`, bevor eine Worker-Fixture `browser.newContext()` ruft. Der Worker-Context erbt also `use` und Timeout 0 ohne eigenes Merging.
- Probe ohne Server (ca. 40 s): Scratchpad-Config importiert die echte per `file:///…/testing/playwright.config.js`, löscht `webServer`, setzt testDir/outputDir/retries 0; Specs als `*.spec.mjs` importieren `test` aus `warm-page.js`. Timeout direkt: `page.context()._timeoutSettings._defaultTimeout`. Nach einem Fehlschlag läuft der Retry kalt.
- Der Teardown-`localStorage.clear()` deckt `mhdbdb-results-view` (app.js) und `mhdbdb-playground-section-<panel>` (playground-main.js); kein Service Worker. Neue Opt-in-Specs auf Storage-Asserts, `page.route` und `context`-Fixture greppen (`grep -rl warm-page testing/tests`).
- Zwei Volläufe gleicher Testzahl streuen um ~30 s: ein Einzellaufpaar belegt keinen Gewinn darunter.
