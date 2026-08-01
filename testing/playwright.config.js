// playwright.config.js
import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  testDir: './tests',
  outputDir: resolve(__dirname, 'test-results/artifacts'),
  // Parallelität auf Datei-, nicht auf Testebene. `search-normalization.spec.js`
  // legt in `beforeAll` eine Seite an und teilt sie über alle Tests der Datei,
  // um den Index einmal statt vierzehnmal zu laden. Bei `fullyParallel: true`
  // würden diese Tests auf mehrere Worker verteilt; die Seite ginge nicht
  // kaputt (Playwright führt `beforeAll` pro Worker erneut aus), aber der
  // Spareffekt stirbt: der Index würde bis zu sechsmal geladen statt einmal,
  // und das trifft genau den Engpass unten.
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  // Ein Versuch mehr, seit sechs Worker laufen (#323). Mit einem Worker war
  // retries: 0 stimmig: was seriell rot wird, ist reproduzierbar rot. Unter
  // Last treten Timing-Flakes einmal auf und beim nächsten Lauf nicht mehr;
  // ohne Retry ist der eine Lauf, in dem das Problem sichtbar war, schon
  // verbraucht. Dass ein Retry einen echten Fehler als flaky ausweisen und
  // damit grün durchwinken kann, verhindert failOnFlakyTests weiter unten.
  //
  // Überall einer, auch in der CI: der übliche Grund für mehr („CI ist
  // langsamer und flakiger, gib ihr Versuche") ist mit failOnFlakyTests
  // entfallen. Ein zusätzlicher Versuch kann dort nichts mehr retten, er
  // kostet nur Zeit, denn der Trace entsteht ohnehin beim ersten Retry.
  retries: 1,
  // Der Retry ist zur Diagnose da, nicht zum Durchwinken. Ohne diese Zeile
  // endet ein Lauf mit Exit 0, sobald ein Test im zweiten Versuch grün wird:
  // er zählt dann als flaky, nicht als failed. Genau dieser Lauf ist vor dem
  // Push Pflicht (DEVELOPMENT.md), und ein Retry darf ihn nicht schönen.
  // Seit Playwright 1.52 als Config-Option, daher die Untergrenze in
  // package.json. Playwright ignoriert unbekannte Config-Properties still,
  // die Wirkung ist deshalb gemessen und nicht angenommen: ein Test, der im
  // ersten Versuch fällt und im Retry grün wird, ergibt mit dieser Zeile
  // Exit 1 und ohne sie Exit 0, beide Male gemeldet als "1 flaky".
  failOnFlakyTests: true,
  // Sechs Worker lokal, gemessen (#323): 20,4 min bei einem Worker gegen 5,0
  // bis 5,3 min bei sechs, über dieselben 276 Tests, fünf Läufe mit dem
  // Trace-Modus unten. Die Grenze ist nicht die Kernzahl (16 verfügbar),
  // sondern der single-threaded `http-server` weiter unten und der
  // Chromium-Heap: jeder Context, der den Korpus-Index lädt, hält ihn
  // entpackt im Speicher (168 MB JSON, als
  // JS-Objekte grob geschätzt das Zwei- bis Dreifache). Mehr Worker verschieben
  // den Engpass auf die Auslieferung der 42 MB pro Seitenaufbau.
  //
  // In der CI zwei: Standard-Runner haben zwei bis vier vCPUs, dort würden
  // sechs Worker plus single-threaded Server nur noch thrashen. Das trägt
  // die Entscheidung allein; verdecken könnten die drei CI-Versuche nichts,
  // dafür sorgt failOnFlakyTests. Heute ohnehin akademisch, weil kein
  // Workflow `npm test` ruft, aber `forbidOnly` verzweigt hier schon auf CI,
  // und die vCPU-Zahl ist der einzige Wert, der sich dort wirklich ändert.
  //
  // Nichts erzwingt serielle Ausführung: kein `test.describe.serial`, kein
  // `test.use()`, keine Abhängigkeit zwischen Tests, und Playwright gibt jedem
  // Test ohnehin einen eigenen Context mit isolierter Storage-Partition.
  workers: process.env.CI ? 2 : 6,
  reporter: [
    ['html', { outputFolder: resolve(__dirname, 'test-results/html-report') }],
    ['json', { outputFile: resolve(__dirname, 'test-results/report.json') }]
  ],
  use: {
    baseURL: 'http://localhost:8080',
    // Zusammen mit retries: 1 oben. 'retain-on-failure' wäre der naive Weg,
    // kostet 19 bis 26 Prozent, je nach Referenzlauf: der Modus zeichnet für
    // JEDEN Test auf und verwirft die Traces der grünen erst hinterher
    // (gemessen 6,3 min gegen 5,0 bis 5,3 min). Bei 276 grünen Tests bezahlt
    // man 275 Aufzeichnungen für eine, die man behält, und das auf genau
    // dem Engpass, den der
    // Worker-Kommentar oben beschreibt. Mit einem Retry fällt der Flake
    // einmal, läuft mit Trace nach und wird als flaky ausgewiesen.
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  // Global test timeout
  timeout: 60000, // 1 minute per test (was unlimited)
  expect: {
    timeout: 10000, // 10 seconds for assertions (was default 5s)
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Disable web security for local file access
        launchOptions: {
          args: ['--disable-web-security', '--allow-running-insecure-content']
        }
      },
    },
  ],

  webServer: {
    command: 'npx http-server .. -p 8080 -c-1',
    port: 8080,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});