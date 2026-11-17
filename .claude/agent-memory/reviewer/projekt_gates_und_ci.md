---
name: projekt-gates-und-ci
description: Was die Gates und CI-Workflows prüfen und was nicht
metadata:
  type: project
---
**`doc-count-audit.py --check`**
- Läuft in data-integrity.yml früh (nach `check-index-versions.py`), in no-cdn-check.yml als letzter Schritt. Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`, `count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`. Ein Anker bindet nur seine Zeile, Katalogzahlen in Prosa sind ungegatet (#451).
- Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl (auch `hilfe-*.html`). Eine Lemma-Löschung berührt `lexicon_entries` und `variants_*`, ein neuer `type_N` hebt `variants_forms`, ein neues Lemma ebenso. Basis ohne Worktree: `git archive origin/main -- . ':!data' ':!api' ':!sources' | tar -x -C <scratch>`, dort `--check`.
- **Wer den gegateten Nenner nachzieht, lässt den ungegateten Zähler daneben stehen** (#216: Homographenzahl in `hilfe-playground.html`). Zeilen des Nachzugs nach einer zweiten Zahl absuchen und sie nach ihrer Zählregel nachfahren. Das Gate meldet auch datierte Sätze, nur Vor-Marker wie „time of the audit" und nachgestelltes „not today's" schirmen ab.
- Cwd-relativ sind `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte: im Worktree mit `env -C <wt>` starten, sonst messen sie still den Main Worktree. Ein Skript, das aus fremdem cwd null Dateien findet, meldet grün: `grep -c __file__` je Skript.

**data-integrity.yml und Lifecycle**
- Zwei Nummernschemata (Workflow-Kopf gegen DEVELOPMENT.md): bei einer Step-Nummer erst das Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des Merge-Refs.
- Freshness-Reihenfolge im zweiten Job: variants (+lexicon), API, Begriffshilfe, lemma-pos, Rebuild-and-Compare, keiner mit `if:`. „X fängt der Rebuild-and-Compare" stimmt nur, wenn kein früherer Schritt rot wird.
- Der Lifecycle hat zwei nummerierte Tabellen (DATA-MODEL `tei/` 1..12 mit 5b, `authority-files/` 1..7), „Schritt 5" ist zweimal belegt. Befehlsfolgen stehen außerdem in `docs/DEVELOPMENT.md` → Build Commands und in `npm run build:data`: ein „nur im Lifecycle" gegen alle halten.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion.
- `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat. `REPO` hängt am Skriptpfad: auf einem Sparse-Worktree ohne `scripts/` per `importlib` laden, `mod.REPO = Path(<worktree>)`, `mod.main()`.
- `check-authority-cross-refs.py` überspringt `#type_N`, scannt nur tei/, `--check` schreibt das gitignorierte `scripts/audit/authority-cross-refs-audit.json` (wegräumen), die Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` vergleicht keine Alternativformen. `check-header-genres.py` ist blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form, außer `scripts/audit/variants-flips-ack.json` (force-added) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` bricht ohne passenden `data/corpus-index.json.gz` ab: Korpus vor Authority.
- **„Index byte-frisch?"** in Minuten: `git clone --no-hardlinks --no-checkout` ins Scratchpad, `checkout <id>`, dann `build-authority-index.py`, `build-api.py`, `build-begriffshilfe.py`. Leeres `git status` = frisch (alle drei deterministisch, gzip mtime=0). Kein Build liest `revisionDesc`: ein `<change>` braucht keinen Rebuild.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer msIdentifier, listBibl und Gattungen.

**validate-corpus.py und die tei_all-Baseline**
- `--corpus-only`, `--authority-only` und `--sample` überspringen den NEW/GONE-Abgleich gegen `KNOWN_TEI_ALL_BASELINE` (`is_full_run`): nur der volle Lauf belegt die Menge. NEW ist rot, GONE ein Hinweis. Eine Datei mit erstem `@reason` an `<w>` braucht den Baseline-Eintrag.
- Die Baselinezahl steht auch deutsch (`schema/README.md`, `hilfe-daten-beitragen.html`), neben TEI-MODEL.md §10 und DECISIONS.md: `git grep -n -E "\b<alt>\b" -- '*.md' '*.html' schema/`.

**extract-variants.py:** „Typ mit >1 Lemma" endet mit return 0, kein Gate. Ohne `--apply` (auch bei `--help`) schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, löschen). `--apply` bereinigt auch sense/@ana, der Textanker-Abbruch kommt erst NACH dem variants-Write. Die Zähler des Dry Runs sehen nur `<w>` mit `@lemmaRef` UND `@corresp`: alle 0 entscheidet nur Schritt 5 der Routing-Tabelle (DATA-MODEL.md), nicht die anderen.

**build-issue-matrix.py**
- Proben in-process per importlib mit gesetztem `GH_REPO`.
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der ein Issue unsichtbar macht**, kein Gate zählt, ob jedes wait:*-Issue landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage, `@wachauer Abnahme:`, dritte Person (`wait != 'wait:julia'` trifft Linda), zwei Abnahme-Zeilen in einem Kommentar.
- Label-Vokabular lebt außerhalb des Repos weiter: Handteil des #44-Body, `gh label list`, Auto-Memory `project_label_schema.md`. Im Repo nur `AUTO_STUFEN` und CLAUDE.md, andere Treffer sind datiert.
- Rot heißt nicht „Ball liegt" (auch Label-Lücken): `gh run view <id> --log-failed | grep "##\[error\]"`. Die Startzeit weicht stundenweit vom Cron ab: über `createdAt` messen.

**Review-Bot:** Log ohne `show_full_output: true` nur `init` plus Result. Rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.

**check-runtime-budget.py (#564)**
- Neuer Workflow-Schritt ohne Eintrag in `runtime-budget.json` hat die Grenze `floor_s`: Eintrag suchen und lokal timen. Datierte Abfolge: bis 14.10.2026 ersetzte der Floor die Grenze, seither max(Budget × Faktor, floor_s).
- Nachkalibrierung: Grundmenge gegen `docs/DEVELOPMENT.md` „Where the numbers come from" halten (p90 der erfolgreichen Läufe, abgebrochene nie). Läufe ohne `status=`-Filter holen, `run.conclusion` und `job.conclusion` mitdrucken.
- `erinnere()` erkennt vorläufige Einträge am Substring "vorlaeufig" in `basis`, nicht an `reason`.

**Workflow-Semantik, lokal probbar**
- Default-Shell ohne `shell:` ist `bash -e` ohne pipefail: `skript | tail` verschluckt jeden Exit. Probe `bash -e -c "... | tail -n 1"; echo $?`.
- `X=$(cmd)` bricht unter `bash -e` ab, wenn cmd scheitert. Ein Gate-Job davor lässt `needs`-Jobs ohne `always()` überspringen, ein Meldeschritt darin läuft nie.
- Zustandsmelder je Endzustand: welcher spätere Lauf hebt dieses Rot auf, und ist das Grün wahr (tragfähig ist der letzte *abgeschlossene* Lauf mit gleicher SHA und success)?
- `workflow_dispatch` läuft hier praktisch nur auf Branches: ein Meldeweg „auf main" braucht die `github.ref`-Bedingung, `runs?branch=main` schließt Branch-Dispatches aus. Ein `pull_request`-Lauf prüft den Merge-Commit, `workflow_dispatch` den Branch-Kopf.
- Liest ein Seitengenerator eine neue Eingabedatei (#417: `build-publikationen.py` → `contributors.xml`), die `paths:` von `no-cdn-check.yml` dagegen halten: data-integrity.yml läuft auf `authority-files/**`, fährt aber keine Seiten-`--check`. Bei jeder neuen Spec oder jedem Audit-Skript `python scripts/audit/check-doc-inventories.py` (rot ohne Zeile in `docs/DEVELOPMENT.md`), ein grüner `npm test` deckt das nicht.

**Playwright in der CI:** nur `nightly-tests.yml` fährt `npm test` (Gegenprobe `rg -l "playwright|npm test|run-tests" .github/workflows`), Trigger `schedule` und `workflow_dispatch`. Ein PR-Push prüft keinen Spec, ein CI-only-Fehler ist vor dem Merge nur per Dispatch auf dem Branch belegbar.

**Runner-Image:** `ubuntu-latest` wechselte zwischen dem 15. und 16.11.2026 von 24.04 auf 26.04 (`gh run view <id> --log | grep "Image: "`). Ein Datum „seit" aus dem ersten Lauf mit neuem Image ableiten, nicht aus dem ersten roten. `scripts/audit/search-budget.json` ist auf 24.04 gemessen, `search-benchmark.yml` läuft auf `ubuntu-latest`.

**Link-Check-Allowlist (#653):** „URL-Eintrag geht vor" heißt nur Vorrang bei passendem Status, ein anderer Status fällt auf den Domain-Eintrag durch. Proben mit `allowlist_treffer(url, s, lade_allowlist_datei())` je Status, nach einem Fix die Formel über die ganze Allowlist greppen, auch im `_comment`.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht.
