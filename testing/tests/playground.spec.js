// tests/playground.spec.js
import { test, expect } from '@playwright/test';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// #326: Sieben Tests dieser Datei prüften bis August 2026 `testing/test.html`,
// also das mitgelieferte Eigenbau-Test-Framework, nicht die Anwendung. Nach dem
// Upload-Rückbau (#314) sagten dessen vier Suiten nichts mehr über die
// Anwendung: zwei riefen `assert(true, ...)`, eine prüfte die Existenz von
// `window.indexedDB`, die vierte maß die Dauer einer String-Konkatenation.
// Seite und Framework sind entfernt; was hier bleibt, lädt den Playground.

test.describe('Playground Integration Tests', () => {
  test('should handle cache clearing functionality', async ({ page }) => {
    // Test the main playground cache clearing
    await page.goto('/playground/index.html');

    // Wait for page to load
    await expect(page).toHaveTitle(/TEI-Daten-Explorer/);

    // Check if clear site data button exists (it's in the footer)
    const clearButton = page.locator('#clearSiteDataBtn');
    await expect(clearButton).toBeVisible({ timeout: 10000 });
  });

  test('should load main playground page without errors', async ({ page }) => {
    // Test that the main playground loads correctly
    await page.goto('/playground/index.html');

    // Wait for page to load
    await expect(page).toHaveTitle(/TEI-Daten-Explorer/);

    // Check for essential elements
    await expect(page.locator('h1')).toContainText('TEI-Daten-Explorer');
    await expect(page.locator('#authorityOverview')).toBeVisible();

    // Check for authority files loading
    const statusText = page.locator('#statusText');

    // Wait for either loading or completion status
    await expect(statusText).toBeVisible({ timeout: 5000 });

    // Take screenshot for manual verification
    await page.screenshot({ path: resolve(__dirname, '../test-results/playground-main-page.png'), fullPage: true });
  });

  test('should have all required JavaScript modules', async ({ page }) => {
    // Der Test wartet auf den vollständigen Korpus-Index, also auf dieselbe
    // Ladung, für die reading-view und tei-caching ebenfalls 120 s ansetzen,
    // während lokal bis zu sechs Worker denselben single-threaded http-server
    // bedienen (in der CI zwei). Ohne diese Zeile wäre das Budget aus der Config (60 s)
    // genau so groß wie der waitForFunction-Timeout unten, liefe aber früher
    // los: es käme immer zuerst, und der catch-Zweig, der die eigentliche
    // Fehlermeldung rettet, griffe nie verlässlich.
    test.setTimeout(120000);

    // #331: Die Listener müssen VOR dem goto hängen. Die Auswertung der
    // ES-Module passiert während des Ladens; ein danach registrierter
    // Listener sieht sie nie. Bis August 2026 stand page.on() hinter
    // page.goto(), der Test konnte also genau die Fehlerklasse nicht sehen,
    // gegen die er schützen soll.
    // Zwei Meldungen sind namentlich ausgenommen, nicht weggezählt. Beide
    // stammen aus corpus-loader.js und sind dort ausdrücklich unkritisch: der
    // Loader fängt sie ab und lädt ohne Cache weiter (Zeile 142 und 164, die
    // zweite trägt den Kommentar „Non-critical error, continue without
    // caching"). Realistisch werden sie, sobald der Platz knapp wird: sechs
    // Worker schreiben je ihre eigene IndexedDB-Partition mit dem entpackten
    // Index. Das dritte console.error derselben Datei (Zeile 32, IndexedDB
    // lässt sich gar nicht öffnen) wirft weiter und bleibt deshalb ein Fehler.
    //
    // Sollte hier je weiteres legitimes Rauschen ankommen, gehört es in diese
    // Liste, nicht in eine erhöhte Schwelle. Ein Freibetrag „höchstens einer"
    // hätte genau einen echten Modulfehler durchgelassen, und das war der
    // Zustand, den #331 beendet hat.
    const unkritisch = [
      '[CorpusLoader] Failed to read cache for',
      '[CorpusLoader] Failed to cache',
    ];
    const MATOMO_HOST = 'https://webstatistics.sbg.ac.at/';

    const konsolenfehler = [];
    const seitenfehler = [];
    page.on('console', msg => {
      if (msg.type() !== 'error') return;
      // Der Matomo-Tracker wird per Script-Injection von einem fremden Host
      // geholt (includes/_matomo.html). Ist der nicht erreichbar, meldet
      // Chromium einen Ressourcenfehler vom Typ error, und der Test wäre
      // offline rot, ohne dass am Playground etwas kaputt ist. Ausgenommen
      // wird deshalb die HERKUNFTS-URL, nicht der Meldungstext: ein Filter
      // auf „Failed to load resource" würde auch ein fehlendes lokales
      // Modul verschlucken, also genau den Fall, für den der Test da ist.
      if (msg.location()?.url?.startsWith(MATOMO_HOST)) return;
      const text = msg.text();
      // startsWith, nicht includes: die Ausnahme gilt für Meldungen, die
      // aus dem Loader kommen, nicht für fremde, die seinen Text zitieren.
      if (unkritisch.some(prefix => text.startsWith(prefix))) return;
      konsolenfehler.push(text);
    });
    // pageerror ist nicht dasselbe wie console.error: eine unbehandelte
    // Ausnahme aus einem Modul kommt hier an, nicht zwingend dort.
    page.on('pageerror', err => seitenfehler.push(err.stack || String(err)));

    await page.goto('/playground/index.html');

    // Auf die vollständige Kette warten statt auf eine feste Zeitspanne:
    // die Module laden den Korpus-Index asynchron nach, und ein Fehler dabei
    // fiele nach einem pauschalen waitForTimeout(3000) je nach Maschine mal
    // auf und mal nicht.
    //
    // Der catch ist kein Schmuck, sondern gemessen: mit einem eingebauten
    // ReferenceError in einem Playground-Modul läuft die Kette gar nicht erst
    // durch, und ohne ihn meldete der Test einen waitForFunction-Timeout,
    // also die Folge statt der Ursache. Liegen Fehler vor, werden die zuerst
    // behauptet; hängt die Kette ohne jeden Fehler, bleibt der Timeout die
    // richtige Meldung.
    //
    // Das `null` ist nicht schmückend: die Signatur ist
    // waitForFunction(pageFunction, arg, options). Ohne das Platzhalter-Argument
    // landet das Options-Objekt als ARGUMENT in der Seite und der Timeout wirkt
    // nie. Genau so stand es im ersten Entwurf, und die Gegenprobe hat es
    // gezeigt: der Lauf endete nicht nach 60 s am eigenen Timeout, sondern nach
    // 120 s am Test-Budget. Dieselbe Verwechslung steckte an weiteren Stellen
    // in sechs Specs und ist dort mitkorrigiert. Wo ein Timeout unter dem
    // Budget lag, hat der Fix ihn erstmals wirksam gemacht; dort steht die
    // Begründung für den gewählten Wert jeweils daneben.
    try {
      await page.waitForFunction(
        () => window.playground?.corpusData?.texts?.length > 0,
        null,
        { timeout: 60000 }
      );
    } catch (timeout) {
      expect(seitenfehler, 'Ladekette blieb stehen, dabei angefallen').toEqual([]);
      expect(konsolenfehler, 'Ladekette blieb stehen, dabei angefallen').toEqual([]);
      throw timeout;
    }

    // Schwelle 0 für alles außerhalb der Ausnahmeliste oben. Gemessen am
    // 02.08.2026 über den ganzen Ladevorgang: 0 console.error, 0 pageerror,
    // 0 fehlgeschlagene Requests. Die Messung lief mit Netz und mit Platz für
    // die Caches; genau deshalb steht die Ausnahmeliste da, statt sich auf die
    // Null zu verlassen.
    //
    // Verglichen wird das ganze Array, nicht seine Länge: im Fehlerfall steht
    // die Meldung im Assertion-Diff, statt dass nur eine Zahl nicht stimmt.
    expect(seitenfehler, 'unbehandelte Ausnahmen beim Laden').toEqual([]);
    expect(konsolenfehler, 'console.error beim Laden').toEqual([]);
  });
});
