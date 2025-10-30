# Data Wrangling Scripts

Scripts for transforming and updating TEI source data from external sources (Zotero, database exports, etc.).

## Overview

The data-wrangling directory contains tools for maintaining the MHDBDB TEI corpus by fetching metadata from external sources and synchronizing it with TEI files. These scripts implement a **two-step workflow**: (1) update authority files from external sources, (2) sync authority data to TEI headers.

## Scripts

### `enhance_works_with_zotero.py`

**Purpose:** Fetch bibliographic metadata (especially editors) from Zotero API and update `authority-files/works.xml`.

**Status:** ✅ Production-ready (Implements Issue #19)

**Workflow:**
1. Fetches all 1,602 items from MHDBDB Zotero collection via API
2. Extracts editor information from `creators` array
3. Converts JSON data to TEI `<biblStruct>` XML elements
4. Matches items by `callNumber` (sigle) to works in `works.xml`
5. Replaces existing `<biblStruct>` elements with updated data
6. Handles xml:id conflicts automatically

**Usage:**
```bash
# Preview changes (recommended first step)
python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run

# Fetch from API and update works.xml
python scripts/data-wrangling/enhance_works_with_zotero.py

# Save API response for offline use
python scripts/data-wrangling/enhance_works_with_zotero.py --cache

# Use cached data (offline mode)
python scripts/data-wrangling/enhance_works_with_zotero.py --offline
```

**Command-Line Arguments:**
- `--dry-run` - Preview changes without modifying files
- `--cache` - Save API response to `.zotero_cache.json` for offline use
- `--offline` - Use cached data instead of fetching from API

**API Details:**
- **Endpoint:** `https://api.zotero.org/groups/5043625/collections/7JU362QV/items`
- **Authentication:** Not required (public group)
- **Pagination:** 100 items per request (~17 API calls for 1,602 items)
- **Rate Limiting:** 0.3s delay between requests (~3 requests/second)
- **Retry Logic:** Exponential backoff on rate limit errors (429)

**Output:**
- Modifies `authority-files/works.xml` in-place
- Adds/updates `<biblStruct>` elements with `<editor>` metadata
- Logs summary statistics (items processed, matches found, missing sigles)

**Dependencies:**
- `lxml` - XML parsing and manipulation
- `requests` - HTTP client for Zotero API
- Python 3.13+

---

### `sync_tei_headers.py`

**Purpose:** General-purpose tool for synchronizing authority file data to TEI file headers (666 files).

**Status:** ✅ Production-ready (Implements Issue #19)

**Architecture:** Extensible class-based design with `AuthoritySyncer` base class. Currently implements `WorksEditorSyncer` for syncing `<editor>` elements.

**Workflow:**
1. Loads data from authority file (e.g., `works.xml`)
2. Extracts relevant metadata (e.g., editor names from `<biblStruct>`)
3. Matches data to TEI files by sigle (filename: `ASG.tei.xml` → sigle `ASG`)
4. Updates TEI `<teiHeader>` elements (e.g., adds `<editor>` to `<titleStmt>`)
5. Writes updated TEI files with pretty-print formatting

**Usage:**
```bash
# Preview changes (recommended first step)
python scripts/data-wrangling/sync_tei_headers.py --works --dry-run

# Sync works.xml (editor data) to TEI headers
python scripts/data-wrangling/sync_tei_headers.py --works

# Future: Sync multiple authority files
python scripts/data-wrangling/sync_tei_headers.py --all
```

**Command-Line Arguments:**
- `--works` - Sync `works.xml` (editor data) [IMPLEMENTED]
- `--persons` - Sync `persons.xml` (author data) [STUB]
- `--genres` - Sync `genres.xml` (genre classifications) [STUB]
- `--concepts` - Sync `concepts.xml` (concept annotations) [STUB]
- `--all` - Sync all authority files [PARTIAL]
- `--dry-run` - Preview changes without modifying files

**Implemented Syncers:**
| Authority File | Syncer Class | Status | Description |
|----------------|--------------|--------|-------------|
| `works.xml` | `WorksEditorSyncer` | ✅ Complete | Syncs `<editor>` elements to `<titleStmt>` |
| `persons.xml` | `PersonsSyncer` | ⚠️ Stub | Future: Sync author/person metadata |
| `genres.xml` | `GenresSyncer` | ⚠️ Stub | Future: Sync genre classifications |
| `concepts.xml` | `ConceptsSyncer` | ⚠️ Stub | Future: Sync concept annotations |

**Output:**
- Modifies TEI files in `tei/` directory (666 files)
- Updates `<teiHeader>` sections with authority data
- Logs summary statistics (files updated, files skipped)

**Dependencies:**
- `lxml` - XML parsing and manipulation
- Python 3.13+

---

### `_ARCHIVED_tei-transformation.py`

**Purpose:** Original monolithic transformation script from `initial-data-wrangling` branch.

**Status:** ⚠️ **ARCHIVED REFERENCE ONLY - DO NOT RUN**

**Contents:**
- 1,977 lines of transformation logic
- Used for one-time RDF/MySQL → TEI migration
- Contains useful utility functions (CSV parsing, TEI creation, ID normalization)

**Usage:** Extract specific functions into new focused scripts. Do not run this file directly.

**Useful Functions:**
- `detect_delimiter()` - Auto-detect CSV delimiter
- `read_csv_data()` - CSV parsing with caching
- `create_tei_base()` - Generate standard TEI structure
- `normalize_id()` - Add/strip ID prefixes
- XML namespace handling utilities

---

## Complete Workflow: Issue #19

**Goal:** Add `<editor>` metadata from Zotero to TEI headers

**Steps:**

### 1. Fetch Editor Data from Zotero
```bash
# Preview what will change
python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run

# Review output (shows how many works will be updated)

# Fetch from API and update works.xml
python scripts/data-wrangling/enhance_works_with_zotero.py --cache

# Review git diff
git diff authority-files/works.xml
```

**Expected Output:**
```
INFO: Fetching items from Zotero API: https://api.zotero.org/groups/5043625/...
INFO: Fetched 100 items (total: 100)
INFO: Fetched 100 items (total: 200)
...
INFO: Finished fetching all 1602 items
INFO: Processing 1602 items from Zotero
INFO: Processed 666 items with callNumber
INFO: Found 542 items with editors
INFO: Indexed 542 unique callNumbers
INFO: Found 666 work entries
INFO: Replacement summary:
INFO: - Existing biblStruct elements removed: 679
INFO: - New biblStruct elements added: 542
INFO: - Works with replacements: 542
INFO: - Missing sigles: 124
```

### 2. Sync to TEI Headers
```bash
# Preview changes to TEI files
python scripts/data-wrangling/sync_tei_headers.py --works --dry-run

# Review output (shows how many TEI files will be updated)

# Apply changes
python scripts/data-wrangling/sync_tei_headers.py --works

# Review git diff of a few TEI files
git diff tei/ASG.tei.xml
```

**Expected Output:**
```
INFO: Loaded data for 542 sigles from works.xml
INFO: Processing 666 TEI files for works...
INFO: [works] Would update 542 TEI files, skipped 124
INFO: SUMMARY:
INFO:   Total files updated: 542
INFO:   Total files skipped: 124
INFO: NEXT STEPS:
INFO:   python scripts/build-authority-index.py
```

### 3. Rebuild Index
```bash
# Rebuild authority index with updated editor metadata
python scripts/build-authority-index.py

# Verify changes
ls -lh data/authority-index.json.gz
```

### 4. Commit Changes
```bash
# Review all changes
git status
git diff

# Commit
git add authority-files/works.xml tei/
git commit -m "Add editor metadata from Zotero API (Issue #19)

- Fetched 1,602 items from Zotero collection 7JU362QV
- Updated 542 works in works.xml with editor information
- Synced editor data to 542 TEI file headers
- Rebuilt authority index

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

## Troubleshooting

### Network Errors

**Problem:** `Network error while fetching from API`

**Solutions:**
1. Check internet connection
2. Verify Zotero API is accessible: `curl https://api.zotero.org`
3. Use cached data: `python enhance_works_with_zotero.py --offline`
4. Retry after a few minutes (temporary API issues)

### Rate Limiting

**Problem:** `Rate limit exceeded after 3 retries`

**Solutions:**
1. The script automatically retries with exponential backoff
2. If persists, increase `REQUEST_DELAY` in `enhance_works_with_zotero.py` (line 67)
3. Use cached data for development: `--cache` then `--offline`

### Missing Sigles

**Problem:** Log shows "Missing sigles: 124" (works with no Zotero match)

**Expected Behavior:** Some works may not have Zotero entries yet. This is normal.

**Action:** Review list in log output. If critical works are missing, check Zotero library.

### No titleStmt Found

**Problem:** `[works] {sigle}: No titleStmt found`

**Solutions:**
1. Check TEI file structure (should have `<teiHeader><fileDesc><titleStmt>`)
2. Fix malformed TEI file
3. File will be skipped (not a fatal error)

### Cache File Not Found

**Problem:** `Cache file not found: scripts/data-wrangling/.zotero_cache.json`

**Solution:** Run without `--offline` first to fetch and cache data:
```bash
python scripts/data-wrangling/enhance_works_with_zotero.py --cache
```

---

## Best Practices

### Always Preview First
```bash
# ALWAYS run with --dry-run first
python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run
python scripts/data-wrangling/sync_tei_headers.py --works --dry-run
```

### Save Cache for Development
```bash
# Fetch once, develop offline
python scripts/data-wrangling/enhance_works_with_zotero.py --cache
python scripts/data-wrangling/enhance_works_with_zotero.py --offline --dry-run
```

### Review Git Diffs
```bash
# After each step, review changes
git diff authority-files/works.xml
git diff tei/*.tei.xml | head -100
```

### Test on Subset First
```bash
# For testing, manually limit TEI files
mkdir tei-backup
mv tei/*.tei.xml tei-backup/
cp tei-backup/ASG.tei.xml tei/
cp tei-backup/WH.tei.xml tei/

# Run sync
python scripts/data-wrangling/sync_tei_headers.py --works

# Restore
mv tei-backup/*.tei.xml tei/
rmdir tei-backup
```

### Commit Incrementally
```bash
# Commit authority file changes separately from TEI changes
git add authority-files/works.xml
git commit -m "Update works.xml with editor data from Zotero"

git add tei/
git commit -m "Sync editor metadata to TEI headers"
```

---

## Development

### Adding New Syncers

To add support for syncing other authority files (e.g., `persons.xml`):

1. **Implement Syncer Class** in `sync_tei_headers.py`:
```python
class PersonsSyncer(AuthoritySyncer):
    def load_authority_data(self) -> Dict:
        """Load person data from persons.xml."""
        # Extract person names, GND IDs, etc.
        return person_data

    def update_tei_header(self, tei_tree, sigle, data, dry_run) -> bool:
        """Update <author> elements in TEI header."""
        # Find and update <author> elements
        return True
```

2. **Register Syncer** in `SYNCERS` dictionary (line 260):
```python
SYNCERS = {
    'works': WorksEditorSyncer,
    'persons': PersonsSyncer,  # NEW
    'genres': GenresSyncer,
    'concepts': ConceptsSyncer,
}
```

3. **Test**:
```bash
python scripts/data-wrangling/sync_tei_headers.py --persons --dry-run
```

### Testing

**Manual Testing:**
```bash
# Test API fetch
python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run

# Test cache
python scripts/data-wrangling/enhance_works_with_zotero.py --cache --dry-run
python scripts/data-wrangling/enhance_works_with_zotero.py --offline --dry-run

# Test sync
python scripts/data-wrangling/sync_tei_headers.py --works --dry-run
```

**Validation:**
```bash
# Check XML validity
xmllint --noout authority-files/works.xml
xmllint --noout tei/ASG.tei.xml

# Check index builds
python scripts/build-authority-index.py
python scripts/validate-indices.py
```

---

## File Structure

```
scripts/data-wrangling/
├── README.md                           # This file
├── enhance_works_with_zotero.py       # Zotero API → works.xml (Issue #19)
├── sync_tei_headers.py                # Authority files → TEI headers (Issue #19)
├── _ARCHIVED_tei-transformation.py    # Reference library (do not run)
└── .zotero_cache.json                 # API response cache (git-ignored)
```

---

## Dependencies

All scripts require Python 3.13+ with the following packages:

```bash
pip install lxml requests
```

Verify installation:
```bash
python -c "import lxml; import requests; print('OK')"
```

---

## Related Documentation

- **Main scripts README:** [scripts/README.md](../README.md)
- **Issue #19:** Add `<editor>` metadata from Zotero to TEI headers
- **Zotero Collection:** https://www.zotero.org/groups/5043625/mittelhochdeutsche_begriffsdatenbank/collections/7JU362QV
- **MHDBDB Knowledge Docs:** [docs/INDEX.MD](../../docs/INDEX.MD)

---

## Contact

For questions or issues with data wrangling scripts:
- **GitHub Issues:** https://github.com/[repo]/issues
- **Email:** mhdbdb@plus.ac.at
