/**
 * MHDBDB Playground - Main Application Class (MIGRATED)
 * Now using modular UI components instead of monolithic ui-helpers.js
 */

import { AuthorityFilesManager } from './authority-files.js';
import { TEIFilesManager } from './tei-files.js';

// NEW: Import modular UI components (replacing ui-helpers.js)
import { updateAllUI, displayFileItem, showProgress, updateProgress, hideSpinner, setupCollapsibleFileList, setupFileFilter } from './ui/UICore.js';
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

        // Load authority files
        await this.authorityManager.loadAuthorityFiles();

        // Load TEI files from session storage
        await this.loadSessionTEIFiles();

        this.updateUI();
    }

    async loadSessionTEIFiles() {
        try {
            const loadedCount = await this.teiManager.loadFromSession();

            if (loadedCount > 0) {
                console.log(`📁 Restored ${loadedCount} TEI files from session`);

                // Display loaded files in UI
                const uploadedFilesContainer = document.getElementById('uploadedFiles');
                if (uploadedFilesContainer) {
                    this.teiData.files.forEach(file => {
                        if (file && file.isSessionFile) {
                            displayFileItem(file, uploadedFilesContainer);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('❌ Error loading session TEI files:', error);
        }
    }

    // ==================== EVENT LISTENERS (UPDATED) ====================
    
    initializeEventListeners() {
        this.setupFileUpload();
        this.setupAuthorityQueries();
        this.setupTEIQueries();
        this.setupXPathInterface();

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
            { id: 'findMultiLemmaBtn', handler: () => this.ui.teiExplorer.findMultipleLemmasInText() },
            { id: 'findCooccurrenceBtn', handler: () => this.ui.teiExplorer.findCooccurringLemmas() },
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

    setupXPathInterface() {
        // UPDATED: Use new XPath interface
        const xpathExecute = document.getElementById('xpathExecute');
        if (xpathExecute) {
            xpathExecute.addEventListener('click', () => this.ui.xpathInterface.executeXPath());
        } else {
            console.warn('XPath button not found');
        }
    }

    // ==================== TEI FILE HANDLING (UPDATED) ====================

    async handleTEIFiles(files) {
        const fileArray = Array.from(files);
        const uploadedFilesContainer = document.getElementById('uploadedFiles');
        const totalFiles = fileArray.length;
        
        if (totalFiles === 0) return;

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

    removeTEIFile(filename) {
        if (this.teiManager.removeTEIFile(filename)) {
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

    clearAllSessionFiles() {
        const removedCount = this.teiManager.clearAllSessionFiles();

        if (removedCount > 0) {
            // Clear UI
            const uploadedFiles = document.getElementById('uploadedFiles');
            if (uploadedFiles) {
                const sessionFileItems = uploadedFiles.querySelectorAll('[data-session-file="true"]');
                sessionFileItems.forEach(item => item.remove());
            }

            // Update file count and overview
            updateFileCount();
            this.updateUI();

            alert(`Cleared ${removedCount} session files`);
        }
    }

    getStorageInfo() {
        return this.teiManager.getStorageInfo();
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

    console.log('MHDBDB Playground migrated to modular UI successfully!');
    console.log('Available UI modules:', Object.keys(window.playground.ui));
});