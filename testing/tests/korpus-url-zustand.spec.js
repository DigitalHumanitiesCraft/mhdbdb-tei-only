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
 *
 * Laufzeit (#564): Die Tests öffnen nie den ersten Treffer von "minne", das ist
 * ein Großtext (JT hat 44 MB), sondern den kleinsten Treffertext der ersten
 * Seite bzw. den kleinsten Text der Liste.
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

/**
 * Position des Treffertextes mit den wenigsten Wörtern unter den angezeigten
 * Karten, bevorzugt einer mit Autorzeile (der Test prüft, dass sie nach dem
 * Schließen wieder leer ist).
 */
async function kleinsteKarte(page) {
    return page.evaluate(() => {
        const karten = document.querySelectorAll('#resultsList > div').length;
        const angezeigt = window._mhdbdbApp.currentResults.slice(0, karten);
        const mitAutor = angezeigt.map((r, i) => i).filter(i => angezeigt[i].author);
        const kandidaten = mitAutor.length > 0 ? mitAutor : angezeigt.map((r, i) => i);
        return kandidaten.reduce((a, b) => (angezeigt[b].wordCount < angezeigt[a].wordCount ? b : a));
    });
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

        await page.locator('#resultsList > div').nth(await kleinsteKarte(page)).click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        await expect(page.locator('#readingAuthor')).not.toBeEmpty();

        expect(params(page).get('search')).toBe(SUCHE);
        expect(params(page).get('textId')).toBeTruthy();
        expect(await page.evaluate(() => history.length)).toBe(vorher + 1);

        // Browser-Zurück: Text zu, Suche und Trefferliste bleiben
        await page.goBack();
        await expect(page.locator('#readingTitle')).toBeEmpty({ timeout: 10000 });
        await expect(page.locator('#readingAuthor')).toBeEmpty();
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
        await page.locator('#resultsList > div').nth(await kleinsteKarte(page)).click();
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
        const karte = page.locator('#resultsList > div').nth(await kleinsteKarte(page));
        await karte.locator('[data-kwic-toggle]').click();
        const beleg = karte.locator('[data-position]').first();
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
        const klein = await page.evaluate(() => {
            const texte = window._mhdbdbApp.corpusData.texts.filter(t => t.wordCount > 0);
            return texte.reduce((a, b) => (b.wordCount < a.wordCount ? b : a)).id;
        });
        await page.locator(`#textList label[data-text-id="${klein}"] .icon-btn[title="Text lesen"]`).click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        expect(params(page).get('search')).toBeNull();
        expect(params(page).get('textId')).toBe(klein);

        await page.goBack();
        await expect(page.locator('#readingTitle')).toBeEmpty({ timeout: 10000 });
        await expect(page.locator('#readingAuthor')).toBeEmpty();
        expect(params(page).get('textId')).toBeNull();
    });

    test('Schließen während des Ladens öffnet das Panel nicht nachträglich', async ({ page }) => {
        test.setTimeout(180000);
        await suchen(page);

        // Öffnen und sofort schließen, noch bevor das TEI geladen ist; dann auf
        // das Ende genau dieses Ladevorgangs warten, nicht auf eine feste Zeit:
        // sonst wäre der Test auch ohne den Abbruch grün, solange das Laden
        // länger dauert als das Warten.
        const r = await page.evaluate(async () => {
            const app = window._mhdbdbApp;
            const reader = app.teiReader;
            const klein = app.corpusData.texts.filter(t => t.wordCount > 0)
                .reduce((a, b) => (b.wordCount < a.wordCount ? b : a)).id;
            const original = reader.loadTEIFile.bind(reader);
            let laden = null;
            reader.loadTEIFile = (datei) => (laden = original(datei));
            app.openText(klein, {});
            app.closeText();
            await laden;
            // das Zurückkehren des abgebrochenen openReadingView einen Takt abwarten
            await new Promise(res => setTimeout(res, 300));
            reader.loadTEIFile = original;
            return {
                geladen: laden !== null,
                titel: document.getElementById('readingTitle').textContent,
                autor: document.getElementById('readingAuthor').textContent,
                aktuell: reader.currentTextId
            };
        });

        expect(r.geladen).toBe(true);
        expect(r.titel).toBe('');
        expect(r.autor).toBe('');
        expect(r.aktuell).toBeNull();
        await expect(page.locator('#readingNavigation')).toBeHidden();
    });

    test('bricht die Suche nach Browser-Zurück ab (leere Textauswahl), zeigen Feld und Liste dieselbe Suche', async ({ page }) => {
        test.setTimeout(180000);
        await suchen(page);
        await page.locator('#resultsList > div').nth(await kleinsteKarte(page)).click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // zweite Suche überschreibt den Eintrag mit Text (replaceState)
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await expect.poll(() => params(page).get('search')).toBe('got');

        // Auswahl leeren, dann zurück: der Eintrag davor trägt ?search=minne und
        // ruft handleSearch auf, das mit leerer Auswahl abbricht
        await page.click('#selectNoneTexts');
        await page.goBack();
        await expect.poll(() => page.evaluate(() => window._mhdbdbApp.lastSearchTerm)).toBe('got');

        expect(await page.inputValue('#searchInput')).toBe('got');
        expect(params(page).get('search')).toBe('got');
    });

    test('Textauswahl und Ansicht bleiben außerhalb der Adresse', async ({ page }) => {
        await suchen(page);
        const vorher = page.url();

        await page.click('#selectNoneTexts');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList, #resultsTable', { timeout: 10000 });

        expect(page.url()).toBe(vorher);
        expect([...params(page).keys()]).toEqual(['search']);
    });

});
