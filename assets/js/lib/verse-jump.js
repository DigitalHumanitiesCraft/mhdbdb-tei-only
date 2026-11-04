/**
 * Sprung zu einer Versnummer in der Leseansicht (#655).
 *
 * Gemessen wird auf dem gerenderten DOM der Leseansicht (tei-text-reader.js):
 * jede <l> ist ein `.verse-line[data-n]`, jedes <div> ein `.tei-div[data-n]`,
 * jede <lg> ein `.verse-group[data-n]`. Nur rein numerische data-n zählen,
 * wie bei der Randnummerierung im Rendering.
 *
 * Drei Modi, in dieser Reihenfolge, der erste eindeutige gewinnt:
 *   'plain'   die Versnummer allein ist im Text eindeutig ("5579")
 *   'div'     erst (nächstes Vorfahr-div mit @n, Vers) ist eindeutig ("339.26")
 *   'section' erst (nächstes Vorfahr-div ODER -lg mit @n, Vers) ist eindeutig
 *   null      keiner der drei: kein Sprungfeld, kein Raten bei Mehrdeutigkeit
 *
 * In den Abschnittsmodi muss jeder numerische Vers einen Abschnitt haben,
 * sonst wäre er mit "Abschnitt.Vers" nicht eingebbar.
 */

const NUMERIC = /^\d+$/;

/**
 * Reine Klassifikation, ohne DOM.
 * @param {Array<{n: string, div: string, sec: string}>} entries
 *   je numerischem Vers: n, @n des nächsten div (oder ''), @n des nächsten
 *   div/lg (oder '')
 * @returns {'plain'|'div'|'section'|null}
 */
export function classifyVerses(entries) {
    if (!entries.length) return null;
    const unique = (keyOf) => {
        const seen = new Set();
        for (const e of entries) {
            const key = keyOf(e);
            if (key === null || seen.has(key)) return false;
            seen.add(key);
        }
        return true;
    };
    if (unique(e => e.n)) return 'plain';
    if (unique(e => (e.div ? `${e.div}\u0000${e.n}` : null))) return 'div';
    if (unique(e => (e.sec ? `${e.sec}\u0000${e.n}` : null))) return 'section';
    return null;
}

/**
 * Baut den Sprungindex über die gerenderte Leseansicht.
 * @param {ParentNode} root  Container (#readingBody)
 * @returns {{mode: 'plain'|'div'|'section'|null, lookup: Map<string, Element>,
 *            example: string}}
 *   lookup: Schlüssel ("5579" oder "339\u000026") -> Zeile; example: ein
 *   echter Eingabewert für den Platzhalter (höchste Versnummer im Modus
 *   'plain', sonst der erste Schlüssel als "Abschnitt.Vers").
 */
export function buildVerseJumpIndex(root) {
    const lines = [];
    for (const el of root.querySelectorAll('.verse-line[data-n]')) {
        const n = el.getAttribute('data-n');
        if (!NUMERIC.test(n)) continue;
        const div = el.parentElement && el.parentElement.closest('.tei-div[data-n]:not([data-n=""])');
        const sec = el.parentElement && el.parentElement.closest(
            '.tei-div[data-n]:not([data-n=""]), .verse-group[data-n]:not([data-n=""])');
        lines.push({
            el, n,
            div: div ? div.getAttribute('data-n') : '',
            sec: sec ? sec.getAttribute('data-n') : ''
        });
    }
    const mode = classifyVerses(lines);
    const lookup = new Map();
    let example = '';
    if (mode === 'plain') {
        let max = -1;
        for (const l of lines) {
            lookup.set(l.n, l.el);
            const v = parseInt(l.n, 10);
            if (v > max) { max = v; example = l.n; }
        }
    } else if (mode) {
        for (const l of lines) {
            const section = mode === 'div' ? l.div : l.sec;
            lookup.set(`${section}\u0000${l.n}`, l.el);
        }
        const first = lines[0];
        example = `${mode === 'div' ? first.div : first.sec}.${first.n}`;
    }
    return { mode, lookup, example };
}

/**
 * Eingabe auslesen.
 * @returns {{key: string, label: string}|null}  null bei unlesbarer Eingabe
 */
export function parseVerseInput(mode, text) {
    const value = String(text || '').trim();
    if (!value) return null;
    if (mode === 'plain') {
        return NUMERIC.test(value) ? { key: value, label: value } : null;
    }
    // Abschnitt und Vers, getrennt durch Punkt, Komma, Doppelpunkt oder
    // Leerzeichen. Nicht gierig, damit "1.2.3" Abschnitt "1.2", Vers 3 liefert.
    const m = value.match(/^(.+?)[\s.,:]+(\d+)$/);
    if (!m) return null;
    return {
        key: `${m[1].trim()}\u0000${m[2]}`,
        label: `${m[1].trim()}.${m[2]}`
    };
}
