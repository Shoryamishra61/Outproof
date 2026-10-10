# Deployment

Public frontend: https://outproof-web.onrender.com

Production API: https://outproof-api.onrender.com

Repository: https://github.com/Shoryamishra61/Outproof (branch `master`). Both Render services use free plans. No new cash spending, overages, training or subscriptions are authorized.

| Service | ID | Build/start |
|---|---|---|
| API | srv-db3vs6ub7d7c739r2sq0 | `pip install uv==0.11.9 && uv sync --locked --no-dev`; `uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-access-log` |
| Web | srv-db3vs8eb7d7c739r31l0 | `npm ci && npm run check`; publish `apps/web/dist` |

Python 3.12.13 and locked dependencies are used. GitHub Actions runs canonical checks and browser regression checks. Render autodeploy is `checksPass`. A green workflow and matching `/v1/version` SHA are separate requirements; consult the final production report for their observed values.

API configuration: `PYTHONPATH=services/api:packages/domain/src`, `GROUND_RULE_ENV=production`, compilation/LIVE true, fixture false, `GEMMA_MODEL=gemma4:e2b-it-qat`, exact frontend CORS origin and API trusted host. Secret names are `GEMMA_API_KEY`, `OLLAMA_BASE_URL`, `SERPAPI_API_KEY` and `SENTRY_DSN`; they are configured server-side. Optional search is explicitly enabled in the observed service configuration; the blueprint defaults it off. The frontend receives only the public API URL and LIVE/voice flags, never credentials.

Local `.env.release`, tools, model weights and credential files are ignored by Git. Env files must be loaded explicitly; shell and uvicorn do not automatically ingest arbitrary release files. Keep Ollama on loopback 11436 and the authenticated proxy on loopback 11435. Do not direct a public tunnel at raw Ollama.

The installed release model is `gemma4:e2b-it-qat` (digest `07ea59a474013479c8b6b802bef095c40e964a1d776ba02f264c0e30e1aede0c`), served by `.tools/ollama/ollama.exe` with model storage in `.tools/models`. This is separate from desktop Ollama's default port 11434. To inspect the already-running project server in PowerShell:

```powershell
$env:OLLAMA_HOST='http://127.0.0.1:11436'
& .\.tools\ollama\ollama.exe list
Invoke-RestMethod 'http://127.0.0.1:11436/api/ps'
```

The actual RTX 3050 Laptop GPU has 4096 MiB VRAM; this quantized model uses GPU and system RAM with a 4096-token context. No additional download is needed. The parser adapter is `services/api/app/parser.py`; ranking is `services/api/app/ranker.py`. The API validates both model outputs and never lets either invent source facts or bypass hard checks. An actual public run after an idle period took 22.162 seconds to the plan; this one measurement does not establish a general latency guarantee.

`GET /v1/health/live` checks the process. `/v1/health/ready` probes the model tag, official source and routing service with a 60-second cache; a listing alone is not inference evidence. `/v1/version` reports environment and commit. Legacy `/v1/health` is bootstrap information and deliberately does not claim compilation availability.

Readiness checks the model and one available reviewed Singapore or India source/route, with bounded fallback probes. It does not establish selected-area or global compilation. Potheri outage diagnostics and the configured `OVERPASS_URL` are documented in [the incident report](../evals/reports/release-potheri-incident.md). Provider failures expose a cooldown interval through `Retry-After`; logs retain exception class/status, not coordinates or raw queries. Restore the prior discovery provider by setting `OVERPASS_URL=https://overpass-api.de/api/interpreter` and redeploying a green build, then verify discovery from production before claiming recovery.

The Cloudflare named tunnel has no existing domain route, so the authorized fallback is a temporary authenticated quick tunnel. Its hostname can change after restart. Update the server-side URL and redeploy if it changes. Render free services may sleep and incur cold starts. This release does not promise 24/7 availability.

## Real post-deployment verification

`.github/workflows/production.yml` follows successful trusted master pushes and supports manual dispatch. It waits for the exact public API commit, checks Outproof frontend, fixture prohibition, model identity and allowed/denied CORS, then requires one actual reviewed LIVE Gemma parser/ranker outing and two typed hard-rule refusals. Evidence uploads even on failure. This uses no GitHub secrets or privileged PR code. It can fail during venue closure or provider/laptop outage; those are recorded availability limits, not passing results. The existing Checks workflow remains the Render checksPass deploy trigger.

Reproduce with `PYTHONPATH=services/api:. uv run python scripts/verify_production.py --commit <exact-sha>` (PowerShell uses `.;services/api`). Do not repeatedly run this against public map providers. It is a bounded smoke, not complete geographic or physical certification.
