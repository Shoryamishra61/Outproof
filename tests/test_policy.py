"""Policy regressions use fictional facts, never provider/model responses."""

import ast
import inspect
import socket
from copy import deepcopy

import httpx
import pytest
from ground_rule import policy
from ground_rule.models import CandidatePlan, ConstraintSet
from pydantic import ValidationError

from evals.cases.policy import NOW, baseline, policy_cases
from evals.runner.policy import run_cases


@pytest.mark.parametrize("case", policy_cases(), ids=lambda case: case["id"])
def test_adversarial_policy(case: dict) -> None:
    from datetime import datetime

    controls = ConstraintSet.model_validate(case["constraints"])
    if case["failure"] == "STRUCTURE":
        with pytest.raises(ValidationError):
            CandidatePlan.model_validate(case["plan"])
        return
    result = policy.validate_plan(
        CandidatePlan.model_validate(case["plan"]),
        controls,
        as_of=datetime.fromisoformat(case["as_of"]) if "as_of" in case else NOW,
        allow_fixture=True,
    )
    assert result.accepted is case["accepted"]
    if case["failure"]:
        assert any(
            check.code == case["failure"] and check.status == "FAIL" for check in result.checks
        )
    assert len(result.checks) == 11


def test_model_and_network_calls_prohibited(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("Policy attempted external I/O")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbidden)
    assert all(row["passed"] for row in run_cases())
    imports = [
        node
        for node in ast.walk(ast.parse(inspect.getsource(policy)))
        if isinstance(node, ast.Import | ast.ImportFrom)
    ]
    allowed = {"datetime", "pydantic", "ground_rule.models"}
    assert all(
        (isinstance(node, ast.ImportFrom) and node.module in allowed)
        or (isinstance(node, ast.Import) and [alias.name for alias in node.names] == ["json"])
        for node in imports
    )


def test_fixture_is_rejected_by_default() -> None:
    plan, controls = baseline()
    assert not policy.validate_plan(
        CandidatePlan.model_validate(plan), ConstraintSet.model_validate(controls), as_of=NOW
    ).accepted


def test_model_copy_cannot_remove_return() -> None:
    raw, controls = baseline()
    plan = CandidatePlan.model_validate(raw)
    corrupted = plan.model_copy(update={"routes": plan.routes[:1]})
    result = policy.validate_plan(
        corrupted, ConstraintSet.model_validate(controls), as_of=NOW, allow_fixture=True
    )
    assert not result.accepted
    assert all(check.status == "FAIL" for check in result.checks)


def test_evidence_cannot_be_rebound_by_mutation() -> None:
    raw, controls = baseline()
    plan = CandidatePlan.model_validate(raw)
    place = plan.stops[0].place
    price = place.price
    assert price is not None
    bad_evidence = price.evidence[0].model_copy(update={"subject_id": "other"})
    price = price.model_copy(update={"evidence": (bad_evidence,)})
    stop = plan.stops[0].model_copy(update={"place": place.model_copy(update={"price": price})})
    assert not policy.validate_plan(
        plan.model_copy(update={"stops": (stop,)}),
        ConstraintSet.model_validate(controls),
        as_of=NOW,
        allow_fixture=True,
    ).accepted


def test_inputs_not_mutated_and_naive_clock_rejected() -> None:
    raw, controls = baseline()
    snapshot = deepcopy((raw, controls))
    plan, constraints = CandidatePlan.model_validate(raw), ConstraintSet.model_validate(controls)
    policy.validate_plan(plan, constraints, as_of=NOW, allow_fixture=True)
    assert (raw, controls) == snapshot
    with pytest.raises(ValidationError):
        policy.validate_plan(plan, constraints, as_of=NOW.replace(tzinfo=None), allow_fixture=True)
