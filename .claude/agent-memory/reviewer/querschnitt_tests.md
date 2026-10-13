---
name: querschnitt-tests
description: Tests im Review: Einzelspec via run-tests.js, --reporter-Falle, report.json, Port-Konflikt, Proben ohne Spec, Locator-Fallen, Tailwind, warmer Worker-Context (#488)
metadata:
  type: project
---
**Läufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet Server selbst, VERDICT TEILLAUF), `npm test -- <spec...>` oder `-- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js`. Ergebnis ist die VERDICT-Zeile.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles grün.
- `testing/test-results/report.json` wird von jedem Einzellauf überschrieben und fehlt, solange `npm test` läuft. **Auch `npx playwright test --list -c testing/playwright.config.js` überschreibt sie** (`expected 0, skipped N`). Vor jedem `--list` oder Einzellauf `stats` des Aufrufers in eine Scratch-Datei kopieren; `node scripts/run-tests.js --list` zählt ohne Server.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei); welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. Bedient ein fremder Baum :8080, endet run-tests.js mit `KEIN ERGEBNIS`; Abhilfe `MHDBDB_TEST_PORT=<port>`.
- **Flaky ist rot, auch bei grünem Retry** (`failOnFlakyTests: true`). Ein TEILLAUF GRUEN ersetzt den Volllauf nicht; „npm test grün“ heißt VOLLLAUF GRUEN.
- **report.json: `config.workers` ist das Maximum, die tatsächliche Zahl steht in `config.metadata.actualWorkers`** (min aus workers und Testgruppen; Einzelspec-Lauf: 1).
- **Einzelspec auf einer Kopie, ohne den Worktree zu berühren:** `git archive HEAD -- assets data korpus.html index.html includes package.json package-lock.json scripts testing authority-files 404.html | tar -x -C <kopie>`, nur die gebrauchten TEI-Dateien per `git show <rev>:tei/X.tei.xml`; node_modules per `cmd //c mklink //J` (danach `cmd //c rmdir` auf die Junction). Dann `MHDBDB_TEST_PORT=8097 node scripts/run-tests.js <spec>`; parallele Specs: je ein Port.
- **Basis gegen Fix, zwei Stände:** je Stand nur die geänderte Seite per `git archive <rev> korpus.html` über gemeinsame `assets data includes`, `tei` und `node_modules` per `ln -sfn` aus dem Klon; je Stand ein `http-server -p 8097/8098 -c-1 -s`. Einzeltests: `MHDBDB_TEST_PORT=<port> node <klon>/node_modules/.bin/playwright test -c testing/playwright.config.js <spec> -g "<titel>" --workers=1 --retries=0` aus der Kopie. Auf dem roten Stand wartet ein abgefangener Klick bis zum Test-Timeout (180 s je Test). **Nach einem roten Lauf kehrt `npx playwright test` nicht zurück:** der HTML-Reporter (`open: on-failure`) wartet; `report.json` ist längst geschrieben. Vorab `PLAYWRIGHT_HTML_OPEN=never` setzen oder aus `report.json` lesen und den Prozess beenden.

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`. Echter Klick statt `dispatchEvent`. Bei belegtem 8080 startet die `.mjs` selbst `http-server` auf 8097 (`spawn(process.execPath, [<wt>/node_modules/http-server/bin/http-server, <wt>, '-p','8097','-s'])`), pollt bis 200, `server.kill()` im `finally`. Ausgabe in eine Datei, `| tail` frisst die ersten Datensätze.
- Reader-Spec ohne Browser (Playwright gesperrt, #390): `#readingBody.textContent` aus dem TEI nachbauen (Vorlage `tei-text-reader.js`), die Spec-Regexes mit `\p{L}` -> `[^\W\d_]` in Python `re`. Auf Basis UND HEAD fahren: nur wenn die Negativ-Regex auf der Basis greift, unterscheidet der Test etwas.
- Nach `page.fill('#ldQuery', …)` fängt das Autocomplete-Dropdown den `page.click('#ldSearchBtn')` ab; Knopf per `page.evaluate(b => document.getElementById(b).click(), …)` auslösen.

**Locator-Fallen**
- ID-Grep reicht nicht: Textlocator (`button:has-text("...")`) mitsuchen und auf der Basis gegen das HTML greppen (kann dort schon tot sein).
- Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt grün und tut nichts.

**Tailwind**
- `tailwind-output.css` ist committet, kein Gate, kein Workflow baut CSS. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify`, `cmp`.
- **Klasse im minifizierten CSS nicht mit `rg -c` zählen (Ein-Zeilen-Datei: nur 0 oder 1) und nicht mit `\.klasse\{`:** das verfehlt gruppierte Selektoren `.a,.b{` (#228, wiederholt am 13.10.: `.flex-shrink-0,.shrink-0{flex-shrink:0}`, Tailwind 3.4.19 erzeugt beide Namen). Tragfähig: `grep -o '[.,]klasse[,{]' assets/css/tailwind-output.css | wc -l`; Mengendifferenz: `grep -o "}[^{}]*{" x.css | sed 's/^}//;s/{$//' | tr ',' '\n' | sort -u` je Datei, dann `comm`. Nur die Mengendifferenz trägt.

**Warmer Worker-Context (#488, `testing/warm-page.js`, Playwright 1.55.1, bei Update neu prüfen)**
- Der Worker-Context erbt `use` und Timeout 0 (`actionTimeout || 0`) ohne eigenes Merging; nach einem Fehlschlag läuft der Retry kalt. Der Teardown-`localStorage.clear()` deckt `mhdbdb-results-view` und `mhdbdb-playground-section-<panel>`; kein Service Worker. Neue Opt-in-Specs auf Storage-Asserts, `page.route` und `context`-Fixture greppen (`grep -rl warm-page testing/tests`).
- Zwei Volläufe streuen um ~30 s: ein Einzellaufpaar belegt keinen Gewinn darunter.

**Warte-Fallen (Playwright 1.55.1, #564 D3)**
- `page.waitForLoadState('networkidle')` nach dem ersten networkidle der Seite ist ein No-op; als Ersatz für eine feste Frist nach einem Klick taugt es nicht.
- `beforeAll`/`afterAll` laufen mit `project.timeout`, nicht mit dem `test.setTimeout` des describe; ihre Zeit fehlt in `result.duration` und damit in der Dauertabelle von run-tests.js.
- Request-Zähler mit `url().includes('/tei/')` trifft auch `playground/js/ui/tei/*.js`. Dauer je Spec aus `results[].duration` des Aufrufers selbst nachsummieren.
- **Korpusladen blockiert den Hauptthread einmal am Stück:** kalter Context ~10 bis 12 s (`pako.ungzip`, `JSON.parse`, IndexedDB-`put`), warmer ~3 s (nur IDB-Lesen; `loadCorpusIndex` gibt bei Cache-Treffer `cachedIndex` zurück). `#fileBrowserSection` (startet display:none, kein Toggle) wird im selben synchronen Block sichtbar (playground-main.js 276 bis 288); jede 5-s-Frist nach einer Aktion ohne vorheriges Warten darauf kann in den Block fallen. Der Log „locator resolved to visible“ vor einem Timeout heißt „Roundtrips im Block hängen geblieben“, nicht „Element unsichtbar“. **Die Longtask-API meldet den Block nicht**; messen mit rAF-Lücken (>100 ms) plus Wrapper um `JSON.parse`/`window.pako.ungzip`/`window.playground.populateFileBrowser`.