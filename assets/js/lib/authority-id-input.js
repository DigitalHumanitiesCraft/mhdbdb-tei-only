/**
 * IDs aus den Authority-Files als Sucheingabe (#545)
 *
 * Die Begriffshilfe (#498) nennt Begriffe mit ihrer ID, etwa "concept_12040000".
 * Damit sich ihre Vorschlaege im Playground nachvollziehen lassen, nehmen die
 * Register-Suchfelder (Personen, Werke, Lemmata, Begriffe, Gattungen, Namen) und
 * die Begriffs-Verteilung auch eine ID an, in denselben Schreibweisen wie die
 * Lemma-Nummer seit #467 (lemma-id-input.js):
 *
 *   concept_12040000 | 12040000 | #concept_12040000 | concepts.xml#concept_12040000
 *
 * Fuehrende Nullen fallen bei rein numerischer Eingabe weg ("012040000"). Gross- und
 * Kleinschreibung zaehlt nicht (work_WZB, genre_00bb7cc9).
 *
 * Anders als in der Korpussuche ersetzt ein ID-Treffer hier die Textsuche nicht,
 * er kommt zu ihren Treffern hinzu: Werksiglen und Gattungs-IDs teilen sich
 * Zeichen mit gewoehnlichen Suchwoertern, und die Register sollen nichts
 * verlieren, was sie vorher gefunden haben.
 */

const ID_INPUT = /^(?:[\w-]+\.xml)?#?(?:([a-z]+)_)?([a-z0-9-]+)$/i;

/**
 * @param {Array<{id: string}>} items Eintraege eines Registers
 * @param {string} prefix ID-Praefix ohne Unterstrich, z. B. "concept"
 * @param {string} term Rohe Eingabe
 * @returns {object|null} der Eintrag mit dieser ID oder null
 */
export function findByIdInput(items, prefix, term) {
    const m = ID_INPUT.exec((term || '').trim());
    if (!m || !items) return null;
    // Ein fremdes Praefix ("person_12" im Begriffsfeld) ist keine ID dieses Registers
    if (m[1] && m[1].toLowerCase() !== prefix.toLowerCase()) return null;
    // Roh und ohne fuehrende Nullen: eine ID, die selbst mit Null beginnt,
    // bleibt so unter ihrer eigenen Schreibweise auffindbar
    const formen = new Set([m[2], m[2].replace(/^0+(?=\d+$)/, '')]
        .map((rest) => `${prefix}_${rest}`.toLowerCase()));
    return items.find((item) => formen.has((item.id || '').toLowerCase())) || null;
}

/**
 * Den ID-Treffer vor die Treffer der Textsuche stellen, ohne Dublette.
 *
 * @param {object|null} idHit Ergebnis von findByIdInput
 * @param {Array<object>} matches Treffer der Textsuche
 * @returns {Array<object>}
 */
export function withIdHit(idHit, matches) {
    if (!idHit) return matches;
    return [idHit, ...matches.filter((item) => item !== idHit)];
}
