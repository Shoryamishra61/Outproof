# Ground Rule — overnight handoff

Historical checkpoint. The subsequent authorized fixture sprint is recorded in
[post-phase-7.md](post-phase-7.md); its architecture work supersedes the held
queues below. These original measurements and failures remain preserved.

Session date: 2026-10-07 Asia/Calcutta. Provider artifacts retain actual UTC
timestamps (2026-10-06 UTC). Submission/accepted-real-outing gate: BLOCKED.
No earlier work was reset, deleted, re-bootstrapped or silently reclassified.

## Completed

| Phase/queue | Status and exact scope |
|---|---|
| Phase 0/1 | Preserved: bootstrap + 17 exported structural contracts |
| Phase 2 | PASS: 85 synthetic policy fixtures, no model/I/O in validation |
| Phase 3 | PASS scoped safety gate: separate 100-case actual local Gemma runs; imperfect semantic accuracy disclosed |
| Phase 4 | PASS: live OSM discovery, 39 grounded Chennai POIs; unknowns retained |
| Phase 5 | PASS: five live directed Valhalla walking legs including returns |
| Phase 6 | PASS candidate-builder gate: three synthetic templates; one real-data candidate built, zero accepted |
| Phase 7 | PASS deterministic price normalization + strict confidence policy; real-price source absent |
| Queue 6 enrichment | Offline adapter/tests complete; LIVE BLOCKED by credential/identity/evidence gaps |
| Queues 7–12 | Held: accepted-real-plan compiler, ranker, proof renderer, compile API, outing UI, GO |
| Queue 13 | Full global outing evaluation NOT EXECUTED; full-eval.md explicitly records this |
| Queue 14 | Technical CLI evaluation latencies/counts/rejections recorded; runtime compiler/Sentry tracing absent |
| Queue 15 | Local Gemma + cached factual rejection demonstrated; fully offline accepted outing not demonstrated |
| Queue 16 | Blank field-test forms, measurement script, synthetic arithmetic tests prepared; zero field results |
| Queue 17 | Unpublished article skeleton, diagram source, evidence table, README and honest demo shot list prepared |

## Verification

Final complete command actually executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
```

- Ruff lint: pass. Ruff format check: 90 files already formatted.
- pytest: **314 passed, 2 skipped in 1.76s**, 316 collected. Skips are explicitly
  opt-in external integrations. 169 prior Phase 0–3 tests remain in this suite;
  145 additional offline tests/regressions passed. No live calls in ordinary pytest.
- Schema drift: 17 checked, unchanged.
- Structural contract evaluation: 60/60, synthetic only.
- Deterministic policy evaluation: 85/85, synthetic only.
- TypeScript strict: pass. Vite production build: pass, 1.46s.
- CI was configured previously; remote CI/deployment were not executed.

Opt-in external check, separately from ordinary verification:

```powershell
$env:GROUND_RULE_LIVE_PLACES='1'
$env:GROUND_RULE_LIVE_ROUTING='1'
uv run pytest tests/test_live_providers.py -q
# 2 passed in 4.82s; each checked actual public provider output
```

Phase checkpoints (each ran full canonical verification):

| Checkpoint | Offline pytest | Schema/contract/policy/TypeScript/build |
|---|---|---|
| Phase 4 | 199 passed, 1 skipped, 1.47s | 17 / 60 / 85 / pass / pass 1.45s |
| Phase 5 | 231 passed, 2 skipped, 1.53s | 17 / 60 / 85 / pass / pass 1.42s |
| Phase 6 | 242 passed, 2 skipped, 1.54s | 17 / 60 / 85 / pass / pass 1.44s |
| Phase 7 | 263 passed, 2 skipped, 1.53s | 17 / 60 / 85 / pass / pass 1.45s |
| Enrichment | 289 passed, 2 skipped, 1.59s | 17 / 60 / 85 / pass / pass 1.42s |
| Cached/field preparation checkpoint | 302 passed, 2 skipped, 1.85s | 17 / 60 / 85 / pass / pass 1.47s |
| Final boundary regressions | 314 passed, 2 skipped, 1.76s | 17 / 60 / 85 / pass / pass 1.46s |

Exact live/evaluation commands:

```powershell
$env:PYTHONPATH='services/api;packages/domain/src'
uv run python -m evals.runner.discovery --output evals/reports/discovery-chennai-live-1.json
# 39 candidates, 3484.96ms request + normalization
uv run python -m evals.runner.routing --discovery evals/reports/discovery-chennai-live-1.json --output evals/reports/routing-chennai-live-1.json
# 5/5 reachable directed legs, 1948.04ms total
uv run python -m evals.runner.templates --discovery evals/reports/discovery-chennai-live-1.json --routing evals/reports/routing-chennai-live-1.json --output evals/reports/templates-chennai-real-data-1.json
# 1 grounded complete candidate, 0 accepted
uv run python -m evals.runner.cached --discovery evals/reports/discovery-chennai-live-1.json --routing evals/reports/routing-chennai-live-1.json --templates evals/reports/templates-chennai-real-data-1.json --model gemma4:e2b-it-qat --output evals/reports/cached-chennai-component-demo-1.json
# actual local Gemma call: 17406.47ms including reload; controls preserved
# 0 external POI/route requests; 0 accepted outings; no refreshed source timestamps
uv run python scripts/field_metrics.py docs/field-test-form.json
# expected exit 2: blank actual planning timestamp; no actual field values fabricated
```

Report paths refuse overwrite; use a new path for a future observation. Component
timings are not an end-to-end latency/Time To Grass measurement and are not summed
to invent one. Model results remain separate in phase-3 report:

| Model/run | Raw exact hard/soft | Median measured request ms |
|---|---:|---:|
| gemma3:4b run-2 | 72/100 | 10135 |
| gemma4:e2b-it-qat run-2 | 82/100 | 3488 |

Final guard replay on Gemma4: 90/100 returned, zero authoritative corruption,
zero parser place fields, 8/8 unsupported requirement/source retention. Full
requested schema rate was 96/100, despite 100/100 static IR shapes. No score
pooling or claim of universal free-text accuracy. E4B/GPU remain untested.
Ollama remains available; final `/api/ps` returned no loaded models, freeing RAM.
Downloaded model weights and failed experiments were preserved.

Final read-only replay of the retained target at its original evaluated_at with
the final builder produced exactly the same ValidationResults as the original
JSON artifact (assertion passed). No facts/timestamps/files were rewritten.
Current parser.py SHA256 remains
`aef37d4a847093f8ba6212ad07ab6dfdc304bd7832fc83e23e4b7b6708a8ca17`,
matching the preserved final Phase 3 guard replay. Source metadata inventory
exposed no SerpApi/Valhalla/Overpass/Sentry connector tools to substitute for the
missing configured enrichment credential.

## Changed files

This continuation added/touched these subsystems; earlier Phase 0–3 sources,
benchmarks, regression fixtures and generated contracts remain preserved.

- API providers: `services/api/app/places.py`, `routing.py`, `enrichment.py`.
  Existing parser.py/main.py behavior and health false unchanged.
- Pure domain: `packages/domain/src/ground_rule/plans.py`, `pricing.py`.
  models.py, policy.py and 17 schema/TypeScript contracts unchanged.
- Tests: test_places.py (30), test_routing.py (38), test_plans.py (15),
  test_pricing.py (21), test_enrichment.py (26), test_cached_demo.py (2),
  test_field_metrics.py (12); test_bootstrap.py gained compile-unavailable
  regression. test_live_providers.py has two opt-in tests.
- Evaluators: `evals/runner/discovery.py`, `routing.py`, `templates.py`, `cached.py`.
- Evidence/reports: four real-provider/cached JSON artifacts named above;
  phase-4.md through phase-7.md, enrichment.md, cached-demo.md, BLOCKED.md,
  full-eval.md and this handoff. Existing policy/contract JSON regenerated by
  canonical checks; earlier failed model runs were not overwritten.
- Field preparation: `scripts/field_metrics.py`, `docs/field-test-form.json`,
  `docs/FIELD_TESTS.md`. Actual result fields remain null.
- Documentation: README.md, TASKS.md, BUILD_ORDER.md, docs/POLICY.md,
  docs/DEMO_PLAN.md, docs/DEV_DRAFT.md, docs/ADR/0007-provider-evidence-boundaries.md.
- Configuration: pyproject.toml registers integration marker; no new dependencies.

Source-control state: HEAD does not exist (`git rev-parse --verify HEAD` reports
no revision); repository files, including original valid work, were already
untracked. Status/diff inspected before phases; no destructive reset, history
rewrite, force-push or unrelated baseline commit. Changes remain uncommitted.
Git diff alone therefore does not enumerate these untracked source changes.

## Current architecture

API still exposes health only. Explicit CLI evaluators call local parser and
the real providers; normalized PlaceCandidate/RouteFact evidence enters pure
templates/pricing/policy. Every mandatory leg includes return. No model owns
price, route, opening or hard feasibility. Unknown/conflicting/stale facts fail.
Optional enrichment retains sourced metadata only after explicit identity binding.
There is no public successful compiler, valid-plan ranker or outing UI path yet.

## Known failures

- Historical unconstrained Gemma 50000 → 100000 and invented date preserved.
  Failed 1B runs and Gemma4 prompt/thinking pilots remain recorded in phase-3.
- Raw model classification errors remain; no accepted control corruption was observed.
- Real Paati Veedu candidate: vegetarian evidence and grounding/routes/duration/
  return/walking PASS; currency/price/budget/hours/exclusions FAIL. 733s out +
  2700s dwell + 716s back = 4149s, 2012m. Those totals do not create missing proof.
- Initial Phase 5 canonical check caught Ruff E501 and stopped; fixed and fully rerun.
- Initial price test incorrectly marked boolean True coverage invalid: 1 failed,
  20 passed focused; full gate 1 failed, 262 passed, 2 skipped. Corrected fixture
  to integer 1, which is rejected. No pricing policy was weakened.
- Final review added route-error/metric contradiction and category/access-expiry
  regressions. New guard tests pass; no new live outage was claimed.
- Required SerpApi credential and provider identity crosswalk absent. Even a key
  does not turn price levels/open-now into complete mandatory cost/visit proof.

## Limitations / unverified claims

Only one public Chennai development area. OSM community facts can be stale;
retrieval time is not a physical venue check. Way/relation centers are not
entrance coordinates. Dedup is exact provider identity, not physical node/way
conflation. Raw hours syntax is preserved, not a complete opening_hours parser.
Templates use explicit fixed dwells and at most 12 sorted eligible identities;
no relevance optimizer or routing matrix. Public access needs positive evidence;
parks are not assumed free/open. Current diet policy conservatively checks every
mandatory stop, including public stops. No safety/accessibility/allergy guarantee.

No accepted real outing, ≥10-city compiler evaluation, measured field route/cost,
exactly-one successful endpoint demonstration, rendered real Plan Proof screenshot,
GO flow, hosted deployment, Sentry trace, local Valhalla graph, fully offline
accepted plan, field Time To Grass/screen ratio, published article or demo video.
Frontend was not edited; build pass does not establish a browser/outing UI gate.

## Current release gates

PASS is scoped to the stated measured population; it is not submission readiness.

| Gate | Status | Evidence / boundary |
|---|---|---|
| Hard-constraint compliance | PASS | 85/85 adversarial synthetic decisions; real incomplete candidate rejected; field compliance untested |
| Parser control preservation | PASS | Final 100-response guard replay plus actual cached local call; 0 corruption observed |
| Place grounding | PASS | 39 real OSM candidates, two live discovery checks; displayed compiler plan absent |
| Routing | PASS | Five real directed legs + repeated live test; returns independent, unreachable/null fail |
| Price confidence | PASS | Strict synthetic policy and 21 normalization tests; real price availability blocked |
| Exactly-one successful output | NOT TESTED | Structural invariant tested; successful compiler endpoint absent |
| Hallucination count for displayed outings | NOT TESTED | Zero accepted/displayed outings; do not claim perfect rate from empty population |
| Global-city coverage | FAIL | One area/city, not ≥10 cities or ≥50 full outing scenarios |
| Local inference | PASS | Separate CPU Gemma benchmarks + actual local cached call; E4B/GPU untested |
| Cached/offline outing demo | FAIL | Cached component rejection only; no accepted offline plan/local graph |
| UI compile flow | FAIL | Compiler/API/result/GO intentionally held; unchanged bootstrap frontend |
| Three field tests | NOT TESTED | Blank forms, no actual measurements |
| Time To Grass <30s | NOT TESTED | Component/parser latency is not field Time To Grass |
| Screen Ratio <5% | NOT TESTED | Metric script tested synthetically; no actual field measurements |

## Exact next task

Obtain and normalize compliant, identity-linked evidence for one Chennai eatery's
complete chosen mandatory cost, dated hours covering dwell and positive no-mall
containment; configure an authorized source privately, refresh routing, and
rerun the exact INR500/person/90min/friend/vegetarian/no-mall/quiet target through
unchanged policy. Only after a real all-checks PASS should the accepted-plan
compiler, endpoint, proof and minimal UI queue advance. See BLOCKED.md.
