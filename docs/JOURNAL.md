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
- See [features/042-lemma-pages.md](features/042-lemma-pages.md) for full spec
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

### #45 planning doc: resolved open design question
- Ran sizing analysis against actual indexes: lemma files average 311 B, total ~23 MB gzipped regardless of approach
- Decided **hybrid file strategy**: individual files for persons/works/concepts/genres/names/texts (~2,700 files), lemmata stay bundled
- Added full API schemas (text metadata, index files, root index), corpus enrichment decision (no), build integration (manual + npm alias)
- Updated issue #45 body on GitHub with planning doc link and revised design
- Updated matrix (#44) to include #45 and #46, moved closed #42 to "Recently Closed"
