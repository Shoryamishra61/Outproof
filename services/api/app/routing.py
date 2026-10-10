"""Valhalla pedestrian facts bound to exact requested coordinates and endpoints."""

import hashlib
import json
import math
from datetime import UTC, datetime
from typing import Protocol

import httpx
from ground_rule.models import CompilationFailure, Coordinates, Evidence, RouteFact

from app.reviewed_gardens import distance_meters


def route_shape(encoded: object) -> tuple[Coordinates, ...]:
    """Decode Valhalla's polyline6; malformed or oversized geometry fails closed."""
    if not isinstance(encoded, str) or not 2 <= len(encoded) <= 200_000:
        raise ValueError("Missing or oversized route shape")
    points = []
    position = 0
    latitude = longitude = 0
    while position < len(encoded):
        deltas = []
        for _ in range(2):
            value = shift = 0
            while True:
                if position >= len(encoded) or shift > 30:
                    raise ValueError("Truncated or overflowing route shape")
                byte = ord(encoded[position]) - 63
                position += 1
                if not 0 <= byte <= 63:
                    raise ValueError("Invalid route shape character")
                value |= (byte & 31) << shift
                shift += 5
                if byte < 32:
                    break
            deltas.append(~(value >> 1) if value & 1 else value >> 1)
        latitude += deltas[0]
        longitude += deltas[1]
        points.append(Coordinates(latitude=latitude / 1_000_000, longitude=longitude / 1_000_000))
        if len(points) > 20_000:
            raise ValueError("Oversized route shape")
    if len(points) < 2:
        raise ValueError("Incomplete route shape")
    return tuple(points)


class RoutingProvider(Protocol):
    async def route(
        self, from_id: str, to_id: str, start: Coordinates, end: Coordinates
    ) -> RouteFact | CompilationFailure: ...


def route_request(start: Coordinates, end: Coordinates) -> dict:
    return dict(
        locations=[
            dict(lat=p.latitude, lon=p.longitude, type="break", search_cutoff=100)
            for p in (Coordinates.model_validate(start), Coordinates.model_validate(end))
        ],
        costing="pedestrian",
        units="kilometers",
    )


def normalize_valhalla(
    payload: object,
    *,
    from_id: str,
    to_id: str,
    start: Coordinates,
    end: Coordinates,
    route_id: str,
    endpoint: str,
    observed_at: datetime,
) -> RouteFact | CompilationFailure:
    try:
        if not isinstance(payload, dict):
            raise ValueError("Invalid route response")
        code = payload.get("error_code")
        unreachable = type(code) is int and code in {170, 171, 441, 442}
        if (
            (code is not None and not unreachable)
            or (unreachable and payload.get("trip") is not None)
            or (payload.get("id") is not None and payload["id"] != route_id)
        ):
            raise ValueError("Conflicting provider error or response identity")
        duration = None
        distance = None
        endpoint_offsets = None
        if not unreachable:
            trip = payload["trip"]
            if (
                payload.get("id") != route_id
                or type(trip["status"]) is not int
                or trip["status"] != 0
                or trip["units"] != "kilometers"
                or len(trip["legs"]) != 1
                or len(trip["locations"]) != 2
            ):
                raise ValueError("Route identity, units or leg structure mismatch")
            for location, expected in zip(trip["locations"], (start, end), strict=True):
                actual = Coordinates(latitude=location["lat"], longitude=location["lon"])
                if (
                    abs(actual.latitude - expected.latitude) > 0.000001
                    or abs(actual.longitude - expected.longitude) > 0.000001
                ):
                    raise ValueError("Route coordinates mismatch")
            summary = trip["summary"]
            seconds, kilometers = summary["time"], summary["length"]
            if any(
                type(value) not in {int, float} or not math.isfinite(value) or value < 0
                for value in (seconds, kilometers)
            ):
                raise ValueError("Unknown or unsafe route metric")
            if (seconds == 0 or kilometers == 0) and start != end:
                raise ValueError(
                    "Zero route metric cannot establish travel between distinct points"
                )
            if trip["legs"][0]["summary"] != summary:
                raise ValueError("Trip and single-leg summaries conflict")
            points = route_shape(trip["legs"][0]["shape"])
            endpoint_offsets = [distance_meters(start, points[0]), distance_meters(end, points[-1])]
            # One meter allows coordinate serialization rounding, not an unverified connector.
            if any(offset > 1 for offset in endpoint_offsets):
                return CompilationFailure(
                    code="UNSUPPORTED_CONSTRAINT",
                    message=(
                        "The walking route does not reach the chosen point. "
                        "Move the map pin onto a public footpath and try again."
                    ),
                )
            # Ferries/tolls may introduce unmodeled mandatory costs; never call them free walks.
            for field in ("has_ferry", "has_toll"):
                if type(summary.get(field)) is not bool:
                    raise ValueError("Unknown paid route segments")
                if summary[field]:
                    return CompilationFailure(
                        code="UNSUPPORTED_CONSTRAINT",
                        message="Walking route has a ferry/toll with unsupported mandatory cost",
                    )
            duration = math.ceil(seconds)
            distance = float(kilometers * 1000)
        value = dict(
            from_id=from_id,
            to_id=to_id,
            from_coordinates=start.model_dump(),
            to_coordinates=end.model_dump(),
            reachable=not unreachable,
            duration_seconds=duration,
            distance_meters=distance,
        )
        evidence = Evidence(
            evidence_id=f"{route_id}:walking_route",
            subject_id=route_id,
            field="walking_route",
            value=value,
            source="VALHALLA",
            source_ref=endpoint,
            observed_at=observed_at,
            expires_at=None,
            confidence="MEDIUM",
        )
        metadata = Evidence(
            evidence_id=f"{route_id}:metadata",
            subject_id=route_id,
            field="valhalla_metadata",
            value=dict(
                costing="pedestrian",
                units="kilometers",
                error_code=code,
                response_id=payload.get("id"),
                request=route_request(start, end),
                shape_endpoint_offsets_meters=endpoint_offsets,
                shape_sha256=hashlib.sha256(trip["legs"][0]["shape"].encode()).hexdigest()
                if not unreachable
                else None,
            ),
            source="VALHALLA",
            source_ref=endpoint,
            observed_at=observed_at,
            expires_at=None,
            confidence="MEDIUM",
        )
        return RouteFact(
            route_id=route_id,
            from_id=from_id,
            to_id=to_id,
            reachable=not unreachable,
            duration_seconds=duration,
            distance_meters=distance,
            evidence=(evidence, metadata),
        )
    except (ValueError, TypeError, KeyError, OverflowError):
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Malformed or mismatched Valhalla facts"
        )


class ValhallaRoutingProvider:
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self.client = client
        self.endpoint = base_url.rstrip("/") + "/route"

    async def route(
        self, from_id: str, to_id: str, start: Coordinates, end: Coordinates
    ) -> RouteFact | CompilationFailure:
        request = route_request(start, end)
        identity = json.dumps([from_id, to_id, request, self.endpoint], sort_keys=True)
        route_id = "valhalla:" + hashlib.sha256(identity.encode()).hexdigest()[:24]
        try:
            response = await self.client.post(
                self.endpoint,
                json=request | {"id": route_id},
                timeout=30,
                headers={
                    "X-Client-Id": "ground-rule-development",
                    "User-Agent": "GroundRule/0.1 (bounded development evaluation)",
                },
            )
            # Documented no-path errors use HTTP 400; other statuses remain provider failures.
            if response.status_code not in {200, 400}:
                response.raise_for_status()
            payload = response.json()
            if response.status_code == 400 and (
                not isinstance(payload, dict)
                or type(payload.get("error_code")) is not int
                or payload["error_code"] not in {170, 171, 441, 442}
            ):
                raise ValueError("HTTP error cannot assert reachable route facts")
            return normalize_valhalla(
                payload,
                from_id=from_id,
                to_id=to_id,
                start=start,
                end=end,
                route_id=route_id,
                endpoint=self.endpoint,
                observed_at=datetime.now(UTC),
            )
        except (httpx.HTTPError, ValueError):
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Valhalla request failed"
            )
