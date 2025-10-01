# MHDBDB Glossary

**Middle High German terms, technical concepts, and MHDBDB-specific terminology**

---

## 📋 Table of Contents

1. [Middle High German Terms](#middle-high-german-terms)
2. [MHDBDB Technical Terms](#mhdbdb-technical-terms)
3. [TEI & Digital Humanities](#tei--digital-humanities)
4. [Search & Analysis Terms](#search--analysis-terms)

---

## 📖 Middle High German Terms

### Linguistic Terms

**Middle High German (Mittelhochdeutsch, MHG)**
- Historical stage of German language (~1050-1350 CE)
- No standardized orthography
- Characterized by: Long vowels (â, ê, î, ô, û), umlauts, diphthongs

**Lemma (pl. Lemmata)**
- Dictionary headword or canonical form of a word
- Example: `vriunt` is the lemma for variants like `vrivnt`, `vrūnt`, `friunt`

**Orthographic Variant**
- Different spelling of the same lemma
- Example: `brôt`, `brott`, `brot`, `broht` (all mean "bread")
- MHDBDB has 176,056 attested variants

**Normalization**
- Process of converting MHG characters to modern equivalents
- Example: `brôt` → `brot`, `ü` → `ue`
- Enables flexible searching

**Inflection**
- Grammatical changes to word form (case, number, gender, tense)
- Example: `vriunt` (nom.) → `vriunde` (dat.)

---

### Common MHG Words in Corpus

**got** (noun, masc.)
- God
- One of most frequent words in corpus

**minne** (noun, fem.)
- Love (especially courtly or divine love)
- Key mystical concept

**sêle** (noun, fem.)
- Soul
- Central in mystical writings

**vriunt** (noun, masc.)
- Friend, lover
- 1,200+ occurrences

**brôt** (noun, neut.)
- Bread
- Common in Eucharist contexts

**wîn** (noun, masc.)
- Wine
- Often paired with `brôt` (Eucharist)

**geist** (noun, masc.)
- Spirit, mind
- Theological concept

**herze** (noun, neut.)
- Heart
- Emotional/spiritual center

**lîp** (noun, masc.)
- Body
- Often contrasted with `sêle` (soul)

**wort** (noun, neut.)
- Word
- Divine word, scripture

---

### MHG Characters & Pronunciation

| Character | Name | Sound (approx.) | Example |
|-----------|------|-----------------|---------|
| â | a-circumflex | long "ah" | brât (bread) |
| ê | e-circumflex | long "ay" | lêre (teaching) |
| î | i-circumflex | long "ee" | wîse (wise) |
| ô | o-circumflex | long "oh" | tôt (death) |
| û | u-circumflex | long "oo" | hûs (house) |
| ä | a-umlaut | "eh" | käme (would come) |
| ö | o-umlaut | "uh" (German ö) | schöne (beautiful) |
| ü | u-umlaut | "ew" (German ü) | müete (effort) |
| æ | ae-ligature | long "eh" | mære (news) |
| œ | oe-ligature | long "uh" (German ö) | schœne (beautiful) |

---

## 🔧 MHDBDB Technical Terms

### Data Structures

**Authority File**
- Controlled vocabulary XML file
- Types: persons, works, lexicon, concepts, genres, names, variants
- Example: `authority-files/persons.xml`

**TEI File**
- Text Encoding Initiative XML file
- Contains one MHG text with annotations
- Example: `tei/ECK_PR_52.tei.xml` (Meister Eckhart, Sermon 52)

**Corpus Index**
- Pre-built JSON index of all 666 texts
- Contains: metadata, lemma positions, word counts
- Size: 20.84 MB compressed
- Location: `data/corpus-index.json.gz`

**Authority Index**
- Pre-built JSON index of all authority files
- Contains: lemmata, persons, works, concepts, genres, names
- Size: 1.27 MB compressed
- Location: `data/authority-index.json.gz`

**Variants Index**
- Mapping of orthographic variants → canonical lemmata
- Generated from TEI corpus
- 192,674 variant-to-lemma mappings
- Location: `authority-files/variants.xml`

---

### MHDBDB Identifiers

**Lemma ID**
- Unique identifier for dictionary entry
- Format: `lemma_###` (e.g., `lemma_879` = "brôt")

**Person ID**
- Unique identifier for author/person
- Format: `person_###` (e.g., `person_445` = "Meister Eckhart")

**Work ID**
- Unique identifier for text/manuscript
- Format: `work_###` (e.g., `work_789` = "Predigt 52")

**Concept ID**
- Unique identifier for semantic concept
- Format: `concept_###` (e.g., `concept_456` = "Love")

**Genre ID**
- Unique identifier for literary genre
- Format: `genre_###` (e.g., `genre_45` = "Mystik")

**Name ID**
- Unique identifier for proper name
- Format: `name_###` (e.g., `name_23` = "Maria")

---

### Search Components

**3-Stage Lemma Resolution**
- Multi-step process for finding lemmata:
  1. **Stage 1**: Exact match in lexicon (canonical forms)
  2. **Stage 2**: Variants index lookup (192K mappings)
  3. **Stage 3**: Partial/fuzzy match (includes search)

**Main Site**
- Simple public-facing corpus browser
- Location: `/` (root)
- Features: Fast search, text reading, filtering

**Playground**
- Advanced research tool
- Location: `/playground/`
- Features: 11 searches, file upload, XPath queries

**Multi-Lemma Search**
- Search for multiple lemmata simultaneously
- Modes: Paragraph, Document, Proximity
- Example: `brôt + wîn` finds texts with both

**Proximity Search**
- Find lemmata within X words of each other
- Example: `got + niht` within 3 words
- Good for: Collocations, phrase-like patterns

---

### Caching & Performance

**IndexedDB**
- Browser database for storing large data
- MHDBDB uses for: Indices, parsed TEI DOMs
- Quota: Typically 1-50 GB (browser-dependent)

**Cache TTL (Time-To-Live)**
- How long cached data stays valid
- Authority files: 30 days
- Corpus index: 30 days
- TEI DOMs: 30 days

**Cache Hit**
- Data found in cache (fast, no network)
- Console logs: "⚡ Loaded from cache"

**Cache Miss**
- Data not in cache (slow, requires network)
- Console logs: "🌐 Fetching from network"

**DOM Caching**
- Storing parsed XML Documents in IndexedDB
- Performance: 97% faster (2-3s vs 60s)
- Trade-off: Uses more storage (~50-200 MB)

---

## 🌐 TEI & Digital Humanities

### TEI (Text Encoding Initiative)

**TEI**
- Standard for encoding texts in XML
- Version: TEI P5
- Website: https://tei-c.org

**TEI Namespace**
- XML namespace for TEI elements
- URL: `http://www.tei-c.org/ns/1.0`
- Prefix: `tei:` (in XPath queries)

**TEI Header**
- Metadata section at start of TEI file
- Contains: title, author, date, encoding info
- Element: `<teiHeader>`

**TEI Body**
- Main content section of TEI file
- Contains: text, annotations
- Element: `<body>`

---

### TEI Annotation Elements

**`<w>` (word)**
- Word element with attributes
- Attributes:
  - `@lemma` - Dictionary form (deprecated, legacy)
  - `@lemmaRef` - Link to lexicon entry (e.g., `lexicon.xml#lemma_879`)
  - `@wordRef` - Variant form reference
  - `@pos` - Part of speech
  - `@ana` - Semantic annotation (concept link)

**`<p>` (paragraph)**
- Paragraph element
- Contains multiple `<w>` elements
- Used in: Paragraph-level multi-lemma search

**`<div>` (division)**
- Text division (section, chapter)
- Hierarchical structure

**`<persName>` (person name)**
- Person name element
- Attributes: `@ref` (link to person ID)
- Example: `<persName ref="#person_445">Meister Eckhart</persName>`

**`@lemmaRef` attribute**
- Points to canonical lemma in lexicon
- Format: `lexicon.xml#lemma_###`
- Example: `<w lemmaRef="lexicon.xml#lemma_879">brott</w>`

**`@ana` attribute**
- Semantic annotation (analysis)
- Points to concept/genre/name ID
- Example: `<w ana="#concept_456">minne</w>`

---

### XPath

**XPath**
- Query language for XML
- Used to select nodes in TEI documents
- Example: `//tei:w[@lemma='got']` (all "God" words)

**XPath Axes**
- Directional relationships:
  - `child::` - Direct children
  - `descendant::` - All descendants
  - `following-sibling::` - Next siblings
  - `ancestor::` - Parent elements

**XPath Predicates**
- Filters in square brackets
- Example: `//tei:w[@pos='noun']` (all nouns)
- Example: `//tei:p[count(.//tei:w) > 50]` (paragraphs with 50+ words)

---

### Digital Humanities Concepts

**Corpus Linguistics**
- Study of language through large text collections
- MHDBDB corpus: 7.4 million words

**KWIC (Keyword In Context)**
- Display format showing search term + surrounding text
- Used in: Main site text modal

**Collocation**
- Words that frequently appear together
- Example: `brôt + wîn` (bread + wine)
- Analyzed via: Proximity search

**Named Entity Recognition (NER)**
- Identifying proper names (persons, places)
- In MHDBDB: `<persName>`, `<placeName>` elements

**Semantic Annotation**
- Linking words to concepts/meanings
- In MHDBDB: `@ana` attribute

---

## 🔍 Search & Analysis Terms

### Search Types

**Exact Match**
- Search term matches lemma exactly
- Example: Search "got" → finds lemma "got"
- Fastest search method

**Fuzzy Match**
- Partial or approximate match
- Example: Search "bro" → finds "brôt", "brott", "broch"
- Uses `includes()` algorithm

**Normalized Match**
- Search with character normalization
- Example: Search "brot" → finds "brôt" (with circumflex)
- All MHDBDB searches use this

---

### Search Modes

**Authority File Search**
- Searches reference vocabularies
- Types: Authors, Works, Lemmata, Concepts, Genres, Names
- Fast (small data sets)

**TEI Text Search**
- Searches corpus texts
- Types: Single lemma, Multi-lemma (3 modes), XPath
- Slower (larger data sets)

**Paragraph-Level Search**
- Finds paragraphs with all search terms
- Tighter results than document-level
- Example: "Multi-Lemma-Suche (Absatz)"

**Document-Level Search**
- Finds texts with all search terms (anywhere)
- Broader results than paragraph-level
- Example: "Multi-Lemma-Suche (Dokument)"

**Proximity Search**
- Finds terms within X words of each other
- Example: "Multi-Lemma-Suche (Nähe)"
- Good for: Collocations, phrases

---

### Result Types

**Occurrence**
- Single instance of a lemma in text
- Example: "got" appears 12,456 times (12,456 occurrences)

**Context**
- Surrounding text around search result
- MHDBDB shows: Full paragraph

**Highlighting**
- Visual emphasis of search terms
- Main site: Yellow highlight
- Multi-lemma: Color-coded (yellow, blue, green, etc.)

**Frequency**
- How often a lemma appears
- Example: "got" = 12,456 occurrences
- Calculated from: Corpus index

---

### Analysis Concepts

**Word Distance**
- Number of words between two lemmata
- Used in: Proximity search
- Example: "brôt ... und ... wîn" = distance 2

**Co-occurrence**
- Two or more lemmata appearing together
- Levels: Paragraph, document, proximity
- Example: "brôt + wîn" in Eucharist texts

**Concordance**
- List of all occurrences with context
- Similar to: KWIC display

**Lemma Frequency Distribution**
- How often each lemma appears in corpus
- Use for: Most/least common words

---

## 📊 Statistics & Metrics

### Corpus Statistics

**666 texts**
- Total number of TEI files in corpus

**7.4 million words**
- Total word count across all texts

**43,750 lemmata**
- Unique dictionary entries in lexicon

**176,056 variants**
- Orthographic variants mapped to lemmata
- Average: ~4 variants per lemma

**210 persons**
- Authors and historical figures

**583 works**
- Texts and manuscripts

**567 concepts**
- Semantic categories

**615 genres**
- Literary genre classifications

**90 names**
- Proper names (persons, places)

---

### Performance Metrics

**1.4 seconds**
- Corpus index load time (cached visit)

**3.8 seconds**
- Playground load time (all authority files)

**97% faster**
- TEI DOM caching speedup (60s → 2-3s)

**95% faster**
- Pre-built indices speedup (3-4 min → 3.8s)

**22 MB**
- Total index size (compressed)

**~100 MB**
- Browser memory usage (decompressed indices)

---

## 🔗 Cross-References

### Related Documentation

- **[User Guide](./USER-GUIDE.md)** - Getting started
- **[Search Guide](./SEARCH-GUIDE.md)** - Detailed search docs
- **[FAQ](./FAQ.md)** - Common questions
- **[Developer Guide](./DEVELOPER-GUIDE.md)** - Technical docs

---

### External Resources

**Middle High German**
- [Mittelhochdeutsches Wörterbuch (Lexer)](http://woerterbuchnetz.de/cgi-bin/WBNetz/wbgui_py?sigle=Lexer)
- [MHDBDB Main Site](https://www.mhdbdb.sbg.ac.at)

**TEI**
- [TEI Guidelines](https://tei-c.org/guidelines/)
- [TEI by Example](https://teibyexample.org/)

**XPath**
- [XPath Tutorial (W3Schools)](https://www.w3schools.com/xml/xpath_intro.asp)
- [XPath Tester](https://www.freeformatter.com/xpath-tester.html)

---

## 📝 Abbreviations

**MHDBDB** - Mittelhochdeutsche Begriffsdatenbank
**MHG** - Middle High German
**TEI** - Text Encoding Initiative
**XML** - eXtensible Markup Language
**XPath** - XML Path Language
**KWIC** - Keyword In Context
**NER** - Named Entity Recognition
**TTL** - Time-To-Live (cache expiration)
**DOM** - Document Object Model
**API** - Application Programming Interface
**CDN** - Content Delivery Network
**MB** - Megabyte
**GB** - Gigabyte

---

## 🆕 Version History

**Version 1.0** (2025-10-01)
- Initial glossary release
- 100+ terms defined
- Covers MHG, TEI, MHDBDB-specific concepts

---

**Last Updated**: 2025-10-01
**Maintained by**: MHDBDB Documentation Team

**Navigation**: [↑ Docs Index](./README.md) | [← FAQ](./FAQ.md)
