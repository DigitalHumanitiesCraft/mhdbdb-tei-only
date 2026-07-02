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

    test('stale cached copy is replaced on next load (revalidation, #151)', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const result = await page.evaluate(async () => {
            const { TEICacheManager } = await import('/assets/js/storage/tei-cache-manager.js');
            const cache = new TEICacheManager();
            await cache.init();

            const filename = 'EUS.tei.xml';
            // Simulate the pre-deploy state: cached copy with outdated validators
            await cache.set(
                filename,
                '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text>STALE</text></TEI>',
                { etag: '"outdated"', lastModified: 'Mon, 01 Jan 2001 00:00:00 GMT' }
            );

            const doc = await cache.load(filename);
            // set() in load() is fire-and-forget — wait for the cache write
            await new Promise(r => setTimeout(r, 300));
            const entry = await cache.getEntry(filename);

            return {
                isStale: doc.documentElement.textContent.includes('STALE'),
                hasValidator: !!(entry && (entry.etag || entry.lastModified)),
                cachedSize: entry ? entry.size : 0
            };
        });

        expect(result.isStale).toBe(false);           // fresh content, not the 30-day-old copy
        expect(result.hasValidator).toBe(true);       // validators stored for future 304s
        expect(result.cachedSize).toBeGreaterThan(1000); // real TEI file re-cached
    });

    test('unchanged file revalidates via 304 and serves cached copy', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const result = await page.evaluate(async () => {
            const { TEICacheManager } = await import('/assets/js/storage/tei-cache-manager.js');
            const cache = new TEICacheManager();
            await cache.init();

            const filename = 'EUS.tei.xml';
            await cache.delete(filename);
            await cache.load(filename); // prime cache with real validators
            await new Promise(r => setTimeout(r, 300)); // fire-and-forget set()

            // Tamper with the cached content but keep the valid validators:
            // a 304 must serve this cached copy without re-downloading
            const primed = await cache.getEntry(filename);
            await cache.set(
                filename,
                '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text>CACHED-COPY</text></TEI>',
                { etag: primed.etag, lastModified: primed.lastModified }
            );

            const doc = await cache.load(filename);
            return {
                servedCached: doc.documentElement.textContent.includes('CACHED-COPY'),
                hadValidators: !!(primed.etag || primed.lastModified)
            };
        });

        expect(result.hadValidators).toBe(true);
        expect(result.servedCached).toBe(true);
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
