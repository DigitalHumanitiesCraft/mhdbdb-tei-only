/**
 * MHDBDB Main Site - Corpus Browser Application
 * Handles corpus loading, text browsing, and simple search
 */

import { IndexedDBManager } from '../playground/js/indexed-db-manager.js';
import { CorpusLoader } from './corpus-loader.js';

export class MainSiteApp {
    constructor() {
        this.dbManager = new IndexedDBManager();
        this.corpusLoader = new CorpusLoader(this.dbManager);
        this.corpusFiles = [];
        this.filteredFiles = [];
    }

    // ==================== INITIALIZATION ====================

    async initialize() {
        console.log('🚀 Initializing MHDBDB Main Site App...');

        try {
            // Initialize IndexedDB
            await this.dbManager.initialize();

            // Check corpus status
            await this.checkCorpusStatus();

            // Setup UI event listeners
            this.setupEventListeners();

            console.log('✅ Main Site App initialized successfully');
            return true;

        } catch (error) {
            console.error('❌ Initialization failed:', error);
            return false;
        }
    }

    // ==================== CORPUS MANAGEMENT ====================

    async checkCorpusStatus() {
        const isLoaded = await this.dbManager.isCorpusLoaded();
        const count = await this.dbManager.getCorpusCount();

        console.log(`📊 Corpus status: ${count}/666 files loaded`);

        if (isLoaded) {
            await this.displayCorpusBrowser();
        } else {
            this.displayCorpusLoadPrompt(count);
        }
    }

    displayCorpusLoadPrompt(currentCount) {
        const container = document.getElementById('corpus-container');
        if (!container) {
            console.warn('⚠️ Corpus container not found');
            return;
        }

        const percentage = Math.round((currentCount / 666) * 100);

        container.innerHTML = `
            <div class="corpus-load-prompt">
                <h2>TEI Corpus Loading</h2>
                ${currentCount > 0 ? `
                    <p>Corpus partially loaded: ${currentCount}/666 files (${percentage}%)</p>
                    <button id="resume-load-btn" class="btn btn-primary">Resume Loading</button>
                    <button id="clear-load-btn" class="btn btn-secondary">Clear and Restart</button>
                ` : `
                    <p>The MHDBDB corpus contains 666 TEI-encoded Middle High German texts (1.5 GB).</p>
                    <p>These files will be downloaded and cached in your browser for offline access.</p>
                    <button id="start-load-btn" class="btn btn-primary">Load Corpus (1.5 GB)</button>
                `}
                <div id="load-progress" style="display: none;">
                    <div class="progress-bar">
                        <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
                    </div>
                    <p id="progress-text">Loading...</p>
                </div>
            </div>
        `;
    }

    async startCorpusLoad() {
        const progressDiv = document.getElementById('load-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');

        progressDiv.style.display = 'block';

        const result = await this.corpusLoader.loadCorpus((loaded, total) => {
            const percentage = Math.round((loaded / total) * 100);
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = `Loading: ${loaded}/${total} files (${percentage}%)`;
        });

        if (result.status === 'loaded' || result.status === 'cached') {
            progressText.textContent = 'Corpus loaded successfully!';
            setTimeout(() => {
                this.displayCorpusBrowser();
            }, 1000);
        } else {
            progressText.textContent = `Error: ${result.error}`;
        }
    }

    async resumeCorpusLoad() {
        const progressDiv = document.getElementById('load-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');

        progressDiv.style.display = 'block';

        const result = await this.corpusLoader.resumeCorpusLoad((loaded, total) => {
            const percentage = Math.round((loaded / total) * 100);
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = `Resuming: ${loaded}/${total} files (${percentage}%)`;
        });

        if (result.status === 'resumed' || result.status === 'complete') {
            progressText.textContent = 'Corpus loaded successfully!';
            setTimeout(() => {
                this.displayCorpusBrowser();
            }, 1000);
        } else {
            progressText.textContent = `Error: ${result.error}`;
        }
    }

    async clearAndRestartCorpusLoad() {
        if (confirm('This will delete all cached corpus files and restart the download. Continue?')) {
            await this.dbManager.clearCorpusFiles();
            this.displayCorpusLoadPrompt(0);
        }
    }

    // ==================== CORPUS BROWSER ====================

    async displayCorpusBrowser() {
        console.log('📚 Displaying corpus browser...');

        // Load corpus file list
        this.corpusFiles = await this.dbManager.listCorpusFiles();
        this.filteredFiles = [...this.corpusFiles];

        const container = document.getElementById('corpus-container');
        if (!container) {
            console.warn('⚠️ Corpus container not found');
            return;
        }

        container.innerHTML = `
            <div class="corpus-browser">
                <div class="corpus-header">
                    <h2>TEI Corpus Browser</h2>
                    <p>${this.corpusFiles.length} texts available</p>
                </div>

                <div class="corpus-controls">
                    <input type="text" id="search-input" class="search-input" placeholder="Search by title, author, or sigle...">
                    <select id="author-filter" class="author-filter">
                        <option value="">All Authors</option>
                    </select>
                    <button id="clear-filters-btn" class="btn btn-secondary">Clear Filters</button>
                </div>

                <div id="corpus-list" class="corpus-list">
                    <!-- Files will be rendered here -->
                </div>
            </div>
        `;

        this.populateAuthorFilter();
        this.renderCorpusList();
    }

    populateAuthorFilter() {
        const authorFilter = document.getElementById('author-filter');
        if (!authorFilter) return;

        // Get unique authors
        const authors = [...new Set(this.corpusFiles.map(f => f.author))].filter(a => a).sort();

        authors.forEach(author => {
            const option = document.createElement('option');
            option.value = author;
            option.textContent = author;
            authorFilter.appendChild(option);
        });
    }

    renderCorpusList() {
        const listContainer = document.getElementById('corpus-list');
        if (!listContainer) return;

        if (this.filteredFiles.length === 0) {
            listContainer.innerHTML = '<p class="no-results">No texts found matching your filters.</p>';
            return;
        }

        listContainer.innerHTML = this.filteredFiles.map(file => `
            <div class="corpus-item" data-filename="${file.filename}">
                <div class="corpus-item-header">
                    <span class="corpus-sigle">${file.sigle}</span>
                    <h3 class="corpus-title">${file.title || file.filename}</h3>
                </div>
                <div class="corpus-item-meta">
                    <span class="corpus-author">${file.author || 'Unknown Author'}</span>
                    <span class="corpus-size">${this.formatFileSize(file.size)}</span>
                </div>
                <button class="btn btn-small view-text-btn" data-filename="${file.filename}">View Text</button>
            </div>
        `).join('');

        // Add event listeners to view buttons
        listContainer.querySelectorAll('.view-text-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filename = e.target.dataset.filename;
                this.viewText(filename);
            });
        });
    }

    applyFilters() {
        const searchInput = document.getElementById('search-input');
        const authorFilter = document.getElementById('author-filter');

        const searchTerm = searchInput?.value.toLowerCase() || '';
        const selectedAuthor = authorFilter?.value || '';

        this.filteredFiles = this.corpusFiles.filter(file => {
            // Search filter
            const matchesSearch = !searchTerm ||
                file.title.toLowerCase().includes(searchTerm) ||
                file.author.toLowerCase().includes(searchTerm) ||
                file.sigle.toLowerCase().includes(searchTerm);

            // Author filter
            const matchesAuthor = !selectedAuthor || file.author === selectedAuthor;

            return matchesSearch && matchesAuthor;
        });

        this.renderCorpusList();
    }

    clearFilters() {
        const searchInput = document.getElementById('search-input');
        const authorFilter = document.getElementById('author-filter');

        if (searchInput) searchInput.value = '';
        if (authorFilter) authorFilter.value = '';

        this.filteredFiles = [...this.corpusFiles];
        this.renderCorpusList();
    }

    // ==================== TEXT VIEWER ====================

    async viewText(filename) {
        console.log(`📖 Viewing text: ${filename}`);

        // Load text content
        const content = await this.dbManager.loadCorpusFile(filename);
        if (!content) {
            alert('Failed to load text content');
            return;
        }

        // Find metadata
        const fileMetadata = this.corpusFiles.find(f => f.filename === filename);

        // Create viewer modal
        this.displayTextViewer(filename, content, fileMetadata);
    }

    displayTextViewer(filename, content, metadata) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'text-viewer-modal';
        modal.innerHTML = `
            <div class="text-viewer-content">
                <div class="text-viewer-header">
                    <div>
                        <span class="text-sigle">${metadata?.sigle || ''}</span>
                        <h2>${metadata?.title || filename}</h2>
                        <p class="text-author">${metadata?.author || 'Unknown Author'}</p>
                    </div>
                    <button class="close-btn" id="close-viewer-btn">&times;</button>
                </div>
                <div class="text-viewer-body">
                    <pre class="tei-content">${this.escapeHtml(content)}</pre>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close button
        document.getElementById('close-viewer-btn').addEventListener('click', () => {
            modal.remove();
        });

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // ESC key to close
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // Corpus loading buttons (delegated event listeners)
        document.body.addEventListener('click', (e) => {
            if (e.target.id === 'start-load-btn') {
                this.startCorpusLoad();
            } else if (e.target.id === 'resume-load-btn') {
                this.resumeCorpusLoad();
            } else if (e.target.id === 'clear-load-btn') {
                this.clearAndRestartCorpusLoad();
            } else if (e.target.id === 'clear-filters-btn') {
                this.clearFilters();
            }
        });

        // Search input (delegated)
        document.body.addEventListener('input', (e) => {
            if (e.target.id === 'search-input') {
                this.applyFilters();
            }
        });

        // Author filter (delegated)
        document.body.addEventListener('change', (e) => {
            if (e.target.id === 'author-filter') {
                this.applyFilters();
            }
        });
    }

    // ==================== UTILITY FUNCTIONS ====================

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Auto-initialize when loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.mhdbdbApp = new MainSiteApp();
        window.mhdbdbApp.initialize();
    });
} else {
    window.mhdbdbApp = new MainSiteApp();
    window.mhdbdbApp.initialize();
}
