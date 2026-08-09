/**
 * Reading View Tests
 * Tests for the TEI text reader panel in korpus.html
 *
 * Covers: URL param loading, metadata display, text rendering,
 * lemma highlighting, highlight navigation, multi-lemma colors, error handling
 *
 * Uses URL parameters to open reading view directly (skips search flow).
 * Issue #43 — Priority 2: reading view coverage
 */

import { test, expect } from '@playwright/test';

test.describe('Reading View', () => {

    // TEI file loading can take 30-90s on first fetch
    test.setTimeout(120000);

    test('should load reading view via URL params', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Reading title should populate after TEI loads
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Reading body should have content
        await expect(page.locator('#readingBody')).not.toBeEmpty();
    });

    test('should display metadata correctly', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Title and author should be populated
        const title = await page.locator('#readingTitle').textContent();
        expect(title.length).toBeGreaterThan(0);

        const author = await page.locator('#readingAuthor').textContent();
        expect(author.length).toBeGreaterThan(0);
    });

    test('should render formatted text content', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Reading body should have substantial text
        const bodyText = await page.locator('#readingBody').textContent();
        expect(bodyText.length).toBeGreaterThan(100);
    });

    test('should highlight lemma occurrences', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Highlighted words should exist in the reading body
        const highlightCount = await page.locator('#readingBody .highlight').count();
        expect(highlightCount).toBeGreaterThan(0);
    });

    test('should show highlight navigation with indicator', async ({ page }) => {
        // Use search flow to get a text with multiple highlights
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        await page.fill('#searchInput', 'got');
        await page.click('#searchButton');
        await page.waitForSelector('#resultsList > div', { timeout: 10000 });
        await page.locator('#resultsList > div').first().click();

        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Navigation should be visible when highlights exist
        await expect(page.locator('#readingNavigation')).toBeVisible({ timeout: 5000 });

        // Indicator shows "Treffer 1 von N"
        const indicator = await page.locator('#highlightIndicator').textContent();
        expect(indicator).toMatch(/Treffer 1 von \d+/);

        // Prev should be disabled at first highlight
        await expect(page.locator('#prevHighlight')).toBeDisabled();

        // Check if next is enabled (text has multiple occurrences)
        const nextDisabled = await page.locator('#nextHighlight').isDisabled();
        if (!nextDisabled) {
            await page.click('#nextHighlight');
            const updated = await page.locator('#highlightIndicator').textContent();
            expect(updated).toMatch(/Treffer 2 von \d+/);

            await page.click('#prevHighlight');
            const backToFirst = await page.locator('#highlightIndicator').textContent();
            expect(backToFirst).toMatch(/Treffer 1 von \d+/);
        }
    });

    test('should color-code multi-lemma highlights', async ({ page }) => {
        // HTR enthält beide Lemmata (brôt 56x, wîn 79x) — ABG enthielt wîn gar
        // nicht, daher konnte der alte Test nie 2 Farben sehen (Audit #110).
        await page.goto('http://localhost:8080/korpus.html?textId=HTR&lemmaIds=lemma_879,lemma_7532');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Multi-lemma highlights should exist
        const highlights = page.locator('#readingBody .highlight');
        const count = await highlights.count();
        expect(count).toBeGreaterThan(0);

        // Collect unique background colors from highlights
        const colors = await page.evaluate(() => {
            const marks = document.querySelectorAll('#readingBody .highlight');
            const bgColors = new Set();
            marks.forEach(m => {
                const bg = m.style.backgroundColor;
                if (bg) bgColors.add(bg);
            });
            return [...bgColors];
        });

        // Beide Lemmata kommen in HTR vor — es MUSS zwei Farben geben, sonst
        // ist die lemmaColorMap-Zuordnung kaputt (Audit #110).
        expect(colors.length).toBeGreaterThanOrEqual(2);
    });

    // === #17: TEI Structural Elements ===

    test('should render div type headers (song, chapter, recipe)', async ({ page }) => {
        // HZU has div type="number" headers
        await page.goto('http://localhost:8080/korpus.html?textId=HZU&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Should have div-type headers with German labels
        const headers = page.locator('#readingBody .tei-div-header');
        await expect(headers.first()).toBeVisible();
        const headerText = await headers.first().textContent();
        expect(headerText).toMatch(/Nr\.\s+\d+/);
    });

    test('should render stanza labels and verse line numbers', async ({ page }) => {
        // NBB (Nibelungenlied) has lg type="stanza" with l elements
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Stanza labels should exist
        const stanzaLabels = page.locator('#readingBody .stanza-label');
        await expect(stanzaLabels.first()).toBeVisible();
        const labelText = await stanzaLabels.first().textContent();
        expect(labelText).toMatch(/Strophe\s+\d+/);

        // Verse lines should have data-n attributes
        const verseLines = page.locator('#readingBody .verse-line[data-n]');
        const count = await verseLines.count();
        expect(count).toBeGreaterThan(0);
    });

    // === #127: visible verse-line numbering policy (.verse-line-numbered) ===
    // Policy: number the FIRST numeric line, then every line whose absolute @n is a
    // multiple of 5; non-numeric @n (e.g. h_* headers) is never numbered.

    test('#127: NBB (stanza-local @n) numbers only the first verse line', async ({ page }) => {
        // Nibelungenlied: @n resets per stanza (1..4) and never reaches a multiple of
        // 5, so only the very first numeric line carries a margin number.
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const numbered = await page.$$eval('#readingBody .verse-line-numbered',
            els => els.map(e => e.getAttribute('data-n')));
        expect(numbered).toEqual(['1']);
        // numeric guard: a numbered line always has a purely numeric @n (no h_* header)
        expect(numbered.every(n => /^\d+$/.test(n))).toBe(true);
    });

    test('#127: AGS (continuous @n) numbers the first line plus every 5th', async ({ page }) => {
        // Der altgewordene Sünder: continuous @n -> first line anchored + 5,10,15,...
        await page.goto('http://localhost:8080/korpus.html?textId=AGS&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const numbered = await page.$$eval('#readingBody .verse-line-numbered',
            els => els.map(e => parseInt(e.getAttribute('data-n'), 10)));
        expect(numbered.length).toBeGreaterThan(1);
        expect(numbered.slice(0, 4)).toEqual([1, 5, 10, 15]);
        // exactly one non-multiple-of-5 survives: the first-line anchor (@n=1)
        expect(numbered.filter(n => n % 5 !== 0)).toEqual([1]);
    });

    test('should render prose line numbers (lb)', async ({ page }) => {
        // ABG: 334 numerische Druckzeilen-Nummern + 5 technische h_-Zeilen
        // (Header-Zählung). Numerische @n rendern als sichtbare .lb-number;
        // h_-Zeilen als unsichtbarer .lb-anchor, der nur als Deep-Link-Ziel
        // (?verse=h_N) dient (#158/#162).
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Erste sichtbare Zeilennummer ist eine echte Druckzeilen-Zahl
        const lineNumbers = page.locator('#readingBody .lb-number');
        await expect(lineNumbers.first()).toBeVisible();
        const firstText = (await lineNumbers.first().textContent()).trim();
        expect(firstText).toMatch(/^\d+$/);

        // .lb-number enthält KEINE leeren h_-Spans mehr
        const emptyCount = await page.locator('#readingBody .lb-number:empty').count();
        expect(emptyCount).toBe(0);

        // h_-Zeilen existieren als unsichtbare Anker mit data-n (Deep-Links)
        const anchor = page.locator('#readingBody .lb-anchor[data-n="h_1"]');
        await expect(anchor).toHaveCount(1);
        expect(((await anchor.textContent()) || '').trim()).toBe('');
    });

    test('#138: Nach-oben-Button ist ohne geladenen Text unsichtbar', async ({ page }) => {
        // Prüft die BERECHNETE Sichtbarkeit, nicht die Klassenliste: .back-to-top
        // steht in korpus.css, das nach tailwind-output.css geladen wird. Ohne
        // die Regel `.back-to-top.hidden { display: none }` gewinnt display:flex
        // gegen Tailwinds .hidden, und der Button steht dauerhaft auf der Seite,
        // obwohl seine Klassenliste korrekt aussieht.
        await page.goto('http://localhost:8080/korpus.html');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        const btn = page.locator('#backToTop');
        await expect(btn).toHaveCount(1);
        await expect(btn).toBeHidden();

        // Auch weit unten auf der Seite bleibt er weg, solange kein Text offen ist.
        await page.mouse.wheel(0, 4000);
        await page.waitForTimeout(400);
        await expect(btn).toBeHidden();
    });

    test('#138: Nach-oben-Button erscheint mit Text und springt zum Panelkopf', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=HUG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Der Reader springt 600 ms nach dem Laden selbst zum ersten Treffer
        // (scrollToHighlight). Ohne dieses Warten überholt dieser Sprung den
        // Klick und der Test misst die falsche Position.
        await page.waitForTimeout(1500);

        const btn = page.locator('#backToTop');

        // Ganz nach oben: der Panelkopf ist im Blick, der Button muss weg sein.
        await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'auto' }));
        await page.mouse.wheel(0, 1);
        await page.mouse.wheel(0, -1);
        await page.waitForTimeout(300);
        await expect(btn).toBeHidden();

        // Weit nach unten in den Text: der Button muss erscheinen.
        await page.evaluate(() => window.scrollTo({ top: 3000, behavior: 'auto' }));
        await page.mouse.wheel(0, 1);
        await expect(btn).toBeVisible({ timeout: 5000 });

        await btn.click();
        await page.waitForTimeout(500);

        // Nach dem Sprung muss der Titel SICHTBAR sein, nicht bloß der Panelkopf
        // an Position 0: der Seiten-Header ist `sticky top-0` und rund 73 px
        // hoch, ein Sprung auf y=16 schöbe Titel und Metadaten darunter.
        const geometrie = await page.evaluate(() => {
            const header = document.querySelector('header');
            const titel = document.getElementById('readingTitle');
            return {
                headerUnterkante: Math.round(header.getBoundingClientRect().bottom),
                titelOberkante: Math.round(titel.getBoundingClientRect().top)
            };
        });
        expect(geometrie.titelOberkante).toBeGreaterThanOrEqual(geometrie.headerUnterkante);

        await expect(btn).toBeHidden();
    });

    test('#138: HUG (div-lokale @n) zeigt in jedem Lied wieder die 1', async ({ page }) => {
        // Julia, 17.07.: sichtbar setzte die Verszählung nur im ersten Lied bei 1
        // ein, danach erst bei 5. Ursache war ein dokumentweiter Anker; er wird
        // jetzt an jedem <div> zurückgesetzt, das seine Zählung bei n="1" neu
        // beginnt. Der #127-Fall (NBB, strophenlokale Zählung) darf davon NICHT
        // betroffen sein — dafür der Test oben.
        await page.goto('http://localhost:8080/korpus.html?textId=HUG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const songs = page.locator('#readingBody .tei-div-song[data-n]');
        const songCount = await songs.count();
        expect(songCount).toBeGreaterThan(2);

        // Die ersten drei Lieder müssen je eine sichtbare "1" tragen.
        for (let i = 0; i < 3; i++) {
            const firstNumbered = songs.nth(i).locator('.verse-line-numbered').first();
            await expect(firstNumbered).toHaveAttribute('data-n', '1');
        }
    });

    test('#138/#127: NLA (divs MIT strophenlokaler Zählung) bekommt keine Randeinsen', async ({ page }) => {
        // Der eigentliche Risikofall der #138-Änderung, nicht NBB: NBB hat gar
        // keine <div>, die Zusicherung dort ist strukturell trivial. NLA hat 38
        // untypisierte <div>, in denen jede Strophe wieder bei n="1" beginnt.
        //
        // Wogegen dieser Test schützt, ist präzise messbar: mit nur der ersten
        // Bedingung („erste numerische <l> trägt n=1") bekäme NLA 38 zusätzliche
        // Randeinsen, mit beiden Bedingungen 0. Gegengerechnet mit
        // `python scripts/audit/count-verse-numbering-resets.py --text NLA`.
        //
        // Wichtig zur Einordnung: gegen main ist der Test NICHT trennscharf, er
        // wäre auch dort grün (main setzt gar nichts zurück). Er sichert die
        // zweite Bedingung gegen ein späteres Vereinfachen ab, nicht das Feature
        // gegen den Vorzustand. Trennscharf ist der HUG-Test darüber.
        await page.goto('http://localhost:8080/korpus.html?textId=NLA&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Vorbedingung: der Text hat wirklich divs mit strophenlokaler Zählung.
        const divCount = await page.locator('#readingBody .tei-div').count();
        expect(divCount).toBeGreaterThan(10);

        // Höchstens der eine dokumentweite Anker darf eine sichtbare 1 tragen.
        const einsen = await page.locator('#readingBody .verse-line-numbered[data-n="1"]').count();
        expect(einsen).toBeLessThanOrEqual(1);
    });

    test('should render note date and year badges', async ({ page }) => {
        // HZU has note type="date" and note type="year"
        await page.goto('http://localhost:8080/korpus.html?textId=HZU&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Year badge
        const yearBadge = page.locator('#readingBody .note-year');
        await expect(yearBadge.first()).toBeVisible();
        const yearText = await yearBadge.first().textContent();
        expect(yearText).toMatch(/\d{4}/);

        // Date badge
        const dateBadge = page.locator('#readingBody .note-date');
        await expect(dateBadge.first()).toBeVisible();
    });

    test('should render hi rend compound values with token classes', async ({ page }) => {
        // IW (Iwein) has hi rend="initial" elements
        await page.goto('http://localhost:8080/korpus.html?textId=IW&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // hi-initial class should exist (token-based, not the old .initial)
        const initials = page.locator('#readingBody .hi-initial');
        const count = await initials.count();
        expect(count).toBeGreaterThan(0);
    });

    test('should render colophon with distinct styling', async ({ page }) => {
        // ALX has div type="colophon"
        await page.goto('http://localhost:8080/korpus.html?textId=ALX&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Colophon div should exist (use div[data-type] to avoid matching the header too)
        const colophon = page.locator('#readingBody div.tei-div[data-type="colophon"]');
        await expect(colophon).toBeVisible();

        // Should have italic styling
        const fontStyle = await colophon.evaluate(el => getComputedStyle(el).fontStyle);
        expect(fontStyle).toBe('italic');
    });

    test('should apply verse-context or prose-context class', async ({ page }) => {
        // NBB (verse) should get verse-context
        await page.goto('http://localhost:8080/korpus.html?textId=NBB&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        await expect(page.locator('#readingBody.verse-context')).toBeVisible();

        // ABG (prose) should get prose-context
        await page.goto('http://localhost:8080/korpus.html?textId=ABG&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });
        await expect(page.locator('#readingBody.prose-context')).toBeVisible();
    });

    test('should show error for missing text', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=NONEXISTENT_TEXT&lemmaIds=lemma_879');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });

        // Wait for error to appear in reading body
        await page.waitForTimeout(3000);

        // Reading body or error display should show an error message
        const bodyText = await page.locator('#readingBody').textContent();
        const hasError = bodyText.toLowerCase().includes('error') ||
                         bodyText.toLowerCase().includes('nicht gefunden') ||
                         bodyText.toLowerCase().includes('not found') ||
                         bodyText.includes('Text not found');
        expect(hasError).toBeTruthy();
    });

});

test.describe('Issue #134: Ausschnitts-Kontext (Excerpt)', () => {

    test.setTimeout(120000);

    test('AK zeigt Excerpt-Banner und Ausschnitt-Metadaten', async ({ page }) => {
        await page.goto('http://localhost:8080/korpus.html?textId=AK');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        // Banner sichtbar über dem Text, OHNE das Metadaten-Panel zu öffnen
        // (Akzeptanzkriterium: Ausschnittsbeziehung muss erkennbar sein)
        const banner = page.locator('.excerpt-banner');
        await expect(banner).toBeVisible();
        await expect(banner).toContainText('Buch von Akkon');
        await expect(banner).toContainText('44579–53866');

        // Metadaten-Panel: strukturierte Ausschnitt-Sektion (Issue-Tabelle)
        await page.click('.metadata-toggle-btn');
        const sections = page.locator('.metadata-sections');
        await expect(sections).toContainText('Ausschnitt');
        await expect(sections).toContainText('Gesamtwerk:');
        await expect(sections).toContainText('Versbereich:');
        await expect(sections).toContainText('Zerstörung Akkons');
    });

    test('analytic-Titel ohne Versbereich löst KEINEN Banner aus (ABG)', async ({ page }) => {
        // 534 Korpus-Header haben <analytic> für gewöhnliche
        // Editions-Angaben (Zeitschriftenartikel, Sammelband-Kapitel).
        // Excerpt-Signal ist ausschließlich biblScope unit="verse".
        await page.goto('http://localhost:8080/korpus.html?textId=ABG');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        await expect(page.locator('.excerpt-banner')).toHaveCount(0);
    });

    test('mehrere biblStructs ohne Versbereich lösen KEINEN Banner aus (FB)', async ({ page }) => {
        // FB trägt zwei biblStruct-Einträge (book + bookSection) — die
        // Excerpt-Erkennung durchsucht alle, findet aber ohne
        // biblScope unit="verse" keinen Ausschnitt (Review-Finding PR #178).
        await page.goto('http://localhost:8080/korpus.html?textId=FB');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        await expect(page.locator('.excerpt-banner')).toHaveCount(0);
    });

});

test.describe('Issue #250: Editorische Eingriffe im Metadatenpanel', () => {

    test.setTimeout(180000);

    test('ABS zeigt die Angaben aus editorialDecl, ohne das Repository-Boilerplate', async ({ page }) => {
        // ABS ist der kleinste Text mit inhaltlichen Angaben (3 Absätze nach
        // Filter, Zahlen aus scripts/audit/count-editorial-notes-and-div-heads.py).
        await page.goto('http://localhost:8080/korpus.html?textId=ABS');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        await page.click('.metadata-toggle-btn');
        const editorial = page.locator('.metadata-editorial');
        await expect(editorial).toBeVisible();
        await expect(editorial).toContainText('Editorische Eingriffe');
        await expect(editorial).toContainText('Der Text besteht aus 57 Rezepten');
        await expect(editorial).toContainText('nicht disambiguiert');
        await expect(page.locator('.metadata-editorial-note')).toHaveCount(3);

        // Das Boilerplate über lokale Dateireferenzen steht in 666 Headern und
        // ist eine Aussage über das Repository, nicht über den Text.
        await expect(page.locator('.metadata-sections')).not.toContainText('Lokale Dateireferenzen');
        // Die englische Parallelfassung ebenso nicht.
        await expect(page.locator('.metadata-sections')).not.toContainText('Local file references');
    });

    test('FR3 zeigt den Divergenz-Hinweis, der den Abschnitt ausgeloest hat', async ({ page }) => {
        // Der Anlassfall: FR3 hat die beiden Anhaenge der Edition vertauscht und
        // einen Verszaehlungsfehler korrigiert. Wer daraus zitiert, ohne das zu
        // wissen, zitiert falsch (#250, Punkt 1).
        await page.goto('http://localhost:8080/korpus.html?textId=FR3');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 120000 });

        await page.click('.metadata-toggle-btn');
        await expect(page.locator('.metadata-editorial')).toBeVisible();

        // Auf die Absätze selbst zusichern, nicht auf den Abschnitt: der
        // statische Einleitungssatz nennt die gedruckte Ausgabe ebenfalls. Er
        // enthält die Kette unten derzeit nicht („ist für Zitate die gedruckte
        // Ausgabe"), aber eine Umformulierung könnte sie hereinholen und die
        // Zusicherung erfüllen, obwohl gar keine Angabe gerendert wurde.
        const notes = page.locator('.metadata-editorial-note');
        await expect(notes.filter({ hasText: 'ist die gedruckte Ausgabe' })).toHaveCount(1);
        await expect(notes.filter({ hasText: 'Anhang II' })).toHaveCount(1);
    });

    test('KVO ohne inhaltliche Angaben zeigt den Abschnitt gar nicht', async ({ page }) => {
        // Gegenprobe: 3 Texte (CEFB, GWTK, KVO) tragen im editorialDecl nur das
        // Boilerplate. Ein leerer Abschnitt waere schlimmer als keiner.
        await page.goto('http://localhost:8080/korpus.html?textId=KVO');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        await page.click('.metadata-toggle-btn');
        await expect(page.locator('.metadata-sections')).toBeVisible();
        await expect(page.locator('.metadata-editorial')).toHaveCount(0);
    });

});

test.describe('Issue #250: Label ueber einer eigenen head-Ueberschrift', () => {

    test.setTimeout(180000);

    test('ABS: Rezeptnummer bleibt sichtbar und wird der Ueberschrift untergeordnet', async ({ page }) => {
        // Alle 57 recipe-divs in ABS tragen einen eigenen <head> ("basteten ."),
        // und keiner davon fuehrt die Nummer aus @n mit. Das Label ist damit die
        // einzige sichtbare Zaehlung und darf nicht verschwinden.
        await page.goto('http://localhost:8080/korpus.html?textId=ABS');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const firstRecipe = page.locator('#readingBody .tei-div[data-type="recipe"]').first();
        const label = firstRecipe.locator('> .tei-div-header');
        await expect(label).toBeVisible();
        await expect(label).toHaveText('Rezept 1');
        await expect(label).toHaveClass(/tei-div-header-above-head/);

        // Die Ueberschrift des Rezepts steht weiterhin als eigene h3 darunter.
        await expect(firstRecipe.locator('> h3.section-head')).toHaveCount(1);
    });

    test('MBS1: Label ohne eigene head-Ueberschrift bleibt unveraendert', async ({ page }) => {
        // Gegenprobe. MBS1 hat 4 recipe-divs, keines mit <head>: die neue Klasse
        // darf dort nicht auftauchen, sonst wuerde die Aenderung Abschnitte
        // umformatieren, die gar keine Doppelung haben.
        await page.goto('http://localhost:8080/korpus.html?textId=MBS1');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const labels = page.locator('#readingBody .tei-div[data-type="recipe"] > .tei-div-header');
        await expect(labels.first()).toBeVisible();
        await expect(labels.first()).not.toHaveClass(/tei-div-header-above-head/);
        await expect(page.locator('#readingBody .tei-div-header-above-head')).toHaveCount(0);
    });

    test('AC1: Kapitel mit eigener Ueberschrift hat nur noch eine h3', async ({ page }) => {
        // Der sichtbarste Fall der Doppelung: bei type="chapter" rendert der
        // Reader sein Label selbst als h3.section-head, der <head> ebenfalls.
        // Vorher standen dort zwei h3 untereinander ("Kapitel 1" / "das i capitel").
        await page.goto('http://localhost:8080/korpus.html?textId=AC1');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await expect(page.locator('#readingTitle')).not.toBeEmpty({ timeout: 90000 });

        const chapter = page.locator('#readingBody .tei-div[data-type="chapter"]').first();
        await expect(chapter.locator('> h3.section-head')).toHaveCount(1);
        const label = chapter.locator('> .tei-div-header');
        await expect(label).toHaveText('Kapitel 1');
        await expect(label).toHaveClass(/tei-div-header-above-head/);
    });

    test('WH: Dreissiger sind Kapitel-divs, keine Seitenmarker (#358)', async ({ page }) => {
        // Bis 2026-08-09 hingen alle 14.002 <l> in EINEM <p>, und die
        // Abschnittsnummer stand nur in den Wort-IDs plus als <pb n="77"/>.
        // Das <pb> war das falsche Element: 465 der 467 Abschnitte haben
        // exakt 30 Verse, das ist der Dreissiger und keine Handschriftenseite.
        await page.goto('http://localhost:8080/korpus.html?textId=WH&verseId=WH_7714');
        await page.waitForSelector('#loadingScreen', { state: 'hidden', timeout: 30000 });
        await page.waitForSelector('.verse-line', { state: 'visible', timeout: 90000 });

        await expect(page.locator('#readingBody .tei-div[data-type="chapter"]')).toHaveCount(467);
        // Die irrefuehrenden Seitenmarker [1]..[467] sind verschwunden
        await expect(page.locator('#readingBody .page-break')).toHaveCount(0);

        // Der Deep-Link aus #193 traegt weiter, und die Stelle ist jetzt
        // ohne Nachrechnen zitierfaehig: Wh. 77,14 steht unter "Kapitel 77".
        const ziel = page.locator('.verse-line[data-core="7714"]');
        await expect(ziel).toHaveCount(1);
        await expect(ziel).toHaveAttribute('data-n', '14');
        const kapitel = page.locator('#readingBody .tei-div[data-n="77"]');
        await expect(kapitel.locator('> h3.section-head')).toHaveText('Kapitel 77');
        await expect(kapitel.locator('.verse-line[data-core="7714"]')).toHaveCount(1);
    });

});
