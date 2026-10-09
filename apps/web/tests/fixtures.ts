import { test as base, expect } from '@playwright/test';

// Controlled map imagery: automated campaigns never pan/zoom the public tile server.
export const test = base.extend({ page: async ({ page }, use) => {
  await page.route('https://tile.openstreetmap.org/**', route => route.fulfill({
    contentType: 'image/png', body: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j3ioAAAAASUVORK5CYII=', 'base64'),
  }));
  await use(page);
} });
export { expect };
