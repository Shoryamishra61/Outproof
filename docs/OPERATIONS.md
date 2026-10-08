# Operations and recovery

Keep the inference laptop plugged in, awake, lid open and online. The proxy requests Windows system-awake state while running, but cannot prevent shutdown, manual sleep or network loss. Never make an unauthenticated public Ollama service a recovery shortcut.

First inspect `/v1/version`, `/v1/health/live`, `/v1/health/ready` and the client request ID. Technical logs contain stage timings, validation/rejection status and request IDs. Sentry technical spans are sampled; absence of a sampled span is not evidence that a request never ran. No private prompt/GPS should be pasted into an incident record.

| Failure | Recovery |
|---|---|
| Model unavailable | Check dedicated local `/api/tags`, model tag/digest, proxy authentication and tunnel. Restart only the owned release processes; keep desktop Ollama instances separate. |
| Temporary tunnel changed | Configure `OLLAMA_BASE_URL` in the API dashboard, preserve authentication, redeploy and test missing/wrong/correct auth plus inference. |
| Source/routing outage | Wait for bounded cooldown, retry once after recovery; do not guess facts or times. Unsupported areas may continue to refuse. |
| Rate limit/busy | Respect `Retry-After`; do not loop or expand concurrency. Two API compiles and one local model chat are admitted at once. |
| Bad deployment | Restore a known green deploy, verify SHA/readiness, then run a supported LIVE compile and clean-browser proof/GO. |

The API admits six compiles/minute per hashed socket peer, caps peer buckets at 2,048 and returns 429 on saturation. Reverse-proxy peer grouping can affect this limit; it is an abuse bound, not user authentication or a distributed quota. No forwarded client header is trusted to bypass it. Provider/model waits and request sizes are bounded; readiness is cached for 60 seconds.

Before rollback save the current deploy ID and SHA. Render API `POST /v1/services/{serviceId}/rollback` accepts `{ "deployId": "<known-green-deploy>" }`. It reuses a previous artifact and does not disable autodeploy. To restore forward, use `POST /v1/services/{serviceId}/deploys` with `{ "commitId": "<green-SHA>" }`, or rollback to that recorded deploy. Check both API and static service. Never assume env/config changes are rolled back with source artifacts.

Official references: [rollback API](https://api-docs.render.com/reference/rollback-deploy), [Render rollback behavior](https://render.com/docs/rollbacks), [deployment/restart behavior](https://render.com/docs/deploys). Actual drills and resulting SHAs belong in `evals/reports/FINAL_PRODUCTION_SMOKE.md`; a recipe alone is not a passed drill.

Cash spending remains $0. Do not enable automatic top-up, billable overages, training, new hosting or trials. Backboard chat is blocked by free-credit restrictions. Revoke/rotate exposed credentials through dashboards without putting replacements in chat or Git.
