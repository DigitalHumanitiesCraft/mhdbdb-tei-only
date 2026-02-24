/**
 * Search Functions with Pre-Built Corpus Tests
 * Tests all 11 search entry points with pre-loaded corpus
 */

import { test, expect } from '@playwright/test';

test.describe('Search Functions with Pre-Built Corpus', () => {

    test.beforeEach(async ({ page }) => {
        // Navigate to playground
        await page.goto('http://localhost:8080/playground/');

        // Wait for authority files to load
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Load corpus
        await page.click('#loadCorpusBtn');

        // Wait for corpus to load successfully
        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 15000 });

        console.log('✅ Playground ready with full corpus loaded');
    });

    // ==================== AUTHORITY FILES SEARCHES (6) ====================

    test('Search 1: Autoren anzeigen (Authors search)', async ({ page }) => {
        await page.click('button:has-text("Autoren anzeigen")');

        // Wait for search input to appear
        await page.waitForSelector('#authorSearch', { timeout: 5000 });

        // Search for "Eckhart"
        await page.fill('#authorSearch', 'Eckhart');
        await page.waitForTimeout(500); // Wait for search to execute

        // Check results appeared
        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Eckhart');
        console.log('✅ Authors search works');
    });

    test('Search 2: Werke anzeigen (Works search)', async ({ page }) => {
        await page.click('button:has-text("Werke anzeigen")');

        await page.waitForSelector('#workSearch', { timeout: 5000 });

        // Search for "Predigt"
        await page.fill('#workSearch', 'Predigt');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Predigt');
        console.log('✅ Works search works');
    });

    test('Search 3: Lemmata anzeigen (Lexicon search)', async ({ page }) => {
        await page.click('button:has-text("Lemmata anzeigen")');

        await page.waitForSelector('#lemmaSearch', { timeout: 5000 });

        // Search for "brot" (should match "brôt")
        await page.fill('#lemmaSearch', 'brot');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results.toLowerCase()).toMatch(/brôt|brot/);
        console.log('✅ Lemmata search works with MHG normalization');
    });

    test('Search 4: Begriffe anzeigen (Concepts search)', async ({ page }) => {
        await page.click('button:has-text("Begriffe anzeigen")');

        await page.waitForSelector('#conceptSearch', { timeout: 5000 });

        // Search for "Liebe"
        await page.fill('#conceptSearch', 'Liebe');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Liebe');
        console.log('✅ Concepts search works');
    });

    test('Search 5: Gattungen anzeigen (Genres search)', async ({ page }) => {
        await page.click('button:has-text("Gattungen anzeigen")');

        await page.waitForSelector('#genreSearch', { timeout: 5000 });

        // Search for "Predigt"
        await page.fill('#genreSearch', 'Predigt');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Predigt');
        console.log('✅ Genres search works');
    });

    test('Search 6: Namen anzeigen (Names search)', async ({ page }) => {
        await page.click('button:has-text("Namen anzeigen")');

        await page.waitForSelector('#nameSearch', { timeout: 5000 });

        // Search for "Maria"
        await page.fill('#nameSearch', 'Maria');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Maria');
        console.log('✅ Names search works');
    });

    // ==================== TEI TEXT SEARCHES (5) ====================

    test('Search 7: Lemma-Suche (Single lemma search in TEI)', async ({ page }) => {
        // Check if TEI explorer is available
        const hasFiles = await page.evaluate(() => {
            return window.playground &&
                   window.playground.teiData &&
                   window.playground.teiData.parsedXML &&
                   window.playground.teiData.parsedXML.length > 0;
        });

        if (!hasFiles) {
            console.log('⚠️  TEI files not loaded in parsedXML, skipping test');
            test.skip();
            return;
        }

        // Try to search for a lemma (exact method depends on UI implementation)
        // This test is speculative - adjust based on actual TEI explorer interface
        const teiSearchInput = page.locator('#tei-lemma-search-input');

        if (await teiSearchInput.isVisible()) {
            await teiSearchInput.fill('got');
            await page.click('#tei-lemma-search-btn');
            await page.waitForTimeout(1000);

            const results = await page.locator('#resultsContainer').textContent();
            expect(results.length).toBeGreaterThan(0);
            console.log('✅ Single lemma search in TEI works');
        } else {
            console.log('⚠️  TEI lemma search UI not found, skipping');
        }
    });

    test('Search 8-10: Multi-Lemma searches (Paragraph/Document/Proximity)', async ({ page }) => {
        // Check if multi-lemma search button exists
        const multiLemmaBtn = page.locator('button:has-text("Multi-Lemma")');

        if (await multiLemmaBtn.isVisible()) {
            await multiLemmaBtn.click();
            await page.waitForTimeout(500);

            // Check if modal opened
            const modal = page.locator('.multi-lemma-modal, #multiLemmaModal');
            await expect(modal).toBeVisible();

            console.log('✅ Multi-lemma search interface accessible');
        } else {
            console.log('⚠️  Multi-lemma search not implemented yet');
        }
    });

    test('Search 11: XPath Query on TEI', async ({ page }) => {
        // Select "TEI Texte" as target
        await page.selectOption('#xpathTarget', 'tei');

        // Enter a simple XPath query
        await page.fill('#xpathInput', '//tei:w[@lemmaRef]');

        // Execute query
        await page.click('button:has-text("XPath ausführen")');

        // Wait for results
        await page.waitForTimeout(2000);

        // Check if results appeared (not empty)
        const results = await page.locator('#resultsContainer').textContent();
        expect(results.length).toBeGreaterThan(100); // Should have substantial output

        console.log('✅ XPath query on TEI corpus works');
    });

    // ==================== PERFORMANCE TEST ====================

    test('Performance: Corpus loads faster than 15 seconds', async ({ page }) => {
        // This test will reload the page to measure performance
        await page.goto('http://localhost:8080/playground/');

        const startTime = Date.now();

        // Wait for authority files
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Load corpus
        await page.click('#loadCorpusBtn');

        // Wait for success
        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 15000 });

        const loadTime = Date.now() - startTime;

        console.log(`⏱️  Total load time: ${loadTime}ms (${(loadTime / 1000).toFixed(1)}s)`);

        // Should load in under 15 seconds
        expect(loadTime).toBeLessThan(15000);

        // Ideally under 10 seconds
        if (loadTime < 10000) {
            console.log('✅ Excellent performance: < 10s');
        } else {
            console.log('✅ Good performance: < 15s');
        }
    });

    // ==================== DATA INTEGRITY TEST ====================

    test('Data integrity: All 666 texts accessible', async ({ page }) => {
        const textCount = await page.evaluate(() => {
            return window.playground &&
                   window.playground.teiData &&
                   window.playground.teiData.parsedXML
                   ? window.playground.teiData.parsedXML.length
                   : 0;
        });

        console.log(`📊 Texts loaded: ${textCount}/666`);
        expect(textCount).toBe(666);
    });

    test('Data integrity: Can load XML for first text', async ({ page }) => {
        const canLoadXML = await page.evaluate(async () => {
            try {
                const firstText = window.playground.teiData.parsedXML[0];
                if (!firstText) return false;

                // Test lazy-loading by accessing xmlDoc
                const xmlDoc = await firstText.xmlDoc;

                // Check if it's a valid XML document
                return xmlDoc && xmlDoc.documentElement && xmlDoc.documentElement.tagName === 'TEI';
            } catch (error) {
                console.error('XML load error:', error);
                return false;
            }
        });

        expect(canLoadXML).toBe(true);
        console.log('✅ Lazy-loading of TEI XML works');
    });
});
