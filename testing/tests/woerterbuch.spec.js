/**
 * Wörterbuch Entry Page Tests (Issue #117)
 * A–Z-Register über den Authority-Index.
 */

import { test, expect } from '@playwright/test';

test.describe('Wörterbuch-Einstiegsseite', () => {

    test('lädt mit Buchstabe A und zeigt Einträge', async ({ page }) => {
        await page.goto('/woerterbuch.html');
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
        await page.goto('/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        await page.click('#letterBar button[data-letter="s"]');

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^S – /);
        expect(page.url()).toContain('buchstabe=s');
    });

    test('Pagination blättert innerhalb des Buchstabens', async ({ page }) => {
        await page.goto('/woerterbuch.html?buchstabe=s');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const firstBefore = await page.textContent('#entryGrid a >> nth=0');
        await page.click('#pagination button:has-text("2")');
        const firstAfter = await page.textContent('#entryGrid a >> nth=0');

        expect(firstAfter).not.toBe(firstBefore);
        expect(page.url()).toContain('seite=2');
    });

    test('URL-State wird beim Laden gelesen (Deep-Link)', async ({ page }) => {
        await page.goto('/woerterbuch.html?buchstabe=m&seite=2');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const heading = await page.textContent('#letterHeading');
        expect(heading).toMatch(/^M – /);

        // Die aktive Seitenzahl ist der einzige disabled Button ohne Pfeiltext
        const activePage = await page.textContent('#pagination button[disabled]:not(:has-text("Zurück")):not(:has-text("Weiter"))');
        expect(activePage).toBe('2');
    });

    test('Eintrag verlinkt auf die Lemma-Seite', async ({ page }) => {
        await page.goto('/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        const href = await page.getAttribute('#entryGrid a >> nth=0', 'href');
        expect(href).toMatch(/^lemma\/\?id=\d+$/);
    });

    test('Nav-Link Wörterbuch ist auf der Startseite vorhanden', async ({ page }) => {
        await page.goto('/index.html');
        const navLink = page.locator('header a[data-nav="woerterbuch"]').first();
        await expect(navLink).toHaveText(/Wörterbuch/);
    });

    // #467: Suche nach der Lemma-Nummer. lemma_4086 ist "mer" (KZWs Beispiel),
    // gemessen am Authority-Index 2026-09-23.
    test('Lemma-Nummer findet genau dieses Lemma (#467)', async ({ page }) => {
        await page.goto('/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        for (const eingabe of ['lemma_4086', 'lexicon.xml#lemma_4086']) {
            await page.fill('#lemmaSearch', eingabe);
            await expect(page.locator('#letterHeading')).toHaveText(`"${eingabe}" – 1 Treffer`);
            await expect(page.locator('#entryGrid a')).toHaveCount(1);
            await expect(page.locator('#entryGrid a')).toHaveText('mer');
            await expect(page.locator('#entryGrid a')).toHaveAttribute('href', 'lemma/?id=4086');
            await expect(page.locator('#entryGrid [data-lemma-number]')).toHaveText('lemma_4086');
        }

        await page.fill('#lemmaSearch', 'lemma_999999999');
        await expect(page.locator('#letterHeading')).toHaveText('Keine Treffer für "lemma_999999999"');
    });

    test('nackte Zahl: Nummer zuerst, Ziffern-Lemmata bleiben (#467)', async ({ page }) => {
        // "36" ist lemma_36 (aberelle) UND ein Lemma, das mit der Ziffer beginnt
        // (lemma_69748 "36"); die Praefixsuche darf dabei nicht verloren gehen.
        // Bis #228 stand hier "46"; dessen Lemma lemma_69733 ist mit dem
        // Apparat entfallen. "36" bleibt, solange die Ziffern in MR1/WVV
        // annotiert sind (offene Frage in #228).
        await page.goto('/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        await page.fill('#lemmaSearch', '36');
        await expect(page.locator('#letterHeading')).toHaveText('"36" – 2 Treffer');
        const eintraege = page.locator('#entryGrid a');
        await expect(eintraege).toHaveText(['aberelle', '36']);
        await expect(page.locator('#entryGrid [data-lemma-number]')).toHaveCount(1);
        await expect(page.locator('#entryGrid [data-lemma-number]')).toHaveText('lemma_36');
    });
});
