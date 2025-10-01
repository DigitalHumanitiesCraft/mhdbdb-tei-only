/**
 * Text Renderer
 * Handles lazy-loading of TEI files and rendering with lemma highlighting
 * Implements jump-to-context navigation
 */

class TextRenderer {
    constructor(corpusIndex, authorityIndex) {
        this.corpusIndex = corpusIndex;
        this.authorityIndex = authorityIndex;

        this.currentTextId = null;
        this.currentLemmaId = null;
        this.currentContexts = [];
        this.currentContextIndex = 0;
        this.elements = null;
    }

    /**
     * Render TEI text with highlighted lemma occurrences
     */
    async renderText(textId, lemmaId, elements) {
        this.currentTextId = textId;
        this.currentLemmaId = lemmaId;
        this.elements = elements;

        console.log(`[TextRenderer] Rendering text: ${textId}, lemma: ${lemmaId}`);

        try {
            // Step 1: Get text metadata from index
            const textMeta = this.corpusIndex.texts.find(t => t.id === textId);

            if (!textMeta) {
                throw new Error(`Text not found: ${textId}`);
            }

            // Step 2: Lazy-load TEI file
            const teiDoc = await this.loadTEIFile(textMeta.filename);

            // Step 3: Find all lemma occurrences
            this.currentContexts = this.findLemmaContexts(teiDoc, lemmaId);

            console.log(`[TextRenderer] Found ${this.currentContexts.length} occurrences`);

            if (this.currentContexts.length === 0) {
                elements.modalContent.innerHTML = '<p class="text-gray-600">Keine Treffer in diesem Text gefunden.</p>';
                this.updateNavigationButtons();
                return;
            }

            // Step 4: Render first context
            this.currentContextIndex = 0;
            this.renderContext();

        } catch (error) {
            console.error('[TextRenderer] Rendering failed:', error);
            elements.modalContent.innerHTML = `<p class="text-red-600">Fehler beim Laden: ${error.message}</p>`;
        }
    }

    /**
     * Lazy-load TEI file from server
     */
    async loadTEIFile(filename) {
        try {
            const response = await fetch(`tei/${filename}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const xmlText = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(xmlText, 'text/xml');

            // Check for parse errors
            const parseError = doc.querySelector('parsererror');
            if (parseError) {
                throw new Error('XML parsing failed');
            }

            return doc;

        } catch (error) {
            console.error(`[TextRenderer] Failed to load ${filename}:`, error);
            throw error;
        }
    }

    /**
     * Find all occurrences of lemma in TEI document
     */
    findLemmaContexts(teiDoc, lemmaId) {
        const contexts = [];

        // Find all <w> elements with matching lemmaRef
        const lemmaRefPattern = `#${lemmaId}`;
        const wordElements = teiDoc.querySelectorAll('w[lemmaRef]');

        wordElements.forEach((wordEl, index) => {
            const lemmaRef = wordEl.getAttribute('lemmaRef');

            // Check if lemmaRef matches: "lexicon.xml#lemma_879" contains "#lemma_879"
            if (lemmaRef && lemmaRef.includes(lemmaRefPattern)) {
                const context = this.extractContext(wordEl, index);
                contexts.push(context);
            }
        });

        return contexts;
    }

    /**
     * Extract surrounding context for a word element
     */
    extractContext(wordEl, wordIndex) {
        const contextWordsBefore = 20;
        const contextWordsAfter = 20;

        // Find parent paragraph or similar structural element
        let contextNode = wordEl.closest('p, div, ab, lg');

        if (!contextNode) {
            contextNode = wordEl.parentElement;
        }

        // Get all words in context
        const allWords = contextNode.querySelectorAll('w');
        const targetIndex = Array.from(allWords).indexOf(wordEl);

        // Extract context window
        const start = Math.max(0, targetIndex - contextWordsBefore);
        const end = Math.min(allWords.length, targetIndex + contextWordsAfter + 1);

        const contextWords = Array.from(allWords).slice(start, end);

        return {
            wordElement: wordEl,
            wordIndex: wordIndex,
            contextWords: contextWords,
            targetWordIndex: targetIndex - start
        };
    }

    /**
     * Render current context with highlighting
     */
    renderContext() {
        const context = this.currentContexts[this.currentContextIndex];

        if (!context) {
            return;
        }

        // Build HTML for context
        const html = context.contextWords.map((wordEl, idx) => {
            const wordText = wordEl.textContent;
            const isTarget = (idx === context.targetWordIndex);

            if (isTarget) {
                return `<span class="highlight-lemma-1 font-bold">${this.escapeHtml(wordText)}</span>`;
            } else {
                return this.escapeHtml(wordText);
            }
        }).join(' ');

        // Render in modal
        this.elements.modalContent.innerHTML = `
            <div class="text-gray-800 leading-relaxed">
                ${html}
            </div>
        `;

        // Update navigation
        this.updateNavigationButtons();

        // Scroll highlighted word into view
        setTimeout(() => {
            const highlighted = this.elements.modalContent.querySelector('.highlight-lemma-1');
            if (highlighted) {
                highlighted.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    }

    /**
     * Navigate to previous/next context
     */
    navigateContext(direction) {
        const newIndex = this.currentContextIndex + direction;

        if (newIndex < 0 || newIndex >= this.currentContexts.length) {
            return;
        }

        this.currentContextIndex = newIndex;
        this.renderContext();
    }

    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        if (!this.elements) return;

        const { prevContext, nextContext, contextIndicator } = this.elements;

        // Update indicator
        if (this.currentContexts.length > 0) {
            contextIndicator.textContent = `Treffer ${this.currentContextIndex + 1} von ${this.currentContexts.length}`;
        } else {
            contextIndicator.textContent = '';
        }

        // Disable/enable buttons
        prevContext.disabled = (this.currentContextIndex === 0);
        nextContext.disabled = (this.currentContextIndex === this.currentContexts.length - 1);
    }

    /**
     * HTML escape utility
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

export { TextRenderer };
