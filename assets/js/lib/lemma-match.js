/**
 * MHDBDB - Lemma Reference Matching Utility
 * Centralized exact-token matching of a searched lemma id against a @lemmaRef.
 *
 * Shared by the reading view (assets/js/rendering/) and the playground
 * (playground/js/), mirroring how text-normalizer.js is shared. Before #130 the
 * same logic was inline-duplicated at 6 sites across 4 files; #126 was caused by
 * one of those copies using an unbounded substring test.
 *
 * Contract: CONTRACTS.md §B.1.
 */

/**
 * Does a @lemmaRef contain the searched lemma id as an exact, whitespace-separated
 * token? A @lemmaRef may carry several space-separated values
 * (e.g. "lexicon.xml#lemma_308 lexicon.xml#lemma_5"). The id is matched against the
 * fragment after '#' of each value — exactly, never as a substring. A substring test
 * would wrongly match "lemma_308" inside "lemma_3089" (jâmer). See #126.
 *
 * @param {string|null} lemmaRef - The raw @lemmaRef attribute value (may be null/empty).
 * @param {string} lemmaId - The searched lemma id, e.g. "lemma_308".
 * @returns {boolean} True iff lemmaId is an exact token of lemmaRef.
 */
export function lemmaRefMatchesId(lemmaRef, lemmaId) {
    if (!lemmaRef || !lemmaId) return false;
    const refIds = lemmaRef.split(/\s+/).map(t => t.split('#')[1]).filter(Boolean);
    return refIds.includes(lemmaId);
}
