---
name: gates-und-ci
description: Was die Gates prüfen und was nicht: doc-count-audit, data-integrity.yml, Einzelgates, extract-variants, issue-matrix, Review-Bot, main-Schutz
metadata:
  type: project
---
Verdichtet 02.10.2026. Zahlen sind Eingabe, vor Gebrauch nachmessen.

**doc-count-audit.py --check**
- Steht in data-integrity.yml VOR allen Datengates (rot = der Rest läuft nicht) und seit Zweig `doc-count-im-leichten-workflow` zusätzlich als letzter Schritt in no-cdn-check.yml; dafür zählt es mit ElementTree statt lxml (`count_xml_elements` erlaubt nur `//tei:<tag>[@xml:id|@corresp]`, sonst ValueError ohne try/except). Messen: `gh run view <id> --json jobs`; der Job hat 5 min Timeout.
- Prüft je Datei nur die Schlüssel aus `DOC_TARGETS`. Bei geänderter Zahl: Gate laufen UND `grep -rn` über die alte Zahl. Eine Lemma-Löschung berührt `lexicon_entries`, `variants_forms`, `variants_entries`, `variants_normalized`.
- Ein Anker bindet eine Zeile; die Zweitzeile daneben ist ungegatet (CONTRACTS.md:380 gegatet, :381/:382 nicht).
- `find_stale_numbers` hat ein Drift-Fenster (2 %, variants_* ±50 %), `anchor_binds_number` keins: jede blanke Alternative (`entries`, `records`) lässt fremde Zahlen die Abdeckung erfüllen. `ANCHOR_SEP` lässt kein Wort dazwischen. Bei NEAR_KEYWORDS-Diffs alle Zahlen mit Anker über alle DOC_TARGETS listen.
- Probe in-process: `find_stale_numbers(kopie, ist, key)`, alter Anker per Monkeypatch `NEAR_KEYWORDS[key]`; Altstand aus dem Scratch nur mit `PYTHONPATH=scripts`.
- **Cwd-Falle, seit Zweig `claude/scripts-repo-root` (05.10.2026, fehlerjournal 104) für die vier CI-Gates behoben:** doc-count-audit (`os.chdir` am Anfang von main), validate-corpus, check-authority-cross-refs, sync_tei_headers lesen über `__file__`. Gemessen aus leerem Fremd-cwd: alle vier gleich wie aus dem Baum. `build-issue-matrix.py` (ROADMAP-Lesung) seit Runde 2 desselben Zweigs ebenfalls (`REPO / ROADMAP`, Sparse-Checkout in issue-matrix.yml legt beides unter dieselbe Wurzel); außerhalb CI u. a. `enhance_works_with_zotero.py`, `find-mentions.py`, die archivierten apply-Skripte. Bei älteren Ständen weiter `env -C <wt>`.
- **Probe-Falle:** eine Vergleichsprobe „Exit + letzte Zeile aus zwei cwds" ist blind für ein Skript, das aus dem fremden cwd null Dateien findet und trotzdem grün meldet; dazu `grep -c __file__` je Skript lesen.
- Ohne Schlüssel (Handarbeit): caesura-Zahl (zwei Kopien in TEI-MODEL.md, `in \d+ files, see 6.5` greppen), altNames-Zahlen (CONTRACTS, DATA-MODEL, person-explorer.js; `grep -l '"altNames"' api/persons/person_*.json | wc -l`), Reset-Zahlen des Readers, Dateizahl des tei/-Ordners in ARCHITECTURE.md (Zahlwort „fifteen files").
- Ein einziger neuer `type_N` hebt `variants_forms` um 1 und `--check` auf Exit 1 (9 Stellen in TEI-MODEL, DATA-MODEL, TEI-MODEL-AUTH-FILES, CONTRACTS, schema/README, index.html, hilfe-daten.html). Vorbild fürs Nachziehen: der letzte Datencommit.
- Neue .js unter `playground/js/ui/tei/` hebt `tei_tools`, `pattern_modules`, `entry_points` zugleich, bis sie in `NON_TOOL_MODULES` steht.

**data-integrity.yml**
- Zwei Nummernschemata: Workflow-Kopf (0, 1, 1a..1d, 2..6, 6b, 6c, 7, 8, 5b) gegen DEVELOPMENT.md (1..15, von Hand gespiegelt). Step-Nummer im Auftrag: erst klären, welches Schema. In DEVELOPMENT.md hängt zudem der Satz „for checks 4 and 14" an der Nummerierung und wandert bei jeder Einfügung davor mit.
- Der `pull_request`-Lauf nimmt die Workflow-Datei des PR-Merge-Refs, nicht die von main (`gh run view <id> --json jobs`).

**Einzelgates**
- `check-index-versions.py` gatet fünf Dateien, nur vier tragen die Korpusversion. `check-index-version-bump.py` ist inhaltsbasiert (`old == new` OK).
- `check-doc-inventories.py`: nur `testing/tests/*.spec.js` gegen DEVELOPMENT.md, dazu lib-README.
- `check-no-em-dash.py --diff-base origin/main` meldet auf einem Branch älter als main Zeilen, die main geändert hat; Gegenprobe `git diff --stat origin/main...HEAD`.
- `check-authority-cross-refs.py`: überspringt Tokens ohne Dateiteil (`#type_N`), scannt nur tei/; `--check` schreibt `scripts/audit/authority-cross-refs-audit.json` (gitignoriert, trotzdem wegräumen). Ratsche feuert nur bei Anstieg.
- `check-author-refs.py` (particDesc-Spiegel): gelöschte preferred-Zeile geht still durch (`if not names: continue`), Alternativformen nicht verglichen, Invariante einseitig.
- `sync_tei_headers.py --works --check`: nur Inhalt der drei msIdentifier-Typen, nicht Reihenfolge, mwb-sigle, biblStruct.
- `validate-corpus.py --corpus-only --sample SIGLE ...` in Sekunden. Parallel (`--jobs`): Worker laufen dem geordneten Verbraucher voraus, bei `--fail-fast` sind trotzdem viele Dateien gestartet (keine Ersparnis); große Dateien ~900 MB RSS je Prozess.
- `check-header-genres.py --check` (Haupt <= Werk <= Haupt+Eltern) ist blind für Köpfe ohne Hauptgattung (Werkgattung nur als `ana="parent"`), gelöschte Elternkategorien, Gloss-Text, doppelte ids.
- `check-variants-flips.py --base <rev>`: vergleicht `variants` mit `git show <base>:data/authority-index.json.gz`, rot bei jeder umgeklappten Form, außer `scripts/audit/variants-flips-ack.json` nennt genau (from-Version, to-Version, Anzahl); prüft zusätzlich `variants[f] == variantCandidates[f][0]`. Base ohne Index = OK; die Quittung ist force-added (`scripts/audit/*.json` ist gitignoriert).
- `build-authority-index.py` hängt seit 1.9.18 von `data/corpus-index.json.gz` ab (`lemma.noCorpus`): Abbruch bei fehlender Datei, falscher Version oder lemmaIndex < 10.000. Reihenfolge Korpus vor Authority; DEVELOPMENT.md „Build Commands“ seit 02.10. in dieser Reihenfolge.
- `schema/examples/*.xml` validiert nichts: eine Pflichtattribut-Änderung im Schema lässt die Beispieldatei still ungültig (Probe mit lxml RelaxNG).
- Kein Gate: tailwind-output.css, sense/@ana, Header-Spiegel gegen works.xml außer Gattungen.
- **Syntaxfehler im Textteil:** seit `tei_header` (iterparse bricht nach `</teiHeader>` ab) fangen ihn 7b/7c nicht mehr; fangen tun Step 4 (extract-variants), Step 6 (build-corpus-index überspringt die Datei mit Exit 0, der Rebuild-Vergleich wird rot), Step 7 (cross-refs). Lokal bleibt build-corpus-index grün, nur die Warnzeile zeigt es.
- **Parallel-Gegenprobe** (cross-refs, Begriffshilfe): `--jobs=1` gegen Vorgabe, per `cmp`; eine `--out`-Datei erst nach `tr -d '\r'` mit dem Baum vergleichen (`core.autocrlf=true`).

**extract-variants.py**
- „Typ mit >1 Lemma" endet mit return 0: kein Gate. Ohne `--apply` schreibt es `authority-files/variants.regen.xml` (nicht gitignoriert, danach löschen); Laufzeit ~1 min.
- `--apply` bereinigt auch sense/@ana in lexicon.xml; der Textanker-Abbruch kommt erst NACH dem variants-Write.
- Seit 1.9.18 schreibt es `form/@n` und zählt `token count n changed`: jede Umannotierung eines corresp-Tokens ändert variants.xml, der Freshness-Step wird ohne Regeneration rot. `check-authority-cross-refs.py` importiert nur `orphan_ana_tokens`.

**build-issue-matrix.py:** `zeile()` schreibt fremde `area:`/`effort:`-Werte roh in die Zelle (nur `auto:` fällt aus der Tabelle); Vokabular dreifach (Konstanten, Docstring, CLAUDE.md), nur AUTO_STUFEN<->ACHSEN per Selbsttest gekoppelt.

**Review-Bot (claude-code-review.yml, claude-code-action@v1)**
- Ohne `show_full_output` zeigt das Log nur `init` und die Result-Zusammenfassung; der `result`-Text mit der Fehlermeldung fällt weg (`sanitizeSdkOutput`). Voll bei `show_full_output: true` oder `ACTIONS_STEP_DEBUG=true`; ob ein Debug-Rerun die Variable exportiert, ist nicht gemessen.
- Muster über rote Läufe: `gh run view <id> --log | grep -o '"is_error": [^,]*'`.

**main-Schutz** ist nur ein Ruleset (`deletion`, `non_fast_forward`): `branches/main .protected=true` heisst nicht PR-Pflicht. `rules/branches/main` und `rulesets/<id>` lesen.
