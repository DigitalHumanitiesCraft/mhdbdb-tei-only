---
name: authority-dateien
description: Authority-Dateien und Authority-Index im Review: concepts-Graph kein Baum, optionale Indexfelder, zwei genre-Felder, Schema an vier Orten, contributors.xml, works-Siglen
metadata:
  type: project
---
Stand 28.09.2026.

**concepts.xml ist kein Baum:** Mehrfacheltern ueber `<ptr type="broader">` und eine Selbstschleife (concept_12050000). Huellen brauchen eine Visited-Menge. Gehoert die Wurzel dazu? „Subtree" meint sie meist mit, „unter X" nicht: beide Lesarten messen und die direkt auf die Wurzel zeigenden Lemmata nennen.

**Authority-Index**
- Optionale Felder (`altDE`, `altEN`, `altNormalized`) stehen nur an Traegern.
- Zwei Felder gleichen Namens: `text.genre` (Korpus-Index, entfernt mit 4.2.22) und `work.genre` (Authority-Index, weg seit #433; heute `work.genres`, `maps.genreToWorks`). Wer „genre" greppt, sieht beide Ketten als eine.
- Gattungsteilbaum aus `genres[].parents` + `maps.genreToWorks`.
- `totalAuthorityFiles = 7` (ui-helpers.js) zaehlt Index-Sammlungen, nicht Dateien.
- Schema steht an vier Orten: DATA-MODEL.md (Schema-Block, XPath-Referenz), TEI-MODEL-AUTH-FILES.md („Index mapping"), CONTRACTS.md §G.3 (normativ). Neues Feld: alle vier greppen.
- api/: `api/lemmata` hat nur index.json; `api/concepts/concept_N.json` ohne Lemmalisten.

**contributors.xml:** build-authority-index liest sie nur in `load_contributor_names()` (direktes Kind persName/orgName je xml:id); `<note>` wird nicht gelesen, `resp_name` endet mit SystemExit bei fremdem Praefix, unbekannter oder leerer ID. contrib_052 traegt eine dritte Kopie der Naming-Zitation (siehe fremdindizes).

**works.xml:** Siglen mit `.//tei:idno[@type="sigle"]` zaehlen wie der Syncer. TRO ist die einzige Doppelsigle (work_69, work_c7da236c). `work_WLK` (#237/#496) hat keinen `biblStruct`, bis der Zotero-Sync ihn nachliefert.
- Werk ohne TEI-Datei ist nicht neu (`WG` work_668, `WLK`); Kontrollwert beim Messen „Siglen ohne Datei". `person-explorer.js` verlinkt `sigles[0]` ungeprueft.
- Werkzahl ungegatet an drei Stellen (TEI-MODEL-AUTH-FILES.md Overview-Tabelle, Kommentar in `build-authority-index.py`, Docstring `sync_tei_headers.py`); die `584` in `mhdbdb-authority.rnc` und `doc-count-audit.py` sind datiert, kein Drift.

**hilfe-daten.html-Groessenliste** = MiB des Git-Blobs, abgeschnitten.
