/**
 * MHDBDB Playground - Main Application Class (MIGRATED)
 * Now using modular UI components instead of monolithic ui-helpers.js
 */

import { AuthorityFilesManager } from './data/authority-manager.js';
import { TEIFilesManager } from './data/tei-manager.js';

// NEW: Import modular UI components (decomposed from UICore.js)
import { updateAllUI } from './ui/core/ui-helpers.js';
import { initRouter, navigate, dispatchFromHash } from './ui/core/router.js';
import { AuthorityUI } from './ui/authority/authority-ui.js';
import { TEIExplorer } from './ui/tei/tei-ui.js';
import { MultiLemmaSearchUI } from './ui/tei/multi-lemma-search.js';
import { WordFrequencyAnalyzer } from './ui/tei/word-frequency.js';
import { TextStatistics } from './ui/tei/text-statistics.js';
import { LemmaDistribution } from './ui/tei/lemma-distribution.js';
import { VersePositionSearch } from './ui/tei/verse-position-search.js';
import { ConceptDistribution } from './ui/tei/concept-distribution.js';
import { TextComparison } from './ui/tei/text-comparison.js';
import { CooccurrenceRanking } from './ui/tei/cooccurrence-ranking.js';
import { RhymeDictionary } from './ui/tei/rhyme-dictionary.js';
import { HapaxLegomenaAnalyzer } from './ui/tei/hapax-legomena.js';
import { VerseEndingProfileAnalyzer } from './ui/tei/verse-ending-profile.js';
import { NamingExplorer } from './ui/tei/naming-explorer.js';
import { HorsesExplorer } from './ui/tei/horses-explorer.js';

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
        
        // Hier stand bis #325 ein this.teiData mit fünf Feldern (files,
        // parsedXML, words, lines, annotations). Befüllt hat es der
        // Datei-Upload, den #314 zurückgebaut hat; danach hatte kein Feld mehr
        // einen Schreiber. Der Container wurde trotzdem noch durch drei
        // Konstruktoren gereicht und hat damit einen Datenfluss suggeriert,
        // den es nicht mehr gab.

        // Data managers (UNCHANGED)
        this.authorityManager = new AuthorityFilesManager(this.authorityData);
        this.teiManager = new TEIFilesManager();

        // NEW: Modular UI instead of single UIHelpers
        this.ui = {
            authorityExplorers: new AuthorityUI(this.authorityData),
            teiExplorer: new TEIExplorer()
        };

        // Initialize after teiExplorer is created
        this.ui.multiLemmaSearch = new MultiLemmaSearchUI(
            this.ui.teiExplorer,
            this.authorityManager
        );
        const corpusTextsThunk = () => this.corpusData?.texts || this.teiManager.corpusIndex?.texts || [];
        this.ui.wordFrequency = new WordFrequencyAnalyzer(
            corpusTextsThunk,
            this.authorityData
        );
        this.ui.textStatistics = new TextStatistics(corpusTextsThunk);
        this.ui.lemmaDistribution = new LemmaDistribution(corpusTextsThunk, this.authorityManager);
        this.ui.versePositionSearch = new VersePositionSearch(corpusTextsThunk, this.authorityManager);
        this.ui.conceptDistribution = new ConceptDistribution(
            corpusTextsThunk,
            this.authorityManager,
            () => this.authorityData
        );
        this.ui.textComparison = new TextComparison(corpusTextsThunk, this.authorityManager);
        this.ui.cooccurrenceRanking = new CooccurrenceRanking(corpusTextsThunk, this.authorityManager);
        this.ui.rhymeDictionary = new RhymeDictionary(corpusTextsThunk, this.authorityManager);
        this.ui.hapaxLegomena = new HapaxLegomenaAnalyzer(corpusTextsThunk, this.authorityData);
        this.ui.verseEndingProfile = new VerseEndingProfileAnalyzer(corpusTextsThunk, this.authorityData);
        this.ui.namingExplorer = new NamingExplorer('../data');
        this.ui.horsesExplorer = new HorsesExplorer('../data');

        this.init();
    }

    async init() {
        this.initializeEventListeners();

        // #314: Die Datenbank MHDBDB_Playground hielt einen einzigen Store
        // (tei_files) für den Datei-Upload. Der ist weg, damit hat sie keinen
        // Schreiber mehr. Bis #280 räumte eine Schema-Migration hier noch
        // Altstores auf; die lief über den IndexedDBManager, den nach dem
        // Rückbau niemand mehr instanziiert. Statt 397 Zeilen Schema-Pflege
        // für eine leere Datenbank wird sie einmalig gelöscht. Auf einer
        // nicht vorhandenen Datenbank ist das ein No-op, der Aufruf darf
        // also bei jedem Start laufen. Korpus und Authority-Daten liegen in
        // MHDBDBMainSite und sind nicht betroffen.
        // Entfernbar, sobald keine Profile mehr im Umlauf sind, die den
        // Playground vor Juli 2026 geöffnet haben: realistisch ab Mitte 2027.
        // Ohne dieses Datum wird der Aufruf selbst zu dem konservierten
        // Zweig, den #314 gerade entfernt hat.
        this.dropLegacyPlaygroundDatabase();

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

    dropLegacyPlaygroundDatabase() {
        if (!window.indexedDB) return;
        try {
            const req = indexedDB.deleteDatabase('MHDBDB_Playground');
            req.onsuccess = () => console.log('Alt-Datenbank MHDBDB_Playground entfernt (#314)');
            // onblocked heißt: ein anderer Tab hält die Datenbank noch offen.
            // Kein Fehlerfall, der nächste Start erledigt es.
            req.onblocked = () => console.log('MHDBDB_Playground noch von einem anderen Tab belegt');
            req.onerror = () => console.warn('MHDBDB_Playground ließ sich nicht löschen:', req.error);
        } catch (e) {
            console.warn('deleteDatabase auf MHDBDB_Playground hat geworfen:', e);
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

            // Also expose under teiManager.corpusIndex so downstream callers
            // (multi-lemma search, word-frequency, text-statistics,
            // lemma-distribution, future modules) can read from a single
            // canonical location regardless of which loader populated it.
            // See #97.
            this.teiManager.corpusIndex = corpusIndex;

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
        this.setupAuthorityQueries();
        this.setupTEIQueries();
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
            { id: 'findMultiLemmaBtn',       handler: () => navigate('multi-lemma') },
            { id: 'findVersePositionBtn',    handler: () => navigate('verse-position') },
            { id: 'showWordFrequencyBtn',    handler: () => navigate('word-frequency') },
            { id: 'showTextStatisticsBtn',   handler: () => navigate('text-statistics') },
            { id: 'showLemmaDistributionBtn', handler: () => navigate('lemma-distribution') },
            { id: 'showConceptDistributionBtn', handler: () => navigate('concept-distribution') },
            { id: 'showTextComparisonBtn', handler: () => navigate('text-comparison') },
            { id: 'showCooccurrenceRankingBtn', handler: () => navigate('cooccurrence-ranking') },
            { id: 'showRhymeDictionaryBtn', handler: () => navigate('rhyme-dictionary') },
            { id: 'showHapaxLegomenaBtn', handler: () => navigate('hapax-legomena') },
            { id: 'showVerseEndingProfileBtn', handler: () => navigate('verse-ending-profile') },
            { id: 'showNamingExplorerBtn', handler: () => navigate('naming') },
            { id: 'showHorsesExplorerBtn', handler: () => navigate('horses') }
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

    // ==================== UI UPDATES (SIMPLIFIED) ====================

    updateUI() {
        // NEW: Use centralized UI update function
        updateAllUI(this.authorityData);
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

    // Note: The "Load Full Corpus" button was removed in the redesign;
    // autoLoadCorpus() in init() handles corpus loading. See #99.

    console.log('MHDBDB Playground migrated to modular UI successfully!');
    console.log('Available UI modules:', Object.keys(window.playground.ui));
});