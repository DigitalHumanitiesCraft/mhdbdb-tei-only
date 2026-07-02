/**
 * Vendor-Guard: Alle Runtime-Bibliotheken kommen aus assets/vendor/,
 * keine CDN-Abhängigkeiten (pako/dexie vendored analog Prism #78).
 *
 * Zwei Ebenen:
 * 1. Statischer Scan — kein <script src="https://..."> in committeten HTML-Seiten
 * 2. Laufzeit — window.pako und window.Dexie sind auf den Seiten verfügbar,
 *    die sie brauchen (lädt ausschließlich lokal, funktioniert daher auch
 *    in Umgebungen ohne CDN-Zugriff)
 */

import { test, expect } from '@playwright/test';
import { readFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

function htmlFiles(dir, acc = []) {
    for (const name of readdirSync(dir)) {
        if (['node_modules', '.git', 'test-results', 'tei'].includes(name)) continue;
        const p = join(dir, name);
        if (statSync(p).isDirectory()) htmlFiles(p, acc);
        else if (name.endsWith('.html')) acc.push(p);
    }
    return acc;
}

test('no external script src in any committed HTML page', () => {
    const offenders = [];
    for (const file of htmlFiles(repoRoot)) {
        const html = readFileSync(file, 'utf8');
        const matches = html.match(/<script[^>]+src="https?:\/\/[^"]*"/g);
        if (matches) offenders.push(`${file.replace(repoRoot + '/', '')}: ${matches.join(', ')}`);
    }
    expect(offenders, `CDN-Referenzen gefunden:\n${offenders.join('\n')}`).toEqual([]);
});

const PAGES_WITH_LIBS = [
    '/index.html',
    '/korpus.html',
    '/woerterbuch.html',
    '/lemma/index.html',
    '/playground/index.html'
];

for (const path of PAGES_WITH_LIBS) {
    test(`vendored pako + dexie load on ${path}`, async ({ page }) => {
        await page.goto(`http://localhost:8080${path}`);
        await page.waitForLoadState('domcontentloaded');
        const libs = await page.evaluate(() => ({
            pako: typeof window.pako !== 'undefined',
            dexie: typeof window.Dexie !== 'undefined'
        }));
        expect(libs.pako, `pako fehlt auf ${path}`).toBe(true);
        expect(libs.dexie, `Dexie fehlt auf ${path}`).toBe(true);
    });
}
