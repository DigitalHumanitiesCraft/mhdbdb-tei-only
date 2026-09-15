/**
 * Playground Corpus Loading Tests
 * Tests for auto-loading pre-built corpus into playground
 */

import { test, expect } from '@playwright/test';

test.describe('Playground Corpus Loading', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
    });

    test('playground shows loading state then file browser', async ({ page }) => {
        // Initially shows loading state
        const loadingState = page.locator('#corpusLoadingState');
        // It may already have loaded by the time we check — either state is fine
        const fileBrowser = page.locator('#fileBrowserSection');

        // Wait for file browser to appear (corpus auto-loads)
        await expect(fileBrowser).toBeVisible({ timeout: 60000 });
    });

    test('corpus loads successfully with 667 texts', async ({ page }) => {
        // Wait for auto-load to complete
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check included count shows 667
        const includedCount = await page.locator('#includedCount').textContent();
        expect(parseInt(includedCount)).toBe(667);
    });

    test('file list populated after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check file list has children
        const fileCount = await page.locator('#fileList > label').count();
        expect(fileCount).toBeGreaterThan(600);
    });

    test('playground features enabled after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Check that TEI explorers section is visible
        const teiSection = page.locator('#teiQueries');
        await expect(teiSection).toBeVisible();
    });

    test('can open multi-lemma search after corpus load', async ({ page }) => {
        // Wait for auto-load
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });

        // Open multi-lemma search modal
        const multiLemmaBtn = page.locator('#findMultiLemmaBtn');
        await expect(multiLemmaBtn).toBeVisible();
        await multiLemmaBtn.click();

        // Verify modal opened
        const modal = page.locator('#multiLemmaModal');
        await expect(modal).toBeVisible();
    });

});

/**
 * Issue #204: Die Korpusauswahl muss fuer die Analysen gelten, und der
 * Anzeigefilter darf nicht mit ihr verwechselt werden.
 *
 * Vorgeschichte: bis 09/2026 bekamen zehn der elf Werkzeuge immer alle Texte.
 * Gemessen am 15.09.: Kookkurrenz-Ranking fuer "minne" zeigte bei Auswahl
 * "nur CR" 7.161 Vorkommen (korpusweiter Wert), obwohl in CR 14 stehen.
 */
test.describe('Playground: Korpusauswahl wirkt (#204)', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/playground/');
        await page.waitForSelector('#fileBrowserSection', { state: 'visible', timeout: 60000 });
    });

    test('auswahlabhaengige Werkzeuge sehen nur die ausgewaehlten Texte', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();

        const scopes = await page.evaluate(() => {
            const ui = window.playground.ui;
            const namen = ['cooccurrenceRanking', 'wordFrequency', 'lemmaDistribution',
                'conceptDistribution', 'versePositionSearch', 'verseEndingProfile',
                'textStatistics'];
            return Object.fromEntries(namen.map(n => [n, ui[n].getCorpusTexts().length]));
        });

        for (const [werkzeug, anzahl] of Object.entries(scopes)) {
            expect(anzahl, `${werkzeug} muss der Auswahl folgen`).toBe(1);
        }
    });

    test('korpusweite Werkzeuge ignorieren die Auswahl bewusst', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();

        // Hapaxlegomena und Textvergleich bleiben korpusweit (KZW 15.09.):
        // "korpusweit einmalig" ist beim Hapax die Definition, und der
        // Vergleich waehlt seine zwei Texte selbst.
        const scopes = await page.evaluate(() => ({
            hapax: window.playground.ui.hapaxLegomena.getCorpusTexts().length,
            vergleich: window.playground.ui.textComparison.getCorpusTexts().length
        }));
        expect(scopes.hapax).toBeGreaterThan(600);
        expect(scopes.vergleich).toBeGreaterThan(600);
    });

    test('Kookkurrenz zaehlt im Einzeltext, nicht korpusweit', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();

        // Gegenprobe gegen den Korpusindex: so oft steht lemma_4130 in CR
        const erwartet = await page.evaluate(() =>
            window.playground.corpusData.texts.find(t => t.id === 'CR').lemmata['lemma_4130'].length
        );
        expect(erwartet).toBe(14);

        await page.locator('#showCooccurrenceRankingBtn').click();
        await page.waitForSelector('#coRkSearchBtn', { state: 'visible', timeout: 60000 });
        await page.fill('#coRkQuery', 'minne');
        await page.press('#coRkQuery', 'Escape'); // Autocomplete schliessen
        await page.click('#coRkSearchBtn');

        await expect(page.locator('#resultsContainer')).toContainText(`${erwartet} Vorkommen`, { timeout: 15000 });
        // Der korpusweite Wert darf gerade NICHT mehr dastehen
        await expect(page.locator('#resultsContainer')).not.toContainText('7.161 Vorkommen');
    });

    test('Kookkurrenz verwirft ein Ergebnis, das ueber eine andere Textmenge lief', async ({ page }) => {
        // Der Test oben verengt VOR der ersten Suche und kann diesen Fall
        // deshalb nicht treffen: das Werkzeug besitzt dort nie ein
        // korpusweites Ergebnis. Gemessen am 15.09.: nach korpusweitem "minne"
        // (7.161) und Verengung auf CR stand beim erneuten Oeffnen weiter
        // 7.161 statt 14, und zwar dauerhaft, nicht nur bis zum Neuoeffnen.
        await page.locator('#showCooccurrenceRankingBtn').click();
        await page.waitForSelector('#coRkSearchBtn', { state: 'visible', timeout: 60000 });
        await page.fill('#coRkQuery', 'minne');
        await page.press('#coRkQuery', 'Escape');
        await page.click('#coRkSearchBtn');
        await expect(page.locator('#resultsContainer')).toContainText('7.161 Vorkommen', { timeout: 30000 });

        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();
        await page.locator('#showCooccurrenceRankingBtn').click();

        await expect(page.locator('#resultsContainer')).not.toContainText('7.161 Vorkommen');
        expect(await page.evaluate(() => window.playground.ui.cooccurrenceRanking.state.result)).toBeNull();

        // Und neu gerechnet kommt der Wert des Einzeltexts heraus
        await page.fill('#coRkQuery', 'minne');
        await page.press('#coRkQuery', 'Escape');
        await page.click('#coRkSearchBtn');
        await expect(page.locator('#resultsContainer')).toContainText('14 Vorkommen', { timeout: 30000 });
    });

    test('ein Tausch gleicher Groesse wird auch erkannt', async ({ page }) => {
        // Eine Signatur ueber die Anzahl wuerde CR gegen WH nicht bemerken,
        // deshalb vergleicht scopeSignature() die IDs.
        const zustand = await page.evaluate(() => {
            const pg = window.playground;
            const cr = pg.ui.cooccurrenceRanking;
            const nur = (id) => {
                pg.corpusData.includedTexts.clear();
                pg.corpusData.includedTexts.add(id);
                pg.updateFileBrowserStats();
            };
            nur('CR');
            cr.show();
            cr.state.result = { totalOccurrences: 14, partners: [] };   // wie nach einer Suche
            nur('WH');
            cr.show();
            return cr.state.result;
        });
        expect(zustand).toBeNull();
    });

    test('Begriffs-Verteilung verwirft eine Verteilung aus anderer Textmenge', async ({ page }) => {
        const zustand = await page.evaluate(() => {
            const pg = window.playground;
            const cd = pg.ui.conceptDistribution;
            const alle = () => {
                pg.corpusData.includedTexts.clear();
                pg.corpusData.texts.forEach(t => pg.corpusData.includedTexts.add(t.id));
                pg.updateFileBrowserStats();
            };
            alle();
            cd.show();
            cd.state.distribution = [{ id: 'PZ', title: 'Parzival', count: 5 }];
            pg.corpusData.includedTexts.clear();
            pg.corpusData.includedTexts.add('CR');
            pg.updateFileBrowserStats();
            cd.show();
            return cd.state.distribution;
        });
        expect(zustand).toBeNull();
    });

    test('leere Auswahl meldet die Auswahl, nicht einen Ladezustand', async ({ page }) => {
        await page.locator('#selectNoneBtn').click();
        // Die Wortfrequenz sitzt im Block "Weitere Korpusanalysen", der seit
        // #410 zugeklappt startet.
        await page.locator('#moreAnalysesToggle').click();
        await page.locator('#showWordFrequencyBtn').click();

        const container = page.locator('#resultsContainer');
        await expect(container).toContainText('Kein Text ausgewählt');
        // Die alte Meldung waere hier eine Falschdiagnose: der Korpus IST geladen
        await expect(container).not.toContainText('Korpus ist noch nicht geladen');
    });

    test('Filter zeigt Hinweis, solange die Auswahl breiter ist', async ({ page }) => {
        const hinweis = page.locator('#filterSelectionMismatch');
        await expect(hinweis).toBeHidden();

        await page.locator('#fileFilter').fill('mori');
        await expect(hinweis).toBeVisible();
        await expect(hinweis).toContainText('nur die Anzeige dieser Liste');
        await expect(hinweis).toContainText('667 Texte');

        // One-Click-Korrektur: Auswahl folgt dem Filter, Hinweis erledigt sich
        await page.locator('#mismatchUseFiltered').click();
        await expect(hinweis).toBeHidden();
        await expect(page.locator('#includedCount')).toHaveText('1');
    });

    test('kein Hinweis, wenn der Filter die Auswahl nicht uebersteigt', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();
        await expect(page.locator('#filterSelectionMismatch')).toBeHidden();
    });

    test('Reim-Woerterbuch uebernimmt den Einzeltext in sein eigenes Feld', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();

        await page.locator('#showRhymeDictionaryBtn').click();
        // Sichtbar statt still: das Werkzeug bleibt korpusweit, traegt die
        // Auswahl aber in sein eigenes Filterfeld ein (chsteiner 15.09.).
        await expect(page.locator('#rdTextFilter')).toHaveValue('CR');
        expect(await page.evaluate(() =>
            window.playground.ui.rhymeDictionary.getCorpusTexts().length
        )).toBeGreaterThan(600);
    });

    test('Reim-Woerterbuch: exakte Sigle schlaegt Titel-Substring', async ({ page }) => {
        // Ohne diese Regel zieht die Vorbelegung "CR" (Moriz von Craûn) auch
        // Diu Crone (CRO) herein, weil deren Titel den Substring enthaelt:
        // ein ausgewaehlter Text, zwei gescannte. Gemessen am 15.09.
        await page.locator('#showRhymeDictionaryBtn').click();
        const treffer = await page.evaluate(() => {
            const rd = window.playground.ui.rhymeDictionary;
            const probe = (f) => {
                rd.state.textFilter = f;
                return rd.filterTexts(rd.getCorpusTexts()).map(t => t.id);
            };
            return {
                sigle: probe('CR'),
                substring: probe('Crone'),
                autor: probe('Hartmann').length
            };
        });
        expect(treffer.sigle).toEqual(['CR']);
        // Ohne Sigle-Treffer greift der Substring weiterhin
        expect(treffer.substring).toEqual(['CRO']);
        expect(treffer.autor).toBeGreaterThan(1);
    });

    /**
     * Die drei folgenden Faelle haben eine gemeinsame Wurzel: Werkzeug-Zustand,
     * der die Verengung des Korpus ueberlebt. Bis #204 konnte er das gefahrlos,
     * weil der Thunk immer alle Texte lieferte und jede gespeicherte Text-ID
     * darin vorkam. Alle drei am 15.09. im laufenden Playground gemessen.
     */
    test('Reim-Woerterbuch verwirft das Ergebnis, das ohne die Sigle gerechnet wurde', async ({ page }) => {
        // Ohne Verwerfen entsteht die Kopfzeile "Filter „CR" → 667 Texte":
        // die Filterangabe kommt aus dem neuen State, die Zahl aus dem alten
        // Ergebnis. Eine Aussage, die sich selbst widerspricht.
        await page.locator('#showRhymeDictionaryBtn').click();
        await page.fill('#rdQuery', 'minne');
        await page.press('#rdQuery', 'Escape');
        await page.click('#rdSearchBtn');
        await expect(page.locator('#resultsContainer')).toContainText('Vorkommen am Versende', { timeout: 60000 });

        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();
        await page.locator('#showRhymeDictionaryBtn').click();

        await expect(page.locator('#rdTextFilter')).toHaveValue('CR');
        expect(await page.evaluate(() => window.playground.ui.rhymeDictionary.state.result)).toBeNull();
        await expect(page.locator('#resultsContainer')).not.toContainText('667 Texte');
    });

    test('Wortfrequenz faellt auf die Auswahl zurueck, wenn ihr Scope-Text wegfaellt', async ({ page }) => {
        const zustand = await page.evaluate(async () => {
            const pg = window.playground;
            const wf = pg.ui.wordFrequency;
            wf.state.scope = 'CR';
            await wf.show();
            pg.corpusData.includedTexts.delete('CR');
            pg.updateFileBrowserStats();
            await wf.show();
            const sel = document.querySelector('#resultsContainer select');
            return {
                scope: wf.state.scope,
                dropdown: sel?.options[sel.selectedIndex]?.text,
                hatDaten: !!wf._lastFreqData
            };
        });
        // Vorher: scope blieb 'CR', Tabelle "Keine Daten", Dropdown "Gesamtkorpus"
        expect(zustand.scope).toBe('corpus');
        expect(zustand.hatDaten).toBe(true);
        expect(zustand.dropdown).toContain('Ausgewählte Texte');
    });

    test('Versendings-Profil faellt auch bei einem author-Scope zurueck', async ({ page }) => {
        // Zweiter Traeger desselben Fehlers: der Scope kann hier "author:X"
        // sein, und ein Autor faellt genauso aus der Auswahl wie ein Text.
        const zustand = await page.evaluate(async () => {
            const pg = window.playground;
            const vep = pg.ui.verseEndingProfile;
            const verstext = vep.verseTexts()[0];
            const autor = verstext.author || 'Unbekannt';
            vep.state.scope = `author:${autor}`;
            await vep.show();
            const vorher = vep.state.scope;

            // Alle Texte dieses Autors aus der Auswahl nehmen
            pg.corpusData.texts
                .filter(t => (t.author || 'Unbekannt') === autor)
                .forEach(t => pg.corpusData.includedTexts.delete(t.id));
            pg.updateFileBrowserStats();
            await vep.show();
            return { vorher, nachher: vep.state.scope, hatProfil: !!vep._lastProfile };
        });
        expect(zustand.vorher).toMatch(/^author:/);
        expect(zustand.nachher).toBe('corpus');
        expect(zustand.hatProfil).toBe(true);
    });

    test('Text-Statistiken zaehlen keine Haekchen mehr, die aus der Auswahl fielen', async ({ page }) => {
        const zustand = await page.evaluate(async () => {
            const pg = window.playground;
            const ts = pg.ui.textStatistics;
            await ts.show();
            ts.selected = new Set(['PZ', 'TR', 'CR']);
            ts.showSelectedOnly = true;
            pg.corpusData.includedTexts.clear();
            pg.corpusData.includedTexts.add('WH');
            pg.updateFileBrowserStats();
            await ts.show();
            return {
                selected: ts.selected.size,
                stats: ts._stats.length,
                text: document.getElementById('resultsContainer').textContent.replace(/\s+/g, ' ')
            };
        });
        // Vorher: "Ausgewählt: 3 / 1" neben "Keine Texte ausgewählt"
        expect(zustand.selected).toBe(0);
        expect(zustand.stats).toBe(1);
        expect(zustand.text).not.toContain('Ausgewählt: 3');
    });

    test('Reim-Woerterbuch folgt einem Wechsel auf einen anderen Einzeltext', async ({ page }) => {
        // Der Test darunter geht durch den LEEREN Zweig und hat diesen Fall
        // deshalb nicht getroffen: steht die eigene Vorbelegung noch im Feld,
        // ist textFilter nicht leer. Gemessen am 15.09.: Auswahl WH, Feld CR,
        // und filterTexts rechnete ueber CR.
        const verlauf = await page.evaluate(async () => {
            const pg = window.playground;
            const rd = pg.ui.rhymeDictionary;
            const nur = (id) => {
                pg.corpusData.includedTexts.clear();
                pg.corpusData.includedTexts.add(id);
                pg.updateFileBrowserStats();
            };
            nur('CR');
            rd.show();
            const nachCR = document.getElementById('rdTextFilter').value;
            nur('WH');
            rd.show();
            return {
                nachCR,
                nachWechsel: document.getElementById('rdTextFilter').value,
                gerechnetUeber: rd.filterTexts(rd.getCorpusTexts()).map(t => t.id)
            };
        });
        expect(verlauf.nachCR).toBe('CR');
        expect(verlauf.nachWechsel).toBe('WH');
        expect(verlauf.gerechnetUeber).toEqual(['WH']);
    });

    test('Reim-Woerterbuch folgt auch ueber eine breite Auswahl hinweg', async ({ page }) => {
        // Der Test darueber wechselt direkt zwischen zwei Einzelauswahlen. Der
        // haeufigere Weg fuehrt aber ueber "Alle", denn das ist der Zustand
        // nach jedem Laden. Solange dabei der Merker geloescht wurde, verlor
        // der Eintrag im Feld seinen Eigentuemer und blieb danach stehen:
        // gemessen am 15.09. Auswahl WH, Feld CR, gerechnet ueber CR.
        const verlauf = await page.evaluate(async () => {
            const pg = window.playground;
            const rd = pg.ui.rhymeDictionary;
            const nur = (id) => {
                pg.corpusData.includedTexts.clear();
                pg.corpusData.includedTexts.add(id);
                pg.updateFileBrowserStats();
            };
            const alle = () => {
                pg.corpusData.includedTexts.clear();
                pg.corpusData.texts.forEach(t => pg.corpusData.includedTexts.add(t.id));
                pg.updateFileBrowserStats();
            };
            nur('CR'); rd.show();
            alle(); rd.show();
            const beiAlle = document.getElementById('rdTextFilter').value;
            nur('WH'); rd.show();
            return {
                beiAlle,
                danach: document.getElementById('rdTextFilter').value,
                gerechnetUeber: rd.filterTexts(rd.getCorpusTexts()).map(t => t.id)
            };
        });
        // Bei breiter Auswahl bleibt der eigene Filter stehen, das ist gewollt
        expect(verlauf.beiAlle).toBe('CR');
        // Der Wechsel auf einen anderen Einzeltext muss trotzdem greifen
        expect(verlauf.danach).toBe('WH');
        expect(verlauf.gerechnetUeber).toEqual(['WH']);
    });

    test('Reim-Woerterbuch laesst eine getippte Eingabe in Ruhe', async ({ page }) => {
        // Gegenstueck zum Test darueber: ueberschrieben wird nur, was leer ist
        // oder von der Vorbelegung selbst stammt.
        const feld = await page.evaluate(async () => {
            const pg = window.playground;
            const rd = pg.ui.rhymeDictionary;
            rd.state.textFilter = 'Hartmann';
            rd._autoFilledSigle = null;
            pg.corpusData.includedTexts.clear();
            pg.corpusData.includedTexts.add('CR');
            pg.updateFileBrowserStats();
            rd.show();
            return document.getElementById('rdTextFilter').value;
        });
        expect(feld).toBe('Hartmann');
    });

    test('Reim-Woerterbuch respektiert ein bewusst geleertes Feld', async ({ page }) => {
        await page.locator('#fileFilter').fill('mori');
        await page.locator('#selectOnlyVisibleBtn').click();

        await page.locator('#showRhymeDictionaryBtn').click();
        await expect(page.locator('#rdTextFilter')).toHaveValue('CR');

        // Feld geleert und gesucht: state ist leer. Beim naechsten Oeffnen darf
        // die Vorbelegung nicht zurueckkommen, solange die Auswahl dieselbe ist.
        await page.evaluate(() => {
            const rd = window.playground.ui.rhymeDictionary;
            rd.state.textFilter = '';   // was runSearch() bei geleertem Feld setzt
            rd.show();
        });
        await expect(page.locator('#rdTextFilter')).toHaveValue('');

        // Wechsel auf einen ANDEREN Einzeltext belegt wieder vor
        const neueSigle = await page.evaluate(() => {
            const pg = window.playground;
            const andere = pg.corpusData.texts.find(t => t.id !== 'CR').id;
            pg.corpusData.includedTexts.clear();
            pg.corpusData.includedTexts.add(andere);
            pg.ui.rhymeDictionary.show();
            return { erwartet: andere, imFeld: document.getElementById('rdTextFilter').value };
        });
        expect(neueSigle.imFeld).toBe(neueSigle.erwartet);
    });

});
