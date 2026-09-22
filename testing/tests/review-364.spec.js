import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

// Exercise the actual deliverable as a local, offline file, without a server.
const url = pathToFileURL(resolve(import.meta.dirname, '../../examples/review-pages/364-lemma-review.html')).href;
test.beforeEach(async ({ page }) => {
  await page.goto(url);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});
async function exported(page) {
  const wait = page.waitForEvent('download');
  await page.getByRole('button', { name: 'JSON exportieren', exact: true }).click();
  const download = await wait;
  return JSON.parse(await readFile(await download.path(), 'utf8'));
}

test('all source tokens present; decision, open state, group protection and local persistence', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const initial = await exported(page);
  expect(initial.decisions).toHaveLength(66);
  expect(initial.decisions.every(d => d.status === 'unreviewed' && d.choice === '')).toBe(true);
  await page.locator('#reviewer').fill('Testredaktion');
  await page.locator('[data-group="lemma_79408"]').click();
  const cards = page.locator('[data-case]');
  await expect(cards).toHaveCount(6);
  const firstId = await cards.first().getAttribute('data-case');
  await cards.first().locator('input[type=radio]').first().check();
  await cards.first().locator('[data-field=comment]').fill('Individuell geprüft <script>alert(1)</script>');
  await cards.first().getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  await cards.nth(1).getByRole('button', { name: 'Geprüft, bleibt offen', exact: true }).click();
  await page.getByText('Gruppenentscheidung bewusst anwenden', { exact: true }).click();
  const choice = await page.locator('#groupChoice option').nth(1).getAttribute('value');
  await page.locator('#groupChoice').selectOption(choice);
  await page.locator('#groupApply').click();
  const saved = await exported(page);
  const group = saved.decisions.filter(d => d.group === 'lemma_79408');
  expect(group.filter(d => d.status === 'decided')).toHaveLength(5);
  expect(group.filter(d => d.status === 'open')).toHaveLength(1);
  expect(group.find(d => d.id === firstId).comment).toContain('<script>');
  await page.reload();
  expect((await exported(page)).decisions).toEqual(saved.decisions);
  await page.locator('[data-group="lemma_79408"]').click();
  await page.locator(`[data-case="${firstId}"] [data-field=comment]`).fill('Überarbeitet');
  await expect(page.locator(`[data-case="${firstId}"]`)).toHaveAttribute('data-status', 'unreviewed');
  expect(errors).toEqual([]);
});

test('JSON round trip, hostile text stays text, incompatible import is atomic; complete HTML report', async ({ page }) => {
  await page.locator('#reviewer').fill('Prüferin <b>Test</b>');
  const card = page.locator('[data-case]').first();
  await card.locator('input[value=other]').check();
  await card.locator('[data-field=other]').fill('Eigener Vorschlag </textarea><script>window.injected=1</script>');
  await card.locator('[data-field=comment]').fill('Mehrzeilig\nmit Umlauten: äöü');
  await card.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  const snapshot = await exported(page);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.locator('#importFile').setInputFiles({name:'answers.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(snapshot))});
  await expect(page.locator('#save')).toContainText('Import vollständig');
  expect((await exported(page)).decisions).toEqual(snapshot.decisions);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
  const invalid = {...snapshot, fingerprint:'wrong'};
  await page.locator('#importFile').setInputFiles({name:'wrong.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});
  await expect(page.locator('#save')).toContainText('Import abgelehnt');
  expect((await exported(page)).decisions).toEqual(snapshot.decisions);
  const wait = page.waitForEvent('download');
  await page.getByRole('button', {name:'HTML-Ergebnisbericht',exact:true}).click();
  const report = await wait;
  const html = await readFile(await report.path(), 'utf8');
  expect(html).toContain('Mehrzeilig\nmit Umlauten: äöü');
  expect(html).toContain('&lt;script&gt;window.injected=1&lt;/script&gt;');
  const p = await page.context().newPage();
  await p.setContent(html);
  await expect(p.locator('article.card')).toHaveCount(66);
  await expect(p.locator('script')).toHaveCount(0);
  expect(await p.evaluate(() => window.injected)).toBeUndefined();
});

test('offline operation, honest storage failure, free-answer validation, filters and extended context', async ({ page, context }) => {
  await context.setOffline(true);
  await page.reload();
  await page.locator('#reviewer').fill('Prüfer');
  const card = page.locator('[data-case]').first();
  await card.locator('input[value=other]').check();
  await card.getByRole('button', {name:'Entscheidung festhalten',exact:true}).click();
  await expect(card.locator('.feedback')).toContainText('andere Antwort ausführen');
  await card.getByRole('button', {name:'Geprüft, bleibt offen',exact:true}).click();
  await page.locator('#filter').selectOption('open');
  await expect(page.locator('[data-case]')).toHaveCount(1);
  await page.getByText('Mehr Kontext anzeigen (bis zu 180 Tokens davor und danach)',{exact:true}).click();
  await expect(page.locator('[data-case] .context').nth(1)).toBeVisible();
  await page.evaluate(() => {Storage.prototype.setItem = () => {throw new Error('disabled');};});
  await page.locator('[data-field=comment]').fill('Auch ohne Browserspeicher exportierbar');
  await expect(page.locator('#save')).toContainText('nicht verfügbar');
  expect((await exported(page)).decisions.some(d => d.comment === 'Auch ohne Browserspeicher exportierbar')).toBe(true);
  await page.locator('#scope').selectOption('extra');
  await expect(page.locator('#nav button')).toHaveCount(24);
});
