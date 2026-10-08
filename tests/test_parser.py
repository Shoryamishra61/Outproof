"""Offline parser boundary/precedence tests; real inference is a separate benchmark."""

import json
from copy import deepcopy
from pathlib import Path

import httpx
import pytest
from app.parser import ParserAdditions, parse_constraints, parse_output
from ground_rule.models import CompilationFailure, ConstraintSet

from evals.cases.parser import parser_cases


def controls() -> ConstraintSet:
    return ConstraintSet.model_validate(parser_cases()[0]["controls"])


def empty_additions() -> dict:
    return {
        "exclusions": [],
        "dietary": None,
        "unsupported": [],
        "preferences": [],
        "party_size": None,
        "max_walking_minutes": None,
        "max_walking_meters": None,
        "return_by_local": None,
    }


@pytest.mark.parametrize("raw", ["not json", "[]", "{}", "null", "{", '{"exclusions":true}'])
def test_malformed_output_fails_closed(raw: str) -> None:
    result = parse_output(raw, controls(), "no mall")
    assert isinstance(result, CompilationFailure)
    assert result.code == "MODEL_OUTPUT_INVALID"


@pytest.mark.parametrize(
    "field,value",
    [
        ("budget_minor_units", 100000),
        ("currency_code", "USD"),
        ("duration_max_minutes", 120),
        ("departure_at", "2023-03-15T09:00:00Z"),
        ("places", ["Invented cafe"]),
        ("coordinates", {"latitude": 1.0, "longitude": 2.0}),
        ("budget_scope", "TOTAL"),
        ("price", 0),
        ("routes", []),
    ],
)
def test_forbidden_fields_reject(field: str, value: object) -> None:
    raw = {**empty_additions(), field: value}
    assert isinstance(parse_output(json.dumps(raw), controls(), "quiet"), CompilationFailure)


def test_preserved_historical_budget_doubling() -> None:
    failure = json.loads(
        (
            Path(__file__).resolve().parents[1] / "fixtures/contracts/gemma-control-corruption.json"
        ).read_text()
    )
    assert failure["authoritative_budget_minor_units"] == 50000
    assert failure["observed_budget_minor_units"] == 100000
    raw = {**empty_additions(), "budget_minor_units": failure["observed_budget_minor_units"]}
    original = controls()
    assert isinstance(parse_output(json.dumps(raw), original, "quiet"), CompilationFailure)
    assert original.budget_minor_units == 50000


@pytest.mark.parametrize(
    "field,value",
    [
        ("party_size", 3),
        ("max_walking_minutes", 120),
        ("max_walking_meters", 9999.0),
        ("return_by_local", "2026-10-06T22:00:00+05:30"),
    ],
)
def test_known_optional_controls_immutable(field: str, value: object) -> None:
    supplied = controls().model_dump(mode="json")
    supplied.update(
        max_walking_minutes=20,
        max_walking_meters=2500.0,
        return_by_local="2026-10-06T21:00:00+05:30",
    )
    original = ConstraintSet.model_validate(supplied)
    raw = {**empty_additions(), field: value}
    assert isinstance(parse_output(json.dumps(raw), original, str(value)), CompilationFailure)


def test_additive_merge_preserves_all_controls_and_existing_requirements() -> None:
    supplied = controls().model_dump()
    supplied["hard_constraints"] = [{"kind": "EXCLUDE_CATEGORY", "value": "chain"}]
    supplied["soft_constraints"] = [{"preference": "explore"}]
    original = ConstraintSet.model_validate(supplied)
    snapshot = original.model_dump()
    raw = {
        **empty_additions(),
        "exclusions": ["mall"],
        "dietary": "vegetarian",
        "preferences": ["quiet", "optional coffee"],
    }
    result = parse_output(json.dumps(raw), original, "veg, no mall, quiet; coffee optional")
    assert isinstance(result, ConstraintSet)
    assert {h.value for h in result.hard_constraints} == {"chain", "mall", "vegetarian"}
    assert {s.preference for s in result.soft_constraints} == {
        "explore",
        "quiet",
        "optional coffee",
    }
    for field in ConstraintSet.model_fields:
        if field not in {"hard_constraints", "soft_constraints"}:
            assert getattr(result, field) == getattr(original, field)
    assert original.model_dump() == snapshot


@pytest.mark.parametrize(
    "text,wanted",
    [
        ("Allergy safe", "allergy safety"),
        ("Peanut allergy", "allergy safety"),
        ("Wheelchair accessible", "wheelchair accessibility"),
        ("Guaranteed safe", "personal safety"),
    ],
)
def test_high_stakes_not_dropped_when_model_omits(text: str, wanted: str) -> None:
    result = parse_output(json.dumps(empty_additions()), controls(), text)
    assert isinstance(result, ConstraintSet)
    assert any(h.kind == "UNSUPPORTED" and h.value == wanted for h in result.hard_constraints)


@pytest.mark.parametrize(
    "field,value,text",
    [
        ("max_walking_minutes", 5, "don't walk much"),
        ("return_by_local", "2026-10-06T21:00:00+05:30", "back by 9"),
    ],
)
def test_unsourced_numbers_dates_rejected(field: str, value: object, text: str) -> None:
    assert isinstance(
        parse_output(json.dumps({**empty_additions(), field: value}), controls(), text),
        CompilationFailure,
    )


def test_explicit_missing_optional_controls_can_be_added() -> None:
    raw = {
        **empty_additions(),
        "max_walking_minutes": 20,
        "max_walking_meters": 1500.0,
        "return_by_local": "2026-10-06T21:00:00+05:30",
    }
    result = parse_output(
        json.dumps(raw),
        controls(),
        "Walk max 20 minutes and 1500 meters, return by 2026-10-06T21:00:00+05:30",
    )
    assert isinstance(result, ConstraintSet)
    assert result.max_walking_minutes == 20
    assert result.max_walking_meters == 1500.0
    assert result.return_by_local.isoformat() == raw["return_by_local"]


def test_adapter_fails_closed_on_timeout_and_incomplete_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    def timeout(*args: object, **kwargs: object) -> None:
        calls.append(1)
        raise httpx.ReadTimeout("test timeout")

    monkeypatch.setattr(httpx.Client, "post", timeout)
    assert isinstance(parse_constraints(controls(), "quiet", model="gemma3:1b"), CompilationFailure)
    assert len(calls) == 1

    def incomplete(*args: object, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            200,
            json={"done": False},
            request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
        )

    monkeypatch.setattr(httpx.Client, "post", incomplete)
    assert isinstance(parse_constraints(controls(), "quiet", model="gemma3:1b"), CompilationFailure)


def test_adapter_rejects_remote_url_and_oversized_text() -> None:
    with pytest.raises(ValueError):
        parse_constraints(controls(), "quiet", model="gemma3:1b", base_url="https://example.com")
    result = parse_constraints(controls(), "x" * 4001, model="gemma3:1b")
    assert isinstance(result, CompilationFailure)


def test_benchmark_population_and_expected_schema() -> None:
    cases = parser_cases()
    assert len(cases) == 100 and len({case["id"] for case in cases}) == 100
    groups = {}
    for case in cases:
        assert case["synthetic"] is True
        groups[case["group"]] = groups.get(case["group"], 0) + 1
        ParserAdditions.model_validate(case["expected"])
        ConstraintSet.model_validate(deepcopy(case["controls"]))
    assert sorted(groups.values()) == [5, 10, 10, 10, 10, 10, 15, 15, 15]


@pytest.mark.parametrize(
    "text",
    ["Must be back by 9", "Return before 10 tonight", "Back by 9pm", "Return before 10:30 pm"],
)
def test_clock_only_deadline_not_silently_dropped(text: str) -> None:
    result = parse_output(json.dumps(empty_additions()), controls(), text)
    assert isinstance(result, ConstraintSet)
    assert result.return_by_local is None
    assert any(
        h.kind == "UNSUPPORTED" and h.value == "time clarification" for h in result.hard_constraints
    )


@pytest.mark.parametrize(
    "field,number,text",
    [
        ("max_walking_minutes", 20, "I have 20 minutes total"),
        ("max_walking_meters", 1500.0, "₹1500 total budget"),
        ("party_size", 500, "₹500 total budget"),
    ],
)
def test_numbers_must_bind_to_the_correct_control(field: str, number: object, text: str) -> None:
    supplied = controls().model_dump()
    supplied["party_size"] = None
    original = ConstraintSet.model_validate(supplied)
    result = parse_output(json.dumps({**empty_additions(), field: number}), original, text)
    assert isinstance(result, CompilationFailure)


@pytest.mark.parametrize(
    "text",
    [
        "No malls please",
        "No alcohol places",
        "No chains",
        "Vegetarian required",
        "Vegan required",
        "Maximum walking 20 minutes",
        "Maximum walking 1500 meters",
    ],
)
def test_explicit_hard_requirement_cannot_disappear(text: str) -> None:
    assert isinstance(
        parse_output(json.dumps(empty_additions()), controls(), text), CompilationFailure
    )


def test_vegan_cannot_be_weakened_to_vegetarian() -> None:
    raw = {**empty_additions(), "dietary": "vegetarian"}
    assert isinstance(
        parse_output(json.dumps(raw), controls(), "vegan required"), CompilationFailure
    )


def test_model_cannot_invent_allergy_requirement() -> None:
    raw = {**empty_additions(), "unsupported": ["allergy safety"]}
    assert isinstance(parse_output(json.dumps(raw), controls(), "quiet"), CompilationFailure)


def test_duplicate_json_fields_fail_closed() -> None:
    raw = json.dumps(empty_additions()).replace(
        '"preferences": []', '"preferences": [], "preferences": ["quiet"]'
    )
    assert isinstance(parse_output(raw, controls(), "quiet"), CompilationFailure)


def test_unsupported_requirement_retained_in_malformed_failure() -> None:
    result = parse_output("not json", controls(), "Wheelchair accessible and allergy safe")
    assert isinstance(result, CompilationFailure)
    assert "wheelchair accessibility" in result.message and "allergy safety" in result.message
    assert "needs evidence" in result.message


def test_party_context_can_fill_an_unknown_size() -> None:
    supplied = controls().model_dump()
    supplied["party_size"] = None
    result = parse_output(
        json.dumps({**empty_additions(), "party_size": 3}),
        ConstraintSet.model_validate(supplied),
        "3 of us",
    )
    assert isinstance(result, ConstraintSet)
    assert result.party_size == 3


@pytest.mark.parametrize(
    "text,exclusions",
    [
        ("No malls or chains", ["mall"]),
        ("No chain or alcohol", ["chain"]),
        ("Vegan, no mall or alcohol", ["mall"]),
        ("alcohol wali jagah nahi", []),
    ],
)
def test_combined_and_hinglish_exclusions_cannot_disappear(text: str, exclusions: list) -> None:
    raw = {**empty_additions(), "exclusions": exclusions}
    if "Vegan" in text:
        raw["dietary"] = "vegan"
    assert isinstance(parse_output(json.dumps(raw), controls(), text), CompilationFailure)


def test_explicit_dated_deadline_cannot_disappear() -> None:
    result = parse_output(
        json.dumps(empty_additions()), controls(), "Return by 2026-10-06T21:00:00+05:30"
    )
    assert isinstance(result, CompilationFailure)


def test_specific_unsupported_requirement_survives_normalization() -> None:
    text = "Severe peanut allergy; avoid cross contamination"
    result = parse_output(json.dumps(empty_additions()), controls(), text)
    assert isinstance(result, ConstraintSet)
    assert any(h.kind == "UNSUPPORTED" and text in h.value for h in result.hard_constraints)
    failure = parse_output("invalid", controls(), text)
    assert isinstance(failure, CompilationFailure) and text in failure.message


def test_negated_exclusion_is_not_a_missing_hard_requirement() -> None:
    result = parse_output(json.dumps(empty_additions()), controls(), "Don't exclude alcohol places")
    assert isinstance(result, ConstraintSet)
    assert not result.hard_constraints


@pytest.mark.parametrize(
    "text", ["I'm not vegan", "I’m not vegan", "Vegetarian is not required", "I don't require veg"]
)
def test_explicit_dietary_nonrequirement_does_not_add_a_requirement(text: str) -> None:
    result = parse_output(json.dumps(empty_additions()), controls(), text)
    assert isinstance(result, ConstraintSet) and not result.hard_constraints
    invented = {**empty_additions(), "dietary": "vegan"}
    assert isinstance(parse_output(json.dumps(invented), controls(), text), CompilationFailure)


def test_negated_self_diet_does_not_erase_other_party_requirement() -> None:
    text = "I'm not vegan, but my friend is vegan"
    assert isinstance(
        parse_output(json.dumps(empty_additions()), controls(), text), CompilationFailure
    )
    result = parse_output(json.dumps({**empty_additions(), "dietary": "vegan"}), controls(), text)
    assert isinstance(result, ConstraintSet)
    assert any(h.kind == "DIETARY" and h.value == "vegan" for h in result.hard_constraints)


@pytest.mark.parametrize("text", ["Food required", "Meal is mandatory", "We must eat"])
def test_required_food_survives_model_omission(text: str) -> None:
    result = parse_output(json.dumps(empty_additions()), controls(), text)
    assert isinstance(result, ConstraintSet)
    assert any(
        h.kind == "UNSUPPORTED" and h.value == "food requirement" for h in result.hard_constraints
    )


def test_optional_food_does_not_become_a_hard_requirement() -> None:
    result = parse_output(
        json.dumps(empty_additions()), controls(), "Food is optional, not required"
    )
    assert isinstance(result, ConstraintSet) and not result.hard_constraints


def test_timeout_retains_specific_unsupported_requirement(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*args: object, **kwargs: object) -> None:
        raise httpx.ReadTimeout("test timeout")

    monkeypatch.setattr(httpx.Client, "post", timeout)
    text = "Severe peanut allergy; avoid cross contamination"
    result = parse_constraints(controls(), text, model="gemma3:4b")
    assert isinstance(result, CompilationFailure)
    assert text in result.message and "allergy safety" in result.message


def test_schema_is_supplied_to_model_without_authoritative_values() -> None:
    from app.parser import model_request

    request = model_request(controls(), "quiet", "gemma4:e2b-it-qat")
    message = request["messages"][0]["content"]
    assert json.dumps(request["format"]) in message
    assert "50000" not in message and "INR" not in message
    assert "budget_minor_units" not in message and "duration_max_minutes" not in message


@pytest.mark.parametrize(
    "field", ["party_size", "max_walking_minutes", "max_walking_meters", "return_by_local"]
)
def test_known_control_echo_violates_the_requested_null_schema(field: str) -> None:
    supplied = controls().model_dump(mode="json")
    supplied.update(
        max_walking_minutes=20,
        max_walking_meters=2500.0,
        return_by_local="2026-10-06T21:00:00+05:30",
    )
    original = ConstraintSet.model_validate(supplied)
    raw = {**empty_additions(), field: supplied[field]}
    result = parse_output(
        json.dumps(raw),
        original,
        "4 of us, walk max 20 minutes and 2500 meters, return by 2026-10-06T21:00:00+05:30",
    )
    assert isinstance(result, CompilationFailure)
