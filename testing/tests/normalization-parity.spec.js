/**
 * Normalization Parity Tests
 *
 * CRITICAL: Ensures Python and JavaScript MHG normalization produce IDENTICAL results.
 * Any discrepancy will cause search failures between build-time indices and runtime search.
 */

import { test, expect } from '@playwright/test';
import { execFileSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { resolvePython, pythonEnv } from '../../scripts/python-bin.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test cases - must match those in scripts/mhg_normalizer.py
const TEST_CASES = [
  { input: 'brôt', expected: 'brot' },
  { input: 'BRÔT', expected: 'brot' },
  { input: 'wîn', expected: 'win' },
  { input: 'vriunt', expected: 'vriunt' },
  { input: 'schône', expected: 'schone' },
  { input: 'schöne', expected: 'schoene' },
  { input: 'Âventiure', expected: 'aventiure' },
  { input: 'mære', expected: 'maere' },
  { input: 'âne', expected: 'ane' },
  { input: 'fröude', expected: 'froeude' },
  { input: 'müede', expected: 'mueede' },
  { input: 'ûzer', expected: 'uzer' },
  { input: 'ōre', expected: 'ore' },
  { input: 'sǒne', expected: 'sone' },
  { input: 'cæsar', expected: 'caesar' },
  { input: 'œnologie', expected: 'oenologie' },
  // Schritt 0, NFC (#224): zerlegte Umlaute müssen wie komponierte
  // normalisieren. Escapes statt Literale, weil ein Editor mit
  // Auto-Normalisierung die zerlegte Form still zu NFC zusammenzöge und den
  // Test damit lautlos entwerten würde.
  { input: 'bo\u0308ses', expected: 'boeses' },
  { input: 'Mu\u0308hldorf', expected: 'muehldorf' },
  // Breve-Umlaute (#224, KZW 28.07.). Die Wenzelsbibel schreibt Umlaute mit
  // Breve; Klaus Schmidts Eingabe war bo + U+0306 + ses aus der Leseansicht.
  { input: 'bo\u0306ses', expected: 'boeses' },   // zerlegt, NFC zieht zusammen
  { input: 'b\u014fses', expected: 'boeses' },    // praekomponiert
  { input: 'w\u016dnschet', expected: 'wuenschet' },
  // Breve auf w/n ist böhmische Schreibkonvention, kein Umlaut: getilgt
  // statt zu einem Digraphen aufgelöst (ADR-017, Julia 06.08.).
  { input: 'few\u0306er', expected: 'fewer' },   // -> lemma_7108 viur
  { input: 'wenn\u0306', expected: 'wenn' },     // -> lemma_7385 wan
  { input: 'Ew\u0306er', expected: 'ewer' },     // Grossbuchstabe
  { input: '', expected: '' },
];

test.describe('MHG Normalization Parity', () => {
  test('Python normalizer self-test passes', () => {
    const scriptPath = path.join(__dirname, '../../scripts/mhg_normalizer.py');

    try {
      // Run Python self-test. execFileSync statt execSync: ohne Shell gibt es
      // kein Zitier-Problem, wenn der Interpreter oder das Skript in einem
      // Pfad mit Leerzeichen liegt (unter Windows die Regel, nicht die
      // Ausnahme).
      execFileSync(resolvePython(), [scriptPath], {
        encoding: 'utf-8',
        env: pythonEnv(),
      });
    } catch (error) {
      throw new Error(`Python normalizer self-test failed:\n${error.message}`);
    }
  });

  test('JavaScript normalizer matches Python for all test cases', async ({ page }) => {
    // Navigate to playground to access TextNormalizer
    await page.goto('http://localhost:8080/playground/');

    // Load TextNormalizer module
    const normalizationResults = await page.evaluate(async (testCases) => {
      // Dynamically import TextNormalizer
      const { TextNormalizer } = await import('/assets/js/lib/text-normalizer.js');

      const results = [];
      for (const testCase of testCases) {
        const jsResult = TextNormalizer.normalizeMHG(testCase.input);
        results.push({
          input: testCase.input,
          expected: testCase.expected,
          jsResult: jsResult,
          matches: jsResult === testCase.expected
        });
      }
      return results;
    }, TEST_CASES);

    // Check each result
    let failures = 0;
    for (const result of normalizationResults) {
      if (!result.matches) {
        console.error(`❌ FAIL: JS normalize("${result.input}") = "${result.jsResult}", expected "${result.expected}"`);
        failures++;
      } else {
        console.log(`✅ PASS: JS normalize("${result.input}") = "${result.jsResult}"`);
      }
    }

    expect(failures).toBe(0);
  });

  test('Python and JavaScript produce identical output', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');

    // Test subset of cases by calling both normalizers
    const testInputs = ['brôt', 'wîn', 'schöne', 'mære', 'Âventiure'];

    for (const input of testInputs) {
      // Get JavaScript result
      const jsResult = await page.evaluate(async (text) => {
        const { TextNormalizer } = await import('/assets/js/lib/text-normalizer.js');
        return TextNormalizer.normalizeMHG(text);
      }, input);

      // Get Python result. Der Prüfstring geht als argv-Element hinein und
      // nicht mehr interpoliert in den Python-Quelltext: sonst zerlegt ein
      // Apostroph im Testfall das Literal, und ein Testfall mit Apostroph
      // ist bei mittelhochdeutschen Formen jederzeit denkbar.
      const pythonResult = execFileSync(
        resolvePython(),
        ['-c',
         'import sys; from scripts.mhg_normalizer import normalize_mhg; '
         + 'print(normalize_mhg(sys.argv[1]), end="")',
         input],
        { encoding: 'utf-8', cwd: path.join(__dirname, '../..'), env: pythonEnv() }
      );

      console.log(`Input: "${input}" | JS: "${jsResult}" | Python: "${pythonResult}"`);

      expect(jsResult).toBe(pythonResult);
    }
  });

  test('Normalization is idempotent', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');

    const testCases = ['brôt', 'wîn', 'schöne'];

    for (const input of testCases) {
      const result = await page.evaluate(async (text) => {
        const { TextNormalizer } = await import('/assets/js/lib/text-normalizer.js');
        const normalized1 = TextNormalizer.normalizeMHG(text);
        const normalized2 = TextNormalizer.normalizeMHG(normalized1);
        return { normalized1, normalized2 };
      }, input);

      // Normalizing twice should give same result
      expect(result.normalized1).toBe(result.normalized2);
      console.log(`✅ Idempotent: "${input}" → "${result.normalized1}" → "${result.normalized2}"`);
    }
  });

  test('matchesNormalized works correctly', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');

    const testCases = [
      { text: 'brôt', search: 'brot', shouldMatch: true },
      { text: 'brôt', search: 'BROT', shouldMatch: true },
      { text: 'brôt', search: 'win', shouldMatch: false },
      { text: 'schöne', search: 'schoene', shouldMatch: true },
      { text: 'mære', search: 'maere', shouldMatch: true },
    ];

    for (const testCase of testCases) {
      const result = await page.evaluate(async ({ text, search }) => {
        const { TextNormalizer } = await import('/assets/js/lib/text-normalizer.js');
        return TextNormalizer.matchesNormalized(text, search);
      }, testCase);

      expect(result).toBe(testCase.shouldMatch);
      console.log(`✅ matchesNormalized("${testCase.text}", "${testCase.search}") = ${result}`);
    }
  });

  test('exactMatchNormalized works correctly', async ({ page }) => {
    await page.goto('http://localhost:8080/playground/');

    const testCases = [
      { text: 'brôt', search: 'brot', shouldMatch: true },
      { text: 'brôt', search: 'BROT', shouldMatch: true },
      { text: 'brôt und wîn', search: 'brot', shouldMatch: false }, // Not exact
      { text: 'schöne', search: 'schoene', shouldMatch: true },
    ];

    for (const testCase of testCases) {
      const result = await page.evaluate(async ({ text, search }) => {
        const { TextNormalizer } = await import('/assets/js/lib/text-normalizer.js');
        return TextNormalizer.exactMatchNormalized(text, search);
      }, testCase);

      expect(result).toBe(testCase.shouldMatch);
      console.log(`✅ exactMatchNormalized("${testCase.text}", "${testCase.search}") = ${result}`);
    }
  });
});
