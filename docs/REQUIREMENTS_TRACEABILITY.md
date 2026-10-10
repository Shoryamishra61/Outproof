# Requirements traceability

Current Outproof receipts take precedence over the historical populations below. `OUTPROOF_BROWSER_REVIEW.md` records actual unmocked public parser/ranker, source proof, GO/voice, keyboard, map and mobile execution, with explicit limitations. The final fixed-build India campaign remains in progress; its checkpoint is `INDIA_100_FINAL.json`. A typed refusal is not working coverage. Physical India visits and human device/screen-reader sessions remain UNEXECUTED.

| Flow | Implementation | Evidence | Current scope |
|---|---|---|---|
| Distinct same-name starting points | geocoding.py; LocationPicker.tsx | test_geocoding.py; location.spec.ts; outproof-origin-refusal-recovered/receipt.json | Real public search/selection; no outing acceptance implied |
| Mapped route-start confirmation | routing.py; models.py; main.tsx; generated failure schema | test_routing.py; test_contracts.py; location.spec.ts; OUTPROOF_CONFIRMED_ORIGIN_LOCAL.json | Real local parser/source/routing/ranker recovery; public verification pending |
| Every limit preserved after selection | main.tsx | location.spec.ts compares submitted controls before/after confirmation | Controlled; origin/departure alone change |
| Map initialization / source failure / GPS denial | LocationPicker.tsx; main.tsx | OUTPROOF_FINAL_MAP_PUBLIC.json; actual public refusal receipt | Public map loading/tiles and real browser permission denial; physical GPS accuracy unmeasured |
| Exact deployed build with actual accepted compilation | production.yml; verify_production.py | OUTPROOF_FINAL_PRODUCTION_GITHUB.json | Real public model, sources, routes and proof; closed venues/outages fail the workflow |
| New demo download, decode and play | demo.html; demo.webm | release-demo-public.json | Actual HTTPS, range, hash, playback and responsive player; no physical footage |

Executed populations are separate: canonical controlled checks, 4,096 synthetic compiler journeys, 124 controlled Chromium journeys, 50 real global attempts, bounded real public probes and zero physical outings. Source filenames are relative to their existing app/domain/test directories. A controlled oracle is not a live geographic capability.

| ID | Requirement | Implementation | Executed oracle / artifact | Evidence status |
|---|---|---|---|---|
| U01 | First visit, clean browser | apps/web/src/main.tsx | apps/web/tests/journeys.spec.ts; public-corrected/receipt.json | PUBLIC PASS |
| U02 | Explicit Chennai origin | main.tsx; parser.py | tests/test_parser.py; journeys.spec.ts | CONTROLLED; Chennai acceptance unsupported |
| U03 | Geolocation allowed | main.tsx | recovery.spec.ts gps | CONTROLLED PASS; consented synthetic GPS |
| U04 | Geolocation denied | main.tsx | journeys.spec.ts geodenied | CONTROLLED PASS |
| U05 | Geolocation timeout / low accuracy | main.tsx | recovery.spec.ts lowaccuracy/gpstimeout | CONTROLLED PASS |
| U06 | Zero budget, solo, 60 min | compiler.py; policy.py | test_journeys.py; release-production-probes.json | PUBLIC verified-free supported scope |
| U07 | ₹500/person, two friends | models.py; policy.py | test_pricing.py; test_journeys.py | CONTROLLED PASS |
| U08 | ₹500 total, four people | models.py; policy.py | test_pricing.py; test_journeys.py | CONTROLLED PASS |
| U09 | Food required and unknown all-in cost | parser.py; compiler.py | test_parser.py food requirement; test_compiler.py | CONTROLLED PASS |
| U10 | Food optional with zero verified paid places | compiler.py | test_compiler.py; test_journeys.py | CONTROLLED PASS |
| U11 | Vegan/vegetarian or allergen constraint | parser.py; policy.py | test_parser.py; test_policy.py | CONTROLLED PASS; dietary venue evidence unsupported live |
| U12 | No malls | policy.py | test_policy.py; test_enrichment.py | CONTROLLED PASS; unknown exclusion fails closed |
| U13 | Quiet date | ranker.py | test_ranker.py; release-production-probes.json | Real ranker use; subjective quiet not independently guaranteed |
| U14 | Walking limit 500m | policy.py; routing.py | test_routing.py; test_journeys.py | CONTROLLED PASS |
| U15 | Return by 9 PM | compilation.py; main.tsx | test_compilation.py deadline; test_policy.py; release-departure-browser.json | CONTROLLED backend and deployed-UI delayed deadline rejection PASS |
| U16 | Near closing hour | hours.py; main.tsx | test_hours_pipeline.py; test_hours.py | CONTROLLED PASS |
| U17 | Weekend, holiday, hours exception | hours.py | test_hours.py unknown holiday/solar rules | CONTROLLED PASS; no holiday certainty invented |
| U18 | Cross-midnight / DST location | hours.py; policy.py | test_hours.py; test_hours_pipeline.py DST | CONTROLLED PASS |
| U19 | Reversed route differs from outbound | routing.py | test_routing.py independent return; public compile-response.json | PUBLIC directed route proof |
| U20 | Park with optional paid tower | live.py | tests/release/test_live_sources.py; FINAL_EVIDENCE_AUDIT.md | CONTROLLED PASS; prior unsupported Anna Nagar claim withdrawn |
| U21 | No candidates | compiler.py | test_compiler.py; FINAL_GLOBAL_EVAL.json | LIVE typed refusals |
| U22 | No verified all-in paid price | policy.py; compiler.py | test_pricing.py; test_compiler.py | CONTROLLED PASS |
| U23 | Route provider down | routing.py | test_routing.py; FINAL_GLOBAL_EVAL.json | CONTROLLED outage/recovery; real provider failures recorded |
| U24 | Model unavailable / invalid JSON | model_bridge.py; ranker.py | test_model_bridge.py; test_ranker.py; release-model-recovery.json | Controlled malformed/timeout; actual recovery receipt |
| U25 | Search/review prompt injection | parser.py; search.py | test_parser.py; test_search_leads.py | CONTROLLED PASS; rejected local injection attempt recorded |
| U26 | Compiling then edit constraints | main.tsx | recovery.spec.ts cancelstale | CONTROLLED PASS |
| U27 | Double click / rapid submit | main.tsx; main.py | recovery.spec.ts double; release-controlled-load.json | CONTROLLED PASS |
| U28 | Proof expand/collapse | proof.py; main.tsx | journeys.spec.ts success; public-corrected/receipt.json | PUBLIC PASS |
| U29 | GO / Next / Back / resume | main.tsx | public-corrected/receipt.json; journeys.spec.ts | PUBLIC next/back PASS; reload clears transient state |
| U30 | Offline or page refresh mid-GO | main.tsx | recovery.spec.ts reload/retry; test_cached_demo.py | CONTROLLED PASS; offline new compilation not supported |
| U31 | Mobile 320/375/390/768 widths | style.css | 124 browser journeys; public-corrected/mobile.png | CONTROLLED 10 widths and public 390 PASS |
| U32 | Keyboard only and screen reader | main.tsx; style.css | journeys.spec.ts keyboard; public-corrected/receipt.json | Keyboard/focus PASS; human screen-reader session UNEXECUTED |
| U33 | Public production URL, fresh session | main.py; live.py; ranker.py | release-production-probes.json; public-corrected/receipt.json | PUBLIC PASS |
| U34 | Unsupported city or country | live.py | FINAL_GLOBAL_EVAL.json | 50 real cases: 0 accepted / 40 rejected / 10 provider errors |
| U35 | Provider 429/500/slow response | places.py; routing.py; main.py | test_runtime.py; test_live_providers.py; release-controlled-load.json | CONTROLLED bounded failure/recovery PASS |
| U36 | Mixed language / unusual currency | parser.py; models.py | test_parser.py; test_pricing.py; test_journeys.py | CONTROLLED currencies; real multilingual model quality not established |
| U37 | Group = 1, 2, 5 and maximum group | models.py; policy.py | test_contracts.py; test_journeys.py | CONTROLLED party arithmetic PASS; capacity unknown fails closed |
| U38 | Malicious source HTML and map redirect | crawl_public_sources.py; main.tsx | test_public_crawl.py; test_boundaries.py | CONTROLLED redirect/SSRF and escaped-content checks |
| U39 | All partner adapters unconfigured | main.py | test_bootstrap.py; test_compile_api.py; test_telemetry.py | CONTROLLED optional disabled startup PASS |
| U40 | Production restart/new deploy | Render; main.py | release-restart-api.json; public-rollback/receipt.json; public-demo/receipt.json | Restart accepted; actual known-green rollback and forward restore with supported public browser PASS |
