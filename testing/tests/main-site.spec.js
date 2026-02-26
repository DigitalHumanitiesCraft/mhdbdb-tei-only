/**
 * Main Site Tests
 * Tests for the public-facing MHDBDB search page (korpus.html)
 *
 * Covers: loading, search, result cards, text list, reading view
 * Rewritten Feb 2026 to match current panel-based architecture (Issue #43)
 */

import { test, expect } from '@playwright/test';

test.describe('Main Site', () => {

    test.beforeEach(async ({ page }) => {
        // Navigate to search page (not landing page)
        await page.goto('http://localhost:8080/korpus.html');
    });

    test('should load without console errors', async ({ page }) => {
        const errors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                errors.push(msg.text());
            }
        });

        // Wait for loading screen to disappear
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        if (errors.length > 0) {
            console.error('Console errors:', errors);
        }
        expect(errors.length).toBe(0);
    });

    test('should display search page elements', async ({ page }) => {
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search controls
        await expect(page.locator('#searchInput')).toBeVisible();
        await expect(page.locator('#searchButton')).toBeVisible();

        // Text list with checkboxes
        await expect(page.locator('#textList')).toBeVisible();
        await expect(page.locator('#textFilter')).toBeVisible();

        // Reading panel (always present, right column)
        await expect(page.locator('#readingPanel')).toBeVisible();
    });

    test('should load indices successfully', async ({ page }) => {
        const logs = [];
        page.on('console', msg => {
            logs.push(msg.text());
        });

        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // App logs "[MainSiteApp] Ready" when fully initialized
        const readyLog = logs.some(log => log.includes('[MainSiteApp] Ready'));
        expect(readyLog).toBeTruthy();
    });

    test('should populate text list with corpus texts', async ({ page }) => {
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Text list should have checkboxes (one per corpus text)
        const textCount = await page.locator('#textList label').count();
        expect(textCount).toBeGreaterThan(100); // 666 texts expected

        // Selected text count should be displayed
        const selectedCount = await page.locator('#selectedTextCount').textContent();
        expect(parseInt(selectedCount)).toBeGreaterThan(0);
    });

    test('should perform a search', async ({ page }) => {
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        await page.fill('#searchInput', 'brot');
        await page.click('#searchButton');

        // Wait for results to appear
        await page.waitForTimeout(2000);

        // Either results section or no-results message should be visible
        const resultsVisible = await page.locator('#resultsSection').isVisible();
        const noResultsVisible = await page.locator('#noResults').isVisible();

        expect(resultsVisible || noResultsVisible).toBeTruthy();
    });

    test('should display search results with proper structure', async ({ page }) => {
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        // Wait for results
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });

        const firstResult = page.locator('#resultsList > div').first();
        await expect(firstResult).toBeVisible();

        // Result card structure: title (h3), author (.text-sm), match count badge (.bg-brand-100)
        await expect(firstResult.locator('h3')).toBeVisible();
        await expect(firstResult.locator('.text-sm').first()).toBeVisible();
        await expect(firstResult.locator('.bg-brand-100')).toBeVisible();
    });

    test('should filter text list', async ({ page }) => {
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const totalTexts = await page.locator('#textList label').count();

        // Type a filter term
        await page.fill('#textFilter', 'Nibelungen');
        await page.waitForTimeout(300);

        // Fewer texts should be visible
        const visibleTexts = await page.locator('#textList label:not([style*="display: none"])').count();
        expect(visibleTexts).toBeLessThan(totalTexts);
        expect(visibleTexts).toBeGreaterThan(0);

        // Filter info should be shown
        await expect(page.locator('#filterInfoText')).toBeVisible();
    });

    test('should open reading view on result click', async ({ page }) => {
        test.setTimeout(120000); // TEI file loading can be slow

        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search for a common term
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        // Wait for results
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });

        // Click first result
        await page.locator('#resultsList > div').first().click();

        // Reading view should populate (title appears)
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Reading body should have content
        await expect(page.locator('#readingBody')).not.toBeEmpty();
    });

    test('should show highlight navigation after search + result click', async ({ page }) => {
        test.setTimeout(120000);

        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        await page.waitForSelector('#resultsList > div', { timeout: 10000 });
        await page.locator('#resultsList > div').first().click();

        // Wait for reading view to load
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Highlight navigation should appear
        await expect(page.locator('#readingNavigation')).toBeVisible({ timeout: 5000 });
        await expect(page.locator('#prevHighlight')).toBeVisible();
        await expect(page.locator('#nextHighlight')).toBeVisible();
        await expect(page.locator('#highlightIndicator')).toBeVisible();
    });

});
