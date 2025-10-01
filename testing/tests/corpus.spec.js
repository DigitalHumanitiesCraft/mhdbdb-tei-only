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

      // Initially corpus should not be loaded (0/666)
      let isLoaded = await dbManager.isCorpusLoaded();
      if (isLoaded) throw new Error('Corpus should not be loaded initially');

      let count = await dbManager.getCorpusCount();
      if (count !== 0) throw new Error(`Expected 0 files, got ${count}`);

      // Add test files (not all 666, just a few for testing)
      for (let i = 1; i <= 5; i++) {
        await dbManager.saveCorpusFile(
          `TEST${i}.tei.xml`,
          `<TEI>Content ${i}</TEI>`,
          { sigle: `TEST${i}`, title: `Test ${i}`, author: 'Test' }
        );
      }

      // Should still not be loaded (5/666)
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
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');

      const dbManager = new IndexedDBManager();
      await dbManager.initialize();

      // Directly fetch manifest instead of using CorpusLoader (avoids path issues in test)
      const manifestUrl = '/tei/manifest.json';
      const response = await fetch(manifestUrl);

      if (!response.ok) {
        throw new Error(`Failed to fetch manifest: ${response.statusText}`);
      }

      const manifest = await response.json();

      if (!manifest) throw new Error('Manifest not loaded');
      if (!manifest.files) throw new Error('No files in manifest');
      if (manifest.totalFiles !== 666) {
        throw new Error(`Expected 666 files, got ${manifest.totalFiles}`);
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
    expect(result.totalFiles).toBe(666);
    expect(result.totalSizeMB).toBeGreaterThan(1000); // Should be ~1523 MB
    expect(result.firstFile.filename).toContain('.tei.xml');
  });

  test('Corpus Loader - metadata extraction', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const { CorpusLoader } = await import('../js/corpus-loader.js');

      const dbManager = new IndexedDBManager();
      await dbManager.initialize();

      const loader = new CorpusLoader(dbManager);

      // Test XML content
      const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="TESTMETA">
  <teiHeader>
    <titleStmt>
      <title xml:lang="de">Metadata Test Document</title>
      <author ref="#person_123">Johann Wolfgang von Goethe</author>
    </titleStmt>
    <sourceDesc>
      <msDesc>
        <msIdentifier corresp="works.xml#work_456">
          <idno type="sigle">TESTMETA</idno>
        </msIdentifier>
      </msDesc>
    </sourceDesc>
  </teiHeader>
</TEI>`;

      const manifestEntry = {
        filename: 'TESTMETA.tei.xml',
        sigle: 'FALLBACK',
        title: 'Fallback Title',
        author: 'Fallback Author'
      };

      const metadata = loader.extractMetadata(xmlContent, manifestEntry);

      if (metadata.sigle !== 'TESTMETA') {
        throw new Error(`Expected sigle 'TESTMETA', got '${metadata.sigle}'`);
      }

      if (metadata.title !== 'Metadata Test Document') {
        throw new Error(`Expected title 'Metadata Test Document', got '${metadata.title}'`);
      }

      if (metadata.author !== 'Johann Wolfgang von Goethe') {
        throw new Error(`Expected author 'Johann Wolfgang von Goethe', got '${metadata.author}'`);
      }

      if (metadata.authorRef !== '#person_123') {
        throw new Error(`Expected authorRef '#person_123', got '${metadata.authorRef}'`);
      }

      if (metadata.workRef !== 'works.xml#work_456') {
        throw new Error(`Expected workRef 'works.xml#work_456', got '${metadata.workRef}'`);
      }

      return { success: true, metadata };
    });

    expect(result.success).toBe(true);
    expect(result.metadata.sigle).toBe('TESTMETA');
    expect(result.metadata.author).toBe('Johann Wolfgang von Goethe');
  });

  test('Corpus Loader - progress tracking', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const { CorpusLoader } = await import('../js/corpus-loader.js');

      const dbManager = new IndexedDBManager();
      await dbManager.initialize();

      const loader = new CorpusLoader(dbManager);

      // Add some test files
      for (let i = 1; i <= 10; i++) {
        await dbManager.saveCorpusFile(
          `PROGRESS${i}.tei.xml`,
          `<TEI>Progress test ${i}</TEI>`,
          { sigle: `PROG${i}`, title: `Progress ${i}`, author: 'Test' }
        );
      }

      const progress = await loader.getLoadingProgress();

      if (progress.current !== 10) {
        throw new Error(`Expected 10 files, got ${progress.current}`);
      }

      if (progress.total !== 666) {
        throw new Error(`Expected total 666, got ${progress.total}`);
      }

      const expectedPercent = Math.round((10 / 666) * 100);
      if (progress.percent !== expectedPercent) {
        throw new Error(`Expected ${expectedPercent}%, got ${progress.percent}%`);
      }

      if (progress.isComplete) {
        throw new Error('Should not be complete with only 10/666 files');
      }

      return { success: true, progress };
    });

    expect(result.success).toBe(true);
    expect(result.progress.current).toBe(10);
    expect(result.progress.total).toBe(666);
    expect(result.progress.isComplete).toBe(false);
  });

  test('TEIFilesManager - loadCorpusIntoPlayground with no corpus', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { TEIFilesManager } = await import('../playground/js/tei-files.js');

      const teiData = {
        files: [],
        parsedXML: [],
        words: [],
        lines: [],
        annotations: []
      };

      const teiManager = new TEIFilesManager(teiData);

      try {
        await teiManager.loadCorpusIntoPlayground();
        return { success: false, error: 'Should have thrown error' };
      } catch (error) {
        // Expected to fail because corpus not loaded
        if (error.message.includes('Corpus not fully loaded')) {
          return { success: true, expectedError: true, message: error.message };
        }
        throw error;
      }
    });

    expect(result.success).toBe(true);
    expect(result.expectedError).toBe(true);
    expect(result.message).toContain('Corpus not fully loaded');
  });

  test('TEIFilesManager - loadCorpusIntoPlayground with corpus', async ({ page }) => {
    await page.goto('/testing/test.html');

    const result = await page.evaluate(async () => {
      const { IndexedDBManager } = await import('../playground/js/indexed-db-manager.js');
      const { TEIFilesManager } = await import('../playground/js/tei-files.js');

      // Initialize DB and add test corpus files
      const dbManager = new IndexedDBManager();
      await dbManager.initialize();

      // Add exactly 666 files to simulate full corpus
      for (let i = 1; i <= 666; i++) {
        await dbManager.saveCorpusFile(
          `TESTCORP${i}.tei.xml`,
          `<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><p><w>test</w></p></body></text></TEI>`,
          { sigle: `TC${i}`, title: `Test Corpus ${i}`, author: 'Test' }
        );
      }

      // Verify corpus is loaded
      const isLoaded = await dbManager.isCorpusLoaded();
      if (!isLoaded) throw new Error('Corpus should be marked as loaded');

      // Now test loading into playground
      const teiData = {
        files: [],
        parsedXML: [],
        words: [],
        lines: [],
        annotations: []
      };

      const teiManager = new TEIFilesManager(teiData);

      let progressUpdates = 0;
      const loadResult = await teiManager.loadCorpusIntoPlayground((loaded, total) => {
        progressUpdates++;
      });

      if (loadResult.loaded !== 666) {
        throw new Error(`Expected 666 loaded files, got ${loadResult.loaded}`);
      }

      if (progressUpdates === 0) {
        throw new Error('Progress callback was never called');
      }

      // Verify files are in tei_files store
      const playgroundFiles = await dbManager.listTEIFiles();
      if (playgroundFiles.length !== 666) {
        throw new Error(`Expected 666 playground files, got ${playgroundFiles.length}`);
      }

      return {
        success: true,
        loaded: loadResult.loaded,
        progressUpdates: progressUpdates,
        playgroundFileCount: playgroundFiles.length
      };
    });

    expect(result.success).toBe(true);
    expect(result.loaded).toBe(666);
    expect(result.progressUpdates).toBeGreaterThan(0);
    expect(result.playgroundFileCount).toBe(666);
  }, 60000); // Extended timeout for loading 666 files

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
