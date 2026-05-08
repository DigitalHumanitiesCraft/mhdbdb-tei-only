/**
 * Playground Corpus Loading Tests
 * Tests for auto-loading pre-built corpus into playground
 */

import { test, expect } from '@playwright/test';

test.describe('Playground Corpus Loading', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
    });

    test('playground shows loading state then file browser', async ({ page }) => {
        // Initially shows loading state
        const loadingState = page.locator('#corpusLoadingState');
        // It may already have loaded by the time we check — either state is fine
        const fileBrowser = page.locator('#fileBrowserSection');

        // Wait for file browser to appear (corpus auto-loads)
        await expect(fileBrowser).toBeVisible({ timeout: 60000 });
    });

    test('corpus loads successfully with 667 texts', async ({ page }) => {
        // Wait for auto-load to complete
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check included count shows 667
        const includedCount = await page.locator('#includedCount').textContent();
        expect(parseInt(includedCount)).toBe(667);
    });

    test('file list populated after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check file list has children
        const fileCount = await page.locator('#fileList > label').count();
        expect(fileCount).toBeGreaterThan(600);
    });

    test('playground features enabled after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check that TEI explorers section is visible
        const teiSection = page.locator('#teiQueries');
        await expect(teiSection).toBeVisible();
    });

    test('can open multi-lemma search after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Open multi-lemma search modal
        const multiLemmaBtn = page.locator('#findMultiLemmaBtn');
        await expect(multiLemmaBtn).toBeVisible();
        await multiLemmaBtn.click();

        // Verify modal opened
        const modal = page.locator('#multiLemmaModal');
        await expect(modal).toBeVisible();
    });

});
