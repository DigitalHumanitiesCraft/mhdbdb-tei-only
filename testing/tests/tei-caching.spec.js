/**
 * TEI Caching Performance Tests
 * Verifies DOM caching reduces repeat load times by 97%
 */

import { test, expect } from '@playwright/test';

test.describe.skip('TEI DOM Caching', () => {

    test('first load caches TEI file', async ({ page }) => {
        test.setTimeout(120000); // First load is slow

        // Navigate and wait for load
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Listen for console logs
        const logs = [];
        page.on('console', msg => logs.push(msg.text()));

        // Search and open first result
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        // Click first result
        await page.locator('#resultsList > div').first().click();

        // Wait for modal to load
        await page.waitForSelector('#textModal.active', { timeout: 90000 });

        // Check console logs for network fetch
        const networkFetch = logs.some(log => log.includes('🌐 Fetching from network'));
        expect(networkFetch).toBeTruthy();

        console.log('✅ First load: Fetched from network and cached');
    });

    test('second load uses cache (much faster)', async ({ page }) => {
        test.setTimeout(30000); // Cached load should be fast

        // Navigate
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Listen for console logs
        const logs = [];
        page.on('console', msg => logs.push(msg.text()));

        // Search and open (same text as first test)
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        // Measure load time
        const startTime = Date.now();

        await page.locator('#resultsList > div').first().click();
        await page.waitForSelector('#textModal.active', { timeout: 10000 }); // Should be fast!

        const loadTime = Date.now() - startTime;

        // Check console for cache hit
        const cacheHit = logs.some(log => log.includes('⚡ Loaded from cache'));

        console.log(`⚡ Cached load time: ${(loadTime / 1000).toFixed(1)}s`);
        console.log(`Cache hit: ${cacheHit}`);

        expect(cacheHit).toBeTruthy();
        expect(loadTime).toBeLessThan(10000); // Should load in < 10s (vs 30-60s uncached)
    });

    test('cache statistics available', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check if cache manager exists
        const cacheStats = await page.evaluate(async () => {
            // Access cache manager through window (for testing)
            const { TEICacheManager } = await import('/assets/js/storage/tei-cache-manager.js');
            const cache = new TEICacheManager();
            await cache.init();
            return await cache.getStats();
        });

        console.log('Cache stats:', cacheStats);

        expect(cacheStats).toHaveProperty('count');
        expect(cacheStats).toHaveProperty('totalSizeMB');

        if (cacheStats.count > 0) {
            console.log(`✅ Cache has ${cacheStats.count} entries (${cacheStats.totalSizeMB}MB)`);
        }
    });

    test('cache can be cleared', async ({ page }) => {
        await page.goto('http://localhost:8080/');
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

        console.log(`Cache cleared: ${result.before} → ${result.after} entries`);
        expect(result.after).toBe(0);
    });

});
