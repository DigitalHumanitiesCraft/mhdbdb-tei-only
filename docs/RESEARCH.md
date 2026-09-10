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

**Historical relationship:** The initial corpus and authority data were exported from Salzburg's RDF-based MHDBDB (three-stage: RDF → CSV snapshots → TEI-XML) and migrated into this repository, completed 2025-07-22. **Since that migration (2025-07-22), this repository is the independent, sole master** – all data is maintained here; there are no ongoing re-exports or syncs with Salzburg. It is now an active project with continuing ingest (WZB/Wenzelsbibel, ARITHMETIC) and manual editorial correction, not a static export. See [INDEX.md → Current Phase](INDEX.md#current-phase) and [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules).

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
- `<ptr type="broader">` - Semantic/hierarchical relationships (concept & genre hierarchy)

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

These vocabularies ensure consistency and enable sophisticated cross-referencing. An 8th authority file, **`contributors.xml`**, was added in 2026-04 to register the MHDBDB team (founders, coordinator, lead-editors, editors) for structured editor-attribution in the TEI headers – it is project-internal and deliberately not part of the searchable corpus index.

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

## Downstream Reuse and Related Projects

### ParzivAI (Heidelberg)

An interactive chatbot answering questions on medieval history and on Middle High German language and literature: MHG → New High German translation, literary and historical context, linguistic analysis, image search, and an interactive quiz. Developed at Heidelberg University.

**Institution and people:**
- Florian Nieser (Heidelberg Center for Digital Humanities)
- Thomas Renkert (Heidelberg School of Education)
- Leonie Weiß (MHDBDB-funded support on the gold-standard translations)

**Link to MHDBDB:** Support ran under the CLARIAH-AT project "MHDBDB goes AI". ParzivAI uses philologically verified translations from that project as training and reference data, covering courtly romance, heroic epic, Minnesang, and didactic-moral poetry.

**Technical state (a moving target):**
- The earlier version ran `llama3.2:1b` via Ollama (see the GitHub repository)
- Current direction: open models such as Apertus, a new JSON schema with "thinking blocks" for reasoning processes, plus synthetic data generation

**Status** (as of the conversation with Florian Nieser, 2026-07-09/10): iteration 1 is finished. Version 2 was planned for the 2026 summer term and did not make it because of workload; the new target is September 2026, followed by a paper and ParzivAI 2.0.

**Sources:**
- Blog post: https://dhsalzburg.hypotheses.org/6295
- GitHub: https://github.com/ssciwr/parzivAI (organization `ssciwr` = Scientific Software Center Heidelberg)
- Video: https://unitv.org/beitrag.asp?ID=1288&Keyword=ki

**Why this is relevant here:** Vlastimil Brom (lead editor of TKR/TKA/VTC/PUC, Masaryk University Brno) asked in recent correspondence about own or fine-tuned language models trained on MHDBDB data; he experiments with GHisBERT and dbmdz-bert-base-german-europeana himself and is looking for more professional approaches. ParzivAI is the closest existing answer, and an introduction between Brom and Nieser could be worthwhile for both sides. Tracked as a people task in [ROADMAP.md → Next: pings to people](ROADMAP.md#next-pings-to-people-after-the-merges).

## Corpus Scope and Rights Basis

Two questions decide whether a text can enter the corpus, and they are independent: **is it inside the period we cover**, and **may we publish it**. A text has to pass both.

### Period: before 1600

**Decided by @wachauer (project lead) on 2026-09-10 in [#263](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/263):**

> Wir machen vor 1600 (nicht vor 1500). Die meisten interessanten Kochbuchhandschriften und weitere Gebrauchstexte fallen sonst raus.

Early New High German is therefore **in scope**, not at the margin of it. The reason given is the material itself: the interesting cookery manuscripts and other practical texts (`Gebrauchstexte`) sit in the sixteenth century, and a 1500 boundary would cut nearly all of them.

The boundary is the date of the **text**, not of its edition. Two anchors that are checkable in our own data:

- `works.xml` cites the Narrenschiff "Nach der Erstausgabe (Basel 1494)". It has been in the corpus all along and was named by the project lead as the kind of text that belongs here.
- The CoReMA cookery manuscripts (#139) define the lower end of the practical-text material.

An earlier version of this rule, derived here from those two examples alone and put at "around 1500", was wrong and was withdrawn the same day. It is recorded because the derivation looked sound: two examples do not make a boundary, and where a scope question has a decision-maker, the boundary is asked for rather than inferred.

Consequences for the ingest candidates in the tracker: the fifteen Gloning cookery and dietetics texts (#263) are almost all in scope rather than almost all out; the Trier text archive material and the RKE Digital corpus (#421) are medieval throughout and never touched the boundary. **Dating a candidate is still the first working step**, it just sorts out individual outliers now instead of halving the list.

### Rights: what lets us publish an edition text

The corpus contains texts from editions that are themselves protected. The basis on which they are made accessible was written up by the project lead in 2016 and is summarized here because it had lived in a file on one laptop until 2026-09-10 (#267).

**Three provisions carry it:**

| Provision | What it gives us |
|---|---|
| § 46 UrhG-AT, § 51 UrhG-DE | the large quotation (`Großzitat`): quoting a work in an independent scholarly work |
| § 76b UrhG-AT | the related right in an edition runs **25 years** from publication. An edition older than that is unproblematic |
| § 57 Abs. 2 UrhG-AT, § 63 Abs. 1 UrhG-DE | the condition attached to the quotation: the source must always be named |

The 25-year figure is the operative one for day-to-day decisions:

> Für die MHDBDB bedeutet dies nun nach meinem Verständnis: Editionen, deren Erstveröffentlichung mehr als 25 Jahre zurückliegt, sind gänzlich unproblematisch.

The source-citation condition is met and visibly met: every text carries a full bibliographic entry in its `sourceDesc`, with editors, publisher, place, year and ISBN, and the reader shows it in the metadata panel.

The underlying assumption about the `editio princeps` rests on: Melichar, Ferdinand: Copyright für Texte und Abbildungen: Rechtsfragen im Umfeld von (mediävistischen) Editionen. In: Wege zum Text: Überlegungen zur Verfügbarkeit mediävistischer Editionen im 21. Jahrhundert. Grazer Kolloquium 17.–19. September 2008. Hrsg. von Wernfried Hofmeister und Andrea Hofmeister-Winter. Tübingen: Niemeyer 2009, S. 133–138.

**One rule on top of the law, and it is a project decision, not a legal necessity.** For the texts whose editions are still inside the 25 years, the MHDBDB does not generate printable PDFs: reading online is what the quotation right supports, replacing the purchase of the book is not something we make convenient. The legal basis says nothing about print versions; this restriction goes beyond it deliberately. What readers do with screenshots or copy and paste is outside our responsibility.

The texts this applies to are marked in the TEI and listed in #267.

### License compatibility when taking in outside material

Our data are **CC BY-NC-SA 4.0** (`LICENSE-DATA`). That is a narrower license than it looks when material arrives from elsewhere. CC BY-SA 4.0, section 3(b) ShareAlike:

> The Adapter's License You apply must be a Creative Commons license with the same License Elements, this version or later, or a BY-SA Compatible License.

The License Elements of BY-SA are BY and SA; BY-NC-SA has BY, NC and SA, so they are not the same. **Material under CC BY-SA cannot simply be redistributed under our license**, and the compatible-licenses list the legal code points to currently returns 404. Where an otherwise welcome corpus is BY-SA (the case in #421), the way forward is an additional license from the rights holders, a dual license in the repository, or linking instead of integrating. That is a decision for the project lead, not a technical question.

## Limitations & Future Directions

### Current Limitations

**Corpus scope:**
- Limited to pre-encoded texts (no dynamic addition)
- Desktop-only interface (not mobile-optimized)
- Static corpus (requires rebuild for updates)

**Technical constraints:**
- Client-only architecture (all processing in browser)
- Large initial download (~43 MB indexes: 3 MB authority + 40 MB corpus, gzipped)
- Limited to browser memory

**Methodological:**
- Semantic annotations reflect project-specific taxonomy
- Not all texts have complete semantic markup
- Some concepts have limited lemma coverage

### Future Research Directions

**Corpus expansion:**
- Add more texts from medieval German tradition
- Include additional text types (letters, documents, etc.)
- Work through the ingest candidates inside the period boundary (see Corpus Scope above; Early New High German up to 1600 is settled scope since 2026-09, not a future extension)

**Enhanced functionality:**
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
