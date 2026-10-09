/**
 * Search Engine
 * Performs lemma searches across the corpus index with filtering
 * Uses MHG normalization for robust search
 */

// Import MHG normalizer from shared library
import { TextNormalizer } from '../lib/text-normalizer.js';
import { isStage3Match, stage3Distance } from '../lib/lemma-resolve.js';
import { parseLemmaIdInput } from '../lib/lemma-id-input.js';
import { countingAttributions, formatAttributionList, personIdOf } from '../lib/attributions.js';

class SearchEngine {
    constructor(authorityIndex, corpusIndex) {
        this.authorityIndex = authorityIndex;
        this.corpusIndex = corpusIndex;

        // Reverse lookup map for the author filter
        // (Die Gattungskette workToGenre/getGenre ist mit #433 entfallen: sie
        // las work.genre, das keines der Werke traegt, und speiste nur den
        // nie sichtbaren Gattungs-Chip der Trefferkarte.)
        this.workToAuthor = this.buildWorkToAuthorMap();

        // #467: Existenzpruefung fuer die Suche per Lemma-Nummer
        this.lemmaIds = new Set(this.authorityIndex.lemmata.map(l => l.id));
    }

    /**
     * Build map: workId → Set of author ids.
     * Alle Zuschreibungen, die als Autor zaehlen (#452): auch "umstritten" und
     * "unsicher zugeschrieben", nicht aber Bearbeiter und verworfene. Werke
     * ohne attributions fallen auf das Kompatibilitaetsfeld authorRef zurueck.
     */
    buildWorkToAuthorMap() {
        const map = new Map();

        this.authorityIndex.works.forEach(work => {
            if (!work.id) return;
            const ids = new Set();
            if (Array.isArray(work.attributions)) {
                countingAttributions(work).forEach(a => {
                    const id = personIdOf(a.ref);
                    if (id) ids.add(id);
                });
            } else if (work.authorRef) {
                // Extract author ID from ref: "persons.xml#person_123" → "person_123"
                ids.add(personIdOf(work.authorRef));
            }
            if (ids.size > 0) {
                map.set(work.id, ids);
            }
        });

        return map;
    }

    /**
     * Search for a lemma across all texts
     * @param {string} searchTerm - Word or lemma to search for
     * @param {object} filters - { includedTexts: Set, authorId: string }
     * @returns {array} - Array of search results
     */
    async searchLemma(searchTerm, filters = {}) {
        // Steps 1+2: normalize and resolve to lemma ID(s), or take a lemma
        // number as given (#467)
        const lemmaIds = this.resolveSearchTerm(searchTerm);

        if (lemmaIds.length === 0) {
            return [];
        }

        // Step 3: Find all texts containing these lemmas
        const results = [];

        lemmaIds.forEach(lemmaId => {
            const textIds = this.corpusIndex.lemmaIndex[lemmaId];

            if (!textIds) {
                return;
            }

            textIds.forEach(textId => {
                const text = this.corpusIndex.texts.find(t => t.id === textId);

                if (!text) {
                    return;
                }

                // Apply filters
                if (!this.passesFilters(text, filters)) {
                    return;
                }

                // Count matches in this text
                const matchCount = text.lemmata[lemmaId] ? text.lemmata[lemmaId].length : 0;

                // Extract snippet (first 100 chars of title or first match context)
                const snippet = this.extractSnippet(text, lemmaId);

                results.push({
                    textId: text.id,
                    lemmaId: lemmaId,
                    title: text.title,
                    author: this.getAuthorLine(text),
                    matchCount: matchCount,
                    wordCount: text.wordCount,
                    snippet: snippet
                });
            });
        });

        // Sort by match count (descending)
        results.sort((a, b) => b.matchCount - a.matchCount);

        return results;
    }

    /**
     * Rohe Eingabe zu Lemma-IDs. Eine Lemma-Nummer ("4086", "lemma_4086")
     * ist eine eindeutige ID und geht nicht durch die drei Stufen (#467,
     * KZW 24.09.2026); eine unbekannte Nummer loest zu nichts auf, statt als
     * Schreibform weitergesucht zu werden.
     * @param {string} searchTerm
     * @returns {string[]} IDs mit `lemma_`-Praefix
     */
    resolveSearchTerm(searchTerm) {
        const idInput = parseLemmaIdInput(searchTerm);
        if (idInput) {
            return this.lemmaIds.has(idInput) ? [idInput] : [];
        }
        return this.resolveLemmaIds(TextNormalizer.normalizeMHG(searchTerm));
    }

    /**
     * Ob die Eingabe in Stufe 2 auf mehrere Kandidaten zeigt (ADR-021, #378).
     * Nur dann steht der Hinweis "kann zu mehreren Lemmata gehoeren" da: eine
     * Lemma-Nummer und ein Stufe-1-Treffer fragen die Variantenliste nie.
     * @param {string} searchTerm
     * @returns {boolean}
     */
    hasAmbiguousVariant(searchTerm) {
        if (parseLemmaIdInput(searchTerm)) return false;
        const normalized = TextNormalizer.normalizeMHG(searchTerm);
        const stage1 = this.authorityIndex.lemmata.some(lemma => lemma.normalized === normalized);
        return !stage1 && Array.isArray(this.authorityIndex.variantCandidates?.[normalized]);
    }

    /**
     * Resolve search term to lemma IDs
     */
    resolveLemmaIds(normalized) {
        const lemmaIds = [];

        // Strategy 1: Exact match on normalized lemma
        this.authorityIndex.lemmata.forEach(lemma => {
            if (lemma.normalized === normalized) {
                lemmaIds.push(lemma.id);
            }
        });

        if (lemmaIds.length > 0) {
            return lemmaIds;
        }

        // Strategy 2: Check variants index. Eine Schreibform mit mehreren
        // Kandidaten steht in variantCandidates, geordnet nach Vorschrift B
        // (ADR-021, #378); sonst traegt variants genau ein Lemma.
        const candidates = this.authorityIndex.variantCandidates?.[normalized];
        if (Array.isArray(candidates)) {
            return [...candidates];
        }
        const variantLemmaId = this.authorityIndex.variants[normalized];
        if (variantLemmaId) {
            lemmaIds.push(variantLemmaId);
            return lemmaIds;
        }

        // Strategy 3: Partial match fallback. Prefix-oriented in both directions
        // (stem input → lemma, inflected input → lemma), never an unbounded
        // substring test: that is what made "böses" resolve to ês/ô/sê (#224).
        // Rule and rationale live in lib/lemma-resolve.js, contract in
        // CONTRACTS.md §C.
        const partial = this.authorityIndex.lemmata
            .filter(lemma => isStage3Match(lemma.normalized, normalized))
            .sort((a, b) =>
                stage3Distance(a.normalized, normalized) - stage3Distance(b.normalized, normalized)
            );
        partial.forEach(lemma => lemmaIds.push(lemma.id));

        return lemmaIds;
    }

    /**
     * Check if text passes filters
     */
    passesFilters(text, filters) {
        // Text inclusion filter (from checkbox selection)
        if (filters.includedTexts) {
            if (!filters.includedTexts.has(text.id)) {
                return false;
            }
        }

        // Author filter
        if (filters.authorId) {
            const textAuthors = this.getAuthorIds(text.workRef);
            if (!textAuthors.has(filters.authorId)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Alle Autor-IDs eines Werks (#452), leeres Set wenn keine bekannt.
     */
    getAuthorIds(workRef) {
        if (!workRef) return new Set();

        // Extract work ID
        const workId = workRef.includes('#') ? workRef.split('#')[1] : workRef;

        return this.workToAuthor.get(workId) || new Set();
    }

    /**
     * Get author ID from work reference: der erste Autor (Kompatibilitaet).
     */
    getAuthorId(workRef) {
        const [first] = this.getAuthorIds(workRef);
        return first || null;
    }

    /**
     * Autorenzeile eines Textes (#452): alle Zuschreibungen des Werks mit
     * Statustext ("Anonym; Konrad von Würzburg (umstritten)"). Ohne Werk oder
     * ohne attributions der Name zum Kompatibilitaetsfeld authorRef.
     */
    getAuthorLine(text) {
        const workId = text.workRef
            ? (text.workRef.includes('#') ? text.workRef.split('#')[1] : text.workRef)
            : null;
        const work = workId ? this.authorityIndex.works.find(w => w.id === workId) : null;
        const line = work ? formatAttributionList(work) : '';
        return line || this.getAuthorName(text.authorRef);
    }

    /**
     * Get author name from author reference
     */
    getAuthorName(authorRef) {
        if (!authorRef) return null;

        // Extract author ID
        const authorId = authorRef.includes('#') ? authorRef.split('#')[1] : authorRef;

        const author = this.authorityIndex.persons.find(p => p.id === authorId);

        return author ? author.preferredName : null;
    }

    /**
     * Extract context snippet for preview
     */
    extractSnippet(text, lemmaId) {
        // For now, return truncated title
        // Later: can extract actual context from TEI file
        const maxLength = 100;

        if (text.title.length > maxLength) {
            return text.title.substring(0, maxLength) + '...';
        }

        return text.title;
    }
}

export { SearchEngine };
