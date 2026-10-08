# Overnight checkpoint — work in progress

2026-10-09 02:22 IST checkpoint; deployed SHA cd4239c65f391733a6279b561e420094034ce812, branch master; subsequent routing/cooldown/bridge fixes are being committed.

Canonical check: 4,862 passed / 2 opt-in external-provider tests skipped; 17 schemas; 60 structural fixtures; 85 policy fixtures; Ruff/format/TypeScript/Vite green. These are controlled checks, not live outings.
4,096 unique compiler journeys; 300 adversarial cases; 100 Chromium journeys passed.
Real local Gemma ranker: gemma4:e2b-it-qat, initial cold 114.7 s. Isolated port 11436 recovered from a conflicting desktop Ollama instance. Actual remote ranker inference over two controlled candidates completed in 58.9 s; missing/wrong authentication returned 401, correct tags 200, administrative operation 404. Temporary tunnel is not durable model hosting. No existing Cloudflare domain is available; no purchase authorized.
Anna Nagar acceptance withdrawn: GCC listing/general hours do not prove admission or venue-specific hours. Singapore sources normalized; current live attempt rejected before actual 05:00 opening.

Public frontend https://outproof-web.onrender.com and API https://outproof-api.onrender.com returned 200. Both Render services use free plans. API readiness returned 200 with model/source reachability after runtime recovery. This is not yet an accepted live user flow.
GitHub CI passed at https://github.com/Shoryamishra61/Outproof/actions/runs/37840031120 including 100 Chromium checks. Later changes require a new green run.
P0: accepted public source/routing/model/proof/GO flow pending actual Singapore opening time. P1: live browser/demo, rollback, partner traces, final reports pending. Copilot read-only source review is running in a clean clone with Entire hooks; no authentic-session claim yet.
Physical trials: NOT EXECUTED.
Next: push checked fixes; verify new CI/deploy; execute live supported compile after actual 05:00 Singapore opening (02:30 IST); record browser and provenance. Global 50-case bounded real discovery campaign is checkpointed in FINAL_GLOBAL_EVAL.partial.json. Preserve all gates.

Current verdict: BLOCKED — CRITICAL REQUIREMENTS UNMET.
