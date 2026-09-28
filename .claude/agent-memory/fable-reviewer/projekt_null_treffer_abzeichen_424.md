---
name: null-treffer-abzeichen-424
description: #424 Null-Treffer-Abzeichen im Playground: Tester Alan = contrib_007, displayResults vs displayHinweis, Proximity-Grundmenge, Einzelspec-Aufruf, Cloud-Umgebung 10.09.2026
metadata:
  type: project
---

Tester „Alan" aus #419 („Testprotokoll AvB") ist Alan van Beek (contributors.xml contrib_007); „Vielhauer" steht nirgends im Repo oder Issue.

`displayResults` (ui-helpers.js) zaehlt `results.length` ins Abzeichen, `displayHinweis(titel, grund, rat)` ist der zaehlerlose Ersatz. Proximity verlangt alle Lemmata je Text (tei-manager.js ~376) und scannt `words[]` (Teilmenge der `lemmata{}`-Zeugen).

Einzelspec: `node scripts/run-tests.js <datei>.spec.js` (VERDICT TEILLAUF). Cloud-Umgebung 10.09.2026: kein gh, aber api.github.com ohne Token 200; user-attachments-Download liefert kein Zip (Login).

**Why:** Zuschreibungen an Personen und Zaehlergrundmengen waren im Auftrag ungeprueft.
**How to apply:** Namen gegen contributors.xml, Abzeichenzahlen gegen die Funktion, die sie schreibt.
