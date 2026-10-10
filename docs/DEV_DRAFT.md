---
title: Outproof — One Outing, With Proof Before GO
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05/).*

<!-- Engineering draft. Broad geographic coverage, permanent inference hosting and physical trials remain unmet. Update with the final deployed evidence before author review; do not publish as a completed release. -->

## What I Built

Outproof turns “I should go outside” into one constrained outing. It is for someone who has limited time and money and wants to stop comparing recommendations. Set your starting area, time including return, budget and hard rules. A successful result contains one plan, its source proof, and GO: one next instruction, then phone down.

The rule is **LLMs interpret. Data grounds. Code verifies.** The model cannot invent a venue, a price or a route. If the evidence cannot support the trip, the app refuses it.

The implemented live source coverage is narrow: Singapore Botanic Gardens at Tanglin; Shanti Kunj and Terraced Gardens in Chandigarh; and Cubbon Park in Bengaluru. Main-ground walks exclude food, parking, purchases and optional attractions. Searchable starting locations worldwide do not mean verified outings worldwide. Arbitrary origins can also fail if the walking provider snaps away from the chosen point.

## Demo

[Open Outproof](https://outproof-web.onrender.com/). Choose the explicitly labelled Chandigarh walking start to inspect the reviewed corridor, or search your public starting area and adjust its map pin.

[Watch the real public software demonstration](https://outproof-web.onrender.com/demo.html). The 73-second recording shows the real renamed Outproof interface, one-plan proof and GO loop. It depicts no physical outing. Inference depends on an awake laptop and an authenticated temporary tunnel; provider outages and cold starts can prevent compilation.

## Code

{% github Shoryamishra61/Outproof %}

[Source, deployment configuration and release evidence](https://github.com/Shoryamishra61/Outproof). Application source is MIT licensed; model, maps and audio have separate terms in `NOTICE`. Established internal Ground Rule package and environment names remain for compatibility.

## How I Built It

Gemma `gemma4:e2b-it-qat` runs locally through Ollama on an RTX 3050 laptop, with CPU/RAM assistance. It parses fuzzy preferences into typed constraints and ranks candidates only after deterministic validation. Structured model output is schema-checked. The deployed FastAPI API reaches that runtime through an authenticated proxy; model credentials stay server-side.

Photon/OpenStreetMap finds a starting point. Fresh official visitor information supplies reviewed admission and hours, joined to exact OSM identities and mapped pedestrian paths. Valhalla independently routes outbound and return legs. Python verifies currency-safe costs, duration, opening intervals, walking limits, provenance and hard exclusions. React shows one result and its evidence ledger.

One real audit changed the implementation: a provider echoed the requested city-centre coordinate while its actual path began about 21 metres away. That connector had no verified time or access. I withdrew that whole-trip claim and added actual path-endpoint validation instead of guessing the missing walk. Duplicate geocoder records also produced indistinguishable buttons; exact duplicates now collapse and distinct map matches remain selectable.

GitHub Actions runs locked builds, schema and policy checks, controlled provider regressions, browser journeys and secret scanning. A separate production workflow requires a real accepted public compilation and hard-rule refusals after deployment. Controlled tests, public execution and physical trials remain separate evidence populations.

Sentry records technical timing rather than private prompts or location history. An actual sampled HTTP/grounding/Gemma hierarchy is retained in the [sanitized trace report](https://github.com/Shoryamishra61/Outproof/blob/master/evals/reports/OUTPROOF_SENTRY_TRACE_LIVE.json). Sampling is 10%; the latest one-hour query did not include a ranking span, and that failed observation check is retained too.

The release reports retain unsuccessful India searches and provider failures. Potheri has no evidence-sufficient accepted outing. The final live campaign produced no verified outing from the 100 original India starting points. Broad India coverage remains unfinished. Three physical India visits and physical screen-ratio measurement are **UNEXECUTED**. The product makes no physical access or safety guarantee.

## Why Does Open Innovation Matter?

Open-weight inference lets me inspect and change the parser/ranker contract and run the model on hardware I already control. It gives the project a replaceable local inference boundary rather than tying its policy to one hosted API. OpenStreetMap and Valhalla make the geographic evidence and routing assumptions inspectable too.

Local model execution does not make the whole product offline or permanently hosted. Fresh place and routing sources still require a network, and the laptop must stay available. The useful freedom is to change these parts while keeping the same deterministic safety contract.

## My Agent Session

Development-session evidence and authentic Copilot/Entire usage are recorded in the repository's [partner ledger](https://github.com/Shoryamishra61/Outproof/blob/master/docs/PARTNER_ELIGIBILITY.md). No DevRelay embed has been verified; no agent-session link is invented here.

## Prize Categories

The implementation has recorded real use of Gemma, Render, Sentry, SerpApi, ElevenLabs, GitHub Copilot and Entire. The linked partner ledger distinguishes runtime use from development tooling and records the actual evidence and limitations. Final category selection is for author review; eligibility is determined by the judges. Arduino and the other unimplemented partner categories are not claimed.
