# Contracts

Cross-language schemas for API + web.

Required:
- `constraint-set.schema.json`
- `evidence.schema.json`
- `place-candidate.schema.json`
- `candidate-plan.schema.json`
- `compiled-plan.schema.json`
- `plan-proof.schema.json`

Runtime may use Pydantic/Zod, but public semantics must match.

## Phase 1 source of truth

`packages/domain/src/ground_rule/models.py` defines 17 Pydantic models.
Generate schemas with `uv run python scripts/export_contracts.py`; check drift
with `uv run python scripts/export_contracts.py --check`.

Generated JSON Schema expresses field shape, bounds, enums and required values.
Pydantic also enforces currency/price consistency, timezone awareness, route
chains, arrival arithmetic, acceptance coherence and proof/source relationships.
JSON Schema alone does not enforce all those cross-field rules. API ingestion
must use Pydantic; frontend types alone never authorize a plan.

Nullable facts are required explicitly unless they are policy defaults.
`strict_budget` defaults to true; other missing provider or user facts are not
invented. Money supports nine explicit currencies (see ADR 0004), never converts
between currencies, and accepts integer minor units only. Full budget, dietary,
hours, grounding, freshness and exclusion policy validation remains Phase 2.
