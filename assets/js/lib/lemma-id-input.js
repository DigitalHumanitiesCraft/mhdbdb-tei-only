/**
 * Lemma-Nummer als Sucheingabe (#467)
 *
 * KZW am 2026-09-24 in #467: Korpussuche und Multi-Lemma-Suche nehmen beide
 * Schreibweisen, "4086" und "lemma_4086", und behandeln sie "jeweils als
 * eindeutige Lemma-ID". Eine Eingabe dieser Form geht deshalb nicht durch die
 * 3-Stufen-Aufloesung (lemma-resolve.js): "36" heisst lemma_36, nicht das
 * Lemma mit der Schreibung "36".
 *
 * Angenommen wird auch die Form aus @lemmaRef im TEI, "lexicon.xml#lemma_4086",
 * wie im Woerterbuch (#481). Fuehrende Nullen fallen weg ("04086" -> lemma_4086),
 * damit eine Eingabe nicht an der Schreibweise der Nummer scheitert.
 *
 * Geteilt von Hauptseite (search-engine.js), Lemma-Seite (Links in die
 * Korpussuche) und Playground (tei-ui.js, multi-lemma-search.js). Das Woerterbuch hat eine eigene Regel, weil es die
 * nackte Zahl zusaetzlich per Praefix sucht (#481).
 */

const LEMMA_ID_INPUT = /^(?:(?:lexicon\.xml)?#?lemma_)?0*(\d+)$/i;

/**
 * @param {string} term Rohe Eingabe
 * @returns {string|null} "lemma_N", wenn die Eingabe eine Lemma-Nummer ist, sonst null
 */
export function parseLemmaIdInput(term) {
    const m = LEMMA_ID_INPUT.exec((term || '').trim());
    return m ? `lemma_${m[1]}` : null;
}
