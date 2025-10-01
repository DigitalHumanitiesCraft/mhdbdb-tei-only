# MHDBDB Main Website Implementation Plan

## Overview
Create a public-facing main entry website (`index.html` in root) that serves as an accessible portal to the MHDBDB TEI corpus, alongside the existing expert-focused playground. The main site will feature:
- Comprehensive "About" information about the MHDBDB project
- Automatic loading of all 666 TEI files from `tei/` directory into IndexedDB
- Simple text browsing and reading interface
- Single-word search functionality (e.g., search "brot" → find all texts containing that lemma)
- Link to the professional Playground for advanced users
- Consistent look and feel with the existing playground (Tailwind CSS, same color scheme)

---

## Implementation Steps

### 1. **Create Main Website Structure** (`index.html` in root)

**File:** `index.html`

- **Header Section:**
  - Project title: "Mittelhochdeutsche Begriffsdatenbank (MHDBDB)"
  - University of Salzburg branding
  - Navigation links (About, Browse Texts, Search, Playground)

- **About Section:**
  - Project description and academic context
  - Corpus statistics (666 TEI texts, 7 authority files)
  - Research team and contact information
  - License information (CC BY-NC-SA 3.0 AT)
  - Link to MHDBDB website: https://mhdbdb.plus.ac.at

- **Text Browser Section:**
  - List view of all 666 TEI files (loaded from `tei/` directory)
  - Sortable/filterable by title, author, sigle
  - Reading interface with full text display
  - Metadata display (work info, author, genre)

- **Simple Search Section:**
  - Single search input: "Search for a word (e.g., brot, vriunt)"
  - Results: List of texts containing the search term (with lemma matching)
  - Context snippets showing word usage
  - Link to full text view
  - Call-to-action: "Need advanced search? Try our [Playground](#) for multi-lemma search, XPath queries, and more"

### 2. **Create Main Website JavaScript Module**

**File:** `js/main-site.js`

**Functionality:**
- **Automatic TEI Loading:**
  - Fetch all 666 TEI files from `tei/` directory (manifest-based or dynamic fetch)
  - Load into IndexedDB using existing `TEIStorageManager`
  - Progress indicator during initial load
  - Persistent caching (no expiration for corpus texts)

- **Text Browser:**
  - Display list of all loaded texts with metadata
  - Filter/search by title, author, sigle
  - Full text reading view with clean typography
  - Extract metadata from TEI headers

- **Simple Word Search:**
  - Reuse `TextNormalizer.normalizeMHG()` for MHG character handling
  - Reuse `AuthorityFilesManager.searchLemmaByOrthography()` for lemma resolution
  - Search across all loaded TEI files for matching lemmas
  - Display results as: **Text Title** → **Snippet with highlighted word** → **Link to full text**
  - Simple pagination for large result sets

### 3. **Create Shared CSS Styles**

**File:** `css/main-site.css`

- Consistent with playground styling (Tailwind + custom brand colors)
- Responsive layout (mobile-friendly, unlike playground)
- Typography optimized for long-form reading
- About section: clean, academic layout
- Search interface: prominent, easy-to-use input
- Text browser: card-based layout with metadata badges

### 4. **Create TEI File Manifest**

**File:** `tei/manifest.json` (or dynamically generate via script)

```json
{
  "texts": [
    {
      "filename": "ABG.tei.xml",
      "title": "Von der Abgeschiedenheit",
      "author": "Meister Eckhart",
      "sigle": "ABG"
    },
    // ... 665 more entries
  ]
}
```

**Purpose:** Avoid fetching all 666 files individually; load manifest first, then lazy-load texts as needed.

### 5. **Reuse Existing Modules**

- **`playground/js/authority-files.js`:** Reuse for lemma resolution
- **`playground/js/utils/text-normalizer.js`:** Reuse for MHG normalization
- **`playground/js/indexed-db-manager.js`:** Reuse for storage
- **`playground/js/authority-storage-manager.js`:** Reuse for authority file caching

**Approach:** Import modules via ES6 imports from `playground/js/` directory.

### 6. **Link Between Main Site and Playground**

- **Main Site → Playground:**
  - Prominent CTA in search section: "For advanced users: Try the [MHDBDB Playground →](#)"
  - Link in header navigation
  - Contextual links in search results: "Refine this search in the Playground"

- **Playground → Main Site:**
  - Add link in playground header: "← Back to Main Site"
  - About section in playground links to main site

### 7. **Update Project Documentation**

**Files to update:**
- `CLAUDE.md`: Add section describing main site architecture
- `README.md` (if exists): Add navigation guide

---

## Technical Architecture

### Data Flow

```
User visits index.html
  ↓
Load tei/manifest.json (list of 666 files)
  ↓
Check IndexedDB for cached files
  ↓
Fetch missing files from tei/ directory
  ↓
Parse TEI XML, extract metadata & words
  ↓
Store in IndexedDB (persistent)
  ↓
Populate text browser UI
  ↓
User searches "brot"
  ↓
Normalize "brot" via TextNormalizer
  ↓
Resolve lemma via AuthorityFilesManager (lexicon + variants)
  ↓
Search all cached TEI files for lemma matches
  ↓
Display results with snippets
  ↓
User clicks result → View full text
```

### Storage Strategy

- **IndexedDB Stores:**
  - `mainSiteTEI`: All 666 corpus texts (no expiration)
  - `authorityFiles`: Authority files (30-day expiration, reused from playground)

- **Loading Strategy:**
  - **First visit:** Fetch all 666 files (~50MB total), cache in IndexedDB, show progress bar
  - **Subsequent visits:** Instant load from cache

### Search Implementation

**Simple Word Search:**
```javascript
async searchWord(searchTerm) {
  // 1. Normalize input
  const normalized = TextNormalizer.normalizeMHG(searchTerm);

  // 2. Resolve lemma ID(s) via authority files
  const lemmaResult = await authorityManager.searchLemmaByOrthography(normalized);

  // 3. Search all TEI files for lemma matches
  const results = [];
  for (const teiFile of teiData.parsedXML) {
    const matches = teiFile.doc.querySelectorAll(`w[lemmaRef*="${lemmaResult.id}"]`);
    if (matches.length > 0) {
      results.push({
        filename: teiFile.filename,
        title: extractTitle(teiFile.doc),
        matches: extractContextSnippets(matches),
        count: matches.length
      });
    }
  }

  return results;
}
```

---

## User Experience Flow

### First-Time Visitor
1. Lands on **About section** (hero with project description)
2. Scrolls to see **simple search box** with example query
3. Enters "brot" → sees loading indicator (corpus loading in background)
4. Results appear: 15 texts containing "brot" with highlighted snippets
5. Clicks a result → reads full text with clean typography
6. Sees CTA: "Need multi-lemma search? Try the Playground"

### Returning Visitor
1. Lands on main site (instant load, cached corpus)
2. Directly searches for a word
3. Instant results (no network delay)

### Expert User
1. Finds Playground link in header
2. Transitions to playground for advanced features (multi-lemma, XPath, co-occurrence)

---

## File Structure (New Files)

```
mhdbdb-tei-only/
├── index.html               (NEW - Main entry site)
├── css/
│   └── main-site.css        (NEW - Main site styles)
├── js/
│   ├── main-site.js         (NEW - Main site app logic)
│   └── tei-loader.js        (NEW - Bulk TEI loading utilities)
├── tei/
│   └── manifest.json        (NEW - TEI file listing)
├── playground/              (EXISTING - No changes to core files)
│   ├── index.html
│   └── js/
│       ├── authority-files.js      (REUSE)
│       ├── utils/text-normalizer.js (REUSE)
│       ├── indexed-db-manager.js   (REUSE)
│       └── ...
└── CLAUDE.md                (UPDATE - Add main site docs)
```

---

## Design Mockup (Text Description)

### Header
- Logo/Title: "MHDBDB – Mittelhochdeutsche Begriffsdatenbank"
- Subtitle: "Universität Salzburg"
- Navigation: [About] [Browse Texts] [Search] [Playground →]

### About Section (Hero)
- Large heading: "Explore Middle High German Literature"
- Description: 666 TEI-encoded texts with semantic annotations
- Statistics cards: 666 Texts | 7 Authority Files | 192,674 Orthographic Variants
- CTA button: "Start Exploring"

### Simple Search Section
- Large search input: "Search for a word (e.g., brot, vriunt, liebe)"
- Helper text: "Searches across all 666 texts with automatic lemma matching"
- Results: Card-based layout with:
  - Text title + author
  - Snippet with highlighted word
  - Match count badge
  - "Read full text" link

### Text Browser Section
- Filter bar: Search by title/author/sigle
- Grid of text cards:
  - Title
  - Author
  - Genre badges
  - Word count
  - "Read" button

### Footer
- License: CC BY-NC-SA 3.0 AT
- Contact: mhdbdb@plus.ac.at
- Link to MHDBDB website
- Link to Playground

---

## Development Tasks

### Phase 1: Core Infrastructure (Priority 1)
1. Create `index.html` with basic layout
2. Create `js/main-site.js` with app initialization
3. Create `tei/manifest.json` (script to generate from directory)
4. Implement IndexedDB loading for all 666 TEI files
5. Create progress indicator UI

### Phase 2: Search Functionality (Priority 1)
6. Implement simple word search with lemma resolution
7. Display search results with context snippets
8. Link search results to full text view
9. Add MHG normalization integration

### Phase 3: Text Browser (Priority 2)
10. Implement text list view with metadata
11. Add filtering/sorting functionality
12. Create full text reading view
13. Extract and display TEI metadata

### Phase 4: About Section (Priority 2)
14. Write comprehensive project description
15. Add corpus statistics
16. Add team/contact information
17. Add license and attribution

### Phase 5: Styling & UX (Priority 3)
18. Apply Tailwind CSS with brand colors
19. Optimize typography for reading
20. Add loading states and animations
21. Test responsive layout

### Phase 6: Integration (Priority 3)
22. Add links between main site and playground
23. Update CLAUDE.md documentation
24. Add README with navigation guide
25. Test cross-browser compatibility

---

## Open Questions / Decisions Needed

1. **TEI Loading Strategy:**
   - Option A: Load all 666 files on first visit (show progress bar)
   - Option B: Lazy-load texts on-demand (faster initial load, slower search)
   - **Recommendation:** Option A (better for search performance)

2. **Manifest Generation:**
   - Manual JSON creation vs. automated script?
   - **Recommendation:** Python script to extract metadata from TEI headers

3. **Mobile Responsiveness:**
   - Main site should be mobile-friendly (unlike playground)
   - Simplified layout for small screens

4. **Search Result Limit:**
   - Show top 50 results? 100 results? All results?
   - **Recommendation:** Top 50 with "Load more" button

---

## Success Criteria

✅ Main site loads quickly (< 3s on first visit)
✅ Search returns results in < 1s (after initial corpus load)
✅ All 666 TEI files load and cache correctly
✅ Lemma search works with MHG normalization (brot → brôt)
✅ Full text reading view is clean and readable
✅ Playground link is prominent and clear
✅ Design matches playground aesthetic
✅ About section provides comprehensive project info