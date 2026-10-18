---
name: projekt-playground-frontend
description: Playground und Frontend im Review: Hash-Pfad bis innerHTML, Multi-Lemma-Suche, Nummernpfad, Werkzeugzustand nach Korpusauswahl, Zählungen, Hilfe/Landing mitlesen, Reader, Auswahlzeile
metadata:
  type: project
---
Verdichtet 18.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Hash bis innerHTML:** router.js `parseHash` -> `handleMultiLemmaRoute` (IDs nur bei `/^\d+$/`) -> `MultiLemmaSearchUI.executeSearch` -> tei-ui.js `display*` (Titel = `searchTerms.join(' + ')`) -> ui-helpers.js `displaySummaryResults`/`displayHinweis`. `mode` per Whitelist, `dist` per parseInt, `q` nur in `input.value`. Roh gerendert: concept-explorer.js `searchTerm` (Selbst-XSS), lemma-explorer.js `componentText`.

**Multi-Lemma-Suche**
- `fetch` sitzt in ui-helpers.js (Klick auf `.result-summary`, `enrichFileResults`), nicht in multi-lemma-search.js; „bis zu 50 Fundstellen je Karte" = tei-ui.js `fileResults.slice(0, 50)`.
- Nummer als Eingabe (#467): `assets/js/lib/lemma-id-input.js` `parseLemmaIdInput` für search-engine.js `resolveSearchTerm` und tei-ui.js `resolveLemmaIds`. `authority-manager.js` `resolveLemmaNames` hat 0 Aufrufer.
- **Ziffernlemmata gegen den Nummernpfad messen:** Prüfbeispiel `1` (lemma_1 *a* gegen lemma_53328; seit `claude/228-ziffern` zeigen alle Ziffernschlüssel des Laufzeit-Wörterbuchs auf lemma_53328, Belege nur NEIM, #453). Jede Übergabe per Schreibform (`lemma-page.js` `korpus.html?search=<lemma.lemma>` und Varianten-Chips, cooccurrence-ranking.js `lemmata=<lemma.lemma>`) landet für sie beim Nummern-Lemma; Übergaben per `ids=` (lemma-explorer.js `sendLemmaToOccurrenceSearch`) sind gepinnt.
- **ID-Eingabe in den sechs Registern und der Begriffs-Verteilung** (#545, `authority-id-input.js` `findByIdInput`/`withIdHit`): in den Registern ADDITIV vor den Texttreffern, in concept-distribution `resolveQuery` ERSETZEND. ID-Formen im Index uneinheitlich (Gattungen hex, `work_WZB`, UUIDs, `person_anonym`): vor einem Befund die Formen zählen.
- Der Lemma-Klick im Begriffe-Explorer setzt `window.location.hash = lemmata&q=lemma_N`. Gleicher-Hash-Falle: die Lemmaliste eines Begriffs (`showLemmasWithConcept`) rendert nur unter `#concepts` und `#names`. Der Begriffshilfe-Download (`build-begriffshilfe.py` SCOPE_B, byte-gleich gegatet) beschreibt das Suchfeld des Begriffe-Explorers: Satz dort gegen das Verhalten halten.
- **Dokumentsuche seit #58:** Karte `.result-summary-dokument`, Fundstellen lazy über `dokument-belege.js`; Links `korpus.html?textId&lemmaIds&position=<§B-Position>`, der Reader zählt in `processWord` gleich.
- **Reader ohne `position`:** tei-text-reader.js setzt `currentHighlightIndex = 0` und scrollt nach 600 ms zum ersten Beleg („Treffer 1 von N"). Ein Hilfetext „öffnet sich am Anfang" ist falsch, sobald der erste Beleg nicht am Textanfang steht. `hilfe-playground.html` nennt „Gesamten Text öffnen" zweimal: eine Korrektur an einer Stelle an der anderen gegenlesen.

**Korpusauswahl (#204):** `selectedTextsThunk` liefert nur die Auswahl; Instanzzustand (`state.scope`, `state.result`, `this.selected`) überlebt die Verengung. Bei jeder Änderung an Thunks oder includedTexts `this.state`/`this._*` je Werkzeug durchgehen. `_corpusAgg` (Hapax) und `_textById` (Reim) hängen am ungefilterten Thunk. Leer-Guard „Kein Text ausgewählt" (#539): Werkzeuge mit Suchfeld löschen dort, die ohne stempeln davor.



**Lesepanel der Hauptseite schließen (#434):** der Kopf hat vier Felder, die populateModal setzt (`readingTitle`, `readingAuthor`, `readingMetadata`, `readingBody`); app.js `showEmptyState` leert nur Titel und Body. Jeder neue Schließ-/Reset-Pfad: alle vier gegen populateModal halten. `lastSearchTerm` wird in `handleSearch` VOR dem `try` gesetzt: jeder neue Leser gegen beide Rückgabe-false-Pfade halten. Specs mit `minne` öffnen einen Großtext: feste `waitForTimeout` sind dort als Negativprobe nicht trennscharf.

