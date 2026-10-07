# Blocker — first accepted real outing

Observed 2026-10-07 locally. Phase 2 policy and scoped Phase 3 control-preserving
parser gates passed. Phases 4–7 components are verified; the live enrichment /
accepted-real-plan milestone is blocked. Compilation remains unavailable.

## Exact blocker

1. No SERPAPI_API_KEY in process environment or local .env file. Presence-only
   check recorded in `enrichment.md`; no secrets displayed or requested publicly.
2. Current OSM candidates lack a verified cross-provider identity link. The
   enrichment adapter refuses a nearby-name guess as identity proof.
3. Real Chennai target candidate lacks complete mandatory price/currency/scope,
   dated hours covering arrival + dwell, and positive no-mall/containment evidence.
   Its vegetarian OSM tag, identity, coordinates and actual directed Valhalla
   routes are preserved. These gaps cannot be repaired by inventing prices,
   assuming parks free/open, interpreting price levels as bounds, or treating
   missing mall tags as affirmative absence.

An authorized SerpApi key alone is not guaranteed to supply the missing facts.
There was no unauthorized scraping, account creation, model-fact fallback or
manual patch of the real evaluation result.

## Work completed / evidence

- Existing 85-case deterministic policy and separate 100-case local model runs preserved.
- Real OSM discovery: 39 named grounded candidates, one public Chennai area.
- Live Valhalla: five reachable directed walking legs including independent returns.
- Three pure candidate templates; complete aggregate price normalization.
- Real target candidate: one built, zero accepted, 4149s including return,
  2012m. PASS grounding/routing/duration/return/walking/diet; FAIL currency,
  price confidence/budget/hours/exclusions. Missing price causes currency failure,
  not an observed foreign currency.
- SerpApi metadata adapter: offline tested, missing-key and missing-link failures typed.
- Cached local Gemma component rejection: controls preserved, no external POI/route
  requests, original source times preserved; no fully offline outing claim.
- Blank field-test forms/measurement script; unpublished demo/article source.

Exact commands/results: phase-4, phase-5, phase-6, phase-7, enrichment,
cached-demo and overnight-handoff reports. Retained JSON observations:
`discovery-chennai-live-1.json`, `routing-chennai-live-1.json`,
`templates-chennai-real-data-1.json`, `cached-chennai-component-demo-1.json`.
Do not overwrite these to present a later result as the original observation.

## Architecture unblocked by the post-Phase-7 sprint

The user's newer instruction authorizes compiler, ranker, deterministic proof,
gated API and fixture result/GO development. These are implemented and tested
against complete FIXTURE observations; see `post-phase-7.md`. The earlier held
queues remain recorded in the historical overnight handoff. The compile route
now returns typed unavailable by default, replacing the previous 404.
Public health is still false, including in explicit fixture development mode.
There are still zero accepted real outings, no field metrics or outing video.

## Safest next action

Obtain a compliant, identity-linked operational evidence source for one Chennai
eatery covering its complete chosen mandatory cost, dated opening interval and
positive no-mall containment. Configure an authorized credential privately if
needed, normalize actual returned facts without confidence upgrades, refresh
expired routing, and rerun the exact target through unchanged hard policy.
Only enable the LIVE compiler/API/UI after a real candidate passes every check. Fixture architecture does not satisfy this gate.
