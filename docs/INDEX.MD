# MHDBDB TEI Knowledge Base

Digital corpus of Middle High German literature with semantic annotations from the Mittelhochdeutsche Begriffsdatenbank (MHDBDB), University of Salzburg.

## Project Overview

The MHDBDB TEI Repository provides a comprehensive digital corpus of Middle High German literature with sophisticated semantic markup. The project combines traditional philological scholarship with modern digital humanities methods, offering both a public-facing search interface and an advanced research playground.

**Live Demos:**
- Main Site: https://dhcraft.org/mhdbdb-tei-only/
- Playground: https://dhcraft.org/mhdbdb-tei-only/playground/

**Target Audience:** Digital humanities researchers, medievalists, linguists, students of Middle High German literature

## Data Basis

### Curated Corpus
- **Hundreds of TEI files** - Complete Middle High German texts with word-level annotations
- **7 authority files** - Controlled vocabularies for persons, works, lexicon, concepts, genres, names, variants
- **Pre-built indexes** - Compressed JSON (3 MB authority + 34 MB corpus) replacing runtime XML parsing

### Key Architecture Decision
The project migrated from runtime XML parsing to pre-built JSON indexes because large XML files caused 30-second browser load times. Pre-built indexes reduce download size by 19× and eliminate parsing overhead. Trade-off: requires Python build step when XML sources change.

## Core Features

### Main Site (Public Interface)
Simple search and reading interface optimized for students and general users:

- **Single Lemma Search** - Search across corpus with Middle High German character normalization
- **Text Selection** - Include/exclude texts via checkbox interface with live filtering
- **Reading View** - Full-text reader with:
  - Multi-lemma highlighting (5 colors for concurrent searches)
  - Rich metadata panel with Wikidata integration
  - Context navigation (jump between occurrences)
  - Separate work vs author identifiers (GND/Wikidata)
- **Variant Resolution** - Automatic mapping of orthographic variants via variants.xml

### Playground (Research Interface)
Advanced exploration tools for medievalists and digital humanities researchers:

- **10 Search Entry Points** - 6 authority file explorers + 4 TEI analysis modes
- **Multi-Lemma Search** - Find texts containing multiple lemmata with:
  - Document-level search (all lemmata anywhere in text)
  - Proximity search (co-occurrence within N words)
  - 3-stage lemma resolution (exact match → variants → partial match)
  - Color-coded results with clickable navigation to reading view
- **Authority Exploration** - Browse and search persons, works, lemmata, concepts, genres, names
- **TEI Analysis** - Upload and analyze custom TEI files

## Technical Stack

### Frontend Architecture
- Vanilla JavaScript ES6+ (no frameworks)
- Pre-built JSON indexes with gzip compression
- IndexedDB caching (30-day expiration for reference data)
- Desktop-optimized (minimum 1200px width)

### Build Pipeline
- Python 3.13+ with lxml for XML processing
- Build scripts extract data from XML → JSON
- Gzip compression for production indexes

### Testing & Deployment
- Playwright end-to-end tests
- GitHub Pages hosting (static site)
- Automated deployment via GitHub Actions

## Documentation Structure

This knowledge base follows a hub-and-spoke architecture with INDEX.MD as the central gateway:

### Stable Knowledge (what the project IS)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[INDEX.MD](INDEX.MD)** | Project overview, navigation hub | Anyone |
| **[DATA-MODEL.MD](DATA-MODEL.MD)** | Data sources, schemas, transformation pipeline | Data engineers |
| **[ARCHITECTURE.MD](ARCHITECTURE.MD)** | Technical components, data flow, storage patterns | Developers |
| **[DESIGN.MD](DESIGN.MD)** | Visual patterns, color system, components, CSS architecture | Developers/Designers |
| **[FEATURES.MD](FEATURES.MD)** | User-facing functionality descriptions | Users/Stakeholders |
| **[DEVELOPMENT.MD](DEVELOPMENT.MD)** | Build commands, git workflow, deployment | New contributors |
| **[RESEARCH.MD](RESEARCH.MD)** | Academic context, TEI/MHG standards | Researchers |
| **[DECISIONS.MD](DECISIONS.MD)** | Architecture Decision Records (ADRs) | Architects |
| **[CONTRACTS.MD](CONTRACTS.MD)** | Cross-language parity constraints, algorithm pseudocode, API contracts | Developers |
| **[TEI-MODEL.md](TEI-MODEL.md)** | Normative TEI encoding (Soll-Modell), IST/SOLL-Vergleiche, Validierungsbaseline | Data engineers, Developers |
| **[USER-GUIDE.MD](USER-GUIDE.MD)** | End-user documentation | Users |

### Process (what's happening and why)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[ROADMAP.md](ROADMAP.md)** | Current priorities, strategic direction, what's blocked | Everyone |
| **[JOURNAL.md](JOURNAL.md)** | Chronological development log, decisions, dead ends | Developers |
| **[features/](features/)** | Feature-scoped planning docs (living, archived when shipped) | Developers |

### Publications (project outputs, not development docs)

Located in `/publications/` (outside `docs/`):
- `BLOG-POST-POS-WORKFLOW.md` — DHCraft blog draft on PoS disambiguation
- `JAHRESBERICHT-2025.md` — CLARIAH-AT annual report

## Project Status

### Current Phase
Post-MVP with stable v4.0.0 corpus index and v1.1.0 authority index

### Recent Milestones
- ✅ **Phase 7 Refactoring** - Modular UI architecture
- ✅ **Corpus Index v4.0.0** - Document-level word indexing for accurate proximity search
- ✅ **Reading View** - Full-text reader with multi-lemma highlighting and Wikidata integration
- ✅ **Pre-Built Index Migration** - Eliminated runtime XML parsing

### Known Limitations
- Desktop-only interface (not mobile-responsive)
- No backend processing (all computation in browser)
- Static corpus (requires rebuild for updates)

### Future Directions
- Mobile optimization
- RESTful API for programmatic access
- Advanced visualizations (network graphs, timelines)
- Backend integration for real-time updates

## Links and Resources

### Project
- **Main Site:** https://dhcraft.org/mhdbdb-tei-only/
- **Playground:** https://dhcraft.org/mhdbdb-tei-only/playground/
- **GitHub Repository:** https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only
- **Issue Tracker:** https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues

### Data Sources
- **MHDBDB Salzburg:** https://www.mhdbdb.sbg.ac.at
- **University of Salzburg:** https://www.plus.ac.at

### Standards
- **TEI P5 Guidelines:** https://www.tei-c.org/release/doc/tei-p5-doc/en/html/
- **GND (Gemeinsame Normdatei):** https://www.dnb.de/gnd
- **Wikidata:** https://www.wikidata.org

### Contact
- **Email:** mhdbdb@plus.ac.at
- **Maintainer:** Digital Humanities Craft OG
- **Project Lead:** University of Salzburg, Department of German Studies
- **License:** CC BY-NC-SA 4.0

## Quick Start

### For Users
1. Visit [Main Site](https://dhcraft.org/mhdbdb-tei-only/)
2. Enter a Middle High German word (e.g., "vriunt", "minne", "êre")
3. Browse search results and click "Text öffnen" to read full text with highlighting

### For Researchers
1. Visit [Playground](https://dhcraft.org/mhdbdb-tei-only/playground/)
2. Explore authority files (persons, works, lemmata, concepts, genres, names)
3. Try multi-lemma search with proximity analysis

### For Developers
1. Clone repository: `git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git`
2. Install dependencies: `npm install`
3. Serve locally: `npm run serve`
4. Read [DEVELOPMENT.MD](DEVELOPMENT.MD) for build and deployment workflows

---

**License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | **Contact:** mhdbdb@plus.ac.at
