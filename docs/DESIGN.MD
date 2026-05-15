# Design

Visual and interaction patterns for the MHDBDB TEI Repository. Complements [ARCHITECTURE.MD](ARCHITECTURE.MD) (technical) and [FEATURES.MD](FEATURES.MD) (user-facing). This document is the reference when building new UI components.

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

**Authoritative source: `tei-text-reader.js` constructor (lines 23-29)**

These colors are used by the reading view for multi-lemma highlighting:

| Slot | Background | Border | Text | Name |
|------|-----------|--------|------|------|
| 1 | `#fecaca` | `#ef4444` | `#991b1b` | Red |
| 2 | `#bfdbfe` | `#3b82f6` | `#1e3a8a` | Blue |
| 3 | `#bbf7d0` | `#22c55e` | `#166534` | Green |
| 4 | `#fde68a` | `#f59e0b` | `#92400e` | Yellow |
| 5 | `#ddd6fe` | `#8b5cf6` | `#5b21b6` | Purple |

**Color assignment:** `colors[idx % 5]` — sequential, wraps after 5 lemmas.

**Also defined in (may differ in slot order):**
- `korpus.css` — `mark.highlight-{n}` classes (6 slots: red, green, blue, pink, orange, purple)
- `playground/css/style.css` — duplicate of korpus.css pattern
- `ui-helpers.js` `LEMMA_COLORS` — playground proximity search

**Known inconsistency:** CSS classes use a different slot order (green=2, blue=3) and different colors for slots 4-5 (pink/orange vs yellow/purple). The JS inline styles in `tei-text-reader.js` override CSS classes in the reading view; CSS classes are used by playground proximity result cards.

Single `<mark>` highlight (single-lemma mode): `#fbbf24` bg / `#78350f` text.

Page background: `bg-slate-100` (`#f1f5f9`) on all pages.

## Typography

### Font Stack

- **UI**: System stack (Tailwind default) — `ui-sans-serif, system-ui, sans-serif`
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

Neun Module unter `playground/js/ui/tei/` teilen eine konsistente Struktur. Wer ein neues Analyse-Werkzeug ergänzt, sollte das Pattern befolgen — neue Module ohne erkennbaren Grund abweichen lassen den Playground inkonsistent wirken und brechen Konventionen, auf die der Router und die Sidebar-Buttons aufbauen.

**Kanonische Beispiele:** `lemma-distribution.js` (#90), `verse-position-search.js` (#47.3), `concept-distribution.js` (#47 R2).

### Konstruktor — Thunks statt direkter Referenzen

```js
constructor(getCorpusTexts, authorityManager, getAuthorityData) {
  this.getCorpusTexts = getCorpusTexts;
  this.authorityManager = authorityManager;
  this.getAuthorityData = getAuthorityData;
  this.state = { ...DEFAULT_STATE };
}
```

`getCorpusTexts`/`getAuthorityData` werden als Funktionen übergeben, nicht als fertige Arrays. Grund: nach Index-Reload (Bump v4.1.1 → v4.2.0, Cache-Invalidate) zeigen direkte Array-Referenzen auf stale Daten. Thunks ziehen jedes Mal das aktuelle Array vom `teiManager`. Lehre aus #97-#100 (Corpus-Index-Property-Drift).

### State — Frozen Defaults + Stateful Instance

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

`Object.freeze` verhindert versehentliches Mutieren des Defaults; `this.state = { ...DEFAULT_STATE }` macht ein frisches mutables Objekt pro Instanz. Bei Reset (z.B. nach Korpus-Wechsel): `this.state = { ...DEFAULT_STATE }`.

### Lifecycle — `show()` ➝ `render()` ➝ `renderForm() + renderBody()` ➝ `attachHandlers()`

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

- `show()` ist der Router-Entrypoint, mit Guard für „Korpus noch nicht geladen".
- `render()` macht **einmal** `innerHTML = ...` und ruft danach `attachHandlers()`. Kein DOM-Diffing — jeder Render ist ein Wegwerf. Form behält den Fokus, weil `attachHandlers()` nach `innerHTML` `refocusInput()` aufrufen kann.
- `renderForm()` / `renderBody()` geben Strings zurück, kein direktes DOM-Mutating. Halt das Template-getrieben.

### State-Driven Body

`renderBody()` ist ein Branch über `this.state`:

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

Order matters: Empty-State → Error-State → No-Match → Computing → Result. Wer das umstellt, liefert dem User „Keine Lemmata zugeordnet" während die Suche eigentlich noch läuft.

### Async + Chunking (für O(L × T) Aggregationen)

Bei Modulen, deren Aggregation den Main-Thread mehr als ~50ms blockieren kann (kritisch ab ~2000 Items), Chunking mit time-based Yield:

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

Vermeide `setTimeout(0)` als Yield — Chrome drosselt es auf >=1000ms im Hintergrund-Tab und macht Tests unreliabel. Vermeide `requestIdleCallback` — kein Garantie über Anteil der Frame-Zeit. MessageChannel ist die robuste Wahl.

### Escape-Helpers — Pro-Modul, nicht importiert

Jedes Modul hat am Ende:

```js
function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
function escapeAttr(s) { return escapeHtml(s); }
```

Self-contained statt zentralem `lib/escape.js`-Import: Modul lässt sich kopieren/verschieben ohne Pfad-Anpassung, und die fünf Zeilen sind schneller geschrieben als die Import-Stelle.

### Brand-Akzent — Nur Default-Button

| Use | Klassen |
|-----|---------|
| Default-Aktion („Suchen", „Anwenden") | `rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100` |
| Sekundär (Cancel, Reset) | `bg-white border-slate-200 hover:border-slate-400` |
| Result-Heading | `text-lg font-semibold text-brand-700` |
| Bar-Chart-Bars | `fill-brand-400 hover:fill-brand-600 transition` |

Brand-Farbe ist der Akzent, nicht die Grundfarbe. Wenn ein Modul plötzlich vier brand-farbene Buttons hat, verliert der Default seinen Akzent-Status.

### Cross-Module Linking

Klick auf Treffer → Reading-View. Pattern:

```js
const href = `../korpus.html?textId=${encodeURIComponent(h.id)}&lemmaIds=${encodeURIComponent(lemmaId)}`;
```

Nicht hash-routen — `korpus.html` ist eine separate Site. Pure-Anchor-Tags mit `target="_blank" rel="noopener"`, damit der User die Playground-Session nicht verliert.

### Multi-Lemma als dokumentierter Outlier

`playground/js/ui/tei/multi-lemma.js` nutzt **Modal statt in-place Form** (`#multiLemmaModal`), weil seine vier Inputs (Lemmata-Liste, Modus, Distanz, Korpus-Auswahl-Checkbox) im Sidebar nicht reinpassen würden. Das ist die einzige zulässige Abweichung — wer ein neues Modul mit 1-3 Inputs baut, gehört in den in-place-Form-Pfad. Modal nur bei genuin grossen Input-Surfaces.

## Layout Patterns

### Container

`container mx-auto px-6` — constrained to `max-w-6xl` (landing) or `max-w-4xl` (lemma page).

### Column Grids

| Layout | Classes | Used in |
|--------|---------|---------|
| 2-column | `grid xl:grid-cols-[1fr_2fr]` | Korpus default |
| 3-column | `grid xl:grid-cols-[1fr_1fr_2fr]` | Playground, korpus post-search |
| Columns collapse at `max-width: 1279px` to single column.

### Section Rhythm (Landing Page)

`py-20` between sections, alternating `bg-white` / `bg-slate-50`.

### Sticky Header

`sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-slate-200` — identical across all pages.

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

Logo (`w-40` image + `text-lg font-bold text-brand-600`) left, nav links right (`hidden md:flex gap-6`). Mobile hamburger at `md:hidden`. No active-page highlighting.

### Footer

Institutional logos row + divider + copyright/clear-data row. `bg-slate-100 py-8`.

### Cross-Page Links

| From | To | Pattern |
|------|----|---------|
| Playground result | Korpus reading view | `window.open('../korpus.html?textId=…&lemmaIds=…')` |
| Lemma occurrence | Korpus reading view | `<a href="../korpus.html?textId=…&lemmaIds=…">` |
| Lemma etymology | Other lemma page | `<a href="{numericId}" class="etymology-link">` |

## CSS Architecture

Three-layer stack (load order):

| Layer | File | Contains |
|-------|------|----------|
| 1 | `tailwind-output.css` | Utility classes (layout, typography, color, spacing, responsive) |
| 2 | `assets/css/shared.css` | Design tokens (CSS vars), spinner, buttons, loading screen, animations |
| 3 | Page-specific CSS | `korpus.css` or `playground/css/style.css` or inline `<style>` (lemma) |

**Rule**: Semantic tokens in CSS vars. Layout and one-off styling in Tailwind utilities. Page-specific components in dedicated CSS. JS-generated HTML uses Tailwind classes in template literals.

### Animations (shared.css)

| Name | Effect | Used for |
|------|--------|----------|
| `fadeIn` | opacity 0 to 1 | General reveal |
| `slideUp` | translate + scale + opacity | Modals, error toast |
| `slideDown` | translate + opacity | Proximity controls |
| `spin` | 360deg rotation | Spinner |
| `chipIn` | scale + opacity | Lemma chip entry (in playground style.css) |

## TEI Reading View CSS Classes

Source: `assets/css/korpus.css` (post-#17 reader-view styling). Element-to-class mapping in [ARCHITECTURE.MD §TEI Element Rendering Map](ARCHITECTURE.MD#tei-element-rendering-map).

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
| `.lb-number` | small superscript-style line counter for prose | follows `<lb>` |
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

**`<hi>` token-based stacking:** `@rend` is space-separated. The renderer emits `class="hi hi-{token1} hi-{token2} …"` per `<hi>`, so compound values like `rend="initial upper_case_first_letter"` accumulate both rules from CSS. Five token classes cover all 20 attested `@rend` shapes (5 single + 15 compounds, ~43k elements that were previously unstyled).

## Known Inconsistencies

- Multi-lemma highlight CSS duplicated in `korpus.css` and `playground/css/style.css` (+ JS array in `ui-helpers.js`)
- Lemma page uses inline `<style>` instead of a dedicated CSS file
- `#3b75d8` hardcoded in some places instead of using `--accent-primary` or `brand-500`
- No active-page highlighting in navigation header
