import asyncio
from datetime import timedelta

import pytest
from app.compiler import valid_candidate_plans
from app.fixtures import FixtureProviders
from app.reviewed_gardens import distance_meters
from ground_rule.models import CompilationFailure, Coordinates, PlaceCandidate


def valid(provider: FixtureProviders, allow_fixture: bool = True) -> object:
    return asyncio.run(
        valid_candidate_plans(
            provider.controls,
            provider,
            provider,
            provider,
            as_of=provider.as_of,
            allow_fixture=allow_fixture,
        )
    )


@pytest.mark.parametrize("count", [0, 1, 2])
def test_zero_one_multiple_valid(count: int) -> None:
    provider = FixtureProviders()
    provider.places = provider.places[:count]
    result = valid(provider)
    assert isinstance(result, tuple) and len(result) == count
    assert all(item.validation.accepted for item in result)


def test_fixture_cannot_pass_default_live_policy() -> None:
    result = valid(FixtureProviders(), allow_fixture=False)
    assert isinstance(result, CompilationFailure) or result == ()


@pytest.mark.parametrize("count", [1, 2])
def test_invalid_price_candidates_removed(count: int) -> None:
    provider = FixtureProviders()
    provider.places = tuple(
        p.model_copy(update={"price": None}) if i < count else p
        for i, p in enumerate(provider.places)
    )
    result = valid(provider)
    assert isinstance(result, tuple) and len(result) == 2 - count


def test_missing_price_or_hours_never_spends_routing_quota() -> None:
    class NoRoute(FixtureProviders):
        async def route(self, *args: object) -> object:
            pytest.fail("Candidate without price/hours must be rejected before routing")

    provider = NoRoute()
    provider.places = tuple(p.model_copy(update={"price": None}) for p in provider.places)
    assert valid(provider) == ()
    provider = NoRoute()
    provider.places = tuple(
        p.model_copy(
            update={
                "opening_windows": None,
                "evidence": tuple(
                    e for e in p.evidence if e.field not in {"opening_hours", "timezone"}
                ),
            }
        )
        for p in provider.places
    )
    assert valid(provider) == ()


def test_observation_during_discovery_uses_current_clock_for_prefilter() -> None:
    provider = FixtureProviders()
    provider.places = tuple(
        p.model_copy(
            update={
                "evidence": tuple(
                    e.model_copy(update={"observed_at": provider.as_of + timedelta(seconds=1)})
                    if e.field == "categories"
                    else e
                    for e in p.evidence
                )
            }
        )
        for p in provider.places
    )
    result = asyncio.run(
        valid_candidate_plans(
            provider.controls,
            provider,
            provider,
            provider,
            as_of=provider.as_of,
            allow_fixture=True,
            clock=lambda: provider.as_of + timedelta(seconds=2),
        )
    )
    assert isinstance(result, tuple) and len(result) == 2


@pytest.mark.parametrize("stage", ["enrichment", "routing", "discovery"])
def test_provider_failure(stage: str) -> None:
    class Broken(FixtureProviders):
        async def discover(self, *args: object, **kwargs: object) -> object:
            if stage == "discovery":
                return CompilationFailure(code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Timeout")
            return await super().discover(*args, **kwargs)

        async def enrich(self, place: object) -> object:
            if stage == "enrichment":
                return CompilationFailure(code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Timeout")
            return await super().enrich(place)

        async def route(self, *args: object) -> object:
            if stage == "routing":
                return CompilationFailure(code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Timeout")
            return await super().route(*args)

    result = valid(Broken())
    assert (
        isinstance(result, CompilationFailure) and result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"
    )


def test_identical_duplicates_collapsed() -> None:
    provider = FixtureProviders()
    provider.places += (provider.places[0],)
    assert len(valid(provider)) == 2


def test_conflicting_duplicate_identity_rejected() -> None:
    provider = FixtureProviders()
    provider.places += (provider.places[0].model_copy(update={"place_id": "different-id"}),)
    result = valid(provider)
    assert isinstance(result, CompilationFailure) and result.code == "NO_GROUNDED_CANDIDATES"


def test_enrichment_cannot_mutate_identity_or_drop_evidence() -> None:
    class Broken(FixtureProviders):
        async def enrich(self, place: object) -> object:
            return place.model_copy(update={"evidence": ()})

    assert valid(Broken()) == ()


def test_one_enrichment_timeout_keeps_other_valid_candidate() -> None:
    class Partial(FixtureProviders):
        async def enrich(self, place: object) -> object:
            if place.place_id == self.places[0].place_id:
                return CompilationFailure(code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Timeout")
            return await super().enrich(place)

    assert len(valid(Partial())) == 1


@pytest.mark.parametrize("walking_minutes,accepted", [(30, False), (45, True)])
def test_walkable_candidates_beyond_one_kilometer_keep_walking_limit(
    walking_minutes: int, accepted: bool
) -> None:
    class GeographicFixtures(FixtureProviders):
        async def discover(
            self, origin: Coordinates, radius_meters: int
        ) -> tuple[PlaceCandidate, ...]:
            return tuple(
                place
                for place in self.places
                if distance_meters(origin, place.coordinates) <= radius_meters
            )

    provider = GeographicFixtures()
    origin = provider.controls.origin.model_copy(
        update={"latitude": provider.controls.origin.latitude - 0.012}
    )
    provider.controls = provider.controls.model_copy(
        update={
            "origin": origin,
            "max_walking_minutes": walking_minutes,
            "max_walking_meters": 4000.0,
        }
    )
    assert all(1000 < distance_meters(origin, p.coordinates) < 3000 for p in provider.places)
    # Relocate explicitly synthetic observations; no live evidence is refreshed.
    provider.routes = tuple(
        route.model_copy(
            update={
                "duration_seconds": 1200,
                "distance_meters": 1800.0,
                "evidence": tuple(
                    evidence.model_copy(
                        update={
                            "value": {
                                **evidence.value,
                                "from_coordinates": origin.model_dump()
                                if route.from_id == "origin"
                                else evidence.value["from_coordinates"],
                                "to_coordinates": origin.model_dump()
                                if route.to_id == "origin"
                                else evidence.value["to_coordinates"],
                                "duration_seconds": 1200,
                                "distance_meters": 1800.0,
                            }
                        }
                    )
                    if evidence.field == "walking_route"
                    else evidence
                    for evidence in route.evidence
                ),
            }
        )
        for route in provider.routes
    )
    result = valid(provider)
    assert isinstance(result, tuple)
    assert bool(result) is accepted
