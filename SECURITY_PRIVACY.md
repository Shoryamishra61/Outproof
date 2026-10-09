# Security & Privacy

## Data involved

Ground Rule may process:
- current/approximate location
- budget
- dietary needs
- social context
- free text
- movement plan

Treat this as personal behavioral data.

## MVP defaults

- no account
- no persistent location timeline
- no persistent raw prompt history
- no analytics SDK capturing raw free text
- no raw prompt in Sentry
- no public precise-coordinate logging
- no review-content warehousing
- no scraped Google/Reddit corpus

## Telemetry allowed

- request UUID
- step latency
- provider status
- candidate counts
- rejection counts
- model latency/token counts
- coarse error types

Redact:
- precise location where possible
- raw user text
- complete private plan
- budget/free-text combinations

## Hosted fallback

If added later:
- label it
- never silently switch from local to hosted
- document what leaves the machine

## Claims to avoid

Do not market as:
- safety guarantee
- accessibility guarantee
- allergy guarantee
- hygiene guarantee
- medical guidance

## Starting-area search and map

Explicit search text is sent to Photon; use a public area or landmark. Map tiles send the visible tile area and site origin to OpenStreetMap. Search and GPS history are not persisted, and raw queries are not logged. A bounded, short-lived process-memory lookup cache uses hashed query keys. See `docs/LOCATION_PICKER.md` for limits and provider policy.
