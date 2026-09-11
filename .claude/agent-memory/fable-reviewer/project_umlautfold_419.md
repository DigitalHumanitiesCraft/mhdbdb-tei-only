---
name: umlautfold-419
description: Review der Umlaut-Faltung (#419): Authority-Index-Felder sind optional je Eintrag, Umlaut-Regex ohne Grossbuchstaben, Fold-Konsumenten die auf matchesNormalized bauen
metadata:
  type: project
---

Drei Fallen aus dem Review von d2ef557b4 (11.09.2026), Zweig `claude/419-reimfilter-und-umlautsuche`.

**`items[0].keys()` ist nicht das Schema des Authority-Index.** Optionale Felder
(`altDE`, `altEN`, `altNormalized`) stehen nur an den Eintraegen, die sie tragen
(concepts 263/266/263 von 567, genres 250/308/250 von 615). Die Sonde des
Aufrufers las die Schluessel des ersten Eintrags und erklaerte die Felder fuer
nicht vorhanden. Messen mit `Counter` ueber alle Eintraege.

**Umlaut-Zaehlung vor dem Lowercasing braucht `[äöüÄÖÜ]`.** `[äöü]` liefert 379
statt 391 ueber termDE/termEN/title der vier Sammlungen; die 12 fehlenden
Werte beginnen mit Ä/Ö/Ü (Ämter, Ölproduktion, Übersinnliche Wahrnehmung).

**Was der Fold wahr macht:** ein Treffer kann existieren, den
`matchesNormalized` nicht sieht. Konsumenten, die auf dem Gegenteil bauen:
`findAlternativeMatch` in `playground/js/ui/authority/concept-explorer.js`
(Hinweis „auch: …"). Bei 56 Begriffen listet der Explorer den Treffer ohne
Hinweis (z. B. „fruchte" -> Obst via altDE „Früchte").

**Ranking-Probe fuer resolveQuery:** Nachbau in Python mit `stufe()` alt/neu,
Kollisionen ueber ALLE verglichenen Felder (auch `normalized` und `alt*`) messen,
nicht nur termDE/termEN. Einziges Paar, das unter normalizeMHG verschieden und
unter dem Fold gleich ist: Vögel/Vogel, beide in concept_14020000.

**Runde 2 (11.09.):** Umlaut-Zaehlung haengt an der Feldmenge: 391 (termDE/termEN/title),
414 (+ Begriffs-Alt-Terme), 446 (+ Werk author/sigle, die Getter des Werk-Explorers).
„No resolution changes target" ist ueber 3.371 deskriptor-abgeleitete Anfragen
falsch fuer 3 (mann, manner, maengel): Fold-Praefix auf Primaerfeld (50) schlaegt
rohen Alt-Praefix (45). `run-tests.js --list` zaehlt Tests ohne Lauf (329/34).
Zweig lag zur Reviewzeit nicht auf origin (`git branch -r`), „gepusht" im JOURNAL
war damit falsch.

**Why:** Der Auftrag lieferte drei Zahlen und eine Feldbehauptung, und alle vier
kamen aus einer Sonde mit engerer Feldmenge als der Code.
**How to apply:** Bei Suchpfad-Aenderungen die Feldmenge des Aufrufers (Getter)
mit der Feldmenge der Messung abgleichen, bevor eine Zahl uebernommen wird.
