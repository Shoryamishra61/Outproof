# Data Sources & Evidence Policy

## Goal

The system is only as trustworthy as its evidence.

The model must never convert weak/missing data into confident facts.

## OpenStreetMap / Overpass

Role:
- global discovery
- coordinates
- category/tags
- some hours/cuisine metadata

Use:
- core source
- honor OSM attribution/licensing requirements

Freshness varies.

## Valhalla

Role:
- walking route feasibility
- distance
- ETA
- matrices/isochrones

Routing truth for MVP, subject to map quality.

## SerpApi

Role:
- fresh local enrichment
- open state/hours
- ratings/counts
- price metadata where present
- identity hints

Never assume all fields exist.

## Google-derived data

Only through compliant/authorized APIs/providers.

Do not:
- scrape Google Maps pages
- bulk copy reviews
- create a shadow Places database

Honor attribution/provider policies.

## Reddit/community

Role:
- weak local relevance
- discovery hints
- "locals discuss this" signal

Never use alone for:
- operational status
- address
- coordinates
- price
- dietary guarantee

Do not scrape without authorization.

## Evidence precedence

Suggested:
1. recent structured provider field
2. direct source/provider record
3. OSM tag
4. community discussion
5. model inference

Model inference is never enough for operational facts.

## Evidence object

```json
{
  "field": "opening_status",
  "value": "open",
  "source": "serpapi",
  "source_ref": "provider-id",
  "observed_at": "2026-10-06T12:00:00Z",
  "confidence": "HIGH"
}
```

## Conflicts

Never silently merge contradictions.

If confidence remains insufficient:
- reject in strict mode

## Price

Use:
- VERIFIED
- BOUNDED
- ESTIMATED
- UNKNOWN

Strict paid plan:
- VERIFIED/BOUNDED only

If no sufficient price evidence:
- compile free outing
- or `NO_BUDGET_VERIFIED_PLAN`

## Local Mode

Community/local signal may affect ranking but never bypass validation.

Possible weak signals:
- repeated local mentions
- independent/non-chain
- neighborhood specificity
- moderate review count

Avoid ungrounded "hidden gem" claims.

## Origin lookup and map imagery

Photon/OpenStreetMap supports explicit starting-area search, and standard OpenStreetMap tiles support the origin picker. Neither is outing proof. Provider limits, attribution, privacy and test isolation are documented in [LOCATION_PICKER.md](LOCATION_PICKER.md).

## Production discovery provider

`OVERPASS_URL` selects the OSM discovery service. The production blueprint uses `https://maps.mail.ru/osm/tools/overpass/api/interpreter`, an instance listed in the [OSM public-instance register](https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances). A bounded Potheri query returned actual HTTP 200 and OSM identities on 2026-10-10 IST. This is discovery evidence, not admission, hours, accessibility or availability proof. The prior `overpass-api.de` endpoint worked from the developer computer but produced `ConnectError` from Render; TLS checks remain enabled.

The query sends the starting coordinate and a 1 km radius to that provider, requests at most 8 MiB of query working memory and uses an identifying project User-Agent. Recovery requests are serialized, with at most one retry for transient connection/gateway failures. Rate limits and access denials are not immediately retried. A minimum 60-second cooldown honors valid server Retry-After values; incomplete/malformed data fail closed, and no failed result becomes a plan. Public endpoints have no project uptime guarantee. A repeated real query hit upstream HTTP 504 after an earlier success. Do not turn the controlled test campaign into live provider load.

## Reviewed India garden sources

`app.reviewed_gardens` freshly joins official venue-specific admission/hours to exact OSM park and pedestrian-path ways. Current registry: Shanti Kunj and Terraced Gardens, Chandigarh. The access node must be inside the named park, on the reviewed footway, and the footway must cross its boundary; routing still uses independent directed Valhalla legs. This is mapped access, not physical gate verification. Missing/changed/hidden/conflicting records fail closed. Source digests and parse lineage travel with each plan; no fees, hours or negative categories are inherited for unreviewed parks. Main walk-only grounds scope excludes food, parking and paid activities. See `evals/reports/INDIA_100_RELEASE.md` for the real 100-origin failures and verification limits.

The deployed Chandigarh authority connection timed out while OSM completed. When the existing protected HTTPS model endpoint is configured, only these two fixed official pages are fetched through its authenticated source relay. Original source URLs, freshness, strict parser assertions and exact OSM geometry remain authoritative; relay transport is explicit in lineage. The relay rejects anonymous/wrong keys, arbitrary IDs/URLs, redirects, oversized bodies and concurrent requests. This shares the laptop/tunnel availability limit. See ADR 0012.
