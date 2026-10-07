# Post-Phase-7 unblocking sprint

Executed locally on Windows, 2026-10-07. **Fixture architecture gate passed;
real outing acceptance gate remains blocked.** Default/public health reports
`compilation_available: false`. There are still **zero accepted real outings**.
Phase-1 domain contracts and the eleven canonical hard-policy checks were reused.
No policy/model authority was weakened to obtain a success.

## Files changed

New implementation:

- `services/api/app/identity.py`: deterministic crosswalk and accepted binding evidence.
- `services/api/app/compiler.py`: bounded provider pipeline returning only validated plans.
- `services/api/app/fixtures.py`: explicit fictional provider implementations.
- `services/api/app/ranker.py`: local Gemma, valid IDs only, fail-closed output.
- `services/api/app/compilation.py`: selection, current evidence recheck, exactly one result.
- `packages/domain/src/ground_rule/hours.py`: maintained OSM hours parser abstraction.
- `packages/domain/src/ground_rule/proof.py`: exact cost aggregation, deterministic proof lines and source inspection.
- `fixtures/compiler/accepted-chennai.json`: complete, entirely FIXTURE-labelled scenario.
- `contracts/domain.ts`: types generated from the existing contract schemas.
- `evals/runner/post_phase_7.py`: separate actual-model fixture compiler observation runner.

Updated implementation/configuration:

- `services/api/app/enrichment.py`, `places.py`, `main.py`: typed enrichment, raw hours/timezone provenance, gated compile endpoint.
- `scripts/export_contracts.py`: generated TypeScript contract drift checking alongside the 17 JSON schemas.
- `prompts/ranker.md`: ID-only selection contract; no fact generation.
- `apps/web/src/main.tsx`, `style.css`, `tsconfig.json`, `index.html`, `package.json`, `package-lock.json`: fixture product flow, runtime schema validation, responsive accessible states.
- `pyproject.toml`, `uv.lock`: opening-hours-py 2.1.4 and timezone database dependencies.
- `.env.example`: compilation/fixture defaults false; measured local E2B model default.

Tests/documentation:

- Eight new test modules listed below; existing `test_enrichment.py` adapted to its richer return type and `test_bootstrap.py` updated from the old absent-route 404 to the required typed disabled-route 503.
- `docs/OPENING_HOURS.md`, `docs/FIXTURE_UI.md`, `docs/ADR/0008-fixture-compiler-live-gate.md` added.
- `TASKS.md`, `BUILD_ORDER.md`, `README.md`, `docs/DEV_DRAFT.md`, `evals/reports/BLOCKED.md`, `full-eval.md` updated. `overnight-handoff.md` retains its historical results beneath a supersession note.
- Two new model observation JSON files and five labelled UI screenshots, linked below. Earlier failed experiments, live observations and the 50000-to-100000 Gemma regression are preserved.

This checkout has no tracked baseline/HEAD; `git status --short` reports the repository as untracked. No reset, re-bootstrap, commit, or previous-artifact overwrite was performed. This inventory identifies this sprint's work, not a fabricated Git diff.

## Behaviors and acceptance

### A / C — Enrichment and identity

`EnrichmentProvider`, `IdentityBinding`, `ProviderEvidence`, `EvidenceFreshness`
and `EnrichmentResult` exist. Matching requires normalized name **and** coordinates
within 40 m, with a provider ID. Category/address/phone/domain contradictions can
reject the match. Multiple eligible identities or duplicate ambiguous responses
return AMBIGUOUS; name alone cannot bind. Accepted signals, provider IDs,
observation time and source reference are persisted. This distance is only an
identity signal, never a travel feasibility estimate. The final binding is code,
not an LLM decision.

Field observations retain their timestamps. Missing price/hours are explicit;
stale/future data does not establish current facts. Conflicts are retained and
invalidate the candidate. Weak/equal evidence cannot refresh or replace stronger
evidence. The compiler additionally prevents mutation of primary identity or loss
of original provenance. SerpApi price levels, open-now and prose hours stay
metadata; they do not become complete mandatory cost or dwell coverage.

The requested exact/ambiguous/wrong-coordinates/wrong-brand/missing-ID, stale
price/hours, contradictory price/hours, absent price/hours and timeout cases are
covered by the crosswalk/enrichment/compiler tests. Fixture identities remain
FIXTURE; external-provider test payloads are synthetic, not live observations.

### B — Opening intervals

Uses the maintained [opening-hours-py implementation](https://github.com/remi-dupre/opening-hours-rs)
at version 2.1.4, rather than a new partial grammar. Evaluates the entire
half-open dwell interval across actual UTC minute boundaries with explicit IANA
timezone. Weekday schedules, multiple intervals, overnight opening, closed days,
arrival before opening, dwell over closing, exact departure at closing, repeated
hours and spring gaps are tested. Raw hours/timezone evidence is connected to
the compiler; derived windows preserve observation time and source reference.

Unknown syntax/warnings/state or missing context return UNKNOWN. Holiday/solar
context, appointments/provider prose, pre-1970 instants, second-offset timezones
and visits over 48 hours are unsupported. No venue timezone is guessed.
See `docs/OPENING_HOURS.md`. Existing freshness rules still apply.

### D / E — Accepted fixture and orchestration

Target: INR 500/person, 90 minutes, two friends, vegetarian required, no mall,
quiet preferred. Every place, coordinate, route, return route, cost upper bound,
diet/exclusion assertion, opening interval and timestamp is labelled FIXTURE.

Two complete fictional cafes survive unchanged policy: **2 valid plans, 22/22
hard checks PASS**. The selected fixture costs INR 410/person, INR 820 for two
against INR 1,000 group allowance. Duration is **62 minutes = 8 outbound + 45
dwell + 9 return**; walking distance is **1,250 m**. There is no explicit deadline,
so the canonical RETURN_TRIP check verifies the complete return with no deadline
restriction. These are authored fixture values, not measured venue prices/routes.

Pipeline: discovery -> enrichment -> directed routing -> existing deterministic
templates -> full interval hours -> unchanged hard policy -> valid plans only.
Zero/one/multiple valid plans, duplicates, candidate invalidation, all invalid,
provider timeouts and route failures are exercised. One failed candidate can be
discarded while another independently valid candidate survives. No valid set
means no ranker call. Fixture data fails default live policy.

### F — Gemma ranker

Receives soft preferences and summaries of already-valid plans. Dynamic ID enum,
strict output schema, duplicate-key rejection and membership validation prevent
selection of unknown/rejected plans. No facts are editable. A finite reason
(`Selected for your soft preferences.`) prevents invented venue prose. Invalid
IDs, invented venue/extra fields, malformed JSON, rejected inputs and model
timeout fail closed. Tie guidance uses fewer stops, less walking, then input
order. This smoke does not measure subjective ranking quality.

Actual local CPU model observations, kept separate:

| Model | Fixture scenarios | Result | Valid candidates | Hard checks | Observed elapsed |
|---|---:|---|---:|---:|---:|
| gemma4:e2b-it-qat | 1 | SUCCESS | 2 | 22 PASS | 22,252.63 ms |
| gemma3:4b | 1 | SUCCESS | 2 | 22 PASS | 27,434.55 ms |

Each selected the first valid fixture cafe. Timing covers the runner's measured
compiler/model section, including model metadata lookup and load effects; the
initial independent candidate enumeration is outside that timer. These are
single observations, **not medians, parser scores or field Time To Grass**.
Model digests, fixture SHA-256, execution time, complete result and proof lines:

- [E2B observation](compiler-gemma4-e2b-fixture-1.json)
- [Gemma 3 4B observation](compiler-gemma3-4b-fixture-1.json)

E4B/GPU was not qualified in this sprint; no combined model score is reported.
Historical parser benchmarks and control-corruption failure remain separate.

### G / H — Deterministic proof and one result

Proof construction reruns policy and requires the exact current validation
result. Exact mandatory group totals use integer money and same-currency
arithmetic. Check IDs, evidence IDs, totals and selected plan align; **11 proof
lines and 11 source records** are retained in each observed compiled fixture.
Source timestamps/reference/expiry remain inspectable; stale-source inspection
is tested. Evidence expiring while ranking prevents successful compilation.
No model writes proof. Rejected plans, alternate/options fields, mismatched
totals/proof or fixture masquerading as LIVE are rejected.

### I — API gate

`POST /v1/plans/compile` exists. Default disabled response: **503**, typed
`SOURCE_TEMPORARILY_UNAVAILABLE`, even before parsing a request body. Explicit
fixture configuration requires all three settings:

```text
GROUND_RULE_COMPILATION_ENABLED=true
GROUND_RULE_FIXTURE_MODE=true
GROUND_RULE_ENV=development
```

Request mode must be FIXTURE. Malformed controls/parser/ranker output fail closed;
provider failure is typed unavailable; no valid plan is a typed failure.
Overall compile timeout is 180 seconds; local ranker has a 120-second bound.
Successful fixture response contains exactly one CompiledPlan. There is **no
configuration route to successful LIVE compilation**. All eight setting
combinations are tested. Health remains false even in fixture dev mode. Example
defaults remain false; only the local demo process was explicitly enabled.

### J / K — Fixture UI and GO

HOME -> COMPILING -> ONE PLAN -> expandable PLAN PROOF -> GO practice, with
persistent fictional/FIXTURE disclosure. Production builds cannot enable the
fixture UI; this was verified at `http://127.0.0.1:4173`. The development demo at
`http://127.0.0.1:5173` uses the explicit fixture API and local Gemma. Empty text
uses structured controls; a real local parser+ranker request with vegetarian,
no-mall and quiet free text also succeeded without changing budget/duration.

GO displays one destination/action and Phone down. Its three practice steps are
8-minute walk, 45-minute dwell, 9-minute return. Fictional destinations have no
external navigation links. There is no feed, carousel, reroll or map browser.

Visual thesis: **a field note with a receipt**. Signature decisions: persistent
FIXTURE identity, scoped cost/time before one sequence, source ledger plus one
next GO action. Existing paper/grass tokens and native controls are reused.

Browser verification:

- 360x900, 768x900, 1024x900, 1440x900: no horizontal overflow. Final default mobile HOME fits within 900 px; expanded optional controls/proof can scroll vertically.
- Keyboard intake -> compile -> proof -> GO; visible focus; focused headings through every GO step, including final step after Next disappears.
- Loading/cancel returns to retained controls; zero-budget failure stays honest; API outage disables compilation and offers Check connection; reconnection works.
- Success returns one 62-minute INR 820 fixture plan; proof exposes all 11 checks/source records. Latest browser warning/error collection: empty.
- Token contrast against paper, calculated with WCAG relative luminance: ink **11.86:1**, muted **5.95:1**, grass/button **9.39:1**, focus **5.69:1**. Text passes AA; focus passes 3:1.
- No animation/transition is introduced; reduced-motion CSS is present. OS reduced-motion emulation and physical phone/assistive-technology testing were not performed.
- Production build: 217 modules, 387.59 kB JS / 118.84 kB gzip; not a measured field performance score.

Screenshots: [mobile HOME](fixture-home-mobile.jpg), [mobile compiling](fixture-compiling-mobile.jpg),
[mobile result](fixture-result-mobile.jpg), [desktop result](fixture-result-desktop.jpg),
[mobile GO practice](fixture-go-mobile.jpg). Temporary browser viewport was reset.

## Exact verification

Final complete command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
```

| Check | Observed result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | 110 files already formatted |
| `uv run pytest` | **417 passed, 2 skipped**, 419 collected; 4.14 s |
| `uv run python scripts/export_contracts.py --check` | 17 schemas checked; generated TypeScript drift also checked |
| `uv run python evals/runner/contracts.py` | **60/60 PASS**, synthetic structural fixtures |
| `uv run python -m evals.runner.policy` | **85/85 PASS**, synthetic policy fixtures |
| `npm run check --prefix apps/web` | strict TypeScript PASS; Vite production build PASS, 2.81 s |

The two skips are opt-in provider integration tests; this suite did not rerun
live discovery/routing. Previously executed live observations remain preserved.

New tests, separately rerun:

```powershell
uv run pytest tests/test_crosswalk.py tests/test_hours.py tests/test_hours_pipeline.py tests/test_compiler.py tests/test_ranker.py tests/test_proof.py tests/test_compilation.py tests/test_compile_api.py -q
```

**103 passed in 4.66 s**:

| New module | Cases |
|---|---:|
| test_crosswalk.py | 20 |
| test_hours.py | 23 |
| test_hours_pipeline.py | 7 |
| test_compiler.py | 13 |
| test_ranker.py | 11 |
| test_proof.py | 6 |
| test_compilation.py | 7 |
| test_compile_api.py | 16 |
| Total | 103 |

The prior 314 passing tests remain green alongside these 103. Expected API
bootstrap behavior intentionally changed from absent route to gated typed route.

```powershell
uv run python 'C:/Users/SHORYA MISHRA/.agents/skills/anti-slop-ui/scripts/ui_audit.py' apps/web
```

**0 findings** across 5 source files (high/medium/low/info all zero). Browser QA
above is separate from this heuristic source audit.

Actual model runner commands:

```powershell
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.post_phase_7 --model gemma4:e2b-it-qat --output evals/reports/compiler-gemma4-e2b-fixture-1.json
uv run python -m evals.runner.post_phase_7 --model gemma3:4b --output evals/reports/compiler-gemma3-4b-fixture-1.json
```

Both exited successfully. Frozen JSON results were subsequently reloaded with
CompiledPlan validation, unchanged-policy proof reconstruction, exact rendered
proof comparison and fixture SHA check: **2/2 valid**. No model rerun was needed
for that artifact integrity check. Runner refuses to overwrite observations.

Development failures corrected before final gate: initial unknown-hours tests
exposed the library-specific ParserError (two failures); exception handling now
returns UNKNOWN. UI audit initially reported seven label heuristics; explicit
input IDs and browser accessible-name checks resolved them. Final review added
a UTC dwell projection regression across DST folds and fixed keyboard focus
when the final GO Next button disappears. One artifact inspection lacked
PYTHONPATH and failed import; it was rerun with the explicit path above. No
remaining test failure is hidden by the final counts.

## L / M — Live provider state and remaining blocker

Presence-only check: process `SERPAPI_API_KEY` **absent**; local `.env` **absent**.
No key was printed/committed. No new live enrichment call or real accepted-plan
artifact was manufactured. Existing real Chennai observations still show 39
grounded POIs and five directed walking legs. The first real candidate remains
rejected: 4,149 seconds, 2,012 m, six checks PASS and five FAIL for missing
currency/cost confidence/budget, dwell hours and no-mall evidence. See
`templates-chennai-real-data-1.json`; it was not overwritten.

**Exact blocker:** one real candidate still lacks complete current,
identity-linked mandatory cost proof (currency/scope/conservative upper bound),
opening hours covering arrival through dwell, and affirmative no-mall/containment
evidence. A credential alone is not guaranteed to supply those facts.

**Exact next action:** obtain an authorized operational evidence source for that
Chennai target; configure any credential privately; bind actual provider identity;
normalize real price/hours/vegetarian/no-mall facts with timestamps/provenance;
refresh expired directed outbound/return routes; save a new observation artifact;
run the exact target through unchanged hard policy. Only an all-check real pass
permits real CompiledPlan/proof, local LIVE enablement, evidence screenshot and
then additional candidates/50-case, 10-city compiler evaluation.

Limitations: identity matching is deliberately conservative (40 m/exact normalized
name); ambiguous real crosswalks fail. Candidate enumeration is capped at 12;
ranking quality/latency distribution is not benchmarked. Optional costs remain
optional under existing normalization. Hidden backup, revalidation at actual GO
time, true offline outing operation, hosted compilation, 50 real scenarios,
10 cities, three physical field tests and field metrics remain unfinished.
The article is an unpublished architecture draft, not a submission-ready claim.

**Tasks A–K and M are satisfied for explicit fixtures. Task L is conditional and
blocked by missing live credentials/evidence. The LIVE acceptance gate is NOT
satisfied, and public compilation remains disabled.**
