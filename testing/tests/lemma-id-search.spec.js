/**
 * Suche nach der Lemma-Nummer in Korpussuche und Multi-Lemma-Suche (#467)
 *
 * KZW am 2026-09-24 in #467: "Bitte beide Schreibweisen, 4086 und lemma_4086,
 * in beiden Suchen unterstuetzen und jeweils als eindeutige Lemma-ID
 * behandeln. Nach der Aufloesung soll das zugehoerige Lemma sichtbar sein,
 * damit Nutzende ihre Eingabe kontrollieren koennen."
 *
 * Das Orakel liest den Authority-Index von der Platte: Name und Existenz der
 * Beispielnummern kommen aus den Daten, nicht aus diesem Test. Das
 * Woerterbuch hat seine eigene Nummernsuche (#481, woerterbuch.spec.js).
 *
 * Relative Pfade gegen baseURL, kein fester Port (#465).
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { gunzipSync } from 'zlib';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const auth = JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', 'authority-index.json.gz'))).toString('utf-8'));
const corpus = JSON.parse(gunzipSync(readFileSync(resolve(wurzel, 'data', 'corpus-index.json.gz'))).toString('utf-8'));
const byId = new Map(auth.lemmata.map(l => [l.id, l]));

// Beispiel aus dem Ticket; "36" ist der Fall, in dem Nummer und Schreibung
// auseinanderlaufen, solange ein Lemma mit der Schreibung "36" existiert.
const MER = byId.get('lemma_4086');
const NR36 = byId.get('lemma_36');
// Kleinste Nummer ohne Lemma, und ein Lemma ohne Korpusbeleg
const FEHLT = (() => { let n = 1; while (byId.has(`lemma_${n}`)) n++; return n; })();
const OHNE_BELEG = auth.lemmata.find(l => !corpus.lemmaIndex[l.id]);

test.describe('Lemma-Nummer in der Korpussuche (#467)', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    });

    for (const eingabe of ['4086', 'lemma_4086']) {
        test(`"${eingabe}" findet genau das Lemma mit dieser Nummer`, async ({ page }) => {
            expect(MER, 'lemma_4086 fehlt im Index').toBeTruthy();
            await page.fill('#searchInput', eingabe);
            await page.click('#searchButton');
            const badges = page.locator('#lemmaList a');
            await expect(badges).toHaveCount(1, { timeout: 15000 });
            await expect(badges.first()).toHaveAttribute('href', 'lemma/?id=4086');
            await expect(badges.first()).toHaveText(MER.lemma);
            await expect(page.locator('#resultsList > div').first()).toBeVisible();
        });
    }

    test('eine Nummer ist eine ID, keine Schreibform', async ({ page }) => {
        await page.fill('#searchInput', '36');
        await page.click('#searchButton');
        const badges = page.locator('#lemmaList a');
        await expect(badges).toHaveCount(1, { timeout: 15000 });
        await expect(badges.first()).toHaveText(NR36.lemma);
    });

    test('ein Lemma ohne Treffer bleibt sichtbar', async ({ page }) => {
        const nummer = OHNE_BELEG.id.replace('lemma_', '');
        await page.fill('#searchInput', OHNE_BELEG.id);
        await page.click('#searchButton');
        await expect(page.locator('#noResults')).toBeVisible({ timeout: 15000 });
        await expect(page.locator('#lemmaList a')).toHaveAttribute('href', `lemma/?id=${nummer}`);
    });

    test('eine unbekannte Nummer ergibt keinen Treffer und kein Lemma', async ({ page }) => {
        await page.fill('#searchInput', `lemma_${FEHLT}`);
        await page.click('#searchButton');
        await expect(page.locator('#noResults')).toBeVisible({ timeout: 15000 });
        await expect(page.locator('#lemmaInfo')).toBeHidden();
    });
});

// Lemmata mit reiner Ziffernschreibung (#228 raeumt sie gerade ab, darum aus
// den Daten und nicht fest verdrahtet) und ihre Ziffern-Varianten
const ZIFFERN = /^\d+$/;
const ZIFFERN_LEMMA = auth.lemmata.find(l => ZIFFERN.test(l.lemma)
    && Object.entries(auth.variants).some(([k, v]) => v === l.id && ZIFFERN.test(k)));

test.describe('Links der Lemma-Seite in die Korpussuche (#467)', () => {
    test('ein Wort-Lemma verlinkt weiter seine Schreibform', async ({ page }) => {
        await page.goto('/lemma/?id=4086');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#externalLinks a', { hasText: 'Im Korpus suchen' }))
            .toHaveAttribute('href', `../korpus.html?search=${encodeURIComponent(MER.lemma)}`);
    });

    test('ein Ziffern-Lemma verlinkt seine ID, nicht die Ziffer', async ({ page }) => {
        test.skip(!ZIFFERN_LEMMA, 'kein Lemma mit Ziffernschreibung und Ziffern-Varianten mehr im Index');
        const nummer = ZIFFERN_LEMMA.id.replace('lemma_', '');
        await page.goto(`/lemma/?id=${nummer}`);
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#externalLinks a', { hasText: 'Im Korpus suchen' }))
            .toHaveAttribute('href', `../korpus.html?search=${ZIFFERN_LEMMA.id}`);
        // Jeder Varianten-Chip aus Ziffern zeigt auf dieses Lemma
        const chips = page.locator('#variantsContent a');
        const anzahl = await chips.count();
        let ziffernChips = 0;
        for (let i = 0; i < anzahl; i++) {
            if (!ZIFFERN.test((await chips.nth(i).textContent()).trim())) continue;
            ziffernChips++;
            await expect(chips.nth(i)).toHaveAttribute('href', `../korpus.html?search=${ZIFFERN_LEMMA.id}`);
        }
        expect(ziffernChips).toBeGreaterThan(0);
    });
});

test.describe('Lemma-Nummer in der Multi-Lemma-Suche (#467)', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/playground/');
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });
    });

    test('beide Schreibweisen loesen zur selben ID auf, unbekannte zu nichts', async ({ page }) => {
        const ids = await page.evaluate(fehlt => ({
            nackt: window.playground.ui.teiExplorer.resolveLemmaIds(['4086']),
            praefix: window.playground.ui.teiExplorer.resolveLemmaIds(['lemma_4086']),
            tei: window.playground.ui.teiExplorer.resolveLemmaIds(['lexicon.xml#lemma_4086']),
            fehlt: window.playground.ui.teiExplorer.resolveLemmaIds([`lemma_${fehlt}`, String(fehlt)])
        }), FEHLT);
        expect(ids).toEqual({ nackt: ['4086'], praefix: ['4086'], tei: ['4086'], fehlt: [] });
    });

    test('der Chip zeigt, worauf die Nummer aufloest', async ({ page }) => {
        await page.click('#findMultiLemmaBtn');
        await page.fill('#lemmaInput', 'lemma_4086');
        await page.press('#lemmaInput', 'Enter');
        await page.fill('#lemmaInput', String(FEHLT));
        await page.press('#lemmaInput', 'Enter');
        const chips = page.locator('#lemmaChips .lemma-chip');
        await expect(chips).toHaveCount(2);
        await expect(chips.nth(0)).toContainText(`lemma_4086 = ${MER.lemma}`);
        await expect(chips.nth(1)).toContainText('unbekannte Lemma-Nummer');
    });

    test('die Dokumentsuche mit lemma_4086 liefert Belege', async ({ page }) => {
        await page.click('#findMultiLemmaBtn');
        await page.fill('#lemmaInput', 'lemma_4086');
        await page.press('#lemmaInput', 'Enter');
        await page.locator('input[name="searchMode"][value="document"]').check({ force: true });
        await page.click('#executeSearch');
        // Die Kopfzeile der Dokumentsuche zaehlt Treffer; eine unaufgeloeste
        // Eingabe landete stattdessen in der roten "Keine gueltigen Lemmata"-Box.
        await expect(page.locator('#resultsContainer')).toContainText('Treffer', { timeout: 60000 });
        await expect(page.locator('#resultsContainer')).not.toContainText('Keine gültigen Lemmata');
    });
});
