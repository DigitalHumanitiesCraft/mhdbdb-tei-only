/**
 * Lemma Matching Exactness Tests (#130, regression guard for #126)
 *
 * Contract: CONTRACTS.md §B.1 — a <w> is highlighted iff its @lemmaRef contains
 * the searched lemma id as an EXACT whitespace-separated token, never a substring.
 *
 * #126 bug: an unbounded substring test (`lemmaRef.includes('#lemma_308')`) also
 * matched neighbouring ids like #lemma_3089 (jâmer), #lemma_30800, #lemma_3087 —
 * inflating highlights and the in-reader hit counter. The fix existed at 6 inline
 * sites across 4 files and shipped untested. #130 extracts the logic into a single
 * lemmaRefMatchesId() and tests it, so no copy can silently regress.
 *
 * Two layers:
 *  - Block 1 (Unit): the real lemmaRefMatchesId() against the §B.1 case table,
 *    incl. multi-value @lemmaRef (corpus-wide absent today, but a live contract).
 *  - Block 2 (E2E): the full reader render path on real corpus data. lemma_308
 *    (arzât) yields exactly 57 highlights in PL1 and 26 in OVG. The old substring
 *    code yielded 689/369 (lemma_3089 etc.) — so this fails red on regression.
 */

import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:8080';

// CONTRACTS §B.1 case table — exact-token semantics.
const CASES = [
  // [lemmaRef, searchId, shouldMatch, note]
  ['lexicon.xml#lemma_308', 'lemma_308', true, 'exact single match (#126 case 1)'],
  ['lexicon.xml#lemma_3089', 'lemma_308', false, 'substring trap: 308 must not match 3089 (jâmer)'],
  ['lexicon.xml#lemma_30800', 'lemma_308', false, 'substring trap: 308 must not match 30800'],
  ['lexicon.xml#lemma_3087', 'lemma_308', false, 'substring trap: 308 must not match 3087'],
  ['lexicon.xml#lemma_308 lexicon.xml#lemma_5', 'lemma_5', true, 'multi-value: second token matches (#126 case 3)'],
  ['lexicon.xml#lemma_308 lexicon.xml#lemma_5', 'lemma_308', true, 'multi-value: first token matches'],
  ['lexicon.xml#lemma_308 lexicon.xml#lemma_5', 'lemma_50', false, 'multi-value: no substring match (5 vs 50)'],
  ['', 'lemma_308', false, 'empty lemmaRef never matches'],
  ['lexicon.xml#lemma_308', '', false, 'empty searchId never matches'],
];

test.describe('B.1 Lemma Matching — unit (lemmaRefMatchesId)', () => {
  test('exact-token semantics match the §B.1 contract table', async ({ page }) => {
    await page.goto(`${BASE}/playground/`);

    const results = await page.evaluate(async (cases) => {
      const { lemmaRefMatchesId } = await import('/assets/js/lib/lemma-match.js');
      return cases.map(([ref, id, expected, note]) => ({
        ref, id, expected, note,
        actual: lemmaRefMatchesId(ref, id),
      }));
    }, CASES);

    for (const r of results) {
      expect(r.actual, `lemmaRefMatchesId("${r.ref}", "${r.id}") — ${r.note}`).toBe(r.expected);
    }
  });
});

test.describe('B.1 Lemma Matching — e2e reader highlight counts', () => {
  // Ground-truth verified against the corpus: exact lemma_308 token counts.
  // The pre-#126 substring code would highlight 689 / 369 here.
  const EXPECTED = [
    { textId: 'PL1', count: 57 },
    { textId: 'OVG', count: 26 },
  ];

  for (const { textId, count } of EXPECTED) {
    test(`${textId}: lemma_308 highlights exactly ${count} words (not the substring-inflated total)`, async ({ page }) => {
      await page.goto(`${BASE}/korpus.html?textId=${textId}&lemmaIds=lemma_308`);
      await page.waitForSelector('#readingBody .highlight', { timeout: 30000 });
      const highlightCount = await page.locator('#readingBody .highlight').count();
      expect(highlightCount).toBe(count);
    });
  }
});
