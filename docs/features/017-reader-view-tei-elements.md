# Issue #17: Reader View — TEI Structural Elements

## Context

The reading view (`tei-text-reader.js`) renders full-text TEI with multi-lemma highlighting and Wikidata metadata. But structural elements are rendered minimally: users cannot visually distinguish stanzas from paragraphs, verse lines from prose line breaks, or navigate by page/column boundaries.

Katharina's core requirement: users must **see and understand the editorial structure** of the text, not just the words. Prerequisite before going public.

**Priority:** prio-1, unblocked by #32 completion.

## Data Source: Raw TEI XML, NOT the Index

The reader view fetches the **raw TEI XML** file via `loadTEIFile()` → `DOMParser` (line 121–141 in `tei-text-reader.js`). `extractAndFormatBody()` walks the DOM tree directly. **No corpus index rebuild is needed for this feature.** The index is only used for filename lookup and metadata fallback.

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
| `<hi rend>` | Only `initial` + `upper_case_first_letter` handled | **~43k compound values unstyled** (see below) |
| `<caesura>` | `<span class="caesura">\|\|</span>` | Adequate |
| `<supplied>` | `<span class="supplied" title="...">[content]</span>` | Adequate |
| `<num>` | `<span class="number">` | Adequate |
| `<note>` | (no case — falls through to default) | No year/date badge rendering |

CSS lives in `assets/css/korpus.css` (lines 352–446). Reading body uses Georgia serif, 1.125rem, line-height 1.8.

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
| `<div type="parallel">` | "Parallelüberlieferung" label |
| `<lg type="stanza" n>` | Stanza block with number in margin |
| `<l n>` | Verse number in margin (line 1 + every 5th: 1, 5, 10, 15...) |
| `<lb n>` | Line number in margin (prose) |
| `<pb n>` | Page marker in margin or inline badge |
| `<cb n>` | Column marker |
| `<head>` | Section heading (already works) |

### Must-Have: Attribute Display

| Attribute | Where | Rendering |
|-----------|-------|-----------|
| `@type` on `<div>` | Section headers | Label (e.g. "Lied 3", "Kapitel 12", "Rezept 45") |
| `@n` on structural elements | Margins | Number display |
| `@rend` on `<hi>` | Inline | `initial`, `upper_case`, `upper_case_first_letter`, `bold`, `italic` |
| `@type="year"` on `<note>` | Inline | Year badge (e.g. "1292") |
| `@type="date"` on `<note>` | Inline | Date badge (e.g. "24. Februar") |

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
                                   
  Strophe 1                        h_1  Daz was ein ritter
  1  Dô sprach der ritter          h_2  der hete lange gesezzen
     guot                          h_3  in sînem hûse und
     er wolte rîten                h_4  pflag sîner kinder
                                   h_5  mit grôzer zuht ...
  Strophe 2                        
  1  Diu vrouwe sprach             
     mit zühten gar                
```

### Navigation Enhancement

Page breaks (`<pb>`) and song/chapter divisions become **jump targets** in the existing navigation sidebar. This connects to the already-built "jump to next occurrence" feature.

## Implementation Plan

### Phase 1: Structural HTML (JS)

File: `assets/js/rendering/tei-text-reader.js`

1. Extend `extractAndFormatBody()` switch cases:
   - `<div>`: emit `data-type` and `data-n` attributes, add type-specific CSS class, generate German label header (see label map below)
   - `<lg>`: emit stanza number label via `data-n`
   - `<l>`: emit `data-n` for line numbering
   - `<lb>`: emit `data-n` for prose line numbering (note: some `@n` values have prefixes like `h_1` — display as-is)
   - `<pb>`: emit as landmark element (not just inline badge)
   - `<note type="year|date">`: emit as inline badge with `@n` content
2. **Fix `processHi()` compound `@rend` handling** — see critical section below
3. Add `verse-context` vs. `prose-context` class to reading body based on whether the text contains `<lg>` elements

#### div/@type Label Map

```javascript
const divLabels = {
    'song':     'Lied',
    'chapter':  'Kapitel',
    'recipe':   'Rezept',
    'number':   'Nr.',
    'section':  'Abschnitt',
    'colophon': 'Kolophon',
    'parallel': 'Parallelüberlieferung'
};
```

### Phase 2: CSS Styling

File: `assets/css/korpus.css`

1. Margin line numbers (`::before` pseudo-elements on `data-n`)
2. Stanza blocks with spacing and optional number
3. `<div>` type headers (song, chapter, recipe, etc.)
4. Page/column break markers
5. Prose vs. verse visual distinction (indentation, spacing)
6. `<hi rend>` variants (see CSS classes below)
7. Note badges (year, date)

### Phase 3: Testing

1. Test with verse text: **NBB** (Nibelungenlied, 2376 Strophen × 4 Verse, per-stanza numbering)
2. Test with prose text: **ABG** (Von der Abgeschiedenheit, `<lb>` with `h_` prefix, `<pb>` page breaks)
3. Test with recipe text: **MBS5** (Rezepte, `div type="recipe"`, `<lb>` with clean numbers)
4. Test with mixed text: **FR1** (Lyrik von Frauenlob, 13 Songs, `div type="song"` + `lg type="stanza"`, variable stanza length up to 40 Verse)
5. Test with date badges: **HZU** (277× `note type="date"`, 119× `note type="year"`)
6. Test with colophon: **ALX** (Alexanderroman, `div type="colophon"`)
7. Test with column breaks: **CLV** (`<cb n>` with `type="manuscript"`; auch in EHB, GWTK)
8. Verify multi-lemma highlighting still works with new structure
9. Verify existing Playwright tests still pass (`npm test`)

## Critical: `<hi rend>` Compound Values

### Problem

The current `processHi()` (line 426) does `switch(rend)` on the full string. But TEI `@rend` is **space-separated** (like CSS classes). ~43k elements have compound values that fall through to unstyled default:

| rend value | Count | Currently handled? |
|------------|------:|:--:|
| `initial` | 277.896 | yes |
| `upper_case_first_letter` | 56.846 | yes |
| `initial upper_case_first_letter` | 35.496 | **NO** |
| `upper_case` | 7.075 | **NO** |
| `upper_case initial` | 771 | **NO** |
| `initial upper_case` | 220 | **NO** |
| `bold` | 141 | **NO** |
| `bold initial` | 56 | **NO** |
| `upper_case italic bold initial` | 38 | **NO** |
| `italic bold` | 38 | **NO** |
| `italic bold upper_case_first_letter` | 38 | **NO** |
| `italic` | 9 | **NO** |
| + 8 weitere Compound-Varianten | ~110 | **NO** |

### Solution

Replace `switch(rend)` with token-based class assignment:

```javascript
// Highlighting args (lemmaId, lemmaIds, lemmaColorMap, highlights, state)
// unchanged — pass through to processChildren as before
processHi(el, rend, lemmaId, lemmaIds, lemmaColorMap, highlights, state) {
    const content = this.processChildren(el, lemmaId, lemmaIds, lemmaColorMap, highlights, state);
    if (!rend) return `<span class="hi">${content}</span>`;

    const tokens = rend.split(/\s+/);
    const classes = tokens.map(t => `hi-${t}`).join(' ');
    return `<span class="hi ${classes}">${content}</span>`;
}
```

CSS classes:

```css
.hi-initial              { font-weight: 700; font-size: 1.5em; color: var(--accent-primary); }
.hi-upper_case_first_letter { text-transform: capitalize; }
.hi-upper_case           { text-transform: uppercase; }
.hi-bold                 { font-weight: 700; }
.hi-italic               { font-style: italic; }
```

Compound values then just stack: `<span class="hi hi-initial hi-upper_case_first_letter">` gets both rules.

**CSS-Migration:** Die bestehenden Selektoren `.reading-body .initial` (korpus.css:405) und `.reading-body .upper-case-first` (korpus.css:411) werden durch die neuen `.hi-*` Klassen ersetzt. Die alten Regeln müssen entfernt werden, da die HTML-Ausgabe nicht mehr `class="initial"` sondern `class="hi hi-initial"` erzeugt.

## Corpus Element Inventory (verified 2026-04-16)

### div/@type

| Value | Count | Rendering | Label |
|-------|------:|-----------|-------|
| `chapter` | 1.429 | Section header | "Kapitel N" |
| `song` | 1.379 | Section header | "Lied N" |
| `recipe` | 520 | Section header | "Rezept N" |
| `number` | 498 | Section header | "Nr. N" |
| `section` | 479 | Subtle separator | "Abschnitt N" |
| `colophon` | 15 | Distinguished block | "Kolophon" |
| `parallel` | 13 | Labelled container | "Parallelüberlieferung" |

15 Texte haben Kolophone: ALX APO ATF AXW CEFB CLV FAN NAR PRJ PTS SPH TKR TUN VUA WGM.

### lg/@type

| Value | Count |
|-------|------:|
| `stanza` | 30.084 |

Einziger Typ. 78 Texte enthalten `<lg>`.

### Zeilenzählung

- **`<l n>`** (Vers): Per-Strophe-Neustart (NBB: immer 1–4; FR1: variabel, bis 40 pro Strophe). Anzeige: Zeile 1 + jede 5. danach (1, 5, 10, 15, 20...) — Katharina bestätigt: "1, 5, 10, 15... passt".
- **`<lb n>`** (Prosa): 64 Texte. Zwei Formate:
  - Reine Zahlen: `n="1"`, `n="2"` — 140k+ Elemente, dominantes Format
  - Manuskript-Präfix: `n="h_1"`, `n="h_2"` — 1.584 Elemente, verteilt auf 43 Texte (spärlich: z.B. ABG 5/339, CLV 14/819) — as-is anzeigen

### Seitenumbrüche

- **`<pb n>`**: 46 Texte. Pattern: `<pb n="400"/>` (Seitenzahl aus der Edition).
- **`<cb n>`**: 3 Texte (CLV, EHB, GWTK). Pattern: `<cb n="1" type="manuscript"/>` (Manuskript-Spalte).

### note/@type (Body-relevant)

| Type | Count | Texte | Rendering |
|------|------:|-------|-----------|
| `date` | 277 | HZU, HZU2 | Badge: Inhalt aus `@n` (z.B. "24. Februar") |
| `year` | 119 | HZU, HZU2 | Badge: Jahreszahl aus `@n` (z.B. "1292") |

`works` (670), `provenance` (125), `fidelity` (125) stehen im `<teiHeader>`, nicht im `<body>` — nicht relevant.

### hi/@rend (vollständig)

| rend (Einzeltoken oder Compound) | Count |
|----------------------------------|------:|
| `initial` (allein) | 277.896 |
| `upper_case_first_letter` (allein) | 56.846 |
| `initial upper_case_first_letter` | 35.496 |
| `upper_case` (allein) | 7.075 |
| `upper_case initial` | 771 |
| `initial upper_case` | 220 |
| `bold` (allein) | 141 |
| `bold initial` | 56 |
| `upper_case initial upper_case_first_letter` | 45 |
| `upper_case italic bold initial` | 38 |
| `italic bold` | 38 |
| `italic bold upper_case_first_letter` | 38 |
| `upper_case upper_case_first_letter` | 31 |
| `bold upper_case_first_letter` | 26 |
| `italic` (allein) | 9 |
| `initial upper_case upper_case_first_letter` | 3 |
| `initial bold upper_case_first_letter` | 2 |
| `upper_case bold` | 1 |
| `initial italic` | 1 |
| `bold initial upper_case_first_letter` | 1 |

**5 Einzeltokens:** `initial`, `upper_case_first_letter`, `upper_case`, `bold`, `italic`.
**15 Compounds** aus diesen 5 Tokens. Token-basierte CSS-Klassen decken alles ab.

## Out of Scope

- User-configurable font size / line height (future UX enhancement)
- Collapsible sections (future)
- TEI header rendering in reading view (separate feature)
- Folio image linking (requires digitization data)
- Critical apparatus display
- `note type="works|provenance|fidelity"` (teiHeader, not body)

## Depends On

- Nothing. Unblocked since #32 completion (2026-04-09/10). Further hardened through #32-followup (2026-04-14/15): the corpus is now strictly validated against a tightened `schema/mhdbdb.rnc`, so the switch-case in `extractAndFormatBody()` can rely on element shapes without defensive guards. Specifically:
  - `<p>` is no longer pathologically large (PL1/PL2/PL3 split at `<pb/>` milestones — per-page `<p>` elements now).
  - `<hi>` no longer nests recursively (flattened across 143 files).
  - `msIdentifier/@corresp` is mandatory — every text has a resolvable `works.xml#work_N` reference.
  - Editor-attribution (#83) is uniform across all 666 headers.

## Blocks

- Public launch readiness (Katharina's prerequisite)

## Files to Touch

- `assets/js/rendering/tei-text-reader.js` — HTML generation (switch cases + `processHi()` rewrite)
- `assets/css/korpus.css` — structural styling (margin numbers, div headers, hi variants, note badges)
- Possibly `assets/js/app.js` — if navigation jump targets change
