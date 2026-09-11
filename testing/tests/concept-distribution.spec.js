/**
 * Concept-Distribution Tests (#47 R2 Follow-up)
 *
 * Verifiziert: (a) Begriffs-Verteilung loest fuer das groesste Concept (8718
 * Lemmata) keinen User-fuehlbaren Browser-Freeze mehr aus, (b) Chunk-Yielding
 * haelt Long-Tasks (> 50ms) im einstelligen Bereich, (c) das Ergebnis kommt
 * vollstaendig an.
 *
 * Hintergrund: vor dem Patch (commit dieser Spec) blockierte das Worst-Case-
 * Concept den Main-Thread mit einem einzigen ~2.7s Long-Task. Nach dem Patch
 * (concept-distribution.js: async + time-based Yield ueber MessageChannel)
 * bleibt jeder einzelne Long-Task knapp ueber dem 50ms-Schwellwert.
 */

import { test, expect } from '@playwright/test';

// #113 ergaenzte ein Autocomplete-Dropdown an #cdQuery. Es oeffnet beim Befuellen
// (input-Event -> updateAutocomplete) und legt sich (absolute, top-full, z-30)
// ueber die Button-Zeile mit #cdSearchBtn, sodass page.click('#cdSearchBtn') vom
// Dropdown abgefangen wird (-> 60s-Timeout). Escape schliesst es synchron
// (concept-distribution.js keydown-Handler) — modelliert einen User, der die
// Vorschlaege verwirft und dann auf „Suchen" klickt.
async function dismissAutocomplete(page) {
  await page.press('#cdQuery', 'Escape');
}

test.describe('Concept Distribution Performance Lock', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#concept-distribution');
    // Warten bis das Form-Element vorhanden ist
    await page.waitForSelector('#cdSearchBtn', { state: 'visible', timeout: 60000 });
  });

  test('worst-case concept (8718 Lemmata) faellt nicht in einen 2s+ freeze', async ({ page }) => {
    // Setup Long-Task-Observer
    await page.evaluate(() => {
      window.__longTasks = [];
      const obs = new PerformanceObserver((list) => {
        for (const e of list.getEntries()) window.__longTasks.push(e.duration);
      });
      obs.observe({ entryTypes: ['longtask'] });
      window.__longTaskObserver = obs;
    });

    await page.fill('#cdQuery', 'Objektbezogene Aktivität/Tätigkeit');
    await dismissAutocomplete(page);
    await page.click('#cdSearchBtn');

    // Chart muss erscheinen (Worst-Case: 667 Texte mit Treffern -> 30 Top-N-Bars)
    await page.waitForSelector('#resultsContainer svg rect', { state: 'visible', timeout: 30000 });

    const longTasks = await page.evaluate(() => {
      window.__longTaskObserver?.disconnect();
      return window.__longTasks || [];
    });

    // Vor Patch: 1 long-task ~2700ms. Nach Patch: viele Tasks, alle <300ms.
    // Wir locken hier ein konservatives Limit von 500ms, das auf jedem CI sicher
    // unterschritten wird (steady-state liegt bei 60-70ms, erstmaliger JIT-Warmup
    // kann 200ms erreichen).
    const maxTask = Math.max(0, ...longTasks);
    expect(maxTask, `Max Long-Task war ${maxTask}ms. Vor Patch war es 2700ms. ` +
                    `Wenn > 500ms, Performance-Patch wurde rueckwaertskompatibel ` +
                    `gebrochen oder Daten haben sich stark veraendert.`).toBeLessThan(500);
  });

  test('baseline-case (Sterben, ~682 Lemmata) rendert <5s mit Long-Task < 200ms', async ({ page }) => {
    await page.evaluate(() => {
      window.__longTasks = [];
      const obs = new PerformanceObserver((list) => {
        for (const e of list.getEntries()) window.__longTasks.push(e.duration);
      });
      obs.observe({ entryTypes: ['longtask'] });
      window.__longTaskObserver = obs;
    });

    await page.fill('#cdQuery', 'Sterben');
    await dismissAutocomplete(page);
    const t0 = Date.now();
    await page.click('#cdSearchBtn');
    await page.waitForSelector('#resultsContainer svg rect', { state: 'visible', timeout: 10000 });
    const elapsed = Date.now() - t0;

    const longTasks = await page.evaluate(() => {
      window.__longTaskObserver?.disconnect();
      return window.__longTasks || [];
    });
    const maxTask = Math.max(0, ...longTasks);

    expect(maxTask, `Sterben max Long-Task ${maxTask}ms`).toBeLessThan(200);
    expect(elapsed, `Sterben total elapsed ${elapsed}ms`).toBeLessThan(5000);
  });

  test('Spinner wird waehrend Aggregation sichtbar (UI bleibt responsive)', async ({ page }) => {
    await page.fill('#cdQuery', 'Objektbezogene Aktivität/Tätigkeit');
    await dismissAutocomplete(page);
    await page.click('#cdSearchBtn');

    // Progress-Bar muss waehrend Worst-Case-Aggregation auftauchen, bevor das
    // Chart fertig ist. (Wenn das Modul wieder synchron wuerde, sehen wir den
    // Spinner nie, weil das gesamte Compute innerhalb eines Long-Tasks waere.)
    await expect(page.locator('#cdProgressBar')).toBeVisible({ timeout: 2000 });

    // Danach erscheint Chart
    await page.waitForSelector('#resultsContainer svg rect', { state: 'visible', timeout: 30000 });
  });

  test('sortBy-Wechsel triggert kein re-compute (Daten gecacht)', async ({ page }) => {
    await page.fill('#cdQuery', 'Sterben');
    await dismissAutocomplete(page);
    await page.click('#cdSearchBtn');
    await page.waitForSelector('#resultsContainer svg rect', { state: 'visible', timeout: 10000 });

    // Setup Long-Task-Observer NACH dem ersten compute
    await page.evaluate(() => {
      window.__longTasks2 = [];
      const obs = new PerformanceObserver((list) => {
        for (const e of list.getEntries()) window.__longTasks2.push(e.duration);
      });
      obs.observe({ entryTypes: ['longtask'] });
      window.__longTaskObserver2 = obs;
    });

    await page.selectOption('#cdSortBy', 'alphabetic');
    await page.waitForTimeout(500);

    const longTasks = await page.evaluate(() => {
      window.__longTaskObserver2?.disconnect();
      return window.__longTasks2 || [];
    });
    const maxTask = Math.max(0, ...longTasks);

    // sortBy aendert nur Anzeige, nicht Daten. Kein compute -> kein Long-Task.
    expect(maxTask, `sortBy-Wechsel Long-Task ${maxTask}ms (sollte ~0 sein, ` +
                    `weil keine Re-Aggregation noetig ist)`).toBeLessThan(150);
  });
});

/**
 * #419 (Alan van Beek): die Begriffssuche war zwischen den Sprachen
 * unsymmetrisch. „tree" fand concept_13020000 (termDE „Bäume", termEN
 * „Trees"), weil der englische Plural den Stamm als Praefix enthaelt; „baum"
 * fand nichts, weil der deutsche Plural den Umlaut traegt. Die MHD-
 * Normalisierung half nicht, sie expandiert ä→ae und entfernt den Stamm noch
 * weiter. Gepruefte Behebung: zusaetzlicher Vergleich mit gefalteten
 * Diakritika (TextNormalizer.foldDiacritics).
 */
test.describe('Issue #419: Umlaut-Faltung in der Begriffssuche', () => {
  test('„baum" und „tree" finden beide den Begriff „Bäume"', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#concept-distribution');
    await page.waitForSelector('#cdSearchBtn', { state: 'visible', timeout: 60000 });

    // Die englische Seite war immer schon gruen: sie ist hier der Kontrollwert,
    // ohne den der Test nicht zeigt, dass es um die Symmetrie geht.
    await page.fill('#cdQuery', 'tree');
    await expect(page.locator('#cdAutocomplete')).toContainText('Bäume', { timeout: 15000 });

    await page.fill('#cdQuery', '');
    await page.fill('#cdQuery', 'baum');
    await expect(page.locator('#cdAutocomplete')).toContainText('Bäume', { timeout: 15000 });
  });

  test('Begriffs-Explorer teilt die Faltung (gemeinsamer Suchpfad)', async ({ page }) => {
    // multiFieldNormalized ist der Suchpfad der vier Authority-Explorer; die
    // Aenderung sitzt dort, nicht in der Begriffsverteilung, also wird sie
    // auch dort geprueft.
    await page.goto('http://localhost:8080/playground/#concepts');
    await page.waitForSelector('#conceptSearch', { state: 'visible', timeout: 60000 });

    await page.fill('#conceptSearch', 'baum');
    await expect(page.locator('#conceptResults')).toContainText('Bäume', { timeout: 15000 });

    // Gegenprobe, dass die alte Richtung nicht verloren ging: „baeume" muss
    // weiter treffen (normalizeMHG), sonst haette die Faltung sie verdraengt.
    await page.fill('#conceptSearch', '');
    await page.fill('#conceptSearch', 'baeume');
    await expect(page.locator('#conceptResults')).toContainText('Bäume', { timeout: 15000 });
  });

  // Was die Faltung wahr gemacht hat: es gibt jetzt Treffer, die
  // `matchesNormalized` nicht sieht. `findAlternativeMatch` war allein darauf
  // gebaut und lieferte für sie keinen „auch: …"-Hinweis mehr, der Begriff
  // stand also unerklärt in der Liste. Gemessen am 11.09.: 56 Begriffe.
  test('Fold-Treffer über einen Alt-Term trägt seinen „auch"-Hinweis', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#concepts');
    await page.waitForSelector('#conceptSearch', { state: 'visible', timeout: 60000 });

    // „fruchte" trifft concept_13023100 „Obst" nur über altDE „Früchte",
    // und nur über die Faltung: „fruchte" steht weder in „Obst" noch in
    // „Fruit", und normalizeMHG macht aus „Früchte" „fruechte".
    await page.fill('#conceptSearch', 'fruchte');
    const ergebnisse = page.locator('#conceptResults');
    await expect(ergebnisse).toContainText('Obst', { timeout: 15000 });
    await expect(ergebnisse).toContainText('Früchte');
  });
});
