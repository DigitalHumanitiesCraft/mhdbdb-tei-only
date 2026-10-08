/**
 * Router-Start ohne Korpus-Index (#535)
 *
 * Der Playground startet den Router nach dem Authority-Index, nicht erst nach
 * dem Korpus-Index. Eine Route ohne Korpus-Bedarf rendert damit, waehrend der
 * Korpus-Index noch laedt; eine Korpus-Route wartet und rendert danach.
 *
 * Der Korpus-Index wird hier per page.route zurueckgehalten, bis der Test ihn
 * freigibt. Deshalb kalter Context aus '@playwright/test' und nicht
 * warm-page.js: im warmen Context kaeme der Index aus IndexedDB, die Route
 * feuerte nie, und der Test bewiese nichts.
 */

import { test, expect } from '@playwright/test';

/** Haelt corpus-index.json.gz zurueck; freigeben() laesst ihn durch. */
async function korpusZurueckhalten(page) {
  let freigeben;
  const frei = new Promise(resolve => { freigeben = resolve; });
  let angefragt = false;
  await page.route('**/data/corpus-index.json.gz', async route => {
    angefragt = true;
    await frei;
    await route.continue();
  });
  return { freigeben: () => freigeben(), angefragt: () => angefragt };
}

test.describe('Playground-Router startet vor dem Korpus-Index (#535)', () => {

  test('#naming rendert, waehrend der Korpus-Index noch laedt', async ({ page }) => {
    const korpus = await korpusZurueckhalten(page);
    await page.goto('/playground/#naming');

    await expect(page.locator('#neWorkSelect')).toBeVisible({ timeout: 60000 });
    // Gegenprobe: der Korpus-Index ist angefragt, aber noch nicht da. Ohne sie
    // waere der Test auch gruen, wenn der Index schon geladen gewesen waere.
    expect(korpus.angefragt()).toBe(true);
    await expect(page.locator('#corpusLoadingState')).toBeVisible();

    korpus.freigeben();
    await expect(page.locator('#corpusLoadingState')).toBeHidden({ timeout: 60000 });
  });

  test('#word-frequency wartet auf den Korpus-Index und rendert danach', async ({ page }) => {
    const korpus = await korpusZurueckhalten(page);
    await page.goto('/playground/#word-frequency');

    // init() startet autoLoadCorpus() und ruft gleich danach
    // dispatchFromHash(); der Abruf des Korpus-Index folgt erst nach mehreren
    // awaits darin. Ist er angefragt, ist die Route also schon dispatcht, und
    // ein Router ohne Wartezeit haette #word-frequency bereits gerendert.
    await expect(page.locator('#corpusLoadingState')).toBeVisible({ timeout: 60000 });
    await expect.poll(() => korpus.angefragt(), { timeout: 60000 }).toBe(true);
    await expect(page.locator('#wfCsvExport')).toHaveCount(0);

    korpus.freigeben();
    await expect(page.locator('#wfCsvExport')).toBeVisible({ timeout: 60000 });
  });
});
