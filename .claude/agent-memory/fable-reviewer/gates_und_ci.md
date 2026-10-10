---
name: gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, extract-variants, Begriffshilfe-Generator, issue-matrix, Review-Bot, main-Schutz
metadata:
  type: project
---
Verdichtet 08. und 10.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**doc-count-audit.py --check**
- Steht in data-integrity.yml VOR allen Datengates (rot = der Rest läuft nicht) und zuletzt in no-cdn-check.yml; zählt mit ElementTree (`count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`, sonst ValueError ohne try/except).
- Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`. Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`. Ein Anker bindet eine Zeile; die Zweitzeile daneben ist ungegatet (CONTRACTS.md:380 gegatet, :381/:382 nicht).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* ±50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) lässt fremde Zahlen die Abdeckung erfüllen. Bei NEAR_KEYWORDS-Diffs alle Zahlen mit Anker über alle DOC_TARGETS listen.
- **Cwd:** doc-count-audit, validate-corpus, check-authority-cross-refs, sync_tei_headers und `build-issue-matrix.py` über `__file__`. Weiter cwd-relativ: `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte. Bei älteren Ständen `env -C <wt>`. **Probe-Falle:** „Exit + letzte Zeile aus zwei cwds" ist blind für ein Skript, das aus fremdem cwd null Dateien findet und grün meldet; `grep -c __file__` je Skript lesen.
- Ein neuer `type_N` hebt `variants_forms` um 1 und `--check` auf Exit 1. Seit #451 zählt das Gate keine Playground-Katalogzahlen mehr; Katalogzahlen in Prosa sind ungegatet. Probe alt gegen neu: altes Skript per `exec` mit `__file__` auf eine `git archive`-Kopie der Doku, `collect_counts` gepatcht.

**data-integrity.yml:** zwei Nummernschemata (Workflow-Kopf 0, 1, 1a..1d, ... gegen DEVELOPMENT.md 1..15, von Hand gespiegelt); Querverweise wandern bei jeder Einfügung mit. Step-Nummer im Auftrag: erst Schema klären. Der `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs.

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-index-version-bump.py` ist inhaltsbasiert (`old == new` OK).
- `check-doc-inventories.py`: nur `testing/tests/*.spec.js` gegen die Spec-Tabelle in DEVELOPMENT.md, dazu lib-README.
- `check-no-em-dash.py --diff-base origin/main` meldet auf einem älteren Branch Zeilen, die main geändert hat; `git diff --stat origin/main...HEAD`.
- `check-authority-cross-refs.py`: überspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, wegräumen). Ratsche feuert nur bei Anstieg.
- `check-author-refs.py`: eine gelöschte preferred-Zeile wird in `ohne_preferred` gesammelt, `--check` rot; Alternativformen werden nicht verglichen. `sync_tei_headers.py --works --check`: nur Inhalt der drei msIdentifier-Typen. `check-header-genres.py --check`: blind für Köpfe ohne Hauptgattung, gelöschte Elternkategorien, doppelte ids. `validate-corpus.py --corpus-only --sample SIGLE ...` läuft in Sekunden.
- `check-variants-flips.py --base <rev>`: rot bei jeder umgeklappten Form gegenüber `git show <base>:data/authority-index.json.gz`, außer `scripts/audit/variants-flips-ack.json` (force-added, `scripts/audit/*.json` ist gitignoriert) nennt genau (from-Version, to-Version, Anzahl).
- `build-authority-index.py` hängt seit 1.9.18 von `data/corpus-index.json.gz` ab (`lemma.noCorpus`): Abbruch bei fehlender Datei, falscher Version oder lemmaIndex < 10.000. Korpus vor Authority.
- `schema/examples/*.xml` validiert nichts: eine Pflichtattribut-Änderung lässt die Beispieldatei still ungültig (Probe mit lxml RelaxNG).
- `check-measured-counts.py` (#414): CLAIMS-Sätze mit Platzhaltern über den normalisierten Dateitext; Zahlengrenze per `exact_pattern`, Diagnose per `loose_pattern`; Allaussagen als Messbedingung, die rot bleibt, bis der Gate-Eintrag geändert wird. Datumsstempel und einzelne Zahlen sind bewusst ungegatet (Liste im Skript). Probe ohne Dateien: `g.normalize` per Lambda umhängen, `g.check(m)` mit `--use-measured`-JSON; frische Messung ~4 min.
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer Gattungen.
- **Syntaxfehler im Textteil:** seit `tei_header` (iterparse bricht nach `</teiHeader>` ab) fangen ihn 7b/7c nicht; fangen tun Step 4 (extract-variants), Step 6 (build-corpus-index überspringt die Datei mit Exit 0, der Rebuild-Vergleich wird rot), Step 7 (cross-refs).
- **Gegenprobe:** `--jobs=1` gegen Vorgabe per `cmp`; `--out`-Dateien per `git hash-object` gegen `git rev-parse HEAD:<pfad>` (`core.autocrlf=true`).

**extract-variants.py:** „Typ mit >1 Lemma“ endet mit return 0, kein Gate. Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, danach löschen; ~1 min). `--apply` bereinigt auch sense/@ana in lexicon.xml; der Textanker-Abbruch kommt erst NACH dem variants-Write. Es schreibt `form/@n`: jede Umannotierung eines corresp-Tokens ändert variants.xml, der Freshness-Step wird ohne Regeneration rot.

**Begriffshilfe-Generator (#498)** `scripts/build-begriffshilfe.py` schreibt `assets/downloads/mhdbdb-begriffshilfe.md`; CI-Step „Freshness Begriffshilfe". Liest nur concepts.xml, lexicon.xml (sense/ptr, entry/@xml:id, form/orth; **nicht** sense/@ana) und w/@ana, daher ändert `extract-variants --apply` die Datei nicht. Gegenprobe: `--out <scratch>`, `git hash-object` gegen `git rev-parse HEAD:<pfad>`. Schreibt LF, bricht bei CR ab; `.gitattributes` setzt `text eol=lf` (querschnitt_git).
- Belegzahl eines Lemmas *unter einem Begriff* summiert nur die Bedeutungen, die ihn tragen (`measure-498-concept-cross-sections.py`, `count_tokens` braucht Minuten).

**build-issue-matrix.py** (PERSONEN-Marker, „wer ist am Zug" aus dem Thread)
- `zeile()` schreibt fremde `area:`/`effort:`-Werte roh in die Zelle; Vokabular dreifach (Konstanten, Docstring, CLAUDE.md), nur AUTO_STUFEN<->ACHSEN per Selbsttest gekoppelt. Vorschau ohne Flag schreibt nichts, `--apply` nie.
- Proben in-process per importlib mit `GH_REPO=DigitalHumanitiesCraft/mhdbdb-tei-only`; Zustandsproben als ganzer Lebenslauf eines Vorgangs (Frage an KZW, ihre Antwort, `@juliahin Abnahme:` mit cc).
- **Der Julia-Vorrang-Skip ist der einzige Pfad, der einen Vorgang unsichtbar macht**; kein Gate zählt, ob jeder wait:*-Vorgang landet. Bei Änderung an einem `continue` vor den Listen proben: offene KZW-Frage; `@wachauer Abnahme:`; dritte Person, die die Bedingung mittrifft (`wait != 'wait:julia'` trifft Linda); zwei Abnahme-Zeilen in einem Kommentar.
- **Eine Invariante mit Ausnahme gegen den Mutanten „Ausnahme immer nehmen“ proben;** bleibt sie grün, ist die Ausnahme ihr ganzer Gegenstand. Die Selbsttest-Invariante deckt nur KZW.

**Review-Bot (claude-code-review.yml):** ohne `show_full_output` zeigt das Log nur `init` und die Result-Zusammenfassung; voll bei `show_full_output: true` oder `ACTIONS_STEP_DEBUG=true`. Muster über rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heißt nicht PR-Pflicht. `rules/branches/main` und `rulesets/<id>` lesen.
