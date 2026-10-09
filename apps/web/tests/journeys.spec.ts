import { test, expect } from './fixtures';
import { resolve } from 'node:path';

const widths = [320, 360, 375, 390, 768, 1024, 1280, 1440, 1920, 3840];
const paths = ['success', 'budget', 'currency', 'walking', 'duration', 'geodenied', 'map', 'cancel', 'offline', 'malformed'];
for (const width of widths) for (const path of paths) {
  test(`${path} at ${width}`, async ({ page, context }) => {
    await page.setViewportSize({ width, height: 900 });
    await context.setExtraHTTPHeaders({ 'X-Test-Client': `${width}-${path}` });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const errors: string[] = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error' && !m.text().includes('Failed to load resource')) errors.push(m.text()); });
    await page.goto('/');
    const submit = page.getByRole('button', { name: 'Compile one fixture plan' });
    await expect(submit).toBeEnabled();
    if (path === 'budget') await page.getByLabel('Budget in INR', { exact: true }).fill('0');
    if (path === 'currency') await page.getByRole('combobox', { name: 'Currency', exact: true }).selectOption('USD');
    if (path === 'walking') await page.getByLabel('Walking, all legs (min)').fill('0');
    if (path === 'duration') await page.getByLabel('Time incl. return (min)').fill('15');
    if (path === 'geodenied') {
      await page.getByLabel('Use my current location (GPS)').check();
      await expect(page.getByRole('alert')).toContainText('Location access unavailable');
      await expect(submit).toBeDisabled();
      await page.getByLabel(/Fixture Chennai example/).check();
    }
    if (path === 'map') {
      await page.getByRole('button', { name: 'Choose on map', exact: true }).click();
      await page.getByRole('button', { name: 'Use map centre as start' }).click();
      await expect(submit).toBeEnabled();
      await expect(page.getByRole('status').filter({ hasText: 'Starting point:' })).toContainText('Chosen starting point');
    } else if (path === 'cancel') {
      await page.route('**/v1/plans/compile', async route => { await new Promise(r => setTimeout(r, 500)); await route.abort(); });
      await submit.click();
      await page.getByRole('button', { name: 'Cancel', exact: true }).click();
      await expect(page.getByRole('alert')).toContainText('Compilation stopped');
    } else if (path === 'offline') {
      await context.setOffline(true);
      await submit.click();
      await expect(page.getByRole('alert')).toBeVisible();
      await context.setOffline(false);
    } else {
      if (path === 'malformed') await page.route('**/v1/plans/compile', route => route.fulfill({ json: { status: 'SUCCESS' } }));
      // Exercise keyboard submission and visible focus, not just mouse clicks.
      await page.keyboard.press('Tab');
      await submit.focus();
      await expect(submit).toBeFocused();
      expect(await submit.evaluate(e => getComputedStyle(e).outlineStyle)).not.toBe('none');
      await page.keyboard.press('Enter');
      if (['budget', 'currency', 'walking', 'duration', 'malformed'].includes(path)) {
        await expect(page.getByRole('alert')).toBeVisible();
        await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toHaveCount(0);
      } else {
        await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toHaveCount(1);
        await page.getByText(/Plan Proof ·/).click();
        await expect(page.getByRole('heading', { name: 'Source observations · FIXTURE' })).toBeVisible();
        await page.getByRole('button', { name: 'GO · practice', exact: true }).click();
        await expect(page.getByText('Phone down.', { exact: true })).toBeVisible();
        await page.getByRole('button', { name: 'Next practice step' }).click();
        await page.getByRole('button', { name: 'Back to plan', exact: true }).click();
        await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toBeVisible();
      }
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    if (path === 'success' && [390, 1440].includes(width)) await page.screenshot({ path: resolve(import.meta.dirname, `../../../artifacts/release/fixture-${width}.png`), fullPage: true });
  });
}
