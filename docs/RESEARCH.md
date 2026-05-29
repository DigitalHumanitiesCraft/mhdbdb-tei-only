# Research

This document describes the academic context, standards, and methodological background for the MHDBDB TEI Repository.

## Project Context

### MHDBDB Salzburg

This MHDBDB TEI Repository is a **standalone, active project** that originated from the University of Salzburg's Mittelhochdeutsche Begriffsdatenbank (MHDBDB), a research project at the University of Salzburg's Department of German Studies. The Salzburg MHDBDB created the original semantic taxonomy and controlled vocabularies for Middle High German philology.

**Project Goals (inherited from the Salzburg MHDBDB):**
- Create comprehensive semantic annotations for MHG texts
- Establish controlled vocabularies for concepts, genres, persons, works
- Enable corpus linguistic analysis of medieval German literature
- Support research in historical semantics and concept history

**Historical relationship:** The initial corpus and authority data were exported from Salzburg's RDF-based MHDBDB (three-stage: RDF → CSV snapshots → TEI-XML) and migrated into this repository, completed 2025-07-22. **Since that migration (2025-07-22), this repository is the independent, sole master** — all data is maintained here; there are no ongoing re-exports or syncs with Salzburg. It is now an active project with continuing ingest (WZB/Wenzelsbibel, ARITHMETIC) and manual editorial correction, not a static export. See [INDEX.md → Current Phase](INDEX.md#current-phase) and [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules).

**Original data source (historical):** https://www.mhdbdb.sbg.ac.at

### TEI Encoding

This repository represents the corpus in TEI P5 format, combining traditional philological scholarship with digital humanities methods. All texts and authority files follow TEI guidelines with project-specific extensions for semantic markup.

## Standards & Technologies

### TEI P5 (Text Encoding Initiative)

**Standard:** https://www.tei-c.org/release/doc/tei-p5-doc/en/html/

TEI P5 provides the foundational markup structure for all texts and authority files in the project.

**Key TEI elements used:**
- `<teiHeader>` - Bibliographic metadata
- `<text><body>` - Main content
- `<w>` - Word tokens with `@lemmaRef`, `@ana`, and `@corresp` attributes
- `<person>`, `<work>`, `<entry>` - Authority file entities
- `<listRelation>` - Semantic relationships

**TEI namespace:** `http://www.tei-c.org/ns/1.0`

**Project-specific extensions:**
- Cross-references via `xml:id` and `@ref` attributes
- Semantic annotations via `@ana` attributes linking to concepts
- Custom authority file schemas for persons, works, lexicon, concepts, genres, names

### Middle High German (MHG)

**Time period:** Approximately 1050-1350 CE
**Geographic area:** German-speaking regions of medieval Europe

**Linguistic characteristics:**
- Long vowels marked with macron or circumflex (â, ê, î, ô, û)
- Umlauts (ä, ö, ü)
- Extensive orthographic variation (no standardized spelling)
- Historical phonological changes from Old High German

**Normalization challenges:**
- Modern databases require consistent search behavior
- Historical texts show extensive spelling variations
- Same word may appear in dozens of orthographic forms
- Solution: Dual normalization strategy (character normalization + variants dictionary)

### Cross-Reference Patterns

**GND (Gemeinsame Normdatei):** German authority file system
- Persistent identifiers for persons, works, concepts
- Maintained by German National Library
- Enables interoperability with other German cultural heritage projects
- URL pattern: `https://d-nb.info/gnd/{identifier}`

**Wikidata:** Linked open data knowledge base
- Multilingual identifiers for entities
- Rich metadata and relationships
- Used for automatic image fetching in reading view
- URL pattern: `https://www.wikidata.org/wiki/{identifier}`

**Project implementation:**
- Separate GND/Wikidata identifiers for works vs authors (v1.1.0)
- Enables precise entity referencing
- Supports future LOD (Linked Open Data) integration

## Research Questions

This corpus enables research across multiple disciplines:

### Medieval German Philology
- Lexical studies (word frequencies, semantic fields)
- Concept history (how meanings change over time)
- Author attribution (stylometric analysis)
- Genre classification and characteristics
- Work-to-work relationships (intertextuality)

### Corpus Linguistics
- Co-occurrence patterns (which words appear together)
- Collocation analysis (word associations)
- Semantic networks (concept relationships)
- Prosopography (biographical analysis of historical persons)

### Digital Humanities Methods
- Distant reading (macroanalysis of large corpora)
- Network analysis (visualizing relationships)
- Temporal analysis (tracking changes across time)
- Comparative analysis (across authors, genres, periods)

## Methodological Approaches

### Semantic Annotation

The project uses concept-based semantic annotation:
- Each word linked to dictionary lemma
- Lemmata linked to semantic concepts
- Concepts organized in hierarchical taxonomy

**Example:**
```
Word: "brott" (orthographic form)
  → Lemma: "brôt" (canonical form)
  → Concept: "Nahrung" (Food)
  → Broader concept: "Lebensnotwendigkeiten" (Necessities of life)
```

This multi-level structure enables both specific and general queries.

### Controlled Vocabularies

Seven authority files provide controlled vocabularies:
- **Persons:** Authors and historical figures with GND/Wikidata IDs
- **Works:** Bibliographic metadata with manuscript information
- **Lexicon:** Dictionary with grammatical and semantic information
- **Concepts:** Semantic taxonomy (German/English terms)
- **Genres:** Literary classification system
- **Names:** Proper names with semantic relations
- **Variants:** Orthographic variants extracted from corpus

These vocabularies ensure consistency and enable sophisticated cross-referencing. An 8th authority file, **`contributors.xml`**, was added in 2026-04 to register the MHDBDB team (founders, coordinator, lead-editors, editors) for structured editor-attribution in the TEI headers — it is project-internal and deliberately not part of the searchable corpus index.

### Distant Reading

The project supports distant reading methods:
- Search across entire corpus (hundreds of texts)
- Identify patterns not visible in close reading
- Quantitative analysis of qualitative data
- Complement traditional philological approaches

**Enabled analyses:**
- Word frequency across corpus
- Co-occurrence patterns (proximity search)
- Distribution across genres/authors/periods
- Semantic field analysis

### Text Normalization Strategy

Dual normalization handles MHG orthographic variation:

**1. Character normalization:**
- Converts MHG diacritics to base forms (â→a, ô→o)
- Enables consistent matching across keyboard inputs
- Applied to all search queries and indexed data

**2. Variants dictionary:**
- Maps attested orthographic forms to canonical lemmata
- Extracted from corpus (corpus-driven, not prescriptive)
- Covers historical spelling variations

**Rationale:** Character normalization handles systematic variations, variants dictionary handles historical spelling differences. Both required for comprehensive search coverage.

## Limitations & Future Directions

### Current Limitations

**Corpus scope:**
- Limited to pre-encoded texts (no dynamic addition)
- Desktop-only interface (not mobile-optimized)
- Static corpus (requires rebuild for updates)

**Technical constraints:**
- Client-only architecture (all processing in browser)
- Large initial download (~37 MB indexes: 3 MB authority + 34 MB corpus, gzipped)
- Limited to browser memory

**Methodological:**
- Semantic annotations reflect project-specific taxonomy
- Not all texts have complete semantic markup
- Some concepts have limited lemma coverage

### Future Research Directions

**Corpus expansion:**
- Add more texts from medieval German tradition
- Include additional text types (letters, documents, etc.)
- Extend temporal range (Early New High German)

**Enhanced functionality:**
- API for programmatic access
- Advanced visualizations (network graphs, timelines)
- Collaborative annotation features
- Mobile-optimized interface

**Methodological development:**
- Machine learning for automatic annotation
- Integration with other medieval corpora
- Cross-linguistic comparison (Latin, other vernaculars)
- Temporal analysis tools

### Ethical Considerations

**Cultural heritage:**
- Texts represent cultural heritage of German-speaking regions
- Responsible presentation of medieval content
- Attribution to original scholars and digitizers

**Open access:**
- Free access to corpus and tools
- CC BY-NC-SA license enables reuse
- Commitment to open digital humanities

**Sustainability:**
- TEI encoding ensures long-term preservation
- Static site architecture reduces maintenance burden
- GitHub hosting provides institutional backup

---

For data structures, see [DATA-MODEL.md](DATA-MODEL.md).
For technical implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
For user-facing features, see [FEATURES.md](FEATURES.md).
