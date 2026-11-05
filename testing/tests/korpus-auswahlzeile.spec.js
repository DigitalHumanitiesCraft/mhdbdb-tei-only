/**
 * #585: Auswahlzeile in der schmalen Suchspalte
 *
 * Bei 1280 px, nach einer Suche (dreispaltiges Raster 1fr 1fr 2fr) und mit
 * Text im Textfilter blieben dem Label "Texte auswählen, TEI anzeigen und Text
 * lesen" neben "Alle | Keine | Nur diese" so wenig Platz, dass es in
 * sechs Reihen umbrach (140 px hoch, gemessen 05.11.2026). Die Zeile
 * darf jetzt umbrechen: passt das Label nicht neben die Knöpfe, bekommt es die
 * ganze Breite und die Knöpfe rutschen darunter.
 *
 * Geprüft wird deshalb, dass das Label einzeilig ist oder die ganze Kopfzeile
 * füllt, nicht eine feste Zeilenzahl: die hängt an der Schrift. Unter Windows
 * braucht das Label bei 1280 px zwei Zeilen, im Nachtlauf unter Linux drei
 * (76 px, Lauf 42081944953). Drei Zeilen sind die obere Grenze.
 *
 * Relative Pfade gegen baseURL.
 */

import { test, expect } from '@playwright/test';

for (const breite of [1280, 1568, 1920]) {
  test(`#585: Label einzeilig oder volle Breite bei ${breite} px, Knöpfe sichtbar`, async ({ page }) => {
    test.setTimeout(120000);
    await page.setViewportSize({ width: breite, height: 900 });
    await page.goto('/korpus.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 90000 });

    await page.fill('#searchInput', 'minne');
    await page.click('#searchButton');
    await expect(page.locator('#resultsSection')).toBeVisible({ timeout: 60000 });

    await page.fill('#textFilter', 'Parzival');
    // "Nur diese" erscheint erst, wenn der Filter wirkt
    await expect(page.locator('#selectOnlyVisible')).toBeVisible();

    const m = await page.locator('#textSelectionHeader label').evaluate(el => {
      const lh = parseFloat(getComputedStyle(el).lineHeight) || 20;
      // Das Label ist selbst ein Flex-Container (gap-2): n Zeilen = n Zeilenhöhen + (n-1) Zeilenabstände
      const gap = parseFloat(getComputedStyle(el).rowGap) || 0;
      return {
        h: el.getBoundingClientRect().height,
        w: el.getBoundingClientRect().width,
        kopf: el.parentElement.clientWidth,
        lh, gap,
      };
    });
    console.log(`Label ${breite}px: Höhe ${m.h}, Breite ${m.w} von ${m.kopf}, Zeilenhöhe ${m.lh}, Zeilenabstand ${m.gap}`);
    const einzeilig = m.h <= m.lh + 2;
    const volleBreite = m.w >= m.kopf - 1;
    expect(einzeilig || volleBreite, 'Label einzeilig oder über die ganze Kopfzeile').toBe(true);
    expect(m.h).toBeLessThanOrEqual(m.lh * 3 + m.gap * 2 + 2);

    for (const id of ['#selectAllTexts', '#selectNoneTexts', '#selectOnlyVisible']) {
      const b = page.locator(id);
      await expect(b).toBeVisible();
      await b.click({ trial: true });
    }
  });
}
