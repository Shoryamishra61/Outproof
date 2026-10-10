import asyncio
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from app.live import LivePlacesProvider
from app.reviewed_gardens import GARDENS, distance_meters, normalize_garden
from ground_rule.hours import windows_from_hours
from ground_rule.models import CompilationFailure


def source_example(index=0):
    garden = GARDENS[index]
    lat, lon = garden.coordinates.latitude, garden.coordinates.longitude
    points = [
        (lat - 0.001, lon - 0.001),
        (lat - 0.001, lon + 0.001),
        (lat + 0.001, lon + 0.001),
        (lat + 0.001, lon - 0.001),
    ]
    park = {
        "elements": [
            *({"type": "node", "id": i, "lat": a, "lon": b} for i, (a, b) in enumerate(points, 1)),
            {
                "type": "way",
                "id": garden.park_way,
                "nodes": [1, 2, 3, 4, 1],
                "tags": {"name": garden.name, "leisure": "park"},
            },
        ]
    }
    path = {
        "elements": [
            {"type": "node", "id": 99, "lat": lat + 0.002, "lon": lon},
            {"type": "node", "id": garden.access_node, "lat": lat, "lon": lon},
            {
                "type": "way",
                "id": garden.path_way,
                "nodes": [99, garden.access_node],
                "tags": {"highway": "footway"},
            },
        ]
    }
    html = (
        f"<h1>{garden.title}</h1>GENERAL INFORMATION Address : {garden.sector}, Chandigarh "
        "Open : Daily Timings : 05:00 AM to 09:00 PM Entry Fee : Not Applicable "
        "Download Tourism"
    )
    return garden, park, path, html


@pytest.mark.parametrize("index", range(len(GARDENS)))
def test_official_fee_hours_are_identity_bound_and_scope_limited(index):
    garden, park, path, html = source_example(index)
    observed = datetime.now(UTC)
    place = normalize_garden(garden, park, path, html, observed)
    assert place.price.upper.minor_units == 0 and place.price.upper.currency_code == "INR"
    assert place.coordinates == garden.coordinates
    assert all(e.observed_at == observed for e in place.evidence)
    assert "not a physically checked gate" in next(
        e.value for e in place.evidence if e.field == "visit_scope"
    )
    assert distance_meters(place.coordinates, garden.coordinates) == 0


@pytest.mark.parametrize(
    "mutation",
    [
        "title",
        "fee",
        "hours",
        "sector",
        "hidden",
        "script",
        "duplicate",
        "private",
        "wrong_way",
        "wrong_path",
        "moved_node",
        "outside",
        "missing_node",
    ],
)
def test_missing_changed_conflicting_or_hidden_sources_fail_closed(mutation):
    garden, park, path, html = source_example()
    if mutation in {"title", "fee", "hours", "sector"}:
        html = html.replace(
            {
                "title": garden.title,
                "fee": "Not Applicable",
                "hours": "05:00",
                "sector": garden.sector,
            }[mutation],
            "Changed",
        )
    elif mutation in {"hidden", "script"}:
        html = (
            "<div hidden>" + html + "</div>"
            if mutation == "hidden"
            else "<script>" + html + "</script>"
        )
    elif mutation == "duplicate":
        html = html.replace("Download Tourism", "Entry Fee : INR 100 Download Tourism")
    elif mutation == "private":
        path["elements"][-1]["tags"]["access"] = "private"
    elif mutation == "wrong_way":
        park["elements"][-1]["id"] = 7
    elif mutation == "wrong_path":
        path["elements"][-1]["id"] = 7
    elif mutation == "moved_node":
        path["elements"][1]["lat"] += 0.01
    elif mutation == "outside":
        for point in park["elements"][:-1]:
            point["lat"] += 1
    else:
        path["elements"][-1]["nodes"] = []
    with pytest.raises((ValueError, KeyError)):
        normalize_garden(garden, park, path, html, datetime.now(UTC))


def test_full_dwell_and_closing_time_are_enforced_without_new_windows():
    garden, park, path, html = source_example()
    observed = datetime(2026, 10, 10, 4, tzinfo=UTC)
    place = normalize_garden(garden, park, path, html, observed)
    hours = next(e for e in place.evidence if e.field == "opening_hours")
    before_close = datetime(2026, 10, 10, 15, 20, tzinfo=UTC)
    assert windows_from_hours(
        hours, before_close, before_close + timedelta(minutes=9), "Asia/Kolkata"
    )
    assert (
        windows_from_hours(
            hours, before_close, before_close + timedelta(minutes=30), "Asia/Kolkata"
        )
        == ()
    )


@pytest.mark.parametrize("status", [301, 403, 429, 503])
def test_reviewed_source_errors_do_not_fall_back_to_unverified_facts(status, caplog):
    calls = []

    def handle(request):
        calls.append(str(request.url))
        return httpx.Response(status, headers={"Location": "http://169.254.169.254/"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            result = await LivePlacesProvider(client, "https://example.test").discover(
                GARDENS[0].coordinates, 1000
            )
        assert isinstance(result, CompilationFailure)
        assert result.code == "SOURCE_TEMPORARILY_UNAVAILABLE" and len(calls) == 1

    asyncio.run(run())
    assert "source_kind=osm_park" in caplog.text
    assert f"http_status={status}" in caplog.text
    assert "169.254" not in caplog.text and "Authorization" not in caplog.text


@pytest.mark.parametrize(
    "mutation", [None, "stale", "future", "wrong_url", "bad_html", "fee", "denied"]
)
def test_relay_preserves_source_identity_freshness_and_claim_checks(monkeypatch, mutation):
    from app.reviewed_gardens import fetch_garden

    garden, park, path, html = source_example()
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://relay.example")
    monkeypatch.setenv("GEMMA_API_KEY", "synthetic-key")
    calls = []

    def handle(request):
        calls.append(request)
        if request.url.host == "www.openstreetmap.org":
            assert "authorization" not in request.headers
            return httpx.Response(
                200, json=park if str(garden.park_way) in request.url.path else path
            )
        assert str(request.url) == f"https://relay.example/sources/chandigarh/{garden.park_way}"
        assert request.headers["authorization"] == "Bearer synthetic-key"
        if mutation == "denied":
            return httpx.Response(401)
        observed = datetime.now(UTC) + timedelta(
            seconds={"stale": -31, "future": 10}.get(mutation, 0)
        )
        return httpx.Response(
            200,
            json={
                "source_url": "https://wrong.example" if mutation == "wrong_url" else garden.url,
                "observed_at": observed.isoformat(),
                "html": 12
                if mutation == "bad_html"
                else html.replace("Not Applicable", "INR 100")
                if mutation == "fee"
                else html,
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            if mutation is None:
                place = await fetch_garden(client, garden)
                assert place.price.upper.minor_units == 0
                lineage = next(e.value for e in place.evidence if e.field == "parse_lineage")
                assert lineage["official_retrieval_transport"] == "authenticated_laptop_relay"
            else:
                with pytest.raises((ValueError, httpx.HTTPStatusError)):
                    await fetch_garden(client, garden)
        assert len(calls) == 3

    asyncio.run(run())
