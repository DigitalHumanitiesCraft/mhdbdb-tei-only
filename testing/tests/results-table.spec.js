// @ts-check
import { test, expect } from '@playwright/test';
import fs from 'fs';

test.describe('Issue #114: Tabellenansicht für Korpussuche', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        // 60000, nicht 30000: bis der arg-Platzhalter fehlte, war dieser Timeout
        // wirkungslos und real band das 60-s-Testbudget. Der Hook laedt Authority-
        // UND Korpus-Index und steht vor Tests, die selbst test.setTimeout(120000)
        // setzen; das greift aber erst im Testkoerper und kann den Hook nicht mehr
        // verlaengern. Die Signaturkorrektur soll hier nichts verschaerfen.
        await page.waitForFunction(() => !!window._mhdbdbApp?.searchEngine, null, { timeout: 60000 });
        // Default-View zurücksetzen, damit Tests reproduzierbar starten
        await page.evaluate(() => localStorage.removeItem('mhdbdb-results-view'));
    });

    test('Toggle UI ist sichtbar nach Suche', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await expect(page.locator('#viewToggleList')).toBeVisible();
        await expect(page.locator('#viewToggleTable')).toBeVisible();
    });

    test('Toggle Liste auf Tabelle wechselt das Rendering', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        // Initial: Listenansicht (Cards), keine Tabelle
        await expect(page.locator('#resultsList table')).toHaveCount(0);

        // Toggle auf Tabelle
        await page.click('#viewToggleTable');
        await expect(page.locator('#resultsList table')).toHaveCount(1);
        // 140 Treffer für "minne" — passe an, falls Korpus wächst
        await expect(page.locator('#resultsList table tbody tr')).toHaveCount(140);
    });

    test('localStorage persistiert View-Wahl über Reload', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');

        // Reload und erneut suchen
        await page.reload();
        await page.waitForFunction(() => !!window._mhdbdbApp?.searchEngine);
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        await expect(page.locator('#resultsList table')).toHaveCount(1);
    });

    test('Sortierung per Header-Klick funktioniert', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        // Default: matchCount desc; JT (612 Treffer) sollte oben sein
        const firstRowSigle = await page.locator('#resultsList tbody tr').first().locator('.font-mono').textContent();
        expect(firstRowSigle?.trim()).toMatch(/^JT$/);

        // Klick Titel-Header und prüfe absteigende Sortierung.
        // Sortierung im App-Code basiert NUR auf r.title (nicht auf textId);
        // die erste td enthält aber Sigle UND Titel als zwei Spans, daher
        // gezielt das zweite span (ohne .font-mono-Klasse) auslesen.
        await page.click('button[data-sort-col="title"]');
        const titlesAfterSort = await page.locator('#resultsList tbody tr td:first-child span:not(.font-mono)').allTextContents();
        const trimmed = titlesAfterSort.map(t => t.trim());
        const sortedDesc = [...trimmed].sort((a, b) => b.localeCompare(a, 'de'));
        expect(trimmed.slice(0, 5)).toEqual(sortedDesc.slice(0, 5));
    });

    test('Row-Klick öffnet Reader und wechselt auf Listen-Modus', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        await page.click('#resultsList tbody tr:first-child');

        // viewMode wechselt auf list
        await page.waitForFunction(() => window._mhdbdbApp.viewMode === 'list', null, { timeout: 5000 });
        const viewMode = await page.evaluate(() => window._mhdbdbApp.viewMode);
        expect(viewMode).toBe('list');

        // localStorage bleibt 'table' (Spec-Verhalten)
        const stored = await page.evaluate(() => localStorage.getItem('mhdbdb-results-view'));
        expect(stored).toBe('table');
    });

    test('CSV-Download wird angeboten', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        const downloadPromise = page.waitForEvent('download');
        await page.click('#resultsDownloadBtn');
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/^mhdbdb-suche-minne-\d{4}-\d{2}-\d{2}\.csv$/);
    });

    // --- Issue #114 Followups (Integrationswünsche aus der Prüfung) ---

    test('Gesamtzeile zeigt die Gesamttrefferzahl (tfoot)', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table tfoot');

        // tfoot-Summe muss der Summe der matchCounts entsprechen
        const expectedTotal = await page.evaluate(() =>
            window._mhdbdbApp.currentResults.reduce((s, r) => s + r.matchCount, 0)
        );
        const totalRowText = await page.locator('#resultsList table tfoot tr').textContent();
        const formatted = expectedTotal.toLocaleString('de-DE');
        expect(totalRowText).toContain('Gesamt');
        expect(totalRowText).toContain(formatted);

        // Gesamttrefferzahl steht auch im Results-Header (gilt auch für Listenansicht)
        const headerText = await page.locator('#resultsCount').textContent();
        expect(headerText).toContain(`${formatted} Treffer gesamt`);
    });

    test('Keyness-Spalte wird gerendert und ist sortierbar', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        await expect(page.locator('button[data-sort-col="keyness"]')).toBeVisible();

        // Jedes Result hat einen numerischen Keyness-Wert
        const keynessOk = await page.evaluate(() =>
            window._mhdbdbApp.currentResults.every(r => typeof r.keyness === 'number')
        );
        expect(keynessOk).toBe(true);

        // Sortierung nach Keyness: erster Wert ist das Maximum
        await page.click('button[data-sort-col="keyness"]');
        const sorted = await page.evaluate(() => {
            const values = window._mhdbdbApp.currentResults.map(r => r.keyness);
            return values.every((v, i) => i === 0 || values[i - 1] >= v);
        });
        expect(sorted).toBe(true);
    });

    test('Keyness-Referenz ist konsistent mit den Treffer-Zählungen (Paritäts-Check)', async ({ page }) => {
        // Bei Vollauswahl (Default) muss die korpusweite Referenzsumme aus
        // computeKeyness (via lemmaIndex) exakt der Summe der matchCounts über
        // alle Ergebnis-Texte entsprechen — beide zählen text.lemmata[id].length
        // (CONTRACTS §B Position-Counting-Parität).
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        const counts = await page.evaluate(() => {
            const app = window._mhdbdbApp;
            const idx = app.searchEngine.corpusIndex;
            const textById = new Map(idx.texts.map(t => [t.id, t]));
            let corpusMatches = 0;
            for (const lemmaId of app._keynessLemmaIds || []) {
                for (const textId of idx.lemmaIndex[lemmaId] || []) {
                    corpusMatches += textById.get(textId)?.lemmata?.[lemmaId]?.length || 0;
                }
            }
            const resultSum = app.currentResults.reduce((s, r) => s + r.matchCount, 0);
            return { corpusMatches, resultSum };
        });
        expect(counts.corpusMatches).toBeGreaterThan(0);
        expect(counts.resultSum).toBe(counts.corpusMatches);
    });

    test('Wörterbuchnetz-Links: javascript:-URLs gefiltert, Attribut-Breakout escapet', async ({ page }) => {
        // Stub der externen API: ein bösartiger javascript:-Link (muss vom
        // Shared Client gefiltert werden) + ein http(s)-Link mit Quote/Markup
        // im Wert (muss escapet in href landen, kein Attribut-Breakout).
        const evilHref = 'https://example.com/x?a="><img src=x onerror=alert(1)>';
        // mXSS-Payload für decodeHtmlEntities: beendet beim alten
        // textarea-innerHTML-Trick den RCDATA-Modus und erzeugte ein echtes
        // <img>, dessen onerror auch detached feuert (window.__pwned).
        const evilLemma = 'br&ocirc;t</textarea><img src=x onerror="window.__pwned=true">';
        await page.route('https://api.woerterbuchnetz.de/**', route => route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ result_set: [
                { sigle: 'MWB', lemma: 'minne', gram: 'stF', wbnetzid: 'X1', wbnetzlink: 'javascript:alert(1)' },
                { sigle: 'MWB', lemma: evilLemma, gram: 'stN', wbnetzid: 'X2', wbnetzlink: evilHref },
            ]}),
        }));

        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#lemmaTypes');

        const slot = page.locator('[data-wbnetz-links]').first();
        // 5 Wörterbücher (MWB, Lexer, LexerN, BMZ, FindeB) × 1 sicherer
        // Eintrag; javascript: gefiltert. Die Zahl ist bewusst hart: wer die
        // Wörterbuchliste ändert, soll hier vorbeikommen (#258).
        await expect(slot.locator('a')).toHaveCount(5, { timeout: 15000 });

        // Kein Breakout: der komplette bösartige Wert steht IM href-Attribut,
        // es wurde kein <img> in den DOM injiziert.
        const hrefs = await slot.locator('a').evaluateAll(as => as.map(a => a.getAttribute('href')));
        for (const href of hrefs) {
            expect(href).toBe(evilHref);
        }
        await expect(slot.locator('img')).toHaveCount(0);

        // decodeHtmlEntities darf beim Dekodieren keinen Code ausführen
        // (DOMParser statt textarea-Trick); Entities bleiben korrekt dekodiert.
        const pwned = await page.evaluate(() => window.__pwned);
        expect(pwned).toBeUndefined();
        await expect(slot).toContainText('brôt');
    });

    test('#258: fünf Wörterbücher, Sigle einmal pro Gruppe mit Volltitel, Duplikate entfernt', async ({ page }) => {
        // Stub: derselbe Deep-Link zweimal (FindeB liefert für Schreibdoubletten
        // dieselbe wbnetzid mehrfach) plus ein zweiter, echter Eintrag.
        const linkA = 'https://woerterbuchnetz.de/?sigle=X&lemid=A1';
        const linkB = 'https://woerterbuchnetz.de/?sigle=X&lemid=B1';
        const requested = [];
        await page.route('https://api.woerterbuchnetz.de/**', route => {
            requested.push(route.request().url());
            route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ result_set: [
                    { sigle: 'X', lemma: 'minne', gram: 'stF', wbnetzid: 'A1', wbnetzlink: linkA },
                    { sigle: 'X', lemma: 'Minne', gram: 'stF', wbnetzid: 'A1', wbnetzlink: linkA },
                    { sigle: 'X', lemma: 'minne', gram: 'swV', wbnetzid: 'B1', wbnetzlink: linkB },
                ]}),
            });
        });

        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#lemmaTypes');

        const slot = page.locator('[data-wbnetz-links]').first();
        // 5 Wörterbücher × 2 verbleibende Einträge — der doppelte Deep-Link
        // ist pro Wörterbuch einmal weg, nicht global (sonst wären es 2).
        await expect(slot.locator('a')).toHaveCount(10, { timeout: 15000 });

        // Eine Gruppe je Wörterbuch, Sigle nur einmal pro Gruppe
        const sigles = ['MWB', 'Lexer', 'LexerN', 'BMZ', 'FindeB'];
        await expect(slot.locator('[data-wbnetz-group]')).toHaveCount(5);
        for (const sigle of sigles) {
            await expect(slot.locator(`[data-wbnetz-group="${sigle}"]`)).toHaveCount(1);
        }

        // Alle fünf Sigel wurden auch wirklich angefragt
        const paths = requested.map(u => u.replace(/^.*\/dictionaries\//, '').split('/')[0]);
        expect([...new Set(paths)].sort()).toEqual([...sigles].sort());

        // Volltitel als title-Attribut an der Sigle (#258 Punkt 3): "FindeB"
        // ist ohne Auflösung unverständlich.
        const titles = await slot.locator('[title]').evaluateAll(els => els.map(e => e.getAttribute('title')));
        expect(titles).toContain('Findebuch zum mittelhochdeutschen Wortschatz');
        expect(titles).toContain('Benecke/Müller/Zarncke, Mittelhochdeutsches Wörterbuch');
        expect(titles).toContain('Lexer, Nachträge zum Mittelhochdeutschen Handwörterbuch');

        // Homographen desselben Wörterbuchs sind über die gram-Angabe
        // unterscheidbar, sonst stünden gleichlautende Links nebeneinander.
        const texts = await slot.locator('[data-wbnetz-group="BMZ"] a')
            .evaluateAll(as => as.map(a => a.textContent.replace(/\s+/g, ' ').trim()));
        expect(new Set(texts).size).toBe(texts.length);
    });

    test('Types (Schreibformen) werden im Lemma-Panel angeboten', async ({ page }) => {
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        await expect(page.locator('#lemmaTypes')).toBeVisible();
        const summary = page.locator('#lemmaTypes details summary').first();
        await expect(summary).toContainText(/\d+ Schreibformen \(Types, normalisiert\) anzeigen/);

        // Aufklappen zeigt Varianten-Chips
        await summary.click();
        const chipCount = await page.locator('#lemmaTypes details[open] span').count();
        expect(chipCount).toBeGreaterThan(0);
    });

    test('KWIC-Aufklappzeile: Detail-Row mit vollem colspan + Belege, Toggle schließt (#160)', async ({ page }) => {
        // Regressionsnetz für das Spaltenmodell: die Detail-Zeile muss die
        // GESAMTE Tabellenbreite überspannen (colspan == Anzahl thead-Spalten).
        // Vor #160 war der Wert hartcodiert ("7") und konnte bei Spalten-
        // Änderungen still auseinanderlaufen.
        test.setTimeout(120000);
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');
        await page.click('#viewToggleTable');
        await page.waitForSelector('#resultsList table');

        const headerCount = await page.locator('#resultsList table thead th').count();
        expect(headerCount).toBeGreaterThan(0);

        // Erste Zeile aufklappen
        const firstBtn = page.locator('[data-kwic-row]').first();
        await firstBtn.click();
        await expect(firstBtn).toHaveAttribute('aria-expanded', 'true');

        const detailRow = page.locator('#resultsList .kwic-detail-row');
        await expect(detailRow).toHaveCount(1);
        const colspan = await detailRow.locator('td').first().getAttribute('colspan');
        expect(parseInt(colspan, 10)).toBe(headerCount);

        // KWIC-Panel lädt echte Belege (TEI-Fetch, kann dauern)
        await expect(detailRow.locator('.kwic-list li').first()).toBeVisible({ timeout: 90000 });

        // Toggle schließt die Detail-Zeile wieder
        await firstBtn.click();
        await expect(page.locator('#resultsList .kwic-detail-row')).toHaveCount(0);
        await expect(firstBtn).toHaveAttribute('aria-expanded', 'false');
    });
});

test.describe('Issue #203: KWIC-Belege-Export', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/korpus.html');
        // 60000, nicht 30000: bis der arg-Platzhalter fehlte, war dieser Timeout
        // wirkungslos und real band das 60-s-Testbudget. Der Hook laedt Authority-
        // UND Korpus-Index und steht vor Tests, die selbst test.setTimeout(120000)
        // setzen; das greift aber erst im Testkoerper und kann den Hook nicht mehr
        // verlaengern. Die Signaturkorrektur soll hier nichts verschaerfen.
        await page.waitForFunction(() => !!window._mhdbdbApp?.searchEngine, null, { timeout: 60000 });
        await page.evaluate(() => localStorage.removeItem('mhdbdb-results-view'));
    });

    test('Belege (CSV) exportiert ALLE Fundstellen ohne Anzeige-Cap', async ({ page }) => {
        test.setTimeout(120000);
        await page.fill('#searchInput', 'minne');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > *');

        // Erstes KWIC-Panel in der Listenansicht öffnen (Top-Treffer JT, >100 Belege)
        const toggle = page.locator('[data-kwic-toggle]').first();
        await toggle.click();
        const panel = page.locator('[data-kwic-panel]').first();
        await expect(panel.locator('.kwic-list li').first()).toBeVisible({ timeout: 90000 });

        const [download] = await Promise.all([
            page.waitForEvent('download'),
            panel.locator('.kwic-export-btn').click()
        ]);

        expect(download.suggestedFilename()).toMatch(/^mhdbdb-belege-minne-.+-\d{4}-\d{2}-\d{2}\.csv$/);

        const csv = fs.readFileSync(await download.path(), 'utf-8');
        const lines = csv.trim().split(/\r\n/);
        expect(lines[0]).toContain('Vers/Zeile');
        expect(lines[0]).toContain('Kontext davor');
        expect(lines[0]).toContain('Keyword');
        expect(lines[0]).toContain('Kontext danach');
        // Anzeige capt bei 100 — der Export darf NICHT gecappt sein
        expect(lines.length - 1).toBeGreaterThan(100);
    });
});
