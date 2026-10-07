import asyncio
from copy import deepcopy
from datetime import UTC, datetime

import httpx
import pytest
from app.places import OverpassPlacesProvider, normalize_overpass, overpass_query
from ground_rule.models import CompilationFailure, Coordinates

NOW = datetime(2026, 10, 7, tzinfo=UTC)
ORIGIN = Coordinates(latitude=13.0418, longitude=80.2341)


def response(**tags: str) -> dict:
    return {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 13.04,
                "lon": 80.23,
                "tags": {"name": "SYNTHETIC venue", "amenity": "restaurant", **tags},
            }
        ]
    }


@pytest.mark.parametrize(
    "tags,category",
    [
        ({}, "restaurant"),
        ({"amenity": "cafe"}, "cafe"),
        ({"amenity": "", "leisure": "park"}, "park"),
    ],
)
def test_categories_and_grounded_identity(tags: dict, category: str) -> None:
    result = normalize_overpass(response(**tags), observed_at=NOW)
    assert not isinstance(result, CompilationFailure)
    assert result[0].categories == (category,)
    assert result[0].provider_id == "node/1" and result[0].coordinates == Coordinates(
        latitude=13.04, longitude=80.23
    )
    assert {e.field for e in result[0].evidence} >= {"identity", "coordinates"}


def test_unknowns_and_raw_metadata() -> None:
    result = normalize_overpass(
        response(opening_hours="Mo-Fr 10:00-20:00", cuisine="indian"), observed_at=NOW
    )
    assert not isinstance(result, CompilationFailure)
    place = result[0]
    assert place.opening_windows is None and place.price is None and place.dietary_options is None
    assert place.evidence[-1].value["opening_hours"] == "Mo-Fr 10:00-20:00"
    assert place.evidence[-1].value["cuisine"] == "indian"
    assert not any(e.field == "excluded_categories" for e in place.evidence)


def test_positive_diet_is_not_cuisine_guess() -> None:
    result = normalize_overpass(response(**{"diet:vegetarian": "yes"}), observed_at=NOW)
    assert not isinstance(result, CompilationFailure)
    assert result[0].dietary_options == ("vegetarian",)


def test_duplicate_and_conflicting_duplicate() -> None:
    payload = response()
    payload["elements"] *= 2
    result = normalize_overpass(payload, observed_at=NOW)
    assert not isinstance(result, CompilationFailure) and len(result) == 1
    payload["elements"][1] = deepcopy(payload["elements"][1])
    payload["elements"][1]["lat"] = 14.0
    assert isinstance(normalize_overpass(payload, observed_at=NOW), CompilationFailure)


@pytest.mark.parametrize(
    "payload",
    [None, {}, {"elements": None}, {"elements": [None]}, {"elements": [], "remark": "timeout"}],
)
def test_malformed_response(payload: object) -> None:
    result = normalize_overpass(payload, observed_at=NOW)
    assert (
        isinstance(result, CompilationFailure) and result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("lat", None),
        ("lat", "13.0"),
        ("lat", True),
        ("lat", 95.0),
        ("lon", float("nan")),
        ("id", True),
        ("tags", []),
    ],
)
def test_invalid_element(field: str, value: object) -> None:
    payload = response()
    payload["elements"][0][field] = value
    assert isinstance(normalize_overpass(payload, observed_at=NOW), CompilationFailure)


@pytest.mark.parametrize("payload", [{"elements": []}, response(amenity="bank"), response(name="")])
def test_empty_or_unsupported(payload: dict) -> None:
    result = normalize_overpass(payload, observed_at=NOW)
    assert isinstance(result, CompilationFailure) and result.code == "NO_GROUNDED_CANDIDATES"


def test_missing_hours_cuisine_and_way_center() -> None:
    payload = response()
    element = payload["elements"][0]
    element.update(type="way", center={"lat": element.pop("lat"), "lon": element.pop("lon")})
    result = normalize_overpass(payload, observed_at=NOW)
    assert not isinstance(result, CompilationFailure)
    assert result[0].evidence[-1].value["coordinate_kind"] == "bbox_center"
    assert result[0].evidence[-1].value["opening_hours"] is None
    assert result[0].evidence[-1].value["cuisine"] is None
    del element["center"]
    assert isinstance(normalize_overpass(payload, observed_at=NOW), CompilationFailure)


@pytest.mark.parametrize("radius", [0, 3001, True, "1000"])
def test_query_limits(radius: object) -> None:
    with pytest.raises(ValueError):
        overpass_query(ORIGIN, radius)


@pytest.mark.parametrize("failure", ["timeout", "http", "json"])
def test_request_failure(failure: str) -> None:
    async def run() -> None:
        def handle(request: httpx.Request) -> httpx.Response:
            if failure == "timeout":
                raise httpx.ReadTimeout("synthetic timeout", request=request)
            return httpx.Response(503 if failure == "http" else 200, text="invalid")

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            result = await OverpassPlacesProvider(client).discover(ORIGIN, 1000)
        assert isinstance(result, CompilationFailure)
        assert result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"

    asyncio.run(run())


def test_provider_success_is_normalized() -> None:
    async def run() -> None:
        def handle(request: httpx.Request) -> httpx.Response:
            assert b"around%3A1000" in request.content
            return httpx.Response(200, json=response())

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            assert not isinstance(
                await OverpassPlacesProvider(client).discover(ORIGIN, 1000), CompilationFailure
            )

    asyncio.run(run())
