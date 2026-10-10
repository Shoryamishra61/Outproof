"""Provider orchestration. Only unchanged-policy accepted plans leave this module."""

import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from time import perf_counter

from ground_rule.hours import windows_from_hours
from ground_rule.models import (
    CandidatePlan,
    CompilationFailure,
    ConstraintSet,
    Contract,
    PlaceCandidate,
    ValidationResult,
)
from ground_rule.plans import build_candidates, has_category_evidence
from ground_rule.policy import validate_plan
from ground_rule.proof import place_sources

from app.enrichment import EnrichmentProvider, EnrichmentResult
from app.places import MAX_DISCOVERY_RADIUS_METERS, PlacesProvider
from app.routing import RoutingProvider

logger = logging.getLogger(__name__)


class ValidCandidatePlan(Contract):
    plan: CandidatePlan
    validation: ValidationResult


def materialize_hours(
    plan: CandidatePlan, *, as_of: datetime, allow_fixture: bool
) -> CandidatePlan:
    stops = []
    for stop in plan.stops:
        place = stop.place
        raw = [e for e in place.evidence if e.field == "opening_hours"]
        zones = [e for e in place.evidence if e.field == "timezone"]
        if place.opening_windows is None and raw and zones and stop.arrival_at:
            windows = []
            permitted = {"OSM", "DIRECT", "SERPAPI"} | ({"FIXTURE"} if allow_fixture else set())
            valid_zone = len(zones) == 1 and (
                zones[0].subject_id == place.place_id
                and zones[0].source in permitted
                and zones[0].confidence in {"HIGH", "MEDIUM"}
                and timedelta(0)
                <= as_of.astimezone(UTC) - zones[0].observed_at.astimezone(UTC)
                < timedelta(days=30)
                and (
                    zones[0].expires_at is None
                    or stop.arrival_at.astimezone(UTC) + timedelta(seconds=stop.dwell_seconds)
                    < zones[0].expires_at.astimezone(UTC)
                )
            )
            for record in raw:
                if (
                    not valid_zone
                    or not isinstance(zones[0].value, str)
                    or any(e.value != record.value for e in raw)
                ):
                    continue
                supported = windows_from_hours(
                    record,
                    stop.arrival_at,
                    stop.arrival_at.astimezone(UTC) + timedelta(seconds=stop.dwell_seconds),
                    zones[0].value,
                )
                if supported:
                    windows.extend(supported)
            place = PlaceCandidate.model_validate(
                place.model_copy(update={"opening_windows": tuple(windows)})
            )
        stops.append(stop.model_copy(update={"place": place}))
    return CandidatePlan.model_validate(plan.model_copy(update={"stops": tuple(stops)}))


async def valid_candidate_plans(
    controls: ConstraintSet,
    discovery: PlacesProvider,
    enrichment: EnrichmentProvider,
    routing: RoutingProvider,
    *,
    as_of: datetime,
    allow_fixture: bool = False,
    clock: Callable[[], datetime] | None = None,
) -> tuple[ValidCandidatePlan, ...] | CompilationFailure:
    controls = ConstraintSet.model_validate(controls)
    if controls.origin is None or controls.departure_at is None:
        return CompilationFailure(
            code="UNSUPPORTED_CONSTRAINT", message="Origin and departure required"
        )
    started = perf_counter()
    # Discovery scope does not assert walking feasibility; both routed legs must still pass policy.
    discovered = await discovery.discover(
        controls.origin, radius_meters=MAX_DISCOVERY_RADIUS_METERS
    )
    if isinstance(discovered, CompilationFailure):
        return discovered
    by_id: dict[str, PlaceCandidate] = {}
    identities: dict[tuple[str, str | None], str] = {}
    for place in discovered:
        place = PlaceCandidate.model_validate(place)
        identity = (place.provider, place.provider_id)
        if (place.place_id in by_id and by_id[place.place_id] != place) or (
            identity in identities and identities[identity] != place.place_id
        ):
            return CompilationFailure(
                code="NO_GROUNDED_CANDIDATES", message="Conflicting duplicate identity"
            )
        by_id[place.place_id] = place
        identities[identity] = place.place_id
    logger.info("discovery count=%s elapsed_ms=%.2f", len(by_id), (perf_counter() - started) * 1000)
    places = []
    failure = None
    # Bounded candidate exploration; up to 12 places proceed to routing.
    for original in sorted(by_id.values(), key=lambda p: p.place_id):
        enriched = await enrichment.enrich(original)
        if isinstance(enriched, CompilationFailure):
            failure = enriched
            continue
        if isinstance(enriched, EnrichmentResult):
            enriched = EnrichmentResult.model_validate(enriched)
            if enriched.binding.status != "MATCH" or enriched.contradictions:
                continue
            candidate = enriched.place.model_copy(
                update={
                    "evidence": enriched.place.evidence + enriched.binding.evidence,
                }
            )
        else:
            candidate = enriched
        candidate = PlaceCandidate.model_validate(candidate)
        if (
            candidate.place_id,
            candidate.provider,
            candidate.provider_id,
            candidate.name,
            candidate.coordinates,
        ) != (
            original.place_id,
            original.provider,
            original.provider_id,
            original.name,
            original.coordinates,
        ):
            continue
        sources = {e.evidence_id: e for e in place_sources(candidate)}
        if any(sources.get(e.evidence_id) != e for e in place_sources(original)):
            continue
        places.append(candidate)
    # Missing admission/price or hours cannot be repaired by routing or ranking.
    prefilter_as_of = max(as_of, clock()) if clock else as_of
    places = [
        p
        for p in places
        if p.price is not None
        and p.price.upper is not None
        and has_category_evidence(p, prefilter_as_of, allow_fixture)
        and (
            p.opening_windows
            or (
                p.opening_windows is None
                and any(e.field == "opening_hours" for e in p.evidence)
                and any(e.field == "timezone" for e in p.evidence)
            )
        )
    ][:12]
    if not places:
        return failure or ()
    legs = [("origin", p.place_id, controls.origin, p.coordinates) for p in places]
    legs += [(p.place_id, "origin", p.coordinates, controls.origin) for p in places]
    legs += [
        (a.place_id, b.place_id, a.coordinates, b.coordinates)
        for a in places
        if {"cafe", "restaurant"} & set(a.categories or ())
        for b in places
        if "park" in (b.categories or ()) and a.place_id != b.place_id
    ]
    routes = []
    for from_id, to_id, start, end in legs:
        if start is None or end is None:
            continue
        route = await routing.route(from_id, to_id, start, end)
        if isinstance(route, CompilationFailure):
            failure = route
        else:
            routes.append(route)
    eval_as_of = max(as_of, clock()) if clock else as_of
    built = build_candidates(
        tuple(places), tuple(routes), controls, as_of=eval_as_of, allow_fixture=allow_fixture
    )
    if isinstance(built, CompilationFailure):
        return failure or built
    valid = []
    for plan in built:
        plan = materialize_hours(plan, as_of=eval_as_of, allow_fixture=allow_fixture)
        validation = validate_plan(plan, controls, as_of=eval_as_of, allow_fixture=allow_fixture)
        if validation.accepted:
            valid.append(ValidCandidatePlan(plan=plan, validation=validation))
        else:
            logger.info(
                "rejection checks=%s", [c.code for c in validation.checks if c.status != "PASS"]
            )
    logger.info(
        "validation valid_count=%s elapsed_ms=%.2f", len(valid), (perf_counter() - started) * 1000
    )
    return tuple(valid)
