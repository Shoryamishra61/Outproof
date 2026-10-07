# Architecture

## Principle

> **LLMs interpret. Data grounds. Code verifies.**

## Pipeline

```text
User
 |
 v
Constraint Intake
 |
 v
Gemma Constraint Parser
 |
 v
Typed ConstraintSet
 |
 +---------------------+
 |                     |
 v                     v
OSM / Overpass      Fresh Enrichment
candidate POIs      SerpApi / compliant sources
 |                     |
 +----------+----------+
            |
            v
     Evidence Normalizer
            |
            v
         Valhalla
  route matrix / isochrone
            |
            v
  Candidate Plan Builder
            |
            v
  Deterministic Validator
            |
        PASS ONLY
            |
            v
        Gemma Ranker
            |
            v
 One Primary + Hidden Backup
            |
            v
        Plan Proof
            |
            v
          GO Mode
```

## 1. Constraint Parser

Input:
- structured controls
- optional natural language

Output:
`ConstraintSet`

Responsibilities:
- normalize "cheap", "quiet", "no mall", "back by 9"
- classify hard vs soft
- preserve numeric limits
- emit unknown instead of guessing

Never generate places.

## 2. Candidate Discovery

Core:
- OSM / Overpass

Returns:
- provider identity
- coordinates
- category
- tags
- available operating metadata

## 3. Enrichment

Optional:
- SerpApi
- compliant place sources
- community evidence

Responsibilities:
- operational signals
- price evidence
- ratings/counts
- hours
- source timestamps

Never overwrite stronger evidence with weaker evidence.

## 4. Evidence Normalizer

Every fact includes:
- value
- source
- observed_at
- confidence
- provider reference

## 5. Routing

Valhalla:
- walking ETA
- distance
- matrices
- route
- optional isochrone

Routing, not Gemma, determines travel feasibility.

## 6. Plan Builder

Deterministic templates:

1. single destination
2. paid stop + public walk
3. free exploration loop

Avoid arbitrary LLM-created itinerary facts.

## 7. Validator

Pure domain logic.

Checks:
- budget
- currency/scope
- total time
- return trip
- hours at projected arrival
- exclusions
- dietary evidence
- walking limit
- grounding
- evidence thresholds

## 8. Ranker

Gemma receives valid plans only.

Ranks for:
- vibe
- conversational suitability
- novelty
- local feel
- effort

Cannot resurrect rejected plans.

## 9. Plan Proof

Human-readable projection of validator results.

## 10. GO Mode

- one next instruction
- minimal UI
- hidden backup only when primary invalidates

## Monorepo boundaries

```text
apps/web
  presentation

services/api
  provider adapters + orchestration

packages/domain
  pure contracts + validators + plan builder + proof

contracts
  JSON schemas

evals
  runner + benchmark reports
```

## API

Primary:
- `POST /v1/plans/compile`

Supporting:
- `POST /v1/plans/{id}/revalidate`
- `POST /v1/feedback`
- `GET /v1/health`

## Latency targets

- parser <= 2 s local/dev
- discovery <= 3 s
- enrichment <= 4 s
- routing <= 2 s
- deterministic compile <= 200 ms
- ranker <= 2 s
- total p50 <= 10 s

## Offline story

### Connected
- local Gemma
- OSM/cache
- enrichment
- Valhalla

### Cached demo
- local Gemma
- cached regional POIs
- local routing extract
- no fresh-price claim without valid evidence

Offline mode must downgrade certainty honestly.
