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
- **Port 8080:** frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei). Welcher Baum? `curl .../<seite> | grep -c '<String aus dem Diff>'`. run-tests.js bricht ab (`KEIN ERGEBNIS`, Exit 2), wenn :8080 ein fremder Baum bedient. Abhilfe `MHDBDB_TEST_PORT=<port> npm.cmd test -- <spec>`: am 02.10.2026 war 8081 ebenfalls fremd belegt, 8097 lief (TEILLAUF GRÜN, 10 Tests 30 s). `netstat -ano | grep LISTEN` findet unter deutscher Konsole nichts (dort ABHÖREN).
- Specs liegen in `testing/tests/`; ein Glob `testing/*.spec.js` läuft still leer.
- Anderer Port ohne Config-Änderung: `MHDBDB_TEST_PORT=8084 node scripts/run-tests.js <spec>`.
- Playwright-Zeilennummern in der Laufausgabe stimmen bei Specs mit Nicht-ASCII-Zeichen nicht mit dem Quelltext überein (B2, 02.10.2026); Zeilen für einen Befund aus `rg -n`.

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
