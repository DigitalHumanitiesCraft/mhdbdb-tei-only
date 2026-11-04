/**
 * Sprung zu Vers in der Leseansicht (#655)
 *
 * Eine bloße Zahl springt in Texten mit eindeutiger Versnummer (ROL), "Abschnitt.Vers"
 * in Texten, deren Nummern sich wiederholen (PZ, NBB). In allen übrigen Texten
 * (mehrdeutig: AXR, CHH; ohne numerische Verse: ABG) ist das Feld ausgeblendet.
 * Die erwarteten Modi stammen aus der Messung über die 667 TEI-Dateien
 * (Klassen plain/div/section/keine, Stand 2026-11-04).
 */

import { test, expect } from '../warm-page.js';

test.describe('Sprung zu Vers (#655)', () => {

    test.setTimeout(120000);

    async function openText(page, sigle) {
        await page.goto(`/korpus.html?textId=${sigle}`);
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        // Kein Locator mit "oder": bei 9.000 Verszeilen prüft Playwright jeden Treffer einzeln
        await page.waitForFunction(
            () => document.getElementById('readingBody').textContent.trim().length > 100,
            null, { timeout: 90000 });
    }

    test('ROL: Zahl und Enter springen zum Vers', async ({ page }) => {
        await openText(page, 'ROL');
        const input = page.locator('#verseJumpInput');
        await expect(page.locator('#verseJumpForm')).toBeVisible();
        await expect(input).toHaveAttribute('placeholder', /^z\. B\. \d+$/);

        await input.fill('5579');
        await input.press('Enter');

        const ziel = page.locator('#readingBody .verse-line[data-n="5579"]');
        await expect(ziel).toHaveCount(1);
        await expect(ziel).toBeInViewport();
        await expect(page.locator('#verseJumpMessage')).toHaveText('');
    });

    test('ROL: Button springt ebenso, ein fehlender Vers wird gemeldet', async ({ page }) => {
        await openText(page, 'ROL');
        const input = page.locator('#verseJumpInput');
        const message = page.locator('#verseJumpMessage');

        await input.fill('99999');
        await page.getByRole('button', { name: 'Springen' }).click();
        await expect(message).toHaveText('Vers 99999 gibt es in diesem Text nicht.');
        await expect(message).toHaveAttribute('aria-live', 'polite');

        await input.fill('100');
        await page.getByRole('button', { name: 'Springen' }).click();
        await expect(message).toHaveText('');
        await expect(page.locator('#readingBody .verse-line[data-n="100"]')).toBeInViewport();

        // Keine Zahl: Hinweis statt Sprung
        await input.fill('abc');
        await input.press('Enter');
        await expect(message).toContainText('Versnummer');
    });

    test('PZ: Abschnitt.Vers springt, eine bloße Zahl wird nicht angenommen', async ({ page }) => {
        await openText(page, 'PZ');
        const input = page.locator('#verseJumpInput');
        const message = page.locator('#verseJumpMessage');
        await expect(page.locator('#verseJumpForm')).toBeVisible();
        await expect(input).toHaveAttribute('placeholder', /^Abschnitt\.Vers, z\. B\. \d+\.\d+$/);

        const ziel = page.locator('#readingBody .tei-div[data-n="339"] .verse-line[data-n="26"]');
        await expect(ziel).toHaveCount(1);

        // Alle erlaubten Trenner führen auf dieselbe Stelle
        for (const eingabe of ['339.26', '339,26', '339:26', '339 26']) {
            await page.evaluate(() => window.scrollTo(0, 0));
            await input.fill(eingabe);
            await input.press('Enter');
            await expect(ziel, eingabe).toBeInViewport();
            await expect(message).toHaveText('');
        }

        // Bloße Zahl: im Parzival tragen rund 800 Verse <l n="26">
        await page.evaluate(() => window.scrollTo(0, 0));
        await input.fill('26');
        await input.press('Enter');
        await expect(message).toContainText('Abschnitt.Vers');
        await expect(ziel).not.toBeInViewport();

        // Abschnitt ohne diesen Vers
        await input.fill('339.99');
        await input.press('Enter');
        await expect(message).toHaveText('Abschnitt.Vers 339.99 gibt es in diesem Text nicht.');
    });

    test('NBB: Strophen-Zählung (lg) trägt Abschnitt.Vers', async ({ page }) => {
        await openText(page, 'NBB');
        const input = page.locator('#verseJumpInput');
        await expect(page.locator('#verseJumpForm')).toBeVisible();

        await input.fill('100.3');
        await input.press('Enter');
        const ziel = page.locator('#readingBody .verse-group[data-n="100"] .verse-line[data-n="3"]');
        await expect(ziel).toHaveCount(1);
        await expect(ziel).toBeInViewport();
    });

    test('mehrdeutige Texte (AXR, CHH) und Prosa ohne Versnummern (ABG): Feld ausgeblendet', async ({ page }) => {
        for (const sigle of ['AXR', 'CHH', 'ABG']) {
            await openText(page, sigle);
            await expect(page.locator('#verseJumpForm'), sigle).toBeHidden();
        }
    });

    test('Schließen des Texts (Browser-Zurück, #434) verbirgt das Feld', async ({ page }) => {
        await openText(page, 'ROL');
        const input = page.locator('#verseJumpInput');
        await input.fill('99999');
        await input.press('Enter');
        await expect(page.locator('#verseJumpMessage')).not.toHaveText('');

        // Derselbe Weg wie handlePopState: closeText() schließt das Panel
        await page.evaluate(() => window._mhdbdbApp.closeText());
        await expect(page.locator('#readingTitle')).toBeEmpty({ timeout: 10000 });
        await expect(page.locator('#verseJumpForm')).toBeHidden();
        await expect(page.locator('#verseJumpMessage')).toHaveText('');
        await expect(input).toHaveValue('');
    });

    test('Textwechsel setzt Feld und Meldung zurück', async ({ page }) => {
        await openText(page, 'ROL');
        const input = page.locator('#verseJumpInput');
        await input.fill('99999');
        await input.press('Enter');
        await expect(page.locator('#verseJumpMessage')).not.toHaveText('');

        // Zweiter Text in derselben Seite, wie beim Sigle-Link in den Metadaten.
        // Ein page.goto lüde ein neues Dokument und wäre ohne Reset genauso leer.
        const openInApp = (sigle) => page.evaluate(async (s) => {
            const app = window._mhdbdbApp;
            await app.teiReader.openReadingView(s, {}, app.elements);
        }, sigle);

        await openInApp('PZ');
        await expect(page.locator('#readingTitle')).not.toHaveText(/Rolandslied/i, { timeout: 90000 });
        await expect(page.locator('#verseJumpForm')).toBeVisible();
        await expect(input).toHaveValue('');
        await expect(page.locator('#verseJumpMessage')).toHaveText('');
        await expect(input).toHaveAttribute('placeholder', /^Abschnitt\.Vers/);

        // Wechsel zu einem Text ohne Versnummern verbirgt das Feld wieder
        await input.fill('339.99');
        await input.press('Enter');
        await expect(page.locator('#verseJumpMessage')).not.toHaveText('');
        await openInApp('ABG');
        await expect(page.locator('#verseJumpForm')).toBeHidden();
        await expect(page.locator('#verseJumpMessage')).toHaveText('');
    });

    test('Modus der reinen Funktion stimmt mit der Messung über die TEI-Dateien überein', async ({ page }) => {
        // Erwartung aus der Python-Klassifikation (plain/div/section/keine) je Text
        const erwartet = {
            ROL: 'plain', ALX: 'plain', PZ: 'div', WH: 'div', HUG: 'div',
            NBB: 'section', AXR: null, CHH: null, ABG: null
        };
        for (const [sigle, modus] of Object.entries(erwartet)) {
            await openText(page, sigle);
            const gemessen = await page.evaluate(async () => {
                const lib = await import('/assets/js/lib/verse-jump.js');
                return lib.buildVerseJumpIndex(document.getElementById('readingBody')).mode;
            });
            expect(gemessen, sigle).toBe(modus);
        }
    });

    test('classifyVerses: Grenzfälle', async ({ page }) => {
        await page.goto('/korpus.html');
        const r = await page.evaluate(async () => {
            const { classifyVerses } = await import('/assets/js/lib/verse-jump.js');
            return {
                leer: classifyVerses([]),
                plain: classifyVerses([{ n: '1', div: '', sec: '' }, { n: '2', div: '', sec: '' }]),
                div: classifyVerses([
                    { n: '1', div: 'a', sec: 'a' }, { n: '1', div: 'b', sec: 'b' }]),
                // gleiche Nummer, ein Vers ohne div: nicht eingebbar, also kein div-Modus
                divLuecke: classifyVerses([
                    { n: '1', div: 'a', sec: 'a' }, { n: '1', div: '', sec: 'x' }]),
                section: classifyVerses([
                    { n: '1', div: '', sec: 'x' }, { n: '1', div: '', sec: 'y' }]),
                mehrdeutig: classifyVerses([
                    { n: '1', div: 'a', sec: 'a' }, { n: '1', div: 'a', sec: 'a' }])
            };
        });
        expect(r).toEqual({
            leer: null, plain: 'plain', div: 'div', divLuecke: 'section',
            section: 'section', mehrdeutig: null
        });
    });
});
