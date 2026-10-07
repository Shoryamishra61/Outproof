# API Agent Instructions

Use provider interfaces:

- `PlacesProvider`
- `EnrichmentProvider`
- `RoutingProvider`
- `ModelProvider`

Normalize provider data before domain use.

## Fail closed

If:
- model JSON invalid
- route unknown
- identity unresolved
- price evidence insufficient

return typed failure.

Never invent defaults.

## Observability

Record:
- latency
- result counts
- rejection reasons

Do not record raw private prompts.
