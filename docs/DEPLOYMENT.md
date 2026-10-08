# Deployment

Public frontend: https://outproof-web.onrender.com

Production API: https://outproof-api.onrender.com

Repository: https://github.com/Shoryamishra61/Outproof (branch `master`). Both Render services use free plans. No new cash spending, overages, training or subscriptions are authorized.

| Service | ID | Build/start |
|---|---|---|
| API | srv-db3vs6ub7d7c739r2sq0 | `pip install uv==0.11.9 && uv sync --locked --no-dev`; `uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-access-log` |
| Web | srv-db3vs8eb7d7c739r31l0 | `npm ci && npm run check`; publish `apps/web/dist` |

Python 3.12.13 and locked dependencies are used. GitHub Actions runs canonical checks and browser regression checks. Render autodeploy is `checksPass`. A green workflow and matching `/v1/version` SHA are separate requirements; consult the final production report for their observed values.

API configuration: `PYTHONPATH=services/api`, `GROUND_RULE_ENV=production`, compilation/LIVE true, fixture false, `GEMMA_MODEL=gemma4:e2b-it-qat`, exact frontend CORS origin and API trusted host. Secret names are `GEMMA_API_KEY`, `OLLAMA_BASE_URL`, `SERPAPI_API_KEY` and `SENTRY_DSN`; they are configured server-side. Optional search is explicitly enabled. The frontend receives only the public API URL and LIVE/voice flags, never credentials.

Local `.env.release`, tools, model weights and credential files are ignored by Git. Env files must be loaded explicitly; shell and uvicorn do not automatically ingest arbitrary release files. Keep Ollama on loopback 11436 and the authenticated proxy on loopback 11435. Do not direct a public tunnel at raw Ollama.

`GET /v1/health/live` checks the process. `/v1/health/ready` probes the model tag, official source and routing service with a 60-second cache; a listing alone is not inference evidence. `/v1/version` reports environment and commit. Legacy `/v1/health` is bootstrap information and deliberately does not claim compilation availability.

The Cloudflare named tunnel has no existing domain route, so the authorized fallback is a temporary authenticated quick tunnel. Its hostname can change after restart. Update the server-side URL and redeploy if it changes. Render free services may sleep and incur cold starts. This release does not promise 24/7 availability.
