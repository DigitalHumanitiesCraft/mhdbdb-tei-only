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

    test('person altNames and altNormalized are index-parallel (#307)', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        const alt = await page.evaluate(() => {
            const persons = window.playground?.authorityData?.persons || [];
            const withAlt = persons.filter(p => p.altNames && p.altNames.length);
            // CONTRACTS §G.3: altNormalized[i] gehoert zu altNames[i]. Faellt das
            // auseinander, zeigt der Explorer die falsche Trefferform an.
            const mismatched = withAlt.filter(
                p => !p.altNormalized || p.altNormalized.length !== p.altNames.length
            ).map(p => p.id);
            const rietenburg = persons.find(p => p.id === 'person_127');
            return {
                withAlt: withAlt.length,
                totalForms: withAlt.reduce((n, p) => n + p.altNames.length, 0),
                mismatched,
                rietenburgAlt: rietenburg ? rietenburg.altNames : null,
                rietenburgNorm: rietenburg ? rietenburg.altNormalized : null
            };
        });

        console.log('Person alternative names:', alt);

        expect(alt.mismatched).toEqual([]);
        expect(alt.withAlt).toBeGreaterThan(70);
        expect(alt.totalForms).toBeGreaterThan(90);
        // Der Anlassfall aus #228: Nebenform vorhanden und normalisiert.
        expect(alt.rietenburgAlt).toContain('Burggraf von Rietenburg');
        expect(alt.rietenburgNorm).toContain('burggraf von rietenburg');
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

    test('performance: authority index loads within 20 seconds', async ({ page }) => {
        const startTime = Date.now();

        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 30000 });

        const loadTime = Date.now() - startTime;

        console.log(`⏱️  Authority index load time: ${loadTime}ms (${(loadTime / 1000).toFixed(1)}s)`);

        // Threshold raised from 10s to 20s on 2026-08-05, the wait from 15s to 30s so
        // the assertion stays the deciding limit. Isolated, the load takes 5.5 to 5.9s
        // (measured, three runs); under the full suite plus a second session it crossed
        // 10s in two of three runs, i.e. the test was measuring machine load. 20s still
        // catches what it exists for: runtime XML parsing cost around 30s before the
        // pre-built indexes replaced it (documented in ARCHITECTURE.md, not measured
        // here; that code path is gone).
        expect(loadTime).toBeLessThan(20000);

        if (loadTime < 3000) {
            console.log('✅ Excellent performance: < 3s');
        } else if (loadTime < 5000) {
            console.log('✅ Good performance: < 5s');
        }
    });
});
