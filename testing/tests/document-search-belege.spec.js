/**
 * Dokumentsuche: von der Trefferkarte zu den Belegen (#58)
 *
 * KZW am 2026-10-12, Variante a + c: eine Trefferkarte der Dokumentsuche
 * klappt auf und zeigt die Fundstellen mit kurzem Kontext und
 * hervorgehobenem Suchwort, jede fuehrt an ihre Stelle in der Leseansicht.
 * Dazu "Gesamten Text öffnen" mit allen gesuchten Lemmata hervorgehoben, und
 * bei mehreren Lemmata bleiben die Belege je Lemma erkennbar.
 *
 * Die Erwartungswerte kommen aus dem geladenen Korpus-Index, nicht als
 * Konstante, aus demselben Grund wie in lemma-occurrence-handoff.spec.js:
 * laufender Ingest soll die Spec nicht aus einem Grund rot machen, der mit
 * der Anzeige nichts zu tun hat. Auch welcher Text geprueft wird, waehlt die
 * Spec zur Laufzeit (der kuerzeste passende, damit das TEI schnell laedt).
 *
 * Die Lemmata werden ueber `ids` fest uebergeben: `arm` ist ein Homograph
 * (lemma_285 Adjektiv, lemma_286 Koerperteil), und die Fundstellen muessen
 * zu der ID gehoeren, mit der gesucht wurde.
 */

import { test, expect } from '../warm-page.js';

const ARM_KOERPERTEIL = '286';
const MINNE = '4130';
const HERZE = '2795';

test.beforeEach(() => {
  // Wie lemma-occurrence-handoff.spec.js: die Route wartet auf den vollen
  // Korpus-Index, und die Leseansicht laedt ihn ein zweites Mal.
  test.setTimeout(150000);
});

/** Route aufrufen und auf das fertige Ergebnis der Dokumentsuche warten. */
async function dokumentSuche(page, lemmata, ids) {
  await page.goto(`/playground/#multi-lemma&lemmata=${lemmata.join(',')}&ids=${ids.join(',')}&mode=document`);
  await expect(page.locator('#resultsContainer'))
    .toContainText(`Multi-Lemma-Suche: ${lemmata.join(' + ')}`, { timeout: 120000 });
  await expect(page.locator('#resultsContainer .result-summary-dokument').first()).toBeVisible();
}

/**
 * Kuerzester Text, der `bedingung` erfuellt; liefert Dateiname, Sigle und die
 * Positionslisten je ID aus dem Index.
 */
function waehleText(page, ids, minJeId) {
  return page.evaluate(([ids, minJeId]) => {
    const pos = (t, id) => t.lemmata?.[`lemma_${id}`] || t.lemmata?.[id] || [];
    const kandidaten = window.playground.corpusData.texts
      .filter(t => ids.every((id, i) => pos(t, id).length >= minJeId[i]))
      .sort((a, b) => a.wordCount - b.wordCount);
    const t = kandidaten[0];
    if (!t) return null;
    return {
      filename: t.filename,
      id: t.id,
      positionen: ids.map(id => [...pos(t, id)].sort((a, b) => a - b))
    };
  }, [ids, minJeId]);
}

function karte(page, filename) {
  return page.locator('#resultsContainer .result-summary-dokument')
    .filter({ has: page.locator('h4', { hasText: new RegExp(`^${filename.replace(/\./g, '\\.')}$`) }) });
}

async function aufklappen(page, k) {
  await k.locator('h4').click();
  await expect(k).toHaveClass(/expanded/);
  await expect(k.locator('.beleg-gruppe').first()).toBeVisible({ timeout: 60000 });
}

function linkTeile(href) {
  const u = new URL(href, 'http://x/playground/');
  return {
    pfad: u.pathname,
    textId: u.searchParams.get('textId'),
    lemmaIds: u.searchParams.get('lemmaIds'),
    position: u.searchParams.get('position')
  };
}

test.describe('#58: Fundstellen der Dokumentsuche', () => {
  test('die Karte klappt auf und zeigt jede Fundstelle des Lemmas mit Kontext', async ({ page }) => {
    await dokumentSuche(page, ['arm'], [ARM_KOERPERTEIL]);
    const text = await waehleText(page, [ARM_KOERPERTEIL], [2]);
    expect(text, 'kein Text mit mindestens zwei Belegen, der Test beweist nichts').toBeTruthy();
    const soll = text.positionen[0];

    const k = karte(page, text.filename);
    await expect(k).toHaveCount(1);
    // Vor dem Aufklappen ist nichts geladen
    await expect(k.locator('.beleg-link')).toHaveCount(0);
    await aufklappen(page, k);

    const gruppen = k.locator('.beleg-gruppe');
    await expect(gruppen).toHaveCount(1);
    await expect(gruppen.first()).toHaveAttribute('data-lemma-id', `lemma_${ARM_KOERPERTEIL}`);

    const zeilen = k.locator('.beleg-link');
    await expect(zeilen).toHaveCount(soll.length);
    const ist = await zeilen.evaluateAll(els => els.map(el => ({
      href: el.getAttribute('href'),
      ziel: el.getAttribute('target'),
      wort: el.querySelector('mark.beleg-wort')?.textContent.trim() || '',
      stelle: el.querySelector('.detail-meta')?.textContent.trim() || '',
      kontext: el.querySelector('.detail-snippet')?.textContent.replace(/\s+/g, ' ').trim() || ''
    })));
    ist.forEach((z, i) => {
      const teile = linkTeile(z.href);
      expect(teile.pfad).toBe('/korpus.html');
      expect(teile.textId).toBe(text.id);
      expect(teile.lemmaIds).toBe(ARM_KOERPERTEIL);
      expect(Number(teile.position), `Zeile ${i + 1}: Position aus dem Index, in Textfolge`).toBe(soll[i]);
      expect(z.ziel).toBe('_blank');
      expect(z.wort, `Zeile ${i + 1}: hervorgehobenes Wort`).not.toBe('');
      expect(z.stelle, `Zeile ${i + 1}: Stellenangabe`).not.toBe('');
      expect(z.kontext.length, `Zeile ${i + 1}: Kontext um das Wort`).toBeGreaterThan(z.wort.length);
    });

    // Zuklappen und wieder aufklappen laedt nicht neu und verliert nichts
    await k.locator('h4').click();
    await expect(k).not.toHaveClass(/expanded/);
    await k.locator('h4').click();
    await expect(k).toHaveClass(/expanded/);
    await expect(zeilen).toHaveCount(soll.length);
  });

  test('ein Klick auf eine freie Stelle der Fundstellenliste klappt die Karte nicht zu', async ({ page }) => {
    await dokumentSuche(page, ['arm'], [ARM_KOERPERTEIL]);
    const text = await waehleText(page, [ARM_KOERPERTEIL], [2]);
    expect(text).toBeTruthy();
    const k = karte(page, text.filename);
    await aufklappen(page, k);

    // Der Gruppenkopf liegt im aufgeklappten Bereich und ist kein Link
    await k.locator('.beleg-gruppe h5').first().click();
    await expect(k).toHaveClass(/expanded/);
    await expect(k.locator('.beleg-link').first()).toBeVisible();

    // Der Rand der Karte unter der Fundstellenliste ist ebenfalls kein Kopf
    const liste = await k.locator('.result-details').boundingBox();
    const rahmen = await k.boundingBox();
    await k.click({ position: { x: 10, y: liste.y + liste.height - rahmen.y + 6 } });
    await expect(k).toHaveClass(/expanded/);

    // Der Kopf der Karte klappt weiterhin zu
    await k.locator('h4').click();
    await expect(k).not.toHaveClass(/expanded/);
  });

  test('eine Fundstelle öffnet die Leseansicht genau an dieser Stelle', async ({ page }) => {
    await dokumentSuche(page, ['arm'], [ARM_KOERPERTEIL]);
    const text = await waehleText(page, [ARM_KOERPERTEIL], [2]);
    expect(text).toBeTruthy();
    const k = karte(page, text.filename);
    await aufklappen(page, k);

    // Die zweite Fundstelle, nicht die erste: der Sprung auf Treffer 1 waere
    // auch ohne Positionsparameter das Verhalten der Leseansicht.
    const [leser] = await Promise.all([
      page.context().waitForEvent('page'),
      k.locator('.beleg-link').nth(1).click()
    ]);
    await expect(leser.locator('#readingTitle')).not.toBeEmpty({ timeout: 120000 });
    await expect(leser.locator('#highlightIndicator'))
      .toHaveText(`Treffer 2 von ${text.positionen[0].length}`, { timeout: 30000 });
    await leser.close();
  });

  test('„Gesamten Text öffnen“ führt ohne Sprungziel in den ganzen Text, alle Belege hervorgehoben', async ({ page }) => {
    await dokumentSuche(page, ['arm'], [ARM_KOERPERTEIL]);
    const text = await waehleText(page, [ARM_KOERPERTEIL], [2]);
    expect(text).toBeTruthy();
    const k = karte(page, text.filename);
    const link = k.getByRole('link', { name: 'Gesamten Text öffnen' });
    await expect(link).toHaveCount(1);

    const teile = linkTeile(await link.getAttribute('href'));
    expect(teile.pfad).toBe('/korpus.html');
    expect(teile.textId).toBe(text.id);
    expect(teile.lemmaIds).toBe(ARM_KOERPERTEIL);
    expect(teile.position).toBeNull();

    const [leser] = await Promise.all([
      page.context().waitForEvent('page'),
      link.click()
    ]);
    // Der Klick auf den Link klappt die Karte nicht auf
    await expect(k).not.toHaveClass(/expanded/);
    await expect(leser.locator('#readingTitle')).not.toBeEmpty({ timeout: 120000 });
    await expect(leser.locator('#highlightIndicator'))
      .toHaveText(`Treffer 1 von ${text.positionen[0].length}`, { timeout: 30000 });
    await leser.close();
  });

  test('mehrere Lemmata: Fundstellen je Lemma getrennt, gekürzt mit Hinweis', async ({ page }) => {
    await dokumentSuche(page, ['minne', 'herze'], [MINNE, HERZE]);
    // Kuerzester Text, in dem minne mehr Belege hat, als die Karte zeigt
    const text = await waehleText(page, [MINNE, HERZE], [51, 1]);
    expect(text, 'kein Text mit mehr als 50 Belegen von minne, Kürzung nicht prüfbar').toBeTruthy();
    const [minne, herze] = text.positionen;

    const k = karte(page, text.filename);
    // Vorschau weist die Zahl je Lemma aus, nicht nur die Summe
    await expect(k.locator('.summary-preview'))
      .toHaveText(new RegExp(`^${minne.length + herze.length} Belege: .+ ${minne.length} · .+ ${herze.length}$`));
    await aufklappen(page, k);

    const gruppen = k.locator('.beleg-gruppe');
    await expect(gruppen).toHaveCount(2);
    expect(await gruppen.evaluateAll(els => els.map(el => el.dataset.lemmaId)))
      .toEqual([`lemma_${MINNE}`, `lemma_${HERZE}`]);

    for (const [i, liste] of [[0, minne], [1, herze]]) {
      const g = gruppen.nth(i);
      const id = i === 0 ? MINNE : HERZE;
      await expect(g.locator('.beleg-zahl')).toHaveText(liste.length === 1 ? '1 Beleg' : `${liste.length} Belege`);
      const zeilen = await g.locator('.beleg-link').evaluateAll(els => els.map(el => ({
        lemma: el.dataset.lemmaId,
        href: el.getAttribute('href')
      })));
      expect(zeilen.length).toBe(Math.min(liste.length, 50));
      zeilen.forEach((z, j) => {
        expect(z.lemma).toBe(`lemma_${id}`);
        const teile = linkTeile(z.href);
        expect(Number(teile.position)).toBe(liste[j]);
        // Die Leseansicht hebt beide gesuchten Lemmata hervor
        expect(teile.lemmaIds).toBe(`${MINNE},${HERZE}`);
      });
      const hinweis = g.locator('.beleg-gekuerzt');
      if (liste.length > 50) {
        await expect(hinweis).toContainText(`50 von ${liste.length} Belegen angezeigt`);
      } else {
        await expect(hinweis).toHaveCount(0);
      }
    }

    // Julia 16.10.: bei sehr vielen Belegen scrollt die Liste in sich, die Karte
    // wächst nicht mit. minne hat hier mehr als 50 Belege, also muss die Liste
    // scrollen; der Fokus kommt per Tastatur hinein (role=region, tabindex=0).
    const liste = gruppen.first().locator('.beleg-liste');
    const mass = await liste.evaluate(el => ({
      overflowY: getComputedStyle(el).overflowY,
      scrollt: el.scrollHeight > el.clientHeight,
      hoehe: el.getBoundingClientRect().height,
      maxHoehe: parseFloat(getComputedStyle(el).maxHeight)
    }));
    expect(mass.overflowY).toBe('auto');
    expect(mass.scrollt, 'Liste mit über 50 Belegen scrollt in sich').toBe(true);
    expect(mass.hoehe).toBeLessThanOrEqual(mass.maxHoehe + 1);
    await expect(liste).toHaveAttribute('role', 'region');
    await expect(liste).toHaveAttribute('tabindex', '0');
  });
});
