# Contributing

## Before PR

Run:

```bash
make lint
make test
make eval-smoke
```

## PR description

Include:
- problem
- change
- test coverage
- eval impact
- assumptions
- source/provider implications

Validation-semantic changes require:
- regression fixture
- ADR when material

## AI-assisted work

AI assistance is allowed, but contributors must:
- validate generated code
- respect provider terms
- never fabricate benchmarks
- never invent source facts
- ensure tests exercise real behavior

Prefer small vertical increments.
