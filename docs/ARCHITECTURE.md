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
- ⚠️ Large initial download (~43 MB indexes)
- ⚠️ No real-time updates (requires rebuild + redeploy)

## Main Site Architecture

**Purpose:** Public-facing corpus browser for students and general users
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Key Files:** `index.html`, `korpus.html`, `woerterbuch.html` + `assets/js/woerterbuch.js` (A–Z lemma register, #117), `assets/js/app.js`, `assets/js/site-chrome.js` (shared nav/footer behaviour, every page), `assets/js/search/`, `assets/js/rendering/`

### Application Structure

**MainSiteApp** (`assets/js/app.js`)
- Initialize corpus loader
- Load pre-built corpus index (~40 MB compressed)
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
9. If no URL params, show empty state (no auto-load): a placeholder prompting the user to enter a word/lemma or click a text (`showEmptyState()`, app.js:947)

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

The reading view converts TEI XML elements to HTML. Source: `extractAndFormatBody()` / `_renderElement` closure in `assets/js/rendering/tei-text-reader.js` (post-#17 token-based rendering).

| TEI Element | Attributes | HTML Output | CSS Class(es) |
|------------|-----------|-------------|---------------|
| `<head>` | | `<h3>` | `.section-head` |
| `<p>`, `<ab>` | | `<p>` | — |
| `<div>` | `@type`, `@n` | Always wraps children in `<div class="tei-div tei-div-{type}" data-type data-n>`. Prepended header is `<h3 class="section-head">{label} {n}</h3>` for `@type="chapter"` (rendered like `<head>`, #101) but `<div class="tei-div-header tei-div-{type}">{label} {n}</div>` for all other types | `.tei-div`, `.tei-div-{type}`, `.tei-div-header`, `.section-head` (label map: song→Lied, chapter→Kapitel, recipe→Rezept, number→Nr., section→Abschnitt, colophon→Kolophon, parallel→Parallelüberlieferung) |
| `<lg>` | `@n` | `<div data-n>` with `<span>Strophe {n}</span>` prefix | `.verse-group`, `.stanza-label` |
| `<l>` | `@n` | `<span data-n>` | `.verse-line` |
| `<lb>` | `@n` | `<br>` followed by `<span>{n}</span>` | `.line-break`, `.lb-number` |
| `<pb>` | `@n` | `<span>[{n}]</span>` | `.page-break` |
| `<cb>` | `@n` | `<span title="Spalte {n}">[Sp. {n}]</span>` | `.column-break` |
| `<caesura>` | | `<span>\|\|</span>` | `.caesura` |
| `<note>` | `@type="year\|date"`, `@n` | `<span title="Datum\|Jahr">{n}</span>` (badge) | `.note-badge`, `.note-{type}` |
| `<hi>` | `@rend` (token-based) | `<span class="hi hi-{token1} hi-{token2} ...">` — splits `@rend` on whitespace, prefixes each token with `hi-` | `.hi`, `.hi-initial`, `.hi-upper_case_first_letter`, `.hi-upper_case`, `.hi-bold`, `.hi-italic` (compounds stack) |
| `<supplied>` | | `<span title="Editorische Ergänzung">[...]</span>` | `.supplied` |
| `<num>` | | `<span>` | `.number` |
| `<pc>` | `@join` | `<span data-join>` | `.punctuation` |
| `<seg>` | | (transparent — children only) | — |
| `<w>` | `@lemmaRef` (exact id match, see CONTRACTS §B.1) | `<mark>` | `.highlight` / `.highlight.multi-lemma` |
| `<w>` | `@lemmaRef` (no match) | escaped text + space | — |
| `<w>` | no `@lemmaRef` | escaped text + space | — |
| (unknown) | | recurse into children | — |

**Multi-lemma color assignment:** `lemmaColorMap[lemmaId] = colors[idx % 5]` — sequential assignment, wraps at 5.

**`<hi rend>` token-based rendering:** `@rend` is space-separated (CSS-class style). The renderer splits on whitespace and emits `hi-{token}` per token. Compound values like `rend="initial upper_case_first_letter"` produce `class="hi hi-initial hi-upper_case_first_letter"`, with rules stacking from CSS. ~43k compound values that previously fell through to the single-class default are now correctly styled. Source: [DESIGN.md §TEI Reading View CSS Classes](DESIGN.md).

**Position counting contract:** see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)

### TEI Cache Management

**TEICacheManager** (`assets/js/storage/tei-cache-manager.js`)
- Caches raw TEI XML strings in IndexedDB (database: `MHDBDB_TEI_Cache`) with HTTP validators (ETag / Last-Modified)
- `load()` revalidates via conditional GET at most once per file per page load (in-memory memo): unchanged files cost one 304 roundtrip, changed files re-download immediately (#151) — corpus updates are visible on the next page load, repeat loads in the same session are pure cache hits
- Cache fallback on network failure/timeout (15s), HTTP errors (5xx) and unparseable 200-bodies; corrupted entries auto-deleted; 30-day TTL purge runs at `init()` (cursor-based `cleanExpired`)
- **Cache invalidation and version check flow:** see [CONTRACTS.md](CONTRACTS.md#e-cache-invalidation)

## Playground Architecture

**Purpose:** Advanced research tool for medievalists and researchers
**URL:** https://dhcraft.org/mhdbdb-tei-only/playground/
**Key Files:** `playground/js/playground-main.js`, `playground/js/data/`, `playground/js/ui/`

### Application Structure

**MHDBDBPlayground** (`playground/js/playground-main.js`)
- Initialize IndexedDB
- Load authority index (~3 MB)
- Initialize data managers (authority, TEI)
- Set up modular UI components (21 modules)

### Data Layer

**AuthorityFilesManager** (`playground/js/data/authority-manager.js`)
- Load and query authority data
- 3-stage lemma resolution:
  1. Exact match in lexicon (canonical forms)
  2. Variants dictionary lookup (~257k mappings)
  3. Partial match fallback (fuzzy search)
- Direct array access (no XML DOM queries)
- Performance maps for fast lookups

**TEIFilesManager** (`playground/js/data/tei-manager.js`)
- TEI document processing and analysis
- Single lemma search with context extraction
- Multi-lemma document search (all lemmata anywhere in text)
- Multi-lemma proximity search (co-occurrence within N words)
- Uses corpus index (v4.1.x) for document-level word positions plus `<l>`-boundary arrays

### UI Layer (Phase 7 Modular Architecture)

**Module Organization:**
```
playground/js/ui/
├── core/              # Core UI utilities
│   ├── ui-helpers.js
│   ├── progress.js
│   ├── file-display.js
│   └── router.js      # Hash-based URL routing (#48)
├── authority/         # Authority file exploration (7 modules)
│   ├── authority-ui.js
│   ├── person-explorer.js
│   ├── work-explorer.js
│   ├── lemma-explorer.js
│   ├── concept-explorer.js
│   ├── genre-explorer.js
│   └── name-explorer.js
├── tei/               # TEI text analysis (Release 1 + 2 + #47.3 + 2026-05-15-Welle)
│   ├── tei-ui.js
│   ├── multi-lemma-search.js
│   ├── word-frequency.js          # Wortfrequenz-Analyse (#88, R1)
│   ├── text-statistics.js         # Text-Statistiken (#89, R1)
│   ├── lemma-distribution.js      # Lemma-Verteilung (#90, R1)
│   ├── verse-position-search.js   # Lemmasuche nach Versposition (#47.3)
│   ├── concept-distribution.js    # Begriffs-Verteilung (#47 R2, + Autocomplete #113)
│   ├── text-comparison.js         # Textvergleich Nur-A/Beide/Nur-B (#108)
│   ├── cooccurrence-ranking.js    # Kookkurrenz-Ranking DWDS-Style (#107)
│   └── naming-explorer.js         # Erweiterte Figurenbezeichnungen, kuratiert 4 Werke (#59, Beta)
└── search/
    └── SearchHelpers.js
```

**Benefits:**
- Clear separation of concerns
- Reusable patterns
- Easier testing and maintenance
- Net reduction: 5,536 lines removed

**Playground TEI-Modul-Konvention:** alle zehn Module unter `playground/js/ui/tei/` (außer `multi-lemma-search.js` als dokumentierter Modal-Outlier) folgen dem gleichen Constructor/`show()`/`render()`-Pattern mit Thunks statt direkter Daten-Referenzen, state-driven `renderBody()`, pro-Modul-Escape-Helpers und MessageChannel-Yield bei großen Aggregationen. Sonderfall `naming-explorer.js` (#59): hängt nicht am Corpus-Index, sondern lädt seinen eigenen kleinen Index (`data/naming-index.json.gz`) lazy per fetch+pako ohne IndexedDB-Cache. Pattern ist als Template in [DESIGN.md §Playground TEI-Analysis Module Pattern](DESIGN.md#playground-tei-analysis-module-pattern) dokumentiert.

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
| Multi-Lemma Search | `#multi-lemma` | Co-occurrence search modal |
| Versposition | `#verse-position` | Lemmasuche nach Versanfang/Versende (#47.3) |
| Wortfrequenz | `#word-frequency` | Top-N Lemmata, mit Stopwort-Filter (#88) |
| Text-Statistiken | `#text-statistics` | Token-Count, Lemma-Diversität, Hapax-Rate (#89) |
| Lemma-Verteilung | `#lemma-distribution` | Bar-Chart pro Lemma über alle Texte (#90) |
| Begriffs-Verteilung | `#concept-distribution` | Bar-Chart pro Konzept über alle Texte (#47 R2, mit Autocomplete-Dropdown #113) |
| Textvergleich | `#text-comparison` | Set-Ops Nur-A / Beide / Nur-B über zwei Texte (#108) |
| Kookkurrenz-Ranking | `#cooccurrence-ranking` | Top-N Nachbar-Lemmata eines Lemmas, POS-gefiltert (#107) |
| Erweiterte Figurenbezeichnungen | `#naming` | Kuratierte Eigennamen/Antonomasien/Epitheta je Figur in 4 Werken (#59, Beta) |

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
| Wörterbuchnetz | External API (async) | See CONTRACTS.md D.2 |

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

### Wörterbuch Entry Page (#117)

**Component:** `woerterbuch.html` + `assets/js/woerterbuch.js` (`WoerterbuchPage`)

A–Z-Einstiegsseite zu den Lemma-Seiten. Lädt nur den Authority-Index (via `CorpusLoader('data')`), bucketet die 43.879 `lemmata`-Einträge client-seitig nach dem Anfangsbuchstaben von `normalized` (NFD-Strip als Fallback für `ë`/`ú`, Ziffern-Lemmata im `#`-Bucket) und rendert pro Buchstabe ein paginiertes Register (200 Einträge/Seite, `Intl.Collator('de')`-Sortierung). URL-State `?buchstabe=&seite=` über `history.replaceState`. Bewusst kein eigenes Build-Artefakt — der vorhandene Index reicht.

---

## Storage Architecture

### IndexedDB Manager

**Component:** `playground/js/indexed-db-manager.js`

**Object Stores:** (`indexed-db-manager.js`, `onupgradeneeded`)
1. **tei_files** - User-uploaded TEI files (Indizes: timestamp, size, source)
2. **corpus_tei_files** - Vorgeladene 667 Korpus-Texte (Indizes: timestamp, size, sigle, author, title)
3. **authority_files** - Authority-Files mit `expires`-Index (Default 24h Expiration)
4. **metadata** - Key/Value-Store
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

## Static JSON API (`api/`)

**Generator:** `scripts/build-api.py` (#45) — reads the two pre-built indexes (`data/*.json.gz`), emits 2,742 plain JSON files (~14 MB) into `api/`.

**Served by:** GitHub Pages, like every other file in the repo — no backend, no runtime component, CORS open (Pages sends `Access-Control-Allow-Origin: *`). The main site and playground do **not** consume the API (they load the gzipped indexes); it exists purely for external programmatic access, so it adds zero runtime cost to the site.

**Structure:** root manifest `api/index.json` (counts + source index versions), lemmata as a single bundle (`api/lemmata/index.json`, 43,879 records), individual `{id}.json` + summary `index.json` per collection (persons, works, concepts, genres, names, texts). Every file carries a `license` field. Human documentation: `api/index.html` (German, standalone page).

**Freshness:** deterministic build + CI gate ("Freshness API" in `data-integrity.yml`) keep `api/` byte-identical to what the committed indexes produce. Contracts (URL schema stability, field schemas): [CONTRACTS.md §G](CONTRACTS.md#g-static-json-api-contract-45).

## External Services

### Wörterbuchnetz API

- **Endpoint**: `https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{searchpattern}`
- **Response**: `{ result_set: [{ sigle, lemma (HTML-encoded), gram, wbnetzid, wbnetzlink }] }`
- **Queried dictionaries**: MWB, Lexer (both via `/dictionaries/{sigle}/lemmata/{form}`; `lemma-page.js:278`)
- **Search term**: Normalized lemma form (e.g., "brot" not "brôt")
- MHDBDB is NOT a directly linkable dictionary in Wörterbuchnetz
- **Integration**: Dynamic fetch on lemma page, results rendered in dedicated section

### MWB Online (Mittelhochdeutsches Wörterbuch, Trier)

- **Portal**: `https://www.mhdwb-online.de/`
- **Deep link**: `https://www.mhdwb-online.de/wb/{lid}` (requires numeric MWB lid)
- **Metadata API** (HTTP only): `http://tares-neu.uni-trier.de:8080/exist/rest/db/MWB/Services/retrieve_MWB_lemma_metadata.xql?lemma={term}`
- **API response**: XML with `<entry><MWB><id>, <lemma>, <gram>, <url></MWB><MWV><lexer>, <bmz>, <fb></MWV></entry>`
- **Current integration**: Dynamic lookup via the Wörterbuchnetz HTTPS API (MWB is a queried dictionary there, alongside Lexer; #73, 2026-05-12). Results render as deep-links to `http://mhdwb-online.de` via `target="_blank"` (navigation to http targets from https pages is not Mixed-Content-blocked)
- **Note**: The Trier metadata API above remains HTTP-only and blocked, but is no longer needed; the Wörterbuchnetz route supersedes it

### Old MHDBDB

`https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid={numericId}`

### Wikidata

- Automatic image fetching via Wikidata P18 property (3-step chain: claims → FilePath → attribution)
- Dual identifier display (work GND/Wikidata vs author GND/Wikidata)
- **Full API request/response specs:** see [CONTRACTS.md](CONTRACTS.md#d-external-api-contracts)

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
**Solution:** 21 specialized modules organized by feature
**Result:** 5,536 lines removed, improved maintainability

### Shared Lemma Matching (#130)

**Problem:** The exact-token `@lemmaRef` match was inline-duplicated at 6 sites across 4 files; one copy used a substring test (#126), highlighting wrong words
**Solution:** Single `lemmaRefMatchesId()` in `assets/js/lib/lemma-match.js`, shared by main site and playground (like `text-normalizer.js`)
**Result:** One tested source of truth (CONTRACTS §B.1); no copy can silently regress

### Build-Injected Site Chrome

**Problem:** Nav + footer were hand-maintained per page, drifting out of sync
**Solution:** Single-source partials (`includes/_nav.html`, `includes/_footer.html`) injected into the marked region (`NAV:START`/`FOOTER:START`) of every registered page by `scripts/build-pages.py` (idempotent, `--check` drift gate); shared behaviour (mobile menu, current-year, cross-browser clear-site-data) in `assets/js/site-chrome.js`, loaded on every page via the footer partial
**Result:** One nav/footer source; active page gets `aria-current="page"` automatically

---

For data structures and schemas, see [DATA-MODEL.md](DATA-MODEL.md).
For user-facing functionality, see [FEATURES.md](FEATURES.md).
For development workflow, see [DEVELOPMENT.md](DEVELOPMENT.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
