// playwright.config.js
import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  testDir: './tests',
  outputDir: resolve(__dirname, 'test-results/artifacts'),
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
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