# PoS Disambiguation Scripts

Scripts for Middle High German (MHG) Part-of-Speech disambiguation workflow. These scripts support an LLM-based validation pipeline that disambiguates compound PoS tags and fills missing tags in TEI-encoded texts.

## Workflow Overview

```
TEI file → Split into chunks → LLM processes → Fix malformed → Merge → Validate → (Refine if needed)
```

**Related documentation:** See `.gemini/skills/pos-disambiguator/SKILL.md` for the complete LLM workflow specification including the 19-tag tagset, disambiguation rules, and error patterns.

---

## Scripts (in workflow order)

### 1. `split-tei-for-pos-validation.py`

**Purpose:** Split a TEI file into manageable markdown chunks for LLM processing.

**When to use:** Start of disambiguation workflow (Phase 1).

**Usage:**
```bash
python .gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py tei/ABG.tei.xml
python .gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py tei/ABG.tei.xml --chunk-size 500
python .gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py tei/ABG.tei.xml --output-dir temp/disambiguation
```

**Input:** `tei/{SIGLE}.tei.xml`
**Output:**
- `temp/disambiguation/{SIGLE}.tei-chunk-{NUM}.md` (multiple chunk files)
- `temp/disambiguation/{SIGLE}.tei-manifest.txt` (list of all chunks)

**Notes:**
- Default chunk size: 500 words
- Default output directory: `temp/disambiguation`
- Each chunk contains context text and word list with markers:
  - `⚠️` compound tags (need disambiguation)
  - `❓` missing tags (need assignment)
  - `✓` single tags (verify or correct)

---

### 2. `find-and-fix-malformed-results.py`

**Purpose:** Detect and fix malformed result lines in LLM output before merging.

**When to use:** After LLM processing, before merge (Phase 3 preparation).

**Usage:**
```bash
# Dry run - see what would be fixed
python .gemini/skills/pos-disambiguator/scripts/find-and-fix-malformed-results.py temp/disambiguation --dry-run

# Apply fixes
python .gemini/skills/pos-disambiguator/scripts/find-and-fix-malformed-results.py temp/disambiguation
```

**Input:** `temp/disambiguation/*-result*.md`
**Output:** Same files, with malformed lines corrected

**Detects and fixes:**
- `ID | ⚠️ word (OLD) - NEW | conf | reason` → `ID | OLD → NEW | conf | reason`
- `ID | ❓ word () - NEW | conf | reason` → `ID |  → NEW | conf | reason`
- `ID | ✓ word (OLD) - NEW | conf | reason` → `ID | OLD → NEW | conf | reason`
- Hyphen `-` instead of arrow `→`

**Also validates:**
- Valid PoS tags (19-tag set + ART, DIG)
- Valid confidence levels (high, medium, low)
- Non-empty reason field

---

### 3. `merge-pos-validation-results.py`

**Purpose:** Merge LLM validation results from markdown files into a disambiguated TEI file.

**When to use:** After LLM processing and fixing malformed results (Phase 3).

**Usage:**
```bash
python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation ABG.tei tei/ABG.tei.xml
```

**Input:**
- `temp/disambiguation/{SIGLE}*-result*.md` (all result files)
- `tei/{SIGLE}.tei.xml` (original TEI)

**Output:**
- `tei/{SIGLE}.disamb.tei.xml` (disambiguated TEI)
- `tei/{SIGLE}.disambiguation-report.md` (change report)

**Key behaviors:**
- **Last-Write-Wins:** If duplicate IDs exist, the last occurrence wins
- **FIX files:** Files matching `*_FIX*.md` are processed AFTER base results, allowing corrections to overwrite
- **Integrity check:** Validates result files before merging (can skip with `--skip-integrity-check`)
- **Compound tags:** Adds `reason` attribute when keeping compound tags (morphological fusions)

**Expected result line format:**
```
xml_id | old_pos → new_pos | confidence | reason
```

---

### 4. `validate-disambiguation.py`

**Purpose:** Validate disambiguated TEI files against their originals.

**When to use:** After merge to verify disambiguation quality (Phase 4).

**Usage:**
```bash
python .gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py
```

**Input:** All `tei/*.disamb.tei.xml` files and their corresponding `tei/*.tei.xml` originals
**Output:** Console report of validation status for ALL files

**Checks:**
- No remaining compound PoS tags without `reason` attribute
- No empty PoS tags
- No unexpected content changes (only `pos`, `reason` attributes and `<change>` entries should differ)
- Structure integrity preserved

**Success criteria:**
- All compound tags have `reason` attribute (documented exceptions)
- No empty tags remain
- No structural changes

---

### 5. `find-missing-decisions.py`

**Purpose:** Find words that the LLM skipped during processing.

**When to use:** Phase 5 refinement - when chunks need re-processing.

**Usage:**
```bash
# All files in directory
python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation

# Filter by SIGLE
python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation ADP

# JSON output for scripting
python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation --json
```

**Input:**
- `temp/disambiguation/{SIGLE}.tei-chunk-*.md` (source chunks)
- `temp/disambiguation/{SIGLE}.tei-chunk-*-result*.md` (result files)

**Output:** Console report showing:
- Which chunks have missing decisions
- Count of missing IDs per chunk
- Total missing decisions

**How it works:** Compares `⚠️` and `❓` items in source chunks against IDs in result files.

---

### 6. `prepare-fix-task.py`

**Purpose:** Prepare a focused fix task for a specific chunk with missing decisions.

**When to use:** Phase 5 refinement - to create targeted LLM tasks.

**Usage:**
```bash
python .gemini/skills/pos-disambiguator/scripts/prepare-fix-task.py temp/disambiguation/ADP.tei-chunk-026.md
```

**Input:** Path to a source chunk file
**Output:** Console output with:
- Context text from the chunk
- List of only the missing items (not already in result files)

**Workflow:** Pipe output to a new FIX task file or use directly as LLM input.

---

## File Naming Conventions

| Pattern | Description |
|---------|-------------|
| `{SIGLE}.tei.xml` | Original TEI file |
| `{SIGLE}.disamb.tei.xml` | Disambiguated TEI file |
| `{SIGLE}.disambiguation-report.md` | Change report from merge |
| `{SIGLE}.tei-chunk-{NUM}.md` | Input chunk for LLM |
| `{SIGLE}.tei-chunk-{NUM}-result.md` | LLM output (base results) |
| `{SIGLE}.tei-chunk-{NUM}-result_FIX*.md` | Correction files (override base) |
| `{SIGLE}.tei-manifest.txt` | List of all chunks for a SIGLE |

**SIGLE examples:** ABG, ABS, AC1, AC2, AC3, ADP, EUS

---

## Typical Workflow Example

```bash
# 1. Split TEI into chunks
python .gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py tei/ABG.tei.xml

# 2. (LLM processes chunks - external to these scripts)
#    Reads: temp/disambiguation/ABG.tei-chunk-001.md, ABG.tei-chunk-002.md, ...
#    Writes: temp/disambiguation/ABG.tei-chunk-001-result.md, ...

# 3. Fix any malformed LLM output
python .gemini/skills/pos-disambiguator/scripts/find-and-fix-malformed-results.py temp/disambiguation

# 4. Merge results into TEI
python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation ABG.tei tei/ABG.tei.xml

# 5. Validate the result
python .gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py

# 6. If issues remain, find what's missing
python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation ABG

# 7. Prepare targeted fix tasks for missing items
python .gemini/skills/pos-disambiguator/scripts/prepare-fix-task.py temp/disambiguation/ABG.tei-chunk-005.md > temp/disambiguation/ABG.tei-chunk-005-FIX-TASK.md

# 8. (LLM processes fix task, writes ABG.tei-chunk-005-result_FIX-01.md)

# 9. Re-merge (FIX files automatically override base results)
python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation ABG.tei tei/ABG.tei.xml

# 10. Validate again
python .gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py
```

---

## Result Line Format Reference

The merge script expects this exact format:

```
xml_id | old_pos → new_pos | confidence | reason
```

**Examples:**
```
ABG_123 | ADV CNJ → ADV | high | adverb in comparative context
ABG_456 |  → DET | high | indefinite article (formerly empty)
ABG_789 | VRB PRO → VRB PRO | high | morphological fusion 'machst+du' | reason="machst+du"
```

**Fields:**
- `xml_id`: The `xml:id` attribute from `<w>` element
- `old_pos`: Original PoS (can be empty for missing tags, can be compound like "ADV CNJ")
- `new_pos`: New PoS (usually single tag, compound only for documented fusions)
- `confidence`: `high`, `medium`, or `low`
- `reason`: Linguistic justification for the decision

**Arrow:** Must use `→` (Unicode U+2192), NOT hyphen `-`
