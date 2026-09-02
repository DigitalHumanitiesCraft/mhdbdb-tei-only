---
name: concepts-graph-pitfalls
description: Was ein Review an einem Skript pruefen muss, das ueber <ptr type="broader"> in concepts.xml eine Huelle bildet (Selbstschleife, Mehrfacheltern, Wurzel-Frage); gemessen 2026-09-01 bei #28 Gleis 1
metadata:
  type: project
---

Der Begriffsgraph in `authority-files/concepts.xml` ist kein Baum. Gemessen am 2026-09-01 (567 `<category>`): 51 Kategorien haben mehr als einen `<ptr type="broader">`, und `concept_12050000` zeigt auf sich selbst. Eine Huellenbildung ohne Visited-Menge laeuft dort endlos oder zaehlt doppelt.

Zweite wiederkehrende Frage: **gehoert die Wurzel selbst zur Huelle?** Bei #28 (Wurzel `concept_23123000`, "Einzelsprachen") zeigten 31 Lemmata mit einem Sense direkt auf die Wurzel, 27 davon ohne Nachfahren-Treffer; das Skript nahm nur echte Nachfahren. Wer "Subtree" schreibt, meint meist die Wurzel mit, wer "unter X" schreibt, nicht. Beim Review beides gegeneinander halten.

**Why:** Der Phasenplan-Text und das Skript-Docstring benutzten in #28 zwei verschiedene Formulierungen fuer dieselbe Menge, und nur die Messung hat den Unterschied sichtbar gemacht.

**How to apply:** Bei jedem Diff, der ueber `broader` in concepts.xml traversiert: Visited-Menge suchen, Wurzel-Inklusion mit einem Python-Einzeiler gegen `api/lemmata/index.json` nachmessen, und die Zahl der direkt auf die Wurzel zeigenden Lemmata im Befund nennen. Messskript-Muster: Kinder aus `catDesc/ptr[@type=broader]` sammeln, DFS mit Stack und `out`-Dict.
