/**
 * Visual Responsive Testing Suite
 * Takes screenshots at different viewport sizes to verify responsive design
 * Desktop-only project (min 1200px) — tests verify playground at various sizes
 */

import { test, expect } from '@playwright/test';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const viewports = {
    'iPhone-SE': { width: 375, height: 667 },
    'iPhone-12': { width: 390, height: 844 },
    'iPad-Mini': { width: 768, height: 1024 },
    'iPad-Pro': { width: 1024, height: 1366 },
    'Desktop': { width: 1440, height: 900 }
};

// Test Playground at various viewport sizes
for (const [device, viewport] of Object.entries(viewports)) {
    test(`Playground - ${device} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize(viewport);
        await page.goto('http://localhost:8080/playground/');

        // Wait for corpus to auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 30000 });

        await page.screenshot({
            path: resolve(__dirname, `../screenshots/playground-${device.toLowerCase()}.png`),
            fullPage: true
        });

        // Test authority search (Lemmata anzeigen)
        const lemmataBtn = page.locator('button:has-text("Lemmata anzeigen")');
        if (await lemmataBtn.isVisible()) {
            await lemmataBtn.click();
            await page.waitForTimeout(500);

            await page.screenshot({
                path: resolve(__dirname, `../screenshots/playground-${device.toLowerCase()}-lemmata.png`),
                fullPage: true
            });

            const lemmaSearch = page.locator('#lemmaSearch');
            if (await lemmaSearch.isVisible()) {
                await lemmaSearch.fill('got');
                await page.waitForTimeout(1000);

                await page.screenshot({
                    path: resolve(__dirname, `../screenshots/playground-${device.toLowerCase()}-lemmata-results.png`),
                    fullPage: true
                });
            }
        }
    });
}

// Landscape orientation tests
test('Main Site - Landscape iPad (1024x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('http://localhost:8080/korpus.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

    await page.screenshot({
        path: resolve(__dirname, '../screenshots/main-site-ipad-landscape.png'),
        fullPage: true
    });
});

test('Playground - Landscape iPad (1024x768)', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('http://localhost:8080/playground/');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 30000 });

    await page.screenshot({
        path: resolve(__dirname, '../screenshots/playground-ipad-landscape.png'),
        fullPage: true
    });
});

// Touch interaction tests
test('Main Site - Touch Interaction Test (iPhone)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8080/korpus.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

    // Search button should be tappable
    const searchBtn = page.locator('#searchButton');
    const searchBtnBox = await searchBtn.boundingBox();
    // Ohne Bounding-Box wäre der Test assertion-frei gewesen (Audit #41)
    expect(searchBtnBox).not.toBeNull();
    expect(searchBtnBox.height).toBeGreaterThanOrEqual(44);
});

test('Playground - Touch Interaction Test (iPhone)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:8080/playground/');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 30000 });

    // Test action buttons are tappable — nur sichtbare Buttons messen und
    // sicherstellen, dass überhaupt gemessen wurde (Audit #41: bei 0 messbaren
    // Buttons blieb minHeight Infinity und Infinity >= 44 bestand vakuös).
    const buttons = page.locator('button:visible');
    const count = await buttons.count();

    let minHeight = Infinity;
    let measured = 0;
    for (let i = 0; i < Math.min(count, 10); i++) {
        const box = await buttons.nth(i).boundingBox();
        if (box) {
            minHeight = Math.min(minHeight, box.height);
            measured++;
        }
    }

    expect(measured).toBeGreaterThan(0);
    expect(minHeight).toBeGreaterThanOrEqual(44);
});
