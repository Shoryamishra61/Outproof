from datetime import UTC, datetime, timedelta

import pytest
from ground_rule.hours import is_open_for_interval, windows_from_hours

from tests.test_crosswalk import NOW, observation


@pytest.mark.parametrize(
    "expression,arrival,departure,expected",
    [
        ("Mo-Fr 09:00-17:00", "2026-10-07T10:00", "2026-10-07T11:00", "OPEN"),
        ("Mo-Fr 09:00-17:00", "2026-10-07T16:00", "2026-10-07T17:00", "OPEN"),
        ("Mo-Fr 09:00-17:00", "2026-10-07T16:00", "2026-10-07T17:00:01", "CLOSED"),
        ("Mo-Fr 09:00-17:00", "2026-10-07T08:59", "2026-10-07T09:30", "CLOSED"),
        ("Mo-Fr 09:00-17:00", "2026-10-10T10:00", "2026-10-10T11:00", "CLOSED"),
        ("Mo-Su 09:00-12:00,14:00-18:00", "2026-10-07T14:00", "2026-10-07T18:00", "OPEN"),
        ("Mo-Su 09:00-12:00,14:00-18:00", "2026-10-07T11:00", "2026-10-07T15:00", "CLOSED"),
        ("We 22:00-02:00", "2026-10-07T23:00", "2026-10-08T02:00", "OPEN"),
        ("24/7; We off", "2026-10-07T10:00", "2026-10-07T11:00", "CLOSED"),
        ("by appointment", "2026-10-07T10:00", "2026-10-07T11:00", "UNKNOWN"),
        ("Mo-Su unknown", "2026-10-07T10:00", "2026-10-07T11:00", "UNKNOWN"),
        ("sunrise-sunset", "2026-10-07T10:00", "2026-10-07T11:00", "UNKNOWN"),
        ("24/7; PH off", "2026-10-07T10:00", "2026-10-07T11:00", "UNKNOWN"),
        (None, "2026-10-07T10:00", "2026-10-07T11:00", "UNKNOWN"),
        ("24/7", "2026-10-07T10:00", "2026-10-07T10:00", "UNKNOWN"),
    ],
)
def test_intervals(expression: str | None, arrival: str, departure: str, expected: str) -> None:
    assert (
        is_open_for_interval(
            expression,
            datetime.fromisoformat(arrival + "+05:30"),
            datetime.fromisoformat(departure + "+05:30"),
            "Asia/Kolkata",
        )
        == expected
    )


@pytest.mark.parametrize(
    "expression,expected", [("Su 00:00-03:00", "OPEN"), ("Su 01:00-01:30", "CLOSED")]
)
def test_repeated_local_hour_checks_both_actual_instants(expression: str, expected: str) -> None:
    # 01:15 EDT -> 01:15 EST: elapsed 60 minutes, not a zero-length interval.
    assert (
        is_open_for_interval(
            expression,
            datetime.fromisoformat("2026-11-01T01:15-04:00"),
            datetime.fromisoformat("2026-11-01T01:15-05:00"),
            "America/New_York",
        )
        == expected
    )


def test_spring_gap_and_utc_inputs() -> None:
    assert (
        is_open_for_interval(
            "Su 01:00-04:00",
            datetime(2026, 3, 8, 6, 30, tzinfo=UTC),
            datetime(2026, 3, 8, 7, 30, tzinfo=UTC),
            "America/New_York",
        )
        == "OPEN"
    )


@pytest.mark.parametrize("kind", ["naive", "zone", "reverse", "too_long"])
def test_invalid_context_unknown(kind: str) -> None:
    start, end, zone = NOW, NOW + timedelta(hours=1), "Asia/Kolkata"
    if kind == "naive":
        start = start.replace(tzinfo=None)
    elif kind == "zone":
        zone = "Not/AZone"
    elif kind == "reverse":
        end = start - timedelta(seconds=1)
    else:
        end = start + timedelta(hours=49)
    assert is_open_for_interval("24/7", start, end, zone) == "UNKNOWN"


def test_derived_window_keeps_original_observation_provenance() -> None:
    record = observation("opening_hours", "24/7")
    result = windows_from_hours(record, NOW, NOW + timedelta(minutes=45), "Asia/Kolkata")
    assert result and result[0].evidence[0].observed_at == record.observed_at
    assert result[0].evidence[0].source_ref == record.source_ref
    assert (
        windows_from_hours(
            record.model_copy(update={"value": "nonsense"}),
            NOW,
            NOW + timedelta(minutes=45),
            "Asia/Kolkata",
        )
        is None
    )
