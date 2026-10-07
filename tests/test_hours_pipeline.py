import asyncio
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from app.compiler import materialize_hours, valid_candidate_plans
from app.fixtures import FixtureProviders
from ground_rule.models import Evidence
from ground_rule.policy import validate_plan


def provider(kind: str) -> FixtureProviders:
    fixture = FixtureProviders()
    records = []
    for place in fixture.places:
        hours = Evidence(
            evidence_id=place.place_id + ":raw-hours",
            subject_id=place.place_id,
            field="opening_hours",
            value="24/7",
            source="FIXTURE",
            source_ref="FIXTURE raw hours",
            observed_at=fixture.as_of,
            expires_at=None,
            confidence="HIGH",
        )
        zone = hours.model_copy(
            update={
                "evidence_id": place.place_id + ":timezone",
                "field": "timezone",
                "value": "Asia/Kolkata",
            }
        )
        if kind == "unknown":
            hours = hours.model_copy(update={"value": "by appointment"})
        elif kind == "stale":
            hours = hours.model_copy(update={"observed_at": fixture.as_of - timedelta(days=2)})
        elif kind == "weak_timezone":
            zone = zone.model_copy(update={"confidence": "LOW"})
        elif kind == "expired_timezone":
            zone = zone.model_copy(update={"expires_at": fixture.as_of + timedelta(minutes=10)})
        raw = (hours, zone)
        if kind == "contradiction":
            raw += (
                hours.model_copy(
                    update={"evidence_id": hours.evidence_id + ":other", "value": "24/7 off"}
                ),
            )
        records.append(
            place.model_copy(update={"opening_windows": None, "evidence": place.evidence + raw})
        )
    fixture.places = tuple(records)
    return fixture


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("valid", 2),
        ("unknown", 0),
        ("stale", 0),
        ("weak_timezone", 0),
        ("expired_timezone", 0),
        ("contradiction", 0),
    ],
)
def test_raw_hours_pipeline(kind: str, expected: int) -> None:
    fixture = provider(kind)
    result = asyncio.run(
        valid_candidate_plans(
            fixture.controls, fixture, fixture, fixture, as_of=fixture.as_of, allow_fixture=True
        )
    )
    assert isinstance(result, tuple) and len(result) == expected


def test_window_projection_uses_elapsed_time_across_fold() -> None:
    fixture = FixtureProviders(as_of=datetime(2026, 11, 1, 5, 7, tzinfo=UTC))
    built = asyncio.run(
        valid_candidate_plans(
            fixture.controls, fixture, fixture, fixture, as_of=fixture.as_of, allow_fixture=True
        )
    )
    plan = built[0].plan
    stop = plan.stops[0]
    hours = Evidence(
        evidence_id="hours",
        subject_id=stop.place.place_id,
        field="opening_hours",
        value="24/7",
        source="FIXTURE",
        source_ref="FIXTURE hours",
        observed_at=fixture.as_of,
        expires_at=None,
        confidence="HIGH",
    )
    zone = hours.model_copy(
        update={"evidence_id": "tz", "field": "timezone", "value": "America/New_York"}
    )
    stop = stop.model_copy(
        update={
            "arrival_at": stop.arrival_at.astimezone(ZoneInfo("America/New_York")),
            "place": stop.place.model_copy(
                update={"opening_windows": None, "evidence": stop.place.evidence + (hours, zone)}
            ),
        }
    )
    result = materialize_hours(
        plan.model_copy(update={"stops": (stop,)}), as_of=fixture.as_of, allow_fixture=True
    )
    window = result.stops[0].place.opening_windows[0]
    assert window.closes_at - window.opens_at == timedelta(minutes=45)
    assert validate_plan(result, fixture.controls, as_of=fixture.as_of, allow_fixture=True).accepted
