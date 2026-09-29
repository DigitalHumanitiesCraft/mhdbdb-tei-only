---
name: projekt-begriffshilfe-498
description: Review-Rezepte fuer die #498-Skripte (measure-498-concept-cross-sections.py, build-begriffshilfe-498.py): Korpusdurchgang cachen, Zaehlfalle Belege unter Begriff vs. Gesamtbelege, Kontrollwerte Aufmerksamkeit
metadata:
  type: project
---
Stand 29.09.2026 (Runde 1 auf `claude/498-begriffshilfe`).

**Korpusdurchgang cachen:** `count_tokens(set(concepts_of))` aus dem Messskript braucht Minuten. Einmal in-process laufen lassen, `(tokens, texts)` als Pickle ins Scratchpad, jede weitere Gegenprobe liest das Pickle. Beide Skripte per `importlib` laden; `gen.load_measure_module()` liefert das Messmodul gleich mit.

**Zaehlfalle:** Die Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die den Begriff tragen. Bei polysemen Lemmata ist das weniger als die Gesamtzahl (muot 779 unter Aufmerksamkeit, 897 gesamt; 376 von 2.685 Top-Lemma-Eintraegen weichen ab). Ein Prompttext, der die Zahl "Belege im Korpus" nennt, behauptet die Gesamtzahl.

**Kontrollwerte Aufmerksamkeit (concept_22650000), Stand b46902a35:** 652 Bedeutungen, 597 Lemma-IDs = 597 Schreibungen (kein Unterschied), Kriegswesen 51 von 652 auf Platz 9 der Mitbegriffe nach Bedeutungen, PMI-Rang 4.240 von 7.791 bei min_support 5. 126 von 62.202 sense ohne Begriff; 5 Begriffe ohne sense. `find_cycles` liefert seit b46902a35 (Selbstverweis Metalle entfernt) eine leere Liste.

**Explorer-Behauptungen, die halten:** concept-explorer.js:146-162 filtert ueber alle Lemmata des Begriffs, sortiert alphabetisch, zeigt 20; lemma-explorer.js:1046-1071 zeigt Begriffe je sense.
