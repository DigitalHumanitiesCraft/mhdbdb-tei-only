# JavaScript Refactoring Plan

## Goal
Clean up JavaScript organization: eliminate name collisions, extract shared code, decompose monolithic files (1065+ lines → 150-300 lines each).

## Directory Structure

### After Refactoring
```
lib/                          # NEW - Shared utilities
├── indexed-db-base.js        # NEW - Base IndexedDB class
├── text-normalizer.js        # MOVED from playground/js/utils/
├── corpus-loader.js          # MOVED from js/
└── README.md

js/                           # Main site (keep folder name)
├── site-main.js              # RENAMED from main.js
├── app.js                    # RENAMED from main-site.js
├── search/
│   ├── search-engine.js
│   └── search-ui.js          # SPLIT from search-engine.js
├── rendering/
│   ├── text-renderer.js
│   └── annotation-renderer.js # SPLIT from text-renderer.js
└── storage/
    └── tei-cache-manager.js

playground/js/                # Playground (keep folder name)
├── playground-main.js        # RENAMED from main.js
├── data/                     # NEW - Data layer
│   ├── authority-manager.js  # RENAMED from authority-files.js
│   ├── tei-manager.js        # RENAMED from tei-files.js
│   └── storage/
│       ├── tei-storage.js    # RENAMED from storage-manager.js
│       └── authority-storage.js
├── ui/                       # UI layer (decomposed)
│   ├── core/                 # NEW
│   │   ├── ui-helpers.js     # SPLIT from UICore.js
│   │   ├── progress.js       # SPLIT from UICore.js
│   │   └── file-display.js   # SPLIT from UICore.js
│   ├── authority/            # NEW
│   │   ├── authority-ui.js        # Coordinator (was AuthorityExplorers.js)
│   │   ├── person-explorer.js     # SPLIT
│   │   ├── work-explorer.js       # SPLIT
│   │   ├── lemma-explorer.js      # SPLIT
│   │   ├── concept-explorer.js    # SPLIT
│   │   ├── genre-explorer.js      # SPLIT
│   │   └── name-explorer.js       # SPLIT
│   ├── tei/                  # NEW
│   │   ├── tei-ui.js              # RENAMED from TEIExplorer.js
│   │   ├── lemma-search.js        # SPLIT from TEIExplorer.js
│   │   └── multi-lemma-search.js  # Keep existing
│   └── search/
│       └── search-helpers.js      # Keep existing
└── utils/                    # Minimal (text-normalizer moved to /lib)
```

## Implementation Phases

### Phase 1: Preparation
- ✅ Create refactoring plan
- ⬜ Create feature branch: `refactor/js-architecture`
- ⬜ Create backup branch: `backup/pre-refactor`

### Phase 2: Create Directory Structure
```bash
# New directories (additive only, no deletions yet)
mkdir lib
mkdir js/search js/rendering js/storage
mkdir playground/js/data playground/js/data/storage
mkdir playground/js/ui/core playground/js/ui/authority playground/js/ui/tei playground/js/ui/search
```

### Phase 3: Extract Shared Library (`/lib`)
1. Create `/lib/indexed-db-base.js` (new base class)
2. Move `playground/js/utils/text-normalizer.js` → `/lib/text-normalizer.js`
3. Copy `js/corpus-loader.js` → `/lib/corpus-loader.js`
4. Update imports in playground
5. Test playground works

### Phase 4: Decompose AuthorityExplorers.js (1065 lines → 7 files)
Split into:
- `authority-ui.js` (coordinator, ~200 lines)
- `person-explorer.js` (~150 lines)
- `work-explorer.js` (~200 lines)
- `lemma-explorer.js` (~250 lines)
- `concept-explorer.js` (~150 lines)
- `genre-explorer.js` (~150 lines)
- `name-explorer.js` (~150 lines)

### Phase 5: Decompose UICore.js (703 lines → 3 files)
Split into:
- `file-display.js` (~200 lines)
- `progress.js` (~150 lines)
- `ui-helpers.js` (~350 lines)

### Phase 6: Reorganize TEI Files
- Rename `tei-files.js` → `data/tei-manager.js`
- Rename `authority-files.js` → `data/authority-manager.js`
- Rename `storage-manager.js` → `data/storage/tei-storage.js`
- Split `TEIExplorer.js` → `ui/tei/tei-ui.js` + `ui/tei/lemma-search.js`
- Move `MultiLemmaSearch.js` → `ui/tei/multi-lemma-search.js`

### Phase 7: Reorganize Main Site Files
- Move `js/main.js` → `js/site-main.js`
- Move `js/main-site.js` → `js/app.js`
- Move `js/search-engine.js` → `js/search/search-engine.js`
- Move `js/text-renderer.js` → `js/rendering/text-renderer.js`
- Move `js/tei-cache-manager.js` → `js/storage/tei-cache-manager.js`
- Update `index.html` script paths

### Phase 8: Rename `main.js` Files (Eliminate Collision)
- Rename `playground/js/main.js` → `playground/js/playground-main.js`
- Update `playground/index.html`:
  ```html
  <script type="module" src="js/playground-main.js"></script>
  ```

### Phase 9: Update Documentation
- Update `CLAUDE.md` with new structure
- Create `/lib/README.md`
- Update `/playground/README.md`

### Phase 10: Final Validation
- Run full test suite: `npm test`
- Manual testing checklist (all 11 search entry points)
- Delete old files (only after validation)
- Clean up orphaned files

## Key Import Path Changes

### Before
```javascript
// playground/index.html
<script type="module" src="js/main.js"></script>

// playground/js/main.js
import { AuthorityExplorers } from './ui/AuthorityExplorers.js';
import { TextNormalizer } from './utils/text-normalizer.js';
```

### After
```javascript
// playground/index.html
<script type="module" src="js/playground-main.js"></script>

// playground/js/playground-main.js
import { AuthorityUI } from './ui/authority/authority-ui.js';
import { TextNormalizer } from '../../lib/text-normalizer.js';
```

## Rollback Strategy
```bash
# If critical issues occur:
git checkout backup/pre-refactor
git checkout -b hotfix/revert-refactor
```

## Success Criteria
- ✅ No files >400 lines
- ✅ No name collisions
- ✅ 100% test pass rate
- ✅ Zero functionality regressions

**Estimated Time:** 20 hours (phased over 2-3 weeks)
