import json
from datetime import datetime, timedelta, tzinfo
from pathlib import Path

import pytest
from ground_rule.models import (
    CandidatePlan,
    CompiledPlan,
    ConstraintSet,
    Evidence,
    Money,
    PlanProof,
)
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]


def test_currency_safe_arithmetic_and_comparison() -> None:
    small = Money(currency_code="INR", minor_units=101)
    limit = Money(currency_code="INR", minor_units=202)
    assert small.add(small) == limit
    assert small.multiply(2) == limit
    assert small.is_at_most(limit)
    assert not limit.is_at_most(small)
    foreign = Money(currency_code="USD", minor_units=101)
    with pytest.raises(ValueError, match="different currencies"):
        small.add(foreign)
    with pytest.raises(ValueError, match="different currencies"):
        small.is_at_most(foreign)


@pytest.mark.parametrize("count", [-1, True, 1.5, "2"])
def test_money_never_coerces_multipliers(count: object) -> None:
    with pytest.raises(ValueError, match="integer"):
        Money(currency_code="JPY", minor_units=100).multiply(count)  # type: ignore[arg-type]


def test_compiled_fixture_roundtrip_is_one_plan_with_return_time() -> None:
    payload = (ROOT / "fixtures/contracts/compiled-plan.json").read_text(encoding="utf-8")
    compiled = CompiledPlan.model_validate_json(payload)
    assert len(compiled.plan.stops) == 1
    assert compiled.plan.routes[-1].to_id == "origin"
    assert compiled.plan.total_duration_seconds == 3600
    assert compiled.plan.walking_distance_meters == 1300
    assert compiled.mode == "FIXTURE"
    assert CompiledPlan.model_validate_json(compiled.model_dump_json()) == compiled
    schema = json.loads((ROOT / "contracts/compiled-plan.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(json.loads(payload))


def test_unreachable_leg_has_unknown_total_and_cannot_be_compiled() -> None:
    compiled_payload = json.loads((ROOT / "fixtures/contracts/compiled-plan.json").read_text())
    candidate_payload = compiled_payload["plan"]
    candidate_payload["routes"][0].update(
        reachable=False, duration_seconds=None, distance_meters=None
    )
    candidate_payload["stops"][0]["arrival_at"] = None
    candidate = CandidatePlan.model_validate(candidate_payload)
    assert candidate.total_duration_seconds is None
    assert candidate.walking_distance_meters is None
    with pytest.raises(ValidationError, match="complete round trip"):
        CompiledPlan.model_validate(compiled_payload)


def test_nested_instances_are_revalidated_even_after_unsafe_copy() -> None:
    compiled = CompiledPlan.model_validate_json(
        (ROOT / "fixtures/contracts/compiled-plan.json").read_text()
    )
    forged = compiled.proof.model_copy(update={"total_duration_seconds": 3000})
    with pytest.raises(ValidationError, match="complete round trip"):
        CompiledPlan.model_validate({**compiled.model_dump(), "proof": forged})


def test_naive_datetime_objects_fail_at_evidence_boundary() -> None:
    compiled = CompiledPlan.model_validate_json(
        (ROOT / "fixtures/contracts/compiled-plan.json").read_text()
    )
    payload = compiled.proof.sources[0].model_dump()
    payload["observed_at"] = datetime(2026, 10, 6, 8)
    with pytest.raises(ValidationError, match="timezone"):
        Evidence.model_validate(payload)


def test_malformed_model_json_fails_closed() -> None:
    with pytest.raises(ValidationError):
        ConstraintSet.model_validate_json('{"duration_max_minutes":')


def test_every_exported_schema_is_valid_json_schema() -> None:
    for path in (ROOT / "contracts").glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text()))


class RepeatedHourTimezone(tzinfo):
    """Model the two UTC offsets of a repeated hour without OS timezone data."""

    def utcoffset(self, value: datetime | None) -> timedelta:
        return timedelta(hours=-5 if value is not None and value.fold else -4)

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(0)


def test_elapsed_time_and_evidence_expiry_use_instants_in_repeated_hour() -> None:
    repeated_hour = RepeatedHourTimezone()
    compiled = CompiledPlan.model_validate_json(
        (ROOT / "fixtures/contracts/compiled-plan.json").read_text()
    )
    first = datetime(2026, 11, 1, 1, 55, tzinfo=repeated_hour, fold=0)
    second = datetime(2026, 11, 1, 1, 5, tzinfo=repeated_hour, fold=1)
    source = compiled.proof.sources[0].model_dump()
    source.update(observed_at=first, expires_at=second)
    assert Evidence.model_validate(source).expires_at == second
    payload = compiled.plan.model_dump()
    payload["departure_at"] = first
    payload["stops"][0]["arrival_at"] = second
    assert CandidatePlan.model_validate(payload).total_duration_seconds == 3600


def test_extreme_travel_time_fails_as_contract_error() -> None:
    payload = json.loads((ROOT / "fixtures/contracts/compiled-plan.json").read_text())["plan"]
    payload["routes"][0]["duration_seconds"] = 10**30
    with pytest.raises(ValidationError, match="datetime range"):
        CandidatePlan.model_validate(payload)


def test_price_proof_cannot_reuse_identifier_with_conflicting_evidence() -> None:
    payload = json.loads((ROOT / "fixtures/contracts/compiled-plan.json").read_text())["proof"]
    payload["cost"]["evidence"][0]["value"]["minor_units"] = 100
    with pytest.raises(ValidationError, match="Cost evidence"):
        PlanProof.model_validate(payload)


def test_compiled_place_cannot_omit_source_evidence() -> None:
    payload = json.loads((ROOT / "fixtures/contracts/compiled-plan.json").read_text())
    payload["plan"]["stops"][0]["place"]["evidence"] = []
    with pytest.raises(ValidationError, match="source evidence"):
        CompiledPlan.model_validate(payload)
