/**
 * Unterseite Textreihentypologie (#93)
 *
 * Haelt fest: alle Seiten sind vom Start aus erreichbar (keine verwaiste Datei),
 * jeder interne Link, jedes Bild, jeder Anker und jeder Download loest auf, der
 * SKOS-Browser zeigt eine Kategorie mit mehreren direkten Eltern unter allen
 * Eltern, die Suche und der Direktlink funktionieren, und nichts ruft die
 * (nicht mehr erreichbare) Domain dhplus.sbg.ac.at auf.
 */

import { test, expect } from '@playwright/test';
import { readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SEITEN_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'textreihen');
const BESCHWOERUNG = 'c_624b0297'; // zwoelf direkte Eltern in der SKOS-Quelle

function internalRefs(html) {
    const refs = [];
    const re = /\b(?:href|src)="([^"]*)"/g;
    let m;
    while ((m = re.exec(html))) {
        const v = m[1].replace(/&amp;/g, '&');
        if (/^(https?:|mailto:|javascript:|data:|\/\/)/.test(v)) continue;
        refs.push(v);
    }
    return refs;
}

function ids(html) {
    const out = new Set();
    const re = /\b(?:id|name)="([^"]+)"/g;
    let m;
    while ((m = re.exec(html))) out.add(m[1]);
    return out;
}

test.describe('Textreihentypologie: Seiten, Links, Downloads', () => {

    test('jede Seite ist vom Start aus erreichbar, und jeder interne Link, jedes Bild und jeder Anker loest auf', async ({ request }) => {
        const dateien = readdirSync(SEITEN_DIR).filter((f) => f.endsWith('.html')).sort();
        expect(dateien.length).toBe(11);

        const seiten = new Map(); // Dateiname -> html
        const queue = ['index.html'];
        const probleme = [];
        const geprueft = new Set();
        while (queue.length) {
            const f = queue.shift();
            if (seiten.has(f)) continue;
            const res = await request.get(`/textreihen/${f}`);
            expect(res.status(), f).toBe(200);
            seiten.set(f, await res.text());
            for (const ref of internalRefs(seiten.get(f))) {
                const [pfad] = ref.split('#');
                if (pfad.endsWith('.html') && !pfad.startsWith('../') && !pfad.startsWith('/')) queue.push(pfad);
            }
        }
        expect([...seiten.keys()].sort()).toEqual(dateien);

        for (const [f, html] of seiten) {
            for (const ref of internalRefs(html)) {
                const [pfad, anker] = ref.split('#');
                const ziel = pfad === '' ? f : pfad;
                const url = new URL(ziel, `http://x/textreihen/${f}`);
                const schluessel = url.pathname + (anker ? '#' + anker : '');
                if (geprueft.has(f + '|' + schluessel)) continue;
                geprueft.add(f + '|' + schluessel);
                if (ref === '#' || ref === '') continue;
                if (pfad.startsWith('../') || pfad.startsWith('/')) {
                    // Nachbarseiten der Site (Playground, Impressum, ...) nur auf Erreichbarkeit
                    const r = await request.get(url.pathname);
                    if (r.status() !== 200) probleme.push(`${f}: ${ref} -> ${r.status()}`);
                    continue;
                }
                if (anker) {
                    const zielHtml = seiten.get(ziel);
                    // Anker, die erst der Browser-JS erzeugt (c_...), sind Direktlinks auf browser.html und werden dort getestet
                    if (ziel === 'browser.html' && /^c_[0-9a-f]{8}$/.test(anker)) continue;
                    if (!zielHtml || !ids(zielHtml).has(anker)) probleme.push(`${f}: Anker ${ref} fehlt`);
                }
                if (!pfad.endsWith('.html') && pfad !== '') {
                    const r = await request.get(url.pathname);
                    if (r.status() !== 200) probleme.push(`${f}: ${ref} -> ${r.status()}`);
                    else if (/\.(png|jpe?g|ttl|rdf|rj|json|md)$/.test(pfad)) {
                        const len = (await r.body()).length;
                        if (len < 1000) probleme.push(`${f}: ${ref} nur ${len} Bytes`);
                    }
                }
            }
        }
        expect(probleme).toEqual([]);
    });

    test('Download-Seite: alle Downloads liegen vor, die Quelldateien sind der Commit 86c233f08', async ({ request, page }) => {
        await page.goto('/textreihen/download.html');
        const links = await page.locator('a[download]').evaluateAll((els) => els.map((e) => e.getAttribute('href')));
        expect(links.length).toBe(5);
        for (const href of links) {
            const r = await request.get(`/textreihen/${href}`);
            expect(r.status(), href).toBe(200);
            expect((await r.body()).length, href).toBeGreaterThan(5000);
        }
        const ttl = await (await request.get('/textreihen/data/skos/MHDBDB-Textreihentypologie.ttl')).text();
        expect((ttl.match(/a skos:Concept\b/g) || []).length).toBe(618);
        await expect(page.locator('main')).toContainText('86c233f08');
        await expect(page.locator('main')).toContainText('CC BY 4.0');
    });

    test('Footer-Link und Hilfe-Kachel fuehren zur Unterseite', async ({ page }) => {
        await page.goto('/index.html');
        const footerLink = page.locator('footer a[href$="textreihen/index.html"]');
        await expect(footerLink).toHaveCount(1);
        await footerLink.click();
        await expect(page).toHaveURL(/\/textreihen\/index\.html$/);
        await expect(page.locator('h1')).toHaveText('MHDBDB-Textreihentypologie');

        await page.goto('/hilfe.html');
        await expect(page.locator('main a[href="textreihen/index.html"]')).toHaveCount(1);
        // kein neuer Menuepunkt
        await expect(page.locator('header a[href*="textreihen"]')).toHaveCount(0);
    });
});

test.describe('Textreihentypologie: SKOS-Browser', () => {

    test('Wurzeln, Zaehlung und keine Anfrage an dhplus.sbg.ac.at', async ({ page }) => {
        const anfragen = [];
        page.on('request', (r) => anfragen.push(r.url()));
        await page.goto('/textreihen/browser.html');
        await expect(page.locator('html[data-tr-ready="1"]')).toBeAttached();
        await expect(page.locator('#trMeta')).toContainText('618 Kategorien');
        await expect(page.locator('#trMeta')).toContainText('3 oberste Kategorien');
        await expect(page.locator('#trMeta')).toContainText('193 Kategorien mit mehreren direkten Eltern');
        await expect(page.locator('#trTree > li')).toHaveCount(3);
        expect(anfragen.filter((u) => u.includes('dhplus.sbg.ac.at'))).toEqual([]);
        // die historische URI erscheint nur als Text, nie als Link
        await page.goto(`/textreihen/browser.html#${BESCHWOERUNG}`);
        await expect(page.locator('#trDetail .tr-uri')).toContainText('https://dhplus.sbg.ac.at/mhdbdb/instance/' + BESCHWOERUNG);
        await expect(page.locator('a[href*="dhplus.sbg.ac.at"]')).toHaveCount(0);
    });

    test('Kategorie mit mehreren direkten Eltern steht unter allen Eltern', async ({ page, request }) => {
        const daten = await (await request.get('/textreihen/data/textreihen.json')).json();
        const eltern = daten.concepts[BESCHWOERUNG].p;
        expect(eltern.length).toBe(12);

        await page.goto(`/textreihen/browser.html#${BESCHWOERUNG}`);
        await expect(page.locator('#trDetail .tr-detail-title')).toHaveText('Beschwörung');
        await expect(page.locator('#trDetail .tr-linklist').first().locator('button')).toHaveCount(12);

        const vorkommen = await page.locator(`#trTree li[data-id="${BESCHWOERUNG}"]`).evaluateAll((els) =>
            els.map((e) => e.parentElement.closest('li').getAttribute('data-id')));
        expect(new Set(vorkommen)).toEqual(new Set(eltern));
        // jedes Vorkommen ist ausgewaehlt markiert
        await expect(page.locator(`#trTree li[data-id="${BESCHWOERUNG}"] > .tr-row.is-selected`)).toHaveCount(vorkommen.length);
        // und traegt die Markierung "12 Eltern"
        await expect(page.locator(`#trTree li[data-id="${BESCHWOERUNG}"] > .tr-row .tr-badge-multi`).first()).toHaveText('12 Eltern');
    });

    test('Suche findet Kategorien und fuehrt in den Baum', async ({ page }) => {
        await page.goto('/textreihen/browser.html');
        await expect(page.locator('html[data-tr-ready="1"]')).toBeAttached();
        await page.fill('#trSearch', 'beschwoerung'); // ohne Umlaut
        await expect(page.locator('#trResults .tr-result')).toHaveCount(1);
        await page.locator('#trResults .tr-result').click();
        await expect(page).toHaveURL(new RegExp('#' + BESCHWOERUNG + '$'));
        await expect(page.locator('#trDetail .tr-detail-title')).toHaveText('Beschwörung');

        // Suche ueber englische Alternativbezeichnung und ueber die ID
        await page.fill('#trSearch', 'Minstrelsy');
        await expect(page.locator('#trResults .tr-result-name')).toContainText(['Minnesängerisches im Spruchsang']);
        await page.fill('#trSearch', 'c_f3e5cee1');
        await expect(page.locator('#trResults .tr-result-name')).toHaveText(['Dietrichsepik']);
        await page.fill('#trSearch', 'xyzzy');
        await expect(page.locator('#trResults')).toContainText('Keine Treffer');
    });

    test('Auf- und Zuklappen ohne Suche', async ({ page }) => {
        await page.goto('/textreihen/browser.html');
        await expect(page.locator('html[data-tr-ready="1"]')).toBeAttached();
        const wurzel = page.locator('#trTree > li').first();
        const toggle = wurzel.locator('> .tr-row > .tr-toggle');
        await expect(toggle).toHaveAttribute('aria-expanded', 'true'); // Ebene 1 ist beim Start offen
        await toggle.click();
        await expect(toggle).toHaveAttribute('aria-expanded', 'false');
        await page.click('#trOpen2');
        await expect(page.locator('#trTree li.is-open').nth(5)).toBeAttached();
        await page.click('#trCollapse');
        await expect(page.locator('#trTree li.is-open')).toHaveCount(0);
    });
});

test.describe('Textreihentypologie: Bibliografie', () => {

    test('190 Eintraege, Textsuche und Schlagwort-Filter', async ({ page }) => {
        await page.goto('/textreihen/bibliography.html');
        const alle = page.locator('#bibList > li');
        await expect(alle).toHaveCount(190);
        await expect(page.locator('#bibStatus')).toHaveText('190 Einträge');

        await page.fill('#bibQuery', 'achnitz');
        const treffer = await page.locator('#bibList > li:not([hidden])').count();
        expect(treffer).toBeGreaterThan(0);
        expect(treffer).toBeLessThan(190);
        await expect(page.locator('#bibStatus')).toHaveText(`${treffer} von 190 Einträgen`);
        await page.fill('#bibQuery', '');

        const optionen = await page.locator('#bibTag option').count();
        expect(optionen).toBe(169); // "alle" plus 168 Schlagwoerter
        await page.selectOption('#bibTag', { index: 1 });
        const gefiltert = await page.locator('#bibList > li:not([hidden])').count();
        expect(gefiltert).toBeGreaterThan(0);
        expect(gefiltert).toBeLessThan(190);
    });
});
