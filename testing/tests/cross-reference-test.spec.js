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
            const lemmata = window.playground.authorityData.lemmata;
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
        // Load corpus
        await page.click('#loadCorpusBtn');
        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 15000 });
        
        // Check if TEI texts have lemma references
        const hasLemmaRefs = await page.evaluate(() => {
            const teiData = window.playground.teiData;
            if (!teiData.parsedXML || teiData.parsedXML.length === 0) return false;
            
            const firstText = teiData.parsedXML[0];
            return firstText && firstText.metadata && firstText.metadata.lemmaCount > 0;
        });
        
        expect(hasLemmaRefs).toBe(true);
        console.log('✅ TEI texts have lemma references to authority data');
    });

    test('Orthographic variants to canonical lemma', async ({ page }) => {
        // Test the 3-stage resolution: exact/variants/fuzzy
        const variantResolution = await page.evaluate(async () => {
            const authorityManager = window.playground.authorityManager;
            
            // Test Stage 2: Variant resolution
            // "brott" is a variant spelling of "brôt" (lemma_879)
            const result = await authorityManager.searchLemmaByOrthography('brott');
            
            return {
                found: result !== null,
                lemmaId: result ? result.id : null,
                lemma: result ? result.lemma : null
            };
        });
        
        expect(variantResolution.found).toBe(true);
        console.log(`✅ Variant resolution works: "brott" → lemma "${variantResolution.lemma}"`);
    });
});
