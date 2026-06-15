# #45 Static JSON API — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Statische, FAIR-konforme JSON-API unter `/api/` auf GitHub Pages: stabile, zitierbare URLs für Persons, Works, Concepts, Genres, Names und Texte; Lemmata als Bundle. Deterministischer Build + CI-Freshness-Gate (Muster #125).

**Architecture:** Neues Skript `scripts/build-api.py` liest die zwei vorhandenen Indexe (`data/*.json.gz`) und emittiert ~2.740 JSON-Dateien nach `/api/`. Kein XML-Parsing, kein Server. Spec: `docs/features/045-static-api.md` — **in der durch Task 1 korrigierten Fassung** (Stand Feb 2026 hatte 2 kritische + 5 mittlere Befunde, /check-md 2026-06-12).

**Tech Stack:** Python 3.13 (json, gzip — keine neuen Dependencies), GitHub Actions, statisches HTML für die Doku-Seite.

**Projektregeln (überschreiben Skill-Defaults):**
- KEIN Commit/Push ohne Christians Freigabe → alle Commit-Steps am Ende gebündelt und explizit gegated (Task 8).
- Nur gezielt benannte Pfade stagen, nie `git add -A` (parallele Sessions). `git add api scripts/build-api.py …` ist ok (eigene, neue Pfade).
- `npm test` nie ungefragt starten.
- Kein Python-Test-Framework → Verifikation über explizite Kommandos (Doppel-Build-Vergleich, Count-Abgleich, curl-Smoke-Test).
- Vor dem Schreiben von `build-api.py` zwei bestehende Build-Skripte lesen (`build-authority-index.py`, `scripts/ingest/naming/01-fetch-and-build-index.py`) — Konventionen übernehmen (Pre-flight, Print-Format, Pfad-Konstanten).

---

## Verbindliche Spec-Entscheidungen (lösen die /check-md-Befunde auf)

| # | Entscheidung | löst Befund |
|---|--------------|-------------|
| E1 | `texts/{sigle}.json` strippt `words`, `lemmata`, **`lineStarts`, `lineEnds`** | CRITICAL 1 |
| E2 | `lemmata/index.json` = **volle Records** (inkl. `senses`/`conceptIds`, `etymology`; ~13 MB) — die lemma→concept-Brücke lebt hier | CRITICAL 2 |
| E3 | Concepts/Genres/Names führen `termDE`/`termEN`/`normalized` (+ `altDE`/`altEN`/`altNormalized` bei Concepts, `conceptIds` bei Names) — es gibt kein `label` | MEDIUM 3 |
| E4 | Root-Index **ohne** `generated`-Timestamp (Determinismus, #125); Provenienz via `"sources": {"authorityIndex": "<version>", "corpusIndex": "<version>"}`, Versionen zur Laufzeit aus den Indexen gelesen | MEDIUM 4 |
| E5 | API-Freshness-Step in `data-integrity.yml` (Rebuild-and-Compare wie Indexe; billig, liest nur die zwei gz) | MEDIUM 5 |
| E6 | Alle Counts dynamisch aus den Indexen; keine hartkodierten Zahlen im Build | MEDIUM 6 |
| E7 | `person.works` wird im API zu Array normalisiert: `"works": ["work_4", …]`, leer = `[]` (Quelle: Komma-String oder null) | MEDIUM 7 |
| E8 | `"license": "CC BY-NC-SA 4.0"` in **jeder** JSON-Datei (FAIR-Versprechen einlösen, ~30 B/Datei) | LOW 9 |
| E9 | Works/Persons/Concepts/…: **volle Index-Records** in den Einzeldateien (inkl. `gnd`, `wikidata`, `handschriftencensus`, `biblStructs`) — keine Feld-Subsets außer bei den `index.json`-Listen | LOW 10 |
| E10 | `maps` (conceptToLemmas, genreToWorks, genreHierarchy) bleiben **out of scope** — client-seitig aus dem Lemmata-Bundle/Works-Liste ableitbar; im Spec-Doc als explizite Entscheidung nachtragen | LOW 11 |
| E11 | JSON kompakt (`ensure_ascii=False`, `separators=(',', ':')`), UTF-8, kein Pretty-Print — identisch zu den Index-Builds, deterministisch | — |
| E12 | Build wischt vor dem Schreiben alle `api/**/*.json` (Orphan-Schutz bei entfernten Ressourcen); `api/index.html` (handgeschrieben) bleibt unberührt | — |
| E13 | ID-Safety-Assert: Authority-IDs `^[a-z]+_[A-Za-z0-9-]+$` (Großbuchstaben im Suffix nötig — `work_WZB` existiert; Bindestrich für 3 RDF-Migrations-UUID-Works wie `work_f1576278-...`), Text-IDs `^[A-Z0-9]+$`; sonst Abbruch. Windows-Case-Kollisionen separat absichern: `assert len({i.lower() for i in ids}) == len(ids)` je Collection | — |
| E14 | Referenz-Felder bleiben **roh** wie im Index (`authorRef: "persons.xml#person_786"` bei Works vs. `"#person_445"` bei Texten — gemischte Syntax ist Quelltreue); die Parsing-Konvention („ID = Teil nach `#`") wird auf `api/index.html` dokumentiert. Einzige Ausnahme bleibt E7 (`person.works`), weil dort ein Komma-String ohne `#`-Konvention vorliegt | LOW 7 (Plan-Check) |

---

### Task 0: Feature-Branch

- [ ] **Step 0.1:**

```bash
git status --porcelain
# Erwartung: clean BIS AUF die zwei untracked/modifizierten 045-*-Feature-Docs
# (gehören zu diesem Task). Fremde Session-Dateien: nicht anfassen.
git checkout -b feature/45-static-api
```

---

### Task 1: Spec-Doc korrigieren

**Files:** Modify: `docs/features/045-static-api.md`

- [ ] **Step 1.1:** Alle /check-md-Befunde einarbeiten (Entscheidungen E1–E10 oben in die jeweiligen Abschnitte; Counts auf Stand 2026-06-12: Lemmata 43.754, Persons 211, Works 584, Concepts 567, Genres 615, Names 90, Variants-Map 234.244, Texte 667; Corpus 42 MB gz / ~200 MB; Karl-IV-Beispiel → `person_1768`; `#id`-Fragment-Formulierung ersetzen; „Not part of CI" → CI-Gate-Absatz).
- [ ] **Step 1.2:** Neuen Abschnitt „Determinismus & Freshness (#125-Erbe)" ergänzen: Build deterministisch, Gate in `data-integrity.yml`, `api/` ist abgeleitete Schicht im Data-Change-Lifecycle.

---

### Task 2: `scripts/build-api.py`

**Files:** Create: `scripts/build-api.py`

- [ ] **Step 2.1:** Vorbild-Skripte lesen (`scripts/build-authority-index.py` Pre-flight + Print-Stil, `scripts/ingest/naming/01-fetch-and-build-index.py` Determinismus-Muster).
- [ ] **Step 2.2:** Skript schreiben. Struktur:

```
Konstanten: DATA_DIR, API_DIR = Path('api'), LICENSE = 'CC BY-NC-SA 4.0'
ID-Regexe (E13): AUTH_ID = ^[a-z]+_[A-Za-z0-9-]+$ ; TEXT_ID = ^[A-Z0-9]+$
  (work_WZB muss matchen!) + je Collection Case-Kollisions-Assert:
  len({i.lower() for i in ids}) == len(ids)

main():
  1. Pre-flight (#100-Muster): git status --porcelain -- data/ muss leer sein
     (dirty Indexe ergäben inkonsistentes API); --allow-dirty als Escape.
  2. Beide Indexe laden (gzip+json).
  3. api/**/*.json löschen (E12), Verzeichnisse anlegen.
  4. Collections schreiben:
     - lemmata/index.json: volle Records (E2)
     - persons|works|concepts|genres|names: je {id}.json (voller Record, E9;
       person.works → Array, E7) + index.json (Kurzliste:
       persons {id, preferredName} / works {id, title, sigle} /
       concepts|genres|names {id, termDE, termEN} / texts {id, title, author, wordCount})
     - texts/{id}.json: Record OHNE words/lemmata/lineStarts/lineEnds (E1)
     - jede Datei + jede Liste bekommt license-Feld (E8); bei Einzelrecords
       als zusätzlicher Key, bei index.json als {"license": ..., "items": [...]}
  5. Root api/index.json: project, license, contact, sources (E4),
     collections mit dynamischen counts (E6) und href.
  6. ID-Assert vor jedem Datei-Write (E13).
  7. Summary-Print: Dateizahl je Collection, Gesamtgröße.
Serialisierung: json.dumps(obj, ensure_ascii=False, separators=(',', ':')) → encode('utf-8'),
write_bytes. Kein Timestamp, kein Zufall, Iteration in Index-Reihenfolge (Listen = stabil).
```

- [ ] **Step 2.3:** `python -m py_compile scripts/build-api.py && echo OK`

---

### Task 3: Doku-Seite `api/index.html` + Verlinkung

**Files:** Create: `api/index.html`; Modify: `hilfe-daten.html`

- [ ] **Step 3.1:** Handgeschriebene deutsche Doku-Seite: URL-Schema-Tabelle, ein curl/fetch-Beispiel pro Collection, Schema-Kurzbeschreibung, **Ref-Parsing-Konvention (E14: ID = Teil nach `#`, gemischte Präfix-Syntax erklären)**, Lizenz + Zitierhinweis (Zenodo-DOI), Kontakt. Stil an `hilfe-*.html` anlehnen, aber **standalone** (kein build-injizierter Nav/Footer — `api/` ist Maschinen-Territorium, ein schlichter Header mit Link zur Hauptseite genügt; dadurch kein Touch an `build-pages.py`). Keine Em-Dashes, keine Emoji-Icons (Projekt-Konventionen).
- [ ] **Step 3.2:** In `hilfe-daten.html` einen Abschnitt/Verweis „Programmatischer Zugriff (JSON-API)" auf `/api/index.html` ergänzen.
- [ ] **Step 3.3:** Prüfen, ob neue Tailwind-Klassen eingeführt wurden → falls ja `npm run build:css` (Konvention), falls `api/index.html` ohne Tailwind auskommt (empfohlen: minimales Inline-CSS), entfällt das.

---

### Task 4: `package.json`-Alias

**Files:** Modify: `package.json`

- [ ] **Step 4.1:** Unter `scripts`: `"build:api": "python scripts/build-api.py"` (neben `build:css`/`build:vendor`).

---

### Task 5: CI-Gate in `data-integrity.yml`

**Files:** Modify: `.github/workflows/data-integrity.yml`, `docs/DEVELOPMENT.md` (CI-Sektion)

- [ ] **Step 5.1:** Neuen Step **VOR** „Freshness Indexe" einfügen (also nach „Freshness variants.xml"). Begründung der Platzierung: der Index-Freshness-Step rebuildet `data/*.json.gz` im Working Tree, und deren **gz-Bytes** dürfen je zlib-Build vom Commit abweichen (deshalb vergleicht das Index-Gate dekomprimiert) — danach wäre `data/` aus Sicht des build-api-Pre-flights dirty und der API-Step würde grundlos abbrechen. Vor dem Index-Step ist `data/` garantiert clean (variants-Step hinterlässt bei Erfolg keinen Diff, tei_all.rng ist gitignored). Billig→teuer bleibt gewahrt (API-Build: Sekunden). Sind die Indexe stale, baut der API-Step zwar aus stalen Indexen ein konsistentes api/ und passiert — das Index-Gate failt dann einen Step später trotzdem.

```yaml
      - name: Freshness API (#45)
        run: |
          python scripts/build-api.py
          if ! git diff --exit-code -- api/; then
            echo "::error file=api/index.json::api/ ist nicht mit den Indexen synchron. Lokal 'python scripts/build-api.py' ausfuehren und mitcommitten (DATA-MODEL.md -> Data-Change-Lifecycle)."
            exit 1
          fi
```

  Hinweis: `git diff` (Byte-Vergleich) ist hier korrekt — der API-Build ist plain JSON ohne gzip, also plattform-byte-identisch, sobald die Indexe identisch sind. Untracked neue Dateien sieht `git diff` zwar nicht, aber jede Ressourcen-Änderung schlägt sich zwingend auch in einer getrackten `index.json` (Liste/Count) nieder.
- [ ] **Step 5.2:** `paths`-Listen (PR + push): `'api/**'` und `'scripts/build-api.py'` ergänzen. Header-Kommentar: Check-Liste auf 8 Einträge erweitern (neuer Punkt zwischen 4 und 5, Nummerierung der Folge-Checks anpassen).
- [ ] **Step 5.3:** YAML-Check: `python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/data-integrity.yml').read_text(encoding='utf-8')); print('YAML OK')"`

---

### Task 6: Build + Verifikation

- [ ] **Step 6.1: Erstbuild + Plausibilität**

```bash
python scripts/build-api.py
# Erwartete Dateizahl: 211+584+567+615+90+667 = 2.734 Einzeldateien
# + 7 index.json + 1 Root = 2.742 JSON (+ index.html)
find api -name '*.json' | wc -l
```

- [ ] **Step 6.2: Count-Abgleich gegen die Indexe** (ein Python-Einzeiler: Root-`collections[*].count` == `len()` der jeweiligen Index-Collection == Dateizahl im Ordner; `assert` je Collection).
- [ ] **Step 6.3: Schema-Stichproben:** `api/texts/ABG.json` enthält KEIN `words`/`lemmata`/`lineStarts`/`lineEnds`; `api/persons/person_1.json` hat `works` als Array mit 15 Einträgen (Komma-Split-Fall) und `api/persons/person_1768.json` (Karl IV., Quelle `null`) hat `works: []`; `api/works/work_WZB.json` existiert (E13-Regex-Probe); ein Lemma im Bundle hat `senses[].conceptIds`; jede gezogene Datei hat `license`.
- [ ] **Step 6.4: Determinismus-Doppelbuild:**

```bash
mkdir -p "$HOME/.cache/claude-scratch" && rm -rf "$HOME/.cache/claude-scratch/api-run1"
cp -r api "$HOME/.cache/claude-scratch/api-run1"
python scripts/build-api.py
diff -r api "$HOME/.cache/claude-scratch/api-run1" && echo DETERMINISTISCH
```

- [ ] **Step 6.5: Smoke-Test über den Dev-Server:** `npm run serve` (läuft ggf. schon), dann `curl -s localhost:8080/api/index.json | python -m json.tool | head` und `curl -s localhost:8080/api/works/work_350.json`. Browser-Stichprobe `api/index.html`.
- [ ] **Step 6.6:** `git status` sichten: NUR `api/`, die geplanten Skript-/Doku-Dateien — nichts Fremdes.

---

### Task 7: Dokumentation

**Files:** Modify: `docs/DATA-MODEL.md`, `docs/DEVELOPMENT.md`, `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/CONTRACTS.md`, `docs/INDEX.md`, `CLAUDE.md`, `README.md`

- [ ] **Step 7.1: DATA-MODEL.md** — `api/` als dritte abgeleitete Schicht: kurzer Abschnitt (Quelle = die zwei Indexe, Build-Kommando, deterministisch) + neue Zeile in den Data-Change-Lifecycle-Tabellen (`Status: CI (Freshness-Gate in data-integrity.yml)`).
- [ ] **Step 7.2: DEVELOPMENT.md** — Command `npm run build:api`; CI-Sektion „Sieben Checks" → „Acht Checks" inkl. neuem Punkt + Debugging-Zeile („API-Freshness → `python scripts/build-api.py` lokal, mitcommitten").
- [ ] **Step 7.3: ARCHITECTURE.md** — Komponenten-/Storage-Abschnitt: `/api/` (statisch, ~2.700 Dateien, ~15 MB) ergänzen.
- [ ] **Step 7.4: FEATURES.md** — User-facing Abschnitt „JSON-API für programmatischen Zugriff" (Zielgruppe: externe Projekte MWB/Wörterbuchnetz, Forschende).
- [ ] **Step 7.5: CONTRACTS.md** — neuer Contract, präzise formuliert: das **URL-Schema** ist stabil (Pfadstruktur, kein Versions-Prefix; Schema-Änderungen werden dokumentiert statt versioniert), aber **Ressourcen folgen dem Datenbestand** — im aktiven Projekt (Ingest + Korrekturen) kann eine einzelne `{id}.json` verschwinden (Orphan-Wipe E12, nachvollziehbar via Git-History). KEINE Record-Permanenz versprechen. Dazu: Feld-Schemas der index.json-Listen + Ref-Parsing-Konvention (E14).
- [ ] **Step 7.6: INDEX.md** — Data-Basis-Bullet (+ API), Future-Directions-Zeile „RESTful API for programmatic access" ersetzen durch erledigt/angepasst, Milestone-Bullet #45.
- [ ] **Step 7.7: CLAUDE.md** — Directory-Layout: Zeile `api/  # Statische JSON-API (generiert, build-api.py)`.
- [ ] **Step 7.8: README.md** — kurzer API-Hinweis mit Link auf `/api/index.html` (FAIR-Sichtbarkeit).
- [ ] **Step 7.9: Sweep:** `grep -rn "RESTful API\|programmatic access" docs/ README.md` — Reste bewerten.

---

### Task 8: Abschluss — Freigabe-Gate, Commit, PR

**STOP: Ab hier nichts ohne Christians explizite Freigabe.**

- [ ] **Step 8.1: Statusbericht** — Dateizahl/Größe, Determinismus-Ergebnis, Smoke-Test-Ergebnis, offene Auffälligkeiten. Fragen: (a) Freigabe Commit+Push+PR? (b) `npm test` vorher? (api berührt kein bestehendes Frontend-JS; einzige neue Seite ist statisch — Suite optional).
- [ ] **Step 8.2: Gezielt stagen:**

```bash
git add api scripts/build-api.py package.json hilfe-daten.html \
  .github/workflows/data-integrity.yml \
  docs/DATA-MODEL.md docs/DEVELOPMENT.md docs/ARCHITECTURE.md docs/FEATURES.md \
  docs/CONTRACTS.md docs/INDEX.md CLAUDE.md README.md \
  docs/features/045-static-api.md docs/features/045-static-api-plan.md
```

- [ ] **Step 8.3: Commit (Projekt-Format), Push, PR** — Titel „Static JSON API unter /api/ (Closes #45)". PR-Body: Spec-Verweis, Verifikations-Belege, Hinweis: der PR-CI-Lauf testet das neue API-Freshness-Gate erstmals (Windows-gebautes api/ vs. Linux-Rebuild — muss byte-identisch sein, da plain JSON aus identischen Indexen).
- [ ] **Step 8.4: CI beobachten;** bei Drift im API-Step: Ursache fixen (wäre ein Determinismus-Bug im Skript, kein Daten-Problem).
- [ ] **Step 8.5: Nach Merge:** Feature-Docs `045-*.md` löschen (Wissen ist nach Task 7 in den Stable-Docs), JOURNAL-Handoff, Milestone ist via Task 7.6 schon drin. Issue #45 schließt via Commit.

---

## Self-Review (beim Schreiben) + zweite /check-md-Runde (2026-06-12)

- **Alle 11 /check-md-Befunde der Spec** haben eine Auflösung in E1–E10 + Task 1 (Spec-Korrektur) bzw. Task 2/5 (Implementierung).
- **Zweite /check-md-Runde auf diesem Plan** (2 critical, 1 medium, 4 low) eingearbeitet: E13-Regex lässt `work_WZB` zu + expliziter Case-Kollisions-Assert; API-Gate VOR dem Index-Gate (gz-Bytes des CI-Index-Rebuilds können vom Commit abweichen → Pre-flight-Kollision); CONTRACTS ohne Record-Permanenz-Versprechen; Stichprobe `person_1` (Komma-Split) statt nur Karl IV. (`null`); Scratch-Verzeichnis idempotent; Step-0-Erwartung präzisiert; Ref-Format-Entscheidung als E14.
- **#125-Kohärenz:** kein Timestamp (E4), Determinismus-Doppelbuild (6.4), Freshness-Gate in data-integrity.yml (5.1).
- **Byte- vs. Inhalt-Vergleich begründet** (5.1): plain JSON ohne gzip → `git diff` reicht, anders als bei den gz-Indexen.
- **Offen/bewusst raus:** Lemma-Einzeldateien (Hybrid-Entscheidung bestätigt), `maps` (E10), Corpus-Enrichment, Variants als Ressourcen — unverändert aus der Spec.
- **Risiko 2.700 neue Dateien im Repo:** Lemma-Pages (#42, ~43k HTML-Dateien) sind der Präzedenzfall; Git/Pages verkraften das nachweislich.
