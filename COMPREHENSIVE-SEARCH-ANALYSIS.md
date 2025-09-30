# Comprehensive Search Analysis - MHDBDB Playground

**Date:** 2025-09-30
**Purpose:** Complete inventory of all search functions and normalization status

---

## Executive Summary

The MHDBDB Playground has **11 distinct search entry points** across two main categories:
1. **Authority Files Exploration** (6 searches) - Browse reference data
2. **TEI Text Analysis** (5 searches) - Search within uploaded corpus

**Current Problem:** Only 1 out of 11 searches uses MHG character normalization (â→a, ô→o, etc.)

---

## Complete Search Inventory

### Category A: Authority Files Exploration
*Purpose: Browse and search reference vocabularies (persons, works, lexicon, concepts, genres, names)*

| # | Button | Method | Search Pattern | Normalization | Issue |
|---|--------|--------|----------------|---------------|-------|
| 1 | **Autoren anzeigen** | `AuthorityExplorers.searchAuthors()` | `SearchPatterns.textContains()` on `preferredName` | ❌ NO | Can't find "Eckhart" by searching "eckhart" if spelled "Êckhart" |
| 2 | **Werke anzeigen** | `AuthorityExplorers.searchWorks()` | `SearchPatterns.multiField()` on `title`, `sigle`, `author` | ❌ NO | Can't find works with titles containing â, ô, etc. |
| 3 | **Lemmata anzeigen** | `AuthorityExplorers.searchLemmata()` | `SearchPatterns.textContains()` on `lemma.lemma` | ❌ NO | Can't find "brôt" by searching "brot" |
| 4 | **Konzepte anzeigen** | `AuthorityExplorers.searchConcepts()` | `SearchPatterns.textContains()` on `termDE`/`termEN` | ❌ NO | German concept terms may contain special chars |
| 5 | **Gattungen anzeigen** | `AuthorityExplorers.searchGenres()` | `SearchPatterns.multiField()` on `termDE`/`termEN` | ❌ NO | Genre terms may contain special chars |
| 6 | **Namen anzeigen** | `AuthorityExplorers.searchNames()` | `SearchPatterns.textContains()` on `termDE`/`termEN` | ❌ NO | Proper names may contain special chars |

**Common Code Path:** All 6 use `SearchHelpers.js` → `SearchPatterns.*` → Direct string `.includes()` with `.toLowerCase()`

---

### Category B: TEI Text Analysis
*Purpose: Search within user-uploaded TEI corpus*

| # | Button | Method | Search Target | Normalization | Issue |
|---|--------|--------|---------------|---------------|-------|
| 7 | **Lemma-Suche** | `TEIExplorer.findLemmaInText()` | Searches `teiData.words[]` array | ❌ NO | Searches by `lemmaRef` (ID) or `word.text` - no normalization |
| 8 | **Multi-Lemma-Suche** (Absatz) | `TEIFilesManager.searchMultipleLemmas()` with `contextType='paragraph'` | XML query: `<w lemmaRef*="lemma_879">` | ✅ YES | Uses `resolveLemmaIds()` → `searchLemmaByOrthography()` which normalizes |
| 9 | **Multi-Lemma-Suche** (Dokument) | `TEIFilesManager.searchMultipleLemmas()` with `contextType='document'` | XML query: `<w lemmaRef*="lemma_879">` | ✅ YES | Same as #8, normalized via variants index |
| 10 | **Multi-Lemma-Suche** (Nähe) | `TEIFilesManager.findCooccurringLemmas()` | XML query: `<w lemmaRef*="lemma_879">` | ✅ YES | Same as #8/#9, but searches proximity |
| 11 | **XPath Query** | `TEIFilesManager.executeXPathOnTEI()` | Raw XPath on TEI XML | ⚠️ N/A | Direct XML query - advanced users only |

**Key Discovery:** Multi-Lemma searches (8-10) ARE normalized because they go through:
```
User Input → resolveLemmaIds() → searchLemmaByOrthography() → normalizeMHGCharacters()
```

But **simple Lemma-Suche (#7)** bypasses this and searches directly on `teiData.words[]` without normalization!

---

## Architecture Analysis

### Current Data Flow

#### Authority Files Search (1-6)
```
User types "brot"
   ↓
AuthorityExplorers.searchLemmata(searchTerm)
   ↓
SearchPatterns.textContains(items, searchTerm, fieldGetter)
   ↓
items.filter(item => fieldGetter(item).toLowerCase().includes(term))
   ↓
❌ PROBLEM: "brôt".toLowerCase().includes("brot") → FALSE
```

#### TEI Simple Search (#7)
```
User types "brot" in prompt
   ↓
TEIExplorer.findLemmaInText()
   ↓
teiData.words.filter(w =>
    w.lemmaRef.includes(searchTerm) ||
    w.text.toLowerCase().includes(searchTerm.toLowerCase())
)
   ↓
❌ PROBLEM: No variant resolution, no normalization
```

#### TEI Multi-Lemma Search (#8-10)
```
User types "brot" in modal
   ↓
TEIExplorer.resolveLemmaIds(["brot"])
   ↓
AuthorityFilesManager.searchLemmaByOrthography("brot")
   ↓
normalizeMHGCharacters("brot") → "brot"
   ↓
Stage 1: Exact match in lexicon (normalized comparison)
Stage 2: Variants index search (normalized comparison)
Stage 3: Partial match fallback (normalized comparison)
   ↓
✅ Returns lemma_879 for "brôt"
   ↓
TEIFilesManager.searchMultipleLemmas([879], contextType)
   ↓
XML query: querySelectorAll('w[lemmaRef*="lemma_879"]')
   ↓
✅ SUCCESS: Finds all <w lemmaRef="...#lemma_879">brôt</w>
```

---

## Problem Root Causes

### 1. **SearchHelpers is Generic**
- File: `playground/js/ui/SearchHelpers.js`
- `SearchPatterns.textContains/multiField/exactMatch` have no MHG awareness
- They're designed to be generic utilities, not domain-specific
- Used by all 6 Authority explorers

### 2. **TEI Simple Search is Primitive**
- File: `playground/js/ui/TEIExplorer.js` line 45-63
- Direct `.includes()` on word text
- No lemma resolution
- No normalization
- Uses `prompt()` dialog (poor UX)

### 3. **Normalization is Isolated**
- Only exists in `AuthorityFilesManager.searchLemmaByOrthography()`
- Not accessible to SearchHelpers or other components
- Duplication risk if we add normalization elsewhere

### 4. **Inconsistent User Experience**
- Multi-Lemma search: Modern modal + normalization ✅
- Simple Lemma search: Prompt dialog + no normalization ❌
- Authority searches: Nice UI + no normalization ❌

---

## Impact Assessment

### High Priority Issues

**Issue #7 (Sonderzeichen in der Suche):**
- ❌ **NOT FULLY SOLVED**
- Multi-Lemma works ✅
- But 7 other searches don't work ❌

**User Scenarios:**
1. User searches "Lemmata anzeigen" for "brot" → Won't find "brôt" ❌
2. User searches "Autoren anzeigen" for "Eckhart" → Won't find "Êckhart" (if exists) ❌
3. User uses "Lemma-Suche" for "win" → Won't resolve to "wîn" lemma ❌
4. User uses "Multi-Lemma-Suche" for "win" → WORKS! Finds "wîn" ✅

This inconsistency confuses users!

---

## Proposed Solution Strategy

### Option A: Minimal Fix (Quick & Dirty)
**Scope:** Only fix TEI simple search (#7)
**Effort:** 1 file change
**Result:** Still leaves 6 authority searches without normalization

### Option B: Centralized Utility (Recommended)
**Scope:** Create shared normalization utility, update all 11 searches
**Effort:** 8 file changes
**Result:** Consistent normalization across entire application

### Option C: Hybrid Approach
**Scope:** Fix TEI searches now, plan authority search refactoring later
**Effort:** 3 file changes now, 6 later
**Result:** TEI analysis consistent, authority files deferred

---

## Recommendation: Option B (Comprehensive Fix)

### Why Option B?

1. **Consistency:** All searches work the same way
2. **User Expectation:** Users expect "brot" to find "brôt" everywhere
3. **Long-term Maintainability:** One normalization function
4. **Issue Resolution:** Fully closes #7
5. **Code Quality:** Centralized utilities are best practice

### Implementation Plan

#### Phase 1: Create Centralized Utility
**File:** `playground/js/utils/text-normalizer.js` (NEW)

```javascript
/**
 * Middle High German Text Normalization Utility
 * Handles special character normalization for search
 */
export class TextNormalizer {
    /**
     * Normalize Middle High German special characters
     * â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue, æ→ae, œ→oe
     */
    static normalizeMHG(text) {
        if (!text) return '';
        return text
            .toLowerCase()
            .replace(/[âā]/g, 'a')
            .replace(/[êē]/g, 'e')
            .replace(/[îī]/g, 'i')
            .replace(/[ôō]/g, 'o')
            .replace(/[ûū]/g, 'u')
            .replace(/ä/g, 'ae')
            .replace(/ö/g, 'oe')
            .replace(/ü/g, 'ue')
            .replace(/æ/g, 'ae')
            .replace(/œ/g, 'oe')
            .replace(/ǒ/g, 'o');
    }

    /**
     * Check if text contains search term (with normalization)
     */
    static matchesNormalized(text, searchTerm) {
        const normalizedText = this.normalizeMHG(text);
        const normalizedSearch = this.normalizeMHG(searchTerm);
        return normalizedText.includes(normalizedSearch);
    }

    /**
     * Check for exact match (with normalization)
     */
    static exactMatchNormalized(text, searchTerm) {
        const normalizedText = this.normalizeMHG(text);
        const normalizedSearch = this.normalizeMHG(searchTerm);
        return normalizedText === normalizedSearch;
    }
}
```

#### Phase 2: Update SearchHelpers
**File:** `playground/js/ui/SearchHelpers.js` (MODIFY)

Add normalized versions of all patterns:
```javascript
import { TextNormalizer } from '../utils/text-normalizer.js';

export const SearchPatterns = {
    // Keep existing patterns for backward compatibility
    textContains: (items, searchTerm, fieldGetter) => { ... },
    multiField: (items, searchTerm, fieldGetters) => { ... },
    exactMatch: (items, searchTerm, fieldGetter) => { ... },

    // NEW: Normalized versions
    textContainsNormalized: (items, searchTerm, fieldGetter) => {
        return items.filter(item =>
            TextNormalizer.matchesNormalized(fieldGetter(item), searchTerm)
        );
    },

    multiFieldNormalized: (items, searchTerm, fieldGetters) => {
        const matchedItems = new Set();
        items.forEach(item => {
            const hasMatch = fieldGetters.some(getter =>
                getter(item) && TextNormalizer.matchesNormalized(getter(item), searchTerm)
            );
            if (hasMatch) matchedItems.add(item);
        });
        return Array.from(matchedItems);
    },

    exactMatchNormalized: (items, searchTerm, fieldGetter) => {
        return items.filter(item =>
            TextNormalizer.exactMatchNormalized(fieldGetter(item), searchTerm)
        );
    }
};
```

#### Phase 3: Update AuthorityExplorers (6 searches)
**File:** `playground/js/ui/AuthorityExplorers.js` (MODIFY)

Change each search method:
```javascript
// Before:
const matches = SearchPatterns.textContains(
    this.authorityData.lemmata,
    searchTerm,
    (lemma) => lemma.lemma
);

// After:
const matches = SearchPatterns.textContainsNormalized(
    this.authorityData.lemmata,
    searchTerm,
    (lemma) => lemma.lemma
);
```

Apply to:
- `searchAuthors()` → `textContainsNormalized`
- `searchWorks()` → `multiFieldNormalized`
- `searchLemmata()` → `textContainsNormalized`
- `searchConcepts()` → `textContainsNormalized`
- `searchGenres()` → `multiFieldNormalized`
- `searchNames()` → `textContainsNormalized`

#### Phase 4: Update TEI Simple Search
**File:** `playground/js/ui/TEIExplorer.js` (MODIFY)

```javascript
import { TextNormalizer } from '../utils/text-normalizer.js';

findLemmaInText() {
    const searchTerm = prompt('Welches Lemma soll im Text gesucht werden?');
    if (!searchTerm) return;

    const matches = this.teiData.words.filter(w =>
        (w.lemmaRef && w.lemmaRef.includes(searchTerm)) ||
        TextNormalizer.matchesNormalized(w.text, searchTerm)
    );

    // ... rest of method
}
```

#### Phase 5: Simplify AuthorityFilesManager
**File:** `playground/js/authority-files.js` (MODIFY)

```javascript
import { TextNormalizer } from './utils/text-normalizer.js';

// Remove custom normalizeMHGCharacters() method
// Update searchLemmaByOrthography() to use TextNormalizer.normalizeMHG()

searchLemmaByOrthography(orthography) {
    const normalized = orthography.toLowerCase();
    const normalizedCharacters = TextNormalizer.normalizeMHG(normalized);
    // ... rest of method using TextNormalizer
}
```

#### Phase 6: Update CLAUDE.md
**File:** `CLAUDE.md` (MAJOR REWRITE)

Add comprehensive sections:
1. **Search Architecture Overview** - All 11 entry points documented
2. **Text Normalization Strategy** - MHG character handling explained
3. **Data Flow Diagrams** - Authority vs TEI search paths
4. **Module Responsibilities** - Clear boundaries

---

## Files to Modify

### NEW Files (1)
1. ✏️ `playground/js/utils/text-normalizer.js` - Centralized normalization utility

### MODIFIED Files (7)
2. ✏️ `playground/js/ui/SearchHelpers.js` - Add normalized search patterns
3. ✏️ `playground/js/ui/AuthorityExplorers.js` - Update 6 search methods
4. ✏️ `playground/js/ui/TEIExplorer.js` - Fix simple lemma search
5. ✏️ `playground/js/authority-files.js` - Use centralized normalizer
6. ✏️ `playground/js/main.js` - Import TextNormalizer (if needed for global access)
7. ✏️ `playground/index.html` - Update hint texts to mention normalization
8. ✏️ `CLAUDE.md` - Comprehensive architecture rewrite

---

## Testing Plan

### Test Matrix

| Search Function | Test Input | Expected Result | Status |
|-----------------|------------|-----------------|--------|
| Lemmata anzeigen | "brot" | Finds "brôt" | ⏳ |
| Lemmata anzeigen | "win" | Finds "wîn" | ⏳ |
| Multi-Lemma-Suche | "brot" | Resolves to lemma_879 | ✅ Already works |
| Simple Lemma-Suche | "brot" | Finds words with lemma "brôt" | ⏳ |
| Autoren anzeigen | "eckhart" | Finds "Êckhart" (if exists) | ⏳ |

### Manual Testing Steps
1. Clear IndexedDB cache
2. Reload page
3. Test each search with normalized input
4. Verify results match canonical forms
5. Check console for normalization logs

---

## Estimated Effort

- **Phase 1 (Utility):** 30 minutes
- **Phase 2 (SearchHelpers):** 30 minutes
- **Phase 3 (Authority):** 45 minutes (6 methods)
- **Phase 4 (TEI Simple):** 15 minutes
- **Phase 5 (AuthorityFiles):** 30 minutes
- **Phase 6 (Documentation):** 60 minutes

**Total:** ~3.5 hours for complete implementation

---

## Benefits

✅ **Consistency** - All 11 searches use same logic
✅ **User Experience** - No confusion about which searches support normalization
✅ **Maintainability** - Single source of truth for MHG rules
✅ **Testability** - TextNormalizer can be unit tested in isolation
✅ **Issue Resolution** - Fully closes GitHub issue #7
✅ **Code Quality** - Follows DRY principle
✅ **Documentation** - Clear architecture guide for future developers

---

## Risks & Mitigation

### Risk 1: Breaking Existing Searches
**Mitigation:** Keep old patterns alongside new ones, gradual migration

### Risk 2: Performance Impact
**Mitigation:** Normalization is lightweight (regex replace), negligible overhead

### Risk 3: Edge Cases
**Mitigation:** Comprehensive testing with real MHG text samples

---

## Next Steps

1. **User Decision:** Choose Option A, B, or C
2. **Implementation:** Follow phased plan above
3. **Testing:** Manual verification of all 11 searches
4. **Documentation:** Update CLAUDE.md with architecture
5. **GitHub:** Close issue #7 with comprehensive comment