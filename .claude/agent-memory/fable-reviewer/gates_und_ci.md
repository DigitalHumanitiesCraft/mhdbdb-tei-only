---
name: gates-und-ci
description: Was die Gates pruefen und was nicht: doc-count-audit (Anker, Fenster, Luecken), data-integrity.yml, Einzelgates, extract-variants, issue-matrix, main-Schutz
metadata:
  type: project
---
Stand 28.09.2026.

**doc-count-audit.py --check**
- In data-integrity.yml Schritt „Dokumentierte Zahlen gegen die Daten", steht VOR allen Datengates: rot heisst, der Rest laeuft nicht.
- Prueft je Datei nur die Schluessel aus `DOC_TARGETS`; der Umfang kann unvollstaendig sein. Bei geaenderter Zahl: Gate laufen UND `grep -rn` ueber die alte Zahl. Eine Lemma-Loeschung beruehrt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`.
- Anker bindet eine Zeile; die Zweitzeile daneben ist ungegatet (Beispiel CONTRACTS.md:380 gegatet, :381 nicht).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* +-50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) laesst fremde Zahlen die Abdeckung erfuellen. `ANCHOR_SEP` laesst kein Wort dazwischen. Bei NEAR_KEYWORDS-Diffs alle Zahlen mit Anker ueber alle DOC_TARGETS listen, Fenster-Flag daneben.
- silent-obsolet endet mit Exit 0.
- Probe in-process: importlib (vorher `os.chdir`), Kopien im Scratch, `find_stale_numbers(kopie, ist, key)`; alter Anker per Monkeypatch `NEAR_KEYWORDS[key]`; Anker alt/neu per `re.compile(ANCHOR_SEP + CODE_ANCHORS[key])` gegen `git show <rev>:<datei>`.
- Ohne Schluessel (Handarbeit): caesura-Zahl (zwei Kopien in TEI-MODEL.md, §3.1 und §6.5; blieb zweimal stehen; `in \d+ files, see 6.5` greppen), altNames-Zahlen (CONTRACTS, DATA-MODEL, person-explorer.js; messen per `grep -l '"altNames"' api/persons/person_*.json | wc -l`), Reset-Zahlen des Readers.
- `lexicon_entries` ist seit 24.09. auch in DATA-MODEL, DESIGN, FEATURES, TEI-MODEL-AUTH-FILES, CONTRACTS gebunden (doc-count-audit.py:266-281, am 28.09. gelesen); die Luecke, die #228 traf, ist zu.

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

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heisst nicht PR-Pflicht, FF-Push nach main geht durch. `rules/branches/main` und `rulesets/<id>` lesen.
