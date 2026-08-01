/**
 * MHDBDB Playground - TEI Explorer
 * Handles TEI text analysis and word-level exploration with MHG normalization
 */

import { displayResults, displaySummaryResults } from '../core/ui-helpers.js';

export class TEIExplorer {
    constructor(teiData, authorityData) {
        this.teiData = teiData;
        this.authorityData = authorityData;
    }

    resolveLemmaIds(searchTerms) {
        const lemmaIds = [];

        searchTerms.forEach(term => {
            // Check if it's already a lemma ID (numeric)
            if (/^\d+$/.test(term)) {
                lemmaIds.push(term);
                return;
            }

            // 3-Stufen-Auflösung über den Authority-Manager (exakt ->
            // Varianten -> Präfix-Match in beide Richtungen). Stufe 3 war bis
            // #224 ein Substring-Test; sie matcht jetzt präfixorientiert und
            // liefert bereits sortiert: erst Nähe zur Eingabe, dann
            // Korpus-Frequenz. matches[0] ist damit das plausibelste Lemma und
            // nicht mehr der erste Index-Treffer (#163/#164).
            // Regel: assets/js/lib/lemma-resolve.js.
            //
            // Davor stand hier bis 2026-07 ein hartkodiertes 11-Eintrag-
            // Wörterbuch als „fast path" (brôt -> 879, wîn -> 7532, …), das die
            // zentrale Auflösung umging (#169 Befund #51). Es war zum Zeitpunkt
            // der Entfernung bereits in fünf von elf Einträgen falsch, weil die
            // Lemma-IDs seit dem Eintragen neu vergeben wurden: „fleisch" und
            // „vleisch" lieferten lemma_1816 forma statt lemma_7121 vleisch,
            // „käse" und „kæse" lemma_26713 eierkæse statt lemma_3175 kæse,
            // „bier" lemma_712 bir (die Birne) statt lemma_702 bier. Die sechs
            // korrekten Einträge verlieren nichts: Stufe 1 und 2 finden sie
            // ohnehin. Genau dieses stille Veralten war der Grund, es zu
            // streichen statt die IDs nachzuziehen.
            const authorityManager = window.playground?.authorityManager;
            if (authorityManager) {
                const matches = authorityManager.searchLemmaByOrthography(term);
                if (matches.length > 0) {
                    const lemmaId = matches[0].id.replace('lemma_', '');
                    lemmaIds.push(lemmaId);
                }
            }
        });

        // Verschiedene Eingaben können auf dasselbe Lemma zeigen: „wîn" und
        // „wein" landen beide auf lemma_7532, das eine über Stufe 1, das
        // andere über die Variantenliste. Ohne Dedup steht diese ID zweimal in
        // der Liste, und die Nähesuche sucht ein Fenster, das dieselbe
        // Positionsliste zweimal abdeckt: das leistet jede einzelne Position,
        // also meldet sie jede Fundstelle als Treffer mit Abstand 0. Vor #169
        // fiel das weniger auf, seit der Fensterlogik ist es deterministisch.
        // Reihenfolge bleibt erhalten, der erste Treffer gewinnt.
        return [...new Set(lemmaIds)];
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

    // opts.verseMode (#106 Punkt 8): Ergebnisse stammen aus der "Im selben
    // Vers"-Suche — Labels sprechen von Versen statt Wortabstand; maxDistance
    // ist dann null. Ergebnis-Shape ist identisch (siehe tei-manager.js).
    displayCooccurrenceResults(results, searchTerms, maxDistance, searchedLemmaIds, opts = {}) {
        const verseMode = !!opts.verseMode;
        if (results.length === 0) {
            displayResults(
                `Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{
                    meta: verseMode
                        ? 'Keine gemeinsamen Verse gefunden'
                        : `Keine Treffer im Abstand von ${maxDistance} Wörtern`,
                    snippet: verseMode
                        ? 'Versuchen Sie die Nähe-Analyse oder andere Begriffe (Prosa-Texte haben keine Verse)'
                        : 'Versuchen Sie einen größeren Abstand oder andere Begriffe'
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
            const preview = verseMode
                ? `${count} ${count === 1 ? 'Vers' : 'Verse'} mit allen Lemmata`
                : `${count} Nähe-Beziehungen im Abstand von max. ${maxDistance} Wörtern`;

            // v3.0.0: Show placeholder until user expands
            const details = fileResults.slice(0, 50).map(match => {
                const meta = verseMode
                    ? `Gemeinsam in Vers ${match.verseN}`
                    : `Abstand: ${match.distance} Wörter`;
                if (match.contextText) {
                    // Has enriched text (after expand)
                    return {
                        meta: meta,
                        snippet: `"${match.contextText}"`
                    };
                } else {
                    // No text yet - show lemma IDs preview
                    const preview = match.contextLemmas ? match.contextLemmas.slice(0, 20).join(' ') : '';
                    return {
                        meta: meta,
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
            verseMode
                ? `Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (im selben Vers)`
                : `Kookkurrenz-Analyse: ${searchTerms.join(' + ')} (max. ${maxDistance} Wörter Abstand)`,
            summaryData,
            results,  // Raw results
            searchedLemmaIds  // ONLY the searched lemmas for highlighting
        );
    }

}