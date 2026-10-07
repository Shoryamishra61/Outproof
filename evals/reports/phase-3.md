# Phase 3 — real local Gemma constraint parser

Gate: **PASS for the specified 100-case parser and fail-closed safety acceptance**,
locally verified 2026-10-07. Reference configuration: explicit
`gemma4:e2b-it-qat`, temperature 0, seed 42, context 4096, prediction limit 384,
thinking disabled, schema supplied in both prompt and Ollama format.

This is real CPU model inference over authored synthetic sentences, **zero real
outings**. Raw exact hard/soft accuracy is **82%**, not perfect. The final guard
returns 90/100 requests; the other ten fail closed. This gate does not establish
held-out language accuracy, real place grounding, field latency or submission readiness.

## Files changed

- `services/api/app/parser.py`: local Ollama adapter, internal ParserAdditions,
  deterministic merge, source binding, immutable controls and typed failures.
- `prompts/parser.md`: finite normalized hard/soft extraction prompt.
- `evals/cases/parser.py`: exactly 100 authored synthetic cases.
- `evals/runner/parser.py`: real inference benchmark with model/source hashes,
  raw outputs and per-case errors; refuses to overwrite previous results.
- `evals/runner/parser_replay.py`: explicitly offline final-guard replay.
- `tests/test_parser.py`: 63 offline boundary and regression tests.
- `fixtures/contracts/gemma-control-corruption.json`, fixture README: historical
  50000 -> 100000 corruption and invented departure retained as recorded observations.
- `docs/ADR/0006-parser-additions.md`, `docs/PROMPT_CONTRACTS.md`: authority boundary.
- Model-specific JSON reports, `parser-pilots.md`, this report; task/build status.

All 17 exported domain schemas and frontend contracts remain unchanged.
`compilation_available` remains false. Parser is a callable adapter; compiler/API
intake wiring, ranker, providers and outing UI remain unimplemented.

## Behavior

The model proposes additions. Code retains budget, currency, scope, duration,
origin, departure, party mode, strictness and existing hard/soft requirements.
Authoritative numeric values are absent from the model request. Known optional
control proposals must be null, even when a model echoes an identical value.
Only unknown optional fields may receive explicitly sourced party/walking/dated
return values. Clock-only deadlines become hard time-clarification requirements;
no date is invented. Walking preferences do not become guessed numerical limits.

Malformed/duplicate/extra output, mismatched hard extraction, wrong-field numbers,
invented dates and known-control proposals fail closed. Allergy/accessibility/
safety requirements retain normalized needs-evidence labels **and original source
text**, including named allergens, in successful unsupported output or failure.
Policy subsequently rejects unsupported requirements. No model calls occur in policy.

## Population and metric definitions

15 clean English, 15 Indian English, 15 Hinglish, 10 ambiguous, 10 multiple hard,
10 budget scope, 10 time/deadline, 10 walking/diet/exclusion, 5 unsupported.
Eight cases require unsupported handling when clock-only deadlines are included.

UI controls deliberately stay INR 50000/person, four people and 90 minutes even
when text requests another value/currency. This tests precedence, not free-text
budget/currency conversion. Unknown party-size filling is verified offline with
explicit numeric source text. This authored development suite is not held out.

Exact extraction compares normalized sets, including correct absence. Static
IR shape validation and **full requested schema validation** are separate: both
models emit four non-null known-party proposals despite the requested const=null.
Shape-valid JSON therefore scores 100%, but requested-schema validity is 96%.
The final guard rejects all four. Rejected proposals never count as preserved
successful outputs or actual control corruption. Zero corruption with no successful
outputs is vacuous; see the preserved failed 1B run below.

Place counts measure forbidden place/venue/coordinate/route fields at this finite
schema boundary. They do not measure real venue grounding. No model invents or
returns a venue in the accepted parser output. Parser-call latency is not Time To Grass.

## Matched updated model comparison — 100 real calls each

The two run-2 files have identical prompt, adapter and case hashes, and identical
settings. The model is the changed variable. Each report records its exact digest.

| Metric | Gemma 3 4B | Gemma 4 E2B QAT |
|---|---|---|
| Static IR shape valid / 100 | 100 | 100 |
| Returned with benchmark-time guards / 100 | 80 | 92 |
| Controls preserved / returned | 80 | 92 |
| Actual authoritative corruption | 0 | 0 |
| Currency preserved / returned | 80 | 92 |
| Numeric controls preserved / returned | 80 | 92 |
| Hard/soft exact / 100 | 72 | 82 |
| Exclusion exact / 100 | 88 | 97 |
| Dietary exact / 100 | 100 | 99 |
| Soft preference exact / 100 | 88 | 88 |
| Raw unsupported retained / 8 | 3 | 5 |
| Merged unsupported retained / 8 | 7 | 7 |
| Unsupported retained in explicit failure / 8 | 1 | 1 |
| Hallucinated place fields | 0 | 0 |
| Invented fields | 0 | 0 |
| All eight additions exact / 100 | 68 | 80 |
| Median parser call, ms | 10135 | 3488 |

Benchmark-time returned counts precede the final identical-control-echo guard.
The actual deployed adapter behavior is shown by the final offline replay below.

| Exact hard/soft classification | Gemma 3 4B | Gemma 4 E2B QAT |
|---|---|---|
| clean_english | 14/15 | 15/15 |
| indian_english | 13/15 | 12/15 |
| hinglish | 13/15 | 13/15 |
| ambiguous | 5/10 | 7/10 |
| multiple_hard | 6/10 | 10/10 |
| budget_scope | 7/10 | 6/10 |
| time_deadline | 5/10 | 6/10 |
| walking_diet_exclusion | 6/10 | 8/10 |
| unsupported | 3/5 | 5/5 |

Gemma 4 is the better tested configuration on this suite: 82% versus 72% exact
classification, with median 3,488 versus 10,135 ms. Clean English 15/15, multiple
hard 10/10 and all five high-stakes cases match exactly on Gemma 4. Remaining
errors include negation, invented walking numbers, party-control proposals and
extra/missing soft preferences. These outcomes remain visible in per-case JSON.

## Final guard replay — zero new inference calls

The am/pm clock guard and strict known-control-echo guard were corrected after
freezing the model runs. Neither correction changes model-request content.
Original measured reports remain untouched; replay records source/adapter hashes.

| Final adapter result | Gemma 3 4B | Gemma 4 E2B QAT |
|---|---|---|
| Full requested schema valid / 100 | 96 | 96 |
| Returned / 100 | 78 | 90 |
| Controls preserved / returned | 78/78 (100%) | 90/90 (100%) |
| Currency/numeric preservation / returned | 78/78 | 90/90 |
| Actual control corruption | 0 | 0 |
| Accepted output missing expected hard requirement | 0 | 0 |
| Unsupported source retained / 8 | 8/8 | 8/8 |

These are offline boundary results, not improved raw-model accuracy or new calls.
Ten Gemma 4 requests reject in the final adapter: four requested-schema violations
and six other semantic/source-binding failures. Soft interpretation errors may
remain in accepted output; soft preferences never override policy.

## Preserved failures and diagnostic runs

| Separate historical run, 100 calls | IR shape valid | Returned then | Hard/soft exact | Place/extra fields | Median ms |
|---|---|---|---|---|---|
| Gemma 3 1B run 1 | 97 | 81 | 0 | 0/0 | 3990 |
| Gemma 3 1B run 2 | 100 | 0 | 0 | 0/0 | 5703 |
| Gemma 3 4B run 1 | 100 | 64 | 41 | 0/0 | 8879 |
| Gemma 4 E2B run 1 | 100 | 70 | 46 | 0/0 | 7020 |

Their raw/per-field/control/unsupported metrics remain in their own JSON files.
Different revisions are not pooled or represented as a model-only comparison.
The 1B run accepting zero outputs is a failed parser, despite zero corruptions.

Five system-role-only calls still failed semantic extraction; only optional
coffee matched exactly. Three thinking=true calls with 1024 prediction tokens
failed semantics and truncated one response, taking 38,642 / 39,769 / 52,231 ms.
Those variants were not promoted. Five schema-in-prompt diagnostic calls produced
four exact matches, supporting the focused request correction recommended by
[Ollama documentation](https://docs.ollama.com/capabilities/structured-outputs).
The remaining pilot still invented a short-outing preference. All three pilots
preserve full requests/responses in separate JSON, not a pooled benchmark score.
Earlier 1B array/boolean/loose-JSON failures are preserved in `parser-pilots.md`.

Offline failure-before-fix evidence: eight merge/source regressions first gave
8 failures / 48 passes; am/pm clock regression gave 1 failure / 58 passes; four
known-control echoes gave 4 failures / 59 passes. Final parser: **63 passed** in
0.55 s. The known historical budget doubling/invented departure remains tested.

## Exact commands and repository verification

```powershell
$env:PYTHONPATH = 'services/api'
uv run python -m evals.runner.parser --model gemma3:1b --output evals/reports/parser-gemma3-1b-run-1.json
uv run python -m evals.runner.parser --model gemma3:1b --output evals/reports/parser-gemma3-1b-run-2.json
uv run python -m evals.runner.parser --model gemma3:4b --output evals/reports/parser-gemma3-4b-run-1.json
uv run python -m evals.runner.parser --model gemma4:e2b-it-qat --output evals/reports/parser-gemma4-e2b-qat-run-1.json
uv run python -m evals.runner.parser --model gemma3:4b --output evals/reports/parser-gemma3-4b-run-2.json
uv run python -m evals.runner.parser --model gemma4:e2b-it-qat --output evals/reports/parser-gemma4-e2b-qat-run-2.json
uv run python -m evals.runner.parser_replay --input evals/reports/parser-gemma3-4b-run-2.json --output evals/reports/parser-gemma3-4b-guard-replay-3.json
uv run python -m evals.runner.parser_replay --input evals/reports/parser-gemma4-e2b-qat-run-2.json --output evals/reports/parser-gemma4-e2b-qat-guard-replay-3.json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
uv run python 'C:/Users/SHORYA MISHRA/.agents/skills/anti-slop-ui/scripts/ui_audit.py' apps/web --fail-on low
```

Each benchmark command ran 100 actual local model calls and completed exit 0.
Runs were sequential, explicitly unloading the previous model before the next.
Commands refuse overwriting preserved final reports; reproduce with new filenames.

Full verification exit 0 on 2026-10-07: Ruff zero findings; 61 files formatted;
**169 tests passed in 1.46 s** (106 Phase 0–2, 63 parser); **17 schemas**;
**60/60** structural eval; **85/85** policy eval; TypeScript strict pass;
Vite production build pass in **1.44 s**. UI source audit: five files, zero findings.
No UI edits, new browser/field tests or remotely executed CI are claimed.

## Hardware and limits

Portable Ollama 0.35.1, cloud disabled, CPU execution; both models report
size_vram=0 and context=4096. Gemma 3 4B: installed 3,338,801,804 bytes, Q4_K_M,
4.3B reported parameters; loaded size 2,881,811,905 bytes. Its cold quiet smoke
took 13,862 ms and extracted only quiet. Gemma 4 E2B QAT: installed
4,336,358,185 bytes, Q4_0, 4.6B reported parameters; loaded size 3,903,816,988
bytes. About 1.0–1.4 GiB free physical RAM remained during its earlier benchmark.
These are observations, not universal hardware minimums. E4B/GPU were not tested.
The default `gemma4:e4b` setting remains unverified; reference calls use the
explicit tested E2B tag. No automatic model fallback hides failed experiments.

Normalized vocabulary and lexical retention guards are deliberately finite.
Arbitrary paraphrases, spelled-out numeric intake, unsupported categories and
held-out accuracy remain unverified. Values needing dates or evidence do not
become guessed facts. No clinical/accessibility/safety guarantee is supported.
Parser acceptance covers the stated benchmark and deterministic boundaries;
18 raw exact-classification errors and ten final rejected requests remain limits.
Phase 4 and all provider/compiler/ranker/UI/field work remain deferred.
