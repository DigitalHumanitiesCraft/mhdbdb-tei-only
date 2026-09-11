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

  // #419 (Alan van Beek, Testfall 8): stand der Filter hoeher als der beste
  // Partner, meldete das Werkzeug „kein benachbartes Versende mit
  // uebereinstimmendem Reimklang" und verschwieg den selbst gesetzten Wert.
  // Dieser Test faehrt beide Faelle nacheinander am selben Lemma, damit die
  // Unterscheidung geprueft wird und nicht nur das Vorhandensein eines Textes.
  test('Mindest-Reimpaare-Filter nennt sich in der Leermeldung', async ({ page }) => {
    await page.fill('#rdQuery', 'gân');
    await dismissAutocomplete(page);
    await page.fill('#rdTextFilter', 'AGS');
    await page.click('#rdSearchBtn');
    await page.waitForSelector('#resultsContainer table tbody tr', { state: 'visible', timeout: 30000 });

    // Vorbedingung: es GIBT Partner. Ohne sie pruefte der Rest nichts.
    const partnerZeilen = await page.locator('#resultsContainer table tbody tr:not([data-rd-belege-row])').count();
    expect(partnerZeilen).toBeGreaterThan(0);

    // Filter ueber jeden moeglichen Partnerwert heben.
    await page.fill('#rdMinCount', '9999');
    await page.press('#rdMinCount', 'Enter');
    await page.locator('#rdMinCount').blur();

    const container = page.locator('#resultsContainer');
    await expect(container).toContainText('Mindest-Reimpaare 9999', { timeout: 15000 });
    await expect(container).toContainText('Häufigster Partner');
    // Genau das ist die Meldung, die den Filter verschwieg.
    await expect(container).not.toContainText('kein benachbartes Versende');
    // Die Kopfzeile darf die Gesamtmenge nicht mehr unterschlagen.
    await expect(container).toContainText('0 von');
  });

  test('Unbekanntes Lemma zeigt Amber-Hinweis statt Ergebnis', async ({ page }) => {
    await page.fill('#rdQuery', 'xyzzyplugh');
    await dismissAutocomplete(page);
    await page.click('#rdSearchBtn');

    await expect(page.locator('#resultsContainer')).toContainText('Kein Lemma gefunden', { timeout: 15000 });
  });
});
