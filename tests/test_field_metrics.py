import pytest

from scripts.field_metrics import field_metrics


def record() -> dict:
    return dict(
        planning_started_at="2026-10-06T10:00:00+05:30",
        go_at="2026-10-06T10:00:20+05:30",
        outside_started_at="2026-10-06T10:01:00+05:30",
        finished_at="2026-10-06T11:01:00+05:30",
        active_outside_ground_rule_screen_seconds=60,
    )


def test_synthetic_measurement_arithmetic() -> None:
    assert field_metrics(record()) == dict(
        planning_to_go_seconds=20.0,
        time_to_grass_seconds=60.0,
        actual_outside_duration_seconds=3600.0,
        screen_ratio_percent=100 / 60,
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("go_at", None),
        ("go_at", "2026-10-06T10:00:20"),
        ("go_at", "2026-10-06T09:00:20+05:30"),
        ("finished_at", "2026-10-06T10:01:00+05:30"),
        ("active_outside_ground_rule_screen_seconds", None),
        ("active_outside_ground_rule_screen_seconds", True),
        ("active_outside_ground_rule_screen_seconds", -1),
        ("active_outside_ground_rule_screen_seconds", 3601),
        ("active_outside_ground_rule_screen_seconds", float("nan")),
    ],
)
def test_blank_invalid_or_impossible_record(field: str, value: object) -> None:
    with pytest.raises(ValueError):
        field_metrics(record() | {field: value})


def test_synthetic_repeated_clock_hour_uses_instants() -> None:
    result = field_metrics(
        dict(
            planning_started_at="2026-11-01T01:50:00-04:00",
            go_at="2026-11-01T01:51:00-04:00",
            outside_started_at="2026-11-01T01:55:00-04:00",
            finished_at="2026-11-01T01:20:00-05:00",
            active_outside_ground_rule_screen_seconds=15,
        )
    )
    assert result["actual_outside_duration_seconds"] == 1500
    assert result["screen_ratio_percent"] == 1.0


def test_non_object_is_not_a_field_record() -> None:
    with pytest.raises(ValueError):
        field_metrics([])
