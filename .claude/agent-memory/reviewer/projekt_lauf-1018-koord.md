---
name: projekt-lauf-1018-koord
description: Sammeldatei des Laufs 18.10.2026 (Koordination), beim Abschluss in projekt_gates_und_ci.md einzutragen; Nachkalibrierung Laufzeitbudget lemma-pos
metadata:
  type: project
---

Eingangsdatei dieses Laufs, damit parallele Spuren nicht in dieselbe Datei schreiben. Beim Abschluss in [[projekt_gates_und_ci]] unter check-runtime-budget.py einarbeiten und diese Datei löschen.

**Nachkalibrierung prüfen: `laeufe` größer als `n` des Schritts ist erklärbar, nicht übernehmen, sondern je Lauf zeigen.** Am 18.10. (Commit 471bf0be7): 22 Läufe, Schritt `Freshness lemma-pos (#462)` n 21; der fehlende Lauf ist ein PR-Lauf eines Zweigs von vor dem Merge des Schritts (Liste der Läufe über `actions/workflows/<wf>/runs?status=success&created=>=<seit>`, dann je Lauf `actions/runs/<id>/jobs` nach dem Schrittnamen). Die Dauern des Schritts waren zweigipflig (9–10 s oder 17–18 s), p90 = max.

**Seit 471bf0be7 trägt kein Eintrag `provisional_since`:** `erinnere()` kehrt immer nach `faellige_kalibrierung` leer zurück; geprüft ist der Pfad nur noch im Selbsttest (synthetische cfg). Erst ein neuer vorläufiger Eintrag weckt ihn wieder: dann auch prüfen, ob `basis` "vorlaeufig" enthält (Substring, `lade_budget`) und `reason` nicht zählt.

**Why:** Reviewer-Runde 1 zu #564 am 18.10.2026.
**How to apply:** bei jedem Diff an `scripts/audit/runtime-budget.json`.
