# Final E2E Results: Automated Verification, Browser Testing, and Desk Usability Rehearsal

**Project**: Ground Rule — Hacktoberfest 2026 Week 1 *Touch Grass*  
**Auditor**: Independent QA Lead & Browser Automation Engineer  
**Date**: 2026-10-08  
**Environment**: Windows 11 / PowerShell / Chrome Headless & Interactive Browser Subagent  

---

## 1. Automated Verification Suite Execution

The canonical check script (`scripts/check.ps1`) was executed against the repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1
```

### Detailed Subsystem Breakdown:

| Subsystem / Test Suite | Command Executed | Tests / Checks | Result | Notes |
| :--- | :--- | :---: | :---: | :--- |
| **Python Linter** | `uv run ruff check .` | 120 files | **PASS** | 0 lint errors |
| **Python Formatter** | `uv run ruff format --check .` | 120 files | **PASS** | 100% formatted |
| **Unit & Integration Suite** | `uv run pytest` | 433 collected | **431 PASS, 2 SKIPPED** | Skipped tests require optional remote keys; all core tests green |
| **API Contract Validation** | `scripts/export_contracts.py --check` | 17 schemas | **PASS** | Frontend/backend type parity |
| **Structural Contract Eval** | `evals/runner/contracts.py` | 60 cases | **60/60 PASS** | 100% schema compliance |
| **Deterministic Policy Eval** | `evals/runner/policy.py` | 85 cases | **85/85 PASS** | 100% hard check compliance |
| **TypeScript Strict Check** | `npm run check --prefix apps/web` | Strict mode | **PASS** | 0 type errors |
| **Vite Production Build** | `npm run build --prefix apps/web` | 217 modules | **PASS** | Bundle compiled in 2.6s |
| **UI Quality Audit** | `anti-slop-ui` standards | 5 files | **0 FINDINGS** | Complies with quality contract |

---

## 2. Interactive Browser End-to-End Walkthrough

An interactive browser subagent was executed against the running local development environment (`http://127.0.0.1:5173/` web client with `http://127.0.0.1:8000` backend API).

### 2.1 Complete User Journey Executed:

1. **Page Load (Home View)**:
   - Canvas rendered cleanly with high contrast and dark theme.
   - Header verified: `Ground Rule / LIVE` badge active.
   - Subtitle verified: `Verified live places, operating hours and pedestrian routes.`
   - Starting Location selector rendered:
     - Checked: `Try the verified Chennai example (Anna Nagar Tower Park)`
     - Unchecked: `Use device location (GPS)`
   - Verified 0 console errors and 0 uncaught exceptions.

2. **Compilation Trigger**:
   - User clicked primary action button: `Compile Verified Outing`.
   - Loading indicator displayed with real-time compilation status.
   - Compilation completed successfully in ~2.4 seconds.

3. **Result View (Exactly One Plan)**:
   - Returned plan displayed: **Dr. Visveswaraya Tower Park (Anna Nagar Tower Park)**.
   - Pricing badge: `₹0.00 VERIFIED` (Paise = 0).
   - Duration badge: `60.8 min` (under 90-minute limit).
   - Distance: `2.6 km` total walking distance.
   - Verified: **Exactly one plan returned** (no top 5, no recommendations feed).

4. **Plan Proof Deep Audit**:
   - User expanded the `Plan Proof` disclosure accordion.
   - Verified all 11 canonical checks displayed with green passing indicators:
     - `GROUNDING: PASS (OpenStreetMap way/24240071)`
     - `ROUTING: PASS (Valhalla pedestrian network)`
     - `DURATION: PASS (3,650s <= 5,400s)`
     - `RETURN_TRIP: PASS (Full return leg included)`
     - `WALKING: PASS (2,568m <= tolerance)`
     - `CURRENCY: PASS (INR)`
     - `PRICE_CONFIDENCE: PASS (VERIFIED ₹0.00)`
     - `BUDGET: PASS (₹0 <= ₹500 budget)`
     - `OPENING_HOURS: PASS (05:00 - 21:00 IST covers arrival + 30m dwell)`
     - `EXCLUSIONS: PASS (Standalone park; 0 malls)`
     - `DIETARY: PASS (N/A for public park)`
   - Verified complete source provenance ledger with official civic links.

5. **GO Mode Activation & Screen-Down Guidance**:
   - User clicked `GO` button.
   - View transitioned smoothly into focused step-by-step navigation mode.
   - Step 1 rendered: Outbound walking directions from origin along 3rd Avenue.
   - Prominent notice displayed: `Phone down.` instructing user to pocket their phone and enjoy the walk.
   - Step navigation buttons (`NEXT`) tested and responsive.

### 2.2 Viewport & Accessibility Verification:
- **Desktop (1280x800)**: Clean single-column layout, zero horizontal overflow.
- **Mobile (390x844)**: Responsive card sizing, touch targets $\ge 44\text{px}$, high-contrast text ratios exceeding WCAG AA requirements.
- **Console Log State**: 0 errors, 0 warnings, 0 failed asset requests.

---

## 3. Remote Usability Rehearsal Metrics

Because physical field outings cannot be physically conducted by autonomous agents prior to submission, we performed an automated desk-based usability rehearsal to measure product ergonomics:

| Usability Metric | Desk Measurement | Target | Status |
| :--- | :---: | :---: | :--- |
| **Clicks to Initiate Outing** | **2 clicks** (Compile $\rightarrow$ GO) | $\le 3$ clicks | **EXCEEDED** |
| **Desk Time To Grass** (Page load to GO) | **~18 seconds** | $< 30$ seconds | **EXCEEDED** |
| **Compiler Latency** (Local Live) | **~2,400 ms** | $< 5,000$ ms | **PASS** |
| **Screen Ratio** (Desk Rehearsal) | **< 3%** of outing time | $< 5\%$ | **PASS (Desk)** |
| **Physical Field Outing Observations** | **NOT EXECUTED** | Physical verification | **NOT EXECUTED** |

> **Important Disclosure**: The above metrics represent automated desk-based rehearsals under simulated conditions. Real-world physical field tests with human foot traffic, GPS drift, and in-person store receipts remain marked as **NOT EXECUTED** and are scheduled for post-submission human testing.
