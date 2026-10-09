# Starting-location repair

Type an area or landmark, select a match, or choose a starting point on the map. LIVE mode no longer silently uses the Singapore example. GPS refresh requests a new fix; coarse fixes need map confirmation, and late callbacks cannot overwrite a newer origin. Numeric coordinate entry is removed.

Local verification: `./scripts/check.ps1` passed 4,900 tests with two opt-in skips, Ruff, 17 schemas, 60 structural cases, 85 policy cases and TypeScript/Vite. `npx --prefix apps/web playwright test --config apps/web/playwright.config.ts` passed all 134 Chromium cases, including ten new location cases. Automated map interaction uses controlled imagery. A real Photon lookup returned five validated Anna Nagar/Chennai origin matches; it establishes no admission, hours or outing feasibility.

Desktop 1440px and mobile 390px visual review found no overflow or page errors. New keyboard/search checks also cover 360/768/1024/1440px. The UI audit reported zero high findings and one motion heuristic; Leaflet animation options and keyboard pan animation are explicitly off, with existing reduced-motion CSS retained. The visual thesis and three signature decisions are documented in `docs/LOCATION_PICKER.md`.

Failures were preserved: initial missing browser installation, author-introduced selector encoding, a recovery selector for an already-open map and duplicate accuracy-text matching. No safety assertion or validator was relaxed. Physical GPS and field trials remain unexecuted. Public changed-build verification is pending deployment; the existing public model connection was found offline and is being restored through the authenticated bridge.
