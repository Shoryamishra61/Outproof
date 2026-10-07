# ADR 0003 — Price Confidence

Status: Accepted

## Decision

Every paid-plan cost has:
- VERIFIED
- BOUNDED
- ESTIMATED
- UNKNOWN

Strict mode accepts only VERIFIED/BOUNDED.

If no paid plan survives:
- free plan if feasible
- otherwise honest failure
