import { test, expect } from './fixtures';

test('source outage is distinct from readiness and retains controls for recovery', async ({ page }) => {
  await page.goto('/');
  const submit = page.getByRole('button', { name: 'Compile one fixture plan' });
  await expect(submit).toBeEnabled();
  await page.route('**/v1/plans/compile', route => route.fulfill({
    status: 503, contentType: 'application/json', headers: { 'Retry-After': '60' },
    body: JSON.stringify({ status: 'FAILURE', code: 'SOURCE_TEMPORARILY_UNAVAILABLE', message: 'Map discovery could not be reached. Retry in 60 seconds; no nearby place has been verified.' }),
  }));
  await submit.click();
  await expect(page.getByRole('alert')).toContainText('Retry in 60 seconds');
  await expect(page.getByText('Last compilation failed · no verified plan', { exact: true })).toBeVisible();
  await expect(page.getByLabel('Time incl. return (min)')).toHaveValue('90');
  await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toHaveCount(0);
  await page.unroute('**/v1/plans/compile');
  await submit.click();
  await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toBeVisible();
});

for (const width of [320, 390, 1440]) for (const path of ['gps', 'lowaccuracy', 'gpstimeout', 'retry', 'double', 'cancelstale', 'zoom', 'voice']) {
  test(`${path} recovery at ${width}`, async ({ page, context }) => {
    await page.setViewportSize({ width, height: 900 });
    await context.setExtraHTTPHeaders({ 'X-Test-Client': `recovery-${width}-${path}` });
    if (['gps', 'lowaccuracy', 'gpstimeout'].includes(path)) {
      await page.addInitScript(({ path }) => {
        Object.defineProperty(navigator.geolocation, 'getCurrentPosition', { value: (success: PositionCallback, error: PositionErrorCallback) => {
          if (path === 'gpstimeout') error({ code: 3, message: 'Controlled timeout' } as GeolocationPositionError);
          else success({ coords: { latitude: 13.0418, longitude: 80.2341, accuracy: path === 'lowaccuracy' ? 3000 : 12 } } as GeolocationPosition);
        } });
      }, { path });
    }
    await page.goto('/');
    const submit = page.getByRole('button', { name: 'Compile one fixture plan' });
    await expect(submit).toBeEnabled();
    if (['gps', 'lowaccuracy', 'gpstimeout'].includes(path)) {
      await page.getByLabel('Use my current location (GPS)').check();
      if (path !== 'gps') {
        await expect(page.getByRole('alert')).toContainText(path === 'lowaccuracy' ? 'accuracy is too low' : 'Controlled timeout');
        await expect(submit).toBeDisabled();
        const chooseMap = page.getByRole('button', { name: 'Choose on map', exact: true });
        if (await chooseMap.isVisible()) await chooseMap.click();
        await page.getByRole('button', { name: 'Use map centre as start' }).click();
        await expect(submit).toBeEnabled();
        return;
      }
      await expect(page.getByRole('radio', { name: 'Device location · accuracy ±12 m', exact: true })).toBeVisible();
    }
    let requests = 0;
    page.on('request', request => { if (request.url().endsWith('/v1/plans/compile')) requests++; });
    if (path === 'retry') {
      await context.setOffline(true);
      await submit.click();
      await expect(page.getByRole('alert')).toBeVisible();
      await context.setOffline(false);
    }
    if (path === 'cancelstale') {
      await page.route('**/v1/plans/compile', async route => {
        const response = await route.fetch();
        await new Promise(resolve => setTimeout(resolve, 700));
        await route.fulfill({ response }).catch(() => {});
      });
      await submit.click();
      await page.getByRole('button', { name: 'Cancel', exact: true }).click();
      await page.getByLabel('Budget in INR', { exact: true }).fill('0');
      await page.waitForTimeout(1000);
      await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toHaveCount(0);
      await page.unroute('**/v1/plans/compile');
      await submit.click();
      await expect(page.getByRole('alert')).toBeVisible();
      return;
    }
    if (path === 'zoom') await page.addStyleTag({ content: 'html { zoom: 2; }' });
    if (path === 'double') {
      await submit.evaluate((button: HTMLButtonElement) => { button.click(); button.click(); });
    } else await submit.click();
    await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toBeVisible();
    if (path === 'double') expect(requests).toBe(1);
    await page.getByRole('button', { name: 'GO · practice', exact: true }).click();
    await expect(page.getByText('Phone down.', { exact: true })).toBeVisible();
    if (path === 'voice') {
      const audio = page.locator('audio');
      await expect(audio).toHaveAttribute('preload', 'none');
      expect(await audio.evaluate((element: HTMLAudioElement) => element.paused)).toBe(true);
      await audio.evaluate((element: HTMLAudioElement) => element.play());
      await expect.poll(() => audio.evaluate((element: HTMLAudioElement) => element.currentTime)).toBeGreaterThan(0);
      await audio.evaluate((element: HTMLAudioElement) => element.pause());
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.reload();
    await expect(page.getByRole('heading', { name: /Less searching/ })).toBeVisible();
    await expect(page.getByText('Phone down.', { exact: true })).toHaveCount(0);
  });
}
