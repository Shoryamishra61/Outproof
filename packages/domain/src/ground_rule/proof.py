"""Deterministic proof construction and rendering. No model text establishes a check."""

from datetime import UTC, datetime

from ground_rule.models import (
    CandidatePlan,
    CheckCode,
    ConstraintSet,
    Contract,
    Evidence,
    Money,
    PlaceCandidate,
    PlanProof,
    PriceConfidence,
    PriceEvidence,
    ValidationResult,
)
from ground_rule.policy import MAX_AGE, validate_plan


def place_sources(place: PlaceCandidate) -> tuple[Evidence, ...]:
    return (
        *place.evidence,
        *(place.price.evidence if place.price else ()),
        *(e for w in place.opening_windows or () for e in w.evidence),
    )


def plan_sources(plan: CandidatePlan) -> tuple[Evidence, ...]:
    sources = [e for r in plan.routes for e in r.evidence]
    sources.extend(e for stop in plan.stops for e in place_sources(stop.place))
    by_id: dict[str, Evidence] = {}
    for record in sources:
        if record.evidence_id in by_id and by_id[record.evidence_id] != record:
            raise ValueError("Conflicting source identifier")
        by_id[record.evidence_id] = record
    return tuple(by_id.values())


def build_proof(
    plan: CandidatePlan,
    validation: ValidationResult,
    controls: ConstraintSet,
    *,
    as_of: datetime,
    allow_fixture: bool = False,
) -> PlanProof:
    plan = CandidatePlan.model_validate(plan)
    actual = validate_plan(plan, controls, as_of=as_of, allow_fixture=allow_fixture)
    if not actual.accepted or actual != validation:
        raise ValueError("Proof requires the current unchanged-policy acceptance for this plan")
    prices = [stop.place.price for stop in plan.stops]
    currency = prices[0].upper.currency_code
    lower, upper, records = (
        Money(currency_code=currency, minor_units=0),
        Money(currency_code=currency, minor_units=0),
        [],
    )
    for price in prices:
        multiplier = controls.party_size if price.scope == "PER_PERSON" else 1
        lower, upper = (
            lower.add(price.lower.multiply(multiplier)),
            upper.add(price.upper.multiply(multiplier)),
        )
        records.extend(price.evidence)
    confidence = (
        PriceConfidence.ESTIMATED
        if any(p.confidence == PriceConfidence.ESTIMATED for p in prices)
        else PriceConfidence.BOUNDED
        if any(p.confidence == PriceConfidence.BOUNDED for p in prices)
        else PriceConfidence.VERIFIED
    )
    return PlanProof(
        validation=actual,
        cost=PriceEvidence(
            confidence=confidence, lower=lower, upper=upper, scope="TOTAL", evidence=tuple(records)
        ),
        total_duration_seconds=plan.total_duration_seconds,
        walking_distance_meters=plan.walking_distance_meters,
        sources=plan_sources(plan),
    )


class ProofLine(Contract):
    code: CheckCode
    text: str
    evidence_ids: tuple[str, ...]


def format_money(money: Money) -> str:
    scale = 1 if money.currency_code == "JPY" else 100
    amount = (
        str(money.minor_units)
        if scale == 1
        else f"{money.minor_units // scale}.{money.minor_units % scale:02}"
    )
    return f"{money.currency_code} {amount}"


def stale_source_ids(proof: PlanProof, as_of: datetime) -> tuple[str, ...]:
    now = as_of.astimezone(UTC)
    return tuple(
        e.evidence_id
        for e in proof.sources
        if (
            (e.expires_at is not None and now >= e.expires_at.astimezone(UTC))
            or (e.field in MAX_AGE and now - e.observed_at.astimezone(UTC) >= MAX_AGE[e.field])
        )
    )


def render_proof(proof: PlanProof, controls: ConstraintSet) -> tuple[ProofLine, ...]:
    proof = PlanProof.model_validate(proof)
    controls = ConstraintSet.model_validate(controls)
    limit = controls.budget_minor_units
    scope = "total"
    if limit is not None and controls.budget_scope == "PER_PERSON":
        if controls.party_size is None:
            raise ValueError("Per-person proof requires party size")
        limit *= controls.party_size
        scope = f"total ({controls.party_size} people; per-person cap)"
    budget = format_money(proof.cost.upper)
    if limit is not None:
        cap = Money(currency_code=controls.currency_code, minor_units=limit)
        budget += f" <= {format_money(cap)} {scope}"
    texts = {
        CheckCode.BUDGET: budget,
        CheckCode.CURRENCY: f"{proof.cost.upper.currency_code}; same-currency mandatory costs",
        CheckCode.DURATION: (
            f"{proof.total_duration_seconds / 60:g} min <= "
            f"{controls.duration_max_minutes} min; includes return"
        ),
        CheckCode.RETURN_TRIP: "Return route included; no explicit deadline"
        if controls.return_by_local is None
        else f"Return deadline met: {controls.return_by_local.isoformat()}",
        CheckCode.PRICE_CONFIDENCE: f"{proof.cost.confidence}; complete mandatory cost",
        CheckCode.OPENING_HOURS: "Open throughout required dwell",
        CheckCode.EXCLUSIONS: "Hard exclusions evidenced"
        if any(h.kind == "EXCLUDE_CATEGORY" for h in controls.hard_constraints)
        else "No hard exclusions supplied",
        CheckCode.DIETARY: "Dietary requirements evidenced"
        if any(h.kind == "DIETARY" for h in controls.hard_constraints)
        else "No dietary requirements supplied",
        CheckCode.WALKING: (
            f"{proof.walking_distance_meters:g} m; every leg checked against walking limits"
        ),
        CheckCode.GROUNDING: "Every place has provider identity and coordinates",
        CheckCode.ROUTING: "Every mandatory walking leg reachable, including return",
    }
    return tuple(
        ProofLine(code=c.code, text=f"{c.status} {texts[c.code]}", evidence_ids=c.evidence_ids)
        for c in proof.validation.checks
    )
