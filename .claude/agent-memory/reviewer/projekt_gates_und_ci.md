---
name: projekt-gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, extract-variants, Begriffshilfe-Generator, issue-matrix, Review-Bot, Laufzeitbudget (floor_s-Abfolge), main-Schutz
metadata:
  type: project
---
Verdichtet 14.10. und 15.10.2026. Zahlen vor Gebrauch nachmessen.

**doc-count-audit.py --check**
- Steht in data-integrity.yml VOR allen Datengates (rot = der Rest läuft nicht) und zuletzt in no-cdn-check.yml; `count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`.
- Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`. Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`; ein neuer `type_N` hebt `variants_forms` um 1. Ein Anker bindet nur seine Zeile; Katalogzahlen in Prosa sind ungegatet (seit #451).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* ±50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) lässt fremde Zahlen die Abdeckung erfüllen.
- **Cwd:** cwd-relativ sind `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte (`env -C <wt>`). **Probe-Falle:** „Exit + letzte Zeile aus zwei cwds" ist blind für ein Skript, das aus fremdem cwd null Dateien findet und grün meldet; `grep -c __file__` je Skript lesen.

**data-integrity.yml:** zwei Nummernschemata (Workflow-Kopf 0, 1, 1a..1d gegen DEVELOPMENT.md 1..15, von Hand gespiegelt); bei einer Step-Nummer im Auftrag erst das Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat.
- `check-authority-cross-refs.py`: überspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, wegräumen); die Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` vergleicht keine Alternativformen. `sync_tei_headers.py --works --check`: msIdentifier und seit #486/#605 listBibl (siehe Header-Spiegel). `check-header-genres.py --check`: blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids. `validate-corpus.py --corpus-only --sample SIGLE ...` läuft in Sekunden.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form gegenüber `<base>:data/authority-index.json.gz`, außer `scripts/audit/variants-flips-ack.json` (force-added, das Verzeichnis ist gitignoriert) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` bricht ohne passenden `data/corpus-index.json.gz` ab (fehlt, falsche Version, lemmaIndex < 10.000): Korpus vor Authority.
- `schema/examples/*.xml` validiert nichts: eine Pflichtattribut-Änderung lässt die Beispieldatei still ungültig (Probe mit lxml RelaxNG).
- `check-measured-counts.py` (#414): Allaussagen sind eine Messbedingung, die rot bleibt, bis der Gate-Eintrag geändert wird; Datumsstempel und einzelne Zahlen ungegatet. Probe: `g.normalize` per Lambda umhängen, `g.check(m)` mit `--use-measured`-JSON.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer msIdentifier, listBibl und Gattungen.
- **Syntaxfehler im Textteil:** 7b/7c fangen ihn nicht (iterparse bricht nach `</teiHeader>` ab); fangen tun Step 4, Step 6 (build-corpus-index überspringt die Datei mit Exit 0, der Rebuild-Vergleich wird rot), Step 7.

**extract-variants.py:** „Typ mit >1 Lemma" endet mit return 0, kein Gate. Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, löschen). `--apply` bereinigt auch sense/@ana in lexicon.xml; der Textanker-Abbruch kommt erst NACH dem variants-Write. Jede Umannotierung eines corresp-Tokens ändert `form/@n` in variants.xml, der Freshness-Step wird ohne Regeneration rot.

**Begriffshilfe-Generator (#498)** `scripts/build-begriffshilfe.py` schreibt `assets/downloads/mhdbdb-begriffshilfe.md`, CI-Step „Freshness Begriffshilfe". Liest nur concepts.xml, lexicon.xml (sense/ptr, entry/@xml:id, form/orth; **nicht** sense/@ana) und w/@ana, daher ändert `extract-variants --apply` die Datei nicht. Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die ihn tragen.

**build-issue-matrix.py** (PERSONEN-Marker, „wer ist am Zug" aus dem Thread)
- Proben in-process per importlib mit `GH_REPO=DigitalHumanitiesCraft/mhdbdb-tei-only`; Zustandsproben als ganzer Lebenslauf eines Vorgangs; Mutationen per `exec` einer Quelltextkopie.
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der einen Vorgang unsichtbar macht**; kein Gate zählt, ob jeder wait:*-Vorgang landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage; `@wachauer Abnahme:`; dritte Person, die die Bedingung mittrifft (`wait != 'wait:julia'` trifft Linda); zwei Abnahme-Zeilen in einem Kommentar.
- **Eine Invariante mit Ausnahme gegen den Mutanten „Ausnahme immer nehmen" proben;** bleibt sie grün, ist die Ausnahme ihr ganzer Gegenstand. Die Selbsttest-Invariante deckt nur KZW.
- Der handgepflegte Teil von #44 trägt eigene CRLF, die `--apply` roh lässt (CR/LF in `gh issue view 44 --json body` zählen). Der Selbsttest hat nur einen Einzahl-Fall für „Dazu kommt"; Plural per importlib proben. Der Tabellenkopf `| Person | Abnehmen | … |` steht immer in `p`: Teilstring-Proben darauf sind stumm, auf Zeilen mit Nummer oder per `partition('### Für Julia')` proben.

**Review-Bot (claude-code-review.yml):** Log ohne `show_full_output: true` oder `ACTIONS_STEP_DEBUG=true` nur `init` plus Result. Rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.
- **Dateiliste eines PR:** gh kappt `--json files` bei 100 (in gh.exe: `rg -a -o 'files\(first: ?[0-9]+\)'`), `changedFiles` nicht. Für manche gemergte PRs liefert die Plattform 0 auf allen Feldern. „Diff berechnet“ belegt nur der `<changed_files>`-Block im Job-Log, der selbst bei 100 kappt. Zählen: offen `git diff --name-only origin/main...<branch>`, gemergt `git diff-tree --no-commit-id --name-only -r <squash>`. Alte `--json files`-Stellen in journal-archive und EINZEL-LEMMA sind historisch, kein Befund.

**check-runtime-budget.py (#564)**
- Neues Pflichtfeld in `lade_budget` macht Ablehnungsfälle im Selbsttest still leer, wenn die Basis-`cfg` es nicht trägt: Ablehnungsgrund je Fall ausgeben. `erinnere` fängt `HTTPException` und AttributeError nicht. Gegenprobe zu `--jobs`: `--jobs=1` gegen Vorgabe per `cmp`, `--out`-Dateien per `git hash-object` gegen `git rev-parse HEAD:<pfad>`.
- **Neuer Workflow-Schritt ohne Eintrag in `runtime-budget.json` hat die Grenze 10 s** (floor_s), rot auf PR darüber. Bei jedem PR, der einen Step in einen PR-Workflow einfügt: Eintrag in `steps` suchen und lokal timen (`date +%s.%N`, kein `/usr/bin/time`); eine Laufzeitangabe im Workflow-Kommentar nachmessen.
- **`floor_s` in `grenze()`, datierte Abfolge:** bis 14.10.2026 ersetzte der Floor die Grenze; seit `9f35902e9` (#564) gilt max(Budget × Faktor, floor_s), strikt `budget * faktor < floor_s`, dritter Rückgabewert None = „Budget × Faktor unter floor“ (änderte genau einen der 19 Einträge, 10 → 10,5 s). Messen: alte und neue `grenze()` per importlib über `lade_budget()`. Falle `zeile_text()`: `{g:.0f}` zeigt 10,5 als „10 s“.
- **`--measure` nachmessen:** Wrapper im Scratchpad holt `gh auth token` per `subprocess` und setzt `GH_TOKEN` (keine Command Substitution); 504 der Actions-API: wiederholen. Step-Dauern: `gh api repos/<r>/actions/runs/<id>/jobs --jq '.jobs[].steps[] | select(.name=="Checkout") | [.started_at,.completed_at] | @tsv'`. Volle Checkouts sind bimodal (~120 s oder 215–270 s).
- **Fenster:** `--measure` nimmt per Vorgabe nur die neuesten 25 (`--max-runs`), auch mit `--since`; `messen()` holt eine Seite (`per_page=100`), ein größeres Fenster wird still gekappt. Die Fensterregel (Docstring Z. 56f., DEVELOPMENT.md „Where the numbers come from“) will für E1-Checkouts alle Läufe seit dem Merge: mit `max_runs=100` per importlib gegenprüfen und den Verlauf je Lauf ansehen (no-cdn-Checkout wechselte am 13.10. ohne Repo-Änderung von 11–15 s auf 8–11 s).
- **„Alle Schritte waren langsamer“ je Job messen:** `gh api repos/<r>/actions/runs/<id>/attempts/<n>/jobs` für beide Läufe, Dauern je (Job, Step) paaren; ein Job kann ohne den anderen langsam sein.
- **Wandzeit unter Last ist keine Laufzeitmessung.** Lastunabhängig: CPU-Zeit über `resource.getrusage(RUSAGE_CHILDREN)` um ein `subprocess.run`. Das Gate läuft offline mit `--check --jobs-json <datei> --repo x/y --run-id 1 --attempt 1 --workflow <wf> --job <job> --event pull_request --ref refs/pull/1/merge`; die Datei trägt `{"jobs":[{"name","steps":[{name,status,conclusion,started_at,completed_at}]}]}` mit dem Gate-Step als letztem.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht. `rules/branches/main` und `rulesets/<id>` lesen.
