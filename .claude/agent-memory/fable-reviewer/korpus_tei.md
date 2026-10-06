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
- Linecode-Gegenprobe nur für Siglen in `sources/linecode-manifest.csv` (MAI, NEI fehlen; GWTK = `neue-texte-klaus/gtk2.txt`, RVBR = `erledigt/rvbr.txt` sind drin, obwohl ein #252-Kommentar vom 23.09. das Gegenteil sagte). Die Zeilennummer im 19-stelligen Linecode-Präfix ist nicht überall die TEI-`@n`: bei RVBR um eins niedriger (06.10.: Linecode 17223 `...,` = TEI l n=17224), bei GWTK gleich. Vor einem Versvergleich den Versatz am Wortlaut der Nachbarzeilen ermitteln. Omissionsmarker im Linecode ist `...` plus Satzzeichen.
- `corpus-index.json.gz` enthält keine xml:ids und keine Versnummern-Stämme (06.10.: `w`-Kontrollwert `NEIC_6303150_0` und `6303150` je 0 Treffer, `lemma_5961` 5.928). Eine gelöschte `pc`-/`caesura`-id kann dort also nicht hängen; Rebuild-Behauptungen des Aufrufers sind so ohne Rebuild prüfbar.
- revisionDesc-Präzedenz bei #252 ist gespalten: erster Durchgang (#426, 103 TEI-Dateien) ohne `<change>`-Eintrag, zweiter (#477) mit je einem pro Datei. Ein fehlender Eintrag bei einer Handkorrektur ist deshalb Klasse C, keine Regelverletzung; dokumentiert ist in TEI-MODEL §2.4 nur die Form.
- Resttabelle TEI-MODEL §6.5a (Zeilen um 736/741) zählt die nicht migrierten Fälle; jede Handkorrektur daraus macht die Zeile falsch, und der Diff fasst sie nicht an.
- Billigstes Messgerät für die Resttabelle: `python scripts/migrate-caesura-to-gap-252.py` ohne `--apply` ist ein reiner Trockenlauf (06.10.: `C: 9`, `B': 35`, Zielmenge 0) und druckt die B'-Zeilen mit Inhalt. Der Skriptkopf (Z. 33-35) sagt „nur unlemmatisierter Wortlaut" für Klasse C; das war schon am 10.09. falsch (EIL 2866 „mit vil" trug damals beide `@lemmaRef`), heute 14 von 18 `<w>` in den 9 Zeilen lemmatisiert.

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
