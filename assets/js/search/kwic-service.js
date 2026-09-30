/**
 * KWIC Service (Issue #129)
 * Extracts keyword-in-context lines for lemma occurrences from a TEI document.
 *
 * Position counting mirrors CONTRACTS §B: only a <w> with @lemmaRef and
 * non-empty text content advances the position counter (parity with
 * build-corpus-index.py and tei-text-reader.js). The reported `position`
 * of each hit is therefore directly usable as `targetPosition` for
 * TEITextReader.openReadingView().
 */

import { lemmaRefMatchesId } from '../lib/lemma-match.js';

/**
 * Determine the line reference for a hit word.
 * Preference: enclosing <l n="..."> (edition verse number) over the last
 * preceding <lb n="..."> (prose line) over the last preceding <pb n="...">
 * (page, coarse fallback).
 *
 * @returns {{type: 'verse'|'line'|'page', n: string}|null}
 */
function lineRefFor(wordEl, lastLbN, lastPbN) {
    let anc = wordEl.parentElement;
    while (anc && anc.localName !== 'body') {
        if (anc.localName === 'l') {
            const n = anc.getAttribute('n');
            if (n) return { type: 'verse', n };
            break;
        }
        anc = anc.parentElement;
    }
    if (lastLbN) return { type: 'line', n: lastLbN };
    if (lastPbN) return { type: 'page', n: lastPbN };
    return null;
}

/**
 * One pass over the <body>: every readable word as a context token, and for
 * every counted position (CONTRACTS §B) its token index, @lemmaRef and line
 * reference. Shared by extractKwicHits and the multi-lemma export of the
 * playground (#448), which needs context windows spanning several lemmata.
 *
 * @param {Document} teiDoc - parsed TEI document
 * @returns {{tokens: string[], positions: Array<{tokenIndex: number,
 *            lemmaRef: string, lineRef: object|null, xmlId: string}>}}
 *          `positions[p]` belongs to §B position p.
 */
function collectPositionTokens(teiDoc) {
    const tokens = [];     // surface forms for context windows (annotated or not)
    const positions = [];  // index = §B position

    const body = teiDoc.querySelector('body');
    if (!body) return { tokens, positions };

    let lastLbN = null;
    let lastPbN = null;

    const doc = teiDoc.ownerDocument || teiDoc;
    const walker = doc.createTreeWalker(body, NodeFilter.SHOW_ELEMENT);

    let node = walker.nextNode();
    while (node) {
        const tag = node.localName;

        if (tag === 'lb') {
            const n = node.getAttribute('n');
            if (n) lastLbN = n;
        } else if (tag === 'pb') {
            const n = node.getAttribute('n');
            if (n) {
                lastPbN = n;
                lastLbN = null; // line numbering restarts page-wise where <lb> is used
            }
        } else if (tag === 'w') {
            const text = node.textContent.trim();
            if (text) {
                const lemmaRef = node.getAttribute('lemmaRef');

                // Running headers / surplus are real <w> in the TEI but not
                // readable context — keep them out of the window UNLESS they
                // are position-counted (then dropping them would break the
                // position↔token mapping; 0 such cases today).
                const inParatext = !lemmaRef && node.closest('fw, surplus') !== null;

                if (!inParatext) {
                    const tokenIndex = tokens.length;
                    tokens.push(text);
                    if (lemmaRef) {
                        positions.push({
                            tokenIndex,
                            lemmaRef,
                            lineRef: lineRefFor(node, lastLbN, lastPbN),
                            xmlId: node.getAttribute('xml:id') || ''
                        });
                    }
                }
            }
        }

        node = walker.nextNode();
    }

    return { tokens, positions };
}

/**
 * Extract KWIC hits for the given lemma IDs.
 *
 * @param {Document} teiDoc - parsed TEI document
 * @param {string[]} lemmaIds - lemma IDs to match (exact token match, §B.1)
 * @param {object} options
 * @param {number} options.contextWords - words of context per side (default 10)
 * @param {number} options.maxHits - cap on returned hits (default Infinity)
 * @returns {{hits: Array<{position: number, lineRef: object|null,
 *            before: string[], keyword: string, after: string[]}>, total: number}}
 */
function extractKwicHits(teiDoc, lemmaIds, { contextWords = 10, maxHits = Infinity } = {}) {
    const ids = (lemmaIds || []).filter(Boolean).map(id => id.toString());
    if (ids.length === 0) return { hits: [], total: 0 };

    const { tokens, positions } = collectPositionTokens(teiDoc);
    const rawHits = positions
        .map((p, position) => ({ ...p, position }))
        .filter(p => ids.some(id => lemmaRefMatchesId(p.lemmaRef, id)));

    const limited = (maxHits === Infinity) ? rawHits : rawHits.slice(0, maxHits);
    const hits = limited.map(h => ({
        position: h.position,
        lineRef: h.lineRef,
        before: tokens.slice(Math.max(0, h.tokenIndex - contextWords), h.tokenIndex),
        keyword: tokens[h.tokenIndex],
        after: tokens.slice(h.tokenIndex + 1, h.tokenIndex + 1 + contextWords)
    }));

    return { hits, total: rawHits.length };
}

/**
 * Format a lineRef for display.
 */
function formatLineRef(lineRef) {
    if (!lineRef) return '';
    switch (lineRef.type) {
        case 'verse': return `V. ${lineRef.n}`;
        case 'line': return `Z. ${lineRef.n}`;
        case 'page': return `S. ${lineRef.n}`;
        default: return '';
    }
}

export { collectPositionTokens, extractKwicHits, formatLineRef };
