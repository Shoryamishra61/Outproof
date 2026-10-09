# Conditional release handoff

Latest Potheri incident: [executed repair report](release-potheri-incident.md). General discovery failed from Render despite Singapore-only readiness passing. Discovery recovered after replacing the unreachable endpoint; a real Potheri browser run found three identities but **no accepted outing**, because admission/hours evidence was insufficient. Current controlled checks: 4,903 Python and 135 browser cases. A separately future-dated supported Singapore API plan passed with real Gemma. Global and Potheri outing coverage remain BLOCKED; thousands of synthetic checks do not establish real-world acceptance.

Latest starting-location repair: October 10, 2026 IST. [Executed report](release-location-picker.md) supersedes the older coordinate-entry UI and test counts below: 4,900 Python tests, 134 controlled browser cases, three real public origin searches, real map imagery, and restored protected Gemma connection. Current closed-time refusal and an explicitly future-dated API plan are reported separately; this is not a current accepted outing or physical field trial.

Checkpoint: **October 9, 2026, 08:03 IST**. Target freeze remains October 10, 2026, 09:00 IST. Engineering for the evidenced supported loop is deployed; worldwide acceptance, permanent inference hosting and physical trials are not established.

Product build: `c99a1f55f793c15941c3fd047393c9bb40ed12b7`, branch `master`. [CI 37874581558](https://github.com/Shoryamishra61/Outproof/actions/runs/37874581558) completed successfully. API deploy `dep-db452j942hec73c6ejlg` and web deploy `dep-db452jh42hec73c6ejug` were both observed live at that SHA. Both report `autoDeploy=yes` and `autoDeployTrigger=checksPass`. Subsequent evidence-only commits receive their own CI/deployment identity check; the local final receipt is `.tools/final-release-checkpoint.json`.

Verified links: [application](https://outproof-web.onrender.com), [production API readiness](https://outproof-api.onrender.com/v1/health/ready), [public demo](https://outproof-web.onrender.com/demo.html), [repository](https://github.com/Shoryamishra61/Outproof).

| Capability | Status | Actual evidence / boundary |
|---|---|---|
| HTTPS frontend / real production API | PASS | Fresh browser, production version, LIVE enabled and fixtures disabled |
| Frontend → API → Gemma | PASS | Real optional text parser and valid-plan ranker; request `c96d90e495904fc6a5ac41ab6a215324` |
| Local hardware/model | PASS in executed run | RTX 3050 Laptop, 4096 MiB VRAM; `gemma4:e2b-it-qat`, GPU plus RAM, context 4096; Ollama 0.35.1 |
| Stable always-on inference | BLOCKED | No existing Cloudflare domain or always-on machine; no paid hosting authorized. Protected temporary connection works while this laptop stays online |
| Live facts and walking | PASS within supported corridor | NParks admission/hours, OSM Tanglin gate, independently fetched outbound/return Valhalla routes; only Singapore main gardens |
| Exactly one plan / hard constraints | PASS in tested population | One stop, eleven PASS gates, verified SGD 0 main-ground total, no fixture sources |
| Unsupported/global acceptance | BLOCKED by evidence | Real 50-case/19-city campaign accepted zero; 40 safe refusals, ten provider failures. No worldwide operational claim |
| Secrets / CORS / bounded abuse | PASS in bounded checks | Exact-value/history/bundle/log and trace scans; 401/401/200 missing/wrong/correct model auth; schema/body/admission bounds; no blanket security guarantee |
| CI / rollback / recovery | PASS | Green CI; actual previous artifact rollback and browser afterward; proxy outage/restart; rollback disabled autodeploy and it was restored/verified |
| Mobile / desktop / keyboard | PASS in tested paths | 124 controlled Chromium cases, real public proof/GO and 390px path; no human screen-reader trial |
| Observability | PASS | Actual HTTP parent with linked grounding and Gemma child spans; technical-only metadata retained |
| Partners | LIMITED, evidence-based | Seven demonstrated uses; nine blocked/excluded. Full sixteen-category ledger in `docs/PARTNER_ELIGIBILITY.md`; judges decide eligibility |
| Demo | PASS | Actual 65.08s screen recording; fresh HTTPS decode/playback/hash/range/voice checks, four widths and keyboard focus; silent screen video, separate opt-in voice cue |
| Physical trials / Screen Ratio | UNEXECUTED / UNMEASURED | Zero of three India outings. Software, GPS mocks and screen recordings do not replace these |
| DEV documentation | PREPARED | `docs/DEV_DRAFT.md` follows the official template; publication/submission reserved to the user |

The latest public parser-plus-ranker journey took **5.930s to plan / 6.328s to GO**, with readiness 200 and no JavaScript exceptions (`artifacts/release/public-readiness-corrected`). A separate post-idle run took 22.162s to plan; initial cold local smoke took about 115s. These samples do not establish a general sub-30s guarantee. Earlier failed runs remain retained.

## Executed campaign and commands

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1`: **4,881 passed, two opt-in external skips**, Ruff, 17 schemas, 60 structural cases, 85 policy cases and TypeScript/Vite green. Local log `.tools/release-canonical-10.log`; independent CI also green.
- `uv run pytest tests/release/test_runtime.py -q`: ten passed, including both working/unavailable concurrent-readiness cases. Those two cases failed before the shared-lock correction. No validator was weakened.
- `npx --prefix apps/web playwright test --config apps/web/playwright.config.ts`: **124 passed**, zero skipped/unexpected/flaky, 68.61s in the last local run. An earlier stale-server run had two passed/122 infrastructure failures; retained in `artifacts/release/browser-infra-failure`. Dedicated server startup fixed the harness failure.
- The canonical population includes **4,096 unique controlled journeys**, 26 accepted/4,070 rejected, full measured pairwise coverage; 300 adversarial cases; 300 passing property examples; four critical-gate mutants detected. `FINAL_USER_FLOW_COVERAGE.json` retains input/oracle hashes. These are synthetic, not physical or worldwide successful outings.
- Twenty bounded real HTTPS probes and three supported public compiles passed (`release-production-probes.json`). Actual global outcomes remain separate in `FINAL_GLOBAL_EVAL.json`.
- `$env:PUBLIC_RUN_LABEL='readiness-corrected'; $env:DEMO_RECORDING='false'; node scripts/record_public_demo.mjs`: real optional text parsing, ranking, eleven checks, one plan, proof, GO, map, voice playback and mobile checks passed on the product SHA above.
- `$env:ASSET_BASE='https://outproof-web.onrender.com'; node scripts/verify_public_demo.mjs`: actual video/voice playback, four widths, focus, HTTP 200/206, exact 3,343,359-byte SHA256 match; `release-demo-public.json`.
- `uv run python scripts/scan_secrets.py`; `$env:PYTHONPATH='.;services/api'; uv run python .tools/release_secret_audit.py`: prefix and exact private-value scans, with current local results in `.tools/final-secret-audit.json`. Trace text is separately scanned; no secret values are printed.
- `uv run python .tools/final_release_checkpoint.py`: asserts current green CI, both matching live deploys, API free instance/static shared-build configuration, restored CI gate, HTTPS readiness, authentication denial/success and demo hash. The ignored runner reads existing private credentials.

## Remaining access and author actions

No additional key or paid approval is needed for the supported release. Stable inference would require an existing domain plus a stable authenticated route and an always-on machine, or separately authorized hosting; neither is currently available. Global success requires authoritative venue-specific mandatory cost, hours, constraints and routing evidence. Backboard chat requires paid-eligible credits beyond the available Memory/RAG-only balance. DigitalOcean/training and physical UNO Q remain excluded; no purchases or subscriptions were enabled. **New cash spend: $0.**

Keep the inference laptop plugged in, awake, lid open and online for live judging. The proxy's system-awake request does not prevent manual sleep, lid shutdown or network loss. Runtime recovery, privacy and observed rollback/autodeploy behavior are in `docs/OPERATIONS.md`; local model inspection and adapters are in `docs/DEPLOYMENT.md`.

The author must review `docs/DEV_DRAFT.md`, keep these limitations and only supported partner claims, confirm fresh public availability, then publish the single DEV entry. No publication or submission was performed. Do not describe this checkpoint as three real outings, worldwide operation or unconditional 24/7 readiness.
