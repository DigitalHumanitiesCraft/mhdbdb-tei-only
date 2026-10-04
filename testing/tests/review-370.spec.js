import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

// Prüfseite #370 Punkt 2 (ingest/wzb/370-corresp/pruefseite-370.html): 29 Karten
// (PRUEFSEITE-Paare), Tabelle aller 484 Paare im Fuß.
const url = pathToFileURL(resolve(import.meta.dirname, '../../ingest/wzb/370-corresp/pruefseite-370.html')).href;

test.beforeEach(async ({ page }) => {
  await page.goto(url);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

async function exported(page) {
  const wait = page.waitForEvent('download');
  await page.locator('#export-json').click();
  const d = await wait;
  return JSON.parse(await readFile(await d.path(), 'utf8'));
}

test('29 Karten, alle unbearbeitet, Tabelle mit 484 Paaren, kein Rückwärtsstrich', async ({ page }) => {
  await expect(page.locator('article.fall')).toHaveCount(29);
  const start = await exported(page);
  expect(start.format).toBe('mhdbdb-pruefseite');
  expect(start.kennung).toBe('mhdbdb-370-wzb-corresp');
  expect(start.antworten).toHaveLength(29);
  expect(start.antworten.every(a => a.stand === 'unbearbeitet' && !a.antwort)).toBe(true);
  // jede Karte nennt einen Vorschlag, und der Vorschlag ist keine Antwort
  expect(start.antworten.every(a => a.vorschlag)).toBe(true);
  const text = await page.locator('body').innerText();
  expect(text).not.toContain('`');
  const summen = await page.locator('details > summary').allInnerTexts();
  expect(summen.join('|')).toContain('von 484 Paaren');
});

test('Antwort, Kommentar und Stand überleben Neuladen; Export und Import laufen rund', async ({ page }) => {
  await page.locator('#name').fill('Testperson');
  const karte = page.locator('article.fall').first();
  await karte.locator('input[type=radio]').nth(2).check();
  await karte.locator('textarea.komm').fill('Kommentar mit äöü');
  await karte.locator('.stand-wahl button[data-stand="offen"]').click();
  const gespeichert = await exported(page);
  const a0 = gespeichert.antworten[0];
  expect(a0.stand).toBe('offen');
  expect(a0.antwort).toBeTruthy();
  expect(a0.kommentar).toBe('Kommentar mit äöü');
  expect(gespeichert.bearbeiterin).toBe('Testperson');

  // Speichern ist entprellt (350 ms): erst neu laden, wenn der Browser es hat
  await expect.poll(() => page.evaluate(() => Object.keys(localStorage)
    .some(k => (localStorage.getItem(k) || '').includes('Kommentar mit')))).toBe(true);
  await page.reload();
  expect((await exported(page)).antworten).toEqual(gespeichert.antworten);

  await page.evaluate(() => localStorage.clear());
  await page.reload();
  page.on('dialog', d => d.accept());
  await page.locator('#import').setInputFiles({
    name: 'export.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(gespeichert)),
  });
  const zurueck = await exported(page);
  expect(zurueck.antworten[0]).toMatchObject({ stand: 'offen', kommentar: 'Kommentar mit äöü' });
});

test('Import einer fremden Prüfseite wird abgelehnt', async ({ page }) => {
  let meldung = '';
  page.on('dialog', async d => { meldung = d.message(); await d.accept(); });
  await page.locator('#import').setInputFiles({
    name: 'fremd.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ format: 'mhdbdb-pruefseite', kennung: 'anderes', antworten: [] })),
  });
  await expect.poll(() => meldung).toContain('anderen Prüfseite');
  expect((await exported(page)).antworten.every(a => a.stand === 'unbearbeitet')).toBe(true);
});
