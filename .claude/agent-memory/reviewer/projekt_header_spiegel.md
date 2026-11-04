---
name: projekt-header-spiegel
description: TEI-Header als Kopien von works.xml und persons.xml: wer schreibt, wer liest (niemand), sync_tei_headers.py-Fallen, listBibl-Gate, check-author-refs, Zuschreibungsstatus
metadata:
  type: project
---
Verdichtet 03.11.2026.

**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --works`, chirurgisch auch für die listBibl, `--bibl-struct` ist der alte lxml-Weg). Der Header ist Kopie (CONTRACTS F.4a).
- Reader, API und Playground nehmen biblStructs, Normdaten und preferredName aus dem Authority-Index, nie aus dem Header (Reader-Titel nur bei `biblScope unit=verse`). Spiegel ohne Leser: msIdentifier-idno, listBibl, `particDesc/.../persName[@type="preferred"]` (kein Sync-Skript, von Hand nachziehen), `publicationStmt/authority` (ändert data/ und api/ nicht).
- Ausnahmen von Zotero stehen in `enhance_works_with_zotero.py` (`SIGLE_ZU_ZOTERO_SCHLUESSEL`, `BESTAND_BEHALTEN`, seit #486/04.11. mit FLG1) und werden an drei Stellen aufgezählt: Modul-Docstring (Z. 21ff.), Kommentar über `BESTAND_BEHALTEN`, CONTRACTS F.4a „Two named exceptions". Wächst die Menge, die Aufzählungen nachzählen. Kommentare dort sind umbrochen: `rg "Buch 1-7"` fand „Buch\n# 1-7" nicht.
- Die `note` eines biblStruct kommt aus der Zotero-Kindnotiz des Items (`notes_map`); „kommt nicht aus Zotero" an einer `note` prüfen per `curl https://api.zotero.org/groups/5043625/items/<KEY>/children?format=json` (öffentlich). Hält `BESTAND_BEHALTEN` die note fest, erreicht eine Zotero-Korrektur das Werk nicht mehr (ATWPNQPS seit 04.11. für FLG und FLG1).
- Sync-Probe ohne Schreiben: Modul per `runpy.run_path`, `fetch_zotero_data_from_api` → `extract_zotero_data` → `replace_editions_with_biblstructs(dry_run=False)` am geparsten Baum, `etree.tostring(..., xml_declaration=True, pretty_print=True)` gegen die Dateibytes (04.11. byte-gleich, Länge 1203068).
- WZB ist CRLF: Zeilenenden vor und nach einer Header-Änderung zählen (projekt-korpus-tei).

**sync_tei_headers.py**
- Schlüssel ist (work_id, sigle) seit #395. Der alte lxml-Pfad (`--bibl-struct`, `--all`) serialisiert alle Korpusdateien neu, löscht alle mwb-sigle und überschreibt listBibl mit Inhaltsverlust.
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt. Der Schreibblock steht vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.

**listBibl-Gate (`--works --check`, #486/#605):** Enthaltensein je @corresp in beide Richtungen, nur Blöcke ohne @corresp (WZB) bleiben draußen. Vor #605 war ein Header-Block ohne works-Block grün: Prosa, die die Regel einem früheren Vorgang zuschreibt, ist B. works.xml hat mehr biblStruct mit @corresp als Header-Blöcke (WG ohne Korpusdatei, TRO mit zwei Werken). `ERLAUBTE_ZUSAETZE` ist blind für die Anzahl (ein zweiter `note type=context` bleibt grün). Mitlesen: Kommentarkopf in `sync_tei_headers.py`, `scripts/README.md`, CONTRACTS F.4a, Docstring von `_datei_bibliographie`, Kommentar in `data-integrity.yml`.

**check-author-refs.py:** eine Ausnahme per Sigle (`LEERE_LISTPERSON`) schaltete die Prüfung für VOR ab, richtig ist `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusätzlicher Nicht-Autor im particDesc ist gewollt. Es liest wie check-header-genres nur den Kopf. Messvorschrift ist die Zeile „particDesc-Spiegel geprüft N".

**Gattungen an Altständen (#495):** works.xml trug Werkgattungen bis 90e5cc604 (#32, 2026-04-10) als `<ref target="genres.xml#...">` je Sprache, erst danach als `<ptr>`; eine Messung an älteren Commits, die nur `ptr` liest, findet null Gattungen. Die Header-Zeiger der FD-Sigel zogen erst in 20243d284 (#71) auf work_6, nicht im Split-Commit. `check-header-genres.py` hat seit #495 leere `AUSNAHMEN`, die Klasse `veraltet` ist damit ohne Gegenstand; Prosa über die Ausnahme steht in `data-integrity.yml` und DEVELOPMENT.md Punkt 17.

**Zuschreibungsstatus (#452):** `titleStmt/author` trägt `@ana` (disputed|uncertain|rejected) und `@role="adapter"`, `text.author` = erster zählender (auch `app.js` liest ihn). Ein verworfener Autor hat keinen particDesc-Eintrag, sein `ref` zeigt ins Leere. `particDesc/person/note[@type="works"]` ist Altbestand ohne Leser. Header-Autorfolge gegen works.xml prüft kein Gate.
