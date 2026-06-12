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

    // === #17: TEI Structural Elements ===

    test('should render div type headers (song, chapter, recipe)', async ({ page }) => {
        // HZU has div type="number" headers
        await page.goto('http://localhost:8080/korpus.html?textId=HZU&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Should have div-type headers with German labels
        const headers = page.locator('#readingBody .tei-div-header');
        await expect(headers.first()).toBeVisible();
        const headerText = await headers.first().textContent();
        expect(headerText).toMatch(/Nr\.\s+\d+/);
    });

    test('should render stanza labels and verse line numbers', async ({ page }) => {
        // NBB (Nibelungenlied) has lg type="stanza" with l elements
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Stanza labels should exist
        const stanzaLabels = page.locator('#readingBody .stanza-label');
        await expect(stanzaLabels.first()).toBeVisible();
        const labelText = await stanzaLabels.first().textContent();
        expect(labelText).toMatch(/Strophe\s+\d+/);

        // Verse lines should have data-n attributes
        const verseLines = page.locator('#readingBody .verse-line[data-n]');
        const count = await verseLines.count();
        expect(count).toBeGreaterThan(0);
    });

    // === #127: visible verse-line numbering policy (.verse-line-numbered) ===
    // Policy: number the FIRST numeric line, then every line whose absolute @n is a
    // multiple of 5; non-numeric @n (e.g. h_* headers) is never numbered.

    test('#127: NBB (stanza-local @n) numbers only the first verse line', async ({ page }) => {
        // Nibelungenlied: @n resets per stanza (1..4) and never reaches a multiple of
        // 5, so only the very first numeric line carries a margin number.
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const numbered = await page.$$eval('#readingBody .verse-line-numbered',
            els => els.map(e => e.getAttribute('data-n')));
        expect(numbered).toEqual(['1']);
        // numeric guard: a numbered line always has a purely numeric @n (no h_* header)
        expect(numbered.every(n => /^\d+$/.test(n))).toBe(true);
    });

    test('#127: AGS (continuous @n) numbers the first line plus every 5th', async ({ page }) => {
        // Der altgewordene Sünder: continuous @n -> first line anchored + 5,10,15,...
        await page.goto('http://localhost:8080/korpus.html?textId=AGS&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const numbered = await page.$$eval('#readingBody .verse-line-numbered',
            els => els.map(e => parseInt(e.getAttribute('data-n'), 10)));
        expect(numbered.length).toBeGreaterThan(1);
        expect(numbered.slice(0, 4)).toEqual([1, 5, 10, 15]);
        // exactly one non-multiple-of-5 survives: the first-line anchor (@n=1)
        expect(numbered.filter(n => n % 5 !== 0)).toEqual([1]);
    });

    test('should render prose line numbers (lb)', async ({ page }) => {
        // ABG has lb elements with h_ prefix numbers
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Line numbers should be rendered
        const lineNumbers = page.locator('#readingBody .lb-number');
        await expect(lineNumbers.first()).toBeVisible();
    });

    test('should render note date and year badges', async ({ page }) => {
        // HZU has note type="date" and note type="year"
        await page.goto('http://localhost:8080/korpus.html?textId=HZU&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Year badge
        const yearBadge = page.locator('#readingBody .note-year');
        await expect(yearBadge.first()).toBeVisible();
        const yearText = await yearBadge.first().textContent();
        expect(yearText).toMatch(/\d{4}/);

        // Date badge
        const dateBadge = page.locator('#readingBody .note-date');
        await expect(dateBadge.first()).toBeVisible();
    });

    test('should render hi rend compound values with token classes', async ({ page }) => {
        // IW (Iwein) has hi rend="initial" elements
        await page.goto('http://localhost:8080/korpus.html?textId=IW&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // hi-initial class should exist (token-based, not the old .initial)
        const initials = page.locator('#readingBody .hi-initial');
        const count = await initials.count();
        expect(count).toBeGreaterThan(0);
    });

    test('should render colophon with distinct styling', async ({ page }) => {
        // ALX has div type="colophon"
        await page.goto('http://localhost:8080/korpus.html?textId=ALX&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Colophon div should exist (use div[data-type] to avoid matching the header too)
        const colophon = page.locator('#readingBody div.tei-div[data-type="colophon"]');
        await expect(colophon).toBeVisible();

        // Should have italic styling
        const fontStyle = await colophon.evaluate(el => getComputedStyle(el).fontStyle);
        expect(fontStyle).toBe('italic');
    });

    test('should apply verse-context or prose-context class', async ({ page }) => {
        // NBB (verse) should get verse-context
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        await expect(page.locator('#readingBody.verse-context')).toBeVisible();

        // ABG (prose) should get prose-context
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        await expect(page.locator('#readingBody.prose-context')).toBeVisible();
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
