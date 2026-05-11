# MHDBDB Playground

Interactive web-based analysis tool for exploring TEI-encoded Middle High German texts and authority files from the Mittelhochdeutsche Begriffsdatenbank (MHDBDB).

## Vision

**"SQL Workbench for TEI"** – Desktop-Browser-basierte Analyse-Engine, die Forscher:innen ermöglicht, **alle erdenklichen Fragen** an ihre MHDBDB-Daten zu stellen.

### Problem Statement

Mediävist:innen haben kein flexibles, exploratives Tool, um ihre TEI-Textkorpora und Authority Files interaktiv zu analysieren. Standard XML tools require deep technical knowledge and lack domain-specific query interfaces.

### Target Users

- MHDBDB-Kernteam
- Externe germanistische und mediävistische Forscher:innen
- Promovierende
- Editionseditor:innen

## Features

### Data Management
- **Auto-loading** of TEI corpus and authority files from the repository (no upload step — UI removed in the current redesign)
- **IndexedDB caching** for large file persistence across sessions
- **Client-side processing** - all data stays in your browser
- **Authority file integration** with 30-day cache expiration

### Search & Analysis

**Authority Files Exploration (6 search types):**
1. **Autoren** - Search by name with MHG character normalization
2. **Werke** - Multi-field search across title, author, sigle
3. **Lemmata** - Lexicon search with orthographic variant support (175,910 variants)
4. **Begriffe** - Semantic concept taxonomy (DE/EN)
5. **Gattungen** - Literary genre classification
6. **Namen** - Proper names with semantic relations

**TEI Text Analysis:**
7. **Multi-Lemma-Suche** - Find one or more lemmata across the corpus (paragraph, document, or proximity mode)

### MHG Character Normalization

All searches (except XPath) support automatic normalization of Middle High German special characters:

- **Long vowels:** â→a, ê→e, î→i, ô→o, û→u
- **Umlauts:** ä→ae, ö→oe, ü→ue
- **Ligatures:** æ→ae, œ→oe

**Example:** Searching "brot" finds "brôt", "brott", "brot" and all 50 attested variants.

### Orthographic Variants

**175,910 variant forms** extracted from the corpus and indexed in `variants.xml`:
- Enables fuzzy orthographic matching
- 3-stage resolution: lexicon exact → variants exact → partial fallback
- Supports medieval spelling variation (e.g., "vriunt" = "vrîunt" = "vrivnt")

## Research Questions Supported

- _"Welche Begriffe sind mit 'vriunt' (Freund) verknüpft?"_
- _"Alle Werke von Hartmann von Aue in Gattung 'Höfischer Roman'"_
- _"Zeige Textstellen mit Lemma X in semantischem Kontext Y"_
- _"Wie oft erscheint Person Z in verschiedenen Werken?"_
- _"Wie viele neue Lemmata kommen im 'Parzival' oder bei Konrad von Würzburg vor, die nur dort belegt sind?"_
- _"Gibt es semantische Cluster rund um den Begriff 'ere' über verschiedene Werke hinweg?"_
- _"Welche Tokens stehen im Umkreis von 'vriunt' (Kookkurrenzen)?"_
- _"Wie sieht das Named-Entity-Netzwerk eines kurzen höfischen Romans aus?"_
- _"Welche Eigenheiten hat mein Dissertationskorpus, bestehend aus 'Erec', 'Iwein' und 'Parzival' im Vergleich zum Gesamtbestand?"_

## Usage

### Quick Start

1. **Start local server:**
   ```bash
   npm run serve
   # Opens on http://localhost:8080/playground/
   ```

2. **Data loads automatically:**
   - Authority files load automatically from `../authority-files/`
   - TEI corpus loads from the pre-built index (no drag & drop; upload UI removed in the current redesign)
   - Large files are automatically cached in IndexedDB for subsequent visits

3. **Explore data:**
   - Use "Authority Files durchsuchen" for metadata queries
   - Use "TEI Textanalyse" for text-based searches
   - Try "Multi-Lemma-Suche" for co-occurrence analysis

### Development

```bash
# Install dependencies
npm install

# Run tests
npm test              # Headless mode
npm run test:ui       # Interactive UI
npm run test:debug    # Debug mode

# View test report
npm run report
```

### Test Coverage

- **24 tests** validating core functionality
- **14 tests** validating search normalization
- **92.9% pass rate** (13/14 normalization tests passed)

## Architecture

### Core Classes

- **`MHDBDBPlayground`** (main.js) - Main application controller
- **`AuthorityFilesManager`** - Authority file loading and parsing
- **`TEIFilesManager`** - TEI document processing and analysis
- **`TEIStorageManager`** - IndexedDB persistence for TEI files
- **`AuthorityStorageManager`** - IndexedDB caching with expiration

### UI Components (Modular)

- **`UICore.js`** - Progress tracking, file display
- **`AuthorityExplorers.js`** - Authority file search interfaces
- **`TEIExplorer.js`** - TEI text analysis features
- **`XPathInterface.js`** - XPath query execution
- **`MultiLemmaSearch.js`** - Multi-lemma co-occurrence modal
- **`SearchHelpers.js`** - Reusable search patterns

### Utilities

- **`TextNormalizer.js`** - Centralized MHG character normalization
- **`IndexedDBManager.js`** - Low-level IndexedDB operations

### Data Flow

1. Authority files loaded with 30-day IndexedDB caching
2. TEI corpus loaded from pre-built index and parsed (large files cached automatically)
3. Cross-references resolved between TEI texts and authority data
4. Search queries utilize normalized patterns and variant resolution
5. Results displayed with color-coded highlighting and context

## Technical Specifications

### Requirements

- **Frontend-only:** Vanilla JavaScript ES6+, GitHub Pages compatible
- **Client-side:** All processing in browser, no server calls
- **Desktop-focused:** Minimum 1200px screen width
- **Modern browser:** Chrome/Firefox/Edge with ES6+ and XML DOM APIs

### Constraints

**Must-Have Features (All Implemented):**
- ✅ F1: TEI corpus loading from pre-built index (drag & drop upload UI was removed in the current redesign)
- ✅ F2: Data structure overview (statistics, browsers)
- ✅ F3: Explorative query engine (11 search types)
- ✅ F4: Contextual results (snippets, metadata, cross-refs)
- ✅ F5: 3-panel desktop layout
- ✅ F6: XPath power-user interface

**Optional Features:**
- ⏳ P1: Export functions (CSV/JSON download)
- ⏳ P2: Visualizations (charts, networks)
- ✅ P3: Session persistence (IndexedDB)

**Non-Goals:**
- ❌ Mobile/responsive design
- ❌ Backend/server components
- ❌ Performance for files >50MB
- ❌ User management or multi-tenancy
- ❌ Editing/annotation of TEI files

## Performance

- **Normalization:** 0.003ms per operation
- **IndexedDB:** Handles 6MB+ files efficiently
- **Caching:** 30-day expiration for authority files
- **Test suite:** ~23 seconds for 38 tests

## Open Problems & Future Work

- kein Standard-Interface für XPath-Queries auf lokal gehostete TEI-Korpora
- Komplexität von TEI-Strukturen erschwert Einstieg, wenn keine Vorkenntnisse vorhanden sind
- Visualisierungen (z. B. Begriffsverteilung, Named Entities) fehlen in vielen TEI-Tools
- Kein gemeinsames Tool für Editionsarbeit, Query-Prototyping und Datenreview

## Domain Context

### Mittelhochdeutsche Begriffsdatenbank (MHDBDB)

Research project with over 50 years of medieval text and concept research at the University of Salzburg.

**Data types:**
- **TEI-XML Texte:** Mittelhochdeutsche Literatur mit mehreren Annotationsniveaus
- **7 searchable Authority Files:** persons, works, lexicon, concepts, genres, names, variants (plus `contributors.xml` as project-internal team register since 2026-04, not part of the Playground UI)
- **Semantische Verknüpfungen:** Cross-References zwischen allen Dateien

### Ziel des Playground

- Interne Testumgebung für MHDBDB 4.0-Komponenten
- Einstiegstor für externe Power-User:innen
- Technologisches Labor für neue Analyse-Features
- Plattform für die kollaborative Weiterentwicklung der MHDBDB-Datenmodelle

## License & Contact

**License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
**Contact:** mhdbdb@plus.ac.at
**Website:** https://mhdbdb.plus.ac.at
**Repository:** https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only

---

For technical implementation details, see [CLAUDE.md](../CLAUDE.md) in the repository root.