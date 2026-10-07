# AGENTS.md — Ground Rule Engineering Contract

This file is authoritative for all coding agents in this repository.

## Mission

Ship a convincing Hacktoberfest 2026 Week 1 **Touch Grass** submission.

Ground Rule transforms fuzzy real-world constraints into **one verified outing** and then reduces screen interaction.

It is not:
- a chatbot
- restaurant recommender
- map browser
- calorie tracker
- social network
- multi-agent showcase

## Non-negotiable invariant

> **LLMs interpret. Data grounds. Code verifies.**

Never allow an LLM to be the source of truth for:
- place existence
- coordinates
- opening hours/status
- walking time/distance
- price arithmetic
- budget compliance
- duration compliance
- hard exclusions
- dietary hard constraints without evidence

If a fact is unsupported, represent it as unknown.

## Output invariant

The default successful response contains **exactly one plan**.

Do not return:
- top 5 lists
- alternate cards
- recommendation feeds
- infinite rerolls
- "you may also like"

A backup may be compiled internally and shown only if the primary becomes invalid.

## MVP scope

### Must ship

1. Constraint intake
2. Gemma constraint parser
3. Global candidate discovery
4. Source normalization + provenance
5. Walking feasibility
6. Deterministic hard validator
7. Candidate-plan builder
8. Gemma ranker over valid plans only
9. Exactly-one response
10. Plan Proof
11. GO mode
12. Evaluation harness
13. Local Gemma path
14. >=3 real field tests
15. DEV article/demo assets

### Out of scope until all core gates pass

- authentication
- social network
- stranger matching
- payments/bookings
- calendar sync
- streaks/gamification
- discovery feed
- native apps
- vector DB without demonstrated need
- calorie/macronutrient tracking
- medical claims
- safety guarantees
- complicated multi-agent architecture
- fine-tuning only to qualify for a prize category

## Engineering priority

1. Correctness
2. Grounding
3. Constraint safety
4. Evaluation
5. Latency
6. UX simplicity
7. Visual polish
8. Optional integrations

Never reverse this order for demo cosmetics.

## Agent workflow

Before coding:
1. Read `PRODUCT_SPEC.md`
2. Read `ARCHITECTURE.md`
3. Read `docs/PLAN_PROOF.md`
4. Read `docs/DATA_SOURCES.md`
5. Read `EVALS.md`
6. Pick the next unchecked item in `TASKS.md`

After coding:
1. Add/update tests.
2. Run relevant tests.
3. Run affected eval fixtures.
4. Update `TASKS.md`.
5. Add an ADR if architecture changed.
6. Document unsupported assumptions.

## Python rules

- Python 3.12+
- type hints required
- Pydantic v2 at API boundaries
- pure/deterministic domain validation where possible
- `Decimal` or integer minor units for money
- timezone-aware datetimes
- no currency conversion without an explicit conversion source
- no silent fallback values for unknown facts

## TypeScript rules

- strict mode
- no `any` unless justified
- frontend contracts mirror `/contracts`
- certainty language must match backend confidence

## Typed domain errors

Prefer:
- `NO_GROUNDED_CANDIDATES`
- `NO_BUDGET_VERIFIED_PLAN`
- `NO_TIME_FEASIBLE_PLAN`
- `NO_OPEN_PLAN`
- `UNSUPPORTED_CONSTRAINT`
- `SOURCE_TEMPORARILY_UNAVAILABLE`
- `MODEL_OUTPUT_INVALID`

Never convert these into invented "best effort" facts.

## Confidence semantics

Budget proof:
- `VERIFIED`
- `BOUNDED`
- `ESTIMATED`
- `UNKNOWN`

Strict mode paid stops:
- allow VERIFIED
- allow BOUNDED
- reject ESTIMATED
- reject UNKNOWN

If no paid plan survives:
- compile a free outing if feasible
- otherwise fail honestly

Never display ESTIMATED as guaranteed.

## Model contract

Gemma is used for:

### Parser
Fuzzy language -> typed hard/soft constraints.

### Ranker
Rank already-valid candidate plans for subjective fit.

Gemma must not:
- invent candidates
- override validators
- own arithmetic
- convert missing evidence into asserted facts
- alter provider facts

Every response:
- structured output
- schema validation
- fail closed if malformed

## Data-source policy

- OpenStreetMap: global candidate layer
- Valhalla: routing truth
- SerpApi: optional fresh enrichment
- Google-derived data: only compliant/authorized access; never scrape/rehost a shadow database
- Reddit/community: optional weak local signal; never operational truth; never unauthorized bulk scraping

See `docs/DATA_SOURCES.md`.

## Privacy

Default:
- no accounts
- no persistent raw location history
- no persistent raw free-text history
- no raw private prompts in Sentry
- record technical metrics, not personal outing history

See `SECURITY_PRIVACY.md`.

## UI rules

### Home
One screen.

### Result
One plan + proof.

### GO
One next instruction.

### Never add
- infinite scroll
- related recommendations
- autoplay engagement loops
- persuasive dark patterns
- review-reading workflow

The product optimizes closure, not retention.

## Required tests

Every plan-generation PR:
1. unit test
2. hard-constraint regression
3. malformed-model-output test
4. missing-source-data test
5. relevant eval fixture

Every pricing change:
- currency-safe comparison
- unknown-price behavior
- strict-mode rejection

Every routing change:
- unreachable candidate
- return-trip accounting

## Release gates

Do not call submission ready until:

- [ ] 0 hallucinated displayed venues
- [ ] 0 hard-constraint violations
- [ ] >=50 automated scenarios
- [ ] >=10 global cities
- [ ] >=3 India field tests
- [ ] median Time To Grass <30 s
- [ ] field Screen Ratio <5%
- [ ] exactly one default plan
- [ ] local Gemma path demonstrated
- [ ] cached/offline demo exists
- [ ] displayed facts carry provenance
- [ ] uncertain prices are never presented as guaranteed

## Anti-patterns

Do not:
- add impressive-but-useless features
- bolt on partner tools for category count
- replace validators with agent reasoning
- fabricate benchmark results
- fabricate prices/hours
- call the system global just because arbitrary city text is accepted
- claim offline if fresh place lookup is required
- claim privacy while logging raw prompts
- optimize for UI recording rather than the real outing

## If uncertain

Choose the narrower, more testable implementation.

One extraordinary loop beats twelve mediocre features.
