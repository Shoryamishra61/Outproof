"""Optional SerpApi metadata with explicit identity linkage; never inferred price proof."""

import json
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol, Self

import httpx
from ground_rule.models import (
    CompilationFailure,
    Contract,
    Coordinates,
    Evidence,
    OpeningWindow,
    PlaceCandidate,
    PriceConfidence,
)
from ground_rule.policy import MAX_AGE
from ground_rule.pricing import mandatory_price
from pydantic import AwareDatetime, TypeAdapter, model_validator

from app.identity import IdentityBinding, ProviderIdentity, bind_identity


class EvidenceFreshness(Contract):
    evidence_id: str
    status: Literal["CURRENT", "STALE", "FUTURE", "UNKNOWN"]


class ProviderEvidence(Contract):
    identity: ProviderIdentity
    records: tuple[Evidence, ...]
    price_confidence: PriceConfidence = PriceConfidence.UNKNOWN


class EnrichmentResult(Contract):
    place: PlaceCandidate
    binding: IdentityBinding
    observations: tuple[Evidence, ...]
    freshness: tuple[EvidenceFreshness, ...]
    absent_fields: tuple[str, ...]
    contradictions: tuple[str, ...]

    @model_validator(mode="after")
    def coherent_binding_and_observations(self) -> Self:
        if self.binding.candidate_id != self.place.place_id:
            raise ValueError("Binding belongs to a different candidate")
        if self.binding.status == "MATCH" and (
            not self.binding.provider_id or not self.binding.evidence
        ):
            raise ValueError("Accepted binding requires identity and supporting evidence")
        if tuple(e.evidence_id for e in self.observations) != tuple(
            e.evidence_id for e in self.freshness
        ):
            raise ValueError("Freshness must align with every observation")
        return self


def evidence_freshness(record: Evidence, as_of: datetime) -> EvidenceFreshness:
    record = Evidence.model_validate(record)
    now = TypeAdapter(AwareDatetime).validate_python(as_of).astimezone(UTC)
    age = now - record.observed_at.astimezone(UTC)
    maximum = MAX_AGE.get(record.field)
    status = "CURRENT"
    if age < timedelta(0):
        status = "FUTURE"
    elif record.expires_at is not None and now >= record.expires_at.astimezone(UTC):
        status = "STALE"
    elif maximum is None or record.value is None:
        status = "UNKNOWN"
    elif age >= maximum:
        status = "STALE"
    return EvidenceFreshness(evidence_id=record.evidence_id, status=status)


def merge_provider_evidence(
    place: PlaceCandidate, provider: ProviderEvidence, *, as_of: datetime
) -> EnrichmentResult:
    """Retain every observation separately; contradictions cannot become authoritative facts."""
    place = PlaceCandidate.model_validate(place)
    as_of = TypeAdapter(AwareDatetime).validate_python(as_of)
    provider = ProviderEvidence.model_validate(provider)
    binding = bind_identity(place, (provider.identity,))
    identity = provider.identity
    if (
        not timedelta(0)
        <= as_of.astimezone(UTC) - identity.observed_at.astimezone(UTC)
        < timedelta(days=30)
    ):
        binding = IdentityBinding(
            status="NO_MATCH",
            candidate_id=place.place_id,
            provider_id=None,
            signals=("provider identity stale or future",),
        )
    elif binding.status == "MATCH":
        binding = binding.model_copy(
            update={
                "evidence": (
                    Evidence(
                        evidence_id=f"{place.place_id}:binding:{identity.provider}:{identity.provider_id}",
                        subject_id=place.place_id,
                        field="identity_binding",
                        value={
                            "provider": identity.provider,
                            "provider_id": identity.provider_id,
                            "signals": list(binding.signals),
                        },
                        source=identity.provider,
                        source_ref=identity.source_ref,
                        observed_at=identity.observed_at,
                        expires_at=None,
                        confidence="MEDIUM",
                    ),
                )
            }
        )
    records = provider.records
    freshness = tuple(evidence_freshness(e, as_of) for e in records)
    absent = tuple(
        f
        for f in ("price", "opening_window")
        if not any(e.field == f and e.value is not None for e in records)
    )
    conflicts: list[str] = []
    retained = list(place.evidence)
    existing = list(place.evidence)
    if place.price:
        existing.extend(place.price.evidence)
    for window in place.opening_windows or ():
        existing.extend(window.evidence)
    strength = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
    updates: dict[str, object] = {}
    for record, age in zip(records, freshness, strict=True):
        if record.subject_id != place.place_id or record.source != provider.identity.provider:
            conflicts.append(f"{record.evidence_id}: provider/subject mismatch")
            continue
        previous = [e for e in existing if e.field == record.field]
        if any(
            json.dumps(e.value, sort_keys=True) != json.dumps(record.value, sort_keys=True)
            for e in previous
        ):
            conflicts.append(f"{record.field}: contradictory observations")
            continue
        if binding.status != "MATCH" or age.status != "CURRENT":
            continue
        if previous and max(strength[e.confidence] for e in previous) > strength[record.confidence]:
            continue
        if previous:
            continue  # Identical observations do not refresh the original timestamp.
        retained.append(record)
        existing.append(record)
        if record.field == "price":
            # Complete aggregate attestations only; generic provider price levels stay metadata.
            price = mandatory_price(record, confidence=provider.price_confidence)
            if isinstance(price, CompilationFailure):
                conflicts.append("price: unsupported mandatory-cost attestation")
            else:
                updates["price"] = price
        elif record.field == "dietary_options" and isinstance(record.value, list):
            updates["dietary_options"] = tuple(record.value)
        elif record.field == "opening_window":
            try:
                if not isinstance(record.value, list) or len(record.value) != 2:
                    raise ValueError("Invalid window")
                updates["opening_windows"] = (
                    OpeningWindow(
                        opens_at=record.value[0], closes_at=record.value[1], evidence=(record,)
                    ),
                )
            except ValueError:
                conflicts.append("opening_window: malformed interval")
    candidate = PlaceCandidate.model_validate(
        place.model_copy(update={**updates, "evidence": tuple(retained)})
    )
    return EnrichmentResult(
        place=candidate,
        binding=binding,
        observations=records,
        freshness=freshness,
        absent_fields=absent,
        contradictions=tuple(dict.fromkeys(conflicts)),
    )


class EnrichmentProvider(Protocol):
    async def enrich(
        self, place: PlaceCandidate
    ) -> PlaceCandidate | EnrichmentResult | CompilationFailure: ...


def provider_link(place: PlaceCandidate, as_of: datetime) -> str | None:
    links = [e for e in place.evidence if e.field == "provider_link"]
    if not links:
        return None
    ids = set()
    for record in links:
        value = record.value
        if (
            record.subject_id != place.place_id
            or record.source not in {"DIRECT", "OSM"}
            or record.confidence not in {"HIGH", "MEDIUM"}
            or not isinstance(value, dict)
            or value.get("provider") != "SERPAPI"
            or not isinstance(value.get("place_id"), str)
            or not value["place_id"].strip()
            or not timedelta(0) <= as_of - record.observed_at.astimezone(UTC) < timedelta(days=7)
            or (record.expires_at is not None and as_of >= record.expires_at.astimezone(UTC))
        ):
            return None
        ids.add(value["place_id"])
    return next(iter(ids)) if len(ids) == 1 else None


def normalize_enrichment(
    place: PlaceCandidate, payload: object, *, reference_id: str, observed_at: datetime
) -> PlaceCandidate | CompilationFailure:
    place = PlaceCandidate.model_validate(place)
    try:
        if provider_link(place, observed_at.astimezone(UTC)) != reference_id:
            raise ValueError("Unresolved cross-provider identity")
        if not isinstance(payload, dict) or payload.get("error"):
            raise ValueError("Provider error")
        result = payload["place_results"]
        if result.get("place_id") != reference_id or result.get("title") != place.name:
            raise ValueError("Provider identity mismatch")
        coords = Coordinates.model_validate(result["gps_coordinates"])
        if place.coordinates is None or (
            abs(coords.latitude - place.coordinates.latitude) > 0.000001
            or abs(coords.longitude - place.coordinates.longitude) > 0.000001
        ):
            raise ValueError("Provider coordinates mismatch")
        # Only permitted compact metadata is retained; no reviews, photos or similar places.
        metadata = {
            key: result.get(key)
            for key in (
                "place_id",
                "data_id",
                "open_state",
                "hours",
                "operating_hours",
                "rating",
                "reviews",
                "price",
            )
        }
        if metadata["rating"] is not None and (
            type(metadata["rating"]) not in {int, float} or not 0 <= metadata["rating"] <= 5
        ):
            raise ValueError("Invalid rating")
        if metadata["reviews"] is not None and (
            type(metadata["reviews"]) is not int or metadata["reviews"] < 0
        ):
            raise ValueError("Invalid rating count")
        field = "serpapi_metadata"
        record = Evidence(
            evidence_id=f"{place.place_id}:{field}",
            subject_id=place.place_id,
            field=field,
            value=metadata,
            source="SERPAPI",
            source_ref=f"https://serpapi.com/maps-place-results#{reference_id}",
            observed_at=observed_at,
            expires_at=None,
            confidence="MEDIUM",
        )
        previous = [e for e in place.evidence if e.field == field]
        if previous:
            if any(e.value != record.value for e in previous):
                raise ValueError("Conflicting enrichment retained; cannot overwrite")
            return place
        return PlaceCandidate.model_validate(
            place.model_copy(update={"evidence": place.evidence + (record,)})
        )
    except (ValueError, TypeError, KeyError, AttributeError):
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE",
            message="SerpApi facts missing, malformed, conflicting or identity unresolved",
        )


class SerpApiEnrichmentProvider:
    def __init__(self, client: httpx.AsyncClient, api_key: str | None) -> None:
        self.client = client
        self.api_key = api_key

    async def enrich(self, place: PlaceCandidate) -> EnrichmentResult | CompilationFailure:
        if not self.api_key:
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="SerpApi credential unavailable"
            )
        place = PlaceCandidate.model_validate(place)
        reference_id = provider_link(place, datetime.now(UTC))
        if reference_id is None:
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE",
                message="Cross-provider place identity unresolved",
            )
        try:
            response = await self.client.get(
                "https://serpapi.com/search.json",
                params=dict(
                    engine="google_maps", type="place", place_id=reference_id, api_key=self.api_key
                ),
                timeout=30,
            )
            response.raise_for_status()
            enriched = normalize_enrichment(
                place, response.json(), reference_id=reference_id, observed_at=datetime.now(UTC)
            )
            if isinstance(enriched, CompilationFailure):
                return enriched
            metadata = next(e for e in enriched.evidence if e.field == "serpapi_metadata")
            records = tuple(
                Evidence(
                    evidence_id=f"{place.place_id}:serpapi:{field}",
                    subject_id=place.place_id,
                    field=f"serpapi:{field}",
                    value=value,
                    source="SERPAPI",
                    source_ref=metadata.source_ref,
                    observed_at=metadata.observed_at,
                    expires_at=metadata.expires_at,
                    confidence="MEDIUM" if value is not None else "UNKNOWN",
                )
                for field, value in metadata.value.items()
            )
            result = merge_provider_evidence(
                enriched,
                ProviderEvidence(
                    identity=ProviderIdentity(
                        provider="SERPAPI",
                        provider_id=reference_id,
                        name=enriched.name,
                        coordinates=enriched.coordinates,
                        categories=enriched.categories or (),
                        observed_at=metadata.observed_at,
                        source_ref=metadata.source_ref,
                    ),
                    records=records,
                ),
                as_of=datetime.now(UTC),
            )
            # Raw price levels/open-now/prose hours remain metadata, never cost or dwell proof.
            return EnrichmentResult.model_validate(
                result.model_copy(
                    update={
                        "place": enriched.model_copy(
                            update={"evidence": enriched.evidence + records}
                        ),
                    }
                )
            )
        except (httpx.HTTPError, ValueError):
            # Never include exception/request URLs, which carry the API credential.
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="SerpApi request failed"
            )
