/**
 * MHDBDB Playground - TEI Explorer
 * Handles TEI text analysis and word-level exploration
 */

import { displayResults, showOverlaySpinner, hideSpinner, displaySummaryResults } from './UICore.js';

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

    // ==================== MULTI-LEMMA SEARCH ====================

    findMultipleLemmasInText() {
        const searchInput = prompt('Geben Sie mehrere Lemmata ein (getrennt durch " + "):\nBeispiel: brôt + wîn');
        if (!searchInput) return;

        // Parse input - support both lemma IDs and Middle High German terms
        const searchTerms = searchInput.split('+').map(term => term.trim());
        const lemmaIds = this.resolveLemmaIds(searchTerms);
        
        if (lemmaIds.length === 0) {
            displayResults('❌ Fehler', [{ 
                meta: 'Keine gültigen Lemmata gefunden', 
                snippet: `Eingabe: "${searchInput}"` 
            }]);
            return;
        }

        // Show context selection dialog
        const contextType = this.showContextSelectionDialog();
        if (!contextType) return;

        if (contextType === 'proximity') {
            this.executeProximitySearch(lemmaIds, searchTerms);
        } else {
            this.executeMultiLemmaSearch(lemmaIds, searchTerms, contextType);
        }
    }

    executeMultiLemmaSearch(lemmaIds, searchTerms, contextType) {
        // Show loading spinner
        showOverlaySpinner('resultsContainer', 'Durchsuche TEI-Texte...', true);

        // Get TEI manager from global reference
        const teiManager = window.playground?.teiManager;
        if (!teiManager) {
            hideSpinner('resultsContainer');
            displayResults('❌ Fehler', [{ 
                meta: 'TEI Manager nicht verfügbar', 
                snippet: 'Bitte laden Sie TEI-Dateien' 
            }]);
            return;
        }

        // Use setTimeout to allow UI to update with spinner before heavy processing
        setTimeout(() => {
            try {
                const results = teiManager.searchMultipleLemmas(lemmaIds, contextType);
                hideSpinner('resultsContainer');
                this.displayMultiLemmaResults(results, searchTerms, contextType);
            } catch (error) {
                hideSpinner('resultsContainer');
                displayResults('❌ Fehler', [{ 
                    meta: 'Suchfehler', 
                    snippet: error.message 
                }]);
            }
        }, 100);
    }

    executeProximitySearch(lemmaIds, searchTerms) {
        const maxDistance = parseInt(prompt('Maximaler Wortabstand (empfohlen: 5-15):', '10')) || 10;
        
        // Show loading spinner
        showOverlaySpinner('resultsContainer', 'Analysiere Nähe-Beziehungen...', true);
        
        // Get TEI manager from global reference
        const teiManager = window.playground?.teiManager;
        if (!teiManager) {
            hideSpinner('resultsContainer');
            displayResults('❌ Fehler', [{ 
                meta: 'TEI Manager nicht verfügbar', 
                snippet: 'Bitte laden Sie TEI-Dateien' 
            }]);
            return;
        }

        // Use setTimeout to allow UI to update with spinner before heavy processing
        setTimeout(() => {
            try {
                const results = teiManager.findCooccurringLemmas(lemmaIds, maxDistance);
                hideSpinner('resultsContainer');
                this.displayCooccurrenceResults(results, searchTerms, maxDistance);
            } catch (error) {
                hideSpinner('resultsContainer');
                displayResults('❌ Fehler', [{ 
                    meta: 'Nähe-Analyse Fehler', 
                    snippet: error.message 
                }]);
            }
        }, 100);
    }

    resolveLemmaIds(searchTerms) {
        const lemmaIds = [];
        
        searchTerms.forEach(term => {
            // Check if it's already a lemma ID (numeric)
            if (/^\d+$/.test(term)) {
                lemmaIds.push(term);
                return;
            }
            
            // Try to find lemma by Middle High German orthography
            const lemmaId = this.findLemmaIdByOrthography(term);
            if (lemmaId) {
                lemmaIds.push(lemmaId);
            } else {
                // Try authority data if available
                const authorityManager = window.playground?.authorityManager;
                if (authorityManager) {
                    const matches = authorityManager.searchLemmaByOrthography(term);
                    if (matches.length > 0) {
                        const lemmaId = matches[0].id.replace('lemma_', '');
                        lemmaIds.push(lemmaId);
                    }
                }
            }
        });
        
        return lemmaIds;
    }

    findLemmaIdByOrthography(orthography) {
        // Common Middle High German lemma mappings
        const commonLemmas = {
            'brôt': '879',
            'brot': '879', 
            'wîn': '7532',
            'win': '7532',
            'wein': '7532',
            'fleisch': '1816',
            'vleisch': '1816',
            'käse': '26713',
            'kæse': '26713',
            'bier': '712',
            'bîr': '712'
        };
        
        const normalized = orthography.toLowerCase();
        return commonLemmas[normalized] || null;
    }

    showContextSelectionDialog() {
        const contextOptions = [
            { value: 'paragraph', label: 'In Absätzen (empfohlen)' },
            { value: 'document', label: 'In ganzen Dokumenten' },
            { value: 'proximity', label: 'Nähebasiert (max. 10 Wörter)' }
        ];
        
        let dialogHtml = 'Wählen Sie den Suchkontext:\n\n';
        contextOptions.forEach((option, index) => {
            dialogHtml += `${index + 1}. ${option.label}\n`;
        });
        
        const choice = prompt(dialogHtml + '\nGeben Sie die Nummer ein (1-3):');
        const choiceIndex = parseInt(choice) - 1;
        
        if (choiceIndex >= 0 && choiceIndex < contextOptions.length) {
            return contextOptions[choiceIndex].value;
        }
        
        return null;
    }

    displayMultiLemmaResults(results, searchTerms, contextType) {
        if (results.length === 0) {
            displayResults(
                `🔍 Multi-Lemma-Suche: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{ 
                    meta: `Keine Treffer in ${contextType}`, 
                    snippet: 'Versuchen Sie andere Suchbegriffe oder einen anderen Kontext' 
                }]
            );
            return;
        }

        // Create summary data for the new display format
        const summaryData = this.createMultiLemmaSummary(results, searchTerms, contextType);

        displaySummaryResults(
            `🔍 Multi-Lemma-Suche: ${searchTerms.join(' + ')}`,
            summaryData
        );
    }

    createMultiLemmaSummary(results, searchTerms, contextType) {
        // Group results by filename for better organization
        const fileGroups = {};
        
        results.forEach(result => {
            if (!fileGroups[result.filename]) {
                fileGroups[result.filename] = [];
            }
            fileGroups[result.filename].push(result);
        });

        return Object.entries(fileGroups).map(([filename, fileResults]) => {
            const count = this.getResultCount(fileResults, contextType);
            const preview = this.createPreviewText(fileResults, contextType);
            const details = this.createDetailItems(fileResults, contextType);

            return {
                title: `📄 ${filename}`,
                count: count,
                preview: preview,
                details: details
            };
        });
    }

    getResultCount(fileResults, contextType) {
        if (contextType === 'paragraph') {
            return fileResults.length; // Each result is a paragraph
        } else if (contextType === 'document') {
            return fileResults.reduce((sum, result) => sum + (result.totalWords || 1), 0);
        } else if (contextType === 'proximity') {
            return fileResults.reduce((sum, result) => 
                sum + (result.cooccurrences ? result.cooccurrences.length : 0), 0);
        }
        return fileResults.length;
    }

    createPreviewText(fileResults, contextType) {
        const count = this.getResultCount(fileResults, contextType);
        
        if (contextType === 'paragraph') {
            return `Kombinationen in ${count} Absätzen gefunden`;
        } else if (contextType === 'document') {
            return `Alle Lemmas im Dokument vorhanden (${count} Wörter)`;
        } else if (contextType === 'proximity') {
            return `${count} Nähe-Beziehungen gefunden`;
        }
        return `${count} Treffer`;
    }

    createDetailItems(fileResults, contextType) {
        return fileResults.map((result, index) => {
            if (contextType === 'paragraph') {
                const matchingSummary = this.formatMatchingWords(result.matchingWords);
                return {
                    meta: `Absatz ${result.paragraphId} • ${matchingSummary}`,
                    snippet: this.highlightLemmasInText(result.text, result.matchingWords)
                };
            } else if (contextType === 'document') {
                const matchingSummary = this.formatMatchingWords(result.matchingWords);
                return {
                    meta: `Volltext • ${matchingSummary}`,
                    snippet: `Alle Suchbegriffe im Dokument vorhanden (${result.totalWords} Wörter)`
                };
            } else if (contextType === 'proximity') {
                const cooccurrences = result.cooccurrences || [];
                return cooccurrences.slice(0, 10).map(c => ({
                    meta: `Abstand: ${c.distance} Wörter • ${c.lemma1.text} ↔ ${c.lemma2.text}`,
                    snippet: `"${c.context}"`
                }));
            }
        }).flat().slice(0, 50); // Limit to 50 detail items for performance
    }

    formatMatchingWords(matchingWords) {
        const summaries = [];
        for (const [lemmaId, words] of Object.entries(matchingWords)) {
            const uniqueTexts = [...new Set(words.map(w => w.text))];
            summaries.push(`${uniqueTexts.join(', ')} (${words.length}x)`);
        }
        return summaries.join(' • ');
    }

    highlightLemmasInText(text, matchingWords) {
        let highlightedText = text;
        
        for (const [lemmaId, words] of Object.entries(matchingWords)) {
            words.forEach(word => {
                const regex = new RegExp(`\\b${word.text}\\b`, 'gi');
                highlightedText = highlightedText.replace(regex, 
                    `<span class="highlight multi-lemma-${lemmaId}">${word.text}</span>`
                );
            });
        }
        
        return highlightedText;
    }

    findCooccurringLemmas() {
        const searchInput = prompt('Geben Sie Lemmata für Nähe-Analyse ein (getrennt durch " + "):\nBeispiel: brôt + wîn');
        if (!searchInput) return;

        const searchTerms = searchInput.split('+').map(term => term.trim());
        const lemmaIds = this.resolveLemmaIds(searchTerms);
        
        if (lemmaIds.length < 2) {
            displayResults('❌ Fehler', [{ 
                meta: 'Mindestens 2 gültige Lemmata benötigt', 
                snippet: `Eingabe: "${searchInput}"` 
            }]);
            return;
        }

        const maxDistance = parseInt(prompt('Maximaler Wortabstand (empfohlen: 5-15):', '10')) || 10;

        // Show loading spinner
        showOverlaySpinner('resultsContainer', 'Analysiere Nähe-Beziehungen...', true);

        // Get TEI manager from global reference
        const teiManager = window.playground?.teiManager;
        if (!teiManager) {
            hideSpinner('resultsContainer');
            displayResults('❌ Fehler', [{ 
                meta: 'TEI Manager nicht verfügbar', 
                snippet: 'Bitte laden Sie TEI-Dateien' 
            }]);
            return;
        }

        // Use setTimeout to allow UI to update with spinner before heavy processing
        setTimeout(() => {
            try {
                const results = teiManager.findCooccurringLemmas(lemmaIds, maxDistance);
                hideSpinner('resultsContainer');
                this.displayCooccurrenceResults(results, searchTerms, maxDistance);
            } catch (error) {
                hideSpinner('resultsContainer');
                displayResults('❌ Fehler', [{ 
                    meta: 'Nähe-Analyse Fehler', 
                    snippet: error.message 
                }]);
            }
        }, 100);
    }

    displayCooccurrenceResults(results, searchTerms, maxDistance) {
        if (results.length === 0) {
            displayResults(
                `🔗 Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{ 
                    meta: `Keine Treffer im Abstand von ${maxDistance} Wörtern`, 
                    snippet: 'Versuchen Sie einen größeren Abstand oder andere Begriffe' 
                }]
            );
            return;
        }

        // Create summary data for cooccurrence results
        const summaryData = results.map(result => {
            const cooccurrences = result.cooccurrences || [];
            const count = cooccurrences.length;
            
            const preview = `${count} Nähe-Beziehungen im Abstand von max. ${maxDistance} Wörtern`;
            
            const details = cooccurrences.slice(0, 20).map(cooc => ({
                meta: `Abstand: ${cooc.distance} Wörter • ${cooc.lemma1.text} ↔ ${cooc.lemma2.text}`,
                snippet: `"${cooc.context}"`
            }));

            return {
                title: `📄 ${result.filename}`,
                count: count,
                preview: preview,
                details: details
            };
        }).filter(summary => summary.count > 0); // Only show files with results

        displaySummaryResults(
            `🔗 Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (max. ${maxDistance} Wörter Abstand)`,
            summaryData
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