---
name: findebuch-dump-259
description: Fallen des Trierer Findebuch-Dumps (#259, ausserhalb des Repos): gram- und hi-Kinder in sublemma, Trennstrich am Geschwister-lb, Akut-Regel der Vorabmessung, Lizenzauflage
metadata:
  type: project
---
Stand 22.09.2026 (Messungen 02.09.).

- Ort: DHCraft-Drive `Projekte/mhdbdb/extern/`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5`; 22 Dateien, kein Namensraum, externe DTD. Default in `compare-findebuch-resolution-259.py`, `--dump` absolut geht. Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`.
- **Keine Wortform aus dem Dump in Berichte:** Strukturbefunde ueber Zaehlungen und maskierten Text (Buchstaben zu `x`).
- `<form type="sublemma">`: 3.462 von 8.610 mit `<gram>`-Kind (immer direktes Kind), 2.705 davon nur gram; `itertext()` haengt das Kuerzel an die Schreibform. Trennstrich steht als Tail des Geschwister-`<lb/>` davor, nicht in der Form. 39 `<hi>`-Kinder erzeugen Scheinleerzeichen an Markup-Grenzen. `<form type="lemma">` hat kein gram.
- Paare: 8.610 mit itertext, 5.905 ohne gram. Die 477/5.500 der Vorabmessung entstehen nur auf der itertext-Menge und mit zusaetzlicher Akut-Tilgung.
- Leeres `--dump` endet laut mit ZeroDivisionError.
- Review-Muster: Modul per importlib, `clean_text` ohne gram-Teilbaum gegen `itertext`; auf nicht-alphabetische Zeichen in normalisierten Formen pruefen.
