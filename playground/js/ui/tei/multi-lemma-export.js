/**
 * Export der Multi-Lemma-Suche als CSV und XLSX (#448)
 *
 * KZW am 2026-09-24 in #448: "eine Zeile je Fundstelle, mit Sigle, Titel,
 * Autor*in, genauer Stellenangabe und Belegkontext. Die aktuellen
 * Suchparameter und die Korpusauswahl sollen nachvollziehbar mitgeliefert
 * werden. Exportiert werden sollen alle Treffer der aktuellen Suche, nicht
 * nur die bis zu 50 angezeigten Fundstellen. Dass dafür die betroffenen
 * Texte nachgeladen werden müssen, ist in Ordnung; bitte Fortschritt
 * anzeigen."
 *
 * Was eine Fundstelle ist, haengt am Modus:
 *   - Naehe-Analyse und Im selben Vers: ein Treffer der Suche, also ein
 *     Fenster, in dem alle Lemmata vorkommen (nach der Dedup der Suche,
 *     tei-manager.js). Stelle sind die Verse/Zeilen der Belegwoerter.
 *   - Dokument-Suche: jeder einzelne Beleg jedes gesuchten Lemmas in den
 *     Texten, die alle Lemmata enthalten. Die Suche selbst liefert dort nur
 *     eine Zahl je Text; die Positionen kommen aus dem Korpus-Index.
 *
 * Stelle ist die Vers- oder Zeilennummer der Edition. In strophischen Texten
 * zaehlt sie je Abschnitt neu (BUH: <l n="12"> steht dort dreimal), deshalb steht
 * daneben die xml:id des Belegworts, die jede Stelle eindeutig macht.
 *
 * Wortlaut und Stellenangabe stehen nur im TEI, der Index traegt Lemma-IDs.
 * Jede betroffene Datei wird einmal geladen und ueber collectPositionTokens
 * (kwic-service.js) gelesen, das die Positionen nach CONTRACTS §B zaehlt wie
 * der Index. Zeigt eine Position im TEI auf ein anderes Lemma als im Index,
 * bricht der Export ab, statt eine falsche Zeile zu schreiben.
 */

import { collectPositionTokens, formatLineRef } from '../../../../assets/js/search/kwic-service.js';
import { lemmaRefMatchesId } from '../../../../assets/js/lib/lemma-match.js';
import { toCsv, downloadCsv, csvDateStamp, csvFilenamePart } from '../../../../assets/js/lib/csv-export.js';
import { toXlsx, downloadXlsx } from '../../../../assets/js/lib/xlsx-export.js';

const MODUS = {
    proximity: 'Nähe-Analyse',
    verse: 'Im selben Vers',
    document: 'Dokument-Suche'
};
const KONTEXT_WOERTER = 10;
const PARALLEL = 4;

/**
 * Was zum Zeitpunkt der Suche galt. executeSearch baut das Objekt, bevor
 * close() die Modalwerte zuruecksetzt; die Auswahl wird kopiert, weil sie
 * sich nach der Suche aendern kann.
 */
export function exportKontext({ mode, distance, searchTerms, lemmaIds, results = [] }) {
    const pg = window.playground;
    const texts = pg?.corpusData?.texts || [];
    return {
        mode,
        distance: mode === 'proximity' ? distance : null,
        searchTerms: [...searchTerms],
        lemmaIds: lemmaIds.map(id => `lemma_${String(id).replace(/^lemma_/, '')}`),
        results,
        auswahl: [...(pg?.corpusData?.includedTexts || [])].sort(),
        textZahl: texts.length,
        indexVersion: pg?.teiManager?.corpusIndex?.version || '',
        datum: csvDateStamp(),
        zeilen: null   // Cache: CSV und XLSX derselben Suche laden die Texte nur einmal
    };
}

function lemmaLabel(id) {
    const lemma = window.playground?.authorityManager?.findLemmaById(id);
    return lemma ? `${lemma.lemma} (${id})` : id;
}

function sucheText(ctx) {
    const modus = ctx.mode === 'proximity'
        ? `${MODUS.proximity}, max. ${ctx.distance} Wörter Abstand`
        : MODUS[ctx.mode];
    return `${modus}: ${ctx.lemmaIds.map(lemmaLabel).join(' + ')}`;
}

function auswahlText(ctx) {
    const n = ctx.auswahl.length;
    return n === ctx.textZahl
        ? `alle ${n} Texte`
        : `${n} von ${ctx.textZahl} Texten: ${ctx.auswahl.join(', ')}`;
}

function kopf(ctx) {
    if (ctx.mode === 'document') {
        return ['Sigle', 'Titel', 'Autor*in', 'Lemma', 'Stelle', 'Wort-ID', 'Kontext davor', 'Beleg', 'Kontext danach', 'Suche', 'Korpusauswahl'];
    }
    const k = ['Sigle', 'Titel', 'Autor*in', 'Stelle', 'Wort-IDs', 'Belegwörter', 'Kontext'];
    if (ctx.mode === 'proximity') k.push('Abstand (Wörter)');
    return [...k, 'Suche', 'Korpusauswahl'];
}

/** Verse/Zeilen der Positionen, doppelte zusammengefasst, in Textfolge. */
function stelle(positions, tei) {
    const refs = [];
    for (const p of positions) {
        const r = formatLineRef(tei.positions[p]?.lineRef);
        if (r && !refs.includes(r)) refs.push(r);
    }
    return refs.join(', ');
}

function pruefePosition(tei, p, lemmaId, datei) {
    const eintrag = tei.positions[p];
    if (!eintrag) {
        throw new Error(`${datei}: Position ${p} fehlt im TEI (${tei.positions.length} Positionen). Index und TEI passen nicht zusammen.`);
    }
    if (lemmaId && !lemmaRefMatchesId(eintrag.lemmaRef, lemmaId)) {
        throw new Error(`${datei}: Position ${p} traegt im TEI ${eintrag.lemmaRef}, im Index ${lemmaId}.`);
    }
    return eintrag;
}

function zeilenFensterModus(ctx, text, tei, treffer, meta) {
    const hits = treffer
        .map(t => ({ t, erste: Math.min(...t.matchPositions) }))
        .sort((a, b) => a.erste - b.erste);
    return hits.map(({ t }) => {
        const pos = [...t.matchPositions].sort((a, b) => a - b);
        for (const p of pos) {
            const e = pruefePosition(tei, p, null, text.filename);
            if (!ctx.lemmaIds.some(id => lemmaRefMatchesId(e.lemmaRef, id))) {
                throw new Error(`${text.filename}: Position ${p} traegt im TEI ${e.lemmaRef}, keines der gesuchten Lemmata.`);
            }
        }
        const von = pruefePosition(tei, t.contextStart, null, text.filename).tokenIndex;
        const bis = pruefePosition(tei, Math.max(t.contextStart, t.contextEnd - 1), null, text.filename).tokenIndex;
        const zeile = [
            ...meta,
            stelle(pos, tei),
            pos.map(p => tei.positions[p].xmlId).join(' / '),
            pos.map(p => tei.tokens[tei.positions[p].tokenIndex]).join(' / '),
            tei.tokens.slice(von, bis + 1).join(' ')
        ];
        if (ctx.mode === 'proximity') zeile.push(t.distance);
        return zeile;
    });
}

function zeilenDokumentModus(ctx, text, tei, meta) {
    const belege = [];
    for (const id of ctx.lemmaIds) {
        // Beide Schluesselformen wie in searchDocumentUsingEnhancedIndex
        const liste = text.lemmata?.[id] || text.lemmata?.[id.replace(/^lemma_/, '')] || [];
        for (const p of liste) belege.push({ id, p });
    }
    belege.sort((a, b) => a.p - b.p);
    return belege.map(({ id, p }) => {
        const e = pruefePosition(tei, p, id, text.filename);
        return [
            ...meta,
            lemmaLabel(id),
            formatLineRef(e.lineRef),
            e.xmlId,
            tei.tokens.slice(Math.max(0, e.tokenIndex - KONTEXT_WOERTER), e.tokenIndex).join(' '),
            tei.tokens[e.tokenIndex],
            tei.tokens.slice(e.tokenIndex + 1, e.tokenIndex + 1 + KONTEXT_WOERTER).join(' ')
        ];
    });
}

async function ladeTei(filename) {
    const antwort = await fetch(`../tei/${encodeURIComponent(filename)}`);
    if (!antwort.ok) throw new Error(`${filename}: HTTP ${antwort.status}`);
    const doc = new DOMParser().parseFromString(await antwort.text(), 'application/xml');
    if (doc.querySelector('parsererror')) throw new Error(`${filename}: TEI nicht lesbar`);
    return collectPositionTokens(doc);
}

/**
 * Alle Zeilen der Suche, Texte parallel nachgeladen.
 * @param {object} ctx aus exportKontext
 * @param {(fertig: number, gesamt: number) => void} fortschritt
 */
export async function exportZeilen(ctx, fortschritt = () => {}) {
    if (ctx.zeilen) return ctx.zeilen;
    const texte = new Map((window.playground?.corpusData?.texts || []).map(t => [t.filename, t]));
    const jeDatei = new Map();
    for (const r of ctx.results) {
        if (!texte.has(r.filename)) throw new Error(`${r.filename}: nicht im Korpus-Index`);
        if (!jeDatei.has(r.filename)) jeDatei.set(r.filename, []);
        jeDatei.get(r.filename).push(r);
    }
    const dateien = [...jeDatei.keys()];
    const ergebnis = new Map();
    let fertig = 0;
    fortschritt(0, dateien.length);

    // Promise.all bricht die anderen Arbeiter nicht ab. Ohne das Flag laden
    // sie nach dem ersten Fehler weiter und ueberschreiben mit ihrem
    // Fortschritt die Fehlermeldung (Review #448).
    let abgebrochen = false;
    let naechste = 0;
    async function arbeiter() {
        while (!abgebrochen && naechste < dateien.length) {
            const datei = dateien[naechste++];
            try {
                const text = texte.get(datei);
                const tei = await ladeTei(datei);
                if (abgebrochen) return;
                const meta = [text.id, text.title || '', text.author || ''];
                ergebnis.set(datei, ctx.mode === 'document'
                    ? zeilenDokumentModus(ctx, text, tei, meta)
                    : zeilenFensterModus(ctx, text, tei, jeDatei.get(datei), meta));
            } catch (error) {
                abgebrochen = true;
                throw error;
            }
            fortschritt(++fertig, dateien.length);
        }
    }
    await Promise.all(Array.from({ length: Math.min(PARALLEL, dateien.length) }, arbeiter));

    // Reihenfolge wie in der Ergebnisliste, nicht wie die Downloads fertig wurden
    const suche = sucheText(ctx);
    const auswahl = auswahlText(ctx);
    ctx.zeilen = dateien.flatMap(d => ergebnis.get(d)).map(z => [...z, suche, auswahl]);
    return ctx.zeilen;
}

function dateiname(ctx, endung) {
    return `mhdbdb-multilemma-${ctx.mode}-${csvFilenamePart(ctx.searchTerms.join('-'))}-${ctx.datum}.${endung}`;
}

export async function exportCsv(ctx, fortschritt) {
    const zeilen = await exportZeilen(ctx, fortschritt);
    downloadCsv(dateiname(ctx, 'csv'), toCsv(kopf(ctx), zeilen));
    return zeilen.length;
}

export async function exportXlsx(ctx, fortschritt) {
    const zeilen = await exportZeilen(ctx, fortschritt);
    // Blatt 1 traegt dieselben Spalten wie die CSV; Blatt 2 sagt dasselbe
    // ueber die Suche noch einmal lesbar, eine Angabe je Zeile.
    const suche = [
        ['Suchmodus', MODUS[ctx.mode]],
        ...(ctx.mode === 'proximity' ? [['Maximaler Abstand (Wörter)', ctx.distance]] : []),
        ['Eingabe', ctx.searchTerms.join(' + ')],
        ['Lemmata', ctx.lemmaIds.map(lemmaLabel).join(' + ')],
        ['Ausgewählte Texte', `${ctx.auswahl.length} von ${ctx.textZahl}`],
        ['Sigeln der Auswahl', ctx.auswahl.length === ctx.textZahl ? 'alle' : ctx.auswahl.join(', ')],
        ['Fundstellen', zeilen.length],
        ['Korpus-Index', ctx.indexVersion],
        ['Exportiert am', ctx.datum],
        ['Quelle', 'MHDBDB, https://dhcraft.org/mhdbdb-tei-only/ (CC BY-NC-SA 4.0)']
    ];
    downloadXlsx(dateiname(ctx, 'xlsx'), toXlsx([
        { name: 'Fundstellen', header: kopf(ctx), rows: zeilen },
        { name: 'Suche', header: ['Angabe', 'Wert'], rows: suche }
    ]));
    return zeilen.length;
}
