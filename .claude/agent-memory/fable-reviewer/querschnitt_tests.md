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
- `testing/test-results/report.json` wird von jedem Einzellauf überschrieben und fehlt, solange `npm test` läuft. **Auch `npx playwright test --list -c testing/playwright.config.js` überschreibt sie** (`expected 0, skipped N`). Vor jedem `--list` oder Einzellauf `stats` des Aufrufers in eine Scratch-Datei kopieren. `node scripts/run-tests.js --list` zählt ohne Server; ein statisches `grep` auf `test(` liegt darunter.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei); welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. Bedient ein fremder Baum :8080, endet run-tests.js mit `KEIN ERGEBNIS`; Abhilfe `MHDBDB_TEST_PORT=<port>`. `netstat` heißt unter deutscher Konsole ABHÖREN statt LISTEN.
- **Flaky ist rot, auch bei grünem Retry:** `testing/playwright.config.js` setzt `retries: 1` und `failOnFlakyTests: true`, `run-tests.js` zählt `stats.flaky` in die ROT-Gründe. Ein TEILLAUF GRUEN ersetzt den Volllauf nicht; „npm test grün" heißt VOLLLAUF GRUEN.
- **report.json: `config.workers` ist das konfigurierte Maximum (6 lokal, 2 mit `--workers=2`), die tatsächliche Zahl steht in `config.metadata.actualWorkers`** = min(workers, Testgruppen), Playwright 1.55.1 `runner/tasks.js:317`; bei `fullyParallel: false` ist eine Testgruppe etwa eine Datei, ein Einzelspec-Lauf hat also 1 Worker. Playwrights Konsole („using N workers") nimmt actualWorkers (#564 D2, 10.10.2026).
- Bei Specs mit Nicht-ASCII-Zeichen stimmen Zeilennummern der Laufausgabe nicht; Zeilen aus `rg -n`.
- **Einzelspec auf einer Kopie, ohne den Worktree zu berühren:** `git archive HEAD -- assets data korpus.html index.html includes package.json package-lock.json scripts testing authority-files 404.html | tar -x -C <kopie>` (reicht für reading-view), nur die gebrauchten TEI-Dateien per `git show <rev>:tei/X.tei.xml`; node_modules per `cmd //c mklink //J <kopie>\node_modules <wt>\node_modules`, danach `cmd //c rmdir` auf die Junction (löscht nur den Link). Dann `MHDBDB_TEST_PORT=8097 node scripts/run-tests.js <spec> [--grep <Titelwort>]` aus der Kopie. Mutationen mit cp/cmp-Restaurierung je Lauf; parallele Specs: je ein Port, Mutationen an verschiedenen TEI-Dateien.

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`. Echter Klick statt `dispatchEvent('mousedown')`: Specs umgehen mouseup/click.
- Bei belegtem 8080: die `.mjs` startet selbst `spawn(process.execPath, [<wt>/node_modules/http-server/bin/http-server, <wt>, '-p','8097','-s'])`, pollt per `fetch` bis 200, `server.kill()` im `finally`; berührt weder `run-tests.js` noch `report.json`. Ausgabe in eine Datei umleiten, `| tail` frisst die ersten Datensätze.
- Nach `page.fill('#ldQuery', …)` fängt das Autocomplete-Dropdown den `page.click('#ldSearchBtn')` ab; Knopf per `page.evaluate(b => document.getElementById(b).click(), …)` auslösen. `node --check` nimmt ESM; kein JS-Parser in node_modules.

**Locator-Fallen**
- ID-Grep reicht nicht: Textlocator (`button:has-text("...")`) mitsuchen und VOR dem Befund auf der Basis gegen das HTML greppen (kann dort schon tot sein).
- Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt grün und tut nichts.

**Tailwind**
- `assets/css/tailwind-output.css` ist committet, kein Gate, kein Workflow baut CSS. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify` (0,6 s), `cmp`.
- **Klasse im minifizierten CSS nur mit Lookahead `[\s{,:.\[>]` oder mit Kontextausgabe zählen; `rg -c` auf der Ein-Zeilen-Datei liefert nur 0 oder 1.** Eine Regex `\.klasse\{` verfehlt gruppierte Selektoren `.a,.b{` (#228, Falschbefund zu `.flex-shrink-0`). Nur die Mengendifferenz trägt.

**Warmer Worker-Context (#488, `testing/warm-page.js`, gemessen an Playwright 1.55.1, bei Update neu prüfen)**
- Auto-Fixtures laufen vor den vom Test genannten; `_setupContextOptions` setzt die gemergten `use`-Optionen und `_defaultContextTimeout = actionTimeout || 0`, bevor eine Worker-Fixture `browser.newContext()` ruft: der Worker-Context erbt `use` und Timeout 0 ohne eigenes Merging.
- Probe ohne Server: Scratchpad-Config importiert die echte per `file:///`, löscht `webServer`, setzt testDir/outputDir/retries 0; Specs als `*.spec.mjs` importieren `test` aus `warm-page.js`. Timeout: `page.context()._timeoutSettings._defaultTimeout`. Nach einem Fehlschlag läuft der Retry kalt.
- Der Teardown-`localStorage.clear()` deckt `mhdbdb-results-view` (app.js) und `mhdbdb-playground-section-<panel>` (playground-main.js); kein Service Worker. Neue Opt-in-Specs auf Storage-Asserts, `page.route` und `context`-Fixture greppen (`grep -rl warm-page testing/tests`).
- Zwei Volläufe gleicher Testzahl streuen um ~30 s: ein Einzellaufpaar belegt keinen Gewinn darunter.
