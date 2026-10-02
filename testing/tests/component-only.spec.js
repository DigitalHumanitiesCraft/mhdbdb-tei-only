/**
 * Reine Wortbestandteile im Wörterbuch und auf der Lemmaseite (#228)
 *
 * Regel (KZW, 01.10.2026): ein Eintrag ohne Korpusbeleg, den eine andere
 * Etymologie als Bestandteil nennt, trägt den Hinweis „Als Wortbestandteil
 * erfasst; kein eigenständiger Beleg im aktuellen Korpus." Der Status wird
 * abgeleitet: `noCorpus: true` am Lemma (setzt der Build, ab Authority-Index
 * 1.9.18) plus `etymology[].lemmaRef` der übrigen Lemmata.
 *
 * Die Spec ersetzt den Authority-Index per Route durch eine Kopie des echten
 * Index, in der `noCorpus` an drei Lemmata gesetzt ist. Sie prüft damit die
 * Anzeigeregel unabhängig davon, ob der Build das Feld schon schreibt.
 * Der Gegenstand, an dem die Regel hängt, sind drei Fälle:
 *   Mur (lemma_66692)  ohne Beleg, von Murouwe und Murstat genannt: Hinweis
 *   Kontrolle A        ohne Beleg, von niemandem genannt: kein Hinweis
 *   ouwe (lemma_4532)  von Murouwe genannt, aber belegt (kein noCorpus): kein Hinweis
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { gunzipSync, gzipSync } from 'node:zlib';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const INDEX_PATH = resolve(HERE, '../../data/authority-index.json.gz');

const NOTE = 'Als Wortbestandteil erfasst; kein eigenständiger Beleg im aktuellen Korpus.';
const MUR = 'lemma_66692';
const OUWE = 'lemma_4532';

/** Echter Index mit gesetztem noCorpus an Mur und an einer ungenannten Kontrolle. */
function buildMockIndex() {
    const index = JSON.parse(gunzipSync(readFileSync(INDEX_PATH)).toString('utf8'));
    const genannt = new Set();
    for (const l of index.lemmata) {
        for (const c of l.etymology || []) if (c.lemmaRef && c.lemmaRef !== l.id) genannt.add(c.lemmaRef);
    }
    const mur = index.lemmata.find(l => l.id === MUR);
    expect(mur, 'Mur im Index').toBeTruthy();
    expect(genannt.has(MUR), 'Mur wird als Bestandteil genannt').toBe(true);
    expect(genannt.has(OUWE), 'ouwe wird als Bestandteil genannt').toBe(true);
    mur.noCorpus = true;
    // Kontrolle A: ein Lemma, das niemand nennt und das mit "z" beginnt
    const kontrolle = index.lemmata.find(l => !genannt.has(l.id) && l.normalized && l.normalized.startsWith('zw') && l.id !== MUR);
    expect(kontrolle, 'Kontrolle A gefunden').toBeTruthy();
    kontrolle.noCorpus = true;
    return { buffer: gzipSync(JSON.stringify(index)), kontrolle };
}

async function mockIndex(page, buffer) {
    await page.route('**/data/authority-index.json.gz', route => route.fulfill({
        status: 200,
        contentType: 'application/gzip',
        body: buffer,
    }));
}

test.describe('Reine Wortbestandteile (#228)', () => {

    test('Wörterbuch: Marke nur bei Mur, volle Aussage als Tooltip', async ({ page }) => {
        const { buffer, kontrolle } = buildMockIndex();
        await mockIndex(page, buffer);
        await page.goto('/woerterbuch.html');
        await page.waitForSelector('#woerterbuchContent:not(.hidden)', { timeout: 30000 });

        await page.fill('#lemmaSearch', 'mur');
        const murRow = page.locator('#entryGrid > div', { has: page.locator(`a[href="lemma/?id=66692"]`) });
        const tag = murRow.locator('[data-component-only]');
        await expect(tag).toHaveCount(1);
        await expect(tag).toHaveText('nur als Wortbestandteil');
        await expect(tag).toHaveAttribute('title', NOTE);

        // Kontrolle B: belegt (kein noCorpus), obwohl als Bestandteil genannt
        await page.fill('#lemmaSearch', 'ouwe');
        await expect(page.locator(`#entryGrid a[href="lemma/?id=4532"]`)).toHaveCount(1);
        await expect(page.locator('#entryGrid [data-component-only]')).toHaveCount(0);

        // Kontrolle A: ohne Beleg, aber von keiner Etymologie genannt
        await page.fill('#lemmaSearch', kontrolle.normalized);
        await expect(page.locator(`#entryGrid a[href="lemma/?id=${kontrolle.id.replace('lemma_', '')}"]`)).toHaveCount(1);
        await expect(page.locator('#entryGrid [data-component-only]')).toHaveCount(0);
    });

    test('Lemmaseite: Hinweis bei Mur, nicht bei ouwe und nicht bei Kontrolle A', async ({ page }) => {
        const { buffer, kontrolle } = buildMockIndex();
        await mockIndex(page, buffer);

        await page.goto('/lemma/?id=66692');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#componentOnlyNote')).toBeVisible();
        await expect(page.locator('#componentOnlyText')).toHaveText(NOTE);

        // Der Hinweis stellt die Zerlegung nicht als geprüft dar
        const text = await page.textContent('#componentOnlyNote');
        expect(text).not.toMatch(/geprüft|bestätigt|korrekt|richtig/i);

        await page.goto('/lemma/?id=4532');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#componentOnlyNote')).toBeHidden();

        await page.goto(`/lemma/?id=${kontrolle.id.replace('lemma_', '')}`);
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        await expect(page.locator('#componentOnlyNote')).toBeHidden();
    });

    test('ohne noCorpus-Feld (alter Index) erscheint nirgends ein Hinweis', async ({ page }) => {
        await page.goto('/lemma/?id=66692');
        await page.waitForSelector('#lemmaContent:not(.hidden)', { timeout: 30000 });
        const hatFeld = await page.evaluate(async () => {
            const { CorpusLoader } = await import('/assets/js/lib/corpus-loader.js');
            const idx = await new CorpusLoader('/data').loadAuthorityIndex();
            return idx.lemmata.some(l => l.noCorpus === true);
        });
        const sichtbar = await page.locator('#componentOnlyNote').isVisible();
        // Solange der Index das Feld nicht trägt, bleibt der Hinweis weg; trägt er es, muss er bei Mur stehen.
        expect(sichtbar).toBe(hatFeld);
    });
});
