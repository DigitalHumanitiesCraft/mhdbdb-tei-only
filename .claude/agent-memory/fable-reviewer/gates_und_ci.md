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
- `validate-corpus.py --corpus-only --sample SIGLE ...` in Sekunden; Stage-2 zaehlt (Stage-1 hat Baseline). RelaxNG ueber ~100 Dateien ~2 min im Hintergrund.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml.

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
