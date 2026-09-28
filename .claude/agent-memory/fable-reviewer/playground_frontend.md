---
name: playground-frontend
description: Playground und Frontend im Review: Hash-Pfad bis innerHTML, Multi-Lemma-Suche, Werkzeugzustand nach Korpusauswahl, Zaehlungen der Werkzeuge, Hilfe/Landing mitlesen, localStorage, CSV-Grenzen
metadata:
  type: project
---
Stand 28.09.2026.

**Hash bis innerHTML:** router.js `parseHash` -> `handleMultiLemmaRoute` (IDs nur bei `/^\d+$/`) -> `MultiLemmaSearchUI.executeSearch` -> tei-ui.js `display*` (Titel = `searchTerms.join(' + ')`) -> ui-helpers.js `displaySummaryResults`/`displayHinweis`. `mode` per Whitelist, `dist` per parseInt, `q` nur in `input.value`. Roh gerendert: concept-explorer.js `searchTerm` (Selbst-XSS), lemma-explorer.js `componentText`. `escapeHtml` ist je Modul kopiert.

**Multi-Lemma-Suche**
- `fetch` sitzt in ui-helpers.js (Klick auf `.result-summary`, `enrichFileResults`), nicht in multi-lemma-search.js; „bis zu 50 Fundstellen je Karte" = tei-ui.js `fileResults.slice(0, 50)`.
- Kennt nur die nackte Zahl (tei-ui.js:19), nicht `lemma_N`. `authority-manager.js` `resolveLemmaNames` hat 0 Aufrufer.
- Proximity verlangt alle Lemmata je Text und scannt `words[]`. Naeheprobe ohne Browser: corpus-index `texts[i].lemmata` = {lemma_id: [positionen]}, Treffer bei `|pa - pb| <= dist`.
- Haelt keinen Zustand (filtert je Aufruf per includedTexts).

**Korpusauswahl (#204):** `selectedTextsThunk` liefert nur die Auswahl. Instanzzustand (`state.scope`, `state.result`, `this.selected`) ueberlebt die Verengung. Bei jeder Aenderung an Thunks oder includedTexts `this.state`/`this._*` je Werkzeug durchgehen. Normierungen sind je Text; `_corpusAgg` (Hapax) und `_textById` (Reim) haengen am ungefilterten Thunk.

**Zaehlungen:** `playground/js/ui/tei` = 13 Werkzeuge + corpus-scope.js + tei-ui.js (`git ls-files`). Landing-Knoepfe per `<button id="...Btn">` in playground/index.html zaehlen; die Bloecke Korpusanalysen, Register & Indizes, Weitere Korpusanalysen, Experimentelle Forschungsdaten stehen in dieser Reihenfolge (Analyse-Bloecke nicht nebeneinander).

**Umbauten an Bloecken/Hilfe**
- Hilfe-Abschnitt gegen Panel-Zugehoerigkeit messen (lxml `get_element_by_id('<panel>')` -> Knopfbeschriftungen gegen `h3` der Hilfe), nicht gegen Namen.
- Landing-Liste in `index.html` (unter der Blockueberschrift) mitlesen.
- `moreAnalysesToggle` sitzt in `#moreTeiQueries` (display:none bis Korpus geladen).
- `#authorityToggle` (Ladezustand) und `#authorityQueriesToggle` auseinanderhalten.

**Diverses**
- `displayResults` zaehlt `results.length` ins Abzeichen; `displayHinweis` ist zaehlerlos.
- localStorage-Schluessel bindestrichgetrennt (`mhdbdb-...`, Abschnitte `mhdbdb-playground-section-<panelId>`); einziges `localStorage.clear()` in site-chrome.js hinter `#clearSiteDataBtn`.
- CSV-Grenzen: word-frequency 50, verse-ending 50, cooccurrence 50, text-comparison 100, rhyme 200. horses-explorer hat keine Klappzeilen. Kopfzeilen von Textvergleich und Versposition sind dynamisch.
- Reimwoerterbuch: 3-Zeichen-Suffix von `normalized`, 2 wenn beide <= 4 Zeichen; `minCount` 1; Autorfilter per Substring.
- Gattungsvorschlaege `findGenreSuggestions`: startsWith vor Textzahl vor Label, Limit `GENRE_SUGGESTION_LIMIT`. `findWorksInGenre` ohne Aufrufer.
- `findAlternativeMatch` (concept-explorer) baut darauf, dass `matchesNormalized` den Treffer nicht sieht.
- Dokumentsuche: CONTRACTS.md §C traegt die Objektform von `searchDocumentUsingEnhancedIndex`; `containsAll` prueft Array-Truthiness.
- Lemma-Seite ist `lemma/lemma-page.js`.
