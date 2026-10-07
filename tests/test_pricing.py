import pytest
from ground_rule.models import (
    CandidatePlan,
    CompilationFailure,
    ConstraintSet,
    Evidence,
    PriceEvidence,
)
from ground_rule.policy import validate_plan
from ground_rule.pricing import mandatory_price

from evals.cases.policy import NOW, baseline, evidence


def record(**changes: object) -> Evidence:
    value = (
        dict(
            currency_code="INR",
            lower_minor_units=35000,
            upper_minor_units=35000,
            scope="PER_PERSON",
            covers_all_mandatory_costs=True,
        )
        | changes
    )
    return Evidence.model_validate(evidence("fixture:stop", "price", value))


@pytest.mark.parametrize(
    "confidence,upper,allowed",
    [
        ("VERIFIED", 35000, True),
        ("BOUNDED", 48000, True),
        ("BOUNDED", 55000, False),
        ("ESTIMATED", 35000, False),
    ],
)
def test_normalized_bounds_then_strict_policy(confidence: str, upper: int, allowed: bool) -> None:
    price = mandatory_price(record(upper_minor_units=upper), confidence)
    assert isinstance(price, PriceEvidence)
    plan, controls = baseline()
    plan["stops"][0]["place"]["price"] = price.model_dump(mode="json")
    assert (
        validate_plan(
            CandidatePlan.model_validate(plan),
            ConstraintSet.model_validate(controls),
            as_of=NOW,
            allow_fixture=True,
        ).accepted
        == allowed
    )


@pytest.mark.parametrize("value", [None, 1, False, 0, "false"])
def test_incomplete_cost_is_not_eligible(value: object) -> None:
    assert isinstance(
        mandatory_price(record(covers_all_mandatory_costs=value), "VERIFIED"), CompilationFailure
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("lower_minor_units", "35000"),
        ("upper_minor_units", 35000.5),
        ("upper_minor_units", True),
        ("currency_code", "cheap"),
        ("scope", "EACH"),
        ("currency_code", None),
        ("scope", None),
        ("upper_minor_units", -1),
    ],
)
def test_unsafe_or_missing_money(field: str, value: object) -> None:
    assert isinstance(mandatory_price(record(**{field: value}), "BOUNDED"), CompilationFailure)


def test_labels_menu_items_and_verified_ranges_rejected() -> None:
    for value in ["cheap", "₹₹", {"price_level": 1}, {"menu_item_minor_units": 35000}]:
        raw = Evidence.model_validate(evidence("fixture:stop", "price", value))
        assert isinstance(mandatory_price(raw, "VERIFIED"), CompilationFailure)
    assert isinstance(
        mandatory_price(record(upper_minor_units=48000), "VERIFIED"), CompilationFailure
    )


def test_unknown_is_not_zero_and_confirmed_zero_is_explicit() -> None:
    for value in [None, Evidence.model_validate(evidence("fixture:stop", "price", None))]:
        price = mandatory_price(value, "UNKNOWN")
        assert isinstance(price, PriceEvidence) and price.upper is None
    zero = mandatory_price(record(lower_minor_units=0, upper_minor_units=0), "VERIFIED")
    assert isinstance(zero, PriceEvidence) and zero.upper.minor_units == 0


def test_optional_unknown_dessert_does_not_change_mandatory_cost() -> None:
    plan, controls = baseline()
    place = plan["stops"][0]["place"]
    place["price"] = mandatory_price(record(), "VERIFIED").model_dump(mode="json")
    place["evidence"].append(
        evidence(
            "fixture:stop",
            "optional_expenses",
            [dict(description="Optional dessert", price=None, mandatory=False)],
        )
    )
    assert validate_plan(
        CandidatePlan.model_validate(plan),
        ConstraintSet.model_validate(controls),
        as_of=NOW,
        allow_fixture=True,
    ).accepted


def test_other_currency_preserved_then_rejected_by_policy() -> None:
    price = mandatory_price(record(currency_code="USD"), "VERIFIED")
    assert isinstance(price, PriceEvidence) and price.upper.currency_code == "USD"
    plan, controls = baseline()
    plan["stops"][0]["place"]["price"] = price.model_dump(mode="json")
    assert not validate_plan(
        CandidatePlan.model_validate(plan),
        ConstraintSet.model_validate(controls),
        as_of=NOW,
        allow_fixture=True,
    ).accepted
