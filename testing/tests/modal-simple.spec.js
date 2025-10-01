/**
 * Simple Modal Test - Diagnose modal opening issue
 */

import { test, expect } from '@playwright/test';

test.describe('Modal Diagnostic Test', () => {

    test('check if modal exists in DOM', async ({ page }) => {
        await page.goto('http://localhost:8080/');

        // Wait for page to load
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Check if modal element exists
        const modal = page.locator('#textModal');
        await expect(modal).toBeAttached();

        console.log('✓ Modal element exists in DOM');
    });

    test('perform search and check results', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Enter search term
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');

        // Wait for results (with generous timeout)
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        // Count results
        const resultCards = await page.locator('#resultsList > div').count();
        console.log(`✓ Found ${resultCards} result cards`);

        expect(resultCards).toBeGreaterThan(0);
    });

    test('check if first result is clickable', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        // Get first result
        const firstResult = page.locator('#resultsList > div').first();
        await expect(firstResult).toBeVisible();

        // Check if it has click handler (via cursor style)
        const cursor = await firstResult.evaluate(el => window.getComputedStyle(el).cursor);
        console.log(`✓ First result cursor style: ${cursor}`);

        expect(cursor).toBe('pointer');
    });

    test('click result and check if modal becomes visible', async ({ page }) => {
        await page.goto('http://localhost:8080/');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Search
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 15000 });

        // Click first result
        const firstResult = page.locator('#resultsList > div').first();
        await firstResult.click();

        // Wait a bit for modal logic to execute
        await page.waitForTimeout(1000);

        // Check if modal has 'active' class
        const modalClasses = await page.locator('#textModal').getAttribute('class');
        console.log(`✓ Modal classes after click: ${modalClasses}`);

        // Check if modal is visible
        const isVisible = await page.locator('#textModal').isVisible();
        console.log(`✓ Modal visible: ${isVisible}`);

        if (!isVisible) {
            // Check for console errors
            const logs = [];
            page.on('console', msg => logs.push(msg.text()));

            console.log('Console output:', logs.slice(-10));
        }
    });

});
