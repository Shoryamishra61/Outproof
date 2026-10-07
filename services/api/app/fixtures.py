"""Explicit synthetic providers. No recorded live observation is refreshed here."""

import json
from datetime import datetime
from pathlib import Path

from ground_rule.models import (
    CompilationFailure,
    ConstraintSet,
    Coordinates,
    PlaceCandidate,
    RouteFact,
)

from app.enrichment import EnrichmentResult, ProviderEvidence, merge_provider_evidence
from app.identity import ProviderIdentity

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "fixtures/compiler/accepted-chennai.json"


class FixtureProviders:
    def __init__(self, *, as_of: datetime | None = None) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        if payload["mode"] != "FIXTURE":
            raise ValueError("Only labelled synthetic observations may use fixture providers")
        original = datetime.fromisoformat(payload["as_of"])
        self.as_of = as_of or original
        delta = self.as_of - original

        def shift(value: object) -> object:
            if isinstance(value, list):
                return [shift(item) for item in value]
            if isinstance(value, dict):
                return {key: shift(item) for key, item in value.items()}
            if isinstance(value, str):
                try:
                    instant = datetime.fromisoformat(value)
                    if instant.tzinfo:
                        return (instant + delta).isoformat()
                except ValueError:
                    pass
            return value

        # This materializes a fresh fictional scenario, never a cached/live observation.
        payload = shift(payload)
        self.controls = ConstraintSet.model_validate(payload["controls"])
        self.places = tuple(PlaceCandidate.model_validate(p) for p in payload["places"])
        self.routes = tuple(RouteFact.model_validate(r) for r in payload["routes"])
        if any(e.source != "FIXTURE" for p in self.places for e in p.evidence):
            raise ValueError("Fixture provider contains non-fixture sources")

    async def discover(self, origin: Coordinates, radius_meters: int) -> tuple[PlaceCandidate, ...]:
        return self.places if origin == self.controls.origin else ()

    async def enrich(self, place: PlaceCandidate) -> EnrichmentResult:
        records = list(place.evidence)
        if place.price:
            records.extend(place.price.evidence)
        for window in place.opening_windows or ():
            records.extend(window.evidence)
        return merge_provider_evidence(
            place,
            ProviderEvidence(
                identity=ProviderIdentity(
                    provider="FIXTURE",
                    provider_id=place.provider_id,
                    name=place.name,
                    coordinates=place.coordinates,
                    categories=place.categories or (),
                    observed_at=self.as_of,
                    source_ref="FIXTURE synthetic provider identity",
                ),
                records=tuple(records),
                price_confidence=place.price.confidence if place.price else "UNKNOWN",
            ),
            as_of=self.as_of,
        )

    async def route(
        self, from_id: str, to_id: str, start: Coordinates, end: Coordinates
    ) -> RouteFact | CompilationFailure:
        for route in self.routes:
            if (route.from_id, route.to_id) == (from_id, to_id):
                return route
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Fixture route absent"
        )
