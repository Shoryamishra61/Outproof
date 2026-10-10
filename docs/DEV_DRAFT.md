---
title: I Stopped Asking AI Where to Go. I Made It Prove the Plan First.
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Week 1 Challenge: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05/).*

## What I Built

I wanted a small outing, not another evening spent comparing recommendations. A normal question—how much time do I have, can I afford it, can I get home, will it be open—can become a dozen browser tabs. Ground Rule closes that loop: **your limits in, one real plan out**.

Its governing rule is simple: **LLMs interpret. Data grounds. Code verifies.** Gemma reads fuzzy preferences and chooses among already-valid plans. It cannot invent a venue, own a price, guess a walking route or override a hard constraint. If evidence is missing, the app says so. A refusal is more useful than a convincing promise about a closed gate.

This release deliberately has narrow live coverage: the Singapore Botanic Gardens Tanglin entrance corridor, main grounds only. The National Parks Board publishes affirmative free-admission and daily opening information. OpenStreetMap independently identifies a pedestrian entrance. Valhalla supplies an outbound route and a separately requested return route. Optional paid attractions, parking and food are excluded from the free outing. Other regions and unproven commercial stops can return a typed failure.

The public interface has one constraint form, one accepted plan, a source ledger, and GO. Starting areas are searchable by name through Photon/OpenStreetMap, with a map pin and keyboard selection instead of numeric coordinate entry. GPS can request a fresh fix; coarse fixes need confirmation. Real public searches were verified for Chennai, London and Tokyo, which establishes origin lookup, not global outing acceptance. GO offers one instruction at a time and a walking-map handoff. Optional ElevenLabs audio is an opt-in generic GO cue, not fabricated turn-by-turn guidance. It is an attributed noncommercial demonstration.

## Demo

[Open the live application](https://outproof-web.onrender.com/) and [watch the public execution recording](https://outproof-web.onrender.com/demo.html). The fresh current-time plan/proof/GO recording shows software execution, not a physical outing. Its HTTPS playback, exact hash, range response, keyboard and responsive checks passed. A [mobile location-search recording](https://outproof-web.onrender.com/location-demo.webm) separately shows the revised starting-area and map interface.

## Code

[Outproof / Ground Rule](https://github.com/Shoryamishra61/Outproof). The public repository was created during the challenge period. Source is MIT licensed; model, map and audio terms remain separate in `NOTICE`.

## How I Built It

Python/Pydantic owns typed boundaries and deterministic policy. React/TypeScript keeps the interface small. Gemma 4 E2B, served through Ollama, parses language and ranks only surviving plan IDs. The browser checks the proof contract again and rechecks evidence, the visit interval and the effective return deadline before GO.

The most useful bug I found was a proof that looked complete. An earlier Anna Nagar Tower Park plan linked to a municipal register, assigned zero admission, and used a general citywide park schedule as venue-specific hours. Eleven passing checks could not rescue those unsupported inputs.

I withdrew the acceptance. The civic register supports a real area—57,927 square metres, about 14.31 acres—and identifies the park. It does not prove every park service is free or a particular visit interval is open. The earlier over-100-acre description was wrong. Regression tests now prevent a familiar park name, or any unrelated “Tower Park,” from gaining fabricated evidence.

The same principle shaped routing. The compiler routes to a reviewed pedestrian gate, not the centre of a park polygon. It retrieves both directions separately, checks the complete dwell interval and return, and retains the real observation timestamps. A stale route does not become fresh because the model or adapter touched it again.

Two less visible failures mattered too: freshly fetched observations were incorrectly compared against the request-start clock, and opening windows were clipped to the original dwell interval, invalidating GO after a few seconds of reading. I reproduced both failures, corrected their shared causes, and retained closure, expiry and daylight-saving regressions.

The release checks passed 4,914 Python tests, 17 schema checks, 60 structural and 85 policy fixtures, plus the TypeScript build. The campaign includes 4,096 distinct controlled compiler journeys, 300 adversarial cases, 300 property examples, four critical-gate mutants detected and 135 controlled Chromium journeys. These describe software checks with controlled providers, not thousands of real outings.

An actual Potheri user attempt exposed a limit those controlled tests did not establish: the production discovery connection failed while the page said “live mode ready.” I reproduced the failure, separated compilation status from the Singapore-only readiness probe, repaired serialized recovery and changed the unreachable discovery provider. Render then discovered three real Potheri identities. None supplied admission and operating-hours proof, so the app still declined to promise an outing. A repeat also hit an upstream gateway timeout, so I added one bounded transient retry without retrying access denials or rate limits. Potheri is not supported yet; the test count does not change that.

After the garden's published opening time, a fresh current-time Singapore browser run reached the plan in 7.973 seconds and GO in 26.486 seconds, including proof-display pauses. It used real Gemma parsing/ranking, eleven hard checks and no fixture facts. The new 68.28-second public recording shows that supported software flow; it does not depict a physical outing or establish Potheri coverage.

The real global campaign attempted 50 cases across 19 cities: zero accepted, 40 typed refusals and ten provider failures. That does not demonstrate worldwide operation. Separately, three supported real public compiles passed, including parser and ranker execution; their small warm sample had a 4.01-second median. A clean browser reached GO in about four seconds.

Real Gemma 4 E2B inference runs on the existing RTX 3050 laptop. The first cold ranker smoke took about 115 seconds, so consistently sub-30-second performance is not established. An authenticated, bounded temporary tunnel connects it to the deployed API, but depends on the laptop and has no stable-hosting guarantee. A real proxy outage made production readiness fail; restarting restored authenticated operation while anonymous access stayed denied. Both Render services were rolled back to a known green build and a fresh public browser passed afterward.

A later first-visit check exposed a readiness race: a concurrent provider check briefly disabled the UI. Both healthy and unavailable-source regressions failed before the correction; the shared readiness probe now preserves its actual result for waiting callers. The corrected build passed independent CI and automatically deployed. A fresh public optional-text parser/ranker journey reached the plan in 5.93 seconds and GO in 6.33 seconds with all eleven checks passing; that one run is execution evidence, not a latency guarantee.

## Why Does Open Innovation Matter?

Open weights make the model boundary inspectable and replaceable. I can run the same Gemma model locally, test malformed outputs, constrain its schema, and compare its ranking with deterministic validation. The policy code owns admissibility; the model owns subjective selection. A model swap cannot authorize a price or invent an opening window.

OpenStreetMap supplies independently inspectable identities and gate coordinates. Public operator information supplies the admission and hours claims. Each displayed operational fact has a source, a timestamp and an expiry policy. The domain checks and failure cases are open so another person can reproduce the decisions instead of trusting a polished paragraph.

This is not completely offline: fresh place and routing evidence require network access. The web shell can be cached, but a cached shell is not an offline verified outing. The model being local also does not mean third-party map providers never receive location: routing needs coordinates, disclosed in the app. Raw prompts and exact GPS are excluded from technical Sentry events, and persistent outing history is not stored.

## My Agent Session

[Read the genuine Copilot review](https://github.com/Shoryamishra61/Outproof/blob/master/docs/agent-sessions/copilot-parser-review.md). It identified a dietary-negation issue that informed a tested correction. Entire captured that actual session through supported manual attachment after noninteractive hooks did not fire. Automatic capture is not claimed, and private credential-containing chat was not imported.

## Prize Categories

Demonstrated uses are Render, Gemma, Sentry technical agent spans, SerpApi official-link discovery, ElevenLabs opt-in voice, GitHub Copilot development review and Entire manual session capture. [The evidence ledger](https://github.com/Shoryamishra61/Outproof/blob/master/docs/PARTNER_ELIGIBILITY.md) describes exactly what ran; judges determine qualification. Backboard authenticated but refused chat inference because its free credits cover Memory/RAG; HTTP 200 was not model success. No physical Arduino UNO Q is available. Unnecessary databases, orchestration frameworks and unapproved training are excluded.

All new cash spending is capped at zero. Existing free quotas and credits are used with bounded calls and no automatic top-up. Three physical India field trials have **not** happened. Screen Ratio, physical departure time, safe access and worldwide coverage are not claimed. The supported product is a small evidenced loop, with honest rejection where the world cannot yet be proved.

The final author review must confirm the fresh public links and final verdict, keep these limitations visible, check partner claims against the ledger, and publish one DEV entry using the challenge template and tags. This draft has not been published.

## India coverage correction

A fresh production campaign tried 100 distinct India starting areas. It returned zero accepted outings: 87 missing-evidence refusals and 13 provider failures. Those results remain published separately from controlled test counts. The shared source repair adds official Chandigarh fee/hour records joined to mapped pedestrian access for Shanti Kunj and Terraced Gardens; both completed real local and deployed Gemma/source/route validation with eleven checks. Two current-time public API plans passed in 5.29 and 4.76 seconds; two clean public browsers passed typed search, real parser/ranker, proof and GO, including mobile and keyboard submission. A fresh 69-second Shanti Kunj screen recording is linked on the public demo page. The first deployed source requests failed and remain retained; a protected fixed-source relay repaired Render’s official-site connection timeout without changing fact validation. This is narrow reviewed support, not a global or 100-place success claim. Physical visits remain unexecuted.
