"""Phase 1 contracts. Structural validity is not hard-constraint verification."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    StringConstraints,
    model_validator,
)

NonEmptyStr = Annotated[StrictStr, StringConstraints(min_length=1, pattern=r"\S")]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(gt=0)]
NonNegativeFloat = Annotated[StrictFloat, Field(ge=0, allow_inf_nan=False)]
BudgetScope = Literal["PER_PERSON", "TOTAL"]
CurrencyCode = Literal["INR", "USD", "GBP", "SGD", "JPY", "EUR", "AUD", "CAD", "AED"]


class Contract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, revalidate_instances="always", allow_inf_nan=False
    )


class Money(Contract):
    currency_code: CurrencyCode
    # JavaScript consumers must be able to represent minor units exactly.
    minor_units: Annotated[StrictInt, Field(ge=0, le=9007199254740991)]

    def add(self, other: Money) -> Money:
        if self.currency_code != other.currency_code:
            raise ValueError("Cannot add different currencies")
        return Money(
            currency_code=self.currency_code, minor_units=self.minor_units + other.minor_units
        )

    def is_at_most(self, limit: Money) -> bool:
        if self.currency_code != limit.currency_code:
            raise ValueError("Cannot compare different currencies")
        return self.minor_units <= limit.minor_units

    def multiply(self, count: int) -> Money:
        if type(count) is not int or count < 0:
            raise ValueError("Money multiplier must be a nonnegative integer")
        return Money(currency_code=self.currency_code, minor_units=self.minor_units * count)


class Coordinates(Contract):
    latitude: Annotated[StrictFloat, Field(ge=-90, le=90, allow_inf_nan=False)]
    longitude: Annotated[StrictFloat, Field(ge=-180, le=180, allow_inf_nan=False)]


class HardConstraint(Contract):
    kind: Literal["EXCLUDE_CATEGORY", "DIETARY", "ACCESSIBILITY", "UNSUPPORTED"]
    value: NonEmptyStr


class SoftConstraint(Contract):
    preference: NonEmptyStr


class ConstraintSet(Contract):
    currency_code: CurrencyCode | None
    budget_minor_units: Annotated[StrictInt, Field(ge=0, le=9007199254740991)] | None
    budget_scope: BudgetScope | None
    duration_max_minutes: Annotated[StrictInt, Field(ge=15)]
    party_mode: Literal["SOLO", "FRIEND", "DATE", "GROUP"]
    party_size: PositiveInt | None
    vibes: tuple[Literal["Food", "Talk", "Explore", "Chill", "Move", "Surprise"], ...]
    hard_constraints: tuple[HardConstraint, ...]
    soft_constraints: tuple[SoftConstraint, ...]
    max_walking_minutes: NonNegativeInt | None
    max_walking_meters: NonNegativeFloat | None
    return_by_local: AwareDatetime | None
    locale: NonEmptyStr | None
    origin: Coordinates | None
    departure_at: AwareDatetime | None
    strict_budget: StrictBool = True

    @model_validator(mode="after")
    def coherent_controls(self) -> Self:
        budget_fields = (self.currency_code, self.budget_minor_units, self.budget_scope)
        if any(value is None for value in budget_fields) and any(
            value is not None for value in budget_fields
        ):
            raise ValueError(
                "Budget amount, currency and scope must be known together or all unknown"
            )
        if self.party_size is not None:
            expected = {"SOLO": 1, "FRIEND": 2, "DATE": 2}.get(self.party_mode)
            if (expected is not None and self.party_size != expected) or (
                self.party_mode == "GROUP" and self.party_size < 2
            ):
                raise ValueError("Party size conflicts with party mode")
        if (
            self.departure_at is not None
            and self.return_by_local is not None
            and self.return_by_local.astimezone(UTC) <= self.departure_at.astimezone(UTC)
        ):
            raise ValueError("Return deadline must follow departure")
        if len(self.vibes) != len(set(self.vibes)):
            raise ValueError("Vibes must be unique")
        return self


class Evidence(Contract):
    evidence_id: NonEmptyStr
    subject_id: NonEmptyStr
    field: NonEmptyStr
    value: JsonValue
    source: Literal["OSM", "VALHALLA", "SERPAPI", "DIRECT", "COMMUNITY", "FIXTURE"]
    source_ref: NonEmptyStr
    observed_at: AwareDatetime
    expires_at: AwareDatetime | None
    confidence: Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

    @model_validator(mode="after")
    def coherent_observation(self) -> Self:
        if self.expires_at is not None and self.expires_at.astimezone(
            UTC
        ) <= self.observed_at.astimezone(UTC):
            raise ValueError("Evidence expiry must follow observation")
        if self.value is None and self.confidence != "UNKNOWN":
            raise ValueError("A missing fact cannot have known confidence")
        return self


class PriceConfidence(StrEnum):
    VERIFIED = "VERIFIED"
    BOUNDED = "BOUNDED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class PriceEvidence(Contract):
    confidence: PriceConfidence
    lower: Money | None
    upper: Money | None
    scope: BudgetScope | None
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def coherent_price(self) -> Self:
        if self.confidence == PriceConfidence.UNKNOWN:
            if any(value is not None for value in (self.lower, self.upper, self.scope)):
                raise ValueError("Unknown price must not assert an amount or scope")
        elif self.lower is None or self.upper is None or self.scope is None or not self.evidence:
            raise ValueError("Known price requires two bounds, scope and source evidence")
        elif not self.lower.is_at_most(self.upper):
            raise ValueError("Price lower bound exceeds upper bound")
        return self


class OpeningWindow(Contract):
    opens_at: AwareDatetime
    closes_at: AwareDatetime
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def ordered_window(self) -> Self:
        if self.closes_at.astimezone(UTC) <= self.opens_at.astimezone(UTC):
            raise ValueError("Closing time must follow opening time")
        return self


class PlaceCandidate(Contract):
    place_id: NonEmptyStr
    provider: Literal["OSM", "SERPAPI", "FIXTURE"]
    provider_id: NonEmptyStr | None
    name: NonEmptyStr | None
    coordinates: Coordinates | None
    categories: tuple[NonEmptyStr, ...] | None
    opening_windows: tuple[OpeningWindow, ...] | None
    price: PriceEvidence | None
    dietary_options: tuple[NonEmptyStr, ...] | None
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def unambiguous_identity(self) -> Self:
        if self.place_id == "origin":
            raise ValueError("origin is reserved for the route origin")
        return self


class RouteFact(Contract):
    route_id: NonEmptyStr
    from_id: NonEmptyStr
    to_id: NonEmptyStr
    reachable: StrictBool
    duration_seconds: NonNegativeInt | None
    distance_meters: NonNegativeFloat | None
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def coherent_reachability(self) -> Self:
        metrics = (self.duration_seconds, self.distance_meters)
        if self.reachable and any(value is None for value in metrics):
            raise ValueError("Reachable route requires duration and distance")
        if not self.reachable and any(value is not None for value in metrics):
            raise ValueError("Unreachable route must not assert travel metrics")
        return self


class PlanStop(Contract):
    place: PlaceCandidate
    arrival_at: AwareDatetime | None
    dwell_seconds: PositiveInt


class CandidatePlan(Contract):
    plan_id: NonEmptyStr
    origin: Coordinates
    departure_at: AwareDatetime
    stops: Annotated[tuple[PlanStop, ...], Field(min_length=1)]
    routes: Annotated[tuple[RouteFact, ...], Field(min_length=2)]

    @model_validator(mode="after")
    def coherent_round_trip(self) -> Self:
        endpoints = ["origin", *(stop.place.place_id for stop in self.stops), "origin"]
        if len(self.routes) != len(self.stops) + 1:
            raise ValueError("Each stop requires an inbound leg and the plan requires a return leg")
        projected_at: datetime | None = self.departure_at.astimezone(UTC)
        for index, route in enumerate(self.routes):
            if (route.from_id, route.to_id) != (endpoints[index], endpoints[index + 1]):
                raise ValueError("Route chain does not match the stop sequence and origin")
            if projected_at is not None and route.duration_seconds is not None:
                try:
                    projected_at += timedelta(seconds=route.duration_seconds)
                except OverflowError as error:
                    raise ValueError("Projected arrival exceeds datetime range") from error
            else:
                projected_at = None
            if index < len(self.stops):
                stop = self.stops[index]
                arrival_at = (
                    stop.arrival_at.astimezone(UTC) if stop.arrival_at is not None else None
                )
                if arrival_at != projected_at:
                    raise ValueError("Arrival must match route timing, or remain unknown")
                if projected_at is not None:
                    try:
                        projected_at += timedelta(seconds=stop.dwell_seconds)
                    except OverflowError as error:
                        raise ValueError("Projected departure exceeds datetime range") from error
        return self

    @property
    def total_duration_seconds(self) -> int | None:
        if any(route.duration_seconds is None for route in self.routes):
            return None
        return sum(
            route.duration_seconds for route in self.routes if route.duration_seconds is not None
        ) + sum(stop.dwell_seconds for stop in self.stops)

    @property
    def walking_distance_meters(self) -> float | None:
        if any(route.distance_meters is None for route in self.routes):
            return None
        return sum(
            route.distance_meters for route in self.routes if route.distance_meters is not None
        )


class CheckCode(StrEnum):
    BUDGET = "BUDGET"
    CURRENCY = "CURRENCY"
    DURATION = "DURATION"
    ROUTING = "ROUTING"
    RETURN_TRIP = "RETURN_TRIP"
    OPENING_HOURS = "OPENING_HOURS"
    WALKING = "WALKING"
    EXCLUSIONS = "EXCLUSIONS"
    DIETARY = "DIETARY"
    GROUNDING = "GROUNDING"
    PRICE_CONFIDENCE = "PRICE_CONFIDENCE"


class ValidationCheck(Contract):
    code: CheckCode
    status: Literal["PASS", "FAIL", "UNKNOWN"]
    hard: StrictBool
    message: NonEmptyStr
    evidence_ids: tuple[NonEmptyStr, ...]


class ValidationResult(Contract):
    plan_id: NonEmptyStr
    accepted: StrictBool
    checks: Annotated[tuple[ValidationCheck, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def accepted_only_with_complete_hard_passes(self) -> Self:
        codes = [check.code for check in self.checks]
        if len(codes) != len(set(codes)):
            raise ValueError("Duplicate validation check codes")
        hard_checks = [check for check in self.checks if check.hard]
        complete_pass = {check.code for check in hard_checks} == set(CheckCode) and all(
            check.status == "PASS" for check in hard_checks
        )
        if self.accepted != complete_pass:
            raise ValueError("Acceptance must match complete hard-check results")
        return self


class PlanProof(Contract):
    validation: ValidationResult
    cost: PriceEvidence
    total_duration_seconds: PositiveInt
    walking_distance_meters: NonNegativeFloat
    sources: Annotated[tuple[Evidence, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def proof_requires_acceptance(self) -> Self:
        if not self.validation.accepted:
            raise ValueError("Plan Proof requires an accepted validation result")
        source_ids = [source.evidence_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Proof evidence identifiers must be unique")
        referenced_ids = {
            evidence_id for check in self.validation.checks for evidence_id in check.evidence_ids
        } | {evidence.evidence_id for evidence in self.cost.evidence}
        if not referenced_ids.issubset(source_ids):
            raise ValueError("Proof must carry all referenced evidence")
        proof_sources = {source.evidence_id: source for source in self.sources}
        if any(proof_sources.get(source.evidence_id) != source for source in self.cost.evidence):
            raise ValueError("Cost evidence must match the proof source with that identifier")
        return self


class CompiledPlan(Contract):
    status: Literal["SUCCESS"] = "SUCCESS"
    plan: CandidatePlan
    proof: PlanProof
    reason: NonEmptyStr
    compiled_at: AwareDatetime
    mode: Literal["LIVE", "FIXTURE", "CACHED"]

    @model_validator(mode="after")
    def proof_matches_plan(self) -> Self:
        if self.plan.plan_id != self.proof.validation.plan_id:
            raise ValueError("Plan and proof identifiers differ")
        if self.plan.total_duration_seconds != self.proof.total_duration_seconds:
            raise ValueError("Proof duration differs from the complete round trip")
        if self.plan.walking_distance_meters != self.proof.walking_distance_meters:
            raise ValueError("Proof walking distance differs from the route facts")
        plan_sources = [evidence for route in self.plan.routes for evidence in route.evidence]
        for stop in self.plan.stops:
            place = stop.place
            if (
                place.provider_id is None
                or place.name is None
                or place.coordinates is None
                or not place.evidence
            ):
                raise ValueError(
                    "Compiled stops require identity, name, coordinates and source evidence"
                )
            plan_sources.extend(place.evidence)
            if place.price is not None:
                plan_sources.extend(place.price.evidence)
            for window in place.opening_windows or ():
                plan_sources.extend(window.evidence)
        proof_sources = {source.evidence_id: source for source in self.proof.sources}
        if any(proof_sources.get(source.evidence_id) != source for source in plan_sources):
            raise ValueError("Proof must preserve all plan source evidence")
        if self.mode != "FIXTURE" and any(
            source.source == "FIXTURE" for source in self.proof.sources
        ):
            raise ValueError("Synthetic fixture evidence must be labelled FIXTURE")
        return self


class CompilationFailure(Contract):
    status: Literal["FAILURE"] = "FAILURE"
    code: Literal[
        "NO_GROUNDED_CANDIDATES",
        "NO_BUDGET_VERIFIED_PLAN",
        "NO_TIME_FEASIBLE_PLAN",
        "NO_OPEN_PLAN",
        "UNSUPPORTED_CONSTRAINT",
        "SOURCE_TEMPORARILY_UNAVAILABLE",
        "MODEL_OUTPUT_INVALID",
    ]
    message: NonEmptyStr


CONTRACT_MODELS = (
    Money,
    Coordinates,
    HardConstraint,
    SoftConstraint,
    ConstraintSet,
    Evidence,
    PriceEvidence,
    OpeningWindow,
    PlaceCandidate,
    RouteFact,
    PlanStop,
    CandidatePlan,
    ValidationCheck,
    ValidationResult,
    PlanProof,
    CompiledPlan,
    CompilationFailure,
)
