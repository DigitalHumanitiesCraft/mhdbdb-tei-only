/**
 * Modal Debug Test
 * Tests text modal opening functionality
 */

import { test, expect } from '@playwright/test';

test.describe('Text Modal Debug', () => {

    test('search and open first result', async ({ page }) => {
        // Capture console and errors
        const consoleMessages = [];
        const errors = [];

        page.on('console', msg => {
            consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
        });

        page.on('pageerror', error => {
            errors.push(error.message);
        });

        // Navigate to main site
        await page.goto('http://localhost:8080/');

        // Wait for loading to complete
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        console.log('✅ Main site loaded');

        // Search for "brot"
        await page.fill('#searchInput', 'brot');
        await page.click('#searchButton');

        // Wait for results
        await page.waitForSelector('#resultsList .border', { timeout: 10000 });

        console.log('✅ Search results appeared');

        // Check that results exist
        const resultCards = await page.locator('#resultsList .border').count();
        console.log(`📊 Found ${resultCards} result cards`);

        if (resultCards === 0) {
            console.log('❌ No results found');
            return;
        }

        // Click first result
        console.log('Clicking first result...');
        await page.click('#resultsList .border:first-child');

        // Wait a moment for modal to appear
        await page.waitForTimeout(2000);

        // Check modal state
        const modalVisible = await page.isVisible('#textModal');
        const modalHasActive = await page.locator('#textModal').evaluate(el => el.classList.contains('active'));

        console.log(`Modal visible: ${modalVisible}`);
        console.log(`Modal has 'active' class: ${modalHasActive}`);

        // Check modal content
        const modalTitle = await page.locator('#modalTitle').textContent();
        const modalAuthor = await page.locator('#modalAuthor').textContent();

        console.log(`Modal title: ${modalTitle}`);
        console.log(`Modal author: ${modalAuthor}`);

        // Print console messages
        console.log('\n=== Browser Console Messages ===');
        consoleMessages.slice(-20).forEach(msg => console.log(msg));

        // Print errors
        if (errors.length > 0) {
            console.log('\n=== Browser Errors ===');
            errors.forEach(err => console.log(err));
        }

        // Verify modal opened
        expect(modalVisible).toBe(true);
        expect(modalHasActive).toBe(true);
    });

    test('check if textRenderer initializes correctly', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const hasTextRenderer = await page.evaluate(() => {
            return window.app && window.app.textRenderer ? true : false;
        });

        console.log(`TextRenderer exists: ${hasTextRenderer}`);
        expect(hasTextRenderer).toBe(true);
    });

    test('check if TEI file can be fetched', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const canFetchTEI = await page.evaluate(async () => {
            try {
                // Try to fetch a known TEI file
                const response = await fetch('tei/ABG.tei.xml');
                return response.ok;
            } catch (error) {
                console.error('Fetch error:', error);
                return false;
            }
        });

        console.log(`Can fetch TEI file: ${canFetchTEI}`);
        expect(canFetchTEI).toBe(true);
    });
});
