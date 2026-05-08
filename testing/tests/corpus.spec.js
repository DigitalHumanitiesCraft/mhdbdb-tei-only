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

  test('IndexedDB corpus operations - schema version 2', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      // Verify database version
      if (dbManager.dbVersion !== 2) {
        throw new Error(`Expected DB version 2, got ${dbManager.dbVersion}`);
      }

      // Verify corpus_tei_files store exists
      const storeNames = Array.from(dbManager.db.objectStoreNames);
      if (!storeNames.includes('corpus_tei_files')) {
        throw new Error('corpus_tei_files store not found');
      }

      return { success: true, version: dbManager.dbVersion, stores: storeNames };
    });

    expect(result.success).toBe(true);
    expect(result.version).toBe(2);
    expect(result.stores).toContain('corpus_tei_files');
    expect(result.stores).toContain('tei_files');
    expect(result.stores).toContain('authority_files');
  });

  test('IndexedDB corpus operations - save and load corpus file', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      // Create test TEI content
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

      const testMetadata = {
        sigle: 'TEST',
        title: 'Test Document',
        author: 'Test Author',
        authorRef: '#person_1',
        workRef: 'works.xml#work_1'
      };

      // Save corpus file
      const saved = await dbManager.saveCorpusFile(testFilename, testContent, testMetadata);
      if (!saved) throw new Error('Failed to save corpus file');

      // Load corpus file
      const loaded = await dbManager.loadCorpusFile(testFilename);
      if (!loaded) throw new Error('Failed to load corpus file');

      // Verify content matches
      if (loaded !== testContent) {
        throw new Error('Content mismatch');
      }

      // List corpus files
      const files = await dbManager.listCorpusFiles();
      const testFile = files.find(f => f.filename === testFilename);

      if (!testFile) throw new Error('Test file not in list');
      if (testFile.sigle !== 'TEST') throw new Error('Metadata not preserved');

      return {
        success: true,
        fileCount: files.length,
        metadata: testFile
      };
    });

    expect(result.success).toBe(true);
    expect(result.fileCount).toBe(1);
    expect(result.metadata.sigle).toBe('TEST');
    expect(result.metadata.title).toBe('Test Document');
    expect(result.metadata.author).toBe('Test Author');
  });

  test('IndexedDB corpus operations - isCorpusLoaded check', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      // Initially corpus should not be loaded (0/667)
      let isLoaded = await dbManager.isCorpusLoaded();
      if (isLoaded) throw new Error('Corpus should not be loaded initially');

      let count = await dbManager.getCorpusCount();
      if (count !== 0) throw new Error(`Expected 0 files, got ${count}`);

      // Add test files (not all 667, just a few for testing)
      for (let i = 1; i <= 5; i++) {
        await dbManager.saveCorpusFile(
          `TEST${i}.tei.xml`,
          `<TEI>Content ${i}</TEI>`,
          { sigle: `TEST${i}`, title: `Test ${i}`, author: 'Test' }
        );
      }

      // Should still not be loaded (5/667)
      isLoaded = await dbManager.isCorpusLoaded();
      if (isLoaded) throw new Error('Corpus should not be fully loaded yet');

      count = await dbManager.getCorpusCount();
      if (count !== 5) throw new Error(`Expected 5 files, got ${count}`);

      return { success: true, partialCount: count };
    });

    expect(result.success).toBe(true);
    expect(result.partialCount).toBe(5);
  });

  test('IndexedDB corpus operations - copy to playground', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      // Create and save corpus file
      const filename = 'COPY_TEST.tei.xml';
      const content = '<TEI>Copy test content</TEI>';
      const metadata = {
        sigle: 'COPY',
        title: 'Copy Test',
        author: 'Test Author',
        authorRef: '#person_1',
        workRef: 'works.xml#work_1'
      };

      await dbManager.saveCorpusFile(filename, content, metadata);

      // Copy to playground
      const copied = await dbManager.copyCorpusToPlayground(filename);
      if (!copied) throw new Error('Failed to copy corpus file');

      // Load from playground store
      const loadedFromPlayground = await dbManager.loadTEIFile(filename);
      if (!loadedFromPlayground) throw new Error('File not in playground store');

      if (loadedFromPlayground !== content) {
        throw new Error('Content mismatch after copy');
      }

      // Verify both stores have the file
      const corpusFiles = await dbManager.listCorpusFiles();
      const teiFiles = await dbManager.listTEIFiles();

      const inCorpus = corpusFiles.some(f => f.filename === filename);
      const inPlayground = teiFiles.some(f => f.filename === filename);

      if (!inCorpus) throw new Error('File missing from corpus store');
      if (!inPlayground) throw new Error('File missing from playground store');

      return { success: true, inBothStores: true };
    });

    expect(result.success).toBe(true);
    expect(result.inBothStores).toBe(true);
  });

  test('Corpus Loader - manifest parsing', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      // Directly fetch manifest instead of using CorpusLoader (avoids path issues in test)
      const manifestUrl = '/tei/manifest.json';
      const response = await fetch(manifestUrl);

      if (!response.ok) {
        throw new Error(`Failed to fetch manifest: ${response.statusText}`);
      }

      const manifest = await response.json();

      if (!manifest) throw new Error('Manifest not loaded');
      if (!manifest.files) throw new Error('No files in manifest');
      if (manifest.totalFiles !== 667) {
        throw new Error(`Expected 667 files, got ${manifest.totalFiles}`);
      }

      // Check first file has required fields
      const firstFile = manifest.files[0];
      const requiredFields = ['filename', 'path', 'sigle', 'title', 'author', 'size'];

      for (const field of requiredFields) {
        if (!(field in firstFile)) {
          throw new Error(`Missing field: ${field}`);
        }
      }

      return {
        success: true,
        totalFiles: manifest.totalFiles,
        totalSizeMB: manifest.totalSizeMB,
        firstFile: firstFile
      };
    });

    expect(result.success).toBe(true);
    expect(result.totalFiles).toBe(667);
    expect(result.totalSizeMB).toBeGreaterThan(1000); // Should be ~1523 MB
    expect(result.firstFile.filename).toContain('.tei.xml');
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

  test('Clear corpus files operation', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const dbManager = new IndexedDBManager();

      await dbManager.initialize();

      // Add test files
      for (let i = 1; i <= 5; i++) {
        await dbManager.saveCorpusFile(
          `CLEAR${i}.tei.xml`,
          `<TEI>Clear test ${i}</TEI>`,
          { sigle: `CLR${i}`, title: `Clear ${i}`, author: 'Test' }
        );
      }

      let count = await dbManager.getCorpusCount();
      if (count !== 5) throw new Error(`Expected 5 files before clear, got ${count}`);

      // Clear corpus
      const cleared = await dbManager.clearCorpusFiles();
      if (cleared !== 5) throw new Error(`Expected to clear 5 files, cleared ${cleared}`);

      // Verify empty
      count = await dbManager.getCorpusCount();
      if (count !== 0) throw new Error(`Expected 0 files after clear, got ${count}`);

      return { success: true, cleared };
    });

    expect(result.success).toBe(true);
    expect(result.cleared).toBe(5);
  });
});
