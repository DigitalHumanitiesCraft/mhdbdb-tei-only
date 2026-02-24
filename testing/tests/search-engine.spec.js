/**
 * Search Engine Tests
 * Tests for SearchEngine class methods via page.evaluate()
 *
 * Covers: searchLemma(), resolveLemmaIds() (3-stage), passesFilters(),
 * text inclusion filtering, snippet extraction
 *
 * Uses window._mhdbdbApp.searchEngine for direct method access.
 * Issue #43 — Priority 3: search engine coverage
 */

import { test, expect } from '@playwright/test';

test.describe('Search Engine', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    });

    test('searchLemma() returns results for known term', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            return await se.searchLemma('got');
        });

        expect(results.length).toBeGreaterThan(0);

        // Each result should have expected fields
        const first = results[0];
        expect(first).toHaveProperty('textId');
        expect(first).toHaveProperty('title');
        expect(first).toHaveProperty('matchCount');
        expect(first).toHaveProperty('lemmaId');
    });

    test('searchLemma() returns no exact/variant match for gibberish', async ({ page }) => {
        // Stage 3 partial match may still return results for any string,
        // so we test that resolveLemmaIds finds no exact or variant match
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            // Stage 1: exact match
            const exact = se.authorityIndex.lemmata.filter(l => l.normalized === 'zzzzqxjk');
            // Stage 2: variant match
            const variant = se.authorityIndex.variants['zzzzqxjk'];
            return { exact: exact.length, variant: !!variant };
        });

        expect(lemmaIds.exact).toBe(0);
        expect(lemmaIds.variant).toBe(false);
    });

    test('resolveLemmaIds() - exact match (Stage 1)', async ({ page }) => {
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('got');
        });

        expect(lemmaIds.length).toBeGreaterThan(0);
    });

    test('resolveLemmaIds() - variant match (Stage 2)', async ({ page }) => {
        // 'brot' is normalized form of 'brôt', should resolve via variants index
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('brot');
        });

        expect(lemmaIds.length).toBeGreaterThan(0);
        // Should resolve to lemma_879 (brôt)
        expect(lemmaIds.some(id => id.includes('879'))).toBeTruthy();
    });

    test('resolveLemmaIds() - partial match (Stage 3)', async ({ page }) => {
        // A term that has no exact or variant match falls through to partial
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('fri');
        });

        // Stage 3 should find at least one partial match
        expect(lemmaIds.length).toBeGreaterThanOrEqual(1);
    });

    test('text inclusion filter restricts results', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            const included = new Set(['ABG', 'NIB']);
            return await se.searchLemma('got', { includedTexts: included });
        });

        // All results should be from included texts only
        results.forEach(r => {
            expect(['ABG', 'NIB']).toContain(r.textId);
        });
    });

    test('deselect all texts - search returns no results (UI)', async ({ page }) => {
        // Click "Keine" to deselect all texts
        await page.click('#selectNoneTexts');
        await page.waitForTimeout(300);

        // Search for a common term
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForTimeout(2000);

        // Should show no results
        const noResults = await page.locator('#noResults').isVisible();
        const resultCount = await page.locator('#resultsList > div').count();

        expect(noResults || resultCount === 0).toBeTruthy();
    });

    test('snippet extraction returns non-empty string', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            return await se.searchLemma('got');
        });

        expect(results.length).toBeGreaterThan(0);
        expect(typeof results[0].snippet).toBe('string');
        expect(results[0].snippet.length).toBeGreaterThan(0);
    });

});
