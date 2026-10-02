---
name: querschnitt-tests
description: Tests im Review: Einzelspec via run-tests.js, --reporter-Falle, report.json, Proben ohne Server, Playwright-Laufzeitprobe, Locator-Fallen, Tailwind
metadata:
  type: project
---
Stand 28.09.2026.

**Laeufe**
- Einzelspec: `node scripts/run-tests.js <spec>` (startet Server selbst, VERDICT TEILLAUF), `npm test -- <spec...>` oder `npm test -- --grep "<titel>"`. Worktree ohne cd: `npm.cmd --prefix <worktree> test -- a.spec.js` (node_modules dort Junction). VERDICT-Zeile ist das Ergebnis; im Hintergrund mit Redirect in Scratch-Datei.
- `--reporter` auf der CLI ersetzt die Reporter der Config: kein report.json, `VERDICT: KEIN ERGEBNIS`, Exit 2, obwohl alles gruen.
- `testing/test-results/report.json` wird von jedem Einzellauf ueberschrieben und fehlt, solange `npm test` laeuft: Volllaufzahl des Aufrufers (`stats.expected/unexpected`) vorher lesen.
- `node scripts/run-tests.js --list` zaehlt ohne Server; statisches `grep -E '^\s*test(\.only|\.skip)?\('` liegt darunter (Schleifen, generierte Tests).
- Port frei? `curl -s -o /dev/null -w "%{http_code}" localhost:8080/...` (000 = frei). Welcher Baum auf :8080? `curl .../<seite> | grep -c '<String aus dem Diff>'`. run-tests.js bricht seit 02.10. (gemessen) selbst ab, wenn :8080 ein fremder Baum bedient (`VERDICT: KEIN ERGEBNIS`, Exit 2); Abhilfe `MHDBDB_TEST_PORT=8081 npm.cmd test --prefix <worktree> -- a.spec.js` (im Bash-Werkzeug mit Redirect in Scratch, lief 30 s fuer 10 Tests).
- run-tests.js bricht mit `VERDICT: KEIN ERGEBNIS (Port 8080 wird von einem fremden ... Server bedient (HTTP 404))` ab, wenn dort ein anderer Baum laeuft; am 02.10.2026 galt das auch fuer 8081. Ausweg ohne Nachfrage: `MHDBDB_TEST_PORT=8097 npm.cmd test -- <spec>` (lief, TEILLAUF GRUEN). `netstat -ano | grep LISTEN` findet unter deutscher Konsole nichts, das Wort heisst dort ABHÖREN.
- Config-Werte ohne Server: `import('./testing/playwright.config.js')` und `use.baseURL`/`webServer` drucken (bei Guard als `temp/*.mjs`).
- Specs liegen in `testing/tests/`; ein Glob `testing/*.spec.js` laeuft still leer.

**Proben ohne Spec**
- Playwright: `.mjs` in $TEMP, `import { chromium } from 'file:///C:/.../node_modules/playwright/index.mjs'` (ohne `file:///` ERR_UNSUPPORTED_ESM_URL_SCHEME), gegen :8080, `page.evaluate` auf `window.playground.ui.<tool>.state`, `show()` direkt rufen; ca. 1 min.
- Echter Klick statt `dispatchEvent('mousedown')`: Specs umgehen mouseup/click.
- ESM-Helfer per `file://`-Import gegen eine woertliche Altkopie ueber eine Probenliste vergleichen; `node --check` nimmt ESM. Kein JS-Parser in node_modules (acorn/espree/esprima fehlen).

**Locator-Fallen**
- ID-Grep reicht nicht: Textlocator (`button:has-text("...")`) mitsuchen, und VOR dem Befund auf der Basis gegen das HTML greppen (kann dort schon tot sein).
- Ein `isVisible()`-Guard wird nach Verstecken nie mehr wahr: Test bleibt gruen und tut nichts.
- Specs koennen datengebunden sein (Pruefseiten): neuer Datenstand bricht sie ohne Vorlagenaenderung.
- `check-doc-inventories.py` haelt `testing/tests/*.spec.js` gegen die Spec-Tabelle in DEVELOPMENT.md: neue Spec ohne Zeile ist ein echter Befund.

**Tailwind**
- `assets/css/tailwind-output.css` ist committet, kein Gate. Frische: `npx tailwindcss -i assets/css/tailwind-input.css -o $TEMP/x.css --minify` (0,6 s), `cmp`.
- Klassen zaehlen: `rg -F 'hover\:bg-brand-50'` oder Python-Regex mit Escape und Lookahead `[\s{,:.\[>]` (sonst trifft `.flex` `.flex-wrap`); `\\:` in Single Quotes ging leer aus. Absolute Selektorzahlen sind zaehlweisenabhaengig, nur die Mengendifferenz traegt.
