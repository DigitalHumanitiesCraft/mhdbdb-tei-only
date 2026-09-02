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
**Key Files:** `index.html`, `korpus.html`, `woerterbuch.html` + `assets/js/woerterbuch.js` (A–Z lemma register, #117), `assets/js/app.js`, `assets/js/site-chrome.js` (shared nav/footer behavior, every page), `assets/js/search/`, `assets/js/rendering/`

### Application Structure

**MainSiteApp** (`assets/js/app.js`)
- Initialize corpus loader
- Load pre-built corpus index (~40 MB compressed)
- Set up search interface and text selection
- Coordinate SearchEngine and TEITextReader

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
5. Create shared `TEICacheManager` (TEI DOM cache, IndexedDB)
6. Create `TEITextReader(corpus, authority, cache)`
7. Populate text list checkboxes from corpus index
8. Check URL parameters (`?textId=...&lemmaIds=...&position=...`)
9. If no URL params, show empty state (no auto-load): a placeholder prompting the user to enter a word/lemma or click a text (`showEmptyState()` in app.js)

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
| `<p>`, `<ab>` | | `<p>` | – |
| `<div>` | `@type`, `@n` | Always wraps children in `<div class="tei-div tei-div-{type}" data-type data-n>`. Prepended header is `<h3 class="section-head">{label} {n}</h3>` for `@type="chapter"` (rendered like `<head>`, #101) but `<div class="tei-div-header tei-div-{type}">{label} {n}</div>` for all other types | `.tei-div`, `.tei-div-{type}`, `.tei-div-header`, `.section-head` (label map: song→Lied, chapter→Kapitel, recipe→Rezept, number→Nr., section→Abschnitt, colophon→Kolophon, parallel→Parallelüberlieferung) |
| `<lg>` | `@n` | `<div data-n>` with `<span>Strophe {n}</span>` prefix | `.verse-group`, `.stanza-label` |
| `<l>` | `@n` | `<span data-n>` | `.verse-line` |
| `<lb>` | `@n` | numeric `@n`: `<br>` followed by `<span>{n}</span>`; non-numeric `@n` (e.g. `h_1` heading lines): `<br>` + empty anchor span (deep-link target only, no visible number – #158) | `.line-break`, `.lb-number`, `.lb-anchor` |
| `<pb>` | `@n` | `<span>[{n}]</span>` | `.page-break` |
| `<cb>` | `@n` | `<span title="Spalte {n}">[Sp. {n}]</span>` | `.column-break` |
| `<caesura>` | | `<span>\|\|</span>` | `.caesura` |
| `<note>` | `@type="year\|date"`, `@n` | `<span title="Datum\|Jahr">{n}</span>` (badge) | `.note-badge`, `.note-{type}` |
| `<hi>` | `@rend` (token-based) | `<span class="hi hi-{token1} hi-{token2} ...">` – splits `@rend` on whitespace, prefixes each token with `hi-` | `.hi`, `.hi-initial`, `.hi-upper_case_first_letter`, `.hi-upper_case`, `.hi-bold`, `.hi-italic` (compounds stack) |
| `<supplied>` | | `<span title="Editorische Ergänzung">[...]</span>` | `.supplied` |
| `<num>` | | `<span>` | `.number` |
| `<pc>` | `@join` | `<span data-join>` | `.punctuation` |
| `<seg>` | | (transparent – children only) | – |
| `<w>` | `@lemmaRef` (exact id match, see CONTRACTS §B.1) | `<mark>` | `.highlight` / `.highlight.multi-lemma` |
| `<w>` | `@lemmaRef` (no match) | escaped text + space | – |
| `<w>` | no `@lemmaRef` | escaped text + space | – |
| (unknown) | | recurse into children | – |

**Multi-lemma color assignment:** `lemmaColorMap[lemmaId] = colors[idx % 5]` – sequential assignment, wraps at 5.

**`<hi rend>` token-based rendering:** `@rend` is space-separated (CSS-class style). The renderer splits on whitespace and emits `hi-{token}` per token. Compound values like `rend="initial upper_case_first_letter"` produce `class="hi hi-initial hi-upper_case_first_letter"`, with rules stacking from CSS. ~43k compound values that previously fell through to the single-class default are now correctly styled. Source: [DESIGN.md §TEI Reading View CSS Classes](DESIGN.md).

**Position counting contract:** see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)

### TEI Cache Management

**TEICacheManager** (`assets/js/storage/tei-cache-manager.js`)
- Caches raw TEI XML strings in IndexedDB (database: `MHDBDB_TEI_Cache`) with HTTP validators (ETag / Last-Modified)
- `load()` revalidates via conditional GET at most once per file per page load (in-memory memo): unchanged files cost one 304 roundtrip, changed files re-download immediately (#151) – corpus updates are visible on the next page load, repeat loads in the same session are pure cache hits
- Cache fallback on network failure/timeout (15s), HTTP errors (5xx) and unparseable 200-bodies; corrupted entries auto-deleted; 30-day TTL purge runs at `init()` (cursor-based `cleanExpired`)
- **Cache invalidation and version check flow:** see [CONTRACTS.md](CONTRACTS.md#e-cache-invalidation)

## Playground Architecture

**Purpose:** Advanced research tool for medievalists and researchers
**URL:** https://dhcraft.org/mhdbdb-tei-only/playground/
**Key Files:** `playground/js/playground-main.js`, `playground/js/data/`, `playground/js/ui/`

### Application Structure

**MHDBDBPlayground** (`playground/js/playground-main.js`)
- Drop the legacy `MHDBDB_Playground` database (`dropLegacyPlaygroundDatabase()`, #314). The playground's only contact with IndexedDB is this deletion, never an initialization: the indexes live in the shared `CorpusLoader`
- Load authority index (~3 MB)
- Initialize data managers (authority, TEI)
- Set up modular UI components (24 modules; 25 before #314 removed `file-display.js` and `progress.js`, 23 until #193 added `horses-explorer.js`)

### Data Layer

**AuthorityFilesManager** (`playground/js/data/authority-manager.js`)
- Load and query authority data
- 3-stage lemma resolution:
  1. Exact match in lexicon (canonical forms)
  2. Variants dictionary lookup: normalized **mappings**, not raw forms. The build deduplicates the raw forms from `variants.xml` after normalization, so there are fewer mappings than forms (current figures, with a date, in [CONTRACTS §C](CONTRACTS.md#c-3-stage-lemma-resolution-algorithm))
  3. Prefix-match fallback, both directions, shared with the main site via `assets/js/lib/lemma-resolve.js` (#224; before that an unbounded substring test, one-directional here and bidirectional on the main site)
- Direct array access (no XML DOM queries)
- Performance maps for fast lookups

**TEIFilesManager** (`playground/js/data/tei-manager.js`)
- Multi-lemma search over the pre-built corpus index (the file-upload path was removed in #314). `searchMultipleLemmasUsingIndex()` dispatches on `contextType` into the three modes below; there is no single-lemma entry point here, the main site has its own
- Document mode: all lemmata anywhere in the same text
- Proximity mode: co-occurrence within N words, via `findCoveringWindow()` over sorted position lists
- Verse mode: co-occurrence within one `<l>` (#106), via the `lineStarts[]`/`lineEnds[]` arrays
- Uses the corpus index (current version: [TEI-MODEL.md §11](TEI-MODEL.md#11-versioning)) for document-level word positions plus `<l>`-boundary arrays (since v4.1.0)

### UI Layer (Phase 7 Modular Architecture)

**Module Organization:**
```
playground/js/ui/
├── core/              # Core UI utilities
│   ├── ui-helpers.js
│   └── router.js      # Hash-based URL routing (#48)
├── authority/         # Authority file exploration (7 modules)
│   ├── authority-ui.js
│   ├── person-explorer.js
│   ├── work-explorer.js
│   ├── lemma-explorer.js
│   ├── concept-explorer.js
│   ├── genre-explorer.js
│   └── name-explorer.js
├── tei/               # TEI text analysis (14 files: router + modal + 12 analysis modules)
│   ├── tei-ui.js                  # Router/entry point, not an analysis tool
│   ├── multi-lemma-search.js      # Modal outlier (DESIGN.md §Multi-Lemma, documented as such)
│   ├── word-frequency.js          # Word frequency analysis (#88, R1)
│   ├── text-statistics.js         # Text statistics (#89, R1)
│   ├── lemma-distribution.js      # Lemma distribution (#90, R1)
│   ├── verse-position-search.js   # Lemma search by verse position (#47.3)
│   ├── concept-distribution.js    # Concept distribution (#47 R2, + autocomplete #113)
│   ├── text-comparison.js         # Text comparison, A only/both/B only (#108)
│   ├── cooccurrence-ranking.js    # Co-occurrence ranking, DWDS style (#107)
│   ├── rhyme-dictionary.js        # Rhyme dictionary over lineEnds[] (#106, minimal variant)
│   ├── hapax-legomena.js          # Corpus-wide hapax legomena (#196)
│   ├── verse-ending-profile.js    # Verse-ending profile, top-N verse-final lemmata + rhyme pressure (#106, items 2/3)
│   ├── naming-explorer.js         # Extended character naming, curated for 4 works (#59, Beta)
│   └── horses-explorer.js         # Arthurian horses, curated for 5 works (#193, Beta)
└── search/
    └── SearchHelpers.js
```

**Benefits:**
- Clear separation of concerns
- Reusable patterns
- Easier testing and maintenance
- Net reduction: 5,536 lines removed

**Playground TEI module convention:** `playground/js/ui/tei/` holds fourteen files. The twelve analysis modules share one constructor/`show()`/`render()` pattern, with thunks instead of direct data references, a state-driven `renderBody()`, per-module escape helpers, and a MessageChannel yield for large aggregations. Two files are exempt: `tei-ui.js` is the router, and `multi-lemma-search.js` is a documented modal outlier. Two are a special case of their own: `naming-explorer.js` (#59) and `horses-explorer.js` (#193) do not read the corpus index but lazily fetch their own small index (`data/naming-index.json.gz`, `data/horses-index.json.gz`) via fetch plus pako, without an IndexedDB cache. Both belong to the playground's third group, "Experimentelle Forschungsdaten" (#194), which collects curated datasets from external research projects; the entry convention is in that issue. The pattern is documented as a template in [DESIGN.md §Playground TEI-Analysis Module Pattern](DESIGN.md#playground-tei-analysis-module-pattern).

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
| Versposition | `#verse-position` | Lemma search by verse-initial or verse-final position (#47.3) |
| Wortfrequenz | `#word-frequency` | Top-N lemmata, with stopword filter (#88) |
| Text-Statistiken | `#text-statistics` | Token count, lemma diversity, hapax rate (#89) |
| Lemma-Verteilung | `#lemma-distribution` | Bar chart per lemma across all texts (#90) |
| Begriffs-Verteilung | `#concept-distribution` | Bar chart per concept across all texts (#47 R2, with autocomplete dropdown #113) |
| Textvergleich | `#text-comparison` | Set operations A only / both / B only over two texts (#108) |
| Kookkurrenz-Ranking | `#cooccurrence-ranking` | Top-N neighboring lemmata of one lemma, POS-filtered (#107) |
| Reim-Wörterbuch | `#rhyme-dictionary` | Rhyme-partner lemmata at adjacent verse endings, suffix heuristic (#106) |
| Hapaxlegomena | `#hapax-legomena` | Lemmata unique across the corpus, with location and dictionary lookup (#196) |
| Versendings-Profil | `#verse-ending-profile` | Top-N verse-final lemmata per scope, with a "Reim-Druck" column (#106 items 2 and 3) |
| Erweiterte Figurenbezeichnungen | `#naming` | Curated proper names, antonomasias and epithets per character in 4 works (#59, beta) |
| Arthurische Pferde | `#horses` | Curated horse attestations in 5 works, with event filter and `?verseId=` reader deep link (#193, beta) |

**Parameters:**

| Param | Applies to | Effect |
|-------|-----------|--------|
| `q` | All authority views | Auto-fills search input and triggers search |
| `show` | All authority views | Expands detail panel for the given item ID |
| `lemmata` | `multi-lemma` only | Comma-separated lemma terms |
| `ids` | `multi-lemma` only | Optional, paired positionally with `lemmata`: the exact lemma id for that term, which pins the resolution instead of deriving it from the written form again (#58). Empty or non-numeric entries, and terms without a counterpart, fall back to the normal 3-stage resolution (CONTRACTS §C) |
| `mode` | `multi-lemma` | `proximity` (default), `document` or `verse` (same-verse search, #106 item 8); source `router.js`, `handleMultiLemmaRoute()` |
| `mode` | `lemmata` | `component` opens the word-component search (#239); the mode forces the search-input interface even without `q` |
| `dist` | `multi-lemma` only | Max word distance (integer) |

**Example:** `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10`

**Example with a pinned id (#58):** `#multi-lemma&lemmata=minne&ids=4130&mode=document`

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

**Purpose:** Persistent, linkable pages for individual lemmata – target URLs for Worterbuchnetz, MWB, and other external systems
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
1. `?id=879` – query parameter (canonical after redirect)
2. `#879` – hash (for systems that strip query params)
3. `/lemma/879` – path segment (pre-redirect, also works post-redirect)

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

A–Z entry page to the lemma pages. It loads the authority index only (via `CorpusLoader('data')`), buckets the 43,879 `lemmata` entries client-side by the first letter of `normalized` (NFD strip as a fallback for `ë` and `ú`, numeric lemmata go into the `#` bucket), and renders a paginated register per letter (200 entries per page, sorted with `Intl.Collator('de')`). URL state `?buchstabe=&seite=` via `history.replaceState`. Deliberately no build artifact of its own: the existing index is enough.

---

## Storage Architecture

### The playground no longer has a database of its own (#314)

Until July 2026 the playground kept a second IndexedDB database, `MHDBDB_Playground`, managed by `playground/js/indexed-db-manager.js`. Its only store, `tei_files`, held the TEI files uploaded by the user and was written from `data/storage/tei-storage.js`. With the dead upload path removed (#314), both the writer and the manager are gone.

`playground-main.js` deletes the database once at startup via `indexedDB.deleteDatabase('MHDBDB_Playground')` (`dropLegacyPlaygroundDatabase()`). On a database that does not exist this is a no-op, so the call may run on every start. It replaces the earlier schema migration from #280, which cleared three writer-less legacy stores (`corpus_tei_files`, `authority_files`, `metadata`) out of existing browser databases via `deleteObjectStore`: after #314 no production code instantiates the manager any more, so that migration would no longer run. Dropping the whole database does the same job more thoroughly.

Corpus and authority data were never stored here. The playground reads them through the same `CorpusLoader` as the main site, that is from `MHDBDBMainSite`. A second cache path must not reappear.

**Expiration policy (ADR-004), enforced in the `CorpusLoader`:**
- Authority and corpus index: 30-day cache (`CACHE_DURATION` in `assets/js/lib/corpus-loader.js`, database `MHDBDBMainSite`) plus version invalidation
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

**Generator:** `scripts/build-api.py` (#45) – reads the two pre-built indexes (`data/*.json.gz`), emits 2,742 plain JSON files (~14 MB) into `api/`.

**Served by:** GitHub Pages, like every other file in the repo – no backend, no runtime component, CORS open (Pages sends `Access-Control-Allow-Origin: *`). The main site and playground do **not** consume the API (they load the gzipped indexes); it exists purely for external programmatic access, so it adds zero runtime cost to the site.

**Structure:** root manifest `api/index.json` (counts + source index versions), lemmata as a single bundle (`api/lemmata/index.json`, 43,879 records), individual `{id}.json` + summary `index.json` per collection (persons, works, concepts, genres, names, texts). Every file carries a `license` field. Human documentation: `api/index.html` (German, standalone page).

**Freshness:** deterministic build + CI gate ("Freshness API" in `data-integrity.yml`) keep `api/` byte-identical to what the committed indexes produce. Contracts (URL schema stability, field schemas): [CONTRACTS.md §G](CONTRACTS.md#g-static-json-api-contract-45).

## External Services

### Wörterbuchnetz API

- **Endpoint**: `https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{searchpattern}`
- **Response**: `{ result_set: [{ sigle, lemma (HTML-encoded), gram, wbnetzid, wbnetzlink }] }`
- **Queried dictionaries** (#258, five since 2026-07-31): MWB, Lexer, LexerN (Lexer-Nachträge), BMZ (Benecke/Müller/Zarncke), FindeB (Findebuch) – all via `/dictionaries/{sigle}/lemmata/{form}`, shared client `assets/js/lib/woerterbuchnetz.js`, `fetchWbnetzEntries()`. The list and its display order live in the exported `DICTIONARIES`, the sigle-to-title resolution in `DICTIONARY_TITLES`; the API serves 52 dictionaries but exposes no titles
- **Search term**: Normalized lemma form (e.g., "brot" not "brôt")
- MHDBDB is NOT a directly linkable dictionary in Wörterbuchnetz
- **Integration**: Dynamic fetch on the lemma page (grouped by dictionary, full titles as headings), in the korpus-search lemma panel and in the hapax detail cell (both compact: sigle plus `title` tooltip, three entries per dictionary)
- **Load**: five parallel requests per lemma, memoized per normalized form for the session. Measured 2026-07-31 in Chrome: 31–81 ms for all five, 41 ms for the panel's worst case of three lemmata (15 requests) – no throttling observed

### MWB Online (Mittelhochdeutsches Wörterbuch, Trier)

- **Portal**: `https://www.mhdwb-online.de/`
- **Deep link**: `https://www.mhdwb-online.de/wb/{lid}` (requires numeric MWB lid)
- **Metadata API** (HTTP only): `http://tares-neu.uni-trier.de:8080/exist/rest/db/MWB/Services/retrieve_MWB_lemma_metadata.xql?lemma={term}`
- **API response**: XML with `<entry><MWB><id>, <lemma>, <gram>, <url></MWB><MWV><lexer>, <bmz>, <fb></MWV></entry>`
- **Current integration**: Dynamic lookup via the Wörterbuchnetz HTTPS API (MWB is one of the five queried dictionaries there; #73, 2026-05-12, list extended in #258). Results render as deep-links to `http://mhdwb-online.de` via `target="_blank"` (navigation to http targets from https pages is not Mixed-Content-blocked). The MWB is still being published, so an empty MWB result for a well-attested word is normal, not a failure
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
- ✅ Main site features (of the 25 tests disabled until #43, `259bc505a` reactivated 13 and deleted the other 12 along with their specs; the inventory of all specs is in [DEVELOPMENT.md → Test File Inventory](DEVELOPMENT.md))

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
**Solution:** Three-stage lookup (exact → variants → prefix match in both directions)
**Result:** Attested orthographic variants resolve via stage 2; stage 3 catches stems and inflected forms without drowning them in short-lemma noise (#224)

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
**Solution:** specialized modules organized by feature (module tree and current count above, under "UI Layer")
**Result:** 5,536 lines removed, improved maintainability

### Shared Lemma Matching (#130)

**Problem:** The exact-token `@lemmaRef` match was inline-duplicated at 6 sites across 4 files; one copy used a substring test (#126), highlighting wrong words
**Solution:** Single `lemmaRefMatchesId()` in `assets/js/lib/lemma-match.js`, shared by main site and playground (like `text-normalizer.js`)
**Result:** One tested source of truth (CONTRACTS §B.1); no copy can silently regress

### Build-Injected Site Chrome

**Problem:** Nav + footer were hand-maintained per page, drifting out of sync
**Solution:** Single-source partials (`includes/_nav.html`, `includes/_footer.html`) injected into the marked region (`NAV:START`/`FOOTER:START`) of every registered page by `scripts/build-pages.py` (idempotent, `--check` drift gate); shared behavior (mobile menu, current-year, cross-browser clear-site-data) in `assets/js/site-chrome.js`, loaded on every page via the footer partial
**Result:** One nav/footer source; active page gets `aria-current="page"` automatically

---

For data structures and schemas, see [DATA-MODEL.md](DATA-MODEL.md).
For user-facing functionality, see [FEATURES.md](FEATURES.md).
For development workflow, see [DEVELOPMENT.md](DEVELOPMENT.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
