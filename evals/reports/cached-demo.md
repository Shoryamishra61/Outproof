# Bounded cached component demo — not an offline verified outing

Executed 2026-10-07 locally; source UTC timestamps preserved verbatim.
This independent work uses completed parser/policy/providers without advancing
the blocked accepted-outing compiler gate.

```powershell
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.cached --discovery evals/reports/discovery-chennai-live-1.json --routing evals/reports/routing-chennai-live-1.json --templates evals/reports/templates-chennai-real-data-1.json --model gemma4:e2b-it-qat --output evals/reports/cached-chennai-component-demo-1.json
# exit 0: actual local Gemma, 17406.47ms (includes model reload/call)
# all authoritative controls preserved; 0 external discovery/routing requests
# one cached candidate validated; 0 accepted outings
uv run pytest tests/test_field_metrics.py tests/test_cached_demo.py -q
# 13 passed in 0.41s at this checkpoint (11 metric + 2 cached harness tests)
uv run python scripts/field_metrics.py docs/field-test-form.json
# expected exit 2: blank planning timestamp; no field measurements invented
```

Saved report: `cached-chennai-component-demo-1.json`. INR50000/person,
90 minutes, FRIEND/2, public Chennai origin/departure unchanged by actual model.
Vegetarian/no mall preserved, quiet/talk preferences parsed. Optional SerpApi
credential failure exercised with a transport that forbids external requests.
The same real-data evidence gaps still reject the candidate. Existing cached
observations are never refreshed to pretend current facts. Later replays can
add ROUTING failure at the policy's 15-minute freshness boundary.

Cached OSM observations derive from OpenStreetMap, © OpenStreetMap contributors,
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), with original IDs and
[attribution](https://www.openstreetmap.org/copyright) in the discovery artifact.
Route observations come from bounded FOSSGIS Valhalla development checks;
they do not prove that a local graph exists or that current routes remain valid.

This proves local open-weight interpretation plus cached evidence validation
without proprietary AI/place/routing requests during the demonstrated command.
It does not prove a usable fully offline plan, cache refresh, an offline map UI,
local Valhalla, or an installed-machine cold start without dependencies/model
weights. Those gates remain untested/blocked. No model results were pooled with
the 100-case benchmark. No private user input/location history was recorded.
