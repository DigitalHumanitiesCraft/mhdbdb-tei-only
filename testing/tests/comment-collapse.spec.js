/**
 * Lange Lexikonkommentare lassen sich einklappen (#554, KZW 16.10.2026)
 *
 * KZW: "Lange Kommentare müssen eingeklappt werden können. Besonders bei wîn,
 * klamirre und brâte sieht man, dass die Felder teilweise viel zu lang sind."
 *
 * Der Index liefert das Orakel: welche Kommentare über der Schwelle liegen,
 * steht dort, nicht als Konstante in der Spec. Geprüft wird auf der Lemmaseite
 * und im Lemma-Explorer des Playgrounds, den beiden Stellen, die Kommentare
 * zeigen (assets/js/lib/collapsible-text.js).
 *
 * Relative Pfade gegen baseURL, kein fester Port (#465).
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { gunzipSync } from 'zlib';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { COLLAPSE_MIN_CHARS } from '../../assets/js/lib/collapsible-text.js';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const auth = JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', 'authority-index.json.gz'))).toString('utf-8'));

const BEISPIELE = ['lemma_7532', 'lemma_12317', 'lemma_828']; // wîn, klamirre, brâte

const kommentarVon = id => auth.lemmata.find(l => l.id === id)?.senses?.find(s => s.comment)?.comment;
const lang = BEISPIELE.map(id => ({ id, lemma: auth.lemmata.find(l => l.id === id)?.lemma, text: kommentarVon(id) }));
// Ein Lemma, dessen Kommentare alle unter der Schwelle liegen
const kurz = (() => {
    const l = auth.lemmata.find(x => (x.senses || []).some(s => s.comment)
        && x.senses.every(s => !s.comment || s.comment.length <= COLLAPSE_MIN_CHARS));
    return { id: l.id, lemma: l.lemma };
})();

async function lemmaSeite(page, id) {
    await page.goto(`/lemma/?id=${id.replace('lemma_', '')}`);
    await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
}

/** Knopf, Text und Messwerte der ersten gekürzten Stelle in `bereich`. */
async function pruefeEinklappen(page, bereich, text) {
    const knopf = bereich.locator('.clamp-toggle').first();
    const kommentar = bereich.locator('.clamp-text').first();
    await expect(knopf).toHaveText('Weiterlesen');
    await expect(knopf).toHaveAttribute('aria-expanded', 'false');
    await expect(kommentar).toHaveClass(/clamp-collapsed/);
    // Gekürzt heißt: es ist mehr da, als sichtbar ist, und alles bleibt im DOM
    expect(await kommentar.evaluate(el => el.scrollHeight > el.clientHeight)).toBe(true);
    await expect(kommentar).toContainText(text.slice(-40));

    await knopf.click();
    await expect(knopf).toHaveText('Weniger anzeigen');
    await expect(knopf).toHaveAttribute('aria-expanded', 'true');
    await expect(kommentar).not.toHaveClass(/clamp-collapsed/);
    expect(await kommentar.evaluate(el => el.scrollHeight <= el.clientHeight + 1)).toBe(true);

    await knopf.click();
    await expect(kommentar).toHaveClass(/clamp-collapsed/);
    await expect(knopf).toHaveAttribute('aria-expanded', 'false');
}

test.describe('Einklappen langer Kommentare (#554)', () => {
    test('Orakel: die drei Beispiele von KZW liegen über der Schwelle, der Kontrollfall darunter', () => {
        for (const b of lang) {
            expect(b.text, `${b.id}: Kommentar im Index`).toBeTruthy();
            expect(b.text.length, `${b.id} ${b.lemma}`).toBeGreaterThan(COLLAPSE_MIN_CHARS);
        }
        expect(kurz.id).toBeTruthy();
    });

    for (const b of lang) {
        test(`Lemmaseite: ${b.id} klappt auf und zu`, async ({ page }) => {
            await lemmaSeite(page, b.id);
            await pruefeEinklappen(page, page.locator('#sensesContent'), b.text);
        });
    }

    // Julia, 19.10.2026: "beim Einklappen wieder nach oben geworfen", sonst hängt man im Footer.
    // Der Test stellt die Seite so, dass der Kommentaranfang `abstand` Pixel unter dem
    // oberen Rand des Fensters steht (negativ: darüber), klickt "Weniger anzeigen" und
    // liefert Anfang und Scrollposition davor und danach.
    async function zuklappenBei(page, abstand) {
        // Polster, damit der Browser die Scrollposition nach dem Zuklappen nicht selbst
        // auf die kürzere Seite zurückstutzt und so eine Verschiebung vortäuscht.
        await page.evaluate(() => { document.body.style.paddingBottom = '3000px'; });
        const wrap = page.locator('#sensesContent .clamp-wrap').first();
        const knopf = wrap.locator('.clamp-toggle');
        await knopf.click();
        await expect(knopf).toHaveText('Weniger anzeigen');
        await wrap.evaluate((el, a) => window.scrollBy(0, el.getBoundingClientRect().top - a), abstand);
        // Vorbedingung (#653): der Knopf muss ganz im Fenster liegen. Sonst scrollt
        // Playwrights click() ihn vorher ins Bild, der Kommentaranfang rutscht nach
        // oben, und die App springt zu Recht. So im Nachtlauf vom 05.11.2026 bei
        // 1600 px Fensterhoehe (Trace: scrollY 168, nach dem Autoscroll 1082, danach 288).
        const imFenster = await knopf.evaluate(el => {
            const r = el.getBoundingClientRect();
            return r.top >= 0 && r.bottom <= window.innerHeight;
        });
        expect(imFenster, 'Knopf vor dem Zuklappen ganz im Fenster').toBe(true);
        const messen = () => wrap.evaluate(el => ({ top: el.getBoundingClientRect().top, y: window.scrollY }));
        const davor = await messen();
        await knopf.click();
        await expect(knopf).toHaveText('Weiterlesen');
        return { davor, danach: await messen() };
    }

    // Hoch genug, dass der aufgeklappte Kommentar samt Knopf auch mit den Schriften
    // des CI-Runners ins Fenster passt (#653); die Vorbedingung oben prueft das.
    const FENSTER = { width: 1280, height: 2600 };

    test('Lemmaseite: Zuklappen springt an den Kommentaranfang, wenn er oberhalb liegt (#554)', async ({ page }) => {
        await page.setViewportSize(FENSTER);
        await lemmaSeite(page, lang[0].id);
        const { davor, danach } = await zuklappenBei(page, -40);
        expect(davor.top).toBeLessThan(0);
        // Im Fenster und unterhalb der festen Kopfleiste
        const kopf = await page.locator('header').first().evaluate(el => el.getBoundingClientRect().bottom);
        expect(danach.top).toBeGreaterThanOrEqual(kopf - 1);
        expect(danach.top).toBeLessThan(300);
    });

    test('Lemmaseite: Zuklappen verschiebt nichts, wenn der Anfang sichtbar ist (#554)', async ({ page }) => {
        await page.setViewportSize(FENSTER);
        await lemmaSeite(page, lang[0].id);
        const { davor, danach } = await zuklappenBei(page, 200);
        expect(davor.y).toBeGreaterThan(0);
        expect(danach.y).toBe(davor.y);
    });

    test('Lemmaseite: ein kurzer Kommentar bekommt keinen Knopf', async ({ page }) => {
        await lemmaSeite(page, kurz.id);
        await expect(page.locator('#sensesContent')).toContainText('Kommentar');
        await expect(page.locator('#sensesContent .clamp-toggle')).toHaveCount(0);
    });

    test('Lemmaseite: knapp über der Schwelle steht ein Knopf nur, wo wirklich gekürzt wird', async ({ page }) => {
        // Reviewrunde 1: die Nachmessung lief vor dem Aufdecken von #lemmaContent
        // (Höhe 0) und nahm nie einen Knopf zurück. Nur ein Text zwischen der
        // Schwelle und sechs vollen Zeilen unterscheidet beide Fälle.
        const l = auth.lemmata.find(x => (x.senses || []).some(
            s => s.comment && s.comment.length > COLLAPSE_MIN_CHARS && s.comment.length <= COLLAPSE_MIN_CHARS + 90));
        expect(l, 'kein Lemma mit Kommentar knapp über der Schwelle').toBeTruthy();
        await lemmaSeite(page, l.id);
        const texte = page.locator('#sensesContent .clamp-text');
        await expect(texte).toHaveCount(1);
        const knoepfe = await page.locator('#sensesContent .clamp-toggle').count();
        const gekuerzt = await texte.evaluate(el =>
            el.classList.contains('clamp-collapsed') && el.scrollHeight > el.clientHeight + 1);
        // Knopf und tatsächliche Kürzung gehören zusammen
        expect(knoepfe === 1, 'Knopf nur bei echter Kürzung').toBe(gekuerzt);
    });

    test('Lemma-Explorer im Playground: wîn klappt auf und zu', async ({ page }) => {
        const b = lang[0];
        // Über die ID, nicht über die Schreibform: "wîn" trifft 345 Lemmata, die
        // Liste zeigt 50, und wîn selbst steht nicht darunter (#545).
        await page.goto(`/playground/#lemmata&q=${encodeURIComponent(b.id)}`);
        await page.waitForFunction(
            () => window.playground?.authorityData?.lemmata?.length > 0, null, { timeout: 60000 });
        const knopf = page.locator(`#lemmaResults [onclick*="showLemmaSenses('${b.id}')"]`);
        await expect(knopf).toHaveCount(1, { timeout: 30000 });
        await knopf.click();
        await pruefeEinklappen(page, page.locator(`#senses-${b.id}`), b.text);
    });
});
