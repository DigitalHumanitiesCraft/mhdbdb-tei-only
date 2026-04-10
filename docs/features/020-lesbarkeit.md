# Issue #20: Lesbarkeit (Readability Fixes)

## Context

Katharina flagged readability problems on the main site: important information (result counts, statistics) is rendered in light grey with small font sizes, making it hard to scan results. The fixes are CSS-only — code is ready, awaiting approval.

**Priority:** Quick win, effort:small.

## Current State

### Result Count Display

- HTML: `<span id="resultsCount" class="text-brand-600">` inside `<h2>Suchergebnisse</h2>` (`korpus.html:192`)
- JS: populated as `(${N} Texte gefunden)` (`app.js:559-561`)
- CSS: color is already `text-brand-600` via Tailwind class, but **no dedicated font-size or font-weight rule** — inherits size from parent `<h2>`
- Per-result match badges: inline Tailwind in `app.js:626` — `bg-brand-100 text-brand-700 text-xs font-semibold rounded-full`

### Design Tokens

`assets/css/shared.css` defines the typography scale and color system. Relevant tokens:
- Font sizes: `--text-sm` (0.875rem), `--text-base` (1rem), `--text-lg` (1.125rem)
- Colors: `--brand-700` (strong), `--slate-500` (muted), `--slate-600` (semi-muted)

### Problem Areas (from Katharina's screenshot)

1. **Total result count** — small, same weight as surrounding text, doesn't stand out despite brand color
2. **Per-result match numbers** — badge exists but small
3. **General contrast** — important numbers should stand out more

## Changes

### 1. Result Count

Make the total result count more prominent. Color is already brand via Tailwind (`text-brand-600`). The span sits inside an `<h2 class="text-2xl">` (= 1.5rem), so it inherits that size. The fix is font-weight only — size is already fine from the parent:

```css
/* Before: inherits h2 size (1.5rem) but no weight differentiation */
/* After: semibold to stand out from the heading text */
#resultsCount {
    font-weight: 600;              /* semibold — distinguishes count from heading */
}
```

If the count should be visually smaller than the heading (e.g. subtitle style), extract it outside the `<h2>` first, then size independently. Don't set `font-size` on a child of `text-2xl` without checking inherited size (1.5rem).

### 2. Per-Result Match Badges

Badge already has `font-semibold`. Only change: increase size from `text-xs` to `text-sm`:

```
/* Tailwind classes in app.js:626 */
/* Before: text-xs font-semibold */
/* After:  text-sm font-semibold */
```

### 3. Statistics and Metadata

Any `text-slate-400` or `text-slate-500` used for important information should shift to `text-slate-600` or `text-slate-700` minimum.

## Files to Touch

- `assets/css/korpus.css` — result count rule, badge sizing
- `assets/js/app.js` — adjust Tailwind classes on match badges (line 626)
- Possibly `assets/css/shared.css` — if new design tokens needed

## Testing

1. Search for a common lemma (e.g. "minne") — verify result count is visually prominent
2. Check contrast ratio meets WCAG AA (4.5:1 for normal text)
3. Verify badge sizes are readable without being visually dominant
4. Run `npm test` — no functional changes, but verify no regressions

## Out of Scope

- Font size toggle / accessibility settings (future)
- Dark mode
- Mobile responsiveness (desktop-only project)

## Status

Code changes prepared, awaiting Christian's/Katharina's visual approval before merge.
