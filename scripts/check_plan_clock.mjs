import assert from 'node:assert/strict';
import fs from 'node:fs';
import { canStart, responseTime, sourceState } from '../apps/web/src/planFreshness.ts';

// Retain the actual public response whose immediate GO failed with a slow browser clock.
const receipt = JSON.parse(fs.readFileSync(new URL('../evals/reports/OUTPROOF_ORIGIN_PUBLIC_FAILURE.json', import.meta.url)));
const plan = receipt.requests[1].body;
const compiled = Date.parse(plan.compiled_at);
assert.equal(canStart(plan, compiled - 500), false);
const aligned = responseTime(new Date(compiled + 1).toISOString(), plan.compiled_at, 13000);
assert.ok(aligned !== null);
assert.equal(canStart(plan, aligned), true);
assert.equal(canStart(plan, aligned + 60000), false);

for (const [header, elapsed] of [[null, 1], ['bad', 1], [new Date(compiled - 1).toISOString(), 1], [plan.compiled_at, -1], [plan.compiled_at, NaN], [plan.compiled_at, 185001]]) {
  assert.equal(responseTime(header, plan.compiled_at, elapsed), null);
}
assert.equal(responseTime(plan.compiled_at, 'bad', 1), null);
const future = structuredClone(plan);
future.proof.sources[0].observed_at = new Date(aligned + 1).toISOString();
assert.equal(canStart(future, aligned), false);
const expired = structuredClone(plan);
expired.proof.sources[0].expires_at = new Date(aligned).toISOString();
assert.equal(canStart(expired, aligned), false);
assert.equal(sourceState(expired.proof.sources[0], aligned), 'Stale — revalidation required');
const stale = structuredClone(plan);
stale.compiled_at = new Date(aligned - 60001).toISOString();
assert.equal(canStart(stale, aligned), false);
const closed = structuredClone(plan);
closed.plan.stops[0].place.opening_windows = [];
assert.equal(canStart(closed, aligned), false);
const late = structuredClone(plan);
late.return_by_local = new Date(aligned + plan.proof.total_duration_seconds * 1000 - 1).toISOString();
assert.equal(canStart(late, aligned), false);
console.log('Actual GO clock-skew regression and unchanged freshness/closing/deadline guards passed.');
