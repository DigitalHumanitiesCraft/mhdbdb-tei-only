/**
 * Main Site Application Controller
 * Manages the public-facing MHDBDB corpus exploration interface
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

        this.elements = null; // Will be initialized in initElements()
    }

    initElements() {
        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
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
            contextIndicator: document.getElementById('contextIndicator'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage'),
            cacheClearBtn: document.getElementById('cacheClearBtn'),
            cacheInfo: document.getElementById('cacheInfo')
        };

        // Validate all elements exist
        this.validateElements();
    }

    validateElements() {
        const missing = [];
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                missing.push(key);
            }
        }
        if (missing.length > 0) {
            console.error('[MainSiteApp] Missing elements:', missing);
            throw new Error(`Missing required elements: ${missing.join(', ')}`);
        }
        console.log('[MainSiteApp] All required elements found');
    }

    async init() {
        try {
            console.log('[MainSiteApp] Initializing...');

            // Initialize DOM element references
            this.initElements();

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

            // Setup event listeners
            this.setupEventListeners();

            // Update cache info
            this.updateCacheInfo();

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
        // Search
        this.elements.searchButton.addEventListener('click', () => this.handleSearch());
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });

        // Filters
        this.elements.genreFilter.addEventListener('change', () => {
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

        // Cache management
        this.elements.cacheClearBtn.addEventListener('click', () => this.handleCacheClear());

        console.log('[MainSiteApp] Event listeners attached');
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

            // Update cache info after loading a text
            this.updateCacheInfo();

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

    async updateCacheInfo() {
        try {
            if (!this.textRenderer || !this.textRenderer.cache) {
                this.elements.cacheInfo.textContent = 'Cache';
                return;
            }

            const stats = await this.textRenderer.cache.getStats();
            if (stats && stats.count > 0) {
                const sizeMB = (stats.totalSize / (1024 * 1024)).toFixed(1);
                this.elements.cacheInfo.textContent = `Cache (${stats.count} / ${sizeMB}MB)`;
            } else {
                this.elements.cacheInfo.textContent = 'Cache (leer)';
            }
        } catch (error) {
            console.error('[MainSiteApp] Error updating cache info:', error);
            this.elements.cacheInfo.textContent = 'Cache';
        }
    }

    async handleCacheClear() {
        if (!confirm('Cache für TEI-Dateien löschen? Dies verbessert die Performance beim nächsten Laden.')) {
            return;
        }

        try {
            console.log('[MainSiteApp] Clearing TEI cache...');
            await this.textRenderer.cache.clear();
            await this.updateCacheInfo();
            alert('Cache erfolgreich geleert!');
            console.log('[MainSiteApp] Cache cleared successfully');
        } catch (error) {
            console.error('[MainSiteApp] Error clearing cache:', error);
            alert('Fehler beim Leeren des Caches: ' + error.message);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new MainSiteApp();
    app.init();
});

export { MainSiteApp };
