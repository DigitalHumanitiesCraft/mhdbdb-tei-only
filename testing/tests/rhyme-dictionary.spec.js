/**
 * Reim-Wörterbuch Tests (#106, Minimalvariante)
 *
 * Verifiziert das 10. TEI-Analyse-Werkzeug im Playground: lemma-basierter
 * Versende-Scan über lineEnds[] (Corpus-Index v4.1.x) mit Suffix-Heuristik.
 *
 * Ground-Truth aus dem Issue (#106): AGS („Der altgewordene Sünder") beginnt
 * mit AABB-Reimpaaren, Vers 1/2 enden auf gân / begân — mit Textfilter „AGS"
 * muss „gân" also „begân" als Reimpartner liefern.
 */

import { test, expect } from '@playwright/test';

// Autocomplete legt sich über die Button-Zeile (gleiches Verhalten wie #113
// bei concept-distribution) — Escape schließt es synchron.
async function dismissAutocomplete(page) {
  await page.press('#rdQuery', 'Escape');
}

test.describe('Issue #106: Reim-Wörterbuch (Minimalvariante)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#rhyme-dictionary');
    await page.waitForSelector('#rdSearchBtn', { state: 'visible', timeout: 60000 });
  });

  test('Route + Sidebar-Button öffnen das Modul', async ({ page }) => {
    await expect(page.locator('#rdQuery')).toBeVisible();
    await expect(page.locator('#resultsContainer')).toContainText('Reim-Wörterbuch');

    // Sidebar-Card existiert und navigiert auf die Route
    await expect(page.locator('#showRhymeDictionaryBtn')).toBeVisible();
  });

  test('Ground-Truth AGS: gân reimt auf begân', async ({ page }) => {
    await page.fill('#rdQuery', 'gân');
    await dismissAutocomplete(page);
    await page.fill('#rdTextFilter', 'AGS');
    await page.click('#rdSearchBtn');

    await page.waitForSelector('#resultsContainer table tbody tr', { state: 'visible', timeout: 30000 });
    const tableText = await page.locator('#resultsContainer table').textContent();
    expect(tableText).toContain('begân');
  });

  test('Korpusweiter Scan liefert klassische MHD-Reimpartner (muot : guot)', async ({ page }) => {
    await page.fill('#rdQuery', 'muot');
    await dismissAutocomplete(page);
    await page.click('#rdSearchBtn');

    await page.waitForSelector('#resultsContainer table tbody tr', { state: 'visible', timeout: 60000 });
    const tableText = await page.locator('#resultsContainer table').textContent();
    // „muot ↔ guot" ist laut Audit (#106) das Top-Reimpaar im Iwein (27×) —
    // korpusweit muss guot als Partner auftauchen.
    expect(tableText).toContain('guot');

    // Header weist Versende-Vorkommen und Reimklang aus
    await expect(page.locator('#resultsContainer')).toContainText('Vorkommen am Versende');
    await expect(page.locator('#resultsContainer')).toContainText('-uot');
  });

  test('Unbekanntes Lemma zeigt Amber-Hinweis statt Ergebnis', async ({ page }) => {
    await page.fill('#rdQuery', 'xyzzyplugh');
    await dismissAutocomplete(page);
    await page.click('#rdSearchBtn');

    await expect(page.locator('#resultsContainer')).toContainText('Kein Lemma gefunden', { timeout: 15000 });
  });
});
