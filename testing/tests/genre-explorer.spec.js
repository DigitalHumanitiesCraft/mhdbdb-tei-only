/**
 * Gattungs-Explorer: Baumansicht der Textreihentypologie (#361)
 *
 * genres.xml speichert die Hierarchie als volle transitive Huelle: jede
 * Kategorie nennt ALLE ihre Vorfahren, nicht nur die naechsten. Vor #361 hat
 * der Explorer diese Menge mit " UND " verkettet, was im schlimmsten Fall eine
 * 408 Zeichen lange Zeile aus 20 Namen ohne Reihenfolge ergab.
 *
 * build-authority-index.py rechnet die Huelle jetzt zur transitiven Reduktion
 * zurueck (Authority-Index v1.9.0, genres[].parents als IDs). Die Zahlen unten
 * sind am 2026-08-10 an authority-files/genres.xml gemessen. Sie sind ein
 * legitimer Lock: die Datei ist kuratiert und aendert sich nur durch eine
 * bewusste Entscheidung, nicht durch einen Rebuild.
 *
 * Der wichtigste Test ist der letzte. 171 der 615 Kategorien haben mehr als
 * einen direkten Elternteil, und das ist der Sinn der Typologie, kein Fehler:
 * ein Predigtmaerlein IST Maere und Predigt. Der Baum zeigt sie deshalb an
 * jeder dieser Stellen, und zwei Knoten derselben Kategorie muessen sich
 * unabhaengig auf- und zuklappen lassen. Genau daran scheitert eine Baumansicht,
 * die ihre DOM-IDs aus der Kategorie-ID statt aus dem Pfad bildet.
 */

import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:8080';

test.describe('Gattungs-Explorer Baumansicht (#361)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE}/playground/#genres`);
    await page.waitForSelector('#genreTree .genre-node', {
      state: 'visible',
      timeout: 60000,
    });
  });

  test('Index traegt direkte Eltern statt der vollen Huelle', async ({ page }) => {
    const daten = await page.evaluate(() => {
      const genres = window.playground.authorityData.genres;
      const byId = new Map(genres.map((g) => [g.id, g]));
      const verteilung = {};
      for (const g of genres) {
        const n = (g.parents || []).length;
        verteilung[n] = (verteilung[n] || 0) + 1;
      }
      return {
        gesamt: genres.length,
        verteilung,
        unaufloesbar: genres.flatMap((g) =>
          (g.parents || []).filter((p) => !byId.has(p))
        ),
        wurzeln: genres
          .filter((g) => !(g.parents || []).length)
          .map((g) => g.termDE)
          .sort(),
      };
    });

    expect(daten.gesamt).toBe(615);
    // gemessen 2026-08-10: 442 mit einem, 139 mit zwei, 29 mit drei, 3 mit vier
    expect(daten.verteilung).toEqual({ 0: 2, 1: 442, 2: 139, 3: 29, 4: 3 });
    expect(daten.unaufloesbar).toEqual([]);
    expect(daten.wurzeln).toEqual([
      'Epik, Lyrik und Dramatik',
      'Wissensliteratur und Gebrauchsliteratur',
    ]);
  });

  test('maps.genreHierarchy ist weg, nichts liest sie mehr', async ({ page }) => {
    const indexes = await page.evaluate(() =>
      Object.keys(window.playground.authorityManager.indexes)
    );
    expect(indexes).not.toContain('genreHierarchy');
  });

  test('Baum startet mit den zwei Wurzeln und klappt auf', async ({ page }) => {
    const wurzeln = page.locator('#genreTree > .genre-node');
    await expect(wurzeln).toHaveCount(2);
    await expect(wurzeln.first()).toContainText('Epik, Lyrik und Dramatik');

    // zugeklappt: keine Kinder im DOM
    await expect(page.locator('#genreTree .genre-node .genre-node')).toHaveCount(0);

    await wurzeln.first().locator('button[aria-expanded]').first().click();
    await expect(
      wurzeln.first().locator('.genre-node')
    ).toHaveCount(7);
  });

  test('leere Zweige sind als solche gekennzeichnet', async ({ page }) => {
    const wurzel = page.locator('#genreTree > .genre-node').first();
    await wurzel.locator('button[aria-expanded]').first().click();

    // 482 der 615 Kategorien haben im ganzen Zweig unter sich kein Werk
    // (gemessen 2026-08-10). Dramatik ist eine davon.
    const dramatik = wurzel.locator('.genre-node', { hasText: 'Dramatik' }).first();
    await expect(dramatik).toContainText('keine Werke');
  });

  test('Detailfeld nennt jeden Pfad, nicht eine UND-Kette', async ({ page }) => {
    const id = await page.evaluate(() => {
      const ge = window.playground.ui.authorityExplorers.genreExplorer;
      const g = ge.authorityData.genres.find((x) => x.termDE === 'Predigtmärlein');
      ge.showGenreDetail(g.id);
      return g.id;
    });
    expect(id).toBeTruthy();

    const detail = page.locator('#genreDetail');
    await expect(detail).toBeVisible();
    await expect(detail).toContainText('6 Einordnungen');
    await expect(detail).toContainText('Märe');
    await expect(detail).toContainText('Predigt');
    await expect(detail).not.toContainText(' UND ');
  });

  test('mehrfach einsortierte Kategorien klappen unabhaengig', async ({ page }) => {
    const zustand = await page.evaluate(() => {
      const ge = window.playground.ui.authorityExplorers.genreExplorer;
      const g = ge.authorityData.genres.find((x) => x.termDE === 'Predigt');
      const pfade = ge.pathsTo(g.id);

      // beide Elternketten sichtbar machen, dann NUR die erste Predigt oeffnen
      for (const pfad of [pfade[0], pfade[1]]) {
        for (let i = 1; i < pfad.length; i++) {
          ge.expanded.add(pfad.slice(0, i).join('/'));
        }
      }
      ge.expanded.add(pfade[0].join('/'));
      ge.renderTree();

      const knoten = [...document.querySelectorAll('#genreTree button[aria-expanded]')]
        .filter((b) => b.getAttribute('onclick').includes(g.id))
        .map((b) => b.getAttribute('aria-expanded'));
      return { pfade: pfade.length, knoten };
    });

    expect(zustand.pfade).toBe(4);
    // dieselbe Kategorie, zwei Stellen, zwei Zustaende
    expect(zustand.knoten).toEqual(['false', 'true']);
  });

  test('Suche zeigt den Pfad und blendet den Baum aus', async ({ page }) => {
    await page.fill('#genreSearch', 'meisterlied');
    await page.waitForSelector('#genreResults >> text=Treffer', { timeout: 10000 });

    await expect(page.locator('#genreTreeSection')).toBeHidden();

    // textContent, nicht innerText: die Meta-Zeile ist per CSS versalisiert, und
    // innerText liefert das Ergebnis der Transformation. Dann steckt in
    // "Epik, Lyrik UND Dramatik" ein " UND ", das mit der alten Verkettung
    // nichts zu tun hat.
    const meta = await page.locator('#genreResults').textContent();
    expect(meta).toContain('Einordnung:');
    expect(meta).not.toContain(' UND ');
    // Pfeil statt Aufzaehlung: die Reihenfolge ist die Aussage
    expect(meta).toContain('›');
  });
});
