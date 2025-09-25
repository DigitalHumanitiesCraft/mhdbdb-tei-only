/**
 * MHDBDB Playground - TEI Files Manager
 * Handles TEI file upload, parsing, and structural analysis
 */

export class TEIFilesManager {
    constructor(teiData) {
        this.teiData = teiData;
    }

    // ==================== FILE VALIDATION ====================

    isTEIFile(file) {
        return file.type === 'text/xml' || 
               file.name.endsWith('.xml') || 
               file.name.endsWith('.tei');
    }

    // ==================== FILE PROCESSING ====================

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
            console.log(`TEI File processed: ${file.name}`);
            
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

    searchMultipleLemmas(lemmaIds, contextType = 'paragraph') {
        const results = [];
        
        this.teiData.parsedXML.forEach(xmlData => {
            if (contextType === 'paragraph') {
                // Search within paragraphs
                const paragraphs = xmlData.doc.querySelectorAll('p');
                
                paragraphs.forEach((paragraph, pIndex) => {
                    const containsAllLemmas = lemmaIds.every(lemmaId => {
                        // Try multiple selector approaches for robustness
                        const selectors = [
                            `w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`,
                            `w[lemmaRef="lexicon.xml#lemma_${lemmaId}"]`,
                            `w[lemmaRef$="#lemma_${lemmaId}"]`
                        ];
                        
                        return selectors.some(selector => {
                            const elements = paragraph.querySelectorAll(selector);
                            return elements.length > 0;
                        });
                    });
                    
                    if (containsAllLemmas) {
                        const matchingWords = this.extractMatchingWordsFromParagraph(paragraph, lemmaIds);
                        results.push({
                            filename: xmlData.filename,
                            context: 'paragraph',
                            paragraphIndex: pIndex,
                            paragraphId: paragraph.getAttribute('n') || `p_${pIndex}`,
                            text: paragraph.textContent?.trim(),
                            matchingWords: matchingWords,
                            htmlContent: paragraph.outerHTML?.substring(0, 1000)
                        });
                    }
                });
            } else if (contextType === 'document') {
                // Search across entire document
                const containsAllLemmas = lemmaIds.every(lemmaId => {
                    const elements = xmlData.doc.querySelectorAll(`w[lemmaRef*="lexicon.xml#lemma_${lemmaId}"]`);
                    return elements.length > 0;
                });
                
                if (containsAllLemmas) {
                    const matchingWords = this.extractMatchingWordsFromDocument(xmlData.doc, lemmaIds);
                    results.push({
                        filename: xmlData.filename,
                        context: 'document',
                        matchingWords: matchingWords,
                        totalWords: this.teiData.words.filter(w => w.filename === xmlData.filename).length
                    });
                }
            }
        });
        
        return results;
    }

    findCooccurringLemmas(lemmaIds, maxDistance = 10) {
        const results = [];
        
        this.teiData.parsedXML.forEach(xmlData => {
            const words = xmlData.doc.querySelectorAll('w');
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
        });
        
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
}