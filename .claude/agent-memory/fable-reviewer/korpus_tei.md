---
name: korpus-tei
description: Strukturtatsachen des TEI-Korpus fürs Review: was der Korpus-Index liest, pc/caesura/gap, Vers vs. Prosa, WZB-Eigenheiten, Header-Konventionen, Reset-Zahlen, Trierer Findebuch-Dump (#259)
metadata:
  type: project
---
Verdichtet 02.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Was `build-corpus-index.py` liest:** nur `w` und `l` (iterwalk; Frames ohne `w` fallen weg) plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`. Änderungen dort sind ohne Rebuild und Bump prüfbar.

**Token-Ebene**
- `@lemmaRef` ist in tei/ einwertig. Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason. Multi-pos = Leerzeichen in @pos.
- pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen, keine Klammern. `pc@join` steuert den Leerraum im Reader.

**caesura/gap (#252)**
- gap immer `reason="lost"`, kein `extent`. Zwei Kopien der caesura-Zahl in TEI-MODEL.md, kein Gate.
- Rohmuster inline: `<pc[^>]*>\(</pc>\s*<caesura[^>]*/>\s*<pc[^>]*>\)</pc>`. `find(T+'caesura')` sieht nur direkte Kinder (MUG `<l><hi><caesura/></hi></l>`).
- Linecode-Gegenprobe nur für Siglen in `sources/linecode-manifest.csv` (MAI, NEI fehlen).

**Vers und Prosa**
- Reader-Deep-Link `?verseId=` löst nur in Texten mit `<l>` auf; Prosa hat nur `lb`, `lb@n` wiederholt sich je Seite (Kochbücher: je Rezept neu).

**WZB:** Eigennamen fehlen im TEI (Lücken im Kontext sind kein Extraktionsfehler). Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreißen Wörter. `<l>` ohne `@n`; kombinierende Breve (`Ew̆er`) zerfallen bei flachem `\w`-Vergleich. CRLF mit einigen nackten LF. Vulgata-Zitate prüfen: Folio gegen Kolumnentitel (pb), Kapitel-`head` des div, dann biblegateway `version=VULGATE`.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+; im Header nackte IDs, in works.xml URLs.
- `status="restricted"` = `n="no-print"`; kein Konsument von excerpt-only/restricted/`@media print` außerhalb der Prüfseiten.
- revisionDesc trägt je-Datei-Zahlen der Annotationsserien (#216, #369): damit lassen sich fremde Zählungen rekonstruieren. Kombinierende Diakritika sind in Headern verbreitet: vor Vergleichen NFC.

**Reset-Zahlen** (`count-verse-numbering-resets.py`) stehen dreimal in tei-text-reader.js und in FEATURES.md, kein Gate. Alt/neu per `git archive`; Regel abschalten per Patch `in_nested_parallel` -> False.

tei/ ist 1,4 GB.

**Trierer Findebuch-Dump (#259, außerhalb des Repos)**
- Ort: DHCraft-Drive `Projekte/mhdbdb/extern/`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5`; 22 Dateien, kein Namensraum, externe DTD. Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`. **Keine Wortform aus dem Dump in Berichte:** Strukturbefunde über Zählungen und maskierten Text (Buchstaben zu `x`).
- `<form type="sublemma">`: 3.462 von 8.610 mit `<gram>`-Kind (immer direktes Kind); `itertext()` hängt das Kürzel an die Schreibform. Der Trennstrich steht als Tail des Geschwister-`<lb/>` davor, nicht in der Form. 39 `<hi>`-Kinder erzeugen Scheinleerzeichen. `<form type="lemma">` hat kein gram. Review-Muster: Modul per importlib, `clean_text` ohne gram-Teilbaum gegen `itertext`.
