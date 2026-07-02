/**
 * Shared Wörterbuchnetz API client (MWB + Lexer)
 *
 * Single implementation for the lemma pages (#73) and the korpus-search
 * lemma panel (#114) — see CONTRACTS.md §D.2. Was previously duplicated
 * in lemma/lemma-page.js and assets/js/app.js.
 *
 * - Results are memoized per normalized form for the session: dictionary
 *   content is static, repeat searches must not re-hit the external API.
 * - Entries whose deep-link is not http(s) are dropped — the link comes
 *   from an external API and goes straight into an href.
 */

const DICTIONARIES = ['MWB', 'Lexer'];

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
 * @returns {Promise<Array<{sigle: string, entries: Array}>>} — failures
 *   resolve to empty entry lists: the links are progressive enhancement
 *   and must never block or break the caller.
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
            if (!r.ok) return { sigle, entries: [] };
            const data = await r.json();
            const entries = (data.result_set || []).filter(e => isSafeLink(e.wbnetzlink));
            return { sigle, entries };
        } catch (e) {
            console.warn(`[Woerterbuchnetz] ${sigle} API unavailable:`, e.message);
            return { sigle, entries: [] };
        }
    }));
    entryCache.set(normalizedForm, promise);
    return promise;
}
