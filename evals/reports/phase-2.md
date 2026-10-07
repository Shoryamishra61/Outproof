# Phase 2 — deterministic hard policy

Gate: **PASS**, initially verified 2026-10-06; final verification 2026-10-07. Scope is synthetic policy fixtures;
zero real outings, provider calls, field tests or geographic coverage claims.

## Changed files

- `packages/domain/src/ground_rule/policy.py`: pure eleven-check validator.
- `evals/cases/policy.py`: 85 fictional adversarial/boundary cases.
- `evals/runner/policy.py`, `evals/reports/policy.json`: executable evaluation and exact outcomes.
- `tests/test_policy.py`: fixture regressions, no-I/O checks and unsafe mutation checks.
- `pyproject.toml`: include repo root for importing the shared eval fixtures in pytest.
- `scripts/check.ps1`, `.github/workflows/check.yml`: include deterministic policy eval.
- `docs/POLICY.md`, `docs/ADR/0005-deterministic-evidence-policy.md`: evidence semantics/ceilings.
- `TASKS.md`, `BUILD_ORDER.md`, this report: truthful phase status.

All 17 Phase 1 models/schemas, frontend contracts, API health and preserved failed
Gemma experiments remain unchanged. `compilation_available` remains false.

Boundary audits added explicit ₹350 UNKNOWN-with-an-asserted-amount structural
rejection, mixed currencies between stops, and route evidence for changed origin
or destination coordinates. Currency totals remain separate even before
rejection. The route regression first produced **3 failures / 87 passes**; binding
both route endpoint coordinates corrected it. The expanded policy tests then
passed **90 tests**, and policy eval passed **85/85** (19 accepted, 66 rejected).

## Behavior

Canonical checks cover grounding, routes including return, all travel/dwell
duration, explicit UTC deadline, scoped exact-currency mandatory budget,
strict confidence/upper bounds, whole-visit hours, positive exclusions, positive
diet evidence and both walking maxima. Missing, expired, future, low-confidence,
misbound or conflicting operational evidence rejects. Synthetic provenance
requires explicit fixture opt-in; it is rejected by default. Unknown free ticket
cost rejects; optional unknown dessert passes only with explicit mandatory=false.
Allergy guarantees and accessibility remain unsupported and reject without
weakening the input requirement. Evidence normalization is documented; no schema
redesign or live adapters were needed.

The requested scope trap rejects a ₹800 TOTAL budget for four against ₹450/person
mandatory cost: ₹1,800 exceeds ₹800. The inverse cost/cap direction passes by
exact arithmetic, and is separately tested.

## Exact verification

Final command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
```

Exit 0. It executed:

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS, zero findings |
| `uv run ruff format --check .` | PASS, 61 files already formatted |
| `uv run pytest` | **169 passed**, 1.46 seconds (106 Phase 0–2; 63 parser boundary) |
| `uv run python scripts/export_contracts.py --check` | PASS, 17 schemas |
| `uv run python evals/runner/contracts.py` | **60/60**, zero failures |
| `uv run python -m evals.runner.policy` | **85/85**, zero failures; 19 accepted / 66 rejected |
| `npm run check --prefix apps/web` | strict TypeScript PASS; Vite build PASS, 1.44 seconds |

Additionally:

```powershell
uv run python 'C:/Users/SHORYA MISHRA/.agents/skills/anti-slop-ui/scripts/ui_audit.py' apps/web --fail-on low
```

Source audit PASS, zero findings. No UI was changed; browser/performance testing
was not repeated. Narrow policy pytest: **90 passed** in 0.74 seconds. Isolated Phase 0–2 pytest:
**106 passed** in 2.33 seconds. Unknown party size now retains an unknown group
cost internally rather than a zero placeholder; it still rejects scope conversion.
No-network regression runs every case with sockets and httpx requests forbidden,
and inspects policy imports: no model/provider/network dependency.

Early test collection lacked the root eval import path; corrected narrowly in
pytest configuration. The first collected run had 5 failures / 73 passes:
fixture generation incorrectly labelled null evidence HIGH, a missing known-price
proof was a structural rejection rather than a policy rejection, and the eval
aggregate exposed those fixture errors. Corrected fixture semantics without
weakening contracts. Final broad check was rerun after all policy changes.

## Limits

Positive attestations prove consistency with supplied evidence, not external
truth. Complete mandatory price coverage must be supplied by future normalization.
Freshness ceilings are explicit conservative policy, not field measurements.
Diet is conservative across every mandatory stop. Policy does not generate
PlanProof, rank, compile or display an outing. Synthetic acceptance provides no
evidence of real venue grounding, parser accuracy, Time To Grass or Screen Ratio.
GitHub CI has been updated but has not been executed remotely.
