/**
 * Kookkurrenz-Ranking + Multi-Lemma-Auflösung Tests (#163, #164)
 *
 * #163: Das Autocomplete-Dropdown zeigt Homographen mit verschiedenen IDs an,
 * aber die Auswahl kam nie bei der Suche an — resolveQuery() löste den
 * Orthographie-String erneut auf und nahm matches[0]. Die Tests verifizieren,
 * dass (a) die Default-Auflösung frequenz-sortiert ist (ADJ rôt, 1567 Belege,
 * schlägt den Eigennamen "Rot" mit 1 Beleg) und (b) eine explizite
 * Dropdown-Auswahl eines selteneren Homographen durchgereicht wird.
 *
 * #164: Multi-Lemma-Suche "rôt + munt" lieferte 0 Treffer, weil rôt auf
 * lemma_11330 "Rot" (NAM) statt lemma_4954 "rôt" (ADJ) auflöste. Ground
 * Truth: alte MHDBDB liefert für rot+munt 553 Zeilen-Treffer; der
 * Corpus-Index enthält 366 Nähe-Kookkurrenzen (dist=10) in 98 Texten.
 */

import { test, expect } from '@playwright/test';

test.describe('Issue #163: Kookkurrenz-Dropdown-Homographen', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#cooccurrence-ranking');
    await page.waitForSelector('#coRkSearchBtn', { state: 'visible', timeout: 60000 });
  });

  test('Default-Auflösung wählt frequentesten Homographen (rot → ADJ rôt)', async ({ page }) => {
    await page.fill('#coRkQuery', 'rot');
    await page.press('#coRkQuery', 'Escape'); // Autocomplete schließen
    await page.click('#coRkSearchBtn');

    // Header muss das Adjektiv lemma_4954 zeigen, nicht den Eigennamen
    await expect(page.locator('#resultsContainer')).toContainText('lemma_4954', { timeout: 60000 });
    await expect(page.locator('#resultsContainer')).toContainText('ADJ');
  });

  test('Dropdown-Auswahl eines selteneren Homographen wird durchgereicht', async ({ page }) => {
    await page.fill('#coRkQuery', 'rôt');
    // Autocomplete zeigt alle Homographen mit ID + POS
    await page.waitForSelector('#coRkAutocomplete button', { state: 'visible', timeout: 15000 });

    // Explizit den Eigennamen lemma_11330 "Rot" (NAM) anklicken — NICHT der
    // frequenz-sortierte Default. Vor dem Fix gewann trotzdem matches[0].
    await page.click('#coRkAutocomplete button:has-text("lemma_11330")');

    // Die Suche muss mit dem GEWÄHLTEN Lemma laufen (1 Vorkommen im Korpus)
    await expect(page.locator('#resultsContainer')).toContainText('lemma_11330', { timeout: 60000 });
    await expect(page.locator('#resultsContainer')).not.toContainText('lemma_4954');
  });
});

test.describe('Issue #164: Multi-Lemma-Suche rôt + munt', () => {
  test('resolveLemmaIds löst rôt auf das Adjektiv-Lemma auf', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');
    await page.waitForFunction(() => {
      return window.playground?.corpusData?.texts?.length > 0 &&
             window.playground?.ui?.multiLemmaSearch;
    }, { timeout: 60000 });

    const ids = await page.evaluate(() => {
      return window.playground.ui.multiLemmaSearch.teiExplorer.resolveLemmaIds(['rôt', 'munt']);
    });
    expect(ids).toEqual(['4954', '4252']);
  });

  test('Nähe-Suche rôt+munt liefert Treffer (Route-E2E)', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma&lemmata=r%C3%B4t,munt&mode=proximity&dist=10');

    // 366 Kookkurrenzen in 98 Texten erwartet — auf jeden Fall nicht "(0 Treffer)"
    await expect(page.locator('#resultsContainer')).toContainText('Nähe-Beziehungen', { timeout: 120000 });
    const text = await page.locator('#resultsContainer').textContent();
    expect(text).not.toContain('(0 Treffer)');
  });
});
