/**
 * MHDBDB - Stage 3 of lemma resolution (partial match fallback)
 *
 * Shared by the main site search (assets/js/search/search-engine.js) and the
 * playground (playground/js/data/authority-manager.js), mirroring how
 * text-normalizer.js and lemma-match.js are shared.
 *
 * This module deliberately exports only the PREDICATE and the COMPARATOR, not
 * the whole three-stage orchestration: the two callers hold their lemmata in
 * different shapes (the main site reads a precomputed `lemma.normalized` from
 * the authority index, the playground normalizes `lemma.lemma` at runtime and
 * additionally ranks by corpus frequency). Sharing the decision rule is what
 * fixes the drift; sharing the loop would not.
 *
 * Contract: CONTRACTS.md §C.
 *
 * Why prefix matching (#224): stage 3 used to be a bidirectional SUBSTRING test
 * (`lemma ⊆ query ∨ query ⊆ lemma`). The `query ⊆ lemma` direction matched every
 * short lemma hiding anywhere inside the input, because the lexicon holds 5
 * one-letter, 98 two-letter and 598 three-letter normalized forms. Middle High
 * German inflection is suffixal, so a prefix test keeps the useful cases (stem
 * input → full lemma, inflected input → lemma) and drops the noise.
 *
 * Note on the #224 report: the search for "böses" shown there carried a
 * DECOMPOSED umlaut (o + U+0308). That is why it missed stages 1 and 2 and
 * reached stage 3 at all, and why the result was ês/ô/sê WITHOUT bœse. With a
 * precomposed ö, stage 2 resolves it correctly via variants["boeses"]. Both
 * causes are fixed: NFC composition in text-normalizer.js, and this rule.
 * Real stage-3 inputs look like "minnecl" (16 hits → 5) or "schwertkampf"
 * (14 hits → 0).
 *
 * Measured over 300 seeded variant forms
 * (scripts/audit/measure-stage3-resolution.py): median result list 8 → 0,
 * largest list 108 → 8, recall 11.3 % → 10.7 %, top-1 accuracy 0.3 % → 10.0 %.
 * The top-1 figure is mostly the new SORTING, not the new rule: the old rule
 * with the same distance ranking already reaches 9.3 %.
 */

/**
 * Traegt ein Lemma mindestens einen Korpusbeleg? (#463) Massstab ist der
 * Reverse-Index `corpusIndex.lemmaIndex` (Eintrag nur bei Beleg, gemessen
 * 10.10.2026: 0 leere Eintraege). Fehlt der Index (alter Stand oder noch nicht
 * geladen) oder ist er leer (der Playground faellt bei fehlendem Feld auf `{}`
 * zurueck), gilt alles als belegt, die Stufen verhalten sich dann wie vor #463.
 *
 * @param {Object|null|undefined} lemmaIndex - corpusIndex.lemmaIndex
 * @param {string} lemmaId - mit `lemma_`-Praefix
 * @returns {boolean}
 */
export function isAttestedLemma(lemmaIndex, lemmaId) {
    if (!lemmaIndex) return true;
    let leer = true;
    for (const _schluessel in lemmaIndex) { leer = false; break; }
    if (leer) return true;
    const textIds = lemmaIndex[lemmaId];
    return Array.isArray(textIds) && textIds.length > 0;
}

/**
 * Haelt Stufe 1? Nur wenn mindestens ein Stufe-1-Treffer belegt ist. Sonst
 * wird Stufe 2 mitgefragt (Stufe 3 bleibt den Eingaben vorbehalten, die in
 * Stufe 1 und 2 nichts finden) und die unbelegten Treffer bleiben in der
 * Liste (#463, Vertrag in CONTRACTS.md §C).
 *
 * @param {string[]} stage1Ids
 * @param {Object|null|undefined} lemmaIndex
 * @returns {boolean}
 */
export function stage1Holds(stage1Ids, lemmaIndex) {
    return stage1Ids.some(id => isAttestedLemma(lemmaIndex, id));
}

/**
 * Minimum normalized lemma length for the "input starts with lemma" direction.
 * Without it, `ô`/`o` and `ês`/`es` match almost any input. Not applied to the
 * other direction, where the lemma is longer than the query by construction.
 * Note the flip side: at exactly 3 a fragment like `hel` can be the single hit
 * for "heldentum", and `matches[0]` consumers take it silently.
 * Keep in sync with MIN_LEMMA_PREFIX_LENGTH in
 * scripts/audit/measure-stage3-resolution.py.
 */
export const MIN_LEMMA_PREFIX_LENGTH = 3;

/**
 * Is a lemma a stage-3 candidate for a search term? Both arguments must already
 * be normalized (TextNormalizer.normalizeMHG + lowercase).
 *
 * Two accepted directions:
 *   1. lemma starts with query   — truncation search, "minn" → "minne"
 *   2. query starts with lemma   — inflected input, "boeses" → "bœse";
 *                                  only for lemmata of MIN_LEMMA_PREFIX_LENGTH+
 *
 * @param {string|null} lemmaNormalized - normalized lemma form
 * @param {string} queryNormalized - normalized search term
 * @returns {boolean}
 */
export function isStage3Match(lemmaNormalized, queryNormalized) {
    if (!lemmaNormalized || !queryNormalized) return false;
    if (lemmaNormalized.startsWith(queryNormalized)) return true;
    return lemmaNormalized.length >= MIN_LEMMA_PREFIX_LENGTH
        && queryNormalized.startsWith(lemmaNormalized);
}

/**
 * How far is a stage-3 candidate from the search term? Lower is better; the
 * exact-length match sorts first, longer compounds last. Callers sort by this
 * and break ties with whatever ranking signal they have (the playground uses
 * corpus frequency, see #163/#164; the main site keeps index order).
 *
 * @param {string} lemmaNormalized - normalized lemma form
 * @param {string} queryNormalized - normalized search term
 * @returns {number}
 */
export function stage3Distance(lemmaNormalized, queryNormalized) {
    return Math.abs((lemmaNormalized || '').length - (queryNormalized || '').length);
}
