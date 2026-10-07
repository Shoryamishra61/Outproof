"""Pure hard policy over supplied facts. No discovery, compilation, or model I/O."""

import json
from datetime import UTC, datetime, timedelta

from pydantic import AwareDatetime, TypeAdapter, ValidationError

from ground_rule.models import (
    CandidatePlan,
    CheckCode,
    ConstraintSet,
    Evidence,
    PriceConfidence,
    ValidationCheck,
    ValidationResult,
)

# Maximum age without a shorter provider expiry; future observations are invalid.
MAX_AGE = {
    "identity": timedelta(days=30),
    "coordinates": timedelta(days=30),
    "categories": timedelta(days=7),
    "excluded_categories": timedelta(days=7),
    "dietary_options": timedelta(days=7),
    "price": timedelta(hours=24),
    "opening_window": timedelta(hours=24),
    "walking_route": timedelta(minutes=15),
}


def validate_plan(
    plan: CandidatePlan,
    constraints: ConstraintSet,
    *,
    as_of: datetime,
    allow_fixture: bool = False,
) -> ValidationResult:
    """All eleven canonical checks must pass. UNKNOWN is a hard rejection.

    Evidence wire values and age limits are documented in docs/POLICY.md.
    Inputs are revalidated, including unsafe Pydantic model_copy mutations.
    """
    now = TypeAdapter(AwareDatetime).validate_python(as_of).astimezone(UTC)
    constraints = ConstraintSet.model_validate(constraints)
    try:
        plan = CandidatePlan.model_validate(plan)
    except ValidationError:
        return ValidationResult(
            plan_id=plan.plan_id,
            accepted=False,
            checks=tuple(
                ValidationCheck(
                    code=code,
                    status="FAIL",
                    hard=True,
                    message="Candidate contract invalid; no feasibility assertion permitted",
                    evidence_ids=(),
                )
                for code in CheckCode
            ),
        )

    sources = [e for route in plan.routes for e in route.evidence]
    for stop in plan.stops:
        sources.extend(stop.place.evidence)
        if stop.place.price:
            sources.extend(stop.place.price.evidence)
        for window in stop.place.opening_windows or ():
            sources.extend(window.evidence)
    by_id: dict[str, Evidence] = {}
    by_fact: dict[tuple[str, str], str] = {}
    conflicts = False
    for source in sources:
        if source.evidence_id in by_id and by_id[source.evidence_id] != source:
            conflicts = True
        by_id[source.evidence_id] = source
        if source.field in MAX_AGE and source.field != "opening_window":
            key = (source.subject_id, source.field)
            value = json.dumps(source.value, sort_keys=True)
            if key in by_fact and by_fact[key] != value:
                conflicts = True
            by_fact[key] = value

    checks: list[ValidationCheck] = []

    def check(code: CheckCode, passed: bool, message: str, ids: list[str]) -> None:
        checks.append(
            ValidationCheck(
                code=code,
                status="PASS" if passed else "FAIL",
                hard=True,
                message=message,
                evidence_ids=tuple(dict.fromkeys(ids)),
            )
        )

    def fact(
        records: tuple[Evidence, ...],
        subject: str,
        field: str,
        expected: object,
        used_at: datetime,
        ids: list[str],
    ) -> bool:
        matching = [e for e in records if e.field == field]
        ids.extend(e.evidence_id for e in matching)
        permitted = {"DIRECT", "SERPAPI", "OSM"}
        if field == "walking_route":
            permitted = {"DIRECT", "VALHALLA"}
        if allow_fixture:
            permitted.add("FIXTURE")
        # Community/low-confidence evidence never establishes a hard fact.
        return (
            bool(matching)
            and not conflicts
            and all(
                e.subject_id == subject
                and json.dumps(e.value, sort_keys=True) == json.dumps(expected, sort_keys=True)
                and e.source in permitted
                and e.confidence in {"HIGH", "MEDIUM"}
                and e.observed_at.astimezone(UTC) <= now
                and max(now, used_at.astimezone(UTC)) - e.observed_at.astimezone(UTC)
                < MAX_AGE[field]
                and (
                    e.expires_at is None
                    or max(now, used_at.astimezone(UTC)) < e.expires_at.astimezone(UTC)
                )
                for e in matching
            )
        )

    ground_ids: list[str] = []
    grounded = not conflicts and (constraints.origin is None or constraints.origin == plan.origin)
    for stop in plan.stops:
        place = stop.place
        grounded &= bool(place.provider_id and place.name and place.coordinates)
        grounded &= fact(
            place.evidence,
            place.place_id,
            "identity",
            {"provider": place.provider, "provider_id": place.provider_id, "name": place.name},
            now,
            ground_ids,
        )
        grounded &= fact(
            place.evidence,
            place.place_id,
            "coordinates",
            place.coordinates.model_dump() if place.coordinates else None,
            now,
            ground_ids,
        )
        if place.provider == "FIXTURE" and not allow_fixture:
            grounded = False
    check(
        CheckCode.GROUNDING,
        grounded,
        "Provider identity and coordinates must be evidenced",
        ground_ids,
    )

    route_ids: list[str] = []
    routed = True
    locations = {"origin": plan.origin}
    locations.update({stop.place.place_id: stop.place.coordinates for stop in plan.stops})
    for route in plan.routes:
        from_coordinates = locations[route.from_id]
        to_coordinates = locations[route.to_id]
        routed &= (
            from_coordinates is not None
            and to_coordinates is not None
            and route.reachable
            and fact(
                route.evidence,
                route.route_id,
                "walking_route",
                {
                    "from_id": route.from_id,
                    "to_id": route.to_id,
                    "from_coordinates": from_coordinates.model_dump(),
                    "to_coordinates": to_coordinates.model_dump(),
                    "reachable": True,
                    "duration_seconds": route.duration_seconds,
                    "distance_meters": route.distance_meters,
                },
                now,
                route_ids,
            )
        )
    check(
        CheckCode.ROUTING,
        routed,
        "Every leg including return needs reachable walking facts",
        route_ids,
    )
    total = plan.total_duration_seconds
    departure_matches = constraints.departure_at is None or (
        constraints.departure_at.astimezone(UTC) == plan.departure_at.astimezone(UTC)
    )
    check(
        CheckCode.DURATION,
        routed
        and departure_matches
        and total is not None
        and total <= constraints.duration_max_minutes * 60,
        "Full elapsed duration includes all routes and all dwells; departure is authoritative",
        route_ids,
    )
    returned = plan.departure_at.astimezone(UTC) + timedelta(seconds=total) if total else None
    check(
        CheckCode.RETURN_TRIP,
        routed
        and returned is not None
        and departure_matches
        and (
            constraints.return_by_local is None
            or returned <= constraints.return_by_local.astimezone(UTC)
        ),
        "Complete round trip must meet the explicit return deadline in UTC",
        route_ids,
    )
    walking_seconds = sum(route.duration_seconds or 0 for route in plan.routes)
    check(
        CheckCode.WALKING,
        routed
        and plan.walking_distance_meters is not None
        and (
            constraints.max_walking_minutes is None
            or walking_seconds <= constraints.max_walking_minutes * 60
        )
        and (
            constraints.max_walking_meters is None
            or plan.walking_distance_meters <= constraints.max_walking_meters
        ),
        "All walking legs count against both supplied maxima",
        route_ids,
    )

    price_ids: list[str] = []
    price_allowed = True
    currencies: set[str] = set()
    # Compare group totals, avoiding division/rounding of per-person limits.
    totals_by_currency: dict[str, int] = {}
    scope_known = True
    for stop in plan.stops:
        for expense in stop.place.evidence:
            if expense.field == "optional_expenses":
                price_ids.append(expense.evidence_id)
                price_allowed &= isinstance(expense.value, list) and all(
                    isinstance(item, dict)
                    and item.get("mandatory") is False
                    and isinstance(item.get("description"), str)
                    and bool(item["description"].strip())
                    and "price" in item
                    for item in expense.value
                )
        price = stop.place.price
        if price is None or price.upper is None or price.lower is None:
            price_allowed = False
            continue
        currencies.add(price.upper.currency_code)
        price_allowed &= fact(
            price.evidence,
            stop.place.place_id,
            "price",
            {
                "currency_code": price.upper.currency_code,
                "lower_minor_units": price.lower.minor_units,
                "upper_minor_units": price.upper.minor_units,
                "scope": price.scope,
                "covers_all_mandatory_costs": True,
            },
            stop.arrival_at or now,
            price_ids,
        )
        price_allowed &= price.confidence != PriceConfidence.UNKNOWN
        if constraints.strict_budget:
            price_allowed &= price.confidence in {PriceConfidence.VERIFIED, PriceConfidence.BOUNDED}
        if price.confidence == PriceConfidence.VERIFIED:
            price_allowed &= price.lower == price.upper
        if price.scope == "PER_PERSON":
            if constraints.party_size is None:
                scope_known = False
                continue
            else:
                amount = price.upper.minor_units * constraints.party_size
        else:
            amount = price.upper.minor_units
        currency = price.upper.currency_code
        totals_by_currency[currency] = totals_by_currency.get(currency, 0) + amount
    currency_valid = len(currencies) == 1 and (
        constraints.currency_code is None or currencies == {constraints.currency_code}
    )
    mandatory_total = (
        next(iter(totals_by_currency.values())) if currency_valid and scope_known else None
    )
    check(
        CheckCode.CURRENCY,
        currency_valid,
        "Costs must share the budget currency; no conversion",
        price_ids,
    )
    check(
        CheckCode.PRICE_CONFIDENCE,
        price_allowed,
        "Complete mandatory cost needs current positive evidence",
        price_ids,
    )
    limit = constraints.budget_minor_units
    if limit is not None and constraints.budget_scope == "PER_PERSON":
        if constraints.party_size is None:
            scope_known = False
        else:
            limit *= constraints.party_size
    check(
        CheckCode.BUDGET,
        price_allowed
        and currency_valid
        and scope_known
        and mandatory_total is not None
        and (limit is None or mandatory_total <= limit),
        "Conservative mandatory group total must fit the same-currency scoped cap",
        price_ids,
    )

    hours_ids: list[str] = []
    opened = routed
    for stop in plan.stops:
        if stop.arrival_at is None:
            opened = False
            continue
        arrival = stop.arrival_at.astimezone(UTC)
        end = arrival + timedelta(seconds=stop.dwell_seconds)
        usable = []
        for window in stop.place.opening_windows or ():
            supported = fact(
                window.evidence,
                stop.place.place_id,
                "opening_window",
                [window.opens_at.isoformat(), window.closes_at.isoformat()],
                end,
                hours_ids,
            )
            usable.append(
                supported
                and window.opens_at.astimezone(UTC) <= arrival
                and end <= window.closes_at.astimezone(UTC)
            )
        # Conflicting attestations, even in an unused window, fail closed.
        opened &= any(usable) and all(
            fact(
                w.evidence,
                stop.place.place_id,
                "opening_window",
                [w.opens_at.isoformat(), w.closes_at.isoformat()],
                end,
                hours_ids,
            )
            for w in stop.place.opening_windows or ()
        )
    check(
        CheckCode.OPENING_HOURS,
        opened,
        "Known hours must cover arrival through required dwell",
        hours_ids,
    )

    exclusion_ids: list[str] = []
    diet_ids: list[str] = []
    excluded = True
    diet = True
    for hard in constraints.hard_constraints:
        value = hard.value.casefold().strip()
        if hard.kind in {"UNSUPPORTED", "ACCESSIBILITY"}:
            diet = False
        elif hard.kind == "DIETARY":
            if value not in {"vegetarian", "vegan"}:
                diet = False
                continue
            for stop in plan.stops:
                options = stop.place.dietary_options
                diet &= (
                    options is not None
                    and value in options
                    and fact(
                        stop.place.evidence,
                        stop.place.place_id,
                        "dietary_options",
                        list(options),
                        stop.arrival_at or now,
                        diet_ids,
                    )
                )
        elif hard.kind == "EXCLUDE_CATEGORY":
            for stop in plan.stops:
                place = stop.place
                records = [e for e in place.evidence if e.field == "excluded_categories"]
                # Positive absence evidence is required, including containment/chain/alcohol.
                absent = records[0].value if records else None
                excluded &= (
                    place.categories is not None
                    and value not in {category.casefold().strip() for category in place.categories}
                    and fact(
                        place.evidence,
                        place.place_id,
                        "categories",
                        list(place.categories),
                        stop.arrival_at or now,
                        exclusion_ids,
                    )
                    and isinstance(absent, list)
                    and value in absent
                    and fact(
                        place.evidence,
                        place.place_id,
                        "excluded_categories",
                        absent,
                        stop.arrival_at or now,
                        exclusion_ids,
                    )
                )
    check(
        CheckCode.EXCLUSIONS,
        excluded,
        "Hard exclusions require positive absence and category evidence",
        exclusion_ids,
    )
    check(
        CheckCode.DIETARY,
        diet,
        "Diet needs positive evidence; allergy/accessibility guarantees unsupported",
        diet_ids,
    )
    return ValidationResult(
        plan_id=plan.plan_id,
        accepted=all(item.status == "PASS" for item in checks),
        checks=tuple(checks),
    )
