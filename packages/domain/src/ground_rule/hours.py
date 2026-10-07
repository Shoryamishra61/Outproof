"""OSM hours evaluation through opening-hours-py; no inferred timezone or open-now proof."""

import re
from datetime import UTC, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from opening_hours import OpeningHours, ParserError, State
from pydantic import AwareDatetime, TypeAdapter

from ground_rule.models import Evidence, OpeningWindow


def is_open_for_interval(
    expression: str | None, arrival_time: datetime, departure_time: datetime, timezone: str
) -> Literal["OPEN", "CLOSED", "UNKNOWN"]:
    """Check [arrival, departure) across actual UTC instants, including repeated local hours.

    Minute-resolution OSM schedules are evaluated at every UTC minute boundary.
    This avoids ambiguous wall-clock interval endpoints in timezone-aware iterators.
    Solar/holiday rules require additional location/calendar context and stay unknown.
    """
    try:
        arrival = TypeAdapter(AwareDatetime).validate_python(arrival_time).astimezone(UTC)
        departure = TypeAdapter(AwareDatetime).validate_python(departure_time).astimezone(UTC)
        zone = ZoneInfo(timezone)
        if (
            not expression
            or len(expression) > 2000
            or arrival.year < 1970
            or not timedelta(0) < departure - arrival <= timedelta(hours=48)
            or re.search(r"\b(?:PH|SH|easter|sunrise|sunset|dawn|dusk)\b", expression)
        ):
            return "UNKNOWN"
        hours = OpeningHours(expression, auto_country=False, auto_timezone=False)
        if hours.warnings:
            return "UNKNOWN"
        cursor = arrival
        states = set()
        while cursor < departure:
            local = cursor.astimezone(zone)
            if local.utcoffset().total_seconds() % 60:
                return "UNKNOWN"
            # Evaluate the local clock without asking the library to disambiguate fold endpoints.
            states.add(hours.state(local.replace(tzinfo=None))[0])
            cursor = cursor.replace(second=0, microsecond=0) + timedelta(minutes=1)
        if State.UNKNOWN in states:
            return "UNKNOWN"
        return "OPEN" if states == {State.OPEN} else "CLOSED"
    except (ValueError, TypeError, SyntaxError, ParserError, ZoneInfoNotFoundError, OverflowError):
        return "UNKNOWN"


def windows_from_hours(
    record: Evidence, arrival: datetime, departure: datetime, timezone: str
) -> tuple[OpeningWindow, ...] | None:
    """Derive only the requested usable interval; preserve source observation time and reference."""
    record = Evidence.model_validate(record)
    if record.field != "opening_hours" or not isinstance(record.value, str):
        return None
    state = is_open_for_interval(record.value, arrival, departure, timezone)
    if state == "UNKNOWN":
        return None
    if state == "CLOSED":
        return ()
    arrival, departure = arrival.astimezone(UTC), departure.astimezone(UTC)
    derived = Evidence.model_validate(
        record.model_copy(
            update={
                "evidence_id": (
                    f"{record.evidence_id}:{arrival.isoformat()}:{departure.isoformat()}"
                ),
                "field": "opening_window",
                "value": [arrival.isoformat(), departure.isoformat()],
            }
        )
    )
    return (OpeningWindow(opens_at=arrival, closes_at=departure, evidence=(derived,)),)
