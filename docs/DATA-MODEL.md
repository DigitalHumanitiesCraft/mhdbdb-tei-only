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
- Word elements (`<w>`) with `@lemmaRef`, `@ana`, and `@corresp` attributes

**Cross-reference pattern:**
```xml
<w lemmaRef="#lemma_879">brott</w>
```

### Authority Files

**Location:** `authority-files/` directory
**Format:** TEI P5 XML with custom MHDBDB schema

Eight authority files — seven inhaltstragende controlled vocabularies (in the corpus index) plus one projekt-interner Mitwirkenden-Register:

- `persons.xml` - Authors and historical persons
- `works.xml` - Work and manuscript metadata
- `lexicon.xml` - Dictionary with tens of thousands of lemmata
- `concepts.xml` - Semantic concept taxonomy
- `genres.xml` - Literary genre classification
- `names.xml` - Proper names with semantic relations
- `variants.xml` - Orthographic variants extracted from corpus
- `contributors.xml` - MHDBDB-Team register (Gründer, Koordination, Editor:innen); **nicht** im Corpus-Index, sondern projekt-interne Authority-Quelle für die Editor-Attribution in den TEI-Headern (see `docs/TEI-MODEL-AUTH-FILES.md §3.8` and `docs/TEI-MODEL.md §2.1bis`)

**Cross-reference patterns:**
- Person ↔ Work via `xml:id` and `@ref`
- Lemma → Concept via `<ptr target="concepts.xml#...">`
- Work → Genre via `<ptr target="genres.xml#..."/>`
- Orthographic variant → Lemma via `@corresp="lexicon.xml#..."`
- Corpus header → Mitwirkende via `<persName ref="contributors.xml#contrib_NNN">` and `<orgName ref="contributors.xml#mhdbdb-team">`

### Authority File XML Schemas

All files use namespace `xmlns="http://www.tei-c.org/ns/1.0"`.

#### lexicon.xml (~33 MB, ~43,750 entries)

```xml
<TEI><text><body><div type="lexicon">
  <entry xml:id="lemma_{n}">
    <form type="lemma"><orth>{lemma text}</orth></form>
    <gramGrp>
      <pos>{POS tag}</pos>+              <!-- NUM, NOM, VRB, ADJ, ADV, PRP, NAM, ... -->
    </gramGrp>
    <etym type="morphological">?          <!-- optional: morphological decomposition -->
      <seg type="component" corresp="lexicon.xml#lemma_{n}">{text}</seg>+
    </etym>
    <sense xml:id="lemma_{n}_sense_{m}" ana="#type_{id} ...">+
      <ptr target="concepts.xml#concept_{id}"/>*
    </sense>
  </entry>+
</div></body></text></TEI>
```

Notes: Multiple `<pos>` per entry possible. Multiple `<sense>` per entry (verb entries often have 2+). `@ana` contains space-separated semantic type references.

#### persons.xml (~74 KB)

```xml
<TEI><text><body><listPerson>
  <person xml:id="person_{n}">
    <persName type="preferred">{canonical name}</persName>
    <persName type="alternative" xml:lang="{de|en}">?{alt name}</persName>*
    <idno type="GND">?{gnd-id}</idno>
    <idno type="wikidata">?{Q-id}</idno>
    <!-- No works list: person→work derived from works.xml <author @ref> at build time -->
  </person>+
</listPerson></body></text></TEI>
```

Notes: IDs are numeric (`person_N`) except `person_anonym`. GND and Wikidata are optional.

#### works.xml (~1.4 MB)

```xml
<TEI><text><body><listBibl>
  <bibl xml:id="work_{n}">
    <title xml:lang="de">{title}</title>
    <title xml:lang="de" type="alternate">?{alt title}</title>*
    <idno type="sigle">{sigle}</idno>+      <!-- one or more sigles per work -->
    <idno type="GND">?{gnd-url-or-id}</idno>
    <idno type="wikidata">?{wikidata-url-or-id}</idno>
    <idno type="handschriftencensus">?{url}</idno>
    <ptr target="genres.xml#genre_{hash}"/>*  <!-- genre label resolved from genres.xml -->
    <author ref="persons.xml#person_{id}">{name}</author>
    <relatedItem>
      <biblStruct type="{journalArticle|bookSection|book}" xml:id="{sigle}_{sigle}"
                  corresp="{zotero-url}" key="{sigle}">*
        <analytic>?                           <!-- present for articles/chapters -->
          <title level="a">{article title}</title>
          <author><name>{name}</name></author>
        </analytic>
        <monogr>                              <!-- always present -->
          <title level="m">{book/journal title}</title>
        <idno type="callNumber">?{sigle}</idno>
        <editor>?<forename>{first}</forename><surname>{last}</surname></editor>
        <imprint>
          <pubPlace>?{place}</pubPlace>
          <publisher>?{publisher}</publisher>
          <date>?{year}</date>
          <biblScope unit="page">?{pages}</biblScope>
        </imprint>
      </monogr>
        <series>?<title level="s">{series title}</title></series>
      </biblStruct>
    </relatedItem>
    <bibl type="digitalIntermediary" corresp="{url}">?  <!-- provenance (Issue #36-40) -->
      <title>{provider name}</title>
      <respStmt><name>{person}</name><resp>{role}</resp></respStmt>
      <ref target="{source url}"/>
      <note type="provenance">{description}</note>
    </bibl>
  </bibl>+
</listBibl></body></text></TEI>
```

Notes: Multiple sigles per work (editions). GND/Wikidata may be full URLs or bare IDs — build script extracts ID portion. Genre `<ref>` elements come in de/en pairs, plus optional parent hierarchy refs.

#### concepts.xml, genres.xml, names.xml (shared pattern)

```xml
<TEI><teiHeader>...<encodingDesc><classDecl>
  <taxonomy xml:id="mhdbdb-{concepts|genres|names}">
    <category xml:id="{type}_{id}">
      <catDesc>
        <term xml:lang="de">{German term}</term>
        <term xml:lang="en">{English term}</term>
        <term type="alternative" xml:lang="{de|en}">?{synonym}</term>*
        <ptr type="broader" target="#{type}_{parent_id}"/>*
      </catDesc>
    </category>+
  </taxonomy>
</classDecl></encodingDesc></teiHeader></TEI>
```

| File | ID format | Extra `<ptr>` types |
|------|-----------|-------------------|
| concepts.xml | `concept_{numeric}` | — |
| genres.xml | `genre_{hex}` | — (but many broader pointers, polyhierarchical) |
| names.xml | `name_{numeric}` | `exactMatch`, `closeMatch` → `concepts.xml#...` |

#### variants.xml (~13 MB, ~176k variant forms)

```xml
<TEI><text><body><div type="orthographicVariants">
  <entry corresp="lexicon.xml#lemma_{n}">
    <form xml:id="type_{m}">{variant text}</form>+
  </entry>+
</div></body></text></TEI>
```

Notes: Flat list of variants grouped by lemma cross-reference. Forms preserve MHG diacritics. One entry per lexicon lemma; multiple forms per entry.

## Pre-Built Index Architecture

The project uses pre-built JSON indexes to avoid runtime XML parsing.

### Authority Index

**File:** `data/authority-index.json.gz`
**Size:** ~3 MB compressed
**Version:** Aktueller Stand in [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung). Quelle im Code: `AUTHORITY_INDEX_VERSION` in `assets/js/lib/corpus-loader.js` und `'version'` in `scripts/build-authority-index.py`.

**Schema (illustrativ — konkrete Version siehe Tabelle in TEI-MODEL.md §11):**
```javascript
{
  version: "1.x.x",
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
    etymology: [{text: "brot", lemmaRef: "lemma_7779"}],
    senses: [{
      id: "lemma_879_sense_1",
      conceptIds: ["concept_1234"]
    }],
    normalized: "brot"
  }],

  concepts: [{
    id: "concept_1234",
    termDE: "Nahrung",
    termEN: "Food",
    broader: "concept_5678",
    narrower: ["concept_9012"],
    normalized: "...",
    altDE: ["Speise", "Essen"],        // optional, only if <term type="alternative" xml:lang="de"> exists
    altEN: ["Sustenance"],              // optional, only if <term type="alternative" xml:lang="en"> exists
    altNormalized: ["speise", "essen"]  // optional, only if altDE exists (normalized via normalizeMHG)
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
**Size:** ~40 MB compressed (v4.1.x; war ~34 MB in v4.0.1)
**Version:** Aktueller Stand in [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung). Quelle im Code: `INDEX_VERSION` in `assets/js/lib/corpus-loader.js` und `'version'` in `scripts/build-corpus-index.py` (dort steht auch der Versions-Historien-Kommentar). MAJOR/MINOR/PATCH-Semantik siehe unten.

**Schema (illustrativ — konkrete Version siehe Tabelle in TEI-MODEL.md §11):**
```javascript
{
  version: "4.x.x",
  generatedAt: "ISO-8601 timestamp",
  totalTexts: 667,
  totalLemmata: 42630,

  texts: [{
    id: "ABG",                       // sigle (primary identifier, used in URLs)
    filename: "ABG.tei.xml",
    title: "Von der Abgeschiedenheit",
    author: "Meister Eckhart",
    authorRef: "person_445",
    workRef: "work_001",
    genre: "Mystik",
    wordCount: 2955,                 // total tokens (all <w> elements)
    words: ["lemma_879", ...],       // lemma IDs in document order; index = position
    lemmata: {                       // reverse map per text: lemma → positions
      "lemma_879": [0, 12, 47],
      "lemma_881": [3, 9]
    },
    lineStarts: [0, 8, 15, ...],     // word-index where each <l> starts (#47.3)
    lineEnds:   [7, 14, 22, ...]     // word-index where each <l> ends (inclusive)
  }],

  lemmaIndex: {                      // global reverse index: lemma → text sigles
    "lemma_879": ["ABG", "NBB", "PZ"],
    "lemma_881": ["NBB"]
  }
}
```

**Key features (v4.1.x):**
- Document-level word indexing (removed paragraph-based indexing in 4.0.0)
- `words[i]` = lemma ID at position `i` (sequential, 0-indexed)
- Only words with `@lemmaRef` are indexed
- `lemmata` is the per-text reverse index (lemma → positions), enables O(1) lookup of "where does lemma X appear in text Y"
- `lemmaIndex` is the global reverse index (lemma → list of text sigles), enables fast "which texts contain lemma X" queries
- `lineStarts[]` / `lineEnds[]` (seit 4.1.0): pro Text die Word-Indizes der `<l>`-Boundaries. Gleiche Länge wie die Anzahl `<l>` mit mindestens einem indizierten Wort. Empty arrays für Prosa-Texte ohne `<l>` (64/667 ≈ 10 % des Korpus). Enables „Lemma am Versanfang/Versende"-Lookups in O(L) statt O(W).
- 100% word coverage from TEI `<body>` elements (Wörter außerhalb von `<l>` wie `<head>`, `<note>`, `<fw>` zählen in `words[]`, aber matchen keine Vers-Boundary)
- Supports accurate proximity search + Versposition-Filter

**Why v4.0.0?** Removed paragraph-based indexing due to position misalignment between Python extraction and JavaScript parsing. Document-level indexing is simpler and more accurate.

**Why v4.0.1?** WZB (Wenzelsbibel) ingested into the corpus after Phase-2 POS coverage reached 95.5% (Issue #34).

**Why v4.1.0?** Per-Text `lineStarts[]` / `lineEnds[]` für #47.3 Lemmasuche nach Versposition. 1.359.789 `<l>`-Elemente über 603 Versdichtungs-Texte. Bumped `Schema-feature-add` (MINOR), nicht nur `data-add` (PATCH). Index-Größe +6 MB gz (34 → 40 MB).

**Why v4.1.1?** Korpus-Rebuild nach Stanza-Insertion-Sweep (#23) — etwa 90 Texte bekamen `<lg type="stanza">`-Wrapper, was die `lineStarts`/`lineEnds`-Werte für diese Texte ändert; keine Schema-Änderung, daher PATCH.

**Field name note:** the primary identifier is `id` (sigle), not `textId`. Older docs and some code paths may use `textId` — the canonical field in the index JSON is `id`.

**Versions-Sync (kritisch):** der Index-Versions-String muss synchron mit `INDEX_VERSION` in `assets/js/lib/corpus-loader.js` und der `'version'`-Konstante in `scripts/build-corpus-index.py` gehalten werden. Sonst greift die Cache-Invalidate-Logik nicht (siehe `docs/CONTRACTS.md` §IndexedDB). CI-Garantie via `.github/workflows/index-version-check.yml`; lokal `python scripts/audit/check-index-versions.py` vor Commit.

## Data Processing Pipeline

### Build Scripts

**Location:** `scripts/` directory
**Language:** Python 3.13+ with lxml

Three core build scripts:

1. **`build-authority-index.py`** - Extract authority data from 7 inhaltstragende XML files (the 8th, `contributors.xml`, is deliberately not indexed — see below)
   - Parse XML with lxml
   - Extract structured data for each entity type
   - Build performance maps (conceptToLemmas, genreToWorks, genreHierarchy)
   - Normalize searchable text
   - Variants dictionary built from `authority-files/variants.xml` (see *Variants regeneration* below)
   - Output: `data/authority-index.json.gz`

2. **`build-corpus-index.py`** - Extract word positions from TEI files
   - Scan `tei/` directory for all `.tei.xml` files
   - Extract metadata and words with `//tei:body//tei:w[@lemmaRef]`
   - Build words array with sequential positions
   - Output: `data/corpus-index.json.gz`

3. **`validate-indices.py`** - Integrity checks
   - Validate unique IDs
   - Check cross-references
   - Verify data quality

**Variants regeneration:** `authority-files/variants.xml` is consumed by `build-authority-index.py` but is itself **derived from the corpus** (one `<form xml:id="type_N">` per orthographic variant, grouped under the lemma it attests). Regenerate it with `python scripts/sync/extract-variants.py --apply` (reads current `@lemmaRef` + `@corresp`; xml:id uniqueness by majority vote) whenever the corpus gains new orthographic forms, then rebuild the authority index and bump its version. *Historical note:* the original extractor lived only on the archived `initial-data-wrangling` branch and read the pre-#32 `@wordRef`, so the file silently drifted by 64,287 forms until the maintained generator was added and `variants.xml` regenerated on 2026-05-29 (192,472 → 256,759 forms; #44/#115).

### Build Script XPath Reference

| Script | Source File | XPath | Extracts |
|--------|-----------|-------|----------|
| `build-authority-index.py` | lexicon.xml | `//tei:entry` | All lemma entries |
| | | `.//tei:form[@type="lemma"]/tei:orth` | Lemma text |
| | | `.//tei:pos` | Part(s) of speech |
| | | `.//tei:etym[@type="morphological"]//tei:seg[@type="component"]` | Etymology components + `@corresp` |
| | | `.//tei:sense` | Senses (with `@xml:id`, `@ana`) |
| | | `.//tei:sense//tei:ptr[contains(@target,"concepts.xml#")]` | Concept pointers per sense |
| | persons.xml | `//tei:person` | Person records |
| | | `.//tei:persName[@type="preferred"]` | Canonical name |
| | | `.//tei:idno[@type="GND"]` | GND identifier |
| | | `.//tei:idno[@type="wikidata"]` | Wikidata ID |
| | | (derived from works.xml `<author @ref>`) | Work IDs (built at index time) |
| | works.xml | `//tei:bibl` (children of `listBibl`) | Work records |
| | | `./tei:title` | All titles (with `@xml:lang`, `@type`) |
| | | `.//tei:idno[@type="sigle"]` | Sigles (may be multiple) |
| | | `.//tei:idno[@type="GND"]` | Work GND (extract ID from URL: strip `https://d-nb.info/gnd/`) |
| | | `.//tei:idno[@type="wikidata"]` | Work Wikidata (extract Q-ID from URL: strip `https://www.wikidata.org/entity/`) |
| | | `.//tei:idno[@type="handschriftencensus"]` | Handschriftencensus URL |
| | | `./tei:ptr[contains(@target,"genres.xml#")]` | Genre pointers (label from genres.xml lookup) |
| | | `./tei:author` | Author name + `@ref` → person ID |
| | | `.//tei:biblStruct` | Bibliography entries (with `@type`, `@key`, `@corresp`) |
| | concepts.xml | `//tei:category` (filter ID starts with `concept_`) | Concept entries |
| | genres.xml | `//tei:category` (filter ID starts with `genre_`) | Genre entries |
| | names.xml | `//tei:category` (filter ID starts with `name_`) | Name entries |
| | (all three) | `.//tei:catDesc//tei:term` (filter `@xml:lang`) | DE/EN labels |
| | genres.xml | `.//tei:catDesc/tei:ptr[@type="broader"]` | Genre hierarchy |
| | names.xml | `.//tei:ptr[contains(@target,"concepts.xml#")]` | Concept cross-references |
| | variants.xml | `//tei:entry` or `//entry` (handles both namespaced/non-namespaced) | Variant groups |
| | | `.//tei:form` or `.//form` | Orthographic forms per lemma |
| `build-corpus-index.py` | tei/*.tei.xml | `//tei:idno[@type="sigle"]/text()` | Sigle (fallback: filename without `.tei.xml`) |
| | | `//tei:titleStmt/tei:title/text()` | Title |
| | | `//tei:titleStmt/tei:author` | Author name + `@ref` |
| | | `//tei:msIdentifier` | `@corresp` → work reference |
| | | `//tei:body//tei:w[@lemmaRef]` | All words with positions (see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)) |

#### Namespace Handling

Build scripts use `get_namespaces()` which handles TEI documents with or without explicit namespace prefix:

1. Read document's `nsmap`
2. If `None` key exists (default namespace), remap to `'tei'` prefix
3. Fallback: set `'tei'` = `'http://www.tei-c.org/ns/1.0'`

Source: `scripts/build-authority-index.py:50-67`

#### Variant Dictionary Deduplication

When building the variants map, **first occurrence wins** — if two lemmata claim the same normalized variant form, only the first is stored. No collision detection or warning. Source: `build-authority-index.py:526-571`.

### Data Wrangling Scripts

**Location:** `scripts/sync/` (ongoing sync) and `scripts/audit/` (validation)

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

**Component:** `assets/js/lib/corpus-loader.js`

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

Search resolves user input to lemma IDs through 3 stages with early return:

| Stage | Method | Return | Performance |
|-------|--------|--------|-------------|
| 1 | Exact match on normalized canonical form | 0..N (homographs) | O(n) scan |
| 2 | Variants dictionary lookup (~176k mappings) | Exactly 1 | O(1) hash |
| 3 | Bidirectional substring fallback | 0..N (fuzzy) | O(n) scan |

Stages are mutually exclusive — first match wins. **Full pseudocode with worked example:** see [CONTRACTS.md](CONTRACTS.md#c-3-stage-lemma-resolution-algorithm)

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
- Punctuation sometimes encoded as entities (`&lt;`, `&gt;` in `<pc>`)
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
python scripts/sync/extract-variants.py --apply   # variants.xml aus Korpus regenerieren (#44/#115)
python scripts/build-authority-index.py
python scripts/build-corpus-index.py
python scripts/validate-indices.py
```

**Cache invalidation:**
- Increment version number in build script
- Browser checks version and refetches if mismatch

---

## Data-Change-Lifecycle

> Das Projekt ist ein **aktives Projekt mit laufendem Ingest** (siehe [INDEX.md → Current Phase](INDEX.md#current-phase)). Der Reader liest TEI live (`tei/<SIG>.tei.xml`) und zeigt Edits sofort, ABER Suche, Lemma-Zähler und alle Index-Features werden aus den vor-gebauten `data/*.json.gz` bedient. Eine Daten-Änderung ist erst „live", wenn die abgeleitete Schicht neu gebaut, versioniert und committet ist. Diese Checklisten sind die verbindliche Schrittfolge; sie ersetzen die früher über mehrere Docs verstreuten Rebuild-Hinweise.

Status-Legende: **CI** = automatisiert (GitHub Actions) · **Skript** = Skript-eingebauter Guard · **manuell** = dokumentiert, nicht erzwungen.

### Wenn sich `tei/` ändert (neuer Text oder Annotations-Edit)

| # | Schritt | Bricht wenn vergessen | Status |
|---|---------|----------------------|--------|
| 1 | UTF-8, Namespace `http://www.tei-c.org/ns/1.0`; positionstragende Annotation auf `<w @lemmaRef>` (nur die zählen für Positionen) | Wort unsichtbar für Suche, falsche Highlight-Positionen | manuell |
| 2 | Schema: `python scripts/audit/validate-corpus.py --sample <SIG>` | invalides TEI; `schema-validation.yml` fängt es auf PR/Push | CI |
| 3 | Korpus-Index: `python scripts/build-corpus-index.py` (Pre-flight bricht bei dirty tree ab, sonst `--allow-dirty`) | Suche, Trefferzahlen, Proximity, Versposition, Playground-Analysen stale; neuer Text fehlt komplett | manuell |
| 4 | **Bei neuen Formen:** `python scripts/sync/extract-variants.py --apply` (`variants.xml` ist korpus-abgeleitet) | neue Wortformen lösen sich nicht zum Lemma auf (Stage-2-Resolution); Lemma-Page-Chips unvollständig | manuell |
| 5 | Nach Schritt 4: `python scripts/build-authority-index.py` | Variant-Map im Index bleibt stale | manuell |
| 6 | Version bumpen (`build-*-index.py` Dict-Literal `'version'` + `corpus-loader.js`), dann `python scripts/audit/check-index-versions.py` | wiederkehrende Nutzer behalten den 30-Tage-IndexedDB-Cache mit altem Index (#47.3/#94) | CI (Konsistenz) |
| 7 | Cross-Ref-Audit: `python scripts/audit/check-authority-cross-refs.py --check` | dangling Refs (Lemma/Variant not found, leere Panels) | CI (in `schema-validation.yml`) |
| 8 | `python scripts/validate-indices.py` + `npm test` (**User vorher fragen**) | strukturelle Index-/Frontend-Regression | manuell |
| 9 | Commit **TEI + gebautes `data/*.json.gz` + Bumps zusammen**, Files by name stagen (nie `git add -A`, shared working dir) | Production serviert stale Suche bzw. alten Cache | manuell |
| 10 | Push zu main → GitHub Pages deployt statisch (~2-5 min, kein Pages-Build) | erreicht Production nie; was committet ist, ist was shippt | CI (Auto-Deploy) |

### Wenn sich `authority-files/` ändert

| # | Schritt | Bricht wenn vergessen | Status |
|---|---------|----------------------|--------|
| 1 | (nur `works.xml`) `enhance_works_with_zotero.py` + `sync_tei_headers.py --works` (erst `--dry-run`) | Editor/Bibliografie + Header stale (nur WorksSyncer implementiert, Persons/Genres/Concepts sind TODO-Stubs) | manuell |
| 2 | **Authority-Index: `python scripts/build-authority-index.py`** (Frontend liest NUR den Index, nie das XML) | jede Authority-Änderung unsichtbar bis Rebuild + Commit (so blieb die lexicon/variants-Drift unbemerkt) | manuell |
| 3 | Version bumpen (`build-authority-index.py` + `corpus-loader.js`) + `check-index-versions.py` | stale Cache bis 30 Tage | CI (Konsistenz) |
| 4 | Cross-Ref-Audit `--check` + Schema `validate-corpus.py --fail-fast` | dangling Refs / invalides XML | CI |
| 5 | Gebautes `data/authority-index.json.gz` + Bumps committen, by name | Production serviert alten Index | manuell |

**Entkopplung:** Eine reine `authority-files/`-Änderung braucht **keinen** Korpus-Index-Rebuild (`build-corpus-index.py` liest `authority-files/` nicht). Eine reine `tei/`-Änderung braucht den Authority-Rebuild nur, wenn neue Formen eine `variants.xml`-Regenerierung erzwingen (Schritt 4 → 5).

**Offene Lücke (kein Trigger):** `lexicon.xml`-Backfill für ingest-erzeugte Lemma/Sense-IDs (977 dangling Refs, 349 IDs, repo-intern, #44/#115). Bis dahin ist `lexicon.xml` in der Cross-Ref-CI-Baseline ausgenommen (nur Refs außerhalb `lexicon.xml` brechen den Build).

---

For technical implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
