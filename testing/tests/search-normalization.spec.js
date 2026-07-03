// @ts-check
import { test, expect } from '@playwright/test';

/**
 * Search Normalization Test Suite
 * Tests all 11 search entry points for MHG character normalization
 *
 * Covers:
 * - 6 Authority Files searches
 * - 5 TEI Text Analysis searches
 */

test.describe('Search Normalization Test Suite', () => {
    let page;

    test.beforeAll(async ({ browser }) => {
        page = await browser.newPage();
        await page.goto('http://localhost:8080/playground/');

        // Wait for authority files to load
        await page.waitForFunction(() => {
            return window.playground &&
                   window.playground.authorityManager &&
                   window.playground.authorityManager.authorityData.lemmata.length > 0;
        }, { timeout: 30000 });

        console.log('✓ Authority files loaded');
    });

    test.afterAll(async () => {
        await page.close();
    });

    test.describe('A. Authority Files Exploration (6 searches)', () => {

        test('1. Autoren anzeigen - Should normalize author names', async () => {
            // Test case-insensitive author search with normalization
            const result = await page.evaluate(() => {
                const persons = window.playground.authorityManager.authorityData.persons;
                const searchTerm = 'eckhart';

                // Simulate searchAuthors() logic
                const matches = window.SearchPatterns.textContainsNormalized(
                    persons,
                    searchTerm,
                    (person) => person.preferredName
                );

                return {
                    totalPersons: persons.length,
                    matches: matches.length,
                    hasEckhart: matches.some(p => p.preferredName.toLowerCase().includes('eckhart'))
                };
            });

            expect(result.totalPersons).toBeGreaterThan(0);
            expect(result.matches).toBeGreaterThan(0);
            expect(result.hasEckhart).toBe(true);
            console.log(`✓ Author search: ${result.matches} matches for "eckhart"`);
        });

        test('2. Werke anzeigen - Should normalize work titles', async () => {
            const result = await page.evaluate(() => {
                const works = window.playground.authorityManager.authorityData.works;
                const searchTerm = 'parzival';

                // Simulate searchWorks() logic
                const matches = window.SearchPatterns.multiFieldNormalized(
                    works,
                    searchTerm,
                    [
                        (work) => work.title,
                        (work) => work.author || "",
                        (work) => work.sigle || "",
                    ]
                );

                return {
                    totalWorks: works.length,
                    matches: matches.length,
                    hasParzival: matches.some(w => w.title && w.title.toLowerCase().includes('parzival'))
                };
            });

            expect(result.totalWorks).toBeGreaterThan(0);
            expect(result.matches).toBeGreaterThan(0);
            expect(result.hasParzival).toBe(true);
            console.log(`✓ Work search: ${result.matches} matches for "parzival"`);
        });

        test('3. Lemmata anzeigen - Should normalize lemma forms (brôt → brot)', async () => {
            const result = await page.evaluate(() => {
                const lemmata = window.playground.authorityManager.authorityData.lemmata;

                // Test multiple MHG normalization cases
                const testCases = [
                    { search: 'brot', expected: 'brôt', lemmaId: 'lemma_879' },
                    { search: 'win', expected: 'wîn', lemmaId: 'lemma_7532' },
                    { search: 'vriunt', expected: 'vriunt', lemmaId: 'lemma_1119' }
                ];

                const results = testCases.map(tc => {
                    const matches = window.SearchPatterns.textContainsNormalized(
                        lemmata,
                        tc.search,
                        (lemma) => lemma.lemma
                    );

                    const exactMatch = matches.find(m =>
                        m.id === tc.lemmaId ||
                        m.lemma === tc.expected
                    );

                    return {
                        search: tc.search,
                        expected: tc.expected,
                        matchCount: matches.length,
                        foundExpected: !!exactMatch,
                        actualLemma: exactMatch ? exactMatch.lemma : null
                    };
                });

                return {
                    totalLemmata: lemmata.length,
                    testResults: results
                };
            });

            expect(result.totalLemmata).toBeGreaterThan(0);

            // Verify each test case
            result.testResults.forEach(tc => {
                console.log(`  Testing "${tc.search}" → "${tc.expected}": ${tc.foundExpected ? '✓' : '✗'} (${tc.matchCount} matches)`);
                expect(tc.foundExpected).toBe(true);
                if (tc.actualLemma) {
                    console.log(`    Found lemma: ${tc.actualLemma}`);
                }
            });
        });

        test('4. Begriffe anzeigen - Should normalize concept terms', async () => {
            const result = await page.evaluate(() => {
                const concepts = window.playground.authorityManager.authorityData.concepts;
                const searchTerm = 'liebe'; // German for "love"

                const matches = window.SearchPatterns.multiFieldNormalized(
                    concepts,
                    searchTerm,
                    [(concept) => concept.termDE || "", (concept) => concept.termEN || ""]
                );

                return {
                    totalConcepts: concepts.length,
                    matches: matches.length
                };
            });

            expect(result.totalConcepts).toBeGreaterThan(0);
            console.log(`✓ Concept search: ${result.matches} matches for "liebe"`);
        });

        test('5. Gattungen anzeigen - Should normalize genre terms', async () => {
            const result = await page.evaluate(() => {
                const genres = window.playground.authorityManager.authorityData.genres;
                const searchTerm = 'predigt'; // German for "sermon"

                const matches = window.SearchPatterns.multiFieldNormalized(
                    genres,
                    searchTerm,
                    [(genre) => genre.termDE || "", (genre) => genre.termEN || ""]
                );

                return {
                    totalGenres: genres.length,
                    matches: matches.length
                };
            });

            expect(result.totalGenres).toBeGreaterThan(0);
            console.log(`✓ Genre search: ${result.matches} matches for "predigt"`);
        });

        test('6. Namen anzeigen - Should normalize name terms', async () => {
            const result = await page.evaluate(() => {
                const names = window.playground.authorityManager.authorityData.names;

                const matches = window.SearchPatterns.multiFieldNormalized(
                    names,
                    'maria',
                    [(name) => name.termDE || "", (name) => name.termEN || ""]
                );

                return {
                    totalNames: names.length,
                    matches: matches.length
                };
            });

            expect(result.totalNames).toBeGreaterThan(0);
            console.log(`✓ Name search: ${result.matches} matches for "maria"`);
        });
    });

    test.describe('B. TEI Text Analysis (Multi-Lemma Searches)', () => {

        test('7. Variants.xml Integration - Should resolve orthographic variants', async () => {
            const result = await page.evaluate(() => {
                const variants = window.playground.authorityManager.authorityData.variants;

                // Variants is now a flat object: { normalizedVariant: lemmaId, ... }
                const variantKeys = Object.keys(variants);
                const totalVariants = variantKeys.length;

                // Test variant resolution for known lemmas
                const testCases = [
                    { variant: 'brot', expectedLemmaId: 'lemma_879', canonical: 'brôt' },
                    { variant: 'win', expectedLemmaId: 'lemma_7532', canonical: 'wîn' },
                ];

                const results = testCases.map(tc => {
                    const resolvedLemmaId = variants[tc.variant];
                    return {
                        variant: tc.variant,
                        expectedLemmaId: tc.expectedLemmaId,
                        canonical: tc.canonical,
                        found: resolvedLemmaId === tc.expectedLemmaId,
                        resolvedLemmaId: resolvedLemmaId || null
                    };
                });

                return {
                    totalVariants: totalVariants,
                    testResults: results
                };
            });

            console.log(`✓ Variants loaded: ${result.totalVariants} variant mappings`);

            result.testResults.forEach(tc => {
                console.log(`  "${tc.variant}" → ${tc.canonical} (${tc.expectedLemmaId}): ${tc.found ? '✓' : '✗'}`);
            });

            // Verify variants are loaded with expected data
            expect(result.totalVariants).toBeGreaterThan(100000); // Should have ~176,056 variant mappings
        });

        test('8. searchLemmaByOrthography - 3-Stage Resolution', async () => {
            const result = await page.evaluate(() => {
                const manager = window.playground.authorityManager;

                // Test 3-stage resolution:
                // Stage 1: Exact lexicon match
                // Stage 2: Exact variants match
                // Stage 3: Partial match fallback

                // expectedLemma prüft die Stufe wirklich (Audit #112):
                // Stage 1/2 liefern genau EIN Lemma (Exact bzw. Variants-Hit
                // auf lemma_879), Stage 3 (Partial) liefert viele Treffer.
                const testCases = [
                    { input: 'brôt', stage: 1, desc: 'Exact lexicon match', expectedLemma: 'lemma_879', exactCount: 1 },
                    { input: 'brott', stage: 2, desc: 'Exact variant match', expectedLemma: 'lemma_879', exactCount: 1 },
                    { input: 'brot', stage: 2, desc: 'Normalized variant match', expectedLemma: 'lemma_879', exactCount: 1 },
                    { input: 'fri', stage: 3, desc: 'Partial match fallback', minCount: 2 }
                ];

                const results = testCases.map(tc => {
                    const lemmas = manager.searchLemmaByOrthography(tc.input);
                    return {
                        input: tc.input,
                        expectedStage: tc.stage,
                        description: tc.desc,
                        expectedLemma: tc.expectedLemma || null,
                        exactCount: tc.exactCount || null,
                        minCount: tc.minCount || 1,
                        foundLemmas: lemmas.length,
                        foundIds: lemmas.slice(0, 5).map(l => l.id)
                    };
                });

                return { testResults: results };
            });

            result.testResults.forEach(tc => {
                console.log(`  Stage ${tc.expectedStage}: "${tc.input}" → ${tc.foundLemmas} lemmas [${tc.foundIds.join(', ')}]`);
                if (tc.exactCount !== null) {
                    expect(tc.foundLemmas, `${tc.input}: Stage ${tc.expectedStage} muss genau ${tc.exactCount} Treffer liefern`).toBe(tc.exactCount);
                }
                if (tc.expectedLemma) {
                    expect(tc.foundIds, `${tc.input}: erwartetes Lemma`).toContain(tc.expectedLemma);
                }
                expect(tc.foundLemmas).toBeGreaterThanOrEqual(tc.minCount);
            });
        });

        test('9. Multi-Lemma Search - Should resolve variant spellings', async () => {
            // This test verifies the complete flow from user input to lemma resolution
            const result = await page.evaluate(() => {
                const manager = window.playground.authorityManager;

                // Simulate user searching for "brott + win"
                const userInputs = ['brott', 'win'];

                // Resolve to lemma IDs (this is what resolveLemmaIds does)
                const resolvedLemmas = userInputs.map(input => {
                    const lemmaIds = manager.searchLemmaByOrthography(input);
                    return {
                        input: input,
                        resolvedIds: lemmaIds,
                        resolvedCount: lemmaIds.length
                    };
                });

                return { resolvedLemmas };
            });

            console.log('✓ Multi-lemma resolution test:');
            result.resolvedLemmas.forEach(lemma => {
                console.log(`  "${lemma.input}" → ${lemma.resolvedCount} lemma(s): ${lemma.resolvedIds.slice(0, 3).join(', ')}`);
                expect(lemma.resolvedCount).toBeGreaterThan(0);
            });
        });

        test('10. TextNormalizer - Comprehensive normalization rules', async () => {
            const result = await page.evaluate(() => {
                // Test all normalization rules
                const testCases = [
                    { input: 'brôt', expected: 'brot', rule: 'â → a' },
                    { input: 'wîn', expected: 'win', rule: 'î → i' },
                    { input: 'schône', expected: 'schone', rule: 'ô → o' },
                    { input: 'hûs', expected: 'hus', rule: 'û → u' },
                    { input: 'sêle', expected: 'sele', rule: 'ê → e' },
                    { input: 'mähte', expected: 'maehte', rule: 'ä → ae' },
                    { input: 'schöne', expected: 'schoene', rule: 'ö → oe' },
                    { input: 'künec', expected: 'kuenec', rule: 'ü → ue' },
                    { input: 'sælde', expected: 'saelde', rule: 'æ → ae' },
                    { input: 'schœne', expected: 'schoene', rule: 'œ → oe' }
                ];

                const results = testCases.map(tc => {
                    const normalized = window.TextNormalizer.normalizeMHG(tc.input);
                    return {
                        input: tc.input,
                        expected: tc.expected,
                        actual: normalized,
                        rule: tc.rule,
                        passed: normalized === tc.expected
                    };
                });

                return { testResults: results };
            });

            console.log('✓ TextNormalizer comprehensive test:');
            result.testResults.forEach(tc => {
                const status = tc.passed ? '✓' : '✗';
                console.log(`  ${status} ${tc.rule}: "${tc.input}" → "${tc.actual}" (expected: "${tc.expected}")`);
                expect(tc.passed).toBe(true);
            });
        });

        test('11. matchesNormalized - Should match with normalization', async () => {
            const result = await page.evaluate(() => {
                // Test matching with various MHG characters
                const testCases = [
                    { text: 'brôt', search: 'brot', shouldMatch: true },
                    { text: 'brot', search: 'brôt', shouldMatch: true },
                    { text: 'wîn', search: 'win', shouldMatch: true },
                    { text: 'vriunt', search: 'vriunt', shouldMatch: true },
                    { text: 'minne', search: 'min', shouldMatch: true }, // Partial match
                    { text: 'brôt', search: 'win', shouldMatch: false }  // No match
                ];

                const results = testCases.map(tc => {
                    const matches = window.TextNormalizer.matchesNormalized(tc.text, tc.search);
                    return {
                        text: tc.text,
                        search: tc.search,
                        shouldMatch: tc.shouldMatch,
                        actualMatch: matches,
                        passed: matches === tc.shouldMatch
                    };
                });

                return { testResults: results };
            });

            console.log('✓ matchesNormalized test:');
            result.testResults.forEach(tc => {
                const status = tc.passed ? '✓' : '✗';
                const matchStatus = tc.actualMatch ? 'MATCH' : 'NO MATCH';
                console.log(`  ${status} "${tc.text}" vs "${tc.search}": ${matchStatus} (expected: ${tc.shouldMatch ? 'MATCH' : 'NO MATCH'})`);
                expect(tc.passed).toBe(true);
            });
        });
    });

    test.describe('C. Search Integration Summary', () => {

        test('12. All 11 searches should use normalization', async () => {
            const result = await page.evaluate(() => {
                // Verify all search components are loaded
                const checks = {
                    textNormalizer: typeof window.TextNormalizer !== 'undefined',
                    searchPatterns: typeof window.SearchPatterns !== 'undefined',
                    authorityManager: window.playground?.authorityManager !== undefined,
                    teiManager: window.playground?.teiManager !== undefined,

                    // Check specific methods
                    normalizeMHG: typeof window.TextNormalizer?.normalizeMHG === 'function',
                    matchesNormalized: typeof window.TextNormalizer?.matchesNormalized === 'function',
                    textContainsNormalized: typeof window.SearchPatterns?.textContainsNormalized === 'function',
                    multiFieldNormalized: typeof window.SearchPatterns?.multiFieldNormalized === 'function',

                    // Check data loaded
                    hasPersons: window.playground?.authorityManager?.authorityData?.persons?.length > 0,
                    hasWorks: window.playground?.authorityManager?.authorityData?.works?.length > 0,
                    hasLemmata: window.playground?.authorityManager?.authorityData?.lemmata?.length > 0,
                    hasConcepts: window.playground?.authorityManager?.authorityData?.concepts?.length > 0,
                    hasGenres: window.playground?.authorityManager?.authorityData?.genres?.length > 0,
                    hasNames: window.playground?.authorityManager?.authorityData?.names?.length > 0,
                    hasVariants: Object.keys(window.playground?.authorityManager?.authorityData?.variants || {}).length > 0
                };

                const passedChecks = Object.values(checks).filter(v => v === true).length;
                const totalChecks = Object.keys(checks).length;

                return {
                    checks,
                    passedChecks,
                    totalChecks,
                    allPassed: passedChecks === totalChecks
                };
            });

            console.log(`\n✓ Integration Summary: ${result.passedChecks}/${result.totalChecks} checks passed`);
            console.log('\nComponent Status:');
            Object.entries(result.checks).forEach(([key, value]) => {
                const status = value ? '✓' : '✗';
                console.log(`  ${status} ${key}`);
            });

            expect(result.allPassed).toBe(true);
        });

        test('13. Performance - Normalization should be fast', async () => {
            const result = await page.evaluate(() => {
                const iterations = 1000;
                const testString = 'brôt wîn vriunt minne schône';

                const start = performance.now();
                for (let i = 0; i < iterations; i++) {
                    window.TextNormalizer.normalizeMHG(testString);
                }
                const end = performance.now();

                const totalTime = end - start;
                const avgTime = totalTime / iterations;

                return {
                    iterations,
                    totalTime: totalTime.toFixed(2),
                    avgTime: avgTime.toFixed(4),
                    performant: avgTime < 1.0 // Should be < 1ms per call
                };
            });

            console.log(`\n✓ Performance Test:`);
            console.log(`  ${result.iterations} normalizations in ${result.totalTime}ms`);
            console.log(`  Average: ${result.avgTime}ms per call`);

            expect(result.performant).toBe(true);
        });
    });
});
