import { test, expect } from '@playwright/test';

test('Check playground console errors', async ({ page }) => {
    const consoleMessages = [];
    const errors = [];
    const failedRequests = [];

    page.on('console', msg => {
        consoleMessages.push(`${msg.type()}: ${msg.text()}`);
    });

    page.on('pageerror', error => {
        errors.push(error.toString());
    });

    page.on('response', response => {
        if (response.status() >= 400) {
            failedRequests.push(`${response.status()} ${response.url()}`);
        }
    });

    await page.goto('http://localhost:8080/playground/');

    // Wait a bit for JS to execute
    await page.waitForTimeout(5000);

    console.log('\n=== CONSOLE MESSAGES ===');
    consoleMessages.forEach(msg => console.log(msg));

    console.log('\n=== PAGE ERRORS ===');
    errors.forEach(err => console.log(err));

    console.log('\n=== FAILED REQUESTS ===');
    failedRequests.forEach(req => console.log(req));

    // Print the status text
    const statusText = await page.locator('#statusText').textContent();
    console.log('\n=== STATUS TEXT ===');
    console.log(statusText);

    // Print summary
    console.log('\n=== SUMMARY ===');
    console.log(`Total errors: ${errors.length}`);
    console.log(`Total failed requests: ${failedRequests.length}`);
});
