# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the MHDBDB TEI Repository - a collection of TEI-encoded Middle High German literature texts with semantic annotations from the [Mittelhochdeutsche Begriffsdatenbank (MHDBDB)](https://www.mhdbdb.sbg.ac.at), University of Salzburg.

**Key Architectural Decision:** Pre-built JSON indexes (19× smaller, 2.9 MB compressed) replace runtime XML parsing (47 MB) for instant browser loading. Frontend-only architecture with no backend server required.

**Target Audience:** Medievalists, researchers, and students exploring Middle High German literature corpus with semantic annotations.

## Comprehensive Documentation

For detailed information about the project, see our comprehensive documentation hub:

@docs/INDEX.MD

This gateway document provides navigation to 7 specialized documentation files:
- **DATA-MODEL.MD** - Data sources, schemas, transformation pipeline
- **ARCHITECTURE.MD** - Technical components, data flow, storage patterns
- **FEATURES.MD** - User-facing functionality descriptions
- **DEVELOPMENT.MD** - Build commands, git workflow, deployment
- **RESEARCH.MD** - Academic context, TEI/MHG standards
- **DECISIONS.MD** - Architecture Decision Records (ADRs)

## Repository Structure

### Core Directories
- **tei/** - 666 TEI-encoded Middle High German texts
- **authority-files/** - 7 controlled vocabulary XML files (persons, works, lexicon, concepts, genres, names, variants)
- **data/** - Pre-built JSON indexes (`authority-index.json.gz`, `corpus-index.json.gz`)
- **playground/** - Advanced research tool with modular UI (18 components)
- **scripts/** - Python build scripts + data-wrangling workflow
- **testing/** - Playwright test suite (40 passing, 25 skipped)
- **docs/** - Comprehensive knowledge documentation (7 specialized files)

### Key Files
- `index.html` / `korpus.html` - Main site (public corpus browser)
- `playground/index.html` - Advanced research tool
- `lib/corpus-loader.js` - Pre-built index loader with IndexedDB caching
- `scripts/build-authority-index.py` - Extract authority data from XML
- `scripts/build-corpus-index.py` - Extract TEI corpus data
- `scripts/data-wrangling/enhance_works_with_zotero.py` - Zotero API integration

## Quick Reference Commands

```bash
# Rebuild authority index (when authority-files/ XML changes)
python scripts/build-authority-index.py

# Rebuild corpus index (when tei/ XML changes)
python scripts/build-corpus-index.py

# Run tests (Playwright auto-starts web server on port 8080)
npm test

# Serve project locally for development
npm run serve

# Zotero data wrangling (Issue #19)
python scripts/data-wrangling/enhance_works_with_zotero.py --offline
python scripts/data-wrangling/sync_tei_headers.py --works
```

## Critical Constraints

**MUST KNOW:**
- **Frontend-only architecture**: All processing happens in browser (no backend)
- **Desktop-focused**: Minimum 1200px screen width (not mobile-responsive)
- **IndexedDB required**: Large files (lexicon.xml = 32.59 MB) cached in browser
- **TEI namespace**: Always use `http://www.tei-c.org/ns/1.0` when working with XML
- **UTF-8 encoding**: All TEI files use UTF-8

## Development Workflow

### Git Branch Strategy
- **`main`**: Production-ready code, stable releases
- **`pre-main-site`**: Preserved branch with old XML parsing architecture (reference only)
- **Feature branches**: Use descriptive names (e.g., `feature/search-improvements`)

### CRITICAL Git Rules
- **NEVER commit or push without user testing and approval first**
- **ALWAYS wait for user to test changes locally before committing**
- Never force push to `main` - resolve merge conflicts properly
- Rebuild indexes after modifying XML files in `authority-files/` or `tei/`
- Run tests before pushing to ensure nothing breaks
- Update `docs/` when architecture changes (see knowledge doc guidelines below)

### Commit Message Format
```
Brief description of changes

## Changes
- Bullet points of what changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Project-Specific Patterns

### Middle High German Text Normalization
Centralized in `lib/text-normalizer.js`:
- Long vowels: `â→a, ê→e, î→i, ô→o, û→u`
- Umlauts: `ä→ae, ö→oe, ü→ue`
- Ligatures: `æ→ae, œ→oe`

### 3-Stage Lemma Resolution
Implemented in `AuthorityFilesManager.searchLemmaByOrthography()`:
1. **Exact match** in lexicon (canonical forms like 'brôt')
2. **Variants index lookup** (176,056 attested orthographic variants from TEI corpus)
3. **Partial match fallback** (fuzzy search with `includes()`)

This achieves 100% recall for historical spelling variations.

### Pre-Built Index Architecture
- Authority data: `data/authority-index.json.gz` (2.90 MB compressed, v1.1.0)
- Corpus data: `data/corpus-index.json.gz` (21 MB compressed, v4.0.0)
- IndexedDB caching with 30-day TTL for indices
- Version-based cache invalidation
- 19× reduction: 47 MB XML → 2.9 MB compressed JSON

### German Title Case Conversion
Zotero API integration (Issue #19) converts titles from sentence case to Title Case:
- Capitalize first word and words after colons
- Keep German articles/prepositions lowercase (der, die, von, und, etc.)
- Capitalize all other words
- Example: "Das stadtratsgedicht heinrichs von rang" → "Das Stadtratsgedicht Heinrichs von Rang"

## Common Gotchas

### v4.0.0 Breaking Changes (Oct 2025)
- **Removed paragraph-based multi-lemma search** due to position alignment issues
- Now uses **document-level word indexing** for proximity search
- **Position counting**: Only count words with `@lemmaRef` attribute
- Python indexing (`build-corpus-index.py`) and JavaScript extraction MUST match exactly

### TEI Parsing
- **Angle bracket entities** (`&lt;`, `&gt;`) are CORRECT XML encoding - NOT bugs
- Represent punctuation marks in `<seg type="pc">` elements
- XPath queries must use TEI namespace prefix with proper namespace declaration

### Testing
- **25 tests skipped** (main site tests) - this is expected and intentional
- Tests automatically start web server on port 8080 via `playwright.config.js`
- Test suite completes in 2.7 minutes (40 passing, 25 skipped)
- Use `npm run test:ui` for interactive debugging

### Data Wrangling
- **Zotero cache** (.zotero_cache.json) should NOT be committed to git (in .gitignore)
- Script updates ALL items with Zotero data (not just those with editors)
- Extracts ALL fields: edition, volume, issue, series, seriesNumber, authors, editors, notes
- Use `--offline` mode for reproducible builds without API calls

## Recent Major Changes

**October 2025:**
- ✅ **Korpus Layout Refactor** - Side-by-side 3-column grid with browser-level scrolling (no container scrollbars)
- ✅ **Zotero API Integration (Issue #19)** - Complete bibliographic metadata sync with Title Case conversion
- ✅ **Phase 7 Modular UI** - Decomposed into 18 specialized components (5,536 lines removed)
- ✅ **Corpus Index v4.0.0** - Fixed proximity search position alignment (document-level indexing)
- ✅ **Main Site Simplification** - Text selection interface with checkboxes (666 texts)
- ✅ **Reading View** - Rich metadata with Wikidata images and GND/Wikidata identifiers
- ✅ **Multi-Lemma Reader Integration** - Playground → main site workflow with color-coded highlighting

## Knowledge Documentation Guidelines

This project maintains comprehensive documentation in `docs/`. When updating documentation:

**✅ DO:**
- Focus on unique architectural decisions and their rationale
- Explain data structures and relationships (not implementation)
- Document trade-offs and alternatives considered
- Use descriptive headers for scanability
- Include one concrete example per concept

**❌ DON'T:**
- Include installation instructions (developers know `npm install`)
- Add exact metrics unless essential (say "hundreds" not "666")
- Write troubleshooting sections (use GitHub issues)
- Repeat information across documents (each fact documented once)
- Show expected command outputs (developers can run commands)

**When to Update docs/:**
- After architectural changes (new components, removed features)
- After data model changes (new index fields, schema changes)
- After major refactorings
- When adding ADRs for significant decisions

**When NOT to Update docs/:**
- Bug fixes (unless they reveal architectural issues)
- Minor UI tweaks
- Dependency updates
- Code cleanup without behavior changes

See @docs/INDEX.MD for complete documentation structure and guidelines.

## System Requirements

### Prerequisites
- **Node.js**: 16+ (for npm scripts and testing)
- **Python**: 3.13+ with lxml (for building indexes from XML sources)
- **Web Browser**: Chrome/Chromium (for Playwright tests)
- **Git**: For version control

**Note**: Pre-built indexes are included in the repository, so Python is only needed if you modify source XML files.

## License and Attribution

**License:** [CC BY-NC-SA 3.0 AT](https://creativecommons.org/licenses/by-nc-sa/3.0/at/)
**Contact:** mhdbdb@plus.ac.at | https://mhdbdb.plus.ac.at
