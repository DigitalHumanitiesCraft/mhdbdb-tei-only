---
name: projekt-onama
description: ONAMA-Pilot (#609) im Review: Reproduktion von anker-abgleich.py und build-paket.py, Positionsparität, Prüfstatus-Definitionen, Explorer-Badges und Spec-Locatoren, Doku-Inventare
metadata:
  type: project
---
Verdichtet 03.11.2026, mit dem ONAMA-Abschnitt des früheren Frontend-Memorys. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**Paket**
- **Reproduktion:** TTL per `curl -sL` aus raw.githubusercontent.com (onama-corpus, gepinnter Commit) nach Temp, beide Skripte mit `env -C <wt> python -X utf8 ...` und `--mhdbdb-commit <basis>` in einen Temp-Ordner, dann `cmp` gegen `playground/data/onama/`. rdflib läuft ohne `-I`. Paket am Commit: `git show <rev>:playground/data/onama/argonauten.json`.
- **Positionsparität:** per importlib `lade_tei` (anker-abgleich.py) gegen `extract_word_data` (build-corpus-index.py) je Sigle (Wortzahl) und je Endpunkt `words[wortposition] == erstes lemmaRef`.
- **Die Prüfstatus-Definition steht an drei Stellen** (Paket meta.hinweise, Kopfbanner im Explorer, Hilfe) und muss zur Zuordnung in build-paket.py passen. Die Regel ist eine Vorrangkette (offen > abgeleitet > geprueft), die Texte nennen Bedingungen ohne Vorrang: an überlappenden Fällen messen (Bild ohne Link, abgeleitete Zuordnung, umgerechnet). Alte gegen neue Regel aufs committete Paket anwenden, Wechsel nach (art, zuordnung, bildlink) gruppieren. `nichtwort_anker` ist per Definition immer `umgerechnet`.
- **Seit #609-Lesbarkeit (05.11.2026) steht die Statusregel an vier Stellen:** meta.hinweise, Kurzfassung im Banner, aufklappbare `dl` im Kopf (`renderStatusErklaerung`), Hilfe. Wer `meta.lizenz` oder andere Paketfelder ändert, liest `docs/DATA-MODEL.md` „ONAMA pilot package" mit, dort steht „as stored".
- **„Herkunft" ist kein `<details>`** (seit Merge 1b85d4aa2): Auftrag oder Thread, die sie aufklappbar nennen, irren.
- **Umrechnung ist einwärts:** Start rückt auf das nächste gezählte Wort danach, Ende auf das letzte davor (`wortspanne` in anker-abgleich.py). Tooltip am Badge „umgerechnet", Infobox, Hilfe und meta.hinweise.wortspanne sagen seit 57b31c721 alle „einwärts/eingegrenzt"; „innerhalb der Stelle" trägt nur, solange Nichtwort-Endpunkte Blätter sind (`w`, `pc`): ein Container-Ende (`l`, `lg`) schnitte seinen Inhalt ab, weil `vorige` in Dokumentordnung vor dem Container liegt. Ungezählte `w`-Endpunkte tragen bisher kein `lemmaRef` (Gegenprobe per lxml). Aufteilung messen: Passagen in argonauten.json nach (status, umgerechnet) zählen, Endpunkt-Elemente über `uri` in anker-abgleich.json `passagen` nachschlagen.
- **Ein Flag an `bool(wortspanne)` fällt bei kollabierter Spanne (None) still auf False:** Mutation per JSON-Walk über `uri` in einer Kopie, je Status einmal, build-paket.py dagegen fahren.

**Explorer und Specs**
- Realisierungs- und Passagenbadge teilen Text und Klasse (`PRUEF_BADGE.abgeleitet`, `on-badge-warn`), daneben steht bei Bildern ohne Sammlung „Zuordnung abgeleitet" mit derselben Klasse. Ein Locator `.on-badge-warn` mit String-`hasText` über `[data-on-real]` trennt die Ebenen nicht: auf den Kopf (`.on-row` in `renderRealisierung`) einschränken und `hasText: /^abgeleitet$/` nehmen. Passagenzeilen per `hasText: pa.von` sind Teilstring über von und bis: Eindeutigkeit messen.
- Spec-Titel gegen Assertions: steht „nicht verlinkt" im Titel, prüfen, ob die Abwesenheit des Links gemessen wird. Ob ein Spec-Fall trennt, an den Daten messen (welche Realisierungen das Konzept tragen, bei welchen es das erste ist). Im Konzept-Einstieg ist `nachKonzept` direkt, der Fallback-Zweig dort unerreichbar.

**Umfeld**
- Die Basis im Auftrag kann der Merge-Base sein, während origin/main weiterrückt: `git merge-base` und `git merge-tree --write-tree` gegen origin/main.
- Neue Playground-Route: Modulbaum und Routentabelle in ARCHITECTURE.md sowie playground/readme.md mitlesen, das Inventar-Gate deckt sie nicht ab.
