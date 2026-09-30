/**
 * Urheberangabe an kuratierten Angaben (#270, ADR-018 Revisionen 23.09. und 25.09.2026)
 *
 * KZW am 2026-09-23 in #270: "Die bereits gespeicherte Urheberangabe soll
 * direkt beim Kommentar sichtbar sein, auf der Lemma-Seite und im
 * Playground. Zum Beispiel: 'Kommentar von Katharina Zeppezauer-Wachauer'."
 *
 * Der Build loest sense.commentResp (contributors.xml#contrib_N) beim Bauen
 * zu sense.commentRespName auf. Das Orakel liest den Index von der Platte:
 * jeder Kommentar mit commentResp muss einen Namen tragen, und jeder Name
 * muss auf beiden Oberflaechen im Label stehen. Heute ist das genau ein
 * Kommentar (lemma_37818 Abba); die Tests verlangen die Menge nicht, nur
 * dass die Seite dem Index folgt.
 *
 * KZW am 2026-09-25: dieselbe Angabe auch bei Definition und
 * Herkunftserklaerung ("Definition von ...", "Herkunftserklärung von ...");
 * Index-Felder definitionRespName und origin.respName (1.9.15).
 *
 * Relative Pfade gegen baseURL, kein fester Port (#465).
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { gunzipSync } from 'zlib';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const auth = JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', 'authority-index.json.gz'))).toString('utf-8'));

/** Alle Kommentare mit Urheber: Lemma, Anzeigeform und aufgeloester Name. */
const kommentare = auth.lemmata.flatMap(l => (l.senses || [])
    .filter(s => s.comment && s.commentResp)
    .map(s => ({ id: l.id, lemma: l.lemma, resp: s.commentResp, name: s.commentRespName })));

/** Dasselbe fuer Definitionen und Herkunftserklaerungen (KZW 25.09.2026). */
const definitionen = auth.lemmata.flatMap(l => (l.senses || [])
    .filter(s => s.definition && s.definitionResp)
    .map(s => ({ id: l.id, lemma: l.lemma, resp: s.definitionResp, name: s.definitionRespName })));
const herkuenfte = auth.lemmata
    .filter(l => l.origin && l.origin.attribution && l.origin.resp)
    .map(l => ({ id: l.id, lemma: l.lemma, resp: l.origin.resp, name: l.origin.respName }));

test.describe('Urheberangabe am kuratierten Kommentar (#270)', () => {
    test('der Index traegt zu jedem commentResp einen Namen', () => {
        // Kontrollwert: Abba traegt seit 2026-07-30 einen Kommentar. Fehlt
        // er hier, liest das Orakel den falschen Index oder das falsche Feld.
        expect(kommentare.map(k => k.id)).toContain('lemma_37818');
        for (const k of kommentare) {
            expect(k.name, `${k.id} ${k.resp}`).toBeTruthy();
        }
    });

    test('der Index traegt zu jeder Definition und Herkunftserklaerung mit Urheber einen Namen', () => {
        // KZW 25.09.2026: dieselbe Angabe auch an <def> und <etym>. Kontrollwert
        // wie oben: Abba traegt beide mit @resp.
        expect(definitionen.map(d => d.id)).toContain('lemma_37818');
        expect(herkuenfte.map(h => h.id)).toContain('lemma_37818');
        for (const x of [...definitionen, ...herkuenfte]) {
            expect(x.name, `${x.id} ${x.resp}`).toBeTruthy();
        }
        // Ohne @resp kein Name: nichts wird aus Nachbarangaben uebernommen.
        const ohneResp = auth.lemmata.filter(l =>
            (l.origin && !l.origin.resp && 'respName' in l.origin) ||
            (l.senses || []).some(s => !s.definitionResp && 'definitionRespName' in s));
        expect(ohneResp).toEqual([]);
    });

    test('die Lemma-Seite nennt den Urheber von Definition und Herkunftserklaerung', async ({ page }) => {
        for (const d of definitionen) {
            await page.goto(`/lemma/?id=${d.id.replace('lemma_', '')}`);
            await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
            await expect(page.locator('#sensesContent')).toContainText(`Definition von ${d.name}`);
        }
        for (const h of herkuenfte) {
            await page.goto(`/lemma/?id=${h.id.replace('lemma_', '')}`);
            await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
            await expect(page.locator('#originContent')).toContainText(`Herkunftserklärung von ${h.name}`);
        }
    });

    test('die Lemma-Seite nennt den Urheber des Kommentars', async ({ page }) => {
        for (const k of kommentare) {
            const nummer = k.id.replace('lemma_', '');
            await page.goto(`/lemma/?id=${nummer}`);
            await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
            await expect(page.locator('#sensesContent')).toContainText(`Kommentar von ${k.name}`);
        }
    });

    test('ein Lemma ohne Kommentar zeigt kein Urheber-Label', async ({ page }) => {
        // lemma_879 ist ein unkuratiertes Lemma (in lemma-page.spec.js
        // benutzt); ein Label ohne Kommentar waere eine Zuschreibung ohne
        // Gegenstand.
        const lemma = auth.lemmata.find(l => l.id === 'lemma_879');
        expect((lemma.senses || []).some(s => s.comment)).toBe(false);
        await page.goto('/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#sensesContent')).not.toContainText('Kommentar von');
    });

    test('der Lemma-Explorer im Playground nennt dieselben Urheber', async ({ page }) => {
        // Je Lemma alle erwarteten Labels, jedes mit dem Namen seiner eigenen
        // Angabe: Definition und Kommentar koennen verschiedene Urheber haben,
        // und ein Lemma mit Definition muss keinen Kommentar tragen.
        const erwartet = new Map();
        const merke = (x, label) => {
            if (!erwartet.has(x.id)) erwartet.set(x.id, { lemma: x.lemma, labels: [] });
            erwartet.get(x.id).labels.push(`${label} von ${x.name}:`);
        };
        kommentare.forEach(k => merke(k, 'Kommentar'));
        definitionen.forEach(d => merke(d, 'Definition'));
        herkuenfte.forEach(h => merke(h, 'Herkunftserklärung'));

        for (const [id, { lemma, labels }] of erwartet) {
            await page.goto(`/playground/#lemmata&q=${encodeURIComponent(lemma.toLowerCase())}`);
            await page.waitForFunction(
                () => window.playground?.authorityData?.lemmata?.length > 0, null, { timeout: 60000 });
            // Die Bedeutungen stehen erst nach "Bedeutungen anzeigen" auf der
            // Trefferkarte dieses Lemmas, nicht in der Trefferliste selbst.
            const knopf = page.locator(`#lemmaResults [onclick*="showLemmaSenses('${id}')"]`);
            await expect(knopf).toHaveCount(1, { timeout: 30000 });
            await knopf.click();
            for (const label of labels) {
                await expect(page.getByText(label)).toBeVisible({ timeout: 30000 });
            }
        }
    });
});
