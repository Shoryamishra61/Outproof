# India production coverage campaign

The actual deployed API at `a519dc8f42494f75973a6a16948eda855875703b` was tested at **100 distinct India starting coordinates**, selected from real Photon search responses. All 100 had an actual compilation request; there were **0 accepted plans, 87 typed rejections and 13 temporary provider errors**. Deployment identity did not change within any case. Every attempted city, origin, input, timestamp, HTTP status, request ID, latency and full response is in `INDIA_100_BASELINE.json`.

Executed 2026-10-09 21:28–22:28 UTC (2026-10-10 02:58–03:58 IST). Departure was explicitly scheduled for 2026-10-10 10:00 IST. These are live software journeys, not physical visits or a claim that those venues are open at the overnight execution time. The initial harness used the wrong case for the typed vibe enum; two harness errors are retained in `INDIA_100_HARNESS_FAILURE.json`, and the corrected full campaign ran after its regression checks passed.

Command:

```powershell
uv run python -u -m evals.runner.india_public --output evals/reports/INDIA_100_BASELINE.json --departure 2026-10-10T10:00:00+05:30
```

The resumable runner spaces journeys at least 12 seconds apart, obeys production Retry-After, preserves every failure, validates returned contracts and independently applies the unchanged hard policy to any accepted plan. It never upgrades location search or a safe refusal to a successful outing. Duplicate actual origins and mixed deployments were audited after execution.

## Repair and source limits

Generic live enrichment was a no-op: unverified admission remained absent. Map identity is insufficient to prove admission, operating hours or actual pedestrian access. The repair adds a narrow, reusable official-garden normalizer backed by a reviewed registry; it does not grant all parks common facts.

- [Shanti Kunj, Sector 16](https://chandigarhtourism.gov.in/gardens/shantikunj): official daily 05:00–21:00, no entry fee. OSM park way `129720606`, pedestrian way `655074179`, inside access node `6137905894`.
- [Terraced Garden, Sector 33B](https://chandigarhtourism.gov.in/gardens/Terracedgarden): official daily 05:00–21:00, no entry fee. OSM park way `129460621`, pedestrian way `1078014066`, inside access node `9883600810`.

Every compilation freshly fetches the exact official page and both OSM ways. A changed title, sector, fee, schedule, private access, moved point or broken park/path containment fails closed. The mapped footway must cross the park boundary; it is not called a physically checked gate. India civil time is normalized to `Asia/Kolkata` from the reviewed Chandigarh jurisdiction, independently of user locale. Only main garden pedestrian paths are priced; food, parking, purchases and paid activities are excluded. Real outbound and return Valhalla requests still establish walking feasibility. Gemma ranks only plans accepted by the existing validator.

Actual local orchestration completed for both gardens at the current execution time with real sources, routes and authenticated Gemma: one plan each, eleven checks PASS, INR 0. Full receipts are in `INDIA_REVIEWED_LOCAL_LIVE.json`. These establish local source support; public deployment verification follows separately.

Other sources were rejected or retained as leads: Waghai has conflicting admission reports; Garden of Fragrance has conflicting official closing times; Rose Garden lacks fee/hour fields; an old BMC PDF cannot grant current admission to all municipal parks. Chennai's official Semmozhi public booking UI was closed until 09:00 IST; booking hours were not substituted for park hours or ticket prices. No authenticated API was bypassed and no booking/payment was attempted.

Local canonical command passed **4,936 Python tests, two opt-in external skips; 17 schemas, 60 structural cases, 85 policy cases, Ruff and TypeScript/Vite**. These remain controlled checks. Public free provider failures are real and retained. UI visual thesis remains a field notebook, with the same chosen pin, limits form and single proof-backed outcome. Source audit found zero high findings and one existing motion heuristic; the map uses nonanimated pan and global reduced-motion rules.

**BLOCKED — CRITICAL REQUIREMENTS UNMET** for a broad India release: zero baseline accepted journeys, many missing source fields and intermittent discovery. The added two-garden support cannot establish 100 working places. Physical India trials remain 0/3 UNEXECUTED, and the authenticated model endpoint still depends on a running laptop and temporary tunnel. No paid service was enabled.

## Production transport incident

The first public India browser and four API probes on `15e591d` returned actual 503; no plan was accepted. The failed browser capture is retained in `artifacts/release/public-india-shanti-kunj`. Diagnostics on `454eacb` identified `official_garden / ConnectTimeout / no HTTP response` at 2026-10-10T03:45:38Z, after both OSM requests completed. The protected model host now relays only the two fixed official HTTPS pages, with a 1 MiB bound, no redirects, serialized requests, original authority identity and a timestamp checked within 30 seconds. Parser and policy assertions are unchanged. Actual model/source authentication returned 401/401/200 after the verified proxy restart; receipt `INDIA_RELAY_AUTH_LIVE.json`. Public recovered compilation has not yet been verified in this checkpoint.
