"""Compute field metrics only from user-recorded aware timestamps and active screen time."""

import argparse
import json
import math
from datetime import UTC, datetime
from pathlib import Path


def field_metrics(record: dict) -> dict[str, float]:
    if not isinstance(record, dict):
        raise ValueError("Field record must be a JSON object of actual measurements")
    instants = []
    for field in ("planning_started_at", "go_at", "outside_started_at", "finished_at"):
        value = record.get(field)
        if not isinstance(value, str):
            raise ValueError(f"Record an actual aware timestamp for {field}")
        instant = datetime.fromisoformat(value)
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError(f"Timezone offset required for {field}")
        instants.append(instant.astimezone(UTC))
    planning, go, outside, finished = instants
    if not planning <= go <= outside < finished:
        raise ValueError("Actual timestamps must follow planning, GO, outside, finish order")
    elapsed = (finished - outside).total_seconds()
    screen = record.get("active_outside_ground_rule_screen_seconds")
    if type(screen) not in {int, float} or not math.isfinite(screen) or not 0 <= screen <= elapsed:
        raise ValueError("Actual outside screen seconds must be known and within outside duration")
    return dict(
        planning_to_go_seconds=(go - planning).total_seconds(),
        time_to_grass_seconds=(outside - planning).total_seconds(),
        actual_outside_duration_seconds=elapsed,
        screen_ratio_percent=100 * screen / elapsed,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(field_metrics(json.loads(args.record.read_text(encoding="utf-8")))))
    except (ValueError, TypeError, OSError) as error:
        parser.error(str(error))
