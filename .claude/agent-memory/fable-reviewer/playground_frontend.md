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
- Nummer als Eingabe (#467, Zweig `claude/467-nummernsuche-korpus-multilemma`, Review 30.09.2026): `assets/js/lib/lemma-id-input.js` `parseLemmaIdInput` (auch `lexicon.xml#lemma_N`, fuehrende Nullen weg) fuer search-engine.js `resolveSearchTerm` und tei-ui.js `resolveLemmaIds`; vor #467 nahm der Playground die nackte Zahl ungeprueft, die Hauptseite gar nicht. `authority-manager.js` `resolveLemmaNames` hat 0 Aufrufer.
- **Ziffern-Lemmata gegen Nummernpfad messen:** am 30.09.2026 4 Lemmata mit reiner Ziffernschreibung und 78 Ziffernschluessel in `authorityIndex.variants`; seit `claude/228-ziffern` (01.10.2026) nur lemma_53328 `1` und 62 Schluessel (Skript ueber data/*.json.gz). Pruefbeispiel der Nummernsuche ist seither `1` (lemma_1 *a* gegen lemma_53328), siehe lexikon_variants.md. Jede Uebergabe per Schreibform (`lemma-page.js` `korpus.html?search=<lemma.lemma>` und Varianten-Chips, cooccurrence-ranking.js `lemmata=<lemma.lemma>`) landet fuer sie beim Nummern-Lemma. Uebergaben per `ids=` (lemma-explorer.js `sendLemmaToOccurrenceSearch`) sind gepinnt und sicher.
- Proximity verlangt alle Lemmata je Text und scannt `words[]`. Naeheprobe ohne Browser: corpus-index `texts[i].lemmata` = {lemma_id: [positionen]}, Treffer bei `|pa - pb| <= dist`.
- Haelt keinen Zustand (filtert je Aufruf per includedTexts).
- Versprobe ohne Browser (30.09.): `lineStarts`/`lineEnds` im corpus-index, Vers per bisect ueber lineStarts, Treffer wenn ein zweites Lemma in [start,end]; Ergebnisreihenfolge = `texts[]`-Reihenfolge = Dateiname sortiert (667/667). minne+herze Vers = 166 Treffer in 66 Texten, erste Datei AXR; multi-lemma-verse.spec.js:7 nennt noch „64 in 18" (alter Index).
- Export-Arbeiter (`exportZeilen`, PARALLEL 4): `abgebrochen`-Flag im catch, Pruefung nach dem await; einzige Zeile ausserhalb des try ist der `fortschritt`-Aufruf. Promise.all haengt an jedem Arbeiter einen Reject-Handler, spaetere Zweitfehler sind keine unhandled rejections.
- Export (#448, `multi-lemma-export.js`): Ergebnisobjekte tragen `contextStart` inkl., `contextEnd` exkl. (tei-manager.js `slice`), `matchPositions`, `distance`; Dokumentmodus nur `matchCount` = Summe der `text.lemmata[lemma_N]`-Laengen, Index-Schluessel sind durchweg `lemma_N` (667/667 gemessen), `text.id` = Sigle = Dateistamm. Leiste haengt hinter `container.firstElementChild` (Kopfzeile von `displaySummaryResults`), also ueber der Liste. `teiManager.corpusIndex` ist das rohe Index-JSON (mit `version`), gesetzt in playground-main.js.

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
- Leseansicht #358 (B2, 02.10.2026): „Buch N" wird im div-Zweig nur gehoben, wenn der book-milestone `firstElementChild` ist; steht ein `pb`/`lb` davor, rendert er wieder unter „Strophe N". Gemessen: alle 827 PZ- und 467 WH-chapter-divs beginnen mit `<l>`, Korpus hat 0 `<milestone>` (Kontrollwert 61 Dateien mit `<pb`); Sonde: lxml ueber `body//div[@type="chapter"]`, erstes Element-Kind zaehlen. Einziger `state`-Bauer ist `extractAndFormatBody`, `processChildren` wirft ausserhalb. In-Repo-Buchgrenzen nur Laufplan §4.2 (II 58,27, III 116,5, IV 179,13), `ingest/parzival-buecher/grenzen.csv` kommt erst mit C2.
