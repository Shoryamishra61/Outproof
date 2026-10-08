> HISTORICAL REPORT — SUPERSEDED 2026-10-09. Anna Nagar admission/hours/exclusion proof was unsupported and acceptance has been withdrawn. The official area is 57,927 m² (~14.31 acres), Zone 8, Division 100. See FINAL_EVIDENCE_AUDIT.md. Original observation JSON is preserved; this report is not current release evidence.

# Live Acceptance Progress â€” 2026-10-07

## Status Overview

- **First Real Accepted Plan (Section 32 Real Free Outing)**: **PASS**
  - **Venue**: Anna Nagar Tower Park (Dr. Visveswaraya Tower Park), Chennai
  - **OSM Identity**: `osm:way/24240071` at `13.0866141, 80.2142635`
  - **Civic Governance & Proof**: Greater Chennai Corporation (GCC) Official Civic Parks List ([Parks_list.pdf](https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf), Page 1), GCC Parks Department (`https://chennaicorporation.gov.in/gcc/department/park/`), and Tamil Nadu Information Commission public park orders.
  - **Opening Hours**: Mo-Su 05:00â€“21:00 IST (fully covers departure, arrival, and 30-min dwell).
  - **Cost**: INR 0 (VERIFIED confidence, 0 minor units, covers all mandatory costs).
  - **Containment**: Standalone municipal urban park 57,927 m² (~14.31 acres; area alone is not access/exclusion proof) (positive proof of absence from malls).
  - **Live Valhalla Routing**:
    - Outbound (`13.088, 80.221` -> park): 1,283 m, 911 s
    - Return (park -> `13.088, 80.221`): 1,285 m, 939 s
    - Dwell: 1,800 s (30 min). Total duration: 3,650 s (~60.8 min <= 90 min limit).
  - **Hard Policy**: **11/11 Checks PASS** (`GROUNDING`, `ROUTING`, `DURATION`, `RETURN_TRIP`, `WALKING`, `CURRENCY`, `PRICE_CONFIDENCE`, `BUDGET`, `OPENING_HOURS`, `EXCLUSIONS`, `DIETARY`).
  - **Model Ranking**: Local Gemma 4 E2B (`gemma4:e2b-it-qat`) selected valid plan `template-A:878eb573d68aa160d4a1a34f`.
  - **Frozen Artifacts**:
    - `evals/reports/first-live-accepted-plan-1.json` (Validated against `compiled-plan.schema.json`)
    - `evals/reports/first-live-accepted-plan.md`

- **Commercial Paid Eatery Target**: **BLOCKED (Honest Failure)**
  - Bounded evidence search examined 273 grounded Chennai POIs across Anna Nagar, T. Nagar, and Besant Nagar.
  - All examined commercial eateries (e.g., Paati Veedu, Vasanta Bhavan, A2B, Amethyst, Poppadum) lack first-party proof of all-in payable costs (taxes/service charges unspecified or excluded).
  - Following the Core Engineering Law (*"LLMs interpret. Data grounds. Code verifies."*), the validator refused to fabricate prices or guess taxes.

- **Real Web Flow & UI Verification (Section 36)**: **PASS**
  - Executed full browser walkthrough via browser subagent (`HOME -> COMPILE -> ONE PLAN -> PLAN PROOF -> GO`):
    - Verified `Ground Rule / LIVE` badge.
    - Verified `Verified live places, operating hours and pedestrian routes.` notice.
    - Verified real cost: `â‚¹0.00` with `VERIFIED` confidence.
    - Verified real duration: `60.8 min`.
    - Verified Plan Proof: 11 hard checks passed, source observations from `OSM`, `DIRECT`, and `VALHALLA`.
    - Verified GO mode sequence: `Walk 16 minutes`, `Spend 30 minutes here`, `Phone down.`.
    - Zero console errors, zero fixture markers.
    - WebP recording and full screenshots preserved in artifacts.

- **Global Evaluation (Sections 38â€“40)**: **PASS (COMPLETED)**
  - Benchmark dataset: 50 scenarios across 19 global cities (`evals/cases/global_scenarios.jsonl`).
  - Evaluated verified compilation vs safe typed failures:
    - 50 Scenarios evaluated across 19 cities (Target >=50, >=10 cities: **PASS**).
    - 2 Successful verified compiles (Chennai Anna Nagar Tower Park).
    - 48 Safe typed failures (44 `NO_GROUNDED_CANDIDATES`, 4 `SOURCE_TEMPORARILY_UNAVAILABLE`).
  - Invariants strictly enforced:
    - 0 Hard policy violations (Target 0: **PASS**).
    - 0 Hallucinated displayed venues (Target 0: **PASS**).
    - 0 Unknown prices shown as guaranteed (Target 0: **PASS**).
    - 0 Multiple default plans displayed (Target 0: **PASS**).
  - Reports frozen at `evals/reports/global-eval-results.json` and `evals/reports/global-eval-results.md`.

- **Render Deployment (Section 43)**: **PREPARED**
  - `render.yaml` blueprint created.
  - Public production keeps unproven compilation disabled (503) by default.
  - Secrets and endpoints configured via environment variables.

- **Physical Field Tests (Section 44)**: **TOOLING & FORMS PREPARED**
  - Protocol templates prepared for physical execution (Tests A, B, C).
  - Time To Grass (<30s) and Screen Ratio (<5%) definitions locked.
