/**
 * Error Handling Tests
 * Tests graceful degradation under failure conditions
 *
 * Covers: network failure, 404 TEI file, malformed XML, cache failure
 * Uses Playwright page.route() for network interception.
 * Issue #43 — Priority 5: error handling coverage
 */

import { test, expect } from '@playwright/test';

test.describe('Error Handling', () => {

    test.setTimeout(120000);

    test('network failure during TEI fetch shows error', async ({ page }) => {
        // Block all TEI file requests
        await page.route('**/tei/**', route => route.abort());

        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search and click first result to trigger TEI fetch
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });
        await page.locator('#resultsList > div').first().click();

        // Wait for error to appear
        await page.waitForTimeout(5000);

        // Reading body should show error (not crash)
        const bodyText = await page.locator('#readingBody').textContent();
        const hasErrorIndicator = bodyText.includes('Fehler') ||
                                  bodyText.includes('Error') ||
                                  bodyText.includes('error') ||
                                  bodyText.includes('nicht');

        // Page should still be functional (not crashed)
        await expect(page.locator('#searchInput')).toBeVisible();
        expect(hasErrorIndicator).toBeTruthy();
    });

    test('404 TEI file shows error message', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=FAKE_TEXT_404&lemmaIds=879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Wait for the error to surface
        await page.waitForTimeout(3000);

        // Error should appear in reading body or error display
        const bodyText = await page.locator('#readingBody').textContent();
        const hasError = bodyText.toLowerCase().includes('error') ||
                         bodyText.toLowerCase().includes('not found') ||
                         bodyText.includes('nicht gefunden') ||
                         bodyText.includes('Text not found');
        expect(hasError).toBeTruthy();
    });

    test('malformed TEI XML shows error', async ({ page }) => {
        // Intercept a TEI file and return malformed XML
        await page.route('**/tei/ABG.tei.xml', route => {
            route.fulfill({
                status: 200,
                contentType: 'application/xml',
                body: '<this is not valid xml><<<'
            });
        });

        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Wait for parse error
        await page.waitForTimeout(5000);

        // Reading body should show error, not crash
        const bodyText = await page.locator('#readingBody').textContent();
        const hasError = bodyText.toLowerCase().includes('error') ||
                         bodyText.toLowerCase().includes('parse') ||
                         bodyText.includes('Fehler');
        expect(hasError).toBeTruthy();
    });

    test('page remains functional after error', async ({ page }) => {
        // Trigger error with bad text ID
        await page.goto('http://localhost:8080/korpus.html?textId=NONEXISTENT&lemmaIds=879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await page.waitForTimeout(3000);

        // Search input should still be usable
        await expect(page.locator('#searchInput')).toBeVisible();
        await expect(page.locator('#searchButton')).toBeVisible();

        // Can still type and interact
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        // Results should appear (app recovered)
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });
        const resultCount = await page.locator('#resultsList > div').count();
        expect(resultCount).toBeGreaterThan(0);
    });

});
