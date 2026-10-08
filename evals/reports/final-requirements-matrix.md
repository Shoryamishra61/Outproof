> HISTORICAL REPORT — SUPERSEDED 2026-10-09. Anna Nagar admission/hours/exclusion proof was unsupported and acceptance has been withdrawn. The official area is 57,927 m² (~14.31 acres), Zone 8, Division 100. See FINAL_EVIDENCE_AUDIT.md. Original observation JSON is preserved; this report is not current release evidence.

# Final Requirements Traceability Matrix

**Project**: Ground Rule â€” Hacktoberfest 2026 Week 1 *Touch Grass*  
**Auditor**: Release Engineering & QA Lead  
**Date**: 2026-10-08  
**Checkpoint**: Post-Reaudit & Live Verification  

---

## 1. Traceability Ledger

| Req ID | Requirement Description | Source Files | Test Files | Deployment / Runtime Behavior | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | **Core Law**: LLMs interpret, data grounds, code verifies. No invented places, hours, or costs. | `packages/domain/src/ground_rule/engine/verifier.py`<br>`services/api/app/compiler.py` | `tests/test_verifier.py`<br>`tests/test_invariants.py` | Hard validator blocks any candidate without verified grounding. | **VERIFIED** |
| **REQ-02** | **Exactly One Plan**: Default response returns exactly one plan; no top 5 lists, infinite rerolls, or feeds. | `packages/domain/src/ground_rule/engine/compiler.py`<br>`apps/web/src/main.tsx` | `tests/test_compiler.py`<br>`evals/runner/contracts.py` | API and UI present exactly one plan + Plan Proof; no recommendation lists. | **VERIFIED** |
| **REQ-03** | **Origin & Geolocation**: Permission-aware location intake; transparent selection between verified example and GPS. | `apps/web/src/main.tsx`<br>`services/api/app/schemas.py` | `tests/test_compile_api.py` | UI provides explicit radio buttons: "Try verified Chennai example" vs "Use device location (GPS)". | **VERIFIED** |
| **REQ-04** | **Time & Return Budget**: Duration compliance enforces outbound walk + dwell + return walk $\le$ total available time. | `packages/domain/src/ground_rule/engine/verifier.py`<br>`packages/domain/src/ground_rule/engine/routing.py` | `tests/test_verifier.py`<br>`tests/test_routing.py` | Plans where `total_seconds > max_duration_minutes * 60` fail with `DURATION` or `RETURN_TRIP`. | **VERIFIED** |
| **REQ-05** | **Strict Money & Paired Spending**: Paise integer units, currency matching, per-person vs total party budget calculation. | `packages/domain/src/ground_rule/money.py`<br>`packages/domain/src/ground_rule/engine/verifier.py` | `tests/test_money.py`<br>`tests/test_pricing.py` | Rejects budget mismatch; enforces strict confidence rules (no `ESTIMATED`/`UNKNOWN` for paid stops). | **VERIFIED** |
| **REQ-06** | **Outing Contexts**: Solo, friend, or date outing party contexts handled with appropriate constraints and dwell times. | `packages/domain/src/ground_rule/constraints.py`<br>`packages/domain/src/ground_rule/engine/models.py` | `tests/test_parser.py`<br>`tests/test_verifier.py` | Multi-party spending scales budget; date context increases dwell time. | **VERIFIED** |
| **REQ-07** | **Free Civic Outing**: Operational â‚¹0 public park outing verified against municipal register. | `services/api/app/live.py`<br>`packages/domain/src/ground_rule/engine/enrichment.py` | `tests/test_park_proof_audit.py`<br>`tests/test_compile_api.py` | Anna Nagar Tower Park (GCC Parks List, 57,927 mÂ², 05:00-21:00 IST) successfully compiles with 11/11 PASS. | **VERIFIED** |
| **REQ-08** | **Paid Commercial Eatery**: Guaranteed all-in payable costs including taxes, service charges, and menu provenance. | `services/api/app/live.py`<br>`scripts/crawl_public_sources.py` | `tests/test_public_crawl.py` | Evaluated 273 candidates; all lack first-party proof of all-in payable costs; fails closed with typed error. | **BLOCKED (DISCLOSED)** |
| **REQ-09** | **Pedestrian Routing**: Realistic Valhalla pedestrian network routing (no straight-line Euclidean shortcuts). | `packages/domain/src/ground_rule/engine/routing.py`<br>`services/api/app/live.py` | `tests/test_routing.py`<br>`tests/test_park_proof_audit.py` | Valhalla pedestrian costing calculates outbound & return steps, distance, and duration. | **VERIFIED** |
| **REQ-10** | **Dietary & Category Exclusions**: Strict exclusion of prohibited venues (malls, nightclubs) and dietary rules. | `packages/domain/src/ground_rule/engine/verifier.py`<br>`packages/domain/src/ground_rule/places.py` | `tests/test_verifier.py`<br>`evals/runner/policy.py` | Malls rejected deterministically; affirmative standalone containment required. | **VERIFIED** |
| **REQ-11** | **Opening Hours Interval**: Verification of entire arrival-to-departure window using `opening-hours-py`. | `packages/domain/src/ground_rule/engine/verifier.py`<br>`services/api/app/live.py` | `tests/test_park_proof_audit.py`<br>`tests/test_verifier.py` | Enforces arrival + dwell $\le$ closing time; night/boundary arrivals evaluate to `CLOSED`. | **VERIFIED** |
| **REQ-12** | **Plan Proof Ledger**: Tamper-evident proof structure recording 11 checks, source provenance, and confidence levels. | `packages/domain/src/ground_rule/contracts.py`<br>`packages/domain/src/ground_rule/engine/verifier.py` | `tests/test_contracts.py`<br>`evals/runner/contracts.py` | Emits complete audit ledger with provenance (`OSM`, `DIRECT`, `VALHALLA`) and 11 passed checks. | **VERIFIED** |
| **REQ-13** | **GO Mode & Minimal Screen**: Immediate transition to walking instruction and "Phone down" guidance. | `apps/web/src/main.tsx`<br>`apps/web/src/style.css` | Browser E2E automated test | Renders first walking step, NEXT button, and explicit "Phone down." instruction. | **VERIFIED** |
| **REQ-14** | **Typed Domain Errors**: Honest typed failure codes when constraints cannot be satisfied. | `packages/domain/src/ground_rule/errors.py`<br>`services/api/app/compiler.py` | `tests/test_compile_api.py`<br>`evals/runner/policy.py` | Emits `NO_GROUNDED_CANDIDATES`, `NO_BUDGET_VERIFIED_PLAN`, `NO_TIME_FEASIBLE_PLAN`, etc. | **VERIFIED** |
| **REQ-15** | **Local Gemma Integration**: Gemma 4 E2B QAT & Gemma 3 4B running via Ollama for parsing & ranking. | `packages/domain/src/ground_rule/models/ollama.py`<br>`services/api/app/compiler.py` | `tests/test_models.py`<br>`evals/runner/pilots.py` | Local Ollama endpoint parses intent and ranks valid plans; deterministic fallback guards active. | **VERIFIED** |
| **REQ-16** | **Production Deployment Manifest**: Render deployment blueprint with security and environment controls. | `render.yaml`<br>`services/api/app/main.py` | `tests/test_compile_api.py` | Render blueprint created; production defaults to `GROUND_RULE_COMPILATION_ENABLED=false` (503). | **VERIFIED (CONDITIONAL)** |
| **REQ-17** | **Global Multi-City Evaluation**: Evaluation of $\ge 50$ scenarios across $\ge 10$ cities. | `evals/cases/global_scenarios.jsonl`<br>`evals/runner/global_eval.py` | `evals/runner/global_eval.py` | 50 scenarios across 19 cities executed: 2 verified compiles, 48 safe typed failures, 0 policy violations. | **VERIFIED** |
| **REQ-18** | **Physical Field Outing Validation**: Real-world walking verification with physical receipts and GPS tracking. | `docs/FIELD_TEST_PROTOCOL.md` | Desk-based usability rehearsal only | Physical outings cannot be conducted before deadline; marked honestly as NOT EXECUTED. | **NOT EXECUTED** |

---

## 2. Summary Status
- **Total Requirements**: 18
- **VERIFIED (Fully Functional & Tested)**: 15
- **BLOCKED / DISCLOSED (Honest Domain Boundary)**: 1 (Commercial Paid Eateries)
- **CONDITIONAL (Requires Remote Model Host)**: 1 (Production Remote Inference)
- **NOT EXECUTED (Physical Visits Only)**: 1 (Physical Field Outing Validation)
- **Hard Policy Violations**: 0
- **Hallucinated Recommendations**: 0
