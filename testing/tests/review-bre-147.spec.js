import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

// Prueft die ausgelieferte Pruefseite der Weingruesse (#147) als lokale Datei, ohne Server.
// Erzeugt von scripts/ingest/bre/22-pruefseite.py; nach einer Aenderung am Template neu bauen.
const url = pathToFileURL(resolve(import.meta.dirname, '../../ingest/bre/pruefung/pruefseite.html')).href;
const ZEILEN = { 'lemma-verdacht.tsv': 50, 'lemma.tsv': 50, 'wortart.tsv': 50, 'bedeutung.tsv': 50 };
const GESAMT = 200;

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

test('Zeilenzahlen, Stichprobe mit Nenner und Seed, nichts vorausgewaehlt', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.reload();
  const initial = await exported(page);
  expect(initial.schema).toBe('mhdbdb-bre-147-pruefseite-v1');
  expect(initial.seed).toBe(147);
  expect(initial.decisions).toHaveLength(GESAMT);
  for (const [datei, n] of Object.entries(ZEILEN)) {
    expect(initial.decisions.filter(d => d.datei === datei)).toHaveLength(n);
  }
  expect(initial.decisions.every(d => d.status === 'unreviewed' && d.passt === '' && d.wahl === '')).toBe(true);
  expect(Object.keys(initial.sources)).toEqual(expect.arrayContaining(Object.keys(ZEILEN).map(d => 'ingest/bre/pruefung/' + d)));
  await expect(page.locator('#nav button')).toHaveCount(4);
  await expect(page.locator('[data-case]')).toHaveCount(50);
  await expect(page.locator('.panel')).toContainText('50 von 233 Zeilen');
  await expect(page.locator('.suggestion.vorschlag')).toHaveCount(50);
  await expect(page.locator('input[type=radio]:checked')).toHaveCount(0);
  await page.locator('[data-group="lemma"]').click();
  await expect(page.locator('[data-case]')).toHaveCount(50);
  await expect(page.locator('.panel')).toContainText('Stichprobe: 50 von 98 Zeilen');
  await expect(page.locator('.panel')).toContainText('Zufallswert 147');
  await page.locator('[data-group="wortart"]').click();
  await page.locator('#sicherheit').selectOption('low');
  await expect(page.locator('[data-case]')).toHaveCount(20);
  await expect(page.locator('[data-case] mark').first()).toBeVisible();
  expect(errors).toEqual([]);
});

test('Entscheiden, Offenlassen, Pflichtangaben, Entwurf nach Aenderung, Speicherung im Browser', async ({ page }) => {
  await page.locator('#reviewer').fill('Testprüferin');
  const cards = page.locator('[data-case]');
  const [id0, id1, id2] = await Promise.all([0, 1, 2].map(i => cards.nth(i).getAttribute('data-case')));
  const c0 = page.locator(`[data-case="${id0}"]`);
  await c0.locator('input[value=nein]').check();
  await expect(c0).toHaveAttribute('data-status', 'draft');
  await c0.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  await expect(c0.locator('.feedback')).toContainText('Korrektur wählen');
  await c0.locator('[data-field=korrekturWahl]').selectOption('kein Lemma');
  await c0.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  await expect(c0).toHaveAttribute('data-status', 'decided');
  const c1 = page.locator(`[data-case="${id1}"]`);
  await c1.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  await expect(c1.locator('.feedback')).toContainText('„ja“ oder „nein“');
  await c1.getByRole('button', { name: '? Nicht zu entscheiden', exact: true }).click();
  await expect(c1).toHaveAttribute('data-status', 'open');
  const c2 = page.locator(`[data-case="${id2}"]`);
  await c2.locator('input[value=ja]').check();
  await c2.locator('[data-field=korrekturWahl]').selectOption('frei');
  await c2.locator('[data-field=korrekturFrei]').fill('lemma_1');
  await c2.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  await expect(c2.locator('.feedback')).toContainText('Korrektur leer');
  await c2.locator('[data-field=korrekturWahl]').selectOption('');
  await c2.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  const saved = await exported(page);
  const by = Object.fromEntries(saved.decisions.map(d => [d.id, d]));
  expect(by[id0]).toMatchObject({ passt: 'nein', korrektur: 'kein Lemma', status: 'decided', reviewer: 'Testprüferin', datei: 'lemma-verdacht.tsv' });
  expect(by[id1]).toMatchObject({ passt: '?', status: 'open' });
  expect(by[id2]).toMatchObject({ passt: 'ja', korrektur: '' });
  expect(saved.decisions.filter(d => d.status !== 'unreviewed')).toHaveLength(3);
  await page.reload();
  expect((await exported(page)).decisions).toEqual(saved.decisions);
  await page.locator(`[data-case="${id0}"] [data-field=anmerkung]`).fill('Nachgedacht');
  await expect(page.locator(`[data-case="${id0}"]`)).toHaveAttribute('data-status', 'draft');
  expect((await exported(page)).decisions.find(d => d.id === id0).passt).toBe('');
});

test('JSON-Rundlauf, feindlicher Text bleibt Text, falscher Import wird ganz abgelehnt, HTML-Bericht vollständig', async ({ page }) => {
  await page.locator('#reviewer').fill('Prüferin <b>Test</b>');
  const card = page.locator('[data-case]').first();
  await card.locator('input[value=nein]').check();
  await card.locator('[data-field=korrekturWahl]').selectOption('frei');
  await card.locator('[data-field=korrekturFrei]').fill('neu </textarea><script>window.injected=1</script>');
  await card.locator('[data-field=anmerkung]').fill('Mehrzeilig\nmit Umlauten: äöü');
  await card.getByRole('button', { name: 'Entscheidung festhalten', exact: true }).click();
  const snapshot = await exported(page);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.locator('#importFile').setInputFiles({ name: 'antworten.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(snapshot)) });
  await expect(page.locator('#save')).toContainText('Import vollständig');
  expect((await exported(page)).decisions).toEqual(snapshot.decisions);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
  for (const invalid of [{ ...snapshot, fingerprint: 'falsch' },
    { ...snapshot, decisions: snapshot.decisions.map((d, i) => i === 0 ? { ...d, passt: 'ja' } : d) }]) {
    await page.locator('#importFile').setInputFiles({ name: 'falsch.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(invalid)) });
    await expect(page.locator('#save')).toContainText('Import abgelehnt');
    expect((await exported(page)).decisions).toEqual(snapshot.decisions);
  }
  const wait = page.waitForEvent('download');
  await page.getByRole('button', { name: 'HTML-Ergebnisbericht', exact: true }).click();
  const html = await readFile(await (await wait).path(), 'utf8');
  expect(html).toContain('Mehrzeilig\nmit Umlauten: äöü');
  expect(html).toContain('&lt;script&gt;window.injected=1&lt;/script&gt;');
  const p = await page.context().newPage();
  await p.setContent(html);
  await expect(p.locator('article.card')).toHaveCount(GESAMT);
  await expect(p.locator('script')).toHaveCount(0);
});

test('ohne Browserspeicher bleibt der Export möglich', async ({ page }) => {
  await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error('gesperrt'); }; });
  await page.locator('[data-case] [data-field=anmerkung]').first().fill('Auch ohne Speicher');
  await expect(page.locator('#save')).toContainText('nicht verfügbar');
  expect((await exported(page)).decisions.some(d => d.anmerkung === 'Auch ohne Speicher')).toBe(true);
});
