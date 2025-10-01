# JavaScript Architecture & File Organization

**Last Updated**: 2025-10-01
**Status**: Clean, optimized, production-ready ✅

---

## Overview

The MHDBDB project uses a **clean, modular JavaScript architecture** with clear separation of concerns:

- **Main Site** (`/js/`) - Public-facing corpus browser
- **Playground** (`/playground/js/`) - Advanced research tool
- **Testing** (`/testing/`) - Automated test suite

---

## File Structure

### Main Site (`/js/`)

**Purpose**: Simple, fast corpus exploration for general users

```
js/
├── main.js                    # Landing page interactions (smooth scroll, nav)
├── main-site.js              # Main application controller (ES module)
├── corpus-loader.js          # Loads pre-built gzipped indices
├── search-engine.js          # 3-stage lemma search (exact/variants/fuzzy)
├── text-renderer.js          # TEI text rendering with highlighting
└── tei-cache-manager.js      # IndexedDB DOM caching (97% faster)
```

**Naming Convention**: `kebab-case.js` for modules

**Key Classes**:
- `MainSiteApp` - Application controller
- `CorpusLoader` - Index loading with Dexie.js
- `SearchEngine` - Lemma search with MHG normalization
- `TextRenderer` - TEI rendering with caching
- `TEICacheManager` - 30-day DOM cache

---

### Playground (`/playground/js/`)

**Purpose**: Advanced TEI analysis for researchers

```
playground/js/
├── main.js                    # MHDBDBPlayground class (main controller)
├── authority-files.js        # AuthorityFilesManager (persons, works, lexicon)
├── tei-files.js              # TEIFilesManager (corpus processing)
├── indexed-db-manager.js     # IndexedDBManager (core storage)
├── storage-manager.js        # TEIStorageManager (file caching)
│
├── ui/                       # Modular UI components (replaced monolithic ui-helpers.js)
│   ├── UICore.js            # Core UI utilities (progress, file display)
│   ├── AuthorityExplorers.js # Authority file search interfaces (6 searches)
│   ├── TEIExplorer.js       # TEI text analysis (lemma search, annotations)
│   ├── XPathInterface.js    # XPath query interface
│   ├── MultiLemmaSearch.js  # Multi-lemma modal (3 modes: paragraph/document/proximity)
│   └── SearchHelpers.js     # Search utilities & patterns
│
└── utils/
    └── text-normalizer.js    # MHG character normalization (â→a, ô→o, etc.)
```

**Naming Convention**:
- `PascalCase.js` for UI components/classes
- `kebab-case.js` for utilities

**Key Architecture**:
- **Modular UI**: 6 specialized components vs monolithic helper
- **Lazy Loading**: TEI files loaded on-demand via getter pattern
- **3-Stage Search**: Exact → Variants (192K mappings) → Fuzzy
- **MHG Normalization**: Centralized in `TextNormalizer` utility

---

## Naming Conventions Summary

### ✅ Current Standards

| Type | Convention | Example |
|------|------------|---------|
| **Modules** | kebab-case | `corpus-loader.js` |
| **Classes** | PascalCase | `CorpusLoader` |
| **UI Components** | PascalCase file | `AuthorityExplorers.js` |
| **Functions** | camelCase | `loadCorpusIndex()` |
| **Constants** | UPPER_SNAKE_CASE | `INDEX_VERSION` |
| **Private methods** | _camelCase | `_parseXML()` |

### File Naming Logic

```javascript
// Data managers & controllers → kebab-case
corpus-loader.js        // CorpusLoader class
tei-files.js           // TEIFilesManager class
indexed-db-manager.js  // IndexedDBManager class

// UI components → PascalCase (matches class name)
AuthorityExplorers.js  // AuthorityExplorers class
TEIExplorer.js        // TEIExplorer class
UICore.js             // UI utility functions

// Utilities → kebab-case
text-normalizer.js    // TextNormalizer utility
```

---

## Import/Export Patterns

### ES Modules (Main Site)
```javascript
// main-site.js
import { CorpusLoader } from './corpus-loader.js';
import { SearchEngine } from './search-engine.js';
import { TextRenderer } from './text-renderer.js';

class MainSiteApp {
    // ...
}

export { MainSiteApp };
```

### ES Modules (Playground)
```javascript
// main.js (Playground)
import { AuthorityFilesManager } from './authority-files.js';
import { TEIFilesManager } from './tei-files.js';
import { AuthorityExplorers } from './ui/AuthorityExplorers.js';

class MHDBDBPlayground {
    // ...
}

// Global exposure for onclick handlers
window.playground = new MHDBDBPlayground();
```

---

## Dependency Graph

### Main Site
```
index.html
    └── main-site.js (MainSiteApp)
        ├── corpus-loader.js (CorpusLoader)
        │   └── [Dexie.js, Pako.js from CDN]
        ├── search-engine.js (SearchEngine)
        │   └── ../playground/js/utils/text-normalizer.js
        └── text-renderer.js (TextRenderer)
            └── tei-cache-manager.js (TEICacheManager)
```

### Playground
```
playground/index.html
    └── main.js (MHDBDBPlayground)
        ├── authority-files.js (AuthorityFilesManager)
        ├── tei-files.js (TEIFilesManager)
        │   └── ../js/corpus-loader.js (for pre-built corpus)
        ├── indexed-db-manager.js (IndexedDBManager)
        ├── storage-manager.js (TEIStorageManager)
        └── ui/
            ├── UICore.js
            ├── AuthorityExplorers.js
            ├── TEIExplorer.js
            ├── XPathInterface.js
            ├── MultiLemmaSearch.js
            └── SearchHelpers.js
```

---

## Code Quality Metrics

### ✅ Clean Code Standards

- **No obsolete files** - All backup files removed
- **No TODO comments** - All planned work completed
- **Consistent naming** - Follows established conventions
- **Modular design** - Single responsibility principle
- **Clear separation** - UI/Data/Utils properly organized
- **ES6+ features** - Modern JavaScript (classes, modules, async/await)
- **Type safety** - JSDoc comments for complex functions
- **Error handling** - Try/catch with graceful degradation

### Lines of Code (Approximate)

```
Main Site:        ~2,500 LOC (7 files)
Playground:       ~6,000 LOC (13 files)
Testing:          ~2,000 LOC (18 test files)
Total:            ~10,500 LOC
```

### Complexity Metrics

- **Average file size**: ~400 LOC
- **Max file size**: ~1,500 LOC (AuthorityExplorers.js)
- **Cyclomatic complexity**: Low-Medium (well-factored)
- **Test coverage**: 12 core searches + 4 cross-reference tests

---

## Performance Optimizations

### Caching Strategy

```javascript
// TEI DOM Caching (js/tei-cache-manager.js)
class TEICacheManager {
    dbName: 'MHDBDB_TEI_Cache'
    expiration: 30 days
    storage: IndexedDB

    // Results: 97% faster repeat loads (60s → 2-3s)
}

// Authority Index Caching (js/corpus-loader.js)
class CorpusLoader {
    indexVersion: '1.0.0'
    expiration: 30 days
    storage: Dexie.js + IndexedDB

    // Results: 95% faster playground load (3.8s vs 3-4 min)
}
```

### Lazy Loading

```javascript
// playground/js/tei-files.js
class TEIFilesManager {
    // Lazy-load TEI XML via getter pattern
    get xmlDoc() {
        if (!this._xmlDoc) {
            this._xmlDoc = this.loadXML();
        }
        return this._xmlDoc;
    }
}
```

### Pre-Built Indices

```
data/authority-index.json.gz    1.27 MB (43,750 lemmata)
data/corpus-index.json.gz       20.84 MB (666 texts, 7.4M words)

Build time: ~10 minutes
Load time: ~1.4 seconds ⚡
```

---

## Testing Strategy

### Test Coverage

```
testing/tests/
├── main-site.spec.js              # Main site E2E tests
├── search-with-corpus.spec.js     # 12 search tests (all passing)
├── cross-reference-test.spec.js   # 4 cross-reference tests
├── tei-caching.spec.js           # Performance tests
├── normalization-parity.spec.js  # 18 MHG normalization tests
├── playground-*.spec.js          # Playground functionality tests
└── corpus*.spec.js               # Corpus loading tests
```

**Total**: 18 test files, 50+ test cases

### Test Results (Latest)

```
✅ 12/12 search tests passing
✅ All 11 searches verified working
✅ Cross-referencing verified
✅ Performance: 1.4s corpus load
✅ All 666 texts accessible
```

---

## Migration History

### Phase 3: UI Modularization (September 2025)

**Before**: Monolithic `ui-helpers.js` (~2000 LOC)

**After**: 6 specialized modules
- `UICore.js` - Core utilities
- `AuthorityExplorers.js` - Authority searches
- `TEIExplorer.js` - TEI analysis
- `XPathInterface.js` - XPath queries
- `MultiLemmaSearch.js` - Advanced search
- `SearchHelpers.js` - Search patterns

**Benefits**:
- Better code organization
- Easier maintenance
- Clearer responsibilities
- Improved testability

---

## Future Considerations

### Potential Improvements

1. **TypeScript Migration** - Add type safety
2. **Bundle Optimization** - Webpack/Vite for production
3. **Service Worker** - Offline functionality
4. **Web Workers** - Background TEI parsing
5. **Progressive Enhancement** - Better mobile support

### Architectural Stability

Current architecture is **production-ready** and **stable**:
- ✅ No major refactoring needed
- ✅ Clear, maintainable code
- ✅ Well-tested functionality
- ✅ Excellent performance

---

## Quick Reference

### Adding a New Feature

1. **Main Site**: Add to `js/main-site.js` or create new module
2. **Playground**: Add to appropriate UI module or create new one
3. **Utility**: Add to `playground/js/utils/`
4. **Test**: Add to `testing/tests/`

### File Naming Checklist

- [ ] Use kebab-case for data/controller modules
- [ ] Use PascalCase for UI component files
- [ ] Match filename to main export class name (when applicable)
- [ ] Place in correct directory (js/ vs playground/js/ vs ui/)
- [ ] Add to this documentation

### Import Checklist

- [ ] Use relative paths (`./`, `../`)
- [ ] Include `.js` extension
- [ ] Import only what you need
- [ ] Avoid circular dependencies
- [ ] Document external dependencies (CDN)

---

**Maintained by**: MHDBDB Development Team
**Last Audit**: 2025-10-01
**Status**: ✅ Clean, optimized, production-ready
