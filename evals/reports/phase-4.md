# Phase 4 — OSM discovery

Acceptance: PASS for discovery, not outing compilation. Executed 2026-10-07.

## Changed files and behavior

- `services/api/app/places.py`: PlacesProvider protocol and bounded Overpass adapter.
  Normalizes named restaurant/cafe/park records into unchanged PlaceCandidate.
  Preserves OSM identity, node or bounding-box-center coordinates, categories,
  original tags, cuisine/raw hours, edit/version/database metadata and fetch time
  through Evidence. MEDIUM indicates community-maintained mapping, not venue verification.
  Unknown prices/opening windows remain unknown; diet requires positive diet tags.
- `tests/test_places.py`: 30 offline synthetic tests, including missing facts,
  malformed metrics, unsupported categories, exact identity duplicates, conflicting
  duplicates, timeout/HTTP/JSON errors, and radius bounds.
- `tests/test_live_providers.py`: explicitly marked, opt-in live integration.
- `evals/runner/discovery.py`: bounded live evaluator, refuses report overwrite.
- `pyproject.toml`: registers integration marker. No dependencies or schemas changed.

## Exact commands/results

```powershell
uv run pytest tests/test_places.py -q
# 30 passed in 0.32s
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.discovery --output evals/reports/discovery-chennai-live-1.json
# exit 0; 39 POIs; 3484.96 ms including request + normalization
$env:GROUND_RULE_LIVE_PLACES='1'
uv run pytest tests/test_places.py tests/test_live_providers.py -q
# 31 passed in 3.24s (30 offline + 1 live)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
# Ruff pass; 65 files formatted; 199 passed, 1 live test skipped in 1.47s
# 17 schemas; structural contracts 60/60; policy fixtures 85/85
# TypeScript strict pass; Vite production pass, 1.45s
```

Live evidence: `discovery-chennai-live-1.json`. Public test center 13.0418,
80.2341, T Nagar, Chennai; 1000m radius. Repository had a Chennai/SRM target
label but no canonical real SRM coordinates, so this explicit Chennai center
was used. Returned IDs include osm:node/2270331348 (Panagal Park) and
osm:node/12473051001 (Paati Veedu). These are provider observations, not field
visits or endorsements. No model calls.

## Limits and source policy

Identity deduplication handles repeat provider IDs, rejects contradictions;
distinct node/way identities representing a possible same physical venue remain
separate. Names alone cannot safely establish equivalence. Ways/relations use
Overpass bounding-box centers, not asserted entrance coordinates.
Raw opening-hours expressions are preserved, not guessed into visit windows.
No positive absence-of-mall evidence is created. Park category does not prove
public access, zero price, open hours, dietary suitability or safety.
Malformed supported records fail the batch closed; unnamed/unsupported records
are explicitly outside discovery output. No provider outage fallback invents data.

Attribution: © OpenStreetMap contributors, ODbL 1.0; see
[OSM copyright](https://www.openstreetmap.org/copyright).
Query uses [documented Overpass output](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL).
Only small development checks were run. Public instances are not the planned
production backend: [Overpass commons policy](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html).
No production, global coverage, browser or real outing gate is claimed.
