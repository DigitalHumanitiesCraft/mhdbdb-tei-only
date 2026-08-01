// tests/corpus.spec.js
import { test, expect } from '@playwright/test';

test.describe('Corpus Loading and Management', () => {
  test.beforeEach(async ({ page }) => {
    // Clear all IndexedDB storage before each test
    await page.goto('/testing/test.html');
    await page.evaluate(async () => {
      // Clear IndexedDB
      const dbs = await indexedDB.databases();
      for (const db of dbs) {
        indexedDB.deleteDatabase(db.name);
      }
      sessionStorage.clear();
    });
  });

  // #314: Der Playground hat keinen Datei-Upload mehr, damit hat die Datenbank
  // MHDBDB_Playground keinen Schreiber. Statt sie per Schema-Migration zu
  // pflegen (so lief es bis #280), loescht der Playground-Start sie einmalig.
  // Geprueft an einer von Hand angelegten Alt-Datenbank.
  test('Alt-Datenbank MHDBDB_Playground wird beim Start entfernt', async ({ page }) => {
    await page.goto('/testing/test.html');

    const seeded = await page.evaluate(async () => {
      await new Promise((resolve, reject) => {
        const request = indexedDB.open('MHDBDB_Playground', 3);
        request.onupgradeneeded = (event) => {
          event.target.result.createObjectStore('tei_files', { keyPath: 'filename' });
        };
        request.onsuccess = () => {
          const db = request.result;
          const tx = db.transaction(['tei_files'], 'readwrite');
          tx.objectStore('tei_files').put({ filename: 'alt.xml', content: '<TEI/>' });
          // Verbindung schliessen, sonst blockiert sie das spaetere deleteDatabase
          tx.oncomplete = () => { db.close(); resolve(); };
          tx.onerror = () => reject(tx.error);
        };
        request.onerror = () => reject(request.error);
      });
      const dbs = await indexedDB.databases();
      return dbs.some((d) => d.name === 'MHDBDB_Playground');
    });
    expect(seeded).toBe(true);

    await page.goto('/playground/index.html');
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

    const stillThere = await page.evaluate(async () => {
      const dbs = await indexedDB.databases();
      return dbs.some((d) => d.name === 'MHDBDB_Playground');
    });
    expect(stillThere).toBe(false);
  });

  test('Corpus index structure after auto-load', async ({ page }) => {
    // Test that the corpus index has the expected structure
    await page.goto('/playground/index.html');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

    const result = await page.evaluate(() => {
      // Auto-load stores corpus in corpusData.texts, not teiData.parsedXML
      const texts = window.playground?.corpusData?.texts;
      if (!texts || texts.length === 0) throw new Error('No corpus texts');

      // Check first text has expected fields
      const firstText = texts[0];

      return {
        success: true,
        textCount: texts.length,
        firstText: {
          id: firstText.id,
          title: firstText.title,
          author: firstText.author,
          wordCount: firstText.wordCount,
        },
        hasAllFields: !!firstText.id && !!firstText.title && !!firstText.author && typeof firstText.wordCount === 'number'
      };
    });

    expect(result.success).toBe(true);
    expect(result.textCount).toBe(667);
    expect(result.hasAllFields).toBe(true);
  });

  test('Corpus progress tracking via UI', async ({ page }) => {
    await page.goto('/playground/index.html');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

    const includedCount = await page.locator('#includedCount').textContent();
    expect(parseInt(includedCount)).toBe(667);
  });

  test('TEIFilesManager - available in playground', async ({ page }) => {
    await page.goto('/playground/index.html');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

    const result = await page.evaluate(() => {
      const teiManager = window.playground?.teiManager;
      if (!teiManager) throw new Error('TEI manager not available');

      return {
        success: true,
        // #314: isTEIFile und loadCorpusIntoPlayground gehoerten zum
        // Upload-Pfad und sind entfernt. Geprueft wird jetzt der aktive
        // Einstiegspunkt der Multi-Lemma-Suche.
        hasMethods: typeof teiManager.searchMultipleLemmasUsingIndex === 'function'
      };
    });

    expect(result.success).toBe(true);
    expect(result.hasMethods).toBe(true);
  });

  test('TEIFilesManager - corpus loaded into corpusData', async ({ page }) => {
    await page.goto('/playground/index.html');

    // Wait for corpus to auto-load
    await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

    const result = await page.evaluate(() => {
      // Auto-load stores corpus in corpusData.texts, not teiData.parsedXML
      const texts = window.playground?.corpusData?.texts;
      if (!texts) throw new Error('No corpusData.texts');

      if (texts.length !== 667) {
        throw new Error(`Expected 667 loaded texts, got ${texts.length}`);
      }

      // Verify lemmaIndex is also populated
      const lemmaIndex = window.playground?.corpusData?.lemmaIndex;
      const lemmaCount = lemmaIndex ? Object.keys(lemmaIndex).length : 0;

      return { success: true, loaded: texts.length, lemmaCount };
    });

    expect(result.success).toBe(true);
    expect(result.loaded).toBe(667);
    expect(result.lemmaCount).toBeGreaterThan(0);
  });

});
