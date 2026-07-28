/**
 * Main Site Application Controller
 * Manages both landing page (index.html) and search page (korpus.html)
 * - index.html: Stats display only (no search)
 * - korpus.html: Full search functionality
 */

import { CorpusLoader } from './lib/corpus-loader.js';
import { TextNormalizer } from './lib/text-normalizer.js';
import { escapeHtml } from './lib/escape.js';
import { fetchWbnetzEntries, decodeHtmlEntities } from './lib/woerterbuchnetz.js';
import { SearchEngine } from './search/search-engine.js';
import { extractKwicHits, formatLineRef } from './search/kwic-service.js';
import { TEICacheManager } from './storage/tei-cache-manager.js';
import { TEITextReader } from './rendering/tei-text-reader.js';

/**
 * Issue #160: Deklaratives Spaltenmodell der Ergebnis-Tabelle (#114/#129).
 *
 * SINGLE SOURCE OF TRUTH für Spalten-Reihenfolge, Header-Labels, Alignment,
 * Sortierung, Zellen-Rendering, Gesamtzeile und TSV/CSV-Export. Vorher lebte
 * dieses Wissen an sieben Stellen in app.js (Header, Zeilen, Keyness-Zelle,
 * tfoot, sortResults, TSV- und CSV-Export) plus einem hartcodierten
 * KWIC-colspan — jede Spaltenänderung musste alle synchron treffen.
 *
 * Feld-Referenz je Spalte:
 *   key          Sort-Key (data-sort-col); null = nicht sortierbar (Belege)
 *   label        Header-Beschriftung der Tabelle
 *   headerAlign  Alignment-Klasse des <th>
 *   cellClass    Zusatzklassen der <td> (results-table-td ist immer gesetzt)
 *   cell(r, app) HTML-INHALT der <td> (bereits escaped)
 *   tdHtml(r, app) alternativ: komplette <td> (Keyness: bedingte Klassen/Titel)
 *   sortValue(r) Wert für den Comparator (string → localeCompare 'de')
 *   exportFields Liste {label, value(r)} — eine Tabellen-Spalte kann in
 *                mehrere Export-Felder aufgehen (Titel → Sigle + Titel)
 *                oder in keines (Belege-Button)
 *   totalColspan / totalSkip / totalClass / totalCell(totals)
 *                Bausteine der tfoot-Gesamtzeile; totalSkip markiert Spalten,
 *                die vom colspan des Vorgängers abgedeckt sind
 */
const RESULT_TABLE_COLUMNS = [
    {
        key: 'title',
        label: 'Titel',
        headerAlign: 'text-left',
        cell: (r) => `<span class="font-mono text-xs text-brand-600 mr-1">${escapeHtml(r.textId)}</span><span>${escapeHtml(r.title)}</span>`,
        sortValue: (r) => (r.title || '').toLowerCase(),
        exportFields: [
            { label: 'Sigle', value: (r) => r.textId },
            { label: 'Titel', value: (r) => r.title || '' },
        ],
        totalColspan: 2,
        totalClass: 'font-semibold',
        totalCell: (t) => `Gesamt (${t.count} Texte)`,
    },
    {
        key: 'author',
        label: 'Autor*in',
        headerAlign: 'text-left',
        cell: (r) => escapeHtml(r.author || '–'),
        // Unbekannte ans Ende (U+FFFF, höchster BMP-Codepoint)
        sortValue: (r) => (r.author || '￿').toLowerCase(),
        exportFields: [{ label: 'Autor*in', value: (r) => r.author || '' }],
        totalSkip: true, // vom colspan der Titel-Spalte abgedeckt
    },
    {
        key: 'matchCount',
        label: 'Treffer',
        headerAlign: 'text-right',
        cellClass: 'text-right tabular-nums',
        cell: (r) => r.matchCount.toLocaleString('de-DE'),
        sortValue: (r) => r.matchCount || 0,
        exportFields: [{ label: 'Treffer', value: (r) => r.matchCount }],
        totalClass: 'text-right tabular-nums font-semibold',
        totalCell: (t) => t.matches.toLocaleString('de-DE'),
    },
    {
        key: 'frequency',
        label: 'Freq./10k W.',
        headerAlign: 'text-right',
        cellClass: 'text-right tabular-nums',
        cell: (r) => (r.wordCount > 0) ? ((r.matchCount / r.wordCount) * 10000).toFixed(1) : '–',
        sortValue: (r) => (r.wordCount > 0) ? (r.matchCount / r.wordCount) * 10000 : -Infinity,
        exportFields: [{ label: 'Frequenz/10k', value: (r) => (r.wordCount > 0) ? ((r.matchCount / r.wordCount) * 10000).toFixed(1) : '' }],
        totalClass: 'text-right tabular-nums font-semibold',
        totalCell: (t) => t.freq,
    },
    {
        key: 'keyness',
        label: 'Keyness (LL)',
        headerAlign: 'text-right',
        // Bedingte Klassen + title-Attribut (Signifikanz ≥ 10,83) → komplette td
        tdHtml: (r, app) => app.formatKeynessCell(r.keyness),
        sortValue: (r) => (typeof r.keyness === 'number') ? r.keyness : -Infinity,
        exportFields: [{ label: 'Keyness (LL)', value: (r) => (typeof r.keyness === 'number') ? r.keyness.toFixed(1) : '' }],
    },
    {
        key: 'wordCount',
        label: 'Wörter',
        headerAlign: 'text-right',
        cellClass: 'text-right tabular-nums text-slate-500',
        cell: (r) => r.wordCount ? r.wordCount.toLocaleString('de-DE') : '–',
        sortValue: (r) => r.wordCount || 0,
        exportFields: [{ label: 'Wörter', value: (r) => r.wordCount || '' }],
        totalClass: 'text-right tabular-nums font-semibold text-slate-600',
        totalCell: (t) => t.words.toLocaleString('de-DE'),
    },
    {
        key: null, // nicht sortierbar
        label: 'Belege',
        headerAlign: 'text-center',
        cellClass: 'text-center',
        cell: () => `<button type="button" class="kwic-row-btn" data-kwic-row title="Belege anzeigen" aria-expanded="false">
                            <svg class="w-4 h-4 kwic-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                        </button>`,
        exportFields: [],
    },
];

class MainSiteApp {
    constructor() {
        this.corpusLoader = new CorpusLoader();
        this.searchEngine = null;
        this.teiCache = null;
        this.teiReader = null; // Unified reading view

        this.currentResults = [];
        this.currentPage = 0;
        this.resultsPerPage = 20;

        // Issue #114: View-Mode für Korpussuche-Ergebnisse
        this.viewMode = this.loadViewMode();        // 'list' | 'table'
        this.sortSpec = { column: 'matchCount', direction: 'desc' };  // Default, nicht persistiert

        // Issue #129: KWIC-Belege in den Suchergebnissen
        this.kwicContextWords = 10;   // Wörter Kontext je Seite (Schmidt-Default)
        this.kwicMaxHits = 100;       // Anzeige-Cap pro Text (total wird ausgewiesen)

        // Corpus data (for text selection)
        this.corpusData = {
            texts: [],
            includedTexts: new Set() // IDs of texts to include in search
        };

        // Detect which page we're on
        this.isSearchPage = window.location.pathname.includes('korpus.html');

        // Expose for Playwright tests
        window._mhdbdbApp = this;

        // Common elements (both pages)
        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage')
        };

        // Search page specific elements
        if (this.isSearchPage) {
            this.elements = {
                ...this.elements,
                searchInput: document.getElementById('searchInput'),
                searchButton: document.getElementById('searchButton'),
                clearSearchButton: document.getElementById('clearSearchButton'),
                lemmaInfo: document.getElementById('lemmaInfo'),
                lemmaList: document.getElementById('lemmaList'),
                textList: document.getElementById('textList'),
                textFilter: document.getElementById('textFilter'),
                selectAllTexts: document.getElementById('selectAllTexts'),
                selectNoneTexts: document.getElementById('selectNoneTexts'),
                selectOnlyVisible: document.getElementById('selectOnlyVisible'),
                selectOnlyVisibleSep: document.getElementById('selectOnlyVisibleSep'),
                selectedTextCount: document.getElementById('selectedTextCount'),
                totalTextCount: document.getElementById('totalTextCount'),
                filterInfoText: document.getElementById('filterInfoText'),
                visibleTextCount: document.getElementById('visibleTextCount'),
                clearTextFilter: document.getElementById('clearTextFilter'),
                resultsSection: document.getElementById('resultsSection'),
                resultsList: document.getElementById('resultsList'),
                resultsCount: document.getElementById('resultsCount'),
                noResults: document.getElementById('noResults'),
                noResultsSummary: document.getElementById('noResultsSummary'),
                filterMismatchNote: document.getElementById('filterMismatchNote'),
                mismatchSearchedCount: document.getElementById('mismatchSearchedCount'),
                mismatchVisibleCount: document.getElementById('mismatchVisibleCount'),
                mismatchApplyFilter: document.getElementById('mismatchApplyFilter'),
                loadMoreContainer: document.getElementById('loadMoreContainer'),
                loadMoreButton: document.getElementById('loadMoreButton'),
                // Reading panel elements (no longer modal)
                readingTitle: document.getElementById('readingTitle'),
                readingAuthor: document.getElementById('readingAuthor'),
                readingLoading: document.getElementById('readingLoading'),
                readingMetadata: document.getElementById('readingMetadata'),
                readingBody: document.getElementById('readingBody'),
                metaAuthor: document.getElementById('metaAuthor'),
                metaSigle: document.getElementById('metaSigle'),
                metaGenre: document.getElementById('metaGenre'),
                metaSource: document.getElementById('metaSource'),
                readingNavigation: document.getElementById('readingNavigation'),
                prevHighlight: document.getElementById('prevHighlight'),
                nextHighlight: document.getElementById('nextHighlight'),
                highlightIndicator: document.getElementById('highlightIndicator'),
                readingPanel: document.getElementById('readingPanel'),
                backToTop: document.getElementById('backToTop')
            };
        }
    }

    async init() {
        try {
            console.log(`[MainSiteApp] Initializing (${this.isSearchPage ? 'Search' : 'Landing'} page)...`);

            if (this.isSearchPage) {
                // Search page: Full initialization
                await this.initSearchPage();
            } else {
                // Landing page: Stats only (no search functionality needed)
                await this.initLandingPage();
            }

            // Setup event listeners (page-specific)
            this.setupEventListeners();

            this.updateLoadingStatus('Fertig!', 100);

            // Hide loading screen after brief delay
            setTimeout(() => {
                this.elements.loadingScreen.classList.add('hidden');
                console.log('[MainSiteApp] Ready');

                // Check for URL parameters (e.g., from playground)
                if (this.isSearchPage) {
                    const hasURLParams = this.handleURLParameters();

                    // If no URL params, show empty state (no auto-load)
                    if (!hasURLParams) {
                        this.showEmptyState();
                    }
                }
            }, 500);

        } catch (error) {
            console.error('[MainSiteApp] Initialization failed:', error);
            this.showError(`Fehler beim Laden: ${error.message}`);
            this.updateLoadingStatus('Fehler beim Laden', 100);
        }
    }

    /**
     * Initialize landing page (stats display only)
     */
    async initLandingPage() {
        // Landing page doesn't need any data loading
        // Stats are hard-coded in the HTML
        console.log('[MainSiteApp] Landing page ready (no data loading needed)');
        this.updateLoadingStatus('Bereit!', 100);
    }

    /**
     * Initialize search page (full functionality)
     */
    async initSearchPage() {
        // Load corpus indices
        this.updateLoadingStatus('Lade Authority-Index...', 10);
        const authorityIndex = await this.corpusLoader.loadAuthorityIndex();

        this.updateLoadingStatus('Lade Korpus-Index...', 50);
        const corpusIndex = await this.corpusLoader.loadCorpusIndex();

        // Store corpus data
        this.corpusData.texts = corpusIndex.texts || [];

        // Initialize all texts as included
        this.corpusData.texts.forEach(text => {
            this.corpusData.includedTexts.add(text.id);
        });

        // Initialize search engine
        this.updateLoadingStatus('Initialisiere Suchmaschine...', 80);
        this.searchEngine = new SearchEngine(authorityIndex, corpusIndex);

        // Shared TEI DOM cache (IndexedDB, revalidated per load — #151)
        this.teiCache = new TEICacheManager();
        this.teiCache.init().catch(err => console.error('[MainSiteApp] TEI cache init failed:', err));

        // Initialize unified TEI reader
        this.teiReader = new TEITextReader(corpusIndex, authorityIndex, this.teiCache);

        // Populate text list with checkboxes
        this.populateTextList();

        console.log('[MainSiteApp] Search page initialized');
    }

    updateLoadingStatus(message, progress) {
        this.elements.loadingStatus.textContent = message;
        this.elements.loadingProgress.style.width = `${progress}%`;
    }

    populateTextList() {
        const textList = this.elements.textList;
        if (!textList) return;

        textList.innerHTML = '';

        this.corpusData.texts.forEach(text => {
            const label = document.createElement('label');
            label.className = 'flex items-start gap-2 p-2 hover:bg-slate-50 rounded transition-colors';
            label.dataset.textId = text.id;
            label.dataset.title = (text.title || '').toLowerCase();
            label.dataset.author = (text.author || '').toLowerCase();

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.className = 'mt-1 w-4 h-4 text-brand-600 border-slate-300 rounded focus:ring-brand-500';
            checkbox.dataset.textId = text.id;
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                this.handleTextToggle(text.id, checkbox.checked);
            });

            const info = document.createElement('div');
            info.className = 'flex-1 min-w-0';

            const titleRow = document.createElement('div');
            titleRow.className = 'flex items-center gap-2';

            const title = document.createElement('span');
            title.className = 'text-sm font-medium text-slate-900 truncate flex-1';
            title.textContent = text.title;

            // Icon buttons container
            const icons = document.createElement('div');
            icons.className = 'text-list-icons flex gap-1 flex-shrink-0';

            // TEI View icon button (Heroicon: document-text)
            const teiBtn = document.createElement('a');
            teiBtn.href = `tei/${text.filename}`;
            teiBtn.target = '_blank';
            teiBtn.className = 'icon-btn';
            teiBtn.title = 'TEI-Datei anzeigen';
            teiBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>';
            teiBtn.addEventListener('click', (e) => e.stopPropagation());

            // Read View icon button (Heroicon: book-open)
            const readBtn = document.createElement('button');
            readBtn.className = 'icon-btn';
            readBtn.title = 'Text lesen';
            readBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>';
            readBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.teiReader.openReadingView(text.id, {}, this.elements);
            });

            icons.appendChild(teiBtn);
            icons.appendChild(readBtn);

            titleRow.appendChild(title);
            titleRow.appendChild(icons);

            const meta = document.createElement('div');
            meta.className = 'text-sm text-slate-600 truncate';
            const author = text.author || 'Unbekannt';
            const wordCount = text.wordCount ? text.wordCount.toLocaleString() : '0';
            meta.textContent = `${text.id} • ${author} • ${wordCount} Wörter`;

            info.appendChild(titleRow);
            info.appendChild(meta);

            label.appendChild(checkbox);
            label.appendChild(info);

            textList.appendChild(label);
        });

        console.log(`[MainSiteApp] Text list populated: ${this.corpusData.texts.length} texts`);
        this.updateTextListStats();
    }

    handleTextToggle(textId, isIncluded) {
        if (isIncluded) {
            this.corpusData.includedTexts.add(textId);
        } else {
            this.corpusData.includedTexts.delete(textId);
        }
        this.updateTextListStats();
    }

    updateTextListStats() {
        const selectedCount = this.corpusData.includedTexts.size;
        const selectedTextCountEl = this.elements.selectedTextCount;
        if (selectedTextCountEl) {
            selectedTextCountEl.textContent = selectedCount;
        }
        const totalTextCountEl = this.elements.totalTextCount;
        if (totalTextCountEl) {
            totalTextCountEl.textContent = this.corpusData.texts.length;
        }
    }

    setupEventListeners() {
        // Search page specific listeners
        if (this.isSearchPage) {
            // Search
            this.elements.searchButton.addEventListener('click', () => this.handleSearch());
            this.elements.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch();
                }
            });

            // Clear search
            this.elements.clearSearchButton.addEventListener('click', () => this.clearSearch());

            // Text filtering
            this.setupTextFiltering();

            // Load more results
            this.elements.loadMoreButton.addEventListener('click', () => this.loadMoreResults());

            // Zum Textanfang springen (#138)
            this.setupBackToTop();

            // Reading panel navigation controls
            this.elements.prevHighlight.addEventListener('click', () => this.teiReader.navigateHighlight(-1));
            this.elements.nextHighlight.addEventListener('click', () => this.teiReader.navigateHighlight(1));

            // Issue #114: View-Mode Toggle
            document.getElementById('viewToggleList')?.addEventListener('click', () => this.setViewMode('list'));
            document.getElementById('viewToggleTable')?.addEventListener('click', () => this.setViewMode('table'));

            // Initial UI-State setzen
            this.updateViewToggleUI();
        }

        console.log(`[MainSiteApp] Event listeners attached (${this.isSearchPage ? 'Search' : 'Landing'} page)`);
    }

    /**
     * Nach-oben-Button der Leseansicht (#138, Wunsch Julia 17.07.).
     *
     * Ziel ist der Kopf des Lesepanels, nicht der Seitenanfang: Wer in einem
     * langen Text steckt, will zurück zu Titel und Metadaten, nicht in die
     * Suchmaske. Sichtbar nur, wenn ein Text geladen ist und der Panelkopf
     * bereits oben aus dem Viewport gescrollt wurde.
     */
    setupBackToTop() {
        const btn = this.elements.backToTop;
        const panel = this.elements.readingPanel;
        if (!btn || !panel) return;

        const SHOW_AFTER_PX = 240;

        const update = () => {
            // Kriterium ist der gesetzte Titel, NICHT readingBody.childElementCount:
            // der Body traegt auch ohne geladenen Text einen Platzhalter
            // ("Bitte geben Sie ein Wort oder Lemma ein ..."), der Button waere
            // sonst schon auf der reinen Ergebnisseite sichtbar.
            const hasText = !!(this.elements.readingTitle
                && this.elements.readingTitle.textContent.trim());
            const scrolledPast = panel.getBoundingClientRect().top < -SHOW_AFTER_PX;
            btn.classList.toggle('hidden', !(hasText && scrolledPast));
        };

        btn.addEventListener('click', () => {
            const top = panel.getBoundingClientRect().top + window.pageYOffset - 16;
            // behavior: 'auto', nicht 'smooth'. In der Leseansicht ist smooth
            // scrolling wirkungslos (in Chrome auf den langen Reader-Seiten
            // verifiziert, unabhaengig von der Distanz und ohne aktives
            // prefers-reduced-motion). Der Reader springt aus demselben Grund
            // schon bei scrollToVerse/scrollToHighlight instant.
            window.scrollTo({ top, behavior: 'auto' });
        });

        // Primaersignal ist ein IntersectionObserver, nicht das scroll-Event:
        // der Reader springt selbst per window.scrollTo (Deep-Links mit
        // ?position= / ?verse=, Highlight-Navigation). Programmatisches
        // Scrollen loest den scroll-Listener nicht zuverlaessig aus, der
        // Button haenge dann im falschen Zustand fest, bis der Nutzer von Hand
        // scrollt. Der Observer feuert unabhaengig davon, wodurch gescrollt
        // wurde. Das scroll-Event bleibt als billiger Zusatz erhalten, damit
        // der Zustand auch bei reinen Layout-Verschiebungen aktuell ist.
        // Beobachtet wird der Panelkopf, nicht das Panel: das Panel ist so hoch
        // wie der ganze Text (bei HUG ueber 180.000 px) und verlaesst den
        // Viewport nie, der Observer feuerte also nie eine Zustandsaenderung.
        const sentinel = panel.querySelector('.reading-header') || panel;
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(update, {
                rootMargin: `-${SHOW_AFTER_PX}px 0px 0px 0px`,
                threshold: [0, 1]
            }).observe(sentinel);
        }
        // Dritter Auslöser: der Titel selbst. Wer auf der Ergebnisliste nach
        // unten gescrollt hat (Button korrekt versteckt, weil kein Text offen)
        // und dann einen Text öffnet, ändert nur `hasText` — ohne Scroll und
        // ohne Positionswechsel feuert sonst kein Signal und der Button bliebe
        // aus, bis der Nutzer von Hand scrollt.
        if (this.elements.readingTitle && 'MutationObserver' in window) {
            new MutationObserver(update).observe(this.elements.readingTitle, {
                childList: true,
                characterData: true,
                subtree: true
            });
        }
        window.addEventListener('scroll', update, { passive: true });
        window.addEventListener('resize', update, { passive: true });
        update();
    }

    setupTextFiltering() {
        const textFilter = this.elements.textFilter;
        const textList = this.elements.textList;
        const filterInfoText = this.elements.filterInfoText;
        const visibleTextCount = this.elements.visibleTextCount;
        const clearTextFilter = this.elements.clearTextFilter;

        // Text filter input
        if (textFilter && textList) {
            textFilter.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase().trim();
                const queryWords = query.split(/\s+/).filter(w => w.length > 0);
                const items = textList.querySelectorAll('label');
                let visibleCount = 0;

                items.forEach(item => {
                    const title = item.dataset.title || '';
                    const author = item.dataset.author || '';
                    const textId = item.dataset.textId || '';
                    const searchText = `${title} ${author} ${textId.toLowerCase()}`;

                    const matches = queryWords.length === 0 ||
                                   queryWords.every(word => searchText.includes(word));

                    if (matches) {
                        item.style.display = '';
                        visibleCount++;
                    } else {
                        item.style.display = 'none';
                    }
                });

                // Show/hide filter info + "Nur diese" button
                if (query) {
                    if (filterInfoText) filterInfoText.style.display = '';
                    if (visibleTextCount) visibleTextCount.textContent = visibleCount;
                    if (this.elements.selectOnlyVisible) this.elements.selectOnlyVisible.style.display = '';
                    if (this.elements.selectOnlyVisibleSep) this.elements.selectOnlyVisibleSep.style.display = '';
                } else {
                    if (filterInfoText) filterInfoText.style.display = 'none';
                    if (this.elements.selectOnlyVisible) this.elements.selectOnlyVisible.style.display = 'none';
                    if (this.elements.selectOnlyVisibleSep) this.elements.selectOnlyVisibleSep.style.display = 'none';
                }
            });
        }

        // Clear filter button
        if (clearTextFilter && textFilter) {
            clearTextFilter.addEventListener('click', () => {
                textFilter.value = '';
                textFilter.dispatchEvent(new Event('input'));
            });
        }

        // Select All / None buttons
        const selectAllTexts = this.elements.selectAllTexts;
        const selectNoneTexts = this.elements.selectNoneTexts;

        if (selectAllTexts && textList) {
            selectAllTexts.addEventListener('click', () => {
                const allCheckboxes = Array.from(textList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = true;
                    this.corpusData.includedTexts.add(cb.dataset.textId);
                });
                if (this.elements.textFilter) {
                    this.elements.textFilter.value = '';
                    this.elements.textFilter.dispatchEvent(new Event('input'));
                }
                this.updateTextListStats();
            });
        }

        if (selectNoneTexts && textList) {
            selectNoneTexts.addEventListener('click', () => {
                this.corpusData.includedTexts.clear();
                const allCheckboxes = Array.from(textList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = false;
                });
                if (this.elements.textFilter) {
                    this.elements.textFilter.value = '';
                    this.elements.textFilter.dispatchEvent(new Event('input'));
                }
                this.updateTextListStats();
            });
        }

        // "Nur diese" — select only visible (filtered) texts, deselect all others
        const selectOnlyVisible = this.elements.selectOnlyVisible;
        if (selectOnlyVisible && textList) {
            selectOnlyVisible.addEventListener('click', () => this.selectOnlyVisibleTexts());
        }

        // Issue #204: One-Click-Korrektur aus dem Mismatch-Hinweis —
        // Auswahl auf die gefilterte Liste einschränken und Suche wiederholen
        if (this.elements.mismatchApplyFilter) {
            this.elements.mismatchApplyFilter.addEventListener('click', () => {
                this.selectOnlyVisibleTexts();
                this.handleSearch();
            });
        }
    }

    /**
     * Wählt genau die aktuell sichtbaren (gefilterten) Texte aus.
     * Genutzt vom "Nur diese"-Button und dem #204-Mismatch-Hinweis.
     */
    selectOnlyVisibleTexts() {
        const textList = this.elements.textList;
        if (!textList) return;
        // Clear includedTexts completely first, then rebuild from visible items
        this.corpusData.includedTexts.clear();
        const allCheckboxes = Array.from(textList.querySelectorAll('input[type="checkbox"]'));
        allCheckboxes.forEach(cb => {
            const label = cb.closest('label');
            const isVisible = !label.style.display || label.style.display !== 'none';
            cb.checked = isVisible;
            if (isVisible) {
                this.corpusData.includedTexts.add(cb.dataset.textId);
            }
        });
        this.updateTextListStats();
    }

    async handleSearch() {
        const searchTerm = this.elements.searchInput.value.trim();

        if (!searchTerm) {
            this.showError('Bitte geben Sie einen Suchbegriff ein.');
            return;
        }

        // Check if any texts are selected
        if (this.corpusData.includedTexts.size === 0) {
            this.showError('Bitte wählen Sie mindestens einen Text aus.');
            return;
        }

        console.log(`[MainSiteApp] Searching for: "${searchTerm}" in ${this.corpusData.includedTexts.size} texts`);

        // Issue #204: Suchraum-Snapshot für Ergebnis-Header, 0-Treffer-Box
        // und Mismatch-Hinweis (Auswahl kann sich nach der Suche ändern)
        this.lastSearchTerm = searchTerm;
        this.lastSearchedCount = this.corpusData.includedTexts.size;

        try {
            // Execute search with text selection filter
            const rawResults = await this.searchEngine.searchLemma(searchTerm, {
                includedTexts: this.corpusData.includedTexts
            });

            // Extract unique lemmata and deduplicate results by textId
            const lemmaSet = new Set();
            const textMap = new Map();

            rawResults.forEach(result => {
                lemmaSet.add(result.lemmaId);

                // Deduplicate by textId and aggregate match counts
                if (textMap.has(result.textId)) {
                    const existing = textMap.get(result.textId);
                    existing.matchCount += result.matchCount;
                    existing.lemmaIds.push(result.lemmaId);
                } else {
                    textMap.set(result.textId, {
                        ...result,
                        lemmaIds: [result.lemmaId]
                    });
                }
            });

            this.currentResults = Array.from(textMap.values());
            this.currentPage = 0;

            // Issue #114 (Followup): Keyness (Log-Likelihood) pro Text.
            // Referenz sind ALLE resolvierten Lemmata (nicht lemmaSet): lemmaSet
            // enthält nur Lemmata mit Treffern in der Textauswahl, wodurch die
            // Referenzsumme sonst mit der Auswahl variieren würde.
            // Berechnung lazy erst beim Tabellen-Render (ensureKeyness) —
            // in der Listenansicht wird Keyness nirgends konsumiert.
            this._keynessLemmaIds = this.searchEngine.resolveLemmaIds(
                TextNormalizer.normalizeMHG(searchTerm)
            );
            this._keynessComputed = false;

            // Issue #114: Sort-Spec bei neuer Suche auf Default zurück
            this.sortSpec = { column: 'matchCount', direction: 'desc' };
            this.sortResults();

            // Display lemma info
            this.displayLemmaInfo(Array.from(lemmaSet));

            // Display results
            this.displayResults();

            // Issue #204: ggf. Hinweis "Filter ≠ Auswahl" über den Ergebnissen
            this.updateFilterMismatchNote();

            // Show clear button
            this.elements.clearSearchButton.style.display = 'block';

        } catch (error) {
            console.error('[MainSiteApp] Search failed:', error);
            this.showError(`Suchfehler: ${error.message}`);
        }
    }

    /**
     * Issue #204: Zeigt einen Hinweis über den Ergebnissen, wenn der
     * Anzeigefilter aktiv ist, die Suche aber eine breitere Auswahl
     * durchsucht hat (Filter ≠ Auswahl — realer Verwechslungsfall).
     */
    updateFilterMismatchNote() {
        const note = this.elements.filterMismatchNote;
        if (!note) return;

        const query = this.elements.textFilter?.value?.trim();
        let visibleIds = null;
        if (query) {
            visibleIds = new Set();
            this.elements.textList?.querySelectorAll('label').forEach(label => {
                if (label.style.display !== 'none') visibleIds.add(label.dataset.textId);
            });
        }

        // Mismatch nur, wenn gefiltert wird, die Filterung Texte übrig lässt
        // UND die Auswahl über die gefilterte Liste hinausgeht
        const mismatch = visibleIds && visibleIds.size > 0 &&
            [...this.corpusData.includedTexts].some(id => !visibleIds.has(id));

        if (!mismatch) {
            note.classList.add('hidden');
            return;
        }

        const searchedCount = this.lastSearchedCount ?? this.corpusData.includedTexts.size;
        this.elements.mismatchSearchedCount.textContent = searchedCount.toLocaleString('de-DE');
        this.elements.mismatchVisibleCount.textContent = visibleIds.size.toLocaleString('de-DE');
        note.classList.remove('hidden');
    }

    displayLemmaInfo(lemmaIds) {
        if (!lemmaIds || lemmaIds.length === 0) {
            this.elements.lemmaInfo.classList.add('hidden');
            return;
        }

        // Get lemma details from authority index (via searchEngine).
        // O(1)-Map statt .find() über 43k Lemmata: Fuzzy-Suchen (Stufe 3,
        // ungecappt) können tausende lemmaIds liefern — DESIGN.md
        // §Performance-Map gegen O(N)-Lookups.
        const lemmata = lemmaIds.map(lemmaId =>
            this.getLemmaById(lemmaId)
                || { id: lemmaId, lemma: lemmaId, normalized: '' }
        );

        // Create lemma badges with links to lemma pages
        this.elements.lemmaList.innerHTML = lemmata.map(lemma => {
            const numericId = lemma.id.replace('lemma_', '');
            return `<a href="lemma/?id=${numericId}" target="_blank" rel="noopener"
                class="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full hover:bg-blue-200 transition">
                ${this.escapeHtml(lemma.lemma)}
            </a>`;
        }).join('');

        // Issue #114 (Followup): Types (Schreibformen) + Wörterbuch-Links (MWB/Lexer)
        this.displayLemmaTypes(lemmata);

        // Show lemma info
        this.elements.lemmaInfo.classList.remove('hidden');

        console.log(`[MainSiteApp] Found ${lemmaIds.length} lemmata:`, lemmata.map(l => l.lemma));
    }

    /**
     * Issue #114 (Followup): Zeigt pro Lemma die belegten Schreibformen (Types,
     * aus dem Variants-Dictionary, MHG-normalisiert) als aufklappbare Liste plus
     * Wörterbuch-Deep-Links (MWB/Lexer via Wörterbuchnetz-API, wie Lemma-Seite #73).
     * Begrenzt auf die ersten 3 Lemmata, damit Fuzzy-Suchen das Panel nicht fluten.
     */
    displayLemmaTypes(lemmata) {
        const container = document.getElementById('lemmaTypes');
        if (!container) return;

        const shown = lemmata.slice(0, 3);
        const blocks = shown.map(lemma => {
            const forms = this.getVariantFormsFor(lemma.id);
            // #187: posAll[] zeigt alle POS-Werte (Fallback: Erstwert aus altem Cache)
            const posLabel = (lemma.posAll || (lemma.pos ? [lemma.pos] : [])).join(' ');
            const posBadge = posLabel
                ? `<span class="ml-1 rounded bg-blue-100 px-1 text-[10px] font-mono text-blue-700">${this.escapeHtml(posLabel)}</span>`
                : '';
            const chips = forms.map(f =>
                `<span class="inline-block bg-white border border-blue-200 px-1.5 py-0.5 rounded text-xs text-slate-700">${this.escapeHtml(f)}</span>`
            ).join(' ');
            const typesBlock = forms.length > 0
                ? `<details class="mt-0.5">
                       <summary class="cursor-pointer text-xs text-blue-800 hover:underline select-none" title="MHG-normalisierte Formen aus dem Variants-Verzeichnis (â→a, ê→e, ü→ue), nicht die Original-Schreibungen der Handschriften">${forms.length} Schreibformen (Types, normalisiert) anzeigen</summary>
                       <div class="mt-1 flex flex-wrap gap-1">${chips}</div>
                   </details>`
                : '<span class="text-xs text-slate-500">Keine Schreibvarianten verzeichnet.</span>';
            return `<div class="pt-1.5 border-t border-blue-100 first:border-t-0 first:pt-0">
                <div class="flex flex-wrap items-center gap-x-2 text-sm">
                    <span class="font-semibold text-blue-900">${this.escapeHtml(lemma.lemma)}</span>${posBadge}
                    <span class="inline-flex flex-wrap gap-2 text-xs" data-wbnetz-links="${this.escapeHtml(lemma.id)}"></span>
                </div>
                ${typesBlock}
            </div>`;
        }).join('');

        const more = lemmata.length > shown.length
            ? `<p class="mt-1.5 text-xs text-slate-500">Schreibformen und Wörterbuch-Links werden nur für die ersten ${shown.length} Lemmata angezeigt (+${lemmata.length - shown.length} weitere).</p>`
            : '';

        container.innerHTML = `<div class="space-y-1.5">${blocks}</div>${more}`;
        container.classList.remove('hidden');

        // Wörterbuch-Links asynchron nachladen (non-blocking, Fehler still)
        shown.forEach(lemma => this.fetchWbnetzLinksInto(lemma));
    }

    /**
     * O(1)-Lookup Lemma-ID → Lemma-Record (lazy gebaute Map über die
     * 43k Lemmata des Authority-Index).
     */
    getLemmaById(lemmaId) {
        if (!this._lemmaById) {
            this._lemmaById = new Map();
            for (const l of this.searchEngine?.authorityIndex?.lemmata || []) {
                if (l?.id) this._lemmaById.set(l.id, l);
            }
        }
        return this._lemmaById.get(lemmaId);
    }

    /**
     * Invertiert das flache Variants-Dictionary (normalisierte Schreibform →
     * Lemma-ID, ~257k Einträge) einmalig zu Lemma-ID → [Formen] und cached es.
     */
    getVariantFormsFor(lemmaId) {
        if (!this._variantsByLemma) {
            this._variantsByLemma = new Map();
            const variants = this.searchEngine?.authorityIndex?.variants || {};
            for (const [form, targetId] of Object.entries(variants)) {
                let list = this._variantsByLemma.get(targetId);
                if (!list) {
                    list = [];
                    this._variantsByLemma.set(targetId, list);
                }
                list.push(form);
            }
            for (const list of this._variantsByLemma.values()) list.sort();
        }
        return this._variantsByLemma.get(lemmaId) || [];
    }

    /**
     * Wörterbuchnetz-Lookup (MWB + Lexer) für ein Lemma, Ergebnis-Links in den
     * zugehörigen data-wbnetz-links-Platzhalter rendern. Shared Client mit
     * Session-Cache in lib/woerterbuchnetz.js (#73/#114, CONTRACTS §D.2):
     * nur anzeigen, wenn es Treffer gibt.
     */
    async fetchWbnetzLinksInto(lemma) {
        if (!lemma.normalized) return;

        const results = await fetchWbnetzEntries(lemma.normalized);

        // Panel kann durch eine neue Suche bereits ersetzt worden sein
        const slot = document.querySelector(`[data-wbnetz-links="${CSS.escape(lemma.id)}"]`);
        if (!slot) return;

        const links = results.flatMap(({ sigle, entries }) =>
            entries.slice(0, 3).map(e =>
                `<a href="${this.escapeHtml(e.wbnetzlink)}" target="_blank" rel="noopener"
                    class="text-brand-700 hover:underline whitespace-nowrap">
                    ${this.escapeHtml(sigle)}: ${this.escapeHtml(decodeHtmlEntities(e.lemma))} ↗
                </a>`
            )
        );
        slot.innerHTML = links.join('');
    }

    clearSearch() {
        // Clear search input
        this.elements.searchInput.value = '';

        // Clear results
        this.currentResults = [];
        this.currentPage = 0;
        this.elements.resultsList.innerHTML = '';

        // Hide results section
        this.elements.resultsSection.classList.add('hidden');
        this.elements.noResults.classList.add('hidden');

        // Hide clear button, lemma info and mismatch note (#204)
        this.elements.clearSearchButton.style.display = 'none';
        this.elements.lemmaInfo.classList.add('hidden');
        this.elements.filterMismatchNote?.classList.add('hidden');

        // Update grid to 2-column layout (search + reading)
        const mainGrid = document.getElementById('mainGrid');
        if (mainGrid) {
            mainGrid.classList.remove('three-column');
            mainGrid.classList.add('two-column');
        }

        console.log('[MainSiteApp] Search cleared');
    }

    displayResults() {
        // Issue #114: Layout je nach View-Mode wechseln.
        // Läuft VOR dem 0-Treffer-Zweig: auch dann muss die Ergebnis-Spalte
        // sichtbar werden, sonst bleibt die noResults-Box unsichtbar (#204 —
        // die Box liegt INNERHALB von resultsSection; das frühere Verstecken
        // der ganzen Section hat sie mitversteckt).
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
        this.elements.resultsSection.classList.remove('hidden');

        // Issue #204: Suchraum sichtbar machen — N = Auswahl zum Suchzeitpunkt
        const searchedCount = this.lastSearchedCount ?? this.corpusData.includedTexts.size;

        if (this.currentResults.length === 0) {
            this.elements.resultsList.innerHTML = '';
            this.elements.loadMoreContainer.classList.add('hidden');
            this.elements.resultsCount.textContent = '';
            // 0-Treffer-Box konkretisieren (#204): Begriff + Suchraum benennen
            if (this.elements.noResultsSummary && this.lastSearchTerm) {
                this.elements.noResultsSummary.textContent =
                    `0 Treffer für „${this.lastSearchTerm}“ in ${searchedCount.toLocaleString('de-DE')} ausgewählten Texten.`;
            }
            this.elements.noResults.classList.remove('hidden');
            // Scroll to no results message (with offset for sticky header)
            this.scrollToElement(this.elements.noResults);
            return;
        }

        this.elements.noResults.classList.add('hidden');

        // Update results count — inkl. Suchraum (#204) + Gesamttrefferzahl (#114 Followup)
        const totalMatches = this.currentResults.reduce((sum, r) => sum + (r.matchCount || 0), 0);
        this.elements.resultsCount.textContent =
            `(${this.currentResults.length} von ${searchedCount.toLocaleString('de-DE')} ausgewählten Texten · ${totalMatches.toLocaleString('de-DE')} Treffer gesamt)`;

        // Clear previous results
        this.elements.resultsList.innerHTML = '';

        // Display first page (Listen-Mode) ODER ganze Tabelle (Tabellen-Mode).
        // currentPage zurücksetzen: displayResults rendert die Liste immer von
        // vorn (innerHTML geleert), aber loadMoreResults zählt currentPage hoch.
        // Ohne Reset zeigt ein erneuter Aufruf (z.B. View-Toggle Tabelle→Liste)
        // einen späteren Slice statt Seite 0 — bei ≤1 Seite bleibt die Liste leer.
        this.currentPage = 0;
        if (this.viewMode === 'table') {
            this.renderTable();
        } else {
            this.loadMoreResults();
        }

        // Auto-scroll to results section (with offset for sticky header)
        setTimeout(() => {
            this.scrollToElement(this.elements.resultsSection);
        }, 100);
    }

    /**
     * Issue #114: Rendert die Tabellen-Ansicht der Suchergebnisse.
     * 6 Spalten: Titel (mit Sigle-Präfix), Autor*in, Treffer, Frequenz/10k,
     * Keyness (LL), Wörter — plus Belege-Spalte (KWIC, #129) und eine
     * Gesamtzeile (tfoot, sticky bottom) mit der Gesamttrefferzahl.
     * Header sind klickbare Sort-Buttons; Zeilen-Klick öffnet den Reader.
     */
    renderTable() {
        // Keyness wird nur in der Tabellen-Ansicht konsumiert (Spalte, Sort,
        // Export) — lazy hier statt bei jeder Suche berechnen.
        this.ensureKeyness();

        const { column, direction } = this.sortSpec;
        const sortIcon = (col) => col === column ? (direction === 'asc' ? '↑' : '↓') : '↕';
        const ariaSort = (col) => col === column ? (direction === 'asc' ? 'ascending' : 'descending') : 'none';

        // Alles Spalten-Wissen kommt aus RESULT_TABLE_COLUMNS (#160).
        const headerCells = RESULT_TABLE_COLUMNS.map(col => {
            if (!col.key) {
                return `<th scope="col" class="results-table-th ${col.headerAlign}" style="position: sticky; top: 0; background: #f8fafc; z-index: 10;">${this.escapeHtml(col.label)}</th>`;
            }
            return `
            <th scope="col" aria-sort="${ariaSort(col.key)}" class="results-table-th ${col.headerAlign}" style="position: sticky; top: 0; background: #f8fafc; z-index: 10;">
                <button type="button" data-sort-col="${col.key}" class="results-table-sort-btn">
                    ${this.escapeHtml(col.label)} <span class="text-xs text-slate-400">${sortIcon(col.key)}</span>
                </button>
            </th>
        `;
        }).join('');

        const rows = this.currentResults.map(r => {
            const cells = RESULT_TABLE_COLUMNS.map(col => {
                if (col.tdHtml) return col.tdHtml(r, this);
                const cls = col.cellClass ? ` ${col.cellClass}` : '';
                return `<td class="results-table-td${cls}">${col.cell(r, this)}</td>`;
            }).join('\n                    ');
            return `
                <tr data-text-id="${this.escapeHtml(r.textId)}" tabindex="0" role="button" class="results-table-row hover:bg-slate-50 cursor-pointer">
                    ${cells}
                </tr>
            `;
        }).join('');

        // Issue #114 (Followup): Gesamtzeile — Lindas Integrationswunsch
        const totalMatches = this.currentResults.reduce((sum, r) => sum + (r.matchCount || 0), 0);
        const totalWords = this.currentResults.reduce((sum, r) => sum + (r.wordCount || 0), 0);
        const totals = {
            count: this.currentResults.length,
            matches: totalMatches,
            words: totalWords,
            freq: totalWords > 0 ? ((totalMatches / totalWords) * 10000).toFixed(1) : '–',
        };
        const totalCells = RESULT_TABLE_COLUMNS
            .filter(col => !col.totalSkip)
            .map(col => {
                const cls = col.totalClass ? ` ${col.totalClass}` : '';
                const span = col.totalColspan ? ` colspan="${col.totalColspan}"` : '';
                const content = col.totalCell ? col.totalCell(totals) : '';
                return `<td class="results-table-td results-table-total-td${cls}"${span}>${content}</td>`;
            }).join('\n                ');
        const totalRow = `
            <tr class="results-table-total-row">
                ${totalCells}
            </tr>
        `;

        const html = `
            <div class="mb-3 flex items-center justify-between gap-3">
                <p class="text-sm text-slate-500">Klick auf Spalten-Header sortiert. Klick auf Zeile öffnet den Text.</p>
                <div class="flex gap-2" id="resultsExportButtons">
                    <button type="button" id="resultsCopyBtn" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-slate-50 inline-flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                        <span>Kopieren</span>
                    </button>
                    <button type="button" id="resultsDownloadBtn" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-slate-50 inline-flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                        <span>CSV</span>
                    </button>
                </div>
            </div>
            <div class="overflow-y-auto rounded-2xl border border-slate-200 bg-white" style="max-height: calc(100vh - 280px);">
                <table class="w-full text-sm">
                    <thead>
                        <tr>
                            ${headerCells}
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                    <tfoot>${totalRow}</tfoot>
                </table>
            </div>
            <p class="mt-2 text-xs text-slate-500">
                Keyness = Log-Likelihood (Dunning 1993): Über-/Unterrepräsentation der Trefferfrequenz
                im Text gegenüber dem Gesamtkorpus. <strong>Fett</strong> markierte Werte ≥ 10,83 sind
                signifikant überrepräsentiert (p&nbsp;&lt;&nbsp;0,001): das Lemma ist ein Schlüsselwort dieses Textes.
            </p>
        `;

        this.elements.resultsList.innerHTML = html;

        // Load-More-Button verstecken (gehört zur Liste)
        this.elements.loadMoreContainer?.classList.add('hidden');

        // Event-Handler binden — Sort, Row-Click, Export (Tasks 6-9 füllen)
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

        // Row-Klick → Reader (Task 7 erweitert)
        this.elements.resultsList.querySelectorAll('.results-table-row').forEach(row => {
            row.addEventListener('click', () => this.handleTableRowClick(row.dataset.textId));
            row.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleTableRowClick(row.dataset.textId);
                }
            });
        });

        // Export-Buttons (Tasks 8-9 erweitern)
        document.getElementById('resultsCopyBtn')?.addEventListener('click', () => this.copyResultsToClipboard());
        document.getElementById('resultsDownloadBtn')?.addEventListener('click', () => this.downloadResultsAsCSV());

        // Issue #129: KWIC-Belege pro Tabellen-Zeile (Detail-Zeile darunter)
        this.elements.resultsList.querySelectorAll('[data-kwic-row]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleKwicTableRow(btn);
            });
            btn.addEventListener('keydown', (e) => e.stopPropagation());
        });
    }

    /**
     * Issue #129: Detail-Zeile mit KWIC-Panel unter einer Tabellen-Zeile
     * ein-/ausklappen. Sortier-Re-Render räumt offene Detail-Zeilen weg.
     */
    toggleKwicTableRow(btn) {
        const row = btn.closest('tr');
        if (!row) return;

        const next = row.nextElementSibling;
        if (next && next.classList.contains('kwic-detail-row')) {
            next.remove();
            btn.setAttribute('aria-expanded', 'false');
            btn.classList.remove('kwic-open');
            return;
        }

        const result = this.currentResults.find(r => r.textId === row.dataset.textId);
        if (!result) return;

        const detail = document.createElement('tr');
        detail.className = 'kwic-detail-row';
        // colspan aus dem Spaltenmodell ableiten statt hartcodieren (#160)
        detail.innerHTML = `<td colspan="${RESULT_TABLE_COLUMNS.length}" class="kwic-detail-cell"><div class="kwic-panel" data-kwic-panel></div></td>`;
        row.after(detail);

        btn.setAttribute('aria-expanded', 'true');
        btn.classList.add('kwic-open');

        this.renderKwicPanel(detail.querySelector('[data-kwic-panel]'), result);
    }

    // Tabellen-Interaktionen: Sortier-Header, Zeilen-Klick, TSV/CSV-Export (#114)
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
    handleTableRowClick(textId) {
        // Result aus currentResults für die lemmaIds finden
        const result = this.currentResults.find(r => r.textId === textId);
        if (!result) return;

        const lemmaIds = result.lemmaIds || [result.lemmaId];

        // Issue #114: Vor Reader-Öffnen zurück auf Listen-Modus wechseln,
        // damit das 3-Spalten-Layout (mit Reader-Slot) wieder greift.
        // localStorage bleibt auf 'table' — beim Reader-Schließen erwartet
        // der User die Tabelle zurück; eine Lösung dafür liegt außerhalb
        // dieses MVPs und ist im Spec als Out-of-Scope dokumentiert.
        if (this.viewMode === 'table') {
            this.viewMode = 'list';
            // localStorage NICHT überschreiben — User-Präferenz bleibt 'table'
            this.updateViewToggleUI();
            this.displayResults();
        }

        this.teiReader.openReadingView(textId, { lemmaIds }, this.elements);
    }
    /**
     * Issue #114: Serialisiert this.currentResults im TSV-Format.
     * Reihenfolge respektiert aktuelle Sortierung.
     */
    serializeResultsAsTSV() {
        const fields = RESULT_TABLE_COLUMNS.flatMap(col => col.exportFields);
        const header = fields.map(f => f.label).join('\t');
        const rows = this.currentResults.map(r =>
            // TSV-Killer (Tab/Newline) aus allen Werten filtern
            fields.map(f => String(f.value(r)).replace(/[\t\n\r]/g, ' ')).join('\t')
        );
        return [header, ...rows].join('\n');
    }

    async copyResultsToClipboard() {
        const btn = document.getElementById('resultsCopyBtn');
        const originalHTML = btn?.innerHTML;
        const successHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span>Kopiert</span>';
        const errorHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg><span>Fehler</span>';
        try {
            const tsv = this.serializeResultsAsTSV();
            await navigator.clipboard.writeText(tsv);
            if (btn) {
                btn.innerHTML = successHTML;
                setTimeout(() => { btn.innerHTML = originalHTML; }, 2000);
            }
        } catch (err) {
            console.error('[MainSiteApp] Clipboard write failed:', err);
            if (btn) {
                btn.innerHTML = errorHTML;
                setTimeout(() => { btn.innerHTML = originalHTML; }, 2000);
            }
        }
    }
    /**
     * Issue #114: CSV-Cell-Quoting nach RFC 4180 / Excel-Konvention.
     * Wenn der Wert Komma, Quote oder Newline enthält, in "..." einfassen
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
        const fields = RESULT_TABLE_COLUMNS.flatMap(col => col.exportFields);
        const header = fields.map(f => this.escapeCsvCell(f.label)).join(',');
        const rows = this.currentResults.map(r =>
            fields.map(f => this.escapeCsvCell(f.value(r))).join(',')
        );
        return [header, ...rows].join('\r\n');  // CRLF für Excel-Kompatibilität
    }

    downloadResultsAsCSV() {
        const today = new Date().toISOString().slice(0, 10);
        const filename = `mhdbdb-suche-${this.safeFilenamePart()}-${today}.csv`;
        this.triggerCsvDownload(filename, this.serializeResultsAsCSV());
    }

    /** Suchbegriff als dateinamen-sicherer Baustein (Pattern #114). */
    safeFilenamePart() {
        const lemma = this.elements.searchInput?.value?.trim() || 'suche';
        return lemma.replace(/[^a-zA-Z0-9äöüÄÖÜß-]/g, '_').slice(0, 40);
    }

    /** Startet den Browser-Download einer CSV (UTF-8 BOM für Excel). */
    triggerCsvDownload(filename, csv) {
        const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Issue #203: Exportiert ALLE Fundstellen eines Texts (ohne Anzeige-Cap)
     * als CSV mit Kontext — Spalten wie das KWIC-Panel, Kontextbreite folgt
     * der aktuellen Panel-Einstellung.
     */
    downloadKwicAsCSV(result, teiDoc) {
        const lemmaIds = (result.lemmaIds || [result.lemmaId]).map(id => id.toString());
        const { hits } = extractKwicHits(teiDoc, lemmaIds, {
            contextWords: this.kwicContextWords,
            maxHits: Infinity
        });

        const header = ['Vers/Zeile', 'Kontext davor', 'Keyword', 'Kontext danach']
            .map(l => this.escapeCsvCell(l)).join(',');
        const rows = hits.map(hit => [
            formatLineRef(hit.lineRef),
            hit.before.join(' '),
            hit.keyword,
            hit.after.join(' ')
        ].map(v => this.escapeCsvCell(v)).join(','));

        const today = new Date().toISOString().slice(0, 10);
        const filename = `mhdbdb-belege-${this.safeFilenamePart()}-${result.textId}-${today}.csv`;
        this.triggerCsvDownload(filename, [header, ...rows].join('\r\n'));
    }

    /**
     * Issue #114: Sortiert this.currentResults in-place gemäß sortSpec.
     * Comparators sind reine Funktionen — Frequenz wird on-the-fly aus
     * matchCount und wordCount berechnet.
     */
    sortResults() {
        const { column, direction } = this.sortSpec;
        const dir = direction === 'asc' ? 1 : -1;

        const spec = RESULT_TABLE_COLUMNS.find(col => col.key === column);
        const valueGetter = spec?.sortValue;

        if (!valueGetter) return;

        this.currentResults.sort((a, b) => {
            const va = valueGetter(a);
            const vb = valueGetter(b);
            if (typeof va === 'string') return va.localeCompare(vb, 'de') * dir;
            return (va - vb) * dir;
        });
    }

    /**
     * Issue #114 (Followup): Keyness einmalig pro Suche berechnen, erst wenn
     * die Tabellen-Ansicht sie braucht. Flag wird in handleSearch zurückgesetzt.
     */
    ensureKeyness() {
        if (this._keynessComputed) return;
        this.computeKeyness(this._keynessLemmaIds || []);
        this._keynessComputed = true;
    }

    /**
     * Issue #114 (Followup, Lindas Keyness-Wunsch): Log-Likelihood (Dunning 1993)
     * pro Ergebnis-Text — vergleicht die Trefferfrequenz im Text mit dem REST des
     * Gesamtkorpus (alle Texte, unabhängig von der Textauswahl; gleiche Referenz
     * wie in Lindas naming-analysis). Positives Vorzeichen = überrepräsentiert,
     * negatives = unterrepräsentiert. Schwellen (df=1): 3,84 → p<0,05; 10,83 → p<0,001.
     *
     * Läuft über den Reverse-Index (corpusIndex.lemmaIndex: Lemma → Texte, die
     * es enthalten) statt über alle 667 Texte × alle Lemma-IDs — Fuzzy-Stufe 3
     * kann tausende IDs liefern, der Aufwand bleibt so proportional zur
     * tatsächlichen Dokumentfrequenz.
     */
    computeKeyness(lemmaIds) {
        const corpusIndex = this.searchEngine?.corpusIndex;
        const texts = corpusIndex?.texts || [];
        if (texts.length === 0 || this.currentResults.length === 0) return;

        // Einmalige Caches: Text-Map für O(1)-Zugriff + Gesamtwortzahl (konstant)
        if (!this._textById) {
            this._textById = new Map();
            let words = 0;
            for (const text of texts) {
                this._textById.set(text.id, text);
                words += text.wordCount || 0;
            }
            this._corpusWordTotal = words;
        }
        const corpusWords = this._corpusWordTotal;

        let corpusMatches = 0;
        if (corpusIndex.lemmaIndex) {
            for (const lemmaId of lemmaIds) {
                const textIds = corpusIndex.lemmaIndex[lemmaId];
                if (!textIds) continue;
                for (const textId of textIds) {
                    const positions = this._textById.get(textId)?.lemmata?.[lemmaId];
                    if (positions) corpusMatches += positions.length;
                }
            }
        } else {
            // Fallback für Index-Stände ohne lemmaIndex: Vollscan
            for (const text of texts) {
                for (const lemmaId of lemmaIds) {
                    const positions = text.lemmata?.[lemmaId];
                    if (positions) corpusMatches += positions.length;
                }
            }
        }

        for (const r of this.currentResults) {
            const c = r.wordCount || 0;
            r.keyness = this.logLikelihood(
                r.matchCount,
                corpusMatches - r.matchCount,
                c,
                corpusWords - c
            );
        }
    }

    /**
     * Signierte Log-Likelihood-Ratio (Dunning 1993) für eine 2x2-Kontingenz:
     * a = Treffer im Text, b = Treffer im Restkorpus,
     * c = Wörter im Text, d = Wörter im Restkorpus.
     */
    logLikelihood(a, b, c, d) {
        if (c <= 0 || d <= 0 || (a + b) <= 0) return 0;
        const e1 = c * (a + b) / (c + d);
        const e2 = d * (a + b) / (c + d);
        let ll = 0;
        if (a > 0 && e1 > 0) ll += a * Math.log(a / e1);
        if (b > 0 && e2 > 0) ll += b * Math.log(b / e2);
        ll *= 2;
        return (a / c >= (a + b) / (c + d)) ? ll : -ll;
    }

    /**
     * Formatiert die Keyness-Zelle der Tabellen-Ansicht: signifikant
     * überrepräsentierte Werte (LL ≥ 10,83, p<0,001) fett + brand-farbig.
     */
    formatKeynessCell(keyness) {
        if (typeof keyness !== 'number') {
            return '<td class="results-table-td text-right tabular-nums text-slate-400">–</td>';
        }
        const formatted = keyness.toLocaleString('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
        if (keyness >= 10.83) {
            return `<td class="results-table-td text-right tabular-nums font-semibold text-brand-700" title="Signifikant überrepräsentiert (p < 0,001): Schlüsselwort dieses Textes">${formatted}</td>`;
        }
        return `<td class="results-table-td text-right tabular-nums text-slate-600">${formatted}</td>`;
    }

    // --- Issue #114: View-Mode helpers ---

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

    // --- Ende Issue #114 View-Mode helpers ---

    /**
     * Scroll to element with offset for sticky header
     */
    scrollToElement(element) {
        if (!element) return;

        const headerHeight = 80; // Approximate header height
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerHeight;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    loadMoreResults() {
        const startIdx = this.currentPage * this.resultsPerPage;
        const endIdx = startIdx + this.resultsPerPage;
        const pageResults = this.currentResults.slice(startIdx, endIdx);

        pageResults.forEach(result => {
            const resultCard = this.createResultCard(result);
            this.elements.resultsList.appendChild(resultCard);
        });

        this.currentPage++;

        // Show/hide "Load More" button
        if (endIdx >= this.currentResults.length) {
            this.elements.loadMoreContainer.classList.add('hidden');
        } else {
            this.elements.loadMoreContainer.classList.remove('hidden');
        }

        console.log(`[MainSiteApp] Displayed results ${startIdx}-${Math.min(endIdx, this.currentResults.length)} of ${this.currentResults.length}`);
    }

    createResultCard(result) {
        const card = document.createElement('div');
        card.className = 'bg-white border border-slate-200 rounded-2xl p-6 hover:border-brand-300 hover:shadow-md transition-all cursor-pointer';

        // Show multi-lemma indicator if multiple lemmata found
        const lemmaCount = result.lemmaIds ? result.lemmaIds.length : 1;
        const lemmaInfo = lemmaCount > 1 ? ` <span class="text-slate-500">(${lemmaCount} Lemmata)</span>` : '';

        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h3 class="font-bold text-lg text-slate-900">${this.escapeHtml(result.title)}</h3>
                    <p class="text-xs text-brand-600 font-semibold mt-1">Sigle: ${this.escapeHtml(result.textId)}</p>
                </div>
                <span class="bg-brand-100 text-brand-700 text-xs font-semibold px-3 py-1 rounded-full flex-shrink-0">${result.matchCount} Treffer${lemmaInfo}</span>
            </div>
            <p class="text-sm text-slate-600 mb-2">${this.escapeHtml(result.author || 'Unbekannte*r Autor*in')}</p>
            ${result.genre ? `<span class="inline-block bg-slate-100 text-slate-700 text-xs px-3 py-1 rounded-full">${this.escapeHtml(result.genre)}</span>` : ''}
            <div class="mt-3 pt-3 border-t border-slate-100">
                <button type="button" class="kwic-toggle-btn" data-kwic-toggle aria-expanded="false">
                    <svg class="w-4 h-4 kwic-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                    <span>Belege anzeigen</span>
                </button>
                <div class="kwic-panel hidden" data-kwic-panel></div>
            </div>
        `;

        // Open reading view with highlighting (pass all lemmaIds for multi-lemma highlighting)
        card.addEventListener('click', () => {
            const lemmaIds = result.lemmaIds || [result.lemmaId];
            this.teiReader.openReadingView(result.textId, { lemmaIds: lemmaIds }, this.elements);
        });

        // Issue #129: KWIC-Belege ausklappen (darf den Karten-Klick nicht auslösen)
        const kwicToggle = card.querySelector('[data-kwic-toggle]');
        const kwicPanel = card.querySelector('[data-kwic-panel]');
        kwicToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleKwicPanel(kwicToggle, kwicPanel, result);
        });
        kwicPanel.addEventListener('click', (e) => e.stopPropagation());

        return card;
    }

    // --- Issue #129: KWIC-Belege (Kontextfenster + Zeilenangaben) ---

    /**
     * Klappt das KWIC-Panel auf/zu; rendert beim ersten Öffnen.
     */
    toggleKwicPanel(toggleBtn, panelEl, result) {
        const isHidden = panelEl.classList.contains('hidden');
        panelEl.classList.toggle('hidden');
        toggleBtn.setAttribute('aria-expanded', String(isHidden));
        toggleBtn.classList.toggle('kwic-open', isHidden);
        const label = toggleBtn.querySelector('span');
        if (label) label.textContent = isHidden ? 'Belege verbergen' : 'Belege anzeigen';

        if (isHidden && !panelEl.dataset.kwicLoaded) {
            this.renderKwicPanel(panelEl, result);
        }
    }

    /**
     * Lädt das TEI (über den Reader-Cache) und rendert die KWIC-Konkordanz.
     */
    async renderKwicPanel(panelEl, result) {
        panelEl.innerHTML = '<p class="kwic-status">Lade Belege …</p>';
        try {
            const text = this.corpusData.texts.find(t => t.id === result.textId);
            const filename = (text && text.filename) || `${result.textId}.tei.xml`;
            const teiDoc = await this.teiReader.loadTEIFile(filename);

            const lemmaIds = (result.lemmaIds || [result.lemmaId]).map(id => id.toString());
            const { hits, total } = extractKwicHits(teiDoc, lemmaIds, {
                contextWords: this.kwicContextWords,
                maxHits: this.kwicMaxHits
            });

            if (hits.length === 0) {
                panelEl.innerHTML = '<p class="kwic-status">Keine Belege gefunden.</p>';
                return;
            }

            const capNote = total > hits.length
                ? `Erste ${hits.length} von ${total.toLocaleString('de-DE')} Belegen`
                : `${total.toLocaleString('de-DE')} Beleg${total === 1 ? '' : 'e'}`;

            const lines = hits.map(hit => `
                <li>
                    <button type="button" class="kwic-line" data-position="${hit.position}" title="Im Volltext öffnen">
                        <span class="kwic-ref">${this.escapeHtml(formatLineRef(hit.lineRef))}</span>
                        <span class="kwic-before"><bdi>${this.escapeHtml(hit.before.join(' '))}</bdi></span>
                        <span class="kwic-keyword">${this.escapeHtml(hit.keyword)}</span>
                        <span class="kwic-after">${this.escapeHtml(hit.after.join(' '))}</span>
                    </button>
                </li>
            `).join('');

            panelEl.innerHTML = `
                <div class="kwic-header">
                    <span class="kwic-count">${capNote}</span>
                    <div class="kwic-header-actions">
                        <label class="kwic-window-label">Kontext:
                            <select class="kwic-window-select" aria-label="Kontextfenster in Wörtern">
                                ${[5, 10, 15, 20].map(n =>
                                    `<option value="${n}"${n === this.kwicContextWords ? ' selected' : ''}>${n} Wörter</option>`
                                ).join('')}
                            </select>
                        </label>
                        <button type="button" class="kwic-export-btn" title="Alle Fundstellen dieses Texts mit Kontext als CSV-Datei herunterladen">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            <span>Belege (CSV)</span>
                        </button>
                    </div>
                </div>
                <ol class="kwic-list">${lines}</ol>
                <p class="kwic-hint">Klick auf einen Beleg öffnet die Fundstelle im Volltext.</p>
            `;
            panelEl.dataset.kwicLoaded = 'true';

            panelEl.querySelector('.kwic-window-select').addEventListener('change', (e) => {
                this.kwicContextWords = parseInt(e.target.value, 10);
                this.renderKwicPanel(panelEl, result);
            });

            panelEl.querySelector('.kwic-export-btn').addEventListener('click', () => {
                this.downloadKwicAsCSV(result, teiDoc);
            });

            panelEl.querySelectorAll('.kwic-line').forEach(btn => {
                btn.addEventListener('click', () => {
                    this.openReaderAtPosition(result, parseInt(btn.dataset.position, 10));
                });
            });

        } catch (error) {
            console.error('[MainSiteApp] KWIC rendering failed:', error);
            panelEl.innerHTML = '<p class="kwic-status">Belege konnten nicht geladen werden.</p>';
        }
    }

    /**
     * Öffnet den Reader an einer konkreten Fundstelle (Wort-Position).
     * Im Tabellen-Modus vorher auf Listen-Layout wechseln (wie handleTableRowClick).
     */
    openReaderAtPosition(result, position) {
        const lemmaIds = result.lemmaIds || [result.lemmaId];

        if (this.viewMode === 'table') {
            this.viewMode = 'list';
            // localStorage NICHT überschreiben — User-Präferenz bleibt 'table'
            this.updateViewToggleUI();
            this.displayResults();
        }

        this.teiReader.openReadingView(result.textId, { lemmaIds, targetPosition: position }, this.elements);
    }

    // --- Ende Issue #129 ---


    showEmptyState() {
        if (this.elements.readingTitle) {
            this.elements.readingTitle.textContent = '';
        }
        if (this.elements.readingBody) {
            this.elements.readingBody.innerHTML =
                '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:16rem;color:#94a3b8;padding:2rem">' +
                '<svg style="width:48px;height:48px;margin-bottom:1rem" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>' +
                '</svg>' +
                '<p style="font-size:1.125rem">Bitte geben Sie ein Wort oder Lemma ein und starten Sie die Suche.</p>' +
                '<p style="font-size:0.875rem;margin-top:0.5rem">Oder klicken Sie auf einen Text in der Liste links.</p>' +
                '</div>';
        }
    }

    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorDisplay.classList.remove('hidden');

        setTimeout(() => {
            this.elements.errorDisplay.classList.add('hidden');
        }, 5000);
    }

    escapeHtml(text) {
        // Delegiert an lib/escape.js (geteilt mit lemma-page.js) — escapt
        // auch Anführungszeichen für Attribut-Kontexte (href="...").
        return escapeHtml(text);
    }

    /**
     * Handle URL parameters for opening the reading view.
     * - Playground multi-lemma jump: ?textId=ABG&lemmaIds=879,7532&position=123
     * - Werk-Deep-Link (#135): ?textId=ABG (öffnet den Text ohne Highlights)
     * - Vers-Deep-Link (#59 Naming-Explorer): ?textId=TRO&verse=20665
     *   (scrollt zur Verszeile <l n="20665">, ohne Lemma-Highlights)
     * - Such-Deep-Link (#144): ?search=brôt (Lemma-Seiten-Button „Im Korpus
     *   suchen" und Schreibformen-Links; gleicher Pfad wie manuelle Eingabe)
     */
    handleURLParameters() {
        const params = new URLSearchParams(window.location.search);
        const textId = params.get('textId');
        const lemmaIdsParam = params.get('lemmaIds');
        const positionParam = params.get('position');
        const verseParam = params.get('verse');
        const searchParam = params.get('search');

        if (!textId) {
            if (searchParam) {
                console.log(`[MainSiteApp] URL search parameter detected: "${searchParam}"`);
                this.elements.searchInput.value = searchParam;
                window.history.replaceState({}, document.title, window.location.pathname);
                this.handleSearch();
                return true;
            }
            return false; // No relevant parameters
        }

        // Lemma-IDs sind optional — beim reinen Werk-Deep-Link (#135) fehlen sie.
        // Deep-Links tragen mal blanke numerische IDs (879), mal kanonische
        // (lemma_879). Der Exact-Token-Match des Readers (lemma-match.js,
        // CONTRACTS §B.1) braucht den lemma_-Präfix — hier normalisieren
        // (idempotent für IDs, die ihn schon tragen), sonst kein Highlight.
        const lemmaIds = lemmaIdsParam
            ? lemmaIdsParam.split(',').map(id => id.trim()).filter(id => id)
                .map(id => id.startsWith('lemma_') ? id : `lemma_${id}`)
            : [];
        const targetPosition = positionParam ? parseInt(positionParam) : null;

        console.log('[MainSiteApp] URL parameters detected:', { textId, lemmaIds, position: positionParam, verse: verseParam });

        // Leeres options-Objekt = Text ohne Lemma-Highlights (wie der "Lesen"-Button).
        const options = {};
        if (lemmaIds.length > 0) {
            options.lemmaIds = lemmaIds;
            if (targetPosition !== null && !isNaN(targetPosition)) {
                options.targetPosition = targetPosition;
            }
        }
        if (verseParam) {
            options.targetVerse = verseParam;
        }

        // Open reader after brief delay (ensure DOM is ready)
        setTimeout(() => {
            this.teiReader.openReadingView(textId, options, this.elements);

            // Clear URL parameters (optional - keeps URL clean)
            window.history.replaceState({}, document.title, window.location.pathname);
        }, 300);

        return true; // URL params were processed
    }

}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const app = new MainSiteApp();
        app.init();
    });
} else {
    const app = new MainSiteApp();
    app.init();
}

export { MainSiteApp };
