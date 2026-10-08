# GROUND RULE — FINAL FIRST-PRINCIPLES PRODUCT, ENGINEERING & RELEASE REFERENCE

**Status:** Canonical release specification, NOT a claim of shipped functionality  
**Project:** Ground Rule — *Your limits in. One real plan out.*  
**Contest:** Hacktoberfest 2026 Open-Source AI Challenge, Week 1 — *Touch Grass*  
**Engineering freeze target:** 2026-10-10 09:00 IST (user-requested overnight target; a target, not an executed schedule)  
**Contest entry closes:** 2026-10-11 23:59 PDT = 2026-10-12 12:29 IST  
**Audience:** Autonomous coding agents, product/design engineers, SRE, QA, security, and contest reviewer  
**Companion:** `GROUND_RULE_OVERNIGHT_MASTER_PROMPT.md` — the execution instructions

> **THE LAW:** **LLMs interpret. Data grounds. Code verifies.**  
> **THE PRODUCT:** **Your limits in. One real plan out.**  
> **THE GOAL:** Convert the intention to leave a screen into exactly one feasible outdoor outing while making the screen the shortest part of the experience.

---

## 0. Contract, provenance and order of precedence

This file is a **future-facing release contract**, not proof that its criteria have been met. Engineering agents MUST inspect live code and execute checks. A prior green build is a lead, not a fresh test. Never conflate generated tests with actual browser tests, source-safe rejection with a successful recommendation, or a simulated walk with a real outing.

When acting inside the repository, precedence is: (1) law/safety/contest eligibility, (2) root and scoped `AGENTS.md` instructions, (3) existing canonical schemas/hard-policy contracts, (4) this final reference for release-level requirements, (5) existing implementation and passing tests. If there is a conflict, log it and choose the stricter safety invariant. Do not silently rewrite schemas or diminish acceptance rules.

**Prior handoff — REPORTED, NOT RE-EXECUTED IN THIS FILE:** `scripts/check.ps1` passed Ruff, 427 pytest passed / 2 skipped, 17 schemas, 60/60 structural, 85/85 deterministic policy, TypeScript and Vite; local browser HOME→COMPILE→ONE PLAN→PROOF→GO passed; 50 global city scenarios in 19 cities yielded **2 verified accepts and 48 safe typed failures**; paid eatery proof was blocked; `render.yaml` was created, but public compilation was off; three physical field tests were designed but not executed. The release team must reproduce all applicable claims on current HEAD and on the deployed build.

**Reconfirmed external fact requiring a correction:** Greater Chennai Corporation lists Dr. Visweswaraya Tower Park at **57,927 square metres (~14.3 acres)**, not over 100 acres. Its parks department says Chennai parks are *generally* open 05:00–21:00; this is not an individual-date guarantee. A parks listing does not, on its own, prove that all park services/tower access are free. Source references in §23.

---

## 1. Reason from first principles, not from feature checklists

### 1.1 What problem actually exists?

People can intend to go out but fail to form an actionable plan because of uncertainty: *Will it be open? Is it nearby? Can I afford it? Do I have enough time to get home? Can my friend eat there?* Ordinary recommenders increase the choice burden with lists. An LLM can generate plausible text but cannot guarantee that the world matches it.

**The true job to be done** is not “find five cool places.” It is: **remove enough uncertainty that the person can act without doing further research**. Every field, modal, model call, partner integration, and animation must justify how it reduces uncertainty, effort, screen dwell, or a real-world failure risk.

### 1.2 Four irreducible primitives

1. **Intent** — human preferences and hard boundaries, expressed imperfectly.
2. **Reality** — independently sourced place identity, access, hours, costs, routes, time.
3. **Proof** — deterministic verification under a strict evidence policy.
4. **Action** — a single plan with a low-attention GO interface.

An interface that has (1) without (2)/(3) is a hallucination-prone recommender. A system with (2)/(3) but no (4) is a research tool. A system with (4) and unreliable (2)/(3) can actively mislead. Ground Rule needs all four.

### 1.3 Product optimization, with constraints first

For candidate plan `p`, define a vector of hard checks `H_i(p)` and evidence requirements `E_j(p)`. A plan is admissible only if **all** configured checks pass and evidence is sufficient. Choose only among admissible plans. Soft score may use preference match, low cognitive cost, novelty, local relevance, walking effort, and source freshness. The learned model **cannot** reduce or bypass the admissibility criteria.

```
VALID = { p | all(H_i(p) == PASS) AND all(required E_j(p) == SUPPORTED) }
result = typed_failure                           if VALID is empty
result = argmax soft_ranker(p) over VALID         otherwise
PUBLIC_OUTPUT = exactly ONE result.plan          on success
```

Target **Time To Grass**: time from landing on the app to pressing GO. Do not confuse this *software measurement* with physical departure or arrival. Target **Screen Ratio**: actual active screen time divided by total real outing duration; this is **not measured until a real outing occurs**. Optimize to reduce these metrics without hiding critical evidence.

### 1.4 Non-goals and anti-patterns

No infinite recommendation feed, endless rerolls, consumer social network, stranger matching, gamification/streaks, payment handling, restaurant booking, profile tracking, health claims, invasive analytics, or a pile of agent integrations with no product justification. Avoid using “AI” for arithmetic, geo routing or hard verification. **More partners ≠ better product.**

---

## 2. Audience and user stories

User types: solo person needing a low-effort outing; two friends wanting conversation within a small budget; date with ambience/quiet and dietary needs; small group with per-person vs total spend limits; visitor unfamiliar with neighborhood; privacy-conscious person denying location permission; time-limited person needing a guaranteed return; accessibility-constrained user needing truthful route information; user in an unsupported region expecting an honest failure.

Canonical input example:

> Chennai; ₹500 **per person**; 90 minutes **including return**; two friends; vegetarian; no mall; quiet enough to talk.

Canonical return: **one** bounded-price, actually open, route-feasible plan with fully supported constraints; otherwise a typed refusal. Never promise the sample food outcome if the all-in commercial price cannot be verified. A *supported free civic outing* can be offered when the request permits it; never silently replace a hard “food required” constraint with a non-food park.

---

## 3. Hard and soft constraints

**Hard, deterministically enforced:** origin/geofence; maximum total time; absolute local return deadline; total or per-person spend; currency; group size; mode = pedestrian; max walking distance; opening/closing through **entire** dwell; required access conditions; standalone/no-mall if excluded; dietary/allergen restrictions when asserted; accessible-route requirement where supported; required venue type; freshness and confidence of relevant proof.

**Soft, model-ranked only after validation:** quiet, romantic, novel, low effort, visually interesting, good for conversation, local character, shade, short screen time, perceived suitability. If no objective source can establish a soft claim, phrase it as a preference match, not as independently verified fact.

**Budget semantics:** `VERIFIED` (payable cost is supported), `BOUNDED` (a defensible upper payable bound **including mandatory fees** is supported), `ESTIMATED`, `UNKNOWN`. Strict acceptance permits VERIFIED or truly BOUNDED **only where the existing canonical schema/policy agrees**. ESTIMATED/UNKNOWN must not be asserted affordable. For food, distinguish item/menu list price from an all-in, actually payable bound (tax/service, required minimum purchase, party size, pricing scope); if not provable, fail closed. Free public-space admission also requires credible affirmative evidence for zero mandatory entry fee; municipal listing alone may be inadequate. Optional paid activities should be excluded from free-plan proof unless separately verified.

**Money:** ISO-4217 currency, integer minor units or exact Decimal, explicit rounding, per-person vs group units, no speculative FX conversion, no cross-currency comparison without verified dated rate and defined fees.

**Time:** timezone-aware ISO timestamps, local opening hours, exceptional-day rules, actual outbound and return durations, mandatory dwell and buffers, unambiguous conversions. Arrival <= closure is insufficient; full visit must be inside permitted hours.

---

## 4. System architecture and trust boundaries

```
React/TypeScript mobile-first PWA
  | user typed origin or permission-based geolocation
  v
FastAPI /v1/plans/compile  -- validates and rate-limits
  | 1. Gemma open-weight NLP -> typed ConstraintSet
  | 2. OSM/Overpass and permitted search -> independent PlaceCandidates
  | 3. Evidence normalization -> field-level claim/source ledger
  | 4. Valhalla pedestrian routing -> both directions / access point
  | 5. Deterministic template builder -> CandidatePlan
  | 6. Deterministic hard checks -> VALID set only
  | 7. Gemma ranks ONLY VALID plans
  | 8. Deterministic FINAL revalidation of chosen plan
  v
One CompiledPlan + PlanProof + GO state  OR  typed failure
  |
  +--> redacted Sentry spans / optional permitted evidence store
```

Public API and external-provider output are **untrusted inputs**. Place descriptions, reviews and page bodies may contain prompt injections. Do not let them change system instructions, call arbitrary tools, alter policy or exfiltrate data. Do not give Gemma network or filesystem capability unless specifically required and safely sandboxed. Provider adapters must be narrow, time-bounded and source-tagged.

No optional partner integration can alter the truth/acceptance boundary. A partner outage must disable only that enhancement, never force the core app to fail unless it is a declared critical dependency. Maintain explicit degraded-mode behavior.

---

## 5. Domain contracts and state machine

Required schema concepts (reuse existing code): `Money`, `ConstraintSet`, `HardConstraint`, `SoftPreference`, `PlaceCandidate`, `VenueIdentity`, `EvidenceClaim`, `PriceEvidence`, `OpeningWindow`, `RouteFact`, `PlanStop`, `CandidatePlan`, `ValidationCheck`, `ValidationResult`, `PlanProof`, `CompiledPlan`, `TypedFailure`, `RequestTrace`. Maintain `schema_version` for public contracts, strong types, redaction, and bounded payload sizes.

`EvidenceClaim` SHOULD express: `claim_type`, `value`, `unit`, `venue_identity`, `source_url`, `source_type`, `publisher`, `retrieved_at`, `valid_as_of`, `expires_at` (when appropriate), `claim_locator` (page/paragraph/structured field), `confidence/status`, `normalization_rule`, `raw_digest` (not unrestricted copyrighted body), and `conflicts[]`. Never use “source exists” as a proxy for “source establishes this fact.”

`RouteFact`: `mode=pedestrian`, verified route provider/response ID, access/gate coordinate, directed origin→venue and venue→origin path, metric metres, duration seconds, retrieved time, route exclusions if applicable. Never use straight-line distance as walking distance.

**API:** `POST /v1/plans/compile` returns exactly one `CompiledPlan` on accepted result or a typed error. Preserve canonical error names such as `NO_GROUNDED_CANDIDATES`, `NO_BUDGET_VERIFIED_PLAN`, `NO_TIME_FEASIBLE_PLAN`, `NO_OPEN_PLAN`, `UNSUPPORTED_CONSTRAINT`, `SOURCE_TEMPORARILY_UNAVAILABLE`, `MODEL_OUTPUT_INVALID`. Distinguish fixable input errors, insufficient proof, upstream outages, and a valid no-plan outcome. No ambiguous `200 OK` containing a fabricated plan.

**Frontend state machine:** `HOME -> INPUT_VALIDATION -> COMPILING -> ONE_PLAN -> PLAN_PROOF (optional disclosure) -> GO -> PHONE_DOWN`. Branches to `EXPLAINED_FAILURE`, `RETRY`, `OFFLINE`, and `LOCATION_DENIED`. No infinite feed or multiple suggested cards. Go/Back/Next must preserve correct itinerary state; inputs changing during compile invalidate older response IDs.

**Suggested Plan Proof gates:** grounding, routing, duration, return trip, walking, currency, price confidence, budget, opening hours, exclusions, dietary. Use the **actual versioned canonical policy list** instead of hardcoding a count for all future deployments. On any gate failure, do not emit an accepted plan.

---

## 6. Reality grounding and the Chennai acceptance correction

Use OSM/Overpass for discovery/identity only within their permitted access patterns; use official municipal/government/operator publications where needed for affirmative admission, hours, access restrictions, menus and required fee claims. SerpApi (if approved) can discover source URLs and venue leads, not magically establish verified payable cost. Community/Reddit reviews are weak discovery hints, never definitive claims. Don't scrape in violation of terms, robots, or fair-use limits.

**Mandatory immediate forensic audit:** Anna Nagar Tower Park / Dr. Visweswaraya Tower Park, `osm:way/24240071` historically reported. GCC parks list: **57,927 m²**. GCC department says parks **generally** open 05:00–21:00; investigate whether venue-specific or exception dates have independent support. Separately prove ₹0 **mandatory park admission**, distinguish any fee for tower admission, and verify public-access entrance vs OSM polygon centroid. Historical Valhalla route 1,283m/911s outbound and 1,285m/939s return plus 1,800s dwell = 3,650s is **previously reported, not a fresh measurement**. Re-fetch and check route access point, directionality, status, and source age.

If any essential fact is inadequately evidenced, **withdraw or downgrade** the accepted plan and show a typed failure. This is a product strength, not a release embarrassment. Fix provenance false positives and add regression tests. Never silently rewrite past evaluation files; preserve previous handoff in history and issue a corrected report.

---

## 7. First-class user experience and cognitive design

**Promise:** no further research required *for claims that have been proven*. Design around low choice overload, certainty calibrated to evidence, and immediate action. A user should be able to understand one clear invitation: *where, when, how long, how much, and why it passed*. The interface should show no pressure-inducing countdowns, dark patterns, irrelevant badges, or partner logos in the main path.

**HOME:** one precise title, one location control (search or explicit permission), short optional natural-language intent and simple constraint controls; sensible editable defaults, always visible currency/total context. Keyboard and screen reader support. Trust boundaries visible without shouting.

**COMPILING:** accurate status (finding places, verifying hours/prices, checking walking routes); no fake progress percentage; explicit cancel/timeout and change-input protection. Never show unvalidated suggestions while loading.

**ONE PLAN:** one primary card with address/entry point, arrival/departure/return, total seconds converted correctly, cost confidence, links to directions where genuinely available, status and freshness. `PLAN PROOF` expandable; source link validity required.

**GO:** large Start/Next/Back controls, short route and dwell instructions, progress that can work without constant eye contact; optional speech only when user opts in. Announce when offline data is incomplete. Prefer system navigation handoff over inventing turn-by-turn directions. No unsupported claim that the app tracks steps or screen ratio automatically.

**FAILURE:** plain-language, typed reason, context-preserving retry, and a constrained alternative only if it respects all hard requirements. “No verified option” is not “there are no places here.” Do not display provider internals or user precise GPS to unauthorized parties.

**Accessibility:** WCAG 2.2 AA as aspiration to test; 320px and above, 200% zoom, contrast, reduced motion, focus order, semantic headings, sufficient tap targets, keyboard activation, live status announcements, form error associations, text resizing, screen reader review. Measure actual mobile screen count and Time To Grass rather than guessing.

---

## 8. Canonical user-journey acceptance matrix

Each journey is a **testable transaction** with a defined oracle. For the automated run: generate combinations and store deterministic seeds; use actual browser automation for representative journeys. The entries below are the minimum named workflows, not the entirety of 4,096 cases.

| ID | Persona / trigger | Expected behavior / oracle |
|---|---|---|
| U01 | First visit, clean browser | Home, no console error, correct API/region disclosure |
| U02 | Explicit Chennai origin | Typed origin honored; not replaced by tester location |
| U03 | Geolocation allowed | User consent; coordinates used only for that request |
| U04 | Geolocation denied | Manual origin path; no crash or location leak |
| U05 | Geolocation timeout / low accuracy | Recoverable error, no false precise origin |
| U06 | Zero budget, solo, 60 min | Valid **verified-free** accepted plan or defensible failure |
| U07 | ₹500/person, two friends | Budget semantics and group spend correct |
| U08 | ₹500 total, four people | Cannot silently apply per-person limit |
| U09 | Food required and unknown all-in cost | Reject price; do not swap to a park as if food met |
| U10 | Food optional with zero verified paid places | May consider free outing if all hard constraints allow |
| U11 | Vegan/vegetarian or allergen constraint | Required claim evidence, otherwise typed refusal |
| U12 | No malls | Standalone venue evidence, exclusion respected |
| U13 | Quiet date | Soft preference affects ranking, never overrides a hard gate |
| U14 | Walking limit 500m | All directed pedestrian distances comply |
| U15 | Return by 9 PM | Arrival/dwell/return including time buffer meet deadline |
| U16 | Near closing hour | Full dwell inside opening window or rejected |
| U17 | Weekend, holiday, hours exception | Unknown exception isn't presented as guaranteed open |
| U18 | Cross-midnight / DST location | Zoned timestamps and date rollover correct |
| U19 | Reversed route differs from outbound | Use independent directed return path |
| U20 | Park with optional paid tower | Verify park admission separately; no false blanket ₹0 |
| U21 | No candidates | `NO_GROUNDED_CANDIDATES` with useful explanation |
| U22 | No verified all-in paid price | `NO_BUDGET_VERIFIED_PLAN` or correct canonical typed error |
| U23 | Route provider down | No guessed distance; controlled failure/retry |
| U24 | Model unavailable / invalid JSON | No accepted hallucinated plan; graceful failure |
| U25 | Search/review prompt injection | Source contents never override policy/instructions |
| U26 | Compiling then edit constraints | Discard stale response; no mismatch from old request |
| U27 | Double click / rapid submit | Prevent duplicate UI plans and uncontrolled provider load |
| U28 | Proof expand/collapse | Exact checks, source attribution, no broken links |
| U29 | GO / Next / Back / resume | Ordered steps, accurate times, working controls |
| U30 | Offline or page refresh mid-GO | Truthful cached/uncached behavior, no invented updates |
| U31 | Mobile 320/375/390/768 widths | No horizontal overflow or inaccessible controls |
| U32 | Keyboard only and screen reader | Every control accessible and state announced |
| U33 | Public production URL, fresh session | Real backend/model/source/route/GO, no fixtures |
| U34 | Unsupported city or country | Honest coverage disclosure and safe rejection |
| U35 | Provider 429/500/slow response | Bounded retries and sane user-facing result |
| U36 | Mixed language / unusual currency | Typed parse and currency-safe validation |
| U37 | Group = 1, 2, 5 and maximum group | Prices and occupancy checks correct or unsupported |
| U38 | Malicious source HTML and map redirect | No XSS/SSRF/script injection |
| U39 | All partner adapters unconfigured | Core app still starts and behaves correctly |
| U40 | Production restart/new deploy | Readiness, supported compilation, proof and GO still pass |

For each journey record: run ID, input redaction, scenario ID, environment, git SHA, deterministic seed, assertion IDs, result, timing, evidence IDs, screenshot or trace path (where applicable), failure classification. A case without meaningful assertions **does not count** toward the target.

---

## 9. Evaluation strategy — 4,096 meaningful cases, not inflated test numbers

### 9.1 Distinct testing layers (DO NOT mix counts)

| Layer | Minimum target | Execution method | Release meaning |
|---|---:|---|---|
| Generated model/domain user journeys | **4,096 distinct** | Hypothesis/stateful/pairwise over controlled providers | Extensive invariant regression; NOT 4,096 live outings |
| Adversarial and boundary cases | **300 assertion-bearing** | Invalid evidence, source injection, provider faults, time/money extremes | Safety robustness, NOT proof of source availability |
| Browser E2E | **100 journeys** | Playwright staging/local services; multiple viewport/permission states | Real UI transitions; separate genuine-provider sample |
| Controlled production smoke | **20 bounded probes/journeys** | Real public frontend/API and genuine supported compile attempts | Production release confidence; MUST cap third-party calls |
| Global scenario benchmark | **50 cases, >=10 cities** | Actual applicable live sources, typed results | Grounded coverage, success rate must be separated from safe failures |
| Real-world physical field trials | **0 until a human conducts them** | Human walking, time/cost receipts, observed screen behavior | Not simulated or claimed complete |

**Generation rule:** build an orthogonal/pairwise covering design, not a Cartesian explosion or 4,096 identical randomized requests. Dimensions: city/region, age/expiry/conflict of evidence, time of day/week/exception, group size, currency/budget scope, free/paid requirement, venue type, dietary constraints, walking limit, return deadline, route direction, source trust, source outage, location permissions, model validity, and concurrency. Unique fingerprints include actual distinct test inputs or state transitions; report coverage by dimension and interaction strength. Fix seed and reproduce failing examples; don't call public maps 4,096 times.

### 9.2 Core machine-checkable properties

- `accept -> all required hard gates PASS && linked evidence supports displayed facts`.
- `no admissible candidates -> typed failure and zero accepted displayed plans`.
- `price ESTIMATED/UNKNOWN -> NEVER guaranteed affordable`.
- `price BOUNDED -> defensible all-in upper bound <= stated correct-scope budget`.
- `end_time <= deadline`, `outbound + dwell + return + buffers <= time_budget`.
- `venue open for complete visit`, including date exceptions.
- `route.mode == pedestrian`; origin and return direction individually verified.
- `exclude mall -> no contained mall; unresolved containment -> no falsely verified no-mall`.
- `diet required -> source-backed support or no plan`.
- `accepted plan count == 1` on success; `== 0` on failure.
- `same model input seed is not a substitute for policy invariants`; revalidate on output.
- `no user PII/exact location/raw prompt in Sentry, backend logs or test snapshots by default`.

### 9.3 Performance measurements

Measure warm and cold separately: compile latency p50/p95/p99; source fetch, actual Gemma parse/rank latency; route latency; API errors; time to interactive; GO-ready from input completion; frontend bundle; memory/RAM/CPU; cold starts and provider 429s. A **<30 s** warm GO-ready target is aspirational, not guaranteed by previous ~24 s mean. Call the metric *automated Time To GO* or *software Time To Grass*; do not imply actual physical departure. No fake screen-ratio measurements.

### 9.4 Quality of tests themselves

Run a few intentionally broken-policy mutants in isolated tests; ensure gates fail when validators are weakened. Test `pytest` exit status, generated-case uniqueness, browser traces, coverage of actual policy branches, race conditions, retry semantics and assertions. A passing test suite with no production example is NOT a passing product.

---

## 10. All 16 featured and partner categories: meaningful integration or honest exclusion

**Eligibility law:** Every category must map to actual executed code or legitimate development-agent evidence, observable result, judge-viewable artifact, and an honest explanation of product value. Install-only, marketing logos, unused cloud credits, or configuration screenshots do not count as demonstrated use. Only claim categories with documented evidence. The contest gives each entry automatic eligibility for every category meaningfully used; one participant can win only **one prize** in this contest.

| Category | Legitimate Ground Rule use / first-principles rationale | Proof/qualification gate | Tier |
|---|---|---|---|
| **Render** | Public UI + production API + runtime health/CI deployment; removes demo friction | Real accessible URLs, deploy SHA, API→model→GO E2E and rollback | P0 |
| **Gemma** | Open-weight parser/ranker, local/open inference, swapability/privacy | Actual named Gemma 4 inference with request/latency and validated output | P0 |
| **Sentry Agent Tracing** | Diagnose model/tool chain latency and rejected evidence safely | Sanitized span tree in actual run; failure trace and fix | P1 |
| **SerpApi** | Live permissible source *discovery*, not blind factual verification | Actual source discovery used in compiler; provenance and validation | P1 |
| **ElevenLabs** | Optional spoken GO instructions, reducing screen use | Opt-in voice synthesis/playback, real recording, muted/fallback works | P1 |
| **GitHub Copilot** | Real code-agent reviews/CLI/agent contribution and CI | Authentic Copilot activity with linked PR/review/session; not GitHub Actions alone | P1 |
| **Entire** | Real searchable development agent sessions and decisions | Shareable sanitized session evidence explaining a concrete design change | P1 |
| **DigitalOcean** | Real remote model-serving instance / fallback compute only if economical | Actual paid/credited runtime, traces, cost cap, availability and measured requests | P1 conditional |
| **Backboard** | Actual R-CLI use or open-model comparison for parser quality | Genuine tool session or provider-based ablation with measured results | P2 conditional |
| **MongoDB Atlas** | Place/evidence cache + auditable provenance with TTL/indexes | Actual Atlas reads/writes, freshness invalidation and app use | P2 conditional |
| **Temporal** | Durable and idempotent multi-provider compile job with retries | Process kill/restart test proving resumed execution, not merely installed SDK | P2 conditional |
| **Mastra** | Meaningful TypeScript agent/tool workflow where it improves the existing app | Actual Mastra orchestration invoking tools without bypassing Python policy | P2 conditional |
| **Prior Labs / TabPFN** | Predict *source availability or retrieval prioritization* from valid historical tabular data; never guarantee price | Real TabPFN inference; leakage-safe held-out study vs naive baseline | P3 gated by data |
| **Thinking Machines / Tinker** | Fine-tune a supported model for extracting typed constraints; real experiment | Train/eval split, true Tinker job, measured generalization gain vs baseline | P3 gated by budget/access |
| **Tiger Data** | Hybrid keyword/vector retrieval of evidence if corpus warrants it | Real Tiger Data/pgvector requests and relevance evaluation | P3 gated by scale/need |
| **Qualcomm / Arduino UNO Q** | Real physical board enables a screen-free hardware interaction | Actual UNO Q hardware, code running on board, authentic demonstration | P3 hard hardware gate |

**Prioritization is safety-critical:** Do not add Atlas AND Tiger Data AND a separate state database without an architectural case. Do not introduce Temporal + Mastra orchestration for a trivial request that already compiles reliably. Do not run Tinker fine-tuning with 20 synthetic rows and claim improvement. Do not label a simulated Arduino or generic microcontroller as a real UNO Q. Optional experimentation can be maintained in a separate benchmark/demo adapter and excluded from public critical path.

Every adapter must have: capability probe, offline test double, real integration smoke where available, timeout/retry, scoped permissions, redactable trace, disable switch, cost/failure limit, and proof ledger. Suggested statuses: `NOT_CONFIGURED`, `CONFIGURED`, `REACHABLE`, `INTEGRATED`, `VERIFIED`, `INELIGIBLE`, `BLOCKED`. **Never mark VERIFIED based only on the presence of an environment variable.**

---

## 11. First action: one consolidated API/access/budget request

The agent must first inspect the repository, `.env.example`, `render.yaml`, CI workflows, provider adapter names, available hardware, git access and already configured integrations. **Do not print or expose secret values.** Ask the user **once**, in a consolidated table, only for genuinely missing authorizations:

- **P0:** GitHub repo access/push rights; Render workspace/service linking; live Gemma inference runtime location/capacity (or consent to provision it); Valhalla/OSM compliant endpoints; deployment domain/access if relevant; any current provider quota limitation.
- **P1:** Sentry DSN/project; SerpApi key; ElevenLabs API/voice permissions; real Copilot/Entire integration availability; DigitalOcean token and **budget cap** if deployment there makes sense.
- **Conditional:** Backboard; Atlas connection; Temporal; Tinker; TabPFN entitlement and historical data; Tiger Data; actual UNO Q hardware; model-training and hosted database cost approval.

Use **secret names, portal paths and instructions**; never request plaintext keys in chat. User configures local ignored `.env`, CI protected secrets or Render Dashboard. All paid provisioning requires explicit approval for provider, maximum cost and shutdown/cleanup. Until then, work on everything unblocked. No optional credential should prevent a green core application.

---

## 12. Production blueprint and minimum credible architecture

**Deployment path preferred:**

1. **Render static web client** (`runtime: static`, Vite `dist`, SPA rewrites, versioned assets, correct public API URL).
2. **Render Python/FastAPI web service** (`runtime: python` or tested Docker, pinned dependencies, explicit start command, bind to platform `$PORT`, CORS allowlist, origin protections, health endpoints, request timeouts/rate limiting).
3. **Reachable open-weight inference:** validated Gemma 4 E2B Ollama runtime (historical tag `gemma4:e2b-it-qat`) on sufficiently provisioned permitted compute. Use Render suitable-instance/private service **or** DigitalOcean GPU/Droplet only when technically feasible and approved. DO NOT assume `localhost:11434` from Render reaches a laptop; it does not. Validate memory and startup model load; Ollama's model listing includes a ~4.3 GB quantized variant, with runtime memory above bare weights.
4. **Live source adapters** for OSM/Overpass, official webpages/structured feeds, permitted SerpApi if authorized, pedestrian Valhalla route service. Respect provider rate limits and license/attribution.
5. **Optional** Sentry and a single justified persistent store (skip if not needed); do not depend on optional services for startup.

If hosted model compute is too expensive or unavailable: (a) obtain user-approved viable inference endpoint, or (b) keep a clearly labelled **recorded demonstration** separate from actual live compile and mark production core as BLOCKED. Never turn a fixture into a fake live demo or bypass model requirements.

### 12.1 Render hard checks

- Validate `render.yaml` using supported `render blueprints validate render.yaml` where CLI available; check service types, plans, regions, repo/branch, build/start, static publish path, SPA rewrite, `healthCheckPath` and CORS.
- Render Blueprints **do not interpolate arbitrary `${VAR}`** within YAML; use documented `fromService`, literal nonsecrets or explicit setup.
- `sync: false` prompts at **initial** Blueprint creation; later-added secrets may require manual Render configuration. Never put tokens in YAML or Git history.
- Separate lightweight `GET /health/live` (process alive) from `GET /health/ready` (critical compile dependency readiness), and possibly restricted diagnostics. Readiness shouldn't assert inference works if it doesn't. Keep health endpoint time bounded enough for platform probing.
- Check actual deployment SHA/environment, TLS, DNS, env, OSM attribution, model reachability, cold start, 401/403/CORS, POST body, 4xx vs 5xx and unexpected `503` guards.
- Validate restart, rollback to a known-good SHA, reload env secrets, and no side effects on retry. Avoid always-on model hosting costs without permission.

### 12.2 Security/privacy

- No public write access to secrets or model admin endpoints; upstream endpoints allowlisted; prevent SSRF/URL redirect abuse and XSS from venue names/content.
- Request bounds, rate limits, dedupe/idempotency, timeout/deadline budgets, provider circuit breakers, sensible retry jitter and no cascading 429s.
- Consent-based geolocation. Never store raw prompt/precise GPS in Sentry or public logs by default. Document any service receiving location data; retention/TTL minimal; avoid identity/profile tracking.
- Pin/scan dependencies, inspect CORS/CSRF semantics, forbid production fixture flag; CI secrets blocked from fork PRs; redact screenshots and demo traces.
- Do not assert a pedestrian route is guaranteed physically safe or accessible unless credible evidence supports it.

### 12.3 Operational SLOs and fallback

Set measured goals rather than retrospective claims: clean browser home loads; viable warm supported compile ideally <=30s GO-ready, but record real p50/p95 and if unachievable explain constraints; no known P0 defects; no policy breaks; gracefully fail on source outage/model outage; zero fake certainty. Define budget alerts, uptime probes, max monthly exposure, rolling restart, canary/smoke after deploy, rollback, and incident checklist.

---

## 13. Controlled end-to-end deployment verification

**Local:** reproduce all canonical checks from clean install, isolated Pydantic/backend schemas, parser/ranker real Ollama, fixtures only where explicitly flagged, live source/hours price provenance, route contract, browser success/failure.

**Staging:** fresh production build, separate secrets/quotas, isolated store, HTTPS, cold start, mobile emulation, keyboard tests, public API origin, model logs, Sentry trace, synthetic fault injection, throttled load.

**Production:** verify deployed frontend URL in clean/incognito browser and on mobile viewport; correct commit SHA; real API compile request in permitted location; real Gemma inference step; source ledger genuine and current; deterministic validator; exactly one accepted plan or honest typed failure; expandable Plan Proof and working GO. Capture live screenshot/video, redacted API response, model ID and latency, all 11 or current canonical checks, timestamp. Repeat after restart and latest deployment. **A static web page plus healthy GET route is not production acceptance.**

Smoke failures need explicit root cause and rollback. Don't run thousands of public API calls through shared Overpass/Valhalla or paid partners. The 20-production-probe target is bounded and can consist of health, CORS, no-fixture, data freshness and a modest number of real compile flows, but clearly distinguish them in reports.

---

## 14. Release severity, gating and freeze

**P0 blocker:** incorrect/unsupported venue claim, unknown price guaranteed, failed hard policy accepted, fixture presented as live, production compile inaccessible, model never actually invoked, injected source gaining system authority, exposed secret, no real supported demo, contest ineligible repo.

**P1 important:** broken main mobile GO flow, keyboard unusability, failed retry, unstable source/routing, nonfunctional claimed partner, CI not enforceable, missing license/reproducibility/demo artifact.

**P2:** secondary responsive imperfections, demo narration polish, optional partner adapter refinement, small latency optimizations.

**Release freeze:** stop optional feature additions when any unresolved P0 threatens overnight deadline. Fix P0 then P1 then submission evidence. Roll back risky last-minute integrations. Avoid arbitrary test skips, altered expectations or fabricated benchmarks.

Exact verdict:

- `RELEASE READY — VERIFIED`: actual public deployed path, real open-weight operation, at least one defensibly supported live accepted outing and browser GO, P0/P1 appropriate gates green, contest documentation/assets assembled, remaining step is user review/publish DEV post.
- `CONDITIONAL RELEASE — DISCLOSED LIMITATIONS`: public core usable, no violations, but credible noncritical omissions or coverage limits fully disclosed.
- `BLOCKED — CRITICAL REQUIREMENTS UNMET`: no real working production path, false provenance, severe security/correctness fault, or unaddressed eligibility requirement.

**No impossible acceptance standard:** You cannot prove zero unknown bugs or guarantee a winning verdict. You can prove the status of a bounded exhaustive campaign with explicit remaining risks.

---

## 15. Realistic overnight sequence and checkpoints

*Target is an agent run that stays active on the user's machine/cloud runner. These documents do not schedule a background job or themselves execute code.*

| Phase | Focus | Stop condition / tangible artifact |
|---|---|---|
| 0 — immediate | Scoped repo/CI/env inspection; consolidated credential/cost question | `docs/ACCESS_REQUEST.md`; inventory without secret values |
| 1 — first-principles audit | Reconcile actual hard invariants vs report; park source correction | Corrected ledger; regression tests; P0 issue list |
| 2 — core production runtime | Make Gemma/API/OSM/Valhalla real and deployable | Locally integrated success/failure and readiness proof |
| 3 — initial cloud release | Staging → Render production, permitted remote model | Public URL and real live supported compile, screenshots |
| 4 — correctness campaign | 4,096 distinct offline journeys; 300 adversarial; 100 browser | Machine-readable seeds/results/coverage and bug fixes |
| 5 — partner value | P1 adapters, real integration smoke, judge proof | Evidence ledger covering 16 categories; honest eligibility |
| 6 — release verification | CI, production smoke, restart, rollback, security | Signed-off SHA / report + residual risk |
| 7 — submission assets | README, diagrams, demo, screenshot, DEV article draft | User has only final fact review/post submission to perform |

Do not let a P3 fine-tuning experiment postpone or damage P0 completion. Stop before spending money if budget/permission hasn't been granted.

---

## 16. Submission quality: build for judges, not hype

A compelling 60–90s demo: **0–8s** human problem (even a simple budget/time/date request); **8–20s** enter constraints; **20–40s** real API/Gemma compile into one valid plan; **40–55s** transparent provenance/11 policy checks; **55–70s** GO + phone-down/voice (only if actually working); **70–90s** architecture/real failure and limitations. Produce a shorter cut where useful; no false filmed outings. It is acceptable to show human action instructions without claiming the user actually visited.

Suggested article title: **“I Stopped Asking AI Where to Go. I Made It Prove the Plan First.”** Thesis: an open-weight model handles subjective language; public/open world data grounds; deterministic code decides what can be shown; the product minimizes screen time. Explain why failing safely on paid eateries is a meaningful design decision, and present global evaluation as **2 accepted / 48 safely rejected (historical; update only after rerun)** instead of saying 50 worldwide successes. Give candid costs and limitations.

A compliant DEV submission needs the official template, `#devchallenge` + `#hf26challenge`, published post, **new project and new repo created/completed during 2026-10-05 through 2026-10-11 PDT**, code repository URL, demo URL/video, explanation of open innovation, and truthful selected partner categories. **One contest entry**, **at most one prize**. No fake backdated repo; if history doesn't meet rule, flag immediately. Include third-party attribution/model licenses, setup instructions and privacy notice. Draft it overnight but **do not publish without user approval**.

---

## 17. Required repository outputs

Preserve existing canonical paths if present; do not overwrite unrelated agents' work.

```
AGENTS.md                                  # obey existing scope and policies
GROUND_RULE_FINAL_REFERENCE.md             # this canonical reference
GROUND_RULE_OVERNIGHT_MASTER_PROMPT.md     # agent launch command
render.yaml                                # verified infra-as-code
.env.example                               # names/descriptions only, zero secrets
README.md                                  # runnable public setup + truthful coverage
LICENSE; NOTICE                           # actual correct license/attribution
.github/workflows/release.yml              # or existing canonical workflow
docs/ACCESS_REQUEST.md                     # missing API/authorization/costs
docs/REQUIREMENTS_TRACEABILITY.md          # requirement -> code -> tests -> proof
docs/ARCHITECTURE_RELEASE.md               # trust boundaries and provider graph
docs/PARTNER_ELIGIBILITY.md                # 16 categories + actual proof/status
docs/USER_JOURNEYS.md                     # primary + fallback state machines
docs/DEPLOYMENT.md                        # complete setup and public URL validation
docs/OPERATIONS.md                        # monitoring, cost, restart, rollback
docs/DEV_DRAFT.md                         # full ready-to-review final article
evals/reports/FINAL_EVIDENCE_AUDIT.md       # including park correction
evals/reports/FINAL_POLICY_EVAL.json
evals/reports/FINAL_GLOBAL_EVAL.json
evals/reports/FINAL_USER_FLOW_COVERAGE.json
evals/reports/FINAL_BROWSER_E2E.md
evals/reports/FINAL_SECURITY.md
evals/reports/FINAL_PRODUCTION_SMOKE.md
evals/reports/FINAL_RELEASE_VERDICT.md
artifacts/release/                        # sanitized screenshots, video, traces
```

Each report has UTC timestamp, git SHA, environment, exact command, results, skips, evidence links, duration, failures, and whether each test used fixture or live providers. Don't commit secrets or giant videos without a storage/size plan.

**Final handoff to user (only after actual execution):** actual public URL; repo URL; SHA; deployment state; last passing commands; number of unique generated cases, adversarial tests, real-browser tests, real prod checks; current accepted global fraction; supported geography; P0/P1 defects left; whether field tests are pending; 16-category eligibility statuses; potential fees; screenshot/demo location; what exactly user must do to publish; objective release verdict.

---

## 18. Sources to verify during implementation

**Contest (authoritative):**
- https://dev.to/challenges/hacktoberfest-week1-2026-10-05/
- https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules
- https://hacktoberfest.com/my/promos (promos may vary; do not assume credits)

**Grounding example:**
- https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf (row 14, p. 1, area 57,927 m²)
- https://chennaicorporation.gov.in/gcc/department/park/ (parks *generally* open 05:00–21:00)

**Production/model:**
- https://render.com/docs/blueprint-spec
- https://render.com/docs/configure-environment-variables
- https://render.com/docs/health-checks
- https://ollama.com/library/gemma4/tags (includes `gemma4:e2b-it-qat`)

**Optional research/training:**
- https://thinkingmachines.ai/tinker/
- https://tinker-docs.thinkingmachines.ai/tinker/quickstart/

Check current documentation, SDK versions, usage limits and licenses when implementing; this section is not a substitute for credentials or an integration test.

---

## 19. One-page final release acceptance card

- [ ] The actual source repository and creation dates comply with contest rules.
- [ ] Mandatory source-to-claim audit corrected park area and proved (or withdrew) hours/admission claim.
- [ ] One real compliant supported outing compiles using live source + real Gemma + real walking route; no fixture disguise.
- [ ] Exactly one accepted card and verifiable Plan Proof; GO works from public URL on mobile.
- [ ] Entire live round trip and mandatory cost are deterministically verified.
- [ ] Real paid-eatery claims are correct, or remain visibly unsupported without speculative promises.
- [ ] All unconfigured optional partners degrade safely, and claimed partners have live evidence.
- [ ] All P0 tests, canonical checks, 4,096 distinct generated cases, 300 adversarial and 100 Playwright target cases pass **or actual shortfall is recorded**.
- [ ] Clean browser prod run, restart, health, CORS, model, source, routing and rollback checks are recorded.
- [ ] Security/privacy, responsive UX, keyboard navigation and screen-reader basics are checked.
- [ ] No unpaid/unauthorized resources provisioned, exposed credentials, or unbounded test traffic.
- [ ] Repo, README, license, screenshots, truthful demo and article draft are prepared.
- [ ] Physical field trials are marked **NOT EXECUTED** unless a human actually performs them.
- [ ] Final release verdict states exactly what is and is not demonstrated.

**Desired end state:** the user needs only to fact-check the ready DEV article and publish the entry. If that state cannot be reached under actual credentials/evidence, the agent must preserve the real blocker rather than manufacture readiness.
