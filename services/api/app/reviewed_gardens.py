"""Fresh official admission/hours joined to reviewed OSM pedestrian access points."""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
from itertools import pairwise
from math import asin, cos, radians, sin, sqrt

import httpx
from ground_rule.models import Coordinates, Evidence, PlaceCandidate
from ground_rule.pricing import mandatory_price


@dataclass(frozen=True)
class ReviewedGarden:
    name: str
    title: str
    sector: str
    park_way: int
    path_way: int
    access_node: int
    coordinates: Coordinates
    probe_origin: Coordinates
    url: str
    city: str = "Chandigarh"
    authority: str = "Chandigarh Tourism Department"
    opening_hours: str = "Mo-Su 05:00-21:00"
    source_format: str = "chandigarh_garden"
    excluded_way: int | None = None


GARDENS = (
    ReviewedGarden(
        "Shanti Kunj",
        "Shanti Kunj",
        "Sector 16",
        129720606,
        655074179,
        6137905894,
        Coordinates(latitude=30.7440211, longitude=76.7781861),
        Coordinates(latitude=30.7443502, longitude=76.7787642),
        "https://chandigarhtourism.gov.in/gardens/shantikunj",
    ),
    ReviewedGarden(
        "Terraced Gardens",
        "Terraced Garden",
        "Sector 33B",
        129460621,
        1078014066,
        9883600810,
        Coordinates(latitude=30.7133495, longitude=76.7702857),
        Coordinates(latitude=30.7132815, longitude=76.7701731),
        "https://chandigarhtourism.gov.in/gardens/Terracedgarden",
    ),
    ReviewedGarden(
        "Cubbon Park",
        "Cubbon Park (Sri Chamarajendra Park), Bangalore",
        "Ambedkar Veedhi",
        22895320,
        1276833566,
        11854682505,
        Coordinates(latitude=12.9771413, longitude=77.5911742),
        Coordinates(latitude=12.9772684, longitude=77.5911720),
        "https://karnatakatourism.org/en/attractions/cubbon-park",
        city="Bengaluru",
        authority="Department of Tourism, Government of Karnataka",
        opening_hours="Tu-Su 06:00-18:00; Tu[2] off",
        source_format="karnataka_attraction",
        excluded_way=208686727,
    ),
)


class GardenPage(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, bool]] = []
        self.parts: list[str] = []
        self.headings: list[str] = []
        self.heading_parts: list[str] = []
        self.rows: list[tuple[str, ...]] = []
        self.row_cells: list[str] = []
        self.cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        style = (attributes.get("style") or "").replace(" ", "").casefold()
        hidden = (
            tag in {"script", "style", "template"}
            or "hidden" in attributes
            or attributes.get("aria-hidden") == "true"
            or "display:none" in style
            or "visibility:hidden" in style
        )
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.stack.append((tag, hidden))
        if tag == "tr":
            self.row_cells = []
        if tag in {"td", "th"}:
            self.cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self.row_cells.append(" ".join(" ".join(self.cell_parts).split()))
            self.cell_parts = []
        if tag == "tr":
            self.rows.append(tuple(self.row_cells))
            self.row_cells = []
        if tag == "h1" and self.heading_parts:
            self.headings.append(" ".join(" ".join(self.heading_parts).split()))
            self.heading_parts = []
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, value: str) -> None:
        if not any(hidden for _, hidden in self.stack):
            self.parts.append(value)
            if any(tag == "h1" for tag, _ in self.stack):
                self.heading_parts.append(value)
            if any(tag in {"td", "th"} for tag, _ in self.stack):
                self.cell_parts.append(value)


def distance_meters(a: Coordinates, b: Coordinates) -> float:
    """Geodesic separation for discovery/binding; never a walking metric."""
    lat_a, lat_b = radians(a.latitude), radians(b.latitude)
    delta_lat = lat_b - lat_a
    delta_lon = radians(b.longitude - a.longitude)
    return 12_742_000 * asin(
        min(1, sqrt(sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2))
    )


def inside_boundary(point: Coordinates, ring: list[Coordinates]) -> bool:
    inside = False
    for a, b in zip(ring, ring[1:], strict=False):
        if (a.latitude > point.latitude) != (b.latitude > point.latitude) and (
            point.longitude
            < (b.longitude - a.longitude)
            * (point.latitude - a.latitude)
            / (b.latitude - a.latitude)
            + a.longitude
        ):
            inside = not inside
    return inside


def segments_intersect(a: Coordinates, b: Coordinates, c: Coordinates, d: Coordinates) -> bool:
    """Conservatively reject boundary touches as well as crossings in reviewed local geometry."""

    def cross(p: Coordinates, q: Coordinates, r: Coordinates) -> float:
        return (q.longitude - p.longitude) * (r.latitude - p.latitude) - (
            q.latitude - p.latitude
        ) * (r.longitude - p.longitude)

    def on_segment(p: Coordinates, q: Coordinates, r: Coordinates) -> bool:
        return (
            abs(cross(p, q, r)) <= 1e-12
            and min(p.latitude, q.latitude) - 1e-12
            <= r.latitude
            <= max(p.latitude, q.latitude) + 1e-12
            and min(p.longitude, q.longitude) - 1e-12
            <= r.longitude
            <= max(p.longitude, q.longitude) + 1e-12
        )

    ab_c, ab_d, cd_a, cd_b = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    return (ab_c * ab_d < 0 and cd_a * cd_b < 0) or any(
        (on_segment(a, b, c), on_segment(a, b, d), on_segment(c, d, a), on_segment(c, d, b))
    )


def normalize_garden(
    garden: ReviewedGarden,
    park: dict,
    path: dict,
    html: str,
    observed_at: datetime,
    official_transport: str = "direct_https",
    excluded: dict | None = None,
) -> PlaceCandidate:
    page = GardenPage()
    page.feed(html)
    visible = " ".join(" ".join(page.parts).split())
    if page.headings != [garden.title]:
        raise ValueError("Official garden identity or information section changed")
    if garden.source_format == "chandigarh_garden":
        if visible.count("GENERAL INFORMATION") != 1:
            raise ValueError("Official information section changed")
        information = visible.split("GENERAL INFORMATION", 1)[1].split("Download Tourism", 1)[0]
        expected = (
            garden.sector,
            garden.city,
            "Open : Daily",
            "Timings : 05:00 AM to 09:00 PM",
            "Entry Fee : Not Applicable",
        )
        if not all(claim in information for claim in expected) or any(
            information.count(field) != 1 for field in ("Open :", "Timings :", "Entry Fee")
        ):
            raise ValueError("Official fee, hours or address changed; no inference permitted")
    elif garden.source_format == "karnataka_attraction":
        fee = ("Entry Fee", "Free (select attractions have nominal charges)")
        hours = ("Cubbon Park (General)", "6:00 AM", "6:00 PM", "Mondays & 2nd Tuesdays")
        if (
            [r for r in page.rows if r and r[0] == fee[0]] != [fee]
            or [r for r in page.rows if r and r[0] == hours[0]] != [hours]
            or garden.sector not in visible
        ):
            raise ValueError("Official general-park fee, schedule or locality changed")
        expected = (*fee, *hours, garden.sector)
    else:
        raise ValueError("Unsupported reviewed source format")
    park_elements, path_elements = park["elements"], path["elements"]
    boundary = [e for e in park_elements if e["type"] == "way"]
    footway = [e for e in path_elements if e["type"] == "way"]
    if len(boundary) != 1 or len(footway) != 1:
        raise ValueError("Ambiguous OSM way identity")
    boundary, footway = boundary[0], footway[0]
    tags = boundary.get("tags", {})
    if (
        (boundary["id"], tags.get("name"), tags.get("leisure"))
        != (garden.park_way, garden.name, "park")
        or tags.get("access") in {"private", "no", "customers"}
        or tags.get("fee") == "yes"
    ):
        raise ValueError("OSM park conflicts with reviewed public admission")
    path_tags = footway.get("tags", {})
    if (
        footway["id"] != garden.path_way
        or path_tags.get("highway") != "footway"
        or path_tags.get("foot") in {"no", "private"}
        or path_tags.get("access") in {"private", "no", "customers"}
        or garden.access_node not in footway["nodes"]
    ):
        raise ValueError("Reviewed pedestrian path unavailable")
    park_nodes = {e["id"]: e for e in park_elements if e["type"] == "node"}
    path_nodes = {e["id"]: e for e in path_elements if e["type"] == "node"}
    point = path_nodes[garden.access_node]
    coordinates = Coordinates(latitude=point["lat"], longitude=point["lon"])
    ring = [
        Coordinates(latitude=park_nodes[n]["lat"], longitude=park_nodes[n]["lon"])
        for n in boundary["nodes"]
    ]
    path_points = [
        Coordinates(latitude=path_nodes[n]["lat"], longitude=path_nodes[n]["lon"])
        for n in footway["nodes"]
    ]
    if (
        len(ring) < 4
        or ring[0] != ring[-1]
        or not inside_boundary(coordinates, ring)
        or distance_meters(coordinates, garden.coordinates) > 10
        or point.get("tags", {}).get("access") in {"no", "private"}
        or point.get("tags", {}).get("foot") == "no"
        or len(path_points) < 2
        or not any(not inside_boundary(p, ring) for p in path_points)
    ):
        raise ValueError("Access point moved or is not inside this garden")
    if garden.excluded_way:
        if excluded is None:
            raise ValueError("Restricted-ground boundary missing")
        ways = [e for e in excluded["elements"] if e["type"] == "way"]
        nodes = {e["id"]: e for e in excluded["elements"] if e["type"] == "node"}
        if (
            len(ways) != 1
            or ways[0]["id"] != garden.excluded_way
            or (ways[0].get("tags", {}).get("amenity"), ways[0].get("tags", {}).get("name"))
            != ("courthouse", "High Court of Karnataka")
        ):
            raise ValueError("Restricted-ground boundary identity changed")
        exclusion = [
            Coordinates(latitude=nodes[n]["lat"], longitude=nodes[n]["lon"])
            for n in ways[0]["nodes"]
        ]
        if (
            len(exclusion) < 4
            or exclusion[0] != exclusion[-1]
            or any(inside_boundary(p, exclusion) for p in path_points)
            or any(
                segments_intersect(a, b, c, d)
                for a, b in pairwise(path_points)
                for c, d in pairwise(exclusion)
            )
        ):
            raise ValueError("Reviewed pedestrian path overlaps restricted grounds")
    subject = f"osm:way/{garden.park_way}"
    park_url = f"https://www.openstreetmap.org/api/0.6/way/{garden.park_way}/full.json"
    path_url = f"https://www.openstreetmap.org/api/0.6/way/{garden.path_way}/full.json"
    excluded_url = f"https://www.openstreetmap.org/api/0.6/way/{garden.excluded_way}/full.json"
    osm_refs = {park_url, path_url, excluded_url}

    def fact(field: str, value: object, reference: str = garden.url) -> Evidence:
        return Evidence.model_validate(
            dict(
                evidence_id=f"{subject}:{field}",
                subject_id=subject,
                field=field,
                value=value,
                source="OSM" if reference in osm_refs else "DIRECT",
                source_ref=reference,
                observed_at=observed_at,
                expires_at=observed_at + timedelta(hours=24),
                confidence="MEDIUM" if reference in osm_refs else "HIGH",
            )
        )

    price = mandatory_price(
        fact(
            "price",
            dict(
                currency_code="INR",
                lower_minor_units=0,
                upper_minor_units=0,
                scope="TOTAL",
                covers_all_mandatory_costs=True,
            ),
        ),
        confidence="VERIFIED",
    )
    return PlaceCandidate(
        place_id=subject,
        provider="OSM",
        provider_id=f"way/{garden.park_way}",
        name=garden.name,
        coordinates=coordinates,
        categories=("park",),
        price=price,
        opening_windows=None,
        dietary_options=None,
        evidence=(
            fact(
                "identity",
                dict(provider="OSM", provider_id=f"way/{garden.park_way}", name=garden.name),
                park_url,
            ),
            fact("coordinates", coordinates.model_dump(), path_url),
            fact("categories", ["park"], park_url),
            fact("public_access", True),
            fact("opening_hours", garden.opening_hours),
            fact("timezone", "Asia/Kolkata"),
            *(
                (
                    fact(
                        "excluded_ground_access",
                        {"boundary_way": garden.excluded_way, "path_outside_boundary": True},
                        excluded_url,
                    ),
                )
                if garden.excluded_way
                else ()
            ),
            fact(
                "visit_scope",
                "Main garden pedestrian paths only. No food, cafeteria, parking, "
                "purchases, attractions, rentals, courts, clubs or paid activities. "
                "Mapped access point, not a physically checked gate.",
            ),
            fact(
                "parse_lineage",
                dict(
                    parser=(
                        "karnataka-main-park-v1"
                        if garden.source_format == "karnataka_attraction"
                        else "chandigarh-garden-v1"
                    ),
                    authority=garden.authority,
                    page_sha256=hashlib.sha256(html.encode()).hexdigest(),
                    official_retrieval_transport=official_transport,
                    coordinate_kind="mapped_pedestrian_access_node",
                    access_node=garden.access_node,
                    path_way=garden.path_way,
                    park_way=garden.park_way,
                    path_crosses_park_boundary=True,
                    excluded_boundary_way=garden.excluded_way,
                    timezone_rule=f"Reviewed {garden.city} jurisdiction uses India civil time",
                    claims=list(expected),
                ),
            ),
        ),
    )


async def read_reviewed_source(
    client: httpx.AsyncClient, url: str, authorization: str | None = None
) -> bytes:
    headers = {"User-Agent": "GroundRule/0.1 (https://github.com/Shoryamishra61/Outproof)"}
    if authorization:
        headers["Authorization"] = authorization
    async with client.stream(
        "GET",
        url,
        timeout=15,
        follow_redirects=False,
        headers=headers,
    ) as response:
        response.raise_for_status()
        body = bytearray()
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > 1_000_000:
                raise ValueError("Reviewed source exceeds byte bound")
        return bytes(body)


async def fetch_garden(client: httpx.AsyncClient, garden: ReviewedGarden) -> PlaceCandidate:
    responses = []
    observed_at = datetime.now(UTC)
    official_transport = "direct_https"
    sources = [
        ("osm_park", f"https://www.openstreetmap.org/api/0.6/way/{garden.park_way}/full.json"),
        ("osm_path", f"https://www.openstreetmap.org/api/0.6/way/{garden.path_way}/full.json"),
    ]
    if garden.excluded_way:
        sources.append(
            (
                "osm_exclusion",
                f"https://www.openstreetmap.org/api/0.6/way/{garden.excluded_way}/full.json",
            )
        )
    sources.append(("official_garden", garden.url))
    for source_kind, url in sources:
        try:
            relay = os.getenv("OLLAMA_BASE_URL", "").rstrip("/")
            key = os.getenv("GEMMA_API_KEY", "")
            if source_kind == "official_garden" and relay.startswith("https://") and key:
                # Render cannot connect to this authority; reuse the protected model host.
                body = await read_reviewed_source(
                    client,
                    f"{relay}/sources/gardens/{garden.park_way}",
                    "Bearer " + key,
                )
                envelope = json.loads(body)
                fetched_at = datetime.fromisoformat(envelope["observed_at"])
                age = (datetime.now(UTC) - fetched_at).total_seconds()
                if envelope["source_url"] != garden.url or not -5 <= age <= 30:
                    raise ValueError("Reviewed relay identity or freshness invalid")
                html = envelope["html"]
                if not isinstance(html, str):
                    raise ValueError("Reviewed relay body invalid")
                responses.append(html.encode("utf-8"))
                observed_at = min(observed_at, fetched_at)
                official_transport = "authenticated_laptop_relay"
            else:
                responses.append(await read_reviewed_source(client, url))
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            status = (
                error.response.status_code if isinstance(error, httpx.HTTPStatusError) else None
            )
            logging.getLogger(__name__).warning(
                "reviewed source failure source_kind=%s kind=%s http_status=%s",
                source_kind,
                type(error).__name__,
                status,
            )
            raise
    return normalize_garden(
        garden,
        json.loads(responses[0]),
        json.loads(responses[1]),
        responses[-1].decode("utf-8"),
        observed_at,
        official_transport,
        json.loads(responses[2]) if garden.excluded_way else None,
    )
