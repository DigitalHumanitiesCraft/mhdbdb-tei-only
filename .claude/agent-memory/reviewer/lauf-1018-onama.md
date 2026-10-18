---
name: lauf-1018-onama
description: ONAMA-Pilot (#609) im Review: Reproduktion von anker-abgleich.py/build-paket.py, Positionsparität gegen build-corpus-index, Prüfstatus-Definitionen, Spec-Schwächen, Doku-Inventare
metadata:
  type: project
---
Runde 1 am 18.10.2026 auf 6f211c556. Zahlen hier sind Eingabe, vor Gebrauch nachmessen.

**Reproduktion:** TTL per `curl -sL` aus raw.githubusercontent.com (onama-corpus@b87468b) nach `%TEMP%`, beide Skripte mit `env -C <wt> python -X utf8 ...` und `--mhdbdb-commit <basis>` in einen Temp-Ordner fahren, dann `diff`/`cmp` gegen `playground/data/onama/`. Am 18.10. byte-gleich. rdflib läuft ohne `-I`.

**Positionsparität:** Probe per importlib: `lade_tei` (anker-abgleich.py) gegen `extract_word_data` (build-corpus-index.py) je Sigle (Wortzahl) und je Endpunkt `words[wortposition] == erstes lemmaRef`. Am 18.10. 16 Texte gleich, 0 Abweichungen. Das Prädikat unterscheidet sich nur bei einem lemmaRef aus reinen Leerzeichen (0 Fälle).

**Wo die Befunde lagen:** Prüfstatus-Definition an drei Stellen (Paket meta.hinweise, Kopfbanner im Explorer, Hilfe) gegen die Zuordnung in build-paket.py halten. „offen“ umfasst auch Bilder ohne Bildlink, „geprüft“ auch Bilder ohne Textanker, und ein <w> ohne lemmaRef als Endpunkt verschiebt die Spanne, während der Status trotzdem „geprüft“ bleibt. Bei Specs mit „nicht verlinkt“ im Titel nachsehen, ob die Abwesenheit des Links wirklich geprüft wird. Runde 2 (76389aa0d): Statusregel ist eine elif-Kette, die Definitionstexte nennen Bedingungen ohne Vorrang; an überlappenden Fällen messen (Bild ohne Link mit abgeleiteter Zuordnung, umgerechnet plus umgekehrt). Ein Flag, das an `bool(wortspanne)` hängt, fällt bei kollabierter Spanne (None) still auf False: Mutationsprobe im Temp, `wortspanne=None` in einer Abgleich-Kopie setzen und build-paket.py dagegen fahren, ohne das Repo anzufassen.

Runde 3 (98e5c4252): Vorrang offen > abgeleitet > geprueft. Probe in einem Skript: alte elif-Regel auf das committete Paket anwenden und die Wechsel nach (art, zuordnung, bildlink) gruppieren; dazu eine geprueft-Invariante per assert (Sammlung, Text nur wortanker ohne umgerechnet, Bild mit Link). Die Wortspannen-Mutation per JSON-Walk über `uri` setzen, je Status (wortanker, nichtwort_anker) einmal; harter Fehler, kein Paket geschrieben. TTL lag noch in `%TEMP%/rev-onama-dl/`. Basis im Auftrag war der Merge-Base, origin/main war weitergerückt: `git merge-base` und `git merge-tree --write-tree` gegen origin/main fahren.

Runde 4 (d32ca7d88, Gruppierung im Konzept-Einstieg): `nachKonzept` ist direkt (konzepte + nebenhandlungs_konzepte, keine Hülle), also trägt im Konzept-Einstieg jeder Treffer das gewählte Konzept, es gibt immer genau eine Gruppe, und der Fallback-Zweig ist dort unerreichbar. Ob ein Spec-Fall trennt, ohne Mutation an den Daten messen: welche Realisierungen das Konzept tragen und bei welchen es das erste ist (Q460 nur Q456, nirgends erstes).

Neue Playground-Route: Modulbaum und Routentabelle in ARCHITECTURE.md sowie playground/readme.md mitlesen, das Inventar-Gate deckt sie nicht ab.
