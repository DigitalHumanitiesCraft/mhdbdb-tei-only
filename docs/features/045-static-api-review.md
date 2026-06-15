# Code-Review #45 — Statische JSON-API

**Branch:** `feature/45-static-api` · **Datum:** 2026-06-13 · **Reviewer:** Claude Code (`/code-review`, high effort)
**Status:** temporäres Artefakt (ticket-gebunden, bei Issue-Close löschen — siehe `CLAUDE.md` → Temporal Artifacts)

## Umsetzungs-Status (2026-06-15)

Verifiziert per Workflow (ein Verifier pro Finding + adversariale Gegenprüfung, 20 Agenten) gegen den aktuellen Stand von `feature/45-static-api`. **Ergebnis: keines der 10 Findings ist umgesetzt — alle offen.** Die adversariale Gegenprüfung bestätigte alle 10 Erst-Urteile (volle Übereinstimmung, je mit Zitat aus dem aktuellen Dateistand). Pro-Finding-Markierungen siehe unten; Prioritäten in der Empfehlungstabelle.

**Präzisierung zu Finding 4:** `--allow-dirty` ist `action='store_true'` mit Default `False`, und `check_working_tree()` blockt bei dirty `data/` — der Titel-Teil „wird zur Standard-Invokation" trifft so nicht zu. Das Kernproblem besteht aber unverändert: `npm run build` (`package.json:20`) enthält kein `build:api`, und es gibt kein Orchestrierungs-Target, das variants → beide Indexe → API in Abhängigkeitsreihenfolge baut.

## Scope

Working-Tree-Diff gegen `HEAD` plus die neuen, untracked Dateien:

- `scripts/build-api.py` (neu, 344 Z. — Hauptcode)
- `api/` (2.742 generierte JSON-Dateien + handgeschriebenes `api/index.html`)
- `.github/workflows/data-integrity.yml` (neuer „Freshness API"-Step + Trigger-Path `api/**`)
- `package.json` (`build:api`-Target)
- Doku: `CLAUDE.md`, `README.md`, `docs/{ARCHITECTURE,CONTRACTS,DATA-MODEL,DEVELOPMENT,FEATURES,INDEX,RESEARCH}.md`, `docs/features/045-static-api.md`, `hilfe-daten.html`

## Methode

7 unabhängige Finder-Angles (3 Korrektheit, 3 Cleanup, 1 Altitude) → ~13 deduplizierte Kandidaten → je ein Verifier pro Kandidat (recall-biased). 1 Kandidat als REFUTED verworfen (das Warn-and-continue bei Git-Fehlern im Pre-flight ist das etablierte #100-Muster, byte-identisch in beiden Sibling-Buildern — kein Defekt). 10 Findings überleben.

**Solide befunden** (alle Stichproben der Verifier bestanden): Determinismus, Pre-Wipe-ID-Validierung, Windows-Case-Kollisionsschutz; alle 45.888 IDs matchen beide Regexes; die in `api/index.html` dokumentierten Schemas und Counts matchen den tatsächlichen Output exakt; die `TEXT_STRIP_KEYS`-Liste deckt alle schweren Per-Text-Felder ab.

## Abgrenzung

Die Claude-Bot-Kommentare auf PR #146 gehören zum **bereits gemmergten** #125-Strang (Determinismus + CI-Gate), nicht zu #45. Ihre Punkte sind im aktuellen Stand größtenteils erledigt (pip-Cache vorhanden, `scripts/audit/**` in Trigger-Paths, `pip install -r` in DEVELOPMENT.md). Sie sind für dieses Review **nicht relevant**. Finding 1 unten (untracked-blindes Gate) wurde unabhängig gefunden und steht in keinem der #125-Bot-Kommentare.

---

## Findings (nach Schwere)

### 1. CI-Freshness-Gate ist blind für untracked Files — **Merge-Blocker**

> **Status 2026-06-15: offen (nicht umgesetzt).** Der API-Freshness-Step nutzt weiterhin ausschließlich `git diff --exit-code -- api/`; keine `git status --porcelain`- oder `git add -N`-Untracked-Erkennung. (Das porcelain-Muster #100 existiert in `build-api.py` `check_working_tree()`, ist aber nur auf `data/` gerichtet, nicht ins Workflow-Gate gespiegelt.)

`.github/workflows/data-integrity.yml:177` · `git diff --exit-code -- api/`

Der neue API-Gate nutzt `git diff`, das **untracked Files ignoriert**. Deletions und Content-Drift an tracked Files werden korrekt erkannt, Additions nicht.

**Failure:** Contributor ingestet einen neuen Text, baut lokal, committet per Pflicht-Regel (kein `git add -A`) `api/texts/index.json` + `api/index.json`, vergisst aber `api/texts/NEU.json`. CI-Rebuild erzeugt `NEU.json` als untracked File, alle tracked Files matchen byte-identisch, `git diff` exit 0 → Gate grün, deployte API liefert 404 auf eine URL, die ihr eigener Index listet.

**Fix:** Zusätzlich auf leeres `git status --porcelain -- api/` prüfen — das eigene Pre-flight-Muster #100 in `build-api.py` macht es aus genau diesem Grund so.

### 2. Lifecycle-Reihenfolge erzwingt zwei rote CI-Runden bei Versions-Bumps — **Merge-Blocker (Doku)**

> **Status 2026-06-15: offen (nicht umgesetzt).** In beiden Lifecycle-Tabellen (`DATA-MODEL.md` ~Z. 779–796) steht der Versions-Bump weiterhin nach allen Rebuild-Schritten, ohne Re-Run-Anweisung danach. Mechanik bestätigt: `build-corpus-index.py` backt die Version zur Build-Zeit ins gz, `build-api.py` liest sie ins Root-Manifest — Pre-Bump-Builds erzeugen also einen CI-Diff.

`docs/DATA-MODEL.md:782` (tei-Tabelle), analog `:795` (Authority-Tabelle)

`build-api` steht als Schritt 6 **vor** dem Versions-Bump (Schritt 7), ohne Re-Run-Anweisung danach. `api/index.json` `sources` und die `.gz`-Indexe tragen dann Pre-Bump-Versionen.

**Failure:** Versionsbumpender Daten-PR nach Tabelle: Indexe gebaut mit alter Konstante, API gebaut (`sources=4.1.4`), dann Bump auf `4.1.5`; `check-index-versions.py` vergleicht nur Skript-Literal vs. `corpus-loader.js` → grün. CI „Freshness Indexe" schlägt fehl (Rebuild ergibt `4.1.5` vs. committete `4.1.4`); nach dem Index-Fix schlägt „Freshness API" fehl, weil niemand `build-api` re-ran. Zwei garantierte CI-Runden für jeden, der die Doku wörtlich befolgt.

**Fix:** Bump vor die Rebuild-Schritte ziehen, oder Re-Run von Index-Builds + `build-api` nach dem Bump explizit dokumentieren.

### 3. Lokales Freshness-Advisory kennt api/ nicht

> **Status 2026-06-15: offen (nicht umgesetzt).** Die `DERIVED`-Registry (`check-index-freshness.py:52–77`) enthält weiterhin nur drei Einträge (`variants.xml`, beide `.json.gz`); kein `api/`-Eintrag, Grep nach `api|build-api` über die ganze Datei ohne Treffer.

`scripts/audit/check-index-freshness.py:52`

Die `DERIVED`-Registry wurde nicht um `api/` erweitert — das Tool meldet „OK", während `api/` stale ist; die Abhängigkeit lebt nur als CI-YAML und Doku-Prosa.

**Failure:** Entwickler ändert `authority-files/`, baut Indexe, lässt das dokumentierte lokale Advisory laufen → „Index-Freshness OK", pusht, lernt erst aus dem roten CI-Run, dass `api/` fehlt; bei einem direkten main-Push (historisch passiert, WZB 2026-05-06) shippt stale API an externe Konsumenten.

**Fix:** Eintrag `{artifact: api/, sources: [beide .json.gz], rebuild: build-api.py}` in die `DERIVED`-Liste.

### 4. `npm run build` enthält build:api nicht; `--allow-dirty` wird zur Standard-Invokation

> **Status 2026-06-15: offen (Kern-Befund), Titel teilweise präzisiert.** `package.json:20` `build` enthält weiterhin kein `build:api`; kein Orchestrierungs-Target vorhanden. Korrektur zum Titel: `--allow-dirty` ist `action='store_true'` (Default `False`) und `check_working_tree()` blockt bei dirty `data/` — es wird also *nicht* zur Default-Invokation. Der empfohlene Fix (Orchestrierungs-Skript für alle abgeleiteten Artefakte) ist nicht umgesetzt.

`package.json:20`

Das `build`-Aggregat baut Indexe, aber nicht die API. Der kanonische Lifecycle erfordert bei jedem normalen Durchlauf `--allow-dirty` (frisch gebaute Indexe sind per Definition uncommitted), wodurch der Sicherheits-Bypass zur Default-Invokation wird.

**Failure:** Entwickler nutzt `npm run build` nach Datenänderung, committet Quellen + Indexe atomar (wie Schritt 10 verlangt) → `api/` stale, PR prallt an CI ab (Fix-up-Commit + zweite Pipeline-Runde). Langfristig: `--allow-dirty` wird Boilerplate; wenn `data/` einmal aus schlechtem Grund dirty ist (abgebrochener Build, parallele Session), wird der Guard reflexhaft umgangen.

**Fix:** Orchestrierungs-Skript/npm-Target, das alle abgeleiteten Artefakte in Abhängigkeits-Reihenfolge baut und in dem Post-Rebuild-Dirtiness der erwartete Zustand ist.

### 5. Falsche Begründung für die Gate-Reihenfolge in der Feature-Doku

> **Status 2026-06-15: offen (nicht umgesetzt).** `045-static-api.md:255` trägt unverändert die gz-Byte-Instabilitäts-Rationale. Der korrekte Pre-flight-Mechanismus ist im selben Dokument zwar belegt (Z. 244, 266), aber nicht in die Rationale auf Z. 255 eingearbeitet.

`docs/features/045-static-api.md:255`

Behauptet wird, gz-Byte-Instabilität würde den Byte-Vergleich des API-Outputs falsch triggern. Tatsächlich (so der Workflow-Kommentar korrekt) würde der Index-Rebuild `data/` dirty hinterlassen und den `build-api`-Pre-flight auslösen; der API-Output ist aus dekomprimiertem Inhalt gebaut und byte-identisch — der `git diff -- api/`-Vergleich kann nie falsch triggern.

**Failure:** Ein künftiger Maintainer vertraut der Doku und „löst" die Ordering-Constraint per `--allow-dirty` in der CI-Invokation — das Gate baut dann gegen CI-rebuilte statt committete Indexe und maskiert genau den Drift, den es fangen soll.

**Fix:** Eine Zeile, Rationale durch den Pre-flight-Mechanismus aus dem Workflow-Kommentar ersetzen. (`CONTRACTS.md` §G ist sauber, die falsche Begründung wurde nicht destilliert.)

### 6. Kein reservierter Dateiname — Sigle `INDEX` kollidiert mit `index.json`

> **Status 2026-06-15: offen (nicht umgesetzt).** `assert_ids` (`build-api.py:139–154`) prüft nur Pattern-Match und Case-Eindeutigkeit unter den IDs, keinen Guard gegen den Namen `index`. Aktuell trägt kein Text die Sigle `INDEX` (Risiko latent), der Fix bleibt unimplementiert.

`scripts/build-api.py:204`

Eine Text-Sigle `INDEX` (gültig unter `TEXT_ID_RE`) erzeugt `api/texts/INDEX.json` und kollidiert case-insensitiv mit dem zuletzt geschriebenen `api/texts/index.json`. `assert_ids` prüft IDs gegeneinander, aber nie gegen `index`. Authority-Collections sind durch den Underscore im Pattern nicht exponiert; aktuelle Daten sauber (alle 45k IDs geprüft).

**Failure:** Künftiger Ingest mit Sigle `INDEX`: auf Windows/NTFS überschreibt die Summary das Record-File (Record still verloren), auf Linux koexistieren beide → byte-divergente `api/`-Bäume zwischen Windows-Dev und Linux-CI, das Freshness-Gate meldet einen dauerhaften, schwer diagnostizierbaren Mismatch.

**Fix:** Eine Zeile in `assert_ids`, `lowered == 'index'` ablehnen.

### 7. Symlink-Skip in clean_api_dir() ist selbst-widersprüchlich

> **Status 2026-06-15: offen (nicht umgesetzt).** `clean_api_dir()` überspringt Symlinks weiterhin per `continue` (`build-api.py` ~Z. 123–127), `unlink()` läuft nur für Nicht-Symlinks; der Docstring beschreibt das Skip als beabsichtigt. Empfohlener Fix (Symlink per `unlink()` entfernen) fehlt.

`scripts/build-api.py:124`

Ein übersprungener Symlink überlebt in die Schreibphase, wo `write_bytes()` ihm folgt und sein Ziel (potenziell außerhalb `api/`) überschreibt — `unlink()` hätte den Link selbst sicher entfernt.

**Failure:** Committeter Symlink `api/persons/person_1.json → ../../scripts/build-api.py` materialisiert auf dem Linux-CI-Runner; der Build schreibt Record-JSON durch den Link und clobbert die Zieldatei; `git diff -- api/` bleibt clean (Link-Target unverändert) → Gate grün trotz überschriebener Datei. Impact niedrig (CI ephemer, Inhalt nicht angreifer-kontrolliert), aber der Guard leistet das Gegenteil seines Zwecks.

**Fix:** Symlinks löschen statt überspringen (`unlink()` entfernt den Link, nicht das Ziel).

### 8. Wipe-Safety deckt nur ID-Validierung ab

> **Status 2026-06-15: offen (nicht umgesetzt).** Pre-Wipe-Validierung (`validate_all_ids`) deckt weiterhin nur IDs ab; Reihenfolge in `main()` unverändert (validate → `clean_api_dir()` → build), kein Temp-Dir-Swap. Die summarize-Lambdas greifen weiterhin hart auf `preferredName`/`title`/`termDE`/`author`/`wordCount` zu, ausgeführt nach dem Wipe.

`scripts/build-api.py:319`

Die summarize-Lambdas greifen hart auf `preferredName`/`title`/`termDE`/`author`/`wordCount` zu — ein KeyError dort träfe NACH `clean_api_dir()` und hinterlässt ein halb gebautes `api/`.

**Failure:** Künftiges Index-Schema benennt z. B. `wordCount → tokenCount` um: ID-Validierung passiert, 2.742 Files gewipet, KeyError in der texts-Lambda → partieller `api/`-Baum. Per `git checkout -- api/` wiederherstellbar und laut/sofort sichtbar, daher nur Härtung.

**Fix:** Pre-Wipe-Validierung um die Pflicht-Summary-Keys pro Collection erweitern, oder in Temp-Dir bauen und swappen.

### 9. api/index.html hardcodet Counts — Drift-by-Design

> **Status 2026-06-15: offen (nicht umgesetzt).** Die Counts (43.754, 211, 584, 567, 615, 90, 667) stehen weiterhin als feste Literale in der URL-Schema-Tabelle; die Seite enthält kein `<script>`, lädt also nichts client-seitig aus `index.json`, und kein Gate vergleicht die Werte.

`api/index.html:146`

Die handgeschriebene Doku-Seite hardcodet alle Collection-Counts (43.754, 211, 584, 567, 615, 90, 667) und Größenangaben; `build-api.py` lässt sie bewusst unangetastet und kein Gate vergleicht sie. Dieselben Zahlen zusätzlich in INDEX/FEATURES/ARCHITECTURE/DATA-MODEL/DEVELOPMENT (der bekannte Doc-Count-Drift-Befund).

**Failure:** ARITHMETIC #92 fügt 6 Texte plus Lemmata hinzu: alle `api/*.json` werden CI-gegated aktualisiert, die öffentliche Doku-Seite daneben nennt unbegrenzt falsche Counts und nichts flaggt es.

**Fix:** Counts aus der URL-Schema-Tabelle entfernen (das Root-Manifest trägt sie bereits, die Seite verweist darauf) oder client-seitig aus `index.json` befüllen.

### 10. Trigger-Path `api/**` matcht auch api/index.html

> **Status 2026-06-15: offen (bewusst zurückgestellt).** Beide Trigger-Listen (`data-integrity.yml`, `pull_request.paths` und `push.paths`) enthalten `api/**` ohne Negativ-Ausschluss. Im Review ausdrücklich als akzeptierbares Restrisiko eingestuft („nur falls Standalone-Edits häufiger werden") — kein Umsetzungs-Mangel, sondern bewusst offen.

`.github/workflows/data-integrity.yml:54`

Ein Doku-only-Edit am handgeschriebenen `api/index.html` feuert den vollen monolithischen 10-Schritte-Job (Variants-Regen, API- und beide Index-Rebuilds, RelaxNG über 667 Files, realistisch 10–25 min), obwohl kein Check anders ausgehen kann. `api/**` selbst ist nötig (Hand-Edits an generierten JSONs müssen das Gate feuern).

**Failure:** Typo-Fix-PR an `api/index.html` kostet einen vollen Run inkl. `tei_all.rng`-Download; ist tei-c.org down oder der P5-Pin gerade überholt, blockt ein fachfremdes rotes X den Doku-PR.

**Fix:** Negativ-Pattern `!api/index.html` nach `api/**`, falls Standalone-Edits häufiger werden.

---

## Empfehlung

| Priorität | Findings | Status (2026-06-15) |
|-----------|----------|---------------------|
| Vor Merge | 1 (Gate untracked-blind), 2 (Lifecycle-Reihenfolge), 3 (Advisory-Registry), 4 (build-Aggregat/`--allow-dirty`) | alle 4 offen |
| Einzeiler | 5 (Doku-Rationale), 6 (`index`-Reservierung), 7 (Symlink) | alle 3 offen |
| Akzeptierbares Restrisiko | 8 (Wipe-Härtung), 9 (Count-Drift), 10 (Trigger-Path) | alle 3 offen (10 bewusst zurückgestellt) |

Der Build-Code selbst ist solide; die schwerwiegenderen Punkte liegen im CI-Gate und in der dokumentierten Prozessreihenfolge, nicht in `build-api.py`.
