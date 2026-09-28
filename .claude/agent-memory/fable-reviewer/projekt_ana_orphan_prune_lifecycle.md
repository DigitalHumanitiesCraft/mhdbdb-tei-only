---
name: ana-orphan-prune-lifecycle
description: Review von c0cf3e1df (claude/ana-orphan-prune, 24.09.2026): extract-variants.py --apply bereinigt sense/@ana in lexicon.xml; Messrezepte fuer Orphans, Anker-Simulation per importlib, Gate-Mutationsprobe, Aufrufer von --apply
metadata:
  type: project
---

Review von c0cf3e1df gegen origin/main 2e495ff05, Runde 1, 24.09.2026. Folge von [[nacht-a4-228-runde2]].

- **Zahlen auf main (gemessen, alle bestaetigt):** 105 verwaiste Tokens in 66 Senses, 43 Typen; 0 Treffer der 43 Typen irgendwo im Korpustext (Kontrollwert type_25866 trifft 19 von 200 Dateien); lexicon.xml 62.202 senses, 43.243 mit @ana (unveraendert, keine Liste faellt ganz weg); variants.xml 256.512 xml:ids, alle `type_`.
- **Anker-Simulation statt Diff-Lesen:** `prune_lexicon_ana` per importlib laden, `mod.LEXICON` auf eine Scratch-Kopie von `git show origin/main:authority-files/lexicon.xml` biegen, mit den variants-IDs aufrufen, Bytes gegen HEAD vergleichen: identisch. Das ersetzt das Pruefen von 132 Diffzeilen.
- **Alle 43.243 sense-Starttags mit @ana sind kanonisch** (`<sense xml:id=".." ana="..">`, einfache Leerzeichen, doppelte Anfuehrungszeichen, kein Attribut danach). Der Textanker in `prune_lexicon_ana` haengt daran; bei Abweichung bricht er mit Exit 1 ab, aber erst NACH `tree.write(variants.xml)` (main(): write Z. 373, prune Z. 374).
- **Aufrufer von `extract-variants.py --apply`, die jetzt lexicon.xml mitschreiben:** data-integrity.yml:400 (Frische-Schritt, dann Diff-Gate auf beide Dateien) und package.json:21 (`npm run build:data`). Ingest-Skripte nennen es nur in Docstrings/Hinweisen (apply-366-375-371.py:365 print). DEVELOPMENT.md:264 ist der Hand-Spiegel des Workflow-Kopfs und wurde nicht mitgezogen.
- **Laufproben im Worktree:** `env -C <worktree> python -X utf8 scripts/...` laeuft (Skripte sind cwd-relativ). `--apply` auf HEAD: 0/0 pruned, Status leer. Gate-Probe: `git show origin/main:authority-files/lexicon.xml > authority-files/lexicon.xml`, `--check`, dann `git checkout -- authority-files/lexicon.xml`; das Gate schreibt scripts/audit/authority-cross-refs-audit.json (gitignoriert per .gitignore:91, trotzdem wegraeumen).
- **Schreiber von lexicon.xml nach Korpusaenderung ausserhalb des Lifecycle:** apply-228.py:220-224 (loescht Eintraege), backfill-lexicon.py:212 (schreibt Stubs). „the one place where a tei/ change can alter lexicon.xml" (DATA-MODEL:893) gilt nur fuer die vier Lifecycle-Skripte.
