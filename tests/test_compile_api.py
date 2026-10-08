import asyncio
import json

import httpx
import pytest
from app.main import create_app, fixture_configuration_enabled
from ground_rule.models import CompilationFailure, CompiledPlan

from tests.test_ranker import StubModel, accepted


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("disabled", 503),
        ("success", 200),
        ("empty", 409),
        ("parser", 422),
        ("timeout", 503),
        ("selection", 422),
        ("live", 422),
        ("malformed", 422),
    ],
)
def test_api(kind: str, expected: int, monkeypatch: pytest.MonkeyPatch) -> None:
    fixture, valid = accepted()
    model = StubModel(
        json.dumps(
            {
                "selected_plan_id": valid[0].plan.plan_id,
                "reason": "Selected for your soft preferences.",
            }
        )
    )
    payload = {
        "mode": "FIXTURE",
        "controls": fixture.controls.model_dump(mode="json"),
        "free_text": "",
    }
    if kind == "empty":
        fixture.places = ()
    elif kind == "parser":
        payload["free_text"] = "vegetarian"
        monkeypatch.setattr(
            "app.main.parse_constraints",
            lambda *a, **k: CompilationFailure(
                code="MODEL_OUTPUT_INVALID", message="Malformed parser output"
            ),
        )
    elif kind == "timeout":

        async def broken(place: object) -> object:
            raise TimeoutError("provider timeout")

        fixture.enrich = broken
    elif kind == "selection":
        model.content = (
            '{"selected_plan_id":"invalid","reason":"Selected for your soft preferences."}'
        )
    elif kind == "live":
        payload["mode"] = "LIVE"
    elif kind == "malformed":
        payload["options"] = []
    app = create_app(
        fixture_enabled=kind != "disabled",
        providers=fixture,
        model=model,
        clock=lambda: fixture.as_of,
    )

    async def run() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            health = await client.get("/v1/health")
            assert health.json()["compilation_available"] is False
            response = await client.post("/v1/plans/compile", json=payload)
        assert response.status_code == expected
        if expected == 200:
            result = CompiledPlan.model_validate(response.json())
            assert (
                result.mode == "FIXTURE" and result.proof.validation.plan_id == result.plan.plan_id
            )
            assert "options" not in response.json() and "plans" not in response.json()
        else:
            CompilationFailure.model_validate(response.json())
        if kind in {"disabled", "empty", "parser", "timeout", "live", "malformed"}:
            assert not model.calls

    asyncio.run(run())


@pytest.mark.parametrize(
    "enabled,fixture,development",
    [
        (False, False, False),
        (False, False, True),
        (False, True, False),
        (False, True, True),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ],
)
def test_fixture_requires_all_three_settings(
    enabled: bool, fixture: bool, development: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GROUND_RULE_COMPILATION_ENABLED", str(enabled))
    monkeypatch.setenv("GROUND_RULE_FIXTURE_MODE", str(fixture))
    monkeypatch.setenv("GROUND_RULE_ENV", "development" if development else "production")
    assert fixture_configuration_enabled() == (enabled and fixture and development)


@pytest.mark.parametrize(
    "enabled,live,development",
    [
        (False, False, False),
        (False, False, True),
        (False, True, False),
        (False, True, True),
        (True, False, False),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ],
)
def test_live_requires_all_three_settings(
    enabled: bool, live: bool, development: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.main import live_configuration_enabled

    monkeypatch.setenv("GROUND_RULE_COMPILATION_ENABLED", str(enabled))
    monkeypatch.setenv("GROUND_RULE_LIVE_MODE", str(live))
    monkeypatch.setenv("GROUND_RULE_ENV", "development" if development else "production")
    monkeypatch.delenv("GROUND_RULE_FIXTURE_MODE", raising=False)
    assert live_configuration_enabled() == (enabled and live)


def test_live_compile_rejects_unsupported_park_pack() -> None:
    from datetime import UTC, datetime, timedelta

    from ground_rule.models import (
        ConstraintSet,
        Coordinates,
        Evidence,
        HardConstraint,
        PlaceCandidate,
        RouteFact,
    )

    now = datetime.now(UTC)
    departure = now + timedelta(minutes=5)
    origin = Coordinates(latitude=13.088, longitude=80.221)
    park_coords = Coordinates(latitude=13.0866141, longitude=80.2142635)
    place_id = "osm:way/24240071"

    ev_identity = Evidence(
        evidence_id=f"{place_id}:identity",
        subject_id=place_id,
        field="identity",
        value={"provider": "OSM", "provider_id": "way/24240071", "name": "Anna Nagar Tower Park"},
        source="OSM",
        source_ref="https://www.openstreetmap.org/way/24240071",
        observed_at=now,
        expires_at=None,
        confidence="MEDIUM",
    )
    ev_coords = Evidence(
        evidence_id=f"{place_id}:coordinates",
        subject_id=place_id,
        field="coordinates",
        value=park_coords.model_dump(),
        source="OSM",
        source_ref="https://www.openstreetmap.org/way/24240071",
        observed_at=now,
        expires_at=None,
        confidence="MEDIUM",
    )
    ev_cat = Evidence(
        evidence_id=f"{place_id}:categories",
        subject_id=place_id,
        field="categories",
        value=["park"],
        source="OSM",
        source_ref="https://www.openstreetmap.org/way/24240071",
        observed_at=now,
        expires_at=None,
        confidence="MEDIUM",
    )
    place = PlaceCandidate(
        place_id=place_id,
        provider="OSM",
        provider_id="way/24240071",
        name="Anna Nagar Tower Park",
        coordinates=park_coords,
        categories=("park",),
        opening_windows=None,
        price=None,
        dietary_options=None,
        evidence=(ev_identity, ev_coords, ev_cat),
    )

    r1_val = {
        "from_id": "origin",
        "to_id": place_id,
        "from_coordinates": origin.model_dump(),
        "to_coordinates": park_coords.model_dump(),
        "reachable": True,
        "duration_seconds": 911,
        "distance_meters": 1283.0,
    }
    r1_ev = Evidence(
        evidence_id="r1:walking_route",
        subject_id="r1",
        field="walking_route",
        value=r1_val,
        source="VALHALLA",
        source_ref="https://valhalla1.openstreetmap.de",
        observed_at=now,
        expires_at=None,
        confidence="MEDIUM",
    )
    r1 = RouteFact(
        route_id="r1",
        from_id="origin",
        to_id=place_id,
        reachable=True,
        duration_seconds=911,
        distance_meters=1283.0,
        evidence=(r1_ev,),
    )

    r2_val = {
        "from_id": place_id,
        "to_id": "origin",
        "from_coordinates": park_coords.model_dump(),
        "to_coordinates": origin.model_dump(),
        "reachable": True,
        "duration_seconds": 939,
        "distance_meters": 1285.0,
    }
    r2_ev = Evidence(
        evidence_id="r2:walking_route",
        subject_id="r2",
        field="walking_route",
        value=r2_val,
        source="VALHALLA",
        source_ref="https://valhalla1.openstreetmap.de",
        observed_at=now,
        expires_at=None,
        confidence="MEDIUM",
    )
    r2 = RouteFact(
        route_id="r2",
        from_id=place_id,
        to_id="origin",
        reachable=True,
        duration_seconds=939,
        distance_meters=1285.0,
        evidence=(r2_ev,),
    )

    class StubPlaces:
        async def discover(self, *a: object, **k: object) -> object:
            return (place,)

    class StubRouting:
        async def route(self, from_id: str, to_id: str, *a: object) -> object:
            return r1 if from_id == "origin" else r2

    controls = ConstraintSet(
        origin=origin,
        departure_at=departure,
        duration_max_minutes=90,
        budget_minor_units=0,
        currency_code="INR",
        budget_scope="TOTAL",
        party_mode="SOLO",
        party_size=1,
        vibes=["Explore"],
        soft_constraints=[],
        max_walking_minutes=60,
        max_walking_meters=3500,
        return_by_local=None,
        locale="en-IN",
        strict_budget=True,
        hard_constraints=[HardConstraint(kind="EXCLUDE_CATEGORY", value="mall")],
    )

    class DummyModel:
        async def generate(self, req: dict[str, object]) -> str:
            import json as j

            plan_id = req["format"]["properties"]["selected_plan_id"]["enum"][0]
            return j.dumps(
                {"selected_plan_id": plan_id, "reason": "Selected for your soft preferences."}
            )

    app = create_app(
        live_enabled=True,
        live_discovery=StubPlaces(),
        live_routing=StubRouting(),
        model=DummyModel(),
        clock=lambda: now,
    )

    async def run_live() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/v1/plans/compile",
                json={
                    "mode": "LIVE",
                    "controls": controls.model_dump(mode="json"),
                    "free_text": "",
                },
            )
        assert resp.status_code == 409
        result = CompilationFailure.model_validate(resp.json())
        assert result.code == "NO_GROUNDED_CANDIDATES"

    asyncio.run(run_live())
