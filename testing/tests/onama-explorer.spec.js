/**
 * ONAMA-Narrativ-Explorer, Pilot Argonautensage (#609, Beta)
 *
 * Smoke-Tests: Route #onama, Kennzeichnung des selektiven Bestands mit
 * Datenversion, Einstieg ueber Ding, Handlung, Entitaet und Konzept, die
 * Trennung von Konzept und Realisierung sowie von allgemeiner und temporaerer
 * Funktion, der Filter Text/Bild, der Sprung in die Leseansicht und die
 * Randfall-Liste.
 *
 * Die erwarteten Zahlen kommen aus playground/data/onama/argonauten.json, die
 * der Test selbst liest: das Paket wird mit einem neuen Korpus-Commit neu
 * gebaut, und ein fest eingetragener Wert wuerde dann den falschen Befund
 * melden. Gesperrt ist nur, was das Modell festlegt (die Spaltenueberschriften).
 */

import { test, expect } from '@playwright/test';

test.describe('ONAMA-Narrativ-Explorer (#609)', () => {
  let paket;

  test.beforeAll(async ({ request }) => {
    const antwort = await request.get('/playground/data/onama/argonauten.json');
    expect(antwort.ok()).toBeTruthy();
    paket = await antwort.json();
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/playground/#onama');
    await page.waitForSelector('#onListe', { state: 'visible', timeout: 60000 });
    // Erst nach dem Korpus handeln, sonst reisst eine Aktion in den Hauptthread-Block (siehe horses-explorer.spec.js).
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });
  });

  test('Route #onama zeigt Selektivitaet, Datenversion und Herkunft', async ({ page }) => {
    const box = page.locator('#resultsContainer');
    await expect(box).toContainText('Selektiver Bestand');
    await expect(box).toContainText(paket.meta.quellen.korpus_commit.slice(0, 7));
    await expect(box).toContainText(paket.meta.quellen.mhdbdb_commit.slice(0, 7));
    await expect(box).toContainText(`${paket.meta.statistik.realisierungen_gesamt}`);
    await expect(box).toContainText('Fachlich bestätigt ist noch nichts');
    await expect(box).toContainText('ONAMA-Q-Nummern sind keine Wikidata-Q-Nummern');
  });

  test('Einstieg ueber Handlung: Trefferzahl stimmt mit dem Paket', async ({ page }) => {
    await page.click('[data-on-modus="handlung"]');
    const erster = page.locator('#onListe .on-item').first();
    const n = Number(await erster.locator('.on-count').textContent());
    const verbLabel = (await erster.locator('span').first().textContent()).trim();
    const id = Object.entries(paket.verben).find(([, l]) => l.de === verbLabel)[0];
    const erwartet = paket.realisierungen.filter(r => r.handlung.includes(id)).length;
    expect(n).toBe(erwartet);
    await erster.click();
    await expect(page.locator('[data-on-real]')).toHaveCount(erwartet);
  });

  test('Konzept und Realisierung, allgemeine und temporaere Funktion bleiben getrennt', async ({ page }) => {
    // Eine Realisierung mit temporaerer Funktion suchen, die Entitaet darin als Einstieg waehlen.
    const mitFunktion = paket.realisierungen.find(r => r.rollen.some(x => x.temporaere_funktionen.length));
    expect(mitFunktion).toBeTruthy();
    const rolle = mitFunktion.rollen.find(x => x.temporaere_funktionen.length && x.beteiligte.some(b => b.entitaet));
    const ent = paket.entitaeten[rolle.beteiligte.find(b => b.entitaet).entitaet];
    const modus = ent.typen.includes('Thing') ? 'ding' : 'entitaet';
    await page.click(`[data-on-modus="${modus}"]`);
    await page.locator(`[data-on-wahl="entitaet:${ent.id}"]`).first().click();
    const box = page.locator('#resultsContainer');
    await expect(box).toContainText('Konzept: abstrakt, medienübergreifend');
    await expect(box).toContainText('Realisierung: konkret in');
    await expect(box.locator('th', { hasText: 'Allgemeine Funktion (der Entität)' }).first()).toBeAttached();
    await expect(box.locator('th', { hasText: 'Funktion in dieser Handlung' }).first()).toBeAttached();
    const tmp = paket.funktionen[rolle.temporaere_funktionen[0]].de;
    await expect(box.locator('.on-fn-tmp', { hasText: tmp }).first()).toBeAttached();
  });

  test('Konzept-Einstieg zeigt das gewaehlte Konzept, auch wenn es nicht das erste der Realisierung ist', async ({ page }) => {
    const r = paket.realisierungen.find(x => x.konzepte.length > 1);
    expect(r).toBeTruthy();
    const gewaehlt = r.konzepte[1];
    await page.click('[data-on-modus="konzept"]');
    await page.locator(`[data-on-wahl="konzept:${gewaehlt}"]`).first().click();
    const titel = paket.konzepte[gewaehlt].labels.de;
    await expect(page.locator('.on-card-head .on-h2', { hasText: titel }).first()).toBeAttached();
    await expect(page.locator(`.on-card:has(.on-card-head .on-h2:text-is("${titel}")) [data-on-real="${r.id}"]`)).toHaveCount(1);
  });

  test('Filter Nur Bild zeigt keine Textrealisierung', async ({ page }) => {
    await page.click('[data-on-modus="konzept"]');
    await page.locator('#onListe .on-item').first().click();
    await page.click('[data-on-art="bild"]');
    const texte = await page.locator('[data-on-real] .on-badge-brand').allTextContents();
    for (const t of texte) expect(t).toMatch(/^Bild/);
    await page.click('[data-on-art="text"]');
    const texte2 = await page.locator('[data-on-real] .on-badge-brand').allTextContents();
    for (const t of texte2) expect(t).toMatch(/^(TRO|TRY)$/);
  });

  test('Geprueftes Anker fuehrt ueber verseId in die Leseansicht', async ({ page }) => {
    const r = paket.realisierungen.find(x => x.art === 'text' && x.passagen.some(p => p.status === 'wortanker' && !p.umgerechnet));
    const pa = r.passagen.find(p => p.status === 'wortanker' && !p.umgerechnet);
    await page.click('[data-on-modus="konzept"]');
    await page.locator(`[data-on-wahl="konzept:${r.konzepte[0]}"]`).first().click();
    const karte = page.locator(`[data-on-real="${r.id}"]`);
    const link = karte.locator('a', { hasText: 'Leseansicht' }).first();
    const href = await link.getAttribute('href');
    expect(href).toContain(`textId=${pa.text}`);
    expect(href).toContain(`verseId=${pa.von}`);
  });

  test('Nicht gefundene Anker werden benannt und nicht verlinkt', async ({ page }) => {
    // Eine Passage mit gefundenem Startpunkt (nur der Endpunkt fehlt): hier koennte ein
    // fehlerhafter Code einen Sprung anbieten, bei text:null gaebe es nie einen Link.
    const r = paket.realisierungen.find(x => x.passagen.some(p => p.status === 'nicht_gefunden' && p.text));
    expect(r).toBeTruthy();
    await page.click('[data-on-modus="konzept"]');
    await page.locator(`[data-on-wahl="konzept:${r.konzepte[0]}"]`).first().click();
    const karte = page.locator(`[data-on-real="${r.id}"]`);
    const zeile = karte.locator('tbody tr', { hasText: 'Anker nicht gefunden' }).first();
    await expect(zeile).toBeVisible();
    await expect(zeile.locator('a')).toHaveCount(0);
    await expect(karte.locator('.on-badge-bad', { hasText: 'offen' })).toBeVisible();
  });

  test('Umgerechnete Spannen sind gekennzeichnet', async ({ page }) => {
    // Vorrang offen vor abgeleitet: eine umgekehrte Passage macht die Realisierung offen, also eine
    // mit abgeleitetem Status waehlen.
    const r = paket.realisierungen.find(x => x.pruefstatus === 'abgeleitet' && x.passagen.some(p => p.umgerechnet));
    expect(r).toBeTruthy();
    await page.click('[data-on-modus="konzept"]');
    await page.locator(`[data-on-wahl="konzept:${r.konzepte[0]}"]`).first().click();
    const karte = page.locator(`[data-on-real="${r.id}"]`);
    await expect(karte.locator('.on-badge-warn', { hasText: 'umgerechnet' }).first()).toBeVisible();
    await expect(karte.locator('.on-badge-warn', { hasText: 'abgeleitet' }).first()).toBeVisible();
  });

  test('Umgerechnete Passage zeigt abgeleitet, kein Anker geprueft und keinen Sprung', async ({ page }) => {
    // Auf Passagenebene gilt dieselbe Regel wie auf Realisierungsebene (#609).
    const r = paket.realisierungen.find(x => x.passagen.some(p => p.status === 'wortanker' && p.umgerechnet));
    const pa = r.passagen.find(p => p.status === 'wortanker' && p.umgerechnet);
    await page.click('[data-on-modus="konzept"]');
    await page.locator(`[data-on-wahl="konzept:${r.konzepte[0]}"]`).first().click();
    const zeile = page.locator(`[data-on-real="${r.id}"] tbody tr`, { hasText: pa.von }).first();
    await expect(zeile).toBeVisible();
    await expect(zeile).not.toContainText('Anker geprüft');
    await expect(zeile.locator('.on-badge-warn', { hasText: 'abgeleitet' })).toBeVisible();
    await expect(zeile.locator('a')).toHaveCount(0);
  });

  test('Randfaelle stehen in einer eigenen, zugeklappten Liste', async ({ page }) => {
    const summary = page.locator('summary', { hasText: 'Nicht im Ausschnitt' });
    await expect(summary).toContainText(`${paket.randfaelle.length} Randfälle`);
    await expect(summary).toContainText(`${paket.ausgeschlossen.length} ausgeschlossen`);
  });
});
