---
name: projekt-gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, extract-variants, Begriffshilfe-Generator, issue-matrix, Review-Bot, Laufzeitbudget (floor_s-Abfolge, Nachkalibrierung), main-Schutz
metadata:
  type: project
---
Verdichtet 18.10.2026. Zahlen vor Gebrauch nachmessen.

**doc-count-audit.py --check**
- Steht in data-integrity.yml VOR allen Datengates (rot = der Rest läuft nicht) und zuletzt in no-cdn-check.yml; `count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`.
- Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`. Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`; ein neuer `type_N` hebt `variants_forms` um 1. Ein Anker bindet nur seine Zeile; Katalogzahlen in Prosa sind ungegatet (seit #451).
- **Cwd:** cwd-relativ sind `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte (`env -C <wt>`). Ein Vergleich „Exit + letzte Zeile aus zwei cwds" ist blind für ein Skript, das aus fremdem cwd null Dateien findet und grün meldet; `grep -c __file__` je Skript lesen.

**data-integrity.yml:** zwei Nummernschemata (Workflow-Kopf 0, 1, 1a..1d gegen DEVELOPMENT.md 1..15, von Hand gespiegelt): bei einer Step-Nummer im Auftrag erst das Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs.
- **Freshness-Reihenfolge im zweiten Job:** variants (+lexicon) → API → Begriffshilfe → lemma-pos `--check` → Index-Rebuild-and-Compare, keiner mit `if:`. Ein Satz „X wird vom Rebuild-and-Compare gefangen" stimmt nur, wenn keiner der früheren Schritte schon rot wird; bei fremder annotierter TEI wird meist variants zuerst rot (20.10., Prüfung build:data --allow-dirty). Alle Fehlermeldungen raten „lokal neu bauen", was mit der fremden Datei im Baum dasselbe Ergebnis reproduziert.
- **Zweite Lifecycle-Kopie:** `scripts/README.md` → „Verwendung" hält eine Befehlsfolge „vollständiger Fall, Reihenfolge zählt" samt Gates; DEVELOPMENT.md → Build Commands eine dritte ohne extract-variants. Ein „nur im Lifecycle" dagegen halten. (Zweig claude/doku-pflege-befehlslisten ersetzt beides, Stand 20.10. ungemergt.)
- **Lifecycle hat zwei nummerierte Tabellen** (DATA-MODEL `tei/` 1..12 mit 5b, `authority-files/` 1..7): „Schritt 5" ist dort zweimal belegt (extract-variants bzw. Begriffshilfe). Jeden Verweis „step N" auf die Tabelle prüfen, die er meint.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat.
- `check-authority-cross-refs.py`: überspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, wegräumen); die Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` vergleicht keine Alternativformen. `sync_tei_headers.py --works --check`: msIdentifier und listBibl. `check-header-genres.py --check`: blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids. `validate-corpus.py --corpus-only --sample SIGLE ...` läuft in Sekunden.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form gegenüber `<base>:data/authority-index.json.gz`, außer `scripts/audit/variants-flips-ack.json` (force-added, das Verzeichnis ist gitignoriert) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` bricht ohne passenden `data/corpus-index.json.gz` ab (fehlt, falsche Version, lemmaIndex < 10.000): Korpus vor Authority.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer msIdentifier, listBibl und Gattungen.

**extract-variants.py:** „Typ mit >1 Lemma" endet mit return 0, kein Gate. Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, löschen). `--apply` bereinigt auch sense/@ana in lexicon.xml; der Textanker-Abbruch kommt erst NACH dem variants-Write. Jede Umannotierung eines corresp-Tokens ändert `form/@n` in variants.xml, der Freshness-Step wird ohne Regeneration rot.


**build-issue-matrix.py** (PERSONEN-Marker, „wer ist am Zug" aus dem Thread)
- Proben in-process per importlib mit `GH_REPO=DigitalHumanitiesCraft/mhdbdb-tei-only`; Zustandsproben als ganzer Lebenslauf eines Vorgangs.
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der einen Vorgang unsichtbar macht**; kein Gate zählt, ob jeder wait:*-Vorgang landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage; `@wachauer Abnahme:`; dritte Person, die die Bedingung mittrifft (`wait != 'wait:julia'` trifft Linda); zwei Abnahme-Zeilen in einem Kommentar.
- **Eine Invariante mit Ausnahme gegen den Mutanten „Ausnahme immer nehmen" proben;** bleibt sie grün, ist die Ausnahme ihr ganzer Gegenstand. Die Selbsttest-Invariante deckt nur KZW.

**Review-Bot (claude-code-review.yml):** Log ohne `show_full_output: true` oder `ACTIONS_STEP_DEBUG=true` nur `init` plus Result. Rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`. **Dateiliste eines PR:** Befehle in querschnitt-git. gh kappt `--json files` bei 100, `changedFiles` nicht; „Diff berechnet“ belegt nur der `<changed_files>`-Block im Job-Log, der selbst bei 100 kappt.

**check-runtime-budget.py (#564)**
- **Neuer Workflow-Schritt ohne Eintrag in `runtime-budget.json` hat die Grenze 10 s** (floor_s), rot auf PR darüber. Bei jedem PR, der einen Step in einen PR-Workflow einfügt: Eintrag in `steps` suchen und lokal timen (`date +%s.%N`, kein `/usr/bin/time`); eine Laufzeitangabe im Workflow-Kommentar nachmessen.
- **`floor_s`, datierte Abfolge:** bis 14.10.2026 ersetzte der Floor die Grenze; seither gilt max(Budget × Faktor, floor_s). Falle `zeile_text()`: `{g:.0f}` zeigt 10,5 als „10 s“.
- **Nachkalibrierung (Diff an `runtime-budget.json`):** `laeufe` größer als `n` des Schritts ist erklärbar, nicht übernehmen, sondern je Lauf zeigen. Beispiel 18.10. (`Freshness lemma-pos (#462)`: 22 Läufe, n 21): der fehlende Lauf war ein PR-Lauf eines Zweigs von vor dem Merge des Schritts. Läufe listen über `actions/workflows/<wf>/runs?status=success&created=>=<seit>`, dann je Lauf `actions/runs/<id>/jobs` nach dem Schrittnamen. Die Dauern waren zweigipflig (9–10 s oder 17–18 s), p90 = max.
- **`provisional_since`:** seit der Nachkalibrierung vom 18.10. trägt kein Eintrag mehr eines; `erinnere()` kehrt dann immer nach `faellige_kalibrierung` leer zurück, geprüft ist der Pfad nur noch im Selbsttest. Ein neuer vorläufiger Eintrag weckt ihn: dann prüfen, ob `basis` "vorlaeufig" enthält (Substring, `lade_budget`); `reason` zählt nicht.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht. `rules/branches/main` und `rulesets/<id>` lesen.
