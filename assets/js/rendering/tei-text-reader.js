/**
 * TEI Text Reader
 * Unified reading view for TEI texts with optional search highlighting
 * Replaces snippet-based context view with full-text reading experience
 *
 * Metadata Source: Prioritizes TEI header data, falls back to corpus index for missing fields
 */

import { lemmaRefMatchesId } from '../lib/lemma-match.js';

class TEITextReader {
    constructor(corpusIndex, authorityIndex, cache) {
        this.corpusIndex = corpusIndex;
        this.authorityIndex = authorityIndex;
        this.cache = cache; // Reuse TextRenderer's TEICacheManager

        this.currentTextId = null;
        this.currentLemmaId = null;
        this.currentLemmaIds = []; // Support multiple lemmas
        this.currentHighlights = [];
        this.currentHighlightIndex = 0;
        this.elements = null;

        // Color scheme for multi-lemma highlighting (matches playground proximity colors)
        this.lemmaColors = [
            { bg: '#fecaca', text: '#991b1b', border: '#ef4444' }, // Red
            { bg: '#bfdbfe', text: '#1e3a8a', border: '#3b82f6' }, // Blue
            { bg: '#bbf7d0', text: '#166534', border: '#22c55e' }, // Green
            { bg: '#fde68a', text: '#92400e', border: '#f59e0b' }, // Yellow
            { bg: '#ddd6fe', text: '#5b21b6', border: '#8b5cf6' }, // Purple
        ];
    }

    /**
     * Open reading view modal
     * @param {string} textId - Text ID to display
     * @param {object} options - { lemmaId: string, lemmaIds: string[], targetPosition: number, targetVerse: string } for highlighting / verse jump (optional)
     * @param {object} elements - DOM element references
     */
    async openReadingView(textId, options = {}, elements) {
        // Request-Generation-Guard (#168): Öffnet der User während eines
        // langsamen Ladevorgangs (großes, ungecachtes TEI) einen anderen
        // Text (z.B. Sigle-Link), darf der ältere Ladevorgang nach seinem
        // await weder DOM noch Instanz-State überschreiben — sonst zeigen
        // Lesebereich, aktive Sigle und Treffer-Navigation verschiedene Werke.
        const mySeq = (this._loadSeq = (this._loadSeq || 0) + 1);

        this.currentTextId = textId;

        // Support both single lemmaId and multiple lemmaIds
        if (options.lemmaIds && Array.isArray(options.lemmaIds)) {
            this.currentLemmaIds = options.lemmaIds.map(id => id.toString());
            this.currentLemmaId = null; // Clear single mode
        } else if (options.lemmaId) {
            this.currentLemmaId = options.lemmaId;
            this.currentLemmaIds = []; // Clear multi mode
        } else {
            this.currentLemmaId = null;
            this.currentLemmaIds = [];
        }

        this.targetPosition = options.targetPosition || null;
        this.targetVerse = options.targetVerse || null;
        this.elements = elements;

        const lemmaInfo = this.currentLemmaIds.length > 0
            ? ` (highlighting ${this.currentLemmaIds.length} lemmas)`
            : this.currentLemmaId ? ` (highlighting: ${this.currentLemmaId})` : '';
        console.log(`[TEITextReader] Opening reading view: ${textId}${lemmaInfo}`);

        try {
            // Get text metadata from corpus index (for filename)
            const textMeta = this.corpusIndex.texts.find(t => t.id === textId);
            if (!textMeta) {
                throw new Error(`Text not found: ${textId}`);
            }

            // Show modal with loading state
            this.showPanel();
            this.showLoading(true);

            // Load TEI file (cached)
            const teiDoc = await this.loadTEIFile(textMeta.filename);

            // Ein neuerer openReadingView-Aufruf hat inzwischen übernommen —
            // dieser ältere Ladevorgang darf nichts mehr rendern.
            if (mySeq !== this._loadSeq) return;

            // Extract metadata (prioritizes TEI header, falls back to corpus index)
            const metadata = this.extractMetadata(teiDoc, textMeta);

            // Extract and format body text (with optional highlighting)
            const bodyResult = this.extractAndFormatBody(
                teiDoc,
                this.currentLemmaId,
                this.currentLemmaIds
            );

            // Populate modal
            this.populateModal(textId, metadata, bodyResult);

            // Setup navigation if highlights exist
            if (bodyResult.highlights.length > 0) {
                this.currentHighlights = bodyResult.highlights;

                // If targetPosition specified, find closest highlight
                if (this.targetPosition !== null) {
                    this.currentHighlightIndex = this.findClosestHighlight(this.targetPosition);
                } else {
                    this.currentHighlightIndex = 0;
                }

                this.showNavigation(true);
                this.updateNavigationButtons();

                // Scroll to target or first highlight after brief delay (wait for DOM to render)
                // — ein expliziter Vers-Deep-Link gewinnt gegen den Highlight-Scroll.
                if (this.targetVerse === null) {
                    setTimeout(() => this.scrollToHighlight(this.currentHighlightIndex), 600);
                }
            } else {
                this.showNavigation(false);
            }

            // Vers-Deep-Link (#59): zur Verszeile <l n="..."> scrollen
            if (this.targetVerse !== null) {
                setTimeout(() => this.scrollToVerse(this.targetVerse), 600);
            }

            // Hide loading
            this.showLoading(false);

        } catch (error) {
            console.error('[TEITextReader] Failed to open reading view:', error);
            // Fehler eines überholten Ladevorgangs nicht anzeigen — sie
            // würden Loading-State/Anzeige des neueren Aufrufs zerstören.
            if (mySeq !== this._loadSeq) return;
            this.showLoading(false);
            this.showError(`Fehler beim Laden: ${error.message}`);
        }
    }

    /**
     * Load TEI file (cached in IndexedDB, revalidated per load — #151)
     */
    async loadTEIFile(filename) {
        try {
            const startTime = Date.now();
            const doc = await this.cache.load(filename);
            console.log(`[TEITextReader] Loaded ${filename} in ${((Date.now() - startTime) / 1000).toFixed(1)}s`);
            return doc;
        } catch (error) {
            console.error(`[TEITextReader] Failed to load ${filename}:`, error);
            throw error;
        }
    }

    /**
     * Extract comprehensive metadata from authority index (primary) and TEI header (fallback)
     * Strategy: msIdentifier/@corresp → works.xml#work_XXX → authority index lookup
     */
    extractMetadata(teiDoc, textMeta) {
        const metadata = {
            // Basic info
            title: textMeta.title || 'Unbekannter Titel',
            titles: [],
            author: textMeta.author || 'Unbekannt',
            sigle: textMeta.id || '',

            // Work info (from authority index)
            workId: null,
            allSigles: [],
            genres: [],

            // Author info (from authority index)
            authorId: null,
            authorGnd: null,
            authorWikidata: null,
            otherWorks: [],

            // Work identifiers (from authority index)
            workGnd: null,
            workWikidata: null,

            // Editions (from authority index)
            editions: [],

            // External links
            handschriftencensus: null,
            zoteroLinks: [],

            // Excerpt relationship (from TEI header biblStruct, #134)
            excerpt: null
        };

        try {
            // 1. Extract work reference from TEI header
            const msIdentifier = teiDoc.querySelector('msIdentifier[corresp]');
            if (msIdentifier) {
                const corresp = msIdentifier.getAttribute('corresp');
                // Extract work ID: "works.xml#work_131" → "work_131"
                if (corresp && corresp.includes('#')) {
                    metadata.workId = corresp.split('#')[1];
                }
            }

            // 1b. Excerpt relationship (#134): a text is an excerpt of a larger
            // work iff its header biblStruct carries a verse range
            // (biblScope unit="verse"). An <analytic> title alone is NOT
            // sufficient — 534 corpus headers have one for ordinary
            // journal/book-section editions. Headers may carry SEVERAL
            // biblStruct entries (book + bookSection, e.g. FB/HZ/WZB), so the
            // verse-scoped one is searched for across all of them, not just
            // the first in document order.
            const excerptBibl = Array.from(teiDoc.querySelectorAll('sourceDesc biblStruct'))
                .find(bs => Array.from(bs.querySelectorAll('imprint biblScope'))
                    .some(scope => scope.getAttribute('unit') === 'verse'));
            if (excerptBibl) {
                const verseScope = Array.from(excerptBibl.querySelectorAll('imprint biblScope'))
                    .find(bs => bs.getAttribute('unit') === 'verse');
                const analyticTitle = excerptBibl.querySelector('analytic > title');
                if (verseScope && analyticTitle && analyticTitle.textContent.trim()) {
                    const contextNote = Array.from(excerptBibl.querySelectorAll('note'))
                        .find(n => n.getAttribute('type') === 'context');
                    metadata.excerpt = {
                        title: analyticTitle.textContent.trim(),
                        verseRange: verseScope.textContent.trim(),
                        context: contextNote ? contextNote.textContent.trim() : null
                    };
                } else {
                    // Authoring-Signal statt stillem No-op: der Banner lebt rein
                    // von kuratierten Header-Daten — fehlt der analytic-Titel
                    // zum Versbereich, soll das beim Kuratieren auffallen,
                    // nicht erst in der manuellen QA (Review-Finding PR #178).
                    console.warn('[TEITextReader] biblScope unit="verse" gefunden, aber kein <analytic><title> — Excerpt-Banner wird nicht angezeigt.');
                }
            }

            // 2. Look up work in authority index
            if (metadata.workId && this.authorityIndex.works) {
                const work = this.authorityIndex.works.find(w => w.id === metadata.workId);

                if (work) {
                    // Primary title
                    metadata.title = work.title || metadata.title;

                    // All titles (including alternates)
                    if (work.titles && Array.isArray(work.titles)) {
                        metadata.titles = work.titles;
                    }

                    // All sigles
                    if (work.sigles && Array.isArray(work.sigles)) {
                        metadata.allSigles = work.sigles;
                    } else if (work.sigle) {
                        metadata.allSigles = work.sigle.split(',').map(s => s.trim());
                    }

                    // All genres
                    if (work.genres && Array.isArray(work.genres)) {
                        metadata.genres = work.genres;
                    }

                    // Author reference
                    if (work.authorRef) {
                        metadata.authorId = work.authorRef.includes('#') ?
                            work.authorRef.split('#')[1] : work.authorRef;
                        metadata.author = work.author || metadata.author;
                    }

                    // Editions (biblStructs)
                    if (work.biblStructs && Array.isArray(work.biblStructs)) {
                        metadata.editions = work.biblStructs.map(bibl => ({
                            key: bibl.key || '',
                            zoteroLink: bibl.corresp || null,
                            text: bibl.textContent || ''
                        }));

                        // Collect Zotero links
                        metadata.zoteroLinks = work.biblStructs
                            .filter(b => b.corresp)
                            .map(b => b.corresp);
                    }

                    // Handschriftencensus link
                    if (work.handschriftencensus) {
                        metadata.handschriftencensus = work.handschriftencensus;
                    }

                    // GND and Wikidata from work (if available)
                    if (work.gnd) {
                        metadata.workGnd = work.gnd;
                    }
                    if (work.wikidata) {
                        metadata.workWikidata = work.wikidata;
                    }

                    console.log('[TEITextReader] Found work in authority index:', metadata.workId);
                }
            }

            // 3. Look up author in authority index
            if (metadata.authorId && this.authorityIndex.persons) {
                const person = this.authorityIndex.persons.find(p => p.id === metadata.authorId);

                if (person) {
                    metadata.author = person.preferredName || metadata.author;
                    metadata.authorGnd = person.gnd || null;
                    metadata.authorWikidata = person.wikidata || null;

                    // Parse other works (can be comma-separated)
                    if (person.works) {
                        metadata.otherWorks = person.works.split(',').map(w => w.trim());
                    }

                    console.log('[TEITextReader] Found author in authority index:', metadata.authorId);
                }
            }

            // 4. Fallback: Extract from TEI header if authority index lookup failed
            if (!metadata.workId) {
                console.warn('[TEITextReader] No work reference found, using TEI header fallback');

                // Title fallback
                const titleEl = teiDoc.querySelector('titleStmt > title');
                if (titleEl) {
                    metadata.title = titleEl.textContent.trim();
                }

                // Author fallback
                const authorEl = teiDoc.querySelector('titleStmt > author');
                if (authorEl) {
                    metadata.author = authorEl.textContent.trim();
                }

                // Genre fallback (from TEI taxonomy)
                const genreEls = teiDoc.querySelectorAll('category[xml\\:id*="genre"] gloss[xml\\:lang="de"]');
                metadata.genres = Array.from(genreEls).map(el => ({
                    text: el.textContent.trim()
                }));
            }

        } catch (error) {
            console.error('[TEITextReader] Error extracting metadata:', error);
        }

        console.log('[TEITextReader] Extracted metadata:', metadata);
        return metadata;
    }

    /**
     * Extract and format body text with TEI structure preservation
     * Handles: <head>, <p>, <div>, <lg>, <l>, <lb>, <pb>, <hi rend="...">, <pc>, <seg>
     * @returns {object} { html: string, highlights: Array<{element, position}> }
     */
    extractAndFormatBody(teiDoc, lemmaId = null, lemmaIds = []) {
        const body = teiDoc.querySelector('body');
        if (!body) {
            return { html: '<p class="text-gray-600">Kein Textinhalt gefunden.</p>', highlights: [] };
        }

        const highlights = [];
        const state = { wordPosition: 0, firstNumericLineShown: false }; // Use object to pass by reference

        // Create lemma-to-color mapping for multi-lemma mode
        const lemmaColorMap = {};
        if (lemmaIds.length > 0) {
            lemmaIds.forEach((id, idx) => {
                lemmaColorMap[id] = this.lemmaColors[idx % this.lemmaColors.length];
            });
        }

        // Render a single TEI element to HTML (single path for both top-level and recursive)
        this._renderElement = (el) => {
            const tagName = el.tagName.toLowerCase();
            const children = () => this.processChildren(el, lemmaId, lemmaIds, lemmaColorMap, highlights, state);

            switch (tagName) {
                case 'head':
                    return `<h3 class="section-head">${children()}</h3>`;
                case 'p':
                case 'ab':
                    return `<p>${children()}</p>`;
                case 'div': {
                    const divType = el.getAttribute('type') || '';
                    const divN = el.getAttribute('n') || '';
                    const divLabels = {
                        'song': 'Lied', 'chapter': 'Kapitel', 'recipe': 'Rezept',
                        'number': 'Nr.', 'section': 'Abschnitt',
                        'colophon': 'Kolophon', 'parallel': 'Parallelüberlieferung'
                    };
                    const label = divLabels[divType];
                    let header = '';
                    if (divType === 'chapter') {
                        // Chapter headings render like <head> (h3.section-head)
                        const heading = label && divN ? `${label} ${divN}` : label || divN;
                        if (heading) header = `<h3 class="section-head">${this.escapeHtml(heading)}</h3>`;
                    } else if (label && divN) {
                        header = `<div class="tei-div-header tei-div-${this.escapeHtml(divType)}">${this.escapeHtml(label)} ${this.escapeHtml(divN)}</div>`;
                    } else if (label) {
                        header = `<div class="tei-div-header tei-div-${this.escapeHtml(divType)}">${this.escapeHtml(label)}</div>`;
                    }
                    return `<div class="tei-div tei-div-${this.escapeHtml(divType)}" data-type="${this.escapeHtml(divType)}" data-n="${this.escapeHtml(divN)}">${header}${children()}</div>`;
                }
                case 'lg': {
                    const lgN = el.getAttribute('n') || '';
                    const lgLabel = lgN ? `<span class="stanza-label">Strophe ${this.escapeHtml(lgN)}</span>` : '';
                    return `<div class="verse-group" data-n="${this.escapeHtml(lgN)}">${lgLabel}${children()}</div>`;
                }
                case 'l': {
                    const lineN = el.getAttribute('n') || '';
                    // Marginal line number: the first verse line carrying a numeric
                    // @n (anchor) and thereafter every 5th by ABSOLUTE @n, not render
                    // order. Non-numeric @n (e.g. ALX heading lines "h_1") and bare
                    // <l> without @n (WZB prose) get no number; stanza-local resets
                    // (NBB l@n=1..4) never hit %5, so they keep only their "Strophe N"
                    // labels and avoid a jumbled margin. See #127.
                    const isNumeric = /^\d+$/.test(lineN);
                    // First numeric line (anchor) shows, then every 5th by absolute
                    // @n. Once the anchor fires the flag stays set, so afterwards only
                    // the %5 branch matters.
                    const showNumber = isNumeric &&
                        (!state.firstNumericLineShown || parseInt(lineN, 10) % 5 === 0);
                    if (showNumber) state.firstNumericLineShown = true;
                    const cls = showNumber ? 'verse-line verse-line-numbered' : 'verse-line';
                    return `<span class="${cls}" data-n="${this.escapeHtml(lineN)}">${children()}</span>`;
                }
                case 'lb': {
                    const lbN = el.getAttribute('n') || '';
                    // Nur numerische @n als sichtbare Marginal-Nummer
                    // (.lb-number), analog zur <l>-Policy (#127). Technische
                    // Kennungen wie "h_1" (Heading-Zeilen) rendern als eigener
                    // .lb-anchor: kein Label, keine Margin-Box — aber data-n
                    // bleibt erhalten, damit ?verse=-Deep-Links auf Prosa-
                    // Zeilen (Druckzeilen-Zählung) weiter auflösen (#143).
                    // Vorher lieferten h_-Zeilen leere .lb-number-Spans, die
                    // .lb-number-Konsumenten (Tests, CSS-Margin) als sichtbare
                    // Nummern missverstanden (#158/#162).
                    if (lbN) {
                        if (/^\d+$/.test(lbN)) {
                            return `<br class="line-break"><span class="lb-number" data-n="${this.escapeHtml(lbN)}">${this.escapeHtml(lbN)}</span>`;
                        }
                        return `<br class="line-break"><span class="lb-anchor" data-n="${this.escapeHtml(lbN)}"></span>`;
                    }
                    return '<br class="line-break">';
                }
                case 'note': {
                    const noteType = el.getAttribute('type');
                    const noteN = el.getAttribute('n') || '';
                    if ((noteType === 'date' || noteType === 'year') && noteN) {
                        // Badge + Kindinhalt (#170): date/year-Notes sind heute
                        // self-closing, aber ein künftig lemmatisiertes <w> darin
                        // zählt im Python-Index und in KWIC mit (CONTRACTS §B) —
                        // das Badge allein würde es im Reader verschlucken und
                        // alle Highlights dahinter verschieben.
                        return `<span class="note-badge note-${this.escapeHtml(noteType)}" title="${noteType === 'date' ? 'Datum' : 'Jahr'}">${this.escapeHtml(noteN)}</span>${children()}`;
                    }
                    return children();
                }
                case 'pb': {
                    const pageNum = el.getAttribute('n');
                    return pageNum ? `<span class="page-break" title="Seite ${pageNum}">[${pageNum}]</span>` : '';
                }
                case 'hi': {
                    const rend = el.getAttribute('rend');
                    return this.processHi(el, rend, lemmaId, lemmaIds, lemmaColorMap, highlights, state);
                }
                case 'pc': {
                    const join = el.getAttribute('join') || 'left';
                    return `<span class="punctuation" data-join="${join}">${this.escapeHtml(el.textContent)}</span>`;
                }
                case 'seg':
                    return children();
                case 'w': {
                    const hasLemmaRef = el.getAttribute('lemmaRef');
                    // Position parity with the Python build (CONTRACTS §B): only a
                    // <w lemmaRef> with non-empty text content is counted. The build
                    // skips empty ones (build-corpus-index.py: `if not text_content:
                    // continue`); without this guard a future ingest with placeholder/
                    // gap tokens would shift every later position relative to the index,
                    // breaking hit-navigation and proximity search. 0 corpus cases today
                    // -> no-op on current data. Enforced by position-parity.spec.js (#131).
                    const hasText = el.textContent.trim().length > 0;
                    const result = this.processWord(el, lemmaId, lemmaIds, lemmaColorMap, highlights, state);
                    if (hasLemmaRef && hasText) {
                        state.wordPosition++;
                    }
                    return result;
                }
                case 'cb': {
                    const colNum = el.getAttribute('n');
                    return colNum
                        ? `<span class="column-break" title="Spalte ${colNum}">[Sp. ${this.escapeHtml(colNum)}]</span>`
                        : '<span class="column-break">[Sp.]</span>';
                }
                case 'milestone': {
                    const unit = el.getAttribute('unit') || '';
                    const msN = el.getAttribute('n') || '';
                    if (unit === 'verse' && msN) {
                        return `<span class="verse-marker" title="Vers ${this.escapeHtml(msN)}">${this.escapeHtml(msN)}</span>`;
                    }
                    return '';
                }
                case 'caesura':
                    return '<span class="caesura" title="Zäsur">||</span>';
                case 'supplied':
                    return `<span class="supplied" title="Editorische Ergänzung">[${children()}]</span>`;
                case 'num':
                    return `<span class="number">${children()}</span>`;
                default:
                    return children();
            }
        };

        // Build HTML from body
        let html = '';
        const children = Array.from(body.children);

        for (const child of children) {
            html += this._renderElement(child);
        }

        // Join punctuation to adjacent words based on @join attribute:
        // join="left" → remove whitespace before (attach to preceding word)
        //   Pass 1: whitespace directly before the punctuation span
        //   Pass 2: trailing space inside a preceding element (e.g. <span>word </span><pc>)
        // join="right" → remove whitespace after (attach to following word)
        html = html.replace(/\s+(<span class="punctuation" data-join="left">)/g, '$1');
        html = html.replace(/(\S)\s+(<\/\w+>\s*<span class="punctuation" data-join="left">)/g, '$1$2');
        html = html.replace(/(<span class="punctuation" data-join="right">[^<]*<\/span>)\s+/g, '$1');

        // Detect verse vs prose context
        const hasVerse = !!body.querySelector('lg');

        return { html, highlights, hasVerse };
    }

    /**
     * Process <hi> element with rend attribute — token-based for compound values
     */
    processHi(el, rend, lemmaId, lemmaIds, lemmaColorMap, highlights, state) {
        const content = this.processChildren(el, lemmaId, lemmaIds, lemmaColorMap, highlights, state);
        if (!rend) return `<span class="hi">${content}</span>`;

        const tokens = rend.split(/\s+/);
        const classes = tokens.map(t => `hi-${t}`).join(' ');
        return `<span class="hi ${classes}">${content}</span>`;
    }

    /**
     * Process word element with potential highlighting
     * Supports both single-lemma and multi-lemma with color coding
     */
    processWord(wordEl, lemmaId, lemmaIds, lemmaColorMap, highlights, state) {
        const wordText = wordEl.textContent.trim();
        const lemmaRef = wordEl.getAttribute('lemmaRef');
        const currentPosition = state.wordPosition;
        // Highlight on exact @lemmaRef token match (CONTRACTS §B.1) — never a
        // substring, which would wrongly match "lemma_308" inside "lemma_3089"
        // (jâmer) and inflate the hit counter. See #126.

        // Multi-lemma mode: check all lemmaIds with colors
        if (lemmaIds.length > 0 && lemmaRef) {
            for (const searchLemmaId of lemmaIds) {
                if (lemmaRefMatchesId(lemmaRef, searchLemmaId)) {
                    const color = lemmaColorMap[searchLemmaId];
                    const id = `highlight-${highlights.length}`;
                    highlights.push({ id, element: null, position: currentPosition }); // Track position

                    // Inline style matching playground proximity highlighting
                    const style = `background-color: ${color.bg}; color: ${color.text}; border-bottom: 2px solid ${color.border}; padding: 2px 4px; border-radius: 3px; font-weight: 500;`;
                    return `<mark class="highlight multi-lemma" id="${id}" style="${style}">${this.escapeHtml(wordText)}</mark> `;
                }
            }
        }

        // Single lemma mode: standard highlighting
        if (lemmaId && lemmaRef) {
            if (lemmaRefMatchesId(lemmaRef, lemmaId)) {
                const id = `highlight-${highlights.length}`;
                highlights.push({ id, element: null, position: currentPosition }); // Track position
                return `<mark class="highlight" id="${id}">${this.escapeHtml(wordText)}</mark> `;
            }
        }

        return this.escapeHtml(wordText) + ' ';
    }

    /**
     * Process children of element recursively, delegating element rendering
     * to the _renderElement closure set up by extractAndFormatBody().
     * Must only be called within an extractAndFormatBody() call chain.
     */
    processChildren(el, lemmaId, lemmaIds, lemmaColorMap, highlights, state) {
        if (!this._renderElement) {
            throw new Error('processChildren called outside extractAndFormatBody context');
        }
        let result = '';

        for (const node of el.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                result += this.escapeHtml(node.textContent);
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                result += this._renderElement(node);
            }
        }

        return result;
    }

    /**
     * Populate modal with comprehensive metadata and text
     */
    populateModal(textId, metadata, bodyResult) {
        // Set title and author in header
        this.elements.readingTitle.textContent = metadata.title;
        this.elements.readingAuthor.textContent = metadata.author;

        // Excerpt banner (#134): sichtbar über dem Text, bewusst NICHT im
        // eingeklappten Metadaten-Bereich — die Ausschnittsbeziehung muss
        // ohne Öffnen des Panels erkennbar sein (Akzeptanzkriterium #134).
        let metadataHTML = '';
        if (metadata.excerpt) {
            metadataHTML += '<div class="excerpt-banner">';
            metadataHTML += `<strong>${this.escapeHtml(metadata.excerpt.title)}</strong> – Ausschnitt aus: ${this.escapeHtml(metadata.title)} (Verse ${this.escapeHtml(metadata.excerpt.verseRange)}).`;
            if (metadata.excerpt.context) {
                metadataHTML += ` ${this.escapeHtml(metadata.excerpt.context)}`;
            }
            metadataHTML += '</div>';
        }

        // Build comprehensive metadata HTML with collapsible section
        metadataHTML += '<div class="metadata-toggle-container">';
        metadataHTML += '<button class="metadata-toggle-btn" aria-expanded="false">';
        // Heroicon: chevron-right (collapsed state)
        metadataHTML += '<svg class="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';
        metadataHTML += ' Metadaten anzeigen';
        metadataHTML += '</button>';
        metadataHTML += '<div class="metadata-sections" style="display: none;">';

        // Wikidata Image Section (will be populated asynchronously)
        metadataHTML += '<div id="wikidataImageContainer" class="wikidata-image-container" style="display: none;"></div>';

        // Section 0: Excerpt relationship (#134) — strukturierte Felder
        // analog zur Tabelle im Issue (Ausschnitt/Gesamtwerk/Versbereich/Kontext)
        if (metadata.excerpt) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Ausschnitt</h4>';
            metadataHTML += `<div class="metadata-row"><strong>Ausschnitt:</strong> ${this.escapeHtml(metadata.excerpt.title)}</div>`;
            metadataHTML += `<div class="metadata-row"><strong>Gesamtwerk:</strong> ${this.escapeHtml(metadata.title)}</div>`;
            metadataHTML += `<div class="metadata-row"><strong>Versbereich:</strong> ${this.escapeHtml(metadata.excerpt.verseRange)}</div>`;
            if (metadata.excerpt.context) {
                metadataHTML += `<div class="metadata-row"><strong>Kontext:</strong> ${this.escapeHtml(metadata.excerpt.context)}</div>`;
            }
            metadataHTML += '</div>';
        }

        // Section 1: All Titles
        if (metadata.titles && metadata.titles.length > 0) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Titel</h4>';
            metadata.titles.forEach(title => {
                const label = title.type === 'alternate' ? 'Alternativtitel' : 'Titel';
                const lang = title.lang ? ` (${title.lang})` : '';
                metadataHTML += `<div class="metadata-row"><strong>${label}${lang}:</strong> ${this.escapeHtml(title.text)}</div>`;
            });
            metadataHTML += '</div>';
        }

        // Section 2: Sigles (with navigation for multi-edition works)
        if (metadata.allSigles && metadata.allSigles.length > 0) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Siglen</h4>';
            metadataHTML += '<div class="metadata-row sigle-navigation">';

            metadata.allSigles.forEach((sigle, index) => {
                if (sigle === textId) {
                    // Current sigle - bold + italic with tooltip
                    metadataHTML += `<strong><em title="Aktuelle Edition">${this.escapeHtml(sigle)}</em></strong>`;
                } else {
                    // Other sigles - clickable links
                    metadataHTML += `<a href="#" class="sigle-link" data-text-id="${this.escapeHtml(sigle)}" title="Text öffnen: ${this.escapeHtml(sigle)}">${this.escapeHtml(sigle)}</a>`;
                }

                // Add separator between sigles
                if (index < metadata.allSigles.length - 1) {
                    metadataHTML += ' <span class="sigle-separator">|</span> ';
                }
            });

            metadataHTML += '</div>';
            metadataHTML += '</div>';
        } else if (metadata.sigle) {
            // Fallback for works with only one sigle
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Sigle</h4>';
            metadataHTML += `<div class="metadata-row"><strong>${this.escapeHtml(metadata.sigle)}</strong></div>`;
            metadataHTML += '</div>';
        }

        // Section 3: Genres
        if (metadata.genres && metadata.genres.length > 0) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Gattungen</h4>';
            const genreList = metadata.genres.map(g => this.escapeHtml(g.text || g)).join(', ');
            metadataHTML += `<div class="metadata-row">${genreList}</div>`;
            metadataHTML += '</div>';
        }

        // Section 4: Work External Links (GND, Wikidata for the work itself)
        if (metadata.workGnd || metadata.workWikidata) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Werk-Identifier</h4>';
            metadataHTML += '<div class="external-links">';
            if (metadata.workGnd) {
                metadataHTML += `<a href="https://d-nb.info/gnd/${metadata.workGnd}" target="_blank" rel="noopener" class="external-link" title="GND: ${metadata.workGnd}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> GND</a>`;
            }
            if (metadata.workWikidata) {
                metadataHTML += `<a href="https://www.wikidata.org/wiki/${metadata.workWikidata}" target="_blank" rel="noopener" class="external-link" title="Wikidata: ${metadata.workWikidata}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> Wikidata</a>`;
            }
            metadataHTML += '</div>';
            metadataHTML += '</div>';
        }

        // Section 5: Author with external links
        metadataHTML += '<div class="metadata-section">';
        metadataHTML += '<h4 class="metadata-section-title">Autor*in</h4>';
        metadataHTML += `<div class="metadata-row"><strong>${this.escapeHtml(metadata.author)}</strong></div>`;

        // Author GND and Wikidata links (Heroicon: arrow-top-right-on-square)
        if (metadata.authorGnd || metadata.authorWikidata) {
            metadataHTML += '<div class="external-links">';
            if (metadata.authorGnd) {
                metadataHTML += `<a href="https://d-nb.info/gnd/${metadata.authorGnd}" target="_blank" rel="noopener" class="external-link" title="Autor*in GND: ${metadata.authorGnd}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> GND</a>`;
            }
            // Wikidata-Link bei Anonym-Autor*innen unterdrücken (Issue #96 KZW-Comment)
            if (metadata.authorWikidata && metadata.authorId !== 'person_anonym') {
                metadataHTML += `<a href="https://www.wikidata.org/wiki/${metadata.authorWikidata}" target="_blank" rel="noopener" class="external-link" title="Autor*in Wikidata: ${metadata.authorWikidata}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> Wikidata</a>`;
            }
            metadataHTML += '</div>';
        }
        metadataHTML += '</div>';

        // Section 6: Editions (Zotero links with current edition highlighted)
        if (metadata.editions && metadata.editions.length > 0) {
            const editionsWithZotero = metadata.editions.filter(e => e.zoteroLink);
            if (editionsWithZotero.length > 0) {
                metadataHTML += '<div class="metadata-section">';
                metadataHTML += '<h4 class="metadata-section-title">Editionen</h4>';
                metadataHTML += '<div class="external-links">';
                editionsWithZotero.forEach(edition => {
                    const label = edition.key ? `${edition.key}` : 'Edition';
                    const isCurrent = edition.key === textId;
                    const tooltip = isCurrent ? 'Aktuelle Edition' : this.escapeHtml(label);

                    // Current edition: bold + italic, Others: normal
                    const labelHTML = isCurrent
                        ? `<strong><em>${this.escapeHtml(label)}</em></strong>`
                        : this.escapeHtml(label);

                    metadataHTML += `<a href="${edition.zoteroLink}" target="_blank" rel="noopener" class="external-link" title="${tooltip}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> ${labelHTML}</a>`;
                });
                metadataHTML += '</div>';
                metadataHTML += '</div>';
            }
        }

        // Section 7: External Resources
        if (metadata.handschriftencensus) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Externe Ressourcen</h4>';
            metadataHTML += `<a href="${metadata.handschriftencensus}" target="_blank" rel="noopener" class="external-link"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> Handschriftencensus</a>`;
            metadataHTML += '</div>';
        }

        // Section 8: TEI-XML-Download (Issue #96)
        metadataHTML += '<div class="metadata-section metadata-tei-download">';
        metadataHTML += '<p class="metadata-tei-download-text">Detaillierte Metadaten (u. a. Referenzedition, verantwortliche Editor*innen und editorische Hinweise) sind in der zugehörigen TEI-XML dokumentiert; die Datei steht ';
        metadataHTML += `<a href="tei/${this.escapeHtml(textId)}.tei.xml" download="${this.escapeHtml(textId)}.tei.xml" class="metadata-tei-download-link" title="TEI-XML-Datei herunterladen"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"></path></svg> hier</a>`;
        metadataHTML += ' auch zum direkten Download bereit.</p>';
        metadataHTML += '</div>';

        metadataHTML += '</div>'; // Close metadata-sections
        metadataHTML += '</div>'; // Close metadata-toggle-container

        // Populate metadata container
        this.elements.readingMetadata.innerHTML = metadataHTML;
        this.elements.readingMetadata.classList.remove('hidden');

        // Add toggle event listener
        const toggleBtn = this.elements.readingMetadata.querySelector('.metadata-toggle-btn');
        const sectionsDiv = this.elements.readingMetadata.querySelector('.metadata-sections');
        const toggleIcon = this.elements.readingMetadata.querySelector('.toggle-icon');

        if (toggleBtn && sectionsDiv && toggleIcon) {
            toggleBtn.addEventListener('click', () => {
                const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
                toggleBtn.setAttribute('aria-expanded', !isExpanded);
                sectionsDiv.style.display = isExpanded ? 'none' : 'flex';

                // Toggle between chevron-right (collapsed) and chevron-down (expanded)
                if (isExpanded) {
                    // Collapsed state: chevron-right
                    toggleIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>';
                    toggleBtn.childNodes[1].textContent = ' Metadaten anzeigen';
                } else {
                    // Expanded state: chevron-down
                    toggleIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>';
                    toggleBtn.childNodes[1].textContent = ' Metadaten verbergen';
                }
            });
        }

        // Add sigle navigation event listeners
        const sigleLinks = this.elements.readingMetadata.querySelectorAll('.sigle-link');
        sigleLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTextId = link.getAttribute('data-text-id');
                if (targetTextId) {
                    // Navigate to the related text (preserve current lemma highlighting)
                    const options = this.currentLemmaIds.length > 0
                        ? { lemmaIds: this.currentLemmaIds }
                        : {};
                    this.openReadingView(targetTextId, options, this.elements);
                }
            });
        });

        // Populate body text with verse/prose context
        this.elements.readingBody.classList.remove('verse-context', 'prose-context');
        this.elements.readingBody.classList.add(bodyResult.hasVerse ? 'verse-context' : 'prose-context');
        this.elements.readingBody.innerHTML = bodyResult.html;

        // Populate highlight element references after DOM insertion
        bodyResult.highlights.forEach(highlight => {
            highlight.element = document.getElementById(highlight.id);
        });

        // Asynchronously fetch and display Wikidata image if available
        if (metadata.workWikidata) {
            this.loadWikidataImage(metadata.workWikidata, metadata.title);
        }
    }

    /**
     * Clean attribution text from Wikimedia (removes HTML, structured data, etc.)
     */
    cleanAttributionText(text) {
        if (!text || text === 'Unknown') return null;

        // Strip HTML tags
        let cleaned = text.replace(/<[^>]*>/g, '');

        // Remove Wikidata qualifiers (like "date QS:P,+1500-00-00T00:00:00Z/6...")
        cleaned = cleaned.replace(/date QS:[^)]+\)/g, '');
        cleaned = cleaned.replace(/\(between circa \d+ and circa \d+\)/g, '');

        // Remove extra whitespace and empty parentheses
        cleaned = cleaned.replace(/\s*\(\s*\)/g, '');
        cleaned = cleaned.replace(/\s+/g, ' ');
        cleaned = cleaned.trim();

        return cleaned || null;
    }

    /**
     * Load and display Wikidata image asynchronously
     */
    async loadWikidataImage(wikidataId, workTitle) {
        const container = document.getElementById('wikidataImageContainer');
        if (!container) return;

        try {
            const imageData = await this.getWikidataImage(wikidataId);

            if (imageData) {
                // Clean attribution data
                const artistText = this.cleanAttributionText(imageData.attribution.artist);
                const licenseText = this.cleanAttributionText(imageData.attribution.license);

                // Build attribution string
                let attributionParts = ['<a href="' + imageData.attribution.url + '" target="_blank" rel="noopener">Wikimedia Commons</a>'];
                if (artistText) attributionParts.push(this.escapeHtml(artistText));
                if (licenseText) attributionParts.push(this.escapeHtml(licenseText));

                container.innerHTML = `
                    <img src="${imageData.imageUrl}"
                         alt="Illustration aus ${this.escapeHtml(workTitle)}"
                         class="wikidata-image"
                         loading="lazy">
                    <div class="wikidata-attribution">
                        <small>Quelle: ${attributionParts.join(' • ')}</small>
                    </div>
                `;
                container.style.display = 'block';
            }
        } catch (error) {
            console.warn('[TEITextReader] Failed to load Wikidata image:', error);
        }
    }

    /**
     * Navigate to next/previous highlight
     */
    navigateHighlight(direction) {
        if (this.currentHighlights.length === 0) return;

        const newIndex = this.currentHighlightIndex + direction;

        if (newIndex < 0 || newIndex >= this.currentHighlights.length) {
            return;
        }

        this.currentHighlightIndex = newIndex;
        this.scrollToHighlight(this.currentHighlightIndex);
        this.updateNavigationButtons();
    }

    /**
     * Find closest highlight to target word position
     */
    findClosestHighlight(targetPosition) {
        if (!this.currentHighlights || this.currentHighlights.length === 0) return 0;

        let closestIndex = 0;
        let minDistance = Math.abs(this.currentHighlights[0].position - targetPosition);

        for (let i = 1; i < this.currentHighlights.length; i++) {
            const distance = Math.abs(this.currentHighlights[i].position - targetPosition);
            if (distance < minDistance) {
                minDistance = distance;
                closestIndex = i;
            }
        }

        console.log(`[TEITextReader] Target position: ${targetPosition}`);
        console.log(`[TEITextReader] Available highlight positions:`, this.currentHighlights.map(h => h.position));
        console.log(`[TEITextReader] Found closest highlight at index ${closestIndex} (position ${this.currentHighlights[closestIndex].position}, distance: ${minDistance})`);

        // If distance is too large (>100 words), just use first highlight
        if (minDistance > 100) {
            console.log(`[TEITextReader] Distance too large, using first highlight instead`);
            return 0;
        }

        return closestIndex;
    }

    /**
     * Scroll to specific highlight (instant jump, no animation)
     */
    scrollToHighlight(index) {
        if (!this.currentHighlights[index]) return;

        const element = this.currentHighlights[index].element;
        if (element) {
            // Use browser-level scrolling (not container scrolling)
            // Account for sticky header height
            const headerOffset = 120;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });

            console.log(`[TEITextReader] Scrolled to highlight ${index} (pos ${this.currentHighlights[index].position})`);

            // Add pulse effect
            element.style.transition = 'transform 0.3s ease';
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 300);
        } else {
            console.warn(`[TEITextReader] Highlight ${index} element not found`);
        }
    }

    /**
     * Scroll zur Verszeile <l n="..."> (Vers-Deep-Link, #59 Naming-Explorer)
     * oder zur Prosa-Zeile <lb n="..."> (Druckzeilen-Zählung, #143).
     * data-n stammt aus dem 'l'- bzw. 'lb'-Rendering (renderElement).
     * Hintergrund-Puls statt scale: verse-line ist eine ganze Zeile,
     * Skalierung würde den Textfluss verschieben.
     */
    scrollToVerse(verseN) {
        const scope = this.elements?.readingBody || document;
        const safe = (window.CSS && CSS.escape)
            ? CSS.escape(String(verseN))
            : String(verseN).replace(/["\\]/g, '');
        const line = scope.querySelector(`.verse-line[data-n="${safe}"], .lb-number[data-n="${safe}"], .lb-anchor[data-n="${safe}"]`);
        if (!line) {
            console.warn(`[TEITextReader] Vers ${verseN} nicht gefunden (kein <l n="${verseN}"> im Text)`);
            return;
        }

        const headerOffset = 120;
        const offsetPosition = line.getBoundingClientRect().top + window.pageYOffset - headerOffset;
        // Instant statt smooth: der Vers-Deep-Link springt direkt nach dem
        // Page-Load, wo Chrome programmatische smooth-Scrolls teils verwirft
        // (im Test: ROL blieb bei scrollY=0). Über sechsstellige Pixel-
        // Distanzen ist instant ohnehin die bessere Orientierung.
        window.scrollTo({ top: offsetPosition, behavior: 'auto' });

        console.log(`[TEITextReader] Scrolled to verse ${verseN}`);

        line.style.transition = 'background-color 0.4s ease';
        line.style.backgroundColor = '#fef3c7'; // amber-100
        setTimeout(() => {
            line.style.backgroundColor = '';
        }, 1600);
    }

    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        if (!this.elements.highlightIndicator) return;

        // Update counter
        if (this.currentHighlights.length > 0) {
            this.elements.highlightIndicator.textContent =
                `Treffer ${this.currentHighlightIndex + 1} von ${this.currentHighlights.length}`;
        } else {
            this.elements.highlightIndicator.textContent = 'Keine Treffer';
        }

        // Update button states
        if (this.elements.prevHighlight) {
            this.elements.prevHighlight.disabled = (this.currentHighlightIndex === 0);
        }
        if (this.elements.nextHighlight) {
            this.elements.nextHighlight.disabled =
                (this.currentHighlightIndex === this.currentHighlights.length - 1);
        }
    }

    /**
     * Fetch Wikidata image for a work
     */
    async getWikidataImage(entityId) {
        if (!entityId) return null;

        try {
            // Get image filename from Wikidata (P18 = image property)
            const response = await fetch(
                `https://www.wikidata.org/w/api.php?action=wbgetclaims&property=P18&entity=${entityId}&format=json&origin=*`
            );
            const data = await response.json();

            if (data.claims?.P18?.[0]) {
                const filename = data.claims.P18[0].mainsnak.datavalue.value;

                // Build image URL with Special:FilePath (auto-scales)
                const imageUrl = `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(filename)}?width=400`;

                // Get attribution info from Wikimedia Commons
                const attrResponse = await fetch(
                    `https://commons.wikimedia.org/w/api.php?action=query&titles=File:${encodeURIComponent(filename)}&prop=imageinfo&iiprop=extmetadata&format=json&origin=*`
                );
                const attrData = await attrResponse.json();

                // Extract attribution details
                const pages = attrData.query?.pages;
                const pageId = Object.keys(pages)[0];
                const imageInfo = pages[pageId]?.imageinfo?.[0];
                const metadata = imageInfo?.extmetadata;

                const attribution = {
                    artist: metadata?.Artist?.value || 'Unknown',
                    license: metadata?.LicenseShortName?.value || metadata?.License?.value || 'Unknown',
                    url: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(filename)}`
                };

                return { imageUrl, attribution };
            }

            return null;
        } catch (error) {
            console.warn('[TEITextReader] Failed to fetch Wikidata image:', error);
            return null;
        }
    }

    /**
     * Show/hide reading panel (replaces modal behavior)
     */
    showPanel() {
        // Show reading panel
        const readingPanel = document.getElementById('readingPanel');
        if (readingPanel) {
            readingPanel.classList.remove('hidden');
        }

        // Update grid layout based on whether search results are visible
        const mainGrid = document.getElementById('mainGrid');
        const resultsSection = document.getElementById('resultsSection');

        if (mainGrid) {
            const hasResults = resultsSection && !resultsSection.classList.contains('hidden');

            if (hasResults) {
                // 3-column layout: search + results + reading
                mainGrid.classList.add('three-column');
                mainGrid.classList.remove('two-column');
            } else {
                // 2-column layout: search + reading
                mainGrid.classList.add('two-column');
                mainGrid.classList.remove('three-column');
            }
        }

        // Highlight active text in text list
        this.highlightTextInList(this.currentTextId);
    }

    /**
     * Highlight the currently viewed text in the text list
     */
    highlightTextInList(textId) {
        // Remove all existing highlights
        const textList = document.getElementById('textList');
        if (!textList) return;

        const allLabels = textList.querySelectorAll('label');
        allLabels.forEach(label => {
            label.classList.remove('text-list-item-active');
        });

        // Add highlight to current text
        if (textId) {
            const currentLabel = Array.from(allLabels).find(label => label.dataset.textId === textId);
            if (currentLabel) {
                currentLabel.classList.add('text-list-item-active');
            }
        }
    }

    /**
     * Show/hide loading state
     */
    showLoading(show) {
        if (this.elements.readingLoading) {
            if (show) {
                this.elements.readingLoading.classList.remove('hidden');
                this.elements.readingBody.classList.add('hidden');
                this.elements.readingMetadata.classList.add('hidden');
            } else {
                this.elements.readingLoading.classList.add('hidden');
                this.elements.readingBody.classList.remove('hidden');
                this.elements.readingMetadata.classList.remove('hidden');
            }
        }
    }

    /**
     * Show/hide navigation footer
     */
    showNavigation(show) {
        if (this.elements.readingNavigation) {
            if (show) {
                this.elements.readingNavigation.classList.remove('hidden');
            } else {
                this.elements.readingNavigation.classList.add('hidden');
            }
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.elements.readingBody) {
            this.elements.readingBody.innerHTML =
                `<p class="text-red-600 font-medium">${this.escapeHtml(message)}</p>`;
            this.elements.readingBody.classList.remove('hidden');
        }
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

export { TEITextReader };
