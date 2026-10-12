/**
 * Fundstellen einer Trefferkarte der Dokumentsuche (#58)
 *
 * KZW am 2026-10-12 in #58, Variante a + c: eine Trefferkarte laesst sich
 * aufklappen, darunter stehen die Fundstellen mit kurzem Kontext und
 * hervorgehobenem Suchwort, jede fuehrt an ihre Stelle in der Leseansicht.
 * Dazu kommt "Gesamten Text öffnen" mit allen gesuchten Lemmata hervorgehoben,
 * und bei mehreren Lemmata bleiben die Belege je Lemma erkennbar.
 *
 * Die Positionen kommen aus dem Korpus-Index (text.lemmata[id], eine Liste je
 * Lemma), Wortlaut und Stellenangabe aus dem TEI. Das TEI wird erst beim
 * Aufklappen geladen und ueber ladeTei/collectPositionTokens gelesen, das nach
 * CONTRACTS §B zaehlt wie der Index; derselbe Weg wie im Export (#448). Zeigt
 * eine Position im TEI auf ein anderes Lemma als im Index, wirft
 * pruefePosition, und die Karte meldet den Fehler, statt eine falsche
 * Fundstelle zu verlinken.
 *
 * Die Lemmata bleiben die IDs, mit denen gesucht wurde. Eine erneute
 * Aufloesung ueber die Schreibform wuerde bei Homographen (arm: lemma_285
 * und lemma_286) still das andere Lemma zeigen.
 */

import { formatLineRef } from '../../../../assets/js/search/kwic-service.js';
import { LEMMA_COLORS } from '../core/ui-helpers.js';
import { ladeTei, pruefePosition } from './multi-lemma-export.js';

/** Hoechstens so viele Fundstellen je Lemma und Karte, wie die Naehe-Suche je Karte zeigt. */
export const BELEGE_JE_LEMMA = 50;
const KONTEXT_WOERTER = 8;

function kanonisch(id) {
    return `lemma_${String(id).replace(/^lemma_/, '')}`;
}

/** Positionsliste eines Lemmas im Index, beide Schluesselformen wie in searchDocumentUsingEnhancedIndex. */
export function indexPositionen(text, id) {
    const nackt = String(id).replace(/^lemma_/, '');
    return text?.lemmata?.[`lemma_${nackt}`] || text?.lemmata?.[nackt] || [];
}

/** Adresse der Leseansicht; ohne Position oeffnet sie den ganzen Text mit Hervorhebung. */
export function readerUrl(textId, lemmaIds, position = null) {
    const params = new URLSearchParams();
    params.set('textId', textId);
    params.set('lemmaIds', lemmaIds.map(id => String(id).replace(/^lemma_/, '')).join(','));
    if (position !== null && position !== undefined) params.set('position', String(position));
    return `../korpus.html?${params.toString()}`;
}

/**
 * Fundstellen je Lemma, in Suchreihenfolge der Lemmata und Textfolge der
 * Belege. Gekuerzt wird je Lemma, nicht ueber alle: sonst verdraengte ein
 * haeufiges Lemma ein seltenes ganz aus der Liste.
 *
 * @returns {Array<{lemmaId: string, slot: number, gesamt: number,
 *   belege: Array<{position: number, stelle: string, vor: string[],
 *   wort: string, nach: string[], vorSlots: number[], nachSlots: number[]}>}>}
 */
export function dokumentBelege(text, tei, lemmaIds, { max = BELEGE_JE_LEMMA, kontext = KONTEXT_WOERTER } = {}) {
    const ids = lemmaIds.map(kanonisch);

    // Tokenindex -> Farbslot fuer alle Belege aller gesuchten Lemmata, damit
    // ein zweites gesuchtes Lemma im Kontext in seiner Farbe erscheint.
    const slotJeToken = new Map();
    ids.forEach((id, slot) => {
        for (const p of indexPositionen(text, id)) {
            const e = tei.positions[p];
            if (e && !slotJeToken.has(e.tokenIndex)) slotJeToken.set(e.tokenIndex, slot);
        }
    });
    const slotsVon = (von, bis) => {
        const s = [];
        for (let i = von; i < bis; i++) s.push(slotJeToken.has(i) ? slotJeToken.get(i) : -1);
        return s;
    };

    return ids.map((id, slot) => {
        const positionen = [...indexPositionen(text, id)].sort((a, b) => a - b);
        const belege = positionen.slice(0, max).map(p => {
            const e = pruefePosition(tei, p, id, text.filename);
            const t = e.tokenIndex;
            const von = Math.max(0, t - kontext);
            const bis = Math.min(tei.tokens.length, t + 1 + kontext);
            return {
                position: p,
                stelle: formatLineRef(e.lineRef) || `Pos. ${p}`,
                vor: tei.tokens.slice(von, t),
                wort: tei.tokens[t],
                nach: tei.tokens.slice(t + 1, bis),
                vorSlots: slotsVon(von, t),
                nachSlots: slotsVon(t + 1, bis)
            };
        });
        return { lemmaId: id, slot, gesamt: positionen.length, belege };
    });
}

function farbe(slot) {
    return LEMMA_COLORS[slot % LEMMA_COLORS.length];
}

function lemmaName(id) {
    const lemma = window.playground?.authorityManager?.findLemmaById(id);
    return lemma?.lemma || id;
}

function kontextHtml(woerter, slots) {
    return woerter.map((w, i) => {
        const slot = slots[i];
        if (slot < 0) return escapeHtml(w);
        const c = farbe(slot);
        return `<span style="background-color: ${c.bg}; color: ${c.text}; padding: 0 2px; border-radius: 3px;">${escapeHtml(w)}</span>`;
    }).join(' ');
}

/** HTML der aufgeklappten Karte aus dem Ergebnis von dokumentBelege. */
export function dokumentBelegeHtml(gruppen, textId, lemmaIds) {
    const alle = lemmaIds.map(kanonisch);
    return gruppen.map(g => {
        const c = farbe(g.slot);
        const zahl = g.gesamt === 1 ? '1 Beleg' : `${g.gesamt} Belege`;
        const zeilen = g.belege.map(b => `
            <a class="detail-item beleg-link block" href="${escapeHtml(readerUrl(textId, alle, b.position))}" target="_blank" rel="noopener"
               data-position="${b.position}" data-lemma-id="${escapeHtml(g.lemmaId)}" title="In der Leseansicht an dieser Stelle öffnen">
                <div class="detail-meta">${escapeHtml(b.stelle)}</div>
                <div class="detail-snippet">${kontextHtml(b.vor, b.vorSlots)}
                    <mark class="beleg-wort" style="background-color: ${c.bg}; color: ${c.text}; border-bottom: 2px solid ${c.border}; padding: 1px 4px; border-radius: 3px; font-weight: 600;">${escapeHtml(b.wort)}</mark>
                    ${kontextHtml(b.nach, b.nachSlots)}</div>
            </a>`).join('');
        const gekuerzt = g.gesamt > g.belege.length
            ? `<p class="beleg-gekuerzt mt-2 text-xs text-slate-500">${g.belege.length} von ${g.gesamt} Belegen angezeigt. Alle zeigt „Gesamten Text öffnen“ hervorgehoben, der Export (CSV/XLSX) listet sie vollständig.</p>`
            : '';
        return `
        <section class="beleg-gruppe mb-4" data-lemma-id="${escapeHtml(g.lemmaId)}">
            <h5 class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-800">
                <span class="rounded px-1.5 py-0.5" style="background-color: ${c.bg}; color: ${c.text}; border-bottom: 2px solid ${c.border};">${escapeHtml(lemmaName(g.lemmaId))}</span>
                <span class="font-mono text-xs font-normal text-slate-500">${escapeHtml(g.lemmaId)}</span>
                <span class="beleg-zahl text-xs font-normal text-slate-600">${zahl}</span>
            </h5>
            <div class="space-y-2">${zeilen}</div>
            ${gekuerzt}
        </section>`;
    }).join('');
}

/**
 * Laedt das TEI einer Trefferkarte und liefert das HTML ihrer Fundstellen.
 * Aufgerufen erst beim ersten Aufklappen (displaySummaryResults, lazyDetails).
 */
export async function ladeDokumentBelege(filename, lemmaIds) {
    const text = (window.playground?.corpusData?.texts || []).find(t => t.filename === filename);
    if (!text) throw new Error(`${filename}: nicht im Korpus-Index`);
    const tei = await ladeTei(filename);
    return dokumentBelegeHtml(dokumentBelege(text, tei, lemmaIds), text.id, lemmaIds);
}

function escapeHtml(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, c => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
}
