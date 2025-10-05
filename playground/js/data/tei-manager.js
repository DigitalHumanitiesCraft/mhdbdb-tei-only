/**
 * MHDBDB Playground - TEI Files Manager
 * Handles TEI file upload, parsing, and structural analysis with IndexedDB
 */

import { TEIStorageManager } from './storage/tei-storage.js';

export class TEIFilesManager {
    constructor(teiData) {
        this.teiData = teiData;
        this.storageManager = new TEIStorageManager();
    }

    // ==================== FILE VALIDATION ====================

    isTEIFile(file) {
        return file.type === 'text/xml' ||
               file.name.endsWith('.xml') ||
               file.name.endsWith('.tei');
    }

    // ==================== DATA MANAGEMENT ====================

    /**
     * Clear all TEI data (used when switching between upload and corpus loading)
     */
    async clearAllTEIData() {
        console.log('🗑️ Clearing all TEI data...');

        // Clear in-memory data
        this.teiData.files = [];
        this.teiData.parsedXML = [];
        this.teiData.words = [];
        this.teiData.lines = [];
        this.teiData.annotations = [];
        this.teiData.lemmaCounts = {};

        // Clear storage cache (IndexedDB)
        await this.storageManager.clearAllCache();

        console.log('✅ All TEI data cleared');
    }

    // ==================== SESSION STORAGE INTEGRATION ====================

    async loadFromCache() {
        try {
            const cachedFiles = await this.storageManager.listCachedFiles();
            let loadedCount = 0;

            for (const cachedFile of cachedFiles) {
                const content = await this.storageManager.loadFromCache(cachedFile.filename);
                if (content) {
                    await this.processTEIFromContent(cachedFile.filename, content, true);
                    loadedCount++;
                }
            }

            if (loadedCount > 0) {
                console.log(`📁 Loaded ${loadedCount} TEI files from IndexedDB cache`);
            }

            return loadedCount;
        } catch (error) {
            console.error('❌ Error loading TEI files from storage:', error);
            return 0;
        }
    }

    async processTEIFromContent(filename, content, isCachedFile = false, fileObj = null) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(content, 'text/xml');

            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                throw new Error('XML Parsing Error: ' + parseError.textContent);
            }

            // Extract metadata from TEI header
            const metadata = this.extractTEIMetadata(xmlDoc);

            // Create a file-like object if not provided
            if (!fileObj) {
                fileObj = {
                    name: filename,
                    size: content.length,
                    type: 'text/xml',
                    isCachedFile: isCachedFile,
                    // Add extracted metadata
                    title: metadata.title,
                    author: metadata.author,
                    authorRef: metadata.authorRef
                };
            } else {
                // Add session file flag and metadata to existing file object
                fileObj.isCachedFile = isCachedFile;
                fileObj.title = metadata.title;
                fileObj.author = metadata.author;
                fileObj.authorRef = metadata.authorRef;
            }

            this.teiData.files.push(fileObj);
            this.teiData.parsedXML.push({
                filename: filename,
                doc: xmlDoc,
                content: content,
                isCachedFile: isCachedFile
            });

            this.analyzeTEIStructure(xmlDoc, filename);
            console.log(`TEI File processed: ${filename} ${isCachedFile ? '(from cache)' : ''}`);

        } catch (error) {
            console.error(`Error processing ${filename}:`, error);
            throw error;
        }
    }

    extractTEIMetadata(xmlDoc) {
        const metadata = {
            title: '',
            author: '',
            authorRef: ''
        };

        try {
            // Extract title from titleStmt
            const titleElement = xmlDoc.querySelector('titleStmt title[xml\\:lang="de"]') ||
                                 xmlDoc.querySelector('titleStmt title');
            if (titleElement) {
                metadata.title = titleElement.textContent.trim();
            }

            // Extract author from titleStmt
            const authorElement = xmlDoc.querySelector('titleStmt author');
            if (authorElement) {
                metadata.author = authorElement.textContent.trim();
                metadata.authorRef = authorElement.getAttribute('ref') || '';
            }
        } catch (error) {
            console.warn(`Failed to extract metadata:`, error);
        }

        return metadata;
    }

    // ==================== FILE PROCESSING ====================

    async processTEIFile(file) {
        try {
            // Check if file is already in storage to avoid duplicates
            if (await this.storageManager.isInCache(file.name)) {
                console.log(`⚠️ File ${file.name} already exists in storage`);
                return 'duplicate';
            }

            const content = await this.readFileAsText(file);

            // Try to save to storage
            const savedToCache = await this.storageManager.saveToCache(file.name, content);

            // Process the file
            await this.processTEIFromContent(file.name, content, false, file);

            // Add storage info
            const lastIndex = this.teiData.files.length - 1;
            if (this.teiData.files[lastIndex]) {
                this.teiData.files[lastIndex].savedToCache = savedToCache;
            }

        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            throw error;
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

        console.log(`TEI Analysis complete: ${words.length} words, ${lines.length} lines, ${annotatedElements.length} annotations`);
    }

    // ==================== SEARCH AND FILTERING ====================

    searchWordsInText(searchTerm) {
        return this.teiData.words.filter(word => 
            (word.lemmaRef && word.lemmaRef.includes(searchTerm)) ||
            word.text.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    findWordsByLemmaRef(lemmaRef) {
        return this.teiData.words.filter(word => 
            word.lemmaRef && word.lemmaRef.includes(lemmaRef)
        );
    }

    findLinesByText(searchTerm) {
        return this.teiData.lines.filter(line => 
            line.text.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    getWordContext(wordIndex, filename, contextSize = 3) {
        // Find surrounding words for context
        const wordsInFile = this.teiData.words.filter(w => w.filename === filename);
        const targetWordIndex = wordsInFile.findIndex(w => w.index === wordIndex);
        
        if (targetWordIndex === -1) return null;

        const start = Math.max(0, targetWordIndex - contextSize);
        const end = Math.min(wordsInFile.length, targetWordIndex + contextSize + 1);
        
        return wordsInFile.slice(start, end);
    }

    getLineContext(lineNumber, filename, contextSize = 2) {
        // Find surrounding lines for context
        const linesInFile = this.teiData.lines.filter(l => l.filename === filename);
        const targetLine = linesInFile.find(l => l.n === lineNumber);
        
        if (!targetLine) return null;

        const targetIndex = linesInFile.indexOf(targetLine);
        const start = Math.max(0, targetIndex - contextSize);
        const end = Math.min(linesInFile.length, targetIndex + contextSize + 1);
        
        return linesInFile.slice(start, end);
    }

    // ==================== CROSS-REFERENCE RESOLUTION ====================

    resolveLemmaReferences(authorityData) {
        // Add resolved lemma information to words
        return this.teiData.words.map(word => {
            if (!word.lemmaRef) return word;

            const lemmaId = word.lemmaRef.split('#')[1];
            const lemma = authorityData.lemmata.find(l => l.id === lemmaId);
            
            return {
                ...word,
                resolvedLemma: lemma
            };
        });
    }

    resolveConceptReferences(authorityData) {
        // Add resolved concept information to annotations
        return this.teiData.annotations.map(annotation => {
            const resolvedConcepts = [];
            
            if (annotation.conceptRef) {
                const conceptId = annotation.conceptRef.split('#')[1];
                const concept = authorityData.concepts.find(c => c.id === conceptId);
                if (concept) resolvedConcepts.push(concept);
            }
            
            return {
                ...annotation,
                resolvedConcepts
            };
        });
    }

    // ==================== STATISTICAL ANALYSIS ====================

    getWordFrequency() {
        const frequency = {};
        this.teiData.words.forEach(word => {
            const text = word.text.toLowerCase();
            frequency[text] = (frequency[text] || 0) + 1;
        });
        
        return Object.entries(frequency)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 100); // Top 100 most frequent words
    }

    getLemmaFrequency() {
        const frequency = {};
        this.teiData.words.forEach(word => {
            if (word.lemmaRef) {
                const lemmaId = word.lemmaRef.split('#')[1];
                frequency[lemmaId] = (frequency[lemmaId] || 0) + 1;
            }
        });
        
        return Object.entries(frequency)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 50); // Top 50 most frequent lemmata
    }

    getPOSDistribution() {
        const distribution = {};
        this.teiData.words.forEach(word => {
            if (word.pos) {
                distribution[word.pos] = (distribution[word.pos] || 0) + 1;
            }
        });
        
        return distribution;
    }

    // ==================== EXPORT FUNCTIONS ====================

    exportWordsAsCSV() {
        const headers = ['filename', 'text', 'pos', 'lemmaRef', 'line'];
        const rows = this.teiData.words.map(word => [
            word.filename,
            word.text,
            word.pos || '',
            word.lemmaRef || '',
            word.line || ''
        ]);
        
        return this.arrayToCSV([headers, ...rows]);
    }

    exportLinesAsCSV() {
        const headers = ['filename', 'lineNumber', 'text'];
        const rows = this.teiData.lines.map(line => [
            line.filename,
            line.n || '',
            line.text
        ]);
        
        return this.arrayToCSV([headers, ...rows]);
    }

    exportAnnotationsAsCSV() {
        const headers = ['filename', 'text', 'tagName', 'meaningRef', 'conceptRef'];
        const rows = this.teiData.annotations.map(annotation => [
            annotation.filename,
            annotation.text,
            annotation.tagName,
            annotation.meaningRef || '',
            annotation.conceptRef || ''
        ]);
        
        return this.arrayToCSV([headers, ...rows]);
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

    arrayToCSV(array) {
        return array.map(row => 
            row.map(field => 
                typeof field === 'string' && field.includes(',') 
                    ? `"${field.replace(/"/g, '""')}"` 
                    : field
            ).join(',')
        ).join('\n');
    }

    // ==================== XPATH UTILITIES ====================

    executeXPathOnTEI(xpath) {
        const results = [];

        this.teiData.parsedXML.forEach(xmlData => {
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
                        filename: xmlData.filename,
                        nodeName: node.nodeName,
                        textContent: node.textContent?.trim(),
                        outerHTML: node.outerHTML?.substring(0, 300)
                    });
                }
            } catch (error) {
                results.push({
                    filename: xmlData.filename,
                    error: error.message
                });
            }
        });

        return results;
    }

    // ==================== MULTI-LEMMA SEARCH ====================

    /**
     * Helper method to get XML doc from either uploaded file or corpus index
     * Handles both structures transparently
     */
    async getXMLDoc(xmlData) {
        // Check if this is an uploaded file (has 'doc' property)
        if (xmlData.doc) {
            return xmlData.doc;
        }

        // Otherwise, it's from corpus index (has xmlDoc getter that returns a Promise)
        if ('xmlDoc' in xmlData) {
            try {
                // xmlDoc is a getter, not a function - access it as a property
                const doc = await xmlData.xmlDoc;
                return doc;
            } catch (error) {
                console.error(`Failed to load XML for ${xmlData.filename}:`, error);
                return null;
            }
        }

        console.warn(`No XML doc available for ${xmlData.filename}`);
        return null;
    }

    async searchMultipleLemmas(lemmaIds, contextType = 'document') {
        const results = [];

        for (const xmlData of this.teiData.parsedXML) {
            // Get XML doc (handles both uploaded files and corpus index)
            const doc = await this.getXMLDoc(xmlData);
            if (!doc) continue;

            if (contextType === 'document') {
                // Search across entire document
                const containsAllLemmas = lemmaIds.every(lemmaId => {
                    const elements = doc.querySelectorAll(`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`);
                    return elements.length > 0;
                });

                if (containsAllLemmas) {
                    const matchingWords = this.extractMatchingWordsFromDocument(doc, lemmaIds);
                    results.push({
                        filename: xmlData.filename,
                        context: 'document',
                        matchingWords: matchingWords,
                        totalWords: this.teiData.words.filter(w => w.filename === xmlData.filename).length
                    });
                }
            }
        }

        return results;
    }

    async findCooccurringLemmas(lemmaIds, maxDistance = 10) {
        const results = [];

        for (const xmlData of this.teiData.parsedXML) {
            // Get XML doc (handles both uploaded files and corpus index)
            const doc = await this.getXMLDoc(xmlData);
            if (!doc) continue;

            const words = doc.querySelectorAll('w');
            const wordArray = Array.from(words);
            
            // Find positions of each lemma
            const lemmaPositions = {};
            lemmaIds.forEach(lemmaId => {
                lemmaPositions[lemmaId] = [];
                wordArray.forEach((word, index) => {
                    const lemmaRef = word.getAttribute('lemmaRef');
                    if (lemmaRef && lemmaRef.includes(`lexicon.xml#lemma_${lemmaId}`)) {
                        lemmaPositions[lemmaId].push({
                            index: index,
                            word: word,
                            text: word.textContent?.trim()
                        });
                    }
                });
            });
            
            // Find co-occurrences within specified distance
            const cooccurrences = this.findProximityMatches(lemmaPositions, maxDistance, wordArray);
            
            if (cooccurrences.length > 0) {
                results.push({
                    filename: xmlData.filename,
                    cooccurrences: cooccurrences,
                    maxDistance: maxDistance
                });
            }
        }

        return results;
    }

    extractMatchingWordsFromParagraph(paragraph, lemmaIds) {
        const matchingWords = {};
        
        lemmaIds.forEach(lemmaId => {
            matchingWords[lemmaId] = [];
            
            // Try multiple selector approaches
            const selectors = [
                `w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`,
                `w[lemmaRef="lexicon.xml#lemma_${lemmaId}"]`,
                `w[lemmaRef$="#lemma_${lemmaId}"]`
            ];
            
            const foundWords = new Set(); // Avoid duplicates
            
            selectors.forEach(selector => {
                const words = paragraph.querySelectorAll(selector);
                words.forEach(word => {
                    const wordId = word.getAttribute('xml:id');
                    if (!foundWords.has(wordId)) {
                        foundWords.add(wordId);
                        matchingWords[lemmaId].push({
                            text: word.textContent?.trim(),
                            id: wordId,
                            lemmaRef: word.getAttribute('lemmaRef')
                        });
                    }
                });
            });
            
        });
        
        return matchingWords;
    }

    extractMatchingWordsFromDocument(doc, lemmaIds) {
        const matchingWords = {};
        
        lemmaIds.forEach(lemmaId => {
            matchingWords[lemmaId] = [];
            
            // Try multiple selector approaches
            const selectors = [
                `w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`,
                `w[lemmaRef="lexicon.xml#lemma_${lemmaId}"]`,
                `w[lemmaRef$="#lemma_${lemmaId}"]`
            ];
            
            const foundWords = new Set(); // Avoid duplicates
            
            selectors.forEach(selector => {
                const words = doc.querySelectorAll(selector);
                words.forEach(word => {
                    const wordId = word.getAttribute('xml:id');
                    if (!foundWords.has(wordId)) {
                        foundWords.add(wordId);
                        matchingWords[lemmaId].push({
                            text: word.textContent?.trim(),
                            id: wordId,
                            lemmaRef: word.getAttribute('lemmaRef'),
                            context: this.getWordParagraphContext(word)
                        });
                    }
                });
            });
            
        });
        
        return matchingWords;
    }

    findProximityMatches(lemmaPositions, maxDistance, wordArray) {
        const cooccurrences = [];
        const lemmaIds = Object.keys(lemmaPositions);
        
        if (lemmaIds.length < 2) return cooccurrences;
        
        // Compare positions between first lemma and others
        const firstLemmaId = lemmaIds[0];
        const firstLemmaPositions = lemmaPositions[firstLemmaId];
        
        firstLemmaPositions.forEach(firstPos => {
            lemmaIds.slice(1).forEach(otherLemmaId => {
                const otherPositions = lemmaPositions[otherLemmaId];
                
                otherPositions.forEach(otherPos => {
                    const distance = Math.abs(firstPos.index - otherPos.index);
                    
                    if (distance <= maxDistance) {
                        const startIndex = Math.min(firstPos.index, otherPos.index);
                        const endIndex = Math.max(firstPos.index, otherPos.index);
                        const contextWords = wordArray.slice(
                            Math.max(0, startIndex - 3),
                            Math.min(wordArray.length, endIndex + 4)
                        );
                        
                        cooccurrences.push({
                            lemma1: { id: firstLemmaId, ...firstPos },
                            lemma2: { id: otherLemmaId, ...otherPos },
                            distance: distance,
                            context: contextWords.map(w => w.textContent?.trim()).join(' ')
                        });
                    }
                });
            });
        });
        
        return cooccurrences;
    }

    getWordParagraphContext(wordElement) {
        const paragraph = wordElement.closest('p');
        if (paragraph) {
            return {
                paragraphId: paragraph.getAttribute('n') || paragraph.getAttribute('xml:id'),
                text: paragraph.textContent?.trim().substring(0, 200) + '...'
            };
        }
        return null;
    }

    // ==================== SESSION MANAGEMENT ====================

    async removeTEIFile(filename) {
        try {
            // Remove from storage
            const removedFromStorage = await this.storageManager.removeFromCache(filename);

            // Remove from in-memory data
            this.teiData.files = this.teiData.files.filter(file => file && file.name !== filename);
            this.teiData.parsedXML = this.teiData.parsedXML.filter(xml => xml.filename !== filename);

            // Remove related analysis data
            this.teiData.words = this.teiData.words.filter(word => word.filename !== filename);
            this.teiData.lines = this.teiData.lines.filter(line => line.filename !== filename);
            this.teiData.annotations = this.teiData.annotations.filter(annotation => annotation.filename !== filename);

            console.log(`🗑️ TEI file removed: ${filename}`);
            return removedFromStorage;
        } catch (error) {
            console.error(`❌ Error removing ${filename}:`, error);
            return false;
        }
    }

    async clearAllCachedFiles() {
        try {
            const cachedFiles = await this.storageManager.listCachedFiles();

            // Remove all files from storage
            const removedCount = await this.storageManager.clearAllCache();

            // Remove session files from in-memory data
            this.teiData.files = this.teiData.files.filter(file => !file || !file.isCachedFile);
            this.teiData.parsedXML = this.teiData.parsedXML.filter(xml => !xml.isCachedFile);

            // Remove related analysis data for session files
            cachedFiles.forEach(cachedFile => {
                const filename = cachedFile.filename;
                this.teiData.words = this.teiData.words.filter(word => word.filename !== filename);
                this.teiData.lines = this.teiData.lines.filter(line => line.filename !== filename);
                this.teiData.annotations = this.teiData.annotations.filter(annotation => annotation.filename !== filename);
            });

            console.log(`🧹 Cleared all cached TEI files: ${removedCount} files removed`);
            return removedCount;
        } catch (error) {
            console.error('❌ Error clearing all cached files:', error);
            return 0;
        }
    }

    async getStorageInfo() {
        return {
            cachedFiles: await this.storageManager.listCachedFiles(),
            quota: await this.storageManager.getStorageQuotaInfo(),
            stats: await this.storageManager.getStorageStats()
        };
    }

    // ==================== CORPUS LOADING ====================

    async loadCorpusIntoPlayground(progressCallback) {
        console.log('📦 Loading corpus into playground using pre-built index...');

        try {
            // Dynamically import CorpusLoader from main site
            const { CorpusLoader } = await import('/lib/corpus-loader.js');

            // Create corpus loader with correct base path (playground is in playground/ subdirectory)
            const corpusLoader = new CorpusLoader('../data');

            // Wait for database to initialize
            await corpusLoader.dbReady;

            // Load corpus index
            if (progressCallback) progressCallback(0, 666);
            console.log('📥 Loading corpus index...');
            const corpusIndex = await corpusLoader.loadCorpusIndex();

            console.log(`📚 Corpus index loaded: ${corpusIndex.texts.length} texts`);

            // Create TEI file wrappers (lazy-loading)
            let loadedCount = 0;
            for (const text of corpusIndex.texts) {
                // Create metadata structure compatible with playground
                const teiData = {
                    filename: text.filename,
                    title: text.title,
                    author: text.author,
                    authorRef: text.authorRef,
                    workRef: text.workRef,
                    genre: text.genre || '',
                    wordCount: text.wordCount,
                    lemmata: text.lemmata,

                    // Lazy-load full XML when needed
                    _xml: null,
                    get xmlDoc() {
                        if (!this._xml) {
                            return this.loadXML();
                        }
                        return Promise.resolve(this._xml);
                    },
                    async loadXML() {
                        if (this._xml) return this._xml;

                        try {
                            const response = await fetch(`../tei/${this.filename}`);
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}`);
                            }
                            const xmlText = await response.text();
                            const parser = new DOMParser();
                            this._xml = parser.parseFromString(xmlText, 'text/xml');
                            return this._xml;
                        } catch (error) {
                            console.error(`Failed to load XML for ${this.filename}:`, error);
                            throw error;
                        }
                    }
                };

                // Add to playground's TEI files list (both files and parsedXML arrays)
                // Note: We don't add to this.teiData.files (file objects), only to parsedXML
                this.teiData.parsedXML.push(teiData);
                loadedCount++;

                if (progressCallback && loadedCount % 10 === 0) {
                    progressCallback(loadedCount, corpusIndex.texts.length);
                }
            }

            if (progressCallback) progressCallback(loadedCount, corpusIndex.texts.length);

            console.log(`✅ Corpus loaded: ${loadedCount} files (lazy-loading enabled)`);

            // Store corpus index reference for fast searches
            this.corpusIndex = corpusIndex;

            return { loaded: loadedCount, skipped: 0, total: loadedCount };

        } catch (error) {
            console.error('❌ Corpus loading failed:', error);
            throw error;
        }
    }

    // ==================== INDEX-BASED SEARCH (FAST) ====================

    /**
     * Check if corpus is loaded from pre-built index (enables fast search)
     */
    hasCorpusIndex() {
        return this.corpusIndex && this.corpusIndex.texts && this.corpusIndex.lemmaIndex;
    }

    /**
     * Find texts containing all specified lemmas using index (instant filtering)
     */
    findTextsContainingLemmas(lemmaIds) {
        if (!this.hasCorpusIndex()) return null;

        console.log(`🔍 Filtering ${this.corpusIndex.texts.length} texts using index...`);

        // Get texts for each lemma from lemmaIndex
        const textSets = lemmaIds.map(lemmaId => {
            const lemmaKey = lemmaId.toString().startsWith('lemma_') ? lemmaId : `lemma_${lemmaId}`;
            return new Set(this.corpusIndex.lemmaIndex[lemmaKey] || []);
        });

        // Find intersection (texts containing ALL lemmas)
        const firstSet = textSets[0];
        const intersection = Array.from(firstSet).filter(textId =>
            textSets.every(set => set.has(textId))
        );

        console.log(`   Found ${intersection.length} texts containing all ${lemmaIds.length} lemmas`);
        return intersection;
    }

    /**
     * Find proximity matches using index data (word positions)
     * Returns: {textId: [{lemma1Pos, lemma2Pos, distance}, ...]}
     */
    findProximityMatchesInIndex(lemmaIds, maxDistance) {
        if (!this.hasCorpusIndex()) return null;

        const candidateTextIds = this.findTextsContainingLemmas(lemmaIds);
        if (!candidateTextIds || candidateTextIds.length === 0) return {};

        console.log(`🔍 Checking proximity in ${candidateTextIds.length} candidate texts...`);

        const matches = {};

        for (const textId of candidateTextIds) {
            // Find text data
            const text = this.corpusIndex.texts.find(t => t.id === textId);
            if (!text || !text.lemmata) continue;

            // Get positions for each lemma
            const positionSets = lemmaIds.map(lemmaId => {
                const lemmaKey = lemmaId.toString().startsWith('lemma_') ? lemmaId : `lemma_${lemmaId}`;
                return text.lemmata[lemmaKey] || [];
            });

            // Check all position combinations for proximity
            const proximityMatches = [];

            // For each position of first lemma
            for (const pos1 of positionSets[0]) {
                // Check if any position of second lemma is within maxDistance
                for (const pos2 of positionSets[1]) {
                    const distance = Math.abs(pos1 - pos2);
                    if (distance <= maxDistance && distance > 0) {
                        proximityMatches.push({
                            positions: [pos1, pos2],
                            distance: distance
                        });
                    }
                }
            }

            if (proximityMatches.length > 0) {
                matches[textId] = proximityMatches;
            }
        }

        console.log(`   Found ${Object.keys(matches).length} texts with proximity matches`);
        return matches;
    }

    /**
     * Fast multi-lemma search using index data (when available)
     * Falls back to XML search for uploaded files
     */
    async searchMultipleLemmasUsingIndex(lemmaIds, contextType = 'document', maxDistance = 10) {
        // v4.0.0: Use document-level index (no paragraph mode)
        const corpusData = window.playground?.corpusData;
        if (!corpusData || !corpusData.texts) {
            console.warn('⚠️ Corpus data not available, falling back to XML search');
            // Fallback to old XML-based search
            if (contextType === 'proximity') {
                return await this.findCooccurringLemmas(lemmaIds, maxDistance);
            } else {
                return await this.searchMultipleLemmas(lemmaIds, contextType);
            }
        }

        // v4.0.0: Pure index-based search (instant results!)
        console.log(`🚀 Using enhanced corpus index v${corpusData.version || '4.0.0'} (${contextType} search)`);

        if (contextType === 'proximity') {
            return this.searchProximityUsingEnhancedIndex(lemmaIds, maxDistance, corpusData);
        } else if (contextType === 'document') {
            return this.searchDocumentUsingEnhancedIndex(lemmaIds, corpusData);
        }

        return [];
    }

    /**
     * v4.0.0: Document search using index (fast filtering)
     * Paragraph mode removed in v4.0.0
     */
    async searchDocumentUsingIndex(lemmaIds) {
        console.log(`🚀 Using index-based document search (fast path)`);

        // Step 1: Fast filtering using index
        const candidateTextIds = this.findTextsContainingLemmas(lemmaIds);
        if (!candidateTextIds || candidateTextIds.length === 0) return [];

        const results = [];

        // Step 2: Load XML only for matching texts
        console.log(`📥 Loading XML for ${candidateTextIds.length} matching texts...`);

        for (const textId of candidateTextIds) {
            const textData = this.teiData.parsedXML.find(t =>
                t.filename && t.filename.replace('.tei.xml', '') === textId
            );

            if (!textData) continue;

            const doc = await this.getXMLDoc(textData);
            if (!doc) continue;

            // Document-level search (already filtered by index)
            const matchingWords = this.extractMatchingWordsFromDocument(doc, lemmaIds);
            results.push({
                filename: textData.filename,
                title: textData.title,
                author: textData.author,
                context: 'document',
                matchingWords: matchingWords,
                totalWords: Object.values(textData.lemmata || {}).flat().length
            });
        }

        console.log(`✅ Index-based search complete: ${results.length} matches`);
        return results;
    }

    /**
     * Proximity search using index data (super fast!)
     */
    async searchProximityUsingIndex(lemmaIds, maxDistance) {
        console.log(`🚀 Using index-based proximity search (fast path)`);

        const proximityMatches = this.findProximityMatchesInIndex(lemmaIds, maxDistance);
        if (!proximityMatches) {
            // Index not available, fall back to XML search
            console.log('   Index not available, falling back to XML search');
            return await this.findCooccurringLemmas(lemmaIds, maxDistance);
        }

        const results = [];

        // Now fetch XML only for matching texts (not all 666!)
        console.log(`📥 Loading XML for ${Object.keys(proximityMatches).length} matching texts...`);

        for (const [textId, matches] of Object.entries(proximityMatches)) {
            // Find the text data
            const textData = this.teiData.parsedXML.find(t =>
                t.filename && t.filename.replace('.tei.xml', '') === textId
            );

            if (!textData) {
                console.warn(`   Text ${textId} not found in parsedXML`);
                continue;
            }

            // Load XML for this specific text
            const doc = await this.getXMLDoc(textData);
            if (!doc) continue;

            // Get all words
            const words = doc.querySelectorAll('w');
            const wordArray = Array.from(words);

            // Extract context for each proximity match
            for (const match of matches) {
                const positions = match.positions;
                const distance = match.distance;

                // Get surrounding context (±10 words)
                const minPos = Math.min(...positions);
                const maxPos = Math.max(...positions);
                const contextStart = Math.max(0, minPos - 10);
                const contextEnd = Math.min(wordArray.length, maxPos + 10);

                const contextWords = wordArray.slice(contextStart, contextEnd);
                const contextText = contextWords.map(w => w.textContent).join(' ');

                // Highlight the matching words
                const highlightedWords = {};
                lemmaIds.forEach((lemmaId, idx) => {
                    highlightedWords[lemmaId] = positions[idx];
                });

                results.push({
                    filename: textData.filename,
                    title: textData.title,
                    author: textData.author,
                    matchPositions: positions,
                    distance: distance,
                    contextText: contextText,
                    contextStart: contextStart,
                    contextEnd: contextEnd
                });
            }
        }

        console.log(`✅ Index-based search complete: ${results.length} proximity matches`);
        return results;
    }

    // ========== REDESIGN: Enhanced Index Search Methods (v2.0.0) ==========
    // These methods use the pre-built corpus index with full word data
    // NO XML LOADING REQUIRED - instant results!

    /**
     * Document-level search using enhanced index (instant!)
     * Returns texts that contain all specified lemmas
     */
    searchDocumentUsingEnhancedIndex(lemmaIds, corpusData) {
        const results = [];
        const includedTexts = corpusData.includedTexts || new Set();

        corpusData.texts.forEach(text => {
            // Skip excluded texts
            if (!includedTexts.has(text.id)) return;

            // Check if text contains all lemmas
            const containsAll = lemmaIds.every(lemmaId => {
                const cleanId = lemmaId.toString().replace('lemma_', '');
                return text.lemmata && (text.lemmata[`lemma_${cleanId}`] || text.lemmata[cleanId]);
            });

            if (containsAll) {
                // Count total matches for each lemma
                const matchingWords = {};
                lemmaIds.forEach(lemmaId => {
                    const cleanId = lemmaId.toString().replace('lemma_', '');
                    const positions = text.lemmata[`lemma_${cleanId}`] || text.lemmata[cleanId] || [];
                    matchingWords[lemmaId] = positions.length;
                });

                results.push({
                    filename: text.filename,
                    title: text.title,
                    author: text.author || 'Unbekannt',
                    context: 'document',
                    matchingWords: matchingWords,
                    totalWords: text.wordCount
                });
            }
        });

        console.log(`✅ Document search complete: ${results.length} texts contain all lemmas`);
        return results;
    }

    // v4.0.0: Paragraph search removed (document-level indexing only)

    /**
     * Enrich v3.0.0 compact results with actual TEI text
     */
    async enrichResultsWithTEIText(results, lemmaIds) {
        console.log('📄 Fetching TEI files to extract actual text...');

        for (const result of results) {
            try {
                // Fetch TEI file
                const teiPath = `../tei/${result.filename}`;
                const response = await fetch(teiPath);
                if (!response.ok) continue;

                const xmlText = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(xmlText, 'text/xml');

                // Get paragraphs
                const paragraphs = doc.querySelectorAll('p, lg');
                const para = paragraphs[result.paragraphIndex];

                if (para) {
                    // Extract paragraph text
                    result.text = para.textContent?.trim() || '';

                    // Extract matching words with actual text
                    const words = para.querySelectorAll('w[lemmaRef]');
                    result.matchingWords = {};

                    lemmaIds.forEach(lemmaId => {
                        const cleanId = lemmaId.toString().replace('lemma_', '');
                        result.matchingWords[lemmaId] = [];

                        words.forEach(word => {
                            const lemmaRef = word.getAttribute('lemmaRef');
                            if (lemmaRef && (lemmaRef.includes(`lemma_${cleanId}`) || lemmaRef.includes(cleanId))) {
                                result.matchingWords[lemmaId].push({
                                    text: word.textContent?.trim() || '',
                                    lemmaRef: lemmaRef
                                });
                            }
                        });
                    });
                }
            } catch (error) {
                console.warn(`Failed to enrich ${result.filename}:`, error);
            }
        }

        console.log('✅ TEI text enrichment complete');
    }

    /**
     * Proximity search using enhanced index (instant!)
     * Finds lemmas within maxDistance words of each other
     */
    async searchProximityUsingEnhancedIndex(lemmaIds, maxDistance, corpusData) {
        const results = [];
        const includedTexts = corpusData.includedTexts || new Set();

        corpusData.texts.forEach(text => {
            // Skip excluded texts
            if (!includedTexts.has(text.id)) return;

            // Skip texts that don't have the enhanced data structure
            if (!text.words) {
                console.warn(`⚠️ Text ${text.id} missing enhanced index data (words)`);
                return;
            }

            // Find all positions for each lemma
            const lemmaPositions = {};
            lemmaIds.forEach(lemmaId => {
                const cleanId = lemmaId.toString().replace('lemma_', '');
                lemmaPositions[lemmaId] = [];

                text.words.forEach((lemmaRef, idx) => {
                    // v3.0.0: words array contains just lemma IDs as strings
                    const cleanLemmaRef = lemmaRef.replace('lemma_', '');
                    if (cleanLemmaRef === cleanId) {
                        lemmaPositions[lemmaId].push(idx);
                    }
                });
            });

            // Check if text contains all lemmas (quick validation)

            // Check if text contains all lemmas
            if (Object.values(lemmaPositions).some(positions => positions.length === 0)) {
                return; // Skip if any lemma is missing
            }

            // Find proximity matches
            // For each occurrence of the first lemma, check if other lemmas are nearby
            const firstLemma = lemmaIds[0];
            const firstPositions = lemmaPositions[firstLemma];

            firstPositions.forEach(firstPos => {
                // Check if all other lemmas have at least one occurrence within maxDistance
                const nearbyPositions = {};
                let allNearby = true;

                for (let i = 1; i < lemmaIds.length; i++) {
                    const lemmaId = lemmaIds[i];
                    const positions = lemmaPositions[lemmaId];

                    // Find closest position to firstPos
                    const nearbyPos = positions.find(pos =>
                        Math.abs(pos - firstPos) <= maxDistance
                    );

                    if (nearbyPos !== undefined) {
                        nearbyPositions[lemmaId] = nearbyPos;
                    } else {
                        allNearby = false;
                        break;
                    }
                }

                if (allNearby) {
                    // Calculate actual distance (max distance between any pair)
                    const allPositions = [firstPos, ...Object.values(nearbyPositions)];
                    const minPos = Math.min(...allPositions);
                    const maxPos = Math.max(...allPositions);
                    const actualDistance = maxPos - minPos;

                    // Extract context (±10 words)
                    const contextStart = Math.max(0, minPos - 10);
                    const contextEnd = Math.min(text.words.length, maxPos + 11);

                    // Store positions and metadata - UI will fetch TEI for actual text
                    results.push({
                        filename: text.filename,
                        title: text.title,
                        author: text.author || 'Unbekannt',
                        matchPositions: allPositions,
                        distance: actualDistance,
                        contextStart: contextStart,
                        contextEnd: contextEnd,
                        contextLemmas: text.words.slice(contextStart, contextEnd)
                    });
                }
            });
        });

        console.log(`✅ Proximity search complete: ${results.length} raw matches within ${maxDistance} words`);

        // v4.0.0: Deduplicate overlapping matches
        // Keep only the closest match when context windows overlap
        const deduplicated = [];

        // Group by filename first
        const byFile = {};
        results.forEach(result => {
            if (!byFile[result.filename]) byFile[result.filename] = [];
            byFile[result.filename].push(result);
        });

        // For each file, remove overlapping matches (keep closest)
        Object.entries(byFile).forEach(([filename, fileResults]) => {
            // Sort by contextStart for easier overlap detection
            fileResults.sort((a, b) => a.contextStart - b.contextStart);

            fileResults.forEach(result => {
                // Check if this result overlaps with any already added result
                const overlaps = deduplicated.some(existing => {
                    if (existing.filename !== result.filename) return false;

                    // Check if context windows overlap
                    const overlapStart = Math.max(existing.contextStart, result.contextStart);
                    const overlapEnd = Math.min(existing.contextEnd, result.contextEnd);
                    const hasOverlap = overlapStart < overlapEnd;

                    if (hasOverlap) {
                        console.log(`  🔄 Overlap detected: ${filename} [${result.contextStart}-${result.contextEnd}] overlaps with [${existing.contextStart}-${existing.contextEnd}], keeping shorter distance (${existing.distance} vs ${result.distance})`);
                    }

                    return hasOverlap;
                });

                if (!overlaps) {
                    deduplicated.push(result);
                }
            });
        });

        const removedCount = results.length - deduplicated.length;
        console.log(`✅ After deduplication: ${deduplicated.length} unique matches (${removedCount > 0 ? `removed ${removedCount} overlapping` : 'no overlaps'})`);

        // v3.0.0: Don't fetch TEI text immediately - only on expand

        return deduplicated;
    }

    /**
     * Enrich v3.0.0 proximity results with actual TEI text
     */
    async enrichProximityResultsWithText(results) {
        console.log('📄 Fetching TEI files for proximity context...');

        for (const result of results) {
            try {
                const teiPath = `../tei/${result.filename}`;
                const response = await fetch(teiPath);
                if (!response.ok) continue;

                const xmlText = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(xmlText, 'text/xml');

                // Get all words
                const words = doc.querySelectorAll('w');

                // Extract context text
                const contextWords = Array.from(words).slice(result.contextStart, result.contextEnd);
                result.contextText = contextWords.map(w => w.textContent?.trim()).join(' ');

            } catch (error) {
                console.warn(`Failed to enrich proximity result ${result.filename}:`, error);
            }
        }

        console.log('✅ Proximity text enrichment complete');
    }
}