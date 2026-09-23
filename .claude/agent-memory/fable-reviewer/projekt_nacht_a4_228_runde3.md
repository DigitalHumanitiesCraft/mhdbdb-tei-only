---
name: nacht-a4-228-runde3
description: Runde 3 zu #228/A4 (24.09.2026): sense/@ana-Prune ist gate- und konsumentenfrei belegt, Messrezepte fuer haengende Typ-Tokens je Revision, MiB-Einheit der hilfe-daten-Liste, doc-count-audit-Luecke
metadata:
  type: project
---

Runde 3 zu #228/A4 (Commits 6a1ec515b, aeafd33dc gegen f13277280), 24.09.2026.

- **sense/@ana hat weder Gate noch Konsument, jetzt an drei Stellen belegt:** `check-authority-cross-refs.py:228-229` ueberspringt Tokens ohne Dateiteil (`#type_N` faellt durch `continue`), `build-authority-index.py:423` liest `ana` nur am `title` des Konzepts, kein Spec und kein Frontend-Modul laedt `lexicon.xml` zur Laufzeit (Specs lesen `data/*.json.gz` per readFileSync; die einzigen Treffer auf `authority-files/` im JS sind Kommentare und ein GitHub-Link in `ui-helpers.js:89`). Ein Prune dort ist deshalb index-, API- und testneutral, ohne Rebuild pruefbar.
- **Haengende Typ-Tokens je Revision messen:** lexicon+variants per `git show rev:pfad` in lxml laden, `split()` ueber sense/@ana gegen die xml:id-Menge von variants; 5 Revisionen in etwa einer Minute. Stand: origin/main = d166fa4b1 = HEAD 105/66, 540733092 188/134, f13277280 187/133; HEAD-Menge exakt die main-Menge.
- **prune-ana-228.py ist ein Einmalskript:** ERWARTET=82 gegen `basis - jetzt`; auf HEAD meldet es 0 und beendet mit FEHLER, schreibt nichts. Anker ist der serialisierte Attributkopf `<sense xml:id=".." ana="..."` mit count==1.
- **Zeilenenden:** lexicon.xml traegt 0 CRLF in allen fuenf Revisionen, LF-Zahl 778.432 seit 540733092 konstant.
- **hilfe-daten.html-Groessenliste ist MiB des Git-Blobs** (persons 57.398 B = 0,05; concepts 217.035 = 0,21; genres 423.625 = 0,4; names 35.320 = 0,03; lexicon 33.305.872 = 31,76; variants 16.352.462 = 15,60). works 1.200.982 B = 1,145, Seite zeigt 1,14 (abgeschnitten, nicht gerundet); alter Text.
- **doc-count-audit.py gatet `lexicon_entries` nicht in DATA-MODEL, DESIGN, FEATURES, TEI-MODEL-AUTH-FILES** (Listen :266-269, :369, :372 nennen nur variants_*/works/contributors/tei_tools/pattern_modules). Die Lemmazahl dort ist Handarbeit; Restvorkommen von 43,878 nur noch in DECISIONS.md:1111 (als v1.9.4-Stand markiert) und JOURNAL.

**Why:** Die Frage #397 („was macht der Fix wahr, woran etwas hing?") war hier mit drei Greps beantwortbar, weil der Konsumentenkreis von sense/@ana leer ist; das spart den Index-Rebuild.
**How to apply:** Bei jedem weiteren Eingriff an sense/@ana oder variants-Typen diese drei Stellen zuerst pruefen, dann die Revisionsmessung fahren, statt zu rebuilden.
