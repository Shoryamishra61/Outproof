import asyncio
import json
from datetime import timedelta

import pytest
from app.compilation import compile_internal
from ground_rule.models import CompilationFailure, CompiledPlan
from pydantic import ValidationError

from tests.test_ranker import StubModel, accepted


def compiled() -> CompiledPlan:
    fixture, plans = accepted()
    result = asyncio.run(
        compile_internal(
            fixture.controls,
            fixture,
            fixture,
            fixture,
            StubModel(
                json.dumps(
                    {
                        "selected_plan_id": plans[0].plan.plan_id,
                        "reason": "Selected for your soft preferences.",
                    }
                )
            ),
            as_of=fixture.as_of,
            mode="FIXTURE",
        )
    )
    assert isinstance(result, CompiledPlan)
    return result


def test_exactly_one_all_evidence_proof_and_roundtrip() -> None:
    result = compiled()
    assert "plan" in result.model_dump() and "plans" not in result.model_dump()
    assert result.proof.validation.plan_id == result.plan.plan_id
    assert len(result.plan.stops) == 1 and result.plan.routes[-1].to_id == "origin"
    assert result.mode == "FIXTURE" and all(e.source == "FIXTURE" for e in result.proof.sources)
    assert CompiledPlan.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("field", ["alternates", "options", "rejected_candidates"])
def test_extra_options_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        CompiledPlan.model_validate({**compiled().model_dump(), field: []})


def test_ranker_cannot_resurrect_invalid_plan() -> None:
    fixture, plans = accepted()
    fixture.places = (fixture.places[0].model_copy(update={"price": None}), fixture.places[1])
    result = asyncio.run(
        compile_internal(
            fixture.controls,
            fixture,
            fixture,
            fixture,
            StubModel(
                json.dumps(
                    {
                        "selected_plan_id": plans[0].plan.plan_id,
                        "reason": "Selected for your soft preferences.",
                    }
                )
            ),
            as_of=fixture.as_of,
            mode="FIXTURE",
        )
    )
    assert isinstance(result, CompilationFailure) and result.code == "MODEL_OUTPUT_INVALID"


def test_post_ranker_evidence_expiry_fails_closed() -> None:
    fixture, plans = accepted()
    result = asyncio.run(
        compile_internal(
            fixture.controls,
            fixture,
            fixture,
            fixture,
            StubModel(
                json.dumps(
                    {
                        "selected_plan_id": plans[0].plan.plan_id,
                        "reason": "Selected for your soft preferences.",
                    }
                )
            ),
            as_of=fixture.as_of,
            mode="FIXTURE",
            clock=lambda: fixture.as_of + timedelta(minutes=16),
        )
    )
    assert isinstance(result, CompilationFailure)


def test_proof_totals_or_live_fixture_mismatch_impossible() -> None:
    result = compiled()
    for changed in [
        result.model_copy(update={"mode": "LIVE"}),
        result.model_copy(
            update={"proof": result.proof.model_copy(update={"total_duration_seconds": 1})}
        ),
    ]:
        with pytest.raises(ValidationError):
            CompiledPlan.model_validate(changed)
