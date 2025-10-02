
# MHDBDB TEI Repository

TEI-encoded Middle High German literature texts with semantic annotations and **dual web interfaces** from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

## Overview

Alle Inhalte basieren auf den Daten der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at) der Universität Salzburg – einem Forschungsprojekt mit über 50 Jahren mediävistischer Text- und Begriffsforschung.

### Corpus Content
- **666 TEI-encoded texts** (Middle High German literature, 7.4M words)
- **7 authority files** (47.3 MB): persons, works, lexicon, concepts, genres, names, variants
- **Pre-built indices** (24 MB compressed): Fast search via offline-generated corpus index
- **Comprehensive test suite** (40 passing, 25 skipped) with Playwright integration

### Two Web Interfaces

| Feature | **Main Site** ([index.html](index.html:1)) | **Playground** ([playground/](playground/index.html:1)) |
|---------|------------------------|------------------|
| **Purpose** | Public search & reading | Advanced research & analysis |
| **Load Time** | 3-5 seconds | Instant (pre-built index) |
| **Data** | Pre-built indices (24 MB) | Pre-built authority index + lazy-loaded TEI |
| **Search** | Single lemma with filters | 11 search types (incl. multi-lemma) |
| **Target Users** | General public, students | Researchers, medievalists |

## 📚 Documentation

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - Complete developer guide and architecture overview (primary reference)
- **[REFACTORING-SUMMARY.md](docs/REFACTORING-SUMMARY.md)** - Recent refactoring work (Phase 7 modular UI)
- **[BUGFIX-2025-10-02.md](docs/BUGFIX-2025-10-02.md)** - Recent bug fixes and improvements
- **[REFACTORING-PLAN.md](docs/REFACTORING-PLAN.md)** - Multi-phase refactoring plan

### For Users
- Playground includes built-in help and search examples
- Authority data browsing with filtering and sorting

## Quick Start

### Start Web Server
```bash
npm run serve
# Opens http://localhost:8080
```

### Build Indices (Optional)
Pre-built indices are included. To rebuild:
```bash
npm run build              # Build all indices (~30 min)
npm run build:authority    # Build authority index only (~30 sec)
npm run build:corpus       # Build corpus index only (~30 min)
npm run validate:indices   # Validate generated indices
```

### Run Tests
```bash
npm test                   # Run all tests
npm run test:ui            # Interactive test UI
npm run test:headed        # Run with visible browser
```

### Programmatic Access
TEI files reference authority data via `xml:id`:
```xml
<author ref="#person_445">Meister Eckhart</author>
<w lemma="vriunt" ana="#concept_12345">vriunt</w>
```

### XPath Examples
```xpath
//tei:persName[@type='preferred']  # All preferred person names
//tei:w[@lemma='vriunt']           # All instances of 'vriunt'
```

## Authority Files

| File | Size | Content |
|------|------|---------|
| **persons.xml** | 0.12 MB | 210 authors and historical persons |
| **works.xml** | 1.41 MB | 583 works and manuscript metadata |
| **lexicon.xml** | 32.59 MB | 43,750 lemmata with grammatical annotations |
| **concepts.xml** | 0.21 MB | 567 semantic concepts (taxonomy) |
| **genres.xml** | 0.4 MB | 615 literary genres (taxonomy) |
| **names.xml** | 0.03 MB | 90 proper names with semantic relations |
| **variants.xml** | 12.46 MB | 192,674 orthographic variants → 39,436 lemmas |

## Architecture

### Pre-Built Indices (New!)

The repository includes pre-built compressed indices for fast loading:

| Index | Size | Contains | Cache |
|-------|------|----------|-------|
| **authority-index.json.gz** | 2.90 MB | All authority files merged | 30 days |
| **corpus-index.json.gz** | 21 MB | 666 texts with lemma positions | 30 days |

**Performance Gains:**
- **Main site:** Loads in 3-5s (was: N/A)
- **Playground:** Loads corpus in 3.8s (was: 3-4 minutes)
- **Memory:** 82% reduction (80 MB vs 450 MB)
- **Caching:** IndexedDB with automatic expiration

### Technology Stack

- **Frontend:** Vanilla JavaScript (ES Modules), Tailwind CSS
- **Compression:** Pako 2.1.0 (gzip, Safari 14+ compatible)
- **Storage:** Dexie.js 3.2.4 (IndexedDB wrapper)
- **Testing:** Playwright (40 passing, 25 skipped, 2.7 min runtime)
- **Build:** Python 3.13 + lxml for index generation
- **Server:** http-server (npm) or Python http.server

### Middle High German Normalization

All search functions use centralized MHG character normalization:
- Long vowels: `â→a, ê→e, î→i, ô→o, û→u`
- Umlauts: `ä→ae, ö→oe, ü→ue`
- 100% parity between Python (build) and JavaScript (runtime)
- 18/18 automated tests passing

## Recent Updates

**October 2, 2025:**
- ✅ Merged Phase 7 refactoring: Modular UI architecture (18 specialized modules)
- ✅ Fixed test suite timeout (40 tests passing, 2.7 min runtime)
- ✅ Rebuilt authority index (2.90 MB compressed)
- ✅ Net reduction: 5,536 lines removed from codebase

See [REFACTORING-SUMMARY.md](docs/REFACTORING-SUMMARY.md) and [BUGFIX-2025-10-02.md](docs/BUGFIX-2025-10-02.md) for details.

## License & Contact

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at
**Project:** University of Salzburg, 50+ years of medievalist research
