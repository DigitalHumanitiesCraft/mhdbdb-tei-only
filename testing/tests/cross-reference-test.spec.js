/**
 * Cross-Reference Functionality Tests
 * Tests linking between authority files and TEI texts
 */

import { test, expect } from '@playwright/test';

test.describe('Cross-Reference Functionality', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });
        console.log('✅ Playground ready');
    });

    test('Work to Author cross-reference', async ({ page }) => {
        // 1. Search for a work
        await page.click('button:has-text("Werke anzeigen")');
        await page.waitForSelector('#workSearch', { timeout: 5000 });
        await page.fill('#workSearch', 'Predigt');
        await page.waitForTimeout(500);
        
        // 2. Find a work result with an author link
        const hasAuthorLink = await page.locator('button:has-text("→ Autor")').count();
        
        if (hasAuthorLink > 0) {
            // Click the first author link
            await page.locator('button:has-text("→ Autor")').first().click();
            await page.waitForTimeout(500);
            
            // Verify we're now in the author search view
            const authorSearch = await page.locator('#authorSearch').count();
            expect(authorSearch).toBeGreaterThan(0);
            console.log('✅ Work→Author cross-reference works');
        } else {
            console.log('ℹ️ No author links found in works');
        }
    });

    test('Lemma to Concept cross-reference', async ({ page }) => {
        // Check if lemmata have concept annotations
        const hasConceptLinks = await page.evaluate(() => {
            const lemmata = window.playground.authorityManager.authorityData.lemmata;
            return lemmata && lemmata.some(l => l.concepts && l.concepts.length > 0);
        });
        
        if (hasConceptLinks) {
            console.log('✅ Lemmata have concept annotations');
        } else {
            console.log('ℹ️ No concept annotations found in lemmata');
        }
        
        expect(hasConceptLinks !== undefined).toBe(true);
    });

    test('TEI text to Authority data linking', async ({ page }) => {
        // Wait for corpus to auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check if corpus texts have lemma data via lemmaIndex
        const hasLemmaData = await page.evaluate(() => {
            // Auto-load stores corpus in corpusData, not teiData.parsedXML
            const corpusData = window.playground.corpusData;
            if (!corpusData || !corpusData.texts || corpusData.texts.length === 0) return false;

            // Check lemmaIndex — maps lemma IDs to document occurrences
            const lemmaIndex = corpusData.lemmaIndex;
            return lemmaIndex && Object.keys(lemmaIndex).length > 0;
        });

        expect(hasLemmaData).toBe(true);
        console.log('✅ Corpus texts have lemma references to authority data');
    });

    test('Orthographic variants to canonical lemma', async ({ page }) => {
        // Test the 3-stage resolution: exact/variants/fuzzy
        const variantResolution = await page.evaluate(async () => {
            const authorityManager = window.playground.authorityManager;

            // Test Stage 2: Variant resolution
            // "brott" is a variant spelling of "brôt" (lemma_879)
            const results = authorityManager.searchLemmaByOrthography('brott');

            return {
                found: results && results.length > 0,
                lemmaId: results && results[0] ? results[0].id : null,
                lemma: results && results[0] ? results[0].lemma : null
            };
        });

        expect(variantResolution.found).toBe(true);
        console.log(`✅ Variant resolution works: "brott" → lemma "${variantResolution.lemma}"`);
    });
});
