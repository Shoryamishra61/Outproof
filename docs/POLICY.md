# Phase 2 deterministic evidence policy

`ground_rule.policy.validate_plan(plan, constraints, as_of=aware_datetime)` is
pure: supplied facts enter, eleven canonical ValidationChecks leave. No network,
model, discovery, ranking, proof generation, or compiler is invoked. Inputs are
revalidated; incomplete/unsafe mutated candidates fail closed. Structural API
ingestion still rejects malformed contracts with Pydantic ValidationError.

Every check is hard. FAIL or UNKNOWN prevents acceptance. Missing facts fail;
soft preferences never relax hard checks. Canonical mappings are:

| Requested concept | Existing code |
|---|---|
| place grounding | GROUNDING |
| reachable routes | ROUTING |
| duration | DURATION |
| complete return/deadline | RETURN_TRIP |
| budget | BUDGET |
| price confidence | PRICE_CONFIDENCE |
| usable opening interval | OPENING_HOURS |
| exclusions | EXCLUSIONS |
| diet/unsupported evidence requirements | DIETARY |
| walking maxima | WALKING |
| currency scope | CURRENCY |

## Evidence normalization

The existing Evidence.value is JSON. This policy specifies its operational wire
values without changing any Phase 1 schema. Records must bind the correct
subject and match the asserted fact exactly, including numeric JSON types.
Conflicting IDs or conflicting operational values for a subject/field reject
the plan, even across evidence containers. Opening windows may have separate
nonconflicting interval records. Provider identity and coordinates must have
positive evidence; a nonempty string alone is insufficient.

| field | subject | value |
|---|---|---|
| identity | place ID | `{provider, provider_id, name}` |
| coordinates | place ID | `{latitude, longitude}` |
| categories | place ID | exact category list, including containment/chain/alcohol |
| excluded_categories | place ID | positively verified absent categories, e.g. `["mall"]` |
| dietary_options | place ID | exact positively supported options list |
| price | place ID | `{currency_code, lower_minor_units, upper_minor_units, scope, covers_all_mandatory_costs: true}` |
| opening_window | place ID | `[opens_at.isoformat(), closes_at.isoformat()]` |
| walking_route | route ID | `{from_id, to_id, from_coordinates, to_coordinates, reachable, duration_seconds, distance_meters}` |
| optional_expenses | place ID | list of `{description, price, mandatory: false}`; price may be null |

Each place price is the **complete mandatory aggregate** (tickets, minimum spend,
fees, etc.), never just a menu item. Additional mandatory costs must be aggregated
into those bounds before validation or represented by another mandatory stop.
Incomplete coverage rejects. Optional expenses cannot be route/dwell stops and
cannot be labelled mandatory or ambiguously optional. They do not contribute to
mandatory spend. Optionality is an explicit data fact, never inferred from text.
Affirmatively verified zero aggregate permits a free stop; absent/UNKNOWN price
or unknown ticket rejects even a zero-budget outing.

HIGH/MEDIUM evidence from DIRECT, SERPAPI or OSM is permitted for place facts;
walking evidence requires VALHALLA or DIRECT. COMMUNITY, LOW and UNKNOWN never
establish hard facts. Synthetic sources/providers require an explicit
`allow_fixture=True`, reserved for tests; default validation rejects them.
This checks supplied provenance and consistency, not the truthfulness of a
provider response. OSM and Valhalla adapters are now implemented and have bounded
live Chennai observations (phase-4/5 reports). This does not prove missing prices,
hours or exclusions. `ground_rule.pricing.mandatory_price` normalizes explicit
complete cost attestations; labels/menu-item-only costs remain insufficient.

## Freshness and unknown policy

All observations must be at or before injected `as_of`. Evidence is invalid at
its expiry instant. Without a shorter explicit expiry, maximum age is 30 days
for identity/coordinates, 7 days for categories/exclusions/diet, 24 hours for
price/hours, and 15 minutes for routing. Place operational evidence must remain
valid through its projected use (hours through dwell end). Routing is a fresh
forecast at validation time. These are explicit conservative prototype ceilings,
not measured provider guarantees. Unknown hours always reject. A known window
must cover arrival through the entire required dwell; closing at dwell end is
allowed. No "open now" shortcut exists.

## Money, time, and unsupported requirements

Integer minor-unit bounds are summed as group totals. PER_PERSON costs and caps
multiply by known party size; TOTAL amounts remain totals. No division, rounding
or currency conversion. Scope conversion with unknown party size rejects.
VERIFIED requires equal bounds. Strict mode permits VERIFIED/BOUNDED and uses
the upper bound; ESTIMATED/UNKNOWN reject. Explicit non-strict mode may validate
an evidenced estimate but does not upgrade its PriceConfidence.

Routes are all walking legs. All legs count against walking time/distance;
duration additionally counts every dwell. Route chains include return to origin.
UTC instants govern arrival, duration and deadline, including repeated DST hours.
Structured origin/departure, when supplied, must match the candidate.

Vegetarian/vegan require positive option evidence at every mandatory stop.
Allergy guarantees, other unsupported dietary values, ACCESSIBILITY and
UNSUPPORTED hard requirements reject under DIETARY, with an explicit message.
Their input requirements are retained. There is no new canonical error code;
a future compiler can map this rejection to UNSUPPORTED_CONSTRAINT.

A ₹800 TOTAL budget for four rejects a ₹450/person mandatory cost: the group cost
is ₹1,800. The inverse (₹800 TOTAL cost against a ₹450/person cap) passes.
Route evidence also binds both endpoint coordinates, so reusing a place ID after
changing the origin or destination cannot reuse an unrelated route forecast.
