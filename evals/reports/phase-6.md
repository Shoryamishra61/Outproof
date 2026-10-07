# Phase 6 — Deterministic candidate templates

Acceptance: PASS for candidate building. No accepted real outing yet.
Executed 2026-10-07 locally (retained evaluation timestamp is UTC).

## Files/behavior

`packages/domain/src/ground_rule/plans.py`: pure deterministic A public/free
30-minute destination dwell, B 45-minute eatery dwell, C 30-minute eatery +
20-minute public-space dwell. Each emitted candidate has every directed leg
including return and passes the existing grounding check. Full policy remains
mandatory afterward. No new domain schema, model call or distance heuristic.
Public templates require explicit positive public-access evidence, and free A
additionally needs confirmed zero mandatory cost. Unknown parks are not assumed
public/free. Missing authoritative origin/departure fails, never invents a date.
Conflicting place identities/routes fail closed; unknown travel keeps arrival
and totals unknown. Existing policy owns all feasibility decisions.

`tests/test_plans.py`: 11 synthetic tests exercise all templates, deterministic
ordering, provenance, fixture isolation, missing return, price/access unknowns,
duplicate conflicts, local midnight and return-over-limit rejection.
`evals/runner/templates.py`: retained real-provider candidate/validation report,
explicitly distinct from successful compilation or a field outing.

## Commands/results

```powershell
uv run pytest tests/test_plans.py -q
# 11 passed in 0.22s
uv run python -m evals.runner.templates --discovery evals/reports/discovery-chennai-live-1.json --routing evals/reports/routing-chennai-live-1.json --output evals/reports/templates-chennai-real-data-1.json
# exit 0: candidate-template gate true, 1 candidate, 0 accepted outings
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
# Ruff pass, 73 files formatted; 242 passed, 2 skipped in 1.54s
# 17 schemas; contract fixtures 60/60; policy fixtures 85/85
# TypeScript pass; Vite pass 1.44s
```

Real candidate: Paati Veedu, 45-minute dwell + 733-second outbound +
716-second return = 4149 seconds (69m9s). 2012m walking. The required INR
500/person, friend, 90 minutes, vegetarian/no mall/quiet target was applied as
structured constraints here, not parsed or patched by a model.

| Check | Real candidate |
|---|---|
| GROUNDING, ROUTING, DURATION, RETURN_TRIP, WALKING, DIETARY | PASS |
| CURRENCY, PRICE_CONFIDENCE, BUDGET, OPENING_HOURS, EXCLUSIONS | FAIL |

Price unknown causes currency/budget checks to fail; it is not evidence of an
actual measured currency mismatch or excessive spend. Raw hours are not usable
visit-window proof. No mall absence/containment assertion was fabricated.

## Limits

At most 12 sorted place identities enter template enumeration; no relevance
ranking or large-area optimizer. Fixed required dwell is explicit template
behavior, not a learned personalized duration. C requires diet evidence at all
mandatory stops under existing policy; public stops with unknown diet evidence
will be rejected for a dietary request. No contract weakening was introduced.
No live-price enrichment, accepted plan, API compilation or UI flow is claimed.

Final boundary review also requires fresh matching category evidence rather than
a spoofed/unsupported PlaceCandidate category field, and public-access evidence
must remain valid through required dwell. Four added regressions bring this
suite to 15 tests (`uv run pytest tests/test_plans.py -q`: 15 passed in 0.24s).
Final canonical verification is recorded in overnight-handoff. Original live
candidate/validation evidence is preserved without timestamp refresh or overwrite.
