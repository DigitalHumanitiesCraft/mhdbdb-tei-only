/**
 * Quick Playground Test
 * Debug authority index loading
 */

import { test, expect } from '@playwright/test';

test('debug playground authority loading', async ({ page }) => {
    const consoleMessages = [];
    const errors = [];

    page.on('console', msg => {
        consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
    });

    page.on('pageerror', error => {
        errors.push(error.message);
    });

    await page.goto('http://localhost:8080/playground/');

    // Wait longer
    await page.waitForTimeout(5000);

    // Check playground object
    const playgroundInfo = await page.evaluate(() => {
        return {
            exists: typeof window.playground !== 'undefined',
            hasAuthorityData: window.playground?.authorityData ? true : false,
            personsCount: window.playground?.authorityData?.persons?.length || 0,
            worksCount: window.playground?.authorityData?.works?.length || 0,
            lemmataCount: window.playground?.authorityData?.lemmata?.length || 0
        };
    });

    console.log('\n=== Playground Info ===');
    console.log(JSON.stringify(playgroundInfo, null, 2));

    console.log('\n=== Console Messages (last 30) ===');
    consoleMessages.slice(-30).forEach(msg => console.log(msg));

    console.log('\n=== Errors ===');
    errors.forEach(err => console.log(err));
});
