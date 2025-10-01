# MHDBDB Frequently Asked Questions

**Quick answers to common questions**

---

## 📋 Table of Contents

1. [General](#general)
2. [Technical](#technical)
3. [Searching](#searching)
4. [Data & Content](#data--content)
5. [Research & Academic Use](#research--academic-use)
6. [Troubleshooting](#troubleshooting)

---

## 🌐 General

### What is MHDBDB?

**MHDBDB** (Mittelhochdeutsche Begriffsdatenbank) is a digital research database providing:
- 666 TEI-encoded Middle High German texts
- 43,750 dictionary entries (lemmata)
- 176,056 orthographic variant mappings
- Semantic annotations (concepts, persons, works, genres)

**Project Home**: https://www.mhdbdb.sbg.ac.at
**GitHub Repository**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only

---

### Who created MHDBDB?

**Institution**: University of Salzburg (Universität Salzburg), Austria
**Project**: Mittelhochdeutsche Begriffsdatenbank
**Contact**: mhdbdb@plus.ac.at

**Project Team**: Medieval studies and digital humanities scholars at the Department of German Studies, University of Salzburg.

---

### Is MHDBDB free to use?

**Yes!** MHDBDB is licensed under **CC BY-NC-SA 3.0 AT**:
- ✅ **Free** for non-commercial use
- ✅ **Free** for academic research
- ✅ **Free** for educational purposes
- ⚠️ **Attribution required** (cite MHDBDB in publications)
- ⚠️ **Share-alike** (derivative works must use same license)
- ❌ **No commercial use** without permission

**Full License**: https://creativecommons.org/licenses/by-nc-sa/3.0/at/

---

### Can I download the entire corpus?

**Yes!** The full corpus is available on GitHub:

```bash
git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git
cd mhdbdb-tei-only
```

**Contents**:
- `tei/` - 666 TEI XML files
- `authority-files/` - 7 reference vocabularies
- `data/` - Pre-built indices (compressed)
- Full source code for web interface

**Size**: ~250 MB total

---

### Which browsers are supported?

**Fully Supported**:
- ✅ Chrome 90+ (Recommended)
- ✅ Firefox 100+
- ✅ Safari 14+
- ✅ Edge 90+

**Minimum Requirements**:
- JavaScript enabled
- IndexedDB support
- 1200px screen width (desktop-focused)

**Not Supported**:
- Internet Explorer (discontinued)
- Mobile browsers (basic functionality may work, but not optimized)

---

### Is MHDBDB mobile-friendly?

**Not currently.** MHDBDB is optimized for desktop research:
- Minimum width: 1200px
- Complex UI not suited for small screens
- Large data downloads (~22 MB indices)

**iPad/Tablet**: May work in landscape mode with Safari/Chrome.

**Future Plans**: Mobile optimization is on the roadmap but not a current priority.

---

### How often is MHDBDB updated?

**Irregularly.** Updates depend on:
- New texts added to corpus
- Annotation improvements
- Bug fixes
- Feature additions

**How to check for updates**:
- GitHub releases: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/releases
- Clear browser cache if data seems outdated

---

## 💻 Technical

### What technologies does MHDBDB use?

**Frontend**:
- Vanilla JavaScript (ES6+ modules)
- Tailwind CSS (styling)
- No React/Vue/Angular (lightweight!)

**Storage**:
- IndexedDB (via Dexie.js wrapper)
- Browser caching (30-day TTL)

**Data Formats**:
- TEI P5 XML (texts)
- JSON.gz (pre-built indices)
- Gzip compression (Pako.js library)

**Hosting**:
- Static files only (no backend)
- Works on any HTTP server

---

### Why is the first load slow?

**First Visit**: 3-5 seconds to download 22 MB of compressed indices:
- `authority-index.json.gz` (1.27 MB)
- `corpus-index.json.gz` (20.84 MB)

**Subsequent Visits**: Instant! Data cached in IndexedDB.

**Why not smaller?**
- Corpus has 666 texts with 7.4 million words
- Authority files have 43,750 lemmata + 176,056 variants
- Pre-built indices enable fast search (no server needed)

**Optimization**: Use a good internet connection for first load. After that, works offline!

---

### What is IndexedDB?

**IndexedDB** is browser storage for large data (similar to a database).

**Why MHDBDB uses it**:
- Store 22 MB+ of indices
- Cache parsed TEI XML DOMs
- Persist data across browser sessions
- Much larger quota than localStorage/sessionStorage

**How to clear IndexedDB**:
1. Main Site: Click 🗑️ "Clear Cache" button
2. Manual: Browser DevTools → Application → IndexedDB → Delete

---

### Why do I get "Quota exceeded" errors?

**Cause**: Your browser's storage quota is full.

**Solutions**:

1. **Clear other site data**:
   - Browser Settings → Privacy → Clear browsing data
   - Select "Cookies and site data"

2. **Use Chrome**: Has best IndexedDB quota (~60% of available disk)

3. **Free up disk space**: IndexedDB quota based on available disk space

4. **Clear MHDBDB cache**:
   - Click 🗑️ button in header
   - Or DevTools → Application → IndexedDB → mhdbdb → Delete

---

### Can MHDBDB work offline?

**Partially:**
- ✅ **Indices**: Cached after first visit (search works offline!)
- ✅ **Opened texts**: Cached after first view
- ❌ **New texts**: Require internet to load
- ❌ **Updates**: Require internet to fetch

**For full offline use**:
1. Visit site online first
2. Let indices load and cache
3. Open all texts you need (they cache automatically)
4. Then you can work offline!

---

### Does MHDBDB collect my data?

**No personal data collection.**

**What is stored** (locally in your browser only):
- Cached indices
- Opened TEI texts
- No tracking cookies
- No analytics (in current version)

**Your searches are private** - nothing is sent to servers.

---

## 🔍 Searching

### Why does my search return no results?

**Common causes**:

1. **Typo or wrong spelling**:
   - Try simpler form: `got` instead of `gottes`
   - Use "Lemmata anzeigen" to verify spelling

2. **Lemma doesn't exist**:
   - Check "Lemmata anzeigen" - if not there, not in corpus

3. **Too specific**:
   - Inflected forms may not match
   - Use root form (infinitive for verbs, nominative for nouns)

4. **Multi-lemma search**: All terms must exist
   - Try individual searches first
   - Verify each lemma exists

5. **Cache corruption**:
   - Clear cache and reload

---

### How do I search for phrases?

**MHDBDB doesn't support phrase search** (e.g., "holy spirit" as exact sequence).

**Workarounds**:

1. **Multi-Lemma Proximity Search**:
   - Search: `heilig + geist`
   - Mode: Nähe (proximity)
   - Distance: 1-2 words
   - Finds most phrase-like occurrences

2. **XPath Query** (advanced):
   ```xpath
   //tei:p[.//tei:w[@lemma='heilig']
          /following-sibling::tei:w[1][@lemma='geist']]
   ```

3. **Manual filtering**:
   - Use paragraph search
   - Read results to find exact phrases

---

### Can I search by meaning (semantic search)?

**Not directly.** MHDBDB searches lemmata (word forms), not meanings.

**Workarounds**:

1. **Concept taxonomy**:
   - "Konzepte anzeigen" → find semantic category
   - Note related lemmata
   - Search those lemmata

2. **Multi-lemma search with synonyms**:
   - Find synonyms in "Lemmata anzeigen"
   - Search: `minne + liebe + kärlich` (all mean "love")

3. **XPath with @ana attribute**:
   - Find concept ID: `concept_456`
   - XPath: `//tei:w[@ana='concept_456']`

**Future**: Semantic search is planned but not yet implemented.

---

### Why are there so many spelling variants?

**Middle High German had no standardized orthography!**

**Reasons for variation**:
- Different scribes, different spellings
- Regional dialects
- Time periods (1050-1350)
- Individual manuscripts
- Phonetic spelling (each scribe spelled what they heard)

**Example**: "friend" has 47+ attested variants:
- vriunt, vrivnt, vrūnt, friunt, vriwnt, vriend, vrunt, vrount, ...

**MHDBDB solution**: Variants index maps all forms to canonical lemma.

---

### How do I know which spelling to search?

**You don't need to!** MHDBDB handles variants automatically.

**Recommendation**:
1. Check "Lemmata anzeigen" first
2. Find canonical form (e.g., `vriunt`)
3. Use canonical form in searches
4. System automatically finds all variants

**Or**: Just search any spelling you know - system resolves it!

---

### What's the difference between paragraph and document search?

**Multi-Lemma-Suche (Absatz)** - Paragraph-level:
- Finds **paragraphs** where ALL lemmata appear
- Tighter results
- Shows co-occurrence in same context
- Good for: Discourse analysis, concept relationships

**Multi-Lemma-Suche (Dokument)** - Document-level:
- Finds **texts** where ALL lemmata appear (anywhere)
- Broader results
- Shows which texts discuss multiple topics
- Good for: Topic modeling, text selection

**Example**:
```
Search: "brôt + wîn"

Paragraph mode:
- Returns 50 paragraphs across 25 texts
- Both words in same paragraph

Document mode:
- Returns 120 texts
- Both words somewhere in text (may be pages apart)
```

---

### How many words can I search at once?

**Technical limit**: 10 lemmata

**Practical limit**: 3-5 lemmata
- Performance degrades with more terms
- Fewer results (more specific)
- Slower queries

**Recommendation**:
- Start with 2-3 most important lemmata
- Narrow down results
- Add more terms if needed

---

## 📚 Data & Content

### How many texts are in MHDBDB?

**666 texts** from Middle High German literature (ca. 1050-1350)

**Size**:
- ~7.4 million words total
- ~11,100 words per text (average)
- Largest: ~500,000 words
- Smallest: ~500 words

---

### What genres are included?

**Major genres**:
- Mystical writings (Meister Eckhart, Mechthild von Magdeburg)
- Sermons (Predigten)
- Religious prose
- Theological treatises
- Spiritual literature

**Genre taxonomy**: 615 genre categories (see "Gattungen anzeigen")

**Note**: Corpus focuses on religious/mystical literature (not epic/courtly romance).

---

### Which authors are most represented?

**Top authors** (by text count):
1. Meister Eckhart (~86 sermons + treatises)
2. Mechthild von Magdeburg
3. David von Augsburg
4. Anonymous spiritual texts

**See**: "Autoren anzeigen" (Playground) for full list of 210 authors.

---

### Are translations provided?

**No.** MHDBDB provides Middle High German texts without modern German or English translations.

**Why?**
- Focus on original language research
- Semantic annotations provide context
- Translations would triple data size

**Workarounds**:
- Use "Lemmata anzeigen" for word meanings
- Consult external dictionaries (Lexer, BMZ)
- Academic MHG grammars and readers

---

### Can I upload my own texts?

**Yes!** (Playground only)

**Requirements**:
- Files must be valid TEI P5 XML
- Must include `@lemma` attributes on `<w>` elements (for lemma search)
- Must follow TEI namespace: `http://www.tei-c.org/ns/1.0`

**How**:
1. Open Playground
2. Click "Upload TEI Files" button
3. Select `.tei.xml` files
4. Wait for parsing
5. Your texts are now searchable!

**Limitations**:
- Large files (>5 MB) may be slow to parse
- Uploaded texts cached locally (not shared with other users)

---

### How accurate are the annotations?

**Authority files** (lemmata, concepts, etc.):
- Manually curated by MHDBDB scholars
- High quality
- Continuously refined

**TEI annotations** (`@lemma`, `@ana`):
- Mixed: Some texts fully annotated, others partial
- Ongoing project (not all 666 texts complete)
- Lemma accuracy varies by text

**Recommendation**: Verify critical findings manually in TEI files.

---

### Can I suggest corrections?

**Yes! Contributions welcome.**

**How to contribute**:
1. **Email**: mhdbdb@plus.ac.at (for content corrections)
2. **GitHub Issues**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues (for data/annotation errors)
3. **Pull Requests**: Fork repository, make changes, submit PR

**What to report**:
- Annotation errors (wrong lemma, wrong concept)
- Missing texts
- TEI encoding issues
- Orthographic variant gaps

---

## 🎓 Research & Academic Use

### How do I cite MHDBDB?

**General citation**:
```
Mittelhochdeutsche Begriffsdatenbank (MHDBDB), University of Salzburg,
https://mhdbdb.plus.ac.at (accessed YYYY-MM-DD).
```

**Specific text citation**:
```
[Author], [Title], in: Mittelhochdeutsche Begriffsdatenbank (MHDBDB),
University of Salzburg, https://mhdbdb.plus.ac.at/tei/[FILENAME].tei.xml,
[Line/Paragraph numbers] (accessed YYYY-MM-DD).
```

**Example**:
```
Meister Eckhart, Predigt 52, in: Mittelhochdeutsche Begriffsdatenbank (MHDBDB),
University of Salzburg, https://mhdbdb.plus.ac.at/tei/ECK_PR_52.tei.xml,
lines 15-18 (accessed 2025-10-01).
```

---

### Can I use MHDBDB in my thesis/dissertation?

**Yes!** MHDBDB is designed for academic research.

**Best practices**:
1. **Cite properly** (see above)
2. **Acknowledge limitations** (partial annotations, ongoing project)
3. **Verify critical data** (check TEI files manually)
4. **Note version** (include access date, as corpus may be updated)

**License**: CC BY-NC-SA 3.0 AT allows thesis use (non-commercial academic work).

---

### Can I publish research based on MHDBDB?

**Yes!** Please acknowledge MHDBDB in your publications.

**Suggested acknowledgment**:
> This research was conducted using the Mittelhochdeutsche Begriffsdatenbank
> (MHDBDB) provided by the University of Salzburg (https://mhdbdb.plus.ac.at).

**License compliance**:
- ✅ Academic publications (free use)
- ✅ Books/articles (non-commercial)
- ⚠️ Commercial publications (contact mhdbdb@plus.ac.at for permission)

---

### How do I export search results for analysis?

**Current method**: Manual copy-paste

**Not yet implemented**:
- ❌ CSV export
- ❌ JSON export
- ❌ Batch download

**Workarounds**:
1. **Copy-paste into spreadsheet**: Select results, copy, paste into Excel/Google Sheets
2. **Use XPath Query**: Returns structured data you can manually export
3. **Clone GitHub repo**: Download all TEI files, run custom scripts

**Future**: Export functionality planned for future release.

---

### Can I integrate MHDBDB into my digital project?

**Yes!** Code is open-source (see DEVELOPER-GUIDE.md).

**Integration options**:

1. **Link to MHDBDB**:
   - Easiest method
   - Link to specific texts or searches

2. **Clone repository**:
   - Host your own instance
   - Customize as needed

3. **Use API** (limited):
   - Load indices programmatically
   - See API-REFERENCE.md (developer docs)

4. **Fork and extend**:
   - Add new features
   - Submit pull requests back to main project

**License**: CC BY-NC-SA 3.0 AT (share-alike requirement applies).

---

## 🐛 Troubleshooting

### Site won't load / stuck loading

**Solutions**:

1. **Check internet connection**: First load requires download

2. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Delete → Clear data
   - Firefox: Ctrl+Shift+Delete → Clear data
   - Safari: Safari menu → Clear History

3. **Try different browser**: Chrome recommended

4. **Disable ad blockers**: May block CDN scripts

5. **Check console for errors**:
   - F12 → Console tab
   - Look for red errors
   - Report to GitHub Issues

---

### Search is slow / unresponsive

**Causes & solutions**:

1. **First corpus load** (expected):
   - 1-2 seconds to load corpus index
   - Wait for "Corpus loaded" message

2. **Large multi-lemma search**:
   - 5-10 seconds normal for corpus-wide search
   - Try document-level search first (faster)

3. **Low RAM / old device**:
   - Close other tabs
   - Restart browser
   - Upgrade hardware (MHDBDB uses ~100 MB RAM)

4. **Corrupted cache**:
   - Clear cache (🗑️ button)
   - Reload page

---

### Modal doesn't open / text won't display

**Checklist**:

1. ✅ **Wait for text to load** (large files take 10-30 seconds)
2. ✅ **Check browser console** (F12) for errors
3. ✅ **Try different text** (some may have encoding issues)
4. ✅ **Clear cache** (corrupted cache can break modals)
5. ✅ **Disable browser extensions** (some block modals)

**Still broken?**
- Report to GitHub Issues with:
  - Browser version
  - Text filename
  - Console errors

---

### Cache button shows wrong size / won't clear

**Solutions**:

1. **Refresh page**: Cache stats update on page load

2. **Manual clear**:
   - F12 → Application tab → IndexedDB
   - Right-click "mhdbdb" → Delete database

3. **Hard refresh**:
   - Chrome/Firefox: Ctrl+Shift+R
   - Safari: Cmd+Shift+R

---

### Special characters display incorrectly

**Cause**: Encoding issue (rare)

**Solutions**:

1. **Check browser encoding**:
   - Should be UTF-8
   - Browser menu → Encoding → UTF-8

2. **Update browser**: Older browsers may have encoding bugs

3. **Report issue**: If specific text has encoding problems

---

### XPath queries fail / return errors

**Common mistakes**:

1. **Missing TEI namespace**:
   - ❌ `//w[@lemma='got']`
   - ✅ `//tei:w[@lemma='got']`

2. **Invalid XPath syntax**:
   - Check parentheses, quotes, brackets
   - Use XPath tester: https://www.freeformatter.com/xpath-tester.html

3. **No text selected**:
   - XPath needs a text to query
   - Select text from dropdown first

4. **Queries too complex**:
   - Simplify query
   - Test parts individually

---

### "Out of memory" error

**Cause**: Browser ran out of RAM (rare)

**Solutions**:

1. **Close other tabs/applications**

2. **Reload page** (clears memory)

3. **Don't open too many large texts** at once

4. **Clear cache** (old cached texts may accumulate)

5. **Upgrade RAM** (MHDBDB can use up to 500 MB with many texts open)

---

## 📧 Still Need Help?

### Contact Options

**Email**: mhdbdb@plus.ac.at
- Research questions
- Content corrections
- General inquiries

**GitHub Issues**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues
- Bug reports
- Feature requests
- Technical problems

**Documentation**:
- [User Guide](./USER-GUIDE.md) - Getting started
- [Search Guide](./SEARCH-GUIDE.md) - Detailed search docs
- [Developer Guide](./DEVELOPER-GUIDE.md) - Technical docs

---

**Last Updated**: 2025-10-01
**Version**: 1.0

**Navigation**: [↑ Docs Index](./README.md) | [← User Guide](./USER-GUIDE.md) | [→ Glossary](./GLOSSARY.md)
