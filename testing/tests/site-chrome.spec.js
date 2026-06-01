/**
 * Site Chrome Tests
 *
 * The shared, build-injected navigation + footer (includes/_nav.html,
 * includes/_footer.html via scripts/build-pages.py) plus assets/js/site-chrome.js.
 *
 * Covers the feature/site-chrome-refactor review fixes:
 *  - single clear-site-data handler (no double-fire — site-chrome.js is sole owner)
 *  - wiring on app.js-less and subfolder pages (../ path resolution)
 *  - active nav item: aria-current + font-semibold (and NOT a leftover font-medium)
 *  - mobile-menu toggle bound on every page (incl. lemma, which had none before)
 */

import { test, expect } from '@playwright/test';

test.describe('Site Chrome (shared nav/footer + clear-site-data)', () => {

    test('clearSiteData fires exactly one confirm dialog (no double-handler)', async ({ page }) => {
        await page.goto('/impressum.html');

        let dialogCount = 0;
        page.on('dialog', async (d) => { dialogCount++; await d.dismiss(); });

        await expect(page.locator('#clearSiteDataBtn')).toBeVisible();
        await page.click('#clearSiteDataBtn');
        await page.waitForTimeout(500);

        // Regression: site-chrome.js + the old inline handler used to both bind this
        // button, firing two confirm dialogs and racing two clear+reload sequences.
        expect(dialogCount).toBe(1);
    });

    test('clearSiteData wired on lemma subfolder page (../ path resolves)', async ({ page }) => {
        await page.goto('/lemma/index.html?id=879');

        let dialogCount = 0;
        page.on('dialog', async (d) => { dialogCount++; await d.dismiss(); });

        await expect(page.locator('#clearSiteDataBtn')).toBeVisible();
        await page.click('#clearSiteDataBtn');
        await page.waitForTimeout(500);

        // A bound handler proves ../assets/js/site-chrome.js loaded from the subfolder.
        expect(dialogCount).toBe(1);
    });

    test('active nav item gets aria-current + font-semibold (not font-medium)', async ({ page }) => {
        await page.goto('/korpus.html');

        const active = page.locator('header a[aria-current="page"]');
        // desktop + mobile nav each mark the active item
        await expect(active).toHaveCount(2);

        const datanavs = await active.evaluateAll((els) => els.map((e) => e.getAttribute('data-nav')));
        expect(datanavs).toEqual(['korpus', 'korpus']);

        // build-pages.py swaps the whole "font-medium text-slate-600" run, so the
        // active link must not carry both font-medium AND font-semibold.
        const classes = await active.evaluateAll((els) => els.map((e) => e.className));
        expect(classes.every((c) => c.includes('font-semibold') && !c.includes('font-medium'))).toBe(true);
    });

    test('mobile-menu toggle is bound on the lemma page (added in refactor)', async ({ page }) => {
        await page.goto('/lemma/index.html?id=879');

        const btn = page.locator('#mobileMenuButton');
        const menu = page.locator('#mobileMenu');
        await expect(btn).toBeAttached();

        // 'hidden' is an exact class token; the element also carries the separate
        // Tailwind token 'md:hidden', so a /hidden/ regex would always match. Check
        // classList.contains('hidden') for the standalone token instead.
        const hidden = () => menu.evaluate((el) => el.classList.contains('hidden'));

        expect(await hidden()).toBe(true);
        // md:hidden at desktop width -> drive via dispatchEvent (no actionability needed)
        await btn.dispatchEvent('click');
        await expect.poll(hidden).toBe(false);
        await btn.dispatchEvent('click');
        await expect.poll(hidden).toBe(true);
    });

    test('footer logo resolves via ../ on subfolder pages', async ({ page }) => {
        await page.goto('/playground/index.html');

        const loaded = await page.locator('footer img[src$="mhdbdb-logo.png"]').first()
            .evaluate((img) => img.complete && img.naturalWidth > 0);
        expect(loaded).toBe(true);
    });
});
