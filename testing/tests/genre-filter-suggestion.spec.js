/**
 * Gattungs-Vorschlag im Textfilter der Korpussuche (#433)
 *
 * KZW am 2026-09-15: "wenn jemand Artus... tippt, soll das genre-Label
 * Artusroman vorgeschlagen werden und dann diese Textauswahl angeklickt sein
 * ... nur beim Tippen darf es als Vorschlag angezeigt werden". Am 2026-09-17
 * angenommen: der Klick setzt die Auswahl (wie "Nur diese"), nicht nur den
 * Filter. Und: "die Untergattungen kommen immer mit".
 *
 * Das Orakel rechnet die erwartete Textmenge unabhängig von der Seite aus
 * den Index-Dateien auf der Platte: Text -> workRef -> Werk, Werk in der
 * Gattung oder einer ihrer Untergattungen. Gemessen am 2026-09-23: Minnesang
 * trägt 140 Texte direkt und 153 mit Untergattungen, Artusroman 28 ohne
 * Untergattungen. Die Tests verlangen nur, dass die Seite dem Orakel folgt
 * und dass bei Minnesang der Teilbaum mehr bringt als die direkte Zuordnung;
 * die Zahlen selbst dürfen mit dem Ingest wandern.
 *
 * Relative Pfade gegen baseURL, kein fester Port (Laufplan 23.09., #465).
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { gunzipSync } from 'zlib';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const lies = (datei) => JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', datei))).toString('utf-8'));

/** Texte einer Gattung, direkt und mit Teilbaum, aus den Dateien auf der Platte. */
function orakel(termDE) {
  const auth = lies('authority-index.json.gz');
  const korpus = lies('corpus-index.json.gz');
  const g2w = auth.maps.genreToWorks;
  const kinder = new Map();
  for (const g of auth.genres) for (const p of g.parents || []) {
    if (!kinder.has(p)) kinder.set(p, []);
    kinder.get(p).push(g.id);
  }
  const teilbaum = (id, gesehen = new Set()) => {
    if (gesehen.has(id)) return new Set();
    gesehen.add(id);
    const werke = new Set(g2w[id] || []);
    for (const k of kinder.get(id) || []) for (const w of teilbaum(k, gesehen)) werke.add(w);
    return werke;
  };
  const gattung = auth.genres.find(g => g.termDE === termDE);
  const texteZu = (werke) => new Set(korpus.texts
    .filter(t => werke.has((t.workRef || '').split('#').pop()))
    .map(t => t.id));
  return {
    direkt: texteZu(new Set(g2w[gattung.id] || [])),
    mitUntergattungen: texteZu(teilbaum(gattung.id)),
    gesamt: korpus.texts.length,
  };
}

async function angehakt(page) {
  return page.locator('#textList input[type="checkbox"]').evaluateAll(
    cbs => cbs.filter(cb => cb.checked).map(cb => cb.dataset.textId).sort());
}

test.describe('#433: Gattungs-Vorschlag im Textfilter', () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(120000);
    await page.goto('/korpus.html');
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 90000 });
  });

  test('"Artus" schlägt Artusroman vor, der Klick wählt genau dessen Texte', async ({ page }) => {
    const erwartet = orakel('Artusroman');
    expect(erwartet.mitUntergattungen.size, 'Orakel ohne Grundlage').toBeGreaterThan(0);

    await page.locator('#textFilter').fill('Artus');
    const vorschlag = page.locator('#genreSuggestions [data-genre-idx]', { hasText: 'Artusroman' });
    await expect(vorschlag).toBeVisible();
    await expect(vorschlag).toContainText(`${erwartet.mitUntergattungen.size} Texte`);

    await vorschlag.dispatchEvent('mousedown');

    expect(await angehakt(page)).toEqual([...erwartet.mitUntergattungen].sort());
    await expect(page.locator('#selectedTextCount')).toHaveText(String(erwartet.mitUntergattungen.size));
    // Das Feld ist leer und die Liste wieder vollständig sichtbar: ein
    // stehengebliebenes Suchwort hätte mit der Auswahl nichts zu tun.
    await expect(page.locator('#textFilter')).toHaveValue('');
    await expect(page.locator('#genreSuggestions')).toBeHidden();
    await expect(page.locator('#filterInfoText')).toBeHidden();
  });

  test('Minnesang bringt die Untergattungen mit', async ({ page }) => {
    const erwartet = orakel('Minnesang');
    expect(erwartet.mitUntergattungen.size).toBeGreaterThan(erwartet.direkt.size);

    await page.locator('#textFilter').fill('Minnesang');
    const vorschlag = page.locator('#genreSuggestions [data-genre-idx]').filter({ hasText: /^\s*Gattung\s*Minnesang\s/ });
    await expect(vorschlag).toHaveCount(1);
    await vorschlag.dispatchEvent('mousedown');

    expect(await angehakt(page)).toEqual([...erwartet.mitUntergattungen].sort());
  });

  test('Tastatur: Pfeil runter und Enter wählen den ersten Vorschlag', async ({ page }) => {
    const feld = page.locator('#textFilter');
    await feld.click();
    await page.keyboard.type('Artusroman');
    await expect(page.locator('#genreSuggestions [data-genre-idx]').first()).toContainText('Artusroman');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    expect(await angehakt(page)).toEqual([...orakel('Artusroman').mitUntergattungen].sort());
  });

  test('unter drei Zeichen und ohne Treffer gibt es keine Vorschläge, und die Auswahl bleibt', async ({ page }) => {
    const vorher = await angehakt(page);
    await page.locator('#textFilter').fill('Ar');
    await expect(page.locator('#genreSuggestions')).toBeHidden();
    await page.locator('#textFilter').fill('qqqqzz');
    await expect(page.locator('#genreSuggestions')).toBeHidden();
    expect(await angehakt(page)).toEqual(vorher);
  });

  test('Tippen allein ändert die Auswahl nicht (#204 bleibt)', async ({ page }) => {
    const vorher = await angehakt(page);
    await page.locator('#textFilter').fill('Artus');
    await expect(page.locator('#genreSuggestions')).toBeVisible();
    expect(await angehakt(page)).toEqual(vorher);
  });
});
