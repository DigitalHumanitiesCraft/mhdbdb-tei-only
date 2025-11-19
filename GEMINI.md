# MHDBDB TEI Repository Context

## Project Overview
This project is a **client-side only** web application for searching and browsing TEI-encoded Middle High German (MHG) literature. It relies on **pre-built JSON indices** generated from XML source files to ensure fast performance in the browser without a backend server.

**Key Components:**
1.  **Main Site** (`index.html`): Public-facing corpus browser.
2.  **Playground** (`playground/index.html`): Advanced research tool with modular UI.
3.  **Build Pipeline** (`scripts/*.py`): Python scripts that convert TEI/XML into compressed JSON indices.

## Architecture & Data Flow
- **Source of Truth:**
    - `tei/*.xml`: Middle High German texts.
    - `authority-files/*.xml`: Controlled vocabularies (persons, works, concepts, etc.).
- **Build Process:** Python scripts parse these XML files and generate optimized JSON indices in `data/`.
- **Runtime:** The browser fetches `data/corpus-index.json.gz` and `data/authority-index.json.gz`, decompresses them, and caches them in **IndexedDB** (via Dexie.js).
- **Frontend:** Vanilla JavaScript (ES Modules) with Tailwind CSS. No framework like React or Vue.

## Key Commands

### Development
- **Start Server:** `npm run serve` (Starts `http-server` on port 8080)
- **Run Tests:** `npm test` (Runs Playwright tests)

### Data Build (Required if XML files change)
- **Rebuild All:** `npm run build`
- **Rebuild Corpus Index:** `python scripts/build-corpus-index.py`
- **Rebuild Authority Index:** `python scripts/build-authority-index.py`

## Directory Structure
- `tei/` - Source TEI XML files (UTF-8).
- `authority-files/` - Source authority XML files.
- `data/` - Generated JSON indices (gzip compressed).
- `js/` - Main site JavaScript (SearchEngine, TextRenderer).
- `playground/js/` - Playground JavaScript (Modular architecture).
- `lib/` - Shared utilities (Text normalization, Corpus loader).
- `scripts/` - Python build and validation scripts.
- `testing/` - Playwright test suite.
- `docs/` - Comprehensive documentation (Architecture, Data Model, etc.).

## Coding Conventions

### JavaScript
- **Style:** Vanilla JS using ES Modules (`import`/`export`).
- **Normalization:** Always use `lib/text-normalizer.js` for MHG character handling (e.g., `â` -> `a`).
- **DOM:** Direct DOM manipulation or utility helpers; no Virtual DOM.
- **Async:** Heavy use of `async/await` for data loading and IndexedDB operations.

### Python (Build Scripts)
- **Version:** Python 3.13+.
- **Libraries:** `lxml` for XML parsing.
- **Parity:** Logic in Python build scripts (e.g., normalization) **MUST** match JavaScript runtime logic.

### XML / TEI
- **Namespace:** Always use `http://www.tei-c.org/ns/1.0`.
- **Encoding:** UTF-8.
- **Entities:** Angle brackets `&lt;` `&gt;` in text content are intentional/correct.

## Testing
- **Framework:** Playwright.
- **Scope:** Tests cover index loading, search logic, normalization, and UI flows.
- **Constraint:** Tests expect the dev server to be running or start it automatically.

## Critical "Gotchas"
1.  **No Backend:** Do not assume server-side logic. Everything happens in the browser.
2.  **Index Consistency:** If you edit a `.xml` file, you **must** rebuild the relevant index for changes to appear in the app.
3.  **Memory:** The app loads large datasets into memory/IndexedDB. Be mindful of memory usage.
4.  **Git:** `main` is production. Feature branches are preferred.
