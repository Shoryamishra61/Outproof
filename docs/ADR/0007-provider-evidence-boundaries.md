# ADR 0007 — Provider evidence boundaries

Status: Accepted for the bounded provider implementation.

Use the existing API provider protocols and 17 domain contracts. OSM identity,
coordinates, categories and original metadata map into PlaceCandidate/Evidence;
Valhalla maps directed walking legs into RouteFact. No model fills provider facts.
The API adapters own HTTP; templates, price normalization and hard policy are pure.

`osm_metadata` retains tags, raw hours/cuisine and original edit/database metadata.
Observed_at is retrieval time, not a claim that venue conditions were field checked.
Bounding-box centers are explicit and not asserted entrances. Unknown operational
hours/prices remain null. Exact provider IDs deduplicate; name-based physical
venue conflation remains unsupported.

Templates classify only from matching, permitted, fresh category evidence.
Public-space templates require additional `public_access:true` evidence at the
same place from OSM/DIRECT/SERPAPI (HIGH/MEDIUM, ≤24h, valid through dwell);
category alone does not prove public access. This is source-based permission,
not an accessibility or safety guarantee. Free templates also require exact
zero complete mandatory price, not generic park/no-price labels.

Optional SerpApi requires explicit `provider_link` evidence with
`{provider:SERPAPI, place_id:...}` from OSM/DIRECT, HIGH/MEDIUM, <7 days and
unexpired. Returned identity/name/coordinates must agree. No heuristic nearby
business crosswalk is generated. Metadata cannot silently replace direct price,
hours or exclusion proof; conflicts fail closed. Reviews/photos are discarded.

Public development endpoints demonstrate bounded requests only. A production
app needs sustainable hosted/self-hosted infrastructure and provider policy
review. Cached artifacts preserve original provenance/times and expire normally.
The compiler/API/result/GO path stays disabled while operational evidence is
insufficient. No new dependency, pricing conversion or schema redesign.
