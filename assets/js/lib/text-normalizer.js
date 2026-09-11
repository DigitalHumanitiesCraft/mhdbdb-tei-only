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
 * - Breve-Umlaute (Wenzelsbibel): ŏ→oe, ŭ→ue
 * - Breve als böhmische Schreibkonvention (Wenzelsbibel): w̆→w, n̆→n
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
            // Breve über o/u ist in der Wenzelsbibel das Umlautzeichen,
            // nicht ein eigener Laut (#224, KZW 28.07.): Klaus Schmidts
            // Eingabe war bo+U+0306+ses aus der WZB-Leseansicht, nicht
            // ein zerlegtes Trema. Belegt an den lemmatisierten WZB-Tokens
            // (bo+breve+ses -> lemma_788 bœse, scho+breve+ne -> lemma_5280
            // schœne); von 469 lemmatisierten Breve-Tokens sitzen 405 auf
            // o/u. Steht nach .normalize('NFC'), weil das kombinierende
            // Breve dort zu U+014F/U+016D wird.
            .replace(/ŏ/g, 'oe')
            .replace(/ŭ/g, 'ue')
            // Breve über w und n ist kein Umlautzeichen, sondern böhmische
            // Schreibkonvention (few̆er = viur, ew̆er = ir, wenn̆ = wan).
            // Es wird daher getilgt, nicht zu einem Digraphen aufgelöst
            // (KZW/Julia 06.08., ADR-017). Betrifft 113 WZB-Tokens, davon 64
            // lemmatisiert. Ohne die Regel war keines davon per Eingabe
            // auffindbar, weil w+U+0306 und n+U+0306 keine präkomponierte
            // Form haben und Schritt 0 sie deshalb stehen lässt.
            // Steht nach ŏ/ŭ, damit die Reihenfolge der Umlautregeln
            // unberührt bleibt; nach .toLowerCase(), damit auch W̆/N̆ greifen.
            // Escapes statt Literale: ein kombinierendes Zeichen im Quelltext
            // ist unsichtbar, und ein Editor mit Auto-Normalisierung könnte
            // es still verändern.
            .replace(/w\u0306/g, 'w')
            .replace(/n\u0306/g, 'n')
            // Breve auf den übrigen Basiszeichen bleibt unangetastet
            // (23 Tokens: y 5, a 5, v 4, r 2, m 2, i 2, e 2, z 1). Nicht weil
            // die präkomponierte Form fehlte, für a/e/i gibt es sie, sondern
            // weil zu wenige und keine lemmatisierten Belege darunter sind,
            // um eine Regel abzuleiten (hălses, nămen, schĕpfen).
            // Ligatures
            .replace(/æ/g, 'ae')
            .replace(/œ/g, 'oe')
            // Other special characters
            .replace(/ǒ/g, 'o');
    }

    /**
     * Fold diacritics onto their base letter: ä→a, ö→o, ü→u, ß→ss,
     * plus the long vowels â→a and so on.
     *
     * This is NOT the MHG normalization above and does not replace it. The
     * two answer opposite questions, and a German search box needs both:
     *
     * - normalizeMHG expands ä→ae, so that typing "baeume" finds "Bäume".
     * - foldDiacritics collapses ä→a, so that typing "baum" finds "Bäume".
     *
     * The second direction is German umlaut alternation (Baum/Bäume,
     * Wald/Wälder, groß/größer): the stem a user types carries no umlaut,
     * the inflected descriptor does. Under ä→ae the stem is not even a
     * prefix of the target, so the hit is unreachable (#419, Alan van
     * Beek: "tree" found "Bäume" via termEN "Trees", "baum" found nothing).
     *
     * Intended for the modern German and English descriptors of the
     * authority files (concepts, genres, names, work titles), not for
     * Middle High German attestations: use normalizeMHG for those.
     *
     * @param {string} text - Text to fold
     * @returns {string} Folded text (NFC, lowercase, diacritics removed)
     */
    static foldDiacritics(text) {
        if (!text) return '';

        return text
            // Same reason as in normalizeMHG: a decomposed "ö" (o + U+0308)
            // would not match the precomposed rules below.
            .normalize('NFC')
            .toLowerCase()
            .replace(/[äâā]/g, 'a')
            .replace(/[öôō]/g, 'o')
            .replace(/[üûū]/g, 'u')
            .replace(/[êē]/g, 'e')
            .replace(/[îī]/g, 'i')
            .replace(/ß/g, 'ss')
            // Ligatures keep the digraph: they are two letters, not an
            // accented one, and "ae" is what a user types for them.
            .replace(/æ/g, 'ae')
            .replace(/œ/g, 'oe')
            // Everything else that carries a mark, generically. The explicit
            // rules above run first and are not redundant: they map to a
            // digraph or to a chosen base letter, which decomposition cannot
            // decide (ß has no combining mark at all, and æ is a letter of
            // its own, not an accented a). What is left after them is the
            // ordinary Latin-with-accent case, and dropping the mark is the
            // right answer there. Without this the @returns above would be a
            // promise the function does not keep: the genre `Malmariée-Lied`
            // stayed unreachable through `malmariee`, which is exactly the
            // kind of miss this function exists to prevent (found by the CI
            // review on #437; it is the only such descriptor in the four
            // authority sets, measured 2026-09-11).
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .normalize('NFC');
    }

    /**
     * Check if text contains search term after diacritic folding.
     * Companion to matchesNormalized for authority-file descriptors,
     * see foldDiacritics for why both are needed.
     * @param {string} text - Text to search in
     * @param {string} searchTerm - Term to search for
     * @returns {boolean} True if folded text contains folded search term
     */
    static matchesFolded(text, searchTerm) {
        if (!text || !searchTerm) return false;

        return this.foldDiacritics(text).includes(this.foldDiacritics(searchTerm));
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