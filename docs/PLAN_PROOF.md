# Plan Proof

## Purpose

Plan Proof turns Ground Rule from a recommender into a constraint compiler.

Every displayed plan answers:

> Why is this plan allowed to exist?

## Checks

### Budget
Example:
`PASS 410 INR <= 500 INR/person`

Requires:
- same currency
- correct scope
- sufficient evidence

### Duration
Example:
`PASS 82 min <= 90 min`

Must include:
- outbound travel
- dwell time
- intermediate travel
- return travel

### Opening hours
Validate projected arrival/dwell, not just "open now".

### Exclusions
Example:
`PASS category != mall`

### Diet
Pass only with policy-compliant evidence.

Do not treat cuisine inference as an allergy guarantee.

### Walking
Example:
`PASS 2.1 km <= 2.5 km`

### Grounding
Each place must map to provider identity + coordinates.

## Pseudocode

```text
for plan in candidate_plans:
    checks = []
    checks += validate_currency(plan, constraints)
    checks += validate_budget(plan, constraints)
    checks += validate_duration(plan, constraints)
    checks += validate_hours(plan)
    checks += validate_route(plan, constraints)
    checks += validate_exclusions(plan, constraints)
    checks += validate_diet(plan, constraints)
    checks += validate_grounding(plan)

    if all_hard_pass(checks):
        accept(plan)
    else:
        reject(plan)
```

## Hard vs soft

Hard:
- numeric budget
- return deadline
- "no mall"
- required vegetarian
- maximum walking

Soft:
- quiet
- romantic
- interesting
- local
- surprising

Gemma ranks soft fit.

Gemma never overrides hard failures.

## UI

```text
PLAN PROOF

✓ ₹410 <= ₹500
✓ 82m <= 90m
✓ vegetarian evidence
✓ open through visit
✓ no mall
✓ walk <= 2.5 km
```

Failure is valid.

Correct:
> No plan satisfied all 6 hard constraints.

Incorrect:
> Here is something close enough.

unless the user explicitly relaxes a constraint.
