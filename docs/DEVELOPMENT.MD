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
│   │   ├── search/        # Search engine
│   │   ├── rendering/     # TEI text reader, text renderer
│   │   ├── storage/       # TEI cache manager
│   │   └── lib/           # Shared utilities (corpus-loader, text-normalizer)
│   └── images/            # Static images
├── authority-files/       # 8 XML authority files (inkl. contributors.xml)
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
├── impressum.html         # Legal notice (#62)
├── hilfe.html             # Hilfe-Hub (entry point)
├── hilfe-korpussuche.html # Korpus-Suche-Anleitung
├── hilfe-playground.html  # Playground-Anleitung
├── hilfe-daten.html       # Daten-Erklärung für Leser:innen
├── hilfe-daten-beitragen.html  # Schema-Konversions-Guide für TEI-Beitragende (#68 Teil 1)
└── 404.html               # Lemma-page redirect (GitHub-Pages-Workaround)
```

## Building Pre-Built Indexes

Pre-built indexes are included in repository. Rebuild only when modifying source XML files.

### When to Rebuild

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
# Output: data/corpus-index.json.gz (~34 MB)

# Validate indices
python scripts/validate-indices.py
```

**Note on variants:** `authority-files/variants.xml` is rebuilt manually when the corpus changes — there is currently no `extract-variants.py` script in the repo (the build-authority-index.py reads `variants.xml` as-is). See [DATA-MODEL.MD](DATA-MODEL.MD#data-processing-pipeline) for context.

### Version Increment

After significant changes, increment version in build script to force browser cache invalidation:

```python
# In build-authority-index.py
VERSION = "1.2.0"  # Increment for breaking changes
```

## Testing

### Playwright Tests

```bash
npm test              # Run all tests (headless)
npm run test:ui       # Interactive mode
npm run test:debug    # Debug with breakpoints
npm run test:headed   # Visible browser
npm run report        # View HTML report
```

**Test configuration:** `testing/playwright.config.js`
- Always use `npm test` — never `npx playwright test` from the project root (config and `baseURL` live in `testing/`)
- Automated web server startup (port 8080)
- Headless Chrome with `--disable-web-security`
- 60-second timeout per test

### Test File Inventory

| File | Category | What it tests |
|------|----------|--------------|
| `main-site.spec.js` | Main site | Landing page, search page loading, search results, reading view |
| `search-engine.spec.js` | Main site | SearchEngine class: resolution, filtering, deduplication |
| `search-normalization.spec.js` | Main site | MHG normalization functions in browser context |
| `search-with-corpus.spec.js` | Main site | Search against real corpus data |
| `reading-view.spec.js` | Main site | TEI reading view rendering, highlighting, navigation |
| `tei-caching.spec.js` | Main site | IndexedDB TEI cache behavior |
| `error-handling.spec.js` | Main site | Graceful error handling |
| `lemma-page.spec.js` | Lemma pages | URL parsing, data rendering, external links |
| `playground.spec.js` | Playground | Authority explorers, TEI analysis, UI navigation |
| `playground-authority-index.spec.js` | Playground | Authority index loading, data structure integrity |
| `playground-corpus.spec.js` | Playground | Corpus index loading, search functions |
| `normalization-parity.spec.js` | Cross-cutting | Python/JS normalizer agreement (see [CONTRACTS.MD](CONTRACTS.MD#a-mhg-normalization-parity)) |
| `cross-reference-test.spec.js` | Data integrity | Authority/corpus cross-reference validity |
| `corpus.spec.js` | Data integrity | Corpus index structure validation |
| `visual-mobile-test.spec.js` | Visual | Responsive layout (skipped — desktop-only) |

**Playwright config** (`testing/playwright.config.js`): Headless Chromium, 1 worker (sequential), 60s timeout per test, auto-starts `http-server` on port 8080. HTML + JSON reports.

### CI: Schema Validation

**Workflow:** `.github/workflows/schema-validation.yml`
**Triggers:** PRs touching `schema/`, `tei/`, `authority-files/`, or `scripts/audit/validate-corpus.py`. Also manual via `workflow_dispatch`.

**Two checks:**

1. **RNC→RNG sync check** — Regenerates `.rng` from `.rnc` sources and fails if committed `.rng` differs. Catches "edited RNC, forgot to regenerate RNG" drift.

2. **Two-stage RelaxNG validation** — Validates all 667 corpus + 8 authority files:
   - Stage 1: `tei_all.rng` (TEI P5 baseline) — 30 known fails (#30 baseline), warnings only
   - Stage 2: `mhdbdb.rng` / `mhdbdb-authority.rng` (project schemas) — **hard gate, must be 0 fails**

**TEI version pin:** CI downloads `tei_all.rng` fresh from TEI Consortium on each run and verifies it matches the pinned version (currently 4.11.0). A new TEI P5 release triggers a CI failure until the pin is explicitly bumped.

**Debugging failures:**
- RNG drift → run `python -m rnc2rng schema/mhdbdb.rnc > schema/mhdbdb.rng` locally, commit the result
- Stage 2 fail → run `python scripts/audit/validate-corpus.py --sample <SIGLE>` locally to reproduce
- TEI version mismatch → update the `EXPECTED` variable in the workflow + `schema/README.md`

### Skipped Tests (Issue #43)

25 tests are intentionally skipped in `main-site.spec.js`. They cover interactions rewritten during Phase 7 (modular UI refactoring) and Phase 0 (folder restructure) — reading view panel interactions, text selection state management, search result card navigation, multi-lemma URL parameter handling. Tracked in Issue #43.

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
git add .
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

Increment version number in build scripts to force browser refetch:

```python
VERSION = "1.2.0"  # In build-authority-index.py
```

## Historical Context: Initial Data Wrangling

### Branch: `initial-data-wrangling`

The MHDBDB project originally maintained data in multiple formats (RDF, relational database, partial XML). To create a single source of truth, all data was transformed into TEI-compliant XML documents.

**Process:**
1. Extract from RDF (semantic concepts, genre hierarchies, names)
2. Extract from relational DB (persons, works, lemmata, bibliographic references)
3. Transform to TEI with consistent cross-reference patterns
4. Validate against TEI P5 schema

**Output:** 7 inhaltstragende TEI authority files in `authority-files/` directory (the 8th, `contributors.xml`, was added later in 2026-04-14 as part of the editor-attribution feature and is not part of this legacy export)

**Status:** Archived (completed, preserved for reference)

**Benefits of TEI as single source:**
- Interoperability (TEI is widely supported standard)
- Self-describing (metadata embedded with data)
- Version control friendly (XML diffs are readable)
- Future-proof (TEI will be supported for decades)

**Trade-off:** Large file sizes (solved with pre-built indexes)

---

For data structures, see [DATA-MODEL.MD](DATA-MODEL.MD).
For technical architecture, see [ARCHITECTURE.MD](ARCHITECTURE.MD).
For user-facing features, see [FEATURES.MD](FEATURES.MD).
For architecture decisions, see [DECISIONS.MD](DECISIONS.MD).
