# Issue #17: Reader View — TEI Structural Elements

## Context

The reading view (`tei-text-reader.js`) renders full-text TEI with multi-lemma highlighting and Wikidata metadata. But structural elements are rendered minimally: users cannot visually distinguish stanzas from paragraphs, verse lines from prose line breaks, or navigate by page/column boundaries.

Katharina's core requirement: users must **see and understand the editorial structure** of the text, not just the words. Prerequisite before going public.

**Priority:** prio-1, unblocked by #32 completion.

## Current State

`assets/js/rendering/tei-text-reader.js`, method `extractAndFormatBody()` (line 328) already handles:

| TEI element | Current output | Gap |
|-------------|---------------|-----|
| `<head>` | `<h3 class="section-head">` | Adequate |
| `<p>`, `<ab>` | `<p>` | No visual distinction from verse |
| `<div>` | `<div class="tei-div">` | No `@type` rendering (song, chapter, recipe...) |
| `<lg>` | `<div class="verse-group">` | No stanza numbering |
| `<l>` | `<span class="verse-line">` | No line number display |
| `<lb>` | `<br class="line-break">` | No line number display |
| `<pb n>` | `<span class="page-break">[N]</span>` | Minimal styling |
| `<cb n>` | `<span class="column-break">[Sp. N]</span>` | Minimal styling |
| `<hi rend="initial">` | `<span class="initial">` | Adequate |
| `<caesura>` | `<span class="caesura">\|\|</span>` | Adequate |
| `<supplied>` | `<span class="supplied" title="...">[content]</span>` | Adequate |
| `<num>` | `<span class="number">` | Adequate |
| `<note>` | (no case — falls through to default) | No year/date badge rendering |

CSS lives in `assets/css/korpus.css` (lines 352-446). Reading body uses Georgia serif, 1.125rem, line-height 1.8.

## Requirements (from Katharina's Issue)

### Must-Have: Semantic Distinction

The single most important requirement:

- **`<l>`** = Verszeile (poetry). Render with verse-line number, indentation, grouped inside `<lg>`.
- **`<lb/>`** = Zeilenumbruch (prose). Render as layout break with line number, no grouping.

Users working with both metrical and prose texts must immediately see which is which.

### Must-Have: Structural Rendering

| TEI element | Rendering |
|-------------|-----------|
| `<div type="song">` | Section header with song number |
| `<div type="chapter">` | Section header with chapter number |
| `<div type="recipe">` | Section header with recipe number |
| `<div type="section">` | Subtle separator |
| `<div type="number">` | Numbered section |
| `<div type="colophon">` | Italic/distinguished block |
| `<lg type="stanza" n>` | Stanza block with number in margin |
| `<l n>` | Verse number in margin (every 5th line, or configurable) |
| `<lb n>` | Line number in margin (prose) |
| `<pb n>` | Page marker in margin or inline badge |
| `<cb n>` | Column marker |
| `<head>` | Section heading (already works) |

### Must-Have: Attribute Display

| Attribute | Where | Rendering |
|-----------|-------|-----------|
| `@type` on `<div>` | Section headers | Label (e.g. "Lied 3", "Kapitel 12", "Rezept 45") |
| `@n` on structural elements | Margins | Number display |
| `@rend` on `<hi>` | Inline | `initial`, `upper_case`, `bold`, `italic` |
| `@type="year"` on `<note>` | Inline | Year badge |
| `@type="date"` on `<note>` | Inline | Date badge |

## Design Approach

### CSS-Driven, Not JS-Heavy

The `extractAndFormatBody()` switch already maps TEI → HTML. Changes needed:

1. **Enrich the HTML output** — add `data-type`, `data-n` attributes from TEI to the generated HTML elements
2. **Add CSS rules** in `korpus.css` — margin numbers, section separators, stanza blocks, prose vs. verse distinction
3. **Minimal JS changes** — the switch statement grows, but logic stays simple

### Verse vs. Prose Visual Language

```
VERSE (poetry):                    PROSE:
                                   
  Lied 3                           Kapitel 12
  ─────────                        ─────────────────────
                                   
  Strophe 1                        1  Daz was ein ritter
  1  Dô sprach der ritter          2  der hete lange gesezzen
     guot                          3  in sînem hûse und
     er wolte rîten                4  pflag sîner kinder
  5  vür den walt sô grüene        5  mit grôzer zuht ...
                                   
  Strophe 2                        
  6  Diu vrouwe sprach             
     mit zühten gar                
```

### Navigation Enhancement

Page breaks (`<pb>`) and song/chapter divisions become **jump targets** in the existing navigation sidebar. This connects to the already-built "jump to next occurrence" feature.

## Implementation Plan

### Phase 1: Structural HTML (JS)

File: `assets/js/rendering/tei-text-reader.js`

1. Extend `extractAndFormatBody()` switch cases:
   - `<div>`: emit `data-type` and `data-n` attributes, add type-specific CSS class
   - `<lg>`: emit stanza number label
   - `<l>`: emit `data-n` for line numbering
   - `<lb>`: emit `data-n` for prose line numbering
   - `<pb>`: emit as landmark element (not just inline badge)
   - `<note type="year|date">`: emit as inline badge
2. Add `verse-context` vs. `prose-context` class to reading body based on whether the text contains `<lg>` elements

### Phase 2: CSS Styling

File: `assets/css/korpus.css`

1. Margin line numbers (CSS counters or `::before` on `data-n`)
2. Stanza blocks with spacing and optional number
3. `<div>` type headers (song, chapter, recipe, etc.)
4. Page/column break markers
5. Prose vs. verse visual distinction (indentation, spacing)
6. `<hi rend>` variants (initial already works; add bold, italic, upper_case)
7. Note badges (year, date)

### Phase 3: Testing

1. Test with verse text (e.g. NIB — Nibelungenlied, stanzas + songs)
2. Test with prose text (e.g. ABG — Von der Abgeschiedenheit, paragraphs)
3. Test with recipe text (e.g. MBS5 — recipes + line breaks)
4. Test with mixed text (e.g. PZ — Parzival, chapters + verse)
5. Verify multi-lemma highlighting still works with new structure
6. Verify existing 121 Playwright tests still pass

## Corpus div/@type Inventory (for reference)

Current values (post-#32 cleanup, April 2026):

| Value | Count | Rendering |
|-------|-------|-----------|
| `chapter` | 1429 | "Kapitel N" header |
| `song` | 1373 | "Lied N" header |
| `recipe` | 520 | "Rezept N" header |
| `number` | 498 | "Nr. N" header |
| `section` | 451 | Subtle separator |
| `colophon` | 15 | Distinguished block |
| `parallel` | 13 | "Parallelüberlieferung" label |

## Out of Scope

- User-configurable font size / line height (future UX enhancement)
- Collapsible sections (future)
- TEI header rendering in reading view (separate feature)
- Folio image linking (requires digitization data)
- Critical apparatus display

## Depends On

- Nothing (unblocked since #32 completion)

## Blocks

- Public launch readiness (Katharina's prerequisite)

## Files to Touch

- `assets/js/rendering/tei-text-reader.js` — HTML generation
- `assets/css/korpus.css` — structural styling
- Possibly `assets/js/app.js` — if navigation jump targets change
