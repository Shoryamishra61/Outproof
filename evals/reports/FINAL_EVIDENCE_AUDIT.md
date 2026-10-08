# Source-to-claim audit

Executed 2026-10-08 UTC / 2026-10-09 IST, working release tree. Commands: real HTTP retrieval, `normalize_tanglin`, `tests/test_park_proof_audit.py`, `tests/release/test_live_sources.py`.

| Claim | Actual source / locator | Release decision |
|---|---|---|
| Anna Nagar area | GCC Parks_list.pdf, page 1, row 14: Dr.Visweswaraya Tower Park, 57,927 m², Zone 8, Division 100 | ~14.31 acres; earlier >100-acre assertion corrected |
| Anna Nagar admission | Civic listing supplies no payable admission guarantee | Unknown; previous zero VERIFIED admission withdrawn |
| Anna Nagar hours | GCC parks department states a general 05:00–21:00 schedule | Insufficient venue/date proof; no asserted opening windows |
| Anna Nagar containment | Park area/name alone does not establish a requested exclusion | No fabricated no-mall proof |
| Singapore main grounds admission | NParks general information: affirmative free entry for everyone, everyday | SGD 0 main grounds only; optional paid attractions/food/parking excluded |
| Singapore hours | Same NParks page: Gardens 5am to 12mn daily | Asia/Singapore, full dwell checked against materialized interval |
| Tanglin access point | NParks identifies Tanglin entrance; OSM node 602215681 independently returns Tanglin Gate, barrier=gate, foot=yes | Route to reviewed gate, not polygon centroid; coordinate movement fails closed |
| Pedestrian travel | Valhalla directional responses and original timestamps | Outbound/return fetched separately; no straight-line substitution |
| Search enrichment | SerpApi official publisher links independently followed by NParks normalizer | Search is discovery only; snippets never establish admission/hours |

Sources: [GCC PDF](https://chennaicorporation.gov.in/gcc/pdf/Parks_list.pdf), [GCC parks](https://chennaicorporation.gov.in/gcc/department/park/), [NParks general information](https://sbg.nparks.gov.sg/visit/general-info/), [OSM entrance](https://www.openstreetmap.org/api/0.6/node/602215681.json).

Direct NParks and OSM HTTP 200 responses were fetched and normalized. A source link existing is insufficient: required visible statements and gate tags must match. Scripts/styles, wrong identities, moved coordinates, redirects, provider faults and missing statements are regression tested. Evidence timestamps come from actual retrieval; no synthetic refresh of unknown claims.

Historical `first-live-accepted-plan-1.json` and earlier global observations remain preserved. Their schema validity does not certify their provenance. Earlier Anna Nagar accepts must not be counted as current verified outings. Current fresh live acceptance and public browser results are separate reports; no physical trial is claimed.
