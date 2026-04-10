# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog — captures the *reasoning* behind changes.

---

## 2025-02-24 — Phase 0: Stabilization

**Trigger:** Before starting #42 (persistent lemma pages), the codebase needed cleanup.

### Wenzelsbibel removal
- Moved `Wenzelsbibel/` to `feature/wenzelsbibel-ingest` branch (connected to #34)
- Was bloating main with 652k lines of unfinished ingest work
- Savepoint: `4562c08`

### Folder restructure
- Consolidated `css/`, `js/`, `lib/` into `assets/{css,js,images}`
- Shared libs now at `assets/js/lib/` (corpus-loader, text-normalizer, etc.)
- 24+ files touched for path updates (HTML, JS, config, tests)
- Playground kept its own `playground/js/` and `playground/css/` — it's a self-contained sub-app
- Savepoint: `6849758`

### Playwright test repair
- Started at 2 passing out of 106 total
- Root causes found:
  1. Outdated Chromium binaries
  2. Multiple workers overwhelming http-server on Windows (`workers: undefined` → `workers: 1`)
  3. Dynamic `import()` in `page.evaluate()` used relative paths that resolved wrong from page context (e.g., `/playground/assets/js/...` instead of `/assets/js/...`). Fix: absolute imports.
  4. TEI cache manager import pointed to wrong subdirectory
- Final result: 36 passed, 25 skipped (intentional), 0 failed
- Filed #43 for test coverage gaps (reading view, search engine, text selection have zero coverage)
- Savepoint: `e16306d`

### Documentation fixes
- DECISIONS.MD: duplicate ADR-006 renamed to ADR-010
- DATA-MODEL.MD: removed phantom `definition`/`examples` fields from lemma senses, fixed etymology schema, corrected sense ID format
- Savepoint: `5154d04`

---

## 2025-02-24 — Issue #42: Preparation (Promptotyping Phase 1-3)

**Trigger:** MWB (Mittelhochdeutsches Worterbuch) and Worterbuchnetz want to link to MHDBDB lemmata. Katharina's meeting revealed end-of-March deadline for MWB evaluation.

### Key finding: IDs already aligned
- Worterbuchnetz `lid=879` = our `lemma_879` = Wikidata P9351 `879`
- MHDBDB already registered as one of 52 dictionaries in Worterbuchnetz (sigle: `MHDBDB`)
- Current `wbnetzlink` points to old Java app on port 8000 — will eventually break
- No mapping work needed, just need a stable target URL

### Worterbuchnetz API structure
- Open API at `api.woerterbuchnetz.de/open-api/`
- External dictionaries provide headword list + persistent URLs
- Currently only `lemmata` method exposed for MHDBDB (no fulltext/definition/citation)
- Some issues: empty `gram` field, duplicate results, encoding problems with special chars

### URL routing decision
- Chose clean paths (`/lemma/879`) over query params or hash routing
- Rationale: external systems store these URLs for years, clean paths are standard for persistent identifiers
- Requires 404.html redirect trick for GitHub Pages (no server-side routing)
- Fallback: also accept `?id=` and `#` patterns

### Requirements distilled
- Full spec was in `features/042-lemma-pages.md` (removed after completion; see Issue #55 for re-documentation)
- Scope: single `lemma/index.html` page that loads authority + corpus index, renders lemma data
- Out of scope for v1: MWB backlinks (needs their ID mapping), inline attestations, JSON-LD

---

## 2026-02-24 — Issue Triage & API Planning

**Trigger:** 23 open issues accumulated without consistent labeling. Most are TEI data-wrangling, not frontend work — but labels didn't reflect that. Also: MWB collaboration and researcher demand created need for a data API.

### Issue triage (#44)
- Analyzed all 23 open issues, read every body
- Created 11 new labels for domain (`data:tei-wrangling`, `data:metadata`, `data:provenance`, `frontend`, `pipeline`), effort (`effort:small/medium/large`), and readiness (`claude-ready`, `depends-on-human`, `needs-clarification`)
- Removed 5 unused GitHub default labels
- Applied labels to all 23 issues
- Created assessment matrix issue (#44) with recommended work order
- Key finding: 13 of 23 issues are data/TEI work, only 7 touch frontend

### Branch housekeeping
- `feature/wenzelsbibel-ingest` existed locally but was never pushed to remote
- Pushed to origin with tracking

### Static JSON API issue (#45)
- Created issue for FAIR-compliant static JSON API on GitHub Pages
- Design decisions: no backend (static pre-built JSON files), no versioning, no auth, JSON only
- New build script `scripts/build-api.py` to generate `/api/` folder from existing indexes
- Includes API docs page at `/api/index.html`
- Connects to #42 (persistent lemma pages — provides the data layer)
- Data exploration: 43,750 lemmata, 210 persons, 583 works, 567 concepts, 615 genres, 90 names, 666 texts
- Open design question: how to handle ~46k individual files (lemmata alone = 43,750 files)

### Promptotyping docs housekeeping
- Reviewed all 7 stable docs for staleness
- Found stale file paths in ARCHITECTURE.MD and DEVELOPMENT.MD (referenced pre-Phase-0 structure: `js/`, `lib/`, `css/` instead of `assets/`)
- Fixed path references to match current `assets/{css,js,images}` structure
- Updated DEVELOPMENT.MD directory tree and historical branches list

---

## 2026-02-24 — Quick Wins: #21, #46, #45 doc update

**Trigger:** Tackling the easiest issues from the triage matrix (#44) to build momentum.

### #21: "Konzepte" → "Begriffe" rename
- Renamed all user-facing German strings from "Konzepte" to "Begriffe" across 11 source files
- English code identifiers (`concepts`, `conceptIds`, filenames) untouched — issue only about UI terminology
- Updated Playwright test selectors/names to match new button text
- Updated USER-GUIDE, playground readme, ROADMAP
- Savepoint: `8012a42`

### #46: Merge Lemma-Suche into Multi-Lemma-Suche
- Removed redundant "Lemma-Suche" button from playground (used `prompt()` dialog, didn't work properly)
- Multi-Lemma-Suche already handles single-lemma queries — no feature loss
- Removed dead handler registration, dead test, updated docs
- Renumbered remaining TEI analysis tests
- Savepoint: `dd0a3c3`

---

## 2026-02-24 — Provenance Batch: #36 model + #35, #37, #38, #39, #40

**Trigger:** ~55 TEI files lack structured documentation of their digital intermediary sources.

### #36: Provenance model design (Promptotyping Phase 1-3)
- Researched TEI P5 Ch. 2.2.7/2.2.8, DTA Basisformat, other DH projects
- Evaluated 4 approaches (flat listBibl, nested relatedItem, biblFull, flat + @corresp)
- Decided: **Approach D** — flat `<listBibl>` with `@corresp` cross-references
- New element: `<bibl type="digitalIntermediary">` (not `<biblStruct>` — keeps all existing code safe)
- Design rationale and full template: ADR-012 in DECISIONS.MD
- Verified no impact on build scripts or JS (all existing code queries `tei:biblStruct` only)
- Savepoint: `164f7a9`

### Implementation: 5 provider groups, 50 files total
- **#35 Klug** (18 files): ABS, BRIX, DES2, FWWB, GSP, HUB1-3, KBL3-4, KDO, KME, KSA1, MBS1-2, MBS5, MBS7, MSB1 → `25f730a`
- **#37 Harsch/Augustana** (24 of 25 files, ASL not in repo): AC3, APO, ASG, ATF, CLV, DAH, DIO, EB1-2, EHB, FAN, FLG, HNI, JEW, LUU, MNA, MSP, NAR, NST, PRJ, REG, SBF, WGA, WGI → `b92c18f`
- **#38 TITUS** (4 files): AXS, KVM, RCC, SAX → `58e3811`
- **#39 Gloning** (8 files): ABG, AXK, ESB, HMRG + dual provenance FWWB, GSP, KDO, KME → `c688ec1`
- **#40 Virginia/Trier** (4 of 5 files, KMH not in repo): DL2, BVH, BRZ, MKN → `a7d2e3c`

### Dual provenance (FWWB, GSP, KDO, KME)
- These have chain: Print → Gloning → Klug → MHDBDB TEI
- Two `<bibl>` elements: Gloning `@corresp` → print edition, Klug `@corresp` → Gloning etext
- Order in `<listBibl>`: `<biblStruct>` → `<bibl>` Gloning → `<bibl>` Klug

### Missing files
- ASL.tei.xml (#37) and KMH.tei.xml (#40) not found in repository — noted in issues

### Code impact analysis
- `build-authority-index.py`: queries `tei:biblStruct` only → **no impact**
- `build-corpus-index.py`: processes `<body>` only → **no impact**
- `sync_tei_headers.py`: removes/re-adds `tei:biblStruct` only → **no impact** (our `<bibl>` survives)
- JS rendering: reads `biblStructs` from JSON index → **no impact**

---

## 2026-02-27 — Documentation Health Check (Issue #49)

**Trigger:** Quarterly health check + changes since 2026-02-24 (asset restructuring, test improvements, new feature docs).

Flow/Algorithms/XPaths: PASS. Rebuild feasibility: Search YELLOW, Build YELLOW, Renderer GREEN (upgraded), **Lemma Pages RED** (new — no feature doc), Cache YELLOW-GREEN. Actions: #54 (deduplication docs), #55 (lemma pages docs). Full report: [Issue #49 comment](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/49#issuecomment-3971322787).

**Process decision:** Health check reports are temporal artifacts — full report goes as Issue #49 comment, scorecard summary goes here in JOURNAL.md, action items become separate Issues. No .md files in `docs/`. See Issue #49 "Output Convention" section.

---

## 2026-02-24 — Quick Wins: #21, #46, #45 doc update

**Trigger:** Tackling the easiest issues from the triage matrix (#44) to build momentum.

### #45 planning doc: resolved open design question
- Ran sizing analysis against actual indexes: lemma files average 311 B, total ~23 MB gzipped regardless of approach
- Decided **hybrid file strategy**: individual files for persons/works/concepts/genres/names/texts (~2,700 files), lemmata stay bundled
- Added full API schemas (text metadata, index files, root index), corpus enrichment decision (no), build integration (manual + npm alias)
- Updated issue #45 body on GitHub with planning doc link and revised design
- Updated matrix (#44) to include #45 and #46, moved closed #42 to "Recently Closed"

---

## 2026-04-07 — TEI Model Consolidation (Issue #32)

**Trigger:** Katharina will externe Daten (ReM, CoReMA, weitere) aufnehmen. Voraussetzung: konsolidiertes TEI-Modell mit formalem Schema als Validierungsgate.

### Strategieentscheidung: Hybrid-Ansatz
- Weder "Fixes zuerst" noch "Schema zuerst" — stattdessen 3+1 Phasen:
  - **Phase 0:** Soll-Modell (docs/TEI-MODEL.md) — Entwurf fertig
  - **Phase 1:** Strukturelle Fixes (#30) am Soll-Modell ausgerichtet
  - **Phase 3:** RELAX NG Schema (schema/mhdbdb.rnc)
  - **Phase 2:** Attribut-Migration — aufgeschoben bis WZB-Merge
- Branch: `feature/tei-model-32`

### TEI P5 Validierung: Ueberraschende Ergebnisse
- `schema/tei_all.rng` (TEI P5 4.11.0) heruntergeladen und gegen Korpus validiert
- **0/100 Dateien valide** — aber nur 2 Fehlertypen:
  1. `@meaningRef` (100% der Dateien) — nicht-Standard-Attribut, blockiert Validierung
  2. `@wordRef` (15% der Dateien) — nicht-Standard, bereits deprecated
- **Ueberraschung:** `@lemmaRef` IST Standard-TEI (att.linguistic seit v3.3.0/2018) — keine Migration noetig!
- `@meaningRef` → `@ana` ist die einzige Migration fuer TEI-Konformanz (einfaches Batch-Rename)
- Zusaetzlich entdeckt: `<monogr>` Element-Reihenfolge falsch in einigen Dateien (author nach title)

### Entschiedene Policy-Fragen (keine offenen Punkte mehr)
- **POS-Tagset:** 19-Tag-System aus SKILL.md ist kanonisch (DET nicht ART, CCNJ/SCNJ nicht CNJ)
- **`<hi rend="initial">`:** Beibehalten (Korpus-Konvention, 655/675 Dateien)
- **`<l>` vs `<lb/>`:** 18 Prosa-Texte migrieren, 3 korrigiert als Vers (HMT, APO, HH)
- **`<seg type="pc">`:** Langfristig zu `<pc>` migrieren (TEI P5 Standard-Element)
- **`@wordRef`:** Deprecated, wird entfernt (kein Code liest es)
- **Attribut-Migration `@lemmaRef`→`@lemma`:** Aufgeschoben (Kosten >> Nutzen, WZB-Konflikt)

### Neue Artefakte
- `docs/TEI-MODEL.md` — Soll-Modell mit IST/SOLL-Vergleichen, Validierungsbaseline
- `schema/mhdbdb-example.xml` — Maximalbeispiel, validiert gegen tei_all.rng
- `scripts/data-wrangling/tei-model/tei-audit.json` + `TEI-AUDIT-REPORT.md` — Korpus-Audit (76 Elementtypen, 9.3M `<w>`)
- `schema/tei_all.rng` — TEI P5 4.11.0 Referenzschema

### Vergleichsprojekte recherchiert
- DTABf (Gold-Standard historische Texte): Strikte TEI-Untermenge, ~80 Elemente, Standoff-Annotation
- MENOTA (Mittelalterliche Texte): Custom-Namespace `me:` fuer Erweiterungen, 3 Transkriptionsebenen
- ReM (Referenzkorpus MHG): HiTS-Tagset, Multi-Layer-Annotation

---

## 2026-04-09 16:00 — handoff

**Summary:** Alle TEI-Modell-Entscheidungen abgeschlossen, Korpus-Audit (666 Dateien, 12.7M Elemente) durchgefuehrt, Maximalbeispiel mit allen 7 div/@type-Werten erstellt und gegen tei_all.rng validiert. 5-Phasen-Implementierungsplan geschrieben (A-E). Issue #44 mit TEI-Relevanz-Analyse aktualisiert, Issue #49 Health-Check gepostet, Issue #67 (Abbreviaturen) erstellt. Schema-Strategie entschieden: RNC Source + RNG generiert, Zwei-Stufen-Validierung, kein ODD.

**Phase:** Distillation abgeschlossen → Implementation bereit. Alle Promptotyping-Docs aktuell:
- `docs/TEI-MODEL.md` — Soll-Modell (0 offene Entscheidungen)
- `scripts/data-wrangling/tei-model/IMPLEMENTATION-PLAN.md` — 5-Phasen-Plan
- `schema/mhdbdb-example.xml` — validiert gegen tei_all.rng
- `scripts/data-wrangling/tei-model/tei-audit.json` + `TEI-AUDIT-REPORT.md` — Korpus-Audit
- `scripts/data-wrangling/tei-model/audit-tei-corpus.py` — Audit-Script
- `scripts/data-wrangling/tei-model/TEXT_DATA_TABLE.xlsx` — Metadaten-Quelle (Issue #67)

**Open issues:**
- Katharinas Entscheidungen zu FLG/FLG1 Zusammenziehen und PL1-3 Zusammenziehen stehen als Empfehlungen (nicht zusammenziehen), aber keine explizite Bestaetigung
- `@meaningRef` → `@ana` JS-Anpassung: 8 Stellen verifiziert, aber Playground-Funktionalitaet nach Migration nicht live getestet
- `<pc join="right">` fuer oeffnende Klammern: Audit der tatsaechlichen Interpunktionszeichen im Korpus fehlt noch (vor Phase C1 noetig)
- TEXT_DATA_TABLE.xlsx DESCRIPTION-Parsing (Issue #67): 124 Texte identifiziert, Pattern-Erkennung noch nicht implementiert

**Next steps:**
1. Naechste Session: `/promptotyping orient` → liest IMPLEMENTATION-PLAN.md
2. Phase A starten (sichere XML-Migrationen, kein Code-Impact)
3. Phase A1 zuerst: `migrate-div-types.py` (div/@type Renames + LZT div→lg)
4. Nach Phase A: Audit erneut laufen → Diff pruefen
5. Phase B: @meaningRef→@ana + JS-Fix, dann @wordRef→@corresp

---

## 2026-04-09 18:30 — handoff

**Summary:** Komplette TEI-Migration implementiert: Korpus (Phases A-E) + Authority Files tei_all-konform + Soll-Modell fuer Authority Files. 15M+ Attribut-/Element-Transformationen ueber 675 Korpusdateien. 9 disamb-Dateien in Base gemergt (+35k POS). Corpus-Index rebuilt (XPath-Performance-Bug gefixt). Authority Files Audit + Implementation Plan geschrieben (Phases F-K). Build-Scripts prophylaktisch optimiert (XPath→iter). enhance_works_with_zotero.py fuer relatedItem-Wrapper aktualisiert.

**Phase:** Implementation (Iteration). Korpus-Migration abgeschlossen, Authority-Migration geplant.

Aktuelle Docs:
- `docs/TEI-MODEL.md` — Korpus Soll-Modell (implementiert)
- `docs/TEI-MODEL-AUTH-FILES.md` — Authority Soll-Modell (noch zu implementieren)
- `scripts/data-wrangling/tei-model/IMPLEMENTATION-PLAN.md` — Korpus-Plan (Phases A-E done)
- `scripts/data-wrangling/tei-model/authority-files/IMPLEMENTATION-PLAN.md` — Authority-Plan (Phases F-K pending)
- `schema/mhdbdb.rnc` + `mhdbdb-authority.rnc` + `mhdbdb-example.xml` — Schemas

Commits auf `feature/tei-model-32` (seit letztem handoff):
- `415e7014` Phase A: div/@type, monogr, typos, dates, langUsage
- `3ec3a5f1` Phase B: @meaningRef→@ana (5.9M), @wordRef→@corresp (7.5M)
- `3720536c` Phase C: seg→pc (1.4M), l→lb 18 files (86k)
- `ad739547` Phase D: normalization from XLSX (663 files)
- `d8bfef08` Phase E: RELAX NG schema + validation
- Diverse Fixes: stale refs, schema move, docs, disamb merge, authority tei_all fixes
- `d7238162` Corpus index XPath→iter performance fix
- `fff00136` Corpus index rebuild
- `6639e723` Build-Scripts: XPath→iter + Zotero relatedItem

**Open issues:**
- Katharinas FLG/FLG1 + PL1-3 Entscheidungen: bestaetigt per Signal ("sieht das gleich")
- `person_schweizer_anonymus`: 1 verwaiste Referenz in works.xml — Person anlegen oder Ref aendern? (Katharina fragen)
- `work_6` (Frauendienst): keine biblStruct — manuell nachpflegen (Katharina/Chris)
- `docs/TEI-MODEL.md` Section 10 (Validierungsbaseline): beschreibt noch Pre-Migration-Zustand
- Browser-Test nach Merge: `<pc>` Rendering + `<lb/>` in Prosa-Texten visuell pruefen
- Wenzelsbibel-Branch hat Merge-Konflikte (alte Attributnamen in Docs)

**Next steps:**
1. **PR #1: Korpus-Migration** — `feature/tei-model-32` → `main` (Phases A-E + Index + Build-Fixes)
2. **Authority-Migration** (Phases G-K) — entweder auf demselben Branch oder neuem Branch
   - G1: Genre-Refs entlabeln (3422 refs → ptr)
   - G2: Externe IDs unwrappen + GND casing
   - H1: persons.xml Works-Links entfernen
   - H2: UUID-IDs migrieren (4 Personen, Cascade minimal)
   - I1: Verwaiste Referenzen bereinigen (226 total)
   - J1: build-authority-index.py Genre-Reader umbauen (Genre-Text aus genres.xml loesen)
   - K: Schema + Validierung
3. **PR #2: Authority-Migration** — nach Abschluss von Phases G-K
4. Authority-Index rebuild (erst nach PR #2)

---

## 2026-04-10 — PR #1 merged + post-merge cleanup

**PR #69** (`feature/tei-model-32` → `main`): Korpus-Migration gemergt. 34 Commits, 731 Dateien, ~33M Zeilen.

### Code-Review Fixes (vor Merge)
- `tei-manager.js`: `resolveConceptReferences()` checkte nur `@conceptRef`, nicht `@ana` — gefixt
- `tei-text-reader.js`: `<pc>` in `processChildren` fehlte `<span class="punctuation">` Wrapper — gefixt
- `enhance_works_with_zotero.py`: `etree.fromstring(etree.tostring())` → `deepcopy()` — gefixt

### Post-Merge Cleanup
- `build-corpus-index.py`: `import time` nach oben, toter `not lemma_ref` Guard entfernt
- `TEI-MODEL.md` Section 10: Validierungsbaseline auf Post-Migration-Zustand aktualisiert (675/675 valide, Version 1.0.0)
- `tei-text-reader.js`: Dual-Rendering-Path Refactor — duplizierte Element-Logik (switch + if-chain) zu einer einzigen `_renderElement` Closure zusammengefuehrt. 27/27 Playwright-Tests bestehen.

### Playwright-Tests: 49/49 funktionale Tests bestanden
Keine Regressionen durch Migration. 20 pre-existierende Fehler (relative URL Config, #43) weiterhin offen.

### Authority-Migration laeuft parallel (Phases G-K)
Zweite Claude-Instanz arbeitet an G1 (Genre-Refs) + G2 (Externe IDs). Aenderungen auf `feature/tei-model-32` Branch.

---

## 2026-04-10 12:30 — handoff

**Summary:** Komplette Authority-Files-Migration (Phases F-K) implementiert. 7/7 Dateien valide gegen tei_all.rng + mhdbdb-authority.rnc. Authority-Index v1.2.0 rebuilt. Zotero-Script 4 Bugs gefixt. Frauendienst/Frauenbuch-Split (work_6/work_7) auf Basis von Katharinas Klassifizierung + eigener Recherche. Schweizer Anonymus als Person angelegt (GND 103130276). Schema-Examples fuer alle 7 Authority-File-Typen erstellt. 120/121 Playwright-Tests bestanden (1 flaky: Corpus-Lade-Timing).

**Phase:** Implementation abgeschlossen. Wartet auf PR-Erstellung (Kollege arbeitet noch am Korpus-Testing auf demselben Branch).

Aktuelle Docs:
- `docs/TEI-MODEL.md` — Section 10 erweitert: Authority-Files Validierungsbaseline
- `docs/TEI-MODEL-AUTH-FILES.md` — Status: Implementiert
- `scripts/data-wrangling/tei-model/authority-files/IMPLEMENTATION-PLAN.md` — Phases F-K alle done
- `schema/mhdbdb-authority.rnc` + `.rng` — SOLL-Modell Schema
- `schema/examples/authority-*.example.xml` — 7 validierte Beispieldateien
- `schema/examples/corpus.example.tei.xml` — Korpus-Beispiel (verschoben aus schema/)

Geaenderte Dateien (15 modified + 15 untracked, nicht committed):
- authority-files: works.xml, persons.xml, lexicon.xml, variants.xml
- data/authority-index.json.gz (v1.2.0)
- scripts: build-authority-index.py, enhance_works_with_zotero.py
- schema: mhdbdb-authority.rnc/.rng, examples/*
- docs: TEI-MODEL.md, TEI-MODEL-AUTH-FILES.md
- tei/LUU.tei.xml (UUID cascade)
- 6 neue Migrations-Scripts in scripts/data-wrangling/tei-model/authority-files/

**Open issues:**
- PR #69 Code-Review laeuft noch auf GitHub — Kollege testet Korpus-Seite
- work_7 (Frauenbuch): Katharina hat Genres bestaetigt (Minnelehre + Streitgedicht), aber "Frauenbuch und Frauendienst haengen zusammen" braucht evtl. noch Recherche fuer die Doku
- `docs/TEI-MODEL.md` Section 10 Authority-Index-Version: im Versionierungsblock steht 1.2.0, aber der Build-Script-Kommentar sagt "1.2.0" — konsistent, aber bei naechstem Authority-Rebuild pruefen
- Post-Migration Audit: 0 orphans, 0 denormalized — sauber, Audit-Report aktualisiert
- Persons with works: 209→207 nach Migration (2 Personen hatten stale listBibl ohne tatsaechliche Author-Referenz)

**Next steps:**
1. Warten bis Kollege mit Korpus-Testing fertig ist
2. PR erstellen: `feature/tei-model-32` → `main` (Authority-Migration)
3. Optional: Migrations-Scripts aufraeumen (gemeinsam mit User)

---

## 2026-04-10 15:00 — handoff

**Summary:** Zusaetzlich zur Authority-Migration: 5 Issues geschlossen (#60 Parzival Chapters, #61 Textfilter multi-word, #67 bereits erledigt, #53 Korpussuche UX, #29 Stricker-Texte). #70 (pc join Rendering) gefixt aber nicht closeable vor Merge. Korpus-Schema (`mhdbdb.rnc`) vom Kollegen fertiggestellt und reviewed. Schema README geschrieben (Kollege). `div type="parallel"` in 7 Stricker-Texten → `section` korrigiert (4 echte Parallelueberlieferungen bleiben). Docs-Konsistenz (DATA-MODEL.MD, ROADMAP.md, JOURNAL.md) aktualisiert. Nav "Korpus" → "Korpussuche" in allen 4 HTML-Dateien (index, korpus, lemma, playground).

**Phase:** PR-ready. Wartet auf Corpus-Index Rebuild nach TEI-Aenderungen (PZ, DKK, PRL, Stricker).

Geaenderte Dateien seit letztem Handoff:
- `assets/js/app.js` — #53 Empty State + #61 Textfilter
- `assets/js/rendering/tei-text-reader.js` — #70 pc join rendering
- `index.html`, `korpus.html`, `lemma/index.html`, `playground/index.html` — #53 Nav-Umbenennung
- `tei/PZ.tei.xml` — #60 827 Chapter-Divs
- `tei/DKK.tei.xml`, `tei/PRL.tei.xml` — #29 parallel→section
- `tei/DES2.tei.xml`, `tei/DGE.tei.xml`, `tei/DJEM.tei.xml`, `tei/DJUM.tei.xml`, `tei/DUB.tei.xml` — parallel→section
- `schema/mhdbdb.rnc`, `schema/mhdbdb.rng` — Korpus-Schema (Kollege)
- `schema/README.md` — Schema-Dokumentation (Kollege + Review)
- `docs/DATA-MODEL.MD`, `docs/ROADMAP.md` — Konsistenz-Fixes

**Open:**
- Corpus-Index Rebuild noetig (PZ + DKK/Stricker Strukturaenderungen)
- #70 (pc join) Issue noch offen — erst nach Merge closebar
- #20 (Lesbarkeit/CSS) und #52 (Authority Files Karte) noch offen
