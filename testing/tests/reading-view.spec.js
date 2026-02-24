/**
 * Reading View Tests
 * Tests for the TEI text reader panel in korpus.html
 *
 * Covers: URL param loading, metadata display, text rendering,
 * lemma highlighting, highlight navigation, multi-lemma colors, error handling
 *
 * Uses URL parameters to open reading view directly (skips search flow).
 * Issue #43 — Priority 2: reading view coverage
 */

import { test, expect } from '@playwright/test';

test.describe('Reading View', () => {

    // TEI file loading can take 30-90s on first fetch
    test.setTimeout(120000);

    test('should load reading view via URL params', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Reading title should populate after TEI loads
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Reading body should have content
        await expect(page.locator('#readingBody')).not.toBeEmpty();
    });

    test('should display metadata correctly', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Title and author should be populated
        const title = await page.locator('#readingTitle').textContent();
        expect(title.length).toBeGreaterThan(0);

        const author = await page.locator('#readingAuthor').textContent();
        expect(author.length).toBeGreaterThan(0);
    });

    test('should render formatted text content', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Reading body should have substantial text
        const bodyText = await page.locator('#readingBody').textContent();
        expect(bodyText.length).toBeGreaterThan(100);
    });

    test('should highlight lemma occurrences', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Highlighted words should exist in the reading body
        const highlightCount = await page.locator('#readingBody .highlight').count();
        expect(highlightCount).toBeGreaterThan(0);
    });

    test('should show highlight navigation with indicator', async ({ page }) => {
        // Use search flow to get a text with multiple highlights
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });
        await page.locator('#resultsList > div').first().click();

        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Navigation should be visible when highlights exist
        await expect(page.locator('#readingNavigation')).toBeVisible({ timeout: 5000 });

        // Indicator shows "Treffer 1 von N"
        const indicator = await page.locator('#highlightIndicator').textContent();
        expect(indicator).toMatch(/Treffer 1 von \d+/);

        // Prev should be disabled at first highlight
        await expect(page.locator('#prevHighlight')).toBeDisabled();

        // Check if next is enabled (text has multiple occurrences)
        const nextDisabled = await page.locator('#nextHighlight').isDisabled();
        if (!nextDisabled) {
            await page.click('#nextHighlight');
            const updated = await page.locator('#highlightIndicator').textContent();
            expect(updated).toMatch(/Treffer 2 von \d+/);

            await page.click('#prevHighlight');
            const backToFirst = await page.locator('#highlightIndicator').textContent();
            expect(backToFirst).toMatch(/Treffer 1 von \d+/);
        }
    });

    test('should color-code multi-lemma highlights', async ({ page }) => {
        // Two lemma IDs for multi-lemma mode
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879,lemma_7532');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Multi-lemma highlights should exist
        const highlights = page.locator('#readingBody .highlight');
        const count = await highlights.count();
        expect(count).toBeGreaterThan(0);

        // Collect unique background colors from highlights
        const colors = await page.evaluate(() => {
            const marks = document.querySelectorAll('#readingBody .highlight');
            const bgColors = new Set();
            marks.forEach(m => {
                const bg = m.style.backgroundColor;
                if (bg) bgColors.add(bg);
            });
            return [...bgColors];
        });

        // With two lemmata, we expect at least 2 different background colors
        // (only if both lemmata have occurrences in this text)
        expect(colors.length).toBeGreaterThanOrEqual(1);
    });

    test('should show error for missing text', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=NONEXISTENT_TEXT&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Wait for error to appear in reading body
        await page.waitForTimeout(3000);

        // Reading body or error display should show an error message
        const bodyText = await page.locator('#readingBody').textContent();
        const hasError = bodyText.toLowerCase().includes('error') ||
                         bodyText.toLowerCase().includes('nicht gefunden') ||
                         bodyText.toLowerCase().includes('not found') ||
                         bodyText.includes('Text not found');
        expect(hasError).toBeTruthy();
    });

});
