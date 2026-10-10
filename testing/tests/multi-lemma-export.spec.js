/**
 * Export der Multi-Lemma-Suche als CSV und XLSX (#448)
 *
 * Geprueft wird, was KZW am 2026-09-24 in #448 verlangt hat: eine Zeile je
 * Fundstelle mit Sigle, Titel, Autor*in, Stelle und Kontext, alle Treffer
 * statt der angezeigten, dazu Suchparameter und Korpusauswahl. Ground-Truth
 * fuer den Versmodus aus multi-lemma-verse.spec.js: BUH Vers 98 ("dâ bî ûz
 * ir herzen blüejet || diu vil süeze minne").
 *
 * Laufzeit (#564): der Export laedt jeden Text mit einem Treffer nach, bei
 * minne + herze sind das im Versmodus 66 Dateien (gemessen 10.10.2026), im
 * Naehemodus 109. Deshalb gibt es diese Suche nur einmal (eine Seite, ein
 * Nachladen), und die uebrigen Faelle laufen auf kleinen Suchen mit wenigen
 * Texten.
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const DATUM = '\\d{4}-\\d{2}-\\d{2}';

async function lade(page, buttonId) {
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 120000 }),
    page.click(`#${buttonId}`)
  ]);
  return { name: download.suggestedFilename(), bytes: readFileSync(await download.path()) };
}

/** RFC-4180-Leser fuer das Hausformat (Komma, CRLF, Quoting bei Bedarf). */
function parseCsv(bytes) {
  expect([...bytes.subarray(0, 3)]).toEqual([0xEF, 0xBB, 0xBF]);
  const text = bytes.toString('utf8').slice(1);
  const zeilen = [];
  let zeile = [], feld = '', inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { feld += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else feld += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ',') { zeile.push(feld); feld = ''; }
    else if (c === '\r' && text[i + 1] === '\n') { zeile.push(feld); zeilen.push(zeile); zeile = []; feld = ''; i++; }
    else feld += c;
  }
  if (feld || zeile.length) { zeile.push(feld); zeilen.push(zeile); }
  return zeilen;
}

async function fundstellenZahl(page) {
  const text = await page.locator('#mlExportLeiste').textContent();
  return parseInt(text.match(/Alle ([\d.]+) Fundstellen/)[1].replace(/\./g, ''), 10);
}

test.describe('Multi-Lemma-Export (#448)', () => {
  // Der Export laedt jeden Text mit einem Treffer nach
  test.setTimeout(240000);

  // Eine Seite fuer die drei Faelle der grossen Suche. Die Reihenfolge ist
  // Teil des Aufbaus: der Fehlerfall zuerst, solange noch nichts geladen und
  // zwischengespeichert ist (ctx.zeilen entsteht erst nach einem erfolgreichen
  // Nachladen), dann das einzige volle Nachladen fuer die CSV, danach liest
  // das XLSX dieselben Zeilen aus dem Zwischenspeicher der Suche.
  test.describe('minne + herze im selben Vers', () => {
    test.describe.configure({ mode: 'serial' });
    let page;

    test.beforeAll(async ({ browser }) => {
      page = await browser.newPage();
      // Ein Hook laeuft mit dem Projekt-Timeout (60 s), nicht mit dem des
      // Testblocks; hier ausdruecklich setzen
      test.setTimeout(240000);
      await page.goto('/playground/#multi-lemma&lemmata=minne,herze&mode=verse');
      await page.waitForSelector('#mlExportCsv', { state: 'visible', timeout: 120000 });
    });

    test.afterAll(async () => {
      await page.close();
    });

    test('Fehler beim Nachladen bleibt stehen, der Fortschritt ueberschreibt ihn nicht', async () => {
      // AXR ist die erste Datei der Liste; die drei anderen Arbeiter laufen
      // zu diesem Zeitpunkt schon
      await page.route('**/tei/AXR.tei.xml', route => route.fulfill({ status: 500, body: '' }));
      let downloads = 0;
      const zaehle = () => { downloads++; };
      // Offene TEI-Anfragen zaehlen. waitForLoadState('networkidle') taugt
      // hier nicht: es kehrt sofort zurueck, wenn die Seite es einmal erreicht
      // hatte (gemessen: 1 ms bei vier offenen Anfragen).
      let offen = 0;
      const auf = (r) => { if (r.url().includes('/tei/')) offen++; };
      const zu = (r) => { if (r.url().includes('/tei/')) offen--; };
      page.on('download', zaehle);
      page.on('request', auf);
      page.on('requestfinished', zu);
      page.on('requestfailed', zu);
      try {
        await page.click('#mlExportCsv');
        const status = page.locator('#mlExportStatus');
        await expect(status).toContainText('Export fehlgeschlagen: AXR.tei.xml: HTTP 500', { timeout: 60000 });
        await expect(page.locator('#mlExportCsv')).toBeEnabled();
        // Warten, bis die restlichen Dateien fertig geladen sind, statt einer
        // festen Frist: erst dann steht fest, dass ihr Fortschritt die Meldung
        // nicht mehr ueberschreibt. Der Fortschritt kommt erst nach dem Parsen,
        // also nach requestfinished; der Leerlauf-Aufruf wartet das ab.
        await expect.poll(() => offen, { timeout: 60000 }).toBe(0);
        await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestIdleCallback(() => r()))));
        await expect(status).toContainText('Export fehlgeschlagen');
        expect(downloads).toBe(0);
      } finally {
        page.off('download', zaehle);
        page.off('request', auf);
        page.off('requestfinished', zu);
        page.off('requestfailed', zu);
        await page.unroute('**/tei/AXR.tei.xml');
      }
    });

    test('Im selben Vers: CSV mit allen Treffern, Stelle und Kontext', async () => {
      const n = await fundstellenZahl(page);

      const csv = await lade(page, 'mlExportCsv');
      expect(csv.name).toMatch(new RegExp(`^mhdbdb-multilemma-verse-minne-herze-${DATUM}\\.csv$`));
      const [kopf, ...zeilen] = parseCsv(csv.bytes);
      expect(kopf).toEqual(['Sigle', 'Titel', 'Autor*in', 'Stelle', 'Wort-IDs', 'Belegwörter', 'Kontext', 'Suche', 'Korpusauswahl']);
      expect(zeilen.length).toBe(n);
      expect(zeilen.every(z => z.length === kopf.length)).toBe(true);

      // BUH zaehlt die Verse je Strophe: "V. 12" ist dort mehrdeutig, die
      // Wort-ID des Belegworts nicht
      const buh = zeilen.find(z => z[4].split(' / ').includes('BUH_401012000_9'));
      expect(buh, 'BUH_401012000_9 fehlt').toBeTruthy();
      expect(buh.slice(0, 4)).toEqual(['BUH', buh[1], buh[2], 'V. 12']);
      expect(buh[5]).toBe('herzen / minne');
      expect(buh[6]).toContain('blüejet diu vil süeze minne');
      expect(zeilen.every(z => z[7].startsWith('Im selben Vers: ') && z[7].includes('+'))).toBe(true);
      expect(zeilen.every(z => /^alle \d+ Texte$/.test(z[8]))).toBe(true);
      expect(zeilen.every(z => z[3] !== '' && z[6] !== '' && /^[A-Z0-9]+_\d+_\d+ \/ /.test(z[4]))).toBe(true);
    });

    test('XLSX: gueltiges Paket mit Fundstellen- und Suchblatt', async () => {
      const n = await fundstellenZahl(page);

      const xlsx = await lade(page, 'mlExportXlsx');
      expect(xlsx.name).toMatch(new RegExp(`^mhdbdb-multilemma-verse-minne-herze-${DATUM}\\.xlsx$`));
      expect([...xlsx.bytes.subarray(0, 4)]).toEqual([0x50, 0x4B, 0x03, 0x04]);
      // Die Eintraege sind unkomprimiert ("stored"), der XML-Text steht lesbar
      // in der Datei
      const inhalt = xlsx.bytes.toString('utf8');
      expect(inhalt).toContain('<sheet name="Fundstellen" sheetId="1"');
      expect(inhalt).toContain('<sheet name="Suche" sheetId="2"');
      const blatt1 = inhalt.slice(inhalt.indexOf('<worksheet'), inhalt.indexOf('</worksheet>'));
      expect(blatt1.match(/<row /g).length).toBe(n + 1);
      expect(blatt1).toContain('süeze minne');
      await expect(page.locator('#mlExportStatus')).toContainText(`als XLSX exportiert`);
    });
  });

  test('Nähe-Analyse: Abstand-Spalte, kein Wert über dem Fenster', async ({ page }) => {
    // Kleine Suche (Wîcher, Wîcnant: 2 Texte): minne + herze lud hier rund 60
    // Sekunden lang 109 Texte nach. Gemessen am 10.10.2026: mit Fenster 3 sind
    // es 5 Zeilen, mit Fenster 40 sechs, die sechste liegt also ausserhalb des
    // Fensters, und genau die darf hier nicht erscheinen.
    await page.goto('/playground/#multi-lemma&lemmata=W%C3%AEcher,W%C3%AEcnant&mode=proximity&dist=3');
    await page.waitForSelector('#mlExportCsv', { state: 'visible', timeout: 120000 });
    const n = await fundstellenZahl(page);
    expect(n).toBeGreaterThan(0);

    const [kopf, ...zeilen] = parseCsv((await lade(page, 'mlExportCsv')).bytes);
    expect(kopf).toContain('Abstand (Wörter)');
    const spalte = kopf.indexOf('Abstand (Wörter)');
    expect(zeilen.length).toBe(n);
    expect(zeilen.every(z => Number(z[spalte]) <= 3)).toBe(true);
    expect(zeilen[0][kopf.indexOf('Suche')]).toMatch(/^Nähe-Analyse, max\. 3 Wörter Abstand: /);
  });

  test('Dokument-Suche: eine Zeile je Beleg, Summe wie in der Ansicht', async ({ page }) => {
    // Kleine Suche mit wenigen Texten; minne + herze lief hier in den
    // 60-Sekunden-Timeout
    await page.goto('/playground/#multi-lemma&lemmata=Gringuljete,ors&mode=document');
    await page.waitForSelector('#mlExportCsv', { state: 'visible', timeout: 120000 });
    const n = await fundstellenZahl(page);

    const [kopf, ...zeilen] = parseCsv((await lade(page, 'mlExportCsv')).bytes);
    expect(kopf).toEqual(['Sigle', 'Titel', 'Autor*in', 'Lemma', 'Stelle', 'Wort-ID', 'Kontext davor', 'Beleg', 'Kontext danach', 'Suche', 'Korpusauswahl']);
    expect(zeilen.length).toBe(n);
    expect(zeilen.every(z => z[7] !== '' && z[5] !== '' && /\(lemma_\d+\)$/.test(z[3]))).toBe(true);
    // Beide Lemmata kommen vor, in jeder Sigle der Datei
    const jeSigle = new Map();
    for (const z of zeilen) {
      if (!jeSigle.has(z[0])) jeSigle.set(z[0], new Set());
      jeSigle.get(z[0]).add(z[3]);
    }
    expect([...jeSigle.values()].every(s => s.size === 2)).toBe(true);
  });
});
