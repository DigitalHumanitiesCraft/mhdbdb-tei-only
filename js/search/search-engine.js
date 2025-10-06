/**
 * Search Engine
 * Performs lemma searches across the corpus index with filtering
 * Uses MHG normalization for robust search
 */

// Import MHG normalizer from shared library
import { TextNormalizer } from '../../lib/text-normalizer.js';

class SearchEngine {
    constructor(authorityIndex, corpusIndex) {
        this.authorityIndex = authorityIndex;
        this.corpusIndex = corpusIndex;

        // Create reverse lookup maps for fast filtering
        this.workToGenre = this.buildWorkToGenreMap();
        this.workToAuthor = this.buildWorkToAuthorMap();

        console.log('[SearchEngine] Initialized');
    }

    /**
     * Build map: workRef → genre
     */
    buildWorkToGenreMap() {
        const map = new Map();

        this.authorityIndex.works.forEach(work => {
            if (work.id && work.genre) {
                map.set(work.id, work.genre);
            }
        });

        return map;
    }

    /**
     * Build map: workRef → authorId
     */
    buildWorkToAuthorMap() {
        const map = new Map();

        this.authorityIndex.works.forEach(work => {
            if (work.id && work.authorRef) {
                // Extract author ID from ref: "persons.xml#person_123" → "person_123"
                const authorId = work.authorRef.includes('#') ? work.authorRef.split('#')[1] : work.authorRef;
                map.set(work.id, authorId);
            }
        });

        return map;
    }

    /**
     * Search for a lemma across all texts
     * @param {string} searchTerm - Word or lemma to search for
     * @param {object} filters - { genre: string, authorId: string }
     * @returns {array} - Array of search results
     */
    async searchLemma(searchTerm, filters = {}) {
        console.log(`[SearchEngine] Searching for: "${searchTerm}"`);

        // Step 1: Normalize search term
        const normalized = TextNormalizer.normalizeMHG(searchTerm);

        // Step 2: Resolve to lemma ID(s)
        const lemmaIds = this.resolveLemmaIds(normalized);

        if (lemmaIds.length === 0) {
            console.log(`[SearchEngine] No lemma found for "${searchTerm}"`);
            return [];
        }

        console.log(`[SearchEngine] Resolved to lemma IDs:`, lemmaIds);

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
                    author: this.getAuthorName(text.authorRef),
                    genre: this.getGenre(text.workRef),
                    matchCount: matchCount,
                    snippet: snippet
                });
            });
        });

        // Sort by match count (descending)
        results.sort((a, b) => b.matchCount - a.matchCount);

        console.log(`[SearchEngine] Found ${results.length} results`);

        return results;
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

        // Strategy 2: Check variants index
        const variantLemmaId = this.authorityIndex.variants[normalized];
        if (variantLemmaId) {
            lemmaIds.push(variantLemmaId);
            return lemmaIds;
        }

        // Strategy 3: Partial match (fuzzy)
        this.authorityIndex.lemmata.forEach(lemma => {
            if (lemma.normalized.includes(normalized) || normalized.includes(lemma.normalized)) {
                lemmaIds.push(lemma.id);
            }
        });

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

        // Genre filter
        if (filters.genre) {
            const textGenre = this.getGenre(text.workRef);
            if (textGenre !== filters.genre) {
                return false;
            }
        }

        // Author filter
        if (filters.authorId) {
            const textAuthor = this.getAuthorId(text.workRef);
            if (textAuthor !== filters.authorId) {
                return false;
            }
        }

        return true;
    }

    /**
     * Get genre from work reference
     */
    getGenre(workRef) {
        if (!workRef) return null;

        // Extract work ID from ref: "works.xml#work_123" → "work_123"
        const workId = workRef.includes('#') ? workRef.split('#')[1] : workRef;

        return this.workToGenre.get(workId) || null;
    }

    /**
     * Get author ID from work reference
     */
    getAuthorId(workRef) {
        if (!workRef) return null;

        // Extract work ID
        const workId = workRef.includes('#') ? workRef.split('#')[1] : workRef;

        return this.workToAuthor.get(workId) || null;
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
