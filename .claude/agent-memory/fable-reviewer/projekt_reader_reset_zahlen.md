---
name: reader-reset-zahlen
description: Reader-Reset-Zahlen (count-verse-numbering-resets.py) auf altem Stand messen, Regel abschalten, Dreifachkopie in tei-text-reader.js; Issue-Zugriff ohne gh per curl; lexicon etym-Zahlen; #239-Abnahme (08.09.2026)
metadata:
  type: project
---

**Alten Stand messen:** `git archive <sha> tei scripts | tar -x -C scratch` und `count-verse-numbering-resets.py` dort laufen lassen; Regel abschalten per sed auf `in_nested_parallel` (return False). NICHT im Archivordner bleiben, wenn der Heute-Lauf folgt (sonst zweimal alt).

Stand 08.09.2026: 1.959/138 Texte, 1.818/50, WH +466 (467 chapter, alle seit #358); ohne Regel section 137 statt 156 und FR3 +117. Vor-#358-Stand (f50612a05^) = 6.789/2.661/1.492 in 137/1.352 in 49, Listen-Diff genau WH +466. Dieselben Zahlen stehen dreimal in `tei-text-reader.js` (:437, :461ff, :566ff) und in FEATURES.md:85.

**Issues ohne gh:** `curl -H "Authorization: Bearer $GITHUB_TOKEN" api.github.com/...` gibt 200, WebFetch auf dieselbe URL 403.

lexicon.xml hat 27.168 `etym[@type="morphological"]`, davon 2 leer (lemma_933, lemma_23628), Index-etymology 27.166, Explorer-Sperrmenge 16.713 stimmt. #239-Abnahme des Scan-Absatzes: wachauer 2026-09-08 14:37 woertlich.

**Why:** Die Reset-Zahlen stehen an vier Stellen und werden nur per Skriptlauf pruefbar.
**How to apply:** Bei jedem Diff an den Reset-Regeln alt/neu per git archive messen, alle vier Kopien mitlesen.
