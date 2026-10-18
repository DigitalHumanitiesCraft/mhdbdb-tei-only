---
name: projekt-header-spiegel
description: TEI-Header als Kopien von works.xml/persons.xml (msIdentifier, biblStruct, particDesc): wer schreibt, wer liest (niemand), sync_tei_headers.py-Fallen, Zotero-Sync, listBibl-Schreiber und -Gate, Zuschreibungsstatus #452
metadata:
  type: project
---
Verdichtet 18.10.2026 (#395, #399, #237, #308, #452, #486).

**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --works`, seit #486 chirurgisch auch für die listBibl; `--bibl-struct` ist der alte lxml-Weg); der Header ist Kopie (entschieden 24.09., CONTRACTS F.4a).
- Reader, API und Playground nehmen biblStructs, hc/GND/wikidata und preferredName aus dem Authority-Index, nie aus dem Header. Reader liest Header-Titel nur bei `biblScope unit=verse`.
- Spiegel ohne Leser: msIdentifier-idno, listBibl/biblStruct, `particDesc/.../persName[@type="preferred"]` (kein Sync-Skript, Namensentscheidungen von Hand nachziehen) und `publicationStmt/authority` (nur `_archived/` und `ingest/ari` schreiben ihn; eine Ergänzung dort ändert data/ und api/ nicht, kein Versions-Bump).

**WZB-Zeilenenden:** WZB ist die einzige CRLF-Datei in tei/, im Blob selbst (`*.xml -text`); vor und nach einer Header-Änderung reine LF-Zeilen mit `(?<!\r)\n` zählen (Gegenprobe: projekt-korpus-tei). PZ ist LF, ein „byte-identisch aus PZ" gilt nur modulo CR.

**sync_tei_headers.py**
- Schlüssel seit #395 (work_id, sigle); vorher gewann je Sigle der letzte Eintrag (TRO).
- Alter lxml-Pfad (`--works --bibl-struct`, `--all`) serialisiert alle 667 Dateien neu, löscht alle mwb-sigle und überschreibt listBibl mit Inhaltsverlust.
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt. Schreibblock vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.


**listBibl-Schreiber (#486, `schreibe_werk_bibliographie`):** `--works` schreibt auch die listBibl, Gate `--works --check` auf Enthaltensein je @corresp.
- Zählfallen: works.xml hat mehr biblStruct mit @corresp als es Header-Blöcke gibt, die Differenz sind WG (keine Korpusdatei) und TRO (zwei Werke, derselbe Schlüssel und dasselbe @corresp); der AK-Block mit Zusatz ist eine eigene Gruppe neben „nur Reihenfolge“.

**listBibl-Gate (#486, seit #605):** Header-Block mit @corresp ohne works-Block ist rot („ohne works.xml-Nachweis"), jeder works-Block mit @corresp braucht einen Header-Block, nur Blöcke ohne @corresp (WZB) bleiben draußen. Vor #605 zählte `_datei_bibliographie` den Header-Block als `ohne` (grün): Prosa, die die Regel einem früheren Vorgang zuschreibt, ist B.
- `ERLAUBTE_ZUSAETZE` prüft freie Kinder gepaarter Container und Kinder eines Header-Containers gegen works-Blatt; blind bleibt die Anzahl (zweiter `note type=context` in AK: grün). Probe: FB ohne Block K2L9LPVV, Container in works.xml leeren.
- Mitlesen: Kommentarkopf in `sync_tei_headers.py`, `scripts/README.md`, CONTRACTS F.4a, Rückgabe-Docstring von `_datei_bibliographie`, Kommentar in `data-integrity.yml`.


**check-author-refs.py:** Die Ausnahme `LEERE_LISTPERSON` war per Sigle geschlüsselt und schaltete die Prüfung für VOR ab; Fix `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusätzlicher Nicht-Autor im particDesc ist gewollt. check-author-refs und check-header-genres lesen nur den Kopf (`corpus_files.tei_header`). particDesc-Zählung: Messvorschrift ist die Zeile „particDesc-Spiegel geprüft N" von `check-author-refs.py`.

**Zuschreibungsstatus #452:** `titleStmt/author` trägt `@ana` (disputed|uncertain|rejected) und `@role="adapter"`; `text.author` = erster zählender. Außerhalb des Diffs: ein verworfener Autor hat keinen particDesc-Eintrag, sein `ref="#person_N"` zeigt ins Leere; `particDesc/person/note[@type="works"]` ist RDF-Altbestand ohne Leser; `text.author` liest auch die Hauptseite (`app.js`). Header-Autorfolge gegen works.xml-attributions prüft kein Gate.
