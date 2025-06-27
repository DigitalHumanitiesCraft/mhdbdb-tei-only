/**
 * MHDBDB Playground - Main Application Class
 * Coordinates between authority files, TEI files, and UI components
 */

import { AuthorityFilesManager } from './authority-files.js';
import { TEIFilesManager } from './tei-files.js';
import { UIHelpers } from './ui-helpers.js';

class MHDBDBPlayground {
    constructor() {
        // Data containers
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

        // Initialize managers
        this.authorityManager = new AuthorityFilesManager(this.authorityData);
        this.teiManager = new TEIFilesManager(this.teiData);
        this.ui = new UIHelpers(this.authorityData, this.teiData);

        this.init();
    }

    async init() {
        this.initializeEventListeners();
        await this.authorityManager.loadAuthorityFiles();
        this.updateUI();
    }

    // ==================== EVENT LISTENERS ====================
    
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
        const authorityButtons = [
            { id: 'showAuthorsBtn', handler: () => this.ui.showAuthors() },
            { id: 'showWorksBtn', handler: () => this.ui.showWorks() },
            { id: 'showLemmataBtn', handler: () => this.ui.showLemmata() },
            { id: 'showConceptsBtn', handler: () => this.ui.showConcepts() },
            { id: 'showGenresBtn', handler: () => this.ui.showGenres() },
            { id: 'showNamesBtn', handler: () => this.ui.showNames() }
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
        const teiButtons = [
            { id: 'showWordsBtn', handler: () => this.ui.showWords() },
            { id: 'showLinesBtn', handler: () => this.ui.showLines() },
            { id: 'findLemmaBtn', handler: () => this.ui.findLemmaInText() },
            { id: 'showAnnotationsBtn', handler: () => this.ui.showAnnotations() }
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
        const xpathExecute = document.getElementById('xpathExecute');
        if (xpathExecute) {
            xpathExecute.addEventListener('click', () => this.ui.executeXPath());
        } else {
            console.warn('⚠️ XPath button not found');
        }
    }

    // ==================== TEI FILE HANDLING ====================

    async handleTEIFiles(files) {
        const fileArray = Array.from(files);
        const uploadedFilesContainer = document.getElementById('uploadedFiles');
        
        for (const file of fileArray) {
            if (this.teiManager.isTEIFile(file)) {
                await this.teiManager.processTEIFile(file);
                this.ui.displayFileItem(file, uploadedFilesContainer);
            }
        }
        
        this.updateUI();
    }

    // ==================== UI UPDATES ====================

    updateUI() {
        this.ui.updateStatus('✅', `${this.authorityData.files.length}/6 Authority Files geladen`);
        this.ui.updateAuthorityOverview();
        this.ui.updateTEIOverview();
        this.ui.enableAuthorityQueries();
        
        if (this.teiData.files.length > 0) {
            this.ui.enableTEIQueries();
        }
        
        if (this.authorityData.files.length > 0 && this.teiData.files.length === 0) {
            this.ui.showWelcomeMessage();
        }
    }
}

// Global reference for onclick handlers
window.playground = null;

// Initialize the playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new MHDBDBPlayground();
});