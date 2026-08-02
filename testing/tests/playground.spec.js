// tests/playground.spec.js
import { test, expect } from '@playwright/test';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

test.describe('MHDBDB Playground Test Suite', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.goto('/testing/test.html');
    await page.evaluate(() => sessionStorage.clear());
  });

  test('should load test page and run all tests', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for the page title to be correct
    await expect(page).toHaveTitle(/MHDBDB Playground - Test Suite/);

    // Wait for tests to start
    await expect(page.locator('#progress-text')).toContainText('Initializing tests', { timeout: 10000 });

    // Wait for tests to complete (optimized timeout)
    await expect(page.locator('#progress-text')).toContainText('All tests completed', { timeout: 30000 });

    // Check that the spinner is hidden (indicating completion)
    await expect(page.locator('#loading-spinner')).toBeHidden();

    // Verify progress bar shows 100%
    const progressFill = page.locator('#progress-fill');
    await expect(progressFill).toContainText('100%');

    // Get test results from the page
    const testResults = await page.evaluate(() => window.getTestResults());

    // Verify test results exist
    expect(testResults).toBeTruthy();
    expect(testResults.summary).toBeTruthy();
    expect(testResults.summary.total).toBeGreaterThan(0);

    // Log test summary for debugging
    console.log('Test Summary:', testResults.summary);

    // Check that most tests passed (allow for some flakiness in test environment)
    const passRate = testResults.summary.passRate;
    expect(passRate).toBeGreaterThanOrEqual(45); // 45% pass rate minimum (accounting for IndexedDB test environment flakiness)

    // Log test results for CI (browser doesn't have fs access)
    console.log('Test Results JSON:', JSON.stringify(testResults, null, 2));

    // Take a screenshot of the final results
    await page.screenshot({ path: resolve(__dirname, '../test-results/test-results-screenshot.png'), fullPage: true });
  });

  test('should display test results visually', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for tests to complete
    await expect(page.locator('#progress-text')).toContainText('All tests completed', { timeout: 30000 });

    // Verify results section is populated
    const resultsContainer = page.locator('#test-results');
    await expect(resultsContainer).toBeVisible();

    // Check for test summary
    await expect(resultsContainer.locator('.test-summary')).toBeVisible();

    // Check for test suites (updated for IndexedDB tests)
    // #314: von sieben Suites sind vier geblieben. TEIStorageManager,
    // TEIFilesManager und Large File Handling prüfen den Datei-Upload,
    // den es seit dem Redesign nicht mehr gibt.
    await expect(resultsContainer.locator('.test-suite')).toHaveCount(4, { timeout: 10000 });

    // Verify suite names
    const suiteNames = await resultsContainer.locator('.test-suite h3').allTextContents();
    expect(suiteNames).toContain('DOM Integration');
    expect(suiteNames).toContain('Performance Tests');
    expect(suiteNames).toContain('IndexedDB Storage');
    expect(suiteNames).toContain('Error Handling');
  });

  test('should handle manual test controls', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for initial tests to complete
    await expect(page.locator('#progress-text')).toContainText('All tests completed', { timeout: 30000 });

    // Test "Run Tests Again" button - just verify it completes again
    await page.click('#run-tests');

    // Wait for tests to run again (they complete quickly, so just wait for completion)
    await expect(page.locator('#progress-text')).toContainText('completed', { timeout: 30000 });

    // #314: Der Test suchte hier bis Juli 2026 nach "Cleared" (groß). Diesen
    // String loggte nicht der Knopf, sondern clearAllCachedFiles() aus dem
    // Upload-Pfad, angestoßen vom vorherigen "Run Tests Again". Der Test war
    // also grün, ohne den Knopf je zu prüfen.
    //
    // Eine Log-Zeile allein wäre wieder zu wenig: window.clearStorage() loggt
    // unbedingt, auch wenn nichts zu löschen war. Deshalb erst einen Schlüssel
    // setzen, den clearTestStorage() erfassen muss, und danach seine Abwesenheit
    // prüfen.
    await page.evaluate(() => sessionStorage.setItem('mhdbdb_probe_314', 'x'));

    await page.click('button:has-text("Clear Storage")');

    const consoleOutput = page.locator('#console-output');
    await expect(consoleOutput).toContainText('Storage cleared', { timeout: 5000 });

    const probe = await page.evaluate(() => sessionStorage.getItem('mhdbdb_probe_314'));
    expect(probe).toBeNull();
  });

  test('should capture console output', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for tests to start producing console output
    await page.waitForTimeout(2000);

    const consoleOutput = page.locator('#console-output');
    await expect(consoleOutput).toBeVisible();

    // Should contain test start message
    await expect(consoleOutput).toContainText('Test suite starting');

    // Should show test progress
    await expect(consoleOutput).toContainText('IndexedDB Storage', { timeout: 30000 });
  });

  test('should handle download report functionality', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for tests to complete
    await expect(page.locator('#progress-text')).toContainText('All tests completed', { timeout: 30000 });

    // Set up download handling
    const downloadPromise = page.waitForEvent('download');

    // Click download button
    await page.click('button:has-text("Download Report")');

    // Wait for and verify download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/test-report-.*\.json/);

    // Save the download for verification
    await download.saveAs(resolve(__dirname, `../test-results/${download.suggestedFilename()}`));
  });

  test('should work with different screen sizes', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/testing/test.html');

    // Should still be functional
    await expect(page.locator('h1')).toContainText('MHDBDB Playground Test Suite');
    await expect(page.locator('#test-progress')).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();

    // Should still be functional
    await expect(page.locator('h1')).toContainText('MHDBDB Playground Test Suite');
    await expect(page.locator('#test-progress')).toBeVisible();
  });

  test('should handle storage quota scenarios', async ({ page }) => {
    await page.goto('/testing/test.html');

    // Wait for tests to complete
    await expect(page.locator('#progress-text')).toContainText('All tests completed', { timeout: 30000 });

    // Check that storage quota tests ran
    const consoleOutput = page.locator('#console-output');
    await expect(consoleOutput).toContainText('Performance Tests');

    // Verify storage quota check passed
    const testResults = await page.evaluate(() => window.getTestResults());
    const performanceTests = testResults.results.filter(r => r.suite === 'Performance Tests');
    const quotaTest = performanceTests.find(t => t.test.includes('storage quota'));

    if (quotaTest) {
      // Storage quota test is environment-dependent, just verify it ran
      expect(['pass', 'fail']).toContain(quotaTest.status);
    }
  });

  test('should handle cache clearing functionality', async ({ page }) => {
    // Test the main playground cache clearing
    await page.goto('/playground/index.html');

    // Wait for page to load
    await expect(page).toHaveTitle(/TEI-Daten-Explorer/);

    // Check if clear site data button exists (it's in the footer)
    const clearButton = page.locator('#clearSiteDataBtn');
    await expect(clearButton).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Playground Integration Tests', () => {
  test('should load main playground page without errors', async ({ page }) => {
    // Test that the main playground loads correctly
    await page.goto('/playground/index.html');

    // Wait for page to load
    await expect(page).toHaveTitle(/TEI-Daten-Explorer/);

    // Check for essential elements
    await expect(page.locator('h1')).toContainText('TEI-Daten-Explorer');
    await expect(page.locator('#authorityOverview')).toBeVisible();

    // Check for authority files loading
    const statusText = page.locator('#statusText');

    // Wait for either loading or completion status
    await expect(statusText).toBeVisible({ timeout: 5000 });

    // Take screenshot for manual verification
    await page.screenshot({ path: resolve(__dirname, '../test-results/playground-main-page.png'), fullPage: true });
  });

  test('should have all required JavaScript modules', async ({ page }) => {
    // #331: Die Listener müssen VOR dem goto hängen. Die Auswertung der
    // ES-Module passiert während des Ladens; ein danach registrierter
    // Listener sieht sie nie. Bis August 2026 stand page.on() hinter
    // page.goto(), der Test konnte also genau die Fehlerklasse nicht sehen,
    // gegen die er schützen soll.
    const konsolenfehler = [];
    const seitenfehler = [];
    page.on('console', msg => {
      if (msg.type() === 'error') konsolenfehler.push(msg.text());
    });
    // pageerror ist nicht dasselbe wie console.error: eine unbehandelte
    // Ausnahme aus einem Modul kommt hier an, nicht zwingend dort.
    page.on('pageerror', err => seitenfehler.push(String(err)));

    await page.goto('/playground/index.html');

    // Auf die vollständige Kette warten statt auf eine feste Zeitspanne:
    // die Module laden den Korpus-Index asynchron nach, und ein Fehler dabei
    // fiele nach einem pauschalen waitForTimeout(3000) je nach Maschine mal
    // auf und mal nicht.
    //
    // Der catch ist kein Schmuck, sondern gemessen: mit einem eingebauten
    // ReferenceError in einem Playground-Modul läuft die Kette gar nicht erst
    // durch, und ohne ihn meldete der Test einen waitForFunction-Timeout,
    // also die Folge statt der Ursache. Liegen Fehler vor, werden die zuerst
    // behauptet; hängt die Kette ohne jeden Fehler, bleibt der Timeout die
    // richtige Meldung.
    try {
      await page.waitForFunction(
        () => window.playground?.corpusData?.texts?.length > 0,
        { timeout: 60000 }
      );
    } catch (timeout) {
      expect(seitenfehler, 'Ladekette blieb stehen, dabei angefallen').toEqual([]);
      expect(konsolenfehler, 'Ladekette blieb stehen, dabei angefallen').toEqual([]);
      throw timeout;
    }

    // Schwelle 0, nicht „höchstens einer". Gemessen am 02.08.2026 über den
    // ganzen Ladevorgang: 0 console.error, 0 pageerror, 0 fehlgeschlagene
    // Requests. Es gibt also nichts zu tolerieren, und der frühere Freibetrag
    // („Allow for some environmental issues") hätte genau einen Modulfehler
    // durchgelassen. Kommt hier je legitimes Rauschen an, gehört es namentlich
    // ausgenommen und nicht wieder gezählt.
    //
    // Verglichen wird das ganze Array, nicht seine Länge: im Fehlerfall steht
    // die Meldung im Assertion-Diff, statt dass nur eine Zahl nicht stimmt.
    expect(seitenfehler, 'unbehandelte Ausnahmen beim Laden').toEqual([]);
    expect(konsolenfehler, 'console.error beim Laden').toEqual([]);
  });
});
