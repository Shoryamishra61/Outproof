# Build Order

## Rule

Build the smallest end-to-end compiler first.

Do not start with:
- logo
- animations
- auth
- voice
- Reddit ingestion
- map-heavy UI
- article prose

## Phase 0 — Bootstrap

- [x] create repo
- [x] copy build pack to root
- [x] initialize FastAPI
- [x] initialize React/Vite PWA
- [x] add `.env.example`
- [x] add lint/test commands
- [x] verify Ollama + Gemma structured output

Verified 2026-10-06 with explicit `gemma3:1b` override on local CPU.
The default `gemma4:e4b` remains unchanged and unverified. PWA setup is a
manifest/service-worker scaffold, not the cached outing demo. See
`evals/reports/phase-0.md`.

Exit:
- frontend boots
- API boots
- one schema-valid local Gemma call works

## Phase 1 — Contracts

Implement:
- Money
- ConstraintSet
- Evidence
- PlaceCandidate
- RouteFact
- CandidatePlan
- ValidationResult
- CompiledPlan
- PlanProof

Exit:
- invalid states are hard to represent
- money is currency-safe
- datetimes timezone-aware

Phase 1 contracts verified on 2026-10-06: 17 schemas, 16 passing tests,
60/60 synthetic structural eval cases. See `evals/reports/phase-1.md`.
Phase 2 is now verified separately in `evals/reports/phase-2.md`.

## Phase 2 — Deterministic validator

Implement before live discovery.

Tests:
- over budget
- over time
- unknown price strict mode
- estimated price strict mode
- excluded mall
- closed at arrival
- return-trip violation
- unsupported dietary proof
- excessive walk

Exit:
- validator rejects every invalid fixture
- zero model calls needed

Verified 2026-10-06: 85/85 synthetic policy cases (19 accepted, 66 rejected),
106 Phase 0–2 tests, unchanged 17 schemas. No real outings or provider integration.

## Phase 3 — Gemma parser

Create >=100 parser fixtures; run separate real local-model benchmarks.

Exit:
- schema-valid JSON
- hard/soft classification works
- malformed output fails closed

Verified 2026-10-07 on the stated 100-case synthetic-language gate:
Gemma 4 E2B QAT 82% raw exact hard/soft classification, 90% final guard success,
zero authoritative corruption/place fields, all eight unsupported requirements
retained. 169 repository tests pass. Accuracy is bounded by this authored suite;
see `evals/reports/phase-3.md`. The overnight queue subsequently authorized
Phases 4–7, verified in their separate reports; no Phase 0–3 re-bootstrap.

## Phase 4 — One-area discovery

Implement OSM/Overpass for one India area.

Exit:
- real candidates
- stable provider identity
- zero invented candidates

## Phase 5 — Routing

Phase 4 PASS: 39 live Chennai POIs, 30 offline tests + opt-in integration.
Raw price/hour/exclusion gaps preserved. See `evals/reports/phase-4.md`.

Valhalla:
- walking matrix
- distance
- return-trip accounting

Exit:
- physically impossible candidates rejected

## Phase 6 — Plan builder

Phase 5 PASS: five live directed Valhalla legs, offline route regressions and
opt-in live integration. No offline local graph demonstrated. See phase-5 report.

Start with:
1. free outing
2. one paid stop
3. paid stop + public walk

Exit:
- deterministic builder outputs candidates

## Phase 7 — Evidence + budget

Phase 6 candidate-builder PASS: all three synthetic templates; one real-data
candidate built but rejected by full policy. See phase-6 report.

Implement:
- VERIFIED
- BOUNDED
- ESTIMATED
- UNKNOWN

Add one enrichment provider.

Exit:
- strict mode never promotes weak price evidence

Phase 7 deterministic price normalization PASS; SerpApi adapter offline verified.
First accepted-real-outing/live enrichment BLOCKED by credential/identity and
price/hour/no-mall evidence gaps. The post-Phase-7 sprint authorizes compiler/ranker/proof/API/GO against labelled fixtures; only real success and global outing evaluation await the live gate. See `evals/reports/BLOCKED.md` and overnight handoff.

## Phase 8 — Compile

Wire:

`parse -> discover -> enrich -> route -> build -> validate`

Return all valid plans internally.

## Phase 9 — Gemma ranker

Input only valid plans.

Output:
- selected ID
- concise subjective reason

## Phase 10 — One-plan UI

- home
- compiling
- result
- Plan Proof
- GO
- failure

## Phase 11 — Eval expansion

Scale to:
- 50 scenarios
- >=10 cities

Exit:
- zero hard violations
- zero hallucinated displayed venues

## Phase 12 — GO mode

Minimal next instruction + external navigation handoff.

## Phase 13 — Field tests

3 India outings.

Collect real:
- planning time
- predicted/actual spend
- predicted/actual duration
- screen time
- failure

## Phase 14 — Submission polish

Only now:
- visual polish
- Sentry screenshots
- demo recording
- architecture image
- DEV post
