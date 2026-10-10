---
name: playground-frontend
description: Playground und Frontend im Review: Hash-Pfad bis innerHTML, Multi-Lemma-Suche, Nummernpfad, Werkzeugzustand nach Korpusauswahl, Zählungen, Hilfe/Landing mitlesen, CSV-Grenzen
metadata:
  type: project
---
Verdichtet 02.10. und 10.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Hash bis innerHTML:** router.js `parseHash` -> `handleMultiLemmaRoute` (IDs nur bei `/^\d+$/`) -> `MultiLemmaSearchUI.executeSearch` -> tei-ui.js `display*` (Titel = `searchTerms.join(' + ')`) -> ui-helpers.js `displaySummaryResults`/`displayHinweis`. `mode` per Whitelist, `dist` per parseInt, `q` nur in `input.value`. Roh gerendert: concept-explorer.js `searchTerm` (Selbst-XSS), lemma-explorer.js `componentText`.

**Multi-Lemma-Suche**
- `fetch` sitzt in ui-helpers.js (Klick auf `.result-summary`, `enrichFileResults`), nicht in multi-lemma-search.js; „bis zu 50 Fundstellen je Karte" = tei-ui.js `fileResults.slice(0, 50)`. Hält keinen Zustand (filtert je Aufruf per includedTexts).
- Nummer als Eingabe (#467): `assets/js/lib/lemma-id-input.js` `parseLemmaIdInput` (auch `lexicon.xml#lemma_N`, führende Nullen weg) für search-engine.js `resolveSearchTerm` und tei-ui.js `resolveLemmaIds`. `authority-manager.js` `resolveLemmaNames` hat 0 Aufrufer.
- **Ziffernlemmata gegen den Nummernpfad messen:** Prüfbeispiel `1` (lemma_1 *a* gegen lemma_53328, siehe lexikon_variants.md). Jede Übergabe per Schreibform (`lemma-page.js` `korpus.html?search=<lemma.lemma>` und Varianten-Chips, cooccurrence-ranking.js `lemmata=<lemma.lemma>`) landet für sie beim Nummern-Lemma; Übergaben per `ids=` (lemma-explorer.js `sendLemmaToOccurrenceSearch`) sind gepinnt.
- **ID-Eingabe in den sechs Registern und der Begriffs-Verteilung** (#545, `assets/js/lib/authority-id-input.js` `findByIdInput`/`withIdHit`): in den Registern ADDITIV vor den Texttreffern (Identitäts-Dedupe), in concept-distribution `resolveQuery` ERSETZEND wie vorher für `concept_N`. Nullen fallen nur bei rein numerischem Rest (`^0+(?=\d+$)`); ID-Formen im Index sind uneinheitlich (Gattungen hex, teils rein numerisch mit führender Null; `work_WZB`, UUIDs; `person_anonym`): vor einem Befund die Formen zählen.
- Der Lemma-Klick im Begriffe-Explorer setzt `window.location.hash = lemmata&q=lemma_N`; der Router füllt `#lemmaSearch`. `switchLemmaSearchMode('component')` übersetzt eine Lemma-ID im Feld per `findByIdInput` in die Schreibform. Gleicher-Hash-Falle: die Lemmaliste eines Begriffs (`showLemmasWithConcept`) rendert nur unter `#concepts` und `#names`. Die Begriffshilfe-Download (`scripts/build-begriffshilfe.py` SCOPE_B, byte-gleich gegatet) beschreibt das Suchfeld des Begriffe-Explorers: Satz dort gegen das Verhalten halten.
- Proximity verlangt alle Lemmata je Text. Probe ohne Browser: corpus-index `texts[i].lemmata` = {lemma_id: [positionen]}, Treffer bei `|pa - pb| <= dist`; Verse per bisect über `lineStarts`/`lineEnds`. Ergebnisreihenfolge = `texts[]` = Dateiname sortiert.
- Export (#448, `multi-lemma-export.js`): `contextStart` inkl., `contextEnd` exkl.; Dokumentmodus nur `matchCount` = Summe der `text.lemmata[lemma_N]`-Längen; `text.id` = Sigle = Dateistamm.

**Korpusauswahl (#204):** `selectedTextsThunk` liefert nur die Auswahl; Instanzzustand (`state.scope`, `state.result`, `this.selected`) überlebt die Verengung. Bei jeder Änderung an Thunks oder includedTexts `this.state`/`this._*` je Werkzeug durchgehen. `_corpusAgg` (Hapax) und `_textById` (Reim) hängen am ungefilterten Thunk. Leer-Guard „Kein Text ausgewählt" (#539): Werkzeuge mit Suchfeld löschen dort, die ohne stempeln davor.

**Zählungen und Umbauten:** `playground/js/ui/tei` = Werkzeuge + corpus-scope.js + tei-ui.js (`git ls-files`). Landing-Knöpfe per `<button id="...Btn">` in playground/index.html zählen. Hilfe-Abschnitt gegen Panel-Zugehörigkeit messen (lxml `get_element_by_id('<panel>')` -> Knopfbeschriftungen gegen `h3` der Hilfe), nicht gegen Namen; Landing-Liste in `index.html` mitlesen. `#authorityToggle` und `#authorityQueriesToggle` auseinanderhalten.

**Router-Start vor dem Korpus (#535):** `dispatch` stellt eine `CORPUS_ROUTES`-Route bis `window.playground.corpusReady` zurück und läuft sie nur bei unverändertem `_navigationEpoch`. Einziger Korpuszugriff außerhalb `ui/tei` und playground-main.js: authority-manager.js `getCorpusFrequency`, gerufen nur von TEI-Werkzeugen. Probe: Spec `playground-router-start.spec.js` hält `corpus-index.json.gz` per `page.route` zurück, kalter Context, nicht warm-page.js (dort käme der Index aus IndexedDB).

**Diverses:** einziges `localStorage.clear()` in site-chrome.js hinter `#clearSiteDataBtn`. CSV-Grenzen: word-frequency, verse-ending, cooccurrence je 50, text-comparison 100, rhyme 200.
