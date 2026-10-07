import asyncio
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from app.enrichment import EnrichmentResult, SerpApiEnrichmentProvider, normalize_enrichment
from app.places import normalize_overpass
from ground_rule.models import CompilationFailure, Evidence, PlaceCandidate

NOW = datetime.now(UTC)


def place() -> PlaceCandidate:
    candidate = normalize_overpass(
        {
            "elements": [
                dict(
                    type="node",
                    id=1,
                    lat=13.04,
                    lon=80.23,
                    tags={"name": "SYNTHETIC cafe", "amenity": "cafe"},
                )
            ]
        },
        observed_at=NOW,
    )[0]
    link = Evidence(
        evidence_id="synthetic-link",
        subject_id=candidate.place_id,
        field="provider_link",
        value=dict(provider="SERPAPI", place_id="synthetic-google-id"),
        source="OSM",
        source_ref="synthetic-test-only",
        observed_at=NOW,
        expires_at=None,
        confidence="MEDIUM",
    )
    return candidate.model_copy(update={"evidence": candidate.evidence + (link,)})


def payload() -> dict:
    return dict(
        place_results=dict(
            title="SYNTHETIC cafe",
            place_id="synthetic-google-id",
            gps_coordinates=dict(latitude=13.04, longitude=80.23),
            rating=4.2,
            reviews=50,
            price="₹₹",
            open_state="Open now",
            hours=[{"Wednesday": "9 AM–5 PM"}],
            user_reviews={"summary": "Must not retain"},
            photos=["Must not retain"],
        )
    )


def normalize(
    value: object, candidate: PlaceCandidate | None = None
) -> PlaceCandidate | CompilationFailure:
    return normalize_enrichment(
        candidate or place(), value, reference_id="synthetic-google-id", observed_at=NOW
    )


def test_available_metadata_does_not_replace_operational_evidence() -> None:
    original = place()
    enriched = normalize(payload(), original)
    assert isinstance(enriched, PlaceCandidate)
    assert enriched.evidence[:-1] == original.evidence
    assert enriched.price is None and enriched.opening_windows is None
    value = enriched.evidence[-1].value
    assert value["rating"] == 4.2 and value["reviews"] == 50 and value["price"] == "₹₹"
    assert value["open_state"] == "Open now"
    assert "user_reviews" not in value and "photos" not in value


def test_missing_metadata_stays_unknown() -> None:
    value = payload()
    for field in ("rating", "reviews", "price", "open_state", "hours"):
        del value["place_results"][field]
    enriched = normalize(value)
    assert isinstance(enriched, PlaceCandidate)
    assert enriched.evidence[-1].value["hours"] is None
    assert enriched.evidence[-1].value["price"] is None


@pytest.mark.parametrize("value", [None, {}, {"error": "failure"}, {"place_results": None}])
def test_malformed(value: object) -> None:
    assert isinstance(normalize(value), CompilationFailure)


@pytest.mark.parametrize(
    "field,value",
    [
        ("place_id", "different"),
        ("title", "different"),
        ("rating", True),
        ("rating", 6),
        ("rating", "4.2"),
        ("reviews", True),
        ("reviews", -1),
        ("reviews", ["copyrighted text"]),
        ("gps_coordinates", {"latitude": 0.0, "longitude": 0.0}),
    ],
)
def test_wrong_identity_or_unsafe_metadata(field: str, value: object) -> None:
    result = payload()
    result["place_results"][field] = value
    assert isinstance(normalize(result), CompilationFailure)


@pytest.mark.parametrize("kind", ["missing", "conflicting", "expired", "future", "weak"])
def test_linkage_is_positive_fresh_and_unambiguous(kind: str) -> None:
    original = place()
    link = original.evidence[-1]
    if kind == "missing":
        records = original.evidence[:-1]
    elif kind == "conflicting":
        records = original.evidence + (
            link.model_copy(update={"value": {"provider": "SERPAPI", "place_id": "different"}}),
        )
    else:
        changes = {
            "expired": {"observed_at": NOW - timedelta(days=8)},
            "future": {"observed_at": NOW + timedelta(seconds=1)},
            "weak": {"confidence": "LOW"},
        }[kind]
        records = original.evidence[:-1] + (link.model_copy(update=changes),)
    assert isinstance(
        normalize(payload(), original.model_copy(update={"evidence": records})), CompilationFailure
    )


def test_conflicts_are_not_silently_overwritten() -> None:
    enriched = normalize(payload())
    assert isinstance(enriched, PlaceCandidate)
    assert normalize(payload(), enriched) == enriched
    changed = deepcopy(payload())
    changed["place_results"]["price"] = "₹₹₹"
    assert isinstance(normalize(changed, enriched), CompilationFailure)


@pytest.mark.parametrize("kind", ["missing_key", "missing_link", "success", "timeout", "error"])
def test_request_boundary_and_secret_redaction(kind: str) -> None:
    async def run() -> None:
        calls = []

        def handle(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            assert request.url.params["engine"] == "google_maps"
            assert request.url.params["type"] == "place"
            if kind == "timeout":
                raise httpx.ReadTimeout("synthetic-key must not appear", request=request)
            return httpx.Response(503 if kind == "error" else 200, json=payload())

        original = place()
        if kind == "missing_link":
            original = original.model_copy(update={"evidence": original.evidence[:-1]})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            result = await SerpApiEnrichmentProvider(
                client, None if kind == "missing_key" else "synthetic-key"
            ).enrich(original)
        assert len(calls) == (0 if kind in {"missing_key", "missing_link"} else 1)
        if kind == "success":
            assert isinstance(result, EnrichmentResult)
            assert result.binding.status == "MATCH" and result.binding.evidence
            assert result.place.price is None and result.place.opening_windows is None
            assert result.absent_fields == ("price", "opening_window")
            assert all(e.source_ref and e.observed_at for e in result.observations)
        else:
            assert isinstance(result, CompilationFailure)
            assert "synthetic-key" not in result.message

    asyncio.run(run())
