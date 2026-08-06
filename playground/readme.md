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
- **IndexedDB caching** of the pre-built corpus and authority indexes, via the shared `CorpusLoader` (database `MHDBDBMainSite`)
- **Client-side processing** - all data stays in your browser
- **Authority file integration** with 30-day cache expiration

### Search & Analysis

**Authority Files Exploration (6 explorers):**
1. **Autoren** - Search by name with MHG character normalization
2. **Werke** - Multi-field search across title, author, sigle
3. **Lemmata** - Lexicon search with orthographic variant support
4. **Begriffe** - Semantic concept taxonomy (DE/EN)
5. **Gattungen** - Literary genre classification
6. **Namen** - Proper names with semantic relations

**TEI Text Analysis (12 tools):** from the multi-lemma search with proximity analysis to the rhyme dictionary and the verse-ending profile.

The list of tools is deliberately **not repeated here**. It already lives in [FEATURES.md](../docs/FEATURES.md), with counts, examples and issue references, and every new tool would otherwise have to be entered in a fourth place. This section carried exactly one of the twelve until 2026-08-06, which is what a duplicated catalog looks like once nobody keeps it in step. The modules themselves are the ground truth: one file per tool in `playground/js/ui/tei/`, one per explorer in `playground/js/ui/authority/`.

### MHG Character Normalization

All searches (except XPath) support automatic normalization of Middle High German special characters:

- **Long vowels:** â→a, ê→e, î→i, ô→o, û→u
- **Umlauts:** ä→ae, ö→oe, ü→ue
- **Ligatures:** æ→ae, œ→oe

**Example:** Searching "brot" also finds "brôt" and the other attested spellings of the same lemma.

### Orthographic Variants

Variant forms are extracted from the corpus and indexed in `variants.xml`:
- Enables fuzzy orthographic matching
- 3-stage resolution: lexicon exact → variants exact → prefix fallback
- Supports medieval spelling variation (e.g., "vriunt" = "vrîunt" = "vrivnt")

**No count is given here on purpose.** There are two of them and they measure different things: the raw `<form>` elements in `variants.xml` and the normalized mappings in the authority index, the latter markedly fewer. Both are correct, neither may be quoted for the other, and both change with every re-annotation. The measured values live in [CONTRACTS.md §C](../docs/CONTRACTS.md) and in [DATA-MODEL.md](../docs/DATA-MODEL.md), where `doc-count-audit.py` keeps them honest. The figure that stood here until 2026-08-06 matched neither of the two.

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
   - The indexes are cached in IndexedDB for subsequent visits

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

### Tests

The suite is repo-wide, not per sub-app: `npm test` from the repository root, and the VERDICT line it prints is the result. The spec inventory with one line per file is in [DEVELOPMENT.md](../docs/DEVELOPMENT.md) and gated against `testing/tests/`, so it cannot quietly go stale the way the count that stood here did.

## Architecture

### Core Classes

- **`MHDBDBPlayground`** (`playground-main.js`) - Main application controller
- **`AuthorityFilesManager`** - Authority file loading and parsing
- **`TEIFilesManager`** - Multi-lemma search over the pre-built corpus index

### UI Components (Modular)

- **`SearchHelpers.js`** (`playground/js/ui/search/`) - wiederverwendbare Suchmuster, exportiert `SearchPatterns`

*Die vier Namen `AuthorityExplorers.js`, `TEIExplorer.js`, `XPathInterface.js` und `MultiLemmaSearch.js` standen bis Juli 2026 hier und benennen keine Datei im Repo. Der aktuelle Modulbaum steht in [ARCHITECTURE.md](../docs/ARCHITECTURE.md) (23 Module unter `playground/js/ui/`). Ein fünfter Eintrag, `UICore.js`, ist mit #314 weggefallen, weil er genau die beiden gelöschten Module benannte.*

### Utilities

- **`text-normalizer.js`** (`assets/js/lib/`) - Centralized MHG character normalization, shared with the main site and mirrored in `scripts/mhg_normalizer.py` (CONTRACTS.md Contract A)

### Data Flow

1. Authority files loaded with 30-day IndexedDB caching
2. TEI corpus read from the pre-built index, not parsed as XML (`playground-main.js`: "use the index directly")
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
- ✅ F3: Explorative query engine (6 authority explorers plus 12 TEI tools)
- ✅ F4: Contextual results (snippets, metadata, cross-refs)
- ✅ F5: 3-panel desktop layout
- ✅ F6: XPath power-user interface

**Optional Features:**
- ⏳ P1: Export functions (CSV/JSON download)
- ⏳ P2: Visualizations (charts, networks)
- ❌ P3: Session persistence (IndexedDB) – war der Datei-Upload, entfernt mit #314

**Non-Goals:**
- ❌ Mobile/responsive design
- ❌ Backend/server components
- ❌ Performance for files >50MB
- ❌ User management or multi-tenancy
- ❌ Editing/annotation of TEI files

## Performance

- **Normalization:** 0.003ms per operation
- **IndexedDB:** Korpus- und Authority-Index über den gemeinsamen `CorpusLoader` (`MHDBDBMainSite`); der frühere Upload-Store ist mit #314 weg
- **Caching:** 30-day expiration for authority files

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