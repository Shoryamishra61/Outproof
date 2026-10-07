# Phase 7 — Operational price evidence

Acceptance: PASS for deterministic normalization/policy; real-price availability
is unverified. Executed 2026-10-07 locally.

`packages/domain/src/ground_rule/pricing.py` consumes the existing canonical
Evidence price wire object into PriceEvidence. Currency, integer minor units,
scope, both bounds and literal boolean complete mandatory-cost coverage are
required. VERIFIED must be exact; BOUNDED stays bounded; ESTIMATED is preserved
and rejected in strict policy; UNKNOWN never becomes zero. Generic cheap/price
levels and individual menu items cannot establish a complete plan cost.
Existing policy performs freshness, provenance, currency and scoped arithmetic.
No conversion, aggregation guess, confidence upgrade or model call.

`tests/test_pricing.py`: 21 offline tests for normalization plus full policy,
upper-bound caps, missing facts, unsafe coercions, exact boolean coverage,
confirmed zero, optional unknown dessert, and foreign-currency rejection.

```powershell
uv run pytest tests/test_pricing.py -q
# Initial: 1 failed, 20 passed; fixture incorrectly listed literal True as incomplete.
# Corrected fixture to integer 1 (must fail; boolean True must pass).
# Final: 21 passed in 0.20s
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
# Initial pytest gate: 1 failed, 262 passed, 2 skipped; same fixture error.
# Final: Ruff pass; 76 files formatted; 263 passed, 2 skipped in 1.53s
# 17 schemas; contract fixtures 60/60; policy fixtures 85/85
# TypeScript pass; Vite pass 1.45s
```

All amounts here are synthetic tests. `templates-chennai-real-data-1.json`
preserves the real candidate's missing price and rejection. No guessed price
was inserted. No live menu or verified free outing has yet been obtained.
Optional expense records explicitly have mandatory:false and are excluded
from mandatory totals; they are not hidden additional required itinerary stops.
