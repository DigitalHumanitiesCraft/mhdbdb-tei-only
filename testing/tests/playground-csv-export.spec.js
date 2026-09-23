/**
 * CSV-Export der tabellarischen TEI-Werkzeuge im Playground (#448)
 *
 * Neun Werkzeuge, ein Test je Werkzeug. Geprueft wird das Hausformat aus
 * assets/js/lib/csv-export.js (BOM, CRLF, Komma, Quoting nur bei Bedarf),
 * die Kopfzeile woertlich und die Zeilenzahl gegen das, was die Ansicht
 * ueber ihre Menge sagt. Wo die Tabelle nach Top-N oder einer
 * Anzeigegrenze kappt, muss die Datei MEHR Zeilen haben als die Tabelle:
 * das ist der Zweck des Exports.
 *
 * Der Hapax-Export (#hxCsvExport) ist aelter, trennt mit Semikolon und
 * steht nicht hier.
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

async function ladeCsv(page, buttonId) {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click(`#${buttonId}`)
  ]);
  const bytes = readFileSync(await download.path());
  return { name: download.suggestedFilename(), bytes };
}

/** Prueft BOM, CRLF und die Kopfzeile; gibt die Datenzeilen zurueck. */
function pruefeFormat(csv, kopf) {
  expect([...csv.bytes.subarray(0, 3)]).toEqual([0xEF, 0xBB, 0xBF]);
  const text = csv.bytes.toString('utf8').slice(1);
  // Kein nacktes LF: jede Zeile endet mit CRLF, und kein Wert enthaelt
  // hier einen Umbruch
  expect(text.replace(/\r\n/g, '')).not.toMatch(/[\r\n]/);
  const zeilen = text.split('\r\n');
  expect(zeilen[0]).toBe(kopf);
  return zeilen.slice(1);
}

const DATUM = '\\d{4}-\\d{2}-\\d{2}';

test.describe('CSV-Export im Playground (#448)', () => {

  test('Wortfrequenz: alle Lemmata, nicht nur Top 50', async ({ page }) => {
    await page.goto('/playground/#word-frequency');
    await page.waitForSelector('#wfCsvExport', { state: 'visible', timeout: 60000 });
    const tabelle = await page.locator('#resultsContainer table tbody tr').count();
    expect(tabelle).toBe(50);
    const ersterName = (await page.locator('#resultsContainer table tbody tr a').first().textContent()).trim();

    const csv = await ladeCsv(page, 'wfCsvExport');
    expect(csv.name).toMatch(new RegExp(`^mhdbdb-wortfrequenz-auswahl-${DATUM}\\.csv$`));
    const zeilen = pruefeFormat(csv, 'Rang,Lemma,ID,PoS,Absolut,pro 1000');
    expect(zeilen.length).toBeGreaterThan(tabelle);
    expect(zeilen[0].startsWith(`1,${ersterName},lemma_`)).toBe(true);
  });

  test('Versendings-Profil: alle Versende-Lemmata, nicht nur Top 50', async ({ page }) => {
    await page.goto('/playground/#verse-ending-profile');
    await page.waitForSelector('#vepCsvExport', { state: 'visible', timeout: 60000 });
    const tabelle = await page.locator('#resultsContainer table tbody tr').count();

    const csv = await ladeCsv(page, 'vepCsvExport');
    const zeilen = pruefeFormat(csv, 'Rang,Lemma,ID,PoS,Versende-Belege,Anteil an annot. Versen (%),Reim-Druck (%)');
    expect(zeilen.length).toBeGreaterThan(tabelle);
  });

  test('Text-Statistiken: eine Zeile je Tabellenzeile, mit Autor*in', async ({ page }) => {
    await page.goto('/playground/#text-statistics');
    await page.waitForSelector('#tsCsvExport', { state: 'visible', timeout: 60000 });
    const tabelle = await page.locator('#resultsContainer table tbody tr').count();

    const csv = await ladeCsv(page, 'tsCsvExport');
    expect(csv.name).toMatch(new RegExp(`^mhdbdb-textstatistik-alle-${DATUM}\\.csv$`));
    const zeilen = pruefeFormat(csv, 'Sigle,Titel,Autor*in,Annot. Tokens,Unique,Diversität,Hapax-Rate,Ø-Freq');
    expect(zeilen.length).toBe(tabelle);
  });

  test('Kookkurrenz-Ranking: alle Partner laut Zaehler', async ({ page }) => {
    await page.goto('/playground/#cooccurrence-ranking');
    await page.waitForSelector('#coRkSearchBtn', { state: 'visible', timeout: 60000 });
    await page.fill('#coRkQuery', 'rot');
    await page.press('#coRkQuery', 'Escape');
    await page.click('#coRkSearchBtn');
    await page.waitForSelector('#coRkCsvExport', { state: 'visible', timeout: 60000 });

    // "x / y angezeigt": y ist die Menge, die die Datei tragen muss
    const zaehler = await page.locator('#resultsContainer').getByText(/angezeigt$/).textContent();
    const gesamt = parseInt(zaehler.split('/')[1].replace(/[^\d]/g, ''), 10);

    const csv = await ladeCsv(page, 'coRkCsvExport');
    const zeilen = pruefeFormat(csv, 'Rang,Partner-Lemma,ID,PoS,Kookkurrenz-Frequenz');
    expect(zeilen.length).toBe(gesamt);
  });

  test('Reim-Wörterbuch: guot steht als Partner von muot in der Datei', async ({ page }) => {
    await page.goto('/playground/#rhyme-dictionary');
    await page.waitForSelector('#rdSearchBtn', { state: 'visible', timeout: 60000 });
    await page.fill('#rdQuery', 'muot');
    await page.press('#rdQuery', 'Escape');
    await page.click('#rdSearchBtn');
    await page.waitForSelector('#rdCsvExport', { state: 'visible', timeout: 60000 });

    const csv = await ladeCsv(page, 'rdCsvExport');
    expect(csv.name).toMatch(new RegExp(`^mhdbdb-reimpartner-muot-${DATUM}\\.csv$`));
    const zeilen = pruefeFormat(csv, 'Rang,Reimpartner-Lemma,ID,PoS,Reimpaare,Texte (Reimpaare)');
    expect(zeilen.some(z => /^\d+,guot,lemma_\d+,/.test(z))).toBe(true);
  });

  test('Textvergleich: die ganze Kategorie, auch ohne "Alle anzeigen"', async ({ page }) => {
    await page.goto('/playground/#text-comparison');
    await page.waitForSelector('#tcSelectA', { state: 'visible', timeout: 90000 });
    await page.selectOption('#tcSelectA', 'PZ');
    await page.selectOption('#tcSelectB', 'ERB');
    await page.click('#tcCompareBtn');
    await page.waitForSelector('#tcCsvExport', { state: 'visible', timeout: 60000 });

    const label = await page.locator('label:has(#tcShowAll)').textContent();
    const gesamt = parseInt(label.replace(/[^\d]/g, ''), 10);
    const tabelle = await page.locator('#resultsContainer table tbody tr').count();
    expect(tabelle).toBeLessThan(gesamt);

    const csv = await ladeCsv(page, 'tcCsvExport');
    const zeilen = pruefeFormat(csv, 'Lemma,ID,PoS,Kategorie,PZ (A),ERB (B),|A-B|');
    expect(zeilen.length).toBe(gesamt);
    expect(zeilen.every(z => z.includes(',beide,'))).toBe(true);
  });

  test('Versposition: eine Zeile je Text der Liste', async ({ page }) => {
    await page.goto('/playground/#verse-position');
    await page.waitForSelector('#vpsSearchBtn', { state: 'visible', timeout: 60000 });
    await page.fill('#vpsQuery', 'minne');
    await page.press('#vpsQuery', 'Escape');
    await page.click('#vpsSearchBtn');
    await page.waitForSelector('#vpsCsvExport', { state: 'visible', timeout: 60000 });
    const liste = await page.locator('#resultsContainer ul li').count();

    const csv = await ladeCsv(page, 'vpsCsvExport');
    expect(csv.name).toMatch(new RegExp(`^mhdbdb-versende-minne-${DATUM}\\.csv$`));
    const zeilen = pruefeFormat(csv, 'Sigle,Titel,Autor*in,Treffer am Versende,Vorkommen im Text,Anteil (%)');
    expect(zeilen.length).toBe(liste);
  });

  test('Arthurische Pferde: eine Zeile je angezeigtem Beleg', async ({ page }) => {
    await page.goto('/playground/#horses');
    await page.waitForSelector('#hxHorseSelect', { state: 'visible', timeout: 60000 });
    await page.selectOption('#hxHorseSelect', 'Gringuljete');
    await page.waitForSelector('#hxHorseCsvExport', { state: 'visible', timeout: 5000 });
    const tabelle = await page.locator('#resultsContainer table tbody tr').count();

    const csv = await ladeCsv(page, 'hxHorseCsvExport');
    const zeilen = pruefeFormat(csv, 'Pferd,Werk,Stelle (Borek),Vers im Korpus,Zuordnung,Wortlaut,Ereignisse,Eigenschaften,Ausrüstung,Figuren,Bezeichnungen');
    expect(zeilen.length).toBe(tabelle);
  });

  test('Bezeichnungen: Figur- und Lemma-Perspektive exportieren ihre Tabelle', async ({ page }) => {
    await page.goto('/playground/#naming');
    await page.waitForSelector('#neWorkSelect', { state: 'visible', timeout: 60000 });

    await page.selectOption('#neWorkSelect', 'IW');
    await page.selectOption('#neFigureSelect', 'Iwein');
    await page.waitForSelector('#neCsvExport', { state: 'visible', timeout: 5000 });
    const lemmata = await page.locator('[data-ne-term]').count();
    const figurCsv = await ladeCsv(page, 'neCsvExport');
    const figurZeilen = pruefeFormat(figurCsv, 'Werk,Lemma,Kategorie,Häufigkeit');
    expect(figurZeilen.length).toBe(lemmata);

    await page.click('[data-ne-persp="lemma"]');
    await page.selectOption('#neWorkSelect', 'ROL');
    await page.selectOption('#neFigureSelect', 'helt');
    await page.waitForSelector('#neCsvExport', { state: 'visible', timeout: 5000 });
    const figuren = await page.locator('[data-ne-term]').count();
    const lemmaCsv = await ladeCsv(page, 'neCsvExport');
    const lemmaZeilen = pruefeFormat(lemmaCsv, 'Werk,Lemma,Benannte Figur,Nennungen,Anteil (%),Erzähler,Figurenrede,Selbst,als Bezeichnung,als Epitheton');
    expect(lemmaZeilen.length).toBe(figuren);
    expect(lemmaZeilen.every(z => z.startsWith('ROL,helt,'))).toBe(true);
  });
});
