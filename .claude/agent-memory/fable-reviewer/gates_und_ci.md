---
name: gates-und-ci
description: Was die Gates pruefen und was nicht: doc-count-audit (Anker, Fenster, Luecken), data-integrity.yml, Einzelgates, extract-variants, issue-matrix, main-Schutz
metadata:
  type: project
---
Stand 28.09.2026.

**doc-count-audit.py --check**
- In data-integrity.yml Schritt „Dokumentierte Zahlen gegen die Daten", steht VOR allen Datengates: rot heisst, der Rest laeuft nicht. Seit Zweig `claude/doc-count-im-leichten-workflow` (f228b2ca3, Review 01.10.) zusaetzlich als letzter Schritt in no-cdn-check.yml (Filter `**.md`, `**/*.html`, `playground/**`, `scripts/audit/**`); dafuer zaehlt das Skript mit ElementTree statt lxml (`count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`, sonst ValueError ohne try/except in main). Gemessen 01.10.: alle 13 Datenzahlen und 6 Code-Zahlen lxml == ET; `--check` 5,7 s lokal; no-cdn-check-Job 77 bis 201 s ueber 6 Laeufe bei 5 min Timeout (`gh run view <id> --json jobs`, startedAt/completedAt). Vollbericht: `wc -l` 49, nicht-leer (`grep -c .`) 43; wer „43 Zeilen" sagt, zaehlt ohne Leerzeilen.
- Prueft je Datei nur die Schluessel aus `DOC_TARGETS`; der Umfang kann unvollstaendig sein. Bei geaenderter Zahl: Gate laufen UND `grep -rn` ueber die alte Zahl. Eine Lemma-Loeschung beruehrt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`.
- Anker bindet eine Zeile; die Zweitzeile daneben ist ungegatet (Beispiel CONTRACTS.md:380 gegatet, :381 nicht).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* +-50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) laesst fremde Zahlen die Abdeckung erfuellen. `ANCHOR_SEP` laesst kein Wort dazwischen. Bei NEAR_KEYWORDS-Diffs alle Zahlen mit Anker ueber alle DOC_TARGETS listen, Fenster-Flag daneben.
- silent-obsolet endet mit Exit 0.
- Probe in-process: importlib (vorher `os.chdir`), Kopien im Scratch, `find_stale_numbers(kopie, ist, key)`; alter Anker per Monkeypatch `NEAR_KEYWORDS[key]`; Anker alt/neu per `re.compile(ANCHOR_SEP + CODE_ANCHORS[key])` gegen `git show <rev>:<datei>`.
- Ohne Schluessel (Handarbeit): caesura-Zahl (zwei Kopien in TEI-MODEL.md, §3.1 und §6.5; blieb zweimal stehen; `in \d+ files, see 6.5` greppen), altNames-Zahlen (CONTRACTS, DATA-MODEL, person-explorer.js; messen per `grep -l '"altNames"' api/persons/person_*.json | wc -l`), Reset-Zahlen des Readers.
- `lexicon_entries` ist seit 24.09. auch in DATA-MODEL, DESIGN, FEATURES, TEI-MODEL-AUTH-FILES, CONTRACTS gebunden (doc-count-audit.py:266-281, am 28.09. gelesen); die Luecke, die #228 traf, ist zu.
- Ein einziger neuer `type_N` (01.10., #459, Runde 1, Commit 1bb1c51cf) hebt `variants_forms` 256,496 auf 256,497 und `--check` auf Exit 1 bei 9 Treffern: TEI-MODEL.md:944, DATA-MODEL.md:169, TEI-MODEL-AUTH-FILES.md:20/55, CONTRACTS.md:381, schema/README.md:127, index.html:279, hilfe-daten.html:167/184. Der Aufrufer hatte alle anderen Gates laufen lassen, dieses nicht, und `doc-count-audit.py:82` globbt cwd-relativ: aus dem Hauptbaum gestartet zaehlt es dessen variants.xml und ist gruen. Vorbild fuer das Nachziehen ist der jeweils letzte Datencommit (hier d65bcac7b, #506, dieselben 9 Stellen plus Zweitzeile CONTRACTS.md:382 „256,496 is the count of raw forms", die ungegatet ist).
- Neue .js unter `playground/js/ui/tei/` hebt `tei_tools`, `pattern_modules`, `entry_points` zugleich (01.10., #503/#505: 12/13/20 statt 11/12/19, 9 Treffer), bis sie in `NON_TOOL_MODULES` steht. Ungegatet daneben: Dateizahl des tei/-Ordners in ARCHITECTURE.md (Baum ~:205 „15 files" und Prosa ~:231 „fifteen files", Zahlwort ohne Key) und die Ausnahmenliste DESIGN.md ~:161. Altstand des Skripts laeuft aus dem Scratch nur mit `PYTHONPATH=scripts` (mhg_normalizer).

**data-integrity.yml**
- Zwei Nummernschemata: Kopf 0, 1, 1a..1d, 2..6, 6b, 6c, 7, 8; DEVELOPMENT.md zaehlt 1..15 (Stand 08.09.: 1b=3, 1c=4, 1d=5+6, 6=11, 6b=12, 6c=13). Step-Nummer im Auftrag: erst Schema klaeren. DEVELOPMENT.md ist Hand-Spiegel des Kopfs.
- Triggert auf `authority-files/**`; Freshness-Step ohne `if:`.

**Einzelgates**
- `check-index-versions.py` gatet fuenf Dateien, nur vier tragen die Korpusversion. `check-index-version-bump.py` ist inhaltsbasiert (`old == new` OK): Rebuild ohne Diff braucht keinen Bump.
- `check-doc-inventories.py` (Plural): nur `testing/tests/*.spec.js` gegen DEVELOPMENT.md, dazu lib-README.
- `check-no-em-dash.py --diff-base origin/main`: auf einem Branch aelter als main meldet es Zeilen, die main geaendert hat; Gegenprobe: `git diff --stat origin/main...HEAD` nennt die Datei nicht.
- `check-no-cdn.py`: Dateiliste per `g.html_files(g.REPO)`; `LINK_REL` `rel\s*=` ohne Attributgrenze (`data-rel`, `?rel=` im href gelten als exempt).
- `check-authority-cross-refs.py`: ueberspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, trotzdem wegraeumen).
- `check-author-refs.py` (particDesc-Spiegel): geloeschte preferred-Zeile geht still durch (`if not names: continue`), alternative-Formen werden nicht verglichen, Invariante einseitig (titleStmt-Autor in particDesc-@corresp).
- `sync_tei_headers.py --works --check` (Step 1b, <1 s): nur Inhalt der drei msIdentifier-Typen; nicht Reihenfolge, mwb-sigle, biblStruct, Dateien ohne msIdentifier.
- `validate-corpus.py --corpus-only --sample SIGLE ...` in Sekunden; Stage-2 zaehlt (Stage-1 hat Baseline). Seit Zweig `claude/validate-parallel` (5bbe4d785, Runde 1 am 01.10.) ProcessPoolExecutor mit Initializer, `--jobs` (default_jobs); voll 675 Dateien lokal 64 s mit 8 Workern (641/34/0), CI-Step vorher 439 s (Lauf 36835505859, Job 810 s). Worker laufen dem geordneten Verbraucher voraus: bei `--fail-fast` mit Fehler an Position 390 (MNB) waren 460/675 schon gestartet, 215 gecancelt, und OVG/PL1/PL2 (Pos. 434/442/443, je ~30 s, Peak 899 MB RSS je Prozess) in Arbeit, deshalb 70 s statt Ersparnis. tei_all.rng kompiliert 5,6 s / 117 MB je Prozess. Exit 2 bei kaputtem Schema faellt im Elternprozess vor dem Pool. Spawn-Pfad laeuft auch ohne `-X utf8`.
- `check-header-genres.py --check` (Zweig `claude/495-kopfgattungen`, Runde 1 am 01.10.): Invariante Haupt <= Werk <= Haupt+Eltern ueber ids; cwd-unabhaengig (Path(__file__)). Blind: Kopf ohne Hauptgattung, dessen Werkgattung nur als `ana="parent"` steht (HNI, HZU, HZU2, alle genre_782dcfc4), geloeschte Elternkategorie ausserhalb der Werkgattungen (28 von 667 Koepfen tragen Eltern, die kein broader-Ziel einer Hauptgattung in genres.xml sind; 639 sind es direkt), Gloss-Text gegen genres.xml-term, doppelte ids. Werke ohne Gattung: 0. Einziger Leser des classDecl: tei-text-reader.js:383 im `if (!metadata.workId)`-Rueckfall, alle category inkl. parent. Kein Build-Skript liest classDecl (rg ueber scripts/ ohne _archived: nur ingest/ari-Konverter).
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml ausser Gattungen (seit #495).
- Syntaxfehler im Textteil (Zweig `claude/perf-parse`, 82e64d9ad, Runde 1 am 01.10.): 7b/7c fangen ihn seit `tei_header` nicht mehr (iterparse bricht nach `</teiHeader>` ab, an Kopie gemessen). Unbedingt fangen ihn davor Step 4 (extract-variants, `etree.parse` je Datei), Step 6 (build-corpus-index faengt die Exception, ueberspringt die Datei mit Exit 0, der Rebuild-Vergleich wird rot) und Step 7 (cross-refs, Exception im Worker), danach Step 8. Lokal bleibt build-corpus-index bei kaputter Datei gruen: nur die Warnzeile zeigt es.
- Parallel-Gegenprobe fuer cross-refs und Begriffshilfe: `--jobs=1` und Vorgabe nacheinander, JSON/`--out` per `cmp`; am 01.10. beide byte-identisch, Konsole nur in der Worker-Zeile verschieden. `--out`-Datei gegen den Baum erst nach `tr -d '\r'` vergleichen: der Worktree hat `core.autocrlf=true`, die committete Begriffshilfe liegt dort mit 646 CR, das Skript schreibt LF.
- `env -C <worktree> rg` findet kein `rg` (nicht im PATH des Bash-Werkzeugs); Zaehlungen ueber tei/ als Python-Skript im Scratch.

**extract-variants.py**
- Meldung „Typ mit >1 Lemma" endet mit return 0: kein Gate.
- Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert): danach als Einzeiler loeschen. Laufzeit ~1 min.
- `--apply` bereinigt seit c0cf3e1df auch sense/@ana in lexicon.xml; Aufrufer data-integrity.yml (Frische-Schritt + Diff-Gate) und `npm run build:data`. Der Textanker-Abbruch kommt erst NACH dem variants-Write.
- Gate-Probe: `git show origin/main:authority-files/lexicon.xml > authority-files/lexicon.xml`, `--check`, dann `git checkout -- authority-files/lexicon.xml`.

**build-issue-matrix.py**
- Tageslauf ist `--apply` (issue-matrix.yml), `--check` ist der Vorflug.
- `zeile()` schreibt fremde `area:`/`effort:`-Werte roh in die Zelle; „faellt aus jeder Tabelle" gilt nur fuer `auto:`.
- Vokabular dreifach (Konstanten, Docstring, CLAUDE.md); nur AUTO_STUFEN<->ACHSEN per Selbsttest gekoppelt. Legende in #44 ist handgeschrieben. Labelzahl aus `gh label list`.
- Selbsttest-Mutationen: Skript ins Scratch, `str.replace` mit `count == 1`, `--selftest`, FAIL zaehlen.

**Review-Bot (claude-code-review.yml, claude-code-action@v1)**, gemessen 30.09.2026
- Ohne `show_full_output` zeigt das Log nur `init` und eine Result-Zusammenfassung (subtype, is_error, duration_ms, num_turns, total_cost_usd, permission_denials_count, modelUsage-Limits); der `result`-Text mit der Fehlermeldung und alle assistant/tool-Nachrichten fallen weg (`base-action/src/run-claude-sdk.ts` sanitizeSdkOutput, v1-Tag b9d5c3b). Voll wird es bei `show_full_output: true` ODER `ACTIONS_STEP_DEBUG=true` im Env (`parse-sdk-options.ts:195-196`); ob ein Debug-Rerun die Variable exportiert, ist nicht gemessen.
- `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs, nicht die von main: PR #500 fuegte in data-integrity.yml den Schritt „Freshness Begriffshilfe (#498)" ein, und Lauf 36596062765 auf dem PR hatte ihn als Schritt 17. `gh run view <id> --json jobs` ist die Messung.
- Tokens im Log: `secrets.*` maskiert GitHub selbst, das OIDC-App-Token maskiert die Action per `core.setSecret` (`src/github/token.ts:181`), SDK-Optionen werden ohne `env` geloggt. Nicht maskierbar ist, was ein Tool-Ergebnis sonst enthaelt.
- Roter Bot seit 28.09.2026 09:33Z: acht Laeufe in Folge `is_error: true`, 1 Turn, 0 USD, 1,8 bis 2,1 s; letzter gruener 24.09. (15 Turns, 0,54 USD). Muster ueber alle roten Laeufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heisst nicht PR-Pflicht, FF-Push nach main geht durch. `rules/branches/main` und `rulesets/<id>` lesen.
