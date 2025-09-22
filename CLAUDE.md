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
  - `js/` - JavaScript modules for data processing
    - `main.js` - Application entry point
    - `authority-files.js` - Authority data handling
    - `tei-files.js` - TEI text processing
    - `ui/` - UI component modules
  - `css/style.css` - Application styling

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

## Development Tasks

### Starting the Web Interface
```bash
# Option 1: Simple HTTP server (Python)
python -m http.server 8000

# Option 2: Node.js server (if available)
npx http-server

# Then open: http://localhost:8000/playground/
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

## Project Context

This is a research repository focused on:
- Digital humanities and medieval studies
- TEI-encoded corpus linguistics
- Semantic annotation of Middle High German literature
- Interactive data exploration for medievalists

When working with this codebase, respect the academic nature of the data and maintain the existing annotation standards and cross-reference integrity.