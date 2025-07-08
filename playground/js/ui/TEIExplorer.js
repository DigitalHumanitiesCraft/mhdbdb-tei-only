/**
 * MHDBDB Playground - TEI Explorer
 * Handles TEI text analysis and word-level exploration
 */

import { displayResults } from './UICore.js';

export class TEIExplorer {
    constructor(teiData, authorityData) {
        this.teiData = teiData;
        this.authorityData = authorityData;
    }

    // ==================== WORDS EXPLORER ====================

    showWords() {
        const displayCount = Math.min(200, this.teiData.words.length);
        const results = this.teiData.words.slice(0, displayCount).map(w => ({
            meta: this.formatWordMeta(w),
            snippet: w.text
        }));

        displayResults(
            `📝 Wörter aus TEI Texten (erste ${displayCount} von ${this.teiData.words.length})`,
            results
        );
    }

    // ==================== LINES EXPLORER ====================

    showLines() {
        const results = this.teiData.lines.map(l => ({
            meta: `${l.filename} • Zeile ${l.n}`,
            snippet: l.text
        }));

        displayResults(
            `📏 Textzeilen aus TEI Texten (${this.teiData.lines.length} Zeilen)`,
            results
        );
    }

    // ==================== LEMMA SEARCH IN TEXT ====================

    findLemmaInText() {
        const searchTerm = prompt('Welches Lemma soll im Text gesucht werden?');
        if (!searchTerm) return;

        const matches = this.teiData.words.filter(w =>
            (w.lemmaRef && w.lemmaRef.includes(searchTerm)) ||
            w.text.toLowerCase().includes(searchTerm.toLowerCase())
        );

        const results = matches.map(m => ({
            meta: `${m.filename} • ${m.lemmaRef ? `Lemma: ${m.lemmaRef.split('#').pop()}` : 'Textsuche'}`,
            snippet: `<span class="highlight">${m.text}</span>`
        }));

        displayResults(
            `🔍 Lemma-Suche: "${searchTerm}" (${matches.length} Treffer)`,
            results
        );
    }

    // ==================== ANNOTATIONS EXPLORER ====================

    showAnnotations() {
        const results = this.teiData.annotations.map(a => ({
            meta: this.formatAnnotationMeta(a),
            snippet: a.text
        }));

        displayResults(
            `🏷️ Alle Annotationen aus TEI Texten (${this.teiData.annotations.length} Annotationen)`,
            results
        );
    }

    // ==================== ADVANCED TEI ANALYSIS ====================

    showWordFrequency() {
        const frequency = this.calculateWordFrequency();
        const results = frequency.slice(0, 50).map(([word, count]) => ({
            meta: `${count} Vorkommen`,
            snippet: word
        }));

        displayResults('📊 Häufigste Wörter (Top 50)', results);
    }

    showLemmaFrequency() {
        const frequency = this.calculateLemmaFrequency();
        const results = frequency.slice(0, 30).map(([lemmaId, count]) => {
            const lemma = this.authorityData.lemmata.find(l => l.id === lemmaId);
            const lemmaText = lemma ? lemma.lemma : lemmaId;
            
            return {
                meta: `${count} Vorkommen • ID: ${lemmaId}`,
                snippet: lemmaText
            };
        });

        displayResults('📊 Häufigste Lemmata (Top 30)', results);
    }

    showPOSDistribution() {
        const distribution = this.calculatePOSDistribution();
        const results = Object.entries(distribution)
            .sort(([,a], [,b]) => b - a)
            .map(([pos, count]) => ({
                meta: `${count} Vorkommen`,
                snippet: pos
            }));

        displayResults('📊 Wortarten-Verteilung', results);
    }

    // ==================== CONTEXT ANALYSIS ====================

    showWordInContext(wordIndex, filename, contextSize = 3) {
        const context = this.getWordContext(wordIndex, filename, contextSize);
        if (!context) return;

        const results = context.map((word, index) => {
            const isTarget = word.index === wordIndex;
            return {
                meta: `${word.filename} • Position ${word.index}`,
                snippet: isTarget ? `<span class="highlight">${word.text}</span>` : word.text
            };
        });

        displayResults(`🔍 Kontext für Wort (±${contextSize})`, results);
    }

    showLineInContext(lineNumber, filename, contextSize = 2) {
        const context = this.getLineContext(lineNumber, filename, contextSize);
        if (!context) return;

        const results = context.map(line => {
            const isTarget = line.n === lineNumber;
            return {
                meta: `${line.filename} • Zeile ${line.n}`,
                snippet: isTarget ? `<span class="highlight">${line.text}</span>` : line.text
            };
        });

        displayResults(`🔍 Kontext für Zeile ${lineNumber} (±${contextSize})`, results);
    }

    // ==================== CROSS-REFERENCE ANALYSIS ====================

    resolveWordReferences() {
        const resolvedWords = this.teiData.words.map(word => {
            if (!word.lemmaRef) return word;

            const lemmaId = word.lemmaRef.split('#')[1];
            const lemma = this.authorityData.lemmata.find(l => l.id === lemmaId);
            
            return {
                ...word,
                resolvedLemma: lemma
            };
        });

        const resultsWithLemma = resolvedWords
            .filter(w => w.resolvedLemma)
            .slice(0, 100);

        const results = resultsWithLemma.map(w => ({
            meta: `${w.filename} • Lemma: ${w.resolvedLemma.lemma} • POS: ${w.resolvedLemma.pos || 'unbekannt'}`,
            snippet: w.text
        }));

        displayResults(
            `🔗 Wörter mit aufgelösten Lemma-Referenzen (erste 100 von ${resultsWithLemma.length})`,
            results
        );
    }

    resolveAnnotationReferences() {
        const resolvedAnnotations = this.teiData.annotations.map(annotation => {
            const resolvedConcepts = [];
            
            if (annotation.conceptRef) {
                const conceptId = annotation.conceptRef.split('#')[1];
                const concept = this.authorityData.concepts.find(c => c.id === conceptId);
                if (concept) resolvedConcepts.push(concept);
            }
            
            return {
                ...annotation,
                resolvedConcepts
            };
        });

        const resultsWithConcepts = resolvedAnnotations
            .filter(a => a.resolvedConcepts.length > 0)
            .slice(0, 50);

        const results = resultsWithConcepts.map(a => ({
            meta: `${a.filename} • ${a.tagName} • Konzepte: ${a.resolvedConcepts.map(c => c.termDE || c.termEN).join(', ')}`,
            snippet: a.text
        }));

        displayResults(
            `🔗 Annotationen mit aufgelösten Konzept-Referenzen (erste 50 von ${resultsWithConcepts.length})`,
            results
        );
    }

    // ==================== STATISTICAL CALCULATIONS ====================

    calculateWordFrequency() {
        const frequency = {};
        this.teiData.words.forEach(word => {
            const text = word.text.toLowerCase();
            frequency[text] = (frequency[text] || 0) + 1;
        });
        
        return Object.entries(frequency)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 100);
    }

    calculateLemmaFrequency() {
        const frequency = {};
        this.teiData.words.forEach(word => {
            if (word.lemmaRef) {
                const lemmaId = word.lemmaRef.split('#')[1];
                frequency[lemmaId] = (frequency[lemmaId] || 0) + 1;
            }
        });
        
        return Object.entries(frequency)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 50);
    }

    calculatePOSDistribution() {
        const distribution = {};
        this.teiData.words.forEach(word => {
            if (word.pos) {
                distribution[word.pos] = (distribution[word.pos] || 0) + 1;
            }
        });
        
        return distribution;
    }

    // ==================== CONTEXT HELPERS ====================

    getWordContext(wordIndex, filename, contextSize = 3) {
        const wordsInFile = this.teiData.words.filter(w => w.filename === filename);
        const targetWordIndex = wordsInFile.findIndex(w => w.index === wordIndex);
        
        if (targetWordIndex === -1) return null;

        const start = Math.max(0, targetWordIndex - contextSize);
        const end = Math.min(wordsInFile.length, targetWordIndex + contextSize + 1);
        
        return wordsInFile.slice(start, end);
    }

    getLineContext(lineNumber, filename, contextSize = 2) {
        const linesInFile = this.teiData.lines.filter(l => l.filename === filename);
        const targetLine = linesInFile.find(l => l.n === lineNumber);
        
        if (!targetLine) return null;

        const targetIndex = linesInFile.indexOf(targetLine);
        const start = Math.max(0, targetIndex - contextSize);
        const end = Math.min(linesInFile.length, targetIndex + contextSize + 1);
        
        return linesInFile.slice(start, end);
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

    // ==================== FORMATTING HELPERS ====================

    formatWordMeta(word) {
        const parts = [word.filename];
        if (word.pos) parts.push(`POS: ${word.pos}`);
        if (word.lemmaRef) parts.push(`Lemma: ${word.lemmaRef.split('#').pop()}`);
        return parts.join(' • ');
    }

    formatAnnotationMeta(annotation) {
        const parts = [annotation.filename, annotation.tagName];
        if (annotation.meaningRef) parts.push(`Meaning: ${annotation.meaningRef.split('#').pop()}`);
        return parts.join(' • ');
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
}