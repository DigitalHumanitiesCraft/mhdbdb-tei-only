# Playground UX Redesign: Auto-Load Enhanced Corpus

**Date:** 2025-10-03
**Status:** Approved - Ready for Implementation

## Problem Statement

Current playground has confusing dual-loading system (upload vs corpus button) and multi-lemma search hangs when using pre-built corpus due to sequential XML loading of 666 files.

## Solution Overview

Auto-load enhanced corpus index on startup that contains complete word data, eliminating need for XML loading entirely. Replace upload/button UI with include/exclude checkboxes for targeted research.

---

## Architecture Changes

### Current Architecture
```
User Action:
├─ Option A: Upload TEI files manually
│  └─ Parses XML → Stores in memory → Search works
└─ Option B: Click "Load Corpus" button
   └─ Loads index (metadata + positions) → Lazy-loads XML on search → HANGS

Search Flow (Corpus):
1. User searches "brot + win" proximity
2. Loop through 666 texts
3. Each iteration: await fetch('../tei/ABG.tei.xml') → sequential!
4. Result: 666 HTTP requests → infinite spinner
```

### New Architecture
```
Startup:
└─ Auto-load enhanced corpus index (~35 MB)
   ├─ Contains: metadata + positions + FULL WORD TEXT
   └─ All 666 texts ready in memory

Search Flow:
1. User searches "brot + win" proximity
2. Filter to included texts (via checkboxes)
3. Calculate proximity using index positions
4. Extract context from words array in index
5. Result: Pure JavaScript → 0.1s → instant display
```

---

## Phase 1: Enhance Corpus Index (Python)

### File: `scripts/build-corpus-index.py`

**Add new extraction function:**

```python
def extract_full_word_data(filepath):
    """
    Extract complete word array with text, lemma, and position.
    Also extract paragraph boundaries.

    Returns: (words, paragraphs, word_count)
    """
    try:
        tree = etree.parse(str(filepath))
        ns = get_namespaces(tree)

        # Get all <w> elements (with or without lemmaRef)
        word_els = tree.xpath('//tei:w', namespaces=ns)

        words = []
        for idx, word_el in enumerate(word_els):
            lemma_ref = word_el.get('lemmaRef', '')

            # Extract lemma ID from reference
            lemma_id = ''
            if lemma_ref and '#' in lemma_ref:
                lemma_id = lemma_ref.split('#')[1]

            # Get word text (handle empty elements)
            word_text = word_el.text.strip() if word_el.text else ''

            if word_text:  # Only include non-empty words
                words.append({
                    'pos': idx,
                    'text': word_text,
                    'lemma': lemma_id
                })

        # Extract paragraph boundaries
        paragraphs = []
        current_pos = 0

        para_els = tree.xpath('//tei:p', namespaces=ns)
        for para_idx, para_el in enumerate(para_els):
            # Count words in this paragraph
            para_words = para_el.xpath('.//tei:w', namespaces=ns)
            para_word_count = len([w for w in para_words if w.text and w.text.strip()])

            if para_word_count > 0:
                paragraphs.append({
                    'id': para_el.get('n', f'p{para_idx}'),
                    'start': current_pos,
                    'end': current_pos + para_word_count - 1
                })
                current_pos += para_word_count

        return words, paragraphs, len(words)

    except Exception as e:
        print(f"⚠️  Error extracting word data from {filepath.name}: {e}")
        return [], [], 0
```

**Update `process_tei_file()` function:**

```python
def process_tei_file(filepath):
    """Process single TEI file and return complete text data."""
    # Extract metadata (existing)
    metadata = extract_metadata(filepath)
    if not metadata:
        return None

    text_id = metadata['id']

    # Extract complete word data (NEW)
    words, paragraphs, word_count = extract_full_word_data(filepath)

    # Also build lemma positions for backward compatibility
    lemmata = defaultdict(list)
    for word in words:
        if word['lemma']:
            lemmata[word['lemma']].append(word['pos'])

    # Combine all data
    text_data = {
        **metadata,
        'wordCount': word_count,
        'lemmata': dict(lemmata),  # Keep for compatibility
        'words': words,            # NEW: Full word array
        'paragraphs': paragraphs   # NEW: Paragraph boundaries
    }

    return text_data
```

**Expected new index structure:**

```javascript
{
  "version": "2.0.0",  // Increment version
  "generatedAt": "2025-10-03T...",
  "totalTexts": 666,
  "texts": [
    {
      "id": "ABG",
      "filename": "ABG.tei.xml",
      "title": "Von der Abgeschiedenheit",
      "author": "Meister Eckhart",
      "authorRef": "#person_445",
      "workRef": "#work_89",
      "genre": "Geistliche Literatur",
      "wordCount": 4194,

      // Existing (keep for compatibility)
      "lemmata": {
        "lemma_879": [15, 42, 108, 245],
        "lemma_7532": [8, 23, 156]
      },

      // NEW: Complete word array
      "words": [
        {"pos": 0, "text": "Von", "lemma": "lemma_123"},
        {"pos": 1, "text": "der", "lemma": "lemma_456"},
        {"pos": 2, "text": "Abgeschiedenheit", "lemma": "lemma_789"},
        // ... 4,191 more words
      ],

      // NEW: Paragraph boundaries
      "paragraphs": [
        {"id": "p1", "start": 0, "end": 50},
        {"id": "p2", "start": 51, "end": 120},
        {"id": "p3", "start": 121, "end": 200}
        // ... more paragraphs
      ]
    }
    // ... 665 more texts
  ],

  // Existing lemmaIndex (keep)
  "lemmaIndex": {
    "lemma_879": ["ABG", "BRZ", "HZU2", ...],
    "lemma_7532": ["ABG", "AXR", ...]
  }
}
```

**Build command:**
```bash
python scripts/build-corpus-index.py
```

**Expected file size:**
- Current: `data/corpus-index.json.gz` (~21 MB compressed)
- New: `data/corpus-index.json.gz` (~30-40 MB compressed)
- Uncompressed: ~120-150 MB (acceptable for modern browsers)

---

## Phase 2: Update Playground HTML

### File: `playground/index.html`

**Replace left column (lines 78-215) with new TEI corpus browser:**

```html
<!-- TEI Corpus Browser -->
<section class="space-y-6 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-sm ring-1 ring-slate-100/40">
    <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-slate-900">TEI-Korpus</h2>
        <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">Auto-Load</span>
    </div>

    <!-- Loading State (shown during initial corpus load) -->
    <div id="corpusLoadingState" class="space-y-3">
        <div class="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div class="flex-1">
                <div class="text-sm font-medium text-blue-900">Korpus wird geladen...</div>
                <div class="text-xs text-blue-700">Lädt erweiterten Index mit vollständigen Wortdaten</div>
            </div>
        </div>
        <div class="text-xs text-slate-500 text-center">
            Download: ~35 MB • Danach sind alle Suchen sofort verfügbar
        </div>
    </div>

    <!-- File List (shown after successful load) -->
    <div id="corpusFileList" class="space-y-3" style="display: none;">

        <!-- Selection Summary -->
        <div class="flex items-center justify-between p-3 bg-brand-50 border border-brand-200 rounded-lg">
            <div class="text-sm font-medium text-brand-900">
                <span id="selectedCount">666</span> / <span id="totalCount">666</span> Texte
            </div>
            <div class="flex gap-2">
                <button id="selectAllBtn"
                        class="text-xs px-2 py-1 font-medium text-brand-700 hover:bg-brand-100 rounded transition">
                    Alle
                </button>
                <button id="deselectAllBtn"
                        class="text-xs px-2 py-1 font-medium text-slate-600 hover:bg-slate-100 rounded transition">
                    Keine
                </button>
            </div>
        </div>

        <!-- Filters and Sorting -->
        <div class="space-y-2">
            <!-- Filename search -->
            <input type="text"
                   id="fileFilterName"
                   placeholder="Nach Dateiname suchen..."
                   class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200">

            <!-- Author filter -->
            <select id="fileFilterAuthor"
                    class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200">
                <option value="">Alle Autoren</option>
                <!-- Populated dynamically from corpus data -->
            </select>

            <!-- Genre filter -->
            <select id="fileFilterGenre"
                    class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200">
                <option value="">Alle Gattungen</option>
                <!-- Populated dynamically from corpus data -->
            </select>

            <!-- Sort options -->
            <select id="fileSortBy"
                    class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200">
                <option value="filename">Sortieren: Dateiname</option>
                <option value="title">Sortieren: Titel</option>
                <option value="author">Sortieren: Autor</option>
                <option value="wordCount">Sortieren: Wortanzahl</option>
            </select>
        </div>

        <!-- File List with Checkboxes (scrollable) -->
        <div id="fileListContainer"
             class="space-y-1 max-h-96 overflow-y-auto border border-slate-200 rounded-lg p-2 bg-slate-50">
            <!-- Populated dynamically with checkbox items -->
        </div>

        <!-- Helper text -->
        <div class="text-xs text-slate-500 text-center pt-2">
            Aktivieren Sie nur die Texte, die Sie durchsuchen möchten
        </div>
    </div>
</section>
```

**Remove:** All upload-related HTML (upload zone, load corpus button, etc.)

---

## Phase 3: Update Playground JavaScript

### File: `playground/js/playground-main.js`

**Update `init()` method:**

```javascript
async init() {
    this.initializeEventListeners();

    // Load authority files (existing - works immediately)
    await this.loadAuthorityIndex();

    // NEW: Auto-load enhanced corpus (replaces manual load)
    await this.autoLoadEnhancedCorpus();

    this.updateUI();
}
```

**Add new method `autoLoadEnhancedCorpus()`:**

```javascript
async autoLoadEnhancedCorpus() {
    const loadingState = document.getElementById('corpusLoadingState');
    const fileList = document.getElementById('corpusFileList');

    try {
        console.log('📦 Auto-loading enhanced corpus index...');

        // Import CorpusLoader
        const { CorpusLoader } = await import('/lib/corpus-loader.js');
        const corpusLoader = new CorpusLoader('../data');
        await corpusLoader.dbReady;

        // Load enhanced corpus index (with words array)
        const corpusIndex = await corpusLoader.loadCorpusIndex();

        console.log(`📚 Enhanced corpus loaded: ${corpusIndex.texts.length} texts`);
        console.log(`📊 Total words in corpus: ${corpusIndex.texts.reduce((sum, t) => sum + t.wordCount, 0).toLocaleString()}`);

        // Store corpus data in TEI manager
        this.teiManager.corpusIndex = corpusIndex;
        this.teiManager.teiData.parsedXML = corpusIndex.texts.map(text => ({
            ...text,
            isCorpusData: true,
            isIncluded: true  // All texts included by default
        }));

        // Populate file list UI
        this.populateFileList(corpusIndex.texts);

        // Switch UI: hide loading, show file list
        loadingState.style.display = 'none';
        fileList.style.display = 'block';

        // Enable TEI search buttons (were disabled during load)
        this.enableTEISearch();

        // Show success notification
        this.showNotification('✅ Korpus geladen: 666 Texte verfügbar für sofortige Suche');

    } catch (error) {
        console.error('❌ Failed to load enhanced corpus:', error);
        loadingState.innerHTML = `
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div class="text-sm font-medium text-red-900">Fehler beim Laden</div>
                <div class="text-xs text-red-700 mt-1">${error.message}</div>
                <button onclick="location.reload()"
                        class="mt-3 text-xs px-3 py-1 bg-red-100 hover:bg-red-200 rounded">
                    Seite neu laden
                </button>
            </div>
        `;
    }
}
```

**Add file list population:**

```javascript
populateFileList(texts) {
    const container = document.getElementById('fileListContainer');
    const authorSelect = document.getElementById('fileFilterAuthor');
    const genreSelect = document.getElementById('fileFilterGenre');

    // Extract unique authors and genres for filters
    const authors = [...new Set(texts.map(t => t.author).filter(a => a))].sort();
    const genres = [...new Set(texts.map(t => t.genre).filter(g => g))].sort();

    // Populate author dropdown
    authors.forEach(author => {
        const option = document.createElement('option');
        option.value = author;
        option.textContent = author;
        authorSelect.appendChild(option);
    });

    // Populate genre dropdown
    genres.forEach(genre => {
        const option = document.createElement('option');
        option.value = genre;
        option.textContent = genre;
        genreSelect.appendChild(option);
    });

    // Render file items with checkboxes
    this.renderFileList(texts);

    // Setup filter/sort listeners
    this.setupFileListFilters();
}

renderFileList(texts) {
    const container = document.getElementById('fileListContainer');
    container.innerHTML = '';

    texts.forEach((text, idx) => {
        const item = document.createElement('label');
        item.className = 'flex items-center gap-2 p-2 hover:bg-white rounded cursor-pointer transition';
        item.setAttribute('data-text-id', text.id);
        item.setAttribute('data-filename', text.filename.toLowerCase());
        item.setAttribute('data-title', (text.title || '').toLowerCase());
        item.setAttribute('data-author', text.author || '');
        item.setAttribute('data-genre', text.genre || '');
        item.setAttribute('data-wordcount', text.wordCount || 0);

        item.innerHTML = `
            <input type="checkbox"
                   class="text-include-checkbox w-4 h-4 text-brand-600 rounded border-slate-300 focus:ring-brand-500"
                   data-text-id="${text.id}"
                   checked>
            <div class="flex-1 min-w-0">
                <div class="text-xs font-medium text-slate-900 truncate">${text.filename}</div>
                ${text.title ? `<div class="text-xs text-slate-600 truncate">${text.title}</div>` : ''}
                <div class="text-xs text-slate-400">
                    ${text.author || 'Unbekannt'} • ${text.wordCount.toLocaleString()} Wörter
                </div>
            </div>
        `;

        container.appendChild(item);
    });

    // Update count
    this.updateSelectedCount();
}

setupFileListFilters() {
    const nameFilter = document.getElementById('fileFilterName');
    const authorFilter = document.getElementById('fileFilterAuthor');
    const genreFilter = document.getElementById('fileFilterGenre');
    const sortBy = document.getElementById('fileSortBy');

    // Combined filter function
    const applyFilters = () => {
        const nameValue = nameFilter.value.toLowerCase();
        const authorValue = authorFilter.value;
        const genreValue = genreFilter.value;

        const items = document.querySelectorAll('#fileListContainer label');
        let visibleCount = 0;

        items.forEach(item => {
            const filename = item.getAttribute('data-filename');
            const title = item.getAttribute('data-title');
            const author = item.getAttribute('data-author');
            const genre = item.getAttribute('data-genre');

            const matchesName = !nameValue ||
                               filename.includes(nameValue) ||
                               title.includes(nameValue);
            const matchesAuthor = !authorValue || author === authorValue;
            const matchesGenre = !genreValue || genre === genreValue;

            const visible = matchesName && matchesAuthor && matchesGenre;
            item.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        });

        console.log(`🔍 Filter applied: ${visibleCount} / ${items.length} visible`);
    };

    // Attach filter listeners
    nameFilter.addEventListener('input', applyFilters);
    authorFilter.addEventListener('change', applyFilters);
    genreFilter.addEventListener('change', applyFilters);

    // Sort function
    sortBy.addEventListener('change', () => {
        const sortKey = sortBy.value;
        const container = document.getElementById('fileListContainer');
        const items = Array.from(container.querySelectorAll('label'));

        items.sort((a, b) => {
            let aVal, bVal;

            if (sortKey === 'wordCount') {
                aVal = parseInt(a.getAttribute('data-wordcount')) || 0;
                bVal = parseInt(b.getAttribute('data-wordcount')) || 0;
                return bVal - aVal; // Descending
            } else {
                aVal = a.getAttribute(`data-${sortKey}`) || '';
                bVal = b.getAttribute(`data-${sortKey}`) || '';
                return aVal.localeCompare(bVal);
            }
        });

        // Re-append in sorted order
        items.forEach(item => container.appendChild(item));
        console.log(`📊 Sorted by: ${sortKey}`);
    });

    // Select/Deselect All buttons
    document.getElementById('selectAllBtn').addEventListener('click', () => {
        const checkboxes = document.querySelectorAll('.text-include-checkbox');
        checkboxes.forEach(cb => {
            // Only check visible items
            if (cb.closest('label').style.display !== 'none') {
                cb.checked = true;
            }
        });
        this.updateSelectedCount();
    });

    document.getElementById('deselectAllBtn').addEventListener('click', () => {
        const checkboxes = document.querySelectorAll('.text-include-checkbox');
        checkboxes.forEach(cb => {
            if (cb.closest('label').style.display !== 'none') {
                cb.checked = false;
            }
        });
        this.updateSelectedCount();
    });

    // Update count when any checkbox changes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('text-include-checkbox')) {
            this.updateSelectedCount();

            // Update text data included state
            const textId = e.target.getAttribute('data-text-id');
            const textData = this.teiManager.teiData.parsedXML.find(t => t.id === textId);
            if (textData) {
                textData.isIncluded = e.target.checked;
            }
        }
    });
}

updateSelectedCount() {
    const total = document.querySelectorAll('.text-include-checkbox').length;
    const selected = document.querySelectorAll('.text-include-checkbox:checked').length;

    document.getElementById('selectedCount').textContent = selected;
    document.getElementById('totalCount').textContent = total;
}

enableTEISearch() {
    // Enable all TEI search buttons
    const teiButtons = [
        'findMultiLemmaBtn',
        'findLemmaBtn',
        'showWordsBtn',
        'showLinesBtn',
        'showAnnotationsBtn'
    ];

    teiButtons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });

    console.log('✅ TEI search enabled');
}

showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}
```

**Remove upload-related methods:**
- `setupFileUpload()`
- `handleFileUpload()`
- `loadCachedTEIFiles()`
- Upload event listeners

---

## Phase 4: Update Search Methods

### File: `playground/js/data/tei-manager.js`

**Update proximity search to use enhanced index:**

```javascript
async searchProximityUsingIndex(lemmaIds, maxDistance) {
    console.log(`🚀 Enhanced index search (zero XML loading)`);

    // Get list of included text IDs from UI checkboxes
    const includedTextIds = this.getIncludedTextIds();
    console.log(`   Searching ${includedTextIds.length} included texts`);

    const proximityMatches = this.findProximityMatchesInIndex(lemmaIds, maxDistance);
    if (!proximityMatches) {
        return await this.findCooccurringLemmas(lemmaIds, maxDistance);
    }

    const results = [];

    // Use words array from index - NO XML LOADING!
    for (const [textId, matches] of Object.entries(proximityMatches)) {
        // Skip excluded texts
        if (!includedTextIds.includes(textId)) {
            console.log(`   Skipping excluded text: ${textId}`);
            continue;
        }

        const text = this.corpusIndex.texts.find(t => t.id === textId);
        if (!text || !text.words) {
            console.warn(`   Text ${textId} missing words array`);
            continue;
        }

        for (const match of matches) {
            const positions = match.positions;
            const distance = match.distance;

            // Extract context from words array (±10 words)
            const minPos = Math.min(...positions);
            const maxPos = Math.max(...positions);
            const contextStart = Math.max(0, minPos - 10);
            const contextEnd = Math.min(text.words.length, maxPos + 11);

            const contextWords = text.words.slice(contextStart, contextEnd);
            const contextText = contextWords.map(w => w.text).join(' ');

            // Build highlighted version (for display)
            const highlightedText = contextWords.map((w, idx) => {
                const absPos = contextStart + idx;
                if (positions.includes(absPos)) {
                    return `<mark class="bg-yellow-200">${w.text}</mark>`;
                }
                return w.text;
            }).join(' ');

            results.push({
                filename: text.filename,
                title: text.title,
                author: text.author,
                genre: text.genre,
                matchPositions: positions,
                distance: distance,
                contextText: contextText,
                highlightedText: highlightedText,
                contextStart: contextStart,
                contextEnd: contextEnd
            });
        }
    }

    console.log(`✅ Instant search: ${results.length} matches (${Object.keys(proximityMatches).length} texts, 0 XML loaded)`);
    return results;
}

getIncludedTextIds() {
    // Get list of text IDs that are checked in the UI
    const checkboxes = document.querySelectorAll('.text-include-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.getAttribute('data-text-id'));
}
```

**Update paragraph/document search similarly:**

```javascript
async searchParagraphOrDocumentUsingIndex(lemmaIds, contextType) {
    console.log(`🚀 Enhanced ${contextType} search using index`);

    const includedTextIds = this.getIncludedTextIds();
    const candidateTextIds = this.findTextsContainingLemmas(lemmaIds);

    // Filter to only included texts
    const filteredTextIds = candidateTextIds.filter(id => includedTextIds.includes(id));

    if (filteredTextIds.length === 0) {
        console.log('   No matches in included texts');
        return [];
    }

    const results = [];

    for (const textId of filteredTextIds) {
        const text = this.corpusIndex.texts.find(t => t.id === textId);
        if (!text || !text.words) continue;

        if (contextType === 'paragraph') {
            // Find paragraphs containing all lemmas using words array
            const paragraphMatches = this.findParagraphMatchesInWords(text, lemmaIds);
            results.push(...paragraphMatches);
        } else {
            // Document-level: already know text contains all lemmas
            const matchingWords = {};
            lemmaIds.forEach(lemmaId => {
                matchingWords[lemmaId] = text.words
                    .filter(w => w.lemma === `lemma_${lemmaId}`)
                    .map(w => ({text: w.text, pos: w.pos}));
            });

            results.push({
                filename: text.filename,
                title: text.title,
                author: text.author,
                context: 'document',
                matchingWords: matchingWords,
                totalWords: text.wordCount
            });
        }
    }

    console.log(`✅ Enhanced search: ${results.length} matches, 0 XML loaded`);
    return results;
}

findParagraphMatchesInWords(text, lemmaIds) {
    const results = [];

    if (!text.paragraphs || !text.words) return results;

    // Check each paragraph
    text.paragraphs.forEach((para, pIndex) => {
        const paraWords = text.words.slice(para.start, para.end + 1);

        // Check if paragraph contains all lemmas
        const containsAllLemmas = lemmaIds.every(lemmaId => {
            return paraWords.some(w => w.lemma === `lemma_${lemmaId}`);
        });

        if (containsAllLemmas) {
            const paraText = paraWords.map(w => w.text).join(' ');

            // Extract matching words
            const matchingWords = {};
            lemmaIds.forEach(lemmaId => {
                matchingWords[lemmaId] = paraWords
                    .filter(w => w.lemma === `lemma_${lemmaId}`)
                    .map(w => ({text: w.text, pos: w.pos}));
            });

            results.push({
                filename: text.filename,
                title: text.title,
                author: text.author,
                context: 'paragraph',
                paragraphIndex: pIndex,
                paragraphId: para.id,
                text: paraText,
                matchingWords: matchingWords
            });
        }
    });

    return results;
}
```

---

## Phase 5: Remove Upload Code

### Files to Clean Up:

**`playground/js/playground-main.js`:**
- Remove `setupFileUpload()` method
- Remove `handleFileUpload()` method
- Remove `loadCachedTEIFiles()` method
- Remove `removeTEIFile()` method
- Remove upload-related event listeners

**`playground/js/data/tei-manager.js`:**
- Keep `processTEIFile()` and related methods (might be useful for future)
- Mark as deprecated with comment

**`playground/js/data/storage/tei-storage.js`:**
- Optional: Can remove entirely or keep for future use

**`playground/js/ui/core/file-display.js`:**
- Remove `displayFileItem()` for uploaded files (no longer needed)
- Keep filter/count functions (used by new file list)

---

## Testing Checklist

### Initial Load
- [ ] Playground loads automatically
- [ ] Loading spinner shows during corpus load
- [ ] Progress updates visible
- [ ] File list appears after load (~10 seconds)
- [ ] All 666 texts shown with checkboxes
- [ ] Authority browsing works immediately (during corpus load)

### File List UI
- [ ] Search by filename filters correctly
- [ ] Filter by author works
- [ ] Filter by genre works
- [ ] Sort by filename/title/author/wordCount works
- [ ] "Select All" checks all visible items
- [ ] "Deselect All" unchecks all visible items
- [ ] Checkbox state persists during filter changes
- [ ] Selected count updates correctly

### Search Functionality
- [ ] Multi-lemma proximity search: instant results
- [ ] Multi-lemma paragraph search: instant results
- [ ] Multi-lemma document search: instant results
- [ ] Search respects include/exclude (only searches checked texts)
- [ ] Results show correct context text from words array
- [ ] No XML fetching occurs during search
- [ ] Console shows "0 XML loaded" messages

### Targeted Research Use Case
- [ ] User can uncheck all texts
- [ ] User can check only 2 specific texts (e.g., ABG + BRZ)
- [ ] Search only runs on those 2 texts
- [ ] Results only from included texts
- [ ] Experience identical to old "upload 2 files" workflow

---

## Performance Benchmarks

### Expected Performance (After Implementation)

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| **Playground startup** | ~2s | ~10s | Slower (acceptable) |
| **Proximity search (666 files)** | Infinite hang | 0.1-0.5s | 60x+ faster |
| **Proximity search (2 files)** | Manual upload needed | 0.1s | Instant |
| **Paragraph search (666 files)** | 30+ seconds | 0.1-0.5s | 60x+ faster |
| **Document search (666 files)** | 30+ seconds | 0.1-0.5s | 60x+ faster |
| **Display search results** | Wait for XML load | Instant | Instant |

### Memory Usage
- **Index in memory:** ~150 MB uncompressed
- **Browser heap:** ~300-400 MB total
- **Acceptable for:** Desktop browsers (Chrome, Firefox, Edge)
- **Not suitable for:** Very old devices, mobile browsers

---

## Documentation Updates

### File: `CLAUDE.md`

**Update sections:**

**Playground Architecture:**
```markdown
### Playground (playground/)
- **Purpose**: Advanced research tool for medievalists and researchers
- **Architecture**: Auto-loads enhanced corpus index on startup
- **Data Loading**:
  - Automatic corpus load (~10s startup time)
  - Enhanced index contains: metadata + word positions + full word text + paragraphs
  - All 666 texts ready for instant search (no XML loading)
- **Include/Exclude UI**:
  - 666 file checkboxes for targeted research
  - Filters: filename, author, genre
  - Sorting: filename, title, author, word count
  - Use case: Uncheck unwanted texts → search only included subset
```

**Data Architecture:**
```markdown
### Enhanced Corpus Index (data/corpus-index.json.gz)

**Version 2.0 Structure:**
- **Size**: ~35 MB compressed (~150 MB uncompressed)
- **Contains**:
  - Metadata: title, author, genre, word count
  - Lemma positions: {lemma_879: [15, 42, 108]}
  - **Full word array**: [{pos: 0, text: "Von", lemma: "lemma_123"}, ...]
  - **Paragraph boundaries**: [{id: "p1", start: 0, end: 50}, ...]
  - Lemma index: {lemma_879: ["ABG", "BRZ", ...]}

**Search Algorithm:**
1. Filter texts using lemmaIndex (instant intersection)
2. Calculate proximity using word positions
3. Extract context from words array (no XML!)
4. Display results immediately

**Performance:**
- Proximity search: 0.1-0.5 seconds
- Zero XML loading required
- Works offline after initial index load
```

---

## Migration Notes

### For Users
- **No action required** - playground auto-loads on visit
- First visit: ~10 second load time
- Subsequent visits: ~2-5 seconds (cached in IndexedDB)
- Old uploaded files: No longer accessible (use include/exclude instead)

### For Developers
- **Rebuild index required**: `python scripts/build-corpus-index.py`
- Upload code removed but methods kept for potential future use
- IndexedDB schema remains compatible (corpus index cached with 30-day TTL)

---

## Future Enhancements (Post-Implementation)

### Possible Additions
1. **Save/Load filter presets**: "My Meister Eckhart subset"
2. **Export included texts list**: Share research subset with colleagues
3. **Batch operations**: "Select all texts from this author"
4. **Advanced filters**: Date range, word count range, genre hierarchy
5. **Visual indicators**: Show which paragraphs contain matches
6. **Context length slider**: Adjust ±10 words dynamically

### Performance Optimizations
1. **Web Worker search**: Offload search to background thread
2. **Virtual scrolling**: Handle 666 items more efficiently
3. **Progressive enhancement**: Load most-used texts first
4. **Compression experiments**: Try different compression for words array

---

## Implementation Timeline

**Estimated time: 4-6 hours**

1. **Phase 1 - Python** (~1 hour)
   - Modify build script
   - Rebuild index
   - Verify structure

2. **Phase 2 - HTML** (~30 minutes)
   - Replace left column
   - Add loading/file list states

3. **Phase 3 - JavaScript** (~2 hours)
   - Auto-load logic
   - File list rendering
   - Filter/sort implementation

4. **Phase 4 - Search Updates** (~1 hour)
   - Update search methods
   - Add include/exclude filtering
   - Test all search modes

5. **Phase 5 - Cleanup** (~30 minutes)
   - Remove upload code
   - Update documentation
   - Final testing

---

## Success Criteria

✅ Playground auto-loads corpus on startup
✅ Initial load completes in ~10 seconds
✅ All 666 texts visible with checkboxes
✅ Filters work (name, author, genre, sort)
✅ Select all/none buttons functional
✅ Proximity search: instant results (0.1-0.5s)
✅ Paragraph search: instant results
✅ Document search: instant results
✅ No XML loading during search (console confirms)
✅ Include/exclude respected in search
✅ Targeted research works (uncheck 664, search 2)
✅ Results display context from words array
✅ No errors in console
✅ Documentation updated

---

## Risk Mitigation

### Risk: Index too large for slow connections
**Mitigation**:
- Show download progress
- Cache in IndexedDB (30-day TTL)
- Subsequent visits instant
- Future: Add "lite mode" option

### Risk: Memory issues on older devices
**Mitigation**:
- Target: Modern desktop browsers
- Document minimum requirements
- Future: Add progressive loading option

### Risk: Users miss upload feature
**Mitigation**:
- Include/exclude provides same functionality
- Better UX (no manual upload needed)
- Document migration in help text

---

**End of Plan**
