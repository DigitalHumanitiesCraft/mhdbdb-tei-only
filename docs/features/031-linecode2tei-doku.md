# Issue #31: Doku Linecode2TEI

## Context

The legacy MHDBDB system encoded text structure using "Linecodes" — a positional letter+number scheme predating TEI. Julia's OneDrive folder and the attached PDF document the mapping. This knowledge exists only in Julia's head and a PDF attachment on the issue — it needs to be in the repo as permanent reference documentation.

**Priority:** Quick win (effort:small), but **blocks #23** (fehlende Stanza-Auszeichnung, 104 Texte). Without understanding the Linecodes, complex structural cases in #23 can't be resolved.

## Source Material

- Julia's PDF: `Zusammenfassung-Linecode2TEI.pdf` (attached to Issue #31)
- OneDrive folder (Katharina's SharePoint): conversion tables, original data
- Key files referenced: `TEXT_DATA_TABLE.csv` (Column E), `Mhdbdb_to_TEI.xlsx`, `Dokumentation.xlsx`

## The Linecode System

### Principle

Each text in the old MHDBDB had a plaintext body + a parallel "Linecode" string. Each letter position in the Linecode represents a structural element; each number group is the running count of that element.

Today's `xml:id` attributes on `<w>` elements are the **surviving fragment** of the Linecode — the non-zero portion. Example: `ALL_20100010_0` derives from Linecode position `0000000000aaau----h` where `20100010` encodes the structural position (paragraph, parallel transmission, line).

### Reading Direction

Linecodes are read **right to left**. Each letter corresponds to a TEI structure:

### Translation Table

| Code | Legacy Name | TEI Element | Notes |
|------|------------|-------------|-------|
| `-` | LINE | `<l>` or `<lb/>` | `<l>` for verse only; `<lb/>` for prose |
| `a` | PARAGRAPH | `<p>` | |
| `b` | BAND | `<div type="volume">` | Removed post-#32 cleanup |
| `c` | CHAPTER | `<div type="chapter">` | |
| `d` | LIED | `<div type="song">` | |
| `f` | NONGRADED | `<div type="nongraded">` | Text classified as spurious |
| `h` | HEADLINE | `<head>` / `<hi rend="head">` | Value `0` = ignore; often means "bold" rather than structural heading |
| `i` | INSERTION | `<supplied>` | |
| `k` | COMMENT | `<note>` | |
| `l` | HANDWRITINGSHEETCOLUMN | `<cb type="manuscript"/>` | Column beginning |
| `n` | TONVARIATION | `<div type="tonvariation">` | Uncertain mapping |
| `p` | PAGE | `<pb/>` | Page beginning |
| `s` | STANZA | `<lg type="stanza">` | Legacy: often `<div type="stanza">` — migrated to `<lg>` in #32 |
| `t` | TEIL | `<div type="part">` | Removed post-#32 cleanup |
| `u` | PARALLELUEBERLIEFERUNG | `<div type="parallel">` | Count = number of parallel transmissions |
| `v` | HANDWRITINGSHEETPAGE | `<pb type="manuscript"/>` | 1=recto, 2=verso |
| `x` | DATE | `<note type="date">` | Uncertain mapping |
| `y` | YEAR | `<note type="year">` | Uncertain mapping |
| `z` | NUMBER | `<note type="number">` | Uncertain mapping |
| `0` | NULL | (skip) | |

### Worked Example

```
Linecode template:  0000000000aaau----h
xml:id:             ALL_20100010_0

Decode (right to left against template):
  h = ?  → headline
  ---- = ?  → line
  u = ?  → parallel transmission
  aaa = ?  → paragraph

Template has 9 field positions (aaa=3 + u=1 + ----=4 + h=1) but the
xml:id numeric part `20100010` has 8 digits. These don't match — either
the field boundaries are different for this text, or the id-stripping
logic doesn't work as a simple concatenation.

[TODO: verify with Julia via Mhdbdb_to_TEI.xlsx before promoting to docs/LINECODE.md:
1. How does `20100010` (8 digits) map to a 9-position template (3+1+4+1)?
2. Is "aaa = 201" one counter (#201) or multi-level (2/0/1)?
3. Test against a second xml:id from the same text to confirm the pattern.]
```

### Known Pitfalls

1. **`h` (HEADLINE) with value 0**: Does not mean "heading" — means "should be printed bold". Only non-zero values are true headings. Many TEI files incorrectly have `<head>` where `<hi rend="head">` was intended.

2. **`-` (LINE) ambiguity**: Verse texts use `<l>`, prose texts use `<lb/>`. The Linecode doesn't distinguish — the converter applied `<l>` everywhere. This is the root cause of the 21-text `<l>` vs. `<lb/>` problem (see #23).

3. **`s` (STANZA) encoding**: The original converter output `<div type="stanza">`. The #32 migration moved these to `<lg type="stanza">`. Any remaining `<div type="stanza">` instances are conversion artifacts.

4. **`v` (HANDWRITINGSHEETPAGE) recto/verso**: Value 1 = recto, value 2 = verso. Some texts lost this distinction during conversion.

5. **Post-#32 cleanup**: `b` (BAND/volume) and `t` (TEIL/part) div types were removed corpus-wide. The Linecode documents their historical existence but they no longer appear in the TEI files.

## How to Use This Documentation

### For #23 (Stanza-Auszeichnung)

When a text has missing or incorrect stanza markup:
1. Look up the text's sigle in `TEXT_DATA_TABLE.csv` (Column E) for the original Linecode template
2. Find `s` positions — these mark stanza boundaries
3. Compare with current TEI: does every `s` boundary have a corresponding `<lg type="stanza">`?
4. If not, the stanza markup was lost in conversion → fix

### For Debugging xml:id Patterns

Every `<w xml:id="SIG_NNNNNNN_T">` encodes the Linecode:
- `SIG` = text sigle
- `NNNNNNN` = non-zero Linecode digits (structure position)
- `T` = token index within that line

To reverse-engineer structure from xml:id, read the digits against the text's Linecode template.

## Placement

This documentation goes into `docs/` as a permanent reference (not a feature doc — it won't be deleted after #31 closes). Suggested filename: `docs/LINECODE.md`, linked from `docs/INDEX.md` and `docs/TEI-MODEL.md`.

## Files to Touch

- **New:** `docs/LINECODE.md` — the documentation itself (content above, polished)
- `docs/INDEX.MD` — add row to documentation table
- `docs/TEI-MODEL.md` — cross-reference where Linecode artifacts are mentioned (line 296)

## Unblocks

- **#23** (fehlende Stanza-Auszeichnung, 104 Texte) — complex cases need Linecode docs to resolve

## Out of Scope

- Rewriting the original conversion scripts (they no longer exist)
- Automated Linecode→TEI re-conversion (one-time conversion already done)
- Archiving the OneDrive source files into the repo (link is sufficient)
