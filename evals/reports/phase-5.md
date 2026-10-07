# Phase 5 — Valhalla walking

Acceptance: PASS for provider routing, not end-to-end outing feasibility.
Executed 2026-10-07. Existing 17 exported contracts unchanged.

## Changed files / behavior

`services/api/app/routing.py`: RoutingProvider and Valhalla pedestrian adapter.
Exact requested endpoint IDs and coordinates bind each RouteFact; request-derived
IDs, response ID/locations, kilometer units and single-leg summaries are checked.
Seconds round upward. Missing, negative, boolean, string and non-finite metrics
fail closed. Documented no-path codes return unreachable facts with null metrics;
outages/malformed replies return SOURCE_TEMPORARILY_UNAVAILABLE.
Ferries/tolls are unsupported because their mandatory costs are not modeled.
No straight-line feasibility or safety/accessibility guarantee.

`tests/test_routing.py`: 32 offline provider tests. `tests/test_live_providers.py`:
opt-in Valhalla integration. `evals/runner/routing.py`: bounded live five-leg
evaluation over recorded real Chennai POIs; retained report cannot be overwritten.

## Commands/results

```powershell
uv run pytest tests/test_routing.py -q
# 32 passed in 0.31s
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.routing --discovery evals/reports/discovery-chennai-live-1.json --output evals/reports/routing-chennai-live-1.json
# exit 0; 5/5 reachable; 1948.04ms total
$env:GROUND_RULE_LIVE_ROUTING='1'
uv run pytest tests/test_routing.py tests/test_live_providers.py -q
# 33 passed, 1 skipped in 1.75s (32 offline + live routing; places opt-in unset)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
# Initial run failed Ruff E501, one 102-character message; corrected, no bypass.
# Final: Ruff pass; 69 files formatted; 231 passed, 2 skipped in 1.53s
# Schemas 17; contract eval 60/60; policy eval 85/85; TypeScript pass; Vite pass 1.42s
```

Live retained observation (`routing-chennai-live-1.json`):

| From | To | seconds | meters |
|---|---|---:|---:|
| public test origin | Paati Veedu (node/12473051001) | 733 | 1006 |
| Paati Veedu | origin | 716 | 1006 |
| origin | Panagal Park (node/2270331348) | 340 | 459 |
| Panagal Park | origin | 323 | 459 |
| Paati Veedu | Panagal Park | 1056 | 1465 |

This is provider ETA, not measured walking or a proven feasible outing. Return
is requested independently, never copied from outbound. Phase 2's 85 fixtures
continue to cover missing return, intermediate unreachable, return exceeding
duration, walking limits, UTC day boundaries and repeated local hours. RouteFact
is elapsed seconds without local-time arithmetic; deadline calculation stays in policy.

## Limits / references

Single pedestrian mode; no wheelchair assurance. Matrix deferred until batch
throughput needs it; five explicit legs are enough for the first templates.
OSM center coordinates may require access/entrance verification. Search cutoff
is 100m to avoid routing to a distant unrelated graph. Graph ETAs remain subject
to map quality and do not establish hours, prices or venue access.
No local Valhalla graph/offline routing has been demonstrated.

[Official API](https://valhalla.github.io/valhalla/api/route/api-reference/)
documents response semantics/error codes. Development endpoint:
https://valhalla1.openstreetmap.de; identifying X-Client-Id supplied as requested
by the [official repository](https://github.com/valhalla/valhalla).
Public demos are not an assumed production service. No model calls in routing.

## Final boundary review

Provider error codes coexisting with success facts, HTTP400 coexisting with
reachable metrics, and zero metrics between distinct requested coordinates are
now explicitly rejected. Six additional regressions bring the offline routing
suite to 38 tests. These were found by code/boundary inspection, not a claimed
new live outage. Final live integration rerun: 2 provider tests passed in 4.82s
(Overpass + Valhalla). Final repository check: 314 passed, 2 live tests skipped,
17 schemas, 60/60 contracts, 85/85 policy, Ruff/TypeScript/build pass. Exact
commands and final timings are in `overnight-handoff.md`.
