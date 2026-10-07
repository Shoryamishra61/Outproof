# MASTER BUILD PROMPT — Ground Rule

You are the principal engineer responsible for implementing **Ground Rule** end-to-end.

## Read first

Read in this exact order:

1. `AGENTS.md`
2. `PRODUCT_SPEC.md`
3. `ARCHITECTURE.md`
4. `docs/PLAN_PROOF.md`
5. `docs/DATA_SOURCES.md`
6. `EVALS.md`
7. `BUILD_ORDER.md`
8. `TASKS.md`

Treat `AGENTS.md` as authoritative.

## Objective

Build a production-quality Hacktoberfest 2026 prototype where:

> A user enters time, budget, party, vibe, location, and hard constraints.  
> Ground Rule returns exactly one real-world outing that has passed deterministic validation.  
> Then the UI minimizes itself so the user leaves.

Core invariant:

> **LLMs interpret. Data grounds. Code verifies.**

## Build method

Do not generate the entire app blindly.

Work phase by phase.

For every phase:
1. inspect existing files
2. implement the smallest complete slice
3. add tests
4. run tests
5. run relevant evals
6. report exact results
7. update `TASKS.md`
8. continue only if green

Never fabricate pass status.

## First implementation target

Build this vertical slice before visual polish:

```text
structured controls + free text
        ↓
Gemma parser
        ↓
ConstraintSet
        ↓
provider fixture / OSM adapter
        ↓
PlaceCandidate[]
        ↓
route fixture / Valhalla adapter
        ↓
RouteFact[]
        ↓
CandidatePlan builder
        ↓
deterministic validator
        ↓
valid plans only
        ↓
Gemma ranker
        ↓
exactly one CompiledPlan + PlanProof
```

Initially it is acceptable to use realistic provider fixtures so long as the real provider interfaces are defined and no benchmark values are fabricated.

## Required repository skeleton

Create:

```text
apps/web
services/api
packages/domain
contracts
prompts
fixtures
evals
scripts
docs/ADR
```

## Domain models

Implement at minimum:

- Money
- ConstraintSet
- HardConstraint
- SoftConstraint
- Evidence
- PriceEvidence
- PlaceCandidate
- RouteFact
- PlanStop
- CandidatePlan
- ValidationCheck
- ValidationResult
- PlanProof
- CompiledPlan

Use Pydantic v2 in Python and JSON schemas in `/contracts`.

## Deterministic validator must exist before live search

Implement and test:

- budget
- duration
- outbound + return routing
- open-at-arrival
- walking maximum
- exclusions
- dietary evidence
- place grounding
- strict price confidence

A model is never permitted to override a failed hard check.

## Gemma parser

Local adapter via Ollama.

Requirements:
- JSON structured output
- preserve explicit numbers
- distinguish hard and soft
- no venue generation
- malformed output fails closed
- parser benchmark fixtures

## Place layer

Core discovery:
- OpenStreetMap / Overpass

Fresh enrichment where configured:
- SerpApi

Rules:
- every fact gets provenance
- unavailable fields remain unknown
- no unauthorized scraping
- community sources are weak ranking evidence only

## Routing

Valhalla abstraction.

Must include return trip in total duration.

If Valhalla is unavailable during early development, use route fixtures behind the same interface; never replace final routing with straight-line distance.

## Candidate-plan builder

Use deterministic plan templates initially:

1. free/public-space outing
2. one paid stop
3. paid stop + public walk

Do not ask the LLM to invent itinerary facts.

## Ranker

Gemma receives valid plans only.

It may rank:
- vibe
- quietness fit
- local feel
- novelty
- effort

It may not edit facts.

## API

Primary endpoint:

`POST /v1/plans/compile`

Return either:
- one `CompiledPlan`
- typed compilation failure

No list of recommendations in the public API response.

## Web

Only after backend vertical slice is green:

1. Home
2. Compiling
3. One plan
4. Plan Proof
5. GO mode
6. Honest failure

Mobile first.

## Evaluation

Implement a runner before adding optional features.

Target:
- 50 cases
- >=10 cities
- 0 hard violations
- 0 hallucinated displayed venues

Do not hardcode a single "correct restaurant"; score invariants.

## Observability

Instrument:
- parser latency
- discovery latency
- route latency
- number of candidates
- rejection reasons
- ranker latency
- total compile latency

Never log raw sensitive prompts to Sentry.

## Stop conditions

Immediately stop and fix if:
- a model invents a displayed venue
- an UNKNOWN price is shown as certain
- a hard constraint can be bypassed
- frontend exposes multiple default options
- total duration omits return travel
- provider failures silently become fake defaults

## Final deliverables

- working repo
- automated tests
- eval report
- three field-test records
- short demo
- architecture diagram
- DEV post assets

Start now with **Phase 0 and Phase 1 only**. Do not jump ahead.
