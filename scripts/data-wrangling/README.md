# Data Wrangling Scripts

Scripts for transforming and updating TEI source data from external sources (Zotero, database exports, etc.).

## Overview

The data-wrangling directory contains tools for maintaining the MHDBDB TEI corpus through two main workflows:

1. **PoS Validation & Disambiguation**: LLM-based linguistic analysis to disambiguate compound Part-of-Speech tags and assign missing PoS tags in TEI files
2. **Metadata Synchronization**: Fetch metadata from external sources (Zotero) and sync to authority files and TEI headers

## TEI Model Tools (`tei-model/`)

Scripts for TEI schema audit, corpus analysis, and validation (Issue #32).

### `tei-model/audit-tei-corpus.py`
Element and attribute inventory of the entire TEI corpus. Analyses all base TEI files (excluding `.disamb.tei.xml`) and produces a complete inventory of elements, attributes, and values. Used to inform the TEI Soll-Modell.

### `tei-model/audit-authority-files.py`
Structure, cross-reference, and data quality audit for all 7 authority files. Checks ID patterns, orphaned references, and structural consistency.

### `tei-model/validate-corpus.py`
Two-stage corpus validation: TEI P5 conformity (`tei_all.rng`) + MHDBDB constraints (`mhdbdb.rng`). Validates all 666 corpus files and reports errors.

### `tei-model/TEXT_DATA_TABLE.xlsx`
Linecode mapping table from the legacy MHDBDB system. Contains per-text metadata including the original Linecode definitions (column E). Reference for structural reconstruction (Issues #23, #30, #31).

---

## Scripts

### `split-tei-for-pos-validation.py`

**Purpose:** Split large TEI files into readable markdown chunks for LLM-based PoS (Part-of-Speech) validation and disambiguation.

**Status:** ✅ Production-ready

**Workflow:**
1. Extracts all `<w>` elements from a TEI file
2. Identifies three categories of words:
   - ⚠️ **Compound tags** (e.g., `pos="VRB VEX"`) - MUST disambiguate
   - ❓ **Missing tags** (empty `pos` attribute) - MUST assign PoS tag
   - ✓ **Single tags** (e.g., `pos="NOM"`) - Validate correctness
3. Creates focused chunks centered on compound tags with surrounding context
4. Generates human-readable markdown files for linguistic analysis

**Usage:**
```bash
# Split a TEI file into chunks (default: 50 compound tags per chunk, 10 context words)
python scripts/data-wrangling/split-tei-for-pos-validation.py tei/ABG.tei.xml

# Custom chunk size
python scripts/data-wrangling/split-tei-for-pos-validation.py tei/ABG.tei.xml --chunk-size 30 --context-size 15

# Custom output directory
python scripts/data-wrangling/split-tei-for-pos-validation.py tei/ABG.tei.xml --output-dir custom/path
```

**Command-Line Arguments:**
- `tei_file` - Path to TEI file (e.g., `tei/ABG.tei.xml`)
- `--chunk-size` - Number of compound tags per chunk (default: 50)
- `--context-size` - Number of context words before/after (default: 10)
- `--output-dir` - Output directory for chunks (default: `temp/disambiguation`)

**Output:**
- Creates `temp/disambiguation/{SIGLE}-chunk-XXX.md` markdown files
- Creates `temp/disambiguation/{SIGLE}-manifest.txt` with chunk inventory
- Each chunk contains:
  - Context text (continuous MHG reading)
  - Word list with markers (⚠️/❓/✓)
  - Instructions for LLM analysis

**Dependencies:**
- `lxml` - XML parsing
- Python 3.13+

---

### `merge-pos-validation-results.py`

**Purpose:** Merge LLM validation results from markdown chunks back into TEI files.

**Status:** ✅ Production-ready

**Workflow:**
1. Reads all `{SIGLE}-chunk-*-result.md` files from output directory
2. Parses each line in format: `xml_id | old_pos → new_pos | confidence | reason`
3. Updates the original TEI file's `<w pos="...">` attributes
4. Adds `<change>` entry to `<revisionDesc>` with timestamp and description
5. Creates disambiguated output: `tei/{SIGLE}.disamb.tei.xml`
6. Generates human-readable report: `tei/{SIGLE}.disambiguation-report.md`

**Usage:**
```bash
# Merge results for a specific TEI file
python scripts/data-wrangling/merge-pos-validation-results.py temp/disambiguation ABG.tei tei/ABG.tei.xml

# Arguments: <results_dir> <sigle> <original_tei_file>
```

**Command-Line Arguments:**
- `results_dir` - Directory containing result files (e.g., `temp/disambiguation`)
- `sigle` - SIGLE identifier (e.g., `ABG.tei`)
- `tei_file` - Path to original TEI file (e.g., `tei/ABG.tei.xml`)

**Output:**
- `tei/{SIGLE}.disamb.tei.xml` - Disambiguated TEI file with updated `pos` attributes
- `tei/{SIGLE}.disambiguation-report.md` - Summary report with statistics

**Dependencies:**
- `lxml` - XML parsing and manipulation
- Python 3.13+

---

### `validate-disambiguation.py`

**Purpose:** Validate disambiguated TEI files to ensure quality and completeness.

**Status:** ✅ Production-ready

**Workflow:**
1. Finds all `*.disamb.tei.xml` files in `tei/` directory
2. Compares each against its original `*.tei.xml` file
3. Checks for three types of problems:
   - **Compound tags remaining**: Any `pos` attribute with spaces (e.g., `pos="ADV CNJ"`)
   - **Empty tags remaining**: Any `pos` attribute that is empty or whitespace
   - **Structure changes**: XML elements added/removed (besides expected `<change>` entry)

**Usage:**
```bash
# Validate all disambiguation files in tei/ directory
python scripts/data-wrangling/validate-disambiguation.py
```

**Output Format:**
```
Problems found in ABG.disamb.tei.xml:

Still has 42 compound PoS tag(s):
  - ABG_402050_12: pos='ADV CNJ'
  - ABG_402050_13: pos='VRB VEX'
  ...

Has 15 empty PoS tag(s):
  - ABG_400004_11
  - ABG_400005_08
  ...
```

Or if clean:
```
ALL OK
✓ Validated 2 disambiguation file(s)
```

**Dependencies:**
- `lxml` - XML parsing and comparison
- Python 3.13+

---

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

## Complete Workflow: PoS Validation & Disambiguation

**Goal:** Disambiguate compound PoS tags and assign missing PoS tags in TEI files using LLM-based linguistic analysis.

**Overview:** This workflow uses the `pos-disambiguator` agent to perform Middle High German grammatical analysis on TEI word elements. The agent works autonomously through a 5-phase pipeline to process, validate, and refine PoS tags until perfect.

### Prerequisites
```bash
# Ensure Python dependencies are installed
pip install lxml

# Ensure pos-disambiguator agent is available
# Located at: .claude/agents/pos-disambiguator.md
```

### Phase 1: Split TEI File into Chunks
```bash
# Split a TEI file with compound tags
python scripts/data-wrangling/split-tei-for-pos-validation.py tei/ABG.tei.xml

# Expected output:
# Processing tei/ABG.tei.xml...
# SIGLE: ABG.tei
# Chunk size: 50 compound tags per chunk
# Context size: 10 words before/after
#
# Total words: 4,532
# Words with compound PoS tags: 1,245
#
# Created 25 chunks
#
# [OK] Created temp/disambiguation/ABG.tei-chunk-001.md (50 compound tags, 115 total words)
# [OK] Created temp/disambiguation/ABG.tei-chunk-002.md (50 compound tags, 118 total words)
# ...
# [OK] Created manifest: temp/disambiguation/ABG.tei-manifest.txt
```

**What happens:**
- Extracts all `<w>` elements from TEI file
- Identifies compound tags (⚠️), missing tags (❓), and single tags (✓)
- Creates markdown chunks with context for linguistic analysis
- Generates manifest file listing all chunks

### Phase 2: Process Chunks with pos-disambiguator Agent
```bash
# Invoke the agent (via Claude Code CLI or API)
# Agent command: "Process all TEI files in temp/disambiguation"
```

**What the agent does autonomously:**

**Phase 1 - Discovery & Resume:**
- Scans `temp/disambiguation/` for manifest files
- Identifies which chunks need processing
- Prioritizes incomplete work and resumes where it left off

**Phase 2 - Linguistic Analysis:**
- Reads each chunk markdown file
- Analyzes Middle High German grammar and context
- Disambiguates compound tags (e.g., `VRB VEX → VEX`)
- Assigns missing PoS tags (e.g., ` → ADV`)
- Validates single tags for correctness
- Writes result files: `{SIGLE}-chunk-XXX-result.md`
- Reports progress every 5 chunks

**Phase 3 - Integration:**
- Runs merge script automatically after all chunks complete
- Creates `tei/{SIGLE}.disamb.tei.xml` with updated PoS tags
- Generates `tei/{SIGLE}.disambiguation-report.md`

**Phase 4 - Validation:**
- Runs validation script automatically
- Parses output for remaining problems (compound tags, empty tags)
- Decides whether to refine or move to next file

**Phase 5 - Refinement:**
- Fixes any remaining errors by re-analyzing specific words
- Edits result files with corrected decisions
- Re-merges and re-validates until clean
- Continues until ALL files pass validation

**Agent output example:**
```
✓ ABG.tei COMPLETE
  - Chunks processed: 25/25
  - Words validated: 4,532
  - Changes made: 1,245
  - Validation: CLEAN
  - Status: Moving to next file

✓ ABS.tei COMPLETE
  - Chunks processed: 17/17
  - Words validated: 3,018
  - Changes made: 892
  - Validation: CLEAN
  - Status: Moving to next file

ALL FILES VALIDATED AND COMPLETE
```

### Phase 3: Review Results

**Check disambiguation reports:**
```bash
# View summary report
cat tei/ABG.tei.disambiguation-report.md

# Example report content:
# PoS Validation Results for ABG.tei
# Generated: 2025-01-14 10:30:15
#
# Total words processed: 4,532
# Changes made: 1,245
# - Compound tags disambiguated: 1,198
# - Missing tags assigned: 47
# - Single tags corrected: 0
#
# High confidence decisions: 1,180 (94.8%)
# Low confidence decisions: 65 (5.2%)
```

**Verify validation passed:**
```bash
# Run validation manually to confirm
python scripts/data-wrangling/validate-disambiguation.py

# Expected output if all clean:
# ALL OK
# ✓ Validated 2 disambiguation file(s)
```

**Review git diff:**
```bash
# Check changes to TEI files
git diff tei/ABG.disamb.tei.xml

# Should show:
# - Updated pos attributes (compound → single, empty → assigned)
# - New <change> entry in <revisionDesc>
# - No other structural changes
```

### Phase 4: Replace Original Files (Optional)

**If disambiguation is production-ready:**
```bash
# Backup originals first
mkdir tei-backup
cp tei/*.tei.xml tei-backup/

# Replace originals with disambiguated versions
mv tei/ABG.disamb.tei.xml tei/ABG.tei.xml
mv tei/ABS.disamb.tei.xml tei/ABS.tei.xml

# Rebuild corpus index
python scripts/build-corpus-index.py
```

### Phase 5: Clean Up

**Remove temporary files:**
```bash
# Remove chunk files and results
rm -rf temp/disambiguation/

# Keep disambiguation reports for documentation
# Files: tei/*.disambiguation-report.md
```

### Phase 6: Commit Changes
```bash
# Review all changes
git status
git diff tei/

# Commit
git add tei/
git commit -m "Disambiguate compound PoS tags via LLM analysis

- Processed 2 TEI files (ABG.tei, ABS.tei)
- Disambiguated 2,090 compound tags
- Assigned 78 missing PoS tags
- All files pass validation (no compound/empty tags remaining)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

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
├── README.md                              # This file
├── enhance_works_with_zotero.py          # Zotero API → works.xml (Issue #19)
├── sync_tei_headers.py                   # Authority files → TEI headers (Issue #19)
├── _ARCHIVED_tei-transformation.py       # Reference library (do not run)
├── .zotero_cache.json                    # API response cache (git-ignored)
└── tei-model/                            # TEI schema tools (Issue #32)
    ├── audit-tei-corpus.py               # Element/attribute inventory
    ├── audit-authority-files.py           # Authority files audit
    ├── validate-corpus.py                # Two-stage schema validation
    └── TEXT_DATA_TABLE.xlsx              # Legacy Linecode mapping

temp/disambiguation/                       # LLM workflow temp files (git-ignored)
├── {SIGLE}-manifest.txt                  # Chunk inventory
├── {SIGLE}-chunk-001.md                  # Chunk for LLM analysis
├── {SIGLE}-chunk-001-result.md           # LLM analysis results
└── ...

tei/
├── {SIGLE}.tei.xml                       # Original TEI file
├── {SIGLE}.disamb.tei.xml                # Disambiguated version (after merge)
└── {SIGLE}.disambiguation-report.md      # Human-readable report
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
- **pos-disambiguator Agent:** [.claude/agents/pos-disambiguator.md](../../.claude/agents/pos-disambiguator.md)
- **Issue #19:** Add `<editor>` metadata from Zotero to TEI headers
- **Zotero Collection:** https://www.zotero.org/groups/5043625/mittelhochdeutsche_begriffsdatenbank/collections/7JU362QV
- **MHDBDB Knowledge Docs:** [docs/INDEX.MD](../../docs/INDEX.MD)
- **TEI P5 Guidelines:** https://www.tei-c.org/release/doc/tei-p5-doc/en/html/

---

## Contact

For questions or issues with data wrangling scripts:
- **GitHub Issues:** https://github.com/[repo]/issues
- **Email:** mhdbdb@plus.ac.at
