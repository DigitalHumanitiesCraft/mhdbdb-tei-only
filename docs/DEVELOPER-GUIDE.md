# MHDBDB Developer Guide

**Last Updated**: 2025-10-01
**Version**: 1.0
**Target Audience**: Developers, AI Agents, Maintainers

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Architecture](#architecture)
4. [Development Setup](#development-setup)
5. [Codebase Structure](#codebase-structure)
6. [Key Components](#key-components)
7. [Data Flow](#data-flow)
8. [Performance Optimizations](#performance-optimizations)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Common Tasks](#common-tasks)
12. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
Node.js 16+
npm 8+
Python 3.9+ (for index building)

# Optional
Git
Chrome/Chromium (for tests)
```

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git
cd mhdbdb-tei-only

# 2. Install dependencies
npm install

# 3. Start development server
npm run serve
# → http://localhost:8080

# 4. Run tests
npm test
```

### Project Status

✅ **Production Ready** (90% complete - Phase 4)

- 666 TEI files indexed
- 43,750 lemmata with 176,056 orthographic variants
- 12/12 tests passing
- Performance optimized (97% faster caching)

---

## 📊 Project Overview

### What is MHDBDB?

**Mittelhochdeutsche Begriffsdatenbank** - A digital humanities project providing:

- 666 TEI-encoded Middle High German texts
- Semantic annotations linked to controlled vocabularies
- Advanced search with Middle High German normalization
- Pre-built indices for fast corpus exploration

### Key Features

1. **Two-Site Architecture**
   - **Main Site** (`/`) - Simple corpus browser for general users
   - **Playground** (`/playground/`) - Advanced research tool

2. **Performance**
   - 95% faster playground load (3.8s vs 3-4 min)
   - 97% faster TEI text repeat loads (2-3s vs 60s)
   - Pre-built compressed indices (22 MB)

3. **Search Capabilities**
   - 11 search entry points (6 authority + 5 TEI)
   - 3-stage lemma resolution (exact/variants/fuzzy)
   - MHG character normalization (â→a, ô→o, etc.)
   - Multi-lemma search (paragraph/document/proximity modes)

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                         │
├──────────────────────┬──────────────────────────────────┤
│   Main Site (/)      │   Playground (/playground/)      │
│                      │                                   │
│  - Simple UI         │  - Advanced UI (6 modules)       │
│  - Pre-built indices │  - File upload                   │
│  - Fast search       │  - 11 searches                   │
│  - Text rendering    │  - XPath queries                 │
└──────────────────────┴──────────────────────────────────┘
           │                        │
           ├────────────────────────┤
           │   IndexedDB Storage    │
           │  - Authority cache     │
           │  - Corpus cache        │
           │  - TEI DOM cache       │
           └────────────────────────┘
                      │
           ┌──────────────────────┐
           │  Static Files (HTTP) │
           │  - data/*.json.gz    │
           │  - tei/*.tei.xml     │
           │  - authority-files/  │
           └──────────────────────┘
```

### Technology Stack

**Frontend:**
- Vanilla JavaScript (ES6+ modules)
- Tailwind CSS (CDN)
- No framework dependencies

**Storage:**
- IndexedDB (Dexie.js wrapper)
- sessionStorage (legacy, being phased out)

**Data Processing:**
- Pako.js (gzip decompression, Safari compatible)
- DOMParser (XML parsing)
- XPath (queries)

**Testing:**
- Playwright (E2E testing)
- 18 test files, 50+ test cases

**Build Tools:**
- Python scripts for index generation
- npm scripts for development

---

## 💻 Development Setup

### Environment Setup

```bash
# Create .env file (optional, no secrets needed)
touch .env

# Install global tools (optional)
npm install -g http-server
npm install -g playwright
```

### Development Commands

```bash
# Development
npm run serve          # Start local server (port 8080)
npm test              # Run all tests
npm run test:ui       # Run tests with UI
npm run test:debug    # Debug tests

# Index Building (Python)
npm run build:authority  # Build authority index (~2s)
npm run build:corpus     # Build corpus index (~10 min)
npm run build            # Build all indices
npm run validate:indices # Validate generated indices

# Testing
npm test                 # All tests
npm run test:headed      # With browser visible
npm run report          # View test report
```

### IDE Setup

**VS Code** (Recommended)
```json
{
  "files.exclude": {
    "node_modules": true,
    "testing/test-results.json": true
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

---

## 📁 Codebase Structure

### Directory Layout

```
mhdbdb-tei-only/
├── index.html                    # Main site entry
├── js/                          # Main site JavaScript
│   ├── main-site.js            # App controller
│   ├── corpus-loader.js        # Index loading
│   ├── search-engine.js        # Search logic
│   ├── text-renderer.js        # TEI rendering
│   └── tei-cache-manager.js    # DOM caching
│
├── playground/
│   ├── index.html              # Playground entry
│   └── js/
│       ├── main.js             # MHDBDBPlayground class
│       ├── authority-files.js  # Authority manager
│       ├── tei-files.js        # TEI manager
│       ├── ui/                 # UI components (6 modules)
│       └── utils/              # Utilities
│
├── data/                       # Pre-built indices
│   ├── authority-index.json.gz  (1.27 MB)
│   └── corpus-index.json.gz     (20.84 MB)
│
├── tei/                        # 666 TEI XML files
├── authority-files/            # 7 XML vocabularies
├── testing/                    # Test suite
├── scripts/                    # Python build scripts
└── docs/                       # Documentation (this file)
```

### File Organization Principles

**Main Site** (`js/`)
- **Naming**: kebab-case.js
- **Purpose**: Simple, fast corpus exploration
- **Dependencies**: Minimal, CDN-based

**Playground** (`playground/js/`)
- **Naming**:
  - Classes: PascalCase.js
  - Utilities: kebab-case.js
- **Purpose**: Advanced research tool
- **Dependencies**: Modular, well-structured

See [JS-ARCHITECTURE.md](../JS-ARCHITECTURE.md) for detailed file documentation.

---

## 🔑 Key Components

### Main Site Components

#### 1. MainSiteApp (`js/main-site.js`)
```javascript
class MainSiteApp {
    // Main application controller
    // Coordinates: corpus loading, search, text rendering

    async init() {
        // Load authority + corpus indices
        // Initialize search engine
        // Setup event listeners
    }
}
```

#### 2. CorpusLoader (`js/corpus-loader.js`)
```javascript
class CorpusLoader {
    // Loads pre-built gzipped indices
    // Uses: Dexie.js + Pako for decompression
    // Cache: 30-day TTL in IndexedDB

    async loadAuthorityIndex() {
        // Returns: { lemmata, persons, works, concepts, genres, names }
    }
}
```

#### 3. SearchEngine (`js/search-engine.js`)
```javascript
class SearchEngine {
    // 3-stage lemma resolution:
    // Stage 1: Exact match in lexicon
    // Stage 2: Variant lookup (192K mappings)
    // Stage 3: Fuzzy match (includes)

    searchLemma(term) {
        // Returns array of results with MHG normalization
    }
}
```

#### 4. TextRenderer (`js/text-renderer.js`)
```javascript
class TextRenderer {
    // TEI text rendering with caching

    async loadTEIFile(filename) {
        // 1. Check cache (97% faster on hit)
        // 2. Fetch from network if miss
        // 3. Parse XML DOM
        // 4. Cache for future use (30-day TTL)
    }
}
```

#### 5. TEICacheManager (`js/tei-cache-manager.js`)
```javascript
class TEICacheManager {
    // IndexedDB DOM caching
    // Stores serialized XML Documents
    // 30-day expiration

    async get(filename) {
        // Returns: Document | null
    }

    async set(filename, doc) {
        // Stores: XMLSerializer.serializeToString(doc)
    }
}
```

### Playground Components

#### 6. MHDBDBPlayground (`playground/js/main.js`)
```javascript
class MHDBDBPlayground {
    constructor() {
        this.authorityManager = new AuthorityFilesManager();
        this.teiManager = new TEIFilesManager();
        this.ui = {
            authorityExplorers: new AuthorityExplorers(),
            teiExplorer: new TEIExplorer(),
            xpathInterface: new XPathInterface(),
            multiLemmaSearch: new MultiLemmaSearchUI()
        };
    }
}
```

#### 7. AuthorityExplorers (`playground/js/ui/AuthorityExplorers.js`)
```javascript
export class AuthorityExplorers {
    // 6 search functions:
    // - showAuthors()
    // - showWorks()
    // - showLemmata()
    // - showConcepts()
    // - showGenres()
    // - showNames()

    // All with MHG normalization
}
```

#### 8. TEIExplorer (`playground/js/ui/TEIExplorer.js`)
```javascript
export class TEIExplorer {
    // 5 TEI analysis functions:
    // - showWords()
    // - showLines()
    // - findLemmaInText()
    // - showAnnotations()
    // - Multi-lemma search (via MultiLemmaSearchUI)
}
```

---

## 🔄 Data Flow

### Main Site: Search Flow

```
User enters "brot" in search
         ↓
SearchEngine.searchLemma("brot")
         ↓
TextNormalizer.normalizeMHG("brot") → "brot"
         ↓
3-Stage Resolution:
  1. Exact: Check lemmata[] for "brot"
  2. Variants: Check variants{} for "brot" → finds "brôt" (lemma_879)
  3. Fuzzy: lemma.includes("brot")
         ↓
Return results with lemma IDs
         ↓
Display results in UI
         ↓
User clicks result → TextRenderer.loadTEIFile()
         ↓
TEICacheManager.get(filename)
  - Cache hit? → Return cached DOM (0.1s) ⚡
  - Cache miss? → Fetch XML (60s) → Parse → Cache → Return
         ↓
Render text with highlighted lemma
```

### Playground: Corpus Loading Flow

```
User clicks "Load Corpus" button
         ↓
TEIFilesManager.loadCorpusIntoPlayground()
         ↓
CorpusLoader.loadCorpusIndex()
  ↓ Check IndexedDB cache
  ├─ Hit? → Load from cache (0.5s)
  └─ Miss? → Fetch + decompress (1.4s) → Cache
         ↓
Parse corpus index (666 texts, 7.4M words)
         ↓
Create lazy-loading proxies for each text
         ↓
Populate UI with text metadata
         ↓
Enable all search buttons
         ↓
User can now search/analyze corpus
```

### Multi-Lemma Search Flow

```
User enters "brott + win" in multi-lemma search
         ↓
Parse input → ["brott", "win"]
         ↓
For each term: AuthorityFilesManager.searchLemmaByOrthography()
  ↓
  Stage 1: Exact match in lexicon → not found
  Stage 2: Variants index search → "brott" → lemma_879, "win" → lemma_7532
  Stage 3: Partial match fallback → (not needed)
         ↓
Resolve to lemma IDs: [879, 7532]
         ↓
TEIFilesManager.searchMultipleLemmas([879, 7532], "paragraph")
         ↓
For each text:
  - Load XML via lazy getter
  - XPath: //w[@lemmaRef="lexicon.xml#lemma_879"]
  - XPath: //w[@lemmaRef="lexicon.xml#lemma_7532"]
  - Find paragraphs containing both
         ↓
Highlight results with color-coding:
  - lemma_879 → yellow
  - lemma_7532 → blue
         ↓
Display results in modal
```

---

## ⚡ Performance Optimizations

### 1. Pre-Built Indices

**Problem**: Loading 34.8 MB of XML authority files takes 3-4 minutes

**Solution**: Pre-build compressed JSON indices

```python
# scripts/build-authority-index.py
# Extracts: persons, works, lemmata, concepts, genres, names
# Output: authority-index.json.gz (1.27 MB, 94% smaller)

# scripts/build-corpus-index.py
# Extracts: metadata, lemma positions from 666 TEI files
# Output: corpus-index.json.gz (20.84 MB)
```

**Result**: 95% faster load (3.8s vs 3-4 min)

### 2. TEI DOM Caching

**Problem**: Parsing large TEI XML files takes 30-60 seconds

**Solution**: Cache parsed DOMs in IndexedDB

```javascript
// js/tei-cache-manager.js
class TEICacheManager {
    async get(filename) {
        // Returns cached Document if available
    }

    async set(filename, doc) {
        const serializer = new XMLSerializer();
        const xmlString = serializer.serializeToString(doc);
        // Store in IndexedDB with 30-day TTL
    }
}
```

**Result**: 97% faster repeat loads (2-3s vs 60s)

### 3. Lazy Loading

**Problem**: Loading all 666 TEI files upfront uses 450 MB RAM

**Solution**: Load files on-demand via getter pattern

```javascript
// playground/js/tei-files.js
class TEIFile {
    get xmlDoc() {
        if (!this._xmlDoc) {
            this._xmlDoc = this.loadXML();
        }
        return this._xmlDoc;
    }
}
```

**Result**: 82% memory reduction (80 MB vs 450 MB)

### 4. Orthographic Variants Index

**Problem**: Searching for variant spellings requires full-text search

**Solution**: Pre-extracted variants → canonical lemma mappings

```xml
<!-- authority-files/variants.xml -->
<entry form="brott" lemmaRef="lexicon.xml#lemma_879"/>
<entry form="brot" lemmaRef="lexicon.xml#lemma_879"/>
<entry form="brôt" lemmaRef="lexicon.xml#lemma_879"/>
```

**Result**: Instant variant resolution (192,674 mappings)

---

## 🧪 Testing

### Test Structure

```
testing/
├── playwright.config.js        # Test configuration
├── tests/
│   ├── main-site.spec.js      # Main site E2E
│   ├── search-with-corpus.spec.js  # 12 search tests ✅
│   ├── cross-reference-test.spec.js # 4 cross-ref tests
│   ├── tei-caching.spec.js    # Performance tests
│   ├── normalization-parity.spec.js # 18 MHG tests
│   └── playground-*.spec.js   # Playground tests
└── test-utils.js              # Test helpers
```

### Running Tests

```bash
# All tests
npm test

# Specific suite
npx playwright test tests/search-with-corpus.spec.js

# With UI
npm run test:ui

# Debug mode
npm run test:debug

# Headed (visible browser)
npm run test:headed

# Report
npm run report
```

### Test Results (Latest)

```
✅ 12/12 search tests passing
✅ All 11 searches verified
✅ Cross-referencing works
✅ Performance: 1.4s corpus load
✅ Cache: 97% faster repeat loads
✅ MHG normalization: 18/18 tests passing
```

### Writing Tests

```javascript
// Example: Testing a search function
import { test, expect } from '@playwright/test';

test('Lemmata search with normalization', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');

    // Wait for playground ready
    await page.waitForSelector('#statusText:has-text("Authority Files geladen")');

    // Click search button
    await page.click('button:has-text("Lemmata anzeigen")');

    // Wait for search input
    await page.waitForSelector('#lemmaSearch');

    // Search for normalized term
    await page.fill('#lemmaSearch', 'brot');  // matches "brôt"
    await page.waitForTimeout(500);

    // Verify results
    const results = await page.locator('#resultsContainer').textContent();
    expect(results.toLowerCase()).toMatch(/brôt|brot/);
});
```

### Test Coverage

- **Functionality**: All 11 searches tested
- **Performance**: Load times, caching verified
- **Cross-browser**: Chrome tested, others pending
- **Normalization**: 18 MHG character mappings tested
- **Integration**: End-to-end user workflows

---

## 🚀 Deployment

See [Deployment Guide](./DEPLOYMENT-GUIDE.md) for detailed instructions.

### Quick Deployment Checklist

```bash
# 1. Build indices (if needed)
npm run build

# 2. Run tests
npm test

# 3. Commit changes
git add .
git commit -m "Release vX.X.X"
git push

# 4. Deploy to production
# (GitHub Pages, or any static file server)
```

### Production Requirements

- **Web Server**: Any HTTP server (Apache, Nginx, http-server)
- **HTTPS**: Required for IndexedDB
- **CORS**: Not needed (same-origin)
- **Node.js**: Not needed (static files only)

### Environment Variables

None required! All configuration is in code.

---

## 🛠️ Common Tasks

### Adding a New Search Function

1. **Playground UI** (`playground/js/ui/AuthorityExplorers.js`):
```javascript
showNewSearch() {
    const searchHTML = createSearchInterface({
        title: "New Search",
        placeholder: "Enter term...",
        searchInputId: "newSearch",
        resultsId: "newResults",
        totalCount: this.authorityData.someArray.length
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("newSearch", (term) => this.searchNewThing(term));
}
```

2. **Add Button** (`playground/index.html`):
```html
<button id="showNewBtn">New Search</button>
```

3. **Wire Up** (`playground/js/main.js`):
```javascript
{ id: 'showNewBtn', handler: () => this.ui.authorityExplorers.showNewSearch() }
```

4. **Test** (`testing/tests/search-with-corpus.spec.js`):
```javascript
test('New search works', async ({ page }) => {
    await page.click('button:has-text("New Search")');
    await page.waitForSelector('#newSearch');
    // ... test logic
});
```

### Modifying MHG Normalization Rules

Edit `playground/js/utils/text-normalizer.js`:

```javascript
export class TextNormalizer {
    static normalizeMHG(text) {
        return text
            .replace(/[âāǎ]/g, 'a')  // Add new mapping here
            .replace(/[êēě]/g, 'e')
            // ...
    }
}
```

### Adding a New Authority File

1. **Place XML** in `authority-files/new-file.xml`

2. **Update Index Builder** (`scripts/build-authority-index.py`):
```python
def extract_new_things(tree, nsmap):
    """Extract new authority data"""
    things = []
    for elem in tree.xpath('//new:thing', namespaces=nsmap):
        things.append({
            'id': elem.get('xml:id'),
            'name': elem.text
        })
    return things
```

3. **Rebuild Index**:
```bash
npm run build:authority
```

4. **Update Playground** to load new data

### Optimizing Performance

**Identify Bottleneck:**
```javascript
console.time('operation');
// ... code
console.timeEnd('operation');
```

**Common Optimizations:**
- Add to cache (if repeatable)
- Move to pre-built index (if static)
- Use lazy loading (if optional)
- Add to Web Worker (if CPU-intensive)

---

## 🐛 Troubleshooting

### "Indices not loading"

```bash
# Check files exist
ls -lh data/*.json.gz

# Rebuild if missing
npm run build

# Check browser console for errors
# Open DevTools → Console
```

### "Search returns no results"

1. Check normalization:
```javascript
// In browser console
window.TextNormalizer.normalizeMHG('brôt')
// Should return: "brot"
```

2. Check data loaded:
```javascript
// In browser console
window.playground.authorityData.lemmata.length
// Should return: 43750
```

3. Check for typos in search term

### "TEI modal doesn't open"

1. Check file exists:
```bash
ls tei/YOUR_FILE.tei.xml
```

2. Check console for errors
3. Verify cache not corrupted:
```javascript
// Clear cache
await window.playground.textRenderer.cache.clear()
```

### "Tests failing"

```bash
# Clear test artifacts
rm -rf testing/test-results.json/

# Update Playwright
npm install -D @playwright/test@latest

# Run with debug
npm run test:debug
```

### "IndexedDB quota exceeded"

```javascript
// Check usage
const estimate = await navigator.storage.estimate();
console.log(`Using ${estimate.usage} of ${estimate.quota} bytes`);

// Clear old caches
await caches.delete('old-cache-name');
```

---

## 📚 Additional Resources

- **[API Reference](./API-REFERENCE.md)** - Detailed API docs
- **[Testing Guide](./TESTING-GUIDE.md)** - Testing best practices
- **[Deployment Guide](./DEPLOYMENT-GUIDE.md)** - Production deployment
- **[JS-ARCHITECTURE.md](../JS-ARCHITECTURE.md)** - File organization
- **[CLAUDE.md](../CLAUDE.md)** - AI agent instructions

---

## 🤝 Contributing

1. Read this guide thoroughly
2. Check [REWORK-STATUS.md](../REWORK-STATUS.md) for current progress
3. Create feature branch
4. Write tests
5. Update documentation
6. Submit pull request

---

## 📧 Support

- **Technical Issues**: GitHub Issues
- **Development Questions**: See FAQ or create issue
- **Research Questions**: mhdbdb@plus.ac.at

---

**Last Updated**: 2025-10-01
**Maintained by**: MHDBDB Development Team
**License**: CC BY-NC-SA 3.0 AT

**Navigation**: [↑ Docs Index](./README.md) | [→ API Reference](./API-REFERENCE.md) | [→ Testing Guide](./TESTING-GUIDE.md)
