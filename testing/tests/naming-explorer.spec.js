/**
 * Naming-Explorer Tests (#59 Erweiterte Figurenbezeichnungen, Beta)
 *
 * Smoke-Tests fuer das kuratierte Figurenbezeichnungs-Modul: Route #naming,
 * Werk/Figur-Auswahl, Kategorie-Tabs, Belegstellen-Expand, MHG-normalisierter
 * Term-Filter und Pflicht-Attribution (Lizenzauflage CC BY-NC-SA).
 *
 * Datengrundlage ist data/naming-index.json.gz (extern kuratiert, lindabeutel/
 * Naming-analysis). Die Tests locken Struktur, nicht exakte Zahlen — bei einem
 * Quelldaten-Update muss nur der weiche Iwein-Lock (242 Belege) mitwandern.
 */

import { test, expect } from '@playwright/test';

test.describe('Naming Explorer (#59)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#naming');
    // dispatchFromHash() laeuft erst nach Corpus-Load; danach laedt das Modul
    // seinen eigenen Index lazy (fetch+pako, ~110 KB)
    await page.waitForSelector('#neWorkSelect', { state: 'visible', timeout: 60000 });
  });

  async function selectIwein(page) {
    await page.selectOption('#neWorkSelect', 'IW');
    await page.selectOption('#neFigureSelect', 'Iwein');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
  }

  test('Route #naming rendert Modul mit allen 4 Werken und Attribution', async ({ page }) => {
    // Beta-Modul-Header
    await expect(page.locator('#resultsContainer')).toContainText('Erweiterte Figurenbezeichnungen');

    // Genau die 4 kuratierten Werke (plus Platzhalter-Option)
    const values = await page.locator('#neWorkSelect option').allTextContents();
    expect(values.join(' ')).toContain('IW - Iwein');
    expect(values.join(' ')).toContain('ENE - Eneasroman');
    expect(values.join(' ')).toContain('ROL - Rolandslied');
    expect(values.join(' ')).toContain('TRO - Trojanerkrieg');
    expect(values.length).toBe(5);

    // Pflicht-Attribution (Lizenzauflage) muss ohne Auswahl sichtbar sein
    await expect(page.locator('#resultsContainer')).toContainText('Naming-analysis nach Linda Beutel-Thurow');
    await expect(page.locator('#resultsContainer a[href*="doi.org/10.5281/zenodo.18770138"]')).toBeVisible();
  });

  test('Werk + Figur liefert Summary und Term-Tabelle mit drei Kategorien', async ({ page }) => {
    await selectIwein(page);

    // Weicher Daten-Lock: Iwein hat 242 kuratierte Belegstellen (Stand edd39cc)
    await expect(page.locator('#resultsContainer')).toContainText('242 kuratierte Belegstellen');

    // Alle drei Kategorien kommen in der Tabelle vor
    const badges = await page.locator('[data-ne-term] td:nth-child(2)').allTextContents();
    const badgeSet = new Set(badges.map(b => b.trim()));
    expect(badgeSet.has('Eigenname')).toBe(true);
    expect(badgeSet.has('Antonomasie')).toBe(true);
    expect(badgeSet.has('Epitheton')).toBe(true);

    // Top-Term ist nach Haeufigkeit sortiert (hoechster Count zuerst)
    const counts = await page.locator('[data-ne-term] td:nth-child(3)').allTextContents();
    const nums = counts.map(c => parseInt(c.replace(/\./g, ''), 10));
    expect(nums[0]).toBe(Math.max(...nums));
  });

  test('Kategorie-Tab filtert auf Epitheta', async ({ page }) => {
    await selectIwein(page);

    await page.click('[data-ne-cat="epi"]');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    const badges = await page.locator('[data-ne-term] td:nth-child(2)').allTextContents();
    expect(badges.length).toBeGreaterThan(0);
    for (const b of badges) {
      expect(b.trim()).toBe('Epitheton');
    }
  });

  test('Belegstellen-Expand zeigt Vers, Phrase und Sprecher', async ({ page }) => {
    await selectIwein(page);

    await page.locator('[data-ne-term]').first().click();

    // Evidence-Row: Versangabe + Sprecher-Label
    await expect(page.locator('#resultsContainer')).toContainText(/V\. \d/);
    await expect(page.locator('#resultsContainer')).toContainText(/Erzähler|Figurenrede|Selbstnennung/);
  });

  test('TRO-Belegstellen verlinken in die Leseansicht, IW-Belegstellen nicht', async ({ page }) => {
    // TRO/ROL: Verszählung deckungsgleich mit MHDBDB -> Vers-Deep-Link
    await page.selectOption('#neWorkSelect', 'TRO');
    await page.selectOption('#neFigureSelect', 'Achilles');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    await page.locator('[data-ne-term]').first().click();

    const link = page.locator('#resultsContainer a[href*="korpus.html?textId=TRO&verse="]').first();
    await expect(link).toBeVisible();
    await expect(link).toContainText(/V\. \d/);

    // IW: abweichende Editionszählung -> bewusst kein Link
    await selectIwein(page);
    await page.locator('[data-ne-term]').first().click();
    await expect(page.locator('#resultsContainer')).toContainText(/V\. \d/);
    await expect(page.locator('#resultsContainer a[href*="verse="]')).toHaveCount(0);
  });

  test('Term-Filter ist MHG-normalisiert (tore findet tôre)', async ({ page }) => {
    await selectIwein(page);

    await page.fill('#neNameFilter', 'tore');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    const terms = await page.locator('[data-ne-term] td:nth-child(1)').allTextContents();
    expect(terms.length).toBeGreaterThan(0);
    expect(terms.some(t => t.includes('tôre'))).toBe(true);
  });

  test('Werk-Wechsel setzt Figur zurueck', async ({ page }) => {
    await selectIwein(page);

    await page.selectOption('#neWorkSelect', 'ROL');
    // Figur-Select ist zurueckgesetzt, Tabelle weg, Hinweis sichtbar
    await expect(page.locator('#neFigureSelect')).toHaveValue('');
    await expect(page.locator('#resultsContainer')).toContainText('Bitte eine Figur auswählen');
  });
});
