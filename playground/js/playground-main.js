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
import { initRouter, navigate, dispatchFromHash } from './ui/core/router.js';
import { AuthorityUI } from './ui/authority/authority-ui.js';
import { TEIExplorer } from './ui/tei/tei-ui.js';
import { MultiLemmaSearchUI } from './ui/tei/multi-lemma-search.js';

// Wire up file display helpers for progress.js
setFileDisplayHelpers(setupCollapsibleFileList, setupFileFilter);

// Import utilities for global exposure (needed for testing)
import { TextNormalizer } from '../../assets/js/lib/text-normalizer.js';
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

        // NEW: Auto-load corpus on startup
        await this.autoLoadCorpus();

        this.updateUI();

        // NEW: Wire up hash router and dispatch any initial hash from the URL.
        // Done after data loading so that handlers can rely on populated state.
        initRouter();
        dispatchFromHash();
    }

    async loadAuthorityIndex() {
        try {
            console.log('📥 Loading pre-built authority index...');

            // Dynamically import CorpusLoader (from parent directory)
            const { CorpusLoader } = await import('../../assets/js/lib/corpus-loader.js');

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
                // Convert objects to Maps for efficient lookup
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

            // Mark authority files as loaded
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

    async autoLoadCorpus() {
        try {
            console.log('📥 Auto-loading corpus on startup...');

            // Show loading state
            const loadingState = document.getElementById('corpusLoadingState');
            const fileBrowserSection = document.getElementById('fileBrowserSection');

            if (loadingState) loadingState.style.display = 'block';
            if (fileBrowserSection) fileBrowserSection.style.display = 'none';

            // Load corpus from pre-built index
            const { CorpusLoader } = await import('../../assets/js/lib/corpus-loader.js');
            const loader = new CorpusLoader('../data');
            await loader.dbReady;

            const corpusIndex = await loader.loadCorpusIndex();

            // Store corpus data (not parsedXML - we'll use the index directly)
            this.corpusData = {
                texts: corpusIndex.texts || [],
                lemmaIndex: corpusIndex.lemmaIndex || {},
                includedTexts: new Set() // Track which texts are included in search
            };

            // Initially include all texts
            this.corpusData.texts.forEach(text => {
                this.corpusData.includedTexts.add(text.id);
            });

            console.log(`✅ Corpus loaded: ${this.corpusData.texts.length} texts`);

            // Hide loading, show file browser
            if (loadingState) loadingState.style.display = 'none';
            if (fileBrowserSection) fileBrowserSection.style.display = 'block';

            // Populate file browser
            this.populateFileBrowser();

            // Enable TEI queries
            const teiQueries = document.getElementById('teiQueries');
            if (teiQueries) teiQueries.style.display = 'block';

        } catch (error) {
            console.error('❌ Failed to auto-load corpus:', error);
            alert('Failed to load corpus. Please refresh the page.');
        }
    }

    populateFileBrowser() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.corpusData.texts.forEach(text => {
            const label = document.createElement('label');
            label.className = 'file-item';
            label.dataset.textId = text.id;
            label.dataset.title = text.title.toLowerCase();
            label.dataset.author = (text.author || '').toLowerCase();

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.dataset.textId = text.id;
            checkbox.addEventListener('change', () => this.handleTextToggle(text.id, checkbox.checked));

            const info = document.createElement('div');
            info.className = 'file-info';

            const title = document.createElement('span');
            title.className = 'file-title';
            title.textContent = text.title;

            const meta = document.createElement('span');
            meta.className = 'file-meta';
            const author = text.author || 'Unbekannt';
            const wordCount = text.wordCount ? text.wordCount.toLocaleString() : '0';
            meta.textContent = `${text.id} • ${author} • ${wordCount} Wörter`;

            info.appendChild(title);
            info.appendChild(meta);

            label.appendChild(checkbox);
            label.appendChild(info);

            fileList.appendChild(label);
        });

        // Update summary stats
        this.updateFileBrowserStats();

        // Setup filter
        this.setupFileBrowserFilter();
    }

    handleTextToggle(textId, isIncluded) {
        if (isIncluded) {
            this.corpusData.includedTexts.add(textId);
        } else {
            this.corpusData.includedTexts.delete(textId);
        }
        this.updateFileBrowserStats();
    }

    updateFileBrowserStats() {
        const includedCount = this.corpusData.includedTexts.size;
        const totalTexts = this.corpusData.texts.length;

        // Update included count
        const includedCountEl = document.getElementById('includedCount');
        if (includedCountEl) includedCountEl.textContent = includedCount;

        // Calculate total words and lemmata for included texts
        let totalWords = 0;
        let lemmataSet = new Set();

        this.corpusData.texts.forEach(text => {
            if (this.corpusData.includedTexts.has(text.id)) {
                totalWords += text.wordCount || 0;
                Object.keys(text.lemmata || {}).forEach(lemmaId => lemmataSet.add(lemmaId));
            }
        });

        const totalWordsEl = document.getElementById('totalWords');
        const totalLemmataEl = document.getElementById('totalLemmata');

        if (totalWordsEl) totalWordsEl.textContent = totalWords.toLocaleString();
        if (totalLemmataEl) totalLemmataEl.textContent = lemmataSet.size.toLocaleString();
    }

    setupFileBrowserFilter() {
        const fileFilter = document.getElementById('fileFilter');
        const fileList = document.getElementById('fileList');
        const filterInfo = document.getElementById('filterInfo');
        const visibleCountEl = document.getElementById('visibleCount');
        const clearFilterBtn = document.getElementById('clearFilterBtn');

        if (!fileFilter || !fileList) return;

        fileFilter.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const items = fileList.querySelectorAll('.file-item');
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

            // Show/hide filter info + "Nur diese" button
            const onlyVisibleBtn = document.getElementById('selectOnlyVisibleBtn');
            const onlyVisibleSep = document.getElementById('selectOnlyVisibleSep');
            if (query) {
                if (filterInfo) filterInfo.style.display = 'flex';
                if (visibleCountEl) visibleCountEl.textContent = visibleCount;
                if (onlyVisibleBtn) onlyVisibleBtn.style.display = '';
                if (onlyVisibleSep) onlyVisibleSep.style.display = '';
            } else {
                if (filterInfo) filterInfo.style.display = 'none';
                if (onlyVisibleBtn) onlyVisibleBtn.style.display = 'none';
                if (onlyVisibleSep) onlyVisibleSep.style.display = 'none';
            }
        });

        // Clear filter button
        if (clearFilterBtn) {
            clearFilterBtn.addEventListener('click', () => {
                fileFilter.value = '';
                fileFilter.dispatchEvent(new Event('input'));
            });
        }

        // Select All / None buttons
        const selectAllBtn = document.getElementById('selectAllBtn');
        const selectNoneBtn = document.getElementById('selectNoneBtn');

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                const allCheckboxes = Array.from(fileList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = true;
                    this.corpusData.includedTexts.add(cb.dataset.textId);
                });
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.value = '';
                    fileFilter.dispatchEvent(new Event('input'));
                }
                this.updateFileBrowserStats();
            });
        }

        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', () => {
                this.corpusData.includedTexts.clear();
                const allCheckboxes = Array.from(fileList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = false;
                });
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.value = '';
                    fileFilter.dispatchEvent(new Event('input'));
                }
                this.updateFileBrowserStats();
            });
        }

        // "Nur diese" — select only visible (filtered) texts, deselect all others
        const selectOnlyVisibleBtn = document.getElementById('selectOnlyVisibleBtn');
        if (selectOnlyVisibleBtn) {
            selectOnlyVisibleBtn.addEventListener('click', () => {
                this.corpusData.includedTexts.clear();
                const allCheckboxes = Array.from(fileList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    const item = cb.closest('.file-item');
                    const isVisible = !item.style.display || item.style.display !== 'none';
                    cb.checked = isVisible;
                    if (isVisible) {
                        this.corpusData.includedTexts.add(cb.dataset.textId);
                    }
                });
                this.updateFileBrowserStats();
            });
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
            // Upload UI removed in redesign - corpus auto-loads instead
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
        // UPDATED: Go through the hash router so the URL reflects the current view.
        const authorityButtons = [
            { id: 'showAuthorsBtn',  handler: () => navigate('authors') },
            { id: 'showWorksBtn',    handler: () => navigate('works') },
            { id: 'showLemmataBtn',  handler: () => navigate('lemmata') },
            { id: 'showConceptsBtn', handler: () => navigate('concepts') },
            { id: 'showGenresBtn',   handler: () => navigate('genres') },
            { id: 'showNamesBtn',    handler: () => navigate('names') }
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
        // UPDATED: Go through the hash router so the URL reflects the current view.
        const teiButtons = [
            { id: 'showWordsBtn',       handler: () => navigate('words') },
            { id: 'showLinesBtn',       handler: () => navigate('lines') },
            { id: 'findMultiLemmaBtn',  handler: () => navigate('multi-lemma') },
            { id: 'showAnnotationsBtn', handler: () => navigate('annotations') }
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
                        <span>Load Full Corpus (667 Files)</span>
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

                // Show file filter for corpus data (useful for 667 files)
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