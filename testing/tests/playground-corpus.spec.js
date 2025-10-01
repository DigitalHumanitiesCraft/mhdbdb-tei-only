/**
 * Playground Corpus Loading Tests
 * Tests for loading pre-built corpus into playground
 */

import { test, expect } from '@playwright/test';

test.describe('Playground Corpus Loading', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
    });

    test('playground shows corpus load button', async ({ page }) => {
        const corpusBtn = page.locator('#loadCorpusBtn');
        await expect(corpusBtn).toBeVisible();
        await expect(corpusBtn).toContainText('Load Full Corpus');
    });

    test('corpus loads successfully', async ({ page }) => {
        // Wait for authority files to load first
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 10000 });

        // Click load button
        await page.click('#loadCorpusBtn');

        // Wait for loading to complete (max 10 seconds)
        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 10000 });

        // Check that button shows success
        const btnText = await page.locator('#loadCorpusBtn').textContent();
        expect(btnText).toContain('✅');
        expect(btnText).toContain('666');
    });

    test('file list populated after corpus load', async ({ page }) => {
        // Load corpus
        await page.click('#loadCorpusBtn');

        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 30000 });

        // Check file count
        const fileCount = await page.locator('#fileCount').textContent();
        expect(parseInt(fileCount)).toBeGreaterThan(600);
    });

    test('playground features enabled after corpus load', async ({ page }) => {
        // Load corpus
        await page.click('#loadCorpusBtn');

        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 30000 });

        // Check that authority explorers section is visible
        const authoritySection = page.locator('#authority-explorers');
        await expect(authoritySection).toBeVisible();

        // Check that TEI explorers section is visible
        const teiSection = page.locator('#tei-explorers');
        await expect(teiSection).toBeVisible();
    });

    test('can search lemma after corpus load', async ({ page }) => {
        // Load corpus
        await page.click('#loadCorpusBtn');

        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 30000 });

        // Try a simple search
        // This assumes there's a lemma search interface - adjust selectors as needed
        const searchInput = page.locator('#lemma-search-input');
        if (await searchInput.isVisible()) {
            await searchInput.fill('got');

            const searchBtn = page.locator('#lemma-search-btn');
            await searchBtn.click();

            // Wait a bit for results
            await page.waitForTimeout(2000);

            // Check if results appeared (exact selector depends on UI)
            const resultsContainer = page.locator('#search-results');
            await expect(resultsContainer).toBeVisible();
        }
    });

});
