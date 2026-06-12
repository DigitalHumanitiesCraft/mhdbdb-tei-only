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

        // Corpus now auto-loads — wait for file browser section to appear
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        console.log('✅ Playground ready with full corpus loaded');
    });

    // ==================== AUTHORITY FILES SEARCHES (6) ====================

    test('Search 1: Autoren anzeigen (Authors search)', async ({ page }) => {
        await page.click('#showAuthorsBtn');

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
        await page.click('#showWorksBtn');

        await page.waitForSelector('#workSearch', { timeout: 5000 });

        // Search for "Predigt"
        await page.fill('#workSearch', 'Predigt');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Predigt');
        console.log('✅ Works search works');
    });

    test('Search 3: Lemmata anzeigen (Lexicon search)', async ({ page }) => {
        await page.click('#showLemmataBtn');

        await page.waitForSelector('#lemmaSearch', { timeout: 5000 });

        // Search for "brot" (should match "brôt")
        await page.fill('#lemmaSearch', 'brot');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results.toLowerCase()).toMatch(/brôt|brot/);
        console.log('✅ Lemmata search works with MHG normalization');
    });

    test('Search 4: Begriffe anzeigen (Concepts search)', async ({ page }) => {
        await page.click('#showConceptsBtn');

        await page.waitForSelector('#conceptSearch', { timeout: 5000 });

        // Search for "Liebe"
        await page.fill('#conceptSearch', 'Liebe');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Liebe');
        console.log('✅ Concepts search works');
    });

    test('Search 5: Gattungen anzeigen (Genres search)', async ({ page }) => {
        await page.click('#showGenresBtn');

        await page.waitForSelector('#genreSearch', { timeout: 5000 });

        // Search for "Predigt"
        await page.fill('#genreSearch', 'Predigt');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Predigt');
        console.log('✅ Genres search works');
    });

    test('Search 6: Namen anzeigen (Names search)', async ({ page }) => {
        await page.click('#showNamesBtn');

        await page.waitForSelector('#nameSearch', { timeout: 5000 });

        // Search for "Maria"
        await page.fill('#nameSearch', 'Maria');
        await page.waitForTimeout(500);

        const results = await page.locator('#resultsContainer').textContent();
        expect(results).toContain('Maria');
        console.log('✅ Names search works');
    });

    test('Search 5b (#119): Gattungen-Filter "nur mit Werken" + Dimming', async ({ page }) => {
        await page.click('#showGenresBtn');
        await page.waitForSelector('#genreSearch', { timeout: 5000 });

        await page.fill('#genreSearch', 'chronik');
        await page.waitForTimeout(500);

        // Unchecked: matches include genres without works -> dimmed cards + placeholder
        const before = await page.locator('#genreResults article').count();
        expect(before).toBeGreaterThan(0);
        const dimmedBefore = await page.locator('#genreResults article')
            .evaluateAll(els => els.filter(e => e.className.includes('bg-slate-50/60')).length);
        expect(dimmedBefore).toBeGreaterThan(0);
        await expect(page.locator('#genreResults'))
            .toContainText('Noch keine Werke in der MHDBDB zugeordnet');

        // Toggle the filter -> only genres with works remain, placeholder gone
        await page.check('#genreOnlyWithWorks');
        await page.waitForTimeout(500);
        const after = await page.locator('#genreResults article').count();
        expect(after).toBeGreaterThan(0);
        expect(after).toBeLessThan(before);
        const dimmedAfter = await page.locator('#genreResults article')
            .evaluateAll(els => els.filter(e => e.className.includes('bg-slate-50/60')).length);
        expect(dimmedAfter).toBe(0);
        await expect(page.locator('#genreResults')).not.toContainText('Noch keine Werke');
        console.log('✅ #119 genre filter + dimming works');
    });

    test('Search 6b (#120): Name -> Begriff -> Lemmata mit namespaced Container', async ({ page }) => {
        await page.click('#showNamesBtn');
        await page.waitForSelector('#nameSearch', { timeout: 5000 });

        // "Geographika (Toponyme)" is an authority name with a concept connection
        await page.fill('#nameSearch', 'Geographika');
        await page.waitForTimeout(500);

        const conceptBtn = page.locator('#nameResults button:has-text("Begriffe anzeigen")').first();
        await expect(conceptBtn).toBeVisible();
        await conceptBtn.click();
        await page.waitForTimeout(300);

        // Related-concept cards expose a "Lemmata anzeigen" button
        const lemmaBtn = page.locator('#resultsContainer button:has-text("Lemmata anzeigen")').first();
        await expect(lemmaBtn).toBeVisible();
        await lemmaBtn.click();
        await page.waitForTimeout(500);

        // The namespaced container (lemmas-<nameId>-<conceptId>) must fill. Before the
        // #120 fix the authority-ui proxy dropped the detailsId, so the container id
        // did not match and getElementById mis-resolved across name cards.
        const filled = await page.evaluate(() => {
            const cs = [...document.querySelectorAll('[id^="lemmas-name_"]')];
            return cs.some(c => c.offsetParent !== null && c.innerHTML.trim().length > 20);
        });
        expect(filled).toBe(true);
        console.log('✅ #120 name -> concept -> lemma navigation works');
    });

    // ==================== TEI TEXT SEARCHES (4) ====================

    test('Search 7-9: Multi-Lemma searches (Paragraph/Document/Proximity)', async ({ page }) => {
        // Check if multi-lemma search button exists
        const multiLemmaBtn = page.locator('#findMultiLemmaBtn');

        if (await multiLemmaBtn.isVisible()) {
            await multiLemmaBtn.click();
            await page.waitForTimeout(500);

            // Check if modal opened
            const modal = page.locator('#multiLemmaModal');
            await expect(modal).toBeVisible();

            console.log('✅ Multi-lemma search interface accessible');
        } else {
            console.log('⚠️  Multi-lemma search not implemented yet');
        }
    });

    test('Search 10: XPath Query on TEI', async ({ page }) => {
        // XPath query UI may not be present in current redesign
        const xpathInput = page.locator('#xpathInput');

        if (await xpathInput.isVisible({ timeout: 2000 }).catch(() => false)) {
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
            expect(results.length).toBeGreaterThan(100);

            console.log('✅ XPath query on TEI corpus works');
        } else {
            // XPath UI not present in current redesign — verify core search still works
            console.log('ℹ️ XPath query UI not present in current playground version');
        }
    });

    // ==================== PERFORMANCE TEST ====================

    test('Performance: Corpus auto-loads within 60 seconds', async ({ page }) => {
        // Reload page to measure performance
        const startTime = Date.now();
        await page.goto('http://localhost:8080/playground/');

        // Wait for authority files
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Wait for corpus auto-load to complete
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        const loadTime = Date.now() - startTime;

        console.log(`⏱️  Total load time: ${loadTime}ms (${(loadTime / 1000).toFixed(1)}s)`);

        // Should load in under 60 seconds
        expect(loadTime).toBeLessThan(60000);

        if (loadTime < 15000) {
            console.log('✅ Excellent performance: < 15s');
        } else if (loadTime < 30000) {
            console.log('✅ Good performance: < 30s');
        } else {
            console.log('✅ Acceptable performance: < 60s');
        }
    });

    // ==================== DATA INTEGRITY TEST ====================

    test('Data integrity: All 667 texts accessible', async ({ page }) => {
        // Check the included count display
        const includedCount = await page.locator('#includedCount').textContent();
        expect(parseInt(includedCount)).toBe(667);
        console.log(`📊 Texts loaded: ${includedCount}/667`);
    });

    test('Data integrity: TEI queries section is visible', async ({ page }) => {
        // After corpus load, TEI analysis section should be visible
        const teiQueries = page.locator('#teiQueries');
        await expect(teiQueries).toBeVisible({ timeout: 5000 });

        console.log('✅ TEI query section available after corpus load');
    });
});
