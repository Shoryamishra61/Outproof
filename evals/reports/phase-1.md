# Phase 1 — contract evidence

Date: 2026-10-06 (Asia/Calcutta). Scope: domain contracts only.

## Implemented

All requested domain models plus Coordinates, OpeningWindow, and typed
CompilationFailure (17 exported schemas total). Models reject extra fields and
coercion of money/numeric controls, require aware timestamps, preserve unknown
facts, and revalidate nested Pydantic instances.

Money uses nonnegative integer minor units within JavaScript's exact-integer
range. Addition/comparison reject different currencies; integer multiplication
does not coerce booleans, floats, or strings. Supported currencies are explicitly
INR, USD, GBP, SGD, JPY, EUR, AUD, CAD, AED. No currency conversion or major-unit
conversion is implemented.

CandidatePlan carries one route leg per stop plus the return leg. Arrival times
derive from those route facts; totals include every leg and dwell. Unreachable
routes have null metrics and cause unknown totals. Elapsed time uses UTC instants,
including repeated local clock hours; timestamp overflow is a contract failure.

ValidationResult acceptance requires all eleven hard check codes to pass.
PlanProof preserves references and evidence values. CompiledPlan has exactly one
`plan`, rejects alternate-option fields, mismatched proof IDs/totals, missing stop
evidence, and fixture evidence labelled as LIVE/CACHED. This represents the
compiler's eventual output shape; it does not implement or prove policy checks.

ADR: `docs/ADR/0004-domain-contracts.md`.

## Exact verification

Final `./scripts/check.ps1` completed successfully:

| Check | Observed result |
|---|---|
| Ruff lint | passed |
| Ruff format | 45 files already formatted |
| pytest | 16 passed, no warnings |
| schema drift | 17 schemas checked |
| synthetic contract eval | 60/60 passed |
| TypeScript strict check | passed |
| production Vite build | passed, 28 modules transformed |

Run contract eval independently:
`uv run python evals/runner/contracts.py`.
Per-case results: [contracts.json](contracts.json).
Fixture source: `evals/cases/contracts.jsonl` and `fixtures/contracts/`.

The 60 cases cover all model roundtrips, invalid money/currencies/coordinates,
partial budgets, party conflicts, typed hard constraints, malformed output shape,
missing evidence, naive timestamps, confidence/price contradictions, invalid hours,
unknown route facts, missing return travel, fabricated arrivals, hard-check
failures, mismatched proofs, and multiple default options. They are **synthetic
structural tests**, not 60 verified outings or global city evaluations.

Two additional provenance regressions failed before their fixes and passed
afterward: conflicting cost evidence under one ID, and a compiled place with its
source records omitted. Pytest also verifies malformed JSON, unsafe nested copies,
currency-safe arithmetic, repeated clock hours, and extreme route-duration input.

Current-schema local Gemma smoke passed with explicit `gemma3:1b` on CPU:
22068 ms, schema valid, all synthetic controls preserved. See
[bootstrap-model.json](bootstrap-model.json). Numeric/location/deadline controls
are constrained using JSON Schema `const`; this checks the local adapter path,
not independent model accuracy. The original Phase 0 result is retained in
[phase-0-model.json](phase-0-model.json).

Mandatory UI audit rerun: zero findings. The visual thesis and browser evidence
remain the Phase 0 Field notebook setup screen; no outing UI was added. API live
health still returns 200 with `compilation_available: false`.

## Failures and limitations

- The unconstrained expanded-model echo doubled 50000 to 100000 minor units and
  invented a departure date. Exact-control equality rejected it. The smoke now
  locks authoritative structured controls; free-text inference and parser quality
  remain unverified Phase 3 work. This is not a passing numeric parser benchmark.
- GPU warm-up and the default Gemma 4 E4B model remain unverified as recorded in
  Phase 0. Only the explicit smaller local CPU smoke passed.
- The Python environment became incomplete (only a held uvicorn launcher remained).
  The API was stopped, the broken directory preserved under ignored
  `.tools/venv-before-contracts`, and `.venv` rebuilt with locked dependencies.
  Automatic review rejected deletion with “blocked by policy”; no deletion or
  approval bypass was used. The exact external cause of the incomplete environment
  was not established.
- One full check failed because the local TypeScript executable was missing.
  `npm ci --prefix apps/web` restored the locked dependencies; the complete
  entrypoint was rerun and passed. Package audit reported zero vulnerabilities.
- Schema exports intentionally cannot encode every Pydantic cross-field validator;
  runtime validation remains required. Frozen models are not a deep-immutability
  guarantee for generic JSON evidence values.
- CI is configured but has not run remotely. PWA installation, Core Web Vitals,
  screen reader behavior, field screen time, real venues, providers, ranking and
  end-to-end compilation are unverified.
- Phase 2 hard-constraint policy, Phase 3 parser benchmarks and all later phases
  are unimplemented. No release gate for real-world compliance, city coverage,
  field tests, latency, or submission readiness is marked complete.
