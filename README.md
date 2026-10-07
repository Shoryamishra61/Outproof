# Ground Rule

> **Your limits in. One real plan out.**

Ground Rule is an **open-weight AI outing compiler** prototype for Hacktoberfest 2026 Week 1: **Touch Grass**, targeting global discovery and India-first field testing.

Current scope: contracts, deterministic hard policy, a measured local Gemma
parser, live Chennai OSM/Valhalla adapters, and deterministic candidate templates.
The first real candidate was rejected for missing price/hours/exclusion evidence.
An internal and explicitly gated FIXTURE compiler/ranker/proof/UI now work. Real outing compilation, global coverage, and field testing remain unverified;
`compilation_available` remains false. See [post-Phase-7 report](evals/reports/post-phase-7.md).

## Local development

Requires Python 3.12+, Node 24, uv, and local Ollama. The measured parser uses
explicit `gemma4:e2b-it-qat`, now the development default. Gemma 4 E4B remains unverified. Gemma 3 4B was measured separately, not pooled into that score.
Dependencies are pinned in `uv.lock` and `apps/web/package-lock.json`.

```powershell
./scripts/setup.ps1
# Run these in separate terminals:
uv run uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000
npm run dev --prefix apps/web
./scripts/start_ollama.ps1
# With Ollama running:
$env:GEMMA_MODEL = "gemma4:e2b-it-qat"
ollama pull gemma4:e2b-it-qat
uv run python scripts/check_ollama.py
./scripts/check.ps1
```

If using the ignored portable install in `.tools/ollama`, use
`./.tools/ollama/ollama.exe pull gemma4:e2b-it-qat` instead of `ollama pull`.
On constrained development hardware, explicitly set `$env:GEMMA_MODEL = 'gemma3:1b'`
and pull that tag to run the bootstrap smoke. This override does not benchmark
the configured Gemma 4 parser or change the default model.
The tested bootstrap uses `./scripts/start_ollama.ps1 -Cpu`; the GPU warm-up
attempt stalled on this machine. The CPU override changes only that process's
environment, and hosted inference is disabled by the start script.
The development page is `http://127.0.0.1:5173`; `/v1/health` reports API
availability only. The PWA manifest and service worker are bootstrap scaffolding,
not an offline outing demo. No keys are needed for these phases.

Verification evidence: [Phase 0](evals/reports/phase-0.md) and
[Phase 1](evals/reports/phase-1.md). `scripts/check.ps1` runs lint, format,
tests, schema drift, synthetic contract evals and the web build. The local model
smoke locks authoritative structured controls; it does not score free-text
interpretation. Free-text accuracy is measured separately in
[Phase 3](evals/reports/phase-3.md). No real outing compiler or submission
readiness is claimed. [Phases 4–7](evals/reports/phase-4.md) cover real provider
discovery/routing and candidate templates with honest evidence rejection.

To replay the bounded cached component demo with the benchmarked model:

```powershell
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.cached --discovery evals/reports/discovery-chennai-live-1.json --routing evals/reports/routing-chennai-live-1.json --templates evals/reports/templates-chennai-real-data-1.json --model gemma4:e2b-it-qat --output evals/reports/my-cached-replay.json
```

Requires that exact model installed locally. Output paths cannot overwrite prior
evidence. Cached routing expires under policy; this demonstrates rejection,
not a fully offline verified outing. See [cached demo](evals/reports/cached-demo.md).
Three real outing forms remain blank: [field-test preparation](docs/FIELD_TESTS.md).

The intended compiler turns a user's:
- time
- budget
- location
- party
- vibe
- hard constraints

into **exactly one grounded, feasible real-world outing**, then minimizes screen interaction.

Ground Rule is deliberately **not** a recommendation feed.


## Explicit fixture product demo

All destinations/costs/routes below are fictional and visibly labelled FIXTURE.
The default/public compiler remains disabled. In the API terminal, explicitly set:

```powershell
$env:GROUND_RULE_ENV='development'
$env:GROUND_RULE_COMPILATION_ENABLED='true'
$env:GROUND_RULE_FIXTURE_MODE='true'
$env:GEMMA_MODEL='gemma4:e2b-it-qat'
uv run uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000
```

In the Vite terminal:

```powershell
$env:VITE_GROUND_RULE_FIXTURE_MODE='true'
npm run dev --prefix apps/web
```

Open http://127.0.0.1:5173. A production web build cannot enable this fixture UI.
The API requires `mode: FIXTURE`, never accepts LIVE, and health remains false.
Default POST compile returns typed `SOURCE_TEMPORARILY_UNAVAILABLE` (503).
Complete scenario: INR 500/person, 90 minutes, friend, vegetarian, no mall, quiet.
The fixture provider materializes fictional observation timestamps for each dev
request; it never refreshes recorded live evidence. Local Gemma parses nonempty
free text and selects only unchanged-policy valid candidates. No live provider
credential is needed for this demonstration.

To repeat a separate local ranker/compiler smoke without overwriting evidence:

```powershell
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.post_phase_7 --model gemma4:e2b-it-qat --output evals/reports/my-fixture-smoke.json
```

## Product thesis

Most outing tools optimize discovery.

Ground Rule optimizes **decision termination**.

A successful session:

1. User supplies constraints in under 30 seconds.
2. Gemma converts fuzzy language into typed constraints.
3. Grounded place sources discover real candidates.
4. Routing proves physical feasibility.
5. Deterministic validators reject anything violating a hard constraint.
6. Gemma ranks only already-valid candidates.
7. User sees **one** plan plus a compact proof.
8. `GO` collapses the UI and gets the phone out of the experience.

## Core invariant

> **LLMs interpret. Data grounds. Code verifies.**

The LLM never owns:
- venue existence
- latitude/longitude
- opening hours
- route time/distance
- price arithmetic
- budget compliance
- duration compliance
- hard exclusions

## North-star metrics

- `Time To Grass`: median < 30 seconds
- `Screen Ratio`: < 5% of outing duration
- hard-constraint violations: 0
- hallucinated displayed venues: 0
- default plans shown: exactly 1
- real India field tests: >= 3
- automated global cities: >= 10
- local/open-weight inference demo: required

## Build priority

Do **not** start with UI polish.

Build this vertical slice first:

`constraints -> typed parse -> grounded places -> route facts -> candidate plans -> deterministic verification -> Gemma rank -> one plan`

Then build GO mode, source transparency, field tests, demo, and DEV post.

## Recommended stack

- Web: React + TypeScript + Vite, mobile-first PWA
- API: FastAPI + Python 3.12
- Open model: Gemma via Ollama
- Global POIs: OpenStreetMap / Overpass
- Routing: Valhalla
- Fresh enrichment: SerpApi when configured
- Community signal: optional authorized/public-search evidence only
- Observability: Sentry
- Deployment: Render
- Validation: Pydantic v2 + deterministic Python domain layer
- Testing: pytest + Vitest/Playwright

## Repository map

```text
ground-rule/
├── AGENTS.md
├── MASTER_BUILD_PROMPT.md
├── README.md
├── PRODUCT_SPEC.md
├── ARCHITECTURE.md
├── BUILD_ORDER.md
├── TASKS.md
├── EVALS.md
├── SECURITY_PRIVACY.md
├── CONTRIBUTING.md
├── Makefile.example
├── .env.example
├── apps/
│   └── web/
├── services/
│   └── api/
├── packages/
│   └── domain/
├── contracts/
├── prompts/
├── fixtures/
├── evals/
├── scripts/
├── docs/
│   └── ADR/
└── .github/
```

**Read `AGENTS.md` before changing anything.**
