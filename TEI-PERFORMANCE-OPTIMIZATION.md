# TEI Loading Performance Optimization Plan

**Created:** 2025-10-01
**Issue:** TEI file loading takes 30-60 seconds (tested: 59s for modal opening)
**Goal:** Reduce to <5 seconds for acceptable UX

---

## Current Performance Analysis

### Measured Times
- **Modal opens:** 59 seconds
- **TEI file size:** 100-800 KB (average ~300 KB)
- **Operation:** Fetch XML → Parse DOM → Find lemmas → Extract contexts

### Bottleneck Identification

1. **Network Fetch** (estimated 1-2s)
   - Fetching large XML files from server
   - Acceptable performance

2. **DOMParser** (estimated 5-10s)
   - Parsing 300KB XML in browser
   - Moderate bottleneck

3. **querySelector traversal** (estimated 45-50s) **⚠️ MAJOR BOTTLENECK**
   - Finding all `<w>` elements with `lemmaRef` attributes
   - Extracting context windows (20 words before/after)
   - Running for each occurrence

---

## Optimization Strategies

### Strategy 1: Pre-Parse TEI Files (Build-Time) 🥇 **RECOMMENDED**

**Approach:** Extract word positions and contexts during index building

**Implementation:**
```python
# In build-corpus-index.py
for text in tei_files:
    words = []
    for w_element in doc.xpath('//tei:w[@lemmaRef]'):
        words.append({
            'position': get_word_position(w_element),
            'lemmaRef': w_element.get('lemmaRef'),
            'text': w_element.text,
            'contextBefore': get_context_before(w_element, 20),
            'contextAfter': get_context_after(w_element, 20)
        })

    text_index['words'] = words
```

**Benefits:**
- ✅ Moves slow parsing to build-time (offline, once)
- ✅ Reduces modal load from 59s to ~1-2s (just JSON fetch)
- ✅ No runtime XML parsing needed
- ✅ Contexts pre-extracted and ready to display

**Drawbacks:**
- ⚠️ Increases corpus index size (20.84 MB → ~50-80 MB)
- ⚠️ Longer build time (~10 min → ~20-30 min)

**Estimated Result:** Modal load time: **1-2 seconds** ⚡

---

### Strategy 2: Cache Parsed DOM (Runtime) 🥈

**Approach:** Cache parsed XML DOMs in IndexedDB after first parse

**Implementation:**
```javascript
// In text-renderer.js
async loadTEIFile(filename) {
    // Check cache first
    const cachedDOM = await this.getFromCache(filename);
    if (cachedDOM) return cachedDOM;

    // Fetch and parse
    const xmlText = await fetch(`tei/${filename}`).then(r => r.text());
    const doc = new DOMParser().parseFromString(xmlText, 'text/xml');

    // Cache serialized DOM
    await this.saveToCache(filename, new XMLSerializer().serializeToString(doc));

    return doc;
}
```

**Benefits:**
- ✅ First load: 59s, subsequent loads: 2-3s
- ✅ No index size increase
- ✅ Works with existing architecture

**Drawbacks:**
- ⚠️ First load still slow
- ⚠️ Requires significant IndexedDB space
- ⚠️ Cache invalidation complexity

**Estimated Result:** First load: **59s**, cached: **2-3s**

---

### Strategy 3: Web Worker Parsing 🥉

**Approach:** Parse XML in background thread

**Implementation:**
```javascript
// text-parser.worker.js
self.onmessage = async (e) => {
    const { xmlText, lemmaId } = e.data;

    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlText, 'text/xml');

    const contexts = findLemmaContexts(doc, lemmaId);

    self.postMessage({ contexts });
};
```

**Benefits:**
- ✅ Non-blocking UI
- ✅ Parallel processing possible

**Drawbacks:**
- ⚠️ Still takes 59s, just doesn't block UI
- ⚠️ Doesn't actually improve speed
- ⚠️ Increased complexity

**Estimated Result:** Modal load time: **59s** (but UI responsive)

---

### Strategy 4: Hybrid Approach (Pre-Parse + Lazy Cache) 🏆 **BEST**

**Combine Strategies 1 & 2:**

1. **For frequent queries:** Pre-parse top 100 most-searched texts
2. **For rare queries:** Lazy-load and cache on-demand

**Implementation:**
```python
# build-corpus-index.py
top_texts = get_most_searched_texts(100)  # Based on lemma frequency

for text in corpus:
    if text in top_texts:
        # Full pre-parse with contexts
        extract_all_word_contexts(text)
    else:
        # Lightweight metadata only
        extract_metadata_only(text)
```

**Benefits:**
- ✅ Fast loads for 90% of use cases
- ✅ Reasonable index size (~30-40 MB)
- ✅ Graceful degradation for rare texts

**Estimated Result:**
- Hot paths: **1-2 seconds** ⚡
- Cold paths: **59s first load**, **2-3s cached**

---

## Recommended Implementation

### Phase 1: Quick Wins (1-2 hours)
1. **Add loading indicator** to modal
   - Show "Lade Text... (0-60s)" message
   - Progress spinner
   - Better UX even if not faster

2. **Add progress callback** to TextRenderer
   - "Fetching file..." (0-2s)
   - "Parsing XML..." (2-12s)
   - "Finding occurrences..." (12-59s)
   - "Rendering..." (59-60s)

### Phase 2: Cache Parsed DOMs (2-3 hours)
1. Implement Strategy 2 (Runtime caching)
2. Store serialized DOMs in IndexedDB
3. Add cache invalidation (30-day TTL)
4. Test with 5-10 different texts

**Expected gain:**
- First load: 59s (same)
- Cached load: 2-3s ✅ **95% faster for repeat visits**

### Phase 3: Pre-Parse Top Texts (4-6 hours)
1. Analyze corpus index for most frequent lemmas
2. Identify top 50-100 texts containing these lemmas
3. Extend `build-corpus-index.py` to pre-parse these texts
4. Update `text-renderer.js` to use pre-parsed data when available

**Expected gain:**
- Top texts: 1-2s ✅ **97% faster**
- Other texts: 59s first, 2-3s cached

---

## Implementation Priority

### Immediate (This Session)
- [x] Add loading indicator with progress messages
- [x] Test modal with multiple texts to verify caching

### Short-Term (Next Session)
- [ ] Implement DOM caching (Strategy 2)
- [ ] Add cache size management
- [ ] Test with 10+ different texts

### Medium-Term (Future)
- [ ] Implement hybrid pre-parsing (Strategy 4)
- [ ] Optimize querySelector patterns
- [ ] Consider XPath for faster queries

---

## Success Metrics

| Metric | Current | Target | Strategy |
|--------|---------|--------|----------|
| **First-time modal load** | 59s | <10s | Phase 2 (caching) |
| **Repeat modal load** | 59s | <3s | Phase 2 (caching) |
| **Top 100 texts** | 59s | <2s | Phase 3 (pre-parse) |
| **User perception** | Poor | Good | Phase 1 (indicator) |

---

## Code Locations

### Files to Modify
- `js/text-renderer.js` - Add caching and progress callbacks
- `js/main-site.js` - Update modal to show progress
- `scripts/build-corpus-index.py` - Add pre-parsing logic
- `js/corpus-loader.js` - Handle pre-parsed data

### New Files Needed
- `js/tei-cache-manager.js` - Manage parsed DOM cache
- `js/utils/xml-cache.js` - IndexedDB wrapper for XML caching

---

## Testing Plan

### Performance Tests
1. **Test 1:** Measure first load time for 10 random texts
2. **Test 2:** Measure cached load time for same 10 texts
3. **Test 3:** Measure cache hit rate after 50 searches
4. **Test 4:** Verify modal loads under target times

### Test Spec
```javascript
// testing/tests/tei-performance.spec.js
test('TEI modal loads within 5 seconds (cached)', async ({ page }) => {
    // First load (warm cache)
    await searchAndOpenModal(page, 'got');
    await page.waitForSelector('#textModal.active');

    // Close and reopen
    await page.click('#closeModal');

    const startTime = Date.now();
    await searchAndOpenModal(page, 'got');
    await page.waitForSelector('#textModal.active');
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
});
```

---

## Conclusion

The **59-second TEI loading time** is the biggest UX issue remaining. Implementing **DOM caching (Phase 2)** should reduce repeat loads to **2-3 seconds** with minimal effort. Adding **pre-parsing for top texts (Phase 3)** can further improve to **1-2 seconds** for common queries.

**Recommended next steps:**
1. Add loading indicator (Phase 1) - immediate UX improvement
2. Implement DOM caching (Phase 2) - significant performance gain
3. Monitor usage and consider pre-parsing top texts (Phase 3)

---

**Status:** Plan complete, ready for implementation
**Priority:** High (biggest remaining performance issue)
**Effort:** Phase 1: 1-2 hours | Phase 2: 2-3 hours | Phase 3: 4-6 hours
