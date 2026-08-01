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
 *  - Block 1 (real corpus): PL1 (prose, lineStarts=0) and OVG (verse). For each we
 *    probe the THREE most frequent lemmata — high-frequency lemmata blanket the
 *    document, so any counting drift anywhere shifts their positions. We also assert
 *    Python's positions sum to wordCount (internal consistency). This is a strong
 *    proxy for full-sequence parity; the exhaustive small-case check is Block 2.
 *  - Block 2 (empty <w lemmaRef> asymmetry): a synthetic fixture whose ENTIRE word
 *    sequence (positions 0,1,2) is verified. It exercises the case Python skips
 *    (empty text content) but the pre-fix JS reader counted — the TDD driver for
 *    the one-line tei-text-reader.js fix.
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
// jsPositionsMap() resolves. /playground/ loads its index asynchronously (does not
// block the load event), the same origin-bootstrap pattern lemma-matching.spec.js
// uses for its unit block.
test.beforeEach(async ({ page }) => {
  await page.goto(`${BASE}/playground/`);
});

/**
 * Python build-time word data for one TEI file, via the real extract_word_data().
 * Returns { wordCount, lemmata } where lemmata maps lemma_id -> [positions].
 * (The helper deliberately omits the full words[] array — unused here.) The
 * lemmata dict is ~wordCount integers, so a raised maxBuffer is warranted.
 */
function pythonData(teiAbsPath, textId) {
  const out = execSync(
    `python3.13 "${HELPER}" "${teiAbsPath}" ${textId}`,
    { encoding: 'utf-8', cwd: REPO_ROOT, maxBuffer: 32 * 1024 * 1024 }
  );
  return JSON.parse(out);
}

/**
 * JS runtime positions for several lemmata in one TEI file, via the real
 * extractAndFormatBody(). The file is fetched and parsed ONCE (mirroring
 * loadTEIFile(): DOMParser, 'text/xml'); each lemma is then run through the real
 * single-lemma reader path. Returns { lemma_id: [positions] }.
 */
async function jsPositionsMap(page, teiUrl, lemmaIds) {
  // Caller must navigate to a same-origin page first (see beforeEach) so the
  // dynamic import('/assets/...') below resolves against the origin.
  return page.evaluate(async ({ url, lemmas }) => {
    const { TEITextReader } = await import('/assets/js/rendering/tei-text-reader.js');
    const xmlText = await (await fetch(url)).text();
    const doc = new DOMParser().parseFromString(xmlText, 'text/xml');
    if (doc.querySelector('parsererror')) throw new Error('XML parse failed: ' + url);
    // corpusIndex/authorityIndex/cache are unused by extractAndFormatBody.
    const reader = new TEITextReader(null, null, null);
    const map = {};
    for (const lemma of lemmas) {
      const { highlights } = reader.extractAndFormatBody(doc, lemma, []);
      map[lemma] = highlights.map(h => h.position);
    }
    return map;
  }, { url: teiUrl, lemmas: lemmaIds });
}

/** The N lemma ids with the most occurrences (ties broken by id for determinism). */
function topLemmata(lemmata, n) {
  return Object.entries(lemmata)
    .sort((a, b) => b[1].length - a[1].length || (a[0] < b[0] ? -1 : 1))
    .slice(0, n)
    .map(([id]) => id);
}

test.describe('B. Position Counting parity — real corpus', () => {
  // PL1 is prose (lineStarts=0), OVG is verse — the two structural shapes the
  // reader handles. We probe the 3 most frequent lemmata of each: together they
  // cover positions densely from start to end, so any drift surfaces as a sequence
  // mismatch (not just a count mismatch).
  const CASES = [
    { textId: 'PL1', label: 'prose (Prosa-Lancelot, lineStarts=0)' },
    { textId: 'OVG', label: 'verse (Steirische Reimchronik)' },
  ];

  for (const { textId, label } of CASES) {
    test(`${textId} ${label}: JS reader positions == Python build positions (top-3 lemmata)`, async ({ page }) => {
      const teiAbs = path.join(REPO_ROOT, 'tei', `${textId}.tei.xml`);
      const { wordCount, lemmata } = pythonData(teiAbs, textId);

      // Python internal consistency: every counted word lands in exactly one
      // lemma bucket, so the position lists partition [0, wordCount).
      const totalPositions = Object.values(lemmata).reduce((n, arr) => n + arr.length, 0);
      expect(totalPositions, `${textId}: positions should sum to wordCount`).toBe(wordCount);

      const probes = topLemmata(lemmata, 3);
      expect(probes.length, `${textId} should have lemmata`).toBeGreaterThan(0);

      const js = await jsPositionsMap(page, `${BASE}/tei/${textId}.tei.xml`, probes);
      for (const lemmaId of probes) {
        // Non-vacuous: a frequent lemma has many occurrences spanning the text.
        expect(lemmata[lemmaId].length, `${textId} ${lemmaId} occurrences`).toBeGreaterThan(0);
        expect(js[lemmaId], `${textId} ${lemmaId}: JS positions must equal Python`).toEqual(lemmata[lemmaId]);
      }
    });
  }
});

test.describe('B. Position Counting parity — empty <w lemmaRef> asymmetry (#131)', () => {
  // CONTRACTS §B "Parity note": Python skips <w lemmaRef> with empty text content
  // (`if not text_content: continue`); the pre-fix JS reader incremented wordPosition
  // for every <w lemmaRef> regardless of text. 0 such cases in the corpus today,
  // but a future ingest with placeholder/gap tokens would silently break parity.
  // Acceptance criterion (#131): both sides skip, or neither does. We align JS to
  // Python (skip). The fixture's entire word sequence (positions 0,1,2) is checked.
  const FIXTURE_REL = 'testing/fixtures/position-parity-empty-w.tei.xml';
  const EXPECTED = { lemma_1: [0, 1], lemma_3: [2] };

  test('fixture: whole sequence — empty <w lemmaRef> is not counted by either side', async ({ page }) => {
    const fixtureAbs = path.join(REPO_ROOT, FIXTURE_REL);
    const { lemmata } = pythonData(fixtureAbs, 'FIXTURE');
    const js = await jsPositionsMap(page, `${BASE}/${FIXTURE_REL}`, Object.keys(EXPECTED));

    for (const [lemmaId, expected] of Object.entries(EXPECTED)) {
      // Pin the contract independent of code, then assert both sides hit it.
      expect(lemmata[lemmaId], `Python should skip the empty <w lemmaRef> for ${lemmaId}`).toEqual(expected);
      expect(js[lemmaId], `JS reader must match Python for ${lemmaId}`).toEqual(expected);
    }
    // The empty <w lemmaRef="...lemma_2"> must not appear as a counted position.
    expect(lemmata.lemma_2, 'empty <w lemmaRef> (lemma_2) must not be counted').toBeUndefined();
  });
});

test.describe('B. Position Counting parity — #170 latent drifts', () => {
  // Fixture with (a) a lemmatized <w> inside a date-<note> and (b) a
  // whitespace-separated multi-reference @lemmaRef (CONTRACTS §B.1). Both have
  // 0 corpus cases today; the fixture pins the contract for future ingest.
  const FIXTURE_REL = 'testing/fixtures/position-parity-170.tei.xml';
  const EXPECTED = { lemma_1: [0, 2], lemma_2: [1], lemma_3: [2], lemma_4: [3] };

  test('Python: multi-lemmaRef registers the position under BOTH ids, no broken key', async () => {
    const fixtureAbs = path.join(REPO_ROOT, FIXTURE_REL);
    const { wordCount, lemmata } = pythonData(fixtureAbs, 'FIXTURE170');

    expect(wordCount, '4 counted words').toBe(4);
    for (const [lemmaId, expected] of Object.entries(EXPECTED)) {
      expect(lemmata[lemmaId], `Python positions for ${lemmaId}`).toEqual(expected);
    }
    // Pre-fix failure mode: split('#')[1] on the multi-ref produced the broken
    // key "lemma_1 lexicon.xml". No key may contain whitespace or a filename.
    const brokenKeys = Object.keys(lemmata).filter(k => /\s|\.xml/.test(k));
    expect(brokenKeys, 'no broken multi-ref keys').toEqual([]);
  });

  test('JS reader: word inside date-<note> is counted AND parity holds (badge + children)', async ({ page }) => {
    const fixtureAbs = path.join(REPO_ROOT, FIXTURE_REL);
    const { lemmata } = pythonData(fixtureAbs, 'FIXTURE170');
    const js = await jsPositionsMap(page, `${BASE}/${FIXTURE_REL}`, Object.keys(EXPECTED));

    for (const [lemmaId, expected] of Object.entries(EXPECTED)) {
      expect(lemmata[lemmaId], `Python positions for ${lemmaId}`).toEqual(expected);
      // Pre-fix: the date-note badge swallowed children(), so lemma_2 had no
      // highlight at all and lemma_4 shifted to [2].
      expect(js[lemmaId], `JS reader must match Python for ${lemmaId}`).toEqual(expected);
    }
  });

  test('enrichFileResults (proximity context): empty <w lemmaRef> does not shift the window', async ({ page }) => {
    // Fourth counting path (#170): the playground proximity-search enrichment
    // maps index positions back onto DOM words. Python position 2 in the
    // empty-w fixture is "ist" (lemma_3); pre-fix, the JS mapping counted the
    // empty <w lemmaRef> too, so the window slid onto "brot" instead.
    const result = await page.evaluate(async () => {
      const { enrichFileResults } = await import('/playground/js/ui/core/ui-helpers.js');
      const r = {
        filename: '../testing/fixtures/position-parity-empty-w.tei.xml',
        contextStart: 2,
        contextEnd: 3,
        distance: 0
      };
      await enrichFileResults([r], ['lemma_3']);
      return r.contextText;
    });

    expect(result, 'context window must land on the Python position').toContain('ist');
    expect(result, 'pre-fix failure mode: window slid onto "brot"').not.toContain('brot');
  });
});
