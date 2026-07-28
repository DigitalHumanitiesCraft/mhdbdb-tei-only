/**
 * Echte Hapaxlegomena Tests (#196)
 *
 * Verifiziert das 11. TEI-Analyse-Werkzeug im Playground: korpusweite
 * Frequenzaggregation (Hapax/Dis/Tris) mit Filter-Toolbar und Detail-Panel.
 *
 * Achtung bei den beiden NUM-Tests: sie ankern auf den Ziffern-Lemmata 42/46/49
 * (`/^\d/` auf dem ersten Listeneintrag). Genau diese Lemmata sollen mit #228
 * aus dem Korpus verschwinden. Wenn #228 umgesetzt ist, werden die Tests rot,
 * obwohl der Filter weiter korrekt arbeitet — dann ist der Anker zu ersetzen,
 * nicht der Filter zu reparieren. Die Schwellwert-Assertion `> 100` übersteht
 * #228 dagegen (116 Lemmata bleiben).
 *
 * Der Wörterbuchnetz-Test spiegelt den Attribut-Breakout-Regressionstest aus
 * results-table.spec.js: derselbe Shared Client (assets/js/lib/woerterbuchnetz.js)
 * rendert hier im Detail-Panel — javascript:-URLs muss der Client filtern,
 * Quote/Markup im wbnetzlink muss escapet im href landen (Review-Finding #206).
 */

import { test, expect } from '@playwright/test';

test.describe('Issue #196: Echte Hapaxlegomena', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#hapax-legomena');
    await page.waitForSelector('#hxFreq', { state: 'visible', timeout: 60000 });
  });

  test('NUM-Filter: Ziffern-Lemmata stehen nicht mehr auf den ersten Plätzen', async ({ page }) => {
    // Anlass des Filters (KZW 27.07.): die Ziffern-Lemmata 42/46/49 standen auf
    // den Rängen 1 bis 3, weil die Liste alphabetisch sortiert ist und Ziffern
    // vor Buchstaben sortieren. Der Filter ist per Default an.
    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });

    const checkbox = page.locator('#hxHideNum');
    await expect(checkbox).toBeChecked();

    // Zweite Zelle = Lemma; die erste trägt die laufende Nummer.
    const erstesLemma = () => page.locator('tbody tr').first().locator('td').nth(1).innerText();
    // Die Gesamtzahl steht im Listenkopf, die Tabelle selbst paginiert bei 100.
    const gesamt = async () => {
      const text = await page.locator('#resultsContainer').innerText();
      return parseInt(text.match(/([\d.]+) Lemmata mit Frequenz/)[1].replace(/\./g, ''), 10);
    };

    expect((await erstesLemma()).trim()).not.toMatch(/^\d/);
    const summeAn = await gesamt();

    // Ausgeschaltet müssen sie wieder auftauchen, und zwar ganz oben.
    await checkbox.uncheck();
    await page.waitForTimeout(500);
    expect(await gesamt()).toBeGreaterThan(summeAn);
    expect((await erstesLemma()).trim()).toMatch(/^\d/);
  });

  test('NUM-Filter: explizite Wortart-Facette NUM schlägt den Default', async ({ page }) => {
    // Wer in der Facette gezielt NUM wählt, will Zahlwörter sehen und darf
    // nicht kommentarlos nur die Lemmata mit Mehrfach-Wortart bekommen.
    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });
    await expect(page.locator('#hxHideNum')).toBeChecked();

    await page.selectOption('#hxPos', 'NUM');
    await page.waitForTimeout(500);

    // Ohne den Vorrang blieben nur die 47 Lemmata mit Mehrfach-Wortart übrig.
    const text = await page.locator('#resultsContainer').innerText();
    const gesamt = parseInt(text.match(/([\d.]+) Lemmata mit Frequenz/)[1].replace(/\./g, ''), 10);
    expect(gesamt).toBeGreaterThan(100);

    // Darunter wieder die reinen Ziffern-Lemmata.
    const erstesLemma = await page.locator('tbody tr').first().locator('td').nth(1).innerText();
    expect(erstesLemma.trim()).toMatch(/^\d/);
  });

  test('NAM-Facette schlägt den Eigennamen-Default und deaktiviert dessen Checkbox', async ({ page }) => {
    // Symmetrisch zum NUM-Vorrang: ohne ihn liefert die Facette NAM eine leere
    // Liste, weil "Eigennamen ausblenden" per Default an ist. Der Test fällt
    // ohne die Änderung durch, weil dann 0 statt gut 3.000 Zeilen kommen.
    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });
    await expect(page.locator('#hxHideNames')).toBeChecked();

    await page.selectOption('#hxPos', 'NAM');
    await expect(page.locator('[data-hx-detail]').first()).toBeVisible({ timeout: 30000 });

    const text = await page.locator('#resultsContainer').innerText();
    const gesamt = parseInt(text.match(/([\d.]+) Lemmata mit Frequenz/)[1].replace(/\./g, ''), 10);
    expect(gesamt).toBeGreaterThan(100);

    // Die Checkbox darf nicht angehakt und wirkungslos dastehen.
    await expect(page.locator('#hxHideNames')).toBeDisabled();
    await expect(page.locator('#hxHideNum')).toBeEnabled();
  });

  test('Detail-Panel nennt Werktitel und Autor der Fundstelle (#196)', async ({ page }) => {
    // KZW 28.07.: "wenn bei den Details auch noch direkt stehen wuerde, wer der
    // Autor ist. Das interessiert bei Hapax besonders auf den ersten Blick."
    // Faellt ohne die Aenderung durch: vor #196 stand im Panel nur die Sigle
    // in der Tabellenspalte, das Panel selbst hatte Konzepte und Woerterbuch.
    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });
    await page.locator('[data-hx-detail]').first().click();

    const panel = page.locator('[id^="hxDetailCell-"]').first();
    await expect(panel).toContainText('Fundstellen:', { timeout: 15000 });

    // Werktitel als Reader-Link, und zwar der TITEL, nicht die Sigle. Ein
    // Laengenvergleich reichte dafuer nicht: Siglen wie DJEM haben vier
    // Zeichen und bestuenden ihn auch als Fallback.
    const zeile = panel.locator('li').first();
    const titel = (await zeile.locator('a').innerText()).trim();
    const sigle = (await zeile.locator('span.font-mono').innerText()).trim();
    await expect(zeile.locator('a')).toHaveAttribute('href', /korpus\.html\?textId=/);
    expect(titel).not.toBe(sigle);

    // Autor per eigenem Attribut statt per Klammer-Regex: Werktitel duerfen
    // selbst Klammern enthalten ("Wenzelsbibel (Pentateuch: ...)"), und 7 der
    // 667 Texte haben gar keinen Autor. Deshalb ueber alle Fundstellen des
    // Panels pruefen, nicht nur ueber die erste.
    expect(await panel.locator('li [data-hx-autor]').count()).toBeGreaterThan(0);
  });

  test('Route + Sidebar-Button öffnen das Modul, Liste füllt sich', async ({ page }) => {
    await expect(page.locator('#resultsContainer')).toContainText('Hapax');
    await expect(page.locator('#showHapaxLegomenaBtn')).toBeVisible();

    // Korpusweite Aggregation liefert Zeilen mit Detail-Buttons
    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });
    const rowCount = await page.locator('[data-hx-detail]').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('Wörterbuchnetz-Links im Detail-Panel: javascript:-URLs gefiltert, Attribut-Breakout escapet', async ({ page }) => {
    // Stub der externen API (Muster aus results-table.spec.js): ein
    // javascript:-Link (muss der Shared Client filtern) + ein http(s)-Link
    // mit Quote/Markup im Wert (muss escapet in href landen, kein Breakout).
    const evilHref = 'https://example.com/x?a="><img src=x onerror=alert(1)>';
    await page.route('https://api.woerterbuchnetz.de/**', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ result_set: [
        { sigle: 'MWB', lemma: 'minne', gram: 'stF', wbnetzid: 'X1', wbnetzlink: 'javascript:alert(1)' },
        { sigle: 'MWB', lemma: 'minne', gram: 'stN', wbnetzid: 'X2', wbnetzlink: evilHref },
      ]}),
    }));

    await page.waitForSelector('[data-hx-detail]', { state: 'visible', timeout: 60000 });
    await page.click('[data-hx-detail="0"]');

    const dict = page.locator('#hxDict-0');
    // 2 Wörterbücher × 1 sicherer Eintrag; javascript: gefiltert
    await expect(dict.locator('a')).toHaveCount(2, { timeout: 15000 });

    // Kein Breakout: der komplette bösartige Wert steht IM href-Attribut,
    // im Detail-Panel wurde kein <img> injiziert.
    const hrefs = await dict.locator('a').evaluateAll(as => as.map(a => a.getAttribute('href')));
    for (const href of hrefs) {
      expect(href).toBe(evilHref);
    }
    await expect(page.locator('#hxDetailCell-0 img')).toHaveCount(0);
  });
});
