/**
 * MHDBDB Playground - TEI Explorer
 * Handles TEI text analysis and word-level exploration with MHG normalization
 */

import { displayResults, displaySummaryResults } from '../core/ui-helpers.js';

export class TEIExplorer {
    // Kein Konstruktor: bis #325/#327 nahm er teiData und authorityData
    // entgegen und legte beide auf this.*, gelesen hat sie hier nie jemand.
    // Den Authority-Manager holt sich resolveLemmaIds unten über
    // window.playground, nicht über ein Konstruktorargument.

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

    // Zeigt ausschließlich Ergebnisse der Dokumentsuche an. Bis #327 nahm die
    // Methode einen contextType entgegen und verzweigte darauf; erreichbar war
    // davon nur 'document'. Der einzige Aufrufer ist der else-Zweig in
    // multi-lemma-search.js, der greift, nachdem 'proximity' und 'verse'
    // abgefangen sind, und alles außerhalb dieser drei Modi hat zwei Zeilen
    // vorher schon `searchMultipleLemmasUsingIndex` abgewiesen (tei-manager.js,
    // „Unbekannter Suchmodus"). Ein eigener Guard hier wäre deshalb wieder
    // Code, der nie läuft: die Prüfung sitzt eine Schicht tiefer, wo
    // contextType echte Dispatch-Variable mit drei lebenden Zweigen ist.
    //
    // Was mit den Zweigen verschwunden ist: getResultCount, createPreviewText
    // und createDetailItems hatten je einen 'proximity'-Zweig plus einen
    // Fallthrough dahinter, der im Fehlerfall eine plausibel aussehende Zahl
    // geliefert hätte statt aufzufallen. createDetailItems schrieb dabei
    // undefined-Einträge in die Detailliste, weil der map-Callback ohne return
    // durchfiel.
    displayMultiLemmaResults(results, searchTerms) {
        if (results.length === 0) {
            displayResults(
                `Multi-Lemma-Suche: ${searchTerms.join(' + ')} (0 Treffer)`,
                [{
                    meta: 'Keine Treffer im gesamten Dokument',
                    snippet: 'Versuchen Sie andere Suchbegriffe oder einen anderen Kontext'
                }]
            );
            return;
        }

        // Create summary data for the new display format
        const summaryData = this.createMultiLemmaSummary(results);

        // Die Dokumentsuche liefert keine matchingPositions (tei-manager.js
        // pusht filename/title/author/context/totalWords), hier stand bis #327
        // ein Ternär, dessen erster Zweig nie griff.
        //
        // Die leere Liste wird trotzdem übergeben, aber nicht aus Not: das
        // Argument hat in displaySummaryResults den Default null, und beide
        // Lesestellen vertragen null (die eine normalisiert mit `|| []`, die
        // andere kehrt per Guard früh zurück). Sie steht hier, damit der Aufruf
        // dieselbe Gestalt hat wie der der Nähe-Suche darunter, die echte IDs
        // übergibt.
        const lemmaIds = [];

        displaySummaryResults(
            `Multi-Lemma-Suche: ${searchTerms.join(' + ')}`,
            summaryData,
            results,  // Raw results
            lemmaIds  // Lemma IDs for enrichment
        );
    }

    createMultiLemmaSummary(results) {
        // Group results by filename for better organization
        const fileGroups = {};

        results.forEach(result => {
            if (!fileGroups[result.filename]) {
                fileGroups[result.filename] = [];
            }
            fileGroups[result.filename].push(result);
        });

        return Object.entries(fileGroups).map(([filename, fileResults]) => {
            const count = this.getResultCount(fileResults);

            return {
                title: `${filename}`,
                count: count,
                preview: this.createPreviewText(count),
                // Die Dokumentsuche hat keine Detailzeilen. createSummaryCard in
                // ui-helpers.js rendert bei leerer Liste die statische Karte
                // ohne Aufklapp-Symbol, genau das ist hier gewollt.
                details: []
            };
        });
    }

    getResultCount(fileResults) {
        return fileResults.reduce((sum, result) => sum + (result.totalWords || 1), 0);
    }

    // Nimmt die fertige Zahl, nicht die Liste: der Aufrufer hat getResultCount
    // zwei Zeilen vorher schon gerufen.
    createPreviewText(count) {
        return `${count} Wörter`;
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
                    // Noch kein Text geladen. Hier stand bis #327 eine
                    // Lemma-ID-Vorschau, die berechnet und dann verworfen wurde:
                    // das snippet daneben ist ein fester Hinweistext.
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