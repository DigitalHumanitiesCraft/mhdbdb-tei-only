# MHDBDB Search Guide

**Complete guide to all 11 search functions**

This document provides detailed instructions for using every search type in MHDBDB, with examples, tips, and best practices.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Main Site Search](#main-site-search)
3. [Authority File Searches (6 types)](#authority-file-searches)
4. [TEI Text Analysis (5 types)](#tei-text-analysis)
5. [Advanced Techniques](#advanced-techniques)
6. [Search Examples](#search-examples)

---

## 🔍 Overview

### Two Search Interfaces

| Interface | Location | Best For | Speed |
|-----------|----------|----------|-------|
| **Main Site** | `/` | Quick lemma lookup, reading texts | Very fast |
| **Playground** | `/playground/` | Advanced research, multi-lemma, analysis | Fast |

### 11 Search Entry Points

**Authority Files** (6 searches - reference data):
1. Autoren anzeigen (Authors)
2. Werke anzeigen (Works)
3. Lemmata anzeigen (Dictionary)
4. Konzepte anzeigen (Concepts)
5. Gattungen anzeigen (Genres)
6. Namen anzeigen (Names)

**TEI Texts** (5 searches - corpus analysis):
7. Lemma-Suche (Single lemma in text)
8. Multi-Lemma-Suche (Absatz) (Paragraph-level)
9. Multi-Lemma-Suche (Dokument) (Document-level)
10. Multi-Lemma-Suche (Nähe) (Proximity search)
11. XPath Query (Advanced XML queries)

### Middle High German Normalization

**All searches use automatic character normalization:**

| MHG Character | Normalized To | Example |
|---------------|---------------|---------|
| â, ā, ǎ | a | brôt → brot |
| ê, ē, ě | e | lêre → lere |
| î, ī, ǐ | i | wîse → wise |
| ô, ō, ǒ | o | tôt → tot |
| û, ū, ǔ | u | hûs → hus |
| ä | ae | käme → kaeme |
| ö | oe | schöne → schoene |
| ü | ue | müete → mueete |
| æ | ae | mære → maere |
| œ | oe | gœte → goete |

**You can search with OR without special characters - both work!**

---

## 🌐 Main Site Search

### Purpose
Fast lemma lookup across the entire corpus with immediate text access.

### How to Use

**Step 1**: Open Main Site
- Navigate to `/` or main domain
- Wait for "Ready to search 666 texts"

**Step 2**: Enter Search Term
- Type a Middle High German word (e.g., `vriunt`)
- Press Enter or click search button

**Step 3**: Review Results
- See lemma matches with:
  - Dictionary form
  - Translation/meaning
  - Grammar info
  - Occurrence count
  - Text locations

**Step 4**: Read Context
- Click any result
- Modal opens with text
- Search term highlighted in yellow
- Scroll to explore context

### Features

✅ **3-Stage Resolution**:
- Stage 1: Exact match in lexicon
- Stage 2: Orthographic variants (192,674 mappings)
- Stage 3: Fuzzy/partial match

✅ **Filters**:
- Genre dropdown (615 genres)
- Author dropdown (210 authors)

✅ **Caching**:
- First visit: 3-5 second load
- Return visits: Instant
- TEI texts cached after first open (97% faster)

### Example 1: Finding "God" References

```
Search: "got"

Results:
├─ got (noun, masc.) - God
│  └─ 12,456 occurrences in 523 texts
├─ gotes (genitive form)
│  └─ 8,932 occurrences
└─ gote (dative form)
   └─ 4,128 occurrences

Click → Opens text with "got" highlighted
```

### Example 2: Filtering by Author

```
1. Select "Meister Eckhart" from Author dropdown
2. Search: "minne" (love)
3. See only Eckhart's usage
4. Compare: Switch to "Mechthild von Magdeburg"
```

### Tips

💡 **Search broadly first**: Start with root form (e.g., "vriunt" not "vriunde")
💡 **Use filters to narrow**: Genre + Author filters reduce noise
💡 **Check variants**: Click "Show variants" to see all spellings
💡 **Clear cache if outdated**: Use 🗑️ button in header

---

## 📚 Authority File Searches

These 6 searches explore reference vocabularies (controlled data).

### Search 1: Autoren anzeigen (Authors)

**Purpose**: Find authors and historical persons

**Location**: Playground → "Autoren anzeigen" button

**Data Source**: `authority-files/persons.xml` (210 persons)

**How to Use**:
1. Click "Autoren anzeigen"
2. Search box appears
3. Type author name (e.g., "Eckhart")
4. Results filter as you type

**What You See**:
- Preferred name (e.g., "Meister Eckhart")
- Alternative names (e.g., "Eckhart von Hochheim")
- Person ID (e.g., `person_445`)
- Related works (if cross-referenced)

**Example**:
```
Search: "Mechthild"

Results:
├─ Mechthild von Magdeburg (person_123)
│  └─ Alternative: Mechtild, Mathilde
│  └─ Works: Das fließende Licht der Gottheit
└─ Mechthild von Hackeborn (person_124)
   └─ Works: Liber specialis gratiae
```

**Use Case**: Finding all texts by a specific author

---

### Search 2: Werke anzeigen (Works)

**Purpose**: Browse titles and manuscripts

**Location**: Playground → "Werke anzeigen" button

**Data Source**: `authority-files/works.xml` (583 works)

**How to Use**:
1. Click "Werke anzeigen"
2. Search by title, sigle, or author
3. Filter results

**What You See**:
- Full title
- Short title (sigle)
- Author (linked to persons)
- Work ID (e.g., `work_789`)

**Example**:
```
Search: "Predigt"

Results:
├─ Predigt 1 (Meister Eckhart)
│  └─ Sigle: ECK_PR_1
│  └─ Author: person_445
├─ Predigt 2 (Meister Eckhart)
│  └─ Sigle: ECK_PR_2
...
└─ Predigt 86 (Meister Eckhart)
```

**Use Case**: Finding specific texts or sermons

---

### Search 3: Lemmata anzeigen (Dictionary)

**Purpose**: Browse the complete Middle High German lexicon

**Location**: Playground → "Lemmata anzeigen" button

**Data Source**: `authority-files/lexicon.xml` (43,750 lemmata)

**How to Use**:
1. Click "Lemmata anzeigen"
2. Search by lemma (canonical form)
3. See all orthographic variants

**What You See**:
- Lemma (dictionary form)
- Part of speech
- Grammar details (gender, etc.)
- All attested spelling variants
- Lemma ID (e.g., `lemma_879`)

**Example**:
```
Search: "vriunt"

Result:
Lemma: vriunt
Part of Speech: noun
Gender: masculine
Lemma ID: lemma_1234

Variants (47 total):
- vriunt, vrivnt, vrūnt, friunt, vriwnt, vriend, vrunt, ...

Occurrences: 1,234 in 89 texts
```

**Use Case**: Understanding orthographic variation, finding canonical forms

---

### Search 4: Konzepte anzeigen (Concepts)

**Purpose**: Explore semantic concept taxonomy

**Location**: Playground → "Konzepte anzeigen" button

**Data Source**: `authority-files/concepts.xml` (567 concepts)

**How to Use**:
1. Click "Konzepte anzeigen"
2. Search by German or English term
3. Browse hierarchical categories

**What You See**:
- Concept term (German)
- English translation
- Taxonomy category
- Concept ID (e.g., `concept_456`)
- Related concepts (hierarchy)

**Example**:
```
Search: "Liebe"

Results:
├─ Liebe (Love)
│  └─ Category: Emotions
│  └─ ID: concept_456
│  └─ Related: Minne, Zuneigung
└─ Gottesliebe (Divine Love)
   └─ Category: Theology
   └─ ID: concept_457
```

**Use Case**: Semantic research, finding concept-annotated words

---

### Search 5: Gattungen anzeigen (Genres)

**Purpose**: Browse literary genre classifications

**Location**: Playground → "Gattungen anzeigen" button

**Data Source**: `authority-files/genres.xml` (615 genres)

**How to Use**:
1. Click "Gattungen anzeigen"
2. Search by genre name (German/English)
3. See taxonomy hierarchy

**What You See**:
- Genre term (German)
- English translation
- Taxonomy category
- Genre ID (e.g., `genre_12`)

**Example**:
```
Search: "Mystik"

Results:
├─ Mystik (Mysticism)
│  └─ Category: Religious Literature
│  └─ ID: genre_45
├─ Predigtmystik (Sermon Mysticism)
│  └─ Parent: Mystik
│  └─ ID: genre_46
└─ Brautmystik (Bridal Mysticism)
   └─ Parent: Mystik
   └─ ID: genre_47
```

**Use Case**: Genre-based corpus analysis

---

### Search 6: Namen anzeigen (Names)

**Purpose**: Search proper names (persons, places)

**Location**: Playground → "Namen anzeigen" button

**Data Source**: `authority-files/names.xml` (90 names)

**How to Use**:
1. Click "Namen anzeigen"
2. Search by name (German/English)
3. See semantic annotations

**What You See**:
- Name (German form)
- English translation/variant
- Name type (person/place/etc.)
- Name ID (e.g., `name_78`)

**Example**:
```
Search: "Maria"

Results:
├─ Maria (Mary)
│  └─ Type: Biblical person
│  └─ ID: name_23
│  └─ Related: Jungfrau Maria, Mutter Gottes
└─ Maria Magdalena
   └─ Type: Biblical person
   └─ ID: name_24
```

**Use Case**: Finding references to specific historical/biblical figures

---

## 📖 TEI Text Analysis

These 5 searches work on uploaded TEI files or the pre-built corpus.

### Prerequisite: Load Corpus

Before using TEI searches, click **"Load Corpus"** button:
- Downloads corpus index (20.84 MB, ~1.4 seconds)
- Caches in IndexedDB for future visits
- Enables lazy-loading of 666 texts

---

### Search 7: Lemma-Suche (Single Lemma Search)

**Purpose**: Find all instances of a word within a specific text

**Location**: Playground → "Lemma-Suche" button (after loading corpus)

**How to Use**:
1. Load corpus
2. Select a text from dropdown
3. Click "Lemma-Suche"
4. Enter lemma (e.g., "vriunt")
5. See highlighted results

**What You See**:
- All occurrences in selected text
- Surrounding context (full sentence)
- Word position (line/paragraph number)
- Highlighted lemma in yellow

**Example**:
```
Text: Predigt 52 (Meister Eckhart)
Search: "vriunt"

Results (3 occurrences):
1. Line 12: "Ein meister sprichet: swer dâ wil vinden einen güten vriunt..."
                                                                  ^^^^^^
2. Line 45: "Der vriunt kumt und sprichet..."
                ^^^^^^
3. Line 78: "Alsô sol der vriunt sîn..."
                       ^^^^^^
```

**Use Case**: Word frequency analysis in a single text

---

### Search 8: Multi-Lemma-Suche (Absatz) - Paragraph Search

**Purpose**: Find paragraphs containing ALL specified lemmata

**Location**: Playground → "Multi-Lemma-Suche (Absatz)" button

**How to Use**:
1. Load corpus
2. Click "Multi-Lemma-Suche (Absatz)"
3. Enter lemmata separated by `+` (e.g., `brôt + wîn`)
4. Click "Search"
5. See paragraphs with ALL words highlighted (color-coded)

**What You See**:
- Paragraphs containing all search terms
- Each lemma highlighted in different color:
  - First lemma: Yellow
  - Second lemma: Blue
  - Third lemma: Green
  - (etc.)
- Text title and paragraph number
- Full context

**Example**:
```
Search: "brôt + wîn"

Result:
Text: Predigt 5 (Meister Eckhart), Paragraph 3

"Daz brôt, daz ich iʒʒe, ist mîn lîp, und der wîn, den ich trinke,
     ^^^^                                     ^^^^
   (yellow)                                  (blue)
 ist mîn bluot."
```

**Technical Details**:
- Supports 3-stage lemma resolution:
  - Canonical forms (e.g., "brôt")
  - Orthographic variants (e.g., "brott", "brot")
  - Lemma IDs (e.g., `879`)
- Searches entire corpus (666 texts)
- Returns up to 100 results per search

**Use Case**: Concept co-occurrence research (e.g., "bread + wine" = Eucharist)

---

### Search 9: Multi-Lemma-Suche (Dokument) - Document Search

**Purpose**: List texts containing ALL specified lemmata (anywhere in text)

**Location**: Playground → "Multi-Lemma-Suche (Dokument)" button

**How to Use**:
1. Load corpus
2. Click "Multi-Lemma-Suche (Dokument)"
3. Enter lemmata: `got + minne + sêle`
4. See list of texts containing all words

**What You See**:
- Text titles containing all search terms
- Number of occurrences per text
- Clickable links to open full text

**Example**:
```
Search: "got + minne + sêle"

Results (23 texts):
├─ Predigt 52 (Meister Eckhart)
│  └─ got: 47 occurrences, minne: 12, sêle: 23
├─ Das fließende Licht (Mechthild)
│  └─ got: 234 occurrences, minne: 89, sêle: 145
...
```

**Use Case**: Finding texts that discuss multiple concepts together

---

### Search 10: Multi-Lemma-Suche (Nähe) - Proximity Search

**Purpose**: Find lemmata appearing near each other (within X words)

**Location**: Playground → "Multi-Lemma-Suche (Nähe)" button

**How to Use**:
1. Load corpus
2. Click "Multi-Lemma-Suche (Nähe)"
3. Enter lemmata: `brôt + wîn`
4. Set distance: `10 words` (or custom)
5. See tight co-occurrences

**What You See**:
- Text excerpts where words appear within distance
- Color-coded highlights
- Word distance count
- Context snippet

**Example**:
```
Search: "brôt + wîn" within 5 words

Result:
Text: Predigt 5, Line 12

"...und er gap in brôt und wîn ze eʒʒenne..."
              ^^^^      ^^^^
            (yellow)   (blue)
Distance: 2 words ✅
```

**vs. Rejected (too far)**:
```
"...daz brôt was guot... und ouch der wîn..."
    ^^^^                           ^^^^
  (yellow)                        (blue)
Distance: 8 words ❌ (exceeds 5-word limit)
```

**Technical Details**:
- Default distance: 10 words
- Customizable: 1-100 words
- Counts only content words (excludes punctuation)

**Use Case**: Discourse analysis, collocation research

---

### Search 11: XPath Query (Advanced)

**Purpose**: Run custom XML queries on TEI files

**Location**: Playground → "XPath Query" button

**Target Audience**: Experts familiar with XML and TEI structure

**How to Use**:
1. Load corpus
2. Click "XPath Query"
3. Select text(s) to query
4. Enter XPath expression
5. Execute query
6. See results with syntax highlighting

**What You See**:
- Query results (nodes/text/attributes)
- Syntax-highlighted XML
- Node count
- Error messages (if invalid query)

**Example 1: Find all nouns**
```xpath
//tei:w[@pos='noun']
```

**Example 2: Find specific lemma with annotations**
```xpath
//tei:w[@lemmaRef='lexicon.xml#lemma_879' and @ana]
```

**Example 3: Find paragraphs with more than 50 words**
```xpath
//tei:p[count(.//tei:w) > 50]
```

**Example 4: Extract all author names**
```xpath
//tei:author/text()
```

**Namespace Note**: Use `tei:` prefix for TEI elements (http://www.tei-c.org/ns/1.0)

**Use Case**: Custom research queries not covered by other search types

---

## 🎓 Advanced Techniques

### 1. Combining Searches

**Strategy**: Use multiple search types to triangulate research questions

**Example Research Question**: "How does Meister Eckhart use 'minne' (love) in mystical contexts?"

**Step 1**: Find Eckhart's works
- Use "Werke anzeigen"
- Search "Eckhart"
- Note work IDs

**Step 2**: Find concept IDs for mysticism
- Use "Konzepte anzeigen"
- Search "Mystik"
- Note concept IDs

**Step 3**: Multi-lemma search
- Use "Multi-Lemma-Suche (Absatz)"
- Search: `minne + sêle + got` (common mystical triad)
- Filter results to Eckhart's works

**Step 4**: XPath verification
- Use "XPath Query"
- Query: `//tei:w[@lemma='minne' and @ana='concept_456']`
- Verify semantic annotations

---

### 2. Variant Resolution Strategies

**Problem**: You're not sure of the exact spelling

**Solution A**: Use variants index
- Search in "Lemmata anzeigen"
- See all attested spellings
- Note canonical form
- Use canonical form in other searches

**Solution B**: Try multiple spellings
- Multi-lemma search accepts variants
- Enter: `brôt + brot + brott` (all variants)
- System resolves to same lemma

**Solution C**: Partial matching
- Main site search uses `includes()`
- Search: `bro` finds `brôt`, `brott`, `broch`, etc.

---

### 3. Performance Optimization

**Slow searches**: Multi-lemma searches on entire corpus can take 5-10 seconds

**Optimization strategies**:

1. **Use document-level first**: Narrows down relevant texts
   - `Multi-Lemma-Suche (Dokument)` → list of 20 texts
   - Then use paragraph-level on specific texts

2. **Filter by genre/author**: Reduces search space
   - Main site: Use dropdowns
   - Playground: Note work IDs, manually filter

3. **Cache aggressive**: Open texts you reference often
   - First open: 60 seconds
   - Subsequent: 2-3 seconds (97% faster)

4. **Use XPath for precision**: More efficient than multi-lemma for specific queries

---

### 4. Research Workflows

**Workflow 1: Keyword-in-Context (KWIC) Analysis**
1. Main site search for lemma
2. Open 10-20 texts with most occurrences
3. Read contexts (all cached for speed)
4. Note patterns
5. Export findings (manual copy-paste currently)

**Workflow 2: Co-occurrence Network**
1. Multi-lemma document search: `got + minne`
2. Note texts with both
3. Multi-lemma document search: `got + sêle`
4. Cross-reference text lists
5. Texts in both lists = network nodes

**Workflow 3: Authorship Comparison**
1. Main site: Filter "Meister Eckhart", search "minne"
2. Note frequency (e.g., 234 occurrences)
3. Switch filter to "Mechthild von Magdeburg"
4. Note frequency (e.g., 456 occurrences)
5. Compare contexts with Multi-lemma paragraph search

---

## 📚 Search Examples

### Example 1: Eucharist Symbolism

**Goal**: Find references to bread and wine (Eucharist)

**Method**: Multi-Lemma Paragraph Search
```
Search: brôt + wîn
Mode: Absatz (paragraph)
Expected: ~50 results in mystical texts
```

**Findings** (example):
- Predigt 5 (Eckhart): 3 paragraphs
- Predigt 52 (Eckhart): 1 paragraph
- Das fließende Licht (Mechthild): 5 paragraphs

**Next Step**: Proximity search to find tight collocations
```
Search: brôt + wîn
Mode: Nähe (proximity)
Distance: 5 words
```

---

### Example 2: Soul and Body Dichotomy

**Goal**: Research how medieval texts discuss soul vs. body

**Method**: Multi-Lemma Document Search
```
Search: sêle + lîp
Mode: Dokument (document)
Expected: ~200 texts
```

**Refinement**: Add third term
```
Search: sêle + lîp + geist
Expected: ~80 texts (more specific)
```

**Analysis**: Use XPath to find contrastive structures
```xpath
//tei:p[.//tei:w[@lemma='sêle'] and .//tei:w[@lemma='lîp']]
```

---

### Example 3: Divine Love Terminology

**Goal**: Map vocabulary of divine love in Eckhart vs. Mechthild

**Method**: Combined Authority + TEI searches

**Step 1**: Find concept IDs
- Konzepte anzeigen → search "Liebe"
- Note concept IDs: `concept_456` (Love), `concept_457` (Divine Love)

**Step 2**: Find lemmata
- Lemmata anzeigen → search "minne", "liebe", "kärlich"
- Note lemma IDs: `lemma_1234`, `lemma_2345`, `lemma_3456`

**Step 3**: Eckhart analysis
- Werke anzeigen → filter Eckhart works
- Multi-Lemma Document → search all 3 lemmata
- Note frequency per text

**Step 4**: Mechthild analysis
- Repeat Step 3 with Mechthild's works

**Step 5**: Compare
- Create frequency table
- Note contextual differences via paragraph search

---

### Example 4: Negation Mysticism

**Goal**: Find negative theology language (God as "nothing", "unknowable")

**Method**: Multi-Lemma Proximity Search
```
Search: got + niht
Mode: Nähe (proximity)
Distance: 3 words
```

**Expected pattern**: "got ist niht" (God is nothing)

**XPath verification**:
```xpath
//tei:p[contains(., 'got') and contains(., 'niht')]
```

**Expansion**: Add more negative terms
```
Search: got + niht + unbekant + verborgen
Mode: Absatz (paragraph)
```

---

## 💡 Pro Tips

### Search Efficiency

1. **Start broad, narrow down**:
   - Document search → Paragraph search → Proximity search

2. **Use canonical forms**:
   - Check "Lemmata anzeigen" first to find standard spelling

3. **Leverage autocomplete** (if available):
   - Type partial word, let system suggest

4. **Cache strategically**:
   - Open frequently-used texts first
   - Subsequent access 97% faster

### Research Accuracy

1. **Always verify in context**:
   - Don't trust search highlights alone
   - Read full paragraph/text

2. **Check orthographic variants**:
   - MHG has no standard spelling
   - System catches most, but manual verification recommended

3. **Cross-reference findings**:
   - Use multiple search types to confirm patterns

4. **Note limitations**:
   - Genre filtering may not work (works lack genre links)
   - XPath requires TEI knowledge

### Collaboration

1. **Document queries**:
   - Save your search strings
   - Share with collaborators

2. **Export results** (manual):
   - Copy-paste into notes
   - Automated export planned for future

3. **Cite properly**:
   - Include text ID, line numbers, search method

---

## ❓ FAQ

**Q: Why does my multi-lemma search return no results?**
A: Check that ALL lemmata exist in the corpus. Try individual searches first.

**Q: How many lemmata can I search at once?**
A: System supports 2-10 lemmata. Performance degrades after 5+.

**Q: Can I save searches?**
A: Not yet implemented. Bookmark URLs or document search strings manually.

**Q: Why are some XPath queries slow?**
A: Complex queries (e.g., nested axes) require full DOM traversal. Simplify or use other search types.

**Q: How do I export results?**
A: Currently manual copy-paste only. CSV export planned for future release.

---

## 📧 Feedback

Found a bug? Have a search feature request? Contact:
- **Email**: mhdbdb@plus.ac.at
- **GitHub**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues

---

**Happy searching! 🔍**

---

**Last Updated**: 2025-10-01
**Version**: 1.0
**License**: CC BY-NC-SA 3.0 AT

**Navigation**: [↑ Docs Index](./README.md) | [← User Guide](./USER-GUIDE.md) | [→ FAQ](./FAQ.md)
