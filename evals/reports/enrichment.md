# Optional SerpApi enrichment — implemented offline, live gate BLOCKED

Executed 2026-10-07. This is not a claim of live SerpApi access.

`services/api/app/enrichment.py` implements EnrichmentProvider with one bounded
authorized SerpApi place request. It requires an explicit recent OSM/DIRECT
provider_link `{provider:SERPAPI, place_id:...}`, exact returned provider ID/name
and coordinate agreement within provider serialization tolerance (1e-6 degrees).
No nearby-name heuristic creates an identity link. Missing credentials/linkage
return SOURCE_TEMPORARILY_UNAVAILABLE before any request.

Available operating status, raw hours, ratings/count and raw price metadata are
retained with source/ref/time through existing Evidence. Missing fields stay null.
Operational price/opening proofs are not overwritten or fabricated from metadata.
Price-level strings are not exact mandatory-cost bounds; open-now isn't dwell
availability. Conflicting enrichment fails closed. Repeated identical metadata
does not refresh old observation timestamps. Reviews, photos, related-place
payloads and private exception/request URLs are never retained by this adapter.

`tests/test_enrichment.py` uses synthetic provider records and MockTransport:
26 tests cover success, metadata missing, wrong identity/coordinates, malformed
numeric values, unresolved/weak/conflicting/stale linkage, conflicts, missing
credential, HTTP error, timeout and secret redaction.

```powershell
uv run pytest tests/test_enrichment.py -q
# 26 passed in 0.31s
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
# Ruff pass; 79 files formatted; 289 passed, 2 skipped in 1.59s
# Schemas 17; structural contracts 60/60; policy fixtures 85/85
# TypeScript pass; Vite production pass in 1.42s
uv run python -c "import os; print({k:bool(os.getenv(k)) for k in ['SERPAPI_API_KEY','SENTRY_DSN','VALHALLA_BASE_URL']})"
# All false; presence-only check, no credential printed. No .env file exists.
```

Official field references: [SerpApi place results](https://serpapi.com/maps-place-results)
and [Google Maps API](https://serpapi.com/google-maps-api).
No Google page scraping, reviews API, trial-account creation or API charge was
performed. An authorized credential alone will not prove completeness of price,
usable dated hours or no-mall containment. Current OSM candidates also lack an
explicit cross-provider link. Those are real evidence gaps to resolve before
the compiler/one-plan API/UI gates can advance. Existing direct stronger facts
must be preserved; tests do not establish production identity-link coverage.
