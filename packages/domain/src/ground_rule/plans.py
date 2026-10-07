"""Small deterministic templates over supplied facts; no discovery or model I/O."""

import hashlib
import json
from datetime import UTC, datetime, timedelta
from itertools import product

from pydantic import AwareDatetime, TypeAdapter

from ground_rule.models import (
    CandidatePlan,
    CheckCode,
    CompilationFailure,
    ConstraintSet,
    PlaceCandidate,
    PlanStop,
    PriceConfidence,
    RouteFact,
)
from ground_rule.policy import validate_plan


def has_category_evidence(place: PlaceCandidate, as_of: datetime, allow_fixture: bool) -> bool:
    records = [e for e in place.evidence if e.field == "categories"]
    permitted = {"OSM", "DIRECT", "SERPAPI"} | ({"FIXTURE"} if allow_fixture else set())
    return (
        place.categories is not None
        and bool(records)
        and all(
            e.subject_id == place.place_id
            and e.value == list(place.categories)
            and e.source in permitted
            and e.confidence in {"HIGH", "MEDIUM"}
            and timedelta(0)
            <= as_of.astimezone(UTC) - e.observed_at.astimezone(UTC)
            < timedelta(days=7)
            and (e.expires_at is None or as_of.astimezone(UTC) < e.expires_at.astimezone(UTC))
            for e in records
        )
    )


def public_space(place: PlaceCandidate, as_of: datetime, allow_fixture: bool) -> bool:
    sources = {"OSM", "DIRECT", "SERPAPI"} | ({"FIXTURE"} if allow_fixture else set())
    records = [e for e in place.evidence if e.field == "public_access"]
    return (
        "park" in (place.categories or ())
        and bool(records)
        and all(
            e.subject_id == place.place_id
            and e.value is True
            and e.source in sources
            and e.confidence in {"HIGH", "MEDIUM"}
            and timedelta(0)
            <= as_of.astimezone(UTC) - e.observed_at.astimezone(UTC)
            < timedelta(days=1)
            and (e.expires_at is None or as_of.astimezone(UTC) < e.expires_at.astimezone(UTC))
            for e in records
        )
    )


def build_candidates(
    places: tuple[PlaceCandidate, ...],
    routes: tuple[RouteFact, ...],
    controls: ConstraintSet,
    *,
    as_of: datetime,
    allow_fixture: bool = False,
) -> tuple[CandidatePlan, ...] | CompilationFailure:
    """Generate A free public stop, B eatery, C eatery + public stop.

    Supplied route catalogue must include each inbound and return leg. Every
    emitted candidate passes policy grounding, but still needs full validation.
    """
    controls = ConstraintSet.model_validate(controls)
    as_of = TypeAdapter(AwareDatetime).validate_python(as_of)
    if controls.origin is None or controls.departure_at is None:
        return CompilationFailure(
            code="UNSUPPORTED_CONSTRAINT", message="Templates require explicit origin and departure"
        )
    places = tuple(PlaceCandidate.model_validate(p) for p in places)
    routes = tuple(RouteFact.model_validate(r) for r in routes)
    by_id: dict[str, PlaceCandidate] = {}
    for place in places:
        if place.place_id in by_id and by_id[place.place_id] != place:
            return CompilationFailure(
                code="NO_GROUNDED_CANDIDATES", message="Conflicting place identity in builder input"
            )
        by_id[place.place_id] = place
    by_leg: dict[tuple[str, str], RouteFact] = {}
    for route in routes:
        key = (route.from_id, route.to_id)
        if key in by_leg and by_leg[key] != route:
            return CompilationFailure(
                code="NO_TIME_FEASIBLE_PLAN", message="Conflicting directed route leg"
            )
        by_leg[key] = route
    # ponytail: bounded exhaustive pairs; use route matrices if larger candidate sets are needed.
    selected = [
        p
        for p in sorted(by_id.values(), key=lambda p: p.place_id)
        if has_category_evidence(p, as_of, allow_fixture)
    ][:12]
    public = [p for p in selected if public_space(p, as_of, allow_fixture)]
    eateries = [p for p in selected if {"restaurant", "cafe"} & set(p.categories or ())]
    free = [
        p
        for p in public
        if p.price is not None
        and p.price.confidence == PriceConfidence.VERIFIED
        and p.price.upper is not None
        and p.price.upper.minor_units == 0
    ]
    sequences = [("A", (p,), (1800,)) for p in free]
    sequences += [("B", (p,), (2700,)) for p in eateries]
    sequences += [
        ("C", (p, park), (1800, 1200))
        for p, park in product(eateries, public)
        if p.place_id != park.place_id
    ]
    plans = []
    for template, stops, dwells in sequences:
        endpoints = ["origin", *(p.place_id for p in stops), "origin"]
        legs = [by_leg.get((a, b)) for a, b in zip(endpoints, endpoints[1:], strict=False)]
        if any(leg is None for leg in legs):
            continue
        projected = controls.departure_at.astimezone(UTC)
        timed_stops = []
        try:
            for index, (place, dwell) in enumerate(zip(stops, dwells, strict=True)):
                duration = legs[index].duration_seconds
                projected = (
                    projected + timedelta(seconds=duration)
                    if (projected is not None and duration is not None)
                    else None
                )
                timed_stops.append(PlanStop(place=place, arrival_at=projected, dwell_seconds=dwell))
                if projected is not None:
                    projected += timedelta(seconds=dwell)
            identity = json.dumps(
                [
                    template,
                    controls.model_dump(mode="json"),
                    [p.place_id for p in stops],
                    [r.route_id for r in legs],
                ]
            )
            plan = CandidatePlan(
                plan_id=f"template-{template}:"
                + hashlib.sha256(identity.encode()).hexdigest()[:24],
                origin=controls.origin,
                departure_at=controls.departure_at,
                stops=tuple(timed_stops),
                routes=tuple(legs),
            )
        except (ValueError, OverflowError):
            continue
        if template != "B" and any(
            not public_space(
                stop.place,
                max(as_of, stop.arrival_at or as_of) + timedelta(seconds=stop.dwell_seconds),
                allow_fixture,
            )
            for stop in plan.stops
            if "park" in (stop.place.categories or ())
        ):
            continue
        validation = validate_plan(plan, controls, as_of=as_of, allow_fixture=allow_fixture)
        if next(
            c for c in validation.checks if c.code == CheckCode.GROUNDING
        ).status == "PASS" and all(
            has_category_evidence(stop.place, max(as_of, stop.arrival_at or as_of), allow_fixture)
            for stop in plan.stops
        ):
            plans.append(plan)
    return tuple(plans) or CompilationFailure(
        code="NO_GROUNDED_CANDIDATES", message="No grounded complete template route chain available"
    )
