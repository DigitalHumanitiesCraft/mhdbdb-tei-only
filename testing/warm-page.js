/**
 * Warme Seite pro Worker (#488, Stufe 3 aus #323).
 *
 * Playwright gibt jedem Test einen frischen Context. Fuer Seiten, die den
 * Korpus-Index laden (korpus.html, Playground, Lemma-Seiten), heisst das:
 * jeder Test holt 42 MB, entpackt und parst sie und schreibt sie in eine
 * leere IndexedDB. Hier bekommt jeder Worker EINEN Context; der erste Test
 * darin fuellt den Cache, jeder weitere liest ihn aus IndexedDB. Jeder Test
 * bekommt trotzdem eine eigene, frische `page`, und nach jedem Test wird
 * localStorage geleert (siehe unten); geteilt bleibt nur IndexedDB.
 *
 * Opt-in je Spec: `import { test, expect } from '../warm-page.js';` statt
 * aus '@playwright/test'. NICHT fuer Specs, die
 *  - Storage-Zustand ueber Tests hinweg pruefen oder setzen (localStorage,
 *    IndexedDB, sessionStorage, setOffline); innerhalb eines Tests ist
 *    localStorage unbedenklich, der Teardown leert es,
 *  - das kalte Laden messen oder pruefen: im warmen Context kommt der Index
 *    aus dem Cache, der Test bleibt gruen und misst nichts mehr,
 *  - Netzantworten mocken, die im Cache landen (der Korpus-Index): in einem
 *    warmen Context bedient der Cache, die Route feuert nie, und der Test
 *    prueft den Cache statt des Mocks, ohne rot zu werden. Stubs fuer
 *    Antworten, die nicht zwischengespeichert werden (api.woerterbuchnetz.de:
 *    nur ein In-Memory-Cache je Seite), sind in Ordnung, wenn der Test die
 *    Stub-Werte prueft; ein umgangener Stub wuerde ihn rot machen (#564),
 *  - neben `page` den `context`-Fixture benutzen: der waere ein anderer
 *    Context als der der Seite. Wer weitere Seiten braucht, nimmt
 *    `page.context()`; der Teardown schliesst uebrig gebliebene Seiten.
 *
 * Die Context-Optionen kommen aus dem Projekt (`use` in der Config), damit
 * baseURL und Viewport dieselben sind wie beim eingebauten Context.
 */

import { test as base, expect } from '@playwright/test';

const CONTEXT_OPTIONEN = [
    'baseURL', 'viewport', 'screen', 'userAgent', 'deviceScaleFactor',
    'isMobile', 'hasTouch', 'locale', 'timezoneId', 'colorScheme',
    'ignoreHTTPSErrors', 'javaScriptEnabled', 'bypassCSP', 'extraHTTPHeaders',
];

export const test = base.extend({
    warmContext: [async ({ browser }, use, workerInfo) => {
        const projekt = workerInfo.project.use || {};
        const optionen = {};
        for (const name of CONTEXT_OPTIONEN) {
            if (projekt[name] !== undefined) optionen[name] = projekt[name];
        }
        const context = await browser.newContext(optionen);
        await use(context);
        await context.close();
    }, { scope: 'worker' }],

    page: async ({ warmContext }, use) => {
        const page = await warmContext.newPage();
        await use(page);
        // localStorage teilt sich der warme Context, und die Seiten schreiben
        // selbst hinein (Aufklappzustand im Playground, Ergebnisansicht auf
        // korpus.html). Ohne das Leeren klappte der naechste Test einen Block
        // zu, den er aufklappen wollte, und lief in den Timeout. Warm bleiben
        // soll nur IndexedDB mit dem Index; sessionStorage gilt je Seite.
        try {
            if (page.url().startsWith('http')) {
                await page.evaluate(() => localStorage.clear());
            }
        } catch {
            // Seite schon geschlossen oder fremder Ursprung: nichts zu leeren
        }
        await page.close();
        // Seiten, die der Test selbst geoeffnet und nicht geschlossen hat (neue
        // Tabs): der eingebaute Context schloss sie mit dem Test, dieser lebt
        // bis zum Ende des Workers und haelt sonst jeden Tab samt Index offen.
        for (const uebrig of warmContext.pages()) {
            await uebrig.close().catch(() => {});
        }
    },
});

export { expect };
