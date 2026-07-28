/**
 * MHDBDB Playground - Text Normalization Utility
 * Centralized Middle High German character normalization for consistent search behavior
 */

/**
 * TextNormalizer provides MHG-specific text normalization utilities
 * for consistent search across all application features.
 *
 * Normalizes:
 * - Long vowels with macrons: â→a, ê→e, î→i, ô→o, û→u
 * - Long vowels with macrons (alternate): ā→a, ē→e, ī→i, ō→o, ū→u
 * - Umlauts: ä→ae, ö→oe, ü→ue
 * - Ligatures: æ→ae, œ→oe
 * - Special characters: ǒ→o
 */
export class TextNormalizer {
    /**
     * Normalize Middle High German special characters for search
     * @param {string} text - Text to normalize
     * @returns {string} Normalized text (lowercase, special chars replaced)
     */
    static normalizeMHG(text) {
        if (!text) return '';

        return text
            // Unicode-Komposition ZUERST (#224): Ein „ö" kann als ein Zeichen
            // (U+00F6) oder als o + kombinierendes Trema (U+006F U+0308)
            // kodiert sein. Beide sehen identisch aus, aber nur die erste Form
            // trifft die ö→oe-Regel unten. Ohne diesen Schritt fällt eine
            // zerlegte Eingabe durch Stufe 1 UND Stufe 2 der Lemma-Auflösung
            // und landet im Partial-Match-Fallback: die Suche nach „böses"
            // lieferte so ês, ô und sê statt bœse (Bug-Report Klaus Schmidt).
            // Zerlegte Formen entstehen beim Kopieren aus macOS-Quellen und
            // aus manchen Editionsdatenbanken.
            .normalize('NFC')
            .toLowerCase()
            // Long vowels with circumflex
            .replace(/[âā]/g, 'a')
            .replace(/[êē]/g, 'e')
            .replace(/[îī]/g, 'i')
            .replace(/[ôō]/g, 'o')
            .replace(/[ûū]/g, 'u')
            // Umlauts (expand to digraphs for better matching)
            .replace(/ä/g, 'ae')
            .replace(/ö/g, 'oe')
            .replace(/ü/g, 'ue')
            // Ligatures
            .replace(/æ/g, 'ae')
            .replace(/œ/g, 'oe')
            // Other special characters
            .replace(/ǒ/g, 'o');
    }

    /**
     * Check if text contains search term (with normalization)
     * @param {string} text - Text to search in
     * @param {string} searchTerm - Term to search for
     * @returns {boolean} True if normalized text contains normalized search term
     */
    static matchesNormalized(text, searchTerm) {
        if (!text || !searchTerm) return false;

        const normalizedText = this.normalizeMHG(text);
        const normalizedSearch = this.normalizeMHG(searchTerm);

        return normalizedText.includes(normalizedSearch);
    }

    /**
     * Check for exact match (with normalization)
     * @param {string} text - Text to compare
     * @param {string} searchTerm - Term to match exactly
     * @returns {boolean} True if normalized texts are identical
     */
    static exactMatchNormalized(text, searchTerm) {
        if (!text || !searchTerm) return false;

        const normalizedText = this.normalizeMHG(text);
        const normalizedSearch = this.normalizeMHG(searchTerm);

        return normalizedText === normalizedSearch;
    }

    /**
     * Check if text starts with search term (with normalization)
     * @param {string} text - Text to check
     * @param {string} searchTerm - Term to check for at start
     * @returns {boolean} True if normalized text starts with normalized search term
     */
    static startsWithNormalized(text, searchTerm) {
        if (!text || !searchTerm) return false;

        const normalizedText = this.normalizeMHG(text);
        const normalizedSearch = this.normalizeMHG(searchTerm);

        return normalizedText.startsWith(normalizedSearch);
    }
}