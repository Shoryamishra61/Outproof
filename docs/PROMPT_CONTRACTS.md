# Prompt Contracts

## Parser

Input:
- structured controls
- optional free text
- locale/currency hints

Output:
- local Gemma JSON matching internal `ParserAdditions`
- deterministic additive merge yields the existing `ConstraintSet`, or typed failure

Rules:
- never invent location
- distinguish hard/soft
- preserve numbers
- represent uncertainty
- never generate places

Structured controls remain authoritative. Budget/currency/scope/duration/origin/
departure/party mode/strictness are absent from the additions schema. Supplied
optional numeric controls and deadlines cannot be overwritten. Missing optional
values require explicit source text; clock-only deadlines never acquire a date.
Unsupported requirements remain hard and fail policy until evidence is supported.
The executed raw-model benchmark is separate from schema/merge boundary checks;
see `evals/reports/phase-3.md` for actual accuracy and remaining limitations.

## Ranker

Input:
- normalized preferences
- already-valid plans

Output:
- selected plan ID
- concise reason
- optional soft-fit scores

Rules:
- cannot edit facts
- cannot change cost/time
- cannot select an absent ID
- cannot resurrect rejected candidates
