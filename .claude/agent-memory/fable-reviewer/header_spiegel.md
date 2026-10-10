---
name: header-spiegel
description: TEI-Header als Kopien von works.xml/persons.xml (msIdentifier, biblStruct, particDesc): wer schreibt, wer liest (niemand), sync_tei_headers.py-Fallen, Zotero-Sync, Messwege
metadata:
  type: project
---
Verdichtet 02.10.2026 (#395, #399, #237, #308).

**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --bibl-struct`); der Header ist Kopie (entschieden 24.09.).
- Reader, API und Playground nehmen biblStructs, hc/GND/wikidata und preferredName aus dem Authority-Index, nie aus dem Header. Reader liest Header-Titel nur bei `biblScope unit=verse`.
- Drei Spiegel ohne Leser: msIdentifier-idno, listBibl/biblStruct, `particDesc/.../persName[@type="preferred"]` (Kopie von persons.xml; kein Sync-Skript, Namensentscheidungen von Hand nachziehen).
- Vierter ohne Leser (05.10.2026): `publicationStmt/authority` (`rg publicationStmt|<authority` über scripts/ assets/js playground/js testing/tests; nur `_archived/` und `ingest/ari` schreiben ihn). Eine Ergänzung dort ändert data/ und api/ nicht, kein Versions-Bump.

**WZB-Zeilenenden:** WZB ist die einzige CRLF-Datei in tei/, und zwar im Blob selbst (`*.xml -text` in .gitattributes, autocrlf wirkungslos). Kontrollzahl 17 reine LF-Zeilen (journal-archive:3119); vor und nach einer Header-Änderung mit `(?<!\r)\n` zählen. PZ ist LF, ein „byte-identisch aus PZ" gilt also nur modulo CR.

**sync_tei_headers.py**
- Schlüssel seit #395 (work_id, sigle); vorher gewann je Sigle der letzte Eintrag (TRO).
- Alter lxml-Pfad (`--works --bibl-struct`, `--all`) serialisiert alle 667 Dateien neu, löscht alle mwb-sigle und überschreibt listBibl mit Inhaltsverlust.
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt. Schreibblock vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.
- Lab-Layout für Proben: `scripts/corpus_files.py` + `scripts/sync/` + `tei/<Auswahl>` + `authority-files/works.xml`, cwd = Scratch.

**Zotero-Sync:** `--cache` = online + Cache schreiben, `--offline` liest ihn. Ein Online-Sync hebt Titel an; die Header laufen nicht mit, und die Handkorrekturen FR1/FLG (#236, #104) werden jedes Mal überschrieben.

**Messen:** Header-biblStruct gegen works.xml per @corresp, c14n per lxml, `>\s+<` kollabiert, NFC. MWB-Siglen: `https://www.mhdwb-online.de/quellenverzeichnis.php?buchstabe=N`.

**check-author-refs.py:** Die Ausnahme `LEERE_LISTPERSON` war per Sigle geschlüsselt und schaltete die Prüfung für VOR ab; Fix `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusätzlicher Nicht-Autor im particDesc ist gewollt. Seit `corpus_files.tei_header` lesen check-author-refs und check-header-genres nur den Kopf; classDecl, particDesc, msIdentifier stehen innerhalb des teiHeader.

**Zuschreibungsstatus #452 (09.10.2026):** `titleStmt/author` trägt `@ana` (disputed|uncertain|rejected) und `@role="adapter"`; `text.author` = erster zählender. Folgen außerhalb des Diffs: (1) ein verworfener Autor hat keinen particDesc-Eintrag, sein `ref="#person_N"` zeigt dann ins Leere (TEI-MODEL.md sagte das Gegenteil); (2) `particDesc/person/note[@type="works"]` ist RDF-Altbestand ohne Leser und ohne Sync; (3) `text.author` liest auch die Hauptseite (`app.js` populateTextList/setupTextFiltering). Header-Autorfolge gegen works.xml-attributions prüft kein Gate: per Skript vergleichen. Autor-Suchfelder rückwärts vom Eingabefeld finden: `rg addEventListener\(['"]input` + `setupSearchInput(` + Platzhalter mit "Autor" über assets/js, playground/js, lemma. `authorId`-Filter der SearchEngine hat keinen Aufrufer.

**particDesc-Zählung:** doc-count-audit kennt die Zahl nicht; Messvorschrift: `check-author-refs.py` druckt „particDesc-Spiegel geprüft N". Der Altstand vor #444 steht datiert in CONTRACTS.md und check-author-refs.py (kein Drift).
