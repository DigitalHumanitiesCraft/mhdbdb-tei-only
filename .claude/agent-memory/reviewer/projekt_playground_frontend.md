---
name: projekt-playground-frontend
description: Playground und Frontend im Review: Hash-Pfad bis innerHTML, Multi-Lemma-Suche, Nummernpfad, Werkzeugzustand nach Korpusauswahl, Zählungen, Hilfe/Landing mitlesen, Reader, Auswahlzeile
metadata:
  type: project
---
Verdichtet 14.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Hash bis innerHTML:** router.js `parseHash` -> `handleMultiLemmaRoute` (IDs nur bei `/^\d+$/`) -> `MultiLemmaSearchUI.executeSearch` -> tei-ui.js `display*` (Titel = `searchTerms.join(' + ')`) -> ui-helpers.js `displaySummaryResults`/`displayHinweis`. `mode` per Whitelist, `dist` per parseInt, `q` nur in `input.value`. Roh gerendert: concept-explorer.js `searchTerm` (Selbst-XSS), lemma-explorer.js `componentText`.

**Multi-Lemma-Suche**
- `fetch` sitzt in ui-helpers.js (Klick auf `.result-summary`, `enrichFileResults`), nicht in multi-lemma-search.js; „bis zu 50 Fundstellen je Karte" = tei-ui.js `fileResults.slice(0, 50)`. Kein Zustand (filtert je Aufruf per includedTexts).
- Nummer als Eingabe (#467): `assets/js/lib/lemma-id-input.js` `parseLemmaIdInput` (auch `lexicon.xml#lemma_N`, führende Nullen weg) für search-engine.js `resolveSearchTerm` und tei-ui.js `resolveLemmaIds`. `authority-manager.js` `resolveLemmaNames` hat 0 Aufrufer.
- **Ziffernlemmata gegen den Nummernpfad messen:** Prüfbeispiel `1` (lemma_1 *a* gegen lemma_53328, projekt_lexikon_variants.md). Jede Übergabe per Schreibform (`lemma-page.js` `korpus.html?search=<lemma.lemma>` und Varianten-Chips, cooccurrence-ranking.js `lemmata=<lemma.lemma>`) landet für sie beim Nummern-Lemma; Übergaben per `ids=` (lemma-explorer.js `sendLemmaToOccurrenceSearch`) sind gepinnt.
- **ID-Eingabe in den sechs Registern und der Begriffs-Verteilung** (#545, `assets/js/lib/authority-id-input.js` `findByIdInput`/`withIdHit`): in den Registern ADDITIV vor den Texttreffern, in concept-distribution `resolveQuery` ERSETZEND. ID-Formen im Index uneinheitlich (Gattungen hex, `work_WZB`, UUIDs, `person_anonym`): vor einem Befund die Formen zählen.
- Der Lemma-Klick im Begriffe-Explorer setzt `window.location.hash = lemmata&q=lemma_N`; der Router füllt `#lemmaSearch`. `switchLemmaSearchMode('component')` übersetzt eine Lemma-ID im Feld per `findByIdInput` in die Schreibform. Gleicher-Hash-Falle: die Lemmaliste eines Begriffs (`showLemmasWithConcept`) rendert nur unter `#concepts` und `#names`. Der Begriffshilfe-Download (`scripts/build-begriffshilfe.py` SCOPE_B, byte-gleich gegatet) beschreibt das Suchfeld des Begriffe-Explorers: Satz dort gegen das Verhalten halten.
- **Dokumentsuche seit #58:** Karte `.result-summary-dokument` (die `.result-summary-static`-Verzweigung in `createSummaryCard` hat keinen Aufrufer mehr), Fundstellen lazy über `dokument-belege.js`; Links `korpus.html?textId&lemmaIds&position=<§B-Position>`, der Reader zählt in `processWord` gleich (w mit lemmaRef und Text).
- **Reader ohne `position`:** tei-text-reader.js ~131-143 setzt `currentHighlightIndex = 0` und scrollt nach 600 ms zum ersten Beleg, `#highlightIndicator` = „Treffer 1 von N". Ein Hilfetext „öffnet sich am Anfang" ist falsch, sobald der erste Beleg nicht am Textanfang steht. `hilfe-playground.html` nennt „Gesamten Text öffnen" zweimal (Dokumentsuche und Abschnitt 9, `grep -n` zählt): eine Verhaltenskorrektur an einer Stelle an der anderen gegenlesen.
- Proximity verlangt alle Lemmata je Text. Probe ohne Browser: corpus-index `texts[i].lemmata` = {lemma_id: [positionen]}, Treffer bei `|pa - pb| <= dist`.
- **Schreibform-Übergabe nach #463:** ohne `ids=` nimmt `resolveLemmaIds` `matches[0]`; ein unbelegtes Lemma mit Stufe-2-Eintrag landet dann bei einem anderen. Probe nur über eine Teilmenge (Volllauf >600 s).

**Korpusauswahl (#204):** `selectedTextsThunk` liefert nur die Auswahl; Instanzzustand (`state.scope`, `state.result`, `this.selected`) überlebt die Verengung. Bei jeder Änderung an Thunks oder includedTexts `this.state`/`this._*` je Werkzeug durchgehen. `_corpusAgg` (Hapax) und `_textById` (Reim) hängen am ungefilterten Thunk. Leer-Guard „Kein Text ausgewählt" (#539): Werkzeuge mit Suchfeld löschen dort, die ohne stempeln davor.

**Zählungen und Umbauten:** `playground/js/ui/tei` = Werkzeuge + corpus-scope.js + tei-ui.js (`git ls-files`). Hilfe-Abschnitt gegen Panel-Zugehörigkeit messen (lxml `get_element_by_id('<panel>')` -> Knopfbeschriftungen gegen `h3` der Hilfe); Landing-Liste in `index.html` mitlesen. `#authorityToggle` und `#authorityQueriesToggle` auseinanderhalten.

**Router-Start vor dem Korpus (#535):** `dispatch` stellt eine `CORPUS_ROUTES`-Route bis `window.playground.corpusReady` zurück und läuft sie nur bei unverändertem `_navigationEpoch`. Probe: `playground-router-start.spec.js` hält `corpus-index.json.gz` per `page.route` zurück, kalter Context, nicht warm-page.js.

**Lesepanel der Hauptseite schließen (#434):** der Kopf hat vier Felder, die populateModal setzt (`readingTitle`, `readingAuthor`, `readingMetadata`, `readingBody`); app.js `showEmptyState` leert nur Titel und Body. Jeder neue Schließ-/Reset-Pfad: alle vier gegen populateModal halten. `lastSearchTerm` ist Quelle der Adresse, wird in `handleSearch` aber VOR dem `try` gesetzt: jeder neue Leser gegen beide Rückgabe-false-Pfade halten. Specs mit `minne` öffnen einen Großtext: feste `waitForTimeout` sind dort als Negativprobe nicht trennscharf.

**Auswahlzeile korpus.html:** die Suchspalte ist nach einer Suche schmaler, weil app.js `displayResults` dem `#mainGrid` die Klasse `three-column` gibt (korpus.css ab 1280 px: `1fr 1fr 2fr`), nicht wegen Flex-Mechanik. „Nur diese" samt Trenner wird sichtbar, sobald `#textFilter` nicht leer ist (app.js, Filter-Handler) und verbreitert die Knopfgruppe; bei 1280 px mit Filter bleibt dem umbrechenden Label (`flex-wrap min-w-0`, Gruppe `shrink-0`) wenig Platz (Überlauf gemessen 13.10., Linux-Font). Playground hat dieselbe Zeile (`#selectNoneBtn`) ohne Überlauf.

**Diverses:** einziges `localStorage.clear()` in site-chrome.js hinter `#clearSiteDataBtn`.
