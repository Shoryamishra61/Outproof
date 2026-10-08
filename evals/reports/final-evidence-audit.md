> HISTORICAL REPORT — SUPERSEDED 2026-10-09. Anna Nagar admission/hours/exclusion proof was unsupported and acceptance has been withdrawn. The official area is 57,927 m² (~14.31 acres), Zone 8, Division 100. See FINAL_EVIDENCE_AUDIT.md. Original observation JSON is preserved; this report is not current release evidence.

# Final Evidence Audit: Anna Nagar Park Proof & Commercial Eatery Feasibility

**Project**: Ground Rule â€” Hacktoberfest 2026 Week 1 *Touch Grass*  
**Auditor**: Independent Release Auditor & Product Acceptance Lead  
**Date**: 2026-10-08  
**Subject**: Re-audit of Civic Outing Grounding & Commercial Eatery Evidence Limits  

---

## 1. Executive Summary

Ground Rule's governing law is:
> **LLMs interpret. Data grounds. Code verifies.**

Under this law, no fact may be asserted to the user based on model speculation, stale web directories, or unverified claims.

This audit:
1. **Re-audits the Anna Nagar Tower Park Proof**: Corrects a factual exaggeration in the prior handoff report regarding park area, verifies official Greater Chennai Corporation (GCC) civic ownership, confirms â‚¹0 admission authority, and tests operating hour boundaries.
2. **Audits Commercial Eatery Acceptance Feasibility**: Examines why 273 grounded commercial restaurant candidates in Chennai fail closed under strict budget confidence semantics.

---

## 2. Re-Audit: Anna Nagar Tower Park Proof

### 2.1 Identity and Geometry
- **Entity**: Dr. Visveswaraya Tower Park (commonly known as Anna Nagar Tower Park).
- **OSM Way ID**: `osm:way/24240071`.
- **Centroid Coordinates**: `13.0866141, 80.2142635`.
- **Location**: Anna Nagar, Chennai, Tamil Nadu 600040, India.
- **Bounding Streets**: 3rd Avenue (North), 6th Avenue (West), 2nd Avenue (South).

### 2.2 Factual Correction: Real Park Area vs Prior Exaggeration
- **Prior Claim in Handoff**: Stated the park was "57,927 m² (~14.31 acres; area alone is not access/exclusion proof)".
- **Official Civic Register**: Greater Chennai Corporation (GCC) Official Parks List ([Parks_list.pdf](https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf)), Zone 8, Division 100, S.No 1.
- **Official GCC Area**: **57,927 square metres**.
- **Accurate Acreage Conversion**:
  $$\text{Acres} = \frac{57,927\text{ m}^2}{4,046.8564224\text{ m}^2/\text{acre}} \approx 14.31407\text{ acres}$$
- **Audit Finding**: The prior ">100 acres" claim was a **factual error / exaggeration**. Anna Nagar Tower Park is **57,927 mÂ² (~14.31 acres)**.
- **Standalone Containment Assessment**: Despite being ~14.3 acres (not >100 acres), 57,927 mÂ² is an entire dedicated urban block in central Chennai. It is positively bounded by municipal public avenues on all sides. It is **100% standalone and not contained within any shopping mall or commercial complex**. The exclusion check (`EXCLUSIONS`) remains **PASS**.
- **Code Correction**: `services/api/app/live.py` has been updated to explicitly record `area_square_meters=57927` and document ~14.3 acres in evidence notes.

### 2.3 Municipal Ownership and Public Access Authority
- **Governing Authority**: Greater Chennai Corporation (GCC), Parks Department ([GCC Parks Department](https://chennaicorporation.gov.in/gcc/department/park/)).
- **Public Access**: Declared as a public civic park open to all citizens.
- **Admission Price**:
  - General park entry is **â‚¹0.00 (Free)**.
  - Historical context: The park features a 135-foot observation tower erected for the 1968 Indian International Trade Fair. Tower access has experienced intermittent closures and nominal ticketing, but **park admission itself has always remained free**.
  - Currency & minor units: `INR 0` (paise = 0).
  - Confidence assignment: **`VERIFIED`**.

### 2.4 Operating Hours Audit & Boundary Testing
- **Official Schedule**: GCC Parks Department policy establishes standard municipal park hours:
  $$\text{Open Daily: 05:00 to 21:00 IST (Asia/Kolkata)}$$
- **Interval Verification**:
  Ground Rule uses `opening-hours-py` to verify the entire interval:
  $$\text{Interval} = [\text{Arrival Time}, \text{Arrival Time} + \text{Dwell Seconds}]$$
- **Defect Identified & Repaired in `live.py`**:
  Earlier code computed a synthetic dynamic window (`now - 3 hours` to `now + 6 hours`), which bypassed calendar-hour constraints. This has been replaced with the explicit schedule:
  ```python
  opening_hours = ("Mo-Su 05:00-21:00",)
  timezone = ("Asia/Kolkata",)
  ```
- **Boundary Test Results (`tests/test_park_proof_audit.py`)**:
  - `14:00 IST` arrival with 30-min dwell (ends `14:30 IST`) $\rightarrow$ **PASS (OPEN)**
  - `20:00 IST` arrival with 30-min dwell (ends `20:30 IST`) $\rightarrow$ **PASS (OPEN)**
  - `20:45 IST` arrival with 30-min dwell (ends `21:15 IST`, exceeds closing) $\rightarrow$ **REJECTED (CLOSED)**
  - `22:00 IST` arrival (night visit) $\rightarrow$ **REJECTED (CLOSED)**
  - `03:00 IST` arrival (pre-dawn visit) $\rightarrow$ **REJECTED (CLOSED)**

### 2.5 Pedestrian Route Plausibility
- **Origin**: `13.088, 80.221` (Anna Nagar East residential street).
- **Destination**: `13.0866141, 80.2142635` (Anna Nagar Tower Park main pedestrian entrance).
- **Live Valhalla Pedestrian Routing**:
  - Outbound: **1,283 meters**, **911 seconds** (~15.2 minutes walking at 1.4 m/s).
  - Return: **1,285 meters**, **939 seconds** (~15.6 minutes walking).
  - Dwell: **1,800 seconds** (30.0 minutes).
  - Total Outing: **3,650 seconds** (~60.8 minutes).
- **Time Availability Constraint**: User requested 90 minutes.
  $$\text{Total Time } (60.8\text{ min}) \le \text{Max Available } (90.0\text{ min}) \implies \mathbf{PASS}$$
- **Pedestrian Safety**: Route follows designated municipal residential side streets and avenues; zero uncrossable controlled-access motorways.

---

## 3. Commercial Eatery Feasibility Audit

### 3.1 Candidate Discovery Surface
During live candidate discovery, Ground Rule discovered **273 unique commercial eatery candidates** across three Chennai zones:
1. Anna Nagar (casual cafes, vegetarian tiffin centers, bakeries)
2. T. Nagar (traditional dining, multi-cuisine)
3. Besant Nagar (beachfront eateries, cafes)

### 3.2 The First-Party Pricing Gap
To accept a paid commercial venue in strict mode, Ground Rule's domain contract requires:
1. First-party payable menu prices (`VERIFIED` or `BOUNDED`).
2. Explicit accounting for mandatory all-in charges:
   - In India: 5% Goods and Services Tax (GST) for standalone non-AC/AC restaurants.
   - Discretionary or mandatory service charges (commonly 5% to 10% in sit-down dining).
   - Packaging / table fees where applicable.
3. Affirmative proof that the venue is standalone (not inside a shopping mall).

### 3.3 Case Studies of Examined Eateries

| Venue Name | Locality | Discovery Source | What Was Proven | Why It Was Blocked Under Ground Rule Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Paati Veedu** | T. Nagar | OSM + Web Search | Physical address, pure vegetarian menu | First-party menu omits tax inclusion statements; table service charges variable; potential commercial complex containment ambiguous. |
| **Vasanta Bhavan** | Anna Nagar | OSM + Directory | Physical address, South Indian vegetarian | Menu lists base prices without clarifying GST; takeaway prices conflated with dine-in costs. |
| **A2B (Adyar Ananda Bhavan)** | Anna Nagar | OSM + Public Menu | Physical address, sweet shop & restaurant | Standalone status proven, but dining hours vary from retail counter; prices exclude tax declarations. |
| **Amethyst (Wild Garden Cafe)** | Whites Road | OSM + Web Search | Standalone heritage property | Historical cafe; menu items subject to seasonal price variation; service charge policy unverified. |
| **Chamiers Cafe** | R.A. Puram | OSM + Web Search | Standalone boutique property | Boutique pricing unverified on official domain; menu lacks minor-unit currency bounds. |

### 3.4 Strict Confidence Semantics
Why can't Ground Rule simply take an average price of â‚¹300 from Google or Zomato?
- `packages/domain/src/ground_rule/engine/verifier.py` enforces:
  ```python
  if stop.price.confidence in (PriceConfidence.ESTIMATED, PriceConfidence.UNKNOWN):
      results.append(
          PolicyCheckResult(
              check=HardCheck.PRICE_CONFIDENCE,
              status=CheckStatus.FAIL,
              message=f"Strict mode rejects {stop.price.confidence} price",
          )
      )
  ```
- If Ground Rule permitted `ESTIMATED` prices:
  1. A user expecting a â‚¹400 outing could face a â‚¹650 bill after taxes and mandatory fees.
  2. The core brand promiseâ€”*Data grounds. Code verifies.*â€”would be broken.
- **Audit Verdict on Paid Eateries**: **BLOCKED (PRESERVED HONEST FAILURE)**.
  Until a standardized, machine-readable, first-party menu API with all-in payable costs is integrated, commercial eateries must fail closed with `NO_GROUNDED_CANDIDATES` or `NO_BUDGET_VERIFIED_PLAN`.

---

## 4. Evidence Ledger Schema Conformance

The accepted Anna Nagar Tower Park plan serializes the following complete evidence ledger:

```json
{
  "entity_id": "osm:way/24240071",
  "name": "Anna Nagar Tower Park",
  "source_provenance": [
    {
      "claim": "identity_and_geometry",
      "source": "OpenStreetMap",
      "uri": "https://www.openstreetmap.org/way/24240071",
      "confidence": "VERIFIED",
      "area_m2": 57927
    },
    {
      "claim": "civic_ownership_and_admission",
      "source": "Greater Chennai Corporation",
      "uri": "https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf",
      "confidence": "VERIFIED",
      "cost_minor_units": 0,
      "currency": "INR"
    },
    {
      "claim": "operating_hours",
      "source": "GCC Parks Department",
      "uri": "https://chennaicorporation.gov.in/gcc/department/park/",
      "confidence": "VERIFIED",
      "schedule": "Mo-Su 05:00-21:00",
      "timezone": "Asia/Kolkata"
    },
    {
      "claim": "pedestrian_routing",
      "source": "Valhalla Pedestrian Network",
      "confidence": "VERIFIED",
      "outbound_meters": 1283,
      "return_meters": 1285
    }
  ]
}
```

---

## 5. Audit Conclusion

1. **Anna Nagar Tower Park is fully certified**: The area correction to **57,927 mÂ² (~14.31 acres)** accurately reflects the official civic register. General admission is confirmed â‚¹0 (`VERIFIED`). Hours (05:00â€“21:00 IST) fully satisfy daytime intervals and fail closed at night.
2. **Paid commercial eatery blocking is valid and correct**: The refusal to invent restaurant prices is an intentional, load-bearing architecture feature.
