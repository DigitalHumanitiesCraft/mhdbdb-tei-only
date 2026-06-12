/**
 * Wörterbuch Entry Page Tests (Issue #117)
 * A–Z-Register über den Authority-Index.
 */

import { test, expect } from '@playwright/test';

test.describe('Wörterbuch-Einstiegsseite', () => {

    test('lädt mit Buchstabe A und zeigt Einträge', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        // Indexleiste: 26 Buchstaben + '#'
        const letterButtons = await page.locator('#letterBar button').count();
        expect(letterButtons).toBe(27);

        // Default-Buchstabe A mit Eintragszahl in der Überschrift
        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^A – [\d.]+ Lemmata$/);

        // Einträge gerendert (Seite 1 = 200)
        const entries = await page.locator('#entryGrid a').count();
        expect(entries).toBe(200);
    });

    test('Buchstabenwechsel auf S aktualisiert Einträge und URL', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        await page.click('#letterBar button[data-letter="s"]');

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^S – /);
        expect(page.url()).toContain('buchstabe=s');
    });

    test('Pagination blättert innerhalb des Buchstabens', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html?buchstabe=s');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const firstBefore = await page.textContent('#entryGrid a >> nth=0');
        await page.click('#pagination button:has-text("2")');
        const firstAfter = await page.textContent('#entryGrid a >> nth=0');

        expect(firstAfter).not.toBe(firstBefore);
        expect(page.url()).toContain('seite=2');
    });

    test('URL-State wird beim Laden gelesen (Deep-Link)', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html?buchstabe=m&seite=2');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^M – /);

        // Die aktive Seitenzahl ist der einzige disabled Button ohne Pfeiltext
        const activePage = await page.textContent('#pagination button[disabled]:not(:has-text("Zurück")):not(:has-text("Weiter"))');
        expect(activePage).toBe('2');
    });

    test('Eintrag verlinkt auf die Lemma-Seite', async ({ page }) => {
        await page.goto('http://localhost:8080/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const href = await page.getAttribute('#entryGrid a >> nth=0', 'href');
        expect(href).toMatch(/^lemma\/\?id=\d+$/);
    });

    test('Nav-Link Wörterbuch ist auf der Startseite vorhanden', async ({ page }) => {
        await page.goto('http://localhost:8080/index.html');
        const navLink = page.locator('header a[data-nav="woerterbuch"]').first();
        await expect(navLink).toHaveText(/Wörterbuch/);
    });
});
