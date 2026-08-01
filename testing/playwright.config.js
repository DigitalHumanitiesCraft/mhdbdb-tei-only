// playwright.config.js
import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  testDir: './tests',
  outputDir: resolve(__dirname, 'test-results/artifacts'),
  // Parallelität auf Datei-, nicht auf Testebene. Der Unterschied ist keine
  // Vorsicht, sondern eine Anforderung: `search-normalization.spec.js` legt in
  // `beforeAll` eine Seite an und teilt sie über alle Tests der Datei, um den
  // Index einmal statt vierzehnmal zu laden. `fullyParallel: true` würde diese
  // Tests auf verschiedene Worker verteilen und die geteilte Seite zerreißen.
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  // Sechs Worker, gemessen (#323): 20,4 min bei einem Worker gegen 5,0 min bei
  // sechs, über dieselben 276 Tests. Die Grenze ist nicht die Kernzahl (16
  // verfügbar), sondern der single-threaded `http-server` weiter unten und der
  // Chromium-Heap: jeder Context hält den entpackten Korpus-Index, rund 500 MB,
  // bei sechs Workern also etwa 3 GB. Mehr Worker verschieben den Engpass auf
  // die Auslieferung der 42 MB pro Seitenaufbau.
  //
  // Nichts erzwingt serielle Ausführung: kein `test.describe.serial`, kein
  // `test.use()`, keine Abhängigkeit zwischen Tests, und Playwright gibt jedem
  // Test ohnehin einen eigenen Context mit isolierter Storage-Partition.
  workers: 6,
  reporter: [
    ['html', { outputFolder: resolve(__dirname, 'test-results/html-report') }],
    ['json', { outputFile: resolve(__dirname, 'test-results/report.json') }]
  ],
  use: {
    baseURL: 'http://localhost:8080',
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