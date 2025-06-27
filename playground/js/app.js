/**
 * MHDBDB Playground - TEI Data Explorer
 * Authority Files (auto-loaded) + TEI Files (user upload)
 * Fixed: TEI namespace handling for xml:lang attributes
 */

class MHDBDBPlayground {
    constructor() {
        // Authority Files (auto-loaded from /lists/output/)
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
        
        // TEI Files (user uploaded)
        this.teiData = {
            files: [],
            parsedXML: [],
            words: [],
            lines: [],
            annotations: []
        };
        
        // Configuration
        this.authorityFiles = [
            'persons.xml',
            'works.xml', 
            'lexicon.xml',
            'concepts.xml',
            'genres.xml',
            'names.xml'
        ];
        
        this.init();
    }

    async init() {
        this.initializeEventListeners();
        await this.loadAuthorityFiles();
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
            { id: 'showAuthorsBtn', handler: () => this.showAuthors() },
            { id: 'showWorksBtn', handler: () => this.showWorks() },
            { id: 'showLemmataBtn', handler: () => this.showLemmata() },
            { id: 'showConceptsBtn', handler: () => this.showConcepts() },
            { id: 'showGenresBtn', handler: () => this.showGenres() },
            { id: 'showNamesBtn', handler: () => this.showNames() }
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
            { id: 'showWordsBtn', handler: () => this.showWords() },
            { id: 'showLinesBtn', handler: () => this.showLines() },
            { id: 'findLemmaBtn', handler: () => this.findLemmaInText() },
            { id: 'showAnnotationsBtn', handler: () => this.showAnnotations() }
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
            xpathExecute.addEventListener('click', () => this.executeXPath());
        } else {
            console.warn('⚠️ XPath button not found');
        }
    }

    // ==================== AUTHORITY FILES LOADING ====================

    async loadAuthorityFiles() {
        this.updateStatus('🔄', 'Lade Authority Files...');
        
        const loadPromises = this.authorityFiles.map(filename => 
            this.loadAuthorityFile(filename).catch(error => {
                console.warn(`⚠️ Failed to load ${filename}:`, error.message);
                return null; // Continue with other files
            })
        );
        
        try {
            await Promise.all(loadPromises);
            const successCount = this.authorityData.files.length;

            this.updateStatus('✅', `${successCount}/${this.authorityFiles.length} Authority Files geladen`);
            this.updateAuthorityOverview();
            this.enableAuthorityQueries();
            this.showWelcomeMessage();

            console.log(`✅ Authority Files loaded: ${successCount}/${this.authorityFiles.length}`);
        } catch (error) {
            this.updateStatus('❌', 'Fehler beim Laden der Authority Files');
            this.showError('Authority Files konnten nicht vollständig geladen werden');
        }
    }

    async loadAuthorityFile(filename) {
        const response = await fetch(`../lists/output/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${filename}`);
        }

        const content = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(content, 'text/xml');

        const parseError = xmlDoc.querySelector('parsererror');
        if (parseError) {
            throw new Error(`XML Parse Error: ${parseError.textContent}`);
        }

        this.authorityData.files.push(filename);
        this.authorityData.parsedXML.push({
            filename: filename,
            doc: xmlDoc,
            content: content
        });

        this.analyzeAuthorityFile(xmlDoc, filename);
        return xmlDoc;
    }

    analyzeAuthorityFile(xmlDoc, filename) {
        // Detect file type and extract data accordingly
        if (filename.includes('persons') || xmlDoc.querySelector('listPerson')) {
            this.extractPersons(xmlDoc);
        } else if (filename.includes('works') || xmlDoc.querySelector('listBibl')) {
            this.extractWorks(xmlDoc);
        } else if (filename.includes('lexicon') || xmlDoc.querySelector('entry')) {
            this.extractLemmata(xmlDoc);
        } else if (filename.includes('concepts') || this.hasConceptCategories(xmlDoc)) {
            this.extractConcepts(xmlDoc);
        } else if (filename.includes('genres') || this.hasGenreCategories(xmlDoc)) {
            this.extractGenres(xmlDoc);
        } else if (filename.includes('names') || this.hasNameCategories(xmlDoc)) {
            this.extractNames(xmlDoc);
        } else {
            console.warn(`⚠️ Unknown authority file structure: ${filename}`);
        }
    }

    // Helper methods for better detection
    hasConceptCategories(xmlDoc) {
        return xmlDoc.querySelector('category[xml\\:id*="concept"]') !== null;
    }

    hasGenreCategories(xmlDoc) {
        return xmlDoc.querySelector('category[xml\\:id*="genre"]') !== null;
    }

    hasNameCategories(xmlDoc) {
        return xmlDoc.querySelector('category[xml\\:id*="name"]') !== null;
    }

    // ==================== DATA EXTRACTION METHODS ====================

    extractPersons(xmlDoc) {
        const persons = xmlDoc.querySelectorAll('person');
        let extracted = 0;

        persons.forEach(person => {
            const id = person.getAttribute('xml:id');
            const preferredName = person.querySelector('persName[type="preferred"]')?.textContent?.trim();
            const gnd = person.querySelector('idno[type="GND"]')?.textContent?.trim();
            const wikidata = person.querySelector('idno[type="wikidata"]')?.textContent?.trim();
            const works = person.querySelector('note[type="works"]')?.textContent?.trim();
            
            if (id && preferredName) {
                this.authorityData.persons.push({
                    id, preferredName, gnd, wikidata, works
                });
                extracted++;
            }
        });

        console.log(`👥 Persons extracted: ${extracted}`);
    }

    extractWorks(xmlDoc) {
        // TEI namespace fix: Use all bibl elements and filter manually
        const allBibls = xmlDoc.querySelectorAll('bibl');
        const works = Array.from(allBibls).filter(bibl => {
            const id = bibl.getAttribute('xml:id');
            return id && id.startsWith('work_');
        });

        let extracted = 0;

        works.forEach(work => {
            const id = work.getAttribute('xml:id');
            // Get the direct child title (not nested ones in edition bibl)
            const titleElement = work.querySelector(':scope > title');
            const title = titleElement?.textContent?.trim();
            const sigle = work.querySelector('idno[type="sigle"]')?.textContent?.trim();
            const authorRef = work.querySelector('author')?.getAttribute('ref');
            const authorText = work.querySelector('author')?.textContent?.trim();
            const author = authorRef || authorText;
            
            if (id && title) {
                this.authorityData.works.push({
                    id, title, sigle, author: author || 'Unbekannt'
                });
                extracted++;
            }
        });

        console.log(`📚 Works extracted: ${extracted}`);
    }

    extractLemmata(xmlDoc) {
        const entries = xmlDoc.querySelectorAll('entry');
        let extracted = 0;

        entries.forEach(entry => {
            const id = entry.getAttribute('xml:id');
            const lemma = entry.querySelector('form[type="lemma"] orth')?.textContent?.trim();
            const pos = entry.querySelector('pos')?.textContent?.trim();
            const senses = entry.querySelectorAll('sense');
            
            if (id && lemma) {
                this.authorityData.lemmata.push({
                    id, lemma, pos, senseCount: senses.length
                });
                extracted++;
            }
        });

        console.log(`🔤 Lemmata extracted: ${extracted}`);
    }

    extractConcepts(xmlDoc) {
        const categories = this.extractTaxonomyCategories(xmlDoc, 'concept_');
        this.authorityData.concepts = categories;
        console.log(`💭 Concepts extracted: ${categories.length}`);
    }

    extractGenres(xmlDoc) {
        const categories = this.extractTaxonomyCategories(xmlDoc, 'genre_');
        this.authorityData.genres = categories;
        console.log(`🎭 Genres extracted: ${categories.length}`);
    }

    extractNames(xmlDoc) {
        const categories = this.extractTaxonomyCategories(xmlDoc, 'name_');
        this.authorityData.names = categories;
        console.log(`📛 Names extracted: ${categories.length}`);
    }

    // Unified extraction for taxonomy-based authority files (concepts, genres, names)
    extractTaxonomyCategories(xmlDoc, idPrefix) {
        const categories = xmlDoc.querySelectorAll('category');
        const results = [];

        // Filter categories by ID prefix
        const filteredCategories = Array.from(categories).filter(cat => {
            const id = cat.getAttribute('xml:id');
            return id && id.includes(idPrefix);
        });

        filteredCategories.forEach(category => {
            const id = category.getAttribute('xml:id');
            const catDesc = category.querySelector('catDesc');
            
            if (catDesc) {
                // TEI namespace fix: Manual filtering for xml:lang attributes
                const allTerms = Array.from(catDesc.querySelectorAll('term'));
                const termDE = allTerms.find(t => t.getAttribute('xml:lang') === 'de')?.textContent?.trim();
                const termEN = allTerms.find(t => t.getAttribute('xml:lang') === 'en')?.textContent?.trim();

                if (id && (termDE || termEN)) {
                    results.push({ id, termDE, termEN });
                }
            }
        });

        return results;
    }

    // ==================== TEI FILE HANDLING ====================

    async handleTEIFiles(files) {
        const fileArray = Array.from(files);
        const uploadedFilesContainer = document.getElementById('uploadedFiles');
        
        for (const file of fileArray) {
            if (this.isTEIFile(file)) {
                await this.processTEIFile(file);
                this.displayFileItem(file, uploadedFilesContainer);
            }
        }
        
        this.updateTEIOverview();
        this.enableTEIQueries();
    }

    isTEIFile(file) {
        return file.type === 'text/xml' ||
               file.name.endsWith('.xml') ||
               file.name.endsWith('.tei');
    }

    async processTEIFile(file) {
        try {
            const content = await this.readFileAsText(file);
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(content, 'text/xml');
            
            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                throw new Error('XML Parsing Error: ' + parseError.textContent);
            }
            
            this.teiData.files.push(file);
            this.teiData.parsedXML.push({
                filename: file.name,
                doc: xmlDoc,
                content: content
            });
            
            this.analyzeTEIStructure(xmlDoc, file.name);
            console.log(`✅ TEI File processed: ${file.name}`);
            
        } catch (error) {
            console.error(`❌ Error processing ${file.name}:`, error);
            this.showError(`Fehler beim Verarbeiten von ${file.name}: ${error.message}`);
        }
    }

    analyzeTEIStructure(xmlDoc, filename) {
        // Extract words (w elements)
        const words = xmlDoc.querySelectorAll('w');
        words.forEach((word, index) => {
            const id = word.getAttribute('xml:id');
            const lemmaRef = word.getAttribute('lemmaRef');
            const pos = word.getAttribute('pos');
            const text = word.textContent?.trim();
            
            if (text) {
                this.teiData.words.push({
                    id, text, lemmaRef, pos, filename, index
                });
            }
        });

        // Extract lines (l elements)
        const lines = xmlDoc.querySelectorAll('l');
        lines.forEach((line, index) => {
            const n = line.getAttribute('n');
            const text = line.textContent?.trim();
            
            if (text) {
                this.teiData.lines.push({
                    n, text, filename, index
                });
            }
        });

        // Extract annotations/semantic references
        const annotatedElements = xmlDoc.querySelectorAll('[meaningRef], [conceptRef]');
        annotatedElements.forEach((element, index) => {
            const meaningRef = element.getAttribute('meaningRef');
            const conceptRef = element.getAttribute('conceptRef');
            const text = element.textContent?.trim();
            
            this.teiData.annotations.push({
                text, meaningRef, conceptRef, filename, index,
                tagName: element.tagName
            });
        });

        console.log(`📜 TEI Analysis complete: ${words.length} words, ${lines.length} lines, ${annotatedElements.length} annotations`);
    }

    // ==================== QUERY FUNCTIONS ====================

    // Authority Files Queries
    showAuthors() {
        this.displayResults(
            '👥 Alle Autoren aus Authority Files',
            this.authorityData.persons.map(p => ({
                meta: `ID: ${p.id}${p.works ? ` • ${p.works.split(',').length} Werke` : ''}`,
                snippet: `${p.preferredName}${p.gnd ? ` <code>GND: ${p.gnd}</code>` : ''}`
            }))
        );
    }

    showWorks() {
        this.displayResults(
            '📚 Alle Werke aus Authority Files',
            this.authorityData.works.map(w => ({
                meta: `ID: ${w.id}${w.sigle ? ` • Sigle: ${w.sigle}` : ''}`,
                snippet: `${w.title}${w.author ? ` von ${w.author}` : ''}`
            }))
        );
    }

    showLemmata() {
        // Check if we have too many lemmata for direct display
        if (this.authorityData.lemmata.length > 500) {
            this.showLemmataWithSearch();
        } else {
            this.showAllLemmata();
        }
    }

    showAllLemmata() {
        const displayCount = Math.min(100, this.authorityData.lemmata.length);
        this.displayResults(
            `🔤 Lemmata aus Authority Files (erste ${displayCount} von ${this.authorityData.lemmata.length})`,
            this.authorityData.lemmata.slice(0, displayCount).map(l => ({
                meta: `ID: ${l.id}${l.pos ? ` • POS: ${l.pos}` : ''}${l.senseCount ? ` • ${l.senseCount} Bedeutungen` : ''}`,
                snippet: l.lemma
            }))
        );
    }

    showLemmataWithSearch() {
        const container = document.getElementById('resultsContainer');
        if (!container) return;

        container.innerHTML = `
            <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
                🔤 Lemmata-Suche (${this.authorityData.lemmata.length} Lemmata verfügbar)
            </div>
            <div style="margin-bottom: 15px;">
                <input type="text" id="lemmaSearch" placeholder="Lemma eingeben (z.B. vriunt, minne, ere)"
                       style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem;">
            </div>
            <div id="lemmaResults" style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                Geben Sie ein Lemma ein, um zu suchen...
            </div>
        `;

        // Add search functionality
        const searchInput = document.getElementById('lemmaSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchLemmata(e.target.value);
            });
        }
    }

    searchLemmata(searchTerm) {
        const resultsContainer = document.getElementById('lemmaResults');
        if (!resultsContainer) return;

        if (!searchTerm.trim()) {
            resultsContainer.innerHTML = `
                <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                    Geben Sie ein Lemma ein, um zu suchen...
                </div>
            `;
            return;
        }

        const term = searchTerm.toLowerCase().trim();
        const matches = this.authorityData.lemmata.filter(lemma =>
            lemma.lemma.toLowerCase().includes(term)
        );

        if (matches.length === 0) {
            resultsContainer.innerHTML = `
                <div style="color: #999; padding: 20px; text-align: center;">
                    Keine Lemmata gefunden für "${searchTerm}"
                </div>
            `;
            return;
        }

        // Limit results for performance
        const displayMatches = matches.slice(0, 50);
        const resultHTML = displayMatches.map(lemma => `
            <div class="result-item">
                <div class="result-meta">ID: ${lemma.id}${lemma.pos ? ` • POS: ${lemma.pos}` : ''}${lemma.senseCount ? ` • ${lemma.senseCount} Bedeutungen` : ''}</div>
                <div class="result-snippet">
                    ${lemma.lemma}
                    ${lemma.senseCount > 0 ? `<button onclick="window.playground.showLemmaSenses('${lemma.id}')" style="margin-left: 10px; padding: 4px 8px; background: #667eea; color: white; border: none; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">Bedeutungen anzeigen</button>` : ''}
                </div>
                <div id="senses-${lemma.id}" style="display: none; margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.05); border-radius: 6px;"></div>
            </div>
        `).join('');

        resultsContainer.innerHTML = `
            <div style="margin-bottom: 15px; color: #667eea; font-weight: 500;">
                ${matches.length} Treffer für "${searchTerm}"${matches.length > 50 ? ` (erste 50 angezeigt)` : ''}
            </div>
            ${resultHTML}
        `;
    }

    showLemmaSenses(lemmaId) {
        const sensesContainer = document.getElementById(`senses-${lemmaId}`);
        if (!sensesContainer) return;

        // Toggle visibility
        if (sensesContainer.style.display !== 'none') {
            sensesContainer.style.display = 'none';
            return;
        }

        // Find the lemma in the XML and extract senses
        const lexiconXML = this.authorityData.parsedXML.find(xml =>
            xml.filename.includes('lexicon')
        );

        if (!lexiconXML) {
            sensesContainer.innerHTML = '<div style="color: #999;">Lexicon XML nicht gefunden</div>';
            sensesContainer.style.display = 'block';
            return;
        }

        // TEI namespace fix: Manual filtering instead of CSS selector
        const allEntries = lexiconXML.doc.querySelectorAll('entry');
        const lemmaEntry = Array.from(allEntries).find(entry => {
            const id = entry.getAttribute('xml:id');
            return id === lemmaId;
        });

        if (!lemmaEntry) {
            sensesContainer.innerHTML = '<div style="color: #999;">Lemma nicht im XML gefunden</div>';
            sensesContainer.style.display = 'block';
            return;
        }

        const senses = lemmaEntry.querySelectorAll('sense');
        if (senses.length === 0) {
            sensesContainer.innerHTML = '<div style="color: #999;">Keine Bedeutungen gefunden</div>';
            sensesContainer.style.display = 'block';
            return;
        }

        const sensesHTML = Array.from(senses).map((sense, index) => {
            const senseId = sense.getAttribute('xml:id') || `sense_${index + 1}`;

            // Extract concept references from this sense
            const conceptPtrs = sense.querySelectorAll('ptr[target*="concepts.xml#"]');
            let conceptsHTML = '';

            if (conceptPtrs.length > 0) {
                const concepts = Array.from(conceptPtrs).map(ptr => {
                    const target = ptr.getAttribute('target');
                    const conceptId = target.split('#')[1]; // Extract ID after #

                    // Find this concept in our authority data
                    const concept = this.authorityData.concepts.find(c => c.id === conceptId);
                    return concept ? concept.termDE || concept.termEN : conceptId;
                }).filter(Boolean);

                if (concepts.length > 0) {
                    conceptsHTML = `
                        <div style="margin-top: 5px; font-size: 0.85rem; color: #666;">
                            <strong>Konzepte:</strong> ${concepts.join(' • ')}
                        </div>
                    `;
                }
            }

            return `
                <div style="margin-bottom: 8px; font-size: 0.9rem;">
                    <strong>Bedeutung ${index + 1}:</strong> ${senseId}
                    ${conceptsHTML}
                </div>
            `;
        }).join('');

        sensesContainer.innerHTML = `
            <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">🔍 ${senses.length} Bedeutungen:</div>
            ${sensesHTML}
        `;
        sensesContainer.style.display = 'block';
    }

    showConcepts() {
        this.displayResults(
            '💭 Alle Konzepte aus Authority Files',
            this.authorityData.concepts.map(c => ({
                meta: `ID: ${c.id}`,
                snippet: `${c.termDE || c.termEN}${c.termDE && c.termEN ? ` / ${c.termEN}` : ''}`
            }))
        );
    }

    showGenres() {
        // Check if we have many genres - use search interface
        if (this.authorityData.genres.length > 50) {
            this.showGenresWithSearch();
        } else {
            this.showAllGenres();
        }
    }

    showAllGenres() {
        this.displayResults(
            '🎭 Alle Gattungen aus Authority Files',
            this.authorityData.genres.map(g => ({
                meta: `ID: ${g.id}`,
                snippet: `${g.termDE || g.termEN}${g.termDE && g.termEN ? ` / ${g.termEN}` : ''}`
            }))
        );
    }

    showGenresWithSearch() {
        const container = document.getElementById('resultsContainer');
        if (!container) return;

        container.innerHTML = `
            <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
                🎭 Gattungen-Explorer (${this.authorityData.genres.length} Gattungen verfügbar)
            </div>
            <div style="margin-bottom: 15px;">
                <input type="text" id="genreSearch" placeholder="Gattung eingeben (z.B. roman, chronik, lied)"
                       style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem;">
            </div>
            <div id="genreResults" style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                Geben Sie eine Gattung ein, um zu suchen...
            </div>
        `;

        // Add search functionality
        const searchInput = document.getElementById('genreSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchGenres(e.target.value);
            });
        }
    }

    searchGenres(searchTerm) {
        const resultsContainer = document.getElementById('genreResults');
        if (!resultsContainer) return;

        if (!searchTerm.trim()) {
            resultsContainer.innerHTML = `
                <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                    Geben Sie eine Gattung ein, um zu suchen...
                </div>
            `;
            return;
        }

        const term = searchTerm.toLowerCase().trim();
        const matches = this.authorityData.genres.filter(genre =>
            (genre.termDE && genre.termDE.toLowerCase().includes(term)) ||
            (genre.termEN && genre.termEN.toLowerCase().includes(term))
        );

        if (matches.length === 0) {
            resultsContainer.innerHTML = `
                <div style="color: #999; padding: 20px; text-align: center;">
                    Keine Gattungen gefunden für "${searchTerm}"
                </div>
            `;
            return;
        }

        // Limit results for performance
        const displayMatches = matches.slice(0, 30);
        const resultHTML = displayMatches.map(genre => {
            const hierarchy = this.getGenreHierarchy(genre.id);

            return `
                <div class="result-item">
                    <div class="result-meta">
                        ID: ${genre.id}
                        ${hierarchy ? ` • Hierarchie: ${hierarchy}` : ''}
                    </div>
                    <div class="result-snippet">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span><strong>${genre.termDE || genre.termEN}</strong>${genre.termDE && genre.termEN ? ` / ${genre.termEN}` : ''}</span>
                            <button onclick="window.playground.showWorksInGenre('${genre.id}', '${(genre.termDE || genre.termEN).replace(/'/g, "\\'")}')"
                                    style="margin-left: 10px; padding: 4px 8px; background: #667eea; color: white; border: none; border-radius: 4px; font-size: 0.8rem; cursor: pointer;">
                                Werke anzeigen
                            </button>
                        </div>
                    </div>
                    <div id="works-${genre.id}" style="display: none; margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.05); border-radius: 6px;"></div>
                </div>
            `;
        }).join('');

        resultsContainer.innerHTML = `
            <div style="margin-bottom: 15px; color: #667eea; font-weight: 500;">
                ${matches.length} Treffer für "${searchTerm}"${matches.length > 30 ? ` (erste 30 angezeigt)` : ''}
            </div>
            ${resultHTML}
        `;
    }

    getGenreHierarchy(genreId) {
        // Find genre in the XML to get hierarchy info
        const genresXML = this.authorityData.parsedXML.find(xml =>
            xml.filename.includes('genres')
        );

        if (!genresXML) return null;

        const categoryElement = genresXML.doc.querySelector(`category[xml\\:id="${genreId}"]`) ||
                               Array.from(genresXML.doc.querySelectorAll('category')).find(cat =>
                                   cat.getAttribute('xml:id') === genreId
                               );

        if (!categoryElement) return null;

        // Look for parent pointer
        const parentPtr = categoryElement.querySelector('ptr[type="broader"]');
        if (!parentPtr) return null;

        const parentTarget = parentPtr.getAttribute('target');
        if (!parentTarget) return null;

        const parentId = parentTarget.replace('#', '');
        const parentGenre = this.authorityData.genres.find(g => g.id === parentId);

        return parentGenre ? (parentGenre.termDE || parentGenre.termEN) : parentId;
    }

    showWorksInGenre(genreId, genreName) {
        const worksContainer = document.getElementById(`works-${genreId}`);
        if (!worksContainer) return;

        // Toggle visibility
        if (worksContainer.style.display !== 'none') {
            worksContainer.style.display = 'none';
            return;
        }

        // Find works that reference this genre
        const matchingWorks = this.authorityData.works.filter(work => {
            // Check if any work references this genre
            const worksXML = this.authorityData.parsedXML.find(xml =>
                xml.filename.includes('works')
            );

            if (!worksXML) return false;

            // Find the work element in XML
            const workElement = Array.from(worksXML.doc.querySelectorAll('bibl')).find(bibl => {
                const id = bibl.getAttribute('xml:id');
                return id === work.id;
            });

            if (!workElement) return false;

            // Check if this work has a ref to our genre
            const genreRefs = workElement.querySelectorAll('ref[target*="genres.xml#"]');
            return Array.from(genreRefs).some(ref => {
                const target = ref.getAttribute('target');
                return target && target.includes(genreId);
            });
        });

        if (matchingWorks.length === 0) {
            worksContainer.innerHTML = `
                <div style="color: #999; font-style: italic;">
                    Keine Werke in Gattung "${genreName}" gefunden
                </div>
            `;
        } else {
            const worksHTML = matchingWorks.slice(0, 20).map(work => `
                <div style="margin-bottom: 3px; font-size: 0.85rem;">
                    • <strong>${work.title}</strong>${work.author && work.author !== 'Unbekannt' ? ` von ${work.author}` : ''}${work.sigle ? ` (${work.sigle})` : ''}
                </div>
            `).join('');

            worksContainer.innerHTML = `
                <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
                    📚 ${matchingWorks.length} Werke in "${genreName}"${matchingWorks.length > 20 ? ' (erste 20)' : ''}:
                </div>
                ${worksHTML}
            `;
        }

        worksContainer.style.display = 'block';
    }

    showNames() {
        this.displayResults(
            '📛 Alle Namen aus Authority Files',
            this.authorityData.names.map(n => ({
                meta: `ID: ${n.id}`,
                snippet: `${n.termDE || n.termEN}${n.termDE && n.termEN ? ` / ${n.termEN}` : ''}`
            }))
        );
    }

    // TEI Files Queries
    showWords() {
        const displayCount = Math.min(200, this.teiData.words.length);
        this.displayResults(
            `📝 Wörter aus TEI Texten (erste ${displayCount} von ${this.teiData.words.length})`,
            this.teiData.words.slice(0, displayCount).map(w => ({
                meta: `${w.filename}${w.pos ? ` • POS: ${w.pos}` : ''}${w.lemmaRef ? ` • Lemma: ${w.lemmaRef.split('#').pop()}` : ''}`,
                snippet: w.text
            }))
        );
    }

    showLines() {
        this.displayResults(
            `📏 Textzeilen aus TEI Texten (${this.teiData.lines.length} Zeilen)`,
            this.teiData.lines.map(l => ({
                meta: `${l.filename} • Zeile ${l.n}`,
                snippet: l.text
            }))
        );
    }

    findLemmaInText() {
        const searchTerm = prompt('Welches Lemma soll im Text gesucht werden?');
        if (!searchTerm) return;

        const matches = this.teiData.words.filter(w => 
            (w.lemmaRef && w.lemmaRef.includes(searchTerm)) ||
            w.text.toLowerCase().includes(searchTerm.toLowerCase())
        );

        this.displayResults(
            `🔍 Lemma-Suche: "${searchTerm}" (${matches.length} Treffer)`,
            matches.map(m => ({
                meta: `${m.filename} • ${m.lemmaRef ? `Lemma: ${m.lemmaRef.split('#').pop()}` : 'Textsuche'}`,
                snippet: `<span class="highlight">${m.text}</span>`
            }))
        );
    }

    showAnnotations() {
        this.displayResults(
            `🏷️ Alle Annotationen aus TEI Texten (${this.teiData.annotations.length} Annotationen)`,
            this.teiData.annotations.map(a => ({
                meta: `${a.filename} • ${a.tagName}${a.meaningRef ? ` • Meaning: ${a.meaningRef.split('#').pop()}` : ''}`,
                snippet: a.text
            }))
        );
    }

    executeXPath() {
        const xpath = document.getElementById('xpathInput').value.trim();
        const target = document.getElementById('xpathTarget').value;
        
        if (!xpath) return;

        const results = [];
        let targetData = [];

        // Determine target data
        switch(target) {
            case 'authority':
                targetData = this.authorityData.parsedXML;
                break;
            case 'tei':
                targetData = this.teiData.parsedXML;
                break;
            default:
                targetData = [...this.authorityData.parsedXML, ...this.teiData.parsedXML];
        }

        targetData.forEach(xmlData => {
            try {
                const xpathResult = xmlData.doc.evaluate(
                    xpath,
                    xmlData.doc,
                    null,
                    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                    null
                );

                for (let i = 0; i < xpathResult.snapshotLength; i++) {
                    const node = xpathResult.snapshotItem(i);
                    results.push({
                        meta: `${xmlData.filename} • Node: ${node.nodeName}`,
                        snippet: node.textContent?.trim() || node.outerHTML?.substring(0, 300) + '...'
                    });
                }
            } catch (error) {
                results.push({
                    meta: `❌ XPath Error in ${xmlData.filename}`,
                    snippet: error.message
                });
            }
        });

        this.displayResults(`⚡ XPath auf ${target}: ${xpath}`, results);
    }

    // ==================== UI HELPER METHODS ====================

    updateStatus(indicator, text) {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        if (statusIndicator) statusIndicator.textContent = indicator;
        if (statusText) statusText.textContent = text;
    }

    displayFileItem(file, container) {
        if (!container) return;

        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-name">${file.name}</div>
            <div class="file-info">${(file.size / 1024).toFixed(1)} KB • TEI Textdatei</div>
        `;
        container.appendChild(fileItem);
    }

    updateAuthorityOverview() {
        const stats = document.getElementById('authorityStats');
        if (!stats) return;

        stats.innerHTML = `
            <div class="data-stat">
                <span class="label">📄 Authority Files:</span>
                <span class="value">${this.authorityData.files.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">👥 Personen:</span>
                <span class="value">${this.authorityData.persons.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">📚 Werke:</span>
                <span class="value">${this.authorityData.works.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">🔤 Lemmata:</span>
                <span class="value">${this.authorityData.lemmata.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">💭 Konzepte:</span>
                <span class="value">${this.authorityData.concepts.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">🎭 Gattungen:</span>
                <span class="value">${this.authorityData.genres.length}</span>
            </div>
            <div class="data-stat">
                <span class="label">📛 Namen:</span>
                <span class="value">${this.authorityData.names.length}</span>
            </div>
        `;
    }

    updateTEIOverview() {
        const overview = document.getElementById('teiOverview');
        const stats = document.getElementById('teiStats');

        if (this.teiData.files.length > 0 && overview && stats) {
            overview.style.display = 'block';
            stats.innerHTML = `
                <div class="data-stat">
                    <span class="label">📄 TEI Dateien:</span>
                    <span class="value">${this.teiData.files.length}</span>
                </div>
                <div class="data-stat">
                    <span class="label">📝 Wörter:</span>
                    <span class="value">${this.teiData.words.length}</span>
                </div>
                <div class="data-stat">
                    <span class="label">📏 Textzeilen:</span>
                    <span class="value">${this.teiData.lines.length}</span>
                </div>
                <div class="data-stat">
                    <span class="label">🏷️ Annotationen:</span>
                    <span class="value">${this.teiData.annotations.length}</span>
                </div>
            `;
        }
    }

    enableAuthorityQueries() {
        const buttonIds = [
            'showAuthorsBtn', 'showWorksBtn', 'showLemmataBtn',
            'showConceptsBtn', 'showGenresBtn', 'showNamesBtn', 'xpathExecute'
        ];

        buttonIds.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = false;
            }
        });
    }

    enableTEIQueries() {
        const teiQueriesSection = document.getElementById('teiQueries');
        if (teiQueriesSection) {
            teiQueriesSection.style.display = 'block';
        }
    }

    displayResults(title, results) {
        const container = document.getElementById('resultsContainer');
        if (!container) return;
        
        if (results.length === 0) {
            container.innerHTML = `
                <div class="result-item">
                    <div class="result-meta">${title}</div>
                    <div class="result-snippet">Keine Ergebnisse gefunden.</div>
                </div>
            `;
            return;
        }

        const resultsHTML = results.map(result => `
            <div class="result-item">
                <div class="result-meta">${result.meta}</div>
                <div class="result-snippet">${result.snippet}</div>
            </div>
        `).join('');

        container.innerHTML = `
            <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">
                ${title} (${results.length} Ergebnisse)
            </div>
            ${resultsHTML}
        `;
    }

    showWelcomeMessage() {
        const container = document.getElementById('resultsContainer');
        if (!container) return;

        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #667eea;">
                <h3>🎉 MHDBDB Playground bereit!</h3>
                <p style="margin-top: 10px; color: #666;">
                    Authority Files sind geladen. Laden Sie TEI-Textdateien hoch oder beginnen Sie mit der Analyse der Authority Files.
                </p>
            </div>
        `;
    }

    showError(message) {
        const container = document.getElementById('resultsContainer');
        if (!container) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = message;
        container.insertBefore(errorDiv, container.firstChild);
    }

    // ==================== UTILITY METHODS ====================

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
}

// Initialize the playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new MHDBDBPlayground();
});