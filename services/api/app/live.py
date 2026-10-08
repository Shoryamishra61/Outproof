"""Live enrichment preserves unknowns until venue-specific sources are verified."""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser

import httpx
from ground_rule.models import (
    CompilationFailure,
    Coordinates,
    Evidence,
    Money,
    PlaceCandidate,
    PriceEvidence,
)

from app.places import OverpassPlacesProvider
from app.source_discovery import SerpSourceDiscovery

PARK_SOURCE = "https://sbg.nparks.gov.sg/visit/general-info/"
GATE_SOURCE = "https://www.openstreetmap.org/api/0.6/node/602215681.json"
GATE = Coordinates(latitude=1.3071437, longitude=103.8185997)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value: str) -> None:
        if not self.hidden:
            self.parts.append(value)


def normalize_tanglin(gate: object, html: str, observed_at: datetime) -> PlaceCandidate:
    text = VisibleText()
    text.feed(html)
    visible = " ".join(" ".join(text.parts).split())
    claims = [
        "The Gardens is free entry for everyone, everyday.",
        "Gardens 5am to 12mn daily",
        "Tanglin Entrance is served by Napier & Holland Road.",
    ]
    if not all(claim in visible for claim in claims):
        raise ValueError("Reviewed official price, hours or gate claim unavailable")
    if not isinstance(gate, dict) or len(gate.get("elements", [])) != 1:
        raise ValueError("Gate response invalid")
    node = gate["elements"][0]
    if (
        node.get("type"),
        node.get("id"),
        node.get("tags", {}).get("name"),
        node.get("tags", {}).get("barrier"),
        node.get("tags", {}).get("foot"),
    ) != ("node", 602215681, "Tanglin Gate", "gate", "yes"):
        raise ValueError("Reviewed entrance identity mismatch")
    coordinates = Coordinates(latitude=node["lat"], longitude=node["lon"])
    if (
        abs(coordinates.latitude - GATE.latitude) > 0.0001
        or abs(coordinates.longitude - GATE.longitude) > 0.0001
    ):
        raise ValueError("Reviewed gate moved; reverify before routing")
    subject = "osm:node/602215681"

    def fact(field: str, value: object, source: str = "DIRECT") -> Evidence:
        return Evidence.model_validate(
            dict(
                evidence_id=f"{subject}:{field}",
                subject_id=subject,
                field=field,
                value=value,
                source=source,
                source_ref=GATE_SOURCE if source == "OSM" else PARK_SOURCE,
                observed_at=observed_at,
                expires_at=observed_at + timedelta(hours=24),
                confidence="HIGH",
            )
        )

    price = PriceEvidence(
        confidence="VERIFIED",
        lower=Money(currency_code="SGD", minor_units=0),
        upper=Money(currency_code="SGD", minor_units=0),
        scope="TOTAL",
        evidence=(
            fact(
                "price",
                {
                    "currency_code": "SGD",
                    "lower_minor_units": 0,
                    "upper_minor_units": 0,
                    "scope": "TOTAL",
                    "covers_all_mandatory_costs": True,
                },
            ),
        ),
    )
    return PlaceCandidate(
        place_id=subject,
        provider="OSM",
        provider_id="node/602215681",
        name="Tanglin Gate",
        coordinates=coordinates,
        categories=("park",),
        opening_windows=None,
        price=price,
        dietary_options=None,
        evidence=(
            fact(
                "identity",
                {"provider": "OSM", "provider_id": "node/602215681", "name": "Tanglin Gate"},
                "OSM",
            ),
            fact("coordinates", coordinates.model_dump(), "OSM"),
            fact("categories", ["park"]),
            fact("public_access", True),
            fact("opening_hours", "Mo-Su 05:00-24:00"),
            fact("timezone", "Asia/Singapore"),
            fact(
                "visit_scope",
                "Main gardens only. No National Orchid Garden, paid attractions, food or parking.",
            ),
            fact(
                "parse_lineage",
                {
                    "parser": "nparks-visitor-v1",
                    "claims": claims,
                    "authority": "National Parks Board Singapore",
                    "coordinate_kind": "entrance_node",
                },
            ),
        ),
    )


class LivePlacesProvider:
    """One reviewed public garden entrance; other regions retain generic discovery only."""

    def __init__(
        self, client: httpx.AsyncClient, endpoint: str, search: SerpSourceDiscovery | None = None
    ) -> None:
        self.client = client
        self.discovery = OverpassPlacesProvider(client, endpoint)
        self.search = search

    async def discover(
        self, origin: Coordinates, radius_meters: int
    ) -> tuple[PlaceCandidate, ...] | CompilationFailure:
        # Restrict to the reviewed entrance corridor; distant origins do not gain coverage.
        if (
            abs(origin.latitude - GATE.latitude) > 0.006
            or abs(origin.longitude - GATE.longitude) > 0.006
        ):
            return await self.discovery.discover(origin, radius_meters)
        try:
            responses = []
            for url in [GATE_SOURCE, PARK_SOURCE]:
                async with self.client.stream(
                    "GET", url, timeout=15, follow_redirects=False
                ) as response:
                    response.raise_for_status()
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > 1_000_000:
                            raise ValueError("Source exceeds byte bound")
                    responses.append(bytes(body))
            place = normalize_tanglin(
                json.loads(responses[0]), responses[1].decode("utf-8"), datetime.now(UTC)
            )
            if self.search:
                links, observed = await self.search.search(self.client)
                if links and observed:
                    lead = Evidence(
                        evidence_id=place.place_id + ":source_discovery",
                        subject_id=place.place_id,
                        field="source_discovery",
                        value={
                            "official_url": links[0],
                            "use": "lead only; claims independently fetched",
                        },
                        source="SERPAPI",
                        source_ref=links[0],
                        observed_at=observed,
                        expires_at=observed + timedelta(days=1),
                        confidence="LOW",
                    )
                    place = place.model_copy(update={"evidence": (*place.evidence, lead)})
            return (place,)
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE",
                message="Reviewed garden source unavailable or changed; no claims asserted",
            )


class LiveEnrichmentProvider:
    def __init__(self, clock: Callable[[], datetime] = lambda: datetime.now(UTC)) -> None:
        self.clock = clock

    async def enrich(self, place: PlaceCandidate) -> PlaceCandidate:
        # GCC's register/general schedule proves neither admission nor venue-specific hours.
        return PlaceCandidate.model_validate(place)
