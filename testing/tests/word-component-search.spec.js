/**
 * Wortbestandteil-Suche im Lemmata-Explorer (#239)
 *
 * Eigener, benannter Modus für Komposita-Recherche, ausgelagert aus #169:
 * mit der Präfix-Regel in Stufe 3 (ADR-016, #224) entfällt die stille
 * Infix-Discovery der normalen Suche, die Funktion selbst ist philologisch
 * aber gewollt.
 *
 * Zwei Dinge, die diese Tests festhalten, weil sie nicht offensichtlich sind:
 *
 * 1. Die Eingabe „wein" findet Wein-Komposita nur über eine Brücke.
 *    normalizeMHG("wein") ist "wein", normalizeMHG("ôsterwîn") ist
 *    "osterwin". Gesucht wird deshalb zusätzlich mit der normalisierten Form
 *    des Lemmas, auf das die Variantenliste zeigt (wîn → "win").
 *
 * 2. `rôtwîn` aus dem Ticket-Beispiel steht NICHT im Lexikon (geprüft gegen
 *    data/authority-index.json.gz: kein Lemma normalisiert auf "rotwin",
 *    kein Varianten-Schlüssel). KZW hat in #239 am 29.07.2026 entschieden,
 *    das Beispiel zu ersetzen statt das Lemma nachzutragen; Leitbeispiel ist
 *    seither lantwîn (lemma_51889). Die Tests belegen die Anforderung an den
 *    vorhandenen Determinativkomposita ôsterwîn, ziperwîn und lantwîn.
 */

import { test, expect } from '@playwright/test';

const KOMPONENTEN_ROUTE = 'http://localhost:8080/playground/#lemmata&mode=component';

/** Wartet, bis der Authority-Index geladen und der Explorer verdrahtet ist. */
async function playgroundBereit(page) {
    await page.waitForFunction(
        () => window.playground?.authorityData?.lemmata?.length > 0 &&
              window.playground?.ui?.authorityExplorers !== undefined,
        { timeout: 60000 }
    );
}

/** Lemma-Beschriftungen einer Positionsgruppe, in Anzeigereihenfolge. */
function gruppe(page, key) {
    return page.evaluate((k) => {
        const el = document.getElementById(`component-group-${k}`);
        if (!el) return null;
        return {
            zugeklappt: el.classList.contains('hidden'),
            lemmata: [...el.querySelectorAll('.component-pick')].map(b => b.value)
        };
    }, key);
}

test.describe('#239: Wortbestandteil-Suche', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(`${KOMPONENTEN_ROUTE}&q=wein`);
        await playgroundBereit(page);
        await page.waitForSelector('#component-group-ende', { timeout: 30000 });
    });

    test('„wein" findet Wein-Komposita in der Gruppe am Wortende', async ({ page }) => {
        const ende = await gruppe(page, 'ende');

        expect(ende.zugeklappt).toBe(false);
        // Determinativkomposita zu wîn, die tatsächlich im Lexikon stehen.
        expect(ende.lemmata).toContain('ôsterwîn');
        expect(ende.lemmata).toContain('ziperwîn');
        expect(ende.lemmata).toContain('lantwîn');
    });

    test('die Normalisierungs-Brücke steht sichtbar im Kopf', async ({ page }) => {
        // Anforderung 4: ohne diesen Satz ist nicht nachvollziehbar, warum die
        // Eingabe „wein" das Lemma wîn und dessen Komposita findet.
        const kopf = page.locator('#lemmaResults');
        await expect(kopf).toContainText('Gesucht wird auf der normalisierten Form');
        await expect(kopf).toContainText('wîn');
        await expect(kopf).toContainText('Angezeigt werden die Originalformen');
    });

    test('gewinnen steht in der Wortmitte, und die Gruppe startet zugeklappt', async ({ page }) => {
        const mitte = await gruppe(page, 'mitte');

        expect(mitte.zugeklappt).toBe(true);
        expect(mitte.lemmata).toContain('gewinnen');

        // Die Gruppe ist zugeklappt, nicht leer: ihre Einträge sind im DOM.
        expect(mitte.lemmata.length).toBeGreaterThan(50);
        await expect(page.locator('#component-group-mitte')).toBeHidden();
    });

    test('winter landet am Wortanfang, nicht in der Wortmitte', async ({ page }) => {
        // Abweichung vom zweiten Akzeptanzkriterium in #239, das winter
        // zusammen mit gewinnen in der Wortmitten-Gruppe erwartet. „winter"
        // BEGINNT mit dem gesuchten Bestandteil „win", die Gruppen sind aber
        // positional definiert (Anforderung 3). Als Zufallstreffer bleibt es
        // trotzdem erkennbar, nur eben eine Gruppe weiter oben.
        const anfang = await gruppe(page, 'anfang');
        const mitte = await gruppe(page, 'mitte');

        expect(anfang.lemmata).toContain('winter');
        expect(mitte.lemmata).not.toContain('winter');
    });

    test('Auswahl wird gesammelt an die Multi-Lemma-Suche übergeben', async ({ page }) => {
        await page.locator('#component-group-ende .component-pick[value="ôsterwîn"]').check();
        await page.locator('#component-group-ende .component-pick[value="ziperwîn"]').check();
        await page.getByRole('button', { name: /Auswahl an die Multi-Lemma-Suche/ }).click();

        await expect(page).toHaveURL(/#multi-lemma&lemmata=/);
        const hash = decodeURIComponent(new URL(page.url()).hash);
        expect(hash).toContain('ôsterwîn');
        expect(hash).toContain('ziperwîn');
    });

    test('auch das Grundwort selbst ist ankreuzbar und übergebbar', async ({ page }) => {
        // Die Eingabe „wein" führt über die Variantenliste auf wîn. Wer
        // Komposita sammelt, will das Grundwort oft mitgeben (wîn + trinken);
        // ohne Checkbox im Kopf müsste man es drüben nachtippen.
        const exaktBox = page.locator('#lemmaResults .component-pick[value="wîn"]');
        await expect(exaktBox).toHaveCount(1);

        await exaktBox.check();
        await page.getByRole('button', { name: /Auswahl an die Multi-Lemma-Suche/ }).click();

        await expect(page).toHaveURL(/#multi-lemma&lemmata=/);
        expect(decodeURIComponent(new URL(page.url()).hash)).toContain('wîn');
    });

    test('ohne Auswahl navigiert der Übergabe-Knopf nicht weg', async ({ page }) => {
        await page.getByRole('button', { name: /Auswahl an die Multi-Lemma-Suche/ }).click();

        await expect(page.locator('#componentPickHint')).toContainText('mindestens ein Lemma');
        expect(page.url()).not.toContain('multi-lemma');
    });

    test('Mindestlänge von 3 Zeichen wird durchgesetzt', async ({ page }) => {
        await page.fill('#lemmaSearch', 'wi');

        await expect(page.locator('#lemmaResults')).toContainText('Mindestens 3 Zeichen');
        await expect(page.locator('#component-group-ende')).toHaveCount(0);
    });

    test('Umlaute umgehen die Mindestlänge nicht', async ({ page }) => {
        // normalizeMHG VERLÄNGERT: "wä" wird zu "wae" und wäre nach der
        // normalisierten Länge allein dreizeichig. Geprüft wird deshalb auch
        // die Rohlänge, sonst verspricht die UI drei Zeichen und lässt zwei zu.
        await page.fill('#lemmaSearch', 'wä');

        await expect(page.locator('#lemmaResults')).toContainText('Mindestens 3 Zeichen');
        await expect(page.locator('#component-group-ende')).toHaveCount(0);
    });

    test('der Fehlerhinweis kehrt nach dem nächsten Häkchen zurück', async ({ page }) => {
        const hinweis = page.locator('#componentPickHint');
        await expect(hinweis).toContainText('UND-verknüpft');

        await page.getByRole('button', { name: /Auswahl an die Multi-Lemma-Suche/ }).click();
        await expect(hinweis).toContainText('mindestens ein Lemma');

        await page.locator('#component-group-ende .component-pick').first().check();
        await expect(hinweis).toContainText('UND-verknüpft');
    });
});

test.describe('#239: Belegte Wortbildungen aus lemma.etymology', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(`${KOMPONENTEN_ROUTE}&q=wein`);
        await playgroundBereit(page);
        await page.waitForSelector('#component-group-ende', { timeout: 30000 });
    });

    test('kuratierte Wortbildungen sind markiert, Zufallstreffer nicht', async ({ page }) => {
        // ôsterwîn führt wîn (lemma_7532) als morphologische Komponente,
        // wiltswîn dagegen swîn, winter gar nichts. Genau die Trennung, die
        // der Zeichenvergleich nicht leisten kann.
        const markiert = await page.evaluate(() => {
            const karte = (wort) => [...document.querySelectorAll('.result-item')]
                .find(a => a.querySelector('.component-pick')?.value === wort);
            const hat = (wort) => {
                const k = karte(wort);
                return k ? k.textContent.includes('belegte Wortbildung') : null;
            };
            return { osterwin: hat('ôsterwîn'), wiltswin: hat('wiltswîn'), winter: hat('winter') };
        });

        expect(markiert.osterwin).toBe(true);
        expect(markiert.wiltswin).toBe(false);
        expect(markiert.winter).toBe(false);
    });

    test('der Filter reduziert auf die verzeichneten Bildungen', async ({ page }) => {
        const vorher = await gruppe(page, 'ende');
        expect(vorher.lemmata).toContain('wiltswîn');

        await page.locator('#componentOnlyMorph').check();
        await page.waitForFunction(
            () => !document.getElementById('component-group-ende')
                || ![...document.querySelectorAll('#component-group-ende .component-pick')]
                     .some(b => b.value === 'wiltswîn'),
            { timeout: 15000 }
        );

        const nachher = await gruppe(page, 'ende');
        expect(nachher.lemmata).toContain('ôsterwîn');
        expect(nachher.lemmata).not.toContain('wiltswîn');
        expect(nachher.lemmata.length).toBeLessThan(vorher.lemmata.length);

        // Die Wortanfang-Gruppe verliert die Zufallstreffer ebenfalls.
        const anfang = await gruppe(page, 'anfang');
        expect(anfang.lemmata).not.toContain('winter');
        expect(anfang.lemmata).toContain('wînrebe');
    });

    test('die Gesamtzahl im Kopf bleibt die ungefilterte', async ({ page }) => {
        const kopf = page.locator('#lemmaResults');
        const vorher = (await kopf.textContent()).match(/(\d+) Lemmata enthalten/)[1];

        await page.locator('#componentOnlyMorph').check();
        await expect(kopf).toContainText('als belegte Wortbildung angezeigt');

        // Die Antwort auf „wie viele enthalten den Bestandteil" ändert sich
        // durch einen Anzeigefilter nicht.
        const nachher = (await kopf.textContent()).match(/(\d+) Lemmata enthalten/)[1];
        expect(nachher).toBe(vorher);
    });

    test('der Filter behält Auswahl und aufgeklappte Gruppen', async ({ page }) => {
        await page.locator('#component-group-ende .component-pick[value="ôsterwîn"]').check();

        // Wortanfang von Hand zuklappen: der Zustand muss den Filter überleben.
        // (Die Wortmitten-Gruppe eignet sich dafür nicht, sie hat mit Filter
        // null Treffer und verschwindet ganz.)
        await page.locator('[aria-controls="component-group-anfang"]').click();
        await expect(page.locator('#component-group-anfang')).toBeHidden();

        await page.locator('#componentOnlyMorph').check();
        await expect(page.locator('#lemmaResults')).toContainText('als belegte Wortbildung angezeigt');

        // ôsterwîn überlebt den Filter (es IST eine belegte Wortbildung) und
        // muss sein Häkchen behalten, sonst ist die Auswahl stillschweigend weg.
        await expect(page.locator('#component-group-ende .component-pick[value="ôsterwîn"]'))
            .toBeChecked();
        await expect(page.locator('#component-group-anfang')).toBeHidden();
    });

    test('der Gruppenkopf trägt aria-expanded passend zum Zustand', async ({ page }) => {
        const ende = page.locator('[aria-controls="component-group-ende"]');
        const mitte = page.locator('[aria-controls="component-group-mitte"]');

        await expect(ende).toHaveAttribute('aria-expanded', 'true');
        await expect(mitte).toHaveAttribute('aria-expanded', 'false');

        await mitte.click();
        await expect(mitte).toHaveAttribute('aria-expanded', 'true');
        await expect(page.locator('#component-group-mitte')).toBeVisible();
    });
});

test.describe('#239: Modus-Umschaltung und Regression der normalen Lemmasuche', () => {
    test('der Umschalter wechselt zwischen beiden Modi und nimmt den Begriff mit', async ({ page }) => {
        await page.goto(`${KOMPONENTEN_ROUTE}&q=wein`);
        await playgroundBereit(page);
        await page.waitForSelector('#component-group-ende', { timeout: 30000 });

        await page.getByRole('button', { name: 'Lemma suchen' }).click();

        // Normale Lemmasuche: keine Positionsgruppen, Suchbegriff erhalten.
        await expect(page.locator('#component-group-ende')).toHaveCount(0);
        await expect(page.locator('#lemmaSearch')).toHaveValue('wein');
        await expect(page.locator('#lemmaResults')).toContainText('Treffer für "wein"');
    });

    test('die normale Lemmasuche arbeitet unverändert (ADR-016 unangetastet)', async ({ page }) => {
        // Regressionstest gegen Akzeptanzkriterium 4: der neue Modus darf die
        // reguläre Suche nicht anfassen. Sie ist unverändert substring-basiert
        // auf der normalisierten Form und kennt keine Gruppen.
        await page.goto('http://localhost:8080/playground/#lemmata&q=minne');
        await playgroundBereit(page);

        await expect(page.locator('#lemmaResults')).toContainText('Treffer für "minne"', { timeout: 30000 });
        await expect(page.locator('#component-group-ende')).toHaveCount(0);
        await expect(page.locator('#lemmaResults')).not.toContainText('Als Grundwort am Wortende');

        const treffer = await page.evaluate(() => {
            const ae = window.playground.ui.authorityExplorers;
            const N = window.playground.authorityData;
            // Dieselbe Menge, die searchLemmata() rendert: normalisierter
            // Substring-Test über alle Lemma-Labels.
            return {
                modus: ae.lemmaExplorer.searchMode,
                hatWortbestandteilMethode: typeof ae.searchWordComponents,
                lemmataGesamt: N.lemmata.length
            };
        });

        expect(treffer.modus).toBe('lemma');
        expect(treffer.hatWortbestandteilMethode).toBe('function');
        expect(treffer.lemmataGesamt).toBeGreaterThan(40000);
    });

    test('die Route ohne mode-Parameter öffnet weiterhin die normale Suche', async ({ page }) => {
        await page.goto('http://localhost:8080/playground/#lemmata');
        await playgroundBereit(page);

        const modus = await page.evaluate(
            () => window.playground.ui.authorityExplorers.lemmaExplorer.searchMode
        );
        expect(modus).toBe('lemma');
    });
});
