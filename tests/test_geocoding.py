import asyncio

import httpx
import pytest
from app.geocoding import LocationSearchProvider, normalize_locations
from app.main import create_app
from ground_rule.models import CompilationFailure


def payload(longitude: object = 80.27, latitude: object = 13.08) -> dict:
    return {
        "features": [
            {
                "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "properties": {"name": "Chennai", "city": "Chennai", "country": "India"},
            }
        ]
    }


@pytest.mark.parametrize(
    "longitude,latitude", [(181, 0), (0, 91), (True, 1), ("80", 13), (float("nan"), 0)]
)
def test_invalid_search_coordinates_are_not_accepted(longitude: object, latitude: object) -> None:
    with pytest.raises(ValueError):
        normalize_locations(payload(longitude, latitude))


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        {"features": None},
        {"features": [None]},
        {"features": [{"geometry": {}, "properties": []}]},
    ],
)
def test_malformed_search_results_fail_closed(value: object) -> None:
    with pytest.raises((ValueError, KeyError)):
        normalize_locations(value)


def test_search_normalizes_point_and_does_not_invent_venue_facts() -> None:
    results = normalize_locations(payload())
    assert results.results[0].label == "Chennai, India"
    assert results.results[0].coordinates.latitude == 13.08
    assert set(results.results[0].model_dump()) == {"label", "coordinates"}
    assert normalize_locations({"features": []}).results == []


def test_duplicate_provider_points_collapse_and_distinct_matches_remain_selectable() -> None:
    first = payload()["features"][0]
    second = payload(latitude=13.09)["features"][0]
    results = normalize_locations({"features": [first, second, second, second]})
    assert [result.label for result in results.results] == [
        "Chennai, India — map match 1",
        "Chennai, India — map match 2",
    ]
    assert [result.coordinates.latitude for result in results.results] == [13.08, 13.09]


def test_search_is_identified_cached_and_globally_rate_limited() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.url.params["limit"] == "5"
        assert "GroundRule" in request.headers["User-Agent"]
        return httpx.Response(200, json=payload())

    async def run() -> None:
        provider = LocationSearchProvider("https://search.example/api/")
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            status, result = await provider.search("Chennai", client)
            assert status == 200 and not isinstance(result, CompilationFailure)
            assert (await provider.search("CHENNAI", client))[0] == 200
            assert len(requests) == 1
            assert (await provider.search("London", client))[0] == 429
            assert all(len(key) == 64 and "chennai" not in key for key in provider.cache)

    asyncio.run(run())


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(302, headers={"Location": "https://other.example"}),
        httpx.Response(503),
        httpx.Response(200, json={"features": [None]}),
        httpx.Response(200, content=b"x" * 1_000_001),
    ],
)
def test_provider_failure_and_redirect_never_select_a_point(response: httpx.Response) -> None:
    async def run() -> None:
        provider = LocationSearchProvider("https://search.example/api/")
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as client:
            status, result = await provider.search("Chennai", client)
            assert status == 503 and isinstance(result, CompilationFailure)
            assert not provider.cache

    asyncio.run(run())


def test_search_body_and_query_are_bounded() -> None:
    async def run() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
        ) as client:
            for value in [
                {"query": " "},
                {"query": "a"},
                {"query": "x" * 161},
                {"query": 1},
                {"query": "Chennai", "url": "https://untrusted.example"},
            ]:
                assert (await client.post("/v1/locations/search", json=value)).status_code == 422
            assert (
                await client.post("/v1/locations/search", content=b"x" * 2049)
            ).status_code == 422

    asyncio.run(run())


def test_api_search_returns_normalized_points_without_logging_query(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    async def search(self: LocationSearchProvider, query: str, client: httpx.AsyncClient) -> tuple:
        assert query == "PRIVATE-TEST-AREA"
        return 200, normalize_locations(payload())

    monkeypatch.setattr(LocationSearchProvider, "search", search)

    async def run() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/locations/search", json={"query": "PRIVATE-TEST-AREA"}
            )
            assert response.status_code == 200
            assert response.json()["results"][0]["coordinates"]["latitude"] == 13.08

    asyncio.run(run())
    assert "PRIVATE-TEST-AREA" not in caplog.text


def test_timed_out_geocoder_fails_closed() -> None:
    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Controlled timeout", request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(timeout)) as client:
            status, result = await LocationSearchProvider("https://search.example").search(
                "London", client
            )
            assert status == 503 and isinstance(result, CompilationFailure)

    asyncio.run(run())
