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
  - **data-wrangling/**: Scripts for enriching authority files with external data
    - `enhance_works_with_zotero.py` - Fetches bibliographic data from Zotero API and updates works.xml
    - `sync_tei_headers.py` - Syncs authority file metadata to TEI file headers
    - `test_zotero_extraction.py` - Validation tests for Zotero data extraction

### Web Interfaces

#### Main Site (index.html + korpus.html)
- **Purpose**: Public-facing corpus browser for general users and students
- **Architecture**: Simple search and display with pre-built corpus index
- **Key Files**:
  - `index.html` - Main landing page with corpus statistics
  - `korpus.html` - Search page with text selection interface
  - `js/app.js` - Main site application controller (`MainSiteApp`)
  - `js/search/search-engine.js` - Search functionality across corpus
  - `js/rendering/text-renderer.js` - Context view with lemma highlighting
  - `js/rendering/tei-text-reader.js` - Reading view with full text and rich metadata
  - `js/storage/tei-cache-manager.js` - TEI file caching
- **Data Source**: Uses `data/corpus-index.json.gz` (21 MB) for instant search
- **Features**:
  - Single lemma search with MHG normalization
  - Text selection via checkboxes (include/exclude texts from search)
  - Filter text list by title, sigle, or author
  - Auto-scroll to results with sticky header offset
  - White result cards on gray background for visual distinction
  - **Reading View** (Oct 6, 2025):
    - Full TEI text display with lemma highlighting
    - Rich metadata panel (expandable/collapsible)
    - Wikidata images with attribution
    - Separate work vs author identifiers (GND/Wikidata)
    - Zotero bibliographic links
    - Context navigation (prev/next occurrence)

#### Playground (playground/)
- **Purpose**: Advanced research tool for medievalists and researchers
- **Architecture**: Modular UI with 18 specialized components
- **Key Files**:
  - `index.html` - Playground interface
  - `js/` - JavaScript modules for data processing (modular architecture)
    - `playground-main.js` - Application entry point (`MHDBDBPlayground` class)
    - `indexed-db-manager.js` - Core IndexedDB operations
    - `data/` - Data management layer
      - `authority-manager.js` - Authority data handling (`AuthorityFilesManager`)
      - `tei-manager.js` - TEI text processing (`TEIFilesManager`) with multi-lemma search
      - `storage/tei-storage.js` - TEI file caching (`TEIStorageManager`)
    - `ui/` - Modular UI components (Phase 7 refactoring)
      - `core/` - Core UI utilities
        - `ui-helpers.js` - General UI update functions
        - `progress.js` - Progress tracking and spinner management
        - `file-display.js` - File list display and filtering
      - `authority/` - Authority file exploration (6 modules)
        - `authority-ui.js` - Main authority UI coordinator
        - `person-explorer.js` - Person search and display
        - `work-explorer.js` - Work search and display
        - `lemma-explorer.js` - Lemma search with sense details
        - `concept-explorer.js` - Concept taxonomy browser
        - `genre-explorer.js` - Genre classification browser
        - `name-explorer.js` - Proper names browser
      - `tei/` - TEI text analysis
        - `tei-ui.js` - TEI exploration interface (`TEIExplorer`)
        - `multi-lemma-search.js` - Multi-lemma search modal (`MultiLemmaSearchUI`)
      - `search/SearchHelpers.js` - Search patterns with MHG normalization
  - `css/style.css` - Application styling
- **lib/**: Shared utilities (used by both main site and playground)
  - `text-normalizer.js` - Middle High German character normalization
  - `corpus-loader.js` - Pre-built index loader with IndexedDB caching
- **testing/**: Playwright test suite
  - `playwright.config.js` - Test configuration with local web server setup
  - `tests/*.spec.js` - End-to-end test files (40 passing, 25 skipped)

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
  version: "1.1.0",  // Bumped for GND/Wikidata work identifiers
  generatedAt: "2025-10-06T12:00:00Z",
  persons: [{id, preferredName, gnd, wikidata, works, normalized}, ...],
  works: [{id, title, titles[], sigle, sigles[], author, authorRef, gnd, wikidata, genres[], biblStructs[], handschriftencensus, normalized}, ...],
  lemmata: [{id, lemma, pos, senseCount, etymology[], senses[], normalized}, ...],
  concepts: [{id, termDE, termEN, normalized}, ...],
  genres: [{id, termDE, termEN, normalized}, ...],
  names: [{id, termDE, termEN, conceptIds[], normalized}, ...],
  variants: {normalizedForm: lemmaId, ...}, // 176,056 mappings
  maps: {
    conceptToLemmas: {conceptId: [lemmaIds]}, // 581 concepts
    genreToWorks: {genreId: [workIds]}, // 113 genres
    genreHierarchy: {genreId: [parentNames]} // 613 entries
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

**Phase 7: Modular UI Architecture** (Merged Oct 2, 2025):
- ✅ Decomposed monolithic UI files into 18 specialized modules
- ✅ Organized by feature: core/, authority/, tei/, search/
- ✅ Each explorer is now an independent module (person, work, lemma, concept, genre, name)
- ✅ Improved maintainability and code organization
- ✅ Net reduction: 5,536 lines removed from codebase

**Corpus Index v4.0.0 Migration** (Oct 5, 2025):
- ✅ **Fixed proximity search position alignment** - removed paragraph-based indexing
- ✅ **Document-level word indexing** - Python and JavaScript now use identical `//tei:body//tei:w[@lemmaRef]` extraction
- ✅ **100% word coverage** - all words in `<body>` are indexed (no missing `<head>` content)
- ✅ **Variant resolution fixed** - "brot" and "brott" now correctly resolve to same lemma via variants.xml (176,056 mappings)
- ✅ **Overlap deduplication** - proximity search no longer shows redundant results with overlapping context windows
- ✅ **Complete text display** - context now includes ALL `<w>` elements (with or without `@lemmaRef`) for readable output
- ✅ **Smaller index size** - ~30% reduction by removing paragraph metadata
- ✅ **Simplified architecture** - removed paragraph search mode entirely (only proximity + document modes remain)

**Main Site Simplification** (Oct 5, 2025):
- ✅ **Removed genre/author filter dropdowns** - replaced with text selection interface matching playground
- ✅ **Added text selection feature** - 666 texts displayed with checkboxes (all selected by default)
- ✅ **Text filtering** - live search by title, sigle, or author with "Alle/Keine" buttons
- ✅ **Improved search UX** - auto-scroll to results with 80px offset for sticky header
- ✅ **Better visual hierarchy** - white result cards on gray background with brand color accents
- ✅ **Search filtering** - SearchEngine now respects `includedTexts` Set for selective corpus search

**Reading View and Rich Metadata** (Oct 6, 2025):
- ✅ **TEI Reading View** - New immersive text reader with lemma highlighting and context navigation (js/rendering/tei-text-reader.js)
- ✅ **Authority Index v1.1.0** - Added GND/Wikidata identifiers for works (separate from author identifiers)
- ✅ **Wikidata Integration** - Automatic image fetching from Wikidata API with cleaned attribution
- ✅ **Dual Identifier Display** - Separate sections for work identifiers vs author identifiers
- ✅ **Scrollable Metadata** - Max-height 400px with overflow scrolling for better UX on small screens
- ✅ **Heroicons Migration** - Replaced all emoji icons (📄, 📖, 🔗, ▶, ▼) with Heroicons for design consistency
- ✅ **Cache Invalidation** - Version-based caching for authority index (v1.1.0)
- ✅ **Improved Labeling** - Updated korpus.html text selection label with inline Heroicons
- ✅ **Playground Enhancements** - Work explorer now displays GND/Wikidata identifiers
- ✅ **TEI Entities** - Confirmed angle bracket entities (`&lt;`, `&gt;`) are correct XML encoding for punctuation marks in `<seg type="pc">` elements

**Multi-Lemma Reader Integration** (Oct 6, 2025):
- ✅ **Clickable Proximity Results** - Playground proximity search results now open main site reading view
- ✅ **Multi-Lemma Highlighting** - Support for multiple lemmas with color coding (5 colors: red, blue, green, yellow, purple)
- ✅ **URL Parameter Passing** - Opens korpus.html with `?textId=ABG&lemmaIds=879,7532&position=310`
- ✅ **Position Synchronization** - Fixed word counting logic to match corpus index (only count words with `@lemmaRef`)
- ✅ **Precise Context Scrolling** - Automatically scrolls to the exact clicked context in full-text view
- ✅ **Cross-Platform Workflow** - Seamless navigation from playground advanced search to main site immersive reading
- ✅ **Position Tracking** - Word position tracked during TEI parsing for accurate highlight targeting

**Data Wrangling Workflow (Oct 30, 2025 - Issue #19)**:
- ✅ **Zotero API Integration** - Enhanced works.xml with bibliographic metadata from Zotero API
- ✅ **Comprehensive Field Extraction** - All Zotero fields now extracted (edition, seriesNumber, issue, etc.)
- ✅ **German Title Case Conversion** - Automatic conversion of titles to proper German bibliographic style
- ✅ **Complete Data Coverage** - Script updates ALL items with Zotero data, not just those with editors
- ✅ **680 biblStruct elements** - Complete bibliographic records for 582 works
- Scripts: `enhance_works_with_zotero.py`, `sync_tei_headers.py`, `test_zotero_extraction.py`

**Recent Bug Fixes and Improvements** (Oct 2-6, 2025):
- ✅ Fixed test suite timeout issue (skipped main site tests)
- ✅ Rebuilt empty authority index (0 bytes → 3.0 MB)
- ✅ Added *.code-workspace to .gitignore
- ✅ Test suite now completes in 2.7 minutes (40 passing, 25 skipped)
- ✅ Fixed missing words in proximity search results (words without `@lemmaRef` now included)
- ✅ Fixed variant normalization in authority-manager.js (flat dictionary lookup instead of array iteration)
- ✅ Fixed genreHierarchy parsing (Oct 6, 2025) - now correctly uses `<ptr type="broader">` references instead of nested categories (0 → 613 entries)
- ✅ Removed redundant listRelation from persons.xml (Oct 6, 2025) - eliminated 590 lines of duplicate person-work relationships (issue #8)
- ✅ Improved concept explorer UX (Oct 6, 2025) - replaced inline "first 20" list with full searchable interface, clickable lemma navigation to Lemma Explorer (issue #6)
- ✅ Code cleanup (Oct 6, 2025) - removed 28 lines of dead code and legacy comments from playground JavaScript files
- See [BUGFIX-2025-10-02.md](docs/BUGFIX-2025-10-02.md) and [PROXIMITY-SEARCH-FIX-PLAN.md](PROXIMITY-SEARCH-FIX-PLAN.md) for details

**What Still Uses XML Parsing**:
- TEI files (user-uploaded) - still parsed in browser as needed
- This is correct and expected for user content

## Knowledge Documentation Guidelines

This project maintains comprehensive knowledge documentation in the `docs/` directory. These guidelines ensure documentation remains focused, actionable, and maintainable.

### Philosophy

**Knowledge Documentation vs Reference Documentation:**
- **Knowledge docs** (docs/*.MD) explain WHY and WHAT - architectural decisions, data relationships, system design
- **Reference docs** (README.md, code comments) explain HOW - installation steps, API usage, implementation details
- **Target audience:** Future developers (including yourself) trying to understand the system, not operate it

**Core Principle:** Focus on knowledge transfer, not operation manuals. Developers know how to install Node.js - they need to understand why we chose pre-built indexes over runtime XML parsing.

### Documentation Structure

**Hub-and-Spoke Architecture:**
- **INDEX.MD** - Central gateway providing 3-5 minute overview with navigation to specialized documents
- **DATA-MODEL.MD** - Data sources, schemas, transformation pipeline
- **ARCHITECTURE.MD** - Technical components, data flow, storage patterns
- **FEATURES.MD** - User-facing functionality descriptions
- **DEVELOPMENT.MD** - Build commands, git workflow, deployment
- **RESEARCH.MD** - Academic context, standards, methodological background
- **DECISIONS.MD** - Architecture Decision Records (ADRs) with full rationale

**Progressive Disclosure:**
- INDEX.MD = 30-second overview → specialized docs = 5-10 minute deep dive → code = implementation details
- Each document focuses on ONE concern - no duplication
- Cross-reference sparingly, only when essential for understanding

### Core Writing Rules

**✅ DO:**
- Focus on **unique architectural decisions** and their rationale (e.g., "Pre-built indexes eliminate 47MB XML parsing → 19× faster loading")
- Explain **data structures and relationships** (e.g., "3-stage lemma resolution: exact match → variants → partial match")
- Document **trade-offs and alternatives** (e.g., "Client-only = zero hosting cost but limited processing power")
- Use **descriptive headers** for scanability (e.g., "Multi-Lemma Proximity Search" not "Search Feature 3")
- Include **one concrete example** per concept (not three variations)
- Mention **key version changes** that affect understanding (e.g., "v4.0.0 removed paragraph-based indexing")

**❌ DON'T:**
- Include **exact metrics/quantifications** unless essential (say "hundreds of texts" not "666 texts" repeated 10 times)
- Write **installation instructions** (developers know `npm install`, focus on what's unique to this project)
- Add **redundant code examples** (full class implementations belong in code, not docs)
- Create **troubleshooting sections** (use GitHub issues for this)
- Show **expected command outputs** (developers can run commands themselves)
- Repeat **information across documents** (each fact documented once, cross-reference if needed)
- Over-use **cross-references** (not every paragraph needs "See ARCHITECTURE.MD#section")

### Anti-Patterns to Avoid

**Excessive Quantification ("blabla about numbers"):**
```
BAD:  "666 TEI files, 43,750 lemmata, 210 persons, 583 works, 176,056 variants"
GOOD: "Hundreds of TEI texts with tens of thousands of dictionary entries"

BAD:  "authority-index.json.gz is 2.90 MB compressed from 15 MB uncompressed"
GOOD: "Authority index compressed to 3 MB (19× reduction)"
```

**Accessibility Blabla (everyone knows this):**
```
BAD:  Detailed Node.js installation instructions for Windows/Mac/Linux
GOOD: "Requires Node.js 16+" (one line)

BAD:  "Check version: node --version, should be 16.0.0 or higher"
GOOD: Omit entirely (developers know this)
```

**Redundant Examples:**
```
BAD:  Three code examples showing slight variations of same pattern
GOOD: One clear example demonstrating the concept

BAD:  Expected command output for every bash command
GOOD: Show output only for non-obvious commands
```

**Over-Documentation:**
```
BAD:  "For more details see ARCHITECTURE.MD#section" after every paragraph
GOOD: One reference at end of major section

BAD:  Full JavaScript class implementation with all methods
GOOD: Key method signatures and high-level flow description
```

### Document-Specific Guidelines

**INDEX.MD (150-200 lines):**
- Gateway document only - no deep dives
- High-level project overview with key numbers (rounded)
- Quick Start section for each user type
- Navigation table to specialized docs
- NO implementation details

**DATA-MODEL.MD (200-250 lines):**
- Data source descriptions and schemas
- Transformation logic (XML → JSON)
- Index structures with field descriptions
- NO full pipeline code, NO every validation rule

**ARCHITECTURE.MD (250-300 lines):**
- Component descriptions and responsibilities
- Data flow between components
- Key architectural patterns (caching, normalization)
- NO full class implementations, NO every method

**FEATURES.MD (200-250 lines):**
- User-facing feature descriptions
- What features do, not how they're implemented
- Visual design and interaction patterns
- NO code examples, NO API documentation

**DEVELOPMENT.MD (150-200 lines):**
- Build commands and git workflow
- Prerequisites (minimal - just versions)
- Deployment process
- NO troubleshooting, NO debug commands, NO installation HOWTOs

**RESEARCH.MD (200-250 lines):**
- Academic context and project background
- TEI/MHG standards and methodologies
- Research questions the project addresses
- CAN be detailed (this is unique knowledge)

**DECISIONS.MD (400-500 lines):**
- Architecture Decision Records (ADRs)
- One ADR per major decision
- Template: Context → Problem → Alternatives → Decision → Consequences
- SHOULD be detailed (captures reasoning for posterity)

### Examples: Good vs Bad

**Good - Focused on Core Knowledge:**
```
"The project migrated from runtime XML parsing to pre-built JSON indexes
because 47MB of authority files caused 30-second load times in browsers.
Pre-built indexes reduce download to 3MB and eliminate parsing overhead,
achieving 19× faster loading. Trade-off: requires Python build step when
XML sources change."
```

**Bad - Excessive Detail and Metrics:**
```
"The authority-index.json.gz file is 2.90 MB compressed (uncompressed: 15.3 MB),
generated on 2025-10-06 at 12:00:00 UTC, containing exactly 43,750 lemmata,
210 persons with GND identifiers, 583 works with bibliographic metadata,
567 concepts, 615 genres, 90 names, and 176,056 variant mappings extracted
from the TEI corpus using the extract-variants.py script which takes
approximately 2 minutes 45 seconds to run on a modern machine..."
```

**Good - Essential Architecture:**
```
"3-stage lemma resolution handles orthographic variants:
1. Exact match in lexicon (canonical forms like 'brôt')
2. Variants dictionary lookup (176k attested forms → lemma IDs)
3. Partial match fallback (fuzzy search)
This achieves 100% recall for historical spelling variations."
```

**Bad - Over-Explained with Code:**
```javascript
// Full 50-line class implementation with every method,
// input validation, error handling, and three usage examples
class AuthorityFilesManager {
  constructor() { ... }
  searchLemmaByOrthography(searchTerm) {
    // Stage 1: exact match
    const normalized = TextNormalizer.normalizeMHG(searchTerm);
    let lemma = this.authorityData.lemmata.find(l =>
      TextNormalizer.matchesNormalized(l.lemma, normalized)
    );
    // ... 40 more lines
  }
}
```

**Good - Trade-offs Explained:**
```
"Client-only architecture eliminates server costs and maintenance but limits
processing power to browser capabilities. Large corpus searches can take
5-10 seconds. Alternative (rejected): Backend API would enable faster search
but requires hosting costs and server maintenance."
```

**Bad - Installation Blabla:**
```
"To install Node.js, visit https://nodejs.org and download the installer
for your operating system. On Windows, run the .msi installer. On Mac,
use the .pkg installer or install via Homebrew with 'brew install node'.
On Linux, use your package manager: 'sudo apt install nodejs' on Ubuntu,
'sudo yum install nodejs' on CentOS. After installation, verify with
'node --version' which should output '16.0.0' or higher..."
```

### Target Line Counts (Realistic)

Based on analysis of well-documented projects:
- **INDEX.MD:** 150-200 lines (gateway, no deep dives)
- **DATA-MODEL.MD:** 200-250 lines (schemas and transformations)
- **ARCHITECTURE.MD:** 250-300 lines (components, not implementations)
- **FEATURES.MD:** 200-250 lines (user-facing descriptions)
- **DEVELOPMENT.MD:** 150-200 lines (build commands, no troubleshooting)
- **RESEARCH.MD:** 200-250 lines (academic context, can be detailed)
- **DECISIONS.MD:** 400-500 lines (ADRs need full rationale)

**Total:** ~1,800 lines for complete knowledge base (vs 3,000+ with over-documentation)

### Maintenance

**When to Update Docs:**
- After architectural changes (new components, removed features)
- After data model changes (new index fields, schema changes)
- After major refactorings (e.g., Phase 7 modular UI)
- When adding ADRs for significant decisions

**When NOT to Update Docs:**
- Bug fixes (unless they reveal architectural issues)
- Minor UI tweaks
- Dependency updates
- Code cleanup without behavior changes

**Review Checklist Before Committing Docs:**
- [ ] Is this core knowledge or operational detail? (Only document core knowledge)
- [ ] Am I repeating information from another document? (Remove duplication)
- [ ] Are metrics essential to understanding? (Most aren't)
- [ ] Would a developer be confused without this? (If not, cut it)
- [ ] Does this belong in code comments instead? (Implementation details do)

## System Requirements

### Prerequisites
- **Node.js**: 16+ (for npm scripts and testing)
- **Python**: 3.13+ (for building pre-built indexes from XML sources)
  - Required packages: `lxml`, `datetime`
  - Install: `pip install lxml`
- **Web Browser**: Chrome/Chromium (for Playwright tests)
- **Git**: For version control

### Python Usage
Python is **required** for:
- Building authority index: `python scripts/build-authority-index.py`
- Building corpus index: `python scripts/build-corpus-index.py`
- Extracting variants: `python scripts/extract-variants.py`
- Validating indices: `python scripts/validate-indices.py`

**Note**: Pre-built indexes are included in the repository, so Python is only needed if you modify source XML files in `authority-files/` or `tei/` directories.

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

The MHDBDB Playground provides **10 distinct search entry points** across two main categories, all with Middle High German character normalization (â→a, ô→o, ü→ue, etc.).

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

#### B. TEI Text Analysis (4 searches)
Search within user-uploaded TEI corpus:

**Note:** v4.0.0 removed paragraph-based multi-lemma search due to position alignment issues. Only document-level and proximity searches remain.

7. **Lemma-Suche** → `TEIExplorer.findLemmaInText()`
   - Searches `teiData.words[]` array
   - Normalization: ✅ `TextNormalizer.matchesNormalized()`

8. **Multi-Lemma-Suche (Dokument)** → `TEIFilesManager.searchMultipleLemmas()` with `contextType='document'`
   - XML query: `<w lemmaRef*="lemma_879">`
   - Normalization: ✅ Via `searchLemmaByOrthography()` with variants index

9. **Multi-Lemma-Suche (Nähe)** → `TEIFilesManager.findCooccurringLemmas()`
    - XML query: `<w lemmaRef*="lemma_879">` with proximity analysis (document-level positions)
    - Normalization: ✅ Via `searchLemmaByOrthography()` with variants index

10. **XPath Query** → `TEIFilesManager.executeXPathOnTEI()`
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
- **File:** `lib/text-normalizer.js` (shared utility)
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
User searches "brott + win" in Multi-Lemma-Suche (Nähe)
   ↓
resolveLemmaIds(["brott", "win"])
   ↓
searchLemmaByOrthography("brott")
  → Stage 2: variants.xml → lemma_879 (brôt)
searchLemmaByOrthography("win")
  → Stage 2: variants.xml → lemma_7532 (wîn)
   ↓
findCooccurringLemmas([879, 7532], maxDistance=10)
   ↓
v4.0.0: Uses document-level word positions from corpus index
   ↓
✅ Results: Proximity matches within 10 words of each other
```

## License and Attribution

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at

## Application Architecture

The playground uses a modular class-based architecture:

### Core Classes

#### Data Layer
- **`MHDBDBPlayground`** (playground-main.js) - Main application controller, orchestrates data managers and UI components
- **`AuthorityFilesManager`** (data/authority-manager.js) - Authority data loading via pre-built index with 3-stage lemma resolution:
  - Stage 1: Exact match in lexicon (canonical forms)
  - Stage 2: Exact match in variants index (192,674 attested orthographic variants from TEI corpus)
  - Stage 3: Partial match fallback (includes search)
- **`TEIFilesManager`** (data/tei-manager.js) - TEI document processing, text analysis, and advanced search features:
  - Single lemma search with context extraction
  - Multi-lemma search (document level, v4.0.0)
  - Co-occurrence analysis (proximity-based lemma search with document-level indexing, v4.0.0)
  - Word-level annotation extraction
- **`CorpusLoader`** (lib/corpus-loader.js) - Shared loader for pre-built indexes:
  - Loads authority-index.json.gz and corpus-index.json.gz
  - IndexedDB caching with 30-day expiration
  - Pako-based gzip decompression

#### Storage Layer (IndexedDB Architecture)
- **`IndexedDBManager`** (indexed-db-manager.js) - Core IndexedDB wrapper with two object stores:
  - `teiFiles` store - Large TEI file caching (>5MB files)
  - `authorityFiles` store - Authority file caching with expiration timestamps
- **`TEIStorageManager`** (data/storage/tei-storage.js) - TEI-specific caching:
  - Automatic caching for large files (>5MB)
  - Persistent storage across browser sessions
  - No expiration policy (user-uploaded content)

#### UI Layer (Modular Components - Phase 7 Refactoring)
Replaced monolithic files with specialized modules organized by feature:
- **Core UI** (ui/core/)
  - `ui-helpers.js` - General UI update functions
  - `progress.js` - Progress tracking and spinner management
  - `file-display.js` - File list display and filtering
- **Authority Exploration** (ui/authority/)
  - `authority-ui.js` - Main coordinator for authority searches
  - `person-explorer.js`, `work-explorer.js`, `lemma-explorer.js` - Individual explorers
  - `concept-explorer.js`, `genre-explorer.js`, `name-explorer.js` - Taxonomy browsers
- **TEI Analysis** (ui/tei/)
  - `tei-ui.js` - TEI exploration interface (lemma search, word extraction)
  - `multi-lemma-search.js` - Multi-lemma search modal with variant resolution
- **Search Utilities** (ui/search/)
  - `SearchHelpers.js` - Advanced search patterns with MHG normalization

### Data Flow
1. **Authority index** loaded on startup via `CorpusLoader`:
   - Check IndexedDB cache first (30-day TTL)
   - If expired or missing, fetch `data/authority-index.json.gz` (2.90 MB)
   - Decompress with Pako, parse JSON
   - Populate authorityData: persons, works, lemmata, concepts, genres, names, variants
   - Variants index: 176,056 mappings extracted from TEI corpus
   - Store in IndexedDB with expiration timestamp
2. **TEI files** loaded from user upload or cache via `TEIStorageManager`:
   - User uploads TEI files through drag-and-drop interface
   - Files >5MB automatically cached in IndexedDB for session persistence
   - Parse XML and extract word tokens, annotations, cross-references
   - Link `@lemma` and `@ana` attributes to authority data
3. **UI components** provide interactive exploration:
   - Single/multi-lemma search across TEI corpus
   - Co-occurrence analysis (proximity-based)
   - Authority file browsers (filterable, sortable)
   - Modular UI with specialized explorers for each data type
4. **Storage architecture** (IndexedDB):
   - `teiFiles` store: No expiration (user data)
   - `indices` store (CorpusLoader): 30-day expiration (reference data)
   - Automatic cleanup of expired data on init

### Testing Architecture
- **Playwright** end-to-end tests in `testing/` directory
- **Test configuration** (`playwright.config.js`):
  - Automated web server startup: `npx http-server .. -p 8080`
  - Headless Chrome with `--disable-web-security` for local XML file access
  - Test timeout: 60 seconds per test
  - HTML and JSON test reports generated in `testing/test-results/`
- **Test Results** (as of Oct 2, 2025):
  - 40 tests passing ✅
  - 25 tests skipped (main site tests)
  - Test suite completes in 2.7 minutes
  - Coverage: playground functionality, corpus loading, normalization, cross-references
- **Test Suites**:
  - `playground-*.spec.js` - Playground functionality and authority index loading
  - `corpus*.spec.js` - Corpus loading and management
  - `normalization-parity.spec.js` - MHG text normalization
  - `cross-reference-test.spec.js` - Authority data linking
  - `search-*.spec.js` - Search functionality with normalized text
  - `main-site.spec.js` (skipped) - Main site tests
  - `modal-*.spec.js` (skipped) - Modal tests for main site
  - `tei-caching.spec.js` (skipped) - DOM caching tests
  - `visual-mobile-test.spec.js` (skipped) - Responsive design tests

## Key Features

### Multi-Lemma Search
The playground implements advanced multi-lemma search capabilities:
- **Document-level search**: List texts containing all lemmas anywhere (v4.0.0)
- **Co-occurrence analysis**: Find lemmas within specified word distance (proximity search, v4.0.0)
- **Smart lemma resolution**: Supports both lemma IDs (`879`) and Middle High German terms (`brôt`)
- **Color-coded highlighting**: Different colors for different lemmas in proximity results
- See [MULTI-LEMMA-SEARCH-IMPLEMENTATION.md](MULTI-LEMMA-SEARCH-IMPLEMENTATION.md) for detailed documentation

**Important:** v4.0.0 removed paragraph-based multi-lemma search due to position misalignment issues between Python indexing and JavaScript extraction. The corpus index now uses document-level word indexing for accurate proximity search.

### Advanced Search Examples
```javascript
// List texts containing both "brôt" (bread) and "wîn" (wine)
teiManager.searchMultipleLemmas(['879', '7532'], 'document')

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

## Git Workflow

### Branch Strategy
- **`main`**: Production-ready code, stable releases
- **`pre-main-site`**: Preserved branch with old XML parsing architecture (for reference)
- **Feature branches**: Use descriptive names (e.g., `refactor/js-architecture`, `feature/search-improvements`)

### Common Git Tasks

#### CRITICAL: Testing Before Commits
- **NEVER commit or push without user confirmation after testing**
- **ALWAYS wait for user to test changes locally before committing**
- Make changes, let user test, then ask if they want to commit

#### Starting New Work
```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit (ONLY AFTER USER TESTS AND CONFIRMS)
git add .
git commit -m "Description of changes"

# Push branch (ONLY AFTER USER APPROVAL)
git push -u origin feature/your-feature-name
```

#### Committing Changes
- **CRITICAL**: Wait for user testing and approval before committing
- Use descriptive commit messages
- Include "🤖 Generated with [Claude Code](https://claude.com/claude-code)" footer
- Add "Co-Authored-By: Claude <noreply@anthropic.com>" for AI-assisted commits
- Reference related issues/PRs when applicable

#### After Refactoring/Major Changes
1. Update `CLAUDE.md` with new architecture details
2. Update `README.md` if user-facing changes
3. Update `docs/` if needed
4. Rebuild pre-built indexes if XML sources changed:
   ```bash
   python scripts/build-authority-index.py
   python scripts/build-corpus-index.py
   ```
5. **TEST LOCALLY** - let user verify changes work
6. **WAIT FOR USER APPROVAL** before committing
7. Run tests: `npm test` (if applicable)
8. Update documentation in commit message

### Important Notes
- **NEVER commit or push without user testing and approval first**
- **Never force push to `main`** - merge conflicts should be resolved properly
- **Rebuild indexes** after modifying XML files in `authority-files/` or `tei/`
- **Run tests** before pushing to ensure nothing breaks
- **Update docs** when file structure or architecture changes

## Important Constraints

- **Frontend-only architecture**: All processing happens in the browser (no backend)
- **Desktop-focused**: Minimum 1200px screen width, not mobile-responsive
- **Large file handling**: Authority files total 34.8 MB, with `lexicon.xml` at 32.59 MB
- **IndexedDB required**: Large files cannot be handled via sessionStorage alone
- **TEI namespace**: Always use `http://www.tei-c.org/ns/1.0` when working with XML
- **UTF-8 encoding**: All TEI files use UTF-8 encoding

## Comprehensive Documentation

This CLAUDE.md provides quick-reference guidance. For detailed knowledge documentation, see the `docs/` directory:

### Documentation Structure

The project follows a hub-and-spoke knowledge base architecture with 7 specialized documents:

| Document | Purpose | Target Audience |
|----------|---------|-----------------|
| **[docs/INDEX.MD](docs/INDEX.MD)** | Project overview and navigation hub | Anyone new to the project |
| **[docs/DATA-MODEL.MD](docs/DATA-MODEL.MD)** | Data sources, schemas, transformation pipeline | Data engineers, backend developers |
| **[docs/ARCHITECTURE.MD](docs/ARCHITECTURE.MD)** | Technical components, data flow, storage patterns | Frontend developers, architects |
| **[docs/FEATURES.MD](docs/FEATURES.MD)** | User-facing functionality descriptions | Product managers, UX designers |
| **[docs/DEVELOPMENT.MD](docs/DEVELOPMENT.MD)** | Build commands, git workflow, deployment | New contributors, DevOps |
| **[docs/RESEARCH.MD](docs/RESEARCH.MD)** | Academic context, TEI/MHG standards | Researchers, medievalists |
| **[docs/DECISIONS.MD](docs/DECISIONS.MD)** | Architecture Decision Records (ADRs) | Architects, technical leads |

### When to Use Each Document

**Starting a new feature?** Read [ARCHITECTURE.MD](docs/ARCHITECTURE.MD) and [DATA-MODEL.MD](docs/DATA-MODEL.MD)

**Fixing a bug?** Check [ARCHITECTURE.MD](docs/ARCHITECTURE.MD) for component details

**Adding documentation?** Follow guidelines in "Knowledge Documentation Guidelines" section above

**Understanding design decisions?** Read [DECISIONS.MD](docs/DECISIONS.MD) for ADRs

**Contributing code?** Read [DEVELOPMENT.MD](docs/DEVELOPMENT.MD) for workflow

**Understanding user features?** Read [FEATURES.MD](docs/FEATURES.MD)

**Academic questions?** Read [RESEARCH.MD](docs/RESEARCH.MD) for context and standards

### Documentation Maintenance

**Update docs/ when:**
- Adding/removing features
- Making architectural changes
- Refactoring major components
- Adding new data structures
- Making significant design decisions (add ADR to DECISIONS.MD)

**DON'T update docs/ for:**
- Bug fixes (unless they reveal architectural issues)
- Minor UI tweaks
- Dependency updates
- Code cleanup without behavior changes

**Remember:** CLAUDE.md provides quick reference for Claude Code, `docs/` provides comprehensive knowledge for humans.