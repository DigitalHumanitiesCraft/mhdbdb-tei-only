---
name: findebuch-dump-259
description: Fallen des Trierer Findebuch-Dumps (temp/woerterbuchnetz2015/FindeB/P5, gitignoriert, ausserhalb jedes Worktrees) fuer Reviews an #259: gram-Kinder in sublemma-Formen, Akut-Regel der Vorabmessung, Lizenzauflage
metadata:
  type: project
---

Der Findebuch-Dump (22 Dateien, kein Namensraum, externe DTD in Zeile 2) liegt nur im Hauptbaum unter `temp/`, nicht im Worktree; Skripte brauchen `--dump` mit absolutem Pfad. Gemessen am 2026-09-02 (Review Runde 1 zu #259):

- **`<form type="sublemma">` enthaelt in 3.462 von 8.610 Faellen ein `<gram>`-Kind** (Wortartkuerzel mit Punkt; Runde 1 hatte 3.457 gezaehlt, Runde 2 misst 3.462, gram immer direktes Kind, nie tiefer), und in 2.705 davon *nur* das gram, ohne Schreibform. Der Trennstrich steht **nicht in der Form**, sondern als Tail des Geschwister-`<lb/>` unmittelbar vor ihr (2.704 von 2.705); ohne gram-Teilbaum ist der Formtext in allen 2.705 Faellen der Leerstring. `itertext()` auf sublemma haengt das Kuerzel an die Schreibform. `<form type="lemma">` ist davon frei: 23.434 mit `<ref>`-Kind, 11.394 ohne, kein einziges gram.
- **Zweite, kleinere Kontamination: `<hi>`-Kinder** (39 in sublemma), meist ein Kuerzel mit Punkten vor oder zwischen Schreibformen. Ein Mehrwort-Filter ueber "Leerzeichen im Text" faengt 21 solcher Formen als Mehrwort, obwohl das Leerzeichen nur an der Markup-Grenze entsteht; 175 der 196 Mehrwortformen (Stand 8b4e5f907) haben das Leerzeichen dagegen im Textknoten selbst. gram-Tails mit Buchstaben: genau 1.
- Die Docstring-Zahl **2.465 (49,7 %)** ist die Zahl der Teil-2-Paare (alt, dedupliziert, 4.960) mit gram-Kind, nicht die mit Leerzeichen/Punkt (das waeren 2.556, 51,5 %).
- **Die 477 / 5.500 der Vorabmessung im Ticket** (Kommentar vom 2026-09-01) entstehen nur auf der itertext-Formenmenge (8.610 Paare) und wenn zusaetzlich zu ezh, e-Trema und Bindestrich auch Akut-Akzente getilgt werden (é→e usw.); mit den drei Regeln allein sind es 475 / 5.494. Beides roh gezaehlt, dedupliziert 467 / 465. Auf der gram-bereinigten Menge (5.709) ergeben die Akute nur noch +6 / +2 (3.415→3.421, 564→566).
- Ein leeres `--dump`-Verzeichnis bricht mit ZeroDivisionError ab (Division durch `len(pairs)` im Ertragsblock), seit dem ersten Commit; laut, nicht stumm.
- Alle 234.243 Werte in `authority-index.variants` sind Strings; `api/lemmata/index.json` und `authority-index.lemmata` haben dieselben 43.363 Normalformen.
- Der Tiebreak nach Id in den Stufe-3-Spiegelungen ist auf diesem Datensatz folgenlos (0 tiebreak-abhaengige Faelle).

**Why:** Das Ticket verlangt, dass keine Wortform aus dem Dump in Berichte gelangt; Strukturbefunde muessen deshalb ueber Zaehlungen und maskierten Text laufen (Buchstaben zu `x`). Und die gram-Kontamination ist im stdout-Report des Skripts unsichtbar, weil er nur zaehlt.

**How to apply:** Bei jedem Diff, der `parse_dump` oder die Normalisierung der Trierer Seite anfasst: Anzahl Paare (8.610 mit itertext, 5.905 ohne gram), Teil 1 und Teil 2 nachmessen, und pruefen, ob nicht-alphabetische Zeichen (Leerzeichen, Punkt) in normalisierten Schreibformen stehen. Messskript-Muster: Modul per `importlib` laden, `clean_text` ohne gram-Teilbaum gegen `itertext` halten. Verwandt: [[concepts-graph-pitfalls]].
