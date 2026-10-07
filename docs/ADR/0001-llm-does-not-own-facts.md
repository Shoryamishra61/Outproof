# ADR 0001 — LLM Does Not Own Real-World Facts

Status: Accepted

## Decision

LLMs are not authoritative for:
- existence
- coordinates
- hours
- prices
- travel times
- hard constraints

Provider evidence and deterministic code own these.

## Consequence

The system may fail more often. This is preferable to confidently wrong outings.
