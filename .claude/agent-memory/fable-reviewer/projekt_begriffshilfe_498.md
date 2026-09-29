---
name: projekt-begriffshilfe-498
description: Review-Rezepte fuer die #498-Skripte (measure-498-concept-cross-sections.py, scripts/build-begriffshilfe.py): Korpusdurchgang cachen, Zaehlfalle Belege unter Begriff vs. Gesamtbelege, Kontrollwerte Aufmerksamkeit, Freshness-Gate
metadata:
  type: project
---
Stand 29.09.2026 (Runde 1 auf `claude/498-begriffshilfe`, Runde 1 auf `claude/498-begriffshilfe-seite`).

**Ausgeliefert (Seite-Zweig):** Generator liegt seit dem Seite-Zweig in `scripts/build-begriffshilfe.py` (nicht mehr audit/, keine Varianten, kein `--topic`, kein git, kein Datum), Ausgabe `assets/downloads/mhdbdb-begriffshilfe.md`, CI-Step „Freshness Begriffshilfe" in data-integrity.yml zwischen API- und Index-Freshness. Zwei Laeufe am 29.09.: SHA ac0ae4ee… identisch, 325.477 Byte, 567 Zeilen, 24 s kalt / 16 s warm. Gegenprobe billig: `--out <scratch>` und sha256sum gegen den Baum, das Skript schreibt dann nichts in den Baum. Das Skript liest nur concepts.xml, lexicon.xml (sense/ptr, entry/@xml:id, form/orth; **nicht** sense/@ana) und w/@ana: `extract-variants --apply` kann die Datei deshalb nicht aendern.

**Nummernkopplung:** DEVELOPMENT.md zaehlt die CI-Checks durch (seit #498: 17, Index-Freshness = 12), der Workflow-Kopf hat eigene Nummern (5b fuer die Begriffshilfe) und nennt im Absatz nach der Liste die DEVELOPMENT-Nummer als Querverweis; der hinkt bei jeder Einfuegung nach.

**Korpusdurchgang cachen:** `count_tokens(set(concepts_of))` aus dem Messskript braucht Minuten. Einmal in-process laufen lassen, `(tokens, texts)` als Pickle ins Scratchpad, jede weitere Gegenprobe liest das Pickle. Beide Skripte per `importlib` laden; `gen.load_measure_module()` liefert das Messmodul gleich mit.

**Zaehlfalle:** Die Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die den Begriff tragen. Bei polysemen Lemmata ist das weniger als die Gesamtzahl (muot 779 unter Aufmerksamkeit, 897 gesamt; 376 von 2.685 Top-Lemma-Eintraegen weichen ab). Ein Prompttext, der die Zahl "Belege im Korpus" nennt, behauptet die Gesamtzahl.

**Kontrollwerte Aufmerksamkeit (concept_22650000), Stand b46902a35:** 652 Bedeutungen, 597 Lemma-IDs = 597 Schreibungen (kein Unterschied), Kriegswesen 51 von 652 auf Platz 9 der Mitbegriffe nach Bedeutungen, PMI-Rang 4.240 von 7.791 bei min_support 5. 126 von 62.202 sense ohne Begriff; 5 Begriffe ohne sense. `find_cycles` liefert seit b46902a35 (Selbstverweis Metalle entfernt) eine leere Liste.

**Explorer-Behauptungen, die halten:** concept-explorer.js:146-162 filtert ueber alle Lemmata des Begriffs, sortiert alphabetisch, zeigt 20; lemma-explorer.js:1046-1071 zeigt Begriffe je sense.
