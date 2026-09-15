---
name: playground-korpusauswahl-204
description: Review-Lehren zu #204 (Korpusauswahl wirkt auf die Analysewerkzeuge): welcher Werkzeug-Zustand die Verengung des Thunks ueberlebt und danach falsch anzeigt, plus Laufzeitprobe per node+playwright gegen :8080
metadata:
  type: project
---

Seit #204 (15.09.2026) liefert `selectedTextsThunk` in `playground-main.js` nur die in Schritt 1 angehakten Texte; bis dahin bekamen 10 von 11 Werkzeugen immer alle 667.

**Was die Aenderung wahr gemacht hat, das vorher falsch sein konnte:** die Werkzeuge halten Zustand auf der Instanz, der Text-IDs oder Ergebnisse aus einem frueheren Thunk-Stand traegt, und `show()` setzt ihn nicht zurueck. Vorher war jede je gewaehlte Text-ID immer im Thunk-Ergebnis; jetzt nicht mehr. In Runde 1 gemessen (Laufzeitprobe):
- `word-frequency.js` / `verse-ending-profile.js`: `state.scope` = Text-ID oder `author:X`; faellt der Text aus der Auswahl, liefert `computeFrequencies`/`computeProfile` null, die Tabelle sagt „Keine Daten.", das Dropdown springt auf die erste Option „Gesamtkorpus (666 Texte)", `state.scope` bleibt 'CR'.
- `rhyme-dictionary.js`: `state.result` bleibt ueber `show()` erhalten; die #204-Vorbelegung `applySingleSelectionDefault()` schreibt `state.textFilter` ohne Neuberechnung, und `filterNote` (Zeile ~427) rendert dann „Filter „CR" → 667 Texte" ueber ein ungefiltertes Ergebnis.
- `text-statistics.js`: eigene `this.selected`-Menge (Zeilen-Haekchen) behaelt IDs, die nicht mehr in `_stats` sind: Leiste „Ausgewaehlt: 3 / 1" neben „Keine Texte ausgewaehlt".
- Beschriftungen, die „Gesamtkorpus"/„im Korpus" sagen und jetzt die Auswahlgroesse zeigen: text-statistics:115, word-frequency:77+127, verse-ending-profile:85+142; index.html:298+307 „ueber alle Texte"; FEATURES.md:248/271/277/313.

**Normierungen** sind alle je Text (`rel = count / text.wordCount * 1000`, verse-position `count / totalOccurrences` aus `text.lemmata`): die Grundgesamtheit schrumpft nicht quer, keine falschen Raten. `_lemmaMap` in cooccurrence/rhyme kommt aus dem Authority-Index, nicht aus Texten. `_corpusAgg` (Hapax) und `_textById` (Reim) haengen am ungefilterten Thunk.

**Messrezepte:**
- Zahlen aus dem Korpusindex: `data/corpus-index.json.gz` per gzip+json, `texts[i].lemmata['lemma_4130']` ist eine Positionsliste (CR: 14, korpusweit 7.161). Alte `filterTexts('cr')` traf CR+CRO (178 Siglen haben Substring-Nebentreffer in Titel/Autor).
- Laufzeitprobe ohne Spec: `require('<repo>/node_modules/playwright').chromium`, gegen den laufenden Server auf :8080, `page.evaluate` auf `window.playground.ui.<tool>.state`; `show()` direkt aufrufen ersetzt die Navigation. Etwa 1 min je Lauf.
- Einzelspec: `node scripts/run-tests.js playground-corpus.spec.js`, 14 Tests in 1,5 min, VERDICT TEILLAUF.
- 11 Werkzeuge = 9 `show*Btn` (ohne Authority/Naming/Horses) + `findMultiLemmaBtn` + `findVersePositionBtn` in playground/index.html.

**Runde 2 (15.09.):** alle drei A-Befunde vom Aufrufer reproduziert und behoben (`state.result = null` im Prefill-Zweig, `ensureScopeResolvable()` vor `computeFrequencies`/`computeProfile`, `this.selected` auf `_stats` geschnitten), je ein Regressionstest; Einzelspec 17/17 in 2 min. Nach dem Fix ist `computeFrequencies`' `if (!text) return null` und das „Keine Daten." der Wortfrequenz nicht mehr erreichbar (Dropdown liefert nur gueltige IDs), das „Keine Daten fuer diese Auswahl" im Versendings-Profil dagegen schon (reine Prosa-Auswahl). Doku-Entscheid: Scope-Aussage einmal in FEATURES.md, ARCHITECTURE-Tabelle traegt keine Marker je Zeile.

**Runde 3 (15.09., Audit statt Diff):** Die Signatur-Loesung (`scopeSignature`, `_computedOver`) stempelt in `show()`, nicht beim Rechnen. Auswahl A, oeffnen (Stempel A), Auswahl bei offenem Werkzeug auf B, Suchen (Ergebnis ueber B), zurueck auf A, oeffnen: Stempel A == A, Ergebnis ueber B bleibt stehen. Gemessen: Kookkurrenz „14 Vorkommen / 30 Partner" unter 667 (korpusweit 7.161), Begriffs-Verteilung „Liebe" 1 Text / 153 unter 667 (korpusweit 654 / 154.345). Faustregel: **ein Stempel gehoert dorthin, wo das Ergebnis entsteht, nicht wo es angezeigt wird.** Zweite Lehre: verlaengert ein PR eine Umformulierung (lemma-distribution „in den ausgewaehlten Texten"), den Zwilling suchen (verse-position-search:169 sagte weiter „im Versdichtungs-Korpus"). Multi-Lemma haelt keinen Zustand: teiManager filtert je Aufruf per includedTexts (1.022 / 1 / 1.022 fuer minne+herze). Prosa-Texte ohne lineStarts: 67 von 667.

**Why:** Ein Fix, der einen Thunk verengt, prueft das Neue (die Guards); die Instanzfelder, die vom alten Vollbestand ausgingen, stehen anderswo und sehen unveraendert aus.
**How to apply:** Bei jeder Aenderung an den Thunks oder an `includedTexts` je Werkzeug `this.state`/`this._*` durchgehen und fragen, welches Feld eine Text-ID oder ein Ergebnis aus einem anderen Auswahlstand traegt; die Probe oben laeuft in einer Minute.
