# Current release status

[The current Outproof release report](OUTPROOF_CURRENT_RELEASE.md) supersedes earlier whole-trip and coverage claims below. Final100: zero accepted,76 typed refusals,24 provider failures; independent evidence audit PASS, broad coverage FAIL. The current origin-confirmation repair is locally verified and public verification is pending.

--- Historical evidence ---

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

## Recovered public API verification

Build `91868df1457622a83ffdabbcc434f35804f70085`, CI `38021995707` PASS, both matching free Render deployments LIVE. Two actual current-time production compiles accepted one LIVE plan each: Shanti Kunj 5.290 s (`486284486cb64912ad757fbef37cbbad`) and Terraced Gardens 4.761 s (`bc45ea5f3615487284e40dd10152b2fb`). Both had eleven checks PASS, real Gemma ranking, fresh original authority/OSM evidence, two directed routes and no fixtures. Five actual negative requests returned 409 without an accepted plan: USD-vs-INR, 20-minute duration, zero walking allowance, a explicitly scheduled 21:01 IST closed visit, and unknown vegetarian evidence. All seven passed their independent unchanged-policy oracle, with deployment identity stable. Full controls/response/ID/timing receipts: `INDIA_REVIEWED_PUBLIC_LIVE.json`. These are two narrow supported public starting corridors, not the 100-area baseline becoming green or a physical outing.

The final relay canonical command passed 4,950 Python tests with two opt-in external skips, plus Ruff, 17 schemas, 60 structural and 85 policy cases and TypeScript/Vite. Matching CI ran 135 controlled browser checks. Public clean-browser proof/GO verification follows separately. The 09:00 IST freeze target was missed while the actual production source transport failure was repaired; it is not backdated as successful.

## Bengaluru reviewed source extension

Cubbon Park is an additional source-backed candidate, pending deployed verification. Its exact official general-park fee/hour rows are checked separately from Chandigarh pages. General admission06:00–18:00 is closed Mondays and second Tuesdays; special walkers/attraction hours are excluded. Fresh OSM park22895320 and pedestrianway1276833566 contain the mapped anchor11854682505; every footway vertex and segment must stay outside the separately fetched High Court boundary208686727. Private/permit court gates and a Press Club gate were rejected. Boundary touches fail closed; source/exclusion lineage remains visible. Actual local full LIVE orchestration passed at04:16UTC with real sources, routes and authenticated Gemma, eleven checks andINR0 (`CUBBON_LOCAL_LIVE.json`); current public support is not claimed until deployment tests pass. Actual new/legacy source transport401/401/200 is retained in CUBBON_RELAY_AUTH_LIVE.json. Canonical4,972Python/two external opt-in skips passed after the crossing regression.

The fresh69.36-second India demo was actually rechecked over publicHTTPS at04:11UTC:200/range206, exacthashmatch, video/voice decoded andplayed, keyboardfocus, six widths320/360/390/768/1024/1440, zero pageerrors. CI38022896878 and bothff39049 servicesLIVE; the identity/free-plan/model401/401/200 checkpoint passed.

## Verified Bengaluru extension — 2026-10-10

Build `f53f7894b3635918825ebd2feadb83389b4f8916`, CI [38023859778](https://github.com/Shoryamishra61/Outproof/actions/runs/38023859778). The provider initially reported the new deployment live while the public API still served the preceding build; those zero-compile precondition failures are preserved in `INDIA_DEPLOY_PROBE_INTERRUPTION.json`. A restart and exact-SHA free redeploy were followed by an actual matching version response. API `dep-db4s0vl9fdbs73amks8g` and web `dep-db4rse3rjlhs73a6df10` were observed live.

`CUBBON_PUBLIC_LIVE.json` records nine real requests with stable identity: two accepted current-time plans (reviewed access start, 5.382 seconds; original Bengaluru baseline origin, 4.598 seconds), then seven HTTP 409 refusals for currency, duration, walking, closing time, Monday, second Tuesday and unsupported diet. The accepted plans independently passed the unchanged policy oracle, contain one stop, use LIVE sources and have eleven PASS checks. Future Monday/Tuesday requests also involve the freshness horizon; the controlled schedule tests independently isolate those recurring closures. The source observations include the official general-hours row, free main-ground fee, fresh park/path geometry, excluded court boundary and two independent Valhalla legs.

`artifacts/release/public-india-cubbon/receipt.json` records a fresh public browser: typed Bengaluru search, initial INR budget without manual repair, actual Gemma parser and ranker, one plan, proof, GO, walking-map link, opt-in voice, back/next, keyboard submission and mobile 390px. Plan/GO took 7.029/7.516 seconds; no page errors or horizontal overflow. Physical access was not executed. The distinct currency widget check passed at 360/390/768/1024/1440px; the Singapore preset sets SGD and budget zero without currency conversion.

Canonical checks: 4,972 Python tests passed, two external opt-in tests skipped; 17 schemas, 60 structural and 85 policy fixtures, Ruff, TypeScript and Vite passed. Matching CI separately passed 135 controlled Chromium journeys. Exact-credential history/files scan checked 616 blobs and 640 files with zero findings; the new browser trace separately checked 47 archive entries and five JSON receipts with zero findings. These are bounded security checks, not a blanket guarantee.

An intermediate 100-area campaign was stopped after 19 actual cases and preserved in `INDIA_100_POST_REPAIR.json`: one accepted, seventeen typed refusals, one provider failure. It is explicitly incomplete. The Chandigarh start exposed the fixed 1 km discovery limit; actual local source/routing/Gemma execution with a discovery-only 3 km override returned a valid 71-minute outing with 41 walking minutes (limit 45). A full final campaign will run after the bounded-radius repair is verified and deployed. Do not combine incomplete outcomes with the original baseline. No paid service, physical trial or broad India coverage is claimed.


## Bounded discovery-radius repair

The compiler's fixed 1 km radius excluded a source-verified, feasible outing at the original Chandigarh city origin. An actual local discovery-only 3 km experiment fetched fresh evidence, two real Valhalla legs and Gemma selection: 2,461 walking seconds (45-minute cap), 4,261 total seconds (90-minute cap). The compiler now uses the provider's existing 3 km maximum; all facts and hard-policy gates remain unchanged. Actual working-tree orchestration without the experimental override also passed in 4.768 seconds (`CHANDIGARH_RADIUS_LOCAL_LIVE.json`). Deployment verification remains pending for this additional fix.

Regression checks exercise explicit synthetic origins beyond 1 km, preserving refusal at 30 walking minutes and acceptance at 45. The initial positive regression failed before the change; an intermediate fixture required consistent float distance evidence and its explicit 4 km distance budget, without altering validators. Final narrow checks: 62 passed. Full `./scripts/check.ps1`: 4,974 passed, two external opt-in skips, 17 schemas, 60 structural/85 policy fixtures, Ruff/format/TypeScript/Vite passed. Matching new CI and deployment are separate pending gates. The fresh UI source audit has zero high findings and one reviewed motion heuristic; physical GPS and human screen-reader execution remain unverified.

Primary-source research also preserves blocked venue facts in `INDIA_OFFICIAL_SOURCE_REVIEW.json`: Chennai Semmozhi Poonga's product prices conflict with its description; all-in admission, age 11 and recurring days remain unresolved. A fresh NDMC horticulture FAQ fetch at 04:43 UTC returned 200 (66,977 bytes), but supplies no affirmative admission tariff. Tourism's Lodi Tomb free entry and the operator's season-specific garden hours do not justify silently asserting all garden services are free. Neither venue is promoted to accepted support.
