/**
 * Filter der Hilfe-Unterseite "Publikationen" (#417)
 *
 * Gehalten wird: der Zotero-Link steht oben (vor dem ersten Abschnitt), der
 * Kontakthinweis steht bei den eigenen Publikationen und nur dort, der Teamfilter
 * zählt gegen den Stand data/zotero-publikationen.json nach (unabhängig vom
 * Build-Skript, an zwei Personen, von denen Klaus M. Schmidt Namensvettern hat),
 * der Jahresfilter schneidet
 * richtig und lässt Einträge ohne Jahr fallen, Zurücksetzen stellt alles her, und
 * ohne JavaScript steht die ganze Liste da.
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const DATEN = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'data');
const stand = JSON.parse(readFileSync(join(DATEN, 'zotero-publikationen.json'), 'utf8'));
const EIGENE = stand.abschnitte.WB4HTUGC.eintraege;
const ERWAEHNENDE = stand.abschnitte.Z2N4SWWI.eintraege;
const ALLE = [...EIGENE, ...ERWAEHNENDE];

// Unabhängige, bewusst einfache Zählung: Nachname als Teilwort und Vorname als Wort derselben Person,
// nur in den Rollen, die die Autorenzeile zeigt (wie ROLLEN in build-publikationen.py)
const ROLLEN = ['author', 'editor', 'contributor'];
const person = (x, nach, vor) => x.personen.some(([n, v, typ]) => {
    if (!ROLLEN.includes(typ)) return false;
    const text = `${v} ${n}`.toLowerCase();
    return new RegExp(`\\b${nach}`).test(text) && new RegExp(`\\b${vor}\\b`).test(text);
});

const sichtbar = (page, id) => page.locator(`#${id} li[data-jahr]:not([hidden])`).count();

test.describe('Publikationen: Filter und Hinweise', () => {
    test('Zotero-Link steht oben, vor dem ersten Abschnitt', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        const link = page.locator('.pub-zotero a');
        await expect(link).toBeVisible();
        await expect(link).toHaveAttribute('href', stand.quelle);
        const yLink = (await link.boundingBox()).y;
        const yAbschnitt = (await page.locator('#wb4htugc h2').boundingBox()).y;
        expect(yLink).toBeLessThan(yAbschnitt);
    });

    test('Kontakthinweis mit mailto steht bei den eigenen Publikationen und nur dort', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        const hinweis = page.locator('#wb4htugc .pub-hinweis');
        await expect(hinweis).toBeVisible();
        await expect(hinweis).toContainText('Forschungszwecke');
        await expect(hinweis.locator('a')).toHaveAttribute('href', 'mailto:mhdbdb@plus.ac.at');
        await expect(page.locator('#z2n4swwi .pub-hinweis')).toHaveCount(0);
    });

    test('Teamfilter: Auswahl nennt nur Mitglieder mit Treffern, Zahlen stimmen mit dem Stand', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        await expect(page.locator('#pub-filter')).toBeVisible();

        const katharina = ALLE.filter((x) => person(x, 'zeppezauer', 'katharina')).length;
        const klaus = ALLE.filter((x) => person(x, 'schmidt', 'klaus')).length;
        const katharinaEigene = EIGENE.filter((x) => person(x, 'zeppezauer', 'katharina')).length;

        const optionen = await page.locator('#pub-team option').allTextContents();
        expect(optionen[0]).toBe('Alle');
        expect(optionen).toContain(`Katharina Zeppezauer-Wachauer (${katharina})`);
        expect(optionen).toContain(`Klaus M. Schmidt (${klaus})`);
        // Namensvettern zählen nicht: wer nur den Nachnamen Schmidt trägt, ist nicht Klaus M. Schmidt.
        // Die Erwartung kommt aus dem Stand, nicht aus festen Namen.
        const mitNachnameSchmidt = ALLE.filter((x) => x.personen.some(([n, , typ]) => ROLLEN.includes(typ) && /\bschmidt/i.test(n))).length;
        expect(klaus).toBeLessThanOrEqual(mitNachnameSchmidt);
        expect(optionen.length - 1).toBeGreaterThan(5);

        await page.selectOption('#pub-team', { label: `Katharina Zeppezauer-Wachauer (${katharina})` });
        expect(await sichtbar(page, 'wb4htugc')).toBe(katharinaEigene);
        expect(await sichtbar(page, 'z2n4swwi')).toBe(katharina - katharinaEigene);
        await expect(page.locator('#wb4htugc .pub-anzahl')).toHaveText(`${katharinaEigene} von ${EIGENE.length}`);
        await expect(page.locator('#pub-status')).toContainText(`${katharina} von ${ALLE.length} Einträgen`);
    });

    test('Jahresfilter schneidet richtig, Einträge ohne Jahr entfallen', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        const erwartet = (liste) => liste.filter((x) => x.jahr && x.jahr >= 2020 && x.jahr <= 2022).length;

        await page.fill('#pub-von', '2020');
        await page.fill('#pub-bis', '2022');
        expect(await sichtbar(page, 'wb4htugc')).toBe(erwartet(EIGENE));
        expect(await sichtbar(page, 'z2n4swwi')).toBe(erwartet(ERWAEHNENDE));

        // Nur Untergrenze: alles ab 2025, ohne die Einträge ohne Jahr
        await page.fill('#pub-bis', '');
        await page.fill('#pub-von', '2025');
        expect(await sichtbar(page, 'z2n4swwi')).toBe(ERWAEHNENDE.filter((x) => x.jahr >= 2025).length);

        // Kombination mit dem Team: beide Bedingungen gelten zugleich
        await page.selectOption('#pub-team', { value: 'contrib_003' });
        const katharina = (x) => person(x, 'zeppezauer', 'katharina');
        expect(await sichtbar(page, 'wb4htugc')).toBe(EIGENE.filter((x) => katharina(x) && x.jahr >= 2025).length);
    });

    test('ein Filter ohne Treffer sagt es, Zurücksetzen stellt die Liste her', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        await page.fill('#pub-von', '2100');
        await expect(page.locator('#wb4htugc .pub-leer')).toBeVisible();
        await expect(page.locator('#wb4htugc .pub-leer')).toContainText('Kein Eintrag');
        expect(await sichtbar(page, 'wb4htugc')).toBe(0);

        await page.click('#pub-zurueck');
        expect(await sichtbar(page, 'wb4htugc')).toBe(EIGENE.length);
        expect(await sichtbar(page, 'z2n4swwi')).toBe(ERWAEHNENDE.length);
        await expect(page.locator('#wb4htugc .pub-anzahl')).toHaveText(String(EIGENE.length));
        await expect(page.locator('#wb4htugc .pub-leer')).toBeHidden();
    });

    test('ohne JavaScript steht die ganze Liste da und das Formular bleibt verborgen', async ({ browser, baseURL }) => {
        const kontext = await browser.newContext({ javaScriptEnabled: false, baseURL });
        const seite = await kontext.newPage();
        await seite.goto('/hilfe-publikationen.html');
        await expect(seite.locator('#pub-filter')).toBeHidden();
        await expect(seite.locator('#wb4htugc li')).toHaveCount(EIGENE.length);
        await expect(seite.locator('#z2n4swwi li')).toHaveCount(ERWAEHNENDE.length);
        await kontext.close();
    });
});
