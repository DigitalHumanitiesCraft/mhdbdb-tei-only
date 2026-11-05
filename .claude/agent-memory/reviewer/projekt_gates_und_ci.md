---
name: projekt-gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, tei_all-Baseline, extract-variants, issue-matrix, Review-Bot, Laufzeitbudget, Workflow-Semantik, main-Schutz
metadata:
  type: project
---
Verdichtet 03.11.2026, mit dem früheren Memory zur tei_all-Baseline. Zahlen vor Gebrauch nachmessen.

**`doc-count-audit.py --check`**
- In data-integrity.yml früh (nach `check-index-versions.py`, vor den Datengates), in no-cdn-check.yml als letzter Schritt. Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`, `count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`. Ein Anker bindet nur seine Zeile, Katalogzahlen in Prosa sind ungegatet (#451).
- Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries` und `variants_*`, ein neuer `type_N` hebt `variants_forms`.
- **Cwd-relativ** sind `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte (`env -C <wt>`). „Exit plus letzte Zeile aus zwei cwds" ist blind für ein Skript, das aus fremdem cwd null Dateien findet und grün meldet: `grep -c __file__` je Skript.

**data-integrity.yml und Lifecycle**
- Zwei Nummernschemata (Workflow-Kopf 0, 1, 1a..1d gegen DEVELOPMENT.md 1..15): bei einer Step-Nummer erst das Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des Merge-Refs.
- Freshness-Reihenfolge im zweiten Job: variants (+lexicon), API, Begriffshilfe, lemma-pos, Rebuild-and-Compare, keiner mit `if:`. „X fängt der Rebuild-and-Compare" stimmt nur, wenn kein früherer Schritt rot wird (bei fremder annotierter TEI meist variants).
- Der Lifecycle hat zwei nummerierte Tabellen (DATA-MODEL `tei/` 1..12 mit 5b, `authority-files/` 1..7), „Schritt 5" ist zweimal belegt. Befehlsfolgen stehen außerdem in `docs/DEVELOPMENT.md` → Build Commands und in `npm run build:data` (Stand 03.11.2026, `scripts/README.md` verweist nur noch): ein „nur im Lifecycle" gegen alle halten.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat.
- `check-authority-cross-refs.py` überspringt `#type_N`, scannt nur tei/, `--check` schreibt das gitignorierte `scripts/audit/authority-cross-refs-audit.json` (wegräumen), die Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` vergleicht keine Alternativformen. `check-header-genres.py` ist blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form, außer `scripts/audit/variants-flips-ack.json` (force-added) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` bricht ohne passenden `data/corpus-index.json.gz` ab: Korpus vor Authority.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer msIdentifier, listBibl und Gattungen.

**validate-corpus.py und die tei_all-Baseline**
- `--corpus-only`, `--authority-only` und `--sample` überspringen den NEW/GONE-Abgleich gegen `KNOWN_TEI_ALL_BASELINE` (`is_full_run`): nur der volle Lauf belegt die Menge, nicht nur die Zahl. Seit 03.11.2026 ist NEW rot, GONE ein Hinweis. Eine Datei mit erstem `@reason` an `<w>` braucht den Baseline-Eintrag.
- **Die Baselinezahl steht auch deutsch** (`schema/README.md`, `hilfe-daten-beitragen.html`), neben TEI-MODEL.md §10 und DECISIONS.md. Ein Grep nach englischen Phrasen verfehlt beide: `git grep -n -E "\b<alt>\b" -- '*.md' '*.html' schema/`.

**extract-variants.py:** „Typ mit >1 Lemma" endet mit return 0, kein Gate. Ohne `--apply` (auch bei `--help`) schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, löschen). `--apply` bereinigt auch sense/@ana in lexicon.xml, der Textanker-Abbruch kommt erst NACH dem variants-Write. Jede Umannotierung eines corresp-Tokens ändert `form/@n`.

**build-issue-matrix.py**
- Proben in-process per importlib mit `GH_REPO=DigitalHumanitiesCraft/mhdbdb-tei-only`, als ganzer Lebenslauf eines Vorgangs.
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der einen Vorgang unsichtbar macht**, kein Gate zählt, ob jeder wait:*-Vorgang landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage, `@wachauer Abnahme:`, dritte Person (`wait != 'wait:julia'` trifft Linda), zwei Abnahme-Zeilen in einem Kommentar. Eine Invariante mit Ausnahme gegen den Mutanten „Ausnahme immer nehmen" proben.
- **Eine Änderung am Label-Vokabular hat lebende Stellen außerhalb des Repos**, die das Skript nicht schreibt: der Handteil des #44-Body außerhalb der Marker (Legende, Arbeitsregeln), die Beschreibungen in `gh label list`, das Auto-Memory `project_label_schema.md`. Im Repo selbst lebt das Vokabular nur in `AUTO_STUFEN` und CLAUDE.md; Treffer in MASTERPLAN §1/§3–§6, `kickoffs/`, ROADMAP und `journal-archive.md` sind datiert (Runde zu auto-zwei-stufen, 04.11.2026).
- Rot heißt nicht „Ball liegt" (auch Label-Lücken): `gh run view <id> --log-failed | grep "##\[error\]"`. Die Startzeit weicht stundenweit vom Cron ab: über `createdAt` messen.

**Review-Bot:** Log ohne `show_full_output: true` nur `init` plus Result. Rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`. „Diff berechnet" belegt nur der `<changed_files>`-Block im Job-Log.

**check-runtime-budget.py (#564)**
- Neuer Workflow-Schritt ohne Eintrag in `runtime-budget.json` hat die Grenze `floor_s` (10 s): Eintrag suchen und lokal timen (`date +%s.%N`). Datierte Abfolge: bis 14.10.2026 ersetzte der Floor die Grenze, seither max(Budget × Faktor, floor_s). `zeile_text()` zeigt 10,5 als „10 s".
- Nachkalibrierung und Anhebung: Grundmenge gegen `docs/DEVELOPMENT.md` „Where the numbers come from" halten (p90 der erfolgreichen Läufe, abgebrochene nie). Läufe ohne `status=`-Filter holen, `run.conclusion` und `job.conclusion` mitdrucken, Statistik je Teilmenge. `laeufe` > `n` ist erklärbar (PR-Lauf von vor dem Merge des Schritts): je Lauf zeigen.
- `provisional_since`: ohne vorläufigen Eintrag kehrt `erinnere()` immer leer zurück. Kommt einer dazu, prüfen, ob `basis` "vorlaeufig" enthält (Substring), `reason` zählt nicht.

**Workflow-Semantik, lokal probbar**
- Default-Shell ohne `shell:` ist `bash -e` ohne pipefail: `skript | tail` verschluckt jeden Exit. Probe `bash -e -c "... | tail -n 1"; echo $?` auf einer Scratch-Kopie.
- `X=$(cmd)` bricht unter `bash -e` ab, wenn cmd scheitert. Ein Gate-Job davor lässt `needs`-Jobs ohne `always()` überspringen, ein Meldeschritt darin läuft nie.
- Zustandsmelder je Endzustand: welcher spätere Lauf hebt dieses Rot auf, und ist das Grün wahr (tragfähig ist der letzte *abgeschlossene* Lauf mit gleicher SHA und success, nicht der letzte erfolgreiche)?
- `workflow_dispatch` läuft hier praktisch nur auf Zweigen: ein Meldeweg „auf main" braucht die `github.ref`-Bedingung, `runs?branch=main` schließt Zweig-Dispatches aus.

**Playwright in der CI (05.11.2026):** nur `nightly-tests.yml` fährt `npm test` (Gegenprobe `rg -l "playwright|npm test|run-tests" .github/workflows`), Trigger `schedule` und `workflow_dispatch`. Ein PR-Push prüft also keinen Spec; ein CI-only-Fehler ist vor dem Merge nur per Dispatch auf dem Zweig belegbar (Concurrency je Ref, `melden` nur auf main). Linux-Runner rendert höher als Windows: aufgeklappter wîn-Kommentar lokal 1319 px bis Knopfunterkante, im Trace des Laufs 42002409117 rund 15 % mehr (abgeleitet über die Zentrierung von `DOM.scrollIntoViewIfNeeded`).

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht.
