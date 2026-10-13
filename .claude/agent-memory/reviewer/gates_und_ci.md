---
name: gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, extract-variants, Begriffshilfe-Generator, issue-matrix, Review-Bot, main-Schutz
metadata:
  type: project
---
Verdichtet 13.10.2026. Zahlen vor Gebrauch nachmessen.

**doc-count-audit.py --check**
- Steht in data-integrity.yml VOR allen Datengates (rot = der Rest läuft nicht) und zuletzt in no-cdn-check.yml; `count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`.
- Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`. Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`; ein neuer `type_N` hebt `variants_forms` um 1. Ein Anker bindet nur seine Zeile; Katalogzahlen in Prosa sind ungegatet (seit #451).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* ±50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) lässt fremde Zahlen die Abdeckung erfüllen. Bei NEAR_KEYWORDS-Diffs alle Zahlen mit Anker listen.
- **Cwd:** cwd-relativ sind `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte; ältere Stände mit `env -C <wt>`. **Probe-Falle:** „Exit + letzte Zeile aus zwei cwds“ ist blind für ein Skript, das aus fremdem cwd null Dateien findet und grün meldet; `grep -c __file__` je Skript lesen.

**data-integrity.yml:** zwei Nummernschemata (Workflow-Kopf 0, 1, 1a..1d gegen DEVELOPMENT.md 1..15, von Hand gespiegelt); Step-Nummer im Auftrag: erst Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat.
- `check-authority-cross-refs.py`: überspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, wegräumen); die Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` vergleicht keine Alternativformen. `sync_tei_headers.py --works --check`: nur die drei msIdentifier-Typen. `check-header-genres.py --check`: blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids. `validate-corpus.py --corpus-only --sample SIGLE ...` läuft in Sekunden.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form gegenüber `<base>:data/authority-index.json.gz`, außer `scripts/audit/variants-flips-ack.json` (force-added, das Verzeichnis ist gitignoriert) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` bricht ohne passenden `data/corpus-index.json.gz` ab (fehlt, falsche Version, lemmaIndex < 10.000): Korpus vor Authority.
- `schema/examples/*.xml` validiert nichts: eine Pflichtattribut-Änderung lässt die Beispieldatei still ungültig (Probe mit lxml RelaxNG).
- `check-measured-counts.py` (#414): Allaussagen sind eine Messbedingung, die rot bleibt, bis der Gate-Eintrag geändert wird; Datumsstempel und einzelne Zahlen ungegatet. Probe ohne Dateien: `g.normalize` per Lambda umhängen, `g.check(m)` mit `--use-measured`-JSON.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer Gattungen.
- **Syntaxfehler im Textteil:** 7b/7c fangen ihn nicht (iterparse bricht nach `</teiHeader>` ab); fangen tun Step 4, Step 6 (build-corpus-index überspringt die Datei mit Exit 0, der Rebuild-Vergleich wird rot), Step 7.
- **Gegenprobe:** `--jobs=1` gegen Vorgabe per `cmp`; `--out`-Dateien per `git hash-object` gegen `git rev-parse HEAD:<pfad>`.

**extract-variants.py:** „Typ mit >1 Lemma“ endet mit return 0, kein Gate. Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, löschen). `--apply` bereinigt auch sense/@ana in lexicon.xml; der Textanker-Abbruch kommt erst NACH dem variants-Write. Jede Umannotierung eines corresp-Tokens ändert `form/@n` in variants.xml, der Freshness-Step wird ohne Regeneration rot.

**Begriffshilfe-Generator (#498)** `scripts/build-begriffshilfe.py` schreibt `assets/downloads/mhdbdb-begriffshilfe.md`, CI-Step „Freshness Begriffshilfe“. Liest nur concepts.xml, lexicon.xml (sense/ptr, entry/@xml:id, form/orth; **nicht** sense/@ana) und w/@ana, daher ändert `extract-variants --apply` die Datei nicht. Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die ihn tragen.

**build-issue-matrix.py** (PERSONEN-Marker, „wer ist am Zug“ aus dem Thread)
- Proben in-process per importlib mit `GH_REPO=DigitalHumanitiesCraft/mhdbdb-tei-only`; Zustandsproben als ganzer Lebenslauf eines Vorgangs; Mutationen per `exec` einer Quelltextkopie.
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der einen Vorgang unsichtbar macht**; kein Gate zählt, ob jeder wait:*-Vorgang landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage; `@wachauer Abnahme:`; dritte Person, die die Bedingung mittrifft (`wait != 'wait:julia'` trifft Linda); zwei Abnahme-Zeilen in einem Kommentar.
- **Eine Invariante mit Ausnahme gegen den Mutanten „Ausnahme immer nehmen“ proben;** bleibt sie grün, ist die Ausnahme ihr ganzer Gegenstand. Die Selbsttest-Invariante deckt nur KZW.
- Der handgepflegte Teil von #44 trägt eigene CRLF, die `--apply` (`--body-file`, `newline='\n'`) roh lässt; messen mit `gh issue view 44 --json body` und CR/LF zählen. Der Selbsttest hat nur einen Einzahl-Fall für „Dazu kommt“; Plural per importlib proben (`baue_personen` mit 2 Vorgängen ohne Frage).
- Der Tabellenkopf `| Person | Abnehmen | Entscheiden | …` steht immer in `p`: eine Teilstring-Probe `'| Abnehmen |' in p` ist stumm. Proben auf Zeilen mit Nummer oder per `partition('### Für Julia')`.

**Review-Bot (claude-code-review.yml):** Log ohne `show_full_output: true` oder `ACTIONS_STEP_DEBUG=true` nur `init` plus Result. Rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.

**check-runtime-budget.py (#564)**
- Neues Pflichtfeld in `lade_budget` macht Ablehnungsfälle im Selbsttest still leer, wenn die Basis-`cfg` es nicht trägt: Ablehnungsgrund je Fall per importlib ausgeben. `erinnere` fängt `HTTPException` und AttributeError nicht.
- **Neuer Workflow-Schritt ohne Eintrag in `runtime-budget.json` hat die Grenze 10 s** (floor_s), rot auf PR darüber. Bei jedem PR, der einen Step in einen PR-Workflow einfügt: Eintrag in `steps` suchen und lokal timen (`date +%s.%N`, kein `/usr/bin/time`); eine Laufzeitangabe im Workflow-Kommentar nachmessen.
- **Wandzeit unter Last ist keine Laufzeitmessung.** Lastunabhängig: CPU-Zeit über `resource.getrusage(RUSAGE_CHILDREN)` um ein `subprocess.run`; Richtwert für 4 freie Kerne CPU/4 plus Serienanteil. Das Gate läuft offline: `--check --jobs-json <datei> --repo x/y --run-id 1 --attempt 1 --workflow data-integrity.yml --job freshness --event pull_request --ref refs/pull/1/merge`, Datei `{"jobs":[{"name":"freshness","steps":[{name,status,conclusion,started_at,completed_at}, ...]}]}` mit dem Gate-Step als letztem. Budget 13 bei factor 1,5: 19,4 s grün, 19,6 s rot.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht. `rules/branches/main` und `rulesets/<id>` lesen.
