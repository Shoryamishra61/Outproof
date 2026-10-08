"""Seeded controlled compiler journeys; geography and facts are explicitly synthetic."""

import asyncio
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import timedelta

import pytest
from app.compilation import compile_internal
from ground_rule.models import (
    CompilationFailure,
    CompiledPlan,
    ConstraintSet,
    PlaceCandidate,
    RouteFact,
)
from hypothesis import given, settings
from hypothesis import strategies as st

from evals.cases.policy import NOW, baseline, refresh

SEED = 20261009
CITIES = [json.loads(line) for line in open("evals/cases/global_scenarios.jsonl", encoding="utf-8")]
CITIES = list({case["city"]: case for case in CITIES}.values())


def journey_cases() -> list[tuple]:
    rng = random.Random(SEED)
    cases: set[tuple] = set()
    while len(cases) < 4096:
        cases.add(
            (
                rng.randrange(19),
                rng.choice(["SOLO", "FRIEND", "DATE", "GROUP"]),
                rng.choice(["TOTAL", "PER_PERSON"]),
                rng.choice([0, 999, 1000, 2000, 4000]),
                rng.choice([30, 56, 57, 90]),
                rng.choice([0, 11, 12, 60]),
                rng.choice(["VERIFIED", "BOUNDED", "ESTIMATED", "UNKNOWN"]),
                rng.choice(
                    [
                        "none",
                        "missing_price",
                        "closed",
                        "stale",
                        "no_return",
                        "mall",
                        "allergy",
                        "model",
                        "outage",
                    ]
                ),
                rng.choice(["Food", "Talk", "Explore", "Chill", "Move", "Surprise"]),
            )
        )
    return sorted(cases)


CASES = journey_cases()


@dataclass
class ControlledProviders:
    place: PlaceCandidate
    routes: tuple[RouteFact, ...]
    fault: str
    model_calls: int = 0

    async def discover(self, *args: object, **kwargs: object) -> object:
        if self.fault == "outage":
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Controlled outage"
            )
        return (self.place,)

    async def enrich(self, place: PlaceCandidate) -> PlaceCandidate:
        return place

    async def route(self, from_id: str, to_id: str, *args: object) -> object:
        for route in self.routes:
            if (route.from_id, route.to_id) == (from_id, to_id):
                return route
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Controlled missing leg"
        )

    async def generate(self, request: dict) -> str:
        self.model_calls += 1
        if self.fault == "model":
            return '{"selected_plan_id":"rejected","reason":"invented venue"}'
        return json.dumps(
            {
                "selected_plan_id": request["format"]["properties"]["selected_plan_id"]["enum"][0],
                "reason": "Selected for your soft preferences.",
            }
        )


def execute_journey(case: tuple) -> tuple[bool, str]:
    city, party, scope, budget, minutes, walk, confidence, fault, vibe = case
    raw, controls = baseline()
    currency = CITIES[city]["controls"]["currency_code"]
    origin = CITIES[city]["origin"]
    raw["origin"] = origin
    place = raw["stops"][0]["place"]
    place["coordinates"] = {
        "latitude": origin["latitude"] + 0.001,
        "longitude": origin["longitude"] + 0.001,
    }
    place["categories"] = ["restaurant"]
    place["name"] = "FIXTURE controlled eatery"
    raw["stops"][0]["dwell_seconds"] = 2700
    raw["routes"][0].update(duration_seconds=300, distance_meters=400.0)
    raw["routes"][1].update(duration_seconds=420, distance_meters=500.0)
    size = {"SOLO": 1, "FRIEND": 2, "DATE": 2, "GROUP": 4}[party]
    controls.update(
        currency_code=currency,
        budget_scope=scope,
        budget_minor_units=budget,
        duration_max_minutes=minutes,
        max_walking_minutes=walk,
        origin=origin,
        departure_at=raw["departure_at"],
        party_mode=party,
        party_size=size,
        vibes=[vibe],
    )
    price = place["price"]
    price.update(confidence=confidence)
    for bound in ["lower", "upper"]:
        price[bound] = {"currency_code": currency, "minor_units": 1000}
    if confidence == "UNKNOWN":
        price.update(lower=None, upper=None, scope=None, evidence=[])
    if fault == "missing_price":
        place["price"] = None
    if fault == "closed":
        place["opening_windows"][0]["closes_at"] = (NOW + timedelta(minutes=49)).isoformat()
    if fault == "mall":
        controls["hard_constraints"] = [{"kind": "EXCLUDE_CATEGORY", "value": "mall"}]
        place["categories"].append("mall")
    if fault == "allergy":
        controls["hard_constraints"] = [
            {"kind": "UNSUPPORTED", "value": "peanut cross contamination"}
        ]
    refresh(raw)
    if fault == "stale":
        raw["routes"][0]["evidence"][0]["observed_at"] = (NOW - timedelta(minutes=16)).isoformat()
    routes = raw["routes"][:1] if fault == "no_return" else raw["routes"]
    providers = ControlledProviders(
        PlaceCandidate.model_validate(place),
        tuple(RouteFact.model_validate(r) for r in routes),
        fault,
    )
    constraints = ConstraintSet.model_validate(controls)
    result = asyncio.run(
        compile_internal(
            constraints, providers, providers, providers, providers, as_of=NOW, mode="FIXTURE"
        )
    )
    expected = (
        budget * (size if scope == "PER_PERSON" else 1) >= 1000 * size
        and minutes >= 57
        and walk >= 12
        and confidence in {"VERIFIED", "BOUNDED"}
        and fault == "none"
    )
    assert isinstance(result, CompiledPlan) is expected, case
    if expected:
        assert result.mode == "FIXTURE" and result.plan.stops[0].place.name.startswith("FIXTURE")
        assert result.proof.cost.upper.minor_units == size * 1000
        assert result.proof.total_duration_seconds == 3420
        assert result.proof.walking_distance_meters == 900
        assert len(result.proof.validation.checks) == 11
        assert all(c.hard and c.status == "PASS" for c in result.proof.validation.checks)
        sources = {s.evidence_id for s in result.proof.sources}
        assert all(set(c.evidence_ids) <= sources for c in result.proof.validation.checks)
        assert providers.model_calls == 1
    else:
        assert isinstance(result, CompilationFailure)
        assert providers.model_calls == (
            1
            if fault == "model"
            and budget * (size if scope == "PER_PERSON" else 1) >= 1000 * size
            and minutes >= 57
            and walk >= 12
            and confidence in {"VERIFIED", "BOUNDED"}
            else 0
        )
    return expected, result.status


@pytest.mark.parametrize(
    "case", CASES, ids=lambda c: hashlib.sha256(repr(c).encode()).hexdigest()[:12]
)
def test_controlled_journey(case: tuple) -> None:
    execute_journey(case)


@settings(max_examples=300, derandomize=True)
@given(st.integers(min_value=0, max_value=9007199254740991), st.integers(min_value=0, max_value=10))
def test_minor_unit_arithmetic_boundary(amount: int, size: int) -> None:
    from ground_rule.models import Money

    if amount * size <= 9007199254740991:
        assert (
            Money(currency_code="JPY", minor_units=amount).multiply(size).minor_units
            == amount * size
        )
    else:
        with pytest.raises(ValueError):
            Money(currency_code="JPY", minor_units=amount).multiply(size)
