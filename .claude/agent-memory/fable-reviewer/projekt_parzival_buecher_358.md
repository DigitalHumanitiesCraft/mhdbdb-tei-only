---
name: parzival-buecher-358
description: Parzival-Buchgrenzen (#358, A3/B2): Messrezept am OCR von Bartsch und Martin, Fallen (VIII = 398,1, Redezeichen-pc, TEI-gegen-TEI-Vergleich), Proben für Skript und Spec
metadata:
  type: project
---
Zusammengelegt aus fünf Runden, verdichtet 10.10.2026.

`ingest/parzival-buecher/grenzen.csv` (16 Buchanfänge nach Lachmann) ist die Eingabe von A3 (`<milestone unit="book">`); ein falscher Wert wandert in den Korpus. Buch VIII beginnt bei 398,1 (PZ_39801_0), nicht bei 399,1.

**Messrezept**
- Quellen als OCR: `https://archive.org/download/<id>/<id>_djvu.txt` nach `.claude/tmp/` (gitignoriert). Bartsch `wolframsvonesch01bartgoog` (Bd. 9), `...03...` (Bd. 10), `...00...` (Bd. 11); Martin Kommentar `parzival00wolfuoft`.
- Bartsch: Überschrift `ACHTES BUCH.` in Großbuchstaben, dann Inhaltsangabe, dann der erste Vers mit Marginalzahl (OCR von Bd. 10 schlecht, locker suchen).
- Martin: Buchüberschrift als kurze römische Zeile (OCR `IL`, `YII.`), dann die erste Note; sie liegt oft nach dem Buchanfang und ist kein Beleg gegen die Grenze.
- `build-grenzen.py` reproduziert die CSV byteidentisch; `git status` zeigt unter autocrlf trotzdem ` M`, der Blob-Hash (`hash-object --no-filters`) ist die Messung.

**Fallen**
- Ein Anfangswort-Vergleich TEI gegen TEI prüft nichts gegen die Quelle (Bartsch 787,1 „Anfortas unt die sîne", TEI „amfortas und die").
- `<pc>&lt;</pc>` vor einem Buchanfang (PZ_43301_0) ist ein Redezeichen; die erste Wort-ID von IX ist `PZ_43301_1`.
- `<hi rend="initial">` steht an 12 von 16 Buchanfängen (nicht XI, XII, XIII, XVI) und an 398,1; `div type="chapter"` sind Dreißiger, Buch-Markup gibt es im TEI nicht.
- DATA-MODEL.md:807 nennt `milestone unit="chapter"` inline, das Schema erlaubt nur `book` unter div.
- Leseansicht (B2): „Buch N" wird im div-Zweig nur gehoben, wenn der book-milestone `firstElementChild` des div ist; steht ein `pb`/`lb` davor, rendert er unter „Strophe N".

**Skript und Spec**
- Basis billig rekonstruieren: ` subtype="dreissiger"` und milestone-Zeilen aus HEAD strippen, Blob-SHA gegen `rev-parse <basis>:tei/PZ.tei.xml`; statt Index-Rebuild `process_tei_file` aus build-corpus-index per importlib auf HEAD und Basis vergleichen.
- `pz-wh-struktur.py` hält das erste `<w>` des `<l>` nach dem milestone gegen `erste_wort_id`; alle Prüfungen laufen vor dem ersten Schreibvorgang.
- `dreissiger-buecher.spec.js`: Soll aus dem TEI, Ist aus dem DOM (`data-core`). Mutationsproben, die rot werden müssen: Label „Kapitel“ statt „Strophe“, Buch nicht gerendert, milestones ans Divende, Nummern vertauscht, PZ ohne milestones.
