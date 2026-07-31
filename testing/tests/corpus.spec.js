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

  // Seit #280 hat MHDBDB_Playground genau einen Store. Die frueheren Stores
  // corpus_tei_files, authority_files und metadata hatten keinen Schreiber mehr
  // und werden in DB-Version 3 auch aus bestehenden Browser-Datenbanken geloescht.
  test('IndexedDB schema - version 3 keeps only tei_files', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      if (dbManager.dbVersion !== 3) {
        throw new Error(`Expected DB version 3, got ${dbManager.dbVersion}`);
      }

      const storeNames = Array.from(dbManager.db.objectStoreNames);
      if (!storeNames.includes('tei_files')) {
        throw new Error('tei_files store not found');
      }

      return { success: true, version: dbManager.dbVersion, stores: storeNames };
    });

    expect(result.success).toBe(true);
    expect(result.version).toBe(3);
    expect(result.stores).toEqual(['tei_files']);
  });

  // Migrationspfad: eine Datenbank auf dem alten Stand (Version 2, vier Stores,
  // Daten im authority_files-Store) muss beim naechsten Oeffnen auf Version 3
  // hochgezogen werden, die Altstores verlieren und tei_files behalten.
  test('IndexedDB schema - v2 database is migrated to v3', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      // Alte v2-Datenbank von Hand nachbauen
      await new Promise((resolve, reject) => {
        const request = indexedDB.open('MHDBDB_Playground', 2);
        request.onupgradeneeded = (event) => {
          const db = event.target.result;
          const teiStore = db.createObjectStore('tei_files', { keyPath: 'filename' });
          teiStore.createIndex('timestamp', 'timestamp', { unique: false });
          db.createObjectStore('corpus_tei_files', { keyPath: 'filename' });
          const authStore = db.createObjectStore('authority_files', { keyPath: 'filename' });
          authStore.createIndex('expires', 'expires', { unique: false });
          db.createObjectStore('metadata', { keyPath: 'key' });
        };
        request.onsuccess = () => {
          const db = request.result;
          const tx = db.transaction(['tei_files', 'authority_files'], 'readwrite');
          tx.objectStore('tei_files').put({ filename: 'keep-me.xml', content: '<TEI/>', timestamp: Date.now() });
          tx.objectStore('authority_files').put({ filename: 'lexicon.xml', content: 'stale', expires: Date.now() });
          tx.oncomplete = () => { db.close(); resolve(); };
          tx.onerror = () => reject(tx.error);
        };
        request.onerror = () => reject(request.error);
      });

      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();
      await dbManager.initialize();

      const stores = Array.from(dbManager.db.objectStoreNames);
      const survived = await dbManager.loadTEIFile('keep-me.xml');

      return { success: true, version: dbManager.db.version, stores, survived };
    });

    expect(result.success).toBe(true);
    expect(result.version).toBe(3);
    expect(result.stores).toEqual(['tei_files']);
    // User-Uploads ueberleben die Migration
    expect(result.survived).toBe('<TEI/>');
  });

  test('IndexedDB user uploads - save, load and list', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      const testFilename = 'TEST.tei.xml';
      const testContent = `<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="TEST">
  <teiHeader>
    <titleStmt>
      <title xml:lang="de">Test Document</title>
      <author ref="#person_1">Test Author</author>
    </titleStmt>
  </teiHeader>
  <text><body><p>Test content</p></body></text>
</TEI>`;

      const saved = await dbManager.saveTEIFile(testFilename, testContent);
      if (!saved) throw new Error('Failed to save TEI file');

      const loaded = await dbManager.loadTEIFile(testFilename);
      if (loaded !== testContent) throw new Error('Content mismatch');

      const files = await dbManager.listTEIFiles();
      const testFile = files.find(f => f.filename === testFilename);
      if (!testFile) throw new Error('Test file not in list');

      return {
        success: true,
        fileCount: files.length,
        size: testFile.size
      };
    });

    expect(result.success).toBe(true);
    expect(result.fileCount).toBe(1);
    expect(result.size).toBeGreaterThan(0);
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
        hasMethods: typeof teiManager.isTEIFile === 'function' &&
                    typeof teiManager.loadCorpusIntoPlayground === 'function'
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

  test('Clear TEI files operation', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      for (let i = 1; i <= 5; i++) {
        await dbManager.saveTEIFile(`CLEAR${i}.tei.xml`, `<TEI>Clear test ${i}</TEI>`);
      }

      let files = await dbManager.listTEIFiles();
      if (files.length !== 5) throw new Error(`Expected 5 files before clear, got ${files.length}`);

      const cleared = await dbManager.clearTEIFiles();
      if (cleared !== 5) throw new Error(`Expected to clear 5 files, cleared ${cleared}`);

      files = await dbManager.listTEIFiles();
      if (files.length !== 0) throw new Error(`Expected 0 files after clear, got ${files.length}`);

      return { success: true, cleared };
    });

    expect(result.success).toBe(true);
    expect(result.cleared).toBe(5);
  });
});
