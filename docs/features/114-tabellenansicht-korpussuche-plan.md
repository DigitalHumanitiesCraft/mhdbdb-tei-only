# Issue #114: Tabellenansicht für Korpussuche — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Korpussuche-Ergebnisse als sortierbare Tabelle mit CSV-Export anzeigen, umschaltbar zwischen Listen- und Tabellen-Ansicht.

**Architecture:** Vanilla-JS-Erweiterung von `MainSiteApp` in `assets/js/app.js`. Zwei zusätzliche State-Properties (`viewMode`, `sortSpec`), Branching in `displayResults()`, neuer `renderTable()`-Pfad. Layout-Klassen-Wechsel auf `#mainGrid` schaltet das CSS-Grid für die Tabelle vollbreit. UI-Erweiterungen in `korpus.html`, CSS in `assets/css/korpus.css`.

**Tech Stack:** Vanilla JS ES6+, Tailwind v3 (Utility-First), Playwright für E2E-Tests. Keine neuen Dependencies.

**Spec-Referenz:** [`docs/features/114-tabellenansicht-korpussuche.md`](114-tabellenansicht-korpussuche.md) (Commit `dabfc601c`).

---

## File Structure Overview

```
assets/js/search/search-engine.js   # Task 1: wordCount-Propagation
assets/js/app.js                    # Tasks 2-10: State, Rendering, Handlers, Export
korpus.html                         # Tasks 2, 9: Toggle-UI, Export-Buttons
assets/css/korpus.css               # Tasks 3, 6: Layout-Override, Sticky-Header
testing/tests/results-table.spec.js # Task 11: NEUER Playwright-Spec
```

Bestehende Dateien werden **modifiziert**, nicht ersetzt. Die Listenansicht bleibt vollständig erhalten — Tabelle ist ein zusätzlicher Pfad in `displayResults()`.

---

## Task 1: wordCount-Propagation in der Search-Engine

**Files:**
- Modify: `assets/js/search/search-engine.js:97-105`
- Test: `testing/tests/search-engine.spec.js` (Augmentation eines bestehenden Tests oder neuer)

**Warum zuerst:** Voraussetzung für alle Frequenz-Berechnungen in der Tabelle. Ohne diese 1-Zeile fehlt `wordCount` im Result-Objekt und die Frequenz-Spalte würde `NaN` zeigen.

- [ ] **Step 1: Bestehenden search-engine.spec.js-Test ergänzen oder neuen Test schreiben, der `wordCount` im Result erwartet**

Datei: `testing/tests/search-engine.spec.js` (bestehend) — neuer Test ans Ende:

```js
test('search results include wordCount for frequency calculations', async ({ page }) => {
  await page.goto('/korpus.html');
  await page.waitForFunction(() => window._mhdbdbApp?.searchEngine !== null, { timeout: 30000 });

  await page.fill('#searchInput', 'minne');
  await page.click('#searchButton');
  await page.waitForSelector('#resultsList > *', { timeout: 5000 });

  const firstResultWordCount = await page.evaluate(() => {
    return window._mhdbdbApp.currentResults[0].wordCount;
  });

  expect(firstResultWordCount).toBeGreaterThan(0);
  expect(typeof firstResultWordCount).toBe('number');
});
```

- [ ] **Step 2: Test laufen lassen und Fehlschlag verifizieren**

Vorher User fragen: „Soll ich `npm test -- --grep 'wordCount for frequency'` laufen lassen?" (Memory-Regel: Playwright nicht ungefragt starten.)

Erwartet: FAIL — `firstResultWordCount` ist `undefined`.

- [ ] **Step 3: Search-Engine-Projektion ergänzen**

Datei: `assets/js/search/search-engine.js`, Zeilen 97-105 finden:

```js
// Vorher:
results.push({
    textId: text.id,
    lemmaId: lemmaId,
    title: text.title,
    author: this.getAuthorName(text.authorRef),
    genre: this.getGenre(text.workRef),
    matchCount: matchCount,
    snippet: snippet
});

// Nachher (eine neue Zeile vor `snippet`):
results.push({
    textId: text.id,
    lemmaId: lemmaId,
    title: text.title,
    author: this.getAuthorName(text.authorRef),
    genre: this.getGenre(text.workRef),
    matchCount: matchCount,
    wordCount: text.wordCount,
    snippet: snippet
});
```

Der Aggregations-Pfad in `app.js:454-464` reicht das automatisch per `...result`-Spread weiter — kein Eingriff dort nötig.

- [ ] **Step 4: Test erneut laufen lassen → PASS erwartet**

Vorher User fragen. Erwartet: PASS.

- [ ] **Step 5: Commit**

```bash
git add assets/js/search/search-engine.js testing/tests/search-engine.spec.js
git commit -m "$(cat <<'EOF'
feat(#114): wordCount in Search-Engine-Result-Projektion

Voraussetzung für die Frequenz-Spalte der Tabellenansicht (#114).
search-engine.js projizierte wordCount bisher nicht; im Corpus-Index
liegt es seit v4.0.0 als text.wordCount vor.

Aggregations-Pfad in app.js:454-464 reicht das automatisch per
Spread weiter, daher dort kein Eingriff.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: viewMode-State + Toggle-UI im Results-Header

**Files:**
- Modify: `assets/js/app.js` (Constructor + neue Methoden)
- Modify: `korpus.html` (Results-Header)

- [ ] **Step 1: Toggle-UI in `korpus.html` einfügen**

Den bestehenden Results-Header (`<h2>Suchergebnisse <span id="resultsCount">…</span></h2>`) finden und in ein flex-Container umwandeln:

```html
<!-- Vorher: -->
<h2 class="text-2xl font-bold text-slate-900">
  Suchergebnisse
  <span id="resultsCount" class="text-brand-600">(140 Texte gefunden)</span>
</h2>

<!-- Nachher: -->
<div class="flex items-center justify-between gap-4 mb-4">
  <h2 class="text-2xl font-bold text-slate-900">
    Suchergebnisse
    <span id="resultsCount" class="text-brand-600"></span>
  </h2>
  <div id="viewToggle" role="group" aria-label="Ergebnis-Ansicht wechseln" class="inline-flex rounded-lg border border-slate-200 bg-white p-0.5">
    <button type="button" id="viewToggleList" class="px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5" aria-pressed="true">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
      Liste
    </button>
    <button type="button" id="viewToggleTable" class="px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5" aria-pressed="false">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18M3 5h18a0 0 0 010 0v14a0 0 0 01-0 0H3a0 0 0 01-0-0V5a0 0 0 010-0z"/></svg>
      Tabelle
    </button>
  </div>
</div>
```

- [ ] **Step 2: State in `MainSiteApp`-Constructor ergänzen**

Datei: `assets/js/app.js`, im Constructor nach `this.resultsPerPage = 20;`:

```js
// Issue #114: View-Mode für Korpussuche-Ergebnisse
this.viewMode = this.loadViewMode();        // 'list' | 'table'
this.sortSpec = { column: 'matchCount', direction: 'desc' };  // Default, nicht persistiert
```

Und neue Methoden auf der Klasse (z.B. nach `displayResults()`):

```js
loadViewMode() {
  const stored = localStorage.getItem('mhdbdb-results-view');
  return (stored === 'table' || stored === 'list') ? stored : 'list';
}

setViewMode(mode) {
  if (mode !== 'list' && mode !== 'table') return;
  this.viewMode = mode;
  localStorage.setItem('mhdbdb-results-view', mode);
  this.updateViewToggleUI();
  // Re-render ohne neue Suche
  if (this.currentResults.length > 0) {
    this.displayResults();
  }
}

updateViewToggleUI() {
  const listBtn = document.getElementById('viewToggleList');
  const tableBtn = document.getElementById('viewToggleTable');
  if (!listBtn || !tableBtn) return;

  const active = 'bg-brand-600 text-white';
  const inactive = 'text-slate-600 hover:bg-slate-50';

  listBtn.className = `px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5 ${this.viewMode === 'list' ? active : inactive}`;
  tableBtn.className = `px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5 ${this.viewMode === 'table' ? active : inactive}`;
  listBtn.setAttribute('aria-pressed', this.viewMode === 'list');
  tableBtn.setAttribute('aria-pressed', this.viewMode === 'table');
}
```

- [ ] **Step 3: Click-Handler im `init()`/`bindEvents()`-Bereich ergänzen**

Datei: `assets/js/app.js`, in der bestehenden Event-Wiring-Methode (typischerweise `bindEvents()` oder `init()`):

```js
document.getElementById('viewToggleList')?.addEventListener('click', () => this.setViewMode('list'));
document.getElementById('viewToggleTable')?.addEventListener('click', () => this.setViewMode('table'));

// Initial UI-State setzen
this.updateViewToggleUI();
```

- [ ] **Step 4: Manuell verifizieren im Dev-Server**

Vorher User fragen, ob Dev-Server-Restart nötig (BG-Task `bjq9bqyew` läuft).

Schritte:
1. Browser → http://localhost:8080/korpus.html
2. Search „minne" → Toggle-Buttons sichtbar
3. Klick „Tabelle" → aktiver Button hervorgehoben, localStorage hat `mhdbdb-results-view: "table"`
4. Page reload → Tabelle bleibt aktiv

Toggle macht aktuell **noch keine Render-Änderung** (`displayResults()` weiß noch nichts vom Mode) — nur der UI-State persistiert. Das ist OK für diesen Task.

- [ ] **Step 5: Commit**

```bash
git add assets/js/app.js korpus.html
git commit -m "$(cat <<'EOF'
feat(#114): viewMode-State + Toggle-UI für Korpussuche

Segmented-Control Liste/Tabelle im Results-Header. Wahl persistiert
in localStorage unter 'mhdbdb-results-view'. Toggle re-rendert noch
nicht — folgt in Task 3 (Layout-Switch) + Task 5 (Tabellen-Renderer).

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Layout-Override + displayResults-Branching

**Files:**
- Modify: `assets/css/korpus.css`
- Modify: `assets/js/app.js` (`displayResults()`)

- [ ] **Step 1: CSS-Override-Klasse hinzufügen**

Datei: `assets/css/korpus.css`, am Ende anhängen:

```css
/*
 * Issue #114: Tabellen-Modus überlagert das 3-Spalten-Layout
 * mit voller Breite, damit die Tabelle bei kleineren Viewports
 * (1280-1920px) nicht in eine ~300-460px-schmale Results-Spalte
 * gequetscht wird.
 */
#mainGrid.table-layout {
  grid-template-columns: 1fr !important;
}

#mainGrid.table-layout > .search-sidebar {
  /* Sidebar belegt volle Breite oberhalb der Tabelle, collapsed-by-default */
  max-height: 4rem;
  overflow: hidden;
  transition: max-height 0.2s ease;
}

#mainGrid.table-layout > .search-sidebar.expanded {
  max-height: none;
}
```

**Anmerkung:** Die Klassennamen `search-sidebar` müssen in `korpus.html` an die tatsächliche Sidebar vergeben werden, falls sie noch keine spezifische Klasse hat. Falls die Sidebar bereits eine eindeutige ID oder Klasse hat, diese stattdessen verwenden.

- [ ] **Step 2: `displayResults()` um Layout-Switch + Mode-Branching erweitern**

Datei: `assets/js/app.js`, Methode `displayResults()` (ab Zeile 539).

Vor `this.elements.resultsList.innerHTML = '';` einfügen:

```js
// Issue #114: Layout je nach View-Mode wechseln
const mainGrid = document.getElementById('mainGrid');
if (mainGrid) {
  if (this.viewMode === 'table') {
    mainGrid.classList.add('table-layout');
    mainGrid.classList.remove('three-column', 'two-column');
  } else {
    mainGrid.classList.add('three-column');
    mainGrid.classList.remove('table-layout', 'two-column');
  }
}
```

Und in `loadMoreResults()` keine Änderung — das ist der Listen-Pfad. Stattdessen ersetzt das Mode-Branching die direkten Card-Calls:

```js
// Display first page (Listen-Mode) ODER ganze Tabelle (Tabellen-Mode)
if (this.viewMode === 'table') {
  this.renderTable();
} else {
  this.loadMoreResults();
}
```

`renderTable()` selbst kommt in Task 5 — vorerst Stub:

```js
renderTable() {
  this.elements.resultsList.innerHTML = '<p class="text-slate-500">Tabelle (Task 5)</p>';
}
```

- [ ] **Step 3: Manuell verifizieren**

1. Browser → `/korpus.html`, Search „minne"
2. Klick „Tabelle" → Layout wechselt auf vollbreite Spalte mit dem Stub-Text
3. Klick „Liste" → Listenansicht zurück, 3-Spalten-Layout

- [ ] **Step 4: Commit**

```bash
git add assets/js/app.js assets/css/korpus.css
git commit -m "$(cat <<'EOF'
feat(#114): Layout-Override + displayResults-Branching

Tabellen-Mode setzt .table-layout-Klasse auf #mainGrid und
überschreibt grid-template-columns auf 1fr. displayResults()
branched auf renderTable() (Stub) oder loadMoreResults().

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: sortSpec-Reset + sortResults-Helper

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: `sortResults`-Helper als Klassen-Methode**

Datei: `assets/js/app.js`, neue Methode:

```js
/**
 * Issue #114: Sortiert this.currentResults in-place gemäß sortSpec.
 * Comparators sind reine Funktionen — Frequenz wird on-the-fly aus
 * matchCount und wordCount berechnet.
 */
sortResults() {
  const { column, direction } = this.sortSpec;
  const dir = direction === 'asc' ? 1 : -1;

  const valueGetter = {
    title: (r) => (r.title || '').toLowerCase(),
    author: (r) => (r.author || '￿').toLowerCase(),  // Unbekannte ans Ende
    matchCount: (r) => r.matchCount || 0,
    wordCount: (r) => r.wordCount || 0,
    frequency: (r) => (r.wordCount > 0) ? (r.matchCount / r.wordCount) * 10000 : -Infinity,
  }[column];

  if (!valueGetter) return;

  this.currentResults.sort((a, b) => {
    const va = valueGetter(a);
    const vb = valueGetter(b);
    if (typeof va === 'string') return va.localeCompare(vb, 'de') * dir;
    return (va - vb) * dir;
  });
}
```

- [ ] **Step 2: Sort-Reset bei neuer Suche**

In der Such-Methode (Suche nach `this.currentResults = ` in `app.js`, vermutlich um Zeile 466), unmittelbar danach:

```js
this.currentResults = Array.from(textMap.values());
this.currentPage = 0;

// Issue #114: Sort-Spec bei neuer Suche auf Default zurück
this.sortSpec = { column: 'matchCount', direction: 'desc' };
this.sortResults();
```

`sortResults()` ist hier idempotent — sortiert den Default-Stand `matchCount desc`, der zwar vom Search-Engine schon kommt, aber expliziter sortResults-Call macht den Pfad einheitlich.

- [ ] **Step 3: Manuell verifizieren**

Console-Test in DevTools:
```js
const app = window._mhdbdbApp;
app.sortSpec = { column: 'title', direction: 'asc' };
app.sortResults();
app.currentResults.slice(0, 5).map(r => r.title);
// Erwartet: alphabetisch aufsteigend
```

- [ ] **Step 4: Commit**

```bash
git add assets/js/app.js
git commit -m "$(cat <<'EOF'
feat(#114): sortSpec-State + sortResults-Helper

Comparators für alle 5 Tabellen-Spalten (Titel/Autor/Treffer/
Wörter/Frequenz). Neue Suche resetet sortSpec auf Default
Treffer ↓. Frequenz on-the-fly aus matchCount/wordCount;
0-wordCount → -Infinity (rutscht bei desc ans Ende).

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: renderTable-Implementation

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: Vollständige `renderTable()`-Methode**

Datei: `assets/js/app.js`, den Stub aus Task 3 ersetzen:

```js
/**
 * Issue #114: Rendert die Tabellen-Ansicht der Suchergebnisse.
 * 5 Spalten: Titel (mit Sigle-Präfix), Autor*in, Treffer, Frequenz/10k, Wörter.
 * Header sind klickbare Sort-Buttons; Zeilen-Klick öffnet den Reader.
 */
renderTable() {
  const { column, direction } = this.sortSpec;
  const sortIcon = (col) => col === column ? (direction === 'asc' ? '↑' : '↓') : '↕';
  const ariaSort = (col) => col === column ? (direction === 'asc' ? 'ascending' : 'descending') : 'none';

  const headerCell = (col, label, alignClass = '') => `
    <th scope="col" aria-sort="${ariaSort(col)}" class="results-table-th ${alignClass}" style="position: sticky; top: 0; background: #f8fafc; z-index: 10;">
      <button type="button" data-sort-col="${col}" class="results-table-sort-btn">
        ${this.escapeHtml(label)} <span class="text-xs text-slate-400">${sortIcon(col)}</span>
      </button>
    </th>
  `;

  const rows = this.currentResults.map(r => {
    const freq = (r.wordCount > 0)
      ? ((r.matchCount / r.wordCount) * 10000).toFixed(1)
      : '–';
    const wordsFmt = r.wordCount ? r.wordCount.toLocaleString('de-DE') : '–';
    const matchesFmt = r.matchCount.toLocaleString('de-DE');
    return `
      <tr data-text-id="${this.escapeHtml(r.textId)}" tabindex="0" role="button" class="results-table-row hover:bg-slate-50 cursor-pointer">
        <td class="results-table-td">
          <span class="font-mono text-xs text-brand-600 mr-1">${this.escapeHtml(r.textId)}</span>
          <span>${this.escapeHtml(r.title)}</span>
        </td>
        <td class="results-table-td">${this.escapeHtml(r.author || '–')}</td>
        <td class="results-table-td text-right tabular-nums">${matchesFmt}</td>
        <td class="results-table-td text-right tabular-nums">${freq}</td>
        <td class="results-table-td text-right tabular-nums text-slate-500">${wordsFmt}</td>
      </tr>
    `;
  }).join('');

  const html = `
    <div class="mb-3 flex items-center justify-between gap-3">
      <p class="text-sm text-slate-500">Klick auf Spalten-Header sortiert. Klick auf Zeile öffnet den Text.</p>
      <div class="flex gap-2" id="resultsExportButtons">
        <button type="button" id="resultsCopyBtn" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-slate-50">📋 Kopieren</button>
        <button type="button" id="resultsDownloadBtn" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-slate-50">⬇ CSV</button>
      </div>
    </div>
    <div class="overflow-y-auto rounded-2xl border border-slate-200 bg-white" style="max-height: calc(100vh - 280px);">
      <table class="w-full text-sm">
        <thead>
          <tr>
            ${headerCell('title', 'Titel', 'text-left')}
            ${headerCell('author', 'Autor*in', 'text-left')}
            ${headerCell('matchCount', 'Treffer', 'text-right')}
            ${headerCell('frequency', 'Freq./10k W.', 'text-right')}
            ${headerCell('wordCount', 'Wörter', 'text-right')}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;

  this.elements.resultsList.innerHTML = html;

  // Load-More-Button verstecken (gehört zur Liste)
  this.elements.loadMoreContainer?.classList.add('hidden');

  // Event-Handler binden — Sort, Row-Click, Export (Tasks 7-10 füllen)
  this.bindTableEvents();
}

bindTableEvents() {
  // Sort-Header
  this.elements.resultsList.querySelectorAll('[data-sort-col]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.handleSortClick(btn.dataset.sortCol);
    });
  });

  // Row-Klick → Reader (Task 8 erweitert)
  this.elements.resultsList.querySelectorAll('.results-table-row').forEach(row => {
    row.addEventListener('click', () => this.handleTableRowClick(row.dataset.textId));
    row.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.handleTableRowClick(row.dataset.textId);
      }
    });
  });

  // Export-Buttons (Tasks 9-10 erweitern)
  document.getElementById('resultsCopyBtn')?.addEventListener('click', () => this.copyResultsToClipboard());
  document.getElementById('resultsDownloadBtn')?.addEventListener('click', () => this.downloadResultsAsCSV());
}

// Stubs — werden in Tasks 7, 8, 9, 10 implementiert
handleSortClick(column) { console.log('[Task 7] sort', column); }
handleTableRowClick(textId) { console.log('[Task 8] open reader for', textId); }
copyResultsToClipboard() { console.log('[Task 9] copy TSV'); }
downloadResultsAsCSV() { console.log('[Task 10] download CSV'); }
```

- [ ] **Step 2: Tabellen-CSS in `korpus.css` ergänzen**

```css
/* Issue #114: Tabellen-Styles */
.results-table-th {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(51 65 85);  /* slate-700 */
  border-bottom: 1px solid rgb(226 232 240);  /* slate-200 */
}

.results-table-sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  color: inherit;
  padding: 0;
}

.results-table-sort-btn:hover {
  color: rgb(37 99 235);  /* brand-600 */
}

.results-table-td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid rgb(241 245 249);  /* slate-100 */
  vertical-align: top;
}

.results-table-row:focus {
  outline: 2px solid rgb(37 99 235);
  outline-offset: -2px;
}

.results-table-row:last-child .results-table-td {
  border-bottom: none;
}
```

- [ ] **Step 3: Manuell verifizieren**

1. Browser → `/korpus.html`, Search „minne", Klick „Tabelle"
2. Tabelle erscheint, 140 Zeilen, sortiert nach Treffer ↓
3. Sigle als monospace-Präfix vor Titel sichtbar
4. Export-Buttons sichtbar
5. Klick auf Header → Console-Log „[Task 7] sort title" etc.
6. Klick auf Zeile → Console-Log „[Task 8] open reader for JT" etc.

- [ ] **Step 4: Commit**

```bash
git add assets/js/app.js assets/css/korpus.css
git commit -m "$(cat <<'EOF'
feat(#114): renderTable mit 5 Spalten + Stub-Handlern

Vollständiges Tabellen-Markup (Titel+Sigle / Autor*in / Treffer /
Freq. / Wörter), sticky-Header per <th>, Number-Formatting mit
de-DE-Locale, Export-Buttons. Sort-, Row-Click- und Export-Handler
sind Stubs, werden in Tasks 7-10 vervollständigt.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Sortier-Verhalten + visuelle Indikatoren

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: `handleSortClick` ausimplementieren**

Den Stub aus Task 5 ersetzen:

```js
handleSortClick(column) {
  if (this.sortSpec.column === column) {
    // Re-Klick toggelt direction
    this.sortSpec.direction = this.sortSpec.direction === 'asc' ? 'desc' : 'asc';
  } else {
    // Neue Spalte → desc als initial
    this.sortSpec = { column, direction: 'desc' };
  }
  this.sortResults();
  this.renderTable();  // Re-render mit neuer Sortierung + aktualisierten Sort-Icons
}
```

- [ ] **Step 2: Manuell verifizieren**

1. Tabelle anzeigen, Search „minne"
2. Klick auf „Titel" → alphabetisch desc (Z→A), Icon ↓ am Titel-Header
3. Re-Klick auf „Titel" → alphabetisch asc, Icon ↑
4. Klick auf „Treffer" → numerisch desc, ↓ wechselt zur Treffer-Spalte, andere Header zeigen ↕
5. Klick auf „Freq./10k W." → Texte mit hoher Frequenz oben

- [ ] **Step 3: Commit**

```bash
git add assets/js/app.js
git commit -m "$(cat <<'EOF'
feat(#114): Sort-Handler für Tabellen-Header

Re-Klick toggelt direction, neue Spalte → desc als initial.
Re-Render aktualisiert sort-Icons (↑↓↕) und aria-sort-Attribute.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Row-Click → Reader

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: `handleTableRowClick` ausimplementieren**

Den Stub aus Task 5 ersetzen:

```js
handleTableRowClick(textId) {
  // Result aus currentResults für die lemmaIds finden
  const result = this.currentResults.find(r => r.textId === textId);
  if (!result) return;

  const lemmaIds = result.lemmaIds || [result.lemmaId];

  // Issue #114: Vor Reader-Öffnen zurück auf Listen-Modus wechseln,
  // damit das 3-Spalten-Layout (mit Reader-Slot) wieder greift.
  // localStorage bleibt auf 'table' — beim Reader-Schließen erwartet
  // der User die Tabelle zurück; eine Lösung dafür liegt außerhalb dieses
  // MVPs und ist im Spec als Out-of-Scope dokumentiert.
  if (this.viewMode === 'table') {
    this.viewMode = 'list';
    // localStorage NICHT überschreiben — User-Präferenz bleibt 'table'
    this.updateViewToggleUI();
    this.displayResults();
  }

  this.teiReader.openReadingView(textId, { lemmaIds }, this.elements);
}
```

- [ ] **Step 2: Manuell verifizieren**

1. Tabelle aktiv, Search „minne"
2. Klick auf eine Zeile (z.B. JT)
3. Layout wechselt auf 3-Spalten-Liste, Reader öffnet sich rechts
4. localStorage-Wert `mhdbdb-results-view` ist weiterhin `'table'`
5. Reader schließen → Listenansicht bleibt (Spec: User wechselt manuell zurück)

- [ ] **Step 3: Commit**

```bash
git add assets/js/app.js
git commit -m "$(cat <<'EOF'
feat(#114): Row-Click in Tabelle öffnet Reader

Wechselt auf Listen-Modus zurück (damit 3-Spalten-Layout mit
Reader-Slot greift), öffnet Reader analog Card-Click in der
Listenansicht. localStorage-Wert bleibt 'table' — User-Präferenz
nicht überschreiben.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: TSV-Clipboard-Export

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: `copyResultsToClipboard` ausimplementieren**

Den Stub aus Task 5 ersetzen, plus Helper:

```js
/**
 * Issue #114: Serialisiert this.currentResults im TSV-Format.
 * Reihenfolge respektiert aktuelle Sortierung.
 */
serializeResultsAsTSV() {
  const header = ['Sigle', 'Titel', 'Autor*in', 'Treffer', 'Frequenz/10k', 'Wörter'].join('\t');
  const rows = this.currentResults.map(r => {
    const freq = (r.wordCount > 0) ? ((r.matchCount / r.wordCount) * 10000).toFixed(1) : '';
    return [
      r.textId,
      (r.title || '').replace(/[\t\n\r]/g, ' '),  // TSV-Killer aus dem Titel filtern
      (r.author || '').replace(/[\t\n\r]/g, ' '),
      r.matchCount,
      freq,
      r.wordCount || ''
    ].join('\t');
  });
  return [header, ...rows].join('\n');
}

async copyResultsToClipboard() {
  const btn = document.getElementById('resultsCopyBtn');
  const originalText = btn?.textContent;
  try {
    const tsv = this.serializeResultsAsTSV();
    await navigator.clipboard.writeText(tsv);
    if (btn) {
      btn.textContent = '✓ Kopiert';
      setTimeout(() => { btn.textContent = originalText; }, 2000);
    }
  } catch (err) {
    console.error('[MainSiteApp] Clipboard write failed:', err);
    if (btn) {
      btn.textContent = '✗ Fehler';
      setTimeout(() => { btn.textContent = originalText; }, 2000);
    }
  }
}
```

- [ ] **Step 2: Manuell verifizieren**

1. Tabelle aktiv, Search „minne", auf Frequenz sortieren
2. Klick „📋 Kopieren" → Button zeigt „✓ Kopiert" für 2s
3. In Excel oder LibreOffice einfügen → 6 Spalten korrekt, Sortierung erhalten

- [ ] **Step 3: Commit**

```bash
git add assets/js/app.js
git commit -m "$(cat <<'EOF'
feat(#114): TSV-Clipboard-Export der Tabellen-Ergebnisse

navigator.clipboard.writeText mit TSV-Serialisierung. Tab/Newline
aus Titel/Autor gefiltert (defensiv — typischerweise sauber).
Button-Feedback ✓/✗ für 2s.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: CSV-Download

**Files:**
- Modify: `assets/js/app.js`

- [ ] **Step 1: `downloadResultsAsCSV` + Helpers ausimplementieren**

```js
/**
 * Issue #114: CSV-Cell-Quoting nach RFC 4180 / Excel-Konvention.
 * Wenn der Wert Komma, Quote oder Newline enthält: in "..." einfassen
 * und enthaltene Quotes verdoppeln.
 */
escapeCsvCell(value) {
  const str = String(value ?? '');
  if (/[",\n\r]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

serializeResultsAsCSV() {
  const header = ['Sigle', 'Titel', 'Autor*in', 'Treffer', 'Frequenz/10k', 'Wörter']
    .map(c => this.escapeCsvCell(c))
    .join(',');
  const rows = this.currentResults.map(r => {
    const freq = (r.wordCount > 0) ? ((r.matchCount / r.wordCount) * 10000).toFixed(1) : '';
    return [
      r.textId,
      r.title || '',
      r.author || '',
      r.matchCount,
      freq,
      r.wordCount || ''
    ].map(c => this.escapeCsvCell(c)).join(',');
  });
  return [header, ...rows].join('\r\n');  // CRLF für Excel-Kompatibilität
}

downloadResultsAsCSV() {
  const lemma = this.elements.searchInput?.value?.trim() || 'suche';
  const safeLemma = lemma.replace(/[^a-zA-Z0-9äöüÄÖÜß-]/g, '_').slice(0, 40);
  const today = new Date().toISOString().slice(0, 10);
  const filename = `mhdbdb-suche-${safeLemma}-${today}.csv`;

  // UTF-8 BOM (﻿) für Excel-Kompatibilität
  const csv = '﻿' + this.serializeResultsAsCSV();
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

- [ ] **Step 2: Manuell verifizieren**

1. Tabelle aktiv, Search „minne"
2. Klick „⬇ CSV" → Datei `mhdbdb-suche-minne-2026-05-28.csv` lädt herunter
3. In Excel öffnen → 6 Spalten, Umlaute korrekt (BOM), Sortierung erhalten
4. Titel mit Komma/Quote → korrekt gequotet

- [ ] **Step 3: Commit**

```bash
git add assets/js/app.js
git commit -m "$(cat <<'EOF'
feat(#114): CSV-Download mit Excel-Kompatibilität

Blob + URL.createObjectURL + a[download]-Trick. UTF-8-BOM voran
für Excel-Umlaute. RFC-4180-konformes Quoting (Komma, Quote,
Newline). Dateiname mhdbdb-suche-<lemma>-<YYYY-MM-DD>.csv.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Playwright-Spec für die ganze Feature

**Files:**
- Create: `testing/tests/results-table.spec.js`

- [ ] **Step 1: Spec-Datei anlegen**

```js
// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Issue #114: Tabellenansicht für Korpussuche', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/korpus.html');
    await page.waitForFunction(() => window._mhdbdbApp?.searchEngine !== null, { timeout: 30000 });
  });

  test('Toggle UI ist sichtbar nach Suche', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');
    await expect(page.locator('#viewToggleList')).toBeVisible();
    await expect(page.locator('#viewToggleTable')).toBeVisible();
  });

  test('Toggle Liste → Tabelle wechselt das Rendering', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');

    // Initial: Listenansicht (Cards)
    await expect(page.locator('#resultsList table')).toHaveCount(0);

    // Toggle
    await page.click('#viewToggleTable');
    await expect(page.locator('#resultsList table')).toHaveCount(1);
    await expect(page.locator('#resultsList table tbody tr')).toHaveCount(140);  // 140 für "minne" — anpassen falls Korpus wächst
  });

  test('localStorage persistiert View-Wahl über Reload', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');
    await page.click('#viewToggleTable');

    // Reload + erneut suchen
    await page.reload();
    await page.waitForFunction(() => window._mhdbdbApp?.searchEngine !== null);
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');

    await expect(page.locator('#resultsList table')).toHaveCount(1);
  });

  test('Sortierung per Header-Klick funktioniert', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');
    await page.click('#viewToggleTable');
    await page.waitForSelector('#resultsList table');

    // Default: matchCount desc — JT (612 Treffer) sollte oben sein
    const firstRowSigle = await page.locator('#resultsList tbody tr').first().locator('.font-mono').textContent();
    expect(firstRowSigle).toMatch(/JT|jt/);

    // Klick Titel-Header → alphabetisch desc
    await page.click('button[data-sort-col="title"]');
    const titlesAfterSort = await page.locator('#resultsList tbody tr td:first-child').allTextContents();
    const sortedDesc = [...titlesAfterSort].sort((a, b) => b.localeCompare(a, 'de'));
    expect(titlesAfterSort.slice(0, 5)).toEqual(sortedDesc.slice(0, 5));
  });

  test('Row-Klick öffnet Reader + wechselt auf Listen-Modus', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');
    await page.click('#viewToggleTable');
    await page.waitForSelector('#resultsList table');

    await page.click('#resultsList tbody tr:first-child');

    // Reader öffnet sich (Reader-spezifischer Selector — anpassen falls anders im DOM)
    await expect(page.locator('#readerSection, [data-reader]')).toBeVisible({ timeout: 5000 });
    // View-Mode auf list zurück
    const viewMode = await page.evaluate(() => window._mhdbdbApp.viewMode);
    expect(viewMode).toBe('list');
  });

  test('CSV-Download wird angeboten', async ({ page }) => {
    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > *');
    await page.click('#viewToggleTable');

    const downloadPromise = page.waitForEvent('download');
    await page.click('#resultsDownloadBtn');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^mhdbdb-suche-minne-\d{4}-\d{2}-\d{2}\.csv$/);
  });
});
```

- [ ] **Step 2: Tests laufen lassen**

User vorher fragen: „Soll ich `npm test -- testing/tests/results-table.spec.js` laufen lassen?"

Erwartet: alle 6 Tests PASS.

Falls Fehler:
- Selector-Mismatch (z.B. Reader-Section anders im DOM) → Selector in Test korrigieren
- Treffer-Anzahl für „minne" hat sich verändert → Zahl 140 im Test aktualisieren

- [ ] **Step 3: Commit**

```bash
git add testing/tests/results-table.spec.js
git commit -m "$(cat <<'EOF'
test(#114): Playwright-Spec für Tabellenansicht

6 Tests: Toggle-UI, Render-Wechsel, localStorage-Persistenz,
Sortierung, Row-Klick + Mode-Wechsel, CSV-Download-Event.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Issue-Comment + Push

**Files:** keine — nur Git + GitHub.

- [ ] **Step 1: Alle Commits push**

```bash
git push origin main
```

- [ ] **Step 2: #114-Comment mit Closing-Vorschlag**

```bash
gh issue comment 114 --body "Implementation fertig + getestet (`<commit-sha>`). Live nach Pages-Deploy. Bitte kurzen Check, dann gerne schließen."
```

- [ ] **Step 3: Manuell verifizieren auf Production (nach Pages-Deploy)**

1. https://dhcraft.org/mhdbdb-tei-only/korpus.html
2. Search „minne" → Toggle „Tabelle" → CSV-Download → in Excel öffnen
3. Falls OK: Issue schließen mit Closing-Comment

---

## Self-Review-Notizen

**Spec-Coverage:**
- [x] 5 Spalten mit Titel+Sigle-Präfix → Task 5
- [x] Sortierung Default Treffer ↓, klickbar, asc/desc-Toggle → Task 4 + 6
- [x] Sort überlebt View-Toggle (sortSpec auf MainSiteApp, nicht resetet im setViewMode) → Task 2 (implizit, sortSpec lebt auf der App nicht im Toggle)
- [x] Toggle Liste/Tabelle in `localStorage` → Task 2
- [x] Pagination: alle auf einmal (kein Load-More im Tabellen-Pfad) → Task 5 (verstecken Load-More via `add('hidden')`)
- [x] Export TSV-Clipboard + CSV-Download → Tasks 8 + 9
- [x] Layout-Mode-Wechsel `three-column` ↔ `table-layout` → Task 3
- [x] Row-Klick → Reader (mit Auto-Wechsel auf Listen-Modus) → Task 7
- [x] Sticky-Header per `<th>`, scrollbarer Container, `z-index` → Task 5 (inline + CSS)
- [x] wordCount-Propagation in Search-Engine → Task 1
- [x] Playwright-Spec → Task 10

**Risk-Coverage:**
- [x] Clipboard-API auf HTTP → Task 8 zeigt graceful fallback bei Failure
- [x] Layout-Klassen-Mutation auf `#mainGrid` → Task 3 doc-Kommentar nennt die Klassen-Konflikt-Möglichkeit
- [x] Reader-Öffnen aus Tabelle → Task 7 dokumentiert Mode-Switch explizit

**Placeholder-Scan:**
- Alle `console.log`-Stubs in Task 5 werden in Tasks 6-9 durch echte Implementations ersetzt — explizit gekennzeichnet.
- Keine TBD/TODO/„später ergänzen"-Vermerke.

**Type-Consistency:**
- `viewMode`: `'list' | 'table'` durchgängig
- `sortSpec`: `{ column, direction }` mit `direction: 'asc' | 'desc'` durchgängig
- `currentResults`-Shape: nach Task 1 mit `wordCount`, danach konsistent in allen Tasks
- Methoden-Namen: `setViewMode`, `loadViewMode`, `updateViewToggleUI`, `renderTable`, `sortResults`, `handleSortClick`, `handleTableRowClick`, `bindTableEvents`, `copyResultsToClipboard`, `serializeResultsAsTSV`, `serializeResultsAsCSV`, `escapeCsvCell`, `downloadResultsAsCSV` — keine Namens-Drift zwischen Tasks.

**Offene Annahmen, die der Implementer prüfen muss:**
- Existing `escapeHtml`-Methode auf `MainSiteApp` — wird in `renderTable` benutzt. Falls sie nicht existiert: Helper-Implementation ergänzen (Standard-Pattern: `String(s).replace(/[&<>"']/g, …)`)
- `this.elements.loadMoreContainer` muss existieren (laut Code-Read in Spec ja). Falls Render-Reihenfolge das versteckt-machen nicht greift: defensive `?.classList.add('hidden')` mit Optional-Chaining ist im Plan schon dort.
- Sidebar-Klassennamen in Task 3 CSS (`.search-sidebar`) — Implementer muss die echte Klasse/ID in `korpus.html` finden und entsprechend anpassen.
