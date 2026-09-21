/**
 * Sprachregelung für den leeren Analyse-Scope (#204).
 *
 * Bis #204 bekamen die Korpusanalysen alle 667 Texte, egal was im
 * Korpus-Browser angehakt war. Ein leeres Textarray konnte deshalb nur eines
 * heißen: der Korpus ist noch nicht geladen. Genau das sagten die elf Guards
 * in den Werkzeugen, und sie sagten es zu Recht.
 *
 * Seit die Auswahl wirkt, hat dasselbe leere Array zwei Ursachen, und die
 * alte Meldung trifft nur noch eine davon. Wer alle Häkchen entfernt und dann
 * eine Analyse startet, bekäme sonst „Korpus ist noch nicht geladen. Bitte
 * einen Moment warten" zu lesen und würde auf etwas warten, das längst fertig
 * ist. Ein Guard, dem die Änderung sein Subjekt entzogen hat.
 *
 * Der Griff auf `window.playground` folgt dem Muster aus
 * `multi-lemma-search.js` (dort seit #167 Finding 22): die Werkzeuge kennen
 * nur ihren Text-Thunk, und die Frage „ist überhaupt ein Korpus da" liegt
 * eine Ebene darüber.
 */

const NICHT_GELADEN =
    'Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.';

const NICHTS_AUSGEWAEHLT =
    'Kein Text ausgewählt. Dieses Werkzeug wertet die Auswahl aus dem Korpus-Browser ' +
    '(Schritt 1) aus: dort mindestens einen Text anhaken, oder über "Alle" das ganze ' +
    'Korpus auswählen.';

/**
 * Begründet einen leeren Scope. Aufrufen erst, wenn der Text-Thunk tatsächlich
 * nichts geliefert hat.
 *
 * @returns {string} Meldung für renderError()
 */
export function emptyScopeMessage() {
    const korpusGeladen = !!window.playground?.corpusData?.texts?.length;
    return korpusGeladen ? NICHTS_AUSGEWAEHLT : NICHT_GELADEN;
}

/**
 * Die Sigle des einzigen ausgewählten Texts, sonst null.
 *
 * Für Werkzeuge mit eigenem Textfilter (Reim-Wörterbuch): die dürfen die
 * Auswahl aus Schritt 1 nicht still mitfiltern, weil ihr eigenes Feld den
 * Zustand dann nur zur Hälfte anzeigt. Stattdessen tragen sie den Einzelfall
 * sichtbar in ihr Feld ein, wo er les- und löschbar ist.
 *
 * @returns {string|null}
 */
export function singleSelectedTextId() {
    const auswahl = window.playground?.corpusData?.includedTexts;
    if (!auswahl || auswahl.size !== 1) return null;
    return [...auswahl][0];
}

/**
 * Kennung der Textmenge, über die gerechnet wurde.
 *
 * Für Werkzeuge, die ihr fertiges Ergebnis im State halten und beim Öffnen
 * nur neu rendern: sie können damit erkennen, dass die Auswahl seit der
 * Berechnung eine andere ist, und das Ergebnis verwerfen, statt eine Zahl
 * stehen zu lassen, die zur Auswahl daneben nicht mehr passt.
 *
 * Die IDs und nicht ihre Anzahl, denn ein Tausch (CR raus, WH rein) lässt
 * die Länge gleich und wäre sonst nicht zu sehen.
 *
 * @param {Array} texts Ergebnis des Text-Thunks
 * @returns {string}
 */
export function scopeSignature(texts) {
    return (texts || []).map(t => t.id).join('|');
}
