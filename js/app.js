/**
 * Main Site Application Controller
 * Manages both landing page (index.html) and search page (korpus.html)
 * - index.html: Stats display only (no search)
 * - korpus.html: Full search functionality
 */

import { CorpusLoader } from '/lib/corpus-loader.js';
import { SearchEngine } from './search/search-engine.js';
import { TextRenderer } from './rendering/text-renderer.js';

class MainSiteApp {
    constructor() {
        this.corpusLoader = new CorpusLoader();
        this.searchEngine = null;
        this.textRenderer = null;

        this.currentResults = [];
        this.currentPage = 0;
        this.resultsPerPage = 20;

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
                genreFilter: document.getElementById('genreFilter'),
                authorFilter: document.getElementById('authorFilter'),
                resultsSection: document.getElementById('resultsSection'),
                resultsList: document.getElementById('resultsList'),
                resultsCount: document.getElementById('resultsCount'),
                noResults: document.getElementById('noResults'),
                loadMoreContainer: document.getElementById('loadMoreContainer'),
                loadMoreButton: document.getElementById('loadMoreButton'),
                textModal: document.getElementById('textModal'),
                modalTitle: document.getElementById('modalTitle'),
                modalAuthor: document.getElementById('modalAuthor'),
                modalContent: document.getElementById('modalContent'),
                modalLoading: document.getElementById('modalLoading'),
                modalLoadingStatus: document.getElementById('modalLoadingStatus'),
                modalTextContent: document.getElementById('modalTextContent'),
                closeModal: document.getElementById('closeModal'),
                prevContext: document.getElementById('prevContext'),
                nextContext: document.getElementById('nextContext'),
                contextIndicator: document.getElementById('contextIndicator')
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

        // Initialize search engine
        this.updateLoadingStatus('Initialisiere Suchmaschine...', 80);
        this.searchEngine = new SearchEngine(authorityIndex, corpusIndex);

        // Initialize text renderer
        this.textRenderer = new TextRenderer(corpusIndex, authorityIndex);

        // Populate filter dropdowns
        this.populateFilters(authorityIndex);

        console.log('[MainSiteApp] Search page initialized');
    }

    updateLoadingStatus(message, progress) {
        this.elements.loadingStatus.textContent = message;
        this.elements.loadingProgress.style.width = `${progress}%`;
    }

    populateFilters(authorityIndex) {
        // Populate genre filter from genres list (if available)
        if (authorityIndex.genres && authorityIndex.genres.length > 0) {
            authorityIndex.genres
                .filter(g => g.termDE)
                .sort((a, b) => a.termDE.localeCompare(b.termDE))
                .forEach(genre => {
                    const option = document.createElement('option');
                    option.value = genre.id;
                    option.textContent = genre.termDE;
                    this.elements.genreFilter.appendChild(option);
                });
        }

        // Populate author filter from persons list
        if (authorityIndex.persons && authorityIndex.persons.length > 0) {
            authorityIndex.persons
                .filter(p => p.preferredName || p.name)
                .sort((a, b) => {
                    const nameA = a.preferredName || a.name;
                    const nameB = b.preferredName || b.name;
                    return nameA.localeCompare(nameB);
                })
                .forEach(person => {
                    const option = document.createElement('option');
                    option.value = person.id;
                    option.textContent = person.preferredName || person.name;
                    this.elements.authorFilter.appendChild(option);
                });
        }

        console.log(`[MainSiteApp] Filters populated: ${this.elements.genreFilter.options.length - 1} genres, ${this.elements.authorFilter.options.length - 1} authors`);
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

            // Filters
            this.elements.genreFilter.addEventListener('click', () => {
                if (this.currentResults.length > 0) {
                    this.handleSearch(); // Re-run search with new filter
                }
            });
            this.elements.authorFilter.addEventListener('change', () => {
                if (this.currentResults.length > 0) {
                    this.handleSearch(); // Re-run search with new filter
                }
            });

            // Load more results
            this.elements.loadMoreButton.addEventListener('click', () => this.loadMoreResults());

            // Modal controls
            this.elements.closeModal.addEventListener('click', () => this.closeModal());
            this.elements.prevContext.addEventListener('click', () => this.textRenderer.navigateContext(-1));
            this.elements.nextContext.addEventListener('click', () => this.textRenderer.navigateContext(1));

            // Close modal on background click
            this.elements.textModal.addEventListener('click', (e) => {
                if (e.target === this.elements.textModal) {
                    this.closeModal();
                }
            });
        }

        console.log(`[MainSiteApp] Event listeners attached (${this.isSearchPage ? 'Search' : 'Landing'} page)`);
    }

    async handleSearch() {
        const searchTerm = this.elements.searchInput.value.trim();

        if (!searchTerm) {
            this.showError('Bitte geben Sie einen Suchbegriff ein.');
            return;
        }

        const genreFilter = this.elements.genreFilter.value;
        const authorFilter = this.elements.authorFilter.value;

        console.log(`[MainSiteApp] Searching for: "${searchTerm}" (genre: ${genreFilter || 'all'}, author: ${authorFilter || 'all'})`);

        try {
            // Execute search
            const results = await this.searchEngine.searchLemma(searchTerm, {
                genre: genreFilter,
                authorId: authorFilter
            });

            this.currentResults = results;
            this.currentPage = 0;

            // Display results
            this.displayResults();

        } catch (error) {
            console.error('[MainSiteApp] Search failed:', error);
            this.showError(`Suchfehler: ${error.message}`);
        }
    }

    displayResults() {
        if (this.currentResults.length === 0) {
            this.elements.resultsSection.classList.add('hidden');
            this.elements.noResults.classList.remove('hidden');
            return;
        }

        // Show results section
        this.elements.noResults.classList.add('hidden');
        this.elements.resultsSection.classList.remove('hidden');

        // Update results count
        this.elements.resultsCount.textContent = `(${this.currentResults.length} Texte gefunden)`;

        // Clear previous results
        this.elements.resultsList.innerHTML = '';

        // Display first page
        this.loadMoreResults();
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
        card.className = 'border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer';

        card.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-lg text-gray-800">${this.escapeHtml(result.title)}</h3>
                <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">${result.matchCount} Treffer</span>
            </div>
            <p class="text-sm text-gray-600 mb-2">${this.escapeHtml(result.author || 'Unbekannter Autor')}</p>
            ${result.genre ? `<span class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded mr-2">${this.escapeHtml(result.genre)}</span>` : ''}
            <p class="text-sm text-gray-700 mt-2 italic">${this.escapeHtml(result.snippet)}</p>
        `;

        card.addEventListener('click', () => this.openText(result));

        return card;
    }

    async openText(result) {
        try {
            console.log(`[MainSiteApp] Opening text: ${result.textId}`);

            // Update modal header
            this.elements.modalTitle.textContent = result.title;
            this.elements.modalAuthor.textContent = result.author || 'Unbekannter Autor';

            // Show modal immediately with loading indicator
            this.elements.textModal.classList.add('active');
            this.elements.modalLoading.classList.remove('hidden');
            this.elements.modalTextContent.classList.add('hidden');

            // Update loading status
            this.updateModalLoadingStatus('Lade TEI-Datei...');

            // Render text content with highlighting (this is slow: 30-60s)
            await this.textRenderer.renderText(result.textId, result.lemmaId, this.elements);

            // Hide loading, show content
            this.elements.modalLoading.classList.add('hidden');
            this.elements.modalTextContent.classList.remove('hidden');

        } catch (error) {
            console.error('[MainSiteApp] Failed to open text:', error);
            this.elements.modalLoading.classList.add('hidden');
            this.showError(`Fehler beim Laden des Textes: ${error.message}`);
        }
    }

    updateModalLoadingStatus(message) {
        if (this.elements.modalLoadingStatus) {
            this.elements.modalLoadingStatus.textContent = message;
        }
    }

    closeModal() {
        this.elements.textModal.classList.remove('active');
        this.elements.modalTextContent.innerHTML = '';
        this.elements.modalLoading.classList.add('hidden');
        this.elements.modalTextContent.classList.remove('hidden');
        console.log('[MainSiteApp] Modal closed');
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
