# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the MHDBDB TEI Repository - a collection of TEI-encoded Middle High German literature texts with semantic annotations from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

## Repository Structure

### Core Data
- **tei/**: 666 TEI-encoded Middle High German texts (.tei.xml files)
- **authority-files/**: 6 controlled vocabulary XML files (34.8 MB total)
  - `persons.xml` (0.12 MB) - Authors and historical persons
  - `works.xml` (1.41 MB) - Work and manuscript metadata
  - `lexicon.xml` (32.59 MB) - Dictionary with grammatical annotations
  - `concepts.xml` (0.21 MB) - Semantic concept taxonomy
  - `genres.xml` (0.4 MB) - Literary genre classification
  - `names.xml` (0.03 MB) - Proper names with semantic relations

### Web Interface
- **playground/**: Web-based exploration tool for TEI data analysis
  - `index.html` - Main interface
  - `test.html` - Test suite interface
  - `js/` - JavaScript modules for data processing
    - `main.js` - Application entry point (`MHDBDBPlayground` class)
    - `authority-files.js` - Authority data handling (`AuthorityFilesManager`)
    - `tei-files.js` - TEI text processing (`TEIFilesManager`)
    - `storage-manager.js` - TEI file caching (`TEIStorageManager`)
    - `indexed-db-manager.js` - Core IndexedDB operations
    - `authority-storage-manager.js` - Authority file caching with 30-day expiration
    - `test-utils.js` - Testing utilities
    - `ui/` - Modular UI components (replaced monolithic ui-helpers.js)
  - `css/style.css` - Application styling
- **tests/**: Playwright test suite
  - `playwright.spec.js` - End-to-end testing

## Data Architecture

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

## Development Commands

### Testing
```bash
# Run all Playwright tests
npm test

# Run tests with UI (interactive)
npm run test:ui

# Run tests in debug mode
npm run test:debug

# View test report
npm run report
```

### Development Server
```bash
# Serve the project locally (preferred method)
npm run serve

# Alternative: Simple HTTP server (Python)
python -m http.server 8000

# Then open: http://localhost:8080/playground/
```

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

## License and Attribution

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)  
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at

## Application Architecture

The playground uses a modular class-based architecture:

### Core Classes
- **`MHDBDBPlayground`** (main.js) - Main application controller, orchestrates data managers and UI components
- **`AuthorityFilesManager`** - Handles loading and parsing of authority XML files
- **`TEIFilesManager`** - Manages TEI document processing and text analysis
- **`TEIStorageManager`** - TEI file caching with IndexedDB persistence
- **`IndexedDBManager`** - Core IndexedDB operations for large file storage
- **`AuthorityStorageManager`** - Authority file caching with 30-day expiration policy
- **Modular UI Components** (ui/ directory) - Replaced monolithic ui-helpers.js:
  - `UICore.js` - Core UI utilities and progress tracking
  - `AuthorityExplorers.js` - Authority file exploration interfaces
  - `TEIExplorer.js` - TEI document analysis interface
  - `XPathInterface.js` - XPath query execution

### Data Flow
1. Authority files loaded first (persons, works, lexicon, concepts, genres, names) with 30-day IndexedDB caching
2. TEI files processed with cross-references to authority data
3. Large TEI files (>5MB) automatically cached in IndexedDB for persistence across sessions
4. UI components provide interactive exploration of linked data
5. All data cached in IndexedDB for performance (sessionStorage deprecated due to size limitations)

### Testing Architecture
- **Playwright** end-to-end tests with local server setup
- **Test isolation** - each test clears IndexedDB cache for clean state
- **Headless Chrome** with disabled web security for local XML file access
- Tests run against `test.html` interface with automated progress tracking
- IndexedDB operations tested for large file handling and storage quota management

## Project Context

This is a research repository focused on:
- Digital humanities and medieval studies
- TEI-encoded corpus linguistics
- Semantic annotation of Middle High German literature
- Interactive data exploration for medievalists

When working with this codebase, respect the academic nature of the data and maintain the existing annotation standards and cross-reference integrity.