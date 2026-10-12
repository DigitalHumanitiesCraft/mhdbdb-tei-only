---
name: korpus-tei
description: Strukturtatsachen des TEI-Korpus fürs Review: was der Korpus-Index liest, pc/caesura/gap, Vers vs. Prosa, WZB-Eigenheiten, Header-Konventionen, Reset-Zahlen, Trierer Findebuch-Dump (#259)
metadata:
  type: project
---
Verdichtet 08.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Was `build-corpus-index.py` liest:** nur `w` und `l` (iterwalk; Frames ohne `w` fallen weg) plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`. Änderungen dort sind ohne Rebuild und Bump prüfbar. `corpus-index.json.gz` enthält keine xml:ids und keine Versnummern-Stämme (gegen einen `lemma_N`-Kontrollwert gemessen): eine gelöschte `pc`-/`caesura`-id kann dort nicht hängen.

**Token-Ebene**
- `@lemmaRef` ist in tei/ einwertig. Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason. Multi-pos = Leerzeichen in @pos.
- pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen, keine Klammern. `pc@join` steuert den Leerraum im Reader.

**caesura/gap (#252)**
- gap immer `reason="lost"`, kein `extent`. Zwei Kopien der caesura-Zahl in TEI-MODEL.md, kein Gate.
- Rohmuster inline: `<pc[^>]*>\(</pc>\s*<caesura[^>]*/>\s*<pc[^>]*>\)</pc>`; `find(T+'caesura')` sieht nur direkte Kinder.
- Linecode-Gegenprobe nur für Siglen in `sources/linecode-manifest.csv` (nachsehen, nicht dem Thread glauben). Die Zeilennummer im Linecode-Präfix ist nicht überall die TEI-`@n` (RVBR um eins niedriger): Versatz am Wortlaut der Nachbarzeilen ermitteln.
- revisionDesc-Präzedenz bei #252 ist gespalten (#426 ohne `<change>`, #477 mit je einem pro Datei): ein fehlender Eintrag bei einer Handkorrektur ist Klasse C.
- Resttabelle TEI-MODEL §6.5a zählt die nicht migrierten Fälle; jede Handkorrektur daraus macht die Zeile falsch, der Diff fasst sie nicht an. Messgerät: `python scripts/migrate-caesura-to-gap-252.py` ohne `--apply`. Der Skriptkopf („nur unlemmatisierter Wortlaut“ für Klasse C) stimmt nicht: EIL 2866 trug beide `@lemmaRef`.

**Vers und Prosa:** Reader-Deep-Link `?verseId=` löst nur in Texten mit `<l>` auf; Prosa hat nur `lb`, `lb@n` wiederholt sich je Seite (Kochbücher: je Rezept neu).

**WZB:** Eigennamen fehlen im TEI (Lücken im Kontext sind kein Extraktionsfehler). Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreißen Wörter. `<l>` ohne `@n`; kombinierende Breve zerfallen bei flachem `\w`-Vergleich. Vulgata-Zitate: Folio gegen Kolumnentitel (pb), Kapitel-`head` des div, dann biblegateway `version=VULGATE`.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+; im Header nackte IDs, in works.xml URLs.
- `status="restricted"` = `n="no-print"`; kein Konsument von excerpt-only/restricted/`@media print` außerhalb der Prüfseiten.
- **NEIM-Liedkonkordanz steht zweimal** (#453): im Header `editorialDecl/normalization` („Lied N = C Str. a-b“) und je Lied als `<note n="1">` im Body (Ziffern als `<w lemmaRef=lemma_53328 pos=NUM>`). Ein Header-Fix ohne die Note erzeugt Widerspruch; die Note anzufassen ist ein `<w>`-Wortlaut-Change (volle Korpus-Checkliste). Bei Header-Korrekturen immer nach einer Body-Kopie suchen.
- revisionDesc trägt je-Datei-Zahlen der Annotationsserien (#216, #369): damit lassen sich fremde Zählungen rekonstruieren. Kombinierende Diakritika sind in Headern verbreitet: vor Vergleichen NFC.

**Reset-Zahlen** (`count-verse-numbering-resets.py`) stehen dreimal in tei-text-reader.js und in FEATURES.md, kein Gate. Alt/neu per `git archive`; Regel abschalten per Patch `in_nested_parallel` -> False. tei/ ist 1,4 GB.

**Trierer Findebuch-Dump (#259, außerhalb des Repos):** DHCraft-Drive `Projekte/mhdbdb/extern/`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5` (kein Namensraum, externe DTD); Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`. **Keine Wortform aus dem Dump in Berichte:** Strukturbefunde über Zählungen und maskierten Text. `<form type="sublemma">` trägt teils ein `<gram>`-Kind, `itertext()` hängt das Kürzel an die Schreibform; `<hi>`-Kinder erzeugen Scheinleerzeichen.
