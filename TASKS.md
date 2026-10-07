# Task Board

## P0 — Must ship

### Repo
- [x] monorepo initialized
- [x] CI lint + unit tests
- [x] `.env.example`
- [x] local setup script
- [ ] Render config

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
- [ ] 30 India cases
- [ ] 20 global cases
- [ ] parser score
- [ ] hard-constraint score
- [ ] hallucination check
- [ ] latency report
- [ ] markdown report

### Field test
- [x] blank forms and measurement script prepared (no actual results)
- [ ] free outing
- [ ] cheap friend outing
- [ ] date/small-group outing
- [ ] actual-vs-predicted table
- [ ] screen-time capture
- [ ] failure documented

### Submission
- [x] unpublished article skeleton, architecture diagram source and evidence table
- [x] demo shot list updated with explicit unverified gates
- [ ] final README
- [ ] architecture image
- [ ] demo video
- [ ] Sentry trace
- [ ] DEV post
- [ ] prize categories
- [ ] DevRelay session if useful

## P1 — Only after core green

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

## P2 — Post-hackathon

- [ ] accounts
- [ ] preference learning
- [ ] saved neighborhoods
- [ ] private group constraints
- [ ] user-contributed prices
- [ ] city packs
- [ ] native mobile

## Post-Phase-7 sprint

Fixture compiler, identity crosswalk, opening-hours parser, local Gemma valid-plan ranker, deterministic proof, gated API and fixture HOME/result/GO are implemented. These checked compiler/API/web items mean explicitly labelled development fixtures only. Public health remains false. See `evals/reports/post-phase-7.md` for executed counts and limitations. A complete identity-linked real Chennai price/hours/no-mall evidence pack remains the next live gate. Hidden backup, field tests, 50-case/10-city outing evaluation and hosted compilation remain unchecked.
