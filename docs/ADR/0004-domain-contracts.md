# ADR 0004 — Pydantic contracts own structural semantics

Status: accepted for Phase 1, 2026-10-06.

Domain models are frozen, reject extra fields, and revalidate nested instances.
Pydantic v2 generates the committed JSON schemas; CI checks schema drift.
Python methods enforce cross-field relationships that generated JSON Schema
does not express. All API ingestion must still use Pydantic validation.

Money uses integer minor units and rejects cross-currency arithmetic/comparison.
Amounts are bounded by JavaScript's safe-integer limit. The prototype explicitly
supports INR, USD, GBP, SGD, JPY, EUR, AUD, CAD, and AED; other currencies fail
validation rather than acquire guessed exponents or conversions. Extend the
supported list only with currency contract tests. No major-unit conversion yet.

The starter ConstraintSet field names remain. Hard/soft string lists become
typed objects; origin, departure, walking distance, and strict-budget policy are
explicit. `return_by_local` must be a complete offset-aware datetime; ambiguous
clock-only deadlines cannot be asserted. Null remains unknown, including budget
triplets and provider facts. Empty opening windows means no known open interval;
null means operating hours unavailable. Neither makes a place eligible by itself.

Plans must contain every route leg through return to origin and source-derived
arrival times. An unreachable leg has null metrics and unknown subsequent
arrivals; its plan can exist as a rejected candidate, never as a compiled plan.
Totals derive from all legs plus dwell. Structural constraints do not prove
budget, hours, exclusions, dietary support, freshness, or provider truth.

Elapsed-time arithmetic and chronological comparisons use UTC instants so
offset changes and repeated local clock hours do not alter routing arithmetic.
Overflow of projected datetimes fails contract validation instead of escaping
as an untyped arithmetic error.

Acceptance requires all eleven hard check codes to pass. Proof must refer to the
same plan and route totals, include referenced evidence, and label synthetic
fixtures explicitly. Only Phase 2 validators may compute those checks; no model
gets authority to create an accepted result. These types alone are not a working
compiler or an independent verification of an external fact.

Evidence references compare both identifiers and values; conflicting records
under the same identifier are rejected. Compiled stops cannot omit their source
records. Provider identity/coordinate/dietary/hour authority still requires the
Phase 2 evidence policy and Phase 4 normalization.

The existing organizer eval example and prompt wording remain untouched; Phase 3
will translate its expected textual constraints to typed contracts and evaluate
the parser. Phase 1 fixtures are labelled synthetic contract tests, not global
venue or parser evaluations.
