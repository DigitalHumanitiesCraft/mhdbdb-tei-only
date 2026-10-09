/**
 * Zuschreibungsstatus fuer Werkautoren (#452, #444)
 *
 * Vier Status (KZW 08.10.2026): ohne Zusatz = anerkannt, "umstritten",
 * "unsicher zugeschrieben", "verworfen"; dazu die Rolle "Bearbeiter". Je eine
 * reale Seite pro Fall, gemessen an den fuenf betroffenen Sigeln:
 *
 *   CR    Anonym; Bligger von Steinach verworfen  -> "Frühere Zuschreibungen"
 *   BAX   Lamprecht; Anonym als Bearbeiter        -> kein Autor
 *   HOF   Stricker allein (Anonym entfaellt)
 *   RHB   Anonym zuerst, Konrad von Würzburg umstritten (zaehlt als Autor)
 *
 * "unsicher zugeschrieben" kommt in den Daten noch nicht vor (kein Werk traegt
 * es); der Anzeigetext wird deshalb an der Bibliothek geprueft, nicht an einer
 * Seite.
 */

import { test, expect } from '@playwright/test';

async function openReader(page, textId) {
    await page.goto(`/korpus.html?textId=${textId}`);
    await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
}

async function openMetadata(page) {
    await page.click('.metadata-toggle-btn');
    const sections = page.locator('.metadata-sections');
    await expect(sections).toBeVisible();
    return sections;
}

test.describe('Zuschreibungsstatus: Leseansicht', () => {
    test('RHB: Konrad umstritten zaehlt als Autor, Anonym steht davor', async ({ page }) => {
        await openReader(page, 'RHB');
        await expect(page.locator('#readingAuthor')).toHaveText('Anonym; Konrad von Würzburg (umstritten)');
        const sections = await openMetadata(page);
        await expect(sections).toContainText('Konrad von Würzburg');
        await expect(sections).toContainText('(umstritten)');
        await expect(sections).not.toContainText('Frühere Zuschreibungen');
        await expect(sections).not.toContainText('Bearbeiter');
    });

    test('BAX: Anonym ist Bearbeiter, nicht Autor', async ({ page }) => {
        await openReader(page, 'BAX');
        await expect(page.locator('#readingAuthor')).toHaveText('Lamprecht der Pfaffe');
        const sections = await openMetadata(page);
        await expect(sections).toContainText('Bearbeiter');
        await expect(sections).toContainText('Anonym');
        await expect(sections.locator('.metadata-row[title*="Basler Fassung"]')).toHaveCount(1);
    });

    test('CR: Bligger von Steinach nur unter "Frühere Zuschreibungen"', async ({ page }) => {
        await openReader(page, 'CR');
        await expect(page.locator('#readingAuthor')).toHaveText('Anonym');
        const sections = await openMetadata(page);
        await expect(sections).toContainText('Frühere Zuschreibungen');
        await expect(sections).toContainText('Bligger von Steinach');
        await expect(sections).toContainText('(verworfen)');
    });

    test('HOF und VDH: Stricker allein', async ({ page }) => {
        for (const textId of ['HOF', 'VDH']) {
            await openReader(page, textId);
            await expect(page.locator('#readingAuthor')).toHaveText('Der Stricker');
            const sections = await openMetadata(page);
            await expect(sections).not.toContainText('Anonym');
            await expect(sections).not.toContainText('Frühere Zuschreibungen');
        }
    });
});

test.describe('Zuschreibungsstatus: Autorfilter der Suchmaschine', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
    });

    /** Textsigle -> Treffer fuer ein Lemma, das der Text sicher traegt, mit dem Autorfilter. */
    async function trefferFuer(page, textId, authorId) {
        return page.evaluate(async ({ textId, authorId }) => {
            const se = window._mhdbdbApp.searchEngine;
            const text = se.corpusIndex.texts.find(t => t.id === textId);
            const lemmaId = Object.keys(text.lemmata)[0];
            const results = await se.searchLemma(lemmaId, { authorId });
            return results.filter(r => r.textId === textId).map(r => ({ textId: r.textId, author: r.author }));
        }, { textId, authorId });
    }

    test('Konrad findet RHB (umstritten zaehlt als Autor), Anonym ebenfalls', async ({ page }) => {
        expect((await trefferFuer(page, 'RHB', 'person_1')).length).toBe(1);
        expect((await trefferFuer(page, 'RHB', 'person_anonym')).length).toBe(1);
    });

    test('Trefferzeile nennt alle Zuschreibungen mit Statustext', async ({ page }) => {
        const [treffer] = await trefferFuer(page, 'RHB', 'person_1');
        expect(treffer.author).toBe('Anonym; Konrad von Würzburg (umstritten)');
    });

    test('Bearbeiter zaehlt nicht: Anonym findet BAX nicht, Lamprecht schon', async ({ page }) => {
        expect((await trefferFuer(page, 'BAX', 'person_anonym')).length).toBe(0);
        expect((await trefferFuer(page, 'BAX', 'person_565')).length).toBe(1);
    });

    test('verworfen zaehlt nicht: Bligger findet CR nicht, Anonym schon', async ({ page }) => {
        expect((await trefferFuer(page, 'CR', 'person_227')).length).toBe(0);
        expect((await trefferFuer(page, 'CR', 'person_anonym')).length).toBe(1);
    });
});

test.describe('Zuschreibungsstatus: Personenansicht und Anzeigetexte', () => {
    test('Bligger fuehrt CR unter "Frühere Zuschreibungen", Werke nur MBS', async ({ page }) => {
        await page.goto('/playground/#authors&q=person_227');
        const treffer = page.locator('#authorResults');
        await expect(treffer).toContainText('ID: person_227', { timeout: 60000 });
        await expect(treffer).toContainText('1 frühere Zuschreibung');
        await treffer.getByRole('button', { name: 'Werke anzeigen' }).first().click();
        const details = page.locator('#works-person_227');
        await expect(details).toContainText('Frühere Zuschreibungen (1)');
        await expect(details).toContainText('(CR)');
        await expect(details).toContainText('(verworfen)');
        await expect(details).toContainText('1 Werke von');
    });

    test('Konrad behaelt RHB als Werk, mit Statustext', async ({ page }) => {
        await page.goto('/playground/#authors&q=person_1');
        const treffer = page.locator('#authorResults');
        await expect(treffer).toContainText('ID: person_1', { timeout: 60000 });
        await treffer.getByRole('button', { name: 'Werke anzeigen' }).first().click();
        await expect(page.locator('#works-person_1')).toContainText('(umstritten)');
    });

    test('Anonym fuehrt BAX nur als Bearbeiter', async ({ page }) => {
        await page.goto('/playground/#authors&q=person_anonym');
        const treffer = page.locator('#authorResults');
        await expect(treffer).toContainText('ID: person_anonym', { timeout: 60000 });
        await treffer.getByRole('button', { name: 'Werke anzeigen' }).first().click();
        const details = page.locator('#works-person_anonym');
        await expect(details).toContainText('Als Bearbeiter (1)');
        await expect(details).toContainText('(BAX)');
    });

    test('Werke-Explorer: die Suche nach Konrad findet RHB und nennt alle Zuschreibungen', async ({ page }) => {
        await page.goto('/playground/#works&q=Konrad+von+W%C3%BCrzburg');
        await expect(page.locator('#workResults')).toContainText('Die Halbe Birne', { timeout: 60000 });
        await expect(page.locator('#workResults')).toContainText('Anonym; Konrad von Würzburg (umstritten)');
    });

    test('Anzeigetexte der drei Status und der Rolle', async ({ page }) => {
        await page.goto('/korpus.html');
        const texte = await page.evaluate(async () => {
            const m = await import('/assets/js/lib/attributions.js');
            const work = { attributions: [
                { name: 'A' },
                { name: 'B', status: 'disputed' },
                { name: 'C', status: 'uncertain' },
                { name: 'D', status: 'rejected' },
                { name: 'E', role: 'adapter' },
            ] };
            return {
                liste: m.formatAttributionList(work),
                bearbeiter: m.adapters(work).map(a => a.name),
                frueher: m.formerAttributions(work).map(a => a.name),
                rolle: m.ADAPTER_LABEL,
            };
        });
        expect(texte.liste).toBe('A; B (umstritten); C (unsicher zugeschrieben)');
        expect(texte.bearbeiter).toEqual(['E']);
        expect(texte.frueher).toEqual(['D']);
        expect(texte.rolle).toBe('Bearbeiter');
    });
});
