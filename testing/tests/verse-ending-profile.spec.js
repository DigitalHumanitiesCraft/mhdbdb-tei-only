/**
 * Versendings-Profil Tests (#106 Punkt 2)
 *
 * Verifiziert das 12. TEI-Analyse-Werkzeug im Playground: Top-N Lemmata an
 * Versenden (lineEnds[]-Scan) mit Scope-Selector (Korpus/Autor*in/Text),
 * Reim-Druck-Spalte und Funktionswort-Filter.
 */

import { test, expect } from '@playwright/test';

test.describe('Issue #106.2: Versendings-Profil', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#verse-ending-profile');
    await page.waitForSelector('#vepScope', { state: 'visible', timeout: 60000 });
  });

  test('Route öffnet das Modul, Korpus-Scope liefert Tabelle mit Reim-Druck-Spalte', async ({ page }) => {
    await expect(page.locator('#resultsContainer')).toContainText('Reim-Druck');
    const rowCount = await page.locator('#resultsContainer table tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('Funktionswort-Filter rendert die Tabelle neu', async ({ page }) => {
    await page.waitForSelector('#resultsContainer table tbody tr', { state: 'visible', timeout: 60000 });

    await page.check('#vepHideFunc');
    await page.waitForSelector('#resultsContainer table tbody tr', { state: 'visible', timeout: 60000 });

    // Datenunabhängige Assertion (Review-Hinweis): sobald ≥1 Funktionswort
    // gefiltert wird, zeigt der Header den Ausgeblendet-Zähler „(–N ausgeblendet)"
    await expect(page.locator('#resultsContainer')).toContainText('ausgeblendet');
    const rowCount = await page.locator('#resultsContainer table tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('Text-Scope zeigt Textmeta statt Korpuslabel', async ({ page }) => {
    // Ein konkreter Vers-Text (IW = Iwein) über das optgroup-Select
    await page.selectOption('#vepScope', 'IW');
    await expect(page.locator('#resultsContainer')).toContainText('IW');
    const rowCount = await page.locator('#resultsContainer table tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);
  });
});
