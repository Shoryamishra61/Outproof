from datetime import timedelta

import pytest
from app.enrichment import EnrichmentResult, ProviderEvidence, merge_provider_evidence
from app.identity import ProviderIdentity, bind_identity
from ground_rule.models import Coordinates, Evidence

from tests.test_enrichment import NOW, place


def identity(**changes: object) -> ProviderIdentity:
    return ProviderIdentity.model_validate(
        {
            "provider": "SERPAPI",
            "provider_id": "external-id",
            "name": "synthetic CAFE",
            "coordinates": {"latitude": 13.04, "longitude": 80.23},
            "categories": ["cafe"],
            "observed_at": NOW,
            "source_ref": "external-id",
            **changes,
        }
    )


def observation(field: str, value: object, **changes: object) -> Evidence:
    return Evidence.model_validate(
        {
            "evidence_id": "external:" + field,
            "subject_id": place().place_id,
            "field": field,
            "value": value,
            "source": "SERPAPI",
            "source_ref": "external-id",
            "observed_at": NOW,
            "expires_at": None,
            "confidence": "HIGH",
            **changes,
        }
    )


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("exact", "MATCH"),
        ("ambiguous", "AMBIGUOUS"),
        ("wrong_coords", "NO_MATCH"),
        ("wrong_brand", "NO_MATCH"),
        ("missing_id", "NO_MATCH"),
        ("name_only", "NO_MATCH"),
        ("category", "NO_MATCH"),
        ("duplicate", "AMBIGUOUS"),
    ],
)
def test_crosswalk(kind: str, expected: str) -> None:
    records = (identity(),)
    if kind == "ambiguous":
        records += (identity(provider_id="second-id"),)
    elif kind == "duplicate":
        records += records
    elif kind == "wrong_coords":
        records = (identity(coordinates=Coordinates(latitude=13.1, longitude=80.3)),)
    elif kind == "wrong_brand":
        records = (identity(name="Other brand"),)
    elif kind == "missing_id":
        records = (identity(provider_id=None),)
    elif kind == "name_only":
        records = (identity(coordinates=None),)
    elif kind == "category":
        records = (identity(categories=["mall"]),)
    result = bind_identity(place(), records)
    assert result.status == expected
    assert (result.provider_id is not None) == (expected == "MATCH")
    if expected == "MATCH":
        assert any("coordinates" in signal for signal in result.signals)


@pytest.mark.parametrize("field", ["price", "opening_window"])
@pytest.mark.parametrize("age,status", [(0, "CURRENT"), (25, "STALE"), (-1, "FUTURE")])
def test_field_freshness_and_absence(field: str, age: int, status: str) -> None:
    value = (
        {
            "currency_code": "INR",
            "lower_minor_units": 35000,
            "upper_minor_units": 35000,
            "scope": "PER_PERSON",
            "covers_all_mandatory_costs": True,
        }
        if field == "price"
        else [NOW.isoformat(), (NOW + timedelta(hours=3)).isoformat()]
    )
    record = observation(field, value, observed_at=NOW - timedelta(hours=age))
    result = merge_provider_evidence(
        place(),
        ProviderEvidence(identity=identity(), records=(record,), price_confidence="VERIFIED"),
        as_of=NOW,
    )
    assert result.freshness[0].status == status
    assert result.observations[0] == record
    assert field not in result.absent_fields
    if status != "CURRENT":
        assert result.place == place()


@pytest.mark.parametrize("field", ["price", "opening_window"])
def test_contradictions_retained_without_overwrite(field: str) -> None:
    first = observation(field, ["original"])
    candidate = place().model_copy(update={"evidence": place().evidence + (first,)})
    conflicting = observation(field, ["contradiction"], confidence="LOW")
    result = merge_provider_evidence(
        candidate, ProviderEvidence(identity=identity(), records=(conflicting,)), as_of=NOW
    )
    assert result.contradictions and result.observations == (conflicting,)
    assert result.place == candidate


def test_missing_price_and_hours_explicit() -> None:
    result = merge_provider_evidence(
        place(), ProviderEvidence(identity=identity(), records=()), as_of=NOW
    )
    assert result.absent_fields == ("price", "opening_window")
    assert result.place.price is None and result.place.opening_windows is None


def test_weaker_identical_evidence_does_not_refresh_stronger() -> None:
    first = observation("dietary_options", ["vegetarian"])
    candidate = place().model_copy(update={"evidence": place().evidence + (first,)})
    weak = first.model_copy(update={"observed_at": NOW + timedelta(seconds=1), "confidence": "LOW"})
    result = merge_provider_evidence(
        candidate, ProviderEvidence(identity=identity(), records=(weak,)), as_of=NOW
    )
    assert result.place == candidate and result.observations == (weak,)


def test_address_conflict_prevents_binding() -> None:
    address = observation("address", "First street")
    candidate = place().model_copy(update={"evidence": place().evidence + (address,)})
    assert bind_identity(candidate, (identity(address="Other street"),)).status == "NO_MATCH"


def test_binding_and_field_observation_alignment_cannot_be_forged() -> None:
    result = merge_provider_evidence(
        place(), ProviderEvidence(identity=identity(), records=()), as_of=NOW
    )
    assert result.binding.evidence[0].value["provider_id"] == "external-id"
    for invalid in [
        result.model_copy(
            update={"binding": result.binding.model_copy(update={"candidate_id": "other"})}
        ),
        result.model_copy(
            update={"observations": (observation("price", None, confidence="UNKNOWN"),)}
        ),
    ]:
        with pytest.raises(ValueError):
            EnrichmentResult.model_validate(invalid)
