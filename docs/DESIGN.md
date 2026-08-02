# Design

Visual and interaction patterns for the MHDBDB TEI Repository. Complements [ARCHITECTURE.md](ARCHITECTURE.md) (technical) and [FEATURES.md](FEATURES.md) (user-facing). This document is the reference when building new UI components.

## Color System

### Brand Palette (tailwind.config.js)

| Token | Hex | Usage |
|-------|-----|-------|
| `brand-50` | `#f1f5fd` | Hero gradient, welcome-state backgrounds |
| `brand-100` | `#e2ebfa` | Badge backgrounds, PoS badge bg, result hover border |
| `brand-200` | `#c0d3f4` | Focus rings, input hover border |
| `brand-500` | `#3b75d8` | Primary accent (`--accent-primary`), spinner, progress bar |
| `brand-600` | `#265cc4` | Primary buttons, links, nav logo text |
| `brand-700` | `#1f4aa2` | Hover state on brand-600 elements |

### Semantic Tokens (shared.css `:root`)

| Purpose | Variable | Value |
|---------|----------|-------|
| Background primary | `--bg-primary` | `#fff` |
| Background secondary | `--bg-secondary` | `#f8fafc` |
| Text primary | `--text-primary` | `#1f2937` |
| Text secondary | `--text-secondary` | `#64748b` |
| Border primary | `--border-primary` | `#e2e8f0` |
| Accent primary | `--accent-primary` | `#3b75d8` |

### Status Colors (Tailwind utilities, no CSS vars)

| Status | Background | Border | Text |
|--------|-----------|--------|------|
| Info | `bg-blue-50` | `border-blue-200` | `text-blue-800` |
| Warning | `bg-yellow-50` | `border-yellow-200` | `text-yellow-800` |
| Error | `bg-red-50` | `border-red-200` | `text-red-700` |
| Success | `bg-green-50` | `border-green-200` | `text-green-700` |

### Multi-Lemma Highlight Palette

**Authoritative source: `tei-text-reader.js` constructor (lines 24-31)**

These colors are used by the reading view for multi-lemma highlighting:

| Slot | Background | Border | Text | Name |
|------|-----------|--------|------|------|
| 1 | `#fecaca` | `#ef4444` | `#991b1b` | Red |
| 2 | `#bfdbfe` | `#3b82f6` | `#1e3a8a` | Blue |
| 3 | `#bbf7d0` | `#22c55e` | `#166534` | Green |
| 4 | `#fde68a` | `#f59e0b` | `#92400e` | Yellow |
| 5 | `#ddd6fe` | `#8b5cf6` | `#5b21b6` | Purple |

**Color assignment:** `colors[idx % 5]` – sequential, wraps after 5 lemmas.

**Also defined in:**
- `korpus.css` (Z. 637-691) – `.multi-lemma-{lemmaId}` classes, hardcoded per lemma ID (879=red, 7532=green, 1816=blue, 26713=pink, 712=orange) plus a `[class*="multi-lemma-"]` purple fallback
- `playground/css/style.css` – duplicate of the korpus.css `.multi-lemma-*` block (verbatim)
- `ui-helpers.js` `LEMMA_COLORS` – playground proximity search

**Note:** The CSS `.multi-lemma-*` classes are lemma-ID-keyed (not index-keyed like the JS `colors[idx % 5]` palette) and are applied to playground proximity result cards. The reading view does not use them – it applies the JS inline styles from `tei-text-reader.js`.

Single `<mark>` highlight (single-lemma mode): `#fbbf24` bg / `#78350f` text.

Page background: `bg-slate-100` (`#f1f5f9`) on all pages.

## Typography

### Font Stack

- **UI**: System stack (Tailwind default) – `ui-sans-serif, system-ui, sans-serif`
- **Reading body**: `Georgia, 'Times New Roman', serif` at `1.125rem / 1.8` line-height (`.reading-body` in `korpus.css`)
- No web fonts loaded

### Scale and Weight

| Class | Size | Typical usage |
|-------|------|---------------|
| `text-xs` | 0.75rem | Badges, metadata labels, timestamps |
| `text-sm` | 0.875rem | Body copy, nav links, form labels |
| `text-base` | 1rem | Default body, button text |
| `text-lg` | 1.125rem | Reading body text |
| `text-xl` | 1.25rem | Card section titles |
| `text-2xl` | 1.5rem | Page section headers |
| `text-3xl` | 1.875rem | Landing page headers |
| `text-4xl` | 2.25rem | Stat numbers |

| Weight | Usage |
|--------|-------|
| `font-medium` (500) | Nav links, body emphasis |
| `font-semibold` (600) | Card titles, form labels, buttons |
| `font-bold` (700) | Page headings, stat labels |

### Eyebrow Label Pattern

Recurring pattern for section sub-labels:
```
text-sm font-semibold uppercase tracking-wider text-slate-500
```

## Icon System

**Style**: Inline Heroicons outline SVGs. No icon font, no CDN, no emoji.

**Pattern**: `fill="none" stroke="currentColor" viewBox="0 0 24 24"` with `stroke-linecap="round" stroke-linejoin="round" stroke-width="2"`.

| Size class | Pixels | Usage |
|-----------|--------|-------|
| `w-3 h-3` | 12px | Dense stat grids, small decorative |
| `w-4 h-4` | 16px | In-text icons, form prefix, inline buttons (most common) |
| `w-5 h-5` | 20px | Modal icons, info panel icons |
| `w-6 h-6` | 24px | Hamburger menu, modal close |

All icons inherit color via `currentColor`.

**Reference**: `assets/js/app.js:213-226` (document-text, book-open examples).

**Exception**: Filled mini-icons in playground corpus stats use `viewBox="0 0 20 20"` with `fill="currentColor"` at `w-3 h-3`.

## Component Patterns

### Cards

| Type | Classes | Used in |
|------|---------|---------|
| Panel | `rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-sm ring-1 ring-slate-100/40` | Playground columns |
| Content card | `bg-slate-50 rounded-2xl p-8 border border-slate-200` | Landing page info |
| Stat card | `bg-white rounded-2xl p-8 text-center border border-slate-200 shadow-sm` | Corpus overview |
| Result card | `bg-white border border-slate-200 rounded-2xl p-6 hover:border-brand-300 hover:shadow-md transition-all cursor-pointer` | Search results |
| Section card | `bg-white rounded-lg shadow-sm border border-slate-200 p-6` | Lemma page sections |
| Empty state | `rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500` | Anywhere |

### Buttons

| Type | Pattern |
|------|---------|
| Primary | `btn-primary`: `px-5 py-3 text-sm font-semibold rounded-lg bg-accent-primary text-white` + hover translateY(-1px) |
| Secondary | `btn-secondary`: same shape, `bg-secondary text-primary border-primary` |
| Small action | `rounded-lg bg-brand-600 px-3 py-1 text-xs font-semibold text-white hover:bg-brand-700` |
| Icon-only | `icon-btn`: `p-1 px-2 rounded-sm bg-secondary border-primary min-w-[2rem]` |
| Text-only | `text-xs font-medium text-brand-600 hover:text-brand-700 transition` |
| Floating (reading view) | `.back-to-top` in `korpus.css`: round 2.75rem button, `position: fixed; right: var(--space-8); bottom: 5.5rem`, `#334155` on white, same shadow as `.reading-nav`. `z-index: 21` deliberately sits one step above the highlight navigation (`z-20`) so the two do not overlap while highlighting is active. Visible only once a text is loaded and the panel header has scrolled out of the viewport (#138) |

### Badges / Pills

| Type | Pattern |
|------|---------|
| Match count | `bg-brand-100 text-brand-700 text-xs font-semibold px-3 py-1 rounded-full` |
| Genre tag | `bg-slate-100 text-slate-700 text-xs px-3 py-1 rounded-full` |
| PoS badge | `bg-brand-100 text-brand-700 text-xs font-semibold uppercase tracking-wide px-[10px] py-[2px] rounded-full` |
| Info badge | `bg-blue-100 text-blue-800 text-sm font-medium rounded-full px-3 py-1` |

### Form Inputs

Standard: `rounded-xl border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:border-brand-500`

Filter with icon: `pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg` + absolute-positioned magnifier SVG.

Checkbox accent: `accent-color: #3b75d8`.

## Playground TEI-Analysis Module Pattern

Eleven analysis modules under `playground/js/ui/tei/` share a consistent structure (the router `tei-ui.js` and the modal controller `multi-lemma-search.js` do not follow the pattern). Anyone adding a new analysis tool should follow it: modules that deviate for no visible reason make the playground feel inconsistent and break conventions the router and the sidebar buttons build on.

**Canonical examples:** `lemma-distribution.js` (#90), `verse-position-search.js` (#47.3), `concept-distribution.js` (#47 R2 + #113 autocomplete), `text-comparison.js` (#108), `cooccurrence-ranking.js` (#107), `rhyme-dictionary.js` (#106), `naming-explorer.js` (#59, deviation: its own lazily fetched index `data/naming-index.json.gz` instead of a corpus thunk).

### Constructor: thunks instead of direct references

```js
constructor(getCorpusTexts, authorityManager, getAuthorityData) {
  this.getCorpusTexts = getCorpusTexts;
  this.authorityManager = authorityManager;
  this.getAuthorityData = getAuthorityData;
  this.state = { ...DEFAULT_STATE };
}
```

`getCorpusTexts`/`getAuthorityData` are passed as functions, not as ready-made arrays. Reason: after an index reload (bump v4.1.1 → v4.2.0, cache invalidation) direct array references point at stale data. Thunks pull the current array from `teiManager` every time. Lesson from #97-#100 (corpus index property drift).

### State – Frozen Defaults + Stateful Instance

```js
const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedConcept: null,
  matchingLemmata: [],
  distribution: null,        // null bis async-compute abgeschlossen
  computing: false,          // true waehrend Long-Running-Aggregation
  computeProgress: 0,        // 0..1 fuer Spinner
  sortBy: 'frequency',
  freqMode: 'absolute',
  topN: 30
});
```

`Object.freeze` prevents accidental mutation of the default; `this.state = { ...DEFAULT_STATE }` creates a fresh mutable object per instance. On reset (e.g. after a corpus switch): `this.state = { ...DEFAULT_STATE }`.

### Lifecycle – `show()` ➝ `render()` ➝ `renderForm() + renderBody()` ➝ `attachHandlers()`

```js
show() {
  const texts = this.getCorpusTexts();
  if (!texts || texts.length === 0) {
    this.renderError('Korpus ist noch nicht geladen.');
    return;
  }
  this.render();
}

render() {
  document.getElementById('resultsContainer').innerHTML = `
    <div class="space-y-4">
      ${this.renderForm()}
      ${this.renderBody()}
    </div>
  `;
  this.attachHandlers();
}
```

- `show()` is the router entry point, with a guard for "corpus not loaded yet".
- `render()` assigns `innerHTML = ...` **once** and calls `attachHandlers()` afterwards. No DOM diffing: every render is throwaway. The form keeps focus because `attachHandlers()` can call `refocusInput()` after `innerHTML`.
- `renderForm()` / `renderBody()` return strings, they never mutate the DOM directly. Keep it template-driven.

### State-Driven Body

`renderBody()` is a branch over `this.state`:

```js
renderBody() {
  if (!this.state.query) return /* "Bitte Suchen" Empty-State */;
  if (!this.state.resolvedConcept) return /* "Kein Begriff gefunden" Amber-Box */;
  if (this.state.matchingLemmata.length === 0) return /* "Keine Lemmata zugeordnet" */;
  if (this.state.computing) return /* Spinner + Progress-Bar */;
  if (!this.state.distribution) return /* Fallback "..." */;
  return /* Chart + Tabelle */;
}
```

Order matters: empty state → error state → no match → computing → result. Reorder it and the user is told „Keine Lemmata zugeordnet" while the search is in fact still running.

### Async + chunking (for O(L × T) aggregations)

For modules whose aggregation can block the main thread for more than ~50ms (critical from ~2000 items on), chunk with a time-based yield:

```js
const CHUNK_BUDGET_MS = 30;

function yieldToMain() {
  // MessageChannel statt setTimeout(0): hat keinen 4ms-Mindest-Delay und wird
  // im hidden Tab NICHT auf 1000ms gedrosselt (siehe concept-distribution.js).
  return new Promise(resolve => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => resolve();
    ch.port2.postMessage(null);
  });
}

async computeDistribution(items, onProgress) {
  const out = [];
  let chunkStart = performance.now();
  for (let i = 0; i < items.length; i++) {
    /* ... arbeite ... */
    if (performance.now() - chunkStart > CHUNK_BUDGET_MS) {
      if (onProgress) onProgress((i + 1) / items.length);
      await yieldToMain();
      chunkStart = performance.now();
    }
  }
  return out;
}
```

Avoid `setTimeout(0)` as the yield: Chrome throttles it to >=1000ms in a background tab and makes tests unreliable. Avoid `requestIdleCallback`: no guarantee about the share of frame time it gets. MessageChannel is the robust choice.

### Escape helpers: per module, not imported

Every module ends with:

```js
function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
function escapeAttr(s) { return escapeHtml(s); }
```

Self-contained instead of a central `lib/escape.js` import: a module can be copied or moved without adjusting paths, and the five lines are written faster than the import line.

### Brand accent: default button only

| Use | Classes |
|-----|---------|
| Default action („Suchen", „Anwenden") | `rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100` |
| Secondary (cancel, reset) | `bg-white border-slate-200 hover:border-slate-400` |
| Result heading | `text-lg font-semibold text-brand-700` |
| Bar chart bars | `fill-brand-400 hover:fill-brand-600 transition` |

The brand color is the accent, not the base color. Once a module has four brand-colored buttons, the default loses its accent status.

### Cross-Module Linking

Click on a hit → reading view. Pattern:

```js
const href = `../korpus.html?textId=${encodeURIComponent(h.id)}&lemmaIds=${encodeURIComponent(lemmaId)}`;
```

Do not hash-route: `korpus.html` is a separate site. Plain anchor tags with `target="_blank" rel="noopener"`, so the user does not lose the playground session.

### Multi-Lemma as a documented outlier

`playground/js/ui/tei/multi-lemma-search.js` uses a **modal instead of an in-place form** (`#multiLemmaModal`), because its four inputs (lemma list, mode, distance, corpus-selection checkbox) would not fit in the sidebar. This is the only permitted deviation: a new module with 1-3 inputs belongs on the in-place form path. Modals only for genuinely large input surfaces.

### Performance map against O(N) lookups (text-comparison lesson)

`AuthorityFilesManager.findLemmaById()` is an `Array.find()` over 43,879 lexicon entries (`authorityData.lemmata` from the authority index), so O(N) per call. As long as a module needs the lookup only dozens of times (concept-distribution, lemma-distribution: 30-50 hits for the top-N display) that does not matter. As soon as an `enrichment` iterates over *thousands* of lemmata, the iterations multiply:

```
text-comparison PZ vs JT, „Beide": 3,058 lookups × 43,754 ≈ 134 million iterations ≈ 5962ms
                                  ↓ (local map built once per show())
                                       1 lookup × 43,754 (build) + 3,058 × O(1) ≈ 53ms (112× faster)
        (43,754 = lexicon size at the time of this measurement; the lexicon grows, the order of magnitude stays)
```

Pattern:

```js
ensureLemmaMap() {
  if (this._lemmaMap) return;
  this._lemmaMap = new Map();
  for (const l of this.authorityManager?.authorityData?.lemmata || []) {
    if (l?.id) this._lemmaMap.set(l.id, l);
  }
}
// In show(): this.ensureLemmaMap();
// In enrich: const lemma = this._lemmaMap.get(lemmaId);
```

Rule of thumb: if a lookup runs in the inner loop over `>500 items`, build a local map. Do NOT modify `AuthorityFilesManager` itself: it still has older consumers whose behavior under an API change is unclear.

### Abort token against race conditions (cooccurrence-ranking lesson)

With async compute that the user can interrupt by re-submitting, switching PoS or switching lemma, the late first run otherwise writes its result after the early second one. State becomes inconsistent (the result flickers, jumps back, jumps forward again). Pattern:

```js
constructor() {
  this._abortToken = 0;
}

async runSearch() {
  this._abortToken += 1;
  const myToken = this._abortToken;
  // ...
  const result = await this.computeCooccurrences(/* ... */);
  if (this._abortToken !== myToken) return;  // anderer Lauf hat uns überholt
  this.state.result = result;
  this.render();
}

async computeCooccurrences(...) {
  const myToken = this._abortToken;
  for (let i = 0; i < texts.length; i++) {
    if (this._abortToken !== myToken) return null;
    // ... chunk ...
    await yieldToMain();
    if (this._abortToken !== myToken) return null;
  }
}
```

The token increment happens SYNCHRONOUSLY in `runSearch()`, before any `await`. That guarantees the second run invalidates the first *before* the first has had even one `yieldToMain()` cycle. The in-loop check after every yield catches it quickly.

### Navigation epoch against cross-view clobber (#159/#168)

The per-module token above only catches **same-view races** (a new search in the same module). If the user navigates to a **different view** while a scan is running, no module token is bumped: the finished result would overwrite the view now showing in `#resultsContainer`. Against that, the router (`playground/js/ui/core/router.js`) exports a global, monotonically increasing counter:

```js
import { getNavigationEpoch } from '../core/router.js';

async runSearch() {
  this._abortToken += 1;             // Same-View-Guard (wie oben)
  const myToken = this._abortToken;
  const myEpoch = getNavigationEpoch();  // Cross-View-Guard
  const result = await this.compute(/* ... */);
  if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return;
  this.state.result = result;
  this.render();
}
```

`dispatch()` increments the epoch on EVERY route change (`navigate()` as well as `hashchange`/back/forward), but only after the unknown-view check (an unknown route does not change the visible view). Both checks belong together in the same condition, including inside the chunk loops after every `yieldToMain()`, so a navigated-away scan aborts at once instead of burning CPU. The per-module `isActiveView()` hash comparison documented here earlier has been replaced by the epoch (one mechanism instead of two, and it also catches same-route re-dispatches with new params).

Implemented (as of 2026-07-07): `cooccurrence-ranking.js`, `rhyme-dictionary.js`, `concept-distribution.js` (there additionally `_searchGen` as a search-generation token, because the `computing` flag fails as an identity criterion: with two overlapping searches the older one won), `multi-lemma-search.js`, `naming-explorer.js` (first load). On the main site, `tei-text-reader.js openReadingView()` uses the same idea as a `_loadSeq` request guard (there is no router there).

### Live autocomplete dropdown (concept-distribution #113 lesson)

A classic DWDS/Google-style dropdown below lemma and concept inputs. Update the DOM directly instead of a full `render()` on every keystroke: otherwise the input loses focus and the selection range, and typing becomes unusable.

```js
DEFAULT_STATE = {
  // ...
  autocompleteOpen: false,
  autocompleteIndex: -1,        // -1 = keiner highlighted; 0..N-1 keyboard-aktiv
  autocompleteItems: []
};

// HTML: <input> mit <div class="absolute top-full ... hidden"> als Dropdown.

updateAutocomplete(query) {
  // Concept-Module: resolveQuery liefert candidates (substring+startsWith-scoring im Modul).
  // Lemma-Module: authorityManager.getLemmaAutocompleteMatches() — prefix-search auf
  // l.normalized (mhd-norm „ere" → matcht „êre") + length-Sort, weil resolveQuery
  // bei exact-match Stage-1-early-returnt und nur 1 Treffer liefert.
  this.state.autocompleteItems = this.authorityManager.getLemmaAutocompleteMatches(query, 8);
  this.state.autocompleteIndex = -1;  // Reset, sonst springt Enter unerwartet
  this.state.autocompleteOpen = this.state.autocompleteItems.length > 0;
  this.renderAutocomplete();  // direkt innerHTML, KEIN render()
}

// Keydown-Switch: ArrowDown/Up → index ±1, Enter mit idx>=0 → wähle aus Items,
// Enter mit idx===-1 → normale Submit-Resolution wie bisher (kompatibel), Escape → schliesse.

// Click-Handler: mousedown statt click, weil blur 150ms vor click feuert:
dd.addEventListener('mousedown', (e) => {
  const btn = e.target.closest('[data-cd-ac-idx]');
  if (!btn) return;
  e.preventDefault();
  // ... auswählen + runSearch()
});

// blur mit setTimeout-Delay schließt Dropdown — sonst feuert blur vor mousedown.
input.addEventListener('blur', () => setTimeout(() => this.closeAutocomplete(), 150));
```

ARIA: `role="combobox" + aria-controls + aria-expanded` on the input, `role="listbox"` on the dropdown, `role="option" + aria-selected` on the buttons. Scroll the active item into view on arrow navigation (`activeEl.scrollIntoView({block: 'nearest'})`). Reuse `resolveQuery()` as the suggestion source: no second resolver path.

The pattern is implemented (as of 2026-05-16) in four modules: `concept-distribution.js` (#113, the original), `lemma-distribution.js`, `verse-position-search.js`, `cooccurrence-ranking.js` (all three ported on 2026-05-16; since #106 also `rhyme-dictionary.js`). If further modules gain a lemma or concept input: copy it and adjust the ids (`xxQuery`/`xxAutocomplete`/`data-xx-ac-idx`).

**Passing the selection through (#163):** the dropdown selection must not only set `input.value` (a string): with homographs (three lemmata „rôt") `resolveQuery()` would resolve that string back to the wrong lemma. Rule: a selection (Enter on an active item, mousedown) additionally sets `this.state.selectedLemma = c` (or `selectedConcept`); the `input` handler resets it to `null` on manual typing; `runSearch()` prefers `selectedLemma` as long as the query text still matches the chosen form. Default resolution without an explicit selection: `searchLemmaByOrthography()` returns stage-1 homographs sorted by frequency (corpus frequency descending), so `matches[0]` is the most plausible lemma.

## Layout Patterns

### Container

`container mx-auto px-6` – constrained to `max-w-6xl` (landing) or `max-w-4xl` (lemma page).

### Column Grids

| Layout | Classes | Used in |
|--------|---------|---------|
| 2-column | `grid xl:grid-cols-[1fr_2fr]` | Korpus default |
| 3-column | `grid xl:grid-cols-[1fr_1fr_2fr]` | Playground, korpus post-search |
| Columns collapse at `max-width: 1279px` to single column.

### Section Rhythm (Landing Page)

`py-20` between sections, alternating `bg-white` / `bg-slate-50`.

### Sticky Header

`sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-slate-200` – identical across all pages.

## Loading and Error States

### Full-Page Loading Screen

`shared.css .loading-screen`: fixed overlay, white bg with `backdrop-filter: blur(6px)`, z-index 9999. Contains spinner (42px) + status text + progress bar (300px wide, `border-radius: 9999px`).

### Spinner

`.spinner`: 32px circle, `border: 3px`, top border colored `--accent-primary`, `animation: spin 0.9s linear`. Respects `prefers-reduced-motion`.

### Error Toast

`.error-display` in `korpus.css`: fixed bottom-right, max-width 400px, `bg-red-50 border-red-500`, auto-dismiss after 5s with `slideUp` animation.

### Empty/No-Results

`bg-yellow-50 border border-yellow-200 rounded-2xl p-8 text-center` with link to playground.

## Navigation

### Header (all pages)

Logo (`w-40` image + `text-lg font-bold text-brand-600`) left, nav links right (`hidden md:flex gap-6`). Mobile hamburger at `md:hidden`. Nav + header markup is build-injected from `includes/_nav.html` by `scripts/build-pages.py`; the active page's link gets `aria-current="page"` + `text-slate-900 font-semibold`. The mobile-menu toggle (open/close, click-outside, close-on-link) lives centrally in `assets/js/site-chrome.js` (`initMobileMenu`) – pages must NOT carry their own inline mobile-menu script.

### Footer

Institutional logos row + divider + copyright/clear-data row. `bg-slate-100 py-8`. Markup is build-injected from `includes/_footer.html`; the copyright year and the cross-browser clear-site-data button are wired in `assets/js/site-chrome.js` (`initCurrentYear`, `initClearSiteData` via delete-by-name), not per page or via `app.js`.

### Cross-Page Links

| From | To | Pattern |
|------|----|---------|
| Playground result | Korpus reading view | `window.open('../korpus.html?textId=…&lemmaIds=…')` |
| Lemma occurrence | Korpus reading view | `<a href="../korpus.html?textId=…&lemmaIds=…">` |
| Lemma etymology | Other lemma page | `<a href="{numericId}" class="etymology-link">` |
| Wörterbuch entry | Lemma page | `<a href="lemma/?id={numericId}">` |

### Hit navigation (reading view)

`.reading-nav` / `.reading-nav-btn` / `.reading-nav-indicator` in `korpus.css` (markup: `#readingNavigation` in `korpus.html`, logic: `tei-text-reader.js updateNavigationButtons()`): floating bar fixed bottom-right above the reading view. White/97 backdrop-blur container with `--border-secondary` border and strong shadow; dark buttons (slate-700, white text, hover slate-800) and a slate-900 semibold counter („Treffer x von y") at `--text-sm`; disabled buttons drop to opacity 0.4. Restyled 2026-07-10 after KZW feedback (previously text-xs, light-gray buttons – too small, too low-contrast).

## CSS Architecture

Three-layer stack (load order):

| Layer | File | Contains |
|-------|------|----------|
| 1 | `tailwind-output.css` | Utility classes (layout, typography, color, spacing, responsive) |
| 2 | `assets/css/shared.css` | Design tokens (CSS vars), spinner, buttons, loading screen, animations |
| 3 | Page-specific CSS | `korpus.css` or `playground/css/style.css` or inline `<style>` (lemma) |

**Rule**: Semantic tokens in CSS vars. Layout and one-off styling in Tailwind utilities. Page-specific components in dedicated CSS. JS-generated HTML uses Tailwind classes in template literals.

**Gotcha**: `tailwind-output.css` is pre-compiled and committed – a utility class that isn't already in the compiled file silently does nothing until `npm run build:css` is run. When Node/npm is unavailable on the working machine, style new components in the page-specific CSS layer instead (precedent: KWIC styles #129, `.reading-nav` 2026-07-10).

### Animations (shared.css)

| Name | Effect | Used for |
|------|--------|----------|
| `fadeIn` | opacity 0 to 1 | General reveal |
| `slideUp` | translate + scale + opacity | Modals, error toast |
| `slideDown` | translate + opacity | Proximity controls |
| `spin` | 360deg rotation | Spinner |
| `chipIn` | scale + opacity | Lemma chip entry (in playground style.css) |

## TEI Reading View CSS Classes

Source: `assets/css/korpus.css` (post-#17 reader-view styling). Element-to-class mapping in [ARCHITECTURE.md §TEI Element Rendering Map](ARCHITECTURE.md#tei-element-rendering-map).

| Class | Key Styling | TEI Element |
|-------|------------|-------------|
| `.reading-body` | `Georgia, serif; 1.125rem; line-height: 1.8` | Container |
| `.section-head` | `sans-serif; 1.25rem; font-weight: 600; color: accent` | `<head>` |
| `.tei-div`, `.tei-div-{type}` | `margin: space-4 0`; per-type variants for song / chapter / recipe / number / section / colophon / parallel | `<div>` |
| `.tei-div-header`, `.tei-div-header.tei-div-{type}` | German label + counter (e.g. „Lied 3", „Kapitel 12") | first child of `<div>` |
| `.verse-group` | `margin: space-4 0` | `<lg>` |
| `.stanza-label` | inline „Strophe N" prefix | first child of `<lg>` |
| `.verse-line` | `display: block; margin-left: space-4; line-height: 1.6`; verse number in margin via `data-n` (1, 5, 10, …) | `<l>` |
| `.line-break` | `display: inline` | `<lb>` |
| `.lb-number` | small superscript-style line counter for prose (numeric `@n` only) | follows `<lb>` |
| `.lb-anchor` | unstyled empty span for non-numeric `<lb>`-`@n` (e.g. `h_1`) – deep-link target only, never visible (#158) | follows `<lb>` |
| `.page-break` | `inline-block; 0.875rem; font-weight: 600; bg-tertiary; cursor: help` | `<pb>` |
| `.column-break` | `inline-block; 0.875rem; font-weight: 600; bg-tertiary; cursor: help` | `<cb>` |
| `.note-badge`, `.note-year`, `.note-date` | inline year/date marker rendered from `<note>@n` | `<note type="year\|date">` |
| `.hi` | base class for any `<hi>` (no `@rend` or unmatched token) | `<hi>` |
| `.hi-initial` | `font-weight: 700; font-size: 1.5em; color: accent` | `<hi rend="initial …">` |
| `.hi-upper_case_first_letter` | `text-transform: capitalize` | `<hi rend="… upper_case_first_letter …">` |
| `.hi-upper_case` | `text-transform: uppercase` | `<hi rend="… upper_case …">` |
| `.hi-bold` | `font-weight: 700` | `<hi rend="… bold …">` |
| `.hi-italic` | `font-style: italic` | `<hi rend="… italic …">` |
| `.punctuation` | `font-weight: normal` | `<pc>` |
| `.caesura` | `color: muted; font-weight: 300; margin: 0 space-1` | `<caesura>` |
| `.supplied` | `color: #6b7280; italic; border-bottom: 1px dotted` | `<supplied>` |
| `.number` | `font-variant-numeric: oldstyle-nums` | `<num>` |
| `mark.highlight` | `bg: #fbbf24; color: #78350f; font-weight: 600; scroll-margin-top: 120px` | `<w>` match (single) |
| `mark.highlight.multi-lemma` | Inline styles from JS (see palette above) | `<w>` match (multi) |

**`<hi>` token-based stacking:** `@rend` is space-separated. The renderer emits `class="hi hi-{token1} hi-{token2} …"` per `<hi>`, so compound values like `rend="initial upper_case_first_letter"` accumulate both rules from CSS. Five token classes cover 20 of the 24 attested `@rend` shapes (5 single + 15 compounds). Four further single-token shapes (`textStyle`, `inkRed`, `initial_historisiert`, `marginalia`; 344 elements total) receive only the base `.hi` class. (The ~43k previously-unstyled elements are the #17 migration figure.)

## Known Inconsistencies

- Multi-lemma highlight CSS duplicated in `korpus.css` and `playground/css/style.css` (+ JS array in `ui-helpers.js`)
- Lemma page uses inline `<style>` instead of a dedicated CSS file
- `#3b75d8` hardcoded in some places instead of using `--accent-primary` or `brand-500`
