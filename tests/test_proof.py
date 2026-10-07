from datetime import timedelta

import pytest
from ground_rule.proof import build_proof, plan_sources, render_proof, stale_source_ids

from tests.test_ranker import accepted


def test_proof_ids_totals_and_sources_align() -> None:
    fixture, valid = accepted()
    for item in valid:
        proof = build_proof(
            item.plan, item.validation, fixture.controls, as_of=fixture.as_of, allow_fixture=True
        )
        assert proof.validation.plan_id == item.plan.plan_id
        assert proof.total_duration_seconds == 3720 and proof.cost.upper.minor_units in {
            82000,
            86000,
        }
        assert proof.sources == plan_sources(item.plan)
        lines = render_proof(proof, fixture.controls)
        assert len(lines) == 11
        assert [line.code for line in lines] == [c.code for c in item.validation.checks]
        assert all(
            line.evidence_ids == check.evidence_ids
            for line, check in zip(lines, item.validation.checks, strict=True)
        )
        assert "62 min <= 90" in next(line.text for line in lines if line.code == "DURATION")
        assert "INR 1000.00" in next(line.text for line in lines if line.code == "BUDGET")


@pytest.mark.parametrize("kind", ["id", "over_budget", "stale", "false_result"])
def test_false_or_failed_proof_rejected(kind: str) -> None:
    fixture, valid = accepted()
    item = valid[0]
    plan, validation, controls, now = item.plan, item.validation, fixture.controls, fixture.as_of
    if kind == "id":
        validation = validation.model_copy(update={"plan_id": "different"})
    elif kind == "over_budget":
        controls = controls.model_copy(update={"budget_minor_units": 1})
    elif kind == "stale":
        now += timedelta(minutes=16)
    else:
        validation = validation.model_copy(update={"accepted": False})
    with pytest.raises(ValueError):
        build_proof(plan, validation, controls, as_of=now, allow_fixture=True)


def test_stale_source_visible_on_later_inspection() -> None:
    fixture, valid = accepted()
    proof = build_proof(
        valid[0].plan,
        valid[0].validation,
        fixture.controls,
        as_of=fixture.as_of,
        allow_fixture=True,
    )
    assert stale_source_ids(proof, fixture.as_of) == ()
    assert stale_source_ids(proof, fixture.as_of + timedelta(days=2))
    assert all(e.source_ref and e.observed_at for e in proof.sources)
