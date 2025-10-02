# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the MHDBDB TEI Repository - a collection of TEI-encoded Middle High German literature texts with semantic annotations from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

## Repository Structure

### Core Data
- **tei/**: 666 TEI-encoded Middle High German texts (.tei.xml files)
- **authority-files/**: 7 controlled vocabulary XML files (47.3 MB total)
  - `persons.xml` (0.12 MB) - Authors and historical persons
  - `works.xml` (1.41 MB) - Work and manuscript metadata
  - `lexicon.xml` (32.59 MB) - Dictionary with grammatical annotations
  - `concepts.xml` (0.21 MB) - Semantic concept taxonomy
  - `genres.xml` (0.4 MB) - Literary genre classification
  - `names.xml` (0.03 MB) - Proper names with semantic relations
  - `variants.xml` (12.46 MB) - Orthographic variants extracted from TEI corpus

### Pre-Built Data Indexes
- **data/**: Pre-built JSON indexes for fast loading (replaces runtime XML parsing)
  - `authority-index.json.gz` (2.90 MB compressed) - Complete authority data with:
    - 43,750 lemmata with full sense details, etymology, and concept mappings
    - 210 persons with GND, Wikidata, and work references
    - 583 works with complete bibliographic details (titles, sigles, genres, biblStructs, handschriftencensus)
    - 567 concepts, 615 genres, 90 names (with concept connections)
    - 176,056 orthographic variant mappings
    - Performance maps: conceptToLemmas (581), genreToWorks (113)
  - `corpus-index.json.gz` (21 MB compressed) - TEI corpus data (666 texts)
- **scripts/**: Python build scripts for generating pre-built indexes
  - `build-authority-index.py` - Extracts complete authority data from XML files
  - `build-corpus-index.py` - Extracts TEI corpus data
  - `mhg_normalizer.py` - Middle High German text normalization utilities
  - `validate-indices.py` - Index validation and integrity checks
  - `generate-manifest.py` - Generates corpus manifest

### Web Interface
- **playground/**: Web-based exploration tool for TEI data analysis
  - `index.html` - Main interface
  - `js/` - JavaScript modules for data processing
    - `main.js` - Application entry point (`MHDBDBPlayground` class)
    - `authority-files.js` - Authority data handling (`AuthorityFilesManager`) - simplified loader
    - `tei-files.js` - TEI text processing (`TEIFilesManager`) with multi-lemma search
    - `storage-manager.js` - TEI file caching (`TEIStorageManager`)
    - `indexed-db-manager.js` - Core IndexedDB operations
    - `ui/` - Modular UI components
      - `UICore.js` - Core UI utilities and progress tracking
      - `AuthorityExplorers.js` - Authority file exploration interfaces (uses pre-built index)
      - `TEIExplorer.js` - TEI document analysis interface
      - `SearchHelpers.js` - Search patterns with MHG normalization
      - `MultiLemmaSearch.js` - Multi-lemma search modal interface
    - `utils/` - Utility modules
      - `text-normalizer.js` - Middle High German character normalization
  - `css/style.css` - Application styling
- **testing/**: Playwright test suite
  - `test.html` - Test suite interface
  - `test-utils.js` - Testing utilities
  - `playwright.config.js` - Test configuration with local web server setup
  - `tests/playground.spec.js` - End-to-end testing

## Data Architecture

### Pre-Built Index Architecture (Current - Main Branch)

**Loading Strategy**: Authority data is loaded from pre-built, compressed JSON indexes instead of parsing XML at runtime.

**Benefits**:
- **19.4× smaller download** (47.3 MB XML → 2.90 MB compressed JSON)
- **Faster loading** (no browser XML parsing overhead)
- **Lower memory usage** (no DOM trees stored in memory)
- **Simpler code** (direct object/array access instead of XPath/querySelector)

**Data Flow**:
1. Browser fetches `data/authority-index.json.gz` (2.90 MB)
2. Browser decompresses gzip in-memory
3. JSON parsed into `authorityData` arrays (persons, works, lemmata, etc.)
4. UI directly queries arrays/objects (no XML DOM)

**Index Structure** (`authority-index.json.gz`):
```javascript
{
  version: "1.0.0",
  generatedAt: "2025-10-02T08:10:00Z",
  persons: [{id, preferredName, gnd, wikidata, works, normalized}, ...],
  works: [{id, title, titles[], sigle, sigles[], author, authorRef, genres[], biblStructs[], handschriftencensus, normalized}, ...],
  lemmata: [{id, lemma, pos, senseCount, etymology[], senses[], normalized}, ...],
  concepts: [{id, termDE, termEN, normalized}, ...],
  genres: [{id, termDE, termEN, normalized}, ...],
  names: [{id, termDE, termEN, conceptIds[], normalized}, ...],
  variants: {normalizedForm: lemmaId, ...}, // 176,056 mappings
  maps: {
    conceptToLemmas: {conceptId: [lemmaIds]}, // 581 concepts
    genreToWorks: {genreId: [workIds]}, // 113 genres
    genreHierarchy: {genreId: [parentNames]} // 0 entries currently
  }
}
```

**Rebuilding Indexes**:
```bash
# Rebuild authority index (when authority-files/ XML changes)
python scripts/build-authority-index.py
# Output: data/authority-index.json.gz (2.90 MB)

# Rebuild corpus index (when tei/ files change)
python scripts/build-corpus-index.py
# Output: data/corpus-index.json.gz (21 MB)
```

**Note**: The `pre-main-site` branch uses the old architecture (runtime XML parsing) and can be used for comparison via git worktree.

### TEI Structure
TEI files follow standard TEI P5 guidelines with MHDBDB-specific annotations:
- Cross-references to authority files via `xml:id` attributes
- Semantic annotations using `@ana` attributes linking to concepts
- Word-level annotations with `@lemma` attributes for dictionary lookup

### Authority File References
All files use consistent cross-referencing:
```xml
<author ref="#person_445">Meister Eckhart</author>
<w lemma="vriunt" ana="#concept_12345">vriunt</w>
```

### Key Architectural Changes (October 2025)

**Migration from XML Parsing to Pre-Built Indexes**:
- ✅ Removed runtime XML parsing for authority files (`parsedXML` dependency eliminated)
- ✅ Build scripts extract complete data structures with all nested relationships
- ✅ Performance maps pre-computed (conceptToLemmas, genreToWorks)
- ✅ All UI code refactored to use index data instead of XML DOM queries
- ✅ XPath interface removed (low priority feature, can be re-added later if needed)
- ✅ Fixed deduplication bug in concept-to-lemmas mapping (old version counted duplicates)

**What Still Uses XML Parsing**:
- TEI files (user-uploaded) - still parsed in browser as needed
- This is correct and expected for user content

## Development Commands

### Testing
```bash
# Run all Playwright tests (automatically starts web server on port 8080)
npm test

# Run tests with UI (interactive mode)
npm run test:ui

# Run tests in debug mode (step through with breakpoints)
npm run test:debug

# Run tests with browser visible
npm run test:headed

# View test report (after test run)
npm run report
```

### Development Server
```bash
# Serve the project locally (preferred method)
npm run serve

# Then open: http://localhost:8080/playground/

# Alternative: Simple HTTP server (Python)
python -m http.server 8000
```

Note: Playwright tests automatically start the web server via `playwright.config.js`, so manual server startup is only needed for local development.

### Common XPath Queries
```xpath
# All preferred person names
//tei:persName[@type='preferred']

# All instances of specific lemma
//tei:w[@lemma='vriunt']

# All works by specific author
//work[author/@ref='#person_1']
```

### Working with TEI Files
- All TEI files are encoded in UTF-8
- Use XML parsers that support TEI namespace: `http://www.tei-c.org/ns/1.0`
- File naming follows MHDBDB sigla system (e.g., ABG.tei.xml = "Von der Abgeschiedenheit")

### Generating Variants Index
To regenerate variants.xml from the TEI corpus:
```bash
# On Windows (Python 3.13+)
python scripts/extract-variants.py

# Output: authority-files/variants.xml (12.46 MB)
# Statistics: 39,436 lemmas, 192,674 orthographic forms
```

The extraction script analyzes all 666 TEI files, extracting orthographic variants from `<w lemmaRef="..." wordRef="...">` elements and generating a structured TEI-compliant variants index.

## Search Architecture

The MHDBDB Playground provides **11 distinct search entry points** across two main categories, all with Middle High German character normalization (â→a, ô→o, ü→ue, etc.).

### Search Categories

#### A. Authority Files Exploration (6 searches)
Browse and search reference vocabularies (persons, works, lexicon, concepts, genres, names):

1. **Autoren anzeigen** → `AuthorityExplorers.searchAuthors()`
   - Searches `preferredName` field
   - Normalization: ✅ `SearchPatterns.textContainsNormalized()`

2. **Werke anzeigen** → `AuthorityExplorers.searchWorks()`
   - Searches `title`, `sigle`, `author` fields
   - Normalization: ✅ `SearchPatterns.multiFieldNormalized()`

3. **Lemmata anzeigen** → `AuthorityExplorers.searchLemmata()`
   - Searches `lemma` field in lexicon
   - Normalization: ✅ `SearchPatterns.textContainsNormalized()`

4. **Konzepte anzeigen** → `AuthorityExplorers.searchConcepts()`
   - Searches `termDE`/`termEN` fields
   - Normalization: ✅ `SearchPatterns.textContainsNormalized()`

5. **Gattungen anzeigen** → `AuthorityExplorers.searchGenres()`
   - Searches `termDE`/`termEN` fields
   - Normalization: ✅ `SearchPatterns.multiFieldNormalized()`

6. **Namen anzeigen** → `AuthorityExplorers.searchNames()`
   - Searches `termDE`/`termEN` fields
   - Normalization: ✅ `SearchPatterns.textContainsNormalized()`

#### B. TEI Text Analysis (5 searches)
Search within user-uploaded TEI corpus:

7. **Lemma-Suche** → `TEIExplorer.findLemmaInText()`
   - Searches `teiData.words[]` array
   - Normalization: ✅ `TextNormalizer.matchesNormalized()`

8. **Multi-Lemma-Suche (Absatz)** → `TEIFilesManager.searchMultipleLemmas()` with `contextType='paragraph'`
   - XML query: `<w lemmaRef*="lemma_879">`
   - Normalization: ✅ Via `searchLemmaByOrthography()` with variants index

9. **Multi-Lemma-Suche (Dokument)** → `TEIFilesManager.searchMultipleLemmas()` with `contextType='document'`
   - XML query: `<w lemmaRef*="lemma_879">`
   - Normalization: ✅ Via `searchLemmaByOrthography()` with variants index

10. **Multi-Lemma-Suche (Nähe)** → `TEIFilesManager.findCooccurringLemmas()`
    - XML query: `<w lemmaRef*="lemma_879">` with proximity analysis
    - Normalization: ✅ Via `searchLemmaByOrthography()` with variants index

11. **XPath Query** → `TEIFilesManager.executeXPathOnTEI()`
    - Raw XPath on TEI XML
    - Normalization: ⚠️ N/A (advanced users, direct XML query)

### Text Normalization Strategy

All searches use centralized MHG character normalization via `TextNormalizer` utility:

**Normalization Rules:**
- Long vowels: `â→a, ê→e, î→i, ô→o, û→u` (also `ā→a, ē→e, ī→i, ō→o, ū→u`)
- Umlauts: `ä→ae, ö→oe, ü→ue`
- Ligatures: `æ→ae, œ→oe`
- Other: `ǒ→o`

**Implementation:**
- **File:** `playground/js/utils/text-normalizer.js`
- **Methods:**
  - `TextNormalizer.normalizeMHG(text)` - Returns normalized text
  - `TextNormalizer.matchesNormalized(text, searchTerm)` - Check if text contains term
  - `TextNormalizer.exactMatchNormalized(text, searchTerm)` - Exact match comparison

**Search Flow Example:**
```
User searches "brot" in Lemmata anzeigen
   ↓
AuthorityExplorers.searchLemmata("brot")
   ↓
SearchPatterns.textContainsNormalized(lemmata, "brot", lemma => lemma.lemma)
   ↓
TextNormalizer.matchesNormalized("brôt", "brot")
   ↓
normalizeMHG("brôt") = "brot" ✅ Match!
```

### Multi-Lemma Variant Resolution

Multi-lemma searches use a 3-stage resolution process in `AuthorityFilesManager.searchLemmaByOrthography()`:

**Stage 1: Exact Match in Lexicon**
- Fastest path
- Searches canonical forms (e.g., "brôt")
- Uses normalized comparison

**Stage 2: Variants Index Search**
- Searches variants.xml with 192,674 attested orthographic variants
- Extracted from 666 TEI files
- Maps variants to canonical lemmas (e.g., "brott" → lemma_879)

**Stage 3: Partial Match Fallback**
- Uses `includes()` search on lexicon
- Catches fuzzy matches and partial terms

**Example:**
```
User searches "brott + win" in Multi-Lemma-Suche
   ↓
resolveLemmaIds(["brott", "win"])
   ↓
searchLemmaByOrthography("brott")
  → Stage 2: variants.xml → lemma_879 (brôt)
searchLemmaByOrthography("win")
  → Stage 2: variants.xml → lemma_7532 (wîn)
   ↓
searchMultipleLemmas([879, 7532], "paragraph")
   ↓
XML: <w lemmaRef="lexicon.xml#lemma_879">brott</w>
     <w lemmaRef="lexicon.xml#lemma_7532">win</w>
   ↓
✅ Results: Paragraphs containing both lemmas
```

## License and Attribution

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at

## Application Architecture

The playground uses a modular class-based architecture:

### Core Classes

#### Data Layer
- **`MHDBDBPlayground`** (main.js) - Main application controller, orchestrates data managers and UI components
- **`AuthorityFilesManager`** (authority-files.js) - Handles loading and parsing of authority XML files with 3-stage lemma resolution:
  - Stage 1: Exact match in lexicon (canonical forms)
  - Stage 2: Exact match in variants index (192,674 attested orthographic variants from TEI corpus)
  - Stage 3: Partial match fallback (includes search)
- **`TEIFilesManager`** (tei-files.js) - TEI document processing, text analysis, and advanced search features:
  - Single lemma search with context extraction
  - Multi-lemma search (paragraph/document level)
  - Co-occurrence analysis (proximity-based lemma search)
  - Word-level annotation extraction

#### Storage Layer (IndexedDB Architecture)
- **`IndexedDBManager`** (indexed-db-manager.js) - Core IndexedDB wrapper with two object stores:
  - `teiFiles` store - Large TEI file caching (>5MB files)
  - `authorityFiles` store - Authority file caching with expiration timestamps
- **`TEIStorageManager`** (storage-manager.js) - TEI-specific caching:
  - Automatic caching for large files (>5MB)
  - Persistent storage across browser sessions
  - No expiration policy (user-uploaded content)
- **`AuthorityStorageManager`** (authority-storage-manager.js) - Authority file caching:
  - 30-day expiration policy (720 hours)
  - Network fetch with fallback to cache
  - Automatic cache invalidation on expiry

#### UI Layer (Modular Components)
Replaced monolithic ui-helpers.js with specialized modules:
- **`UICore.js`** - Core UI utilities (progress tracking, file display, collapsible lists)
- **`AuthorityExplorers.js`** - Authority file exploration interfaces (persons, works, concepts, etc.)
- **`TEIExplorer.js`** - TEI analysis interfaces (lemma search, multi-lemma search, word extraction)
- **`XPathInterface.js`** - XPath query execution with syntax highlighting
- **`SearchHelpers.js`** - Advanced search utilities for multi-lemma and co-occurrence analysis

### Data Flow
1. **Authority files** loaded on startup via `AuthorityStorageManager`:
   - Check IndexedDB cache first (30-day TTL)
   - If expired or missing, fetch from `authority-files/` directory
   - Parse XML and extract persons, works, lexicon entries, concepts, genres, names, variants
   - Variants index: 39,436 lemmas with 192,674 orthographic forms extracted from TEI corpus
   - Store in IndexedDB with expiration timestamp
2. **TEI files** loaded from user upload or cache via `TEIStorageManager`:
   - User uploads TEI files through drag-and-drop interface
   - Files >5MB automatically cached in IndexedDB for session persistence
   - Parse XML and extract word tokens, annotations, cross-references
   - Link `@lemma` and `@ana` attributes to authority data
3. **UI components** provide interactive exploration:
   - Single/multi-lemma search across TEI corpus
   - Co-occurrence analysis (proximity-based)
   - XPath queries with syntax highlighting
   - Authority file browsers (filterable, sortable)
4. **Storage architecture** (IndexedDB replaces sessionStorage):
   - `teiFiles` store: No expiration (user data)
   - `authorityFiles` store: 30-day expiration (reference data)
   - Automatic cleanup of expired authority files on init

### Testing Architecture
- **Playwright** end-to-end tests in `testing/` directory
- **Test configuration** (`playwright.config.js`):
  - Automated web server startup: `npx http-server .. -p 8080`
  - Headless Chrome with `--disable-web-security` for local XML file access
  - Test timeout: 60 seconds per test
  - HTML and JSON test reports generated in `testing/test-results/`
- **Test isolation** - each test clears IndexedDB cache for clean state
- **Test suite** (`tests/playground.spec.js`):
  - 7 test suites: TEIStorageManager, TEIFilesManager, DOM Integration, Performance, IndexedDB Storage, Large File Handling, Error Handling
  - Tests run against `test.html` interface with automated progress tracking
  - Validates IndexedDB operations, large file caching, storage quota management
- **Test utilities** (`test-utils.js`):
  - Mock TEI file generation
  - IndexedDB test helpers
  - Progress tracking assertions

## Key Features

### Multi-Lemma Search
The playground implements advanced multi-lemma search capabilities:
- **Paragraph-level search**: Find paragraphs containing all specified lemmas
- **Document-level search**: List texts containing all lemmas anywhere
- **Co-occurrence analysis**: Find lemmas within specified word distance (proximity search)
- **Smart lemma resolution**: Supports both lemma IDs (`879`) and Middle High German terms (`brôt`)
- **Color-coded highlighting**: Different colors for different lemmas in results
- See [MULTI-LEMMA-SEARCH-IMPLEMENTATION.md](MULTI-LEMMA-SEARCH-IMPLEMENTATION.md) for detailed documentation

### Advanced Search Examples
```javascript
// Search for paragraphs containing both "brôt" (bread) and "wîn" (wine)
teiManager.searchMultipleLemmas(['879', '7532'], 'paragraph')

// Find co-occurring lemmas within 10 words of each other
teiManager.findCooccurringLemmas(['879', '7532'], 10)

// Resolve Middle High German terms to lemma IDs
authorityManager.resolveLemmaNames(['brôt', 'wîn'])
```

## Project Context

This is a research repository focused on:
- Digital humanities and medieval studies
- TEI-encoded corpus linguistics
- Semantic annotation of Middle High German literature
- Interactive data exploration for medievalists

When working with this codebase, respect the academic nature of the data and maintain the existing annotation standards and cross-reference integrity.

## Important Constraints

- **Frontend-only architecture**: All processing happens in the browser (no backend)
- **Desktop-focused**: Minimum 1200px screen width, not mobile-responsive
- **Large file handling**: Authority files total 34.8 MB, with `lexicon.xml` at 32.59 MB
- **IndexedDB required**: Large files cannot be handled via sessionStorage alone
- **TEI namespace**: Always use `http://www.tei-c.org/ns/1.0` when working with XML
- **UTF-8 encoding**: All TEI files use UTF-8 encoding