---
name: projekt-korpus-tei
description: Strukturtatsachen des TEI-Korpus fürs Review: was der Korpus-Index liest, pc/caesura/gap, Vers vs. Prosa, WZB-Eigenheiten und Tafelskripte (Zeilenenden, Index-Abgleich), Parzival-Buchgrenzen (#358), Header-Konventionen, Reset-Zahlen, Trierer Findebuch-Dump (#259)
metadata:
  type: project
---
Verdichtet 18.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Was `build-corpus-index.py` liest:** nur `w` und `l` (iterwalk; Frames ohne `w` fallen weg) plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`. Änderungen dort sind ohne Rebuild und Bump prüfbar. `corpus-index.json.gz` enthält keine xml:ids: eine gelöschte `pc`-/`caesura`-id kann dort nicht hängen.

**Token-Ebene**
- `@lemmaRef` ist in tei/ einwertig. Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason. Multi-pos = Leerzeichen in @pos.
- pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen, keine Klammern. `pc@join` steuert den Leerraum im Reader.



**Parzival-Buchgrenzen (#358)**
- `ingest/parzival-buecher/grenzen.csv` (16 Buchanfänge nach Lachmann) ist die Eingabe von `<milestone unit="book">`; ein falscher Wert wandert in den Korpus. Buch VIII beginnt bei 398,1 (PZ_39801_0).
- Buchmarkup: nur der `milestone`; `div type="chapter"` sind Dreißiger. DATA-MODEL.md nennt `milestone unit="chapter"` inline, das Schema erlaubt nur `book` unter div. Leseansicht: „Buch N" wird nur gehoben, wenn der book-milestone `firstElementChild` des div ist.

**WZB:** Eigennamen fehlen im TEI (Lücken sind kein Extraktionsfehler). Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreißen Wörter; seit #390 sind 16 zusammengeführt (Wort unter der xml:id der ersten Hälfte). Breve: 607 Tokens zerlegt (o+U+0306), 26 vorkomponiert (U+014F), also nicht „überall zerlegt". `|` ist normale Interpunktion. `<l>` ohne `@n`. Die xml:id `WZB_<blatt>_<zeile>_<n>` zählt ab 0 über `<w>` **und** `<pc>`, Suffix auch `13b`: ein „Wort n+1" aus der id ist bei Satzzeichen davor falsch.

**WZB-Tafelskripte (`scripts/ingest/wzb/wzb-*.py`, `wzb-corresp-punkt2.py`, #370/#526)**
- `REPO` = `Path(__file__).parents[3]`, lesen `tei/WZB.tei.xml` und `data/authority-index.json.gz` hart. Probe auf Kopie: Scratch mit `scripts/ingest/wzb/`, `tei/`, `data/`, Basis-TEI per `git show origin/main:tei/WZB.tei.xml`. Nicht idempotent (zweiter Lauf bricht am Tafel-Abgleich ab): nur auf der Basiskopie reproduzieren.
- **EOL:** WZB ist die einzige CRLF-Datei in tei/, im Blob selbst (gemischte Zeilenenden). Ein Handedit kann LF-Zeilen auf CRLF kippen, `git diff --stat` zeigt nur eine zu hohe Zeilenzahl. Gegenprobe: `difflib` auf `split(b"\n")` gegen den Basis-Blob, je Zeile `endswith(b"\r")`; erwartet nur Token-Zeilen plus change-Zeile.
- **Alt/neu:** beide Stände per lxml zu `xml:id -> (text, lemmaRef, corresp, pos, ana)`, Mengen vergleichen; Zeilenvergleich nur nach Entfernen der richtigen revisionDesc-Zeile (`#370 Punkt 2` trifft ZWEI change-Zeilen).
- **Begriffshilfe bleibt unberührt**, entgegen „FOLGEN: Begriffshilfe neu bauen" im Docstring der drei #526-Skripte: diese Läufe schreiben kein `w/@ana`.
- **Guard-Grenze (#526):** Regel V prüft nur `treffer > 0`: ein falsches, aber in der WZB belegtes Lemma+pos läuft durch; dort trägt allein die Tafel, also den Vers lesen.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+; im Header nackte IDs, in works.xml URLs.
- **NEIM-Liedkonkordanz steht zweimal** (#453): im Header `editorialDecl/normalization` und je Lied als `<note n="1">` im Body. Ein Header-Fix ohne die Note erzeugt Widerspruch; die Note anzufassen ist ein `<w>`-Wortlaut-Change. Bei Header-Korrekturen immer nach einer Body-Kopie suchen.
- Kombinierende Diakritika sind in Headern verbreitet: vor Vergleichen NFC.


**Trierer Findebuch-Dump (#259, außerhalb des Repos):** DHCraft-Drive `Projekte/mhdbdb/extern/`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5` (kein Namensraum, externe DTD); Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`. **Keine Wortform aus dem Dump in Berichte:** Strukturbefunde über Zählungen und maskierten Text. `<form type="sublemma">` trägt teils ein `<gram>`-Kind, `itertext()` hängt das Kürzel an die Schreibform; `<hi>`-Kinder erzeugen Scheinleerzeichen.
