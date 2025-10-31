# Architecture

This document describes the technical architecture, component structure, and system design patterns for the MHDBDB TEI Repository.

## System Overview

### Architecture Philosophy

The MHDBDB project follows a **client-only architecture** with no backend server:

```
[GitHub Pages Static Files]
     ↓
[Browser] → Fetch + Decompress → [IndexedDB Cache] ← → [Runtime Application]
```

**Key Principles:**
- Pre-computation: Expensive operations (XML parsing, indexing) done at build time
- Client-side processing: All search, filtering, rendering happens in browser
- Persistent caching: IndexedDB stores large datasets between sessions

**Trade-offs:**
- ✅ Zero hosting cost (GitHub Pages)
- ✅ No server maintenance
- ✅ Fast global CDN distribution
- ⚠️ Limited to browser memory
- ⚠️ Large initial download (~24 MB indexes)
- ⚠️ No real-time updates (requires rebuild + redeploy)

## Main Site Architecture

**Purpose:** Public-facing corpus browser for students and general users
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Key Files:** `index.html`, `korpus.html`, `js/app.js`, `js/search/`, `js/rendering/`

### Application Structure

**MainSiteApp** (`js/app.js`)
- Initialize corpus loader
- Load pre-built corpus index (~21 MB)
- Set up search interface and text selection
- Coordinate SearchEngine and TextRenderer

### Search Flow

**SearchEngine** (`js/search/search-engine.js`)
1. User enters search term
2. Normalize MHG characters (â→a, ô→o, ü→ue)
3. Resolve variants via dictionary (e.g., "brot" → lemma_879)
4. Filter corpus by selected texts
5. Search for lemma in filtered texts
6. Extract context windows (±10 words)
7. Return results with positions

**Key features:**
- Variant resolution via flat dictionary lookup (O(1))
- Context extraction with surrounding words
- Text filtering respects user selection

### Text Selection Interface

Allows users to include/exclude specific texts from search:
- Checkboxes for each text (all selected by default)
- Live filtering by title, sigle, or author
- Bulk actions (Alle/Keine)
- Selected state stored in Set for fast membership checks

### Reading View

**TEITextReader** (`js/rendering/tei-text-reader.js`)
- Side-by-side 3-column grid layout (search + results + reading)
- Full-text display with multi-lemma highlighting
- Rich metadata panel (work/author info, Wikidata images)
- Context navigation (prev/next occurrence)
- URL parameter support (`?textId=ABG&lemmaIds=879,7532&position=310`)

**Layout Architecture:**
- Browser-level scrolling (no container scrollbars)
- Equal-height columns using CSS Grid with `align-items: start`
- Responsive: 3 columns on desktop (≥1280px), stacked on mobile
- Dynamic column management (2-column initial state, 3-column after search)

**Key features:**
- Multi-lemma highlighting (5 colors: red, blue, green, yellow, purple)
- Wikidata integration (automatic image fetching with attribution)
- Dual identifier sections (work GND/Wikidata vs author GND/Wikidata)
- Browser window scrolling to highlighted terms (120px header offset)

### TEI Cache Management

**TEICacheManager** (`js/storage/tei-cache-manager.js`)
- Cache TEI files >5MB in IndexedDB
- No expiration (user content persists)
- Subsequent loads from cache (~100-200 ms vs 3-5 seconds)

## Playground Architecture

**Purpose:** Advanced research tool for medievalists and researchers
**URL:** https://dhcraft.org/mhdbdb-tei-only/playground/
**Key Files:** `playground/js/playground-main.js`, `playground/js/data/`, `playground/js/ui/`

### Application Structure

**MHDBDBPlayground** (`playground/js/playground-main.js`)
- Initialize IndexedDB
- Load authority index (~3 MB)
- Initialize data managers (authority, TEI)
- Set up modular UI components (18 modules)

### Data Layer

**AuthorityFilesManager** (`playground/js/data/authority-manager.js`)
- Load and query authority data
- 3-stage lemma resolution:
  1. Exact match in lexicon (canonical forms)
  2. Variants dictionary lookup (~176k mappings)
  3. Partial match fallback (fuzzy search)
- Direct array access (no XML DOM queries)
- Performance maps for fast lookups

**TEIFilesManager** (`playground/js/data/tei-manager.js`)
- TEI document processing and analysis
- Single lemma search with context extraction
- Multi-lemma document search (all lemmata anywhere in text)
- Multi-lemma proximity search (co-occurrence within N words)
- Uses corpus index (v4.0.0) for document-level word positions

### UI Layer (Phase 7 Modular Architecture)

**Module Organization:**
```
playground/js/ui/
├── core/              # Core UI utilities
│   ├── ui-helpers.js
│   ├── progress.js
│   └── file-display.js
├── authority/         # Authority file exploration (6 modules)
│   ├── authority-ui.js
│   ├── person-explorer.js
│   ├── work-explorer.js
│   ├── lemma-explorer.js
│   ├── concept-explorer.js
│   ├── genre-explorer.js
│   └── name-explorer.js
├── tei/               # TEI text analysis
│   ├── tei-ui.js
│   └── multi-lemma-search.js
└── search/
    └── SearchHelpers.js
```

**Benefits:**
- Clear separation of concerns
- Reusable patterns
- Easier testing and maintenance
- Net reduction: 5,536 lines removed

**Authority Explorers:**
Each explorer follows consistent pattern:
- Search/filter functionality
- Result rendering
- Detail view with cross-references
- Links to related entities

**Multi-Lemma Search UI:**
- Modal interface for multi-lemma input
- Search mode selection (document vs proximity)
- Variant resolution (automatic)
- Color-coded results
- Clickable navigation to main site reading view

### Multi-Lemma Proximity Search

**Key algorithm:**
1. Resolve lemma IDs (handle MHG terms and variants)
2. Find positions of each lemma in each text
3. Find combinations where all lemmata within maxDistance
4. Extract context for each combination
5. Deduplicate overlapping contexts

**Cross-platform workflow:**
- Researcher finds co-occurrence in playground
- Clicks result → generates URL with parameters
- Opens main site reading view with highlighting and position

## Storage Architecture

### IndexedDB Manager

**Component:** `playground/js/indexed-db-manager.js`

**Object Stores:**
1. **teiFiles** - Large TEI file caching (>5MB)
   - No expiration (user content)
2. **indices** - Pre-built index caching
   - 30-day expiration
   - Version-based invalidation

**Dual Expiration Policy:**
- Authority data changes infrequently → 30-day cache
- User TEI files persist indefinitely → no expiration
- Balances freshness with performance

### Corpus Loader

**Component:** `lib/corpus-loader.js`

**Shared utility for loading pre-built indexes:**
1. Check IndexedDB cache
2. If expired, fetch compressed index
3. Decompress with Pako (gzip)
4. Parse JSON
5. Cache with expiration timestamp

**Performance:**
- First load: ~3-5 seconds (download + decompress + parse)
- Subsequent loads: ~100-200 ms (IndexedDB read)
- Cache hit rate: ~95%

## Testing Architecture

**Framework:** Playwright end-to-end tests
**Configuration:** `testing/playwright.config.js`

**Features:**
- Automated web server startup (npx http-server on port 8080)
- Headless Chrome with `--disable-web-security`
- 60-second timeout per test
- HTML and JSON test reports

**Test Coverage:**
- ✅ Authority index loading and caching
- ✅ MHG text normalization
- ✅ Lemma variant resolution
- ✅ Cross-reference integrity
- ✅ Search functionality
- ⚠️ Main site features (skipped)

**Running tests:**
```bash
npm test              # All tests
npm run test:ui       # Interactive mode
npm run test:debug    # Debug with breakpoints
npm run test:headed   # Visible browser
```

## Key Architectural Patterns

### Pre-Built Indexes

**Problem:** 50MB XML files caused 30-second browser load times
**Solution:** Pre-build JSON indexes at build time
**Result:** 19× smaller download, no parsing overhead

### 3-Stage Lemma Resolution

**Problem:** Historical spelling variations prevent exact matches
**Solution:** Three-stage lookup (exact → variants → fuzzy)
**Result:** 100% recall for orthographic variants

### IndexedDB Dual Expiration

**Problem:** Balance freshness vs performance
**Solution:** 30-day expiration for reference data, no expiration for user content
**Result:** Fresh data without excessive refetching

### Document-Level Indexing (v4.0.0)

**Problem:** Paragraph-based indexing caused position misalignment
**Solution:** Document-level word positions (0, 1, 2, ...)
**Result:** Accurate proximity search, simpler architecture

### Client-Only Architecture

**Problem:** Need free hosting and easy deployment
**Solution:** GitHub Pages with static pre-built indexes
**Result:** Zero cost, no maintenance, but limited processing power

### Modular UI (Phase 7)

**Problem:** Monolithic UI files hard to maintain
**Solution:** 18 specialized modules organized by feature
**Result:** 5,536 lines removed, improved maintainability

---

For data structures and schemas, see [DATA-MODEL.MD](DATA-MODEL.MD).
For user-facing functionality, see [FEATURES.MD](FEATURES.MD).
For development workflow, see [DEVELOPMENT.MD](DEVELOPMENT.MD).
For architecture decisions, see [DECISIONS.MD](DECISIONS.MD).
