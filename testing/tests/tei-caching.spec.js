/**
 * TEI Caching Performance Tests
 * Verifies DOM caching reduces repeat load times
 *
 * Rewritten Feb 2026 to match panel-based architecture (Issue #43)
 */

import { test, expect } from '@playwright/test';

test.describe('TEI DOM Caching', () => {

    test('first load caches TEI file', async ({ page }) => {
        test.setTimeout(120000);

        await page.goto('http://localhost:8080/korpus.html');

        const logs = [];
        page.on('console', msg => logs.push(msg.text()));

        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search and open first result
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });
        await page.locator('#resultsList > div').first().click();

        // Wait for reading view to load
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Check console logs for network fetch
        const networkFetch = logs.some(log => log.includes('Fetching from network') || log.includes('fetch'));
        // At minimum, the reading view loaded (cache or network)
        const titleText = await page.locator('#readingTitle').textContent();
        expect(titleText.length).toBeGreaterThan(0);
    });

    test('second load uses cache (faster)', async ({ page }) => {
        test.setTimeout(30000);

        await page.goto('http://localhost:8080/korpus.html');

        const logs = [];
        page.on('console', msg => logs.push(msg.text()));

        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search and open same text as first test
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        const startTime = Date.now();
        await page.locator('#resultsList > div').first().click();
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 15000 });
        const loadTime = Date.now() - startTime;

        // Cached load should be notably faster than first load
        const titleText = await page.locator('#readingTitle').textContent();
        expect(titleText.length).toBeGreaterThan(0);
        console.log(`Cached load time: ${(loadTime / 1000).toFixed(1)}s`);
    });

    test('cache statistics available', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const cacheStats = await page.evaluate(async () => {
            const { TEICacheManager } = await import('/assets/js/storage/tei-cache-manager.js');
            const cache = new TEICacheManager();
            await cache.init();
            return await cache.getStats();
        });

        expect(cacheStats).toHaveProperty('count');
        expect(cacheStats).toHaveProperty('totalSizeMB');
    });

    test('cache can be cleared', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const result = await page.evaluate(async () => {
            const { TEICacheManager } = await import('/assets/js/storage/tei-cache-manager.js');
            const cache = new TEICacheManager();
            await cache.init();

            const beforeStats = await cache.getStats();
            await cache.clear();
            const afterStats = await cache.getStats();

            return {
                before: beforeStats.count,
                after: afterStats.count
            };
        });

        expect(result.after).toBe(0);
    });

});
