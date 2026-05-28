// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Issue #114: Tabellenansicht für Korpussuche', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        await page.waitForFunction(() => window._mhdbdbApp?.searchEngine !== null, { timeout: 30000 });
        // Default-View zurücksetzen, damit Tests reproduzierbar starten
        await page.evaluate(() => localStorage.removeItem('mhdbdb-results-view'));
    });

    test('Toggle UI ist sichtbar nach Suche', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await expect(page.locator('#viewToggleList')).toBeVisible();
        await expect(page.locator('#viewToggleTable')).toBeVisible();
    });

    test('Toggle Liste auf Tabelle wechselt das Rendering', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        // Initial: Listenansicht (Cards), keine Tabelle
        await expect(page.locator('#resultsList table')).toHaveCount(0);

        // Toggle auf Tabelle
        await page.click('#viewToggleTable');
        await expect(page.locator('#resultsList table')).toHaveCount(1);
        // 140 Treffer für "minne" — passe an, falls Korpus wächst
        await expect(page.locator('#resultsList table tbody tr')).toHaveCount(140);
    });

    test('localStorage persistiert View-Wahl über Reload', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');

        // Reload und erneut suchen
        await page.reload();
        await page.waitForFunction(() => window._mhdbdbApp?.searchEngine !== null);
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        await expect(page.locator('#resultsList table')).toHaveCount(1);
    });

    test('Sortierung per Header-Klick funktioniert', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        // Default: matchCount desc; JT (612 Treffer) sollte oben sein
        const firstRowSigle = await page.locator('#resultsList tbody tr').first().locator('.font-mono').textContent();
        expect(firstRowSigle?.trim()).toMatch(/^JT$/);

        // Klick Titel-Header und prüfe absteigende Sortierung
        await page.click('button[data-sort-col="title"]');
        const titlesAfterSort = await page.locator('#resultsList tbody tr td:first-child').allTextContents();
        const trimmed = titlesAfterSort.map(t => t.replace(/\s+/g, ' ').trim());
        const sortedDesc = [...trimmed].sort((a, b) => b.localeCompare(a, 'de'));
        expect(trimmed.slice(0, 5)).toEqual(sortedDesc.slice(0, 5));
    });

    test('Row-Klick öffnet Reader und wechselt auf Listen-Modus', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        await page.click('#resultsList tbody tr:first-child');

        // viewMode wechselt auf list
        await page.waitForFunction(() => window._mhdbdbApp.viewMode === 'list', { timeout: 5000 });
        const viewMode = await page.evaluate(() => window._mhdbdbApp.viewMode);
        expect(viewMode).toBe('list');

        // localStorage bleibt 'table' (Spec-Verhalten)
        const stored = await page.evaluate(() => localStorage.getItem('mhdbdb-results-view'));
        expect(stored).toBe('table');
    });

    test('CSV-Download wird angeboten', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        const downloadPromise = page.waitForEvent('download');
        await page.click('#resultsDownloadBtn');
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/^mhdbdb-suche-minne-\d{4}-\d{2}-\d{2}\.csv$/);
    });
});
