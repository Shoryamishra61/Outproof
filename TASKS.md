# Task Board

## Current overnight release — 2026-10-09 IST

This section supersedes earlier phase claims below, including withdrawn Anna Nagar acceptance, worldwide success, disabled public compilation and unexecuted CI. Uppercase final reports are authoritative for current evidence.

- [x] Free public Render frontend/API; actual supported NParks/OSM/Valhalla/Gemma/proof/GO browser execution
- [x] 4,879 Python checks; 17 schemas; 60 structural / 85 policy fixtures; Ruff/TS/build
- [x] 4,096 distinct controlled compiler journeys; 300 adversarial; 300 property examples; four critical-gate mutants detected
- [x] 124 controlled Chromium journeys; GPS/error/retry/cancel/keyboard/mobile/zoom/audio; stale return deadline rejected
- [x] 50 fresh real global attempts across 19 cities: zero accepted, 40 refused, 10 provider failures; no global operational claim
- [x] 20 bounded real production probes with three supported compiles, one parser plus ranker
- [x] Actual authenticated proxy outage/restart and public readiness recovery; known-green API/web rollback and live browser afterward
- [x] Actual Sentry grounding/rank spans, SerpApi discovery, ElevenLabs generation/playback, Copilot review and manual Entire capture
- [x] Backboard failure investigated: Memory/RAG-only free credits block chat; no billing enabled, no successful inference claim
- [x] 65-second actual public demo recorded; local range/decode/viewport/focus/audio checks passed; release reports and DEV draft prepared
- [x] Fresh public demo-asset range/hash/decode/playback verified on checked deployed release; final evidence update gets its own CI/deployment check
- [ ] Stable/always-on model hosting: no existing domain, no paid hosting authorized; protected temporary fallback disclosed
- [ ] Three physical India trials and field Screen Ratio: UNEXECUTED/unmeasured
- [ ] Author's final DEV review and publication: reserved to the user

## P0 â€” Must ship

### Repo
- [x] monorepo initialized
- [x] CI lint + unit tests
- [x] `.env.example`
- [x] local setup script
- [x] Render config (`render.yaml` created with API and web services)

### Contracts
- [x] Money
- [x] ConstraintSet
- [x] Evidence
- [x] PlaceCandidate
- [x] RouteFact
- [x] CandidatePlan
- [x] ValidationResult
- [x] CompiledPlan
- [x] PlanProof

Also implemented HardConstraint, SoftConstraint, PriceEvidence, PlanStop,
ValidationCheck, Coordinates, OpeningWindow, and CompilationFailure. Phase 1
has 17 generated schemas, 16 passing tests, and 60 passing synthetic contract
cases; these are not the 50-case global outing benchmark. See
`evals/reports/phase-1.md`. Only structural contracts are complete; the
deterministic feasibility validator is now verified in Phase 2; see
`evals/reports/phase-2.md` (85 synthetic cases, no real outings).

### Domain
- [x] currency-safe money
- [x] duration budget
- [x] arrival/open-hours validation
- [x] walking limit
- [x] exclusions
- [x] dietary evidence policy
- [x] budget proof policy
- [x] return-trip accounting

Return-trip accounting covers route-chain structure and derived totals,
including unknown totals for unreachable legs. Phase 2 checks hard
duration/deadline feasibility; Phase 5 now supplies live Valhalla route facts.

### Gemma
- [x] Ollama adapter
- [x] parser prompt
- [x] structured output validation
- [x] malformed-output failure
- [x] ranker prompt
- [x] selected-ID validation
- [x] parser benchmark (100 cases per run; scoped acceptance, see phase-3 report)

Phase 3 acceptance verified 2026-10-07 with explicit `gemma4:e2b-it-qat`:
82/100 raw exact hard/soft classifications; 90/100 final guard returns, zero
control corruption/place fields, 8/8 unsupported source retentions. This is
synthetic-language CPU inference, not real outing or held-out accuracy.
See `evals/reports/phase-3.md`; compiler availability remains false.

### Places
- [x] OSM/Overpass adapter
- [x] provider normalization
- [x] duplicate resolution (provider ID; physical node/way conflation unsupported)
- [x] category mapping
- [x] source timestamps

Phase 4: 30 offline tests + opt-in live integration; 39 real Chennai POIs.
See `evals/reports/phase-4.md`. Discovery does not establish outing feasibility.

### Routing
- [x] Valhalla client
- [ ] walking matrix (deferred; bounded initial templates use explicit legs)
- [x] route facts
- [x] unreachable handling
- [x] return trip

Phase 5: 32 offline routing tests and live five-leg Chennai integration.
See `evals/reports/phase-5.md`. This is routing evidence, not a field outing.

### Enrichment
- [x] SerpApi adapter (offline verified; live credential/identity linkage blocked)
- [x] price proof mapping (explicit aggregate attestations; live price source absent)
- [x] opening status
- [x] ratings metadata (raw available provider fields; offline tests)
- [x] source provenance
- [x] graceful provider failure

Live enrichment remains blocked; OSM hours now have a tested interval parser with explicit timezone context; price levels/open-now do
not establish paid visit feasibility. See `evals/reports/enrichment.md` and
`evals/reports/BLOCKED.md`.

### Compiler
- [x] plan templates
- [x] plan builder
- [x] validator pipeline
- [x] primary selection
- [ ] hidden backup
- [x] Plan Proof renderer

Phase 6: three synthetic templates verified, one real-provider Chennai candidate
built and honestly rejected for missing price/hours/exclusion evidence. See
`evals/reports/phase-6.md`. The real accepted-outing gate remains unchecked. The post-Phase-7 fixture compiler is implemented separately.

### API
- [x] `POST /v1/plans/compile`
- [x] typed errors
- [x] health endpoint
- [ ] request ID
- [x] timeouts

### Web
- [x] home
- [x] compiling
- [x] result
- [x] proof drawer
- [x] GO mode
- [x] failure states
- [x] PWA manifest

### Evaluation
- [x] 30 India cases (Chennai 12, Bengaluru 4, Mumbai 3, Delhi 3, Hyderabad 3, Pune 2, Kolkata 1, Kochi 1, Jaipur 1)
- [x] 20 global cases (London 2, New York 2, San Francisco 2, Singapore 2, Tokyo 2, Berlin 2, Paris 2, Sydney 2, Toronto 2, Dubai 2)
- [x] parser score
- [x] hard-constraint score (0 hard violations across 50 cases)
- [x] hallucination check (0 hallucinated venues across 50 cases)
- [x] latency report (average compile latency 24,129 ms)
- [x] markdown report (`evals/reports/global-eval-results.md` & `evals/reports/global-eval-results.json`)

### Field test
- [x] blank forms and measurement script prepared (no actual results)
- [ ] free outing
- [ ] cheap friend outing
- [ ] date/small-group outing
- [ ] actual-vs-predicted table
- [ ] screen-time capture
- [ ] failure documented

### Submission
- [x] unpublished article skeleton, architecture diagram source and evidence table (`docs/DEV_DRAFT.md` fully updated)
- [x] demo shot list updated with explicit unverified gates
- [ ] final README
- [ ] architecture image
- [ ] demo video
- [ ] Sentry trace
- [ ] DEV post
- [ ] prize categories
- [ ] DevRelay session if useful

## P1 â€” Only after core green

Phase 0 verified locally on 2026-10-06; CI is configured but has not run on
GitHub. That historical smoke used explicit `gemma3:1b` CPU override; its
then-default `gemma4:e4b` was unverified. Phase 3 parser runs and the later
post-Phase-7 fixture compiler/ranker smokes are recorded separately. The current
development default is the measured `gemma4:e2b-it-qat`.
See `evals/reports/phase-0.md` for evidence and limitations.

- [ ] optional audio GO cue
- [ ] one reroll with reason
- [ ] community/local ranking signal
- [ ] anti-chain/local mode
- [ ] cached-area offline demo

Bounded local Gemma + cached provider component rejection demonstrated; this
does not check the full offline outing gate. See `evals/reports/cached-demo.md`.
- [ ] revalidate before GO

## P2 â€” Post-hackathon

- [ ] accounts
- [ ] preference learning
- [ ] saved neighborhoods
- [ ] private group constraints
- [ ] user-contributed prices
- [ ] city packs
- [ ] native mobile

## Post-Phase-7 sprint

Fixture compiler, identity crosswalk, opening-hours parser, local Gemma valid-plan ranker, deterministic proof, gated API and fixture HOME/result/GO are implemented. These checked compiler/API/web items mean explicitly labelled development fixtures only. Public health remains false. See `evals/reports/post-phase-7.md` for executed counts and limitations. A complete identity-linked real Chennai price/hours/no-mall evidence pack remains the next live gate. Hidden backup, field tests, 50-case/10-city outing evaluation and hosted compilation remain unchecked.

## Live acceptance search â€” 2026-10-07

- [x] verified baseline and created safe checkpoint `a8daccf`
- [x] refreshed three bounded Chennai discovery areas (273 unique identities)
- [x] bounded official-source crawl with robots/access restrictions and one regression check
- [ ] WITHDRAWN: prior accepted LIVE Chennai outing lacked sufficient admission/hours evidence (`osm:way/24240071`, Anna Nagar Tower Park, â‚¹0, 60.8 min, 11/11 hard checks PASS)
- [x] end-to-end browser walkthrough (`HOME -> COMPILE -> ONE PLAN -> PLAN PROOF -> GO`) with 0 console errors and verified LIVE badges
- [x] global evaluation: 50 scenarios across 19 global cities (0 hard violations, 0 hallucinations, 0 price guessing, 1 plan invariant held)
- [x] deployment configuration (`render.yaml` blueprint with public compilation disabled by default)

## Final Release Engineering & QA Audit â€” 2026-10-08

- [x] Re-audited Anna Nagar Tower Park proof: corrected factual exaggeration from ">100 acres" to official GCC metric: 57,927 mÂ² (~14.31 acres) per GCC Parks List PDF (Zone 8, Division 100).
- [x] Repaired operating hours defect in `live.py`: replaced synthetic dynamic window with calendar schedule (05:00 to 21:00 IST in `Asia/Kolkata`); verified interval boundaries.
- [x] Added `tests/test_park_proof_audit.py` (4 tests) covering area unit math, open/closed interval boundaries, dwell exceeding closing time, and provider fields.
- [x] Added transparent origin selection to web UI ("Try verified Chennai example" vs "Use device location (GPS)") with geolocation error handling.
- [x] Re-ran browser E2E verification across Desktop and Mobile viewports with 0 console errors.
- [x] Completed canonical verification suite: 431 passed, 2 skipped (433 collected); Ruff clean (120 files); 60/60 contracts; 85/85 policy; TypeScript & Vite build clean.
- [x] Authored 6 canonical release reports in `evals/reports/`:
  - `evals/reports/final-requirements-matrix.md`
  - `evals/reports/final-evidence-audit.md`
  - `evals/reports/final-release-audit.md`
  - `evals/reports/final-e2e-results.md`
  - `evals/reports/final-production-smoke.md`
  - `evals/reports/final-release-verdict.md`
- [x] Re-formatted `docs/DEV_DRAFT.md` to match official Hacktoberfest Week 1 DEV.to template.
- [x] Final release verdict established: **CONDITIONAL RELEASE â€” DISCLOSED LIMITATIONS**.

