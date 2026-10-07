# Phase 0 — bootstrap evidence

Date: 2026-10-06 (Asia/Calcutta). Scope: bootstrap only.

## Results

- Git initialized in the existing build-pack directory; organizer instructions,
  logging policies, prompts, and example eval remain present.
- Python 3.12.13; uv 0.11.9; Node 24.15.0; npm 11.12.1.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: pass.
- `uv run pytest`: 1 passed, no warnings after replacing the deprecated
  TestClient transport with httpx ASGITransport.
- `npm run check --prefix apps/web`: TypeScript strict check and production
  build pass. Bundle: 224.12 kB JS / 70.08 kB gzip, 1.47 kB CSS / 0.68 kB gzip.
- API started with uvicorn; live `GET /v1/health` returned 200 and explicitly
  reported `compilation_available: false`.
- Development URL `http://127.0.0.1:5173` and production preview
  `http://127.0.0.1:4173` both showed the connected bootstrap state in browser.
- Explicit `GEMMA_MODEL=gemma3:1b` local CPU echo: schema valid, all synthetic
  controls preserved, measured call latency 17100 ms. See
  [phase-0-model.json](phase-0-model.json). This is one synthetic smoke,
  not a parser accuracy benchmark or Time To Grass measurement.
- Ollama 0.35.1 standalone archive SHA-256:
  `dc50b9ca7f9023c86525012632cd1615b093d0407987444a7f62ecab617e8e93`,
  matched the official release checksum before extraction.
- Local model digest:
  `8648f39daa8fbf5b18c7b4e6a8fb4990c692751d49917417b8842ca5758e7ffc`.

## UI evidence

Visual thesis: Field notebook. Paper/grass tokens, a single notebook rule for
the setup action, and the compiler invariant as footer. See `docs/UI_BRIEF.md`.

- Tested 360, 768, 1024, and 1440 CSS-pixel widths, 800px height. Document
  scroll width equaled viewport width at each size; retry target is 49.6px tall.
- Keyboard Tab reached retry with `:focus-visible` and a visible outline.
- Browser exercised connected, unavailable, retry recovery, and pending/disabled
  states. The pending test used a temporary local 3-second health server;
  the real API was then restored.
- Measured text contrast: muted/footer 5.95:1, status 11.86:1, button 9.39:1.
- No warning/error entries in the recovered page's captured browser logs.
- Mandatory `ui_audit.py apps/web`: zero findings after adding button type.
- Static UI has no animation; reduced-motion CSS is present. OS motion-emulation,
  screen reader testing, Core Web Vitals, and standalone PWA installation were
  not tested. This is not a product UI release claim.
- Screenshot: `docs/evidence/bootstrap.png`.

## Failed attempts and limits

- One smoke was attempted before model installation completed and returned 404.
- GPU inference stayed in warm-up without a model response and was stopped;
  the resulting client connection error is not a successful model run.
- The first CPU echo passed schema validation but failed exact-control equality.
  The smoke's schema was tightened to require every optional key, including
  nulls; the subsequent echo passed. Optional keys in the original schema did
  not provide a complete echo contract.
- Default Gemma 4 E4B download was stopped because of slow transfer. Partial
  files remain ignored and resumable; its inference and quality are unverified.
- Current startup script disables hosted inference; CPU mode is explicit.
- CI workflow is configured; no remote CI execution is claimed.
- No parser, provider, validator, compiler, outing UI, field test, or submission
  deliverable is claimed. Later phases remain unchecked.

Official setup references: [Windows Ollama](https://docs.ollama.com/windows),
[structured output](https://docs.ollama.com/capabilities/structured-outputs),
[CPU selection](https://docs.ollama.com/gpu).
