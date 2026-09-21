---
name: gerade-anfuehrungszeichen-440
description: Review #440 (schraege -> gerade Anfuehrungszeichen im Frontend): Messverfahren, wo ausserhalb des Diffs noch U+201E/U+201C liegen, und welche Stellen die Auftragszahlen verfehlt haben
metadata:
  type: project
---

Runde 1 am 21.09.2026, Arbeitsbaum 41055ea4 auf 573894f12 (HEAD war origin/main^, bd98c4310 fehlte, beruehrt aber keine der 23 Dateien).

**Messverfahren, das getragen hat:** Delta HEAD gegen Arbeitsbaum je Datei per `git show HEAD:<f>` und `count('„')`, dazu difflib-Zeilenpaare mit der Probe `a.replace(„,").replace(“,") == b` (0 andere Aenderungen). Kommentar-gegen-Code-Klassifikation mit eigenem Zeichenscanner (Scratchpad `scan.py`: //, /* */, ', ", Template mit ${}-Stack, Regex-Heuristik ueber letztes signifikantes Zeichen). Kein JS-Parser in node_modules (acorn/espree/esprima fehlen), also bleibt der Scanner der Weg.

**Ergebnis 21.09.:** 106 = 72 HTML (9 Dateien) + 32 JS (13) + 2 Spec; 93 oeffnend, 13 schliessend. Rest: 137 nur in JS-Kommentaren (120 playground/js, 17 assets/js), korpus.css 2 im Kommentar, 10 in Spec-Strings sind ausnahmslos Testnamen (`test('...')`/`describe`), keine Assertions. Keine Entities (&bdquo; usw.), keine „-Escapes, keine Slug-Erzeugung aus Ueberschriftentext, kein CSS `content:`.

**Wo der Auftrag danebenlag:** `ingest/review/359-borek/359-pruefseite.html` traegt 8 Zeichen, nicht 3: 6 aus `vorschlaege.json` plus 2 aus dem seitenspezifischen Generator `scripts/review/build-359-page.py:562` (emittierter HTML-String `'„landen“ statt die Lende'`); `review_page.py` hat 0, das stimmt. Dazu `ingest/pos-disambig/418-houwen/pruefseite.html` 1 Zeichen (Zeile 109), im Auftrag nicht genannt. Beide Pruefseiten sind ausgelieferte Seiten, aber vom Aufrufer als ausserhalb des Geltungsbereichs eingestuft; Scope-Frage, kein Diff-Befund.

**Widerspruch im Bestand:** `docs/playbooks/kickoffs/2026-09-21-kickoff-spur-b-pruefseite.md:92` schreibt einer Spur „schliessende Anfuehrungszeichen U+201C" vor, gegen die Entscheidung vom selben Tag.

**How to apply:** In Folgerunden nur Delta gegen 41055ea4 messen; bei neuen Pruefseiten unter `ingest/` fragen, ob sie im Geltungsbereich sind, bevor Zeichen gezaehlt werden. `assets/js/app.js` ist im Arbeitsbaum w/lf bei i/lf (autocrlf=true), das ist kein Commit-Unterschied.
