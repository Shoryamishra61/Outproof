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
