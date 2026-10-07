import asyncio
from copy import deepcopy
from datetime import UTC, datetime

import httpx
import pytest
from app.routing import ValhallaRoutingProvider, normalize_valhalla
from ground_rule.models import CompilationFailure, Coordinates, RouteFact

START = Coordinates(latitude=13.04, longitude=80.23)
END = Coordinates(latitude=13.045, longitude=80.235)


def payload() -> dict:
    summary = dict(time=601.1, length=0.85, has_ferry=False, has_toll=False)
    return dict(
        id="test-route",
        trip=dict(
            status=0,
            units="kilometers",
            summary=summary,
            legs=[dict(summary=deepcopy(summary))],
            locations=[dict(lat=p.latitude, lon=p.longitude) for p in (START, END)],
        ),
    )


def normalize(value: object) -> RouteFact | CompilationFailure:
    return normalize_valhalla(
        value,
        from_id="origin",
        to_id="osm:node/1",
        start=START,
        end=END,
        route_id="test-route",
        endpoint="https://test/route",
        observed_at=datetime(2026, 10, 7, tzinfo=UTC),
    )


def test_rounds_duration_up_and_binds_coordinates() -> None:
    route = normalize(payload())
    assert isinstance(route, RouteFact)
    assert route.duration_seconds == 602 and route.distance_meters == 850.0
    assert route.evidence[0].value["from_coordinates"] == START.model_dump()
    assert route.evidence[0].value["to_coordinates"] == END.model_dump()


@pytest.mark.parametrize("code", [170, 171, 441, 442])
def test_unreachable_is_never_zero(code: int) -> None:
    route = normalize(dict(error_code=code))
    assert isinstance(route, RouteFact) and not route.reachable
    assert route.duration_seconds is None and route.distance_meters is None


@pytest.mark.parametrize("code", [442, 500, "442"])
def test_error_and_success_facts_cannot_conflict(code: object) -> None:
    value = payload()
    value["error_code"] = code
    assert isinstance(normalize(value), CompilationFailure)


@pytest.mark.parametrize("field", ["time", "length"])
def test_zero_cannot_prove_travel_between_distinct_coordinates(field: str) -> None:
    value = payload()
    value["trip"]["summary"][field] = 0
    value["trip"]["legs"][0]["summary"][field] = 0
    assert isinstance(normalize(value), CompilationFailure)


@pytest.mark.parametrize(
    "field,value",
    [
        ("time", None),
        ("length", None),
        ("time", True),
        ("time", -1),
        ("length", "0.85"),
        ("time", float("inf")),
        ("length", float("nan")),
    ],
)
def test_unsafe_metrics(field: str, value: object) -> None:
    value_payload = payload()
    value_payload["trip"]["summary"][field] = value
    assert isinstance(normalize(value_payload), CompilationFailure)


@pytest.mark.parametrize(
    "value", [None, {}, {"trip": None}, {"error_code": 500}, {"error_code": "442"}]
)
def test_malformed(value: object) -> None:
    assert isinstance(normalize(value), CompilationFailure)


@pytest.mark.parametrize(
    "field,value",
    [
        ("units", "miles"),
        ("status", False),
        ("status", 1),
        ("legs", []),
        ("locations", []),
        ("summary", None),
    ],
)
def test_trip_mismatch(field: str, value: object) -> None:
    value_payload = payload()
    value_payload["trip"][field] = value
    assert isinstance(normalize(value_payload), CompilationFailure)


@pytest.mark.parametrize("kind", ["coordinate", "id", "summary"])
def test_wrong_response_binding(kind: str) -> None:
    value_payload = payload()
    if kind == "coordinate":
        value_payload["trip"]["locations"][1]["lat"] += 1
    elif kind == "id":
        value_payload["id"] = "different-route"
    else:
        value_payload["trip"]["legs"][0]["summary"]["time"] += 1
    assert isinstance(normalize(value_payload), CompilationFailure)


@pytest.mark.parametrize("field", ["has_ferry", "has_toll"])
def test_unmodeled_paid_route(field: str) -> None:
    value_payload = payload()
    value_payload["trip"]["summary"][field] = True
    value_payload["trip"]["legs"][0]["summary"][field] = True
    result = normalize(value_payload)
    assert isinstance(result, CompilationFailure) and result.code == "UNSUPPORTED_CONSTRAINT"


@pytest.mark.parametrize("kind", ["success", "unreachable", "timeout", "server", "http_conflict"])
def test_http_boundary(kind: str) -> None:
    async def run() -> None:
        def handle(request: httpx.Request) -> httpx.Response:
            import json

            sent = json.loads(request.content)
            assert sent["costing"] == "pedestrian" and sent["units"] == "kilometers"
            assert request.headers["X-Client-Id"] == "ground-rule-development"
            if kind == "timeout":
                raise httpx.ReadTimeout("synthetic", request=request)
            if kind == "server":
                return httpx.Response(503)
            if kind == "unreachable":
                return httpx.Response(400, json={"error_code": 442})
            value = payload()
            value["id"] = sent["id"]
            return httpx.Response(400 if kind == "http_conflict" else 200, json=value)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            result = await ValhallaRoutingProvider(client, "https://test").route(
                "origin", "osm:node/1", START, END
            )
        if kind in {"timeout", "server", "http_conflict"}:
            assert isinstance(result, CompilationFailure)
        else:
            assert isinstance(result, RouteFact) and result.reachable == (kind == "success")

    asyncio.run(run())
