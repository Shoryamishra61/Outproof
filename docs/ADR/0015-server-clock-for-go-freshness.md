# Server clock for GO freshness

An actual public Bengaluru recovery compiled a valid plan, but immediate GO returned to intake. The browser received the result around half a second before its local wall clock reached the API's `compiled_at`. The failed receipt and trace are retained; this was a real user-flow failure, not a successful release.

The API now emits its own precise `X-Server-Time` at response completion and exposes that nonsecret header to the configured CORS origin. Incoming client headers cannot set it. The frontend calibrates only an accepted LIVE response, requiring a finite server time at or after compilation. It includes the entire measured request duration as a conservative upper bound on transport delay, then advances using the greater of monotonic elapsed time and wall-clock elapsed time. Suspension and forward clock adjustments cannot extend freshness.

GO and source-observation labels use the same clock. The existing 60-second plan freshness limit, future-observation rejection, source expiry, visit opening interval and return deadline remain unchanged. Missing or invalid clock metadata keeps the prior strict client-clock behavior. Long requests may conservatively require recompilation; no deadline or freshness tolerance is enlarged.

The pure clock and GO regression reuses the actual failed public response. It checks slow-client recovery and continued rejection of stale, future, expired, closed and late-return plans. API tests verify server ownership and exact allowed-origin CORS. Public verification of the repaired clock is pending deployment.
