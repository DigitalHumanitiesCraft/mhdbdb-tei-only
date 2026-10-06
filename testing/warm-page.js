/**
 * Warme Seite pro Worker (#488, Stufe 3 aus #323).
 *
 * Playwright gibt jedem Test einen frischen Context. Fuer Seiten, die den
 * Korpus-Index laden (korpus.html, Playground, Lemma-Seiten), heisst das:
 * jeder Test holt 42 MB, entpackt und parst sie und schreibt sie in eine
 * leere IndexedDB. Hier bekommt jeder Worker EINEN Context; der erste Test
 * darin fuellt den Cache, jeder weitere liest ihn aus IndexedDB. Jeder Test
 * bekommt trotzdem eine eigene, frische `page`.
 *
 * Opt-in je Spec: `import { test, expect } from '../warm-page.js';` statt
 * aus '@playwright/test'. NICHT fuer Specs, die
 *  - Storage-Zustand pruefen oder setzen (localStorage, IndexedDB,
 *    sessionStorage ueber Tests hinweg, setOffline),
 *  - Netzantworten mit page.route/context.route mocken: in einem warmen
 *    Context bedient der Cache, die Route feuert nie, und der Test prueft
 *    den Cache statt des Mocks, ohne rot zu werden,
 *  - neben `page` den `context`-Fixture benutzen: der waere ein anderer
 *    Context als der der Seite.
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
        await page.close();
    },
});

export { expect };
