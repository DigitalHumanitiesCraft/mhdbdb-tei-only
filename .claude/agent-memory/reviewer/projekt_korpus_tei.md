---
name: projekt-korpus-tei
description: Strukturtatsachen des TEI-Korpus fürs Review: was der Korpus-Index liest, pc/caesura/gap, Vers vs. Prosa, WZB-Eigenheiten und Tafelskripte (Zeilenenden, Index-Abgleich), Parzival-Buchgrenzen (#358), Header-Konventionen, Reset-Zahlen, Trierer Findebuch-Dump (#259)
metadata:
  type: project
---
Verdichtet 14.10. und 16.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Was `build-corpus-index.py` liest:** nur `w` und `l` (iterwalk; Frames ohne `w` fallen weg) plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`. Änderungen dort sind ohne Rebuild und Bump prüfbar. `corpus-index.json.gz` enthält keine xml:ids und keine Versnummern-Stämme (gegen einen `lemma_N`-Kontrollwert gemessen): eine gelöschte `pc`-/`caesura`-id kann dort nicht hängen.

**Token-Ebene**
- `@lemmaRef` ist in tei/ einwertig. Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason. Multi-pos = Leerzeichen in @pos.
- pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen, keine Klammern (auch `<pc>&lt;</pc>` vor einem Buchanfang in PZ). `pc@join` steuert den Leerraum im Reader.

**caesura/gap (#252)**
- gap immer `reason="lost"`, kein `extent`. Zwei Kopien der caesura-Zahl in TEI-MODEL.md, kein Gate.
- Rohmuster inline: `<pc[^>]*>\(</pc>\s*<caesura[^>]*/>\s*<pc[^>]*>\)</pc>`; `find(T+'caesura')` sieht nur direkte Kinder.
- Linecode-Gegenprobe nur für Siglen in `sources/linecode-manifest.csv`; die Zeilennummer im Linecode-Präfix ist nicht überall die TEI-`@n` (RVBR um eins niedriger): Versatz am Wortlaut der Nachbarzeilen ermitteln.
- revisionDesc-Präzedenz bei #252 ist gespalten (#426 ohne `<change>`, #477 mit je einem pro Datei): ein fehlender Eintrag ist Klasse C.
- Resttabelle TEI-MODEL §6.5a zählt die nicht migrierten Fälle; jede Handkorrektur daraus macht die Zeile falsch, der Diff fasst sie nicht an. Messgerät: `python scripts/migrate-caesura-to-gap-252.py` ohne `--apply`.

**Vers und Prosa:** Reader-Deep-Link `?verseId=` löst nur in Texten mit `<l>` auf; Prosa hat nur `lb`, `lb@n` wiederholt sich je Seite (Kochbücher: je Rezept neu).

**Parzival-Buchgrenzen (#358)**
- `ingest/parzival-buecher/grenzen.csv` (16 Buchanfänge nach Lachmann) ist die Eingabe von `<milestone unit="book">`; ein falscher Wert wandert in den Korpus. Buch VIII beginnt bei 398,1 (PZ_39801_0), nicht 399,1; die erste Wort-ID von IX ist `PZ_43301_1`.
- Quellen als OCR nach `.claude/tmp/`: `https://archive.org/download/<id>/<id>_djvu.txt` (Bartsch `wolframsvonesch01bartgoog`, `...03...`, `...00...`; Martin Kommentar `parzival00wolfuoft`). Bartsch: Überschrift in Großbuchstaben, dann Inhaltsangabe, dann der erste Vers mit Marginalzahl (OCR schlecht, locker suchen). Martin: die erste Note liegt oft nach dem Buchanfang und ist kein Beleg gegen die Grenze.
- Ein Anfangswort-Vergleich TEI gegen TEI prüft nichts gegen die Quelle.
- Buchmarkup im TEI: nur der `milestone`; `div type="chapter"` sind Dreißiger. DATA-MODEL.md nennt `milestone unit="chapter"` inline, das Schema erlaubt nur `book` unter div.
- Leseansicht: „Buch N" wird im div-Zweig nur gehoben, wenn der book-milestone `firstElementChild` des div ist; steht ein `pb`/`lb` davor, rendert er unter „Strophe N".

**WZB:** Eigennamen fehlen im TEI (Lücken im Kontext sind kein Extraktionsfehler). Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreißen Wörter; seit #390 (`wzb-wortgrenzen-390.py`) sind 16 davon zusammengeführt (Wort unter der xml:id der ersten Hälfte; 6 `pc join=left` mitgewandert, deren id-Folio nicht mehr zur Position passt). Breve: 607 Tokens zerlegt (o+U+0306), 26 vorkomponiert (U+014F), also nicht „überall zerlegt"; `|` ist mit 5.651 `<pc join="left">` normale Interpunktion. `<l>` ohne `@n`; kombinierende Breve zerfallen bei flachem `\w`-Vergleich. Vulgata-Zitate: Folio gegen Kolumnentitel (pb), Kapitel-`head` des div, dann biblegateway `version=VULGATE`. Die xml:id `WZB_<blatt>_<zeile>_<n>` zählt ab 0 über `<w>` **und** `<pc>`, Suffix auch `13b`: ein „Wort n+1" aus der id ist bei Satzzeichen davor falsch.

**WZB-Tafelskripte (`scripts/ingest/wzb/wzb-*.py`, `wzb-corresp-punkt2.py`, #370/#526)**
- `REPO` = `Path(__file__).parents[3]`, lesen `tei/WZB.tei.xml` und `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch mit `scripts/ingest/wzb/`, `tei/`, `data/`, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`. Gleiches `--out-dir` gibt bytegleiche Ausgabe. Nicht idempotent (zweiter Lauf bricht am Tafel-Abgleich ab): nur auf der Basiskopie reproduzieren.
- **EOL:** WZB ist die einzige CRLF-Datei in tei/, im Blob selbst (gemischte Zeilenenden). Ein Handedit kann LF-Zeilen auf CRLF kippen, `git diff --stat` zeigt nur eine zu hohe Zeilenzahl. Gegenprobe: `difflib` auf `split(b"\n")` gegen den Basis-Blob, je Zeile `endswith(b"\r")`; erwartet nur Token-Zeilen plus change-Zeile.
- **Alt/neu:** beide Stände per lxml zu `xml:id -> (text, lemmaRef, corresp, pos, ana)`, Mengen vergleichen; Zeilenvergleich nur nach Entfernen der richtigen revisionDesc-Zeile (`#370 Punkt 2` trifft ZWEI change-Zeilen).
- **Index-Abgleich ohne Neubau:** `corpus-index.json.gz` beider Stände per `git show`, `texts[WZB].lemmata[lemma]`-Längen vergleichen: Summe der Differenzen = Tokenzahl des Laufs; `lemmaIndex` gleich, wenn alle Ziel-Lemmata in der WZB schon belegt waren, dann ist auch der Authority-Index unberührt. `wordCount` zählt nur lemmatisierte `<w>`.
- **Begriffshilfe bleibt unberührt**, entgegen „FOLGEN: Begriffshilfe neu bauen" im Docstring der drei #526-Skripte: diese Läufe schreiben kein `w/@ana`.
- **#397:** die Ratsche `corresp-coverage-baseline.json` steigt um die Tokenzahl und muss per `--update-baseline=corresp` mitkommen; `check-authority-cross-refs.py` ohne `--check` druckt die Istwerte. Die Konsolenausgabe kürzt `vergleich_belege[:10]`, die CSV nicht.
- **Guard-Grenze (#526):** Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos für eine mehrdeutige Form läuft durch; dort trägt allein die Tafel, also den Vers lesen.
- **Mitalternde Nachbarn (kein Gate):** WZB-projectDesc (`@corresp`-Quoten), CONTRACTS.md Variant-Dictionary-Absatz und §A (unannotierte WZB-Tokens als Invariante, seit #534 datiert), DATA-MODEL.md `variantCandidates`-Kommentar; bei einem neuen Lauf dort und im Thread nach Rest-Zählungen suchen. Der ADR-Text in `DECISIONS.md` ist datiert und wird nicht nachgezogen.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+; im Header nackte IDs, in works.xml URLs.
- `status="restricted"` = `n="no-print"`; kein Konsument von excerpt-only/restricted/`@media print` außerhalb der Prüfseiten.
- **NEIM-Liedkonkordanz steht zweimal** (#453): im Header `editorialDecl/normalization` und je Lied als `<note n="1">` im Body (Ziffern als `<w lemmaRef=lemma_53328 pos=NUM>`). Ein Header-Fix ohne die Note erzeugt Widerspruch; die Note anzufassen ist ein `<w>`-Wortlaut-Change (volle Korpus-Checkliste). Bei Header-Korrekturen immer nach einer Body-Kopie suchen.
- revisionDesc trägt je-Datei-Zahlen der Annotationsserien (#216, #369): damit lassen sich fremde Zählungen rekonstruieren. Kombinierende Diakritika sind in Headern verbreitet: vor Vergleichen NFC.

**Reset-Zahlen** (`count-verse-numbering-resets.py`) stehen dreimal in tei-text-reader.js und in FEATURES.md, kein Gate. Alt/neu per `git archive`; Regel abschalten per Patch `in_nested_parallel` -> False. tei/ ist 1,4 GB.

**Trierer Findebuch-Dump (#259, außerhalb des Repos):** DHCraft-Drive `Projekte/mhdbdb/extern/`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5` (kein Namensraum, externe DTD); Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`. **Keine Wortform aus dem Dump in Berichte:** Strukturbefunde über Zählungen und maskierten Text. `<form type="sublemma">` trägt teils ein `<gram>`-Kind, `itertext()` hängt das Kürzel an die Schreibform; `<hi>`-Kinder erzeugen Scheinleerzeichen.
