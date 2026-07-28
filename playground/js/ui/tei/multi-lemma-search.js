/**
 * MHDBDB Playground - Multi-Lemma Search UI Controller
 * Handles the modal interface for advanced multi-lemma search
 */

import { getNavigationEpoch } from '../core/router.js';

export class MultiLemmaSearchUI {
    constructor(teiExplorer, authorityManager) {
        this.teiExplorer = teiExplorer;
        this.authorityManager = authorityManager;
        this.lemmas = [];
        this.isOpen = false;

        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.modal = document.getElementById('multiLemmaModal');
        this.lemmaInput = document.getElementById('lemmaInput');
        this.lemmaChips = document.getElementById('lemmaChips');
        this.executeBtn = document.getElementById('executeSearch');
        this.cancelBtn = document.getElementById('cancelSearch');
        this.closeBtn = document.getElementById('closeModal');
        this.proximityControls = document.getElementById('proximityControls');
        this.proximityDistance = document.getElementById('proximityDistance');
        this.searchModeRadios = document.querySelectorAll('input[name="searchMode"]');
    }

    attachEventListeners() {
        // Modal controls
        this.closeBtn.addEventListener('click', () => this.close());
        this.cancelBtn.addEventListener('click', () => this.close());
        this.executeBtn.addEventListener('click', () => this.executeSearch());

        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Lemma input handling
        this.lemmaInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',' || e.key === '+') {
                e.preventDefault();
                this.addLemmaFromInput();
            }
        });

        this.lemmaInput.addEventListener('blur', () => {
            // Add lemma when input loses focus (if there's text)
            if (this.lemmaInput.value.trim()) {
                this.addLemmaFromInput();
            }
        });

        // Search mode change handler
        this.searchModeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.value === 'proximity') {
                    this.proximityControls.style.display = 'block';
                } else {
                    this.proximityControls.style.display = 'none';
                }
            });
        });
    }

    open() {
        this.isOpen = true;
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Focus the input
        setTimeout(() => {
            this.lemmaInput.focus();
        }, 100);
    }

    close() {
        this.isOpen = false;
        this.modal.style.display = 'none';
        document.body.style.overflow = '';

        // Reset form
        this.reset();
    }

    reset() {
        this.lemmas = [];
        this.lemmaInput.value = '';
        this.lemmaChips.innerHTML = '';
        this.executeBtn.disabled = true;

        // Reset to proximity mode (v4.0.0: paragraph mode removed)
        const proximityRadio = document.querySelector('input[name="searchMode"][value="proximity"]');
        if (proximityRadio) {
            proximityRadio.checked = true;
        }
        this.proximityControls.style.display = 'block';
        this.proximityDistance.value = '10';
    }

    addLemmaFromInput() {
        const input = this.lemmaInput.value.trim();
        if (!input) return;

        // Split by comma or plus sign
        const terms = input.split(/[,+]/).map(t => t.trim()).filter(t => t);

        terms.forEach(term => {
            if (term && !this.lemmas.includes(term)) {
                this.lemmas.push(term);
                this.addLemmaChip(term);
            }
        });

        this.lemmaInput.value = '';
        this.updateExecuteButton();
    }

    addLemmaChip(lemma) {
        const chip = document.createElement('div');
        chip.className = 'lemma-chip';
        chip.dataset.lemma = lemma;

        chip.innerHTML = `
            <span>${this.escapeHtml(lemma)}</span>
            <button type="button" aria-label="Remove ${this.escapeHtml(lemma)}">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;

        const removeBtn = chip.querySelector('button');
        removeBtn.addEventListener('click', () => {
            this.removeLemma(lemma);
        });

        this.lemmaChips.appendChild(chip);
    }

    removeLemma(lemma) {
        this.lemmas = this.lemmas.filter(l => l !== lemma);

        // dataset comparison instead of a CSS selector: a lemma containing
        // quotes would throw in querySelector (#audit-66).
        const chip = [...this.lemmaChips.children].find(ch => ch.dataset && ch.dataset.lemma === lemma);
        if (chip) {
            chip.style.animation = 'chipOut 200ms ease-in forwards';
            setTimeout(() => {
                chip.remove();
            }, 200);
        }

        this.updateExecuteButton();
    }

    updateExecuteButton() {
        this.executeBtn.disabled = this.lemmas.length === 0;
    }

    getSelectedSearchMode() {
        const selected = document.querySelector('input[name="searchMode"]:checked');
        return selected ? selected.value : 'proximity'; // v4.0.0: default to proximity
    }

    async executeSearch() {
        if (this.lemmas.length === 0) return;

        const searchMode = this.getSelectedSearchMode();
        const searchTerms = [...this.lemmas]; // Create copy

        // Close modal first
        this.close();

        // Show loading immediately
        const resultsContainer = document.getElementById('resultsContainer');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="loading-overlay" style="position: relative;">
                    <div class="spinner spinner-large"></div>
                    <p class="loading-message">Durchsuche TEI-Texte...</p>
                </div>
            `;
        }

        // Get TEI manager
        const teiManager = window.playground?.teiManager;
        if (!teiManager) {
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                        Fehler: TEI Manager nicht verfügbar. Bitte laden Sie TEI-Dateien.
                    </div>
                `;
            }
            return;
        }

        // Guard analog zu den 8 Schwester-Tools: vor dem Corpus-Load liefert
        // die Suche sonst still leere Ergebnisse (#167 Finding 22).
        if (!window.playground?.corpusData?.texts?.length) {
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="text-sm text-red-600">
                        Korpus ist noch nicht geladen. Bitte einen Moment warten und erneut suchen.
                    </div>
                `;
            }
            return;
        }

        // Navigiert der User während der async Korpus-Suche zu einer
        // anderen View, darf das fertige Ergebnis die dort angezeigte
        // View nicht überschreiben (#159). Vor dem try deklariert, damit
        // auch der catch-Pfad den Guard prüfen kann.
        const myEpoch = getNavigationEpoch();

        try {
            // Resolve lemma IDs
            const lemmaIds = this.teiExplorer.resolveLemmaIds(searchTerms);

            if (lemmaIds.length === 0) {
                if (resultsContainer) {
                    resultsContainer.innerHTML = `
                        <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                            Keine gültigen Lemmata gefunden für: ${searchTerms.map(t => this.escapeHtml(t)).join(', ')}
                        </div>
                    `;
                }
                return;
            }

            // Execute search based on mode (now async)
            // Use fast index-based search when available (corpus index)
            let results;
            if (searchMode === 'proximity') {
                const maxDistance = parseInt(this.proximityDistance.value) || 10;
                // Try fast index-based search first (falls back to XML if needed)
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, 'proximity', maxDistance);
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayCooccurrenceResults(results, searchTerms, maxDistance, lemmaIds);
            } else if (searchMode === 'verse') {
                // #106 Punkt 8: Kookkurrenz auf ein gemeinsames <l> beschränkt
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, 'verse');
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayCooccurrenceResults(results, searchTerms, null, lemmaIds, { verseMode: true });
            } else {
                // Use fast index-based search for paragraph/document mode
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, searchMode);
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayMultiLemmaResults(results, searchTerms, searchMode);
            }

        } catch (error) {
            console.error('Search error:', error);
            // Gleicher Epoch-Guard wie in den Success-Pfaden: eine nach dem
            // View-Wechsel fehlschlagende Suche darf die neue View nicht mit
            // der Fehlermeldung überschreiben (Review-Finding PR #174).
            if (getNavigationEpoch() !== myEpoch) return;
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                        Suchfehler: ${this.escapeHtml(String(error.message))}
                    </div>
                `;
            }
        }
    }

    // Regex-based instead of the textContent/innerHTML trick: the value is
    // also interpolated into attribute contexts (aria-label), where unescaped
    // quotes would break out of the attribute (#audit-66).
    escapeHtml(text) {
        if (text == null) return '';
        return String(text).replace(/[&<>"']/g, c => (
            { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
        ));
    }
}

// Add chipOut animation to CSS (will be added via style tag if needed)
if (!document.querySelector('#chipOut-keyframes')) {
    const style = document.createElement('style');
    style.id = 'chipOut-keyframes';
    style.textContent = `
        @keyframes chipOut {
            to {
                opacity: 0;
                transform: scale(0.8);
            }
        }
    `;
    document.head.appendChild(style);
}