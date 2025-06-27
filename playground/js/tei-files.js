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
            console.log(`✅ TEI File processed: ${file.name}`);
            
        } catch (error) {
            console.error(`❌ Error processing ${file.name}:`, error);
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

        console.log(`📜 TEI Analysis complete: ${words.length} words, ${lines.length} lines, ${annotatedElements.length} annotations`);
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
}