# Wörterbuch-Einstiegsseite (#117) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A–Z-Einstiegsseite `woerterbuch.html` für die ~43.754 Lemma-Seiten, mit Indexleiste, Pagination und Nav-Eintrag auf allen Seiten.

**Architecture:** Reine Frontend-Seite nach dem Muster von `lemma/lemma-page.js`: lädt den bestehenden `data/authority-index.json.gz` über `CorpusLoader` (IndexedDB-Cache, 30 Tage), bucketet client-seitig nach Anfangsbuchstabe des `normalized`-Felds und rendert ein paginiertes Register. Kein neues Build-Artefakt. Nav/Footer kommen über `scripts/build-pages.py` (Marker-Injection).

**Tech Stack:** Vanilla JS ES6-Module, Tailwind (pre-compiled), Pako + Dexie via CDN, Playwright.

**Spec:** `docs/features/117-woerterbuch-einstiegsseite.md` (Design approved 2026-06-11).

**Projektregeln, die Skill-Defaults überschreiben:**
- KEINE Commits pro Task. Ein Sammelcommit ganz am Ende, erst nach Christians Test + Freigabe (CLAUDE.md).
- `npm test` (Playwright) NIEMALS ungefragt starten — Testlauf ist ein expliziter Rückfrage-Schritt.
- Stets gezielt stagen (`git add <pfad>`), nie `git add -A` (parallele Sessions).

---

### Task 1: Controller `assets/js/woerterbuch.js`

**Files:**
- Create: `assets/js/woerterbuch.js`
- Referenz (nur lesen): `lemma/lemma-page.js`, `assets/js/lib/corpus-loader.js`

Der Authority-Index liefert `lemmata`-Einträge der Form
`{ id: "lemma_879", lemma: "brôt", normalized: "brot", pos: "NOM", senseCount: 1, ... }`.
Randfälle: 14 Lemmata beginnen mit `ë`/`ú` (nicht in der MHG-Normalisierungstabelle) → Unicode-NFD-Strip; 5 „Lemmata" beginnen mit Ziffern (`1`, `36`, `42`, `46`, `49`) → `#`-Bucket.

- [ ] **Step 1: Datei anlegen mit vollständigem Controller**

```js
/**
 * Wörterbuch Page Controller (#117)
 * A–Z-Einstiegsseite für die persistenten Lemma-Seiten (/lemma/?id=N).
 * Liest den pre-built Authority-Index (CorpusLoader, IndexedDB-Cache).
 * URL-State: ?buchstabe=s&seite=3
 */

import { CorpusLoader } from './lib/corpus-loader.js';

const PAGE_SIZE = 200;
const LETTERS = [...'abcdefghijklmnopqrstuvwxyz', '#'];

class WoerterbuchPage {
    constructor() {
        this.corpusLoader = new CorpusLoader('data');
        this.buckets = new Map();   // letter → sortierte Lemma-Einträge
        this.collator = new Intl.Collator('de');
        this.activeLetter = 'a';
        this.activePage = 1;

        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
            content: document.getElementById('woerterbuchContent'),
            letterBar: document.getElementById('letterBar'),
            letterHeading: document.getElementById('letterHeading'),
            entryGrid: document.getElementById('entryGrid'),
            pagination: document.getElementById('pagination'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage'),
        };
    }

    /** Anfangsbuchstabe a–z über normalized, NFD-Fallback für ë/ú; sonst '#'. */
    bucketKey(entry) {
        const base = entry.normalized || entry.lemma || '';
        if (!base) return '#';
        const c = base[0].toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        return c >= 'a' && c <= 'z' ? c : '#';
    }

    buildBuckets(lemmata) {
        for (const letter of LETTERS) this.buckets.set(letter, []);
        for (const entry of lemmata) {
            this.buckets.get(this.bucketKey(entry)).push(entry);
        }
        for (const list of this.buckets.values()) {
            list.sort((a, b) =>
                this.collator.compare(a.normalized || a.lemma, b.normalized || b.lemma)
                || this.collator.compare(a.lemma, b.lemma));
        }
    }

    readUrlState() {
        const params = new URLSearchParams(window.location.search);
        const letter = (params.get('buchstabe') || 'a').toLowerCase();
        if (this.buckets.has(letter)) this.activeLetter = letter;
        const page = parseInt(params.get('seite'), 10);
        this.activePage = Number.isInteger(page) && page >= 1 ? page : 1;
    }

    writeUrlState() {
        const params = new URLSearchParams();
        params.set('buchstabe', this.activeLetter);
        if (this.activePage > 1) params.set('seite', String(this.activePage));
        history.replaceState(null, '', `${window.location.pathname}?${params}`);
    }

    selectLetter(letter, page = 1) {
        this.activeLetter = letter;
        const pageCount = Math.max(1, Math.ceil(this.buckets.get(letter).length / PAGE_SIZE));
        this.activePage = Math.min(Math.max(1, page), pageCount);
        this.writeUrlState();
        this.renderLetterBar();
        this.renderEntries();
        this.renderPagination();
    }

    renderLetterBar() {
        this.elements.letterBar.innerHTML = '';
        for (const letter of LETTERS) {
            const count = this.buckets.get(letter).length;
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = letter === '#' ? '#' : letter.toUpperCase();
            btn.title = `${count.toLocaleString('de-DE')} Lemmata`;
            btn.dataset.letter = letter;
            btn.disabled = count === 0;
            const isActive = letter === this.activeLetter;
            btn.className = isActive
                ? 'w-9 h-9 rounded-md text-sm font-semibold bg-brand-600 text-white'
                : count === 0
                    ? 'w-9 h-9 rounded-md text-sm font-medium text-slate-300 cursor-default'
                    : 'w-9 h-9 rounded-md text-sm font-medium text-slate-600 hover:bg-brand-100 hover:text-brand-700 transition';
            if (!btn.disabled && !isActive) {
                btn.addEventListener('click', () => this.selectLetter(letter));
            }
            this.elements.letterBar.appendChild(btn);
        }
    }

    renderEntries() {
        const list = this.buckets.get(this.activeLetter);
        const start = (this.activePage - 1) * PAGE_SIZE;
        const pageEntries = list.slice(start, start + PAGE_SIZE);

        const label = this.activeLetter === '#' ? '#' : this.activeLetter.toUpperCase();
        this.elements.letterHeading.textContent =
            `${label} – ${list.length.toLocaleString('de-DE')} Lemmata`;

        this.elements.entryGrid.innerHTML = '';
        for (const entry of pageEntries) {
            const numericId = entry.id.replace('lemma_', '');
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between gap-2 py-1.5 px-2 rounded hover:bg-slate-50';

            const link = document.createElement('a');
            link.href = `lemma/?id=${numericId}`;
            link.textContent = entry.lemma;
            link.className = 'text-brand-700 hover:text-brand-900 hover:underline font-medium truncate';

            const pos = document.createElement('span');
            pos.textContent = entry.pos || '—';
            pos.className = 'pos-badge bg-brand-100 text-brand-700 flex-shrink-0';

            row.appendChild(link);
            row.appendChild(pos);
            this.elements.entryGrid.appendChild(row);
        }
    }

    renderPagination() {
        const total = this.buckets.get(this.activeLetter).length;
        const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
        const el = this.elements.pagination;
        el.innerHTML = '';
        if (pageCount === 1) return;

        const makeBtn = (text, page, { disabled = false, active = false } = {}) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = text;
            btn.disabled = disabled || active;
            btn.className = active
                ? 'px-3 py-1.5 rounded-md text-sm font-semibold bg-brand-600 text-white'
                : disabled
                    ? 'px-3 py-1.5 rounded-md text-sm text-slate-300 cursor-default'
                    : 'px-3 py-1.5 rounded-md text-sm text-slate-600 hover:bg-brand-100 hover:text-brand-700 transition';
            if (!btn.disabled) {
                btn.addEventListener('click', () => this.selectLetter(this.activeLetter, page));
            }
            return btn;
        };

        el.appendChild(makeBtn('‹ Zurück', this.activePage - 1, { disabled: this.activePage === 1 }));

        // Fensterung: erste, letzte, ±2 um die aktive Seite; Lücken als „…"
        let lastShown = 0;
        for (let p = 1; p <= pageCount; p++) {
            const show = p === 1 || p === pageCount || Math.abs(p - this.activePage) <= 2;
            if (!show) continue;
            if (p - lastShown > 1) {
                const gap = document.createElement('span');
                gap.textContent = '…';
                gap.className = 'px-1 text-slate-400 text-sm';
                el.appendChild(gap);
            }
            el.appendChild(makeBtn(String(p), p, { active: p === this.activePage }));
            lastShown = p;
        }

        el.appendChild(makeBtn('Weiter ›', this.activePage + 1, { disabled: this.activePage === pageCount }));
    }

    updateLoading(message, percent) {
        if (this.elements.loadingStatus) this.elements.loadingStatus.textContent = message;
        if (this.elements.loadingProgress) this.elements.loadingProgress.style.width = `${percent}%`;
    }

    showError(message) {
        this.elements.loadingScreen.style.display = 'none';
        this.elements.errorDisplay.classList.remove('hidden');
        this.elements.errorMessage.textContent = message;
    }

    async init() {
        try {
            this.updateLoading('Lade Wörterbuchdaten...', 30);
            const authorityIndex = await this.corpusLoader.loadAuthorityIndex();
            this.updateLoading('Baue Register...', 80);

            this.buildBuckets(authorityIndex.lemmata);
            this.readUrlState();
            this.selectLetter(this.activeLetter, this.activePage);

            this.elements.loadingScreen.style.display = 'none';
            this.elements.content.classList.remove('hidden');
        } catch (error) {
            console.error('[WoerterbuchPage] Initialisierung fehlgeschlagen:', error);
            this.showError(`Der Authority-Index konnte nicht geladen werden: ${error.message}`);
        }
    }
}

const page = new WoerterbuchPage();
page.init();
```

- [ ] **Step 2: Syntax-Check**

Run: `node --check assets/js/woerterbuch.js`
Expected: kein Output, Exit 0.

(Kein Commit — Sammelfreigabe am Ende.)

---

### Task 2: Seite `woerterbuch.html`

**Files:**
- Create: `woerterbuch.html`
- Referenz (nur lesen): `korpus.html` (Kopf), `lemma/index.html` (Loading/Error-Muster, `.pos-badge`-Stil)

Die Seite bekommt leere NAV/FOOTER-Markerpaare; `build-pages.py` (Task 3) füllt sie. Der `.pos-badge`-Stil wird von `lemma/index.html` übernommen (dort inline definiert, hier ebenso — bewusst kein Refactor in shared.css, beide Seiten bleiben eigenständig).

- [ ] **Step 1: Datei anlegen**

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="MHDBDB Wörterbuch - Alle Lemmata der Mittelhochdeutschen Begriffsdatenbank von A bis Z">
    <meta name="keywords" content="Middle High German, dictionary, Wörterbuch, Lemmata, MHDBDB">
    <meta name="author" content="Universität Salzburg">

    <title>Wörterbuch - MHDBDB</title>

    <!-- Pako for gzip decompression -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>

    <!-- Dexie.js for IndexedDB -->
    <script src="https://unpkg.com/dexie@3.2.4/dist/dexie.min.js"></script>

    <!-- Tailwind CSS (pre-compiled) -->
    <link rel="stylesheet" href="assets/css/tailwind-output.css">

    <link rel="icon" type="image/png" href="assets/images/mhdbdb-logo.png">
    <link rel="stylesheet" href="assets/css/shared.css">

    <style>
        .pos-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
</head>
<body class="bg-slate-100 text-slate-900">

    <!-- Loading Screen -->
    <div id="loadingScreen" class="loading-screen">
        <div class="loading-content">
            <div class="spinner-large spinner"></div>
            <h2 class="text-xl font-semibold text-slate-800">Wörterbuch wird geladen...</h2>
            <p id="loadingStatus" class="loading-message">Initialisiere Datenbank...</p>
            <div class="progress-bar-container">
                <div id="loadingProgress" class="progress-bar" style="width: 0%"></div>
            </div>
        </div>
    </div>

<!-- NAV:START -->
<!-- NAV:END -->

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8 max-w-6xl">

        <!-- Error state -->
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 class="text-xl font-semibold text-red-800 mb-2">Wörterbuch konnte nicht geladen werden</h2>
            <p id="errorMessage" class="text-red-600"></p>
        </div>

        <div id="woerterbuchContent" class="hidden space-y-6">

            <!-- Title -->
            <div>
                <h1 class="text-3xl font-bold text-slate-900">Wörterbuch</h1>
                <p class="text-sm text-slate-500 mt-1">
                    Alle Lemmata der MHDBDB von A bis Z – der Wortindex der Mittelhochdeutschen
                    Begriffsdatenbank. Jeder Eintrag führt zur Lemma-Seite mit Bedeutungen,
                    Schreibformen und Belegstellen.
                </p>
            </div>

            <!-- Letter Index Bar -->
            <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-3 sticky top-20 z-40">
                <div id="letterBar" class="flex flex-wrap gap-1 justify-center"></div>
            </div>

            <!-- Entries -->
            <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                <h2 id="letterHeading" class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4"></h2>
                <div id="entryGrid" class="grid grid-cols-3 xl:grid-cols-4 gap-x-6"></div>
                <div id="pagination" class="flex flex-wrap items-center justify-center gap-1 mt-6"></div>
            </div>

        </div>
    </main>

<!-- FOOTER:START -->
<!-- FOOTER:END -->

    <script type="module" src="assets/js/woerterbuch.js"></script>

</body>
</html>
```

- [ ] **Step 2: Verifizieren, dass die Marker leer sind und die Seite noch NICHT in build-pages registriert ist** (passiert in Task 3)

---

### Task 3: Navigation + build-pages-Registrierung

**Files:**
- Modify: `includes/_nav.html` (Desktop-Block UND Mobile-Block)
- Modify: `scripts/build-pages.py:41-54` (`PAGES`-Dict)

- [ ] **Step 1: Desktop-Nav-Link einfügen** in `includes/_nav.html`, zwischen Playground und Hilfe (Reihenfolge aus dem Issue):

```html
                <a href="{{ROOT}}playground/index.html" data-nav="playground" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition">
                    Playground
                </a>
                <a href="{{ROOT}}woerterbuch.html" data-nav="woerterbuch" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition">
                    Wörterbuch
                </a>
                <a href="{{ROOT}}hilfe.html" data-nav="hilfe" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition">
                    Hilfe
                </a>
```

- [ ] **Step 2: Mobile-Nav-Link einfügen** (gleiches Partial, unterer Block, `py-2`-Variante):

```html
                <a href="{{ROOT}}playground/index.html" data-nav="playground" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition py-2">
                    Playground
                </a>
                <a href="{{ROOT}}woerterbuch.html" data-nav="woerterbuch" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition py-2">
                    Wörterbuch
                </a>
                <a href="{{ROOT}}hilfe.html" data-nav="hilfe" class="text-sm font-medium text-slate-600 hover:text-slate-900 transition py-2">
                    Hilfe
                </a>
```

- [ ] **Step 3: Seite registrieren** in `scripts/build-pages.py`, `PAGES`-Dict, nach `"korpus.html"`:

```python
    "woerterbuch.html": ("woerterbuch", ""),
```

- [ ] **Step 4: Build laufen lassen**

Run: `python scripts/build-pages.py`
Expected: alle Seiten als updated gelistet (neuer Nav-Link überall), inkl. `woerterbuch.html`.

- [ ] **Step 5: Drift-Gate prüfen**

Run: `python scripts/build-pages.py --check`
Expected: `OK — all 13 pages in sync with includes/_nav.html + includes/_footer.html`

---

### Task 4: Fehlerfall der Lemma-Seite verlinkt aufs Wörterbuch

**Files:**
- Modify: `lemma/lemma-page.js:82` (Fehlertext ohne ID)
- Modify: `lemma/index.html:173-179` (Error-Block bekommt zweiten Link)

- [ ] **Step 1: Fehlertext anpassen** in `lemma/lemma-page.js`:

```js
            if (!numericId) {
                this.showError('Keine Lemma-ID angegeben. Alle Lemmata finden Sie im Wörterbuch.');
                return;
            }
```

- [ ] **Step 2: Wörterbuch-Link in den Error-Block** von `lemma/index.html` (vor dem bestehenden Korpus-Suche-Link):

```html
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 class="text-xl font-semibold text-red-800 mb-2">Lemma nicht gefunden</h2>
            <p id="errorMessage" class="text-red-600"></p>
            <div class="flex justify-center gap-3 mt-4">
                <a href="../woerterbuch.html" class="inline-block px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition">
                    Zum Wörterbuch
                </a>
                <a href="../korpus.html" class="inline-block px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition">
                    Zur Korpus-Suche
                </a>
            </div>
        </div>
```

(Der bisherige einzelne `<a>` mit `mt-4 px-4 …` wird durch den Flex-Container ersetzt.)

---

### Task 5: Playwright-Smoke-Test

**Files:**
- Create: `testing/tests/woerterbuch.spec.js`
- Referenz (nur lesen): `testing/tests/lemma-page.spec.js`

- [ ] **Step 1: Test schreiben**

```js
/**
 * Wörterbuch Entry Page Tests (Issue #117)
 * A–Z-Register über den Authority-Index.
 */

import { test, expect } from '@playwright/test';

test.describe('Wörterbuch-Einstiegsseite', () => {

    test('lädt mit Buchstabe A und zeigt Einträge', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        // Indexleiste: 26 Buchstaben + '#'
        const letterButtons = await page.locator('#letterBar button').count();
        expect(letterButtons).toBe(27);

        // Default-Buchstabe A mit Eintragszahl in der Überschrift
        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^A – [\d.]+ Lemmata$/);

        // Einträge gerendert (Seite 1 = 200)
        const entries = await page.locator('#entryGrid a').count();
        expect(entries).toBe(200);
    });

    test('Buchstabenwechsel auf S aktualisiert Einträge und URL', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        await page.click('#letterBar button[data-letter="s"]');

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^S – /);
        expect(page.url()).toContain('buchstabe=s');
    });

    test('Pagination blättert innerhalb des Buchstabens', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html?buchstabe=s');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const firstBefore = await page.textContent('#entryGrid a >> nth=0');
        await page.click('#pagination button:has-text("2")');
        const firstAfter = await page.textContent('#entryGrid a >> nth=0');

        expect(firstAfter).not.toBe(firstBefore);
        expect(page.url()).toContain('seite=2');
    });

    test('URL-State wird beim Laden gelesen (Deep-Link)', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html?buchstabe=m&seite=2');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^M – /);
        const activePage = await page.textContent('#pagination button[disabled]:not(:has-text("Zurück")):not(:has-text("Weiter"))');
        expect(activePage).toBe('2');
    });

    test('Eintrag verlinkt auf die Lemma-Seite', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const href = await page.getAttribute('#entryGrid a >> nth=0', 'href');
        expect(href).toMatch(/^lemma\/\?id=\d+$/);
    });

    test('Nav-Link Wörterbuch ist auf der Startseite vorhanden', async ({ page }) => {
        await page.goto('http://localhost:8080/index.html');
        const navLink = page.locator('header a[data-nav="woerterbuch"]').first();
        await expect(navLink).toHaveText(/Wörterbuch/);
    });
});
```

- [ ] **Step 2: NICHT ausführen.** Christian fragen, ob `npm test` (oder gezielt nur diese Spec über die npm-Konfiguration) gestartet werden soll. Playwright-Läufe nie ungefragt.

---

### Task 6: Abschluss (CSS, Doku, manuelle Verifikation)

**Files:**
- Possibly modify: `assets/css/tailwind-output.css` (generiert)
- Modify: `docs/INDEX.md`, `docs/FEATURES.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md` (Doc-Count-Drift: neue Hauptseite)

- [ ] **Step 1: Tailwind-Rebuild** (neue Utility-Klassen wie `top-20`, `z-40`, `grid-cols-3`, `max-w-6xl` könnten im gepurgten Output fehlen)

Run: `npm run build:css`
Expected: Build ohne Fehler; `git diff --stat assets/css/tailwind-output.css` zeigt, ob sich etwas geändert hat.

- [ ] **Step 2: Dev-Server für Christians manuellen Test**

Run: `npm run serve`
Dann Christian Bescheid geben: `http://localhost:8080/woerterbuch.html` (Buchstabenwechsel, Pagination, #-Bucket, Deep-Link `?buchstabe=s&seite=3`, Klick auf ein Lemma).

- [ ] **Step 3: Doku nachziehen** — in `docs/INDEX.md` (Core Features → Main Site), `docs/FEATURES.md`, `docs/ARCHITECTURE.md` (Seitenliste), `docs/DESIGN.md` (falls Seiten aufgezählt) die neue Wörterbuch-Seite ergänzen. Kurze Einträge, gleicher Stil wie Nachbarpunkte.

- [ ] **Step 4: Nach Christians Freigabe — Sammelcommit** (gezielt stagen, NIE `-A`):

```bash
git add woerterbuch.html assets/js/woerterbuch.js includes/_nav.html scripts/build-pages.py \
  lemma/index.html lemma/lemma-page.js testing/tests/woerterbuch.spec.js \
  index.html korpus.html impressum.html barrierefreiheit.html hilfe.html hilfe-daten.html \
  hilfe-daten-beitragen.html hilfe-korpussuche.html hilfe-playground.html hilfe-schema.html \
  playground/index.html assets/css/tailwind-output.css \
  docs/INDEX.md docs/FEATURES.md docs/ARCHITECTURE.md docs/DESIGN.md \
  docs/features/117-woerterbuch-einstiegsseite.md docs/features/117-woerterbuch-plan.md
git commit -m "feat: #117 Wörterbuch-Einstiegsseite (A-Z-Register für Lemma-Seiten)

## Changes
- woerterbuch.html + assets/js/woerterbuch.js: A-Z-Register über den Authority-Index
  (Bucketing auf normalized, Pagination à 200, URL-State ?buchstabe=&seite=)
- Nav-Eintrag 'Wörterbuch' zwischen Playground und Hilfe (alle Seiten, build-injiziert)
- lemma/: Fehlerfall ohne ID verlinkt aufs Wörterbuch
- Playwright-Smoke-Tests (testing/tests/woerterbuch.spec.js)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 5: Nach dem Push** — @wachauer im Issue #117 anpingen (Live-URL `https://dhcraft.org/mhdbdb-tei-only/woerterbuch.html`, Test-Hinweise, Begründung der Namensentscheidung aus der Spec zitieren). Issue offen lassen bis ihr OK.

---

## Self-Review (erledigt)

- **Spec-Coverage:** Namensentscheidung → Untertitel + Issue-Kommentar (Task 2/6); Bucketing/NFD/`#` → Task 1; Indexleiste/Pagination/URL-State → Task 1/2; Nav-Reihenfolge → Task 3; lemma-Fehlerfall → Task 4; Abschlusskriterien → Task 5/6. Keine Lücken.
- **Platzhalter:** keine.
- **Konsistenz:** IDs (`letterBar`, `letterHeading`, `entryGrid`, `pagination`, `woerterbuchContent`, `errorDisplay`, `errorMessage`, Loading-Trio) stimmen zwischen Task 1 (JS), Task 2 (HTML) und Task 5 (Tests) überein; `data-nav="woerterbuch"` stimmt zwischen Task 3 und Task 5 überein; `CorpusLoader('data')` passt zum Root-Pfad der Seite.
