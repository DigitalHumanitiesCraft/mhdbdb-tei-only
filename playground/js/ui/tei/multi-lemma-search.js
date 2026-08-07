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

        // Schreibform -> feste Lemma-ID (#58). Wer aus dem Lemmata-Explorer
        // kommt, hat ein bestimmtes Lemma angeklickt; die Auflösung über die
        // Schreibform nimmt dagegen matches[0]. Gemessen am 2026-08-07 über
        // authority-files/lexicon.xml, gruppiert mit normalize_mhg() aus
        // scripts/mhg_normalizer.py: 477 normalisierte Formen tragen mehr
        // als einen Eintrag, zusammen 993 der 43.879 Lemmata (2,26 Prozent),
        // darunter sin, wal, mal und de. Für die stünde hier sonst still ein
        // anderes Lemma. Gefüllt wird die Map nur vom Router, nie von einer
        // Handeingabe: siehe addLemmaFromInput.
        this.lemmaIdHints = new Map();

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
        this.lemmaIdHints.clear();
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
                // Eine Handeingabe ist eine Schreibform und sonst nichts. Trägt
                // die Map noch einen Zeiger unter demselben Label (erst die
                // Route, dann ein zweites Lemma von Hand), würde die Eingabe
                // still die ID der Route erben.
                this.lemmaIdHints.delete(term);
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
        this.lemmaIdHints.delete(lemma);

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

    /**
     * Suchbegriffe zu Lemma-IDs auflösen, mit Vorrang für gesetzte Zeiger.
     *
     * Der einzige Unterschied zu `resolveLemmaIds` ist dieser Vorrang. Er muss
     * an jeder Stelle gelten, die aus Begriffen IDs macht, auch in der
     * Fehlerdiagnose weiter unten: sonst meldet die „kein Lemma gefunden"-Zeile
     * einen Begriff als unauflösbar, dessen ID feststeht.
     *
     * `zeiger` wird ausdrücklich übergeben und nicht aus `this` gelesen.
     * `executeSearch` schließt das Modal, bevor es auflöst, und `close()` leert
     * über `reset()` auch diese Map: ein Zugriff auf `this.lemmaIdHints` fände
     * hier also immer eine leere Map vor. Genau denselben Grund nennt der
     * Kommentar an `searchTerms` schon für die Begriffsliste.
     *
     * Dedupliziert wie das Original, aus demselben Grund (siehe dort): zwei
     * Eingaben auf derselben ID lassen die Nähesuche jede Fundstelle mit
     * Abstand 0 melden.
     *
     * @param {string[]} terms
     * @param {Map<string, string>} zeiger Schreibform -> feste Lemma-ID
     * @returns {string[]} Lemma-IDs ohne `lemma_`-Präfix
     */
    resolveTerms(terms, zeiger) {
        const ids = terms.flatMap(term =>
            zeiger.has(term)
                ? [zeiger.get(term)]
                : this.teiExplorer.resolveLemmaIds([term])
        );
        return [...new Set(ids)];
    }

    getSelectedSearchMode() {
        const selected = document.querySelector('input[name="searchMode"]:checked');
        return selected ? selected.value : 'proximity'; // v4.0.0: default to proximity
    }

    async executeSearch() {
        if (this.lemmas.length === 0) return;

        const searchMode = this.getSelectedSearchMode();
        const searchTerms = [...this.lemmas]; // Create copy
        // Aus demselben Grund kopiert wie die Begriffe eine Zeile darüber:
        // close() setzt über reset() auch die Zeiger zurück (#58).
        const zeiger = new Map(this.lemmaIdHints);

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
            const lemmaIds = this.resolveTerms(searchTerms, zeiger);

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

            // Nähe- und Vers-Suche brauchen zwei VERSCHIEDENE Lemmata. Nach
            // der Auflösung können mehrere Eingaben auf dasselbe Lemma zeigen
            // („wîn" und „wein" beide auf lemma_7532), und mit nur einer ID
            // sucht die Fensterlogik ein Fenster ohne weitere abzudeckende
            // Liste: das leistet jede Position, jede Fundstelle würde als
            // Treffer mit Abstand 0 gemeldet. Lieber sagen, was los ist.
            if ((searchMode === 'proximity' || searchMode === 'verse') && lemmaIds.length < 2) {
                if (resultsContainer) {
                    // Zwei sehr verschiedene Ursachen führen hierher, und die
                    // falsche Diagnose schickt jemanden auf die Suche nach
                    // einer Homonymie, die es nicht gibt: „minne" + „qqqq"
                    // ergibt ebenfalls eine ID, weil der zweite Begriff
                    // überhaupt nicht auflöst. Deshalb je Begriff einzeln
                    // nachfragen; das kostet nur in diesem Fehlerfall etwas.
                    const ohneTreffer = searchTerms.filter(
                        t => this.resolveTerms([t], zeiger).length === 0
                    );
                    const grund = ohneTreffer.length > 0
                        ? `Kein Lemma gefunden für: ${ohneTreffer.map(t => this.escapeHtml(t)).join(', ')}.`
                        : searchTerms.length > 1
                            ? `Ihre Eingaben (${searchTerms.map(t => this.escapeHtml(t)).join(', ')}) führen auf dasselbe Lemma.`
                            : 'Es ist nur ein Lemma angegeben.';
                    resultsContainer.innerHTML = `
                        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                            Diese Suche vergleicht die Fundstellen zweier Lemmata und braucht deshalb zwei verschiedene. ${grund}
                            Für die Belege eines einzelnen Lemmas eignet sich die Suche über das ganze Dokument.
                        </div>
                    `;
                }
                return;
            }

            // Execute search based on mode (now async)
            // Alle drei Modi lesen den vorgebauten Korpus-Index. Den XML-Fallback
            // gab es bis #314; faellt der Index aus, wirft die Suche jetzt und
            // der catch unten zeigt das an.
            let results;
            if (searchMode === 'proximity') {
                const maxDistance = parseInt(this.proximityDistance.value) || 10;
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, 'proximity', maxDistance);
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayCooccurrenceResults(results, searchTerms, maxDistance, lemmaIds);
            } else if (searchMode === 'verse') {
                // #106 Punkt 8: Kookkurrenz auf ein gemeinsames <l> beschränkt
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, 'verse');
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayCooccurrenceResults(results, searchTerms, null, lemmaIds, { verseMode: true });
            } else {
                // Dokumentweite Suche über den Index
                results = await teiManager.searchMultipleLemmasUsingIndex(lemmaIds, searchMode);
                if (getNavigationEpoch() !== myEpoch) return;
                this.teiExplorer.displayMultiLemmaResults(results, searchTerms);
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