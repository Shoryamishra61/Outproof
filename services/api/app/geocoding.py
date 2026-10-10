"""Origin lookup only; a search result never establishes a venue's outing facts."""

import asyncio
import hashlib
import json
from time import monotonic
from urllib.parse import urlsplit

import httpx
from ground_rule.models import CompilationFailure, Contract, Coordinates
from pydantic import Field, ValidationError


class LocationResult(Contract):
    label: str = Field(min_length=1, max_length=280)
    coordinates: Coordinates


class LocationResults(Contract):
    results: list[LocationResult] = Field(max_length=5)
    attribution: str = "OpenStreetMap contributors / Photon"


def normalize_locations(payload: object) -> LocationResults:
    if not isinstance(payload, dict) or not isinstance(payload.get("features"), list):
        raise ValueError("Invalid geocoder response")
    results = []
    for feature in payload["features"][:5]:
        if (
            not isinstance(feature, dict)
            or not isinstance(feature.get("geometry"), dict)
            or not isinstance(feature.get("properties"), dict)
        ):
            raise ValueError("Invalid location feature")
        point = feature["geometry"]
        coordinates = point["coordinates"]
        if point["type"] != "Point" or not isinstance(coordinates, list) or len(coordinates) != 2:
            raise ValueError("Invalid location geometry")
        if any(type(v) not in (int, float) for v in coordinates):
            raise ValueError("Invalid location coordinates")
        parts = []
        for key in ("name", "street", "district", "county", "city", "state", "country"):
            value = feature["properties"].get(key)
            if value is not None and (not isinstance(value, str) or len(value) > 280):
                raise ValueError("Invalid location label")
            if value and value not in parts:
                parts.append(value)
        result = LocationResult(
            label=", ".join(parts)[:280],
            coordinates=Coordinates(latitude=coordinates[1], longitude=coordinates[0]),
        )
        if result not in results:
            results.append(result)
    labels = [result.label for result in results]
    for index, result in enumerate(results):
        if labels.count(result.label) > 1:
            match = labels[: index + 1].count(result.label)
            results[index] = result.model_copy(
                update={"label": f"{result.label[:250]} — map match {match}"}
            )
    return LocationResults(results=results)


class LocationSearchProvider:
    def __init__(self, endpoint: str) -> None:
        url = urlsplit(endpoint)
        if (
            url.scheme != "https"
            or not url.netloc
            or url.username
            or url.password
            or url.query
            or url.fragment
        ):
            raise ValueError("Geocoder must be a configured HTTPS endpoint")
        self.endpoint = endpoint
        self.lock = asyncio.Lock()
        self.next_request_at = 0.0
        # shortcut: one production process; use a shared quota before scaling instances.
        self.cache: dict[str, tuple[float, LocationResults]] = {}

    async def search(
        self, query: str, client: httpx.AsyncClient
    ) -> tuple[int, LocationResults | CompilationFailure]:
        key = hashlib.sha256(query.casefold().encode()).hexdigest()
        now = monotonic()
        self.cache = {k: v for k, v in self.cache.items() if v[0] > now}
        if key in self.cache:
            return 200, self.cache[key][1]
        if self.lock.locked() or now < self.next_request_at:
            return 429, CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE",
                message="Location search is busy. Wait a moment and search again.",
            )
        async with self.lock:
            self.next_request_at = monotonic() + 1
            try:
                async with asyncio.timeout(12):
                    async with client.stream(
                        "GET",
                        self.endpoint,
                        params={"q": query, "limit": 5, "lang": "en"},
                        headers={
                            "User-Agent": "GroundRule/0.1 (+https://github.com/Shoryamishra61/Outproof)"
                        },
                        timeout=10,
                        follow_redirects=False,
                    ) as response:
                        if response.status_code != 200:
                            raise ValueError("Geocoder unavailable")
                        body = bytearray()
                        async for chunk in response.aiter_bytes():
                            body.extend(chunk)
                            if len(body) > 1_000_000:
                                raise ValueError("Oversized geocoder response")
                    result = normalize_locations(json.loads(body))
                if len(self.cache) >= 128:
                    self.cache.pop(next(iter(self.cache)))
                self.cache[key] = (monotonic() + 3600, result)
                return 200, result
            except (
                httpx.HTTPError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                ValidationError,
            ):
                return 503, CompilationFailure(
                    code="SOURCE_TEMPORARILY_UNAVAILABLE",
                    message="Place search is unavailable. Try again or choose on the map.",
                )
