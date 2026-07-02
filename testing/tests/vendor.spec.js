/**
 * Vendor-Guard: Alle Runtime-Bibliotheken kommen aus assets/vendor/,
 * keine CDN-Abhängigkeiten (pako/dexie vendored analog Prism #78).
 *
 * Zwei Ebenen:
 * 1. Statischer Scan — kein externes <script src> in committeten HTML-Seiten
 *    (doppelte/einfache/fehlende Quotes und protokoll-relative URLs abgedeckt)
 * 2. Laufzeit — window.pako und window.Dexie sind auf jeder Seite verfügbar,
 *    die sie referenziert (Seitenliste wird aus dem HTML-Scan abgeleitet,
 *    kein hartkodiertes Set). Lädt ausschließlich lokal und funktioniert
 *    daher auch in Umgebungen ohne CDN-Zugriff.
 */

import { test, expect } from '@playwright/test';
import { readFileSync, readdirSync } from 'fs';
import { resolve, dirname, join, relative } from 'path';
import { fileURLToPath } from 'url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

function htmlFiles(dir, acc = []) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
        if (['node_modules', '.git', 'test-results', 'tei', 'data'].includes(entry.name)) continue;
        const p = join(dir, entry.name);
        if (entry.isDirectory()) htmlFiles(p, acc);
        else if (entry.name.endsWith('.html')) acc.push(p);
    }
    return acc;
}

// Externe script-src in allen Quote-Varianten plus protokoll-relativ (//cdn...)
const EXTERNAL_SCRIPT_SRC = /<script[^>]+src\s*=\s*["']?\s*(?:https?:)?\/\//gi;

const pages = htmlFiles(repoRoot).map(file => ({
    file,
    urlPath: '/' + relative(repoRoot, file).split('\\').join('/'),
    html: readFileSync(file, 'utf8')
}));

test('no external script src in any committed HTML page', () => {
    const offenders = [];
    for (const { file, html } of pages) {
        const matches = html.match(EXTERNAL_SCRIPT_SRC);
        if (matches) offenders.push(`${relative(repoRoot, file)}: ${matches.join(', ')}`);
    }
    expect(offenders, `CDN-Referenzen gefunden:\n${offenders.join('\n')}`).toEqual([]);
});

// Seiten, die pako/dexie referenzieren — aus dem HTML abgeleitet, damit neue
// Seiten automatisch mitgeprüft werden (falscher relativer Pfad → Test rot)
const pagesWithLibs = pages.filter(p => /assets\/vendor\/(pako|dexie)\//.test(p.html));

test('at least the 5 known pages reference vendored pako/dexie', () => {
    expect(pagesWithLibs.length).toBeGreaterThanOrEqual(5);
});

for (const { urlPath } of pagesWithLibs) {
    test(`vendored pako + dexie load on ${urlPath}`, async ({ page }) => {
        await page.goto(`http://localhost:8080${urlPath}`);
        await page.waitForLoadState('domcontentloaded');
        const libs = await page.evaluate(() => ({
            pako: typeof window.pako !== 'undefined',
            dexie: typeof window.Dexie !== 'undefined'
        }));
        expect(libs.pako, `pako fehlt auf ${urlPath}`).toBe(true);
        expect(libs.dexie, `Dexie fehlt auf ${urlPath}`).toBe(true);
    });
}
