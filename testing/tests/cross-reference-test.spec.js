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
        // Ein "→ Autor"-Button existiert im Work-Explorer nicht (mehr) — die
        // Work→Author-Verknüpfung zeigt sich als "Autor*in:"-Angabe in Karte
        // und Details-Panel (Audit #39: der alte if-Zweig war unerreichbar,
        // der Test damit dauerhaft assertion-frei grün).
        await page.click('button:has-text("Werke anzeigen")');
        await page.waitForSelector('#workSearch', { timeout: 5000 });
        await page.fill('#workSearch', 'Iwein');
        await page.waitForTimeout(500);

        const results = page.locator('#workResults .result-item');
        expect(await results.count()).toBeGreaterThan(0);

        // Iwein (Hartmann von Aue) muss die Autor-Zeile zeigen
        await expect(page.locator('#workResults')).toContainText('Autor*in:');

        // Details-Panel öffnet und enthält die Autor-Angabe ebenfalls
        await results.first().locator('button:has-text("Details anzeigen")').click();
        await page.waitForTimeout(300);
        await expect(page.locator('#workResults')).toContainText('Autor*in:');
    });

    test('Lemma to Concept cross-reference', async ({ page }) => {
        // Reales Datenmodell: Lemma → senses[] → conceptIds[] (ein flaches
        // l.concepts-Feld gab es nie; Audit #40 — die alte Assertion
        // `x !== undefined` konnte nie fehlschlagen).
        const hasConceptLinks = await page.evaluate(() => {
            const lemmata = window.playground.authorityManager.authorityData.lemmata;
            return !!lemmata && lemmata.some(l =>
                Array.isArray(l.senses) &&
                l.senses.some(s => Array.isArray(s.conceptIds) && s.conceptIds.length > 0)
            );
        });

        expect(hasConceptLinks).toBe(true);
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
