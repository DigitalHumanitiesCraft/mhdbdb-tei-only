---
name: querschnitt-tests
description: Tests im Review: Einzelspec via run-tests.js, --reporter-Falle, report.json, Port-Konflikt, Proben ohne Spec, Locator-Fallen, Tailwind, warmer Worker-Context (#488), Warte-Fallen
metadata:
  type: project
---
Verdichtet 18.10.2026.

**Läufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet Server selbst, VERDICT TEILLAUF), `npm test -- <spec...>` oder `-- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js`. Ergebnis ist die VERDICT-Zeile.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles grün.
- `testing/test-results/report.json` wird von jedem Einzellauf überschrieben und fehlt, solange `npm test` läuft; **auch `npx playwright test --list -c testing/playwright.config.js` überschreibt sie.** Vorher `stats` des Aufrufers in eine Scratch-Datei kopieren; `node scripts/run-tests.js --list` zählt ohne Server. `config.workers` ist das Maximum, die tatsächliche Zahl steht in `config.metadata.actualWorkers`.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei); welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. Bedient ein fremder Baum :8080, endet run-tests.js mit `KEIN ERGEBNIS`; Abhilfe `MHDBDB_TEST_PORT=<port>`.
- **Flaky ist rot, auch bei grünem Retry** (`failOnFlakyTests: true`). Ein TEILLAUF GRUEN ersetzt den Volllauf nicht.
- **Einzelspec auf einer Kopie, ohne den Worktree zu berühren:** `git archive HEAD -- assets data korpus.html index.html includes package.json package-lock.json scripts testing authority-files 404.html | tar -x -C <kopie>`, nur die gebrauchten TEI-Dateien per `git show <rev>:tei/X.tei.xml`; node_modules per `cmd //c mklink //J` (danach `cmd //c rmdir` auf die Junction). Dann `MHDBDB_TEST_PORT=8097 node scripts/run-tests.js <spec>`; parallele Specs: je ein Port.

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`. Echter Klick statt `dispatchEvent`. Bei belegtem 8080 startet die `.mjs` selbst `http-server` auf 8097, pollt bis 200, `server.kill()` im `finally`. Ausgabe in eine Datei, `| tail` frisst die ersten Datensätze.
- **Mutationsprobe ohne Baum anzufassen:** in der `.mjs` `page.route('**/<pfad>.js', async r => { const resp = await r.fetch(); ... r.fulfill({ response: resp, body }) })` und den Body per String-Ersatz mutieren; Trefferzahl je Ersatz mitausgeben (ein mehrzeiliger Anker verfehlte am 18.10. still, einzeiliger Anker nehmen). Ersetzt die Rücknahme per git, wenn der Aufrufer „still halten" verlangt.
- Reader-Spec ohne Browser (#390): `#readingBody.textContent` aus dem TEI nachbauen (Vorlage `tei-text-reader.js`), die Spec-Regexes mit `\p{L}` -> `[^\W\d_]` in Python `re`. Auf Basis UND HEAD fahren: nur wenn die Negativ-Regex auf der Basis greift, unterscheidet der Test etwas.

**Locator-Fallen:** ID-Grep reicht nicht, Textlocator (`button:has-text("...")`) mitsuchen und auf der Basis gegen das HTML greppen (kann dort schon tot sein). Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt grün und tut nichts.

**Tailwind**
- `tailwind-output.css` ist committet, kein Gate, kein Workflow baut CSS. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify`, `cmp`.
- **Klasse im minifizierten CSS nicht mit `rg -c` (Ein-Zeilen-Datei) und nicht mit `\.klasse\{` zählen** (verfehlt gruppierte Selektoren). Tragfähig: `grep -o '[.,]klasse[,{]' assets/css/tailwind-output.css | wc -l`; Mengendifferenz: `grep -o "}[^{}]*{" x.css | sed 's/^}//;s/{$//' | tr ',' '\n' | sort -u` je Datei, dann `comm`.


**Warte-Fallen (Playwright 1.55.1, #564 D3)**
- `page.waitForLoadState('networkidle')` nach dem ersten networkidle der Seite ist ein No-op und ersetzt keine feste Frist nach einem Klick.
- `beforeAll`/`afterAll` laufen mit `project.timeout`; ihre Zeit fehlt in `result.duration` und der Dauertabelle von run-tests.js. Request-Zähler mit `url().includes('/tei/')` trifft auch `playground/js/ui/tei/*.js`.
