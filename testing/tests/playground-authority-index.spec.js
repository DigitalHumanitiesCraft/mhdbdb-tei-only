/**
 * Playground Authority Index Loading Tests
 * Tests that playground now uses pre-built authority index instead of XML files
 */

import { test, expect } from '@playwright/test';

test.describe('Playground Authority Index Loading', () => {

    test('playground loads authority index instead of XML files', async ({ page }) => {
        // Capture console messages
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
        });

        // Navigate to playground
        await page.goto('http://localhost:8080/playground/');

        // Wait for authority data to load
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Check console for authority index loading
        const hasAuthorityIndexLog = consoleMessages.some(msg =>
            msg.includes('Loading pre-built authority index') ||
            msg.includes('Authority index loaded')
        );

        console.log('Console messages:', consoleMessages.filter(m => m.includes('Authority')).join('\n'));

        expect(hasAuthorityIndexLog).toBe(true);
    });

    test('authority data populated correctly from index', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        const authorityStats = await page.evaluate(() => {
            return {
                persons: window.playground?.authorityData?.persons?.length || 0,
                works: window.playground?.authorityData?.works?.length || 0,
                lemmata: window.playground?.authorityData?.lemmata?.length || 0,
                concepts: window.playground?.authorityData?.concepts?.length || 0,
                genres: window.playground?.authorityData?.genres?.length || 0,
                names: window.playground?.authorityData?.names?.length || 0
            };
        });

        console.log('Authority data stats:', authorityStats);

        // Check that data is populated
        expect(authorityStats.persons).toBeGreaterThan(200);
        expect(authorityStats.works).toBeGreaterThan(500);
        expect(authorityStats.lemmata).toBeGreaterThan(40000);
        expect(authorityStats.concepts).toBeGreaterThan(500);
        expect(authorityStats.genres).toBeGreaterThan(600);
        expect(authorityStats.names).toBeGreaterThan(80);
    });

    test('authority searches work with index data', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Click "Lemmata anzeigen"
        await page.click('#showLemmataBtn');

        // Wait for search interface
        await page.waitForSelector('#lemmaSearch', { timeout: 5000 });

        // Search for "brot"
        await page.fill('#lemmaSearch', 'brot');
        await page.waitForTimeout(500);

        // Check results
        const resultsText = await page.locator('#resultsContainer').textContent();
        expect(resultsText.toLowerCase()).toContain('brôt');

        console.log('✅ Lemma search works with authority index');
    });

    test('corpus browser available after auto-load', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');

        // Wait for corpus auto-load to complete
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check file browser section is visible with file list
        const fileList = page.locator('#fileList');
        await expect(fileList).toBeVisible();

        console.log('✅ Corpus browser available after auto-load');
    });

    test('corpus auto-loads 667 texts', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');

        // Wait for corpus auto-load to complete
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check included count
        const includedCount = await page.locator('#includedCount').textContent();
        expect(parseInt(includedCount)).toBe(667);

        console.log('✅ Corpus auto-loaded 667 texts');
    });

    test('performance: authority index loads within 10 seconds', async ({ page }) => {
        const startTime = Date.now();

        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        const loadTime = Date.now() - startTime;

        console.log(`⏱️  Authority index load time: ${loadTime}ms (${(loadTime / 1000).toFixed(1)}s)`);

        // Pre-built index should load in under 10 seconds
        expect(loadTime).toBeLessThan(10000);

        if (loadTime < 3000) {
            console.log('✅ Excellent performance: < 3s');
        } else if (loadTime < 5000) {
            console.log('✅ Good performance: < 5s');
        }
    });
});
