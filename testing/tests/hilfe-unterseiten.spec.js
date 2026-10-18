/**
 * Hilfe-Unterseiten "Publikationen" (#417) und "Demnächst im Korpus" (#537)
 *
 * Beide Seiten entstehen aus eingefrorenen Ständen unter data/ (scripts/
 * build-publikationen.py, scripts/build-demnaechst.py). Gehalten wird hier:
 * die Kacheln der Hilfeseite und der Fusslink fuehren hin, jeder Eintrag des
 * Standes steht auf der Seite (mit DOI oder Link, wo es einen gibt), die Seite
 * ruft zur Laufzeit weder Zotero noch GitHub auf, und auf "Demnächst" steht
 * nichts, was auf `wait:extern` wartet, und "Zeitpunkt offen" steht hinten.
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const DATEN = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'data');
const lesen = (name) => JSON.parse(readFileSync(join(DATEN, name), 'utf8'));

test.describe('Hilfe-Unterseite Publikationen', () => {
    const stand = lesen('zotero-publikationen.json');

    test('Kachel auf der Hilfeseite und Link im Seitenfuss fuehren hin', async ({ page }) => {
        await page.goto('/hilfe.html');
        await page.locator('a[href="hilfe-publikationen.html"]').first().click();
        await expect(page).toHaveURL(/hilfe-publikationen\.html$/);
        await expect(page.locator('h1')).toHaveText('Publikationen');

        await page.goto('/hilfe.html');
        await page.locator('footer a[href="hilfe-publikationen.html"]').click();
        await expect(page).toHaveURL(/hilfe-publikationen\.html$/);
    });

    test('jeder Eintrag des Standes steht auf der Seite, mit DOI oder Link', async ({ page }) => {
        const anfragen = [];
        page.on('request', (r) => anfragen.push(r.url()));
        await page.goto('/hilfe-publikationen.html');

        for (const [sammlung, abschnitt] of Object.entries(stand.abschnitte)) {
            const liste = page.locator(`#${sammlung.toLowerCase()} li`);
            await expect(liste, sammlung).toHaveCount(abschnitt.eintraege.length);
            // Das DOI-Feld ist Freitext: nur eine echte DOI oder eine Web-Adresse gibt einen Link
            const mitLink = abschnitt.eintraege.filter((x) => {
                const doi = x.doi.replace(/^(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:\s*)/i, '').trim();
                return /^10\.\d{4,9}\/\S+$/.test(doi) || /^https?:\/\/\S+$/i.test(x.doi) || /^https?:\/\/\S+$/i.test(x.url);
            }).length;
            await expect(page.locator(`#${sammlung.toLowerCase()} li a`), sammlung).toHaveCount(mitLink);
        }

        // Kein Link ist relativ, und keiner traegt doi.org doppelt
        const hrefs = await page.locator('.pub-liste a').evaluateAll((as) => as.map((a) => a.getAttribute('href')));
        expect(hrefs.filter((h) => !/^https?:\/\//.test(h))).toEqual([]);
        expect(hrefs.filter((h) => /doi\.org\/https?:/.test(h))).toEqual([]);

        // Ein DOI-Eintrag fuehrt auf doi.org, nicht auf die Zotero-Bibliothek
        const mitDoi = stand.abschnitte.WB4HTUGC.eintraege.find((x) => /^10\.\d{4,9}\/\S+$/.test(x.doi));
        await expect(page.locator(`a[href="https://doi.org/${mitDoi.doi}"]`).first()).toBeVisible();

        expect(anfragen.filter((u) => /zotero\.org\/(groups|api)|api\.zotero/.test(u))).toEqual([]);
    });

    test('Eintraege stehen neueste zuerst, ohne Jahr am Ende', async ({ page }) => {
        await page.goto('/hilfe-publikationen.html');
        for (const sammlung of Object.keys(stand.abschnitte)) {
            const meta = await page.locator(`#${sammlung.toLowerCase()} .pub-meta`).allTextContents();
            const jahre = meta.map((t) => {
                const m = t.match(/\b(1[5-9]\d\d|20\d\d)\b/);
                return m ? Number(m[1]) : 0;
            });
            const sortiert = [...jahre].sort((a, b) => b - a);
            expect(jahre, sammlung).toEqual(sortiert);
        }
    });
});

test.describe('Hilfe-Unterseite Demnächst im Korpus', () => {
    const issues = lesen('demnaechst-issues.json').issues;
    const plan = lesen('demnaechst-zeitplan.json');

    // Dieselbe Regel wie scripts/build-demnaechst.py, hier aus den Dateien nachgerechnet
    const sichtbar = issues.filter((i) => !(String(i.nummer) in plan.ausgeschlossen) && !i.labels.includes('wait:extern'));

    test('Kachel auf der Hilfeseite fuehrt hin', async ({ page }) => {
        await page.goto('/hilfe.html');
        await page.locator('a[href="hilfe-demnaechst.html"]').click();
        await expect(page).toHaveURL(/hilfe-demnaechst\.html$/);
        await expect(page.locator('h1')).toHaveText('Demnächst im Korpus');
    });

    test('es stehen genau die Issues da, die die Regel durchlaesst, und kein wait:extern', async ({ page }) => {
        const anfragen = [];
        page.on('request', (r) => anfragen.push(r.url()));
        await page.goto('/hilfe-demnaechst.html');

        await expect(page.locator('.pub-liste > li')).toHaveCount(sichtbar.length);
        expect(sichtbar.length).toBeGreaterThan(0);

        // Der Kontrollwert liegt ausserhalb der Regel: ein Issue, das wartet, darf nicht erscheinen
        // und jedes, das die Zeitplan-Datei ausschliesst (etwa weil die Rechtefrage offen ist, #537)
        const wartend = issues.filter((i) => i.labels.includes('wait:extern') || String(i.nummer) in plan.ausgeschlossen);
        expect(wartend.length).toBeGreaterThan(2);
        const text = await page.locator('main').innerText();
        for (const i of wartend) {
            expect(text, `#${i.nummer}`).not.toContain(i.titel);
        }

        expect(anfragen.filter((u) => /api\.github\.com/.test(u))).toEqual([]);
    });

    test('Zeitpunkt offen steht hinten, die Quartale davor aufsteigend, und die Schaetzung ist gesagt', async ({ page }) => {
        await page.goto('/hilfe-demnaechst.html');
        const zeiten = await page.locator('.pub-liste .pub-meta').allTextContents();
        const rang = (t) => {
            const m = t.match(/^(\d)\. Quartal (\d{4})$/);
            return m ? Number(m[2]) * 10 + Number(m[1]) : Infinity;
        };
        const raenge = zeiten.map(rang);
        expect(raenge).toEqual([...raenge].sort((a, b) => a - b));
        expect(zeiten.some((t) => t === 'Zeitpunkt offen')).toBe(true);
        await expect(page.locator('main')).toContainText('Zeitangaben sind Schätzungen');
    });
});
