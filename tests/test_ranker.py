import asyncio
import json

import httpx
import pytest
from app.compiler import valid_candidate_plans
from app.fixtures import FixtureProviders
from app.ranker import LocalGemma, RankSelection, rank_valid_plans
from ground_rule.models import CompilationFailure


def accepted() -> tuple:
    fixture = FixtureProviders()
    plans = asyncio.run(
        valid_candidate_plans(
            fixture.controls, fixture, fixture, fixture, as_of=fixture.as_of, allow_fixture=True
        )
    )
    return fixture, plans


class StubModel:
    def __init__(self, content: str | CompilationFailure) -> None:
        self.content, self.calls = content, []

    async def generate(self, request: dict[str, object]) -> str | CompilationFailure:
        self.calls.append(request)
        return self.content


@pytest.mark.parametrize(
    "kind",
    [
        "correct",
        "unknown",
        "rejected",
        "venue",
        "malformed",
        "extra",
        "duplicate",
        "tie",
        "timeout",
    ],
)
def test_selection(kind: str) -> None:
    fixture, plans = accepted()
    content = json.dumps(
        {"selected_plan_id": plans[0].plan.plan_id, "reason": "Selected for your soft preferences."}
    )
    if kind in {"unknown", "rejected"}:
        content = content.replace(plans[0].plan.plan_id, kind + "-id")
    elif kind == "venue":
        content = content.replace(
            "Selected for your soft preferences.", "Visit Invented Restaurant."
        )
    elif kind == "extra":
        content = content[:-1] + ', "venue": "Invented"}'
    elif kind == "malformed":
        content = "not JSON"
    elif kind == "duplicate":
        content = content[:-1] + ', "selected_plan_id": "unknown"}'
    elif kind == "timeout":
        content = CompilationFailure(code="MODEL_OUTPUT_INVALID", message="Timeout")
    model = StubModel(content)
    result = asyncio.run(
        rank_valid_plans(plans, fixture.controls, model, as_of=fixture.as_of, allow_fixture=True)
    )
    assert isinstance(result, RankSelection if kind in {"correct", "tie"} else CompilationFailure)
    assert len(model.calls) == 1
    assert "coordinates" not in str(model.calls[0]) and "FIXTURE Neem" not in str(model.calls[0])


def test_empty_or_rejected_set_does_not_call_model() -> None:
    fixture, plans = accepted()
    model = StubModel("not used")
    for selected in [(), plans]:
        result = asyncio.run(
            rank_valid_plans(
                selected, fixture.controls, model, as_of=fixture.as_of, allow_fixture=False
            )
        )
        assert isinstance(result, CompilationFailure)
    assert not model.calls


def test_real_adapter_timeout_fails_closed() -> None:
    async def run() -> None:
        def handle(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("synthetic timeout", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            assert isinstance(
                await LocalGemma(client, "fixture-model").generate({}), CompilationFailure
            )

    asyncio.run(run())
