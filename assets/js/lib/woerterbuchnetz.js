/**
 * Shared Wörterbuchnetz API client (five MHG dictionaries)
 *
 * Single implementation for the lemma pages (#73), the korpus-search
 * lemma panel (#114) and the hapax tool (#196) — see CONTRACTS.md §D.2.
 * Was previously duplicated in lemma/lemma-page.js and assets/js/app.js.
 *
 * - Results are memoized per normalized form for the session: dictionary
 *   content is static, repeat searches must not re-hit the external API.
 * - Entries whose deep-link is not http(s) are dropped — the link comes
 *   from an external API and goes straight into an href.
 * - Entries repeating a deep-link already seen in the same dictionary are
 *   dropped: FindeB returns the same wbnetzid several times when a headword
 *   has spelling doublets, which would render as identical links (#258).
 */

/**
 * Query order = display order, coarsely chronological by relevance for the
 * corpus: the current reference work first, then Lexer with its supplement
 * volume, then the older BMZ, then the Findebuch, whose job is to map attested
 * spellings onto normalized headwords and which therefore reads as a pointer
 * rather than as an article (#258, order per the issue).
 */
export const DICTIONARIES = ['MWB', 'Lexer', 'LexerN', 'BMZ', 'FindeB'];

/**
 * The API exposes sigles only (`/dictionaries` returns sigle + path, no
 * titles), so the resolution lives here. "BMZ" and "FindeB" are unreadable
 * without it (#258 point 3). Years are deliberately left out: the sources
 * disagree on BMZ (1854–1863 vs. 1854–1866) and a wrong year in a tooltip
 * is worse than none.
 */
export const DICTIONARY_TITLES = {
    MWB: 'Mittelhochdeutsches Wörterbuch',
    Lexer: 'Lexer, Mittelhochdeutsches Handwörterbuch',
    LexerN: 'Lexer, Nachträge zum Mittelhochdeutschen Handwörterbuch',
    BMZ: 'Benecke/Müller/Zarncke, Mittelhochdeutsches Wörterbuch',
    FindeB: 'Findebuch zum mittelhochdeutschen Wortschatz',
};

/** Full title for a sigle; unknown sigles fall back to the sigle itself. */
export function dictionaryTitle(sigle) {
    return DICTIONARY_TITLES[sigle] || sigle;
}

const entryCache = new Map(); // normalizedForm -> Promise<[{sigle, entries}]>

function isSafeLink(url) {
    return typeof url === 'string' && /^https?:\/\//i.test(url);
}

export function decodeHtmlEntities(str) {
    // DOMParser statt textarea-innerHTML-Trick: ein API-Wert wie
    // "…</textarea><img src=x onerror=…>" beendet beim innerHTML-Write den
    // RCDATA-Modus und erzeugt echte Elemente, deren Handler auch detached
    // feuern können (mXSS-Klasse) — bevor nachgelagertes Escaping greift.
    // DOMParser-Dokumente haben keinen Browsing-Context: kein Skript läuft,
    // keine Ressource (img src) wird geladen; Markup wird zu reinem Text.
    const doc = new DOMParser().parseFromString(String(str ?? ''), 'text/html');
    return doc.body.textContent ?? '';
}

/**
 * Fetch dictionary entries for a MHG-normalized lemma form.
 *
 * @param {string} normalizedForm - lemma.normalized (â→a, ê→e, ü→ue …)
 * @returns {Promise<Array<{sigle: string, entries: Array, failed: boolean}>>} —
 *   failures resolve to empty entry lists: the links are progressive
 *   enhancement and must never block or break the caller. `failed` says which
 *   of those empty lists mean "request did not go through" rather than "no
 *   such headword". Callers that render links can ignore it; a caller that
 *   turns an empty result into a statement about the evidence must not, or an
 *   outage reads as an absence of attestation (#258 review finding 1).
 */
export function fetchWbnetzEntries(normalizedForm) {
    if (!normalizedForm) return Promise.resolve([]);
    if (entryCache.has(normalizedForm)) return entryCache.get(normalizedForm);

    const lookupForm = encodeURIComponent(normalizedForm);
    const promise = Promise.all(DICTIONARIES.map(async sigle => {
        try {
            const r = await fetch(
                `https://api.woerterbuchnetz.de/open-api/dictionaries/${sigle}/lemmata/${lookupForm}`,
                { signal: AbortSignal.timeout(10000) }
            );
            // 4xx (kein Eintrag) ist ein echtes, cachebares Ergebnis;
            // 5xx ist transient und darf nicht memoisiert werden.
            if (!r.ok) return { sigle, entries: [], failed: r.status >= 500 };
            const data = await r.json();
            // Deduplizierung pro Wörterbuch, nicht global: derselbe Deep-Link
            // in zwei Wörterbüchern sind zwei verschiedene Artikel, derselbe
            // Deep-Link zweimal in einem Wörterbuch ist ein Duplikat.
            const seen = new Set();
            const entries = [];
            for (const e of data.result_set || []) {
                if (!isSafeLink(e.wbnetzlink) || seen.has(e.wbnetzlink)) continue;
                seen.add(e.wbnetzlink);
                entries.push(e);
            }
            return { sigle, entries, failed: false };
        } catch (e) {
            console.warn(`[Woerterbuchnetz] ${sigle} API unavailable:`, e.message);
            return { sigle, entries: [], failed: true };
        }
    })).then(results => {
        // Degradierte Antworten (Timeout, Netzfehler, 5xx) aus dem Cache
        // entfernen — sonst bleibt das Wörterbuch für diese Form die ganze
        // Session leer und erholt sich nie (#167 Finding 13).
        if (results.some(r => r.failed)) entryCache.delete(normalizedForm);
        return results.map(({ sigle, entries, failed }) => ({ sigle, entries, failed: !!failed }));
    });
    entryCache.set(normalizedForm, promise);
    return promise;
}
