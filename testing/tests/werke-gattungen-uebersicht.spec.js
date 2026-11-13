/**
 * Werke-Explorer: Gattungen in der Trefferübersicht (#495)
 *
 * Es gibt keine Haupt- und Nebengattungen. Die Übersicht nennt die erste
 * Gattung und zählt die übrigen ("(+2 weitere Gattungen)"); die vollständige
 * Liste steht in der Detailansicht. Gemessen an authority-index.json.gz:
 *
 *   work_350  Aalener Stadtratsgedicht   1 Gattung  (Kleindidaxe)
 *   work_478  Abriss der böhmischen Geschichte  2 Gattungen
 *   work_6    Frauendienst               3 Gattungen
 */

import { test, expect } from '@playwright/test';

async function searchWork(page, term, workId) {
    await page.fill('#workSearch', term);
    const item = page.locator('#workResults .result-item', { hasText: `ID: ${workId}` });
    await expect(item).toHaveCount(1, { timeout: 10000 });
    return item;
}

test.describe('Werke-Explorer: Gattungen in der Übersicht (#495)', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });
        await page.click('button:has-text("Werke anzeigen")');
        await page.waitForSelector('#workSearch', { timeout: 5000 });
    });

    test('eine Gattung: ohne Zusatz', async ({ page }) => {
        const item = await searchWork(page, 'Aalener Stadtratsgedicht', 'work_350');
        await expect(item).toContainText('Kleindidaxe');
        await expect(item).not.toContainText('weitere Gattung');
    });

    test('zwei Gattungen: "(+1 weitere Gattung)" im Singular', async ({ page }) => {
        const item = await searchWork(page, 'Abriss der böhmischen Geschichte', 'work_478');
        await expect(item).toContainText('Lokalchronik, Territorialchronik und Herrschaftschronik (+1 weitere Gattung)');
        await expect(item).not.toContainText('weitere Gattungen');
    });

    test('drei Gattungen: "(+2 weitere Gattungen)", Details nennen alle', async ({ page }) => {
        const item = await searchWork(page, 'Frauendienst', 'work_6');
        await expect(item).toContainText('Liebesroman und Abenteuerroman (+2 weitere Gattungen)');
        await item.locator('button:has-text("Details anzeigen")').click();
        const details = item.locator('#details-work_6');
        await expect(details).toContainText('Liebesroman und Abenteuerroman');
        await expect(details).toContainText('Minnesang');
        await expect(details).toContainText('Brief');
        await expect(details).not.toContainText('weitere Gattung');
    });
});
