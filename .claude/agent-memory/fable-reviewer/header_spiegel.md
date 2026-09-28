---
name: header-spiegel
description: TEI-Header als Kopien von works.xml/persons.xml (msIdentifier, biblStruct, particDesc): wer schreibt, wer liest (niemand), sync_tei_headers.py-Fallen, Zotero-Online-Sync, Messwege
metadata:
  type: project
---
Stand 28.09.2026 (#395, #399, #237, #308).

**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --bibl-struct`); der Header ist Kopie (entschieden 24.09.).
- Reader, API und Playground nehmen biblStructs, hc/GND/wikidata und preferredName aus dem Authority-Index, nie aus dem Header. Header-idno liest kein Build. Reader liest Header-Titel nur bei `biblScope unit=verse`.
- Drei Spiegel ohne Leser: msIdentifier-idno, listBibl/biblStruct, `particDesc/.../persName[@type="preferred"]` (Kopie von persons.xml; kein Sync-Skript pflegt ihn, Namensentscheidungen von Hand nachziehen).

**sync_tei_headers.py**
- Schluessel seit #395 (work_id, sigle); vorher gewann je Sigle der letzte Eintrag (TRO).
- Alter lxml-Pfad (`--works --bibl-struct`, `--all`) serialisiert alle 667 Dateien neu, loescht alle mwb-sigle und ueberschreibt listBibl mit Inhaltsverlust (nicht nur Reihenfolge).
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt.
- Schreibblock vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.
- Lab-Layout fuer Proben: `scripts/corpus_files.py` + `scripts/sync/` + `tei/<Auswahl>` + `authority-files/works.xml`, cwd = Scratch (TEI_DIR an `__file__`, AUTHORITY_DIR relativ); Mutation mit `assert new != blk`.

**Zotero-Sync**
- `--cache` = online + Cache schreiben, `--offline` liest ihn; Cache `scripts/sync/.zotero_cache.json`.
- Online-Sync nach title_case-Aenderung hebt viele Titel an; die Header laufen nicht mit, und die Handkorrekturen FR1/FLG (#236, #104) werden jedes Mal ueberschrieben.

**Messen:** Header-biblStruct gegen works.xml per @corresp, c14n per lxml, `>\s+<` kollabiert, NFC; ASCII-safe drucken. MWB-Siglen: `https://www.mhdwb-online.de/quellenverzeichnis.php?buchstabe=N`.

**check-author-refs.py:** Ausnahme `LEERE_LISTPERSON` war per Sigle geschluesselt und schaltete die Pruefung fuer VOR ab; Fix `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusaetzlicher Nicht-Autor im particDesc ist gewollt (Figur oder Person im Text).
