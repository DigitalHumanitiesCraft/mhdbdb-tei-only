# MHDBDB User Guide

**Welcome to the Mittelhochdeutsche Begriffsdatenbank (MHDBDB)!**

This guide will help you explore our collection of 666 Middle High German texts with semantic annotations.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Main Site Guide](#main-site-guide)
3. [Playground Guide](#playground-guide)
4. [Search Strategies](#search-strategies)
5. [Understanding Results](#understanding-results)
6. [Tips & Tricks](#tips--tricks)
7. [Frequently Asked Questions](#frequently-asked-questions)

---

## 🚀 Getting Started

### What is MHDBDB?

The **Mittelhochdeutsche Begriffsdatenbank** is a digital research tool providing:

- **666 annotated texts** from Middle High German literature
- **43,750 dictionary entries** (lemmata) with grammatical information
- **176,056 spelling variants** mapped to canonical forms
- **Semantic annotations** linking words to concepts, persons, works, and genres

### Who is this for?

- **Medieval scholars** researching Middle High German literature
- **Linguists** studying historical German language
- **Students** learning about medieval texts
- **Digital humanists** exploring corpus linguistics

### Two Ways to Explore

1. **Main Site** (Recommended for beginners)
   - Simple search interface
   - Fast results
   - Text reading with highlighting
   - Best for: Finding specific words or texts

2. **Playground** (For advanced users)
   - 11 different search types
   - Upload your own TEI files
   - XPath queries
   - Multi-lemma search
   - Best for: Deep research and analysis

---

## 🔍 Main Site Guide

The main site is the fastest way to search the MHDBDB corpus.

### Accessing the Main Site

1. Open your web browser (Chrome recommended)
2. Navigate to: `https://mhdbdb.plus.ac.at` (or your local server)
3. Wait for indices to load (~3-5 seconds on first visit)
4. You'll see: "Ready to search 666 texts"

### Searching for a Word

**Example**: Finding the word "vriunt" (friend)

1. Type `vriunt` in the search box
2. Press Enter or click the search button
3. See results grouped by:
   - **Exact matches** (e.g., "vriunt")
   - **Spelling variants** (e.g., "vrivnt", "vrūnt", "friunt")
   - **Related terms** (similar words)

**Tip**: You can search with modern spelling! Type `vruent` or `vriunt` - both work.

### Understanding Search Results

Results show:
- **Lemma**: The dictionary form of the word (e.g., "vriunt")
- **Meaning**: Translation or definition
- **Grammar**: Part of speech (noun, verb, etc.)
- **Occurrences**: How many times it appears in the corpus
- **Texts**: Which texts contain this word

### Reading a Text

1. Click on a search result
2. A modal window opens showing the text
3. Your search term is **highlighted in yellow**
4. Navigate:
   - **Scroll** to read context
   - **Click outside** the modal to close
   - **Search again** for different words

### Using Filters

**Filter by Genre** (if applicable):
- Click the Genre dropdown
- Select a literary genre (e.g., "Mystik", "Predigt")
- Results update automatically

**Filter by Author**:
- Click the Author dropdown
- Select an author (e.g., "Meister Eckhart")
- See only texts by that author

### Performance Tips

- **First visit**: Takes 3-5 seconds to download indices
- **Subsequent visits**: Instant (cached in your browser)
- **Clear cache**: Use the 🗑️ button if data seems outdated

---

## 🧪 Playground Guide

The Playground offers advanced search and analysis tools.

### Accessing the Playground

1. Navigate to `/playground/` (or click "Playground" link)
2. Wait for authority files to load
3. You'll see: "Authority Files geladen" (Authority files loaded)

### 11 Search Types

The Playground provides **11 different ways to search**:

#### Authority File Searches (6 types)

These search reference vocabularies:

1. **Autoren anzeigen** (Show Authors)
   - Search for authors and historical persons
   - Example: Search "Eckhart" → finds "Meister Eckhart"

2. **Werke anzeigen** (Show Works)
   - Search for titles and manuscripts
   - Example: Search "Predigt" → finds all sermons

3. **Lemmata anzeigen** (Show Lemmata)
   - Browse the entire dictionary
   - Example: Search "got" → finds "got" (God), "gote", "gotes"

4. **Konzepte anzeigen** (Show Concepts)
   - Explore semantic categories
   - Example: Search "Liebe" → finds concept taxonomy

5. **Gattungen anzeigen** (Show Genres)
   - Browse literary genres
   - Example: "Mystik", "Legende", "Predigt"

6. **Namen anzeigen** (Show Names)
   - Search proper names
   - Example: "Maria", "Adam"

#### TEI Text Analysis (5 types)

**First, load the corpus**: Click "Load Corpus" button

7. **Lemma-Suche** (Single Lemma Search)
   - Find all instances of a word in a specific text
   - Example: Search "vriunt" in a text → see all occurrences highlighted

8. **Multi-Lemma-Suche (Absatz)** (Multi-Lemma Paragraph Search)
   - Find paragraphs containing ALL specified words
   - Example: Search "brôt + wîn" → finds paragraphs with both bread AND wine

9. **Multi-Lemma-Suche (Dokument)** (Multi-Lemma Document Search)
   - List texts containing ALL specified words (anywhere in the text)
   - Example: Search "got + minne" → finds texts discussing God AND love

10. **Multi-Lemma-Suche (Nähe)** (Proximity Search)
    - Find words appearing near each other (within X words)
    - Example: "brôt + wîn" within 10 words → finds co-occurrences

11. **XPath Query** (Advanced)
    - Run custom XML queries on TEI files
    - For experts only
    - Example: `//w[@lemma='vriunt']` → all friend-words

### Multi-Lemma Search Tutorial

**Goal**: Find paragraphs where "bread" and "wine" appear together

**Step-by-step**:

1. Click "Load Corpus" (wait ~2 seconds)
2. Click "Multi-Lemma-Suche (Absatz)"
3. Enter: `brôt + wîn` (or `brot + win` - both work!)
4. Click "Search"
5. Results show paragraphs containing both words
6. Each word is **color-coded**:
   - `brôt` → yellow highlight
   - `wîn` → blue highlight

**Advanced**: Use proximity search to find words within 5 words of each other:
- Click "Multi-Lemma-Suche (Nähe)"
- Enter: `brôt + wîn`
- Set distance: `5 words`
- See only close co-occurrences

### Uploading Your Own TEI Files

1. Click "Upload TEI Files" button
2. Select one or more `.tei.xml` files
3. Wait for parsing (large files may take a minute)
4. Your files are now searchable alongside the corpus

**Note**: Files >5MB are automatically cached for faster repeat access.

---

## 🎯 Search Strategies

### Finding a Specific Word

**Problem**: You want to find all instances of "love" (minne)

**Solution**:
1. Use **Main Site** for quick search
2. Type: `minne`
3. Click on results to read context
4. Note: Also finds variants like "mynne", "minnen"

### Researching a Concept

**Problem**: You're researching how "friendship" is discussed

**Solution**:
1. Use **Playground** → "Konzepte anzeigen"
2. Search: `Freundschaft`
3. Find concept ID
4. Use **Multi-Lemma Search** to find related words

### Comparing Two Authors

**Problem**: Compare how Meister Eckhart vs. Mechthild use "got" (God)

**Solution**:
1. **Main Site**: Filter by author "Meister Eckhart"
2. Search "got"
3. Note frequency and contexts
4. Change filter to "Mechthild"
5. Compare results

### Finding Co-Occurring Concepts

**Problem**: Where do "bread" and "wine" appear together? (Eucharist research)

**Solution**:
1. **Playground** → "Multi-Lemma-Suche (Absatz)"
2. Enter: `brôt + wîn`
3. Find all paragraphs discussing both
4. Or use **Proximity Search** for tighter co-occurrences

### Exploring Orthographic Variation

**Problem**: How many different spellings of "vriunt" exist?

**Solution**:
1. **Playground** → "Lemmata anzeigen"
2. Search: `vriunt`
3. See canonical form + all 100+ variants
4. Note: System automatically finds all variants when searching

---

## 📊 Understanding Results

### Search Result Anatomy

```
Lemma: vriunt (noun, masculine)
Meaning: friend, lover
Variants: vrivnt, vrūnt, friunt, vriwnt (47 total)
Occurrences: 1,234 instances in 89 texts
```

**What this means**:
- **Lemma**: The "dictionary form" used by scholars
- **Part of speech**: Grammar category
- **Meaning**: English translation or definition
- **Variants**: Different historical spellings found in corpus
- **Occurrences**: Total count of all forms combined

### Text Display

When you open a text, you'll see:

```
[Text metadata at top]
Title: Von der Abgeschiedenheit
Author: Meister Eckhart
Date: ca. 1300

[Highlighted text below]
Ein meister sprichet: swer dâ wil vinden einen güten vriunt,
der muoz sich vor lützel dingen kêren.
                                    ^^^^^^^^ (highlighted)
```

- **Yellow highlight**: Your search term
- **Line numbers**: For citation
- **Context**: Full paragraph for understanding

### Multi-Lemma Results

```
Paragraph #3 from "Predigt 52" (Meister Eckhart):

Daz brôt, daz ich iʒʒe, ist mîn lîp, und der wîn, den ich trinke...
    ^^^^                                    ^^^^
  (yellow)                                 (blue)
```

- **Multiple colors**: Each searched word has its own color
- **Context**: Shows how words relate in medieval usage

---

## 💡 Tips & Tricks

### Spelling Matters (But Not Really!)

Middle High German has **no standardized spelling**. Good news: MHDBDB handles this!

**You can search**:
- Modern spelling: `brot` → finds `brôt`, `brott`, `broht`
- Historical spelling: `brôt` → finds all variants
- Partial spelling: `bro` → finds words starting with "bro"

**Special characters** (â, ô, ü):
- You can type them: `brôt`
- Or skip them: `brot`
- Both work identically!

### Using the Cache

**What is caching?**
- Your browser stores downloaded data locally
- Makes subsequent visits **instant**

**When to clear cache**:
- Data seems outdated
- Search results look wrong
- After project updates

**How to clear**:
1. Main Site: Click 🗑️ "Clear Cache" button
2. Playground: Browser DevTools → Application → IndexedDB → Delete

**Cache size**: ~22 MB (indices) + ~50-200 MB (texts you've opened)

### Keyboard Shortcuts

(Planned feature - not yet implemented)

### Working Offline

**After first visit**:
- Indices are cached (you can search offline!)
- Individual texts load on-demand (need internet)

**Full offline use**:
- Not currently supported
- Contact developers if this is important for your research

### Citation

When citing MHDBDB texts, include:

```
[Author], [Title], MHDBDB TEI Repository,
https://mhdbdb.plus.ac.at, [Text ID], [Line numbers]
```

**Example**:
```
Meister Eckhart, Predigt 52, MHDBDB TEI Repository,
https://mhdbdb.plus.ac.at, ECK_PR_52, lines 15-18
```

---

## ❓ Frequently Asked Questions

### General

**Q: Is MHDBDB free to use?**
A: Yes! Licensed under CC BY-NC-SA 3.0 AT (free for non-commercial research).

**Q: Can I download the entire corpus?**
A: Yes, clone the GitHub repository: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only

**Q: How often is the corpus updated?**
A: Updates are irregular. Check the GitHub repository for latest changes.

**Q: Which browsers are supported?**
A: Chrome 90+, Firefox 100+, Safari 14+, Edge 90+ (Chrome recommended).

### Searching

**Q: Why does my search return no results?**
A:
1. Check spelling (try simpler form, e.g., "got" not "gottes")
2. Try without special characters (`brot` not `brôt`)
3. Search in "Lemmata anzeigen" to see if word exists

**Q: How do I search for phrases?**
A: Use Multi-Lemma Search:
- "Absatz" mode finds paragraphs with all words
- "Nähe" mode finds words near each other

**Q: Can I search by meaning (semantic search)?**
A: Not directly. Use "Konzepte anzeigen" to explore semantic categories, then search related lemmata.

**Q: Why are there so many spelling variants?**
A: Middle High German had no spelling standard! Each scribe spelled phonetically.

### Technical

**Q: Why is the first load slow?**
A: The browser downloads 22 MB of compressed indices. Subsequent visits are instant (cached).

**Q: What is IndexedDB?**
A: Browser storage for large data. Allows offline caching.

**Q: My browser says "Storage quota exceeded"**
A: Clear cache or use a browser with larger quota (Chrome has best support).

**Q: Can I use MHDBDB on mobile?**
A: Basic functionality works, but site is optimized for desktop (min 1200px width).

### Research

**Q: How accurate are the annotations?**
A: Annotations are manually curated by MHDBDB scholars. See project documentation for methodology.

**Q: Can I suggest corrections?**
A: Yes! Email mhdbdb@plus.ac.at or open a GitHub issue.

**Q: How do I export search results?**
A: Currently not supported. Feature planned for future release.

**Q: Can I save my searches?**
A: Not yet implemented. Bookmark specific result URLs (coming soon).

### Advanced

**Q: What is XPath and should I use it?**
A: XPath is an XML query language. Use only if you're familiar with TEI-XML structure.

**Q: Can I upload non-TEI files?**
A: No. Files must be valid TEI P5 XML.

**Q: How do I create my own TEI files?**
A: See TEI Guidelines: https://tei-c.org/guidelines/

**Q: Can I integrate MHDBDB into my own project?**
A: Yes! All code is open-source. See DEVELOPER-GUIDE.md for API documentation.

---

## 📧 Getting Help

### Documentation

- **This guide**: User-friendly overview
- **[SEARCH-GUIDE.md](./SEARCH-GUIDE.md)**: Detailed search documentation
- **[FAQ.md](./FAQ.md)**: Extended frequently asked questions
- **[GLOSSARY.md](./GLOSSARY.md)**: MHG terminology explained

### Support Channels

- **Email**: mhdbdb@plus.ac.at (research questions)
- **GitHub Issues**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues (technical problems)
- **Feedback**: We welcome suggestions for improvements!

### Reporting Bugs

If something doesn't work:

1. Check browser console (F12 → Console tab)
2. Take a screenshot
3. Open GitHub issue with:
   - What you were trying to do
   - What happened instead
   - Browser version
   - Console error messages

---

## 🎓 Learning Resources

### Middle High German

- **Grammar**: "Mittelhochdeutsche Grammatik" (Paul/Wiehl/Grosse)
- **Dictionary**: "Mittelhochdeutsches Wörterbuch" (Lexer)
- **Online**: https://www.mhdbdb.sbg.ac.at

### TEI (Text Encoding Initiative)

- **TEI Guidelines**: https://tei-c.org/guidelines/
- **TEI by Example**: https://teibyexample.org/

### Digital Humanities

- **Programming Historian**: https://programminghistorian.org/
- **DH Resources**: Your university library

---

## 🏆 Best Practices

### For Efficient Research

1. **Start simple**: Use Main Site first, then Playground if needed
2. **Explore variants**: Don't assume one spelling - check "Lemmata anzeigen"
3. **Use filters**: Narrow results by author/genre before searching
4. **Read context**: Always check full paragraph, not just highlighted word
5. **Cross-reference**: Verify findings in multiple texts

### For Accurate Citations

1. **Record**: Text ID, author, title, line numbers
2. **Verify**: Check original TEI file if uncertain
3. **Cite version**: Include access date and repository URL
4. **Credit**: Acknowledge MHDBDB in your publications

### For Collaboration

1. **Share queries**: Document your search strategy
2. **Export findings**: Copy-paste results into your notes
3. **Discuss**: Contact MHDBDB team with research questions
4. **Contribute**: Suggest improvements or corrections

---

## 🎯 Next Steps

### Beginner Path

1. ✅ Read this guide
2. ⏭️ Try Main Site search with a simple word (e.g., "got")
3. ⏭️ Explore Playground "Lemmata anzeigen"
4. ⏭️ Try Multi-Lemma search with 2 words
5. ⏭️ Read SEARCH-GUIDE.md for advanced techniques

### Advanced Path

1. ✅ Read this guide
2. ⏭️ Read DEVELOPER-GUIDE.md
3. ⏭️ Clone GitHub repository
4. ⏭️ Upload your own TEI files
5. ⏭️ Experiment with XPath queries
6. ⏭️ Contribute improvements via pull requests

---

**Welcome to MHDBDB! Happy researching! 📚**

---

**Last Updated**: 2025-10-01
**Version**: 1.0
**License**: CC BY-NC-SA 3.0 AT
**Contact**: mhdbdb@plus.ac.at

**Navigation**: [↑ Docs Index](./README.md) | [→ Search Guide](./SEARCH-GUIDE.md) | [→ FAQ](./FAQ.md)
