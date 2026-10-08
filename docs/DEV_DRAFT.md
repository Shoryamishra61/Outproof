---
title: I Stopped Asking AI Where to Go. I Made It Prove the Plan First.
published: false
tags: devchallenge, hf26challenge
---

*Author-review draft for the Hacktoberfest Week 1 Touch Grass challenge. Live release evidence and demo links are being assembled; do not publish this checkpoint.*

## What I Built

I wanted a small outing, not another evening spent comparing recommendations. A normal question—how much time do I have, can I afford it, can I get home, will it be open—can become a dozen browser tabs. Ground Rule closes that loop: **your limits in, one real plan out**.

Its governing rule is simple: **LLMs interpret. Data grounds. Code verifies.** Gemma reads fuzzy preferences and chooses among already-valid plans. It cannot invent a venue, own a price, guess a walking route or override a hard constraint. If evidence is missing, the app says so. A refusal is more useful than a convincing promise about a closed gate.

This release deliberately has narrow live coverage: the Singapore Botanic Gardens Tanglin entrance corridor, main grounds only. The National Parks Board publishes affirmative free-admission and daily opening information. OpenStreetMap independently identifies a pedestrian entrance. Valhalla supplies an outbound route and a separately requested return route. Optional paid attractions, parking and food are excluded from the free outing. Other regions and unproven commercial stops can return a typed failure.

The public interface has one constraint form, one accepted plan, a source ledger, and GO. GO offers one instruction at a time and a walking-map handoff. Optional ElevenLabs audio is an opt-in generic GO cue, not fabricated turn-by-turn guidance. It is an attributed noncommercial demonstration.

## Demo

Repository: [Outproof / Ground Rule](https://github.com/Shoryamishra61/Outproof).

Public deployment and a genuine live video are pending verification in this checkpoint. Add only the URLs recorded in FINAL_PRODUCTION_SMOKE.md and the final demo artifact. No physical outing footage has been recorded.

## My Experience

The most useful bug I found was a proof that looked complete. An earlier Anna Nagar Tower Park plan linked to a municipal register, assigned zero admission, and used a general citywide park schedule as venue-specific hours. Eleven passing checks could not rescue those unsupported inputs.

I withdrew the acceptance. The civic register supports a real area—57,927 square metres, about 14.31 acres—and identifies the park. It does not prove every park service is free or a particular visit interval is open. The earlier over-100-acre description was wrong. Regression tests now prevent a familiar park name, or any unrelated “Tower Park,” from gaining fabricated evidence.

The same principle shaped routing. The compiler routes to a reviewed pedestrian gate, not the centre of a park polygon. It retrieves both directions separately, checks the complete dwell interval and return, and retains the real observation timestamps. A stale route does not become fresh because the model or adapter touched it again.

The automated campaign currently includes 4,096 distinct controlled compiler journeys, 300 adversarial cases and 100 actual Chromium journeys across ten widths. These counts describe software tests with synthetic providers, not thousands of real outings. Canonical Python/TypeScript/schema/policy checks were executed; the final release reports will give exact final counts, failures, skips, public smoke results and global accepted/rejected/provider-error breakdown.

Real Gemma 4 E2B inference ran on the existing laptop. The first cold ranker smoke took about 115 seconds, so the under-30-second target is not established. A secured temporary tunnel can make that machine reachable from the API, but it depends on the laptop and has no stable-hosting guarantee. I am keeping that limitation visible rather than calling a model listing proof of reliable inference.

## Why Open Innovation Matters

Open weights make the model boundary inspectable and replaceable. I can run the same Gemma model locally, test malformed outputs, constrain its schema, and compare its ranking with deterministic validation. The policy code owns admissibility; the model owns subjective selection. A model swap cannot authorize a price or invent an opening window.

OpenStreetMap supplies independently inspectable identities and gate coordinates. Public operator information supplies the admission and hours claims. Each displayed operational fact has a source, a timestamp and an expiry policy. The domain checks and failure cases are open so another person can reproduce the decisions instead of trusting a polished paragraph.

This is not completely offline: fresh place and routing evidence require network access. The web shell can be cached, but a cached shell is not an offline verified outing. The model being local also does not mean third-party map providers never receive location: routing needs coordinates, disclosed in the app. Raw prompts and exact GPS are excluded from technical Sentry events, and persistent outing history is not stored.

## Partners and limitations

Only integrations with executed evidence will be listed in the final article. Render/Gemma/source discovery/tracing/voice and any bounded Backboard experiment are tracked separately in PARTNER_ELIGIBILITY.md. GitHub Actions is not proof that a Copilot agent was used. No physical Arduino UNO Q is available. Unnecessary databases, orchestration frameworks and unapproved training are excluded.

All new cash spending is capped at zero. Existing free quotas and credits are used with bounded calls and no automatic top-up. Three physical India field trials have **not** happened. Screen Ratio, physical departure time, safe access and worldwide coverage are not claimed. The supported product is a small evidenced loop, with honest rejection where the world cannot yet be proved.

The final author review must confirm actual public availability, replace the pending demo section with verified links, check partner claims against the ledger, and publish one DEV entry using the challenge template and tags. This draft has not been published.
