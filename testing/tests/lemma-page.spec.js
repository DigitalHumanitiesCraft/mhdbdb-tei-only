/**
 * Lemma Page Tests (Issue #42)
 * Verifies persistent lemma pages load and display correctly
 */

import { test, expect } from '@playwright/test';

test.describe('Persistent Lemma Pages', () => {

    test('lemma page loads with query param (?id=879)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');

        // Wait for loading to complete
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Check title block
        const title = await page.textContent('#lemmaTitle');
        expect(title.length).toBeGreaterThan(0);

        // Check POS badge is present
        const pos = await page.textContent('#lemmaPos');
        expect(pos.length).toBeGreaterThan(0);

        // Check lemma ID displayed
        const displayedId = await page.textContent('#lemmaId');
        expect(displayedId).toBe('lemma_879');
    });

    test('lemma page shows correct data for brôt (879)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // brôt should be a noun
        const title = await page.textContent('#lemmaTitle');
        expect(title).toContain('br');  // brôt or similar MHG form

        // Should have normalized form
        const normalized = await page.textContent('#lemmaNormalized');
        expect(normalized).toContain('brot');

        // Page title should include lemma
        const pageTitle = await page.title();
        expect(pageTitle).toContain('MHDBDB');
    });

    test('lemma page shows corpus occurrences', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Wait a bit for corpus index to load
        await page.waitForSelector('#occurrencesSection:not(.hidden)', { timeout: 30000 });

        // Check occurrence count text is present
        const countText = await page.textContent('#occurrenceCount');
        expect(countText).toContain('Texten');

        // Should have clickable text links
        const links = await page.locator('#occurrencesContent a').count();
        expect(links).toBeGreaterThan(0);
    });

    test('lemma page shows external links', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Should have old MHDBDB link with correct URL
        const mhdbdbLink = page.locator('#externalLinks a:has-text("MHDBDB")');
        await expect(mhdbdbLink).toBeVisible();
        const mhdbdbHref = await mhdbdbLink.getAttribute('href');
        expect(mhdbdbHref).toContain('mhdbdb-old.sbg.ac.at');
        expect(mhdbdbHref).toContain('lid=879');

        // Should have corpus search link
        const corpusLink = page.locator('#externalLinks a:has-text("Korpus")');
        await expect(corpusLink).toBeVisible();
    });

    test('lemma page loads Wörterbuchnetz entries via API', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Wörterbuchnetz section appears after async API call (brôt → brot)
        await page.waitForSelector('#wbnetzSection:not(.hidden)', { timeout: 15000 });

        // Should have at least one dictionary link (MWB or Lexer)
        const wbnLinks = page.locator('#wbnetzLinks a');
        const count = await wbnLinks.count();
        expect(count).toBeGreaterThan(0);

        // Links point to either mhdwb-online.de (MWB) or woerterbuchnetz.de (Lexer)
        // — both come from the Wörterbuchnetz API but the original deep-links
        // differ per dictionary (#73, dcbee3479).
        const firstHref = await wbnLinks.first().getAttribute('href');
        expect(firstHref).toMatch(/(mhdwb-online|woerterbuchnetz)\.de/);
    });

    test('invalid lemma ID shows error', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=99999999');

        // Should show error, not content
        await page.waitForSelector('#errorDisplay:not(.hidden)', { timeout: 30000 });

        const errorText = await page.textContent('#errorMessage');
        expect(errorText).toContain('nicht gefunden');

        // Content should remain hidden
        const contentHidden = await page.locator('#lemmaContent').evaluate(el => el.classList.contains('hidden'));
        expect(contentHidden).toBe(true);
    });

    test('no ID shows error message', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/');

        await page.waitForSelector('#errorDisplay:not(.hidden)', { timeout: 30000 });

        const errorText = await page.textContent('#errorMessage');
        expect(errorText).toContain('Keine Lemma-ID');
    });

    test('minne (4130) - high-frequency lemma loads', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=4130');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        const title = await page.textContent('#lemmaTitle');
        expect(title.length).toBeGreaterThan(0);

        // minne should appear in many texts
        await page.waitForSelector('#occurrencesSection:not(.hidden)', { timeout: 30000 });
        const countText = await page.textContent('#occurrenceCount');
        expect(countText).toContain('Texten');
    });

    test('etymology links point to other lemma pages', async ({ page }) => {
        // lemma_100 (ahzehen) has etymology components
        await page.goto('http://localhost:8080/lemma/?id=100');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Check if etymology section is visible (not all lemmata have etymology)
        const etymVisible = await page.locator('#etymologySection').evaluate(el => !el.classList.contains('hidden'));
        if (etymVisible) {
            const etymLinks = await page.locator('#etymologyContent a.etymology-link').count();
            expect(etymLinks).toBeGreaterThan(0);

            // Links should point to other lemma pages
            const firstHref = await page.locator('#etymologyContent a.etymology-link').first().getAttribute('href');
            expect(firstHref).toMatch(/^\?id=\d+$/); // Query param link
        }
    });

    test('copy ID button exists and is clickable', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Verify button exists and shows initial text
        const btn = page.locator('#copyIdBtn');
        await expect(btn).toBeVisible();
        await expect(btn).toHaveText('kopieren');

        // Click — clipboard API may not work in test context, just verify no error
        await btn.click();
    });

    test('orthographic variants shown for brôt (879)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // brôt should have multiple attested spelling variants
        await page.waitForSelector('#variantsSection:not(.hidden)', { timeout: 5000 });

        const countText = await page.textContent('#variantsCount');
        expect(countText).toMatch(/\(\d+\)/); // e.g. "(23)"

        // Variant links should point to corpus search
        const firstVariant = page.locator('#variantsContent a').first();
        const href = await firstVariant.getAttribute('href');
        expect(href).toContain('korpus.html?search=');
    });

    test('compounds section shown for brôt (879)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // brôt should have compounds (halpbrôt, himelbrôt, etc.)
        await page.waitForSelector('#compoundsSection:not(.hidden)', { timeout: 5000 });

        const countText = await page.textContent('#compoundsCount');
        expect(countText).toMatch(/\(\d+\)/);

        // Compound links should point to other lemma pages (numeric IDs)
        const firstCompound = page.locator('#compoundsContent a').first();
        const href = await firstCompound.getAttribute('href');
        expect(href).toMatch(/^\?id=\d+$/);
    });

    test('IMAREAL link present in external links', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        const imrealLink = page.locator('#externalLinks a:has-text("REALonline")');
        await expect(imrealLink).toBeVisible();
        const href = await imrealLink.getAttribute('href');
        expect(href).toContain('realonline.imareal.sbg.ac.at/suche');
    });

    test('occurrence links navigate to korpus reading view', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#occurrencesSection:not(.hidden)', { timeout: 30000 });

        // Get first occurrence link
        const firstLink = page.locator('#occurrencesContent a').first();
        const href = await firstLink.getAttribute('href');

        // Should link to korpus.html with correct params
        expect(href).toContain('korpus.html');
        expect(href).toContain('textId=');
        // Reader-Highlight braucht den kanonischen lemma_-Präfix (CONTRACTS §B.1);
        // der Belegstellen-Link muss ihn also mitgeben, nicht abstreifen.
        expect(href).toContain('lemmaIds=lemma_879');
    });

    // Kuratierte Angaben (Authority Index v1.7.0): Herkunftssprache aus
    // <etym type="borrowing">, Bedeutung aus <def>, Kommentar aus
    // <note type="comment">. Alle drei sind optional und stehen heute nur an
    // lemma_37818 (Abba) — genau deshalb prüft der zweite Test, dass ein
    // Lemma ohne Kuratierung die Sektion nicht zeigt.
    test('kuratierte Herkunft und Bedeutung erscheinen für Abba (37818)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=37818');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        // Beide Herkunftsschichten samt Code. Die Liste muss deckungsgleich mit
        // den Sprach-Konzepten des Eintrags sein (Kurationsregel in
        // TEI-MODEL-AUTH-FILES §3.1), deshalb wird sie hier gegen beide geprüft.
        await page.waitForSelector('#originSection:not(.hidden)', { timeout: 5000 });
        const origin = await page.textContent('#originContent');
        expect(origin).toContain('Aramäisch');
        expect(origin).toContain('Lateinisch');
        expect(origin).toContain('Bibel');

        // Die Codes gezielt gegen die gerenderten Spans, nicht gegen den
        // Gesamttext: „Lateinisch" und „lateinische Bibel" enthalten den String
        // „la" auch dann, wenn der Code überhaupt nicht angezeigt würde.
        const codes = (await page.locator('#originContent .font-mono').allTextContents())
            .map(c => c.trim());
        expect(codes).toEqual(['arc', 'la']);

        // Definition und Kommentar stehen im Bedeutungs-Block, vor den
        // Begriffs-Chips; der Kommentar trägt ein sichtbares Label.
        const senses = await page.textContent('#sensesContent');
        expect(senses).toContain('Anrede Gottes');
        expect(senses).toContain('Kommentar');
        expect(senses).toContain('ZUK 2377');
        expect(senses).toContain('Markus 14,36');

        // Die neuen Begriffszuordnungen sind sichtbar, die entfernte nicht
        expect(senses).toContain('Aramäisch');
        expect(senses).toContain('Lateinisch');
        expect(senses).toContain('Bibel/Religionsgeschichte');
        expect(senses).not.toContain('Kirchliche Hierarchie');
    });

    test('Lemma ohne kuratierte Herkunft zeigt keine Herkunft-Sektion (879)', async ({ page }) => {
        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });

        const originHidden = await page.locator('#originSection')
            .evaluate(el => el.classList.contains('hidden'));
        expect(originHidden).toBe(true);
    });

    test('occurrence link click-through highlights the lemma in the reader', async ({ page }) => {
        // Audit #12: der href-String-Test allein hatte das kaputte Link-Format
        // zementiert — hier wird der reale Klickpfad bis zum sichtbaren
        // Highlight verifiziert.
        test.setTimeout(120000);

        await page.goto('http://localhost:8080/lemma/?id=879');
        await page.waitForSelector('#occurrencesSection:not(.hidden)', { timeout: 30000 });

        await page.locator('#occurrencesContent a').first().click();

        // Navigiert auf korpus.html; Reader lädt und MUSS Treffer markieren
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        const highlights = page.locator('#readingBody .highlight');
        await expect(highlights.first()).toBeVisible({ timeout: 15000 });
    });
});
