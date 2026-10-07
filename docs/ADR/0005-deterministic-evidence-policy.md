# ADR 0005 — Hard checks consume exact positive attestations

Accepted for Phase 2, 2026-10-06.

Keep all 17 Phase 1 schemas and canonical check codes. Add one pure validator
with an injected aware clock and explicit fixture opt-in. Specify Evidence.value
wire semantics in docs/POLICY.md instead of adding new cost/provider abstractions.
Prices attest complete mandatory cost bounds; optional expenses explicitly state
mandatory=false. Absence of evidence never establishes absence of a restriction.

Freshness ceilings and positive exclusions/diet are conservative prototype
policy. They can reject otherwise usable places; relaxing them requires explicit
evidence and regressions. Unsupported requirements fail closed. No compiler,
provider, model call, or API availability change is part of this decision.
