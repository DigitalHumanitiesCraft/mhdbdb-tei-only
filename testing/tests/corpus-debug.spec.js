import { test, expect } from '@playwright/test';

test.describe('Corpus Loading Debug', () => {
    test('debug corpus loading with console logs', async ({ page }) => {
        // Capture console messages
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
        });

        // Capture errors
        const errors = [];
        page.on('pageerror', error => {
            errors.push(error.message);
        });

        // Navigate to playground
        await page.goto('http://localhost:8080/playground/index.html');

        // Wait for authority files to load
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 10000 });

        // Click load corpus button
        console.log('Clicking load corpus button...');
        await page.click('#loadCorpusBtn');

        // Wait for loading to start
        await page.waitForTimeout(500);

        // Check button text after 500ms
        const btnText1 = await page.locator('#loadCorpusBtn').textContent();
        console.log('Button text after 500ms:', btnText1);

        // Wait for success message (before it resets after 3 seconds)
        await page.waitForFunction(() => {
            const btn = document.getElementById('loadCorpusBtn');
            return btn && btn.textContent.includes('✅');
        }, { timeout: 10000 });

        // Check button text when success appears
        const btnText2 = await page.locator('#loadCorpusBtn').textContent();
        console.log('Button text with success:', btnText2);

        // Verify success
        expect(btnText2).toContain('✅');
        expect(btnText2).toContain('666');

        // Print all console messages
        console.log('\n=== Browser Console Messages ===');
        consoleMessages.forEach(msg => console.log(msg));

        // Print all errors
        if (errors.length > 0) {
            console.log('\n=== Browser Errors ===');
            errors.forEach(err => console.log(err));
        }

        // Check if there were any errors
        expect(errors.length).toBe(0);
    });

    test('check if corpus loader module loads', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/index.html');

        // Wait for page to load
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 10000 });

        // Try to import CorpusLoader directly in browser
        const result = await page.evaluate(async () => {
            try {
                const module = await import('../../js/corpus-loader.js');
                return {
                    success: true,
                    hasCorpusLoader: typeof module.CorpusLoader === 'function',
                    exports: Object.keys(module)
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        });

        console.log('Module import result:', result);
        expect(result.success).toBe(true);
        expect(result.hasCorpusLoader).toBe(true);
    });

    test('check if corpus index file is accessible', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/index.html');

        const result = await page.evaluate(async () => {
            try {
                const response = await fetch('../data/corpus-index.json.gz');
                return {
                    ok: response.ok,
                    status: response.status,
                    statusText: response.statusText,
                    contentLength: response.headers.get('content-length')
                };
            } catch (error) {
                return {
                    ok: false,
                    error: error.message
                };
            }
        });

        console.log('Corpus index fetch result:', result);
        expect(result.ok).toBe(true);
        expect(result.status).toBe(200);
    });
});
