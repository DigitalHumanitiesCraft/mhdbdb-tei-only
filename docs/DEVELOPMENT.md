# Development

This document describes the development workflow, build processes, and deployment procedures for the MHDBDB TEI Repository.

## Prerequisites

- **Node.js 16+** (for npm scripts and testing)
- **Python 3.13+** with lxml (for building pre-built indexes)
- **Web Browser** (Chrome/Chromium preferred for testing)
- **Git** (for version control)

**Note:** Pre-built indexes are included in repository, so Python is only needed if modifying source XML files.

## Project Setup

```bash
# Clone repository
git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git
cd mhdbdb-tei-only

# Install dependencies
npm install

# Start development server
npm run serve
# Opens on http://localhost:8080
```

### Directory Structure

```
mhdbdb-tei-only/
├── assets/                # Main site static assets
│   ├── css/               # Stylesheets (korpus.css, tailwind)
│   ├── js/                # Main site JavaScript
│   │   ├── app.js         # Application entry point
│   │   ├── site-chrome.js # Shared nav/footer behavior (mobile menu, current-year, clear-site-data), loaded on every page
│   │   ├── search/        # Search engine
│   │   ├── rendering/     # TEI text reader, text renderer
│   │   ├── storage/       # TEI cache manager
│   │   └── lib/           # Shared utilities (corpus-loader, text-normalizer, lemma-match)
│   └── images/            # Static images
├── includes/              # Nav/footer/matomo single-source partials (_nav.html, _footer.html, _matomo.html), build-injected by scripts/build-pages.py
├── authority-files/       # 8 XML authority files (incl. contributors.xml)
├── tei/                   # TEI corpus files
├── data/                  # Pre-built indexes (generated)
├── scripts/               # Python build scripts
├── playground/            # Playground interface (self-contained sub-app)
├── lemma/                 # Persistent lemma pages (Issue #42)
├── publications/          # Project outputs (blog posts, reports)
├── testing/               # Playwright tests
├── docs/                  # Documentation hub
├── schema/                # RELAX NG schemas (mhdbdb.rnc, mhdbdb-authority.rnc, examples)
├── index.html             # Landing page
├── korpus.html            # Main site search + reading view
├── woerterbuch.html       # Dictionary: A–Z register of all lemmata (#117)
├── impressum.html         # Legal notice (#62)
├── barrierefreiheit.html  # Accessibility statement
├── hilfe.html             # Help hub (entry point)
├── hilfe-korpussuche.html # Corpus search guide
├── hilfe-playground.html  # Playground guide
├── hilfe-daten.html       # What the data is, for readers
├── hilfe-daten-beitragen.html  # Schema conversion guide for TEI contributors (#68 part 1)
├── hilfe-schema.html      # Normative TEI schema + Prism examples (#78)
└── 404.html               # Lemma-page redirect (GitHub-Pages-Workaround)
```

## Building Pre-Built Indexes

Pre-built indexes are included in repository. Rebuild only when modifying source XML files.

### When to Rebuild

> **Canonical, ordered step sequence:** [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle). The list here is only the short form of the triggers.

**Authority Index:**
- Authority XML files modified
- Cross-references added/changed
- New GND/Wikidata identifiers

**Corpus Index:**
- TEI files added/removed/modified
- Word annotations changed

**Variants:**
- TEI corpus modified (new orthographic forms)
- Usually paired with corpus index rebuild

### Build Commands

```bash
# Build authority index (consumes authority-files/variants.xml, no extraction step)
python scripts/build-authority-index.py
# Output: data/authority-index.json.gz (~3 MB)

# Build corpus index
python scripts/build-corpus-index.py
# Output: data/corpus-index.json.gz (~40 MB, v4.1.x)

# Validate indices
python scripts/validate-indices.py

# Build static JSON API from the two indexes (#45), alias: npm run build:api
python scripts/build-api.py
# Output: api/ (2,742 plain JSON files, ~14 MB). Single-shot target, needs a clean data/.
# Run build:api ALONE to regenerate only the API from the already-committed indexes
# (no index rebuild). To rebuild the indexes AND the API together (kept in lockstep),
# use `npm run build:data` / `npm run build` (see below).
```

### Frontend Build Commands

```bash
# Rebuild the purged Tailwind stylesheet (run after new utility classes appear in HTML/JS)
npm run build:css        # assets/css/tailwind-input.css → assets/css/tailwind-output.css (--minify)

# Bundle vendored JS dependencies (PrismJS, pako, Dexie: no runtime CDN dependencies,
# sources pinned via package.json/package-lock, output committed under assets/vendor/)
npm run build:vendor     # node scripts/build-vendor.js

# Re-inject the shared nav + footer into every registered page after editing
# includes/_nav.html or includes/_footer.html (NOT the pages directly):
python scripts/build-pages.py            # rewrite changed pages (idempotent)
python scripts/build-pages.py --check    # exit 1 if any page is out of sync (drift gate)

# Build the full derived layer in dependency order: corpus index, variants.xml, authority index, API
npm run build:data       # build:corpus && extract-variants --apply && build:authority && build-api --allow-dirty
# build-api runs with --allow-dirty here because the just-rebuilt indexes in data/ are still uncommitted (dirty)

# Aggregate: CSS + vendor + the full data chain (npm run build now includes build:data)
npm run build            # build:css && build:vendor && build:data
```

**Note on variants:** `authority-files/variants.xml` is corpus-derived. Regenerate it with `python scripts/sync/extract-variants.py --apply` after the corpus gains new orthographic forms, then rebuild the authority index and bump its version. Full step sequence: [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle).

### Version Increment

After significant changes, increment version in build script to force browser cache invalidation:

```python
# In build-authority-index.py / build-corpus-index.py the version sits as an
# inline dict literal inside the index, e.g. 'version': '1.4.0' (there is NO
# VERSION constant). It has to be bumped together with the matching constant in
# assets/js/lib/corpus-loader.js (INDEX_VERSION / AUTHORITY_INDEX_VERSION);
# check-index-versions.py enforces parity. Current state: TEI-MODEL.md §11.
```

## Testing

### Playwright Tests

```bash
npm test              # Run all tests (headless), 5.0 to 5.3 min (6 workers)
npm run test:changed  # Only specs touched since origin/main
npm run test:quick    # Three specs as a smoke test, 22 tests (main-site, playground, corpus)
npm run test:ui       # Interactive mode
npm run test:debug    # Debug with breakpoints
npm run test:headed   # Visible browser
npm run report        # View HTML report
```

**The first three run through `scripts/run-tests.js`, and its last line is the result.** The question "did the suite pass?" used to have three answers that lie in different ways, and the issue playbook had grown four separate rules around them (§2.1, since 2026-08-05 merged into rule 6). The wrapper answers it once: it deletes the stale `report.json` before the run, refuses to start when port 8080 is served by a different working tree, sets `PW_TEST_HTML_REPORT_OPEN=never`, and builds its verdict from `testing/test-results/report.json` rather than from the console line or the exit code. On a run without filters it also compares the spec files on disk against the files that appear in the report, so a run whose population silently shrank comes out red instead of green with a smaller number. Both sides of that comparison are measured at runtime; there is no maintained expected count that could drift.

The verdict line names the test count, the file count and the working tree that was measured, and belongs in the PR verification block as it stands. Exit codes: 0 green, 1 red, 2 the run never happened (no report written, or a foreign server on 8080). `test:ui`, `test:debug` and `test:headed` stay unwrapped, they run under supervision and write no usable report.

**Python interpreter (#318).** Two specs call Python (`normalization-parity`, `position-parity`), and so do the npm build scripts. The interpreter is searched for, not guessed: `scripts/python-bin.js` tries `python3.13`, `python3`, `python` and `py` in that order and takes the first one reporting 3.13 or newer. If it finds none, that is a hard error listing what was tried, not a silent skip. Before that, `python3.13` was a fixed string in the calls; under Windows that name only exists for an installation from the Microsoft Store, while the python.org installer conversely does not put `python.exe` on the PATH by default and registers only `py`. Deviating setups (venv, Conda) point `MHDBDB_PYTHON` at the path of the real `python.exe`, not at a `.bat` shim:

```bash
MHDBDB_PYTHON=.venv/bin/python npm test          # Bash
$env:MHDBDB_PYTHON = ".venv\Scripts\python.exe"  # PowerShell, then npm test
```

Positional arguments in Playwright are **regular expressions against the file path**, not file names. Unanchored, the filter `corpus.spec.js` in `test:quick` therefore also pulled in `playground-corpus.spec.js` and `search-with-corpus.spec.js`: in the July 2026 state 47 tests in five files instead of 29 in three (today it is 22 in three, see above), and among them of all things the file with the most `waitForTimeout` calls. Since #323 the filters are anchored at the end with `$` and disciplined at the front by the prefix `tests.`. A `^` would be wrong and would find nothing at all: Playwright matches against the **absolute** path, measured (`^main-site\.spec\.js$` and `^tests.main-site\.spec\.js$` both yield zero tests, `tests.main-site\.spec\.js$` yields 14). Whoever changes the selection counts it with `-- --list`; that does not start the `webServer` and costs seconds.

`test:changed` (`--only-changed=origin/main`) is the everyday command while working on a branch: only what the branch touched runs. **Before pushing, `npm test` stays mandatory.** `--only-changed` follows the Node imports of the specs, and since #318 there is exactly one: both parity specs import `scripts/python-bin.js`. A change there therefore pulls them into the run correctly, unlike everything else in the table below. The rest of the project code is reached at runtime, not imported: site code through the browser (`await import('/assets/js/…')` inside `page.evaluate`), Python through `execFileSync`, fixtures and vendored files through the path. The command is blind to:

| What | tested by | how it is reached |
|---|---|---|
| `assets/js/`, `playground/js/`, `tei/`, `data/` | almost every spec | browser, `localhost:8080` |
| `scripts/mhg_normalizer.py` | `normalization-parity.spec.js` | `execFileSync` |
| `scripts/build-corpus-index.py` | `position-parity.spec.js` | `importlib`, from inside the helper |
| `testing/helpers/extract_word_positions.py` | `position-parity.spec.js` | `execFileSync` |
| `tei/PL1.tei.xml`, `tei/OVG.tei.xml` | `position-parity.spec.js` | path (Python) and browser |
| `testing/fixtures/*.tei.xml` | `position-parity.spec.js` | path |
| `assets/vendor/`, all HTML pages | `vendor.spec.js` | `readdirSync`/`readFileSync` |

The Python rows are the nastiest, because there one expects the opposite. `scripts/mhg_normalizer.py` and `scripts/build-corpus-index.py` are one half each of the parity promises in the hard constraints in `CLAUDE.md`, and the two `*-parity.spec.js` are their guards. For the build script the path is additionally hidden: `extract_word_positions.py` is a shim that loads the real `extract_word_data()` via `importlib` instead of reimplementing it. Whoever changes the Python side and runs `test:changed` gets zero specs, which is precisely not the test that checks the change (measured for `mhg_normalizer.py`).

Particularly relevant for this repository are `tei/` and `data/`: with ingest running these are the most frequently changed directories, and both are blind because they are loaded over `localhost:8080`. Two pitfalls around the ref: `origin/main` has to exist (it does not in a shallow clone), and it has to be current. Whoever has not fetched for a while compares against an old state and gets too many or too few specs, so run `git fetch origin main` first. If the selection stays empty, the command ends with exit 0 (measured, Playwright 1.55.1): `--pass-with-no-tests` is not needed.

**Test configuration:** `testing/playwright.config.js`
- Always use `npm test` – never `npx playwright test` from the project root (config and `baseURL` live in `testing/`, and only the npm route goes through the wrapper that forms the verdict)
- Automated web server startup (port 8080)
- Headless Chrome with `--disable-web-security`
- 60-second timeout per test
- **6 workers locally, 2 in CI** (#323), overridable on weaker machines with `npm test -- --workers=2`: 20.4 min with one worker against 5.0 to 5.3 min with six, over the same 276 tests, five runs. The reasoning for both numbers sits as a comment in the config; in short, the bottleneck is the single-threaded `http-server` and the Chromium heap, not the core count, and standard CI runners have too few vCPUs for six
- **`retries: 1`** (everywhere, CI included) plus `failOnFlakyTests: true`. The retry exists only so that a timing flake under six workers leaves a trace behind; without `failOnFlakyTests` it would also prettify the run, because Playwright ends with exit 0 as soon as a test turns green on the second attempt. With the option the run stays red and the trace file is there all the same
- **`fullyParallel: false` is deliberate.** `search-normalization.spec.js` shares one page created in `beforeAll` across all tests of the file, in order to load the index once instead of fourteen times. Test parallelism would not break the page (Playwright runs `beforeAll` again per worker), but it would break the saving: the index would be loaded up to six times

### Test File Inventory

Completeness against `testing/tests/` is gated by `scripts/audit/check-doc-inventories.py` (runs in `no-cdn-check.yml`, callable locally without dependencies; the same script also checks the script table further down). A new spec without a row here turns CI red: this table is the only place stating what a spec is for. Until #329 ten out of thirty were missing.

| File | Category | What it tests |
|------|----------|--------------|
| `main-site.spec.js` | Main site | Landing page, search page loading, search results, reading view |
| `search-engine.spec.js` | Main site | SearchEngine class: resolution, filtering, deduplication |
| `search-normalization.spec.js` | Main site | MHG normalization functions in browser context |
| `search-with-corpus.spec.js` | Main site | Search against real corpus data |
| `reading-view.spec.js` | Main site | TEI reading view rendering, highlighting, navigation |
| `results-table.spec.js` | Main site | Corpus search results table view (#114): columns, sorting |
| `tei-caching.spec.js` | Main site | IndexedDB TEI cache behavior |
| `error-handling.spec.js` | Main site | Graceful error handling |
| `woerterbuch.spec.js` | Main site | A–Z register over the authority index, pagination, deep links (#117) |
| `lemma-page.spec.js` | Lemma pages | URL parsing, data rendering, external links |
| `playground.spec.js` | Playground | Start page loads (title, `#authorityOverview`), reset button visible, modules load without `console.error`/`pageerror` (#331). Since #326 only these three tests |
| `playground-authority-index.spec.js` | Playground | Authority index loading, data structure integrity |
| `playground-corpus.spec.js` | Playground | Corpus index loading, search functions |
| `concept-distribution.spec.js` | Playground | Concept distribution analysis (concept → senses → lemmata → texts) |
| `cooccurrence-ranking.spec.js` | Playground | Co-occurrence ranking and homograph resolution of the multi-lemma search (#163/#164) |
| `proximity-and-resolution.spec.js` | Playground | Proximity window for three or more lemmata, overlap dedup, lemma resolution (#169) |
| `multi-lemma-verse.spec.js` | Playground | Search mode „Im selben Vers" over `lineStarts[]`/`lineEnds[]` (#106) |
| `rhyme-dictionary.spec.js` | Playground | Rhyme dictionary: verse-ending scan plus suffix heuristic (#106) |
| `verse-ending-profile.spec.js` | Playground | Verse-ending profile: top-N lemmata at verse ends, scope selector (#106) |
| `hapax-legomena.spec.js` | Playground | Corpus-wide hapax/dis/tris aggregation, filter toolbar, detail panel (#196) |
| `word-component-search.spec.js` | Playground | Word-component mode in the lemma explorer, for research on compounds (#239) |
| `naming-explorer.spec.js` | Playground | Character naming: route, work/character selection, category tabs, mandatory attribution (#59) |
| `normalization-parity.spec.js` | Cross-cutting | Python/JS normalizer agreement (see [CONTRACTS.md](CONTRACTS.md#a-mhg-normalization-parity)) |
| `lemma-matching.spec.js` | Cross-cutting | Lemma highlight matching exactness, #130 (see [CONTRACTS.md](CONTRACTS.md#b1-lemma-highlight-matching-contract)) |
| `position-parity.spec.js` | Cross-cutting | Python/JS word-position agreement, #131 (see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)) |
| `site-chrome.spec.js` | Cross-cutting | Build-injected nav/footer + mobile-menu (`build-pages.py`) |
| `vendor.spec.js` | Cross-cutting | Runtime libraries come from `assets/vendor/`, no CDN dependency (runtime counterpart to `no-cdn-check.yml`) |
| `cross-reference-test.spec.js` | Data integrity | Authority/corpus cross-reference validity |
| `corpus.spec.js` | Data integrity | Corpus index structure validation |
| `visual-mobile-test.spec.js` | Visual | Responsive screenshots + touch target size across several viewports (iPhone SE 375px … desktop 1440px) |

### CI: Data Integrity

**Workflow:** `.github/workflows/data-integrity.yml` (since #125 it consolidates the former `schema-validation.yml` + `index-version-check.yml`)
**Triggers:** PRs + main pushes touching `schema/`, `tei/`, `authority-files/`, the three index `.json.gz` files (corpus/authority/naming), `api/**`, the build scripts (`build-*-index.py`, `build-api.py`, `mhg_normalizer.py`), `scripts/sync/`, `scripts/audit/`, `scripts/ingest/naming/`, `corpus-loader.js` or `requirements.txt`. Plus `workflow_dispatch`.

**Eleven checks, cheap to expensive (fail fast);** beforehand a helper step determines the diff base (PR: first parent of the merge ref, `git rev-parse HEAD^1`; push: `event.before`) for checks 2 and 9:

1. **Index version constants** (#47.3) – the build scripts and `corpus-loader.js` have to name the same versions, otherwise the IndexedDB cache invalidation does not fire. Locally: `python scripts/audit/check-index-versions.py`.
2. **Index version bump gate** (#154) – if the decompressed content of the corpus or authority index changed against the diff base, the `version` string has to have changed too; otherwise the version bump was forgotten and the Dexie cache does not invalidate (users keep the old index for up to 30 days). Locally: `python scripts/audit/check-index-version-bump.py --base origin/main`. Without a determinable diff base (workflow_dispatch, force push) the check is skipped.
3. **RNC→RNG sync check** (P2-14) – regenerates `.rng` from `.rnc`, any diff fails.
4. **TEI P5 pin** – the committed `tei_all.rng` is checked against the pinned version (4.11.0).
5. **Freshness of variants.xml** (#125) – `extract-variants.py --apply` has to reproduce the committed file byte for byte („corpus changed, variants.xml forgotten"). Blocking and BEFORE check 7: the index comparison alone cannot detect variants drift.
6. **Freshness of the API** (#45) – `build-api.py` has to reproduce the committed `api/` byte for byte (plain JSON, `git diff` suffices). Before the index gate, because the CI index rebuild leaves `data/` gz-dirty.
7. **Freshness of the indexes** (#125, rebuild-and-compare) – both indexes are built fresh and compared decompressed against the committed state („source or build script changed, rebuild forgotten"). This works only because the builds are deterministic.
8. **Naming index consistency** (#152) – `source.commit` provenance present and every `works[].sigle` exists as `tei/<SIG>.tei.xml` (a sigle rename would otherwise silently break the reader link in the playground). Offline, always runs. Locally: `python scripts/audit/check-naming-index.py`.
9. **Freshness of the naming index** (#152, rebuild-and-compare) – a rebuild from the `source.commit` pinned inside the index has to reproduce the committed state. Runs ONLY if naming paths changed against the diff base (external fetch to `lindabeutel/Naming-analysis`; no external network dependency on every data PR, the #125 principle).
10. **Cross-reference integrity** (#44/#115/#152) – dangling refs outside `lexicon.xml` break the build; `lexicon.xml` is gated as an **id-set ratchet** against the committed baseline (`scripts/audit/lexicon-baseline.json`): any id outside the baseline is red (even with a compensating backfill in the same PR), tolerated legacy stock is green, a shrunken actual state gives a `::warning` → run `--update-baseline` and commit the file diff along.
11. **Two-stage RelaxNG validation** (P2-13) – stage 1 `tei_all.rng` (warnings, the #30 baseline), stage 2 `mhdbdb.rng`/`mhdbdb-authority.rng` (hard gate). Deliberately last, as the most expensive check.

**Note on dependency pins:** lxml and rnc2rng are pinned in `requirements.txt` (single source, CI installs from it) so that serialization changes in newer versions do not show up as drift false alarms. Locally use `pip install -r requirements.txt`; after a pin bump regenerate `variants.xml` and rebuild the `.rng` files.

**Debugging failures:**
- Version drift → run `python scripts/audit/check-index-versions.py` locally, align the constants
- Bump forgotten (#154) → bump the version in `build-*-index.py` + `corpus-loader.js`, rebuild the index, all in one commit
- RNG drift → `python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng` locally, commit
- variants or index freshness → work through the Data-Change-Lifecycle in DATA-MODEL.md (regenerate, rebuild, bump, all in one commit)
- API freshness → `python scripts/build-api.py` locally, commit `api/` along
- Stage 2 failure → `python scripts/audit/validate-corpus.py --sample <SIGLE>` locally
- TEI version mismatch → bump `EXPECTED` in the workflow and `schema/README.md`

### CI: Release Version Check (Zenodo)

**Workflow:** `.github/workflows/release-version-check.yml`
**Triggers:** pushing tags `v*` + `workflow_dispatch`.

**Background (#91, 2026-06-10):** on release Zenodo pulls the record metadata from `.zenodo.json`. A `version` field hardcoded there and forgotten while tagging produces a Zenodo record with a wrong version, without an error and without a warning. Hence two rules: `.zenodo.json` has **no** `version` field (Zenodo then takes the tag name automatically; the git tag is the single source of truth), and `CITATION.cff → version` has to match the tag (it feeds GitHub's „Cite this repository" widget).

**Timing:** the check runs on the tag push, the Zenodo webhook only fires when the GitHub release is published. If the check fails, delete the tag, fix `CITATION.cff`, tag again: Zenodo has not seen anything yet.

**Release procedure:** (1) `CITATION.cff`: bump `version` and `date-released` (update the `.zenodo.json` contributors if needed), (2) `git tag vX.Y.Z && git push origin vX.Y.Z`, (3) create the GitHub release (`gh release create vX.Y.Z`) → Zenodo automatically archives a new version under the concept DOI `10.5281/zenodo.20627656`.

**Locally:** `python scripts/audit/check-release-version.py v1.1.0`

### CI: File Size Guard

**Workflow:** `.github/workflows/file-size-check.yml`
**Triggers:** every PR and every push to `main`, plus `workflow_dispatch`. Deliberately **no** `paths:` filter, see below.

**Background (#350, 2026-08-04):** GitHub blocks files larger than 100 MiB on push and warns from 50 MiB. That is the only size limit with teeth. Repository size itself has a recommendation only (under 1 GB ideal, under 5 GB strongly recommended), and the sole documented consequence of exceeding it is an email from GitHub Support. Measured on 2026-08-04, `tei/OVG.tei.xml` sits at 62.9 MiB and is the only file above the 50 MiB warning threshold; in the history it already stood at 79.7 MiB. Annotation work grows TEI files without anyone watching the file size.

**Why 90 MiB and not 100:** this gate cannot prevent a rejected push. GitHub refuses the push before any workflow starts, and by then the commit already exists locally. The purpose is advance warning while the push still goes through and the file can still be split in an orderly way. A gate that warns at 100 MiB never warns. A `::warning` from 75 MiB marks the point where a splitting plan belongs on the table.

**Why no path filter:** a file can grow too large in any directory. `data-integrity.yml` covers the likely candidates but not `ingest/` (which already holds a 31 MB TSV) and no newly created folder. A guard that first has to decide which folder may grow carries the same boundary problem the project dropped for the em-dash gate on 2026-08-03. The run costs seconds because `git ls-tree -l` supplies the sizes and no file is read.

**Locally, and this is the actual safety net:** `python scripts/audit/check-file-sizes.py`

### Audit Scripts Reference

Diagnostic and validation scripts in `scripts/audit/`. Completeness against the directory is gated by `scripts/audit/check-doc-inventories.py`, the same script as for the spec table above. Until #329 this table named 11 of 22 scripts, among them neither of the em-dash and no-CDN gates that run in every CI.

Two kinds are mixed here, and the difference is the important one: **gates** have an exit code and are called by a workflow, **diagnostics** measure something for a human and are run by hand. Where a workflow calls, the row says so.

| Script | Purpose |
|--------|-------|
| `validate-corpus.py` | Two-stage RelaxNG validation of all 667 corpus and 8 authority files (called by data-integrity.yml) |
| `check-index-versions.py` | Version consistency between build scripts and loader, called by `data-integrity.yml` (details above) |
| `check-index-version-bump.py` | Version bump gate (#154): index content changed against `--base` ⇒ the `version` string has to change with it. Called by `data-integrity.yml` (details above) |
| `check-release-version.py` | Release tag against `CITATION.cff` version; forbids a `version` field in `.zenodo.json`. Called by `release-version-check.yml` (details above) |
| `check-file-sizes.py` | Size guard (#350) against GitHub's hard 100 MiB per-file block: red from 90 MiB, `::warning` from 75 MiB. Called by `file-size-check.yml` (details above), stdlib only, reads no file content. `--selftest` secures parser and thresholds against synthetic input, because the gate is expected to stay green for years (27 MiB of headroom today) and a permanently green gate proves nothing |
| `build-issue-matrix.py` | Writes the countable half of the triage matrix (#44) from the issue labels: quick stats, the ping list from `wait:*` and one table per autonomy level, between the `MATRIX` markers in the issue body. Everything outside the markers stays hand-written. Two different dates, on purpose: the tables show the last comment by anyone, the ping list shows the last comment **by the person being waited on** (for `wait:extern`, the last comment not from our own side), so that our own follow-up does not reset the clock. Run daily by `issue-matrix.yml`, not as a PR gate: the staleness comes from ticket movement, not from code changes, so a gate would redden other people's PRs without fixing anything. Also checks the label axes and turns red on a gap (a ticket without `auto:*`, an `auto:blocked` without `wait:*`). `--selftest` covers counting, sorting and marker replacement without network access |
| `audit-authority-files.py` | Structure, cross-references and data quality **within** the 8 authority files (authority→authority; id patterns, orphaned references, structural consistency) |
| `check-authority-cross-refs.py` | **Corpus→authority** cross-ref integrity: dangling `@lemmaRef`/`@ana`/`@corresp`/`@ref`/`@target`. `--check` is the CI gate in `data-integrity.yml`: unresolved refs outside `lexicon.xml` are red immediately; `lexicon.xml` acts as an id-set ratchet against `lexicon-baseline.json` (#152), new ids red, legacy stock green; `--update-baseline` advances the ratchet. The only detector of derived-file drift (#44/#115) |
| `check-naming-index.py` | Naming index consistency (#152): `source.commit` present and every `works[].sigle` exists in `tei/`; `--print-source-commit` yields the pin for the workflows. Called by `data-integrity.yml` and `naming-index-update.yml` (details above) |
| `audit-tei-corpus.py` | Corpus-wide spot checks (e.g. missing `<l>`/`<lg>`, unusual xml:id patterns, encoding anomalies) |
| `check-lexicon-senses.py` | `lexicon.xml` sanity: lemmata without `<sense>`, senses without `conceptIds` |
| `doc-count-audit.py` | Drift detector between the actual corpus and authority counts and the values anchored in the docs. Heuristic: window of ±2 absolute or ±2 % relative, strict keyword anchor immediately after the number. Runs as a health-check tool by hand, no workflow calls it. Plus a self-check reporting which configured (file, key) pairs check nothing: either the anchor word is missing, or it stands in prose only instead of behind a number (#342) |
| `check-doc-inventories.py` | Inventory gate (#329) for both tables in this file: „Test File Inventory" against `testing/tests/`, „Audit Scripts Reference" against `scripts/audit/`, in both directions each. stdlib only, called by `no-cdn-check.yml`; `--selftest` checks the scanner against synthetic input |
| `check-no-cdn.py` | Gate in `no-cdn-check.yml`: no external `<script src>` in committed HTML pages, runtime libraries come from `assets/vendor/` (#78). The runtime counterpart is `vendor.spec.js` |
| `check-no-em-dash.py` | Gate in `no-cdn-check.yml` (#140): no em-dashes in user-visible HTML/JS/CSS or in any `.md`, code comments exempt. HTML, JS and CSS are checked in full; Markdown only in the lines that are new against `--diff-base <rev>` (#292), fences and inline code excluded, every `.md` in the repo and no folder exempt. Narrowing it to "user-visible Markdown" was built and discarded on 2026-08-03: the whitelist cost more than the rule it saved and opened two holes of its own. `--selftest` secures scanner, file selection and diff layer against mutations, because several earlier versions were fail-opens that passed every test case |
| `check-author-refs.py` | Author statements in `titleStmt` against `persons.xml` (#228), six overlapping error classes. The trigger was seven texts with `<author ref="#person_N"/>` and **no** text content: schema-valid, reference intact, and still authorless in the frontend |
| `classify-lexicon-backfill.py` | Read-only classification of the open `lexicon.xml` gaps (#115/#44). Groups every unresolved reference by lemma and separates „entry missing entirely" from „only the sense missing"; the sense-to-concept assignment stays curatorial |
| `quantify-unannotated-tokens.py` | Survey of the `<w>` **without** `@lemmaRef` (#189): coverage per text, surface forms aggregated corpus-wide, homograph flag. CSV reports, no corpus change |
| `coverage-bias-check.py` | Follow-up question to the previous one (#309): does the uneven annotation coverage skew the per-thousand rates of the analysis tools, and in which direction? Not trivial, because for rare items the numerator is pushed down as well |
| `measure-stage3-resolution.py` | Impact measurement for stage 3 of the lemma resolution (#224): how many short lemmata the earlier bidirectional substring matching washed into every search |
| `survey-concept-distribution.py` | Mirrors `concept-distribution.js` one to one in Python and measures lemma count, matching texts and occurrences per concept (#47 R2), to find browser edge cases with very large concepts |
| `count-verse-numbering-resets.py` | Reach of the #138 verse numbering: which `<div>` reset the margin numbering, and how many margin numbers that adds. Rebuilds the render order instead of estimating; two earlier estimates by text-window heuristic were both wrong |
| `count-editorial-notes-and-div-heads.py` | Measurement procedure behind the two reader changes from #250 (editorial interventions in the metadata panel, label above an own `head` heading). Both depend on corpus properties that shift with every ingest |
| `review-rounds.py` | Impact measurement for the local reviewer (2026-08-02): review rounds per merged PR, with the baseline from before the switch. Needs `gh`, no corpus access. The measurement procedure sits in the docstring and depends on two conditions: `use_sticky_comment` stays off (otherwise one comment is no longer one run), and the CI action stays the only LLM commenter |
| `drop-negative-variant-corresp.py` | One-off migration (#115): removes dead `@corresp="variants.xml#type_-N"` (legacy punctuation codes, never defined in `variants.xml`) from `<w>`. Already applied, the corpus contains 0 such references today; kept as evidence of the change |

### Skipped Tests (Issue #43 – resolved)

No tests are currently skipped (0 skipped project-wide). The 25 tests formerly disabled in `main-site.spec.js` (phase 7 and phase 0 refactoring) were reactivated or replaced in commit `259bc505a` (2026-02-24, „88 passing, 0 skipped"); #43 is settled with that.

### Manual Testing Checklist

Before deploying:
- [ ] Search for common word (e.g., "vriunt")
- [ ] Search with variant (e.g., "brot" → "brôt")
- [ ] Text selection and filtering
- [ ] Open reading view
- [ ] Playground explorers
- [ ] Multi-lemma proximity search
- [ ] Playground → main site navigation

## Git Workflow

### Branch Strategy

- **main:** Production-ready code, stable releases
- **Feature branches:** `feature/your-feature-name`
- **Historical branches:**
  - `pre-main-site` - Old XML parsing architecture (archived)
  - `initial-data-wrangling` - RDF/Relational DB → TEI transformation (archived)
  - `feature/wenzelsbibel-ingest` - Wenzelsbibel text ingest (Issue #34, active)

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test locally
npm run serve
# Test in browser...

# 3. Run automated tests
npm test

# 4. CRITICAL: Wait for user to test and approve
# DO NOT COMMIT without user approval!

# 5. Commit with descriptive message
# Stage specific files BY NAME — never `git add .` / `git add -A`.
# Concurrent sessions share the working dir; a blanket add captures another
# session's staged files (see CLAUDE.md Git Rules, commit 8b5d0e6ac mishap).
git add path/to/file1 path/to/file2
git commit -m "Add feature: description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push (ONLY AFTER USER APPROVAL)
git push -u origin feature/your-feature-name

# 7. Merge to main
git checkout main
git merge feature/your-feature-name
git push origin main
```

### Commit Guidelines

**DO:**
- Use descriptive messages (not "fix bug" or "update file")
- Include context (what changed and why)
- Reference issues/PRs when applicable
- Add AI-assisted footer

**DON'T:**
- Commit without user testing and approval
- Force push to main
- Skip hooks or validation

### Autonomous sessions (playbooks)

For autonomous issue work and PR merge sessions there are reusable procedures with an operating contract, gates and known failure modes in [`docs/playbooks/`](playbooks/). They only run after an explicit kickoff by the user and are updated with the lessons after every session.

## Deployment

### GitHub Pages

**Hosting:** GitHub Pages (static site, free)
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Branch:** `main` (automatically deployed)

### Deployment Process

1. Push to `main` branch
2. GitHub Actions automatically builds and deploys
3. Site updates within 2-5 minutes

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Manual testing complete
- [ ] Pre-built indexes rebuilt (if XML sources changed)
- [ ] Documentation updated
- [ ] User has tested and approved changes

### Post-Deployment Verification

1. Visit https://dhcraft.org/mhdbdb-tei-only/
2. Test main site search
3. Test playground explorers
4. Verify pre-built indexes load correctly

### Cache Invalidation

Increment the version number in the build scripts to force a browser refetch. The
version sits as a dict literal in the index, not as a constant; see [Version
Increment](#version-increment) above for the exact place and its counterpart in
`corpus-loader.js`.

## Historical Context: Initial Data Wrangling

### Branch: `initial-data-wrangling`

The MHDBDB project originally maintained data in multiple formats (RDF, relational database, partial XML). To create a single source of truth, all data was transformed into TEI-compliant XML documents.

**Process:**
1. Extract from RDF (semantic concepts, genre hierarchies, names)
2. Extract from relational DB (persons, works, lemmata, bibliographic references)
3. Transform to TEI with consistent cross-reference patterns
4. Validate against TEI P5 schema

**Output:** 7 content-bearing TEI authority files in the `authority-files/` directory (the 8th, `contributors.xml`, was added later on 2026-04-14 as part of the editor-attribution feature and is not part of this legacy export)

**Status:** Archived (completed, preserved for reference)

**Benefits of TEI as single source:**
- Interoperability (TEI is widely supported standard)
- Self-describing (metadata embedded with data)
- Version control friendly (XML diffs are readable)
- Future-proof (TEI will be supported for decades)

**Trade-off:** Large file sizes (solved with pre-built indexes)

---

For data structures, see [DATA-MODEL.md](DATA-MODEL.md).
For technical architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
For user-facing features, see [FEATURES.md](FEATURES.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
