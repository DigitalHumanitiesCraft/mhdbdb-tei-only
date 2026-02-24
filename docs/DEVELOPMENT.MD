# Development

This document describes the development workflow, build processes, and deployment procedures for the MHDBDB TEI Repository.

## Prerequisites

- **Node.js 16+** (for npm scripts and testing)
- **Python 3.13+** with lxml (for building pre-built indexes)
- **Web Browser** (Chrome/Chromium preferred for testing)
- **Git** (for version control)

**Note:** Pre-built indexes are included in repository, so Python is only needed if modifying source XML files.

## Project Setup

```bash
# Clone repository
git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git
cd mhdbdb-tei-only

# Install dependencies
npm install

# Start development server
npm run serve
# Opens on http://localhost:8080
```

### Directory Structure

```
mhdbdb-tei-only/
├── assets/                # Main site static assets
│   ├── css/               # Stylesheets (korpus.css, tailwind)
│   ├── js/                # Main site JavaScript
│   │   ├── app.js         # Application entry point
│   │   ├── search/        # Search engine
│   │   ├── rendering/     # TEI text reader, text renderer
│   │   ├── storage/       # TEI cache manager
│   │   └── lib/           # Shared utilities (corpus-loader, text-normalizer)
│   └── images/            # Static images
├── authority-files/       # 7 XML authority files
├── tei/                   # TEI corpus files
├── data/                  # Pre-built indexes (generated)
├── scripts/               # Python build scripts
├── playground/            # Playground interface (self-contained sub-app)
├── lemma/                 # Persistent lemma pages (Issue #42)
├── publications/          # Project outputs (blog posts, reports)
├── testing/               # Playwright tests
├── docs/                  # Documentation hub
├── index.html             # Main landing page
└── korpus.html            # Main site search page
```

## Building Pre-Built Indexes

Pre-built indexes are included in repository. Rebuild only when modifying source XML files.

### When to Rebuild

**Authority Index:**
- Authority XML files modified
- Cross-references added/changed
- New GND/Wikidata identifiers

**Corpus Index:**
- TEI files added/removed/modified
- Word annotations changed

**Variants:**
- TEI corpus modified (new orthographic forms)
- Usually paired with corpus index rebuild

### Build Commands

```bash
# Extract variants from TEI corpus
python scripts/extract-variants.py

# Build authority index (includes variants)
python scripts/build-authority-index.py
# Output: data/authority-index.json.gz (~3 MB)

# Build corpus index
python scripts/build-corpus-index.py
# Output: data/corpus-index.json.gz (~21 MB)

# Validate indices
python scripts/validate-indices.py
```

### Version Increment

After significant changes, increment version in build script to force browser cache invalidation:

```python
# In build-authority-index.py
VERSION = "1.2.0"  # Increment for breaking changes
```

## Testing

### Playwright Tests

```bash
npm test              # Run all tests (headless)
npm run test:ui       # Interactive mode
npm run test:debug    # Debug with breakpoints
npm run test:headed   # Visible browser
npm run report        # View HTML report
```

**Test configuration:** `testing/playwright.config.js`
- Automated web server startup (port 8080)
- Headless Chrome with `--disable-web-security`
- 60-second timeout per test

**Test coverage:**
- Authority index loading and caching
- MHG text normalization
- Lemma variant resolution
- Cross-reference integrity
- Search functionality

### Manual Testing Checklist

Before deploying:
- [ ] Search for common word (e.g., "vriunt")
- [ ] Search with variant (e.g., "brot" → "brôt")
- [ ] Text selection and filtering
- [ ] Open reading view
- [ ] Playground explorers
- [ ] Multi-lemma proximity search
- [ ] Playground → main site navigation

## Git Workflow

### Branch Strategy

- **main:** Production-ready code, stable releases
- **Feature branches:** `feature/your-feature-name`
- **Historical branches:**
  - `pre-main-site` - Old XML parsing architecture (archived)
  - `initial-data-wrangling` - RDF/Relational DB → TEI transformation (archived)
  - `feature/wenzelsbibel-ingest` - Wenzelsbibel text ingest (Issue #34, active)

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test locally
npm run serve
# Test in browser...

# 3. Run automated tests
npm test

# 4. CRITICAL: Wait for user to test and approve
# DO NOT COMMIT without user approval!

# 5. Commit with descriptive message
git add .
git commit -m "Add feature: description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push (ONLY AFTER USER APPROVAL)
git push -u origin feature/your-feature-name

# 7. Merge to main
git checkout main
git merge feature/your-feature-name
git push origin main
```

### Commit Guidelines

**DO:**
- Use descriptive messages (not "fix bug" or "update file")
- Include context (what changed and why)
- Reference issues/PRs when applicable
- Add AI-assisted footer

**DON'T:**
- Commit without user testing and approval
- Force push to main
- Skip hooks or validation

## Deployment

### GitHub Pages

**Hosting:** GitHub Pages (static site, free)
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Branch:** `main` (automatically deployed)

### Deployment Process

1. Push to `main` branch
2. GitHub Actions automatically builds and deploys
3. Site updates within 2-5 minutes

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Manual testing complete
- [ ] Pre-built indexes rebuilt (if XML sources changed)
- [ ] Documentation updated
- [ ] User has tested and approved changes

### Post-Deployment Verification

1. Visit https://dhcraft.org/mhdbdb-tei-only/
2. Test main site search
3. Test playground explorers
4. Verify pre-built indexes load correctly

### Cache Invalidation

Increment version number in build scripts to force browser refetch:

```python
VERSION = "1.2.0"  # In build-authority-index.py
```

## Historical Context: Initial Data Wrangling

### Branch: `initial-data-wrangling`

The MHDBDB project originally maintained data in multiple formats (RDF, relational database, partial XML). To create a single source of truth, all data was transformed into TEI-compliant XML documents.

**Process:**
1. Extract from RDF (semantic concepts, genre hierarchies, names)
2. Extract from relational DB (persons, works, lemmata, bibliographic references)
3. Transform to TEI with consistent cross-reference patterns
4. Validate against TEI P5 schema

**Output:** 7 TEI authority files in `authority-files/` directory

**Status:** Archived (completed, preserved for reference)

**Benefits of TEI as single source:**
- Interoperability (TEI is widely supported standard)
- Self-describing (metadata embedded with data)
- Version control friendly (XML diffs are readable)
- Future-proof (TEI will be supported for decades)

**Trade-off:** Large file sizes (solved with pre-built indexes)

---

For data structures, see [DATA-MODEL.MD](DATA-MODEL.MD).
For technical architecture, see [ARCHITECTURE.MD](ARCHITECTURE.MD).
For user-facing features, see [FEATURES.MD](FEATURES.MD).
For architecture decisions, see [DECISIONS.MD](DECISIONS.MD).
