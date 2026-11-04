---
name: querschnitt-tests
description: Tests im Review: Einzelspec über run-tests.js, report.json und Reporter-Falle, Port-Konflikt, Specs auf einer Kopie, Proben ohne Spec, CSS-Zustände, Locator- und Warte-Fallen, Tailwind
metadata:
  type: project
---
Verdichtet 03.11.2026.

**Läufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet den Server, VERDICT TEILLAUF) oder `npm test -- <spec...>`, `-- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js`. Ergebnis ist die VERDICT-Zeile. Flaky ist rot (`failOnFlakyTests: true`), TEILLAUF GRUEN ersetzt den Volllauf nicht.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles grün.
- `testing/test-results/report.json` überschreibt jeder Einzellauf, auch `npx playwright test --list -c testing/playwright.config.js`: vorher `stats` des Aufrufers sichern. `node scripts/run-tests.js --list` zählt ohne Server. Tatsächliche Worker in `config.metadata.actualWorkers`.
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei). Welcher Baum? Seite holen und einen String aus dem Diff greppen. Fremder Baum auf :8080 gibt `KEIN ERGEBNIS`: `MHDBDB_TEST_PORT=<port>`.
- **Spec auf einer Kopie:** `git archive HEAD -- assets data korpus.html index.html includes package.json package-lock.json scripts testing authority-files 404.html | tar -x -C <kopie>`, nötige TEI per `git show`, node_modules per `cmd //c mklink //J` (danach `cmd //c rmdir`), eigener Port je Spec.
- „Kein Test deckt Seite X ab" belegt ein Grep nach dem Seitennamen nicht: `vendor.spec.js` (`htmlFiles`) läuft über jede `.html` außer `tei/`, `data/`, `.claude/` u. a. Gegenprobe `rg -n readdirSync testing/tests`.

**Proben ohne Spec**
- `.mjs` in Temp, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), `page.evaluate` auf `window.playground.ui.<tool>.state`, echter Klick statt `dispatchEvent`. Bei belegtem 8080 eigenen `http-server` starten, `server.kill()` im `finally`. Ausgabe in eine Datei.
- Mutation ohne Baum: `page.route('**/<pfad>.js', ...)` mit `r.fetch()` und `r.fulfill({ response, body })`, Body per String-Ersatz, Trefferzahl je Ersatz ausgeben (mehrzeilige Anker verfehlen still).
- **CSS-Zustände je Revision:** `git show <rev>:<css>`, `page.setContent`, Hover/Active per CDP `CSS.forcePseudoState`, dann `getComputedStyle`. `(pointer: coarse)` matcht unter `hasTouch: true` nur bis zum ersten `cdp.detach()`: je Revision ein frischer Kontext, `matchMedia` mit ausgeben. `forcePseudoState` wirkt nur auf den einen Knoten (`:has(.kopf:hover)` am Kind und an der Karte getrennt erzwingen).
- Reader-Spec ohne Browser: `#readingBody.textContent` aus dem TEI nachbauen, `\p{L}` -> `[^\W\d_]`. Auf Basis UND HEAD fahren: nur wenn die Negativ-Regex auf der Basis greift, trennt der Test.

**Locator- und Warte-Fallen**
- ID-Grep reicht nicht, Textlocatoren (`button:has-text("...")`) mitsuchen und auf der Basis gegen das HTML greppen. Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: grün, tut nichts. String-`hasText` ist Teilstring, nur `/^…$/` trennt.
- Ein Test „Textwechsel setzt X zurück" mit `page.goto` prüft nichts: neues Dokument, jeder JS-Zustand ist ohnehin weg. In-App-Wechsel im Reader: `window._mhdbdbApp.teiReader.openReadingView(id, {}, window._mhdbdbApp.elements)` oder ein `.sigle-link` (#655). Die `.sigle-link` stehen im eingeklappten `#readingMetadata`, nicht in `.reading-header` (korpus.html).
- `waitForLoadState('networkidle')` nach dem ersten networkidle ist ein No-op. Feste `waitForTimeout` sind bei Großtexten (`minne`) als Negativprobe nicht trennscharf. `beforeAll`/`afterAll` fehlen in `result.duration`. `url().includes('/tei/')` trifft auch `playground/js/ui/tei/*.js`.

**Tailwind:** `tailwind-output.css` ist committet, kein Gate baut sie. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o <temp>/x.css --minify`, `cmp`. Klassen im minifizierten CSS mit `grep -o '[.,]klasse[,{]' ... | wc -l` zählen, nicht `rg -c` (eine Zeile) oder `\.klasse\{` (verfehlt Gruppen).
