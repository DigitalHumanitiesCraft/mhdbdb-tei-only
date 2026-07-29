/**
 * MHDBDB Playground - TEI Files Manager
 * Handles TEI file upload, parsing, and structural analysis with IndexedDB
 */

import { TEIStorageManager } from './storage/tei-storage.js';
import { lemmaRefMatchesId } from '../../../assets/js/lib/lemma-match.js';

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
        const annotatedElements = xmlDoc.querySelectorAll('[ana], [conceptRef]');
        annotatedElements.forEach((element, index) => {
            const ana = element.getAttribute('ana');
            const conceptRef = element.getAttribute('conceptRef');
            const text = element.textContent?.trim();
            
            this.teiData.annotations.push({
                text, ana, conceptRef, filename, index,
                tagName: element.tagName
            });
        });

        console.log(`TEI Analysis complete: ${words.length} words, ${lines.length} lines, ${annotatedElements.length} annotations`);
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
                // Search across entire document.
                // Exact lemma-id match (CONTRACTS §B.1) — never a substring:
                // the former *= selector matched lemma_3089 when searching lemma_308 (#126).
                const words = Array.from(doc.querySelectorAll('w[lemmaRef]'));
                const containsAllLemmas = lemmaIds.every(lemmaId =>
                    words.some(word => lemmaRefMatchesId(word.getAttribute('lemmaRef'), `lemma_${lemmaId}`))
                );

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
                    // Exact lemma-id match (CONTRACTS §B.1) — never a substring. See #126.
                    if (lemmaRefMatchesId(lemmaRef, `lemma_${lemmaId}`)) {
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

    extractMatchingWordsFromDocument(doc, lemmaIds) {
        const matchingWords = {};

        // Exact lemma-id match (CONTRACTS §B.1) — never a substring: the former
        // *= selector pulled lemma_3089 words into lemma_308 results (#126).
        // One pass per lemma over all w[lemmaRef]; no dedup needed since each
        // word is checked exactly once.
        const words = Array.from(doc.querySelectorAll('w[lemmaRef]'));

        lemmaIds.forEach(lemmaId => {
            matchingWords[lemmaId] = [];

            words.forEach(word => {
                if (lemmaRefMatchesId(word.getAttribute('lemmaRef'), `lemma_${lemmaId}`)) {
                    matchingWords[lemmaId].push({
                        text: word.textContent?.trim(),
                        id: word.getAttribute('xml:id'),
                        lemmaRef: word.getAttribute('lemmaRef'),
                        context: this.getWordParagraphContext(word)
                    });
                }
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
            const { CorpusLoader } = await import('../../../assets/js/lib/corpus-loader.js');

            // Create corpus loader with correct base path (playground is in playground/ subdirectory)
            const corpusLoader = new CorpusLoader('../data');

            // Wait for database to initialize
            await corpusLoader.dbReady;

            // Load corpus index
            if (progressCallback) progressCallback(0, 667);
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
            // Fallback to XML-based search if index unavailable
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
        } else if (contextType === 'verse') {
            return this.searchVerseUsingEnhancedIndex(lemmaIds, corpusData);
        } else if (contextType === 'document') {
            return this.searchDocumentUsingEnhancedIndex(lemmaIds, corpusData);
        }

        return [];
    }

    /**
     * "Im selben Vers"-Suche (#106 Punkt 8): Kookkurrenz eingeschränkt auf ein
     * gemeinsames <l>, über die lineStarts[]/lineEnds[]-Arrays des Corpus-Index
     * v4.1.0+ (CONTRACTS §B: word-index-Grenzen pro Vers, inklusive).
     *
     * Prosa-Texte (leere lineStarts) werden übersprungen — dort gibt es keine
     * Verse (#106 Caveat). Ergebnis-Shape ist identisch zur Proximity-Suche
     * (matchPositions/distance/contextStart/contextEnd/contextLemmas), plus
     * verseN (1-basierte Versnummer im Text) für die Anzeige; Expand und
     * Reader-Deep-Links funktionieren dadurch unverändert.
     */
    searchVerseUsingEnhancedIndex(lemmaIds, corpusData) {
        const results = [];
        const includedTexts = corpusData.includedTexts || new Set();

        // Binärsuche: Index des Verses, der Wortposition pos enthält, sonst -1.
        // lineStarts ist aufsteigend sortiert; Wörter außerhalb jedes <l>
        // (Überschriften, Noten) liegen zwischen lineEnds[v] und lineStarts[v+1].
        const verseIndexFor = (pos, lineStarts, lineEnds) => {
            let lo = 0, hi = lineStarts.length - 1, found = -1;
            while (lo <= hi) {
                const mid = (lo + hi) >> 1;
                if (lineStarts[mid] <= pos) { found = mid; lo = mid + 1; }
                else { hi = mid - 1; }
            }
            return (found !== -1 && pos <= lineEnds[found]) ? found : -1;
        };

        corpusData.texts.forEach(text => {
            if (!includedTexts.has(text.id)) return;
            if (!text.words || !text.lemmata) return;
            if (!text.lineStarts || text.lineStarts.length === 0) return; // Prosa

            // Alle Positionen je Lemma aus der Reverse-Map lemmata{} —
            // multi-ref-bewusst per CONTRACTS §B.1 (words[] hält nur die
            // erste @lemmaRef-ID pro <w>), wie findProximityMatchesInIndex.
            const lemmaPositions = {};
            lemmaIds.forEach(lemmaId => {
                const lemmaKey = lemmaId.toString().startsWith('lemma_') ? lemmaId : `lemma_${lemmaId}`;
                lemmaPositions[lemmaId] = text.lemmata[lemmaKey] || [];
            });
            if (Object.values(lemmaPositions).some(positions => positions.length === 0)) {
                return;
            }

            // Für jeden Vers, der das erste Lemma enthält: alle anderen prüfen.
            // Ein Vers zählt höchstens einmal (seenVerses), egal wie oft das
            // erste Lemma darin steht.
            const firstPositions = lemmaPositions[lemmaIds[0]];
            const seenVerses = new Set();

            firstPositions.forEach(firstPos => {
                const v = verseIndexFor(firstPos, text.lineStarts, text.lineEnds);
                if (v === -1 || seenVerses.has(v)) return;
                seenVerses.add(v);

                const vStart = text.lineStarts[v];
                const vEnd = text.lineEnds[v];
                const nearbyPositions = {};
                let allInVerse = true;
                for (let i = 1; i < lemmaIds.length; i++) {
                    const pos = lemmaPositions[lemmaIds[i]].find(p => p >= vStart && p <= vEnd);
                    if (pos === undefined) { allInVerse = false; break; }
                    nearbyPositions[lemmaIds[i]] = pos;
                }
                if (!allInVerse) return;

                const allPositions = [firstPos, ...Object.values(nearbyPositions)];
                const minPos = Math.min(...allPositions);
                const maxPos = Math.max(...allPositions);

                // Kontext: der ganze Vers plus etwas Umgebung
                const contextStart = Math.max(0, vStart - 5);
                const contextEnd = Math.min(text.words.length, vEnd + 6);

                results.push({
                    filename: text.filename,
                    title: text.title,
                    author: text.author || 'Unbekannt',
                    matchPositions: allPositions,
                    distance: maxPos - minPos,
                    verseN: v + 1,
                    contextStart: contextStart,
                    contextEnd: contextEnd,
                    contextLemmas: text.words.slice(contextStart, contextEnd)
                });
            });
        });

        console.log(`✅ Verse search complete: ${results.length} verses containing all lemmata`);
        return results;
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

        // Now fetch XML only for matching texts (not all 667!)
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
                            // Exact lemma-id match (CONTRACTS §B.1) — never a substring. See #126.
                            if (lemmaRefMatchesId(lemmaRef, `lemma_${cleanId}`)) {
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
     * Index der ersten Position >= value in einer aufsteigend sortierten Liste
     * (untere Schranke), sonst list.length.
     */
    lowerBound(list, value) {
        let lo = 0, hi = list.length;
        while (lo < hi) {
            const mid = (lo + hi) >> 1;
            if (list[mid] < value) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    /**
     * Kleinstes Fenster der Breite maxDistance, das firstPos und je eine
     * Position aus jeder weiteren Positionsliste enthält (#169 Befund #15).
     *
     * Vorher prüfte die Nähesuche jedes weitere Lemma nur gegen den Anker
     * firstPos. Bei „innerhalb 5 Wörter" passierten damit B bei Anker−5 und
     * C bei Anker+5 beide, obwohl sie real 10 auseinanderliegen. Die daneben
     * berechnete `actualDistance` meldete die 10 dann sogar korrekt: der
     * Filter hatte sie nur schon durchgelassen. KZW hat den Fix am 28.07. in
     * #169 freigegeben, sinkende Trefferzahlen ab 3 Lemmata inklusive.
     *
     * Es genügt nicht, die alte Auswahl nachträglich an der Spanne zu prüfen
     * und sonst zu verwerfen: `positions.find()` nahm die erste Position im
     * Ankerfenster, nicht die günstigste. Bei B = {90, 110}, C = {109},
     * firstPos = 100 und maxDistance = 10 fiele der Treffer sonst weg, obwohl
     * B = 110 zusammen mit C = 109 und dem Anker eine Spanne von genau 10
     * bildet. Deshalb wird über die möglichen Fensteranfänge iteriert und die
     * kleinste tragfähige Spanne gewählt; das hält zugleich die angezeigte
     * Distanz minimal.
     *
     * @param {number} firstPos - Ankerposition (erstes Lemma)
     * @param {number[][]} otherPositionLists - aufsteigend sortierte Positionen
     *   der weiteren Lemmata, in Eingabereihenfolge
     * @param {number} maxDistance - erlaubte Spanne in Wörtern
     * @returns {number[]|null} gewählte Positionen in Listenreihenfolge, oder
     *   null, wenn kein Fenster alle Lemmata trägt
     */
    findCoveringWindow(firstPos, otherPositionLists, maxDistance) {
        if (otherPositionLists.length === 0) return [];

        // Ein optimales Fenster beginnt immer auf einer belegten Position:
        // entweder auf dem Anker selbst oder auf einer Position links davon,
        // die noch in Reichweite liegt.
        const candidates = new Set([firstPos]);
        for (const list of otherPositionLists) {
            for (let i = this.lowerBound(list, firstPos - maxDistance);
                 i < list.length && list[i] <= firstPos; i++) {
                candidates.add(list[i]);
            }
        }

        let best = null;
        let bestSpan = Infinity;

        for (const windowStart of [...candidates].sort((a, b) => a - b)) {
            const windowEnd = windowStart + maxDistance;
            if (firstPos > windowEnd) continue;

            const chosen = [];
            let covered = true;
            for (const list of otherPositionLists) {
                const i = this.lowerBound(list, windowStart);
                if (i >= list.length || list[i] > windowEnd) {
                    covered = false;
                    break;
                }
                chosen.push(list[i]);
            }
            if (!covered) continue;

            const span = Math.max(firstPos, ...chosen) - Math.min(firstPos, ...chosen);
            if (span < bestSpan) {
                bestSpan = span;
                best = chosen;
            }
        }

        return best;
    }

    /**
     * Proximity search using enhanced index (instant!)
     * Finds lemmas within maxDistance words of each other
     */
    async searchProximityUsingEnhancedIndex(lemmaIds, maxDistance, corpusData) {
        const results = [];
        const includedTexts = corpusData.includedTexts || new Set();

        // Der Wortabstand kommt aus einem Eingabefeld mit max="50", die
        // Hash-Route prüft ihn aber nur auf > 0 (router.js, Parameter dist).
        // Die alte Ankerprüfung war unabhängig von maxDistance teuer, die
        // Fenstersuche nicht: ihre Kandidatenmenge wächst mit der Distanz.
        // Ein hand-getipptes dist=9999 auf einem häufigen Lemma träfe damit
        // die Kandidatensuche, deshalb hier auf den deklarierten UI-Bereich
        // klemmen statt sich auf die Oberfläche zu verlassen.
        const parsed = Number(maxDistance);
        maxDistance = Number.isFinite(parsed) ? Math.max(0, Math.min(50, parsed)) : 10;

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

            // Positionslisten der weiteren Lemmata, in der Reihenfolge der
            // Eingabe; aufsteigend sortiert, weil sie aus einem Index-Scan
            // über words[] stammen.
            const otherPositionLists = lemmaIds.slice(1).map(id => lemmaPositions[id]);

            firstPositions.forEach(firstPos => {
                // #169 Befund #15: alle gewählten Positionen müssen zusammen in
                // ein Fenster der Breite maxDistance passen, nicht nur einzeln
                // in Ankernähe liegen.
                const chosen = this.findCoveringWindow(firstPos, otherPositionLists, maxDistance);
                if (chosen === null) return;

                const allPositions = [firstPos, ...chosen];
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
            });
        });

        console.log(`✅ Proximity search complete: ${results.length} raw matches within ${maxDistance} words`);

        // v4.0.0: Deduplicate overlapping matches
        // Keep only the closest match when context windows overlap
        //
        // #169 Befund #48: bis 2026-07 sortierte diese Stelle nach contextStart
        // und behielt damit den zuerst STARTENDEN Treffer, während Kommentar
        // und Log-Zeile „keeping shorter distance" das Gegenteil behaupteten.
        // Bei Überlappung bekam der Nutzer also gegebenenfalls die weiter
        // entfernte Kookkurrenz angezeigt. Jetzt entscheidet tatsächlich die
        // Distanz: pro Datei aufsteigend nach Distanz greedy auswählen, bei
        // Gleichstand der frühere Treffer. Ausgegeben wird wieder in
        // Lesereihenfolge, damit die Anzeige dem Textverlauf folgt.
        const deduplicated = [];

        // Group by filename first
        const byFile = {};
        results.forEach(result => {
            if (!byFile[result.filename]) byFile[result.filename] = [];
            byFile[result.filename].push(result);
        });

        // For each file, remove overlapping matches (keep closest)
        Object.entries(byFile).forEach(([filename, fileResults]) => {
            const byDistance = [...fileResults].sort((a, b) =>
                (a.distance - b.distance) || (a.contextStart - b.contextStart)
            );

            const kept = [];
            byDistance.forEach(result => {
                const overlapping = kept.find(existing =>
                    Math.max(existing.contextStart, result.contextStart) <
                    Math.min(existing.contextEnd, result.contextEnd)
                );

                if (overlapping) {
                    console.log(`  🔄 Overlap detected: ${filename} [${result.contextStart}-${result.contextEnd}] overlaps with [${overlapping.contextStart}-${overlapping.contextEnd}], keeping shorter distance (${overlapping.distance} vs ${result.distance})`);
                    return;
                }

                kept.push(result);
            });

            kept.sort((a, b) => a.contextStart - b.contextStart);
            deduplicated.push(...kept);
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