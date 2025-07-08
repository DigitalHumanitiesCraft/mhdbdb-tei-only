/**
 * MHDBDB Playground - Main Application Class (MIGRATED)
 * Now using modular UI components instead of monolithic ui-helpers.js
 */

import { AuthorityFilesManager } from './authority-files.js';
import { TEIFilesManager } from './tei-files.js';

// NEW: Import modular UI components (replacing ui-helpers.js)
import { updateAllUI, displayFileItem } from './ui/UICore.js';
import { AuthorityExplorers } from './ui/AuthorityExplorers.js';
import { TEIExplorer } from './ui/TEIExplorer.js';
import { XPathInterface } from './ui/XPathInterface.js';

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
            names: []
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
            authorityExplorers: new AuthorityExplorers(this.authorityData),
            teiExplorer: new TEIExplorer(this.teiData, this.authorityData),
            xpathInterface: new XPathInterface(this.authorityData, this.teiData)
        };

        this.init();
    }

    async init() {
        this.initializeEventListeners();
        await this.authorityManager.loadAuthorityFiles();
        this.updateUI();
    }

    // ==================== EVENT LISTENERS (UPDATED) ====================
    
    initializeEventListeners() {
        this.setupFileUpload();
        this.setupAuthorityQueries();
        this.setupTEIQueries();
        this.setupXPathInterface();
    }

    setupFileUpload() {
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');

        if (!uploadZone || !fileInput) {
            console.error('❌ Upload elements not found');
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
                console.warn(`⚠️ Missing authority button: ${id}`);
            }
        });
    }

    setupTEIQueries() {
        // UPDATED: Use new TEI explorer methods
        const teiButtons = [
            { id: 'showWordsBtn', handler: () => this.ui.teiExplorer.showWords() },
            { id: 'showLinesBtn', handler: () => this.ui.teiExplorer.showLines() },
            { id: 'findLemmaBtn', handler: () => this.ui.teiExplorer.findLemmaInText() },
            { id: 'showAnnotationsBtn', handler: () => this.ui.teiExplorer.showAnnotations() }
        ];

        teiButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            } else {
                console.warn(`⚠️ Missing TEI button: ${id}`);
            }
        });
    }

    setupXPathInterface() {
        // UPDATED: Use new XPath interface
        const xpathExecute = document.getElementById('xpathExecute');
        if (xpathExecute) {
            xpathExecute.addEventListener('click', () => this.ui.xpathInterface.executeXPath());
        } else {
            console.warn('⚠️ XPath button not found');
        }
    }

    // ==================== TEI FILE HANDLING (UPDATED) ====================

    async handleTEIFiles(files) {
        const fileArray = Array.from(files);
        const uploadedFilesContainer = document.getElementById('uploadedFiles');
        
        for (const file of fileArray) {
            if (this.teiManager.isTEIFile(file)) {
                await this.teiManager.processTEIFile(file);
                displayFileItem(file, uploadedFilesContainer); // NEW: Use UICore function
            }
        }
        
        this.updateUI();
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
        window.playground.ui.xpathInterface = window.playground.ui.xpathInterface;
    }

    console.log('🎉 MHDBDB Playground migrated to modular UI successfully!');
    console.log('Available UI modules:', Object.keys(window.playground.ui));
});