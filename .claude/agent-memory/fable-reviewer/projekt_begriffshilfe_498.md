---
name: projekt-begriffshilfe-498
description: Review-Rezepte für die #498-Skripte (measure-498-concept-cross-sections.py, scripts/build-begriffshilfe.py): Korpusdurchgang cachen, Zählfalle Belege unter Begriff vs. gesamt, Freshness-Gate
metadata:
  type: project
---
Verdichtet 02.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Generator** `scripts/build-begriffshilfe.py` schreibt `assets/downloads/mhdbdb-begriffshilfe.md`; CI-Step „Freshness Begriffshilfe" in data-integrity.yml zwischen API- und Index-Freshness. Er liest nur concepts.xml, lexicon.xml (sense/ptr, entry/@xml:id, form/orth; **nicht** sense/@ana) und w/@ana: `extract-variants --apply` kann die Datei deshalb nicht ändern. Gegenprobe billig: `--out <scratch>` und sha256sum gegen den Baum (schreibt dann nichts in den Baum; CRLF siehe gates_und_ci).

**Nummernkopplung:** DEVELOPMENT.md zählt die CI-Checks durch, der Workflow-Kopf hat eigene Nummern (5b) und nennt im Absatz nach der Liste die DEVELOPMENT-Nummer als Querverweis; der hinkt bei jeder Einfügung nach (siehe auch „for checks 4 and 14" in gates_und_ci).

**Korpusdurchgang cachen:** `count_tokens(set(concepts_of))` aus dem Messskript braucht Minuten. Einmal in-process laufen lassen, `(tokens, texts)` als Pickle ins Scratchpad; beide Skripte per `importlib` laden (`gen.load_measure_module()` liefert das Messmodul mit).

**Zählfalle:** Die Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die den Begriff tragen, bei polysemen Lemmata weniger als die Gesamtzahl (muot 779 unter Aufmerksamkeit, 897 gesamt). Ein Prompttext, der „Belege im Korpus" nennt, behauptet die Gesamtzahl.

**Kontrollwerte Aufmerksamkeit (concept_22650000), Stand b46902a35:** 652 Bedeutungen, 597 Lemma-IDs = 597 Schreibungen; `find_cycles` leer.
