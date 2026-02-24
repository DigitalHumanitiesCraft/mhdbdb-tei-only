/**
 * Main Site Application Controller
 * Manages both landing page (index.html) and search page (korpus.html)
 * - index.html: Stats display only (no search)
 * - korpus.html: Full search functionality
 */

import { CorpusLoader } from './lib/corpus-loader.js';
import { SearchEngine } from './search/search-engine.js';
import { TextRenderer } from './rendering/text-renderer.js';
import { TEITextReader } from './rendering/tei-text-reader.js';

class MainSiteApp {
    constructor() {
        this.corpusLoader = new CorpusLoader();
        this.searchEngine = null;
        this.textRenderer = null;
        this.teiReader = null; // Unified reading view

        this.currentResults = [];
        this.currentPage = 0;
        this.resultsPerPage = 20;

        // Corpus data (for text selection)
        this.corpusData = {
            texts: [],
            includedTexts: new Set() // IDs of texts to include in search
        };

        // Detect which page we're on
        this.isSearchPage = window.location.pathname.includes('korpus.html');

        // Common elements (both pages)
        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage'),
            clearSiteDataBtn: document.getElementById('clearSiteDataBtn')
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
                selectedTextCount: document.getElementById('selectedTextCount'),
                filterInfoText: document.getElementById('filterInfoText'),
                visibleTextCount: document.getElementById('visibleTextCount'),
                clearTextFilter: document.getElementById('clearTextFilter'),
                resultsSection: document.getElementById('resultsSection'),
                resultsList: document.getElementById('resultsList'),
                resultsCount: document.getElementById('resultsCount'),
                noResults: document.getElementById('noResults'),
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
                highlightIndicator: document.getElementById('highlightIndicator')
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

                    // If no URL params, load ABG text automatically
                    if (!hasURLParams) {
                        setTimeout(() => {
                            this.teiReader.openReadingView('ABG', {}, this.elements);
                        }, 200);
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

        this.updateLoadingStatus('Lade Corpus-Index...', 50);
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

        // Initialize text renderer (for cache only)
        this.textRenderer = new TextRenderer(corpusIndex, authorityIndex);

        // Initialize unified TEI reader
        this.teiReader = new TEITextReader(corpusIndex, authorityIndex, this.textRenderer.cache);

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
            meta.className = 'text-xs text-slate-500 truncate';
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
    }

    setupEventListeners() {
        // Clear Site Data button (both pages)
        if (this.elements.clearSiteDataBtn) {
            this.elements.clearSiteDataBtn.addEventListener('click', () => this.handleClearSiteData());
        }

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

            // Reading panel navigation controls
            this.elements.prevHighlight.addEventListener('click', () => this.teiReader.navigateHighlight(-1));
            this.elements.nextHighlight.addEventListener('click', () => this.teiReader.navigateHighlight(1));
        }

        console.log(`[MainSiteApp] Event listeners attached (${this.isSearchPage ? 'Search' : 'Landing'} page)`);
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
                const items = textList.querySelectorAll('label');
                let visibleCount = 0;

                items.forEach(item => {
                    const title = item.dataset.title || '';
                    const author = item.dataset.author || '';
                    const textId = item.dataset.textId || '';

                    const matches = title.includes(query) ||
                                   author.includes(query) ||
                                   textId.toLowerCase().includes(query);

                    if (matches) {
                        item.style.display = '';
                        visibleCount++;
                    } else {
                        item.style.display = 'none';
                    }
                });

                // Show/hide filter info
                if (query) {
                    if (filterInfoText) filterInfoText.style.display = '';
                    if (visibleTextCount) visibleTextCount.textContent = visibleCount;
                } else {
                    if (filterInfoText) filterInfoText.style.display = 'none';
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
                const visibleCheckboxes = Array.from(textList.querySelectorAll('label:not([style*="display: none"]) input[type="checkbox"]'));
                visibleCheckboxes.forEach(cb => {
                    cb.checked = true;
                    this.corpusData.includedTexts.add(cb.dataset.textId);
                });
                this.updateTextListStats();
            });
        }

        if (selectNoneTexts && textList) {
            selectNoneTexts.addEventListener('click', () => {
                const visibleCheckboxes = Array.from(textList.querySelectorAll('label:not([style*="display: none"]) input[type="checkbox"]'));
                visibleCheckboxes.forEach(cb => {
                    cb.checked = false;
                    this.corpusData.includedTexts.delete(cb.dataset.textId);
                });
                this.updateTextListStats();
            });
        }
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

            // Display lemma info
            this.displayLemmaInfo(Array.from(lemmaSet));

            // Display results
            this.displayResults();

            // Show clear button
            this.elements.clearSearchButton.style.display = 'block';

        } catch (error) {
            console.error('[MainSiteApp] Search failed:', error);
            this.showError(`Suchfehler: ${error.message}`);
        }
    }

    displayLemmaInfo(lemmaIds) {
        if (!lemmaIds || lemmaIds.length === 0) {
            this.elements.lemmaInfo.classList.add('hidden');
            return;
        }

        // Get lemma details from authority index (via searchEngine)
        const lemmaDetails = lemmaIds.map(lemmaId => {
            const lemma = this.searchEngine.authorityIndex.lemmata.find(l => l.id === lemmaId);
            return lemma ? lemma.lemma : lemmaId;
        });

        // Create lemma badges with links to lemma pages
        this.elements.lemmaList.innerHTML = lemmaIds.map((lemmaId, i) => {
            const numericId = lemmaId.replace('lemma_', '');
            const lemmaText = this.escapeHtml(lemmaDetails[i]);
            return `<a href="lemma/?id=${numericId}" target="_blank" rel="noopener"
                class="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full hover:bg-blue-200 transition">
                ${lemmaText}
            </a>`;
        }).join('');

        // Show lemma info
        this.elements.lemmaInfo.classList.remove('hidden');

        console.log(`[MainSiteApp] Found ${lemmaIds.length} lemmata:`, lemmaDetails);
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

        // Hide clear button and lemma info
        this.elements.clearSearchButton.style.display = 'none';
        this.elements.lemmaInfo.classList.add('hidden');

        // Update grid to 2-column layout (search + reading)
        const mainGrid = document.getElementById('mainGrid');
        if (mainGrid) {
            mainGrid.classList.remove('three-column');
            mainGrid.classList.add('two-column');
        }

        console.log('[MainSiteApp] Search cleared');
    }

    displayResults() {
        if (this.currentResults.length === 0) {
            this.elements.resultsSection.classList.add('hidden');
            this.elements.noResults.classList.remove('hidden');
            // Scroll to no results message (with offset for sticky header)
            this.scrollToElement(this.elements.noResults);
            return;
        }

        // Show results section
        this.elements.noResults.classList.add('hidden');
        this.elements.resultsSection.classList.remove('hidden');

        // Update grid to 3-column layout (search + results + reading)
        const mainGrid = document.getElementById('mainGrid');
        if (mainGrid) {
            mainGrid.classList.add('three-column');
            mainGrid.classList.remove('two-column');
        }

        // Update results count
        this.elements.resultsCount.textContent = `(${this.currentResults.length} Texte gefunden)`;

        // Clear previous results
        this.elements.resultsList.innerHTML = '';

        // Display first page
        this.loadMoreResults();

        // Auto-scroll to results section (with offset for sticky header)
        setTimeout(() => {
            this.scrollToElement(this.elements.resultsSection);
        }, 100);
    }

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
            <p class="text-sm text-slate-600 mb-2">${this.escapeHtml(result.author || 'Unbekannter Autor')}</p>
            ${result.genre ? `<span class="inline-block bg-slate-100 text-slate-700 text-xs px-3 py-1 rounded-full">${this.escapeHtml(result.genre)}</span>` : ''}
        `;

        // Open reading view with highlighting (pass all lemmaIds for multi-lemma highlighting)
        card.addEventListener('click', () => {
            const lemmaIds = result.lemmaIds || [result.lemmaId];
            this.teiReader.openReadingView(result.textId, { lemmaIds: lemmaIds }, this.elements);
        });

        return card;
    }


    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorDisplay.classList.remove('hidden');

        setTimeout(() => {
            this.elements.errorDisplay.classList.add('hidden');
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Handle URL parameters from playground (multi-lemma reader jump)
     * Expected params: ?textId=ABG&lemmaIds=879,7532&position=123
     */
    handleURLParameters() {
        const params = new URLSearchParams(window.location.search);
        const textId = params.get('textId');
        const lemmaIdsParam = params.get('lemmaIds');
        const positionParam = params.get('position');

        if (!textId || !lemmaIdsParam) {
            return false; // No relevant parameters
        }

        console.log('[MainSiteApp] URL parameters detected:', { textId, lemmaIds: lemmaIdsParam, position: positionParam });

        // Parse lemma IDs (comma-separated)
        const lemmaIds = lemmaIdsParam.split(',').map(id => id.trim()).filter(id => id);
        const targetPosition = positionParam ? parseInt(positionParam) : null;

        // Build options object
        const options = {
            lemmaIds: lemmaIds
        };

        if (targetPosition !== null && !isNaN(targetPosition)) {
            options.targetPosition = targetPosition;
        }

        // Open reader after brief delay (ensure DOM is ready)
        setTimeout(() => {
            this.teiReader.openReadingView(textId, options, this.elements);

            // Clear URL parameters (optional - keeps URL clean)
            window.history.replaceState({}, document.title, window.location.pathname);
        }, 300);

        return true; // URL params were processed
    }

    /**
     * Clear all site data (equivalent to Chrome DevTools "Clear site data")
     * Clears:
     * - TEI cache (IndexedDB: MHDBDB_TEI_Cache)
     * - Authority/Corpus indices (IndexedDB: MHDBDBMainSite)
     * - localStorage
     * - sessionStorage
     */
    async handleClearSiteData() {
        const message = `Alle gespeicherten Daten löschen?\n\nDies umfasst:\n` +
            `• TEI-Dateien Cache\n` +
            `• Authority- und Corpus-Indizes\n` +
            `• Alle lokalen Einstellungen\n\n` +
            `Die Seite wird neu geladen.`;

        if (!confirm(message)) {
            return;
        }

        try {
            console.log('[MainSiteApp] Clearing all site data...');

            // 1. Clear TEI cache
            if (this.textRenderer && this.textRenderer.cache) {
                console.log('[MainSiteApp] Clearing TEI cache...');
                await this.textRenderer.cache.clear();
            }

            // 2. Clear corpus loader IndexedDB (authority/corpus indices)
            if (this.corpusLoader && this.corpusLoader.db) {
                console.log('[MainSiteApp] Clearing corpus indices...');
                await this.corpusLoader.db.indices.clear();
            }

            // 3. Clear all IndexedDB databases
            console.log('[MainSiteApp] Clearing all IndexedDB databases...');
            const databases = await indexedDB.databases();
            for (const db of databases) {
                console.log(`[MainSiteApp] Deleting database: ${db.name}`);
                indexedDB.deleteDatabase(db.name);
            }

            // 4. Clear localStorage and sessionStorage
            console.log('[MainSiteApp] Clearing localStorage and sessionStorage...');
            localStorage.clear();
            sessionStorage.clear();

            console.log('[MainSiteApp] All site data cleared successfully');

            // Reload page to reinitialize
            alert('Alle Daten wurden gelöscht. Die Seite wird neu geladen.');
            window.location.reload();

        } catch (error) {
            console.error('[MainSiteApp] Error clearing site data:', error);
            alert('Fehler beim Löschen der Daten: ' + error.message);
        }
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
