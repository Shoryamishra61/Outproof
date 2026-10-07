# 0008 — Fixture architecture with a separate real-evidence gate

The post-Phase-7 instruction explicitly permits architecture development while
the real Chennai evidence pack is incomplete. Preserve the Phase-1 contracts,
eleven canonical checks and hard-policy semantics.

Internal orchestration consumes the existing discovery/enrichment/routing
interfaces, bounds discovery to the builder's 12 candidates, builds deterministic
templates and returns only revalidated plans. Primary identity and prior source
objects cannot be changed by enrichment. Contradictions remain explicit and
invalidate that candidate; other valid candidates may survive a provider failure.

Crosswalk uses normalized name plus a 40 m coordinate bound; optional category,
address, phone and domain evidence can reject a match. Multiple matching provider
identities are ambiguous. Proximity is never used for travel feasibility.
Bindings retain provider identity, timestamp, reference and accepted signals.

opening-hours-py 2.1.4 supplies OSM parsing. Explicit venue timezone is required;
minute-resolution schedules are checked across UTC instants to handle folds.
Derived dwell windows retain raw observation timestamps. Unsupported context is
unknown; the policy's existing hour freshness and full-dwell checks still apply.

Gemma receives valid plan summaries only and returns an existing ID. The reason
has finite wording to prevent model-generated venue/operational claims. Proof is
computed in pure domain code with exact group money arithmetic and all sources.
Evidence is rechecked after ranking, before constructing one CompiledPlan.

Default POST compile returns typed unavailable. Three backend settings are
required for fixture success: compilation enabled, fixture mode, development
environment. Requests must explicitly say FIXTURE. Production web builds cannot
activate the fixture UI. Health stays false regardless of these dev flags.
There is no environment-variable route to an unproven LIVE success.

Fixture timestamp shifting materializes a fictional scenario only. Recorded live
artifacts are never shifted or overwritten. Optional expenses do not enter the
mandatory aggregate. Public LIVE compilation needs a future audited evidence pack
and unchanged-policy real acceptance; a credential alone does not establish it.
