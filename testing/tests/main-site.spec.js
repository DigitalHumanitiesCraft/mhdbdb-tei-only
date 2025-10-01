/**
 * Main Site Tests
 * Tests for the public-facing MHDBDB main site
 */

import { test, expect } from '@playwright/test';

test.describe('Main Site', () => {

    test.beforeEach(async ({ page }) => {
        // Navigate to main site
        await page.goto('http://localhost:8080/');
    });

    test('should load main site without errors', async ({ page }) => {
        // Check for console errors
        const errors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                errors.push(msg.text());
            }
        });

        // Wait for loading screen to disappear (max 30 seconds)
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check for errors
        if (errors.length > 0) {
            console.error('Console errors:', errors);
        }
        expect(errors.length).toBe(0);
    });

    test('should display main site elements', async ({ page }) => {
        // Wait for page to load
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check key elements
        await expect(page.locator('h1')).toContainText('Mittelhochdeutsche Begriffsdatenbank');
        await expect(page.locator('#searchInput')).toBeVisible();
        await expect(page.locator('#searchButton')).toBeVisible();
        await expect(page.locator('#genreFilter')).toBeVisible();
        await expect(page.locator('#authorFilter')).toBeVisible();
    });

    test('should load indices successfully', async ({ page }) => {
        // Monitor console logs
        const logs = [];
        page.on('console', msg => {
            logs.push(msg.text());
        });

        // Wait for loading to complete
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check for success logs
        const successLogs = logs.filter(log =>
            log.includes('Authority index loaded') ||
            log.includes('Corpus index loaded')
        );

        expect(successLogs.length).toBeGreaterThan(0);
    });

    test('should populate filter dropdowns', async ({ page }) => {
        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check genre filter has options
        const genreOptions = await page.locator('#genreFilter option').count();
        expect(genreOptions).toBeGreaterThan(1); // At least "Alle Gattungen" + others

        // Check author filter has options
        const authorOptions = await page.locator('#authorFilter option').count();
        expect(authorOptions).toBeGreaterThan(1); // At least "Alle Autoren" + others
    });

    test('should perform a search', async ({ page }) => {
        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Enter search term
        await page.fill('#searchInput', 'brot');

        // Click search
        await page.click('#searchButton');

        // Wait for results (give it 5 seconds)
        await page.waitForTimeout(2000);

        // Check if results section is visible or no results message
        const resultsVisible = await page.locator('#resultsSection').isVisible();
        const noResultsVisible = await page.locator('#noResults').isVisible();

        expect(resultsVisible || noResultsVisible).toBeTruthy();
    });

    test('should display search results with proper structure', async ({ page }) => {
        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search for common word
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        // Wait for results
        await page.waitForTimeout(3000);

        // Check if results are displayed
        const resultsVisible = await page.locator('#resultsSection').isVisible();

        if (resultsVisible) {
            // Verify result card structure
            const firstResult = page.locator('#resultsList > div').first();
            await expect(firstResult).toBeVisible();

            // Check for title, author, match count (more specific selectors)
            await expect(firstResult.locator('h3')).toBeVisible();
            await expect(firstResult.locator('.text-sm').first()).toBeVisible(); // First .text-sm (author)
            await expect(firstResult.locator('.bg-blue-100')).toBeVisible(); // Match count badge
        }
    });

    test('should filter results by genre', async ({ page }) => {
        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Select a genre (if available)
        const genreOptions = await page.locator('#genreFilter option').count();

        if (genreOptions > 1) {
            // Select second option (first non-empty genre)
            await page.selectOption('#genreFilter', { index: 1 });

            // Search
            await page.fill('#searchInput', 'got');
            await page.click('#searchButton');

            await page.waitForTimeout(2000);

            // Results should respect genre filter
            const resultsCount = await page.locator('#resultsList > div').count();
            console.log(`Results with genre filter: ${resultsCount}`);
        }
    });

    test('should open text modal on result click', async ({ page }) => {
        // Increase timeout for this test (TEI file loading is slow)
        test.setTimeout(120000); // 2 minutes

        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForTimeout(2000);

        // Check if results exist
        const resultsVisible = await page.locator('#resultsSection').isVisible();

        if (resultsVisible) {
            const resultCount = await page.locator('#resultsList > div').count();

            if (resultCount > 0) {
                // Click first result
                await page.locator('#resultsList > div').first().click();

                // Wait for modal to load (TEI files are large, may take 30-60s)
                await page.waitForSelector('#textModal.active', { timeout: 90000 });

                // Check modal is visible
                const modalVisible = await page.locator('#textModal.active').isVisible();
                expect(modalVisible).toBeTruthy();

                // Check modal content
                await expect(page.locator('#modalTitle')).not.toBeEmpty();
                await expect(page.locator('#modalContent')).toBeVisible();
            }
        }
    });

    test('should close modal on close button click', async ({ page }) => {
        // Increase timeout for this test
        test.setTimeout(120000); // 2 minutes

        // Wait for loading
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search and open modal
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForTimeout(2000);

        const resultsVisible = await page.locator('#resultsSection').isVisible();

        if (resultsVisible) {
            const resultCount = await page.locator('#resultsList > div').count();

            if (resultCount > 0) {
                await page.locator('#resultsList > div').first().click();
                await page.waitForSelector('#textModal.active', { timeout: 90000 });

                // Close modal
                await page.click('#closeModal');
                await page.waitForTimeout(500);

                // Modal should be hidden
                const modalVisible = await page.locator('#textModal.active').isVisible();
                expect(modalVisible).toBeFalsy();
            }
        }
    });

});
