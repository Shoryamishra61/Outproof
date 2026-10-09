# Searchable starting point, distinct from venue evidence

Replace numeric coordinate entry with explicit Photon place search and a Leaflet map. No paid geocoding account is required. Queries are user-triggered rather than autocomplete, and the server validates and bounds provider output, serializes requests and caches briefly in memory. Map tiles retain attribution and an origin referrer; tests use controlled tile imagery. See [location picker](../LOCATION_PICKER.md) for privacy, provider policy and capacity limits.

Search supplies only the user's origin. It never supplies outing admission, hours, price or safety proof. All existing hard validators and exactly-one-plan checks remain authoritative. Worldwide origin selection does not establish worldwide supported outings.

LIVE mode begins without an origin. The Singapore example requires explicit selection. Fresh GPS can be retried, and a coarse fix requires map confirmation; request identities prevent a delayed GPS fix from replacing a newer choice. Keyboard map movement and selection are available without dragging.
