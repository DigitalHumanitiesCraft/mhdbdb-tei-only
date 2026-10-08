/**
 * IDs in den Suchfeldern des Playgrounds (#545)
 *
 * Die Begriffshilfe (#498) nennt Begriffe mit ihrer ID; Alan fand
 * concept_12040000 im Begriffe-Explorer nicht. Seit #545 nehmen die sechs
 * Register und die Begriffs-Verteilung eine ID an, voll oder als blosse
 * Nummer (assets/js/lib/authority-id-input.js). Die Beispiel-IDs stammen aus
 * data/authority-index.json.gz, gemessen am 2026-10-08.
 */

import { test, expect } from '@playwright/test';

const FAELLE = [
    { view: 'concepts', results: '#conceptResults', q: '12040000', id: 'concept_12040000', text: 'Mineralien' },
    { view: 'concepts', results: '#conceptResults', q: 'concept_12040000', id: 'concept_12040000', text: 'Mineralien' },
    { view: 'authors', results: '#authorResults', q: 'person_1768', id: 'person_1768', text: 'Karl IV.' },
    { view: 'works', results: '#workResults', q: '350', id: 'work_350', text: 'Aalener Stadtratsgedicht' },
    { view: 'names', results: '#nameResults', q: '#name_40000000', id: 'name_40000000', text: 'Namen' },
    // Gattungs-IDs sind Hexfolgen; diese beginnt mit einer Null, die nicht wegfallen darf
    { view: 'genres', results: '#genreResults', q: '06677194', id: 'genre_06677194', text: 'ID: genre_06677194' },
    { view: 'lemmata', results: '#lemmaResults', q: 'lexicon.xml#lemma_1', id: 'lemma_1', text: 'ID: lemma_1' },
];

test.describe('ID-Suche in den Registern (#545)', () => {
    for (const f of FAELLE) {
        test(`${f.view}: "${f.q}" findet ${f.id}`, async ({ page }) => {
            await page.goto(`/playground/#${f.view}&q=${encodeURIComponent(f.q)}`);
            const treffer = page.locator(f.results);
            await expect(treffer).toContainText(`ID: ${f.id}`, { timeout: 60000 });
            await expect(treffer).toContainText(f.text);
        });
    }

    test('ein fremdes Praefix ist keine ID dieses Registers', async ({ page }) => {
        await page.goto(`/playground/#concepts&q=${encodeURIComponent('person_1768')}`);
        await expect(page.locator('#conceptResults')).toContainText('Keine Begriffe gefunden', { timeout: 60000 });
    });

    test('die Textsuche findet weiter, was sie vorher fand', async ({ page }) => {
        await page.goto('/playground/#works&q=ASG');
        await expect(page.locator('#workResults')).toContainText('ID: work_350', { timeout: 60000 });
    });

    test('Begriffs-Verteilung schlaegt den Begriff zur blossen Nummer vor', async ({ page }) => {
        await page.goto('/playground/#concept-distribution');
        await page.waitForSelector('#cdQuery', { state: 'visible', timeout: 60000 });
        await page.fill('#cdQuery', '12040000');
        await expect(page.locator('#cdAutocomplete')).toContainText('Mineralien', { timeout: 15000 });
    });

    // Der Klick auf ein Lemma im Begriffe-Explorer oeffnet es ueber seine ID.
    // Ueber die Schreibform stand "vels" zwischen velsen, velseht usw.
    test('Lemma-Klick im Begriffe-Explorer zeigt genau dieses Lemma', async ({ page }) => {
        await page.goto('/playground/#concepts&q=concept_12040000');
        const treffer = page.locator('#conceptResults');
        await expect(treffer).toContainText('ID: concept_12040000', { timeout: 60000 });
        await treffer.getByRole('button', { name: 'Lemmata anzeigen' }).first().click();
        await page.fill('#lemmas-concept_12040000-search', 'vels');
        const link = page.locator('a[title="Details im Lemma-Explorer anzeigen"]')
            .filter({ has: page.locator('span', { hasText: /^vels$/ }) });
        await link.first().click();

        await expect(page.locator('#lemmaSearch')).toHaveValue(/^lemma_\d+$/, { timeout: 15000 });
        const ergebnis = page.locator('#lemmaResults');
        await expect(ergebnis).toContainText('vels');
        await expect(ergebnis.getByText(/ID: lemma_\d+/)).toHaveCount(1);
    });
});
