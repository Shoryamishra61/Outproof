"""Bounded OSM discovery; provider tags never become inferred operational facts."""

import asyncio
import logging
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from math import ceil
from time import monotonic
from typing import Protocol

import httpx
from ground_rule.models import CompilationFailure, Coordinates, Evidence, PlaceCandidate
from pydantic import ValidationError

MAX_DISCOVERY_RADIUS_METERS = 3000


class PlacesProvider(Protocol):
    async def discover(
        self, origin: Coordinates, radius_meters: int
    ) -> tuple[PlaceCandidate, ...] | CompilationFailure: ...


class OverpassAvailability:
    def __init__(self) -> None:
        self.retry_at = 0.0
        self.lock = asyncio.Lock()


def retry_delay_seconds(value: str | None) -> int:
    if value is None:
        return 60
    try:
        if len(value) <= 12:
            return max(60, int(value))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(value)
        if retry_at.tzinfo is not None:
            return max(60, ceil((retry_at - datetime.now(UTC)).total_seconds()))
    except (ValueError, TypeError, OverflowError):
        pass
    return 60


def overpass_query(origin: Coordinates, radius_meters: int) -> str:
    origin = Coordinates.model_validate(origin)
    if type(radius_meters) is not int or not 1 <= radius_meters <= MAX_DISCOVERY_RADIUS_METERS:
        raise ValueError("Discovery radius must be an integer between 1 and 3000 meters")
    around = f"(around:{radius_meters},{origin.latitude},{origin.longitude})"
    return (
        "[out:json][timeout:25][maxsize:8388608];("
        f'nwr["amenity"~"^(restaurant|cafe)$"]{around};'
        f'nwr["leisure"="park"]{around};);out meta center;'
    )


def normalize_overpass(
    payload: object, *, observed_at: datetime
) -> tuple[PlaceCandidate, ...] | CompilationFailure:
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("Observation must be timezone aware")
    if not isinstance(payload, dict) or not isinstance(payload.get("elements"), list):
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Malformed Overpass response"
        )
    if payload.get("remark"):
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Overpass returned an incomplete query"
        )
    places: dict[str, PlaceCandidate] = {}
    try:
        for element in payload["elements"]:
            if (
                not isinstance(element, dict)
                or element.get("type") not in {"node", "way", "relation"}
                or type(element.get("id")) is not int
                or element["id"] <= 0
            ):
                raise ValueError("Invalid OSM identity")
            tags = element.get("tags", {})
            if not isinstance(tags, dict) or any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in tags.items()
            ):
                raise ValueError("Invalid OSM tags")
            category = tags.get("amenity")
            if category not in {"restaurant", "cafe"}:
                category = "park" if tags.get("leisure") == "park" else None
            if category is None or not tags.get("name", "").strip():
                continue
            location = element if element["type"] == "node" else element.get("center")
            if not isinstance(location, dict):
                raise ValueError("Missing OSM coordinates")
            coordinates = Coordinates(latitude=location.get("lat"), longitude=location.get("lon"))
            provider_id = f"{element['type']}/{element['id']}"
            place_id = f"osm:{provider_id}"
            reference = f"https://www.openstreetmap.org/{provider_id}"

            def evidence(
                field: str, value: object, *, subject: str = place_id, ref: str = reference
            ) -> Evidence:
                return Evidence.model_validate(
                    dict(
                        evidence_id=f"{subject}:{field}",
                        subject_id=subject,
                        field=field,
                        value=value,
                        source="OSM",
                        source_ref=ref,
                        observed_at=observed_at,
                        expires_at=None,
                        confidence="MEDIUM" if value is not None else "UNKNOWN",
                    )
                )

            categories = [category]
            # Positive tags are retained; absence never proves no mall/alcohol/chain.
            if tags.get("shop") == "mall" or tags.get("building") == "mall":
                categories.append("mall")
            if tags.get("brand") or tags.get("brand:wikidata"):
                categories.append("chain")
            if tags.get("alcohol") == "yes":
                categories.append("alcohol")
            diet = (
                tuple(
                    kind
                    for kind in ("vegetarian", "vegan")
                    if tags.get(f"diet:{kind}") in {"yes", "only"}
                )
                or None
            )
            place = PlaceCandidate(
                place_id=place_id,
                provider="OSM",
                provider_id=provider_id,
                name=tags["name"],
                coordinates=coordinates,
                categories=tuple(categories),
                opening_windows=None,
                price=None,
                dietary_options=diet,
                evidence=(
                    evidence(
                        "identity", dict(provider="OSM", provider_id=provider_id, name=tags["name"])
                    ),
                    evidence("coordinates", coordinates.model_dump()),
                    evidence("categories", categories),
                    evidence("dietary_options", list(diet) if diet else None),
                    *(
                        evidence(field, tags[field])
                        for field in ("opening_hours", "timezone")
                        if tags.get(field)
                    ),
                    evidence(
                        "osm_metadata",
                        dict(
                            tags=tags,
                            opening_hours=tags.get("opening_hours"),
                            cuisine=tags.get("cuisine"),
                            edited_at=element.get("timestamp"),
                            version=element.get("version"),
                            database_timestamp=payload.get("osm3s", {}).get("timestamp_osm_base"),
                            coordinate_kind="node" if element["type"] == "node" else "bbox_center",
                        ),
                    ),
                ),
            )
            if place_id in places and places[place_id] != place:
                raise ValueError("Conflicting duplicate OSM identity")
            places[place_id] = place
    except (ValueError, TypeError, AttributeError, ValidationError):
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Invalid or conflicting Overpass facts"
        )
    return tuple(places[key] for key in sorted(places)) or CompilationFailure(
        code="NO_GROUNDED_CANDIDATES", message="No named grounded supported POIs in this response"
    )


class OverpassPlacesProvider:
    def __init__(
        self,
        client: httpx.AsyncClient,
        endpoint: str = "https://overpass-api.de/api/interpreter",
        availability: OverpassAvailability | None = None,
    ) -> None:
        self.client = client
        self.endpoint = endpoint
        self.availability = availability or OverpassAvailability()

    async def discover(
        self, origin: Coordinates, radius_meters: int
    ) -> tuple[PlaceCandidate, ...] | CompilationFailure:
        query = overpass_query(origin, radius_meters)
        async with self.availability.lock:
            return await self._discover(query)

    async def _discover(self, query: str) -> tuple[PlaceCandidate, ...] | CompilationFailure:
        retry_seconds = ceil(self.availability.retry_at - monotonic())
        if retry_seconds > 0:
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE",
                message=(
                    f"Map discovery is temporarily unavailable. Retry in {retry_seconds} seconds; "
                    "no nearby place has been verified."
                ),
            )
        for attempt in range(2):
            try:
                response = await self.client.post(
                    self.endpoint,
                    data={"data": query},
                    timeout=40,
                    headers={
                        "User-Agent": "GroundRule/0.1 (https://github.com/Shoryamishra61/Outproof)"
                    },
                    follow_redirects=False,
                )
                response.raise_for_status()
                result = normalize_overpass(response.json(), observed_at=datetime.now(UTC))
                if (
                    isinstance(result, CompilationFailure)
                    and result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"
                ):
                    self.availability.retry_at = monotonic() + 60
                else:
                    self.availability.retry_at = 0
                return result
            except (httpx.HTTPError, ValueError) as error:
                status = (
                    error.response.status_code if isinstance(error, httpx.HTTPStatusError) else None
                )
                logging.getLogger(__name__).warning(
                    "discovery failure kind=%s http_status=%s", type(error).__name__, status
                )
                retry_after = (
                    error.response.headers.get("Retry-After")
                    if isinstance(error, httpx.HTTPStatusError)
                    else None
                )
                transient = isinstance(
                    error, (httpx.ConnectError, httpx.TimeoutException)
                ) or status in {502, 503, 504}
                if attempt == 0 and transient and retry_after is None:
                    await asyncio.sleep(1)
                    continue
                delay = retry_delay_seconds(retry_after)
                self.availability.retry_at = monotonic() + delay
                return CompilationFailure(
                    code="SOURCE_TEMPORARILY_UNAVAILABLE",
                    message=(
                        f"Map discovery is temporarily unavailable. Retry in {delay} seconds; "
                        "no nearby place has been verified."
                    ),
                )
        raise AssertionError("Bounded discovery attempt did not return")
