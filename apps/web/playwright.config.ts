import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  workers: 2,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: '../../artifacts/release/browser-results.json' }]],
  use: { baseURL: 'http://127.0.0.1:5174', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  webServer: [
    { command: 'uv run uvicorn tests.release.browser_api:app --host 127.0.0.1 --port 8000', cwd: '../..', url: 'http://127.0.0.1:8000/v1/health/live', env: { PYTHONPATH: 'services/api', GROUND_RULE_ENV: 'development' }, reuseExistingServer: false },
    // Vite must keep serving when the headless runner closes its stdin.
    { command: 'npm run dev -- --port 5174', url: 'http://127.0.0.1:5174', env: { CI: 'true', VITE_GROUND_RULE_FIXTURE_MODE: 'true', VITE_GROUND_RULE_LIVE_MODE: 'false', VITE_GROUND_RULE_VOICE_ENABLED: 'true' }, reuseExistingServer: false },
  ],
});
