import { defineConfig, devices } from '@playwright/test';

/**
 * Configuração do Playwright para testes E2E
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',

  /* Executar testes em paralelo */
  fullyParallel: true,

  /* Falhar build se deixou test.only por acidente */
  forbidOnly: !!process.env.CI,

  /* Retry em CI */
  retries: process.env.CI ? 2 : 0,

  /* Workers paralelos */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter */
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],

  /* Configuração global */
  use: {
    /* URL base para testes */
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    /* Coletar trace em caso de falha */
    trace: 'on-first-retry',

    /* Screenshot em falha */
    screenshot: 'only-on-failure',

    /* Video em retry */
    video: 'retain-on-failure',

    /* Timeout de ações */
    actionTimeout: 10000,

    /* Timeout de navegação */
    navigationTimeout: 30000,
  },

  /* Configurar servidor local */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },

  /* Configurar projetos para diferentes navegadores */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Testes mobile */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* Timeout global de testes */
  timeout: 60000,
});
