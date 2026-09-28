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
- Fremdindizes: naming `source.license`, horses `source.licence`.

**contributors.xml:** build-authority-index liest sie nur in `load_contributor_names()` (direktes Kind persName/orgName je xml:id); `<note>` wird nicht gelesen, `resp_name` endet mit SystemExit bei fremdem Praefix, unbekannter oder leerer ID. contrib_052 traegt eine dritte Kopie der Naming-Zitation (siehe naming_420).

**works.xml:** Siglen mit `findall` zaehlen. TRO ist die einzige Doppelsigle (work_69 Konrad, work_c7da236c Fortsetzung); 70 von 584 Werken fuehren mehrere Siglen (07.09.).

**hilfe-daten.html-Groessenliste** = MiB des Git-Blobs, abgeschnitten statt gerundet.
