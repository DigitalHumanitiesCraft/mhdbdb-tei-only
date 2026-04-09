/**
 * MHDBDB Playground - TEI Explorer
 * Handles TEI text analysis and word-level exploration with MHG normalization
 */

import { displayResults, displaySummaryResults } from '../core/ui-helpers.js';
import { showOverlaySpinner, hideSpinner } from '../core/progress.js';
import { TextNormalizer } from '../../../../assets/js/lib/text-normalizer.js';

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
            `Wörter aus TEI Texten (erste ${displayCount} von ${this.teiData.words.length})`,
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
            `Textzeilen aus TEI Texten (${this.teiData.lines.length} Zeilen)`,
            results
        );
    }

    // ==================== LEMMA SEARCH IN TEXT ====================

    findLemmaInText() {
        const searchTerm = prompt('Welches Lemma soll im Text gesucht werden?');
        if (!searchTerm) return;

        // Search with MHG normalization support
        const matches = this.teiData.words.filter(w =>
            (w.lemmaRef && w.lemmaRef.includes(searchTerm)) ||
            TextNormalizer.matchesNormalized(w.text, searchTerm)
        );

        const results = matches.map(m => ({
            meta: `${m.filename} • ${m.lemmaRef ? `Lemma: ${m.lemmaRef.split('#').pop()}` : 'Textsuche'}`,
            snippet: `<span class="highlight">${m.text}</span>`
        }));

        displayResults(
            `Lemma-Suche: "${searchTerm}" (${matches.length} Treffer)`,
            results
        );
    }

    // ==================== MULTI-LEMMA SEARCH ====================
    // Note: The UI modal is now handled by MultiLemmaSearchUI class
    // This method is kept for backward compatibility but delegates to the modal

    executeMultiLemmaSearch(lemmaIds, searchTerms, contextType) {
        // Show loading spinner
        showOverlaySpinner('resultsContainer', 'Durchsuche TEI-Texte...', true);

        // Get TEI manager from global reference
        const teiManager = window.playground?.teiManager;
        if (!teiManager) {
            hideSpinner('resultsContainer');
            displayResults('Fehler', [{ 
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
                displayResults('Fehler', [{ 
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
            displayResults('Fehler', [{
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
                this.displayCooccurrenceResults(results, searchTerms, maxDistance, lemmaIds);
            } catch (error) {
                hideSpinner('resultsContainer');
                displayResults('Fehler', [{
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

            // Try hardcoded common lemma mappings first (fast path)
            // Supports exact variants like: brôt/brot, wîn/win/wein, etc.
            const lemmaId = this.findLemmaIdByOrthography(term);
            if (lemmaId) {
                lemmaIds.push(lemmaId);
            } else {
                // Fallback: Search through lexicon.xml for any matching lemma
                // This uses 'includes()' so it's very flexible:
                // - Searches all lemma entries in the lexicon
                // - Finds partial matches (e.g., "brot" finds "brôt")
                // - Works with any orthographic variant present in the lexicon
                // Note: Takes first match if multiple lemmata contain the search term
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

    // Context selection is now handled by the MultiLemmaSearchUI modal

    displayMultiLemmaResults(results, searchTerms, contextType) {
        if (results.length === 0) {
            displayResults(
                `Multi-Lemma-Suche: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{ 
                    meta: `Keine Treffer in ${contextType}`, 
                    snippet: 'Versuchen Sie andere Suchbegriffe oder einen anderen Kontext' 
                }]
            );
            return;
        }

        // Create summary data for the new display format
        const summaryData = this.createMultiLemmaSummary(results, searchTerms, contextType);

        // Pass raw results and lemma IDs for lazy TEI loading
        const lemmaIds = results.length > 0 && results[0].matchingPositions
            ? [...new Set(results.flatMap(r => r.matchingPositions || []).map(p => p.lemmaRef.replace('lemma_', '')))]
            : [];

        displaySummaryResults(
            `Multi-Lemma-Suche: ${searchTerms.join(' + ')}`,
            summaryData,
            results,  // Raw results
            lemmaIds  // Lemma IDs for enrichment
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
                title: `${filename}`,
                count: count,
                preview: preview,
                details: details
            };
        });
    }

    getResultCount(fileResults, contextType) {
        // v4.0.0: Paragraph mode removed
        if (contextType === 'document') {
            return fileResults.reduce((sum, result) => sum + (result.totalWords || 1), 0);
        } else if (contextType === 'proximity') {
            return fileResults.reduce((sum, result) =>
                sum + (result.cooccurrences ? result.cooccurrences.length : 0), 0);
        }
        return fileResults.length;
    }

    createPreviewText(fileResults, contextType) {
        const count = this.getResultCount(fileResults, contextType);

        // v4.0.0: Paragraph mode removed
        if (contextType === 'document') {
            // Document search: show just word count as metadata
            return `${count} Wörter`;
        } else if (contextType === 'proximity') {
            return `${count} Nähe-Beziehungen gefunden`;
        }
        return `${count} Treffer`;
    }

    createDetailItems(fileResults, contextType) {
        // v4.0.0: Paragraph mode removed - only document and proximity modes remain
        if (contextType === 'document') {
            return []; // Document search: no detail items - just show file list
        }

        return fileResults.map((result, index) => {
            if (contextType === 'proximity') {
                // v3.0.0: proximity results are flat, not nested in cooccurrences
                if (result.contextText) {
                    // Has actual text (enriched)
                    return {
                        meta: `Abstand: ${result.distance} Wörter`,
                        snippet: `"${result.contextText}"`
                    };
                } else {
                    // Fallback: show lemma IDs
                    const preview = result.contextLemmas ? result.contextLemmas.slice(0, 20).join(' ') : '';
                    return {
                        meta: `Abstand: ${result.distance} Wörter`,
                        snippet: `<code style="font-size: 0.85em;">${preview}...</code>`
                    };
                }
            }
        }).flat().slice(0, 50); // Limit to 50 detail items for performance
    }

    // v3.0.0 compact format helpers
    formatMatchingPositions(matchingPositions) {
        if (!matchingPositions || matchingPositions.length === 0) {
            return 'Keine Positionen';
        }
        const lemmaRefs = matchingPositions.map(p => p.lemmaRef).filter(Boolean);
        const uniqueLemmas = [...new Set(lemmaRefs)];
        return `${uniqueLemmas.length} Lemmata (${matchingPositions.length} Vorkommen)`;
    }

    formatParagraphLemmas(paragraphLemmas) {
        if (!paragraphLemmas || paragraphLemmas.length === 0) {
            return 'Kein Text verfügbar';
        }
        // Show first 100 lemma IDs as placeholder
        const preview = paragraphLemmas.slice(0, 100).join(' ');
        const more = paragraphLemmas.length > 100 ? ` ... (+${paragraphLemmas.length - 100} weitere)` : '';
        return `<code style="font-size: 0.85em; color: #475569;">${preview}${more}</code>`;
    }

    formatMatchingWordsOrCounts(matchingWords) {
        // Handle both formats: array of words (paragraph) or counts (document)
        const summaries = [];
        for (const [lemmaId, data] of Object.entries(matchingWords)) {
            if (typeof data === 'number') {
                // Document search: data is a count
                summaries.push(`lemma_${lemmaId} (${data}x)`);
            } else if (Array.isArray(data)) {
                // Paragraph search: data is array of word objects
                const uniqueTexts = [...new Set(data.map(w => w.text))];
                summaries.push(`${uniqueTexts.join(', ')} (${data.length}x)`);
            }
        }
        return summaries.join(' • ');
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
                // Escape special regex characters in word.text
                const escapedWord = word.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                // Use negative lookahead to avoid double-wrapping already highlighted text
                const regex = new RegExp(`(?<!<[^>]*)\\b${escapedWord}\\b(?![^<]*<\\/span>)`, 'gi');
                highlightedText = highlightedText.replace(regex,
                    `<span class="highlight multi-lemma-${lemmaId}">${word.text}</span>`
                );
            });
        }

        return highlightedText;
    }

    highlightCooccurrenceContext(context, lemma1, lemma2) {
        let highlightedContext = context;

        // Highlight lemma1
        const escapedText1 = lemma1.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex1 = new RegExp(`\\b${escapedText1}\\b`, 'gi');
        highlightedContext = highlightedContext.replace(regex1,
            `<span class="highlight multi-lemma-${lemma1.id}">${lemma1.text}</span>`
        );

        // Highlight lemma2 (avoid double-wrapping)
        const escapedText2 = lemma2.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex2 = new RegExp(`(?<!<[^>]*)\\b${escapedText2}\\b(?![^<]*<\\/span>)`, 'gi');
        highlightedContext = highlightedContext.replace(regex2,
            `<span class="highlight multi-lemma-${lemma2.id}">${lemma2.text}</span>`
        );

        return highlightedContext;
    }

    // findCooccurringLemmas() method removed - now handled by MultiLemmaSearchUI modal
    // Co-occurrence analysis is available as "Nähe-Analyse" mode in the multi-lemma search

    displayCooccurrenceResults(results, searchTerms, maxDistance, searchedLemmaIds) {
        if (results.length === 0) {
            displayResults(
                `Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{
                    meta: `Keine Treffer im Abstand von ${maxDistance} Wörtern`,
                    snippet: 'Versuchen Sie einen größeren Abstand oder andere Begriffe'
                }]
            );
            return;
        }

        // v3.0.0: results is a flat array, group by filename
        const fileGroups = {};
        results.forEach(result => {
            if (!fileGroups[result.filename]) {
                fileGroups[result.filename] = [];
            }
            fileGroups[result.filename].push(result);
        });

        // Create summary data for cooccurrence results
        const summaryData = Object.entries(fileGroups).map(([filename, fileResults]) => {
            const count = fileResults.length;
            const preview = `${count} Nähe-Beziehungen im Abstand von max. ${maxDistance} Wörtern`;

            // v3.0.0: Show placeholder until user expands
            const details = fileResults.slice(0, 50).map(match => {
                if (match.contextText) {
                    // Has enriched text (after expand)
                    return {
                        meta: `Abstand: ${match.distance} Wörter`,
                        snippet: `"${match.contextText}"`
                    };
                } else {
                    // No text yet - show lemma IDs preview
                    const preview = match.contextLemmas ? match.contextLemmas.slice(0, 20).join(' ') : '';
                    return {
                        meta: `Abstand: ${match.distance} Wörter`,
                        snippet: `<em style="color: #475569;">Klicken Sie auf "KLICKEN ZUM ERWEITERN" um den vollständigen Text anzuzeigen</em>`
                    };
                }
            });

            return {
                title: filename,
                count: count,
                preview: preview,
                details: details
            };
        }).filter(summary => summary.count > 0);

        // Use the searched lemma IDs (e.g., [879, 7532]) not all positions from results
        displaySummaryResults(
            `Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (max. ${maxDistance} Wörter Abstand)`,
            summaryData,
            results,  // Raw results
            searchedLemmaIds  // ONLY the searched lemmas for highlighting
        );
    }

    // ==================== ANNOTATIONS EXPLORER ====================

    showAnnotations() {
        const results = this.teiData.annotations.map(a => ({
            meta: this.formatAnnotationMeta(a),
            snippet: a.text
        }));

        displayResults(
            `Alle Annotationen aus TEI Texten (${this.teiData.annotations.length} Annotationen)`,
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

        displayResults('Häufigste Wörter (Top 50)', results);
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

        displayResults('Häufigste Lemmata (Top 30)', results);
    }

    showPOSDistribution() {
        const distribution = this.calculatePOSDistribution();
        const results = Object.entries(distribution)
            .sort(([,a], [,b]) => b - a)
            .map(([pos, count]) => ({
                meta: `${count} Vorkommen`,
                snippet: pos
            }));

        displayResults('Wortarten-Verteilung', results);
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

        displayResults(`Kontext für Wort (±${contextSize})`, results);
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

        displayResults(`Kontext für Zeile ${lineNumber} (±${contextSize})`, results);
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
            `Wörter mit aufgelösten Lemma-Referenzen (erste 100 von ${resultsWithLemma.length})`,
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
            meta: `${a.filename} • ${a.tagName} • Begriffe: ${a.resolvedConcepts.map(c => c.termDE || c.termEN).join(', ')}`,
            snippet: a.text
        }));

        displayResults(
            `Annotationen mit aufgelösten Begriffsreferenzen (erste 50 von ${resultsWithConcepts.length})`,
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
        const headers = ['filename', 'text', 'tagName', 'ana', 'conceptRef'];
        const rows = this.teiData.annotations.map(annotation => [
            annotation.filename,
            annotation.text,
            annotation.tagName,
            annotation.ana || '',
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
        if (annotation.ana) parts.push(`Meaning: ${annotation.ana.split('#').pop()}`);
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