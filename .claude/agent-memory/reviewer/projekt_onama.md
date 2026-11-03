---
name: projekt-onama
description: ONAMA-Pilot (#609) im Review: Reproduktion von anker-abgleich.py/build-paket.py, Positionsparität gegen build-corpus-index, Prüfstatus-Definitionen, Spec-Schwächen, Doku-Inventare
metadata:
  type: project
---
Verdichtet 03.11.2026 aus vier Runden (18.10.). Zahlen sind Eingabe, vor Gebrauch nachmessen.

- **Reproduktion:** TTL per `curl -sL` aus raw.githubusercontent.com (onama-corpus, gepinnter Commit) nach `%TEMP%`, beide Skripte mit `env -C <wt> python -X utf8 ...` und `--mhdbdb-commit <basis>` in einen Temp-Ordner, dann `cmp` gegen `playground/data/onama/`. rdflib läuft ohne `-I`.
- **Positionsparität:** per importlib `lade_tei` (anker-abgleich.py) gegen `extract_word_data` (build-corpus-index.py) je Sigle (Wortzahl) und je Endpunkt `words[wortposition] == erstes lemmaRef`.
- **Prüfstatus-Definition steht an drei Stellen** (Paket meta.hinweise, Kopfbanner im Explorer, Hilfe) und muss zur Zuordnung in build-paket.py passen. Die Regel ist eine Vorrangkette (offen > abgeleitet > geprueft), die Texte nennen Bedingungen ohne Vorrang: an überlappenden Fällen messen (Bild ohne Link, abgeleitete Zuordnung, umgerechnet). Alte gegen neue Regel auf das committete Paket anwenden, Wechsel nach (art, zuordnung, bildlink) gruppieren.
- **Ein Flag an `bool(wortspanne)` fällt bei kollabierter Spanne (None) still auf False:** Mutation per JSON-Walk über `uri` in einer Kopie, je Status einmal, build-paket.py dagegen fahren.
- **Spec-Titel gegen Assertions:** bei „nicht verlinkt" im Titel prüfen, ob die Abwesenheit des Links gemessen wird. Ob ein Spec-Fall trennt, an den Daten messen (welche Realisierungen das Konzept tragen, bei welchen es das erste ist); im Konzept-Einstieg ist `nachKonzept` direkt, der Fallback-Zweig dort unerreichbar.
- **Basis im Auftrag kann der Merge-Base sein**, während origin/main weiterrückt: `git merge-base` und `git merge-tree --write-tree` gegen origin/main.
- **Neue Playground-Route:** Modulbaum und Routentabelle in ARCHITECTURE.md sowie playground/readme.md mitlesen, das Inventar-Gate deckt sie nicht ab.
