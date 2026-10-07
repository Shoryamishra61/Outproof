# Synthetic contract fixtures

These files are fictional structural examples. They are not sourced venues,
routes, opening hours, prices, or validator measurements. Compiled examples
must use `mode: FIXTURE`; their PASS checks are synthetic markers.

`evals/cases/contracts.jsonl` covers valid roundtrips and invalid relationships.
Run `uv run python evals/runner/contracts.py`. It cannot measure grounding,
Gemma interpretation, real-world compliance, city coverage, or latency targets.

`gemma-control-corruption.json` preserves the recorded changed fields from the
historical unconstrained Gemma smoke failure (50000 became 100000; a departure
was invented). It is not a reconstructed complete response or a successful parse.
Phase 3 tests reject the forbidden budget/departure output fields.
