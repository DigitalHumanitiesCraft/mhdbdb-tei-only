---
name: korpus-tei
description: Strukturtatsachen des TEI-Korpus fuers Review: was der Korpus-Index liest, pc/caesura/gap, Vers vs. Prosa, WZB-Eigenheiten, Header-Konventionen, Reset-Zahlen
metadata:
  type: project
---
Stand 28.09.2026.

**Was `build-corpus-index.py` liest:** nur `w` und `l` (iterwalk; Frames ohne `w` fallen weg) plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`. Aenderungen dort sind ohne Rebuild und Bump pruefbar.

**Token-Ebene**
- `@lemmaRef` ist in tei/ einwertig (0 Dateien mehrwertig, 21.09.).
- Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason (0 Verstoesse, 23.09.). Multi-pos = Leerzeichen in @pos.
- pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen, keine Klammern. `pc@join` steuert den Leerraum im Reader.

**caesura/gap (#252)**
- gap immer `reason="lost"`, kein `extent`. Zwei Kopien der caesura-Zahl in TEI-MODEL.md, kein Gate.
- Rohmuster inline: `<pc[^>]*>\(</pc>\s*<caesura[^>]*/>\s*<pc[^>]*>\)</pc>`.
- `find(T+'caesura')` sieht nur direkte Kinder (MUG `<l><hi><caesura/></hi></l>`).
- Linecode-Gegenprobe nur fuer Siglen in `sources/linecode-manifest.csv` (Spalte `sigle`; MAI, NEI fehlen).

**Vers und Prosa**
- Reader-Deep-Link `?verseId=` loest nur in Texten mit `<l>` auf; Prosa hat nur `lb`, und `lb@n` wiederholt sich je Seite.
- 67 von 667 Texten ohne lineStarts (Prosa).
- Kochbuecher (HUB3 u.a.): Rezepte sind `div` mit `head` ohne `@n`, `lb@n` startet je Rezept neu.

**WZB**
- Eigennamen fehlen im TEI (Luecken im Kontext sind kein Extraktionsfehler).
- Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreissen Woerter.
- `<l>` ohne `@n`; kombinierende Breve (`Ew̆er`) zerfallen bei flachem `\w`-Vergleich.
- CRLF mit einigen nackten LF im Bestand.
- Vulgata-Zitate pruefen: Folio gegen Kolumnentitel (pb), Kapitel-`head` des div, dann biblegateway `version=VULGATE`.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+; im Header nackte IDs, in works.xml URLs.
- `status="restricted"` = `n="no-print"`; kein Konsument von excerpt-only/restricted/`@media print` ausserhalb der Pruefseiten.
- revisionDesc traegt je-Datei-Zahlen der Annotationsserien (#216, #369): damit lassen sich fremde Zaehlungen rekonstruieren.
- Kombinierende Diakritika sind in Headern verbreitet: vor Vergleichen NFC.

**Reset-Zahlen** (`count-verse-numbering-resets.py`) stehen dreimal in tei-text-reader.js und in FEATURES.md, kein Gate. Alt/neu per `git archive`; Regel abschalten per Patch `in_nested_parallel` -> False.

tei/ ist 1,4 GB (OVG allein ~66 MB).
