---
name: projekt-header-spiegel
description: TEI-Header als Kopien von works.xml/persons.xml (msIdentifier, biblStruct, particDesc): wer schreibt, wer liest (niemand), sync_tei_headers.py-Fallen, Zotero-Sync, Zuschreibungsstatus #452
metadata:
  type: project
---
Verdichtet 14.10.2026 (#395, #399, #237, #308, #452).

**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --works`, seit #486 chirurgisch auch für die listBibl; `--bibl-struct` ist der alte lxml-Weg); der Header ist Kopie (entschieden 24.09., CONTRACTS F.4a).
- Reader, API und Playground nehmen biblStructs, hc/GND/wikidata und preferredName aus dem Authority-Index, nie aus dem Header. Reader liest Header-Titel nur bei `biblScope unit=verse`.
- Spiegel ohne Leser: msIdentifier-idno, listBibl/biblStruct, `particDesc/.../persName[@type="preferred"]` (Kopie von persons.xml; kein Sync-Skript, Namensentscheidungen von Hand nachziehen) und `publicationStmt/authority` (`rg publicationStmt|<authority` über scripts/ assets/js playground/js testing/tests; nur `_archived/` und `ingest/ari` schreiben ihn; eine Ergänzung dort ändert data/ und api/ nicht, kein Versions-Bump).

**WZB-Zeilenenden:** WZB ist die einzige CRLF-Datei in tei/, im Blob selbst (`*.xml -text`, autocrlf wirkungslos); vor und nach einer Header-Änderung reine LF-Zeilen mit `(?<!\r)\n` zählen (projekt_526_breve_makron). PZ ist LF, ein „byte-identisch aus PZ" gilt nur modulo CR.

**sync_tei_headers.py**
- Schlüssel seit #395 (work_id, sigle); vorher gewann je Sigle der letzte Eintrag (TRO).
- Alter lxml-Pfad (`--works --bibl-struct`, `--all`) serialisiert alle 667 Dateien neu, löscht alle mwb-sigle und überschreibt listBibl mit Inhaltsverlust.
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt. Schreibblock vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.

**Zotero-Sync:** `--cache` = online + Cache schreiben, `--offline` liest ihn. Bis #486 liefen die Header nicht mit und die Handkorrekturen FR3/FLG wurden jedes Mal überschrieben; seit dem Zweig `claude/486-listbibl-kette` (14.10.) hält `BESTAND_BEHALTEN` in `enhance_works_with_zotero.py` FLG (Schlüssel ATWPNQPS) und FR3 (bis MVWV5QYG in Zotero korrigiert ist). Die Handkorrektur aus #236 steht in FR3, nicht FR1.

**listBibl-Schreiber (#486, `schreibe_werk_bibliographie`):** `--works` schreibt seit dem Zweig auch die listBibl, Gate `--works --check` auf Enthaltensein je @corresp. Probe ohne Dateischreiben: Modul importieren, Block per `_header_text`/`LISTBIBL`/`BIBL_BLOCK` holen, String mutieren, `_scan`/`_edits` laufen lassen und Edits selbst anwenden (Skript war in `%TEMP%/rev486_probe*.py`, Konsole braucht `PYTHONIOENCODING=utf-8`). Gemessen 14.10.: ein selbstschließendes Blatt im Header (`<forename/>` in MSB1 und NEI) ist nicht ersetzbar, der Schreiber bricht mit ValueError ab; ein fehlendes Element mit Kindern auf biblStruct-Ebene wird mit der ganzen Kind-Einrückung als Einheit eingerückt (16 Leerzeichen je Stufe), eine Stufe tiefer korrekt. Zählfallen: works.xml 680 biblStruct mit @corresp gegen 678 Header-Blöcke, die Differenz sind WG (kein tei/WG.tei.xml) und TRO (zwei Werke, derselbe Schlüssel und dasselbe @corresp); meine Reihenfolgezählung ergab 120, davon 1 AK (Zusatzelemente), also 119 wie behauptet.

**Messen:** Header-biblStruct gegen works.xml per @corresp, c14n per lxml, `>\s+<` kollabiert, NFC. MWB-Siglen: `https://www.mhdwb-online.de/quellenverzeichnis.php?buchstabe=N`.

**check-author-refs.py:** Die Ausnahme `LEERE_LISTPERSON` war per Sigle geschlüsselt und schaltete die Prüfung für VOR ab; Fix `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusätzlicher Nicht-Autor im particDesc ist gewollt. check-author-refs und check-header-genres lesen seit `corpus_files.tei_header` nur den Kopf; classDecl, particDesc, msIdentifier stehen innerhalb des teiHeader. particDesc-Zählung: doc-count-audit kennt die Zahl nicht; Messvorschrift: `check-author-refs.py` druckt „particDesc-Spiegel geprüft N".

**Zuschreibungsstatus #452:** `titleStmt/author` trägt `@ana` (disputed|uncertain|rejected) und `@role="adapter"`; `text.author` = erster zählender. Folgen außerhalb des Diffs: ein verworfener Autor hat keinen particDesc-Eintrag, sein `ref="#person_N"` zeigt ins Leere; `particDesc/person/note[@type="works"]` ist RDF-Altbestand ohne Leser und Sync; `text.author` liest auch die Hauptseite (`app.js`). Header-Autorfolge gegen works.xml-attributions prüft kein Gate. Autor-Suchfelder rückwärts vom Eingabefeld finden (`rg addEventListener\(['"]input`, `setupSearchInput(`).
