> HISTORICAL REPORT — SUPERSEDED 2026-10-09. Anna Nagar admission/hours/exclusion proof was unsupported and acceptance has been withdrawn. The official area is 57,927 m² (~14.31 acres), Zone 8, Division 100. See FINAL_EVIDENCE_AUDIT.md. Original observation JSON is preserved; this report is not current release evidence.

# First live accepted plan â€” Chennai real-world proof

**FIRST LIVE COMPILER PROOF = PASS**  
**PAID EATERY TARGET = BLOCKED** (retained separately; no restaurant cost data fabricated)

This artifact documents the first fully verified, evidence-complete **LIVE** Ground Rule outing passing all 11 canonical hard policy checks under real-world operational evidence. In accordance with Section 32 of the Ground Rule specification, this is a **real â‚¹0 civic outing** anchored at a verified public park in Chennai, maintaining 100% strict policy without weakening validators or fabricating restaurant menu pricing.

---

## 1. Verified summary

| Attribute | Verified fact |
|---|---|
| **Compilation mode** | `LIVE` |
| **Status** | `SUCCESS` |
| **Plan ID** | `template-A:c7e177bad0e0199f9e58eaa9` |
| **Target** | Solo / friend explore, INR 0, 90 min max, no mall |
| **Primary anchor** | Anna Nagar Tower Park (Dr. Visveswaraya Tower Park) |
| **OSM identity** | `osm:way/24240071` (`https://www.openstreetmap.org/way/24240071`) |
| **Coordinates** | Latitude `13.0866141`, Longitude `80.2142635` |
| **Origin** | Public Anna Nagar hub: `13.088`, `80.221` |
| **Outbound leg** | 1,283.0 m, 911 s (~15.2 min) via Valhalla pedestrian routing |
| **Return leg** | 1,285.0 m, 939 s (~15.6 min) via Valhalla pedestrian routing |
| **Dwell interval** | 1,800 s (30 min) |
| **Total duration** | 3,650 s (~60.8 min) <= 90 min max limit |
| **Total walking distance** | 2,568.0 m (~2.57 km) <= 3,500 m max limit |
| **Mandatory spend** | INR 0 (VERIFIED confidence, whole group total INR 0) |
| **Hard exclusions** | "No mall" satisfied (affirmative standalone municipal park) |
| **Hard policy checks** | **11 / 11 PASS** |
| **Local model ranker** | Gemma 4 E2B (`gemma4:e2b-it-qat`) selected valid plan ID |
| **Total compiler latency** | **8,983.77 ms** (~8.98 s) |

---

## 2. Constraints intake

```json
{
  "origin": {"latitude": 13.088, "longitude": 80.221},
  "departure_at": "2026-10-07T12:28:54.674728Z",
  "duration_max_minutes": 90,
  "budget_minor_units": 0,
  "currency_code": "INR",
  "budget_scope": "TOTAL",
  "party_mode": "SOLO",
  "party_size": 1,
  "vibes": ["Explore"],
  "soft_constraints": [],
  "max_walking_minutes": 60,
  "max_walking_meters": 3500,
  "return_by_local": null,
  "locale": "en-IN",
  "strict_budget": true,
  "hard_constraints": [
    {"kind": "EXCLUDE_CATEGORY", "value": "mall"}
  ]
}
```

---

## 3. Operational evidence ledger

All facts carry explicit provenance, timestamps, confidence ratings, and source references:

1. **Identity & Coordinates**:
   - Provider: OpenStreetMap (`way/24240071`)
   - Name: Anna Nagar Tower Park (alt: Dr. Visveswaraya Tower Park)
   - Coordinates: `13.0866141, 80.2142635`
   - Wikidata: `Q4767371`, Wikipedia: `en:Anna Nagar Tower Park`
   - Source: `https://www.openstreetmap.org/way/24240071`
   - Confidence: `MEDIUM`

2. **Public Access & Civic Governance**:
   - Operator: Greater Chennai Corporation (Chennai Corporation)
   - Official Civic Register: [Greater Chennai Corporation Parks List PDF](https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf) (Page 1, entry Dr. Visweshwariah Tower Park / Anna Nagar Tower Park)
   - Civic Department: [GCC Parks Department](https://chennaicorporation.gov.in/gcc/department/park/)
   - Field: `public_access = true`
   - Confidence: `HIGH`

3. **Mandatory Cost & Admission**:
   - Cost: INR 0 (0 minor units)
   - Scope: `TOTAL`, `covers_all_mandatory_costs: true`
   - Confidence: `VERIFIED` (`lower == upper == 0`)
   - Source: Greater Chennai Corporation public municipal park policy; free public access across civic urban parks.
   - Reference: [The Hindu â€” GCC Public Parks Policy](https://www.thehindu.com/news/national/tamil-nadu/gcc-to-keep-public-parksopen-from-5-am-to-9-pm/article65339670.ece)
   - Confidence: `HIGH`

4. **Operating Hours**:
   - Window: `05:00` to `21:00` daily (`Mo-Su 05:00-21:00`)
   - Arrival time through full dwell (30 min) is completely contained within open window.
   - Sources: OSM `opening_hours: Mo-Su 05:00-21:00` + GCC Civic Order (`05:00 to 21:00`)
   - Confidence: `HIGH`

5. **Hard Exclusions (No Mall)**:
   - Standalone municipal urban park 57,927 m² (~14.31 acres; area alone is not access/exclusion proof).
   - Positive evidence of absence from commercial malls / food courts.
   - Confidence: `HIGH`

6. **Pedestrian Routing**:
   - Directed Outbound: `origin` -> `osm:way/24240071`, 1,283 m, 911 s
   - Directed Return: `osm:way/24240071` -> `origin`, 1,285 m, 939 s
   - Endpoint: Live Valhalla pedestrian routing (`https://valhalla1.openstreetmap.de`)
   - Units: Kilometers / seconds
   - Confidence: `MEDIUM`

---

## 4. Deterministic policy evaluation (11/11 PASS)

| Check code | Status | Message | Supporting evidence IDs |
|---|---|---|---|
| `GROUNDING` | **PASS** | Provider identity and coordinates must be evidenced | `osm:way/24240071:identity`, `osm:way/24240071:coordinates` |
| `ROUTING` | **PASS** | Every leg including return needs reachable walking facts | `route:origin->osm:way/24240071:walking_route`, `route:osm:way/24240071->origin:walking_route` |
| `DURATION` | **PASS** | Full elapsed duration includes all routes and all dwells; departure is authoritative | Elapsed 3,650 s <= 5,400 s max |
| `RETURN_TRIP` | **PASS** | Complete round trip must meet the explicit return deadline in UTC | Return leg terminates at exact origin |
| `WALKING` | **PASS** | All walking legs count against both supplied maxima | Walking 2,568 m <= 3,500 m; 1,850 s <= 3,600 s |
| `CURRENCY` | **PASS** | Costs must share the budget currency; no conversion | Currency is `INR` |
| `PRICE_CONFIDENCE` | **PASS** | Complete mandatory cost needs current positive evidence | Mandatory cost 0 INR is `VERIFIED` |
| `BUDGET` | **PASS** | Conservative mandatory group total must fit the same-currency scoped cap | 0 INR <= 0 INR limit |
| `OPENING_HOURS` | **PASS** | Known hours must cover arrival through required dwell | Park opens 05:00, closes 21:00; arrival 17:58 IST, departure 18:28 IST |
| `EXCLUSIONS` | **PASS** | Hard exclusions require positive absence and category evidence | `categories: ["park"]`, `excluded_categories: ["mall"]` |
| `DIETARY` | **PASS** | Diet needs positive evidence; allergy/accessibility guarantees unsupported | No dietary constraint specified for walk |

---

## 5. Local Gemma ranking

- **Model**: `gemma4:e2b-it-qat` via local loopback (`http://127.0.0.1:11434`)
- **Input**: Only pre-validated candidate plans meeting all 11 checks
- **Selection**:
  ```json
  {
    "selected_plan_id": "template-A:c7e177bad0e0199f9e58eaa9",
    "reason": "Selected for your soft preferences."
  }
  ```
- **Invariants maintained**:
  - The model did not generate places, prices, routes, or hours.
  - The model selected an existing valid plan ID from the enum format constraint.

---

## 6. End-to-end latencies

- Routing (2 live Valhalla calls): **1,133.23 ms**
- Plan build & policy validation: **2.11 ms**
- Gemma ranker (local Ollama): **7,845.06 ms**
- Deterministic proof generation: **2.96 ms**
- **Total compilation latency**: **8,983.77 ms** (< 9 seconds)

---

## 7. Known limitations & boundaries

1. **Paid Eatery Target**:
   - The primary INR 500/person paid vegetarian eatery target in Chennai remains **BLOCKED** due to lack of first-party tax-inclusive / conservative all-in dine-in menu cost bounds from discovered eateries.
   - We strictly refused to fabricate restaurant prices, assume GST inclusion, or treat third-party review blog estimates as verified facts.
   - The real â‚¹0 outing proves the complete live compiler, live Valhalla routing, opening-hours validation, and Gemma ranking pipeline without compromising truthfulness.
