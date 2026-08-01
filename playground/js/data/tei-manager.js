/**
 * MHDBDB Playground - TEI Files Manager
 * Multi-Lemma-Suche über den vorgebauten Korpus-Index.
 *
 * Der früher hier liegende Upload-Pfad (Datei einlesen, XML-DOM parsen,
 * darin suchen) ist mit #314 entfernt: die Upload-UI war beim Redesign
 * weggefallen, damit war der ganze Zweig unerreichbar. Die Suche laeuft
 * ausschließlich über data/corpus-index.json.gz, und Positionen sind
 * damit durchgängig die aus CONTRACTS Paragraph B.
 */

import { lemmaRefMatchesId } from '../../../assets/js/lib/lemma-match.js';

export class TEIFilesManager {
    constructor(teiData) {
        this.teiData = teiData;
    }

    // ==================== INDEX-BASED SEARCH (FAST) ====================

    /**
     * Multi-Lemma-Suche über den vorgebauten Korpus-Index.
     */
    async searchMultipleLemmasUsingIndex(lemmaIds, contextType = 'document', maxDistance = 10) {
        // v4.0.0: Dokumentweiter Index, drei Modi. Der frühere
        // paragraph-Modus fiel mit v4.0.0 weg.
        const corpusData = window.playground?.corpusData;
        if (!corpusData || !corpusData.texts) {
            // Früher lief hier ein XML-Fallback für hochgeladene Dateien.
            // Der ist mit #314 weg; ohne Index gibt es nichts zu durchsuchen,
            // und ein stilles [] würde wie "keine Treffer" aussehen.
            console.error('Korpus-Index nicht geladen, Multi-Lemma-Suche nicht möglich');
            throw new Error('Korpus-Index nicht verfügbar');
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

        // Aus demselben Grund wie oben: ein stilles [] sähe wie "keine Treffer"
        // aus. Erreichbar ist der Zweig heute nicht (die UI hat drei Radios,
        // und der Router ignoriert unbekannte Modi aus dem Hash), aber genau
        // diese Konstellation hat den Upload-Pfad 1300 Zeilen lang konserviert.
        throw new Error(`Unbekannter Suchmodus: ${contextType}`);
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
        // Dieselbe Degeneration wie im Nähe-Pfad, andere Ursache: die
        // Vergleichsschleife startet bei i = 1 und läuft mit einem Lemma
        // gar nicht, allInVerse bliebe true und jeder Vers mit dem Lemma
        // wäre ein Treffer.
        //
        // Deshalb einmal normalisieren, deduplizieren und mit DIESER Liste
        // weiterarbeiten. Nur zu zaehlen genuegt nicht: "7532" und
        // "lemma_7532" sind dieselbe ID, ein Aufruf mit
        // ['7532','lemma_7532','9999'] kaeme sonst durch den Guard, und der
        // doppelte Eintrag laege per Konstruktion im selben Vers wie der
        // Anker. Eine Anfrage ueber drei Lemmata waere still als eine ueber
        // zwei beantwortet. Die Funktionskoerper vertragen bare IDs.
        lemmaIds = [...new Set(lemmaIds.map(id => String(id).replace(/^lemma_/, '')))];
        if (lemmaIds.length < 2) return [];

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
            // erste @lemmaRef-ID pro <w>).
            //
            // Kein Vergleich mit dem Nähe-Pfad: searchProximityUsingEnhancedIndex
            // scannt weiterhin words[] und ist damit die bekannte Abweichung
            // von der Consumer-Rule, nicht das Vorbild. Folgenlos ist das nur,
            // solange kein <w> mehrere Referenzen trägt; gemessen am Korpus
            // sind das derzeit 0 von 7.532.998 @lemmaRef-Werten.
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
        // Weniger als zwei VERSCHIEDENE Lemmata lassen die Fenstersuche
        // degenerieren: ohne abzudeckende Restliste liefert findCoveringWindow
        // ein leeres Array, das ist truthy, und jede Fundstelle käme als
        // Treffer mit Abstand 0 zurück. Die Oberfläche fängt den Fall schon ab
        // und erklärt ihn; dieser Guard steht für den nächsten Aufrufer.
        // Einmal normalisieren, deduplizieren und mit DIESER Liste
        // weiterarbeiten. Nur zu zaehlen genuegt nicht: "7532" und
        // "lemma_7532" sind dieselbe ID, ein Aufruf mit
        // ['7532','lemma_7532','9999'] kaeme sonst durch den Guard und
        // truege dieselbe Positionsliste zweimal als abzudeckende Liste
        // ein. Die deckt sich selbst ab. Die gemeldete Distanz bleibt
        // dabei gleich (das dritte Lemma muss ohnehin abgedeckt werden,
        // und windowStart = firstPos ist immer tragfaehig), der Unterschied
        // steht in matchPositions: dort stuende die Trefferposition
        // doppelt, [12, 12, 30] statt [12, 30]. Eine Anfrage ueber drei
        // Lemmata waere still als eine ueber zwei beantwortet.
        //
        // Beobachtbare Folge in der Oberflaeche hat das heute keine: das
        // Feld wird nur in ui-helpers.js als Math.min fuer die
        // Sprungposition gelesen, und ein Duplikat verschiebt das Minimum
        // nicht. Der Guard ist Vertragshygiene fuer den naechsten
        // Aufrufer und auf API-Ebene getestet. Die Funktionskoerper
        // vertragen bare IDs.
        lemmaIds = [...new Set(lemmaIds.map(id => String(id).replace(/^lemma_/, '')))];
        if (lemmaIds.length < 2) return [];

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

}