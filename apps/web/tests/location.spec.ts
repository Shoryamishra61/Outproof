import { test, expect } from './fixtures';
import type { ConstraintSet } from '../../../contracts/domain';

const chennai = { label: 'Chennai, Tamil Nadu, India', coordinates: { latitude: 13.0418, longitude: 80.2341 } };

test('a routed start needs explicit consent and preserves every limit', async ({ page }) => {
  const submitted: ConstraintSet[] = [];
  const proposed = { latitude: 13.0419, longitude: 80.2341 };
  await page.route('**/v1/plans/compile', route => {
    submitted.push(route.request().postDataJSON().controls);
    return route.fulfill({ status: 409, json: { status: 'FAILURE', code: 'UNSUPPORTED_CONSTRAINT', message: 'Controlled connector refusal', suggested_origin: proposed } });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
  const confirm = page.getByRole('button', { name: 'Set start to mapped route', exact: true });
  await expect(confirm).toBeVisible();
  await expect(page.getByText(/Travel from your current pin/)).toBeVisible();
  await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
  await expect.poll(() => submitted.length).toBe(2);
  expect(submitted[1].origin).toEqual(submitted[0].origin);
  await expect(confirm).toBeVisible(); await confirm.press('Enter');
  await expect(confirm).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Compile one fixture plan' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect.poll(() => submitted.length).toBe(3);
  expect(submitted[2].origin).toEqual(proposed);
  const limits = ({ origin: _origin, departure_at: _departure, ...rest }: ConstraintSet) => rest;
  expect(limits(submitted[2])).toEqual(limits(submitted[0]));
  await expect(page.getByRole('heading', { name: 'One fixture plan.' })).toHaveCount(0);
});

for (const kind of ['distant', 'missing-source', 'invalid']) {
  test(`unsafe routed-start proposal ${kind} is not selectable`, async ({ page }) => {
    await page.route('**/v1/plans/compile', route => route.fulfill({ status: 409, json: {
      status: 'FAILURE', code: kind === 'missing-source' ? 'NO_GROUNDED_CANDIDATES' : 'UNSUPPORTED_CONSTRAINT', message: 'Controlled unsafe proposal',
      suggested_origin: { latitude: kind === 'invalid' ? 91 : kind === 'distant' ? 14 : 13.0419, longitude: 80.2341 },
    } }));
    await page.goto('/'); await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Set start to mapped route', exact: true })).toHaveCount(0);
  });
}

test('distinct same-name map matches submit the selected point', async ({ page }) => {
  const matches = [
    { ...chennai, label: 'Chennai, India — map match 1' },
    { label: 'Chennai, India — map match 2', coordinates: { latitude: 13.05, longitude: 80.24 } },
  ];
  await page.route('**/v1/locations/search', route => route.fulfill({ json: { results: matches } }));
  await page.goto('/');
  await expect(page.locator('.eyebrow').first()).toContainText('Outproof');
  await page.getByLabel('Search for your starting area').fill('Chennai');
  await page.getByRole('button', { name: 'Search places', exact: true }).click();
  await page.getByRole('button', { name: matches[1].label, exact: true }).press('Enter');
  await expect(page.getByRole('button', { name: 'Hide map', exact: true })).toBeFocused();
  let submitted: unknown;
  await page.route('**/v1/plans/compile', route => {
    submitted = route.request().postDataJSON().controls.origin;
    return route.fulfill({ status: 409, json: { status: 'FAILURE', code: 'NO_GROUNDED_CANDIDATES', message: 'Controlled evidence refusal' } });
  });
  await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
  await expect.poll(() => submitted).toEqual(matches[1].coordinates);
});

for (const width of [360, 768, 1024, 1440]) {
  test(`search select and keyboard map at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.route('**/v1/locations/search', route => route.fulfill({ json: { results: [chennai] } }));
    await page.goto('/');
    await expect(page.getByLabel('Latitude', { exact: true })).toHaveCount(0);
    await page.getByLabel('Search for your starting area').fill('Chennai');
    await expect(page.getByRole('button', { name: 'Compile one fixture plan' })).toBeDisabled();
    await page.getByLabel('Search for your starting area').press('Enter');
    const match = page.getByRole('button', { name: chennai.label, exact: true });
    await match.focus(); await match.press('Enter');
    await expect(page.getByRole('status').filter({ hasText: 'Starting point:' })).toContainText(chennai.label);
    await expect(page.getByRole('region', { name: 'Starting location map' })).toBeVisible();
    const centre = page.getByRole('button', { name: 'Use map centre as start' });
    await expect(centre).toBeEnabled();
    await page.getByRole('region', { name: 'Starting location map' }).focus();
    await page.keyboard.press('ArrowRight');
    await centre.focus(); await centre.press('Enter');
    await expect(page.getByRole('status').filter({ hasText: 'Starting point:' })).toContainText('Chosen starting point');
    let submittedLongitude: number | undefined;
    await page.route('**/v1/plans/compile', route => {
      submittedLongitude = route.request().postDataJSON().controls.origin.longitude;
      return route.fulfill({ status: 503, json: { status: 'FAILURE', code: 'SOURCE_TEMPORARILY_UNAVAILABLE', message: 'Controlled failure' } });
    });
    await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
    await expect.poll(() => submittedLongitude).toBeGreaterThan(chennai.coordinates.longitude);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}

for (const failure of ['empty', 'offline', 'malformed', 'busy']) {
  test(`location search ${failure} has honest recovery`, async ({ page }) => {
    await page.route('**/v1/locations/search', route => failure === 'offline' ? route.abort() : route.fulfill({
      status: failure === 'busy' ? 429 : 200,
      json: { results: failure === 'empty' ? [] : [{ label: 'Invalid place', coordinates: { latitude: 91, longitude: 0 } }] },
    }));
    await page.goto('/'); await page.getByLabel('Search for your starting area').fill('Somewhere');
    await page.getByRole('button', { name: 'Search places', exact: true }).click();
    await expect(failure === 'empty' ? page.getByRole('status').filter({ hasText: 'No matching places' }) : page.getByRole('alert')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Compile one fixture plan' })).toBeDisabled();
    await page.getByRole('button', { name: 'Choose on map', exact: true }).click();
    await page.getByRole('button', { name: 'Use map centre as start' }).click();
    await expect(page.getByRole('button', { name: 'Compile one fixture plan' })).toBeEnabled();
  });
}

test('GPS can refresh an earlier fix and cannot override a newer map choice', async ({ page }) => {
  await page.addInitScript(() => {
    let calls = 0;
    Object.defineProperty(navigator.geolocation, 'getCurrentPosition', { value: (success: PositionCallback) => {
      calls++;
      const point = { coords: { latitude: 13.0418 + calls / 10000, longitude: 80.2341, accuracy: 12 } } as GeolocationPosition;
      if (calls === 3) setTimeout(() => success(point), 500); else success(point);
      (window as unknown as { gpsCalls: number }).gpsCalls = calls;
    } });
  });
  await page.goto('/'); await page.getByLabel('Use my current location (GPS)').check();
  await page.getByRole('button', { name: 'Refresh GPS' }).click();
  expect(await page.evaluate(() => (window as unknown as { gpsCalls: number }).gpsCalls)).toBe(2);
  await page.getByRole('button', { name: 'Refresh GPS' }).click();
  await page.getByRole('button', { name: 'Use map centre as start' }).click();
  await page.waitForTimeout(600);
  await expect(page.getByRole('status').filter({ hasText: 'Starting point:' })).toContainText('Chosen starting point');
  await expect(page.getByRole('button', { name: 'Compile one fixture plan' })).toBeEnabled();
});

test('map pointer selects the exact submitted origin', async ({ page }) => {
  await page.goto('/'); await page.getByRole('button', { name: 'Choose on map', exact: true }).click();
  const map = page.getByRole('region', { name: 'Starting location map' });
  await expect(page.getByRole('button', { name: 'Use map centre as start' })).toBeEnabled();
  await map.click({ position: { x: 130, y: 130 } });
  let origin: { latitude: number; longitude: number } | undefined;
  await page.route('**/v1/plans/compile', route => {
    origin = route.request().postDataJSON().controls.origin;
    return route.fulfill({ status: 503, json: { status: 'FAILURE', code: 'SOURCE_TEMPORARILY_UNAVAILABLE', message: 'Controlled failure' } });
  });
  await page.getByRole('button', { name: 'Compile one fixture plan' }).click();
  await expect.poll(() => origin !== undefined).toBe(true);
  expect(Number.isFinite(origin?.latitude)).toBe(true);
  expect(Number.isFinite(origin?.longitude)).toBe(true);
});
