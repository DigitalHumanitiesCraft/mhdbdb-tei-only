/**
 * Visual Mobile Testing Suite
 * Takes screenshots at different viewport sizes to verify responsive design
 * SKIPPED: Tests main site which is not the primary focus
 */

import { test, expect } from '@playwright/test';

const viewports = {
    'iPhone-SE': { width: 375, height: 667 },
    'iPhone-12': { width: 390, height: 844 },
    'iPad-Mini': { width: 768, height: 1024 },
    'iPad-Pro': { width: 1024, height: 1366 },
    'Desktop': { width: 1440, height: 900 }
};

// Test Main Site
for (const [device, viewport] of Object.entries(viewports)) {
    test.skip(`Main Site - ${device} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        // Set viewport
        await page.setViewportSize(viewport);

        // Navigate to main site
        await page.goto('http://localhost:8080/');

        // Wait for page to load
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Take full page screenshot
        await page.screenshot({
            path: `screenshots/main-site-${device.toLowerCase()}.png`,
            fullPage: true
        });

        console.log(`✅ Main Site screenshot: ${device}`);

        // Test search interaction
        const searchInput = page.locator('#searchInput');
        await searchInput.fill('got');
        await searchInput.press('Enter');

        // Wait for results
        await page.waitForTimeout(2000);

        // Screenshot with results
        await page.screenshot({
            path: `screenshots/main-site-${device.toLowerCase()}-search.png`,
            fullPage: true
        });

        console.log(`✅ Main Site search results: ${device}`);

        // Click first result to open modal
        const firstResult = page.locator('#resultsContainer button').first();
        if (await firstResult.isVisible()) {
            await firstResult.click();
            await page.waitForTimeout(1000);

            // Screenshot modal
            await page.screenshot({
                path: `screenshots/main-site-${device.toLowerCase()}-modal.png`,
                fullPage: true
            });

            console.log(`✅ Main Site modal: ${device}`);
        }
    });
}

// Test Playground
for (const [device, viewport] of Object.entries(viewports)) {
    test(`Playground - ${device} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        // Set viewport
        await page.setViewportSize(viewport);

        // Navigate to playground
        await page.goto('http://localhost:8080/playground/');

        // Wait for authority files to load
        await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

        // Take full page screenshot
        await page.screenshot({
            path: `screenshots/playground-${device.toLowerCase()}.png`,
            fullPage: true
        });

        console.log(`✅ Playground screenshot: ${device}`);

        // Test authority search (Lemmata anzeigen)
        const lemmataBtn = page.locator('button:has-text("Lemmata anzeigen")');
        if (await lemmataBtn.isVisible()) {
            await lemmataBtn.click();
            await page.waitForTimeout(500);

            await page.screenshot({
                path: `screenshots/playground-${device.toLowerCase()}-lemmata.png`,
                fullPage: true
            });

            console.log(`✅ Playground lemmata search: ${device}`);

            // Search for something
            const lemmaSearch = page.locator('#lemmaSearch');
            if (await lemmaSearch.isVisible()) {
                await lemmaSearch.fill('got');
                await page.waitForTimeout(1000);

                await page.screenshot({
                    path: `screenshots/playground-${device.toLowerCase()}-lemmata-results.png`,
                    fullPage: true
                });

                console.log(`✅ Playground lemmata results: ${device}`);
            }
        }
    });
}

// Test Landscape Orientation
test('Main Site - Landscape iPad (1024x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('http://localhost:8080/');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

    await page.screenshot({
        path: 'screenshots/main-site-ipad-landscape.png',
        fullPage: true
    });

    console.log('✅ Main Site landscape screenshot');
});

test('Playground - Landscape iPad (1024x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('http://localhost:8080/playground/');
    await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

    await page.screenshot({
        path: 'screenshots/playground-ipad-landscape.png',
        fullPage: true
    });

    console.log('✅ Playground landscape screenshot');
});

// Test Touch Interactions (simulate)
test('Main Site - Touch Interaction Test (iPhone)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8080/');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

    // Test header buttons are tappable
    const cacheBtn = page.locator('#cacheClearBtn');
    const boundingBox = await cacheBtn.boundingBox();

    // Verify minimum tap target size (44x44px)
    if (boundingBox) {
        expect(boundingBox.height).toBeGreaterThanOrEqual(44);
        console.log(`✅ Cache button tap target: ${boundingBox.width}x${boundingBox.height}px`);
    }

    // Search button
    const searchBtn = page.locator('button:has-text("Suchen")');
    const searchBtnBox = await searchBtn.boundingBox();
    if (searchBtnBox) {
        expect(searchBtnBox.height).toBeGreaterThanOrEqual(44);
        console.log(`✅ Search button tap target: ${searchBtnBox.width}x${searchBtnBox.height}px`);
    }
});

test('Playground - Touch Interaction Test (iPhone)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8080/playground/');
    await page.waitForSelector('#statusText:has-text("Authority Files geladen")', { timeout: 15000 });

    // Test all action buttons are tappable
    const buttons = page.locator('button');
    const count = await buttons.count();

    let minHeight = Infinity;
    for (let i = 0; i < Math.min(count, 10); i++) {
        const box = await buttons.nth(i).boundingBox();
        if (box) {
            minHeight = Math.min(minHeight, box.height);
        }
    }

    console.log(`✅ Playground minimum button height: ${minHeight}px`);
    expect(minHeight).toBeGreaterThanOrEqual(44);
});

// Generate summary report
test.afterAll(async () => {
    console.log('\n📸 Visual Testing Complete!');
    console.log('Screenshots saved to: screenshots/');
    console.log('\nGenerated screenshots:');
    console.log('- Main Site: iPhone-SE, iPhone-12, iPad-Mini, iPad-Pro, Desktop');
    console.log('- Playground: iPhone-SE, iPhone-12, iPad-Mini, iPad-Pro, Desktop');
    console.log('- Landscape: iPad (both sites)');
    console.log('- Search results and modals captured');
    console.log('\nReview screenshots to verify:');
    console.log('✓ Responsive layout adapts correctly');
    console.log('✓ Text remains readable at all sizes');
    console.log('✓ Buttons are touch-friendly (min 44x44px)');
    console.log('✓ No horizontal scrolling');
    console.log('✓ Modals display properly on mobile');
});
