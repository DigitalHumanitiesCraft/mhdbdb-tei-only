---
name: projekt-warm-context-488
description: Warmer Worker-Context (#488, testing/warm-page.js): was ein browser.newContext() in einer Worker-Fixture erbt, Probe-Rezept ohne Server, Retry/Teardown-Verhalten, App-Storage, Laufzeitskalen
metadata:
  type: project
---
Gemessen an Playwright 1.55.1; bei einem Update neu prüfen.

**Optionen und Timeout:** Auto-Fixtures laufen vor den vom Test genannten; `_setupContextOptions` setzt die gemergten `use`-Optionen und `_defaultContextTimeout = actionTimeout || 0`, bevor eine Worker-Fixture `browser.newContext()` ruft. Ein Worker-Context erbt also `use` und Timeout 0 auch ohne eigenes Merging. `workerInfo.project.use` ist die gemergte Sicht.

**Probe ohne Server (ca. 40 s):** Scratchpad-Config importiert die echte per `file:///…/testing/playwright.config.js`, löscht `webServer`, setzt testDir/outputDir/retries 0; Specs als `*.spec.mjs` importieren `test` aus `warm-page.js` bzw. `@playwright/test/index.mjs` (gleiche Modulinstanz). Aufruf mit eigenem `MHDBDB_TEST_PORT`. Timeout direkt lesen: `page.context()._timeoutSettings._defaultTimeout`.

**Retry und Teardown:** nach einem Fehlschlag stoppt der Dispatcher den Worker, der Retry läuft kalt. Nach Test-Timeout bekommt der Fixture-Teardown einen eigenen Slot. Dialoge ohne Listener werden auto-dismissed.

**App-Storage, den der Teardown-`localStorage.clear()` abdeckt:** `mhdbdb-results-view` (app.js), `mhdbdb-playground-section-<panel>` (playground-main.js), matomo-optout nur gelesen (lemma/index.html). `deleteDatabase('MHDBDB_Playground')` ist Altlast-Löschung (#314). Kein Service Worker. Neue Opt-in-Specs auf Storage-Asserts, `page.route` und `context`-Fixture greppen (`grep -rl warm-page testing/tests`, ohne `-r` scheitert es).

**Laufzeitskalen:** die `stats:`-Sekunden aus `run-tests.js` (`report.json` `stats.duration`) enthalten den Serverstart und liegen ~2 s unter der Wanduhr um `npm test`. Zwei Volläufe gleicher Testzahl streuen um ~30 s: ein Einzellaufpaar belegt keinen Gewinn darunter.
