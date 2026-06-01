# Shared Site-Chrome (Nav + Footer) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** De-duplicate the header navigation and footer (currently hand-copied and drifted across 12 HTML files) into single source partials injected by a Python build step, and centralize their behaviour (mobile-menu toggle, clear-site-data, current-year) into one small script loaded everywhere.

**Architecture:** Build-step injection (chosen over client-side rendering for accessibility / no-JS / GitHub-Pages-static output). `includes/_nav.html` + `includes/_footer.html` hold the canonical markup with a `{{ROOT}}` path placeholder and an active-state mechanism. `scripts/build-pages.py` finds marker comments in each page, resolves `{{ROOT}}` from directory depth, sets the active nav item, and rewrites the marked region idempotently; a `--check` mode acts as a CI drift gate. A new `assets/js/site-chrome.js` (loaded on every page) handles the nav/footer behaviours, replacing the per-page / missing handlers.

**Tech Stack:** Python 3.13 (stdlib only — `re`, `pathlib`, `argparse`), vanilla JS ES6, existing Tailwind classes (no new utilities → no CSS rebuild).

**Two commits:**
- **Commit 1** — HTML centralization (partials + build script + convert 12 pages). The "variant b" core, low-risk, independently verifiable.
- **Commit 2** — `site-chrome.js` (behaviour), wire it into every page, remove the now-duplicate `clearSiteData` wiring from `app.js`.

---

## File Structure

**Create:**
- `includes/_nav.html` — canonical header nav (desktop + mobile), source from `korpus.html` lines 38-96. Paths use `{{ROOT}}`. Each nav link tagged `data-nav="<page-key>"` for active-state.
- `includes/_footer.html` — canonical footer, source from `index.html` lines 658-752 (the most complete variant: logos + license + 5 links incl. Barrierefreiheit + clear-data button). Paths use `{{ROOT}}`.
- `scripts/build-pages.py` — the generator + `--check` gate.
- `assets/js/site-chrome.js` — (Commit 2) mobile-menu toggle, clear-site-data, current-year.

**Modify (Commit 1):** all 12 pages that carry the nav — replace `<header>…</header>` and `<footer>…</footer>` with marker blocks:
- Root (`{{ROOT}}` = ``): `index.html`, `korpus.html`, `impressum.html`, `barrierefreiheit.html`, `hilfe.html`, `hilfe-daten.html`, `hilfe-daten-beitragen.html`, `hilfe-korpussuche.html`, `hilfe-playground.html`, `hilfe-schema.html`
- Depth-1 (`{{ROOT}}` = `../`): `lemma/index.html`, `playground/index.html`
- `404.html` — has no standard nav today; out of scope for this refactor (note in commit body).

**Modify (Commit 2):** `assets/js/app.js` (remove `clearSiteDataBtn` listener + `handleClearSiteData`, now in site-chrome.js), all 12 pages get a `<script src="{{ROOT}}assets/js/site-chrome.js">` (injected via build).

**Page → nav active-key + `{{ROOT}}` map** (drives build):
```
index.html                 -> key=start   root
korpus.html                -> key=korpus  root
playground/index.html      -> key=playground depth1
hilfe.html                 -> key=hilfe   root
hilfe-daten.html           -> key=hilfe   root
hilfe-daten-beitragen.html -> key=hilfe   root
hilfe-korpussuche.html     -> key=hilfe   root
hilfe-playground.html      -> key=hilfe   root
hilfe-schema.html          -> key=hilfe   root
impressum.html             -> key=(none)  root
barrierefreiheit.html      -> key=(none)  root
lemma/index.html           -> key=(none)  depth1
```
Active state = `aria-current="page"` + `text-slate-900 font-semibold` on the matching `data-nav` link (Kontakt links to `index.html#contact`, never active).

---

## Marker contract

Each page keeps thin markers; the build owns the region between them:
```html
<!-- NAV:START key=korpus -->
  …generated nav, do not edit by hand…
<!-- NAV:END -->
…
<!-- FOOTER:START -->
  …generated footer, do not edit by hand…
<!-- FOOTER:END -->
```
- `{{ROOT}}` in the partials → `` for root pages, `../` for depth-1.
- Build is idempotent: marker content fully replaced each run → second run = no diff.
- `--check`: rebuild into memory, compare to disk; exit 1 + list drifted files if different. No writes.
- Self-migrating first run: if a page has no `NAV:START` marker but has `<header …>…</header>`, replace that block with the markered nav; same for `<footer …>…</footer>`. One `<header>`/`<footer>` per page → non-greedy regex is safe.

---

## Commit 1 — HTML centralization

### Task 1: Canonical partials

**Files:**
- Create: `includes/_nav.html`
- Create: `includes/_footer.html`

- [ ] **Step 1: Create `includes/_nav.html`** — copy the header block from `korpus.html:38-96` verbatim, then: replace `href="index.html"` → `href="{{ROOT}}index.html"`, `href="korpus.html"` → `href="{{ROOT}}korpus.html"`, `href="playground/index.html"` → `href="{{ROOT}}playground/index.html"`, `href="hilfe.html"` → `href="{{ROOT}}hilfe.html"`, `href="index.html#contact"` → `href="{{ROOT}}index.html#contact"`, `src="assets/images/mhdbdb-logo.png"` → `src="{{ROOT}}assets/images/mhdbdb-logo.png"`. Add `data-nav="start|korpus|playground|hilfe"` to the four nav links (both desktop and mobile copies). Kontakt link gets no `data-nav`.

- [ ] **Step 2: Create `includes/_footer.html`** — copy the footer block from `index.html:658-752` verbatim, then replace `src="assets/images/…"` → `src="{{ROOT}}assets/images/…"` (3 logos), `href="impressum.html"` → `href="{{ROOT}}impressum.html"`, `href="barrierefreiheit.html"` → `href="{{ROOT}}barrierefreiheit.html"`. Leave mailto/external/CC links unchanged. Keep the `clearSiteDataBtn` button and `current-year` span as-is.

### Task 2: Build script

**Files:**
- Create: `scripts/build-pages.py`

- [ ] **Step 1: Write `scripts/build-pages.py`** with: a `PAGES` dict (page path → `{key, root}` per the map above); `load_partial(name)` reads `includes/_nav.html` / `includes/_footer.html`; `render(partial, root, active_key)` does `partial.replace("{{ROOT}}", root)` then, for nav, adds `aria-current="page"` + ` font-semibold` and swaps `text-slate-600` → `text-slate-900` on the `data-nav="<active_key>"` anchors (regex on the specific tag); `inject(html, start, end, content)` replaces between marker comments (regex `re.compile(re.escape(start)+r".*?"+re.escape(end), re.S)`); first-run migration: if no `NAV:START`, replace `<header[^>]*>.*?</header>` (re.S, non-greedy) with `NAV:START/END` block, same for `<footer[^>]*>.*?</footer>`. `main()` supports `--check` (compare, exit 1 on drift, never write) and default (write changed files, print summary). stdlib only.

- [ ] **Step 2: Dry-run check on a copy** — Run: `python scripts/build-pages.py --check`
  Expected: exit 1, lists all 12 pages as "would change" (markers not yet present). Confirms detection works before writing.

### Task 3: Convert all pages + verify idempotency

- [ ] **Step 1: Run the build (writes markers + generated content)** — Run: `python scripts/build-pages.py`
  Expected: "12 pages updated". Each page now has NAV/FOOTER markers with generated content; `lemma/`+`playground/` links carry `../`.

- [ ] **Step 2: Verify idempotency** — Run: `python scripts/build-pages.py` again.
  Expected: "0 pages updated" (no diff on second run).

- [ ] **Step 3: Verify `--check` is green** — Run: `python scripts/build-pages.py --check`
  Expected: exit 0, "all pages in sync".

- [ ] **Step 4: Review the diff** — Run: `git --no-pager diff --stat`
  Expected: 12 HTML files changed + 2 new partials + 1 new script. Spot-read `lemma/index.html` (links must be `../index.html` etc.) and `index.html` (root links unchanged, footer identical to before).

### Task 4: Live verification (verify skill — runtime observation)

- [ ] **Step 1: Hard-reload each depth + check nav links resolve** — In browser (server on :8080): load `/index.html`, `/korpus.html`, `/lemma/index.html`, `/playground/index.html`. For each, JS-assert every nav `<a>` href resolves to an existing page (no `../` from root, correct `../` from subdirs) and the active item has `aria-current="page"`.
- [ ] **Step 2: Footer parity** — On a previously-minimal page (`lemma/index.html`), confirm the full footer now renders (logos + 5 links). On `hilfe.html`, confirm footer present.
- [ ] **Step 3: No console errors** on any of the four pages.

- [ ] **Step 5: Commit 1** (await user approval per repo rules)
```bash
git add includes/_nav.html includes/_footer.html scripts/build-pages.py index.html korpus.html impressum.html barrierefreiheit.html hilfe.html hilfe-daten.html hilfe-daten-beitragen.html hilfe-korpussuche.html hilfe-playground.html hilfe-schema.html lemma/index.html playground/index.html
git commit -m "refactor: centralize nav + footer into build-injected partials"
```

---

## Commit 2 — Shared behaviour (site-chrome.js)

### Task 5: site-chrome.js

**Files:**
- Create: `assets/js/site-chrome.js`

- [ ] **Step 1: Write `assets/js/site-chrome.js`** — an IIFE / `DOMContentLoaded` handler that:
  (a) **mobile menu**: `document.getElementById('mobileMenuButton')?.addEventListener('click', () => document.getElementById('mobileMenu')?.classList.toggle('hidden'))`;
  (b) **current year**: `document.querySelectorAll('.current-year').forEach(el => el.textContent = String(new Date().getFullYear()))`;
  (c) **clear site data**: bind `#clearSiteDataBtn` click → `confirm(...)` → delete all IndexedDB DBs (`indexedDB.databases()` loop) + `localStorage.clear()` + `sessionStorage.clear()` + `alert(...)` + `location.reload()`. This is the standalone equivalent of `app.js:1032-1081` steps 3-4 (steps 1-2 are redundant — step 3 deletes all DBs regardless).

### Task 6: Wire into every page via build

**Files:**
- Modify: `scripts/build-pages.py`
- Modify: `includes/_footer.html` (or a dedicated `SCRIPT` marker)

- [ ] **Step 1: Add a `<!-- CHROME-JS -->` injection** — simplest: append `<script src="{{ROOT}}assets/js/site-chrome.js" defer></script>` as part of the footer partial (it already renders on every page and carries `{{ROOT}}`). Re-run `python scripts/build-pages.py`; verify every page now loads the script (incl. previously script-less hilfe/impressum/barrierefreiheit and lemma/404).

### Task 7: Remove duplicate wiring from app.js

**Files:**
- Modify: `assets/js/app.js:47` (drop `clearSiteDataBtn` element ref), `:289-291` (drop the listener), `:1032-1081` (`handleClearSiteData` method)

- [ ] **Step 1: Remove the `clearSiteDataBtn` element lookup, its `addEventListener`, and the `handleClearSiteData` method** from `app.js`. site-chrome.js now owns this on every page. This prevents a double listener (double-clear) on index/korpus where both scripts load.

### Task 8: Live verification

- [ ] **Step 1: Mobile menu** — on a narrow viewport (or via JS) click `#mobileMenuButton` on a previously-script-less page (e.g. `hilfe.html`) → `#mobileMenu` toggles `hidden`. (Was dead before.)
- [ ] **Step 2: current-year** — confirm `.current-year` shows the live year on all pages.
- [ ] **Step 3: clear-site-data, no double-fire** — on `korpus.html` (loads both app.js + site-chrome.js) verify exactly one click handler is bound to `#clearSiteDataBtn` (e.g. instrument or check no duplicate clear). Do NOT click through (native `confirm`/`alert` blocks browser automation); verify binding via the function/console instead.
- [ ] **Step 4: No console errors** on index/korpus/hilfe/impressum/lemma/playground.

- [ ] **Step 5: Commit 2** (await user approval)
```bash
git add assets/js/site-chrome.js scripts/build-pages.py includes/_footer.html assets/js/app.js index.html korpus.html impressum.html barrierefreiheit.html hilfe.html hilfe-daten.html hilfe-daten-beitragen.html hilfe-korpussuche.html hilfe-playground.html hilfe-schema.html lemma/index.html playground/index.html
git commit -m "refactor: shared site-chrome.js for nav/footer behaviour; drop duplicate clearSiteData from app.js"
```

---

## Follow-ups enabled (not in this plan)
- **#117 Wörterbuch menu item**: after this lands, adding the 6th nav item = one edit to `includes/_nav.html` + rebuild (was: 12 files × 2). Pending the naming decision.
- **CI gate**: add `python scripts/build-pages.py --check` to the existing CI workflow so hand-edits of generated regions fail fast.
- **DEVELOPMENT.md**: document "edit partials, run build-pages.py, never hand-edit between markers".

## Notes / risks
- `handleClearSiteData` uses native `confirm()`/`alert()` — unchanged for real users; cannot be "really" clicked through in browser automation (dialog blocks the extension) → verify via function/console.
- No new Tailwind utilities introduced → no `npm run build:css` needed.
- No index rebuild needed (no data/index change).
- Concurrent-session git rule: stage files by name (done in commit steps), never `git add -A`.
