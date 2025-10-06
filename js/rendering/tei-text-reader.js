/**
 * TEI Text Reader
 * Unified reading view for TEI texts with optional search highlighting
 * Replaces snippet-based context view with full-text reading experience
 *
 * Metadata Source: Prioritizes TEI header data, falls back to corpus index for missing fields
 */

class TEITextReader {
    constructor(corpusIndex, authorityIndex, cache) {
        this.corpusIndex = corpusIndex;
        this.authorityIndex = authorityIndex;
        this.cache = cache; // Reuse TextRenderer's TEICacheManager

        this.currentTextId = null;
        this.currentLemmaId = null;
        this.currentHighlights = [];
        this.currentHighlightIndex = 0;
        this.elements = null;
    }

    /**
     * Open reading view modal
     * @param {string} textId - Text ID to display
     * @param {object} options - { lemmaId: string } for highlighting (optional)
     * @param {object} elements - DOM element references
     */
    async openReadingView(textId, options = {}, elements) {
        this.currentTextId = textId;
        this.currentLemmaId = options.lemmaId || null;
        this.elements = elements;

        console.log(`[TEITextReader] Opening reading view: ${textId}${this.currentLemmaId ? ` (highlighting: ${this.currentLemmaId})` : ''}`);

        try {
            // Get text metadata from corpus index (for filename)
            const textMeta = this.corpusIndex.texts.find(t => t.id === textId);
            if (!textMeta) {
                throw new Error(`Text not found: ${textId}`);
            }

            // Show modal with loading state
            this.showModal();
            this.showLoading(true);

            // Load TEI file (cached)
            const teiDoc = await this.loadTEIFile(textMeta.filename);

            // Extract metadata (prioritizes TEI header, falls back to corpus index)
            const metadata = this.extractMetadata(teiDoc, textMeta);

            // Extract and format body text (with optional highlighting)
            const bodyResult = this.extractAndFormatBody(teiDoc, this.currentLemmaId);

            // Populate modal
            this.populateModal(metadata, bodyResult);

            // Setup navigation if highlights exist
            if (bodyResult.highlights.length > 0) {
                this.currentHighlights = bodyResult.highlights;
                this.currentHighlightIndex = 0;
                this.showNavigation(true);
                this.updateNavigationButtons();

                // Scroll to first highlight after brief delay
                setTimeout(() => this.scrollToHighlight(0), 300);
            } else {
                this.showNavigation(false);
            }

            // Hide loading
            this.showLoading(false);

        } catch (error) {
            console.error('[TEITextReader] Failed to open reading view:', error);
            this.showLoading(false);
            this.showError(`Fehler beim Laden: ${error.message}`);
        }
    }

    /**
     * Load TEI file from cache or network
     */
    async loadTEIFile(filename) {
        try {
            // Try cache first
            const cachedDoc = await this.cache.get(filename);
            if (cachedDoc) {
                console.log(`[TEITextReader] ⚡ Loaded from cache: ${filename}`);
                return cachedDoc;
            }

            // Cache miss - fetch from network
            console.log(`[TEITextReader] 🌐 Fetching from network: ${filename}`);
            const startTime = Date.now();

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

            const loadTime = Date.now() - startTime;
            console.log(`[TEITextReader] Loaded in ${(loadTime / 1000).toFixed(1)}s`);

            // Cache for next time (don't wait)
            this.cache.set(filename, doc).catch(err =>
                console.error('[TEITextReader] Cache write failed:', err)
            );

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
            zoteroLinks: []
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
     * Handles: <head>, <p>, <div>, <lg>, <l>, <lb>, <pb>, <hi rend="...">, <seg type="pc">
     * @returns {object} { html: string, highlights: Array<{element, position}> }
     */
    extractAndFormatBody(teiDoc, lemmaId = null) {
        const body = teiDoc.querySelector('body');
        if (!body) {
            return { html: '<p class="text-gray-600">Kein Textinhalt gefunden.</p>', highlights: [] };
        }

        const highlights = [];
        let highlightCounter = 0;

        // Process element recursively
        const processElement = (el) => {
            const tagName = el.tagName.toLowerCase();

            // Handle different TEI elements
            switch (tagName) {
                case 'head':
                    // Section heading
                    return `<h3 class="section-head">${this.processChildren(el, lemmaId, highlights)}</h3>`;

                case 'p':
                case 'ab':
                    // Paragraph
                    return `<p>${this.processChildren(el, lemmaId, highlights)}</p>`;

                case 'div':
                    // Division (generic container)
                    return `<div class="tei-div">${this.processChildren(el, lemmaId, highlights)}</div>`;

                case 'lg':
                    // Line group (verse)
                    return `<div class="verse-group">${this.processChildren(el, lemmaId, highlights)}</div>`;

                case 'l':
                    // Single line (verse)
                    return `<span class="verse-line">${this.processChildren(el, lemmaId, highlights)}</span>`;

                case 'lb':
                    // Line break
                    return '<br class="line-break">';

                case 'pb':
                    // Page break - show page number
                    const pageNum = el.getAttribute('n');
                    return pageNum ? `<span class="page-break" title="Seite ${pageNum}">[${pageNum}]</span>` : '';

                case 'hi':
                    // Highlighting (rend="initial", rend="upper_case_first_letter")
                    const rend = el.getAttribute('rend');
                    return this.processHi(el, rend, lemmaId, highlights);

                case 'seg':
                    // Segment (type="pc" = punctuation)
                    const type = el.getAttribute('type');
                    if (type === 'pc') {
                        return `<span class="punctuation">${this.escapeHtml(el.textContent)}</span>`;
                    }
                    return this.processChildren(el, lemmaId, highlights);

                case 'w':
                    // Word element
                    return this.processWord(el, lemmaId, highlights);

                default:
                    // For unknown elements, process children
                    return this.processChildren(el, lemmaId, highlights);
            }
        };

        // Build HTML from body
        let html = '';
        const children = Array.from(body.children);

        for (const child of children) {
            html += processElement(child);
        }

        return { html, highlights };
    }

    /**
     * Process <hi> element with rend attribute
     */
    processHi(el, rend, lemmaId, highlights) {
        const content = this.processChildren(el, lemmaId, highlights);

        switch (rend) {
            case 'initial':
                return `<span class="initial">${content}</span>`;
            case 'upper_case_first_letter':
                return `<span class="upper-case-first">${content}</span>`;
            default:
                return `<span class="hi">${content}</span>`;
        }
    }

    /**
     * Process word element with potential highlighting
     */
    processWord(wordEl, lemmaId, highlights) {
        const wordText = wordEl.textContent.trim();

        // Check if this word should be highlighted
        if (lemmaId) {
            const lemmaRef = wordEl.getAttribute('lemmaRef');
            const lemmaRefPattern = `#${lemmaId}`;

            if (lemmaRef && lemmaRef.includes(lemmaRefPattern)) {
                const id = `highlight-${highlights.length}`;
                highlights.push({ id, element: null }); // Will be populated after DOM insertion
                return `<mark class="highlight" id="${id}">${this.escapeHtml(wordText)}</mark> `;
            }
        }

        return this.escapeHtml(wordText) + ' ';
    }

    /**
     * Process children of element recursively
     */
    processChildren(el, lemmaId, highlights) {
        let result = '';

        for (const node of el.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) {
                result += this.escapeHtml(node.textContent);
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const tagName = node.tagName.toLowerCase();

                if (tagName === 'w') {
                    result += this.processWord(node, lemmaId, highlights);
                } else if (tagName === 'lb') {
                    result += '<br class="line-break">';
                } else if (tagName === 'pb') {
                    const pageNum = node.getAttribute('n');
                    result += pageNum ? `<span class="page-break" title="Seite ${pageNum}">[${pageNum}]</span> ` : '';
                } else if (tagName === 'hi') {
                    const rend = node.getAttribute('rend');
                    result += this.processHi(node, rend, lemmaId, highlights);
                } else if (tagName === 'seg') {
                    const type = node.getAttribute('type');
                    if (type === 'pc') {
                        result += this.escapeHtml(node.textContent);
                    } else {
                        result += this.processChildren(node, lemmaId, highlights);
                    }
                } else if (tagName === 'l') {
                    result += `<span class="verse-line">${this.processChildren(node, lemmaId, highlights)}</span>`;
                } else {
                    // Recursively process other elements
                    result += this.processChildren(node, lemmaId, highlights);
                }
            }
        }

        return result;
    }

    /**
     * Populate modal with comprehensive metadata and text
     */
    populateModal(metadata, bodyResult) {
        // Set title and author in header
        this.elements.readingTitle.textContent = metadata.title;
        this.elements.readingAuthor.textContent = metadata.author;

        // Build comprehensive metadata HTML with collapsible section
        let metadataHTML = '<div class="metadata-toggle-container">';
        metadataHTML += '<button class="metadata-toggle-btn" aria-expanded="false">';
        // Heroicon: chevron-right (collapsed state)
        metadataHTML += '<svg class="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';
        metadataHTML += ' Metadaten anzeigen';
        metadataHTML += '</button>';
        metadataHTML += '<div class="metadata-sections" style="display: none;">';

        // Wikidata Image Section (will be populated asynchronously)
        metadataHTML += '<div id="wikidataImageContainer" class="wikidata-image-container" style="display: none;"></div>';

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

        // Section 2: Sigles
        if (metadata.allSigles && metadata.allSigles.length > 0) {
            metadataHTML += '<div class="metadata-section">';
            metadataHTML += '<h4 class="metadata-section-title">Siglen</h4>';
            metadataHTML += `<div class="metadata-row">${metadata.allSigles.join(', ')}</div>`;
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
        metadataHTML += '<h4 class="metadata-section-title">Autor</h4>';
        metadataHTML += `<div class="metadata-row"><strong>${this.escapeHtml(metadata.author)}</strong></div>`;

        // Author GND and Wikidata links (Heroicon: arrow-top-right-on-square)
        if (metadata.authorGnd || metadata.authorWikidata) {
            metadataHTML += '<div class="external-links">';
            if (metadata.authorGnd) {
                metadataHTML += `<a href="https://d-nb.info/gnd/${metadata.authorGnd}" target="_blank" rel="noopener" class="external-link" title="Autor GND: ${metadata.authorGnd}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> GND</a>`;
            }
            if (metadata.authorWikidata) {
                metadataHTML += `<a href="https://www.wikidata.org/wiki/${metadata.authorWikidata}" target="_blank" rel="noopener" class="external-link" title="Autor Wikidata: ${metadata.authorWikidata}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> Wikidata</a>`;
            }
            metadataHTML += '</div>';
        }
        metadataHTML += '</div>';

        // Section 6: Editions (Zotero links only)
        if (metadata.editions && metadata.editions.length > 0) {
            const editionsWithZotero = metadata.editions.filter(e => e.zoteroLink);
            if (editionsWithZotero.length > 0) {
                metadataHTML += '<div class="metadata-section">';
                metadataHTML += '<h4 class="metadata-section-title">Editionen</h4>';
                metadataHTML += '<div class="external-links">';
                editionsWithZotero.forEach(edition => {
                    const label = edition.key ? `${edition.key}` : 'Edition';
                    metadataHTML += `<a href="${edition.zoteroLink}" target="_blank" rel="noopener" class="external-link" title="${this.escapeHtml(label)}"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"></path></svg> ${this.escapeHtml(label)}</a>`;
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

        // Populate body text
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
     * Scroll to specific highlight (instant jump, no animation)
     */
    scrollToHighlight(index) {
        if (!this.currentHighlights[index]) return;

        const element = this.currentHighlights[index].element;
        if (element) {
            // Instant scroll (no animation)
            element.scrollIntoView({ behavior: 'instant', block: 'center' });

            // Add pulse effect
            element.style.transition = 'transform 0.3s ease';
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 300);
        }
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
     * Show/hide modal
     */
    showModal() {
        if (this.elements.readingModal) {
            this.elements.readingModal.classList.add('active');
        }
    }

    closeModal() {
        if (this.elements.readingModal) {
            this.elements.readingModal.classList.remove('active');
        }

        // Reset state
        this.currentHighlights = [];
        this.currentHighlightIndex = 0;
        this.currentTextId = null;
        this.currentLemmaId = null;

        // Clear content
        if (this.elements.readingBody) {
            this.elements.readingBody.innerHTML = '';
        }
        if (this.elements.readingMetadata) {
            this.elements.readingMetadata.classList.add('hidden');
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
