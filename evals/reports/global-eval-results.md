# Global Evaluation Report: 50 Scenarios across 19 Cities

Evaluated At: 2026-10-07T13:22:52.498503+00:00

## Summary Metrics

| Metric | Target | Actual | Gate Status |
|---|---|---|---|
| Total Scenarios | >=50 | 50 | PASS |
| Global Cities Covered | >=10 | 19 | PASS |
| Hard Policy Violations | 0 | 0 | PASS |
| Hallucinated Displayed Venues | 0 | 0 | PASS |
| Unknown Prices Shown as Guaranteed | 0 | 0 | PASS |
| Multiple Default Plans Displayed | 0 | 0 | PASS |
| Successful Verified Compiles | - | 2 | RECORDED |
| Safe Typed Failures | - | 48 | RECORDED |
| Average Latency | - | 24129.1 ms | RECORDED |

## Core Engineering Law Compliance

> **LLMs interpret. Data grounds. Code verifies.**

Across all 50 global scenarios in 19 cities:
1. **0 Hard Violations**: Every accepted plan satisfies all 11 deterministic checks.
2. **0 Hallucinations**: Every displayed POI is grounded to an authoritative OSM record.
3. **0 Guesswork**: Unproven commercial places in external cities fail closed with typed domain errors (`NO_GROUNDED_CANDIDATES`, `NO_BUDGET_VERIFIED_PLAN`, etc.) rather than fabricating menu prices, hours, or indoor mall status.
4. **Exactly One Plan**: Every successful compilation returns exactly one verified plan with deterministic Plan Proof.

## Failure Breakdown (Safe Closed Failures)

| Typed Failure Code | Count | Semantic Justification |
|---|---|---|
| `NO_GROUNDED_CANDIDATES` | 44 | Grounded facts incomplete; failed closed per AGENTS.md invariant |
| `SOURCE_TEMPORARILY_UNAVAILABLE` | 4 | Grounded facts incomplete; failed closed per AGENTS.md invariant |

## Cities Tested (19)

Bengaluru, Berlin, Chennai, Delhi, Dubai, Hyderabad, Jaipur, Kochi, Kolkata, London, Mumbai, New York, Paris, Pune, San Francisco, Singapore, Sydney, Tokyo, Toronto

## Detailed Scenario Results

| ID | City | Outcome | Venue / Error | Latency |
|---|---|---|---|---|
| in-che-01 | Chennai | SUCCESS | Anna Nagar Tower Park | 24128.7 ms |
| in-che-02 | Chennai | SUCCESS | Anna Nagar Tower Park | 10414.71 ms |
| in-che-03 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 21173.29 ms |
| in-che-04 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23680.55 ms |
| in-che-05 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23699.87 ms |
| in-che-06 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23672.41 ms |
| in-che-07 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23693.03 ms |
| in-che-08 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 26347.82 ms |
| in-che-09 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23683.87 ms |
| in-che-10 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23899.75 ms |
| in-che-11 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 3675.71 ms |
| in-che-12 | Chennai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 9702.25 ms |
| in-blr-01 | Bengaluru | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 2228.41 ms |
| in-blr-02 | Bengaluru | SAFE_FAILURE | `SOURCE_TEMPORARILY_UNAVAILABLE` | 7156.05 ms |
| in-blr-03 | Bengaluru | SAFE_FAILURE | `SOURCE_TEMPORARILY_UNAVAILABLE` | 8672.02 ms |
| in-blr-04 | Bengaluru | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 35028.98 ms |
| in-bom-01 | Mumbai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23711.27 ms |
| in-bom-02 | Mumbai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23669.28 ms |
| in-bom-03 | Mumbai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 20670.63 ms |
| in-del-01 | Delhi | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 39692.91 ms |
| in-del-02 | Delhi | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23692.83 ms |
| in-del-03 | Delhi | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 34677.04 ms |
| in-hyd-01 | Hyderabad | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 34684.78 ms |
| in-hyd-02 | Hyderabad | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 34693.53 ms |
| in-hyd-03 | Hyderabad | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 19671.53 ms |
| in-pnq-01 | Pune | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23714.34 ms |
| in-pnq-02 | Pune | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23694.72 ms |
| in-ccu-01 | Kolkata | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 34702.28 ms |
| in-cok-01 | Kochi | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23669.43 ms |
| in-jai-01 | Jaipur | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 58680.9 ms |
| gb-lon-01 | London | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23723.24 ms |
| gb-lon-02 | London | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 25434.21 ms |
| us-nyc-01 | New York | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23663.05 ms |
| us-nyc-02 | New York | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23709.08 ms |
| us-sfo-01 | San Francisco | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23684.74 ms |
| us-sfo-02 | San Francisco | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23678.38 ms |
| sg-sin-01 | Singapore | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 30516.18 ms |
| sg-sin-02 | Singapore | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23680.3 ms |
| jp-tyo-01 | Tokyo | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 34695.44 ms |
| jp-tyo-02 | Tokyo | SAFE_FAILURE | `SOURCE_TEMPORARILY_UNAVAILABLE` | 23668.64 ms |
| de-ber-01 | Berlin | SAFE_FAILURE | `SOURCE_TEMPORARILY_UNAVAILABLE` | 23694.17 ms |
| de-ber-02 | Berlin | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23709.15 ms |
| fr-par-01 | Paris | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23759.44 ms |
| fr-par-02 | Paris | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23887.72 ms |
| au-syd-01 | Sydney | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23390.66 ms |
| au-syd-02 | Sydney | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23727.69 ms |
| ca-tor-01 | Toronto | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23705.12 ms |
| ca-tor-02 | Toronto | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23692.59 ms |
| ae-dxb-01 | Dubai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 26221.88 ms |
| ae-dxb-02 | Dubai | SAFE_FAILURE | `NO_GROUNDED_CANDIDATES` | 23730.33 ms |
