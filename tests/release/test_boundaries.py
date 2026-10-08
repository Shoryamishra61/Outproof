from copy import deepcopy
from datetime import timedelta

import pytest
from ground_rule.models import CandidatePlan, ConstraintSet
from ground_rule.policy import validate_plan

from evals.cases.policy import NOW, baseline, refresh

FAULTS = [
    "budget",
    "currency",
    "duration",
    "walking",
    "deadline",
    "closed",
    "dwell_close",
    "stale_route",
    "future_route",
    "wrong_identity",
    "wrong_coordinate",
    "missing_price",
    "mandatory_fee",
    "unsupported_allergy",
    "unknown_hours",
]


@pytest.mark.parametrize("fault,index", [(fault, i) for fault in FAULTS for i in range(20)])
def test_adversarial_boundary(fault: str, index: int) -> None:
    raw, controls = baseline()
    place = raw["stops"][0]["place"]
    # Each variant changes a policy input, not merely its name.
    raw["routes"][1]["duration_seconds"] += index
    refresh(raw)
    if fault == "budget":
        controls["budget_minor_units"] = 42000 - index - 1
    elif fault == "currency":
        controls["currency_code"] = "USD"
        controls["budget_minor_units"] += index
    elif fault == "duration":
        controls["duration_max_minutes"] = 59
    elif fault == "walking":
        controls["max_walking_meters"] = 1300.0 - index - 1
    elif fault == "deadline":
        controls["departure_at"] = raw["departure_at"]
        controls["return_by_local"] = (NOW + timedelta(seconds=3599)).isoformat()
    elif fault in {"closed", "dwell_close"}:
        place["opening_windows"][0]["closes_at"] = (
            NOW + timedelta(seconds=600 if fault == "closed" else 2999 - index)
        ).isoformat()
        refresh(raw)
    elif fault in {"stale_route", "future_route"}:
        raw["routes"][0]["evidence"][0]["observed_at"] = (
            NOW + timedelta(seconds=index + 1)
            if fault == "future_route"
            else NOW - timedelta(seconds=900 + index)
        ).isoformat()
    elif fault == "wrong_identity":
        place["evidence"][0]["subject_id"] = "wrong"
    elif fault == "wrong_coordinate":
        value = place["evidence"][1]["value"]
        place["evidence"][1]["value"] = {
            **value,
            "latitude": value["latitude"] + (index + 1) / 10000,
        }
    elif fault == "missing_price":
        place["price"] = None
    elif fault == "mandatory_fee":
        place["price"]["evidence"][0]["value"]["covers_all_mandatory_costs"] = False
    elif fault == "unsupported_allergy":
        controls["hard_constraints"] = [
            {"kind": "UNSUPPORTED", "value": "allergen cross contamination"}
        ]
    else:
        place["opening_windows"] = None
    result = validate_plan(
        CandidatePlan.model_validate(deepcopy(raw)),
        ConstraintSet.model_validate(controls),
        as_of=NOW,
        allow_fixture=True,
    )
    assert not result.accepted
    assert any(c.status == "FAIL" for c in result.checks)
