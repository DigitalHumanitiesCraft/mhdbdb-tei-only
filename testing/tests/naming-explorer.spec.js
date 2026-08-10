/**
 * Naming-Explorer Tests (#59 Erweiterte Figurenbezeichnungen, Beta)
 *
 * Smoke-Tests fuer das kuratierte Figurenbezeichnungs-Modul: Route #naming,
 * Werk/Figur-Auswahl, Kategorie-Tabs, Belegstellen-Expand, MHG-normalisierter
 * Term-Filter und Pflicht-Attribution (Lizenzauflage CC BY-NC-SA).
 *
 * Datengrundlage ist data/naming-index.json.gz (extern kuratiert, lindabeutel/
 * Naming-analysis). Die Tests locken Struktur, nicht exakte Zahlen — bei einem
 * Quelldaten-Update muss nur der weiche Iwein-Lock (242 Belege) mitwandern.
 */

import { test, expect } from '@playwright/test';

test.describe('Naming Explorer (#59)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8080/playground/#naming');
    // dispatchFromHash() laeuft erst nach Corpus-Load; danach laedt das Modul
    // seinen eigenen Index lazy (fetch+pako, ~110 KB)
    await page.waitForSelector('#neWorkSelect', { state: 'visible', timeout: 60000 });
  });

  async function selectIwein(page) {
    await page.selectOption('#neWorkSelect', 'IW');
    await page.selectOption('#neFigureSelect', 'Iwein');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
  }

  test('Route #naming rendert Modul mit allen 4 Werken und Attribution', async ({ page }) => {
    // Beta-Modul-Header
    await expect(page.locator('#resultsContainer')).toContainText('Erweiterte Figurenbezeichnungen');

    // Genau die 4 kuratierten Werke (plus Platzhalter-Option)
    const values = await page.locator('#neWorkSelect option').allTextContents();
    expect(values.join(' ')).toContain('IW - Iwein');
    expect(values.join(' ')).toContain('ENE - Eneasroman');
    expect(values.join(' ')).toContain('ROL - Rolandslied');
    expect(values.join(' ')).toContain('TRO - Trojanerkrieg');
    expect(values.length).toBe(5);

    // Pflicht-Attribution (Lizenzauflage) muss ohne Auswahl sichtbar sein
    await expect(page.locator('#resultsContainer')).toContainText('Naming-analysis nach Linda Beutel-Thurow');
    await expect(page.locator('#resultsContainer a[href*="doi.org/10.5281/zenodo.18770138"]')).toBeVisible();
  });

  test('Werk + Figur liefert Summary und Term-Tabelle mit drei Kategorien', async ({ page }) => {
    await selectIwein(page);

    // Weicher Daten-Lock: Iwein hat 242 kuratierte Belegstellen (Stand edd39cc)
    await expect(page.locator('#resultsContainer')).toContainText('242 kuratierte Belegstellen');

    // Alle drei Kategorien kommen in der Tabelle vor
    const badges = await page.locator('[data-ne-term] td:nth-child(2)').allTextContents();
    const badgeSet = new Set(badges.map(b => b.trim()));
    expect(badgeSet.has('Eigenname')).toBe(true);
    expect(badgeSet.has('Antonomasie')).toBe(true);
    expect(badgeSet.has('Epitheton')).toBe(true);

    // Top-Term ist nach Haeufigkeit sortiert (hoechster Count zuerst)
    const counts = await page.locator('[data-ne-term] td:nth-child(3)').allTextContents();
    const nums = counts.map(c => parseInt(c.replace(/\./g, ''), 10));
    expect(nums[0]).toBe(Math.max(...nums));
  });

  test('Kategorie-Tab filtert auf Epitheta', async ({ page }) => {
    await selectIwein(page);

    await page.click('[data-ne-cat="epi"]');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    const badges = await page.locator('[data-ne-term] td:nth-child(2)').allTextContents();
    expect(badges.length).toBeGreaterThan(0);
    for (const b of badges) {
      expect(b.trim()).toBe('Epitheton');
    }
  });

  test('Belegstellen-Expand zeigt Vers, Phrase und Sprecher', async ({ page }) => {
    await selectIwein(page);

    await page.locator('[data-ne-term]').first().click();

    // Evidence-Row: Versangabe + Sprecher-Label
    await expect(page.locator('#resultsContainer')).toContainText(/V\. \d/);
    await expect(page.locator('#resultsContainer')).toContainText(/Erzähler|Figurenrede|Selbstnennung/);
  });

  test('TRO-Belegstellen verlinken in die Leseansicht, IW-Belegstellen nicht', async ({ page }) => {
    // TRO/ROL: Verszählung deckungsgleich mit MHDBDB -> Vers-Deep-Link
    await page.selectOption('#neWorkSelect', 'TRO');
    await page.selectOption('#neFigureSelect', 'Achilles');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    await page.locator('[data-ne-term]').first().click();

    const link = page.locator('#resultsContainer a[href*="korpus.html?textId=TRO&verse="]').first();
    await expect(link).toBeVisible();
    await expect(link).toContainText(/V\. \d/);

    // IW: abweichende Editionszählung -> bewusst kein Link
    await selectIwein(page);
    await page.locator('[data-ne-term]').first().click();
    await expect(page.locator('#resultsContainer')).toContainText(/V\. \d/);
    await expect(page.locator('#resultsContainer a[href*="verse="]')).toHaveCount(0);
  });

  test('Term-Filter ist MHG-normalisiert (tore findet tôre)', async ({ page }) => {
    await selectIwein(page);

    await page.fill('#neNameFilter', 'tore');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    const terms = await page.locator('[data-ne-term] td:nth-child(1)').allTextContents();
    expect(terms.length).toBeGreaterThan(0);
    expect(terms.some(t => t.includes('tôre'))).toBe(true);
  });

  test('Werk-Wechsel setzt Figur zurueck', async ({ page }) => {
    await selectIwein(page);

    await page.selectOption('#neWorkSelect', 'ROL');
    // Figur-Select ist zurueckgesetzt, Tabelle weg, Hinweis sichtbar
    await expect(page.locator('#neFigureSelect')).toHaveValue('');
    await expect(page.locator('#resultsContainer')).toContainText('Bitte eine Figur auswählen');
  });

  // --- Lindas beide Wuensche, #59-Kommentar 2026-07-29 -------------------

  test('Unterfilter nach nennender Instanz grenzt die Belegstellen ein', async ({ page }) => {
    await selectIwein(page);

    // Ohne Filter die Gesamtzahl, mit Filter die Teilmenge samt Bezugsgroesse
    await expect(page.locator('#resultsContainer')).toContainText('242 kuratierte Belegstellen');
    const optionen = await page.locator('#neSubFilter option').allTextContents();
    expect(optionen[0]).toContain('Alle (242)');
    expect(optionen.join(' ')).toContain('Erzähler');
    expect(optionen.join(' ')).toContain('Selbstnennung');
    // Einzelne Nenner stehen unter "Figurenrede, alle"
    expect(optionen.some(o => o.trim().startsWith('Lunete'))).toBe(true);

    // Wert statt Label: die Einzelnenner sind mit NBSP eingerueckt
    await page.selectOption('#neSubFilter', 'fig:lunete');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    await expect(page.locator('#resultsContainer')).toContainText('31 von 242 kuratierte Belegstellen');

    // Belegstellen tragen jetzt nur noch Lunete als Sprecher
    await page.locator('[data-ne-term]').first().click();
    const evidence = await page.locator('tr.bg-slate-50\\/50').first().innerText();
    expect(evidence).toContain('Figurenrede: Lunete');
    expect(evidence).not.toContain('Erzähler');
  });

  test('Nenner-Perspektive gruppiert die Terme nach genannter Figur', async ({ page }) => {
    await page.click('[data-ne-persp="namer"]');
    await page.selectOption('#neWorkSelect', 'IW');
    // Der Nenner-Select fuehrt den Erzaehler als eigenen Eintrag
    const nenner = await page.locator('#neFigureSelect option').allTextContents();
    expect(nenner.some(o => o.startsWith('Erzähler'))).toBe(true);
    expect(nenner.some(o => o.startsWith('Iwein'))).toBe(true);

    // Lindas Frage: "Welche Benennungen fuer wen findet Iwein im Iwein?"
    await page.selectOption('#neFigureSelect', 'iwein');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    await expect(page.locator('#resultsContainer')).toContainText(/benennt \d+ Figuren in \d+ kuratierten Belegstellen/);

    // Vierte Spalte "Genannte Figur" kommt dazu, mit mehr als einer Figur
    await expect(page.locator('thead th').first()).toHaveText('Genannte Figur');
    const figuren = (await page.locator('[data-ne-term] td:first-child').allTextContents())
      .map(t => t.trim()).filter(Boolean);
    expect(new Set(figuren).size).toBeGreaterThan(1);
    // Kategorie und Haeufigkeit ruecken um eine Spalte weiter
    const badges = await page.locator('[data-ne-term] td:nth-child(3)').allTextContents();
    expect(new Set(badges.map(b => b.trim())).has('Antonomasie')).toBe(true);
  });

  test('Perspektivwechsel setzt die Auswahl zurueck', async ({ page }) => {
    await selectIwein(page);
    await page.click('[data-ne-persp="namer"]');
    // Ein Figurenname ist kein Nenner-Schluessel, die Auswahl darf nicht stehenbleiben
    await expect(page.locator('#neFigureSelect')).toHaveValue('');
    await expect(page.locator('#neWorkSelect')).toHaveValue('IW');
    await expect(page.locator('#resultsContainer')).toContainText('Bitte einen Nenner auswählen');
  });

  test('Die Notation der Quelle steht in der Nennerliste und wird erklaert', async ({ page }) => {
    // Das fuehrende '#' markiert eine Instanz, die keine handelnde Figur des
    // Werks ist (Linda, #59 2026-08-10). Es wird angezeigt statt abgeschnitten:
    // #David (zitiert) und ein handelnder David waeren sonst derselbe Nenner.
    await page.click('[data-ne-persp="namer"]');
    await page.selectOption('#neWorkSelect', 'ROL');

    const nenner = await page.locator('#neFigureSelect option').allTextContents();
    expect(nenner.some(o => o.startsWith('#'))).toBe(true);
    // Genau ein Eintrag je Nenner, seit Linda die Schreibungen vereinheitlicht
    // hat (Quell-Commit b7cc0585): frueher zerfiel Engel in #Engel und Engel.
    expect(nenner.filter(o => /^#?Engel /.test(o)).length).toBe(1);
    await expect(page.locator('#resultsContainer')).toContainText('Notation der Quelle');

    await page.selectOption('#neFigureSelect', '#engel');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    await expect(page.locator('#resultsContainer')).toContainText('#Engel');
  });

  test('Alias-Override zaehlt Alexander bei Paris als Deckname', async ({ page }) => {
    // Deckname des Paris im Trojanerkrieg, werkspezifisch in
    // scripts/ingest/naming/alias-overrides.json. Eigene vierte Kategorie
    // statt Eigenname auf Lindas Praezisierung hin (#59, 2026-08-10).
    await page.selectOption('#neWorkSelect', 'TRO');
    await page.selectOption('#neFigureSelect', 'Paris');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    // Der Deckname-Tab erscheint nur, wo die Kategorie trifft: hier ja
    await expect(page.locator('[data-ne-cat="deck"]')).toBeVisible();

    await page.fill('#neNameFilter', 'Alexander');
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });
    const zeilen = await page.locator('[data-ne-term]').allTextContents();
    expect(zeilen.length).toBe(1);
    await expect(page.locator('[data-ne-term] td:nth-child(2)')).toHaveText('Deckname');
  });

  test('Der Erzaehler ist als Nenner auswaehlbar und liefert Terme', async ({ page }) => {
    // Regression aus PR #360: NARRATOR_KEY lag als U+0000-Sentinel im
    // option-value, und der HTML-Tokenizer macht daraus U+FFFD. Der Wert aus
    // dem Select traf den Schluessel damit nie, die Auswahl lieferte in allen
    // vier Werken 0 Treffer. Der Erzaehler ist der belegstaerkste Nenner
    // jedes Werks, und kein Test hatte ihn je ausgewaehlt.
    await page.click('[data-ne-persp="namer"]');
    await page.selectOption('#neWorkSelect', 'ROL');
    // Den Wert aus dem DOM zuruecklesen statt ihn hinzuschreiben: genau das
    // ist die Eigenschaft, die der Sentinel braucht. Mit dem NUL-Sentinel
    // stuende hier "�erzaehler", die Auswahl gelaenge und liefe leer.
    const erzaehlerWert = await page.$eval('#neFigureSelect', sel =>
      [...sel.options].find(o => o.textContent.startsWith('Erzähler'))?.value);
    expect(erzaehlerWert).toBeTruthy();
    await page.selectOption('#neFigureSelect', erzaehlerWert);
    await page.waitForSelector('[data-ne-term]', { state: 'visible', timeout: 5000 });

    // Tausenderpunkt zulassen: der ROL-Erzaehler hat 1.222 Belege
    await expect(page.locator('#resultsContainer')).toContainText(/benennt [\d.]+ Figuren in [\d.]+ kuratierten Belegstellen/);
    // Die Auswahl haelt den Re-Render aus: der Schluessel muss durch das
    // Attribut und wieder zurueck kommen, sonst springt das Select auf leer
    await expect(page.locator('#neFigureSelect')).not.toHaveValue('');
    await expect(page.locator('#resultsContainer .text-lg')).toHaveText('Erzähler');
  });

  test('Der Deckname-Tab bleibt weg, wo die Kategorie nicht trifft', async ({ page }) => {
    // Genau ein Beleg im ganzen Index; eine dauerhafte Null-Kategorie neben
    // drei gefuellten laese sich wie ein Erhebungsmangel.
    await selectIwein(page);
    await expect(page.locator('[data-ne-cat="eig"]')).toBeVisible();
    await expect(page.locator('[data-ne-cat="deck"]')).toHaveCount(0);
  });
});
