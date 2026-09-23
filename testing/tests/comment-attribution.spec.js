/**
 * Urheberangabe am kuratierten Kommentar (#270, ADR-018 Revision 23.09.2026)
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

test.describe('Urheberangabe am kuratierten Kommentar (#270)', () => {
    test('der Index traegt zu jedem commentResp einen Namen', () => {
        // Kontrollwert: Abba traegt seit 2026-07-30 einen Kommentar. Fehlt
        // er hier, liest das Orakel den falschen Index oder das falsche Feld.
        expect(kommentare.map(k => k.id)).toContain('lemma_37818');
        for (const k of kommentare) {
            expect(k.name, `${k.id} ${k.resp}`).toBeTruthy();
        }
        // Nur Kommentare bekommen einen Namen: definitionResp und origin.resp
        // bleiben unaufgeloest, bis #270 das fuer <def> und <etym> entscheidet.
        const fremd = auth.lemmata.filter(l =>
            (l.origin && 'respName' in l.origin) ||
            (l.senses || []).some(s => 'definitionRespName' in s));
        expect(fremd).toEqual([]);
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

    test('der Lemma-Explorer im Playground nennt denselben Urheber', async ({ page }) => {
        for (const k of kommentare) {
            await page.goto(`/playground/#lemmata&q=${encodeURIComponent(k.lemma.toLowerCase())}`);
            await page.waitForFunction(
                () => window.playground?.authorityData?.lemmata?.length > 0, null, { timeout: 60000 });
            // Die Bedeutungen stehen erst nach "Bedeutungen anzeigen" auf der
            // Trefferkarte dieses Lemmas, nicht in der Trefferliste selbst.
            const knopf = page.locator(`#lemmaResults [onclick*="showLemmaSenses('${k.id}')"]`);
            await expect(knopf).toHaveCount(1, { timeout: 30000 });
            await knopf.click();
            await expect(page.getByText(`Kommentar von ${k.name}:`)).toBeVisible({ timeout: 30000 });
        }
    });
});
