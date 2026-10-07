"""Fictional policy cases. No venue, price, route, or outing has been observed."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import Any

NOW = datetime(2026, 10, 6, 8, tzinfo=UTC)


def evidence(subject: str, field: str, value: object) -> dict[str, Any]:
    return {
        "evidence_id": f"{subject}:{field}",
        "subject_id": subject,
        "field": field,
        "value": value,
        "source": "FIXTURE",
        "source_ref": "synthetic-policy-fixture",
        "observed_at": NOW.isoformat(),
        "expires_at": None,
        "confidence": "HIGH" if value is not None else "UNKNOWN",
    }


def baseline() -> tuple[dict[str, Any], dict[str, Any]]:
    controls = {
        "currency_code": "INR",
        "budget_minor_units": 50000,
        "budget_scope": "PER_PERSON",
        "duration_max_minutes": 90,
        "party_mode": "GROUP",
        "party_size": 4,
        "vibes": ["Talk"],
        "hard_constraints": [],
        "soft_constraints": [],
        "max_walking_minutes": None,
        "max_walking_meters": None,
        "return_by_local": None,
        "locale": "en-IN",
        "origin": None,
        "departure_at": None,
        "strict_budget": True,
    }
    place = {
        "place_id": "fixture:stop",
        "provider": "FIXTURE",
        "provider_id": "fictional",
        "name": "Synthetic public space",
        "coordinates": {"latitude": 12.8, "longitude": 80.0},
        "categories": ["park"],
        "dietary_options": ["vegetarian", "vegan"],
        "price": {
            "confidence": "VERIFIED",
            "lower": {"currency_code": "INR", "minor_units": 42000},
            "upper": {"currency_code": "INR", "minor_units": 42000},
            "scope": "PER_PERSON",
            "evidence": [],
        },
        "opening_windows": [
            {
                "opens_at": NOW.isoformat(),
                "closes_at": (NOW + timedelta(hours=3)).isoformat(),
                "evidence": [],
            }
        ],
        "evidence": [],
    }
    plan = {
        "plan_id": "synthetic-policy",
        "origin": {"latitude": 12.81, "longitude": 80.01},
        "departure_at": NOW.isoformat(),
        "stops": [
            {
                "place": place,
                "arrival_at": (NOW + timedelta(minutes=10)).isoformat(),
                "dwell_seconds": 2400,
            }
        ],
        "routes": [
            {
                "route_id": "out",
                "from_id": "origin",
                "to_id": "fixture:stop",
                "reachable": True,
                "duration_seconds": 600,
                "distance_meters": 650.0,
                "evidence": [],
            },
            {
                "route_id": "back",
                "from_id": "fixture:stop",
                "to_id": "origin",
                "reachable": True,
                "duration_seconds": 600,
                "distance_meters": 650.0,
                "evidence": [],
            },
        ],
    }
    refresh(plan)
    return plan, controls


def refresh(plan: dict[str, Any]) -> None:
    """Rebuild positive fixture evidence after intentional fact changes."""
    projected = datetime.fromisoformat(plan["departure_at"]).astimezone(UTC)
    locations = {"origin": plan["origin"]}
    locations.update(
        {stop["place"]["place_id"]: stop["place"]["coordinates"] for stop in plan["stops"]}
    )
    for index, route in enumerate(plan["routes"]):
        route["evidence"] = [
            evidence(
                route["route_id"],
                "walking_route",
                {
                    key: route[key]
                    for key in (
                        "from_id",
                        "to_id",
                        "reachable",
                        "duration_seconds",
                        "distance_meters",
                    )
                }
                | {
                    "from_coordinates": locations[route["from_id"]],
                    "to_coordinates": locations[route["to_id"]],
                },
            )
        ]
        if projected is not None and route["duration_seconds"] is not None:
            projected += timedelta(seconds=route["duration_seconds"])
        else:
            projected = None
        if index < len(plan["stops"]):
            stop = plan["stops"][index]
            stop["arrival_at"] = projected.isoformat() if projected else None
            if projected:
                projected += timedelta(seconds=stop["dwell_seconds"])
    for stop in plan["stops"]:
        place = stop["place"]
        place["evidence"] = [
            evidence(
                place["place_id"],
                "identity",
                {key: place[key] for key in ("provider", "provider_id", "name")},
            ),
            evidence(place["place_id"], "coordinates", place["coordinates"]),
            evidence(place["place_id"], "categories", place["categories"]),
            evidence(place["place_id"], "excluded_categories", ["mall", "alcohol", "chain"]),
            evidence(place["place_id"], "dietary_options", place["dietary_options"]),
        ]
        price = place["price"]
        if price and price["upper"]:
            price["evidence"] = [
                evidence(
                    place["place_id"],
                    "price",
                    {
                        "currency_code": price["upper"]["currency_code"],
                        "lower_minor_units": price["lower"]["minor_units"],
                        "upper_minor_units": price["upper"]["minor_units"],
                        "scope": price["scope"],
                        "covers_all_mandatory_costs": True,
                    },
                )
            ]
        for window in place["opening_windows"] or []:
            window["evidence"] = [
                evidence(
                    place["place_id"], "opening_window", [window["opens_at"], window["closes_at"]]
                )
            ]


def policy_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(
        name: str,
        plan: dict[str, Any],
        controls: dict[str, Any],
        accepted: bool,
        failure: str | None = None,
    ) -> None:
        cases.append(
            {
                "id": name,
                "synthetic": True,
                "plan": deepcopy(plan),
                "constraints": deepcopy(controls),
                "accepted": accepted,
                "failure": failure,
            }
        )

    plan, controls = baseline()
    add("420-per-person-under-500", plan, controls, True)
    for amount, accepted in [(49999, True), (50000, True), (50001, False), (52000, False)]:
        p, c = baseline()
        p["stops"][0]["place"]["price"]["lower"]["minor_units"] = amount
        p["stops"][0]["place"]["price"]["upper"]["minor_units"] = amount
        refresh(p)
        add(f"mandatory-amount-{amount}", p, c, accepted, None if accepted else "BUDGET")
    for confidence, upper, accepted in [
        ("ESTIMATED", 35000, False),
        ("BOUNDED", 48000, True),
        ("BOUNDED", 55000, False),
    ]:
        p, c = baseline()
        price = p["stops"][0]["place"]["price"]
        price["confidence"] = confidence
        price["lower"]["minor_units"] = 35000
        price["upper"]["minor_units"] = upper
        refresh(p)
        add(
            f"{confidence}-{upper}",
            p,
            c,
            accepted,
            None if accepted else "PRICE_CONFIDENCE" if confidence == "ESTIMATED" else "BUDGET",
        )
    for absent in [True, False]:
        p, c = baseline()
        p["stops"][0]["place"]["price"] = (
            None
            if absent
            else {
                "confidence": "UNKNOWN",
                "lower": None,
                "upper": None,
                "scope": None,
                "evidence": [],
            }
        )
        add(f"unknown-price-{absent}", p, c, False, "PRICE_CONFIDENCE")
    for scope, budget, amount, accepted in [
        ("TOTAL", 80000, 45000, False),
        ("PER_PERSON", 45000, 80000, True),
        ("TOTAL", 45000, 80000, False),
    ]:
        p, c = baseline()
        price = p["stops"][0]["place"]["price"]
        price["scope"] = "PER_PERSON" if amount == 45000 else "TOTAL"
        price["lower"]["minor_units"] = price["upper"]["minor_units"] = amount
        c.update(budget_scope=scope, budget_minor_units=budget)
        refresh(p)
        add(f"scope-{scope}-{budget}-{amount}", p, c, accepted, None if accepted else "BUDGET")
    for currency in ["USD", "GBP", "JPY"]:
        p, c = baseline()
        price = p["stops"][0]["place"]["price"]
        price["lower"]["currency_code"] = price["upper"]["currency_code"] = currency
        refresh(p)
        add(f"currency-{currency}", p, c, False, "CURRENCY")
    p, c = baseline()
    price = p["stops"][0]["place"]["price"]
    price["lower"]["minor_units"] = price["upper"]["minor_units"] = 0
    c["budget_minor_units"] = 0
    refresh(p)
    add("confirmed-free", p, c, True)
    price["evidence"][0]["value"]["covers_all_mandatory_costs"] = False
    add("unknown-ticket-on-free-outing", p, c, False, "PRICE_CONFIDENCE")
    for outbound, dwell, back, accepted in [
        (20, 50, 25, False),
        (20, 45, 25, True),
        (20, 46, 25, False),
    ]:
        p, c = baseline()
        p["routes"][0]["duration_seconds"] = outbound * 60
        p["routes"][1]["duration_seconds"] = back * 60
        p["stops"][0]["dwell_seconds"] = dwell * 60
        refresh(p)
        add(f"duration-{outbound}-{dwell}-{back}", p, c, accepted, None if accepted else "DURATION")
    p, c = baseline()
    p["routes"].pop()
    add("missing-return", p, c, False, "STRUCTURE")
    for leg in [0, 1]:
        p, c = baseline()
        p["routes"][leg].update(reachable=False, duration_seconds=None, distance_meters=None)
        refresh(p)
        add(f"unreachable-{leg}", p, c, False, "ROUTING")
    p, c = baseline()
    second = deepcopy(p["stops"][0])
    second["place"]["place_id"] = "fixture:second"
    second["place"]["price"]["lower"]["minor_units"] = 10000
    second["place"]["price"]["upper"]["minor_units"] = 10000
    second["dwell_seconds"] = 60
    p["stops"].append(second)
    middle = deepcopy(p["routes"][1])
    middle.update(route_id="middle", to_id="fixture:second", duration_seconds=60)
    p["routes"].insert(1, middle)
    p["routes"][-1]["from_id"] = "fixture:second"
    refresh(p)
    add("420-plus-mandatory-100", p, c, False, "BUDGET")
    mixed = deepcopy(p)
    second_price = mixed["stops"][1]["place"]["price"]
    second_price["lower"]["currency_code"] = second_price["upper"]["currency_code"] = "USD"
    refresh(mixed)
    add("mixed-currencies-between-stops", mixed, c, False, "CURRENCY")
    p["routes"][1].update(reachable=False, duration_seconds=None, distance_meters=None)
    refresh(p)
    add("unreachable-intermediate", p, c, False, "ROUTING")
    for close, accepted in [(9, False), (49, False), (50, True)]:
        p, c = baseline()
        p["stops"][0]["place"]["opening_windows"][0]["closes_at"] = (
            NOW + timedelta(minutes=close)
        ).isoformat()
        refresh(p)
        add(f"closing-at-{close}", p, c, accepted, None if accepted else "OPENING_HOURS")
    p, c = baseline()
    p["stops"][0]["place"]["opening_windows"] = None
    add("unknown-hours", p, c, False, "OPENING_HOURS")
    for category in ["mall", "alcohol", "chain"]:
        p, c = baseline()
        c["hard_constraints"] = [{"kind": "EXCLUDE_CATEGORY", "value": category}]
        add(f"positive-exclusion-{category}", p, c, True)
        p["stops"][0]["place"]["categories"] = ["restaurant", category]
        refresh(p)
        add(f"forbidden-{category}", p, c, False, "EXCLUSIONS")
    p, c = baseline()
    c["hard_constraints"] = [{"kind": "EXCLUDE_CATEGORY", "value": "mall"}]
    p["stops"][0]["place"]["evidence"] = [
        e for e in p["stops"][0]["place"]["evidence"] if e["field"] != "excluded_categories"
    ]
    add("absence-is-not-exclusion-proof", p, c, False, "EXCLUSIONS")
    for dietary in ["vegetarian", "vegan"]:
        p, c = baseline()
        c["hard_constraints"] = [{"kind": "DIETARY", "value": dietary}]
        add(f"supported-{dietary}", p, c, True)
        p["stops"][0]["place"]["dietary_options"] = None
        refresh(p)
        add(f"unsupported-{dietary}", p, c, False, "DIETARY")
    for kind, value in [
        ("DIETARY", "allergy safe"),
        ("ACCESSIBILITY", "wheelchair"),
        ("UNSUPPORTED", "safety guarantee"),
    ]:
        p, c = baseline()
        c["hard_constraints"] = [{"kind": kind, "value": value}]
        add(value, p, c, False, "DIETARY")
    for field, limit, accepted in [
        ("max_walking_minutes", 19, False),
        ("max_walking_minutes", 20, True),
        ("max_walking_meters", 1299.0, False),
        ("max_walking_meters", 1300.0, True),
    ]:
        p, c = baseline()
        c[field] = limit
        add(f"{field}-{limit}", p, c, accepted, None if accepted else "WALKING")
    for minutes, accepted in [(59, False), (60, True)]:
        p, c = baseline()
        c["return_by_local"] = (NOW + timedelta(minutes=minutes)).isoformat()
        add(f"return-deadline-{minutes}", p, c, accepted, None if accepted else "RETURN_TRIP")
    p, c = baseline()
    p["departure_at"] = "2026-11-01T01:55:00-04:00"
    refresh(p)
    c["return_by_local"] = "2026-11-01T01:55:00-05:00"
    # Evidence must still be fresh at validation in November.
    for stop in p["stops"]:
        window = stop["place"]["opening_windows"][0]
        window.update(opens_at="2026-11-01T01:00:00-04:00", closes_at="2026-11-01T03:00:00-05:00")
    refresh(p)
    for source in all_sources(p):
        source["observed_at"] = "2026-11-01T05:55:00+00:00"
    add("repeated-local-hour", p, c, True)
    cases[-1]["as_of"] = "2026-11-01T05:55:00+00:00"
    p, c = baseline()
    p["stops"][0]["place"]["evidence"].append(
        evidence(
            "fixture:stop",
            "optional_expenses",
            [{"description": "dessert", "price": None, "mandatory": False}],
        )
    )
    add("optional-unknown-dessert", p, c, True)
    for field in [
        "identity",
        "coordinates",
        "categories",
        "dietary_options",
        "price",
        "opening_window",
        "walking_route",
    ]:
        p, c = baseline()
        c["hard_constraints"] = [
            {"kind": "EXCLUDE_CATEGORY", "value": "mall"},
            {"kind": "DIETARY", "value": "vegetarian"},
        ]
        targets = [e for e in all_sources(p) if e["field"] == field]
        for e in targets:
            e["observed_at"] = (NOW - timedelta(days=40)).isoformat()
        add(f"stale-{field}", p, c, False)
    for mutation in [
        "conflicting-id",
        "conflicting-price",
        "wrong-subject",
        "future",
        "expired",
        "low-confidence",
        "community",
        "missing-price-proof",
        "incomplete-cost",
    ]:
        p, c = baseline()
        price = p["stops"][0]["place"]["price"]
        e = price["evidence"][0]
        if mutation in {"conflicting-id", "conflicting-price"}:
            other = deepcopy(e)
            other["value"]["upper_minor_units"] = 1
            if mutation == "conflicting-price":
                other["evidence_id"] += ":conflict"
            price["evidence"].append(other)
        elif mutation == "wrong-subject":
            e["subject_id"] = "different-place"
        elif mutation == "future":
            e["observed_at"] = (NOW + timedelta(seconds=1)).isoformat()
        elif mutation == "expired":
            e["observed_at"] = (NOW - timedelta(hours=1)).isoformat()
            e["expires_at"] = NOW.isoformat()
        elif mutation == "low-confidence":
            e["confidence"] = "LOW"
        elif mutation == "community":
            e["source"] = "COMMUNITY"
        elif mutation == "missing-price-proof":
            price["evidence"] = []
        else:
            e["value"]["covers_all_mandatory_costs"] = False
        add(mutation, p, c, False, "STRUCTURE" if mutation == "missing-price-proof" else None)
    for field in ["provider_id", "coordinates", "name"]:
        p, c = baseline()
        p["stops"][0]["place"][field] = None
        refresh(p)
        add(f"ungrounded-{field}", p, c, False, "GROUNDING")
    p, c = baseline()
    c["party_size"] = None
    add("unknown-party-size", p, c, False, "BUDGET")
    p, c = baseline()
    c["departure_at"] = (NOW + timedelta(minutes=1)).isoformat()
    add("structured-departure-mutated", p, c, False, "DURATION")
    p, c = baseline()
    price = p["stops"][0]["place"]["price"]
    price["lower"]["minor_units"] = price["upper"]["minor_units"] = 0
    refresh(p)
    price["evidence"][0]["value"]["upper_minor_units"] = False
    add("boolean-is-not-zero-price-evidence", p, c, False, "PRICE_CONFIDENCE")
    for mandatory in [True, None, "false", 0]:
        p, c = baseline()
        p["stops"][0]["place"]["evidence"].append(
            evidence(
                "fixture:stop",
                "optional_expenses",
                [{"description": "ticket", "price": None, "mandatory": mandatory}],
            )
        )
        add(f"invalid-optionality-{mandatory}", p, c, False, "PRICE_CONFIDENCE")
    p, c = baseline()
    e = deepcopy(p["stops"][0]["place"]["price"]["evidence"][0])
    e["evidence_id"] += ":elsewhere"
    e["value"]["upper_minor_units"] = 1
    p["stops"][0]["place"]["evidence"].append(e)
    add("conflicting-fact-in-another-evidence-bucket", p, c, False)
    p, c = baseline()
    p["routes"][0]["evidence"][0]["source"] = "OSM"
    add("osm-is-not-routing-truth", p, c, False, "ROUTING")
    p, c = baseline()
    price = p["stops"][0]["place"]["price"]
    price["confidence"] = "ESTIMATED"
    c["strict_budget"] = False
    add("explicit-nonstrict-estimate", p, c, True)
    p, c = baseline()
    price = p["stops"][0]["place"]["price"]
    price["confidence"] = "UNKNOWN"
    price["lower"]["minor_units"] = price["upper"]["minor_units"] = 35000
    add("350-unknown-cannot-assert-an-amount", p, c, False, "STRUCTURE")
    p, c = baseline()
    p["origin"] = {"latitude": 40.7128, "longitude": -74.006}
    add("route-evidence-for-a-different-origin", p, c, False, "ROUTING")
    p, c = baseline()
    place = p["stops"][0]["place"]
    place["coordinates"] = {"latitude": 40.7128, "longitude": -74.006}
    next(e for e in place["evidence"] if e["field"] == "coordinates")["value"] = place[
        "coordinates"
    ]
    add("route-evidence-for-a-different-destination", p, c, False, "ROUTING")
    return cases


def all_sources(plan: dict[str, Any]) -> list[dict[str, Any]]:
    sources = [e for route in plan["routes"] for e in route["evidence"]]
    for stop in plan["stops"]:
        place = stop["place"]
        sources.extend(place["evidence"])
        if place["price"]:
            sources.extend(place["price"]["evidence"])
        for window in place["opening_windows"] or []:
            sources.extend(window["evidence"])
    return sources
