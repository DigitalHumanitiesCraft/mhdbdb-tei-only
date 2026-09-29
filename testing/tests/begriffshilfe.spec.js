/**
 * Begriffshilfe (#498): Hilfeseite, Download und die Verweise aus dem Playground.
 *
 * Die Datei assets/downloads/mhdbdb-begriffshilfe.md wird von
 * scripts/build-begriffshilfe.py gebaut. Die Zahl der Tabellenzeilen wird gegen
 * die Zeile "Begriffe: N" der Datei selbst geprueft und nicht gegen eine feste
 * Zahl: das Begriffssystem waechst (#63).
 */

import { test, expect } from '@playwright/test';

test.describe('Begriffshilfe (#498)', () => {

    test('Hilfeseite laedt und bietet die Datei zum Herunterladen an', async ({ page }) => {
        await page.goto('/hilfe-begriffe-finden.html');
        await expect(page.locator('h1')).toBeVisible();

        const link = page.locator('a[href="assets/downloads/mhdbdb-begriffshilfe.md"]').first();
        await expect(link).toHaveAttribute('download', /.*/);

        const response = await page.request.get('/assets/downloads/mhdbdb-begriffshilfe.md');
        expect(response.status()).toBe(200);
        const text = await response.text();

        const declared = text.match(/^- Begriffe: (\d+)$/m);
        expect(declared, 'Zeile "Begriffe: N" fehlt').not.toBeNull();
        const rows = text.split('\n').filter(line => line.startsWith('| concept_'));
        expect(rows.length).toBe(Number(declared[1]));
        // Die Mitbegriff-Spalte ist der Teil, der im Test vom 29.09. den
        // Unterschied gemacht hat; ohne sie waere es die alte Variante A.
        expect(text).toContain('Häufigste Mitbegriffe');
    });

    test('Hilfe-Uebersicht verlinkt die Seite', async ({ page }) => {
        await page.goto('/hilfe.html');
        await expect(page.locator('a[href="hilfe-begriffe-finden.html"]').first()).toBeVisible();
    });

    test('Begriffe-Explorer verweist auf die Hilfeseite, auch bei null Treffern', async ({ page }) => {
        await page.goto('/playground/#concepts');
        await page.waitForSelector('#conceptSearch', { state: 'visible', timeout: 60000 });

        const underSearch = page.locator('#resultsContainer [data-begriffshilfe-link] a');
        await expect(underSearch.first()).toHaveAttribute('href', '../hilfe-begriffe-finden.html');

        await page.fill('#conceptSearch', 'Wachsamkeit');
        await expect(page.locator('#conceptResults')).toContainText('Keine Begriffe gefunden', { timeout: 15000 });
        await expect(page.locator('#conceptResults [data-begriffshilfe-link] a'))
            .toHaveAttribute('href', '../hilfe-begriffe-finden.html');
    });

    test('Begriffs-Verteilung verweist auf die Hilfeseite', async ({ page }) => {
        await page.goto('/playground/#concept-distribution');
        await page.waitForSelector('#cdQuery', { state: 'visible', timeout: 60000 });
        await expect(page.locator('[data-begriffshilfe-link] a').first())
            .toHaveAttribute('href', '../hilfe-begriffe-finden.html');
    });
});
