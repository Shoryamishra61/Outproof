from copy import deepcopy
from datetime import UTC, datetime, timedelta, timezone

import pytest
from ground_rule.models import (
    CandidatePlan,
    CompilationFailure,
    ConstraintSet,
    PlaceCandidate,
    RouteFact,
)
from ground_rule.plans import build_candidates
from ground_rule.policy import validate_plan

from evals.cases.policy import NOW, baseline, evidence, refresh


def inputs() -> tuple:
    plan, controls = baseline()
    controls.update(origin=plan["origin"], departure_at=plan["departure_at"])
    eatery = deepcopy(plan["stops"][0]["place"])
    eatery.update(place_id="fixture:eatery", provider_id="eatery", categories=["restaurant"])
    park = deepcopy(eatery)
    park.update(place_id="fixture:park", provider_id="park", categories=["park"])
    park["price"]["lower"]["minor_units"] = park["price"]["upper"]["minor_units"] = 0
    plan["stops"] = [
        {"place": eatery, "dwell_seconds": 1800, "arrival_at": None},
        {"place": park, "dwell_seconds": 1200, "arrival_at": None},
    ]
    plan["routes"] = [
        dict(
            route_id=f"route-{a}-{b}",
            from_id=a,
            to_id=b,
            reachable=True,
            duration_seconds=300,
            distance_meters=350.0,
            evidence=[],
        )
        for a, b in [
            ("origin", "fixture:eatery"),
            ("fixture:eatery", "fixture:park"),
            ("fixture:park", "origin"),
        ]
    ]
    refresh(plan)
    park["evidence"].append(evidence("fixture:park", "public_access", True))
    extra_routes = []
    for start, end in [("origin", "fixture:park"), ("fixture:eatery", "origin")]:
        single = deepcopy(plan)
        single["stops"] = [single["stops"][1 if end == "fixture:park" else 0]]
        place_id = single["stops"][0]["place"]["place_id"]
        single["routes"] = [
            dict(
                route_id=f"route-{a}-{b}",
                from_id=a,
                to_id=b,
                reachable=True,
                duration_seconds=300,
                distance_meters=350.0,
                evidence=[],
            )
            for a, b in [("origin", place_id), (place_id, "origin")]
        ]
        refresh(single)
        extra_routes.append(next(r for r in single["routes"] if r["from_id"] == start))
    return (
        tuple(PlaceCandidate.model_validate(p) for p in (eatery, park)),
        tuple(RouteFact.model_validate(r) for r in plan["routes"] + extra_routes),
        ConstraintSet.model_validate(controls),
    )


def test_three_templates_pass_fixture_policy_and_include_return() -> None:
    places, routes, controls = inputs()
    result = build_candidates(places, routes, controls, as_of=NOW, allow_fixture=True)
    assert not isinstance(result, CompilationFailure) and len(result) == 3
    assert {p.plan_id.split(":")[0] for p in result} == {"template-A", "template-B", "template-C"}
    for plan in result:
        assert len(plan.routes) == len(plan.stops) + 1
        assert plan.routes[-1].to_id == "origin"
        assert validate_plan(plan, controls, as_of=NOW, allow_fixture=True).accepted
    assert result == build_candidates(
        places[::-1], routes[::-1], controls, as_of=NOW, allow_fixture=True
    )


def test_fixtures_cannot_become_real_candidates() -> None:
    assert isinstance(build_candidates(*inputs(), as_of=NOW), CompilationFailure)


@pytest.mark.parametrize("kind", ["mismatch", "stale", "missing"])
def test_template_category_requires_positive_matching_evidence(kind: str) -> None:
    places, routes, controls = inputs()
    place = places[0]
    records = []
    for record in place.evidence:
        if record.field == "categories":
            if kind == "missing":
                continue
            record = record.model_copy(
                update={"value": ["park"]}
                if kind == "mismatch"
                else {"observed_at": NOW - timedelta(days=7)}
            )
        records.append(record)
    place = place.model_copy(update={"evidence": tuple(records)})
    assert isinstance(
        build_candidates((place,), routes, controls, as_of=NOW, allow_fixture=True),
        CompilationFailure,
    )


@pytest.mark.parametrize("field", ["origin", "departure_at"])
def test_missing_authoritative_context(field: str) -> None:
    places, routes, controls = inputs()
    controls = controls.model_copy(update={field: None})
    assert isinstance(
        build_candidates(places, routes, controls, as_of=NOW, allow_fixture=True),
        CompilationFailure,
    )


def test_unknown_park_cost_or_access_never_creates_free_template() -> None:
    places, routes, controls = inputs()
    for park in [
        places[1].model_copy(update={"price": None}),
        places[1].model_copy(update={"evidence": places[1].evidence[:-1]}),
    ]:
        result = build_candidates(
            (places[0], park), routes, controls, as_of=NOW, allow_fixture=True
        )
        assert not isinstance(result, CompilationFailure)
        assert all(not p.plan_id.startswith("template-A") for p in result)


def test_unknown_eatery_cost_still_needs_validation() -> None:
    places, routes, controls = inputs()
    result = build_candidates(
        (places[0].model_copy(update={"price": None}),),
        routes,
        controls,
        as_of=NOW,
        allow_fixture=True,
    )
    assert not isinstance(result, CompilationFailure) and len(result) == 1
    assert not validate_plan(result[0], controls, as_of=NOW, allow_fixture=True).accepted


def test_public_access_must_last_through_required_dwell() -> None:
    places, routes, controls = inputs()
    park = places[1]
    records = tuple(
        record.model_copy(update={"expires_at": NOW + timedelta(minutes=20)})
        if record.field == "public_access"
        else record
        for record in park.evidence
    )
    park = park.model_copy(update={"evidence": records})
    result = build_candidates((places[0], park), routes, controls, as_of=NOW, allow_fixture=True)
    assert not isinstance(result, CompilationFailure)
    assert len(result) == 1 and result[0].plan_id.startswith("template-B")


def test_missing_return_routes_do_not_create_templates() -> None:
    places, routes, controls = inputs()
    routes = tuple(r for r in routes if r.to_id != "origin")
    assert isinstance(
        build_candidates(places, routes, controls, as_of=NOW, allow_fixture=True),
        CompilationFailure,
    )


def test_ungrounded_place_is_dropped() -> None:
    places, routes, controls = inputs()
    result = build_candidates(
        (places[0].model_copy(update={"coordinates": None}),),
        routes,
        controls,
        as_of=NOW,
        allow_fixture=True,
    )
    assert isinstance(result, CompilationFailure)


def test_return_over_limit_rejected_and_unreachable_totals_unknown() -> None:
    places, routes, controls = inputs()
    raw_routes = [r.model_dump(mode="json") for r in routes]
    for route in raw_routes:
        if route["from_id"] == "fixture:eatery" and route["to_id"] == "origin":
            route["duration_seconds"] = 2701
            route["evidence"][0]["value"]["duration_seconds"] = 2701
    result = build_candidates(
        (places[0],),
        tuple(RouteFact.model_validate(r) for r in raw_routes),
        controls,
        as_of=NOW,
        allow_fixture=True,
    )
    assert not isinstance(result, CompilationFailure)
    assert result[0].total_duration_seconds == 5701
    assert not validate_plan(result[0], controls, as_of=NOW, allow_fixture=True).accepted
    for route in raw_routes:
        if route["to_id"] == "fixture:eatery":
            route.update(reachable=False, duration_seconds=None, distance_meters=None)
            route["evidence"][0]["value"].update(
                reachable=False, duration_seconds=None, distance_meters=None
            )
    result = build_candidates(
        (places[0],),
        tuple(RouteFact.model_validate(r) for r in raw_routes),
        controls,
        as_of=NOW,
        allow_fixture=True,
    )
    assert not isinstance(result, CompilationFailure) and result[0].total_duration_seconds is None
    assert result[0].stops[0].arrival_at is None


def test_duplicate_conflicts_fail_closed() -> None:
    places, routes, controls = inputs()
    assert isinstance(
        build_candidates(
            places + (places[0].model_copy(update={"name": "changed"}),),
            routes,
            controls,
            as_of=NOW,
            allow_fixture=True,
        ),
        CompilationFailure,
    )
    assert isinstance(
        build_candidates(
            places,
            routes + (routes[0].model_copy(update={"duration_seconds": 999}),),
            controls,
            as_of=NOW,
            allow_fixture=True,
        ),
        CompilationFailure,
    )


def test_time_projection_crosses_local_midnight_using_instants() -> None:
    places, routes, controls = inputs()
    departure = datetime(2026, 10, 6, 23, 59, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    controls = controls.model_copy(update={"departure_at": departure})
    # Freshness is unrelated to the date math under test; identity stays within 30 days.
    result = build_candidates((places[0],), routes, controls, as_of=NOW, allow_fixture=True)
    assert not isinstance(result, CompilationFailure)
    assert result[0].stops[0].arrival_at == departure.astimezone(UTC) + timedelta(seconds=300)
    assert result[0].stops[0].arrival_at.astimezone(departure.tzinfo).day == 7
    assert CandidatePlan.model_validate(result[0]).total_duration_seconds == 3300
