# Features

This document describes user-facing functionality of the MHDBDB TEI Repository, organized by interface (Main Site vs Playground).

## Main Site Features

The main site provides a streamlined interface optimized for students and general users.

### Single Lemma Search

Search for Middle High German words across the corpus with automatic normalization and variant resolution.

**How it works:**
- User enters search term
- System normalizes MHG characters (â→a, ô→o, ü→ue)
- Resolves orthographic variants (e.g., "brot", "brott" → "brôt")
- Searches across selected texts
- **Multi-lemma disambiguation:** When search resolves to multiple lemmata, results are deduplicated by text with all matched lemmata displayed
- Returns results with match counts aggregated across lemmata

**Visual design:**
- Blue info box showing all matched lemmata as badges
- White result cards showing title, sigle, author, genre
- Match count with lemma indicator (e.g., "2399 Treffer (2 Lemmata)")
- Auto-scroll to results with offset for sticky header

### Text Selection Interface

Include/exclude specific texts from search corpus.

**How it works:**
- Click button to open selection panel
- See all texts with checkboxes (all checked by default)
- Filter by title, sigle, or author
- Bulk actions: "Alle auswählen" / "Keine auswählen"
- Search respects selected texts

**Use cases:**
- Genre-specific search (select only mystical prose)
- Author-specific search (select all Meister Eckhart works)
- Comparative analysis across selected authors

### Reading View

Full-text immersive reader with multi-lemma highlighting and rich metadata.

**Key features:**
- **Multi-lemma highlighting:** Up to 5 lemmas with distinct colors (red, blue, green, yellow, purple)
- **Rich metadata panel:** Work details, author info, bibliographic references
- **Wikidata integration:** Automatic image fetching with attribution
- **Dual identifiers:** Separate GND/Wikidata for work vs author
- **Context navigation:** Prev/next buttons to jump between occurrences
- **URL parameters:** `?textId=ABG&lemmaIds=879,7532&position=310`

**Visual design:**
- Two-column layout (text 70%, metadata 30%)
- Readable serif font with comfortable line height
- Expandable/collapsible metadata sections
- Scrollable metadata (max-height 400px)

### TEI File Caching

Cache large TEI files in browser storage for faster subsequent loads.

**How it works:**
- Files >5MB automatically cached in IndexedDB
- No expiration (user content persists)
- Subsequent loads ~100-200ms vs 3-5 seconds

## Playground Features

The playground provides advanced research tools for medievalists and digital humanities researchers.

### Authority File Exploration

Browse and search six controlled vocabularies with consistent interface patterns.

**Person Explorer:**
- Search by author name
- Display: Name, GND/Wikidata links, work count
- Action: View all works by author

**Work Explorer:**
- Search by title, sigle, or author
- Display: Title, sigle, author, genres, GND/Wikidata (work-specific), bibliographic references
- Note: v1.1.0 added separate work identifiers (distinct from author)

**Lemma Explorer:**
- Search by lemma (normalized MHG)
- Display: Lemma, POS, sense count, etymology, full sense definitions with concepts
- Action: Search lemma in corpus

**Concept Explorer:**
- Search by concept term (German or English)
- Display: Term, hierarchy (broader/narrower), associated lemmata
- Action: Navigate hierarchy, view all lemmata for concept
- Note: v1.1.0 replaced inline truncation with full searchable interface

**Genre Explorer:**
- Search by genre term
- Display: Term, hierarchy (broader genres), associated works
- Action: View all works in genre
- Note: v1.1.0 fixed hierarchy extraction

**Name Explorer:**
- Search by proper name
- Display: Name, related concepts
- Action: View concept relationships

### TEI Text Analysis

Upload and analyze custom TEI files.

**Single Lemma Search:**
- Upload TEI files (drag-and-drop or file picker)
- Search by lemma ID or MHG term
- Display all occurrences with context

**Multi-Lemma Document Search:**
- Input multiple lemmata (space-separated or one per line)
- Find texts containing ALL lemmata (anywhere in document)
- Automatic variant resolution
- Results: List of matching texts

**Multi-Lemma Proximity Search:**
- Input multiple lemmata
- Set max distance (1-50 words, default 10)
- Find co-occurrences within distance
- Automatic variant resolution
- Results: Context snippets with color-coded highlighting
- Click result → open main site reading view with URL parameters

**Cross-platform workflow:**
1. Perform proximity search in playground
2. Find interesting co-occurrence
3. Click result
4. Opens main site reading view with all lemmata highlighted
5. Auto-scroll to exact position

### Search Normalization

Consistent search behavior across all 10 entry points via Middle High German character normalization.

**Normalization rules:**
- Long vowels: â→a, ê→e, î→i, ô→o, û→u
- Umlauts: ä→ae, ö→oe, ü→ue
- Ligatures: æ→ae, œ→oe

**Implementation:**
- Shared utility: `lib/text-normalizer.js`
- Applied to all search inputs and indexed data
- Enables consistent matching across orthographic variations

**Note:** Normalization handles **character variations**, variants.xml handles **spelling variations**. Both used together for comprehensive search coverage.

---

For technical implementation, see [ARCHITECTURE.MD](ARCHITECTURE.MD).
For data structures, see [DATA-MODEL.MD](DATA-MODEL.MD).
For development workflow, see [DEVELOPMENT.MD](DEVELOPMENT.MD).
