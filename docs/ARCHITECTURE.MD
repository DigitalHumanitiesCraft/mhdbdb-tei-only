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
- ⚠️ Large initial download (~37 MB indexes)
- ⚠️ No real-time updates (requires rebuild + redeploy)

## Main Site Architecture

**Purpose:** Public-facing corpus browser for students and general users
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Key Files:** `index.html`, `korpus.html`, `assets/js/app.js`, `assets/js/search/`, `assets/js/rendering/`

### Application Structure

**MainSiteApp** (`assets/js/app.js`)
- Initialize corpus loader
- Load pre-built corpus index (~34 MB compressed)
- Set up search interface and text selection
- Coordinate SearchEngine and TextRenderer

### Page Detection and Dual Initialization

`MainSiteApp` detects the current page and branches initialization:

| Path | Detection | Initialization | Data Loaded |
|------|-----------|---------------|-------------|
| `index.html` | `!pathname.includes('korpus.html')` | Landing page mode | None (stats hardcoded in HTML) |
| `korpus.html` | `pathname.includes('korpus.html')` | Search page mode | Authority + Corpus indexes |

**Search page initialization sequence** (source: `assets/js/app.js`):
1. Load authority index (via `CorpusLoader`)
2. Load corpus index (via `CorpusLoader`)
3. Initialize all texts as included (`Set` of text IDs)
4. Create `SearchEngine(authority, corpus)`
5. Create `TextRenderer(corpus, authority)` (for cache)
6. Create `TEITextReader(corpus, authority, cache)`
7. Populate text list checkboxes from corpus index
8. Check URL parameters (`?textId=...&lemmaIds=...&position=...`)
9. If no URL params, auto-open ABG text in reading view

### Search Flow

**SearchEngine** (`assets/js/search/search-engine.js`)
1. User enters search term
2. Normalize MHG characters (â→a, ô→o, ü→ue)
3. Resolve variants via dictionary (e.g., "brot" → lemma_879)
4. Filter corpus by selected texts
5. Search for lemma in filtered texts
6. **Multi-lemma deduplication:** When search resolves to multiple lemmata, aggregate results by textId
7. Extract context windows (±10 words)
8. Return results with positions and all matched lemmaIds

**Multi-Lemma Deduplication:**
- Problem: Variant resolution may map one term to multiple lemmata (e.g., "brot" → both "brôt" and "brot")
- Solution: Use Map keyed by textId to deduplicate results
- Result: Each text appears once with aggregated match counts and all lemmaIds for multi-lemma highlighting
- Benefits: Cleaner UI, accurate counts, transparent disambiguation with lemma badges

**Key features:**
- Variant resolution via flat dictionary lookup (O(1))
- Context extraction with surrounding words
- Text filtering respects user selection
- Deduplication by textId for multi-lemma results

### Text Selection Interface

Allows users to include/exclude specific texts from search:
- Checkboxes for each text (all selected by default)
- Live filtering by title, sigle, or author
- Bulk actions (Alle/Keine)
- Selected state stored in Set for fast membership checks

### Reading View

**TEITextReader** (`assets/js/rendering/tei-text-reader.js`)
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

### TEI Element Rendering Map

The reading view converts TEI XML elements to HTML. Source: `extractAndFormatBody()` / `_renderElement` closure in `assets/js/rendering/tei-text-reader.js`

| TEI Element | Attributes | HTML Output | CSS Class |
|------------|-----------|-------------|-----------|
| `<head>` | | `<h3>` | `.section-head` |
| `<p>`, `<ab>` | | `<p>` | — |
| `<div>` | | `<div>` | `.tei-div` |
| `<lg>` | | `<div>` | `.verse-group` |
| `<l>` | | `<span>` | `.verse-line` |
| `<lb>` | | `<br>` | `.line-break` |
| `<pb>` | `@n` | `<span>[{n}]</span>` | `.page-break` |
| `<cb>` | `@n` | `<span>[Sp. {n}]</span>` | `.column-break` |
| `<caesura>` | | `<span>\|\|</span>` | `.caesura` |
| `<hi>` | `@rend="initial"` | `<span>` | `.initial` |
| `<hi>` | `@rend="upper_case_first_letter"` | `<span>` | `.upper-case-first` |
| `<hi>` | (other) | `<span>` | `.hi` |
| `<supplied>` | | `<span>[...]</span>` | `.supplied` |
| `<num>` | | `<span>` | `.number` |
| `<pc>` | `@join` | `<span>` with `data-join` | `.punctuation` |
| `<seg>` | | (transparent — children only) | — |
| `<w>` | `@lemmaRef` (match) | `<mark>` | `.highlight` / `.highlight.multi-lemma` |
| `<w>` | `@lemmaRef` (no match) | escaped text + space | — |
| `<w>` | no `@lemmaRef` | escaped text + space | — |
| (unknown) | | recurse into children | — |

**Multi-lemma color assignment:** `lemmaColorMap[lemmaId] = colors[idx % 5]` — sequential assignment, wraps at 5.

**Position counting contract:** see [CONTRACTS.MD](CONTRACTS.MD#b-position-counting-contract)

### TEI Cache Management

**TEICacheManager** (`assets/js/storage/tei-cache-manager.js`)
- Cache serialized DOM as XML string in IndexedDB (database: `MHDBDB_TEI_Cache`)
- 30-day expiration (checked on read, corrupted entries auto-deleted)
- Subsequent loads from cache (~100-200 ms vs 3-5 seconds)
- **Cache invalidation and version check flow:** see [CONTRACTS.MD](CONTRACTS.MD#e-cache-invalidation)

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
│   ├── file-display.js
│   └── router.js      # Hash-based URL routing (#48)
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

### URL Routing (Hash-Based)

**Component:** `playground/js/ui/core/router.js`
**Purpose:** Shareable, bookmarkable playground URLs via hash fragments.

**URL schema:** `#<view>[&key=value&...]`

| View | Hash Fragment | What it opens |
|------|-------------|---------------|
| Authority explorers | `#authors`, `#works`, `#lemmata`, `#concepts`, `#genres`, `#names` | Corresponding explorer tab |
| Multi-Lemma Search | `#multi-lemma` | Co-occurrence search |
| TEI Analysis | `#words`, `#lines`, `#annotations` | TEI analysis views (currently non-functional, see #87) |

**Parameters:**

| Param | Applies to | Effect |
|-------|-----------|--------|
| `q` | All authority views | Auto-fills search input and triggers search |
| `show` | All authority views | Expands detail panel for the given item ID |
| `lemmata` | `multi-lemma` only | Comma-separated lemma terms |
| `mode` | `multi-lemma` only | `proximity` or `document` |
| `dist` | `multi-lemma` only | Max word distance (integer) |

**Example:** `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10`

**Core functions:**

| Function | What it does |
|----------|-------------|
| `parseHash()` | Extracts `{view, params}` from `location.hash` |
| `buildHash(view, params)` | Constructs hash string with URL-encoded values |
| `dispatch(view, params)` | Looks up view handler, calls it, then defers `q`/`show` to next tick |
| `navigate(view, params)` | Updates hash and dispatches (suppresses listener to prevent double-fire) |
| `initRouter()` | Wires `hashchange` listener, called once after data loads |

**Known limitation:** `triggerExpand(itemId)` only works for items in the currently visible result set (typically top 50).

## Lemma Pages Architecture

**Purpose:** Persistent, linkable pages for individual lemmata — target URLs for Worterbuchnetz, MWB, and other external systems
**URL:** `https://dhcraft.org/mhdbdb-tei-only/lemma/{numericId}`
**Key Files:** `lemma/index.html`, `lemma/lemma-page.js`, `404.html`

### URL Routing (GitHub Pages workaround)

GitHub Pages has no server-side routing. Clean URLs (`/lemma/879`) return 404. Solution: `404.html` intercepts and redirects:

```
User requests /lemma/879
  → GitHub Pages: no file at /lemma/879 → serves 404.html
  → 404.html JS: detects "lemma" in path, extracts "879"
  → window.location.replace("/lemma/?id=879")
  → lemma/index.html loads → lemma-page.js parses ?id=879
```

Three URL formats accepted (parsed in order, first match wins):
1. `?id=879` — query parameter (canonical after redirect)
2. `#879` — hash (for systems that strip query params)
3. `/lemma/879` — path segment (pre-redirect, also works post-redirect)

### Initialization Sequence

```
1. parseLemmaId()            → extract numeric ID from URL
2. loadAuthorityIndex()      → via CorpusLoader (same as main site)
3. Find lemma by "lemma_{id}" in authorityIndex.lemmata
4. renderLemma()             → title, POS, etymology, senses
5. renderVariants()          → invert variants map to find all forms → this lemma
6. renderCompounds()         → find lemmata whose etymology references this lemma
7. loadCorpusIndex()         → non-blocking (page renders without it)
8. renderOccurrences()       → texts containing this lemma, sorted by frequency
9. renderExternalLinks()     → static links + async Wörterbuchnetz API
```

### Data Rendering Pipeline

| Section | Data Source | Algorithm |
|---------|-----------|-----------|
| Etymology | `lemma.etymology[]` | Each component linked via `?id={numId}` if it has `lemmaRef` |
| Senses | `lemma.senses[].conceptIds` | Resolve concept IDs → German labels via `authorityIndex.concepts` |
| Variants | `authorityIndex.variants` (flat map) | **Invert**: scan all entries, collect those where `value === lemmaKey` |
| Compounds | `authorityIndex.lemmata` | Filter lemmata whose `etymology[].lemmaRef === lemmaKey` |
| Occurrences | `corpusIndex.lemmaIndex[lemmaKey]` → textIds | Look up text metadata, count positions, sort by frequency desc |
| Wörterbuchnetz | External API (async) | See CONTRACTS.MD D.2 |

### Concept Label Resolution

```
resolveConceptLabels(conceptIds):
    for each cid in conceptIds:
        concept = authorityIndex.concepts.find(c => c.id === cid)
        label = concept.termDE || concept.termEN || cid    // German preferred
    return labels
```

### Integration with Main Site

- **Occurrence links** → `../korpus.html?textId={id}&lemmaIds={numericId}` (opens reading view with highlighting)
- **Corpus search link** → `../korpus.html?search={lemma.lemma}` (triggers main site search)
- **Shared dependencies**: CorpusLoader, Pako, Dexie.js, shared.css, tailwind-output.css (all via `../assets/`)

---

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

**Component:** `assets/js/lib/corpus-loader.js`

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

## External Services

### Wörterbuchnetz API

- **Endpoint**: `https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{searchpattern}`
- **Response**: `{ result_set: [{ sigle, lemma (HTML-encoded), gram, wbnetzid, wbnetzlink }] }`
- **Queried dictionaries**: BMZ, Lexer, LexerN, FindeB (all MHG-relevant dictionaries in the network)
- **Search term**: Normalized lemma form (e.g., "brot" not "brôt")
- MHDBDB is NOT a directly linkable dictionary in Wörterbuchnetz
- **Integration**: Dynamic fetch on lemma page, results rendered in dedicated section

### MWB Online (Mittelhochdeutsches Wörterbuch, Trier)

- **Portal**: `https://www.mhdwb-online.de/`
- **Deep link**: `https://www.mhdwb-online.de/wb/{lid}` (requires numeric MWB lid)
- **Metadata API** (HTTP only): `http://tares-neu.uni-trier.de:8080/exist/rest/db/MWB/Services/retrieve_MWB_lemma_metadata.xql?lemma={term}`
- **API response**: XML with `<entry><MWB><id>, <lemma>, <gram>, <url></MWB><MWV><lexer>, <bmz>, <fb></MWV></entry>`
- **Current integration**: Static link only — API is HTTP-only, blocked by mixed content policy on HTTPS pages
- **Upgrade path**: Switch to dynamic lookup (like Wörterbuchnetz) when MWB migrates API to HTTPS

### Old MHDBDB

`https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid={numericId}`

### Wikidata

- Automatic image fetching via Wikidata P18 property (3-step chain: claims → FilePath → attribution)
- Dual identifier display (work GND/Wikidata vs author GND/Wikidata)
- **Full API request/response specs:** see [CONTRACTS.MD](CONTRACTS.MD#d-external-api-contracts)

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
