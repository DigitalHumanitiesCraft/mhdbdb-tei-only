# Cross-System Contracts

Technical contracts that bind Python (build-time) and JavaScript (runtime) together. Breaking any of these causes silent data corruption — search returns wrong results, highlights land on wrong words, or caches serve stale data.

**Why this document exists:** These constraints span multiple files and languages. No single module owns them. They are the most dangerous knowledge to lose because violations produce no error messages — just silently wrong behavior.

---

## A. MHG Normalization Parity

**Contract:** `scripts/mhg_normalizer.py` and `assets/js/lib/text-normalizer.js` MUST produce identical output for all inputs.

**Why:** Build scripts normalize lemma forms when creating the authority index. The browser normalizes user search input at runtime. If the two normalizations diverge, indexed terms won't match runtime queries — search appears broken with no error.

**Parity test:** `testing/tests/normalization-parity.spec.js`

### Transformation Rules (ordered — order matters)

| Step | Operation | Characters | Result | JS | Python |
|------|-----------|-----------|--------|-----|--------|
| 1 | Lowercase | all | lowercase | `.toLowerCase()` | `.lower()` |
| 2 | Long vowels (circumflex + macron) | â ā | a | `/[âā]/g` | `.replace('â','a').replace('ā','a')` |
| 2 | | ê ē | e | `/[êē]/g` | `.replace('ê','e').replace('ē','e')` |
| 2 | | î ī | i | `/[îī]/g` | `.replace('î','i').replace('ī','i')` |
| 2 | | ô ō | o | `/[ôō]/g` | `.replace('ô','o').replace('ō','o')` |
| 2 | | û ū | u | `/[ûū]/g` | `.replace('û','u').replace('ū','u')` |
| 3 | Umlauts → digraphs | ä | ae | `/ä/g` | `.replace('ä','ae')` |
| 3 | | ö | oe | `/ö/g` | `.replace('ö','oe')` |
| 3 | | ü | ue | `/ü/g` | `.replace('ü','ue')` |
| 4 | Ligatures | æ | ae | `/æ/g` | `.replace('æ','ae')` |
| 4 | | œ | oe | `/œ/g` | `.replace('œ','oe')` |
| 5 | Special | ǒ | o | `/ǒ/g` | `.replace('ǒ','o')` |

### Test Cases

These 17 cases must pass in both languages. Source: `scripts/mhg_normalizer.py:131-151`

| Input | Expected | Why |
|-------|----------|-----|
| `brôt` | `brot` | ô → o (circumflex, NOT umlaut) |
| `BRÔT` | `brot` | Uppercase + circumflex |
| `wîn` | `win` | î → i |
| `vriunt` | `vriunt` | No special characters — passthrough |
| `schône` | `schone` | ô → o (circumflex — NOT ö → oe) |
| `schöne` | `schoene` | ö → oe (actual umlaut) |
| `Âventiure` | `aventiure` | Uppercase Â → lowercase → a |
| `mære` | `maere` | æ → ae (ligature) |
| `âne` | `ane` | â → a |
| `fröude` | `froeude` | ö → oe |
| `müede` | `mueede` | ü → ue, existing e remains → "mueede" |
| `ûzer` | `uzer` | û → u |
| `ōre` | `ore` | ō → o (macron) |
| `sǒne` | `sone` | ǒ → o |
| `cæsar` | `caesar` | æ → ae |
| `œnologie` | `oenologie` | œ → oe |
| `''` | `''` | Empty string |
| `None`/`null` | `''` | Null handling |

### Common Pitfall

`schône` (ô = circumflex) → `schone`, NOT `schoene`. The circumflex ô maps to plain `o`, while the umlaut ö maps to `oe`. Visually similar, semantically different.

### Helper Functions (must also match)

| Purpose | Python | JavaScript |
|---------|--------|-----------|
| Contains (normalized) | `matches_normalized(text, search)` | `TextNormalizer.matchesNormalized(text, search)` |
| Exact match (normalized) | `exact_match_normalized(text, search)` | `TextNormalizer.exactMatchNormalized(text, search)` |
| Starts with (normalized) | `starts_with_normalized(text, search)` | `TextNormalizer.startsWithNormalized(text, search)` |

---

## B. Position Counting Contract

**Contract:** Python build scripts and JavaScript TEI renderer MUST assign identical word positions to each `<w>` element.

**Why:** The corpus index stores lemma positions as integers (e.g., lemma_879 appears at positions [0, 15, 42]). The reading view highlights words by matching these positions during DOM traversal. If Python counts position 42 differently than JavaScript, highlights land on the wrong word. Proximity search (`|pos_a - pos_b| <= maxDistance`) also breaks.

### Rules

1. **Only count `<w>` elements with `@lemmaRef` attribute**
2. `<w>` elements without `@lemmaRef` are **skipped** (not counted, not stored)
3. All other elements (`<pb>`, `<lb>`, `<seg>`, `<hi>`, text nodes, etc.) are **ignored** for counting
4. Counting starts at **0** for each document
5. Order = **document order** (depth-first traversal of `<body>`)

### Python (build-time)

Source: `scripts/build-corpus-index.py`

```
XPath: //tei:body//tei:w[@lemmaRef]
Position = index in result list (0, 1, 2, ...)

For each <w lemmaRef="lexicon.xml#lemma_X">:
    lemma_id = lemmaRef.split('#')[1]      → "lemma_X"
    word_text = ''.join(el.itertext()).strip()
    position = len(words)                   → sequential from 0
    words.append(lemma_id)
    lemmata[lemma_id].append(position)
```

### JavaScript (runtime)

Source: `assets/js/rendering/tei-text-reader.js:394-401, 509-515`

```
Recursive DOM traversal of <body> children:
    state = { wordPosition: 0 }

    For each element encountered:
        if tagName === 'w':
            hasLemmaRef = el.getAttribute('lemmaRef')
            processWord(el, ...)  // render + check highlight
            if (hasLemmaRef):
                state.wordPosition++   // ONLY increment when lemmaRef exists
```

### Example

```xml
<body>
  <p>
    <w lemmaRef="lexicon.xml#lemma_100">Der</w>        <!-- position 0 -->
    <w>unbekannt</w>                                     <!-- SKIPPED (no lemmaRef) -->
    <w lemmaRef="lexicon.xml#lemma_879">brôt</w>        <!-- position 1 -->
    <seg type="pc">,</seg>                               <!-- not a <w>, ignored -->
    <w lemmaRef="lexicon.xml#lemma_200">ist</w>         <!-- position 2 -->
  </p>
</body>
```

Corpus index stores: `lemmata: { "lemma_879": [1] }` — position 1, not 2.

### Version History

- **v3.x:** Paragraph-based indexing (positions reset per `<p>` — caused misalignment between Python XPath extraction and JavaScript DOM traversal)
- **v4.0.0:** Document-level indexing (positions never reset — simple, reliable)

---

## C. 3-Stage Lemma Resolution Algorithm

**Contract:** Search resolves user input to lemma IDs through exactly 3 stages, in order, with early return.

**Why:** MHG has extensive orthographic variation. A single lemma can appear as dozens of attested forms. The 3-stage approach balances precision (exact first) with recall (fuzzy last).

Source: `assets/js/search/search-engine.js:118-147`

### Pseudocode

```
function resolveLemmaIds(normalized):
    // Input: already normalized via normalizeMHG() (Contract A)
    // Called by searchLemma() which normalizes the raw user input first

    // Stage 1: Exact match on normalized canonical form
    results = []
    for each lemma in authorityIndex.lemmata:
        if lemma.normalized === normalized:
            results.push(lemma.id)
    if results.length > 0:
        return results                       // EARLY RETURN — skip stages 2-3

    // Stage 2: Variants dictionary lookup (O(1) hash map)
    variantMatch = authorityIndex.variants[normalized]
    if variantMatch:
        return [variantMatch]                // EARLY RETURN — skip stage 3

    // Stage 3: Partial match fallback (bidirectional substring)
    results = []
    for each lemma in authorityIndex.lemmata:
        if lemma.normalized.includes(normalized)
           OR normalized.includes(lemma.normalized):
            results.push(lemma.id)
    return results                           // May be empty
```

### Stage Behavior

| Stage | Input Type | Return | Performance | Example |
|-------|-----------|--------|-------------|---------|
| 1 | Canonical or normalized form | 0..N lemma IDs (homographs) | O(n) scan | `brot` → `[lemma_879]` |
| 2 | Attested orthographic variant | Exactly 1 lemma ID | O(1) lookup | `brott` → normalize → `brot` → variants[`brot`] → `lemma_879` |
| 3 | Partial/fuzzy match | 0..N lemma IDs | O(n) scan | `bro` → matches `brot`, `brogen`, ... |

### Worked Example

User types: **brott**

1. Normalize: `brott` → `brott` (no special MHG characters)
2. Stage 1: Scan all lemmata for `.normalized === 'brott'` → no match
3. Stage 2: Check `authorityIndex.variants['brott']` → `'lemma_879'` → **found!**
4. Return: `['lemma_879']` (Stage 3 never runs)

### Variant Dictionary Structure

- Flat map: `{ normalized_variant_form: lemma_id }`
- ~176,000 entries, extracted from `authority-files/variants.xml`
- **First occurrence wins** — if two lemmata claim the same variant form, only the first one stored (source: `build-authority-index.py:526-571`)
- Keys are **normalized** forms (lowercase + MHG character mapping applied before storage)

---

## D. External API Contracts

### D.1 Wikidata Image Fetch

**Trigger:** Reading view opens a text whose work has a `wikidata` field in the authority index.

Source: `assets/js/rendering/tei-text-reader.js` (Wikidata section, ~line 730+)

**Request chain (3 sequential calls):**

```
1. GET https://www.wikidata.org/w/api.php
     ?action=wbgetclaims&property=P18&entity={wikidataId}&format=json&origin=*
   Response: { claims: { P18: [{ mainsnak: { datavalue: { value: "Filename.jpg" }}}]}}
   Extract: filename from claims.P18[0].mainsnak.datavalue.value

2. Image URL (no API call):
   https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=400

3. GET https://commons.wikimedia.org/w/api.php
     ?action=query&titles=File:{filename}&prop=imageinfo&iiprop=extmetadata&format=json&origin=*
   Response: { query: { pages: { "-1": { imageinfo: [{ extmetadata: {
     Artist: { value: "..." },
     LicenseShortName: { value: "CC BY-SA 3.0" }
   }}]}}}}
   Extract: Artist.value (HTML — cleaned to text), LicenseShortName.value
```

**Error handling:** All calls wrapped in try/catch. On any failure, image section stays hidden (graceful degradation).

### D.2 Wörterbuchnetz API

**Trigger:** Lemma page loads (`lemma/lemma-page.js:269-312`)

```
GET https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{normalizedForm}

Parallel requests for: BMZ, Lexer, LexerN, FindeB
Uses: Promise.allSettled() (one failure doesn't block others)

Response: {
    result_set: [{
        sigle: "BMZ",
        lemma: "br&ocirc;t",     // HTML-encoded — decode with textarea trick
        gram: "stN",
        wbnetzid: "B02435",
        wbnetzlink: "https://www.woerterbuchnetz.de/BMZ/B02435"
    }]
}
```

**HTML entity decoding:** `lemma` field contains HTML entities. Decoded via `document.createElement('textarea'); textarea.innerHTML = str; return textarea.value;`

### D.3 Static External Links (no API calls)

| Target | URL Pattern | Source |
|--------|------------|--------|
| Old MHDBDB | `https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid={numericId}` | `lemma-page.js:234` |
| MWB Online (Trier) | `https://www.mhdwb-online.de/` (static, no deep linking) | `lemma-page.js:239` |
| REALonline (IMAREAL) | `https://realonline.imareal.sbg.ac.at/suche#{json}` where json = `{"s":"{normalized}"}` | `lemma-page.js:245` |
| Corpus search | `../korpus.html?search={lemma.lemma}` | `lemma-page.js:250` |
| GND (person/work) | `https://d-nb.info/gnd/{gndId}` | `tei-text-reader.js` |
| Wikidata (person/work) | `https://www.wikidata.org/wiki/{wikidataId}` | `tei-text-reader.js` |
| Handschriftencensus | URL stored in authority index `work.handschriftencensus` | `tei-text-reader.js` |
| Zotero | URL stored in `work.biblStructs[].corresp` | `tei-text-reader.js` |

### D.4 MWB Online Metadata API (blocked)

```
GET http://tares-neu.uni-trier.de:8080/exist/rest/db/MWB/Services/retrieve_MWB_lemma_metadata.xql?lemma={term}

Response (XML):
<entry>
  <MWB><id>...</id><lemma>...</lemma><gram>...</gram><url>https://www.mhdwb-online.de/wb/{id}</url></MWB>
  <MWV><lexer>...</lexer><bmz>...</bmz><fb>...</fb></MWV>
</entry>
```

**Status:** HTTP-only API. Blocked by mixed content when called from HTTPS page. Currently using static link only. Upgrade to dynamic lookup when MWB team migrates to HTTPS.

---

## E. Cache Invalidation

### IndexedDB Databases

| Database | Library | Store | Key | Used By |
|----------|---------|-------|-----|---------|
| `MHDBDBMainSite` | Dexie.js | `indices` | `name` (string) | `assets/js/lib/corpus-loader.js` |
| `MHDBDB_TEI_Cache` | Raw IndexedDB | `parsedTEI` | `filename` (string) | `assets/js/storage/tei-cache-manager.js` |

### Index Cache (MHDBDBMainSite)

**Store schema:** `{ name, version, timestamp, data }`

**Version check flow** (source: `corpus-loader.js:115-158`):

```
getCachedIndex(name):
    cached = db.indices.get(name)
    if !cached → return null (cache miss)

    // Version check
    if name === 'corpus-index':
        if cached.version !== INDEX_VERSION ('4.0.0'):  → invalidate
    if name === 'authority-index':
        if cached.version !== cached.data.version:      → invalidate

    // Expiration check
    age = Date.now() - cached.timestamp
    if age > 30 days:                                   → invalidate

    return cached.data
```

**How to force refetch:**

| Method | What to change | When |
|--------|---------------|------|
| Corpus version bump | Change `INDEX_VERSION` in `corpus-loader.js` | After rebuilding corpus index with schema changes |
| Authority version bump | Change `version` field in `build-authority-index.py` output | After rebuilding authority index with schema changes |
| User manual clear | "Alle Daten löschen" button on index.html | Clears all IndexedDB + localStorage |
| Developer clear | Browser DevTools → Application → IndexedDB → delete databases | Debugging |

### TEI File Cache (MHDBDB_TEI_Cache)

**Store schema:** `{ filename, xmlString, cachedAt, size, metadata }`

**Strategy:** Serialize parsed DOM to XML string via `XMLSerializer`, restore via `DOMParser`. This avoids re-fetching and re-parsing individual TEI files on repeat visits.

**Expiration:** 30 days (same as index cache). Checked on read (`get()`). Background cleanup via `cleanExpired()`.

**Corruption handling:** If `DOMParser` returns a `parsererror` element, the cached entry is deleted and null returned (triggers fresh network fetch).
