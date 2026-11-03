---
name: projekt-playground-frontend
description: Playground und Hauptseite im Review: Hash-Pfad bis innerHTML, Suche und Nummernpfad, Ergebniskarten, Reader, Werkzeugzustand nach Korpusauswahl, Lesepanel, Singular/Plural-Fundlisten, Footer und SEO-Region
metadata:
  type: project
---
Verdichtet 03.11.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Hash bis innerHTML:** router.js `parseHash` -> `handleMultiLemmaRoute` (IDs nur bei `/^\d+$/`) -> `MultiLemmaSearchUI.executeSearch` -> tei-ui.js `display*` -> ui-helpers.js `displaySummaryResults`/`displayHinweis`. `mode` per Whitelist, `dist` per parseInt, `q` nur in `input.value`. Roh gerendert: concept-explorer.js `searchTerm`, lemma-explorer.js `componentText`.

**Suche und Nummernpfad**
- `fetch` sitzt in ui-helpers.js (`enrichFileResults`), nicht in multi-lemma-search.js. „Bis zu 50 Fundstellen je Karte" = tei-ui.js `fileResults.slice(0, 50)`.
- Nummer als Eingabe: `assets/js/lib/lemma-id-input.js` `parseLemmaIdInput` für search-engine.js `resolveSearchTerm` und tei-ui.js `resolveLemmaIds`.
- **Ziffernlemmata:** Prüfbeispiel `1` (lemma_1 *a* gegen lemma_53328, auf das alle Ziffernschlüssel des Wörterbuchs zeigen). Jede Übergabe per Schreibform (`lemma-page.js` `korpus.html?search=`, Varianten-Chips, cooccurrence-ranking.js `lemmata=`) landet beim Nummern-Lemma, Übergaben per `ids=` sind gepinnt. Ebenso Linkmuster für eine externe KI (Begriffshilfe): die Spalte auf Leerzeichen, nachgestellte Leerzeichen und `1` prüfen, den Generator mit `--out <scratch>` fahren und per `cmp` halten.
- **ID-Eingabe in den Registern und der Begriffs-Verteilung** (`authority-id-input.js`): in den Registern ADDITIV vor den Texttreffern, in concept-distribution `resolveQuery` ERSETZEND. ID-Formen sind uneinheitlich (hex, `work_WZB`, UUIDs, `person_anonym`): vor einem Befund zählen.
- Gleicher-Hash-Falle: die Lemmaliste eines Begriffs (`showLemmasWithConcept`) rendert nur unter `#concepts` und `#names`. Der Begriffshilfe-Download (`build-begriffshilfe.py`, byte-gleich gegatet) beschreibt das Suchfeld des Begriffe-Explorers: den Satz gegen das Verhalten halten.
- Dokumentsuche: Karte `.result-summary-dokument`, Fundstellen lazy über `dokument-belege.js`, Links mit `position=<§B-Position>`, der Reader zählt in `processWord` gleich.

**Ergebniskarten (`setupSummaryExpansion`, ui-helpers.js)**
- Der Listener hängt an der ganzen `<article>`, umgeklappt wird nur bei Klick in `.summary-header, .summary-expand-hint`. Padding ist tote Zone, obwohl `cursor: pointer` und Hover-Lift an der ganzen Karte hängen. Spec-Klick `x: 10` liegt im Padding.
- Zeiger- und „nur"-Aussagen am gerenderten Zustand messen (Playwright, `setContent` plus echtes `style.css`): jede Fundstellenzeile ist ein `<a class="beleg-link">` mit UA-`pointer`.
- `role=button` auf `.summary-header` macht den ganzen Kopfinhalt zum Namen, ein Link darin ist verschachtelt interaktiv: per `ariaSnapshot()` messen, `getByRole('link')` bleibt grün.
- **Spezifität gegen die Touch-Ausnahme:** `@media (pointer: coarse)` nimmt Hover mit `.result-summary:hover` (0,2,0) zurück. Hover-Regeln mit `:not(.x)` oder `:has(...)` haben (0,3,0) und schlagen sie (`:where()` senkt). `box-shadow:none` im Hover löscht auch das `shadow-sm` der Ruhe.
- Der Hinweistext ist über `aria-labelledby` Teil des Knopfnamens: jeden Pfad prüfen, der ihn zurücksetzt. Der Guard `!fileResults[0].text` ist bei Nähe- und Vers-Ergebnissen immer wahr (`tei-manager.js` legt nie `text` an).
- `collapsible-text.js`: 600 Zeichen sind Vorauswahl, `enhanceCollapsibles` nimmt den Knopf zurück, wenn nichts verdeckt ist.
- **Scrollen auf Lemmaseite und Playground (03.11.2026, #554):** beide laden `shared.css`, beide haben den sticky `<header>` aus `_nav.html` (gemessen 72,5 px bei 1200, 1280 und 1920 Breite). Der Lemma-Explorer scrollt das Fenster, `#resultsContainer` ist `overflow-hidden` ohne Höhe und bleibt bei `scrollTop` 0. Messen per Playwright-Skript im Scratchpad gegen `node testing/serve.js` (Port per `MHDBDB_TEST_PORT`); Ausfallprobe ohne Dateiänderung: `Element.prototype.scrollIntoView` per `page.evaluate` stummschalten.

**Reader ohne `position`** springt nach 600 ms zum ersten Beleg: „öffnet sich am Anfang" ist dann falsch. `hilfe-playground.html` nennt „Gesamten Text öffnen" zweimal.

**Layout messen nach `innerHTML`** ist auf der Lemmaseite wirkungslos, solange `#lemmaContent` `hidden` trägt (`renderLemma` läuft vor dem Aufdecken). Aufrufpfad bis zum `classList.remove('hidden')` verfolgen. Schwellen-Specs mit null Zeilen Marge prüfen bei anderer Schrift (Linux-CI) still nichts.

**Korpusauswahl (#204):** `selectedTextsThunk` liefert nur die Auswahl, Instanzzustand (`state.scope`, `state.result`, `this.selected`) überlebt die Verengung: `this.state`/`this._*` je Werkzeug durchgehen. `_corpusAgg` (Hapax) und `_textById` (Reim) hängen am ungefilterten Thunk. Leer-Guard (#539): Werkzeuge mit Suchfeld löschen, die ohne stempeln.

**Lesepanel (#434):** populateModal setzt vier Kopffelder, `showEmptyState` leert nur Titel und Body: neue Schließpfade gegen alle vier halten. `lastSearchTerm` wird vor dem `try` gesetzt.

**Singular/Plural-Fundlisten (#643):** eine Suche nach `${n} Belege` verpasst ein Adjektiv dazwischen (horses-explorer `Die ${n} angezeigten Belege`, im Tooltip) und den Dativ (`${a} von ${b} Belegen`, rhyme-dictionary bei `minCount` 1). Andere Nomen derselben Ansicht (`Lemmata`, `Reimpartner`) mitprüfen. Erreichbarkeit von n=1 am Index zählen (`data/naming-index.json.gz`, `data/horses-index.json.gz` per Python), nicht behaupten. Neuer Faltungs-Aufruf auf MHD-Text: CONTRACTS.md §Fold nennt die Ausnahmen einzeln.

**Footer, Logos, SEO:** Footer-Quelle `includes/_footer.html`. `build-pages.py --check` zählt alle Seiten mit Chrome-Region und meldet SEO-Seiten getrennt (`SEO_PAGES` = `PAGES` + `api/index.html`). og:description wird aus `name="description"` kopiert: eine ungegatete Zahl dort steht doppelt. Logos: `assets/images/*-logo.*`, `textreihen/img/logo-*`, PNG-Maße per struct aus Bytes 16-24.
