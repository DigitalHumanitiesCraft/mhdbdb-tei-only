/**
 * Editorische Notizen der Weingruß-Transkriptionen (#147) stehen im TEI, aber nicht im Lesetext:
 * <note type="transcription"> und <note type="editorial"> sind Anmerkungen in nhd. Prosa (Bilder,
 * moderne Bleistifteintragungen, Druckvergleiche, Textkritisches); KZW will sie nicht im Lesetext. BRE_D3 trägt Notizen im Verstext
 * ("Links daneben: Bild einer Deutehand.", "Ein Holzschnitt teilt den Ausdruck ...").
 */
import { test, expect } from '@playwright/test';

test('Lesetext von BRE_D3 zeigt keine Transkriptionsnotizen, aber die Verse', async ({ page }) => {
    await page.goto('/korpus.html?search=wein&textId=BRE_D3');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    await expect(page.locator('#readingBody')).toContainText('gsellen', { timeout: 30000 });
    const text = (await page.locator('#readingBody').textContent()).replace(/\s+/g, ' ');
    expect(text).toContain('Nun mercken lieben gsellen mein');
    expect(text).not.toContain('Deutehand');
    expect(text).not.toContain('Holzschnitt');
});
