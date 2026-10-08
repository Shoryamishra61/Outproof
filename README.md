# Ground Rule / Outproof

**Your limits in. One real plan out.** An open-weight Gemma outing compiler for Touch Grass.

Release work is in progress. Live coverage is limited to the reviewed Singapore Botanic Gardens Tanglin entrance corridor, main grounds only. Official NParks admission/hours, an OSM pedestrian gate and independent Valhalla round trips ground the compiler. Other locations may yield a typed refusal; worldwide operation is not claimed.

Anna Nagar's previous accepted result was withdrawn: a civic listing and general schedule do not prove zero admission or venue-specific hours. The correct area is 57,927 m² (~14.31 acres). See [release evidence audit](evals/reports/FINAL_EVIDENCE_AUDIT.md).

Core law: **LLMs interpret. Data grounds. Code verifies.** Exactly one plan on success; unknown facts stay unknown. Strict paid stops require verified/bounded all-in prices. No payment, profile, persistent location history or safety guarantee.

## Run and verify

Requires Python 3.12+, Node 24, uv and Ollama. Dependencies are locked. Run `./scripts/setup.ps1`, then `./scripts/check.ps1`. To use live mode, set `GROUND_RULE_ENV=development`, `GROUND_RULE_COMPILATION_ENABLED=true`, `GROUND_RULE_LIVE_MODE=true`, fixture mode false, `GEMMA_MODEL=gemma4:e2b-it-qat`; start API with `uv run uvicorn app.main:app --app-dir services/api --no-access-log` and Vite with `VITE_GROUND_RULE_LIVE_MODE=true`.

Use `.env.example` for variable names. Shells do not load env files automatically. Configure secrets in ignored local files or provider dashboards; never use frontend variables for credentials. Remote Ollama requires HTTPS plus `GEMMA_API_KEY`. The authenticated temporary laptop tunnel has no uptime guarantee; it is not stable hosting.

`/v1/health/live` reports the process only. `/v1/health/ready` probes the configured model tag, authoritative source and route service, cached for 60 seconds. `/v1/version` exposes build SHA. Production forbids fixture mode.

## Evidence

The current checkpoint records 4,096 distinct controlled compiler journeys, 300 adversarial cases and 100 Chromium journeys. These are synthetic/control tests, not actual outings. Local real Gemma ranker inference was executed. Cloud/browser/CI evidence is still being assembled; use [current verdict](evals/reports/FINAL_RELEASE_VERDICT.md), not older reports. Three physical outings remain unexecuted.

MIT source code. Model/data/audio terms are separate: [NOTICE](NOTICE). OpenStreetMap © contributors, ODbL. Gemma weights are not redistributed. Free ElevenLabs audio is an opt-in, noncommercial attributed demo.

Public repository: https://github.com/Shoryamishra61/Outproof . DEV article stays a draft pending author approval.
