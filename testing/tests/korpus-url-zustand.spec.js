/**
 * URL-Zustand der Korpussuche und Browser-Zurück (#434)
 *
 * Die Suche setzt `?search=` per replaceState, das Öffnen eines Textes setzt
 * `?search=…&textId=…` (bei KWIC-Treffern mit `&position=…`) per pushState, ein
 * popstate-Handler schließt oder öffnet das Lesepanel. Textauswahl, Filter,
 * Seite und Sortierung stehen nicht in der Adresse.
 *
 * Alans Fall (#419, Testfall 6 und 15): Treffertext öffnen, Browser-Zurück,
 * und die Suche war weg.
 */

import { test, expect } from '@playwright/test';

const SUCHE = 'minne';

async function suchen(page, begriff = SUCHE) {
    await page.goto('/korpus.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    await page.fill('#searchInput', begriff);
    await page.click('#searchButton');
    await page.waitForSelector('#resultsList > div', { timeout: 20000 });
}

const params = page => new URL(page.url()).searchParams;

test.describe('Korpussuche: URL-Zustand und Browser-Zurück (#434)', () => {

    test('die Suche setzt ?search= ohne History-Eintrag', async ({ page }) => {
        await page.goto('/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        const vorher = await page.evaluate(() => history.length);

        await page.fill('#searchInput', SUCHE);
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 20000 });

        expect(params(page).get('search')).toBe(SUCHE);
        expect(params(page).get('textId')).toBeNull();
        expect(await page.evaluate(() => history.length)).toBe(vorher);
    });

    test('Text öffnen setzt textId per pushState, Browser-Zurück führt zur Trefferliste', async ({ page }) => {
        test.setTimeout(180000);
        await suchen(page);
        const vorher = await page.evaluate(() => history.length);

        await page.locator('#resultsList > div').first().click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        expect(params(page).get('search')).toBe(SUCHE);
        expect(params(page).get('textId')).toBeTruthy();
        expect(await page.evaluate(() => history.length)).toBe(vorher + 1);

        // Browser-Zurück: Text zu, Suche und Trefferliste bleiben
        await page.goBack();
        await expect(page.locator('#readingTitle')).toBeEmpty({ timeout: 10000 });
        expect(params(page).get('search')).toBe(SUCHE);
        expect(params(page).get('textId')).toBeNull();
        expect(await page.inputValue('#searchInput')).toBe(SUCHE);
        expect(await page.locator('#resultsList > div').count()).toBeGreaterThan(0);
        await expect(page.locator('#readingNavigation')).toBeHidden();

        // Browser-Vor: derselbe Text mit Hervorhebung
        await page.goForward();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        expect(params(page).get('textId')).toBeTruthy();
        await expect(page.locator('#readingNavigation')).toBeVisible({ timeout: 10000 });
    });

    test('Neuladen von korpus.html?search=minne zeigt die Treffer', async ({ page }) => {
        await suchen(page);
        const anzahl = await page.locator('#resultsList > div').count();

        await page.reload();
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await page.waitForSelector('#resultsList > div', { timeout: 20000 });

        expect(await page.inputValue('#searchInput')).toBe(SUCHE);
        expect(await page.locator('#resultsList > div').count()).toBe(anzahl);
        expect(params(page).get('search')).toBe(SUCHE);
    });

    test('die kopierte Adresse mit search und textId öffnet in einem neuen Tab Suche und Text', async ({ page, context }) => {
        test.setTimeout(180000);
        await suchen(page);
        await page.locator('#resultsList > div').first().click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        const titel = (await page.locator('#readingTitle').textContent()).trim();
        const adresse = page.url();

        const neu = await context.newPage();
        await neu.goto(adresse);
        await neu.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await neu.waitForSelector('#resultsList > div', { timeout: 20000 });
        await expect(neu.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        expect((await neu.locator('#readingTitle').textContent()).trim()).toBe(titel);
        expect(await neu.inputValue('#searchInput')).toBe(SUCHE);
        // Die Hervorhebung kommt aus den Treffern, die Adresse trägt keine lemmaIds
        await expect(neu.locator('#readingNavigation')).toBeVisible({ timeout: 10000 });
        // Die Adresse bleibt, wie sie übergeben wurde
        expect(neu.url()).toBe(adresse);
        await neu.close();
    });

    test('KWIC-Beleg öffnen setzt position in die Adresse', async ({ page }) => {
        test.setTimeout(180000);
        await suchen(page);
        await page.locator('#resultsList > div [data-kwic-toggle]').first().click();
        const beleg = page.locator('#resultsList > div [data-position]').first();
        await beleg.waitFor({ timeout: 20000 });
        const position = await beleg.getAttribute('data-position');
        await beleg.click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        expect(params(page).get('position')).toBe(position);
        expect(params(page).get('textId')).toBeTruthy();
    });

    test('ohne Suche: Text aus der Liste öffnen, Browser-Zurück schließt ihn', async ({ page }) => {
        test.setTimeout(180000);
        await page.goto('/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await page.locator('#textList button[title="Text lesen"], #textList .icon-btn[title="Text lesen"]').first().click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        expect(params(page).get('search')).toBeNull();
        expect(params(page).get('textId')).toBeTruthy();

        await page.goBack();
        await expect(page.locator('#readingTitle')).toBeEmpty({ timeout: 10000 });
        expect(params(page).get('textId')).toBeNull();
    });

    test('Schließen während des Ladens öffnet das Panel nicht nachträglich', async ({ page }) => {
        test.setTimeout(180000);
        await suchen(page);
        const textId = await page.evaluate(() => window._mhdbdbApp.currentResults[0].textId);

        // Öffnen und sofort schließen, noch bevor das TEI geladen ist
        await page.evaluate(id => {
            const app = window._mhdbdbApp;
            app.openText(id, {});
            app.closeText();
        }, textId);
        await page.waitForTimeout(5000);

        await expect(page.locator('#readingTitle')).toBeEmpty();
        await expect(page.locator('#readingNavigation')).toBeHidden();
        expect(await page.evaluate(() => window._mhdbdbApp.teiReader.currentTextId)).toBeNull();
    });

    test('Textauswahl, Seite und Sortierung bleiben außerhalb der Adresse', async ({ page }) => {
        await suchen(page);
        await page.click('#selectNoneTexts');
        await page.fill('#searchInput', SUCHE);
        const keys = [...params(page).keys()];
        expect(keys).toEqual(['search']);
    });

});
