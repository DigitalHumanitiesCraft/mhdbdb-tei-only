# Comprehensive Plan: Fix Proximity Search by Removing Paragraph Logic

## Problem Analysis

The current corpus index building logic **only indexes words inside `<p>` and `<lg>` elements**, but TEI files contain `<w>` elements in OTHER locations like:
- `<head>` elements (109 words in ABS.tei.xml alone!)
- Potentially `<div>`, `<ab>`, `<l>`, and other TEI structures

### Evidence
**ABS.tei.xml word distribution:**
- Words in `<head>`: **109 words** ❌ NOT INDEXED
- Words in `<p>`: 3,255 words ✅ indexed
- Total in `<body>`: 3,364 words
- **Missing: 109 words (3.2%)**

This causes **position mismatches** between:
- **Python corpus index**: Only indexes 3,255 words (missing 109) → wrong positions
- **JavaScript TEI parsing**: Gets all 3,364 words → different positions

**Result**: Proximity search extracts context from **completely wrong positions** → 0/2 searched lemmas found in extracted context

---

## Solution: Simplify to Document-Level Indexing

Remove paragraph-based logic entirely and use **flat document-level word indexing**:
- Index ALL `<w lemmaRef>` elements in `<body>` in document order
- Remove paragraph metadata (no longer needed)
- Keep only: `words[]` array and `lemmata{}` positions
- Support **proximity search** and **document context** only (no paragraph context)

---

## Implementation Steps

### 1. **Update Python: Build Simplified Corpus Index**
**File:** `scripts/build-corpus-index.py`

**Current logic (WRONG):**
```python
# Line 164: Only selects <p> and <lg> - MISSES words in <head>, etc.
paragraph_els = tree.xpath('//tei:body//tei:p | //tei:body//tei:lg', namespaces=ns)

for para_el in paragraph_els:
    word_els = para_el.xpath('.//tei:w[@lemmaRef]', namespaces=ns)
    # ... iterate words
```

**New logic (CORRECT):**
```python
# Get ALL words in <body> in document order
word_els = tree.xpath('//tei:body//tei:w[@lemmaRef]', namespaces=ns)

words = []
lemmata = defaultdict(list)

for word_el in word_els:
    lemma_ref = word_el.get('lemmaRef')
    # ... extract lemma ID
    word_idx = len(words)
    words.append(lemma_id)
    lemmata[lemma_id].append(word_idx)
```

**Changes:**
- Remove paragraph iteration logic (lines 163-205)
- Use single XPath: `tree.xpath('//tei:body//tei:w[@lemmaRef]', namespaces=ns)`
- Build flat arrays:
  - `words = [lemma_879, lemma_123, ...]` (ALL words in body)
  - `lemmata = {lemma_879: [0, 15, 234], ...}` (position indices)
- **Remove `paragraphs` array entirely**
- Update JSON structure:
  ```json
  {
    "version": "4.0.0",
    "texts": [
      {
        "filename": "ABS.tei.xml",
        "words": ["lemma_879", "lemma_123", ...],  // ALL words
        "lemmata": {"lemma_879": [0, 15, 234], ...}
        // NO paragraphs array
      }
    ]
  }
  ```
- Update version to `4.0.0` (breaking change)

### 2. **Update JavaScript: Remove Paragraph Search**
**Files:**
- `playground/js/data/tei-manager.js`
  - Remove `searchMultipleLemmas()` paragraph mode
  - Keep only proximity and document modes

- `playground/js/ui/tei/multi-lemma-search.js`
  - Remove paragraph radio button from HTML
  - Remove paragraph context handling

- `playground/js/ui/tei/tei-ui.js`
  - Remove paragraph display logic
  - Keep proximity and document displays

**Keep:**
- ✅ Proximity search (distance-based)
- ✅ Document context (file list only)
- ❌ Remove paragraph context entirely

### 3. **Update JavaScript: Fix TEI Word Extraction**
**File:** `playground/js/ui/core/ui-helpers.js`

**Current (complex paragraph iteration):**
```javascript
// Lines 369-394: Iterates through paragraphs, then words
const paragraphsResult = doc.evaluate('//tei:body//tei:p | //tei:body//tei:lg', ...);
for (let i = 0; i < paragraphsResult.snapshotLength; i++) {
  const para = paragraphsResult.snapshotItem(i);
  const wordsInPara = doc.evaluate('.//tei:w[@lemmaRef]', para, ...);
  // ...
}
```

**New (simple, matches Python):**
```javascript
// Single XPath matching Python exactly
const nsResolver = () => 'http://www.tei-c.org/ns/1.0';
const xpathResult = doc.evaluate(
  '//tei:body//tei:w[@lemmaRef]',
  doc,
  nsResolver,
  XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
  null
);

const words = [];
for (let i = 0; i < xpathResult.snapshotLength; i++) {
  words.push(xpathResult.snapshotItem(i));
}

// Direct position slicing
const contextWords = words.slice(result.contextStart, result.contextEnd);
```

### 4. **Update Cache Version**
**File:** `lib/corpus-loader.js`
- Change line 8: `const INDEX_VERSION = '4.0.0';` (force cache invalidation)
- Update comment: `// Bumped for document-level indexing (removed paragraph logic)`

### 5. **Rebuild Corpus Index**
```bash
python scripts/build-corpus-index.py
```

**Expected changes:**
- ✅ Indexes ALL words in `<body>` (including `<head>`)
- ✅ Smaller file size (no paragraph metadata) - estimate: ~30 MB compressed (vs 37 MB)
- ✅ Faster processing (single XPath instead of paragraph iteration)
- ✅ Correct word positions

### 6. **Update UI Labels and Documentation**
- Remove "Absatz" (paragraph) option from multi-lemma search modal
- Update `CLAUDE.md` to reflect simplified architecture
- Update German/English labels:
  - Keep: "Nähe" (proximity), "Dokument" (document)
  - Remove: "Absatz" (paragraph)

---

## Benefits

✅ **Fixes proximity search** - positions will finally align between Python and JavaScript!
✅ **Simpler architecture** - no paragraph logic to maintain
✅ **Complete word coverage** - indexes ALL words in `<body>`, not just `<p>/<lg>`
✅ **Smaller index** - no paragraph metadata (saves ~20%)
✅ **Faster processing** - single XPath instead of paragraph iteration
✅ **More maintainable** - one source of truth for word ordering

---

## Files to Modify

1. ✏️ `scripts/build-corpus-index.py` - Simplified extraction logic (remove paragraph iteration)
2. ✏️ `lib/corpus-loader.js` - Bump cache version to 4.0.0
3. ✏️ `playground/js/data/tei-manager.js` - Remove paragraph search mode
4. ✏️ `playground/js/ui/core/ui-helpers.js` - Simplified TEI word extraction
5. ✏️ `playground/js/ui/tei/multi-lemma-search.js` - Remove paragraph radio button
6. ✏️ `playground/js/ui/tei/tei-ui.js` - Remove paragraph display logic
7. 🔄 `data/corpus-index.json.gz` - Rebuild with new Python script

---

## Testing Plan

After implementation:

1. **Rebuild index**: `python scripts/build-corpus-index.py`
2. **Clear browser cache**: Hard refresh (Ctrl+Shift+R)
3. **Test proximity search**: Search "brot + win" with 10 words distance
4. **Verify results**: Click expand on results, check console logs
   - Should see: `🎯 Found 2/2 searched lemmas in context`
   - Should show: Highlighted "brott" and "win" in results
5. **Test document context**: Verify file list shows correctly
6. **Cross-check**: Compare a few results manually with TEI files

---

## Rollback Plan

If issues arise:
1. Restore `INDEX_VERSION = '3.0.1'` in corpus-loader.js
2. Restore old corpus-index.json.gz from git history
3. Revert JavaScript changes
4. User will get old (broken) behavior but at least it's stable
