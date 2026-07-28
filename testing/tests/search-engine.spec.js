/**
 * Search Engine Tests
 * Tests for SearchEngine class methods via page.evaluate()
 *
 * Covers: searchLemma(), resolveLemmaIds() (3-stage), passesFilters(),
 * text inclusion filtering, snippet extraction
 *
 * Uses window._mhdbdbApp.searchEngine for direct method access.
 * Issue #43 — Priority 3: search engine coverage
 */

import { test, expect } from '@playwright/test';

test.describe('Search Engine', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    });

    test('searchLemma() returns results for known term', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            return await se.searchLemma('got');
        });

        expect(results.length).toBeGreaterThan(0);

        // Each result should have expected fields
        const first = results[0];
        expect(first).toHaveProperty('textId');
        expect(first).toHaveProperty('title');
        expect(first).toHaveProperty('matchCount');
        expect(first).toHaveProperty('lemmaId');
    });

    test('authority index has no exact or variant entry for gibberish', async ({ page }) => {
        // Stage 3 partial match may still return results for any string,
        // so we test that resolveLemmaIds finds no exact or variant match
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            // Stage 1: exact match
            const exact = se.authorityIndex.lemmata.filter(l => l.normalized === 'zzzzqxjk');
            // Stage 2: variant match
            const variant = se.authorityIndex.variants['zzzzqxjk'];
            return { exact: exact.length, variant: !!variant };
        });

        expect(lemmaIds.exact).toBe(0);
        expect(lemmaIds.variant).toBe(false);
    });

    test('resolveLemmaIds() - exact match (Stage 1)', async ({ page }) => {
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('got');
        });

        expect(lemmaIds.length).toBeGreaterThan(0);
    });

    test('resolveLemmaIds() - variant match (Stage 2)', async ({ page }) => {
        // 'brot' is normalized form of 'brôt', should resolve via variants index
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('brot');
        });

        expect(lemmaIds.length).toBeGreaterThan(0);
        // Should resolve to lemma_879 (brôt)
        expect(lemmaIds.some(id => id.includes('879'))).toBeTruthy();
    });

    test('resolveLemmaIds() - partial match (Stage 3)', async ({ page }) => {
        // A term that has no exact or variant match falls through to partial
        const lemmaIds = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            return se.resolveLemmaIds('fri');
        });

        // Stage 3 should find at least one prefix match ('fri' is a prefix of
        // Friaul, Frîtel, friên, ...)
        expect(lemmaIds.length).toBeGreaterThanOrEqual(1);
    });

    test('resolveLemmaIds() - Stage 3 drops short-lemma noise (#224)', async ({ page }) => {
        // WICHTIG: der Suchbegriff muss Stufe 3 auch erreichen. "boeses" tut das
        // NICHT — variants["boeses"] existiert, Stufe 2 fängt es ab und liefert
        // korrekt bœse. Genau daran wäre ein Test mit "boeses" wertlos: er wäre
        // auch vor dem Fix grün. "minnecl" trifft weder Stufe 1 noch Stufe 2.
        const result = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            const byId = new Map(se.authorityIndex.lemmata.map(l => [l.id, l]));
            const norm = 'minnecl';
            return {
                stage1: se.authorityIndex.lemmata.some(l => l.normalized === norm),
                stage2: !!se.authorityIndex.variants[norm],
                hits: se.resolveLemmaIds(norm).map(id => byId.get(id)?.normalized || '')
            };
        });

        // Vorbedingung des Tests: der Begriff landet wirklich in Stufe 3.
        expect(result.stage1, 'minnecl darf Stufe 1 nicht treffen').toBeFalsy();
        expect(result.stage2, 'minnecl darf Stufe 2 nicht treffen').toBeFalsy();

        expect(result.hits.length).toBeGreaterThan(0);

        // Jeder Treffer teilt eine Präfixgrenze mit der Eingabe.
        for (const n of result.hits) {
            const lemmaIstPraefix = 'minnecl'.startsWith(n);
            const beginntMitEingabe = n.startsWith('minnecl');
            expect(lemmaIstPraefix || beginntMitEingabe,
                `"${n}" ist weder Präfix der Eingabe noch beginnt damit`).toBeTruthy();
            if (lemmaIstPraefix && !beginntMitEingabe) {
                expect(n.length).toBeGreaterThanOrEqual(3);
            }
        }

        // Das alte Substring-Verhalten lieferte hier i, in, nec, innec.
        for (const rauschen of ['i', 'in', 'nec', 'innec']) {
            expect(result.hits).not.toContain(rauschen);
        }
    });

    test('resolveLemmaIds() - Stage 3 ranks the closest lemma first (#224)', async ({ page }) => {
        // Sortierung nach Längendifferenz: minnec (6) steht vor minneclîcheit (13).
        const hits = await page.evaluate(() => {
            const se = window._mhdbdbApp.searchEngine;
            const byId = new Map(se.authorityIndex.lemmata.map(l => [l.id, l]));
            return se.resolveLemmaIds('minnecl').map(id => byId.get(id)?.normalized || '');
        });

        expect(hits.length).toBeGreaterThan(1);
        expect(hits[0]).toBe('minnec');

        const abstand = n => Math.abs(n.length - 'minnecl'.length);
        for (let i = 1; i < hits.length; i++) {
            expect(abstand(hits[i])).toBeGreaterThanOrEqual(abstand(hits[i - 1]));
        }
    });

    test('resolveLemmaIds() - zerlegtes Umlaut-ö wird komponiert (#224)', async ({ page }) => {
        // Die eigentliche Ursache im Bug-Report: "böses" mit o + U+0308 verfehlte
        // Stufe 1 UND Stufe 2 und fiel in den Fallback. Beide Schreibweisen
        // müssen jetzt dasselbe liefern.
        const result = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            // korpus.html legt TextNormalizer nicht auf window (nur der
            // Playground tut das), deshalb hier dynamisch importieren statt
            // Produktionscode für den Test zu erweitern.
            const { TextNormalizer: N } = await import('/assets/js/lib/text-normalizer.js');
            const byId = new Map(se.authorityIndex.lemmata.map(l => [l.id, l]));
            const KOMPONIERT = 'böses';        // b + U+00F6 + ses
            const ZERLEGT    = 'böses';       // b + o + U+0308 + ses
            const aufloesen = eingabe => se.resolveLemmaIds(N.normalizeMHG(eingabe))
                .map(id => byId.get(id)?.normalized || '');
            return {
                normKomponiert: N.normalizeMHG(KOMPONIERT),
                normZerlegt: N.normalizeMHG(ZERLEGT),
                komponiert: aufloesen(KOMPONIERT),
                zerlegt: aufloesen(ZERLEGT)
            };
        });

        // Beide Schreibweisen normalisieren gleich ...
        expect(result.normZerlegt).toBe('boeses');
        expect(result.normZerlegt).toBe(result.normKomponiert);

        // ... und loesen deshalb beide ueber Stufe 2 auf das richtige Lemma auf.
        expect(result.komponiert).toEqual(['boese']);
        expect(result.zerlegt).toEqual(result.komponiert);
    });

    test('text inclusion filter restricts results', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            const included = new Set(['ABG', 'NIB']);
            return await se.searchLemma('got', { includedTexts: included });
        });

        // All results should be from included texts only
        results.forEach(r => {
            expect(['ABG', 'NIB']).toContain(r.textId);
        });
    });

    test('deselect all texts - search returns no results (UI)', async ({ page }) => {
        // Click "Keine" to deselect all texts
        await page.click('#selectNoneTexts');
        await page.waitForTimeout(300);

        // Search for a common term
        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForTimeout(2000);

        // Should show no results
        const noResults = await page.locator('#noResults').isVisible();
        const resultCount = await page.locator('#resultsList > div').count();

        expect(noResults || resultCount === 0).toBeTruthy();
    });

    test('snippet extraction returns non-empty string', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            return await se.searchLemma('got');
        });

        expect(results.length).toBeGreaterThan(0);
        expect(typeof results[0].snippet).toBe('string');
        expect(results[0].snippet.length).toBeGreaterThan(0);
    });

    test('search results include wordCount for frequency calculations', async ({ page }) => {
        const results = await page.evaluate(async () => {
            const se = window._mhdbdbApp.searchEngine;
            return await se.searchLemma('minne');
        });

        expect(results.length).toBeGreaterThan(0);

        const firstResult = results[0];
        expect(firstResult).toHaveProperty('wordCount');
        expect(typeof firstResult.wordCount).toBe('number');
        expect(firstResult.wordCount).toBeGreaterThan(0);
    });

});
