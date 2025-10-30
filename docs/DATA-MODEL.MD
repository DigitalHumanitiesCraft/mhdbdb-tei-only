# Data Model

This document describes the data sources, schemas, and transformation pipeline for the MHDBDB TEI Repository.

## Overview

The MHDBDB data architecture follows a three-stage flow:

```
[Source XML Files]
   ↓ Python Build Scripts
[Pre-Built JSON Indexes]
   ↓ Browser Fetch + Decompress
[Runtime Data Structures]
```

**Key Principle:** Pre-compute expensive operations (XML parsing, cross-reference resolution) at build time rather than runtime, reducing browser load from ~50 MB XML to ~3 MB compressed JSON (19× reduction).

## Source Data

### TEI Corpus Files

**Location:** `tei/` directory
**Format:** TEI P5 XML (UTF-8, namespace: `http://www.tei-c.org/ns/1.0`)

Each TEI file contains:
- TEI Header with bibliographic metadata
- Text body with word-level annotations
- Word elements (`<w>`) with `@lemmaRef` and `@wordRef` attributes

**Cross-reference pattern:**
```xml
<w lemmaRef="#lemma_879">brott</w>
```

### Authority Files

**Location:** `authority-files/` directory
**Format:** TEI P5 XML with custom MHDBDB schema

Seven controlled vocabularies:
- `persons.xml` - Authors and historical persons
- `works.xml` - Work and manuscript metadata
- `lexicon.xml` - Dictionary with tens of thousands of lemmata
- `concepts.xml` - Semantic concept taxonomy
- `genres.xml` - Literary genre classification
- `names.xml` - Proper names with semantic relations
- `variants.xml` - Orthographic variants extracted from corpus

**Cross-reference patterns:**
- Person ↔ Work via `xml:id` and `@ref`
- Lemma → Concept via `@ana`
- Work → Genre via genre IDs
- Orthographic variant → Lemma via normalized form lookup

## Pre-Built Index Architecture

The project uses pre-built JSON indexes to avoid runtime XML parsing.

### Authority Index

**File:** `data/authority-index.json.gz`
**Size:** ~3 MB compressed
**Version:** 1.1.0

**Schema:**
```javascript
{
  version: "1.1.0",
  generatedAt: "ISO-8601 timestamp",

  persons: [{
    id: "person_445",
    preferredName: "Meister Eckhart",
    gnd: "118528696",
    wikidata: "Q43976",
    works: ["work_001", ...],
    normalized: "meister eckhart"
  }],

  works: [{
    id: "work_001",
    title: "Von der Abgeschiedenheit",
    titles: ["Von der Abgeschiedenheit", ...],
    sigle: "ABG",
    sigles: ["ABG"],
    author: "Meister Eckhart",
    authorRef: "person_445",
    gnd: "work GND",              // Added v1.1.0
    wikidata: "work Wikidata",    // Added v1.1.0
    genres: ["genre_123"],
    biblStructs: [{type, key, title}],
    handschriftencensus: "12345",
    normalized: "..."
  }],

  lemmata: [{
    id: "lemma_879",
    lemma: "brôt",
    pos: "N",
    senseCount: 3,
    etymology: [{language, form}],
    senses: [{
      id: "sense_001",
      definition: "...",
      conceptIds: ["concept_1234"],
      examples: [...]
    }],
    normalized: "brot"
  }],

  concepts: [{
    id: "concept_1234",
    termDE: "Nahrung",
    termEN: "Food",
    broader: "concept_5678",
    narrower: ["concept_9012"],
    normalized: "..."
  }],

  genres: [{
    id: "genre_123",
    termDE: "Mystische Prosa",
    termEN: "Mystical Prose",
    broader: ["Prosa", "Mystik"],
    normalized: "..."
  }],

  names: [{
    id: "name_456",
    termDE: "Aristoteles",
    termEN: "Aristotle",
    conceptIds: ["concept_7890"],
    normalized: "..."
  }],

  variants: {
    "brot": "lemma_879",   // normalized form → lemma ID
    "brott": "lemma_879",
    // ... ~176k mappings
  },

  maps: {
    conceptToLemmas: {
      "concept_1234": ["lemma_879", ...]
    },
    genreToWorks: {
      "genre_123": ["work_001", ...]
    },
    genreHierarchy: {
      "genre_123": ["Prosa", "Mystik"]
    }
  }
}
```

**Key features:**
- Normalized searchable text for all entities (MHG character conversion: â→a, ô→o, ü→ue)
- Performance maps pre-computed (conceptToLemmas, genreToWorks, genreHierarchy)
- Variants dictionary enables O(1) orthographic variant lookup
- v1.1.0 added separate GND/Wikidata identifiers for works vs authors

### Corpus Index

**File:** `data/corpus-index.json.gz`
**Size:** ~21 MB compressed
**Version:** 4.0.0

**Schema:**
```javascript
{
  version: "4.0.0",
  generatedAt: "ISO-8601 timestamp",

  texts: [{
    textId: "ABG",
    title: "Von der Abgeschiedenheit",
    author: "Meister Eckhart",
    authorRef: "person_445",
    workRef: "work_001",
    words: [{
      lemmaId: "lemma_879",
      lemma: "brôt",
      form: "brott",          // orthographic form in text
      position: 0             // document-level word position
    }],
    wordCount: 1234
  }]
}
```

**Key features (v4.0.0):**
- Document-level word indexing (removed paragraph-based indexing)
- Position = sequential word number (0, 1, 2, ...)
- Only words with `@lemmaRef` are indexed
- 100% word coverage from TEI `<body>` elements
- Supports accurate proximity search

**Why v4.0.0?** Removed paragraph-based indexing due to position misalignment between Python extraction and JavaScript parsing. Document-level indexing is simpler and more accurate.

## Data Processing Pipeline

### Build Scripts

**Location:** `scripts/` directory
**Language:** Python 3.13+ with lxml

Four core build scripts:

1. **`build-authority-index.py`** - Extract authority data from 7 XML files
   - Parse XML with lxml
   - Extract structured data for each entity type
   - Build performance maps (conceptToLemmas, genreToWorks, genreHierarchy)
   - Normalize searchable text
   - Output: `data/authority-index.json.gz`

2. **`build-corpus-index.py`** - Extract word positions from TEI files
   - Scan `tei/` directory for all `.tei.xml` files
   - Extract metadata and words with `//tei:body//tei:w[@lemmaRef]`
   - Build words array with sequential positions
   - Output: `data/corpus-index.json.gz`

3. **`extract-variants.py`** - Generate variants.xml from corpus
   - Scan all TEI files
   - Extract `<w lemmaRef="..." wordRef="...">` elements
   - Group by lemma ID and collect unique orthographic forms
   - Output: `authority-files/variants.xml`

4. **`validate-indices.py`** - Integrity checks
   - Validate unique IDs
   - Check cross-references
   - Verify data quality

### Data Wrangling Scripts

**Location:** `scripts/data-wrangling/`

Scripts for enriching authority files with external data:

1. **`enhance_works_with_zotero.py`** - Sync Zotero bibliographic data
   - Fetch from Zotero API (group 5043625, collection 7JU362QV)
   - Extract ALL fields: title, edition, volume, issue, series, seriesNumber, authors, editors, place, publisher, date, pages, ISBN, notes
   - Transform titles to German Title Case (capitalize words except articles/prepositions)
   - Update works.xml with complete biblStruct elements
   - Three modes: live API, cache, offline

2. **`sync_tei_headers.py`** - Propagate authority metadata to TEI headers
   - Read authority file changes (works.xml, persons.xml)
   - Update corresponding TEI file headers
   - Maintain intentional redundancy for accessibility

3. **`test_zotero_extraction.py`** - Validation tests
   - Compare Zotero data with generated biblStruct
   - Verify complete field extraction
   - Ensure data integrity

**Title Case Transformation:** Zotero stores titles in sentence case, but German bibliographic style requires Title Case. The script converts automatically:
- Capitalizes first word and words after colons
- Keeps German articles/prepositions lowercase (der, die, von, und, etc.)
- Capitalizes all other words
- Example: "Das stadtratsgedicht heinrichs von rang" → "Das Stadtratsgedicht Heinrichs von Rang"

### Browser Loading Pipeline

**Component:** `lib/corpus-loader.js`

**Process:**
1. Check IndexedDB cache (30-day expiration for indices)
2. If expired or missing, fetch compressed index
3. Decompress with Pako (gzip)
4. Parse JSON
5. Store in IndexedDB with expiration timestamp
6. Populate runtime data structures

**Cache strategy:**
- Authority index: 30-day expiration (reference data)
- Corpus index: 30-day expiration (corpus data)
- TEI files: No expiration (user content)

## Data Relationships

### 3-Stage Lemma Resolution

The project uses a sophisticated 3-stage resolution process for handling orthographic variants:

**Stage 1: Exact Match in Lexicon**
- Search canonical forms (e.g., "brôt")
- Uses normalized comparison

**Stage 2: Variants Dictionary Lookup**
- Search variants index with ~176k attested orthographic forms
- Maps variants to canonical lemmas (e.g., "brott" → lemma_879)
- O(1) lookup via flat dictionary

**Stage 3: Partial Match Fallback**
- Uses `includes()` search on lexicon
- Catches fuzzy matches

**Why 3 stages?** Historical spelling variations in Middle High German are extensive. Variants dictionary captures actual corpus attestations, while fallback handles edge cases.

### Cross-Reference Integrity

All cross-references validated during build:
- Work `authorRef` points to existing person
- Lemma `conceptIds` point to existing concepts
- Word `lemmaRef` points to existing lemma
- Work `genres` point to existing genre IDs

### Performance Maps

Three pre-computed maps accelerate common queries:

**conceptToLemmas:** Find all lemmata for a concept
- Avoids scanning entire lexicon
- Used in concept explorer

**genreToWorks:** Find all works in a genre
- Avoids scanning entire works list
- Used in genre explorer

**genreHierarchy:** Get parent genres for a genre
- Extracted from `<ptr type="broader">` references
- Fixed in v1.1.0 (was broken before)

## Data Quality

### Known Issues

**Missing Identifiers:**
- Some works lack GND identifiers (historical: not all works have entries)
- Some persons lack Wikidata IDs (newer addition, ongoing enhancement)

**TEI Encoding:**
- Punctuation sometimes encoded as entities (`&lt;`, `&gt;` in `<seg type="pc">`)
- This is correct XML encoding, not a bug

**Genre Hierarchy:**
- Fixed in v1.1.0 to use `<ptr type="broader">` references
- Previously extracted nested categories (incorrect approach)

### Validation

Build scripts perform integrity checks:
- Unique IDs across all entities
- Valid cross-references (no dangling references)
- No empty required fields
- Normalized text matches expected format

### Maintenance

**When to rebuild authority index:**
- Authority XML files modified
- Cross-references added/changed
- New GND/Wikidata identifiers added

**When to rebuild corpus index:**
- TEI files added/removed/modified
- Word annotations changed

**When to regenerate variants:**
- TEI corpus modified (new orthographic forms)
- Usually paired with corpus index rebuild

**Rebuild workflow:**
```bash
python scripts/extract-variants.py
python scripts/build-authority-index.py
python scripts/build-corpus-index.py
python scripts/validate-indices.py
```

**Cache invalidation:**
- Increment version number in build script
- Browser checks version and refetches if mismatch

---

For technical implementation, see [ARCHITECTURE.MD](ARCHITECTURE.MD).
For architecture decisions, see [DECISIONS.MD](DECISIONS.MD).
