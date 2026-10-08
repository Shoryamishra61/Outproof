"""Unsupported civic facts must never acquire proof or a fresh timestamp."""

import asyncio
from datetime import UTC, datetime

import pytest
from app.live import LiveEnrichmentProvider
from app.places import normalize_overpass


@pytest.mark.parametrize("osm_id,name", [(24240071, "Anna Nagar Tower Park"), (1, "Tower Park")])
def test_register_does_not_establish_admission_or_hours(osm_id: int, name: str) -> None:
    observed = datetime(2026, 10, 8, tzinfo=UTC)
    places = normalize_overpass(
        {
            "elements": [
                {
                    "type": "way",
                    "id": osm_id,
                    "center": {"lat": 13.0866141, "lon": 80.2142635},
                    "tags": {"name": name, "leisure": "park"},
                }
            ]
        },
        observed_at=observed,
    )
    original = places[0]
    enriched = asyncio.run(LiveEnrichmentProvider().enrich(original))
    assert enriched == original
    assert enriched.price is None and enriched.opening_windows is None
    assert not any(e.field in {"public_access", "excluded_categories"} for e in enriched.evidence)
    assert all(e.observed_at == observed for e in enriched.evidence)
