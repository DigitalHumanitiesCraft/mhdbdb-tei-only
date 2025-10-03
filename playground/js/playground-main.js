/**
 * MHDBDB Playground - Main Application Class (MIGRATED)
 * Now using modular UI components instead of monolithic ui-helpers.js
 */

import { AuthorityFilesManager } from './data/authority-manager.js';
import { TEIFilesManager } from './data/tei-manager.js';

// NEW: Import modular UI components (decomposed from UICore.js)
import { updateAllUI } from './ui/core/ui-helpers.js';
import { displayFileItem, setupCollapsibleFileList, setupFileFilter, updateFileCount } from './ui/core/file-display.js';
import { showProgress, updateProgress, hideSpinner, setFileDisplayHelpers } from './ui/core/progress.js';
import { AuthorityUI } from './ui/authority/authority-ui.js';
import { TEIExplorer } from './ui/tei/tei-ui.js';
import { MultiLemmaSearchUI } from './ui/tei/multi-lemma-search.js';

// Wire up file display helpers for progress.js
setFileDisplayHelpers(setupCollapsibleFileList, setupFileFilter);

// Import utilities for global exposure (needed for testing)
import { TextNormalizer } from '/lib/text-normalizer.js';
import { SearchPatterns } from './ui/search/SearchHelpers.js';

class MHDBDBPlayground {
    constructor() {
        // Data containers (UNCHANGED)
        this.authorityData = {
            files: [],
            parsedXML: [],
            persons: [],
            works: [],
            lemmata: [],
            concepts: [],
            genres: [],
            names: [],
            variants: []
        };
        
        this.teiData = {
            files: [],
            parsedXML: [],
            words: [],
            lines: [],
            annotations: []
        };

        // Data managers (UNCHANGED)
        this.authorityManager = new AuthorityFilesManager(this.authorityData);
        this.teiManager = new TEIFilesManager(this.teiData);

        // NEW: Modular UI instead of single UIHelpers
        this.ui = {
            authorityExplorers: new AuthorityUI(this.authorityData),
            teiExplorer: new TEIExplorer(this.teiData, this.authorityData)
        };

        // Initialize after teiExplorer is created
        this.ui.multiLemmaSearch = new MultiLemmaSearchUI(
            this.ui.teiExplorer,
            this.authorityManager
        );

        this.init();
    }

    async init() {
        this.initializeEventListeners();

        // Load authority files from pre-built index (UPDATED)
        await this.loadAuthorityIndex();

        // Load TEI files from IndexedDB cache (user-uploaded files)
        await this.loadCachedTEIFiles();

        this.updateUI();
    }

    async loadAuthorityIndex() {
        try {
            console.log('📥 Loading pre-built authority index...');

            // Dynamically import CorpusLoader (from parent directory)
            const { CorpusLoader } = await import('/lib/corpus-loader.js');

            // Create loader with correct path (playground is in playground/ subdirectory)
            const loader = new CorpusLoader('../data');
            await loader.dbReady;

            // Load authority index
            const authorityIndex = await loader.loadAuthorityIndex();

            // Populate authorityData from index
            this.authorityData.persons = authorityIndex.persons || [];
            this.authorityData.works = authorityIndex.works || [];
            this.authorityData.lemmata = authorityIndex.lemmata || [];
            this.authorityData.concepts = authorityIndex.concepts || [];
            this.authorityData.genres = authorityIndex.genres || [];
            this.authorityData.names = authorityIndex.names || [];
            this.authorityData.variants = authorityIndex.variants || {};

            // Load pre-built performance Maps (if available)
            if (authorityIndex.maps) {
                // Convert objects to Maps for compatibility with old code
                if (authorityIndex.maps.conceptToLemmas) {
                    this.authorityManager.indexes.conceptToLemmas = new Map(Object.entries(authorityIndex.maps.conceptToLemmas));
                }
                if (authorityIndex.maps.genreToWorks) {
                    this.authorityManager.indexes.genreToWorks = new Map(Object.entries(authorityIndex.maps.genreToWorks));
                }
                if (authorityIndex.maps.genreHierarchy) {
                    this.authorityManager.indexes.genreHierarchy = new Map(Object.entries(authorityIndex.maps.genreHierarchy));
                }
                console.log(`📊 Performance Maps loaded: concept→lemmas: ${this.authorityManager.indexes.conceptToLemmas.size}, genre→works: ${this.authorityManager.indexes.genreToWorks.size}, genreHierarchy: ${this.authorityManager.indexes.genreHierarchy.size}`);
            }

            // Mark as loaded (for compatibility with old code)
            this.authorityData.files = [
                { name: 'persons.xml' },
                { name: 'works.xml' },
                { name: 'lexicon.xml' },
                { name: 'concepts.xml' },
                { name: 'genres.xml' },
                { name: 'names.xml' },
                { name: 'variants.xml' }
            ];

            console.log(`✅ Authority index loaded: ${this.authorityData.lemmata.length} lemmata, ${this.authorityData.persons.length} persons`);

        } catch (error) {
            console.error('❌ Failed to load authority index:', error);
            alert('Failed to load authority data. Please refresh the page.');
        }
    }

    async loadCachedTEIFiles() {
        try {
            const loadedCount = await this.teiManager.loadFromCache();

            if (loadedCount > 0) {
                console.log(`📁 Restored ${loadedCount} TEI files from IndexedDB`);

                // Display loaded files in UI
                const uploadedFilesContainer = document.getElementById('uploadedFiles');
                if (uploadedFilesContainer) {
                    this.teiData.files.forEach(file => {
                        if (file && file.isCachedFile) {
                            displayFileItem(file, uploadedFilesContainer);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('❌ Error loading cached TEI files:', error);
        }
    }

    // ==================== EVENT LISTENERS (UPDATED) ====================
    
    initializeEventListeners() {
        this.setupFileUpload();
        this.setupAuthorityQueries();
        this.setupTEIQueries();

        // Setup collapsible file list functionality
        setupCollapsibleFileList();
        setupFileFilter();
    }

    setupFileUpload() {
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');

        if (!uploadZone || !fileInput) {
            console.error('Upload elements not found');
            return;
        }

        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            this.handleTEIFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', (e) => {
            this.handleTEIFiles(e.target.files);
        });
    }

    setupAuthorityQueries() {
        // UPDATED: Use new modular UI methods
        const authorityButtons = [
            { id: 'showAuthorsBtn', handler: () => this.ui.authorityExplorers.showAuthors() },
            { id: 'showWorksBtn', handler: () => this.ui.authorityExplorers.showWorks() },
            { id: 'showLemmataBtn', handler: () => this.ui.authorityExplorers.showLemmata() },
            { id: 'showConceptsBtn', handler: () => this.ui.authorityExplorers.showConcepts() },
            { id: 'showGenresBtn', handler: () => this.ui.authorityExplorers.showGenres() },
            { id: 'showNamesBtn', handler: () => this.ui.authorityExplorers.showNames() }
        ];

        authorityButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            } else {
                console.warn(`Missing authority button: ${id}`);
            }
        });
    }

    setupTEIQueries() {
        // UPDATED: Use new TEI explorer methods
        const teiButtons = [
            { id: 'showWordsBtn', handler: () => this.ui.teiExplorer.showWords() },
            { id: 'showLinesBtn', handler: () => this.ui.teiExplorer.showLines() },
            { id: 'findLemmaBtn', handler: () => this.ui.teiExplorer.findLemmaInText() },
            { id: 'findMultiLemmaBtn', handler: () => this.ui.multiLemmaSearch.open() }, // Use new modal UI
            { id: 'showAnnotationsBtn', handler: () => this.ui.teiExplorer.showAnnotations() }
        ];

        teiButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            } else {
                console.warn(`Missing TEI button: ${id}`);
            }
        });
    }

    // ==================== TEI FILE HANDLING (UPDATED) ====================

    async handleTEIFiles(files) {
        const fileArray = Array.from(files);
        const uploadedFilesContainer = document.getElementById('uploadedFiles');
        const totalFiles = fileArray.length;

        if (totalFiles === 0) return;

        // Check if corpus is already loaded
        if (this.teiData.parsedXML.length > 0) {
            const hasCorpusData = this.teiData.parsedXML.some(item => 'xmlDoc' in item);
            if (hasCorpusData) {
                const confirmed = confirm(
                    `Der vollständige Korpus (${this.teiData.parsedXML.length} Dateien) ist bereits geladen.\n\n` +
                    `Möchten Sie diesen löschen und stattdessen ${totalFiles} neue Datei(en) hochladen?`
                );
                if (!confirmed) return;

                // Clear corpus data before uploading
                await this.teiManager.clearAllTEIData();

                // Reset load corpus button to original state
                const loadCorpusBtn = document.getElementById('loadCorpusBtn');
                if (loadCorpusBtn) {
                    loadCorpusBtn.disabled = false;
                    loadCorpusBtn.classList.remove('bg-green-50', 'border-green-200', 'text-green-700');
                    loadCorpusBtn.classList.add('hover:bg-brand-100');
                    loadCorpusBtn.innerHTML = `
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                        </svg>
                        <span>Load Full Corpus (666 Files)</span>
                    `;
                }

                // Clear corpus UI indicators
                const fileCountBadge = document.getElementById('fileCount');
                if (fileCountBadge) {
                    fileCountBadge.textContent = '0';
                }

                // Clear file list container
                const uploadedFilesContainer = document.getElementById('uploadedFiles');
                if (uploadedFilesContainer) {
                    uploadedFilesContainer.innerHTML = '';
                }

                // Show file filter again
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.style.display = '';
                    fileFilter.value = ''; // Reset filter
                }

                this.updateUI();
            }
        }

        // Show progress if uploading multiple files
        if (totalFiles > 1) {
            showProgress('uploadedFilesSection', 0, totalFiles, 'Lade TEI-Dateien');
        }
        
        let processedCount = 0;
        
        for (const file of fileArray) {
            if (this.teiManager.isTEIFile(file)) {
                try {
                    // Update progress for multi-file uploads
                    if (totalFiles > 1) {
                        updateProgress('uploadedFilesSection', processedCount, totalFiles,
                            `Verarbeite: ${file.name}`);
                    }
                    
                    await this.teiManager.processTEIFile(file);
                    processedCount++;
                    
                    // For single file, show immediate feedback
                    if (totalFiles === 1) {
                        displayFileItem(file, uploadedFilesContainer);
                    }
                } catch (error) {
                    console.error(`Fehler beim Verarbeiten von ${file.name}:`, error);
                    // Continue with other files even if one fails
                }
            }
        }
        
        // Complete progress and show all files for multi-file uploads
        if (totalFiles > 1) {
            updateProgress('uploadedFilesSection', totalFiles, totalFiles, 'Abgeschlossen');

            // After a brief delay, show the file list
            setTimeout(() => {
                hideSpinner('uploadedFilesSection');

                // Get fresh reference to container after HTML reset
                const freshUploadedFilesContainer = document.getElementById('uploadedFiles');

                // Display all successfully processed files
                this.teiData.files.forEach(file => {
                    displayFileItem(file, freshUploadedFilesContainer);
                });
            }, 500);
        }

        this.updateUI();
    }

    // ==================== SESSION FILE MANAGEMENT ====================

    async removeTEIFile(filename) {
        if (await this.teiManager.removeTEIFile(filename)) {
            // Update UI
            const fileItem = document.querySelector(`[data-filename="${filename.toLowerCase()}"]`);
            if (fileItem) {
                fileItem.remove();
            }

            // Update file count and overview
            updateFileCount();
            this.updateUI();
        }
    }

    async clearAllCachedFiles() {
        try {
            // Clear TEI files
            const removedCount = await this.teiManager.clearAllCachedFiles();

            // NOTE: Authority file cache is managed by CorpusLoader (Dexie.js)
            // and will be cleared when the page reloads

            if (removedCount > 0) {
                // Clear UI
                const uploadedFiles = document.getElementById('uploadedFiles');
                if (uploadedFiles) {
                    const cachedFileItems = uploadedFiles.querySelectorAll('[data-cached-file="true"]');
                    cachedFileItems.forEach(item => item.remove());
                }

                // Update file count and overview
                updateFileCount();
                this.updateUI();

                // Show success message and offer full page reload
                const reload = confirm(`Cleared ${removedCount} cached TEI files.\n\nReload the page to also clear authority cache?`);
                if (reload) {
                    window.location.reload();
                }
            } else {
                // No TEI files to clear, just offer reload
                const reload = confirm(`No cached TEI files found.\n\nReload the page to clear authority cache?`);
                if (reload) {
                    window.location.reload();
                }
            }
        } catch (error) {
            console.error('❌ Error clearing cache:', error);
            alert('Error clearing cache. Please reload the page manually.');
        }
    }

    async getStorageInfo() {
        return await this.teiManager.getStorageInfo();
    }

    // ==================== UI UPDATES (SIMPLIFIED) ====================

    updateUI() {
        // NEW: Use centralized UI update function
        updateAllUI(this.authorityData, this.teiData);
    }
}

// ==================== GLOBAL ONCLICK HANDLER SUPPORT ====================

// Global reference for dynamically generated onclick handlers
window.playground = null;

// Initialize the playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new MHDBDBPlayground();

    // CRITICAL: Expose UI modules globally for onclick handlers
    // This maintains backward compatibility with dynamically generated onclick calls
    if (window.playground && window.playground.ui) {
        // Make authority explorers methods available globally
        window.playground.ui.authorityExplorers = window.playground.ui.authorityExplorers;
        window.playground.ui.teiExplorer = window.playground.ui.teiExplorer;
    }

    // Expose utilities globally for testing
    window.TextNormalizer = TextNormalizer;
    window.SearchPatterns = SearchPatterns;

    // Setup Load Corpus button handler
    const loadCorpusBtn = document.getElementById('loadCorpusBtn');
    if (loadCorpusBtn) {
        loadCorpusBtn.addEventListener('click', async () => {
            if (!window.playground) return;

            // Show loading state
            const originalText = loadCorpusBtn.innerHTML;
            loadCorpusBtn.disabled = true;
            loadCorpusBtn.innerHTML = '<span>Clearing previous data...</span>';

            try {
                // Clear any previously uploaded TEI files first
                await window.playground.teiManager.clearAllTEIData();

                loadCorpusBtn.innerHTML = '<span>Loading corpus...</span>';
                const result = await window.playground.teiManager.loadCorpusIntoPlayground((loaded, total) => {
                    const percentage = Math.round((loaded / total) * 100);
                    loadCorpusBtn.innerHTML = `<span>Loading: ${loaded}/${total} (${percentage}%)</span>`;
                });

                // Success! Keep button showing loaded state
                loadCorpusBtn.innerHTML = `<span>✅ ${result.loaded} TEI files loaded</span>`;
                loadCorpusBtn.disabled = true; // Keep disabled to prevent re-loading
                loadCorpusBtn.classList.remove('hover:bg-brand-100');
                loadCorpusBtn.classList.add('bg-green-50', 'border-green-200', 'text-green-700');

                // Clear and repopulate the file display with corpus entries
                const uploadedFilesContainer = document.getElementById('uploadedFiles');
                if (uploadedFilesContainer) {
                    uploadedFilesContainer.innerHTML = '';

                    // Display corpus files with metadata
                    window.playground.teiData.parsedXML.forEach(teiData => {
                        displayFileItem(teiData, uploadedFilesContainer);
                    });
                }

                // Update file count badge (just the number)
                const fileCountBadge = document.getElementById('fileCount');
                if (fileCountBadge) {
                    fileCountBadge.textContent = result.loaded;
                }

                // Show file filter for corpus data (useful for 666 files)
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.style.display = '';
                    fileFilter.value = ''; // Reset filter
                }

                // Show files summary section
                const filesSummary = document.getElementById('filesSummary');
                if (filesSummary) {
                    filesSummary.style.display = 'flex';
                }

                // Update UI
                window.playground.updateUI();

                // Auto-open TEI analysis panel
                const teiQueries = document.getElementById('teiQueries');
                if (teiQueries) {
                    teiQueries.style.display = 'block';
                    teiQueries.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }

                console.log(`✅ Corpus loaded successfully: ${result.loaded} files available for analysis`);

            } catch (error) {
                console.error('Corpus loading error:', error);
                loadCorpusBtn.innerHTML = `<span>❌ Error: ${error.message}</span>`;

                // Reset button after 5 seconds
                setTimeout(() => {
                    loadCorpusBtn.disabled = false;
                    loadCorpusBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    }

    console.log('MHDBDB Playground migrated to modular UI successfully!');
    console.log('Available UI modules:', Object.keys(window.playground.ui));
});