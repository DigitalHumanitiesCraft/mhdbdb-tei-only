import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const url = pathToFileURL(resolve(import.meta.dirname, '../../examples/review-pages/Glossar-554-Pruefung.html')).href;
test.beforeEach(async ({ page }) => {
  await page.goto(url);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});
async function exported(page) {
  const wait = page.waitForEvent('download');
  await page.locator('#backup').click();
  const d = await wait;
  return JSON.parse(await readFile(await d.path(), 'utf8'));
}

test('offline: 44 Fälle in fünf Gruppen, nichts vorbelegt, Pflichtfelder und Persistenz', async ({ page, context }) => {
  await context.setOffline(true);
  await page.reload();
  const start = await exported(page);
  const je = g => start.decisions.filter(d => d.group === g).length;
  expect([je('A'), je('B'), je('C'), je('D'), je('E')]).toEqual([17, 19, 5, 1, 2]);
  expect(start.decisions).toHaveLength(44);
  expect(start.decisions.every(d => d.status === 'unreviewed' && !d.choice && !d.text)).toBe(true);
  await expect(page.locator('#introGrid section')).toHaveCount(5);

  await page.locator('[data-action=decided]').first().click();
  await expect(page.locator('#feedback')).toContainText('Namen');
  await page.locator('#reviewer').fill('Katharina');
  await page.locator('[data-action=decided]').click();
  await expect(page.locator('#feedback')).toContainText('Antwort wählen');

  // A: Bedeutungsoption verlangt einen Text, der vorbelegt ist
  await page.locator('input[name=choice]').first().check();
  await expect(page.locator('#text')).not.toHaveValue('');
  await page.locator('#text').fill('');
  await page.locator('[data-action=decided]').click();
  await expect(page.locator('#feedback')).toContainText('Text');
  await page.locator('input[value=none]').check();
  await page.locator('[data-action=decided]').click();
  await expect(page.locator('#caseStatus')).toHaveText('Entschieden');
  await page.locator('[data-step="1"]').first().click();
  await page.locator('#comment').fill('Bitte noch klären.');
  await page.locator('[data-action=open]').click();

  const saved = await exported(page);
  expect(saved.decisions.filter(a => a.status === 'decided')).toHaveLength(1);
  expect(saved.decisions.filter(a => a.status === 'open')).toHaveLength(1);
  await page.reload();
  expect((await exported(page)).decisions).toEqual(saved.decisions);
  await page.locator('#comment').fill('Nachtrag');
  await expect(page.locator('#caseStatus')).toHaveText('Unbearbeitet / Entwurf');
});

test('B zeigt die entfallenen Teile, D nennt den Beleg, brôt hat die Schels-Fragen', async ({ page }) => {
  await page.locator('#area').selectOption('B');
  await expect(page.locator('#casePick option')).toHaveCount(19);
  await expect(page.locator('details ol.dropped li').first()).toBeAttached();
  await page.locator('#casePick').selectOption('B-2084');
  await expect(page.locator('.question')).toContainText('Schels');
  await expect(page.locator('input[value=schels-nachweis]')).toBeAttached();
  await expect(page.locator('input[value=eigene-zusammenfassung]')).toBeAttached();
  await page.locator('#area').selectOption('D');
  await expect(page.locator('.suggestion')).toContainText('person_867');
  await expect(page.locator('.suggestion')).toContainText('person_46');
  await page.locator('input[value=heinrich]').check();
  await expect(page.locator('#text')).toHaveValue(/Heinrichs von dem Türlin/);
});

test('Export, HTML-Bericht ohne Skripte, JSON-Rundlauf und fremde Datei', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.locator('#reviewer').fill('Katharina');
  await page.locator('input[value=none]').check();
  await page.locator('#comment').fill('Zeile 1\nZeile 2: äöü <script>window.injected=1</script>');
  await page.locator('[data-action=decided]').click();
  const saved = await exported(page);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.locator('#importFile').setInputFiles({ name: 'result.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(saved)) });
  expect((await exported(page)).decisions).toEqual(saved.decisions);
  const wrong = structuredClone(saved);
  wrong.fingerprint = 'fremd';
  await page.locator('#importFile').setInputFiles({ name: 'wrong.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(wrong)) });
  await expect(page.locator('#save')).toContainText('Import abgelehnt');
  expect((await exported(page)).decisions).toEqual(saved.decisions);
  await page.locator('#returnButton').click();
  await expect(page.locator('#exportJson')).toBeFocused();
  const wait = page.waitForEvent('download');
  await page.locator('#exportHtml').click();
  const d = await wait;
  const html = await readFile(await d.path(), 'utf8');
  expect(html).toContain('Zeile 1\nZeile 2: äöü');
  expect(html).toContain('&lt;script&gt;window.injected=1&lt;/script&gt;');
  const report = await page.context().newPage();
  await report.setContent(html);
  await expect(report.locator('article.card')).toHaveCount(44);
  await expect(report.locator('script')).toHaveCount(0);
  expect(await report.evaluate(() => window.injected)).toBeUndefined();
  expect(errors).toEqual([]);
});

test('Filter und Export überstehen gesperrten Browserspeicher', async ({ page }) => {
  await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error('disabled'); }; });
  await page.locator('#reviewer').fill('Katharina');
  await expect(page.locator('#save')).toContainText('nicht verfügbar');
  await page.locator('#comment').fill('Bewusst offen.');
  await page.locator('[data-action=open]').click();
  await page.locator('#filter').selectOption('open');
  await expect(page.locator('#casePick option')).toHaveCount(1);
  expect((await exported(page)).decisions.filter(d => d.status === 'open')).toHaveLength(1);
});
