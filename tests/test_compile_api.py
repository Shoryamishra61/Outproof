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
