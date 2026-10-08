# GROUND RULE — OVERNIGHT SHIP-READY RELEASE COMMAND

**Deadline target:** October 10, 2026 (IST), leaving a separate buffer before the official contest deadline.
**Role:** Principal engineer + SRE + QA lead + security auditor + AI evaluation scientist + deployment engineer + contest compliance reviewer.
**Execution contract:** Inspect, implement, execute, verify, repair, retest, deploy, and document. Do not stop after proposing a plan. Do not claim a win, perfect software, real-world usage, or integration eligibility without evidence.

## 0. FIRST RESPONSE: CREDENTIALS AND COST APPROVAL — ASK NOW

Before making external deployments or starting integration work, perform a **five-minute read-only inventory** of the project, `AGENTS.md`, the existing `.env.example`, `render.yaml`, provider SDKs and environment variable *names* (never reveal values), and integration inventory. Then send the user **one consolidated credential/access request**, grouped as:

- **P0 needed to deploy working core:** GitHub repository push/access, Render access/linked repository, reachable live Gemma 4 E2B inference endpoint or approved runtime/hosting account, routing/map provider configuration, official venue evidence providers, and domain if applicable.
- **P1 useful prize integrations:** Sentry DSN/auth, SerpApi key, ElevenLabs key, access to GitHub Copilot and Entire/agent-session tools, and DigitalOcean account/GPU budget only if the user approves a secondary runtime.
- **Optional gated categories:** Backboard credentials; MongoDB Atlas; Temporal Cloud or self-host permission; Mastra (normally library, no key by itself); Prior Labs/TabPFN model entitlement/data; Thinking Machines Tinker key and explicit training spend cap; Tiger Data DB credentials; whether a real Arduino UNO Q physically exists.
- **Budgets:** ask permission for each resource with expected monetary charges; assume **no paid spend** until explicitly approved. Mention promo credits at https://hacktoberfest.com/my/promos but do not assume their existence or value.

Ask for *capability and access*, not for plaintext secrets in chat. Tell the user to configure secrets locally in ignored `.env` files, a securely connected CI secret store, and Render/environment dashboards. Never output, commit, or expose tokens, service-account JSON, full connection strings, or passwords.

After sending the one message, **continue autonomously on all tasks not dependent on missing credentials**. Do not suspend the whole project waiting on optional services. If approval/authorization is needed, stop only the affected external action, retain a clear blocker, and proceed elsewhere.

## 1. SOURCE OF TRUTH AND HONESTY

Read the repository's actual instructions, established specifications, tests, schemas, decision logs, source provenance, current commit history, and previous reports. Existing passing checks reported: Ruff; 427 pytest pass/2 skip; 17 schemas; 60 structural cases; 85 policy cases; strict TypeScript; Vite; one live validated Anna Nagar Tower Park plan; 50 global evaluation cases (2 accepted, 48 typed failures); existing `render.yaml`; browser walkthrough. **These are prior reported results, not evidence that current HEAD or deployment still works.** Reproduce them.

Core invariant: **LLMs interpret. Data grounds. Code verifies.** The model only interprets intent/ranks already-valid plans. Deterministic code verifies ground truth, walking duration both ways, hours including dwell, cost guarantees, dietary constraints, exclusions, and return deadline. No unsafe fallbacks or fixture results dressed up as live results. Do not weaken a hard gate simply to obtain a demo.

Contest rules: https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules and challenge https://dev.to/challenges/hacktoberfest-week1-2026-10-05/ . This challenge requires a **new project AND new repository built/completed inside the Oct 5–11 entry period**. If repo history conflicts, report it immediately; do not rewrite history to disguise dates. One entry per person/team, one prize per challenge; qualify only where a partner integration is real and meaningful. Writing quality is weighted most heavily. User wants the application finished first, with only final write-up review/publication left.

## 2. EXECUTION PLAN AND PRIORITY FREEZE

Sequence:
1. P0 audit correctness, reproducibility, rule compliance, actual system status.
2. P0 rectify source-provenance error(s), domain policy, model routing, and release-blocking bugs.
3. P0 production deployment through real public path; backend + frontend + model connectivity; verify with real requests and headless browser.
4. P0 security and deterministic policy release suite.
5. P1 thousands of generated contract/user-journey cases; actual browser E2E and accessibility; load/chaos tests.
6. P1 valuable partner integrations behind fully independent adapters, with live verification and evidence.
7. P1 final README, docker/deployment guide, walkthrough recording, screenshots, final DEV article **draft only**. Do not publish post without user approval.
8. P2 optional services and cosmetic polish ONLY if core release remains green.

Commit small, descriptive, reversible changes. Do not alter canonical design or core architecture without justification. Do not rewrite the entire app. Preserve all relevant tests and CI; do not mark broken tests skipped or weaken expected assertions.

Set a release cut-off: once primary public end-to-end path is green, avoid risky new integrations close to the user deadline. Quantify time remaining and stop adding features if an outstanding P0 threatens release.

## 3. PRODUCT CONTRACT AND USER FLOW

Ground Rule reduces screen time by choosing exactly ONE credible outing rather than offering an endless recommendation feed.

Primary success path:
`OPEN -> INTENT -> LOCATION / PERMISSION -> BUDGET & CLOCK -> CONSTRAINTS -> COMPILE -> SOURCE + POLICY PROOF -> EXACTLY ONE PLAN -> GO -> PHONE DOWN`.

Real requirements, where specified in canonical repository contract:
- Current location explicit entry and permission-based geolocation, with informative denied/missing/fallback states.
- Solo/friend/date intent; free civic walk and paid eatery where evidence permits.
- Budgets including zero, per-person and total, taxes and mandatory service fees, correct currency minor units.
- Available time, arrival, dwell, walking legs, departure, deadline and timezone.
- Walking max distance; no car/airline distance substituted for pedestrian routing.
- Opening hours covering entire visit and return feasibility.
- Dietary/allergen, crowd/quiet, accessibility and explicit excluded venues if defined by product spec.
- Exactly ONE plan on success, route proof and provenance ledger, GO state with minimal controls and optional speech.
- Strict, comprehensible typed failure otherwise, with only evidence-backed alternatives.

Never display a universal coverage promise unless supported. First-time experience must make supported city/example and demo mode truthfully clear.

Front-end audit: loading indicator; stale response protection; cancel/retry; network offline; route errors; keyboard; screen reader; 320px to 4K layouts; no clipped/overlapping text; focus trap only for real modals; min touch targets; reduced motion; high-contrast readability; no artificial urgency, infinite exploration, unrelated chat features, or noisy popups. Keep the screen the shortest portion of the experience.

## 4. FIRST CRITICAL FACT CHECK: ANNA NAGAR

Official civic list https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf, first page, row for Dr.Visweswaraya Tower Park: area **57,927 m² (~14.3 acres), not >100 acres**. Fix every database record, display string, test, README, screenshot caption, and write-up referencing the incorrect figure. Run a source-to-claim audit rather than merely editing strings.

Recheck whether the municipal department's GENERAL parks hours (reported 05:00–21:00) actually establish specific park hours at proposed date and any holidays. Prove gate location and route endpoints; verify OSM identity `osm:way/24240071`; independently verify INR 0 *mandatory admission* and distinguish potential fee-bearing tower access. A parks list is not proof of zero fee. If official evidence is not sufficient under canonical price confidence contract, downgrade/withdraw success proof rather than fabricating evidence. Retest live acceptance.

Route example previously reported: outbound 1,283m/911s; return 1,285m/939s; 1,800s dwell, total 3,650s. Recalculate with real live Valhalla calls at verified gate/coordinates. Do not recycle historical values as fresh values. Preserve source URL, checked timestamp, claim text, authority, confidence, parse lineage and expiry in each provenance record.

## 5. TRUST, DATA, AND COMPILER PIPELINE

Trace every stage: schema input -> intent extraction -> normalized constraints -> discovery -> deduplication -> evidence extraction -> confidence -> route -> time budget -> exclusion and dietary gates -> candidate scoring -> open-weight model ranking -> deterministic final revalidation -> single-plan output -> GO. Audit asynchronous paths, caching, stale data, timezones, unit math, contradictory sources, bounded provider calls, malformed model response and invariant preservation under all errors.

Always distinguish `VERIFIED`/`ESTIMATED`/`UNKNOWN` using the existing schema. Never show unknown/estimated as payable guarantee. For paid food, menu sticker price does NOT equal all-in price without taxes/mandatory charges when applicable. Reddit and reviews are discovery hints only, not sufficient official transactional price evidence. Venue data may be sparse: safe typed rejection is correct, but honestly characterize coverage and usability.

Prevent SSRF in source fetchers (DNS and private IP ranges and redirects), XSS/sanitization attacks, open redirects, malicious place names, prompt injection in web content, poisoned provenance, hardcoded keys, unbounded requests, and injection across logs. User location is sensitive: avoid storing precision GPS by default; redact coordinates and identifiers from Sentry by default; define retention where applicable.

## 6. WORKING PRODUCTION, NOT A YAML FILE

Inspect `render.yaml` against current https://render.com/docs/blueprint-spec . Recommended minimal stack if existing implementation supports it:
- Render static site built from Vite `dist` with explicit SPA deep-link routing and correct API origin.
- Render Python/FastAPI web API (actual commands, lock files, Python runtime and port binding from repository) with `/health/live`, `/health/ready`, `/version`, non-secret `/capabilities` and `/compile` (adjust routes to real code contract).
- Accessible Gemma inference runtime deployed with sufficient resources, reachable through a controlled URL from Render. Can be a permitted, billed remote inference instance (e.g. DigitalOcean) or real Render-capable model service. Never use `localhost:11434` in remote production unless Ollama actually runs in that same service/network context.
- Route engine and evidence providers with bounded timeouts, TLS and correct CORS.
- Optional data/observability stores only when real and necessary.

Validate explicit production mode without fixtures. If production compilation flag currently disables the entire app, make the trusted live compiler work where verifiable, not by turning on fixtures or removing checks. A prerecorded accepted plan may be shown only as an unmistakably **recorded/replay demo**, with distinct UI and with real model-inference evidence demonstrated elsewhere. Never call it a live compile.

Check deployment: repo push, blueprint parsing, build/install, health and readiness, CORS, DNS, TLS HTTPS, caching, static rewrites, environment interpolation behavior (Render Blueprints do not interpolate arbitrary `${VAR}` values), branch settings, correct asset path, `/api` URL, cross-origin preflight, exact API methods, service cold start, multi-region latency, concurrency, storage lifecycle, logging, metrics, secrets, rate limits, readiness tied to critical dependencies, crash recovery, rollback, auto-deploy policy, minimum resources, and budget alerts.

Require staging test and then production smoke. Set separate `/health/live` and `/health/ready` semantics: liveness can pass when app process runs; readiness should truthfully state whether critical compile services are available. Never return healthy for a completely unusable backend if the check is used as deployment readiness. Do not expose keys, precise user coordinates, provider internals, or full prompt contents to public health endpoints.

Run **from a clean browser** against **actual deployed public URLs** (not localhost): home -> valid input -> real compilation -> policy-proven one plan -> GO. Reverify after restart/new build. Capture screenshot and trace with timestamp, commit SHA, environment, evidence IDs and response ID. If external auth/payment/user approval is missing, stop the affected deployment and record exact instructions, never invent a live URL or claim completion.

## 7. FIRST ASK FOR THIRD-PARTY APIS; THEN BUILD PARTNER ADAPTERS

16 partner categories: Render, Prior Labs/TabPFN, Thinking Machines/Tinker, Qualcomm Arduino UNO Q, DigitalOcean, Gemma, Backboard, ElevenLabs, Entire, GitHub Copilot, Mastra, MongoDB Atlas, Sentry Agent Tracing, SerpApi, Temporal, Tiger Data.

A partner is **qualified** only if a genuine meaningful integration is implemented, executed, verified, and documented. Installing a package or showing a logo is NOT sufficient. One submission can opt into multiple qualifying categories, but can win only one prize.

Design a capability registry and partner adapters behind environment flags: `configured`, `reachable`, `working`, `used_in_real_feature`, `evidence_available`. Make P0 core independent of optional adapters; no startup crash because optional key missing. Exact SDK config must follow current provider docs discovered during implementation; never invent endpoints.

Partner-specific proof contracts:

1. **Render (P0):** publicly operational Ground Rule web and API, deployment and runtime logs, real inference connectivity. No mere `render.yaml` claim.
2. **Gemma (P0):** verified model identity/version and real open-weight inference on user intent/ranking, compare model-dependent output to deterministic verification, record latency and meaningful contribution.
3. **Sentry (P1):** real model+tool tracing spans with private data scrubbed, deploy environment, one diagnosed failure and one successful trace; no raw exact GPS or credentials.
4. **SerpApi (P1):** live search used in candidate/source discovery with source attribution; pass results through authoritative evidence verifier; demonstrate freshness and relevance plus injection handling.
5. **ElevenLabs (P1):** spoken GO instruction or narration that reduces screen-on time, with actual API playback or generated audio artifact, opt-in/privacy, error fallback; if only narration is used, say so.
6. **GitHub Copilot (P1):** actual Copilot agent/CLI/review work and GitHub Actions with identifiable execution evidence, not claiming Copilot use without it.
7. **Entire (P1):** real recorded development-agent sessions and searchable session provenance; attach relevant link/artifact, respect privacy.
8. **DigitalOcean (P1 only if approved):** actual live hosted model/backend with measured performance and cost; no unused droplet; account access, credit, spend cap required.
9. **Backboard (P2):** actual R-CLI usage or consistent multi-model eval via Backboard; measured test cases and meaningful comparison; key required if API route.
10. **Temporal (P2):** genuine durable workflow (provider fan-out/retries/checkpoint) with proof of restart/retry recovery, if long-running flows warrant it.
11. **MongoDB Atlas (P2):** production source provenance/candidate storage, indexing, retention and audit, explicit real reads/writes, not duplicate unused SQL database.
12. **Mastra (P2):** meaningful TypeScript agent/tool orchestration with clean Python compiler contract; do not refactor core into Mastra just for a prize.
13. **Prior Labs TabPFN (conditional):** valid historical CSV/tabular data, meaningful prediction (such as evidence/source availability or candidate retrieval priority, never guaranteed pricing), leakage-safe train/test split, baseline and held-out metrics. If dataset unavailable or model unsuitable, not eligible.
14. **Thinking Machines Tinker (conditional):** real supported-model fine-tuning of bounded intent-structuring/classification task, baseline vs tuned holdout, latency/cost, actual training receipts/metrics. Never falsely call arbitrary Gemma prompting a Tinker fine-tune. User must approve spend.
15. **Tiger Data (conditional):** real pgvector/hybrid retrieval over candidate/evidence corpus, measurable retrieval relevance; migration and tests. Avoid adding a second unnecessary persistence layer.
16. **Arduino UNO Q (conditional HARDWARE):** physical UNO Q connected, model or sensor performs real interaction, with authentic recorded on-board results. If absent, mark INELIGIBLE; simulator cannot prove hardware usage.

Freeze and skip integrations that jeopardize core release. Create `docs/PARTNER_ELIGIBILITY.md` with one row per category: intended feature, exact code path, API/service proof, measured live result, category claimed Y/N and reason. **Do not list a category in submission unless eligible.**

## 8. MASSIVE TEST CAMPAIGN — THOUSANDS OF MEANINGFUL JOURNEYS

Create `tests/release/` preserving existing structure. Use pytest + Hypothesis/property-based/stateful tests for domain invariants, generated pairwise coverage for user-journey state space, Playwright for browser, route/provider contract tests, load/chaos with bounded limits. The user requested **thousands**; minimum target **4,096 distinct, meaningful, assertion-bearing offline/controlled user-journey cases**, **300 boundary/adversarial cases**, **100 browser E2E journeys on test/staging**, and **20 live production smoke journeys or the maximum safe small sample of source-real scenarios**. All counts must be separately reported, with no padding by identical fixtures. If resources or rate limits make a target infeasible, report actual executed number and remaining, not invented pass counts. Do not hammer production/public map APIs with thousands of requests.

Model realistic input dimensions: current-location permission states, 19-city geography plus impossible coordinates, personas, budget tiers and currency, group size, free vs paid, travel/walking limits, quiet/crowd preferences, diet and allergy restrictions, daytime vs closed vs after-midnight, deadlines, live price confidence, provider health, stale source, and concurrent submissions. Use pairwise/multi-way generation to avoid combinatorial explosion. Persist deterministic seeds and case IDs for replay.

**Contract-level state machines:**
- All accepted outputs must have 11/11 (or current canonical count) hard gates passed and complete matching source ledger.
- Never accept UNKNOWN or ESTIMATED guarantee.
- A closed venue never appears as open; dwell and return must fit.
- Walking outputs must correspond to pedestrian routes and real direction-specific data.
- Exactly one accepted plan; zero or one on failure, never many.
- No mall/excluded category if hard-excluded.
- Allergy/diet constraints never dropped.
- Failure typed, human-readable, retryable only where appropriate.
- User data does not leak across concurrent requests.
- Stale responses cannot overwrite a newer user request.

**Browser E2E flows** (real Firefox/Chromium/WebKit if installed/available): initial render; fresh user; geolocation allow/deny/error; typed location; keyboard-only path; budget validation; free civic; paid candidate; combo diet+quiet+deadline; zero candidates; temporary outage; recovery; one plan; proof expansion; source links; GO instruction sequence; next/back; mobile 320/375/390/768/1024/1440 widths; zoom/reduced motion; refresh; back; idle timeout; offline; low bandwidth; double click; rapid edits; canceled requests; clipboard/map links; narration toggle; basic screen reader semantics. Catch console errors, failed requests, broken images, missing aria names, focus loss, horizontal overflow, unhandled promise rejections and dead buttons. Snapshot accessible semantic DOM and screenshots where applicable.

**Geo/time/cost:** pedestrian-only, both directions, gate-coordinate validity, units, total duration including dwell, time budget strict inequality, midnight/daylight saving, cross-timezone city tests, missing opening hours, weekly exceptions, holidays, required fees, taxes/tips/service charges where mandatory, varying group cost, precision/rounding, impossible currency conversion and zero budget.

**Fault/security:** provider 401/403/404/429/500/502/503/504, hung/slow providers, DNS/SSL errors, partial payload, invalid schema, malformed Gemma JSON, empty/overlong response, tool injection, shell/SQL/HTML injection, public-provider redirects/SSRF, stale cache, missing key, expired tokens, oversized input, tight resource limits, model eviction, service restart, Redis/DB drop if used, concurrency spike, retry storms, graceful shutdown, network disconnect, mobile browser suspend.

**Evidence red team:** verify each real candidate claim has source support, detect unsupported area/hours/free-cost assertions, contradictory sources, hallucinated citation URLs, transient page content, venue identity collisions, stale prices, unofficial reviews being promoted to definitive evidence, OSM geometry mismatch, costs that are per person but rendered as group price.

**Performance:** warm-load UI, mobile bundle size, source fetch latency, model latency, route timeout, complete compile p50/p95/p99, time from intent completion to GO, concurrent 1/5/10/25 virtual users under controlled load, memory/CPU, cold-start recovery, Sentry spans. Establish evidence-backed SLO (target <=30 seconds for the warm supported GO-ready flow if achievable). Report failure rate and cold start separately. Do NOT claim physical Time to Grass or screen ratio.

**Quality of test suite:** coverage per feature not just total; mutation tests on critical functions if feasible; reproduce at least three known failure patterns; verify assertions fail if trusted validator is intentionally broken in isolated mutation run; rerun canonical checks after fixes. CI must publish reports, trace, screenshots, seeds, coverage and release decision. No CI green by skipping all real checks.

## 9. CURRENT GLOBAL BENCHMARK

Rerun `evals/cases/global_scenarios.jsonl` (50 cases / 19 cities) against actual applicable sources. Keep accepted verified plans separate from typed failures, errors and timeouts. Historical 2/50 accepted is low verified coverage despite zero known hard-policy violations; avoid saying globally operational. If live verified coverage remains sparse, keep user-visible supported-region disclosure and honest no-plan fallback. Prioritize a small number of actually useful, live, geographically diverse cases, with fully supported facts, rather than weakly evidenced breadth.

For each global scenario: result status, provider error category, candidate identity, locale, gate breakdown, confidence, full provenance, duration, model identifier, retry info, latency and reproducible trace. Never conflate 48 safe failures with 48 successful plans.

## 10. PROD CI/CD, DEPENDENCIES AND OPERATIONS

Establish deterministic lockfiles and pinned critical runtimes, staged migrations, `.env.example` names without values, secret scanner, dependency vulnerability check, package license check, linter/formatter/typechecks, backend unit/integration tests, frontend unit tests, generated property tests, browser E2E, service contract checks, proper exit codes and branch protection where permitted. Use least-privilege CI tokens and non-production secrets in pull requests. Prevent untrusted PR jobs reading production credentials.

Integrate CI with Render deployment only upon mandatory green gates; expose commit SHA/build version and use smoke checks post-deploy. On failure: revert or rollback to last verified build, document root cause. Have an explicit `docs/OPERATIONS.md` with startup, backend runtime, model availability, source provider outages, manual restart, rollback, budget, rate limits, Sentry dashboard pointers and emergency fixture-switch prohibition.

Observe legal and provider usage limits: OpenStreetMap attribution/Overpass fair-use, Valhalla public provider terms, website crawl rate limits/robots, partner model licenses, geocoding, privacy and GDPR/region constraints if applicable. Do not exfiltrate user location or credentials to external AI inference beyond disclosed expected data.

## 11. SCREEN RECORDING, PROJECT PRESENTATION AND WRITEUP DRAFT

Prepare working screenshots and a **60–90 second evidence-based video**, optimized for judging; a short 45–60 second cut is optional. Show public URL, setting a practical budget/time, compiling one actual verified live plan, expanding full proof, real Gemma and source ledger, switching to GO and screen-down guidance, and a brief observability/debugging proof if partner eligible. If using a prerecorded live example, label it; never edit footage to impersonate real inference. Use no fictional outings or fabricated field receipts.

Write a polished DEV article draft with correct sections, code URL, demo URL, source references, diagrams, how open AI changes project capabilities, architectural tradeoffs, what failed, test metrics, real limitations, and supported partner prize categories. **Do not publish on behalf of user without explicit authorization.** Contest judges value writing quality most heavily.

Avoid unsubstantiated 'world's best', '100% perfect', and 'winner guaranteed'. Make every statistic traceable to a committed report. New project/repo dates, licensing, crediting and challenge tags must be verified.

## 12. RELEASE DELIVERABLES AND EXACT FINAL REPORT

Create in repository, using existing canonical locations where appropriate:
- `docs/RELEASE_READINESS.md` – requirements-to-code-to-test traceability and verdict.
- `docs/DEPLOYMENT.md` – exact deployment and verification instructions.
- `docs/OPERATIONS.md` – runbook / fallback / rollback.
- `docs/PARTNER_ELIGIBILITY.md` – all 16 partner gates and proof.
- `docs/USER_JOURNEYS.md` – reproducible primary and failure pathways.
- `docs/DEV_DRAFT.md` – complete final draft, not published.
- `evals/reports/evidence_audit.md` – claims and verified sources including Anna Nagar correction.
- `evals/reports/global_eval_final.json` / `.md` – accepted vs rejected, not conflated.
- `evals/reports/production_smoke.md` – actual public URL, request IDs, screenshots, SHA.
- `evals/reports/user_flow_coverage.json` – unique case count, parameter dimensions, pass/fail/skip, seeds, coverage.
- `evals/reports/security_fault_audit.md` – threat and failure testing.
- `evals/reports/release_verdict.md` – final objective checklist with unsupported features.

Create an `artifacts/release/` directory for browser trace ZIPs, screenshots, video output and sanitized metrics. Do not commit large binaries unnecessarily; ensure durable artifact links.

Final response to user MUST contain:
1. **Git SHA/branch and exact changed files.**
2. **Public web URL, API endpoint, model version, and runtime; only if actually verified.**
3. **Canonical check result, distinct generated user-flow count, actual browser E2E count, production smoke count, and reason for skips.**
4. **Real accepted / typed rejected benchmark counts, complete policy violation count, provenance inconsistencies.**
5. **What bugs were fixed, with regression IDs.**
6. **All 16 partner categories: QUALIFIED / NOT QUALIFIED / BLOCKED and evidence.**
7. **Any secrets/services/paid approvals that still require user action; never output secret contents.**
8. **What remains for final DEV submission; only document review/publication is acceptable as a desired target, not an assumed state.**
9. **One exact verdict:** `RELEASE READY — VERIFIED`, `CONDITIONAL RELEASE — DISCLOSED LIMITATIONS`, or `BLOCKED — CRITICAL REQUIREMENTS UNMET`.

Absolute exit conditions for `RELEASE READY — VERIFIED`:
- Verified public deployment with successfully running true supported user flow.
- Live/ready health truthful, stable across reboot and repeat test.
- Core model actually performs a meaningful step and deterministic safety is intact.
- Zero unresolved critical/high severity defects and no uncovered known safety/provenance mismatch.
- Local build/CI green and critical regression suite green.
- At least one genuinely supported live outing (or more), defensible evidence, real pedestrian route and GO.
- Functional responsive UI/accessibility smoke.
- Contest repo/demo/licensing/reproducibility requirements met.
- Article draft, screenshots and demo ready.
- No fabricated partner eligibility/physical usage.

If any cannot be achieved, report a truthful conditional or blocked release with exact steps and evidence. This is preferable to presenting an unusable app as finished.

**Start by checking repository files and immediately send the consolidated API/credentials/spend approval question. Then execute every unblocked step. Do not stop at a plan.**
