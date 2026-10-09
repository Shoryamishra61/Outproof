# Potheri compilation incident

On 2026-10-09 at 20:23 UTC, production `3dd2dd95` returned readiness HTTP 200 with `compilation_available=true`, then a Potheri compile returned HTTP 503 `SOURCE_TEMPORARILY_UNAVAILABLE` in 0.58 seconds (request `c4f933b4f1084f9a8ff20237b9480991`). The same bounded Overpass query returned HTTP 200 from the developer computer. Readiness checked only the reviewed Singapore source/route; it did not verify general discovery or a selected Potheri outing. The UI incorrectly described this as “live mode ready.”

The repaired provider serializes recovery probes, preserves cooldown for network failures and incomplete query results, clears cooldown on complete valid responses, reports a retry interval and logs only exception class/HTTP status. Neither coordinates nor query text enter these diagnostics. Readiness now states its limited scope; the UI separately displays failed compilation. Missing evidence is distinguished from a temporary provider outage.

The three named Potheri map identities found in the bounded query lack admission/price and operating-hours facts. These are discovery leads, not supported outings. A bounded official-source search found no sufficient venue-specific admission and hours proof. This does not prove no such source exists. Validation and exactly-one-plan rules remain unchanged.

Local `./scripts/check.ps1`: 4,903 passed, two opt-in skips; 17 schemas, 60 structural cases, 85 policy cases, Ruff and TypeScript/Vite passed. `npx --prefix apps/web playwright test --config apps/web/playwright.config.ts`: 135 controlled browser checks passed, including a source outage followed by successful fixture recovery with controls retained. These are controlled automated checks, not real field usage. The first run exposed an unnecessary internal return-contract change; that change was removed and the entire command passed. Deployed verification is pending. Source UI audit: zero high findings; one pre-existing motion heuristic requires human review. Exact-value secret scan: 490 history blobs and 564 working files/bundles/reports/logs, zero leaks detected.

Production build `a343e4e1299cf0eeaa455a0c90d63cf9c0b4d2f4` passed [CI 37987600830](https://github.com/Shoryamishra61/Outproof/actions/runs/37987600830). Both services deployed. A real Potheri browser run reproduced HTTP 503; the new technical log showed `ConnectError`, without an HTTP response. Its exact DNS/TLS/socket cause was not determined. No certificate verification was disabled. An alternative public Overpass service was tested with the same bounded query, then only `OVERPASS_URL` changed on the existing free API service. Deployment `dep-db4l0ovlot8c73beq9o0` went live.

The next real public Potheri browser run (request `2e5ed40ab75e4550aec9983c2c40e2a3`) returned HTTP 409 `NO_GROUNDED_CANDIDATES`, rather than an outage. Render logged three discovered identities in 12.205 seconds. This verifies discovery recovery, **not an accepted Potheri outing**. The actual browser displayed the missing-evidence explanation, retained limits, displayed no plan/GO, supported keyboard submission, had no page exceptions and no overflow at 320/390/1440 pixels. The first smoke script used an over-specific currency selector and timed out; its corrected accessible-role selector passed. These receipts and a real screen recording remain in `.tools/potheri-public`.

A separate actual production parser/ranker/source/route check returned HTTP 200, exactly one stop and eleven hard checks PASS in 20.811 seconds (request `ca78fe90eb784fb187e458a5d1591e44`). Departure was explicitly future-dated to 2026-10-10 09:00 Singapore time. This is a supported Singapore API plan, not a current Potheri outing or physical trial. `.tools/potheri-gemma-production.json` retains the full proof.

Visual thesis remains a field notebook: one chosen starting pin, a plain limits form and one proof-backed outcome. The incident repair uses the existing ink/paper/grass tokens, in-flow error text and a distinct technical status; no new cards, feeds or animation. The real mobile screenshot was inspected. Existing global reduced-motion CSS covers the source audit's motion heuristic.

| Capability | Status | Evidence |
|---|---|---|
| Potheri origin search and map discovery | PASS in executed run | Real Photon lookup and three OSM discovery identities from Render |
| Potheri accepted outing | BLOCKED | No verified admission/price and operating-hours facts for these candidates |
| Failure/status presentation | PASS in executed run | Real public error and keyboard/mobile/desktop checks; no “live mode ready” claim |
| Gemma parser/ranker | PASS in executed run | Future-dated supported Singapore API plan; eleven hard checks, real inference |
| Worldwide accepted outings | BLOCKED | Discovery/location search is not outing coverage |
| Physical trials | UNEXECUTED | Software checks and screen recordings do not replace field trials |

The configured endpoints are public community services with no uptime guarantee; the authenticated model tunnel still depends on this laptop. No paid service was enabled.

## Repeat failure and bounded recovery

Final-build repeat at `2200b6f6cd5680e5f063c0ad4b453c679d0d3131` returned another HTTP 503 (request `3c44abddc03345c88ef36f88d944d981`). The actual upstream result was HTTP 504. The previous successful discovery run therefore does **not** establish stable discovery availability. The real browser still displayed the correct failure, retained limits and no plan/GO, with no page exceptions or overflow at 320/390/1440 pixels. Computed error/status text contrasts were 11.859:1 and 5.948:1. Both services matched green CI 37988737783; authentication remained 401/401/200.

Recovery now attempts at most two requests, separated by one second, for connection/timeouts and HTTP 502/503/504 without a server Retry-After. It never immediately retries access denials, rate limits, malformed/incomplete data or unknown operational facts. A valid server Retry-After (seconds or HTTP date) is respected with a minimum 60-second cooldown. No facts from partial responses are merged. Eleven additional controlled checks cover transient recovery, private-safe diagnostics, serialization and server cooldown. `./scripts/check.ps1` then passed 4,914 tests/two opt-in skips, 17 schemas, 60 structural cases, 85 policy cases, Ruff and TypeScript/Vite. Production verification of this final retry change is pending; the recorded upstream 504 remains a real failure.
