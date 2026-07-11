/**
 * Multi-Lemma-Suchmodus „Im selben Vers" Tests (#106 Punkt 8)
 *
 * Verifiziert den dritten Suchmodus der Multi-Lemma-Suche: Kookkurrenz
 * beschränkt auf ein gemeinsames <l>, via lineStarts[]/lineEnds[]-Binärsuche
 * (Corpus-Index v4.1.0+). Ground-Truth aus dem PR (#211): „minne + herze"
 * liefert korpusweit 64 Vers-Treffer in 18 Texten, z. B. BUH Vers 98
 * („dâ bî ûz ir herzen blüejet || diu vil süeze minne").
 */

import { test, expect } from '@playwright/test';

test.describe('Issue #106.8: Multi-Lemma-Modus „Im selben Vers"', () => {
  test('Hash-Route mode=verse liefert Vers-Kookkurrenzen (minne + herze)', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma&lemmata=minne,herze&mode=verse');

    // Ergebnis-Header weist den Vers-Modus aus
    await expect(page.locator('#resultsContainer')).toContainText('(im selben Vers)', { timeout: 120000 });

    // Treffer tragen die Vers-Angabe statt eines Wortabstands
    await expect(page.locator('#resultsContainer')).toContainText('Gemeinsam in Vers');
    const results = await page.locator('#resultsContainer').textContent();
    expect(results).not.toContain('undefined');
    expect(results).not.toContain('null');
  });

  test('Unbekannter mode-Wert fällt auf Proximity zurück', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#multi-lemma&lemmata=minne,herze&mode=quatsch');

    // Fallback: Proximity-Ergebnisse (Wortabstand), kein Vers-Header
    await expect(page.locator('#resultsContainer')).toContainText('Kookkurrenz-Analyse', { timeout: 120000 });
    await expect(page.locator('#resultsContainer')).not.toContainText('(im selben Vers)');
  });
});
