
# MHDBDB TEI Repository

TEI-encoded Middle High German literature texts with semantic annotations and **dual web interfaces** from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

## Overview

Alle Inhalte basieren auf den Daten der [Mittelhochdeutschen Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at) der Universität Salzburg – einem Forschungsprojekt mit über 50 Jahren mediävistischer Text- und Begriffsforschung.

### Corpus Content
- TEI-encoded texts of Middle High German literature
- Authority files: persons, works, lexicon, concepts, genres, names, variants
- Pre-built indices for fast search
- Comprehensive test suite with Playwright integration

### Two Web Interfaces

| Feature | **Main Site** ([index.html](index.html:1)) | **Playground** ([playground/](playground/index.html:1)) |
|---------|------------------------|------------------|
| **Purpose** | Public search & reading | Advanced research & analysis |
| **Data** | Pre-built indices | Pre-built authority index + lazy-loaded TEI |
| **Search** | Single lemma with filters | Multiple search types (incl. multi-lemma) |
| **Target Users** | General public, students | Researchers, medievalists |

## 📚 Documentation

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - Primary developer guide and project overview
- **[docs/INDEX.MD](docs/INDEX.MD)** - Comprehensive knowledge base gateway with links to specialized documentation

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
npm run build              # Build all indices
npm run build:authority    # Build authority index only
npm run build:corpus       # Build corpus index only
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

| File | Content |
|------|---------|
| **persons.xml** | Authors and historical persons |
| **works.xml** | Works and manuscript metadata |
| **lexicon.xml** | Lemmata with grammatical annotations |
| **concepts.xml** | Semantic concepts (taxonomy) |
| **genres.xml** | Literary genres (taxonomy) |
| **names.xml** | Proper names with semantic relations |
| **variants.xml** | Orthographic variants mapped to lemmas |

## Architecture

### Pre-Built Indices

The repository includes pre-built compressed indices for fast loading:

| Index | Contains |
|-------|----------|
| **authority-index.json.gz** | All authority files merged |
| **corpus-index.json.gz** | Texts with lemma positions |

**Features:**
- Compressed JSON format for reduced download size
- IndexedDB caching with automatic expiration
- No XML parsing overhead in browser

### Technology Stack

- **Frontend:** Vanilla JavaScript (ES Modules), Tailwind CSS
- **Compression:** Pako (gzip compression)
- **Storage:** Dexie.js (IndexedDB wrapper)
- **Testing:** Playwright
- **Build:** Python + lxml for index generation
- **Server:** http-server (npm) or Python http.server

### Middle High German Normalization

All search functions use centralized MHG character normalization:
- Long vowels: `â→a, ê→e, î→i, ô→o, û→u`
- Umlauts: `ä→ae, ö→oe, ü→ue`
- Parity between Python (build) and JavaScript (runtime)
- Comprehensive automated test coverage

## License & Contact

**License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at
**Project:** University of Salzburg, 50+ years of medievalist research
