---
name: projekt-header-spiegel
description: TEI-Header als Kopien von works.xml und persons.xml, ihre Sync-Skripte und Gates
metadata:
  type: project
---
**Kette und Leser**
- Zotero -> works.xml (`enhance_works_with_zotero.py`) -> Header (`sync_tei_headers.py --works`, chirurgisch auch für die listBibl, `--bibl-struct` ist der alte lxml-Weg). Der Header ist Kopie (CONTRACTS F.4a).
- Reader, API und Playground nehmen biblStructs, Normdaten und preferredName aus dem Authority-Index, nie aus dem Header (Reader-Titel nur bei `biblScope unit=verse`). Spiegel ohne Leser: msIdentifier-idno, listBibl, `particDesc/.../persName[@type="preferred"]` (kein Sync-Skript, von Hand nachziehen), `publicationStmt/authority`.
- Ausnahmen von Zotero stehen in `enhance_works_with_zotero.py` (`SIGLE_ZU_ZOTERO_SCHLUESSEL`, `BESTAND_BEHALTEN`) und werden an drei Stellen aufgezählt: Modul-Docstring, Kommentar über `BESTAND_BEHALTEN`, CONTRACTS F.4a „Two named exceptions". Wächst die Menge, die Aufzählungen nachzählen. Die Kommentare sind umbrochen: Grep über ein Fenster, nicht eine Zeile.
- Die `note` eines biblStruct kommt aus der Zotero-Kindnotiz (`notes_map`), prüfbar per `curl https://api.zotero.org/groups/5043625/items/<KEY>/children?format=json` (öffentlich). Hält `BESTAND_BEHALTEN` die note fest, erreicht eine Zotero-Korrektur das Werk nicht mehr.
- Sync-Probe ohne Schreiben: Modul per `runpy.run_path`, `replace_editions_with_biblstructs(dry_run=False)` am geparsten Baum, `etree.tostring(..., xml_declaration=True, pretty_print=True)` gegen die Dateibytes.
- `enhance_works_with_zotero.py` und `sync_tei_headers.py` fassen `<author>` nur im biblStruct an, nie Werk- oder titleStmt-Autoren.

**sync_tei_headers.py**
- Schlüssel ist (work_id, sigle) seit #395. Der alte lxml-Pfad (`--bibl-struct`, `--all`) serialisiert alle Korpusdateien neu, löscht alle mwb-sigle und überschreibt listBibl mit Inhaltsverlust.
- Regex-Schreiber: idno mit Zusatzattribut oder auf der sigle-Zeile wird dupliziert statt entfernt. Der Schreibblock steht vor dem Stub-Guard: schreibt erst, endet dann mit Exit 1.

**listBibl-Gate (`--works --check`, #486/#605):** Enthaltensein je @corresp in beide Richtungen, nur Blöcke ohne @corresp (WZB) bleiben draußen. Vor #605 war ein Header-Block ohne works-Block grün: Prosa, die die Regel einem früheren Issue zuschreibt, ist B. works.xml hat mehr biblStruct mit @corresp als Header-Blöcke (WG ohne Korpusdatei, TRO mit zwei Werken). `ERLAUBTE_ZUSAETZE` ist blind für die Anzahl. Die Regel steht auch in (Kommentarkopf `sync_tei_headers.py`, `scripts/README.md`, CONTRACTS F.4a, `_datei_bibliographie`, `data-integrity.yml`).

**check-author-refs.py:** eine Ausnahme per Sigle (`LEERE_LISTPERSON`) schaltete die Prüfung für VOR ab, richtig ist `sigle in LEERE_LISTPERSON and not corresp_ids`. Ein zusätzlicher Nicht-Autor im particDesc ist gewollt. Liest wie check-header-genres nur den Kopf. Messvorschrift ist die Zeile „particDesc-Spiegel geprüft N".

**Gattungen an Altständen (#495):** works.xml trug Werkgattungen bis #32 (2026-04-10) als `<ref target="genres.xml#...">` je Sprache, danach als `<ptr>`: eine Messung an älteren Commits, die nur `ptr` liest, findet null. `check-header-genres.py` hat seit #495 leere `AUSNAHMEN`, die Klasse `veraltet` ist ohne Gegenstand. Prosa darüber steht in `data-integrity.yml` und DEVELOPMENT.md.

**Zuschreibungsstatus (#452):** `titleStmt/author` trägt `@ana` (disputed|uncertain|rejected) und `@role="adapter"`, `text.author` = erster zählender (auch `app.js` liest ihn). Ein verworfener Autor hat keinen particDesc-Eintrag, sein `ref` zeigt ins Leere. `particDesc/person/note[@type="works"]` ist Altbestand ohne Leser. Header-Autorfolge gegen works.xml prüft kein Gate. Ein zusätzlicher zählender Autor lässt den Korpusindex byte-gleich, nur Authority-Index und API bewegen sich: Rebuild aller drei im Scratch-Clone plus `check-index-version-bump.py --base <sha>`.
