# ADR 0006 — Gemma proposes additions, code preserves structured controls

Accepted for Phase 3 implementation, 2026-10-06. Benchmark acceptance is reported
separately in evals/reports/phase-3.md.

Keep ConstraintSet as the domain/API contract. A local Ollama call returns an
internal ParserAdditions schema with finite normalized categories/preferences
and optional sourced walking/party/deadline fields. The deterministic merger
retains all authoritative controls and existing requirements. Extra model fields,
incoherent additions, invented numbers/dates and attempted control overrides fail
with MODEL_OUTPUT_INVALID. No place data or compiler endpoint is connected.

This replaces model rewriting of the whole ConstraintSet: an observed Gemma echo
doubled 50000 minor units and invented a date. That failure remains preserved and
has a regression fixture. Control preservation is an architectural guarantee of
the merger, not a claim that the model reasons reliably about numbers.

Explicit unsupported safety/accessibility language has deterministic retention
guards. Benchmark raw model semantics separately from merged output and guards.
The normalized vocabulary is deliberately limited; extend it only with grounded
requirements and held-out parser cases. No dependency, model-provider framework,
agent handoff, UI, ranking, or discovery adapter is added.


Measured diagnostic calls on Gemma 4 showed that schema enforcement alone did
not ground semantic extraction. Supply the same schema in the input prompt as
well as Ollama format, then validate its output. System-role and thinking pilots
failed and remain preserved. Original unsupported source text is retained in
output requirements/failures so normalization does not drop named allergens.
