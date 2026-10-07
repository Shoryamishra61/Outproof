"""Only opt-in live checks contact public endpoints; ordinary pytest is network independent."""

import asyncio
import os
from pathlib import Path

import pytest

from evals.runner.discovery import evaluate
from evals.runner.routing import evaluate as evaluate_routes


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("GROUND_RULE_LIVE_PLACES") != "1", reason="Opt-in live Overpass")
def test_live_overpass(tmp_path) -> None:
    report = asyncio.run(
        evaluate(
            os.getenv("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter"),
            tmp_path / "live-discovery.json",
        )
    )
    assert report["passed"]
    assert report["result"]
    for place in report["result"]:
        assert place["provider"] == "OSM" and place["provider_id"] and place["coordinates"]
        assert {e["field"] for e in place["evidence"]} >= {"identity", "coordinates"}


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("GROUND_RULE_LIVE_ROUTING") != "1", reason="Opt-in live Valhalla")
def test_live_valhalla(tmp_path) -> None:
    report = asyncio.run(
        evaluate_routes(
            Path("evals/reports/discovery-chennai-live-1.json"),
            os.getenv("VALHALLA_BASE_URL", "https://valhalla1.openstreetmap.de"),
            tmp_path / "live-routing.json",
        )
    )
    assert report["passed"]
    assert len(report["routes"]) == 5
    for item in report["routes"]:
        route = item["result"]
        assert route["reachable"] and route["duration_seconds"] > 0
        assert route["distance_meters"] > 0
        assert route["evidence"][0]["source"] == "VALHALLA"
