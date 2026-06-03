/**
 * Position Counting Parity Tests (#131)
 *
 * Contract: CONTRACTS.md §B "Position Counting" — the Python build script
 * (scripts/build-corpus-index.py, extract_word_data) and the JS runtime reader
 * (assets/js/rendering/tei-text-reader.js, extractAndFormatBody) MUST assign
 * IDENTICAL word positions to each <w>. The corpus index stores lemma positions
 * as integers; the reader uses them to navigate between hits and proximity search
 * uses |pos_a - pos_b| <= maxDistance. If the two counters drift, navigation
 * jumps to the wrong word and proximity search silently breaks — no error.
 *
 * §B was the last cross-language invariant without its own test (§A normalization,
 * §B.1 highlight matching, §C 3-stage resolution are all covered). This is the
 * §B analogue of normalization-parity.spec.js: run a real TEI text through BOTH
 * counting paths and assert the position sequences are identical.
 *
 * Mechanism (mirrors §A): Python via execSync calling the REAL extract_word_data
 * (testing/helpers/extract_word_positions.py loads it from the hyphenated build
 * script via importlib); JS via the REAL extractAndFormatBody in the browser. For
 * a probed lemma, the reader's highlights[].position array must equal Python's
 * lemmata[lemmaId] array element-for-element.
 *
 * Two blocks:
 *  - Block 1 (real corpus): PL1 (prose, lineStarts=0) and OVG (verse) with
 *    lemma_308 — a regression guard for the live invariant on real data.
 *  - Block 2 (empty <w lemmaRef> asymmetry): a synthetic fixture exercising the
 *    case Python skips (empty text content) but the pre-fix JS reader counted.
 *    This is the TDD driver for the one-line tei-text-reader.js fix.
 */

import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.join(__dirname, '../..');
const HELPER = path.join(__dirname, '../helpers/extract_word_positions.py');

const BASE = 'http://localhost:8080';

// Establish a same-origin document so the dynamic import('/assets/...') inside
// jsPositions() resolves. /playground/ loads its index asynchronously (does not
// block the load event), the same origin-bootstrap pattern lemma-matching.spec.js
// uses for its unit block.
test.beforeEach(async ({ page }) => {
  await page.goto(`${BASE}/playground/`);
});

/**
 * Python build-time positions for one lemma in one TEI file, via the real
 * extract_word_data(). Returns the lemmata[lemmaId] array ([] if absent).
 */
function pythonPositions(teiAbsPath, textId, lemmaId) {
  const out = execSync(
    `python3.13 "${HELPER}" "${teiAbsPath}" ${textId}`,
    { encoding: 'utf-8', cwd: REPO_ROOT, maxBuffer: 128 * 1024 * 1024 }
  );
  const data = JSON.parse(out);
  return data.lemmata[lemmaId] || [];
}

/**
 * JS runtime positions for one lemma in one TEI file, via the real
 * extractAndFormatBody(). Replicates loadTEIFile()'s parse exactly
 * (DOMParser, 'text/xml') and reads highlights[].position for single-lemma mode.
 */
async function jsPositions(page, teiUrl, lemmaId) {
  // Caller must navigate to a same-origin page first (see beforeEach) so the
  // dynamic import('/assets/...') below resolves against the origin.
  return page.evaluate(async ({ url, lemma }) => {
    const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
    const xmlText = await (await fetch(url)).text();
    const doc = new DOMParser().parseFromString(xmlText, 'text/xml');
    if (doc.querySelector('parsererror')) throw new Error('XML parse failed: ' + url);
    // corpusIndex/authorityIndex/cache are unused by extractAndFormatBody.
    const reader = new TEITextReader(null, null, null);
    const { highlights } = reader.extractAndFormatBody(doc, lemma, []);
    return highlights.map(h => h.position);
  }, { url: teiUrl, lemma: lemmaId });
}

test.describe('B. Position Counting parity — real corpus', () => {
  // lemma_308 (arzât) occurs in both a prose and a verse text. Ground truth from
  // #130: 57 highlights in PL1, 26 in OVG — i.e. identical occurrence counts on
  // both sides. Here we assert the full position SEQUENCES match, not just counts.
  const CASES = [
    { textId: 'PL1', label: 'prose (Prosa-Lancelot, lineStarts=0)', lemmaId: 'lemma_308' },
    { textId: 'OVG', label: 'verse (Steirische Reimchronik)', lemmaId: 'lemma_308' },
  ];

  for (const { textId, label, lemmaId } of CASES) {
    test(`${textId} ${label}: JS reader positions == Python build positions for ${lemmaId}`, async ({ page }) => {
      const teiAbs = path.join(REPO_ROOT, 'tei', `${textId}.tei.xml`);
      const py = pythonPositions(teiAbs, textId, lemmaId);
      const js = await jsPositions(page, `${BASE}/tei/${textId}.tei.xml`, lemmaId);

      // Guard against a vacuous pass (wrong lemma id -> both empty -> trivially equal).
      expect(py.length, `${lemmaId} should occur in ${textId}`).toBeGreaterThan(0);
      expect(js).toEqual(py);
    });
  }
});

test.describe('B. Position Counting parity — empty <w lemmaRef> asymmetry (#131)', () => {
  // CONTRACTS §B "Parity note": Python skips <w lemmaRef> with empty text content
  // (`if not word_text: continue`); the pre-fix JS reader incremented wordPosition
  // for every <w lemmaRef> regardless of text. 0 such cases in the corpus today,
  // but a future ingest with placeholder/gap tokens would silently break parity.
  // Acceptance criterion (#131): both sides skip, or neither does. We align JS to
  // Python (skip), so the sequences below must be identical.
  const FIXTURE_REL = 'testing/fixtures/position-parity-empty-w.tei.xml';
  const EXPECTED = { lemma_1: [0, 1], lemma_3: [2] };

  for (const [lemmaId, expected] of Object.entries(EXPECTED)) {
    test(`fixture: JS == Python == ${JSON.stringify(expected)} for ${lemmaId} (empty <w> not counted)`, async ({ page }) => {
      const fixtureAbs = path.join(REPO_ROOT, FIXTURE_REL);
      const py = pythonPositions(fixtureAbs, 'FIXTURE', lemmaId);
      const js = await jsPositions(page, `${BASE}/${FIXTURE_REL}`, lemmaId);

      // Sanity: the documented expectation pins the contract independent of code.
      expect(py, `Python should skip the empty <w lemmaRef> for ${lemmaId}`).toEqual(expected);
      expect(js, `JS reader must match Python for ${lemmaId}`).toEqual(expected);
    });
  }
});
