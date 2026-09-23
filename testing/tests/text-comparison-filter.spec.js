/**
 * Tippfilter über den Textlisten des Textvergleichs (#435)
 *
 * Aus Alan van Beeks Testprotokoll (#419, Testfall 7): "bisschen tricky hier
 * den herzog ernst zu finden im dropdownmenu, kann man das nicht einfach
 * eintippen?" Die beiden Listen sind nach Sigle sortiert, der Herzog Ernst
 * steht unter E. KZW hat am 2026-09-15 entschieden: Tippfilter über dem
 * Dropdown.
 *
 * Zeugen, gemessen am 2026-09-23 gegen data/corpus-index.json.gz (667 Texte):
 * "herzog" trifft fünf Texte (ERB, ERD, HHP, HZU, HZU2), "herzog ernst" zwei
 * (ERB, ERD), "parzival" genau einen (PZ). Die Tests verlangen davon nur, was
 * ein Ingest nicht kippt: ERB und ERD sind unter "herzog" dabei, jeder
 * gezeigte Text trägt das Wort, und PZ ist unter "parzival" der einzige.
 *
 * Relative Pfade gegen baseURL, kein fester Port (Laufplan 23.09., #465).
 */

import { test, expect } from '@playwright/test';

/** Optionen einer Liste ohne den Kopfeintrag (value=""). */
function optionen(page, side) {
  return page.locator(`#tcSelect${side} option:not([value=""])`);
}

test.describe('#435: Tippfilter im Textvergleich', () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(120000);
    await page.goto('/playground/#text-comparison');
    await page.waitForSelector('#tcFilterA', { state: 'visible', timeout: 90000 });
  });

  test('"herzog" lässt nur Texte stehen, die das Wort tragen, darunter beide Herzog Ernst', async ({ page }) => {
    const gesamt = await optionen(page, 'A').count();
    expect(gesamt, 'ungefilterte Liste').toBeGreaterThan(100);

    await page.locator('#tcFilterA').fill('herzog');

    const labels = await optionen(page, 'A').allTextContents();
    expect(labels.length).toBeGreaterThan(1);
    expect(labels.length).toBeLessThan(gesamt);
    for (const l of labels) expect(l.toLowerCase()).toContain('herzog');
    const werte = await optionen(page, 'A').evaluateAll(os => os.map(o => o.value));
    expect(werte).toContain('ERB');
    expect(werte).toContain('ERD');

    // Der Kopfeintrag nennt die Menge und ihren Nenner.
    await expect(page.locator('#tcSelectA option[value=""]'))
      .toHaveText(`${labels.length} von ${gesamt} Texten, bitte wählen …`);

    // Die andere Liste bleibt unberührt.
    await expect(optionen(page, 'B')).toHaveCount(gesamt);
  });

  test('bleibt genau ein Text übrig, ist er gewählt', async ({ page }) => {
    await page.locator('#tcFilterA').fill('parzival');
    await expect(optionen(page, 'A')).toHaveCount(1);
    await expect(page.locator('#tcSelectA')).toHaveValue('PZ');
  });

  test('Tippen behält den Fokus im Feld', async ({ page }) => {
    const feld = page.locator('#tcFilterA');
    await feld.click();
    await page.keyboard.type('herzog ernst', { delay: 20 });
    await expect(feld).toBeFocused();
    await expect(feld).toHaveValue('herzog ernst');
    await expect(optionen(page, 'A')).toHaveCount(2);
  });

  test('ein gewählter Text bleibt stehen, auch wenn der Filter ihn nicht trifft', async ({ page }) => {
    await page.locator('#tcSelectA').selectOption('PZ');
    await page.locator('#tcFilterA').fill('herzog');
    await expect(page.locator('#tcSelectA')).toHaveValue('PZ');
    const werte = await optionen(page, 'A').evaluateAll(os => os.map(o => o.value));
    expect(werte).toContain('PZ');
    expect(werte).toContain('ERB');
  });

  test('kein Treffer sagt das, statt eine leere Liste zu zeigen', async ({ page }) => {
    await page.locator('#tcFilterA').fill('qqqqzz');
    await expect(optionen(page, 'A')).toHaveCount(0);
    await expect(page.locator('#tcSelectA option[value=""]')).toHaveText('Kein Text passt zu "qqqqzz"');
  });

  test('Filter und Wahl überstehen "Vergleichen", der Vergleich läuft über die getippten Texte', async ({ page }) => {
    await page.locator('#tcFilterA').fill('parzival');
    await page.locator('#tcFilterB').fill('herzog ernst');
    await page.locator('#tcSelectB').selectOption('ERB');
    await page.locator('#tcCompareBtn').click();

    await expect(page.locator('#tcFilterA')).toHaveValue('parzival');
    await expect(page.locator('#tcFilterB')).toHaveValue('herzog ernst');
    await expect(page.locator('#tcSelectA')).toHaveValue('PZ');
    await expect(page.locator('#tcSelectB')).toHaveValue('ERB');
    await expect(page.locator('[data-tc-cat]').first()).toBeVisible();
  });
});
