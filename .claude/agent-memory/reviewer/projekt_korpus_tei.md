---
name: projekt-korpus-tei
description: Strukturtatsachen des TEI-Korpus fürs Review: was der Korpus-Index liest, Token-Ebene, WZB-Eigenheiten und Tafelskripte, Parzival-Buchgrenzen, HUG gegen Hofmeister, Header-Konventionen, monogr-Inhaltsmodell, Trierer Findebuch-Dump
metadata:
  type: project
---
Verdichtet 03.11.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Was `build-corpus-index.py` liest:** nur `w` und `l` plus Header `idno[@type=sigle]`, titleStmt title/author, `msIdentifier/@corresp`, keywords. Nicht: revisionDesc, availability, gap/caesura, particDesc, Header-biblStruct, `@pos`: dort ohne Rebuild und Bump prüfbar. Der Index enthält keine xml:ids.

**Token-Ebene:** `@lemmaRef` ist in tei/ einwertig. Attributreihenfolge an `w`: xml:id lemmaRef pos ana corresp reason. Multi-pos = Leerzeichen in @pos. pc `<`/`>` sind in GWTK, BRF, MR1, GAR Redezeichen. `pc@join` steuert den Leerraum im Reader.

**Parzival (#358):** `ingest/parzival-buecher/grenzen.csv` ist die Eingabe von `<milestone unit="book">`, ein falscher Wert wandert in den Korpus. `div type="chapter"` sind Dreißiger. DATA-MODEL.md nennt `milestone unit="chapter"`, das Schema erlaubt unter div nur `book`. Die Leseansicht hebt „Buch N" nur, wenn der milestone `firstElementChild` des div ist.

**WZB**
- Eigennamen fehlen im TEI. Kolumnentitel und Buchzahlen stehen als unannotierte `<w>` im Fluss und zerreißen Wörter. Breve teils zerlegt, teils vorkomponiert. `|` ist normale Interpunktion.
- **Prosa mit `<l>` als Satzeinheit (ohne `@n`) und `<lb/>` für die Handschriftenzeile**, gegen TEI-MODEL.md („`<l>` is reserved for verse"): Zählungen „in Verszeilen" per Sigle aufschlüsseln. WZB war im Oktober 2026 die einzige Datei mit `<l>` und `<lb>`: `git grep -l -P --all-match -e '<lb[\s/>]' -e '<l[\s>]' <rev> -- tei/`.
- Die xml:id `WZB_<blatt>_<zeile>_<n>` zählt ab 0 über `<w>` **und** `<pc>`, Suffix auch `13b`: „Wort n+1" aus der id ist bei Satzzeichen davor falsch.
- **Einzige CRLF-Datei in tei/, im Blob selbst** (gemischte Zeilenenden). Ein Handedit kann LF-Zeilen kippen, `git diff --stat` zeigt nur eine zu hohe Zeilenzahl. Gegenprobe: `(?<!\r)\n` vor und nach zählen, oder `difflib` auf `split(b"\n")` gegen den Basis-Blob mit `endswith(b"\r")`. „Byte-identisch aus PZ" gilt nur modulo CR.

**WZB-Tafelskripte (`scripts/ingest/wzb/`, #370/#526):** `REPO` = `parents[3]`, lesen `tei/WZB.tei.xml` und `data/authority-index.json.gz` hart. Probe auf einer Scratch-Kopie mit Basis-TEI per `git show origin/main:`, nicht idempotent. Alt gegen neu per lxml als `xml:id -> (text, lemmaRef, corresp, pos, ana)`. Sie schreiben kein `w/@ana` (Begriffshilfe bleibt unberührt, entgegen dem Docstring). Regel V prüft nur `treffer > 0`: ein falsches, aber belegtes Lemma+pos läuft durch.

**Header**
- msIdentifier-Reihenfolge: sigle, handschriftencensus, GND, wikidata, [mwb-sigle], msName+. Im Header nackte IDs, in works.xml URLs. Kombinierende Diakritika sind verbreitet: vor Vergleichen NFC.
- **Header-Angaben können im Body kopiert stehen** (NEIM-Liedkonkordanz in `editorialDecl/normalization` und als `<note n="1">` je Lied, #453). Dort anzufassen ist ein Wortlaut-Change.
- **`<monogr>` ohne jing:** `define name="monogr"` in `schema/tei_all.rng` hat in der optionalen `choice` DREI Alternativen (author/editor zuerst, title/idno zuerst, `authority, idno`). Im title-zuerst-Zweig steht jedes `idno` vor dem ersten author/editor. Kindfolgen per lxml gegen eine Regex aus den drei Zweigen plus Schwanz halten.

**HUG (Hugo von Montfort, #138):** Vorlage Hofmeister 2005, PDF lokal bei Christian (Druckseite = PDF-Seite minus 40), nichts daraus ins Repo zitieren. `l/@n` zählt je `div type="song"` ab 1, deckt sich aber nicht überall mit dem Druck: in Nr. 6 springt die Randzählung des Drucks am Repeticio-Refrain (13. Zeile, die 14. trägt schon Randzahl 15), Nr. 6 „das ich der pender" ist bei uns V. 17, im Druck V. 18 (Randzahl 20 zwei Zeilen tiefer). Nr. 7 und 9 haben auch Repeticio, zählen aber ohne Sprung, Nr. 8 hat keine; Nr. 3 (88 Verse, Str. 4 ab 13) und Nr. 18 (Str. II ab 5) decken sich mit uns (alles gemessen 08.11.2026, PDF 51 bis 54, 73 bis 79, 101; Nr. 26 und 28 nicht). Eine Angabe „im Druck ab V. N" daher an der Randzahl nachzählen, nicht aus einem Lied aufs andere schließen. Strophengrenzen lassen sich am Reimschema (abab) aus dem TEI selbst prüfen, ohne Druck.

**Trierer Findebuch-Dump (#259, außerhalb des Repos):** Ort, Lizenz und Bytezahl in `sources/INVENTAR-ARCHIV.md`, lokal `~/.cache/mhdbdb/woerterbuchnetz2015/FindeB/P5`. **Keine Wortform aus dem Dump in Berichte**, nur Zählungen und maskierter Text. `itertext()` hängt `<gram>`-Kürzel an Sublemmata, `<hi>`-Kinder erzeugen Scheinleerzeichen.
