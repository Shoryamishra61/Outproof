# Evaluation Plan

## Purpose

The project is not credible if it only produces nice-looking plans.

Prove:

1. Gemma understands fuzzy constraints.
2. Displayed facts are grounded.
3. Deterministic code enforces hard limits.
4. "Global" works across actual cities.
5. The product minimizes screen time.

## 50-case benchmark

### India — 30

Suggested:
- Chennai/SRM: 12
- Bengaluru: 4
- Mumbai: 3
- Delhi NCR: 3
- Hyderabad: 3
- Pune: 2
- Kolkata: 1
- Kochi: 1
- Jaipur: 1

### Global — 20

At least:
- London
- New York
- San Francisco
- Singapore
- Tokyo
- Berlin
- Paris
- Sydney
- Toronto
- Dubai

## Vary

- currency
- budget scope
- duration
- party
- walking tolerance
- free/paid
- dietary rules
- exclusions
- quiet/active
- return deadline
- sparse POIs
- missing prices
- closing soon

## Metrics

### Parser
- numeric accuracy
- currency accuracy
- duration accuracy
- hard/soft classification
- exclusion accuracy
- dietary accuracy

### Grounding
- place identity grounded
- coordinates grounded
- displayed operational facts sourced

Target:
- hallucinated displayed venues = 0

### Compiler
Target:
- budget violations = 0
- duration violations = 0
- exclusion violations = 0
- strict-mode weak-price acceptance = 0

### Routing
- route present
- return trip counted
- unreachable rejected

### Product
- default plans returned = 1
- median Time To Grass <30 s
- failure rate recorded
- reroll rate recorded

## Field tests

### A — Free
- solo
- ₹0
- 45–75 min

### B — Friend
- ₹250–₹500/person
- 60–120 min
- food + talk

### C — Date/group
- more hard constraints
- at least one diet/exclusion

Record:

| Metric | Predicted | Actual |
|---|---:|---:|
| duration | | |
| spend | | |
| walking distance | | |
| planning screen time | | |
| outing screen time | | |

Also record one unexpected failure and the engineering change made afterward.

## Release

Submission candidate only if:
- 50 cases run
- 0 hallucinated displayed venues
- 0 hard violations
- >=10 cities
- >=3 field tests
- local model demo
- cached/offline demo
- final report in `evals/reports/final.md`

Never fabricate benchmark values.
