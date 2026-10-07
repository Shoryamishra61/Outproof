"""Conservative deterministic crosswalk; proximity is an identity signal, not routing."""

import math
import re
import unicodedata
from typing import Literal

from ground_rule.models import Contract, Coordinates, Evidence, NonEmptyStr, PlaceCandidate
from pydantic import AwareDatetime


class ProviderIdentity(Contract):
    provider: Literal["SERPAPI", "DIRECT", "FIXTURE"]
    provider_id: NonEmptyStr | None
    name: NonEmptyStr
    coordinates: Coordinates | None
    categories: tuple[str, ...] = ()
    address: str | None = None
    phone: str | None = None
    domain: str | None = None
    observed_at: AwareDatetime
    source_ref: NonEmptyStr


class IdentityBinding(Contract):
    status: Literal["MATCH", "AMBIGUOUS", "NO_MATCH"]
    candidate_id: NonEmptyStr
    provider_id: NonEmptyStr | None
    signals: tuple[str, ...]
    evidence: tuple[Evidence, ...] = ()


def normalized(value: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", value).casefold()))


def distance_meters(a: Coordinates, b: Coordinates) -> float:
    lat_a, lat_b = math.radians(a.latitude), math.radians(b.latitude)
    h = (
        math.sin((lat_b - lat_a) / 2) ** 2
        + math.cos(lat_a)
        * math.cos(lat_b)
        * math.sin(math.radians(b.longitude - a.longitude) / 2) ** 2
    )
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def bind_identity(
    place: PlaceCandidate, identities: tuple[ProviderIdentity, ...]
) -> IdentityBinding:
    place = PlaceCandidate.model_validate(place)
    matches: dict[tuple[str, str], tuple[str, ...]] = {}
    for identity in identities:
        identity = ProviderIdentity.model_validate(identity)
        if not (place.name and place.coordinates and identity.coordinates and identity.provider_id):
            continue
        if normalized(place.name) != normalized(identity.name):
            continue
        distance = distance_meters(place.coordinates, identity.coordinates)
        # ponytail: conservative 40 m crosswalk; entrances/address geometry need a separate upgrade.
        if distance > 40:
            continue
        signals = ["normalized name matches", f"coordinates within 40 m ({distance:.2f} m)"]
        if identity.categories and place.categories:
            if not set(map(normalized, identity.categories)) & set(
                map(normalized, place.categories)
            ):
                continue
            signals.append("category matches")
        contradictory = False
        for field in ("address", "phone", "domain"):
            values = [e.value for e in place.evidence if e.field == field and e.value is not None]
            supplied = getattr(identity, field)
            if supplied and values:
                if any(
                    not isinstance(v, str) or normalized(v) != normalized(supplied) for v in values
                ):
                    contradictory = True
                    break
                signals.append(f"{field} matches")
        if not contradictory:
            key = (identity.provider, identity.provider_id)
            if key in matches:
                return IdentityBinding(
                    status="AMBIGUOUS",
                    candidate_id=place.place_id,
                    provider_id=None,
                    signals=("duplicate provider identity records",),
                )
            matches[key] = tuple(signals)
    status = "MATCH" if len(matches) == 1 else "AMBIGUOUS" if matches else "NO_MATCH"
    return IdentityBinding(
        status=status,
        candidate_id=place.place_id,
        provider_id=next(iter(matches))[1] if status == "MATCH" else None,
        signals=next(iter(matches.values())) if status == "MATCH" else ("identity unresolved",),
    )
