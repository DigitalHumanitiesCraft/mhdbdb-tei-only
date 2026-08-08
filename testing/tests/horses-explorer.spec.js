/**
 * Arthurische Pferde (#193, Beta)
 *
 * Smoke-Tests fuer das kuratierte Pferde-Modul: Route #horses, Pferdeauswahl,
 * Ereignisfilter, Pflicht-Attribution und der Deep-Link in die Leseansicht.
 *
 * Datengrundlage ist data/horses-index.json.gz aus Luise Boreks CC0-Datensatz
 * (hdl:tudatalib/3695). Die Quelle ist statisch und per sha256 im Index
 * festgehalten, anders als beim Naming-Index gibt es keinen woechentlichen
 * Rebuild. Exakte Zahlen sind hier deshalb ein legitimer Lock: 13 Pferde,
 * 346 Belege, davon 120 zu Gringuljete.
 *
 * Der letzte Test ist der wichtigste. Er prueft ?verseId=, den Deep-Link ueber
 * die Wort-ID: ?verse= wuerde hier still das Falsche treffen, weil im Parzival
 * <l n> nur innerhalb des Dreissigers zaehlt.
 */

import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:8080';

test.describe('Arthurische Pferde (#193)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE}/playground/#horses`);
    // dispatchFromHash() laeuft erst nach Corpus-Load; danach laedt das Modul
    // seinen eigenen Index lazy (fetch+pako, 11 KB)
    await page.waitForSelector('#hxHorseSelect', { state: 'visible', timeout: 60000 });
  });

  async function selectGringuljete(page) {
    await page.selectOption('#hxHorseSelect', 'Gringuljete');
    await page.waitForSelector('#resultsContainer table', { state: 'visible', timeout: 5000 });
  }

  test('Route #horses rendert Modul mit 13 Pferden und Attribution', async ({ page }) => {
    await expect(page.locator('#resultsContainer')).toContainText('Arthurische Pferde');

    // 13 Pferde plus Platzhalter-Option
    const options = await page.locator('#hxHorseSelect option').allTextContents();
    expect(options.length).toBe(14);
    expect(options.join(' ')).toContain('Gringuljete');
    expect(options.join(' ')).toContain('ungenanntes Pferd');

    // Attribution muss ohne Auswahl sichtbar sein: der Datensatz ist CC0,
    // die Nennung ist trotzdem Pflicht (Konvention der Rubrik, #194)
    await expect(page.locator('#resultsContainer')).toContainText('Arthurische Pferde nach Luise Borek');
    await expect(page.locator('#resultsContainer a[href*="tudatalib"]')).toBeVisible();
    await expect(page.locator('#resultsContainer')).toContainText('CC0 1.0');
  });

  test('Pferdeauswahl liefert Summary, Ereignis-Tabs und Belegtabelle', async ({ page }) => {
    await selectGringuljete(page);

    // Gringuljete ist das einzige Pferd in zwei Werken
    await expect(page.locator('#resultsContainer')).toContainText('Parzival, Erec');
    await expect(page.locator('#resultsContainer')).toContainText('120');
    // Schreibvarianten aus Boreks <orth>
    await expect(page.locator('#resultsContainer')).toContainText('Gringalet');

    const rows = page.locator('#resultsContainer tbody tr');
    expect(await rows.count()).toBe(120);
  });

  test('Ereignis-Tab filtert die Belege', async ({ page }) => {
    await selectGringuljete(page);
    const alle = await page.locator('#resultsContainer tbody tr').count();

    const tab = page.locator('[data-hx-event]:not([data-hx-event="all"])').first();
    const label = (await tab.textContent()).trim().split(/\s+/)[0];
    await tab.click();
    await page.waitForSelector('#resultsContainer tbody tr', { state: 'visible', timeout: 5000 });

    const gefiltert = await page.locator('#resultsContainer tbody tr').count();
    expect(gefiltert).toBeGreaterThan(0);
    expect(gefiltert).toBeLessThan(alle);
    // Jede sichtbare Zeile traegt das Badge des gewaehlten Ereignisses
    const zellen = await page.locator('#resultsContainer tbody tr td:nth-child(3)').allTextContents();
    for (const z of zellen) expect(z).toContain(label);
  });

  test('Belege zeigen Boreks Zitation und verlinken ueber verseId', async ({ page }) => {
    await selectGringuljete(page);

    // Sichtbar ist IMMER Boreks Angabe, nicht unser aufgeloester Vers
    await expect(page.locator('#resultsContainer')).toContainText('Pz. 339,24');

    const link = page.locator('#resultsContainer a[href*="verseId=PZ_"]').first();
    await expect(link).toBeVisible();

    // Der verschobene Block: Boreks 339,24 zeigt auf unser PZ_33926
    const shifted = page.locator('#resultsContainer a', { hasText: 'Pz. 339,24' });
    await expect(shifted).toHaveAttribute('href', /verseId=PZ_33926/);
    // und traegt den Hinweis, dass die Zaehlung abweicht
    const zelle = page.locator('#resultsContainer tbody tr', { hasText: 'Pz. 339,24' }).first();
    await expect(zelle.locator('[title*="abweichend"]')).toBeVisible();
  });

  test('verseId springt im Reader auf den richtigen Vers', async ({ page }) => {
    // Der Kern des Deep-Links: ?verse=26 waere im Parzival mehrdeutig (rund
    // 800 Verse tragen <l n="26">), ?verseId=PZ_33926 ist es nicht.
    await page.goto(`${BASE}/korpus.html?textId=PZ&verseId=PZ_33926`);
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

    const ziel = page.locator('#readingBody .verse-line[data-core="33926"]');
    await expect(ziel).toHaveCount(1);
    // Der Vers, auf den Borek mit 339,24 zeigt
    await expect(ziel).toContainText('gürten');

    // Die Seite ist tatsaechlich dorthin gescrollt, nicht nur gerendert
    await expect.poll(() => page.evaluate(() => window.scrollY), { timeout: 10000 })
      .toBeGreaterThan(100);
  });

  test('verseId findet auch den Ambraser Einschub, der kein eigenes <l> hat', async ({ page }) => {
    // Der ganze Einschub steht als <supplied> in EINEM <l n="4629"> und deckt
    // die Kerne 462900 bis 462957 ab. Zehn Belege zeigen dorthin; mit nur dem
    // ersten Kern am <l> faenden sie ihr Ziel nicht und der Sprung liefe
    // stumm ins Leere. Deshalb traegt ein mehrversiges <l> data-core-max.
    await page.goto(`${BASE}/korpus.html?textId=ER&verseId=ER_462918`);
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

    const einschub = page.locator('#readingBody .verse-line[data-core="462900"][data-core-max="462957"]');
    await expect(einschub).toHaveCount(1);
    await expect(einschub).toContainText(/walwân/i);

    await expect.poll(() => page.evaluate(() => window.scrollY), { timeout: 10000 })
      .toBeGreaterThan(100);
  });
});
