# Issue #52: Playground — Authority Files Card

## Context

The "Authority Files" overview card in the playground left sidebar is too dominant and confusing. Users see a card they can't click on. Katharina's feedback: "Karte nicht so dominant, die verwirrt. Weil anklicken kann man dzt. ja auch nichts. Vielleicht zum Ausklappen."

**Priority:** Quick win, effort:small.

## Current State

The left sidebar has two separate sections — the card and the buttons are NOT in the same container:

### 1. Authority Overview Card (`playground/index.html:181-197`)

```
#authorityOverview (rounded card, bg-slate-50)
├── #authorityToggle (button, toggles stats)
│   ├── "Authority Files" (h3)
│   ├── #authorityStatus + #statusText ("Lade...")
│   └── #authorityChevron (rotates on toggle, starts expanded)
└── #authorityStats (text-xs, stats populated by JS)
```

Small card. Contains only a title, loading indicator, and a collapsible stats section. No buttons. Starts **expanded** (chevron has `rotate-180`, stats div has no `hidden` class).

### 2. Query Interface Section (`playground/index.html:200-240`)

Separate `<section>` element below the authority card:

```
Query Interface (Schritt 2)
├── "Authority Files durchsuchen" (h3)
│   ├── #showAuthorsBtn     [disabled]
│   ├── #showWorksBtn       [disabled]
│   ├── #showLemmataBtn     [disabled]
│   ├── #showConceptsBtn    [disabled]
│   ├── #showGenresBtn      [disabled]
│   └── #showNamesBtn       [disabled]
└── "TEI Textanalyse" (#teiQueries, display:none)
    ├── #findMultiLemmaBtn
    ├── #showWordsBtn
    ├── #showLinesBtn
    └── #showAnnotationsBtn
```

The 6 disabled authority buttons live here, together with 4 TEI analysis buttons. Buttons enable once data loads.

### The Actual Problem

The authority card (`#authorityOverview`) shows stats that are not actionable — the user sees numbers but can't do anything with them from the card. The Query Interface section below has the actual buttons, but they start disabled. The card takes visual attention without offering interaction.

## Design

### Option A: Collapse authority card by default (recommended)

The stats aren't needed until the user wants them. Start collapsed, expand on click.

```
Before (current):                After:
┌─────────────────────┐         Authority Files ▸  (collapsed, one line)
│ Authority Files     │
│ Stats: 43750 Lemmata│         ← Click to expand:
│ ...                 │         ┌─────────────────────┐
└─────────────────────┘         │ 43750 Lemmata       │
┌─────────────────────┐         │ 210 Personen  ...   │
│ Query Interface     │         └─────────────────────┘
│ [btn] [btn] [btn]   │         ┌─────────────────────┐
│ [btn] [btn] [btn]   │         │ Query Interface     │
└─────────────────────┘         │ [btn] [btn] ...     │
                                └─────────────────────┘
```

### Option B: Remove authority card entirely

Move loaded-count badge into the Query Interface header ("Authority Files durchsuchen (7 geladen)"). Delete the card. Stats available elsewhere (browser console, API).

**Recommendation: Option A** — minimal change, uses existing toggle. The stats have value for researchers who want a quick corpus overview.

## Implementation

### HTML (`playground/index.html`)

1. Add `hidden` class to `#authorityStats` (line 196) — starts collapsed
2. Remove `rotate-180` from `#authorityChevron` (line 193) — chevron points down when collapsed (click to expand), up when expanded
3. Optionally reduce card padding (`p-4` → `p-3`) for a lighter footprint

### JS (`playground/js/playground-main.js` or `ui/`)

1. Toggle logic already works — no JS changes needed for Option A
2. Optional: update `#statusText` to show count ("7 geladen") after load completes, so the collapsed card still conveys status

### CSS

No CSS changes needed. Existing Tailwind utilities handle the collapsed/expanded states.

## Files to Touch

- `playground/index.html` — 2 attribute changes (add `hidden`, remove `rotate-180`)
- Optionally `playground/js/playground-main.js` — status text update after load

## Testing

1. Load playground — authority card should be collapsed (one line, chevron right)
2. Click to expand — stats appear, chevron rotates down
3. Query Interface section below is unaffected — buttons still enable on data load
4. Verify all 6 authority explorers still launch correctly from buttons
5. `npm test` — no regressions

## Out of Scope

- Redesigning the Query Interface section
- Adding new authority file types
- Making the sidebar responsive/mobile
