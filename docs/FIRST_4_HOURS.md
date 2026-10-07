# First 4 Hours — Execute Exactly This

This is the immediate build order.

## Hour 0–1 — Repo + local model

1. Create Git repo.
2. Copy this package into root.
3. Scaffold:
   - `services/api` FastAPI
   - `apps/web` React/Vite
   - `packages/domain`
4. Add formatter/linter/test commands.
5. Install Ollama.
6. Pull the chosen Gemma edge model.
7. Write one script that requests JSON from Gemma.
8. Validate that JSON with Pydantic.
9. Commit.

**Do not touch maps yet.**

Exit:
- API boots
- web boots
- local Gemma emits valid JSON

## Hour 1–2 — Domain contracts

Implement:
- Money
- ConstraintSet
- Evidence
- PriceProof enum
- PlaceCandidate
- RouteFact
- CandidatePlan
- ValidationCheck
- ValidationResult
- PlanProof
- CompiledPlan

Write unit tests for construction/serialization.

Exit:
- domain types green

## Hour 2–3 — Validator first

Build pure functions:

- `validate_budget`
- `validate_duration`
- `validate_grounding`
- `validate_open_hours`
- `validate_route`
- `validate_exclusions`
- `validate_diet`
- `validate_walking_limit`

Create invalid fixtures.

Mandatory tests:
- ₹600 rejected for ₹500 cap
- UNKNOWN price rejected in strict mode
- BOUNDED accepted when conservative max <= cap
- plan with 60 min outbound + 40 min return rejected for 90 min window
- mall rejected under `no mall`
- closed venue rejected
- ungrounded place rejected

Exit:
- no LLM involved
- every invalid fixture fails correctly

## Hour 3–4 — Gemma parser benchmark

Implement parser prompt.

Create >=15 initial cases immediately.

Example inputs:

1. `₹500 each, 90 min, vegetarian, no mall, quiet`
2. `$10 total, solo, an hour, preferably free`
3. `2 friends, dessert, back before 9`
4. `don't make me walk much`
5. `₹0, explore, 45 mins`
6. `coffee but not a chain`
7. `date, 2 hours, somewhere we can talk`
8. `vegan, under £15 each`
9. `no alcohol`
10. `active but not a gym`
11. `wheelchair accessible` → mark unsupported/high-stakes unless evidence model supports it
12. `allergy safe` → do not promise; unsupported high-stakes constraint
13. `cheap street food`
14. `somewhere open late`
15. `no crowded mall`

Measure field-level parser correctness.

Exit:
- parser schema-valid
- explicit numbers preserved
- unsupported high-stakes constraints detected
- no place names hallucinated

## At hour 4

Only then integrate OSM.

If the first four hours are not green, do not move on.
