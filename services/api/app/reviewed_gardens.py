"""Fresh official admission/hours joined to reviewed OSM pedestrian access points."""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
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
)


class GardenPage(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, bool]] = []
        self.parts: list[str] = []
        self.headings: list[str] = []
        self.heading_parts: list[str] = []

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

    def handle_endtag(self, tag: str) -> None:
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


def distance_meters(a: Coordinates, b: Coordinates) -> float:
    """Discovery proximity only; Valhalla still owns every walking metric."""
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


def normalize_garden(
    garden: ReviewedGarden, park: dict, path: dict, html: str, observed_at: datetime
) -> PlaceCandidate:
    page = GardenPage()
    page.feed(html)
    visible = " ".join(" ".join(page.parts).split())
    if page.headings != [garden.title] or visible.count("GENERAL INFORMATION") != 1:
        raise ValueError("Official garden identity or information section changed")
    information = visible.split("GENERAL INFORMATION", 1)[1].split("Download Tourism", 1)[0]
    expected = (
        garden.sector,
        "Chandigarh",
        "Open : Daily",
        "Timings : 05:00 AM to 09:00 PM",
        "Entry Fee : Not Applicable",
    )
    if not all(claim in information for claim in expected) or any(
        information.count(field) != 1 for field in ("Open :", "Timings :", "Entry Fee")
    ):
        raise ValueError("Official fee, hours or address changed; no inference permitted")
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
    subject = f"osm:way/{garden.park_way}"
    park_url = f"https://www.openstreetmap.org/api/0.6/way/{garden.park_way}/full.json"
    path_url = f"https://www.openstreetmap.org/api/0.6/way/{garden.path_way}/full.json"

    def fact(field: str, value: object, reference: str = garden.url) -> Evidence:
        return Evidence.model_validate(
            dict(
                evidence_id=f"{subject}:{field}",
                subject_id=subject,
                field=field,
                value=value,
                source="OSM" if reference in {park_url, path_url} else "DIRECT",
                source_ref=reference,
                observed_at=observed_at,
                expires_at=observed_at + timedelta(hours=24),
                confidence="MEDIUM" if reference in {park_url, path_url} else "HIGH",
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
            fact("opening_hours", "Mo-Su 05:00-21:00"),
            fact("timezone", "Asia/Kolkata"),
            fact(
                "visit_scope",
                "Main garden pedestrian paths only. No food, cafeteria, parking, "
                "purchases or paid activities. Mapped access point, not a physically checked gate.",
            ),
            fact(
                "parse_lineage",
                dict(
                    parser="chandigarh-garden-v1",
                    authority="Chandigarh Tourism Department",
                    page_sha256=hashlib.sha256(html.encode()).hexdigest(),
                    coordinate_kind="mapped_pedestrian_access_node",
                    access_node=garden.access_node,
                    path_way=garden.path_way,
                    park_way=garden.park_way,
                    path_crosses_park_boundary=True,
                    timezone_rule="Reviewed Chandigarh jurisdiction uses India civil time",
                    claims=list(expected),
                ),
            ),
        ),
    )


async def fetch_garden(client: httpx.AsyncClient, garden: ReviewedGarden) -> PlaceCandidate:
    responses = []
    for source_kind, url in zip(
        ("osm_park", "osm_path", "official_garden"),
        (
            f"https://www.openstreetmap.org/api/0.6/way/{garden.park_way}/full.json",
            f"https://www.openstreetmap.org/api/0.6/way/{garden.path_way}/full.json",
            garden.url,
        ),
        strict=True,
    ):
        try:
            async with client.stream(
                "GET",
                url,
                timeout=15,
                follow_redirects=False,
                headers={
                    "User-Agent": "GroundRule/0.1 (https://github.com/Shoryamishra61/Outproof)"
                },
            ) as response:
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 1_000_000:
                        raise ValueError("Reviewed source exceeds byte bound")
                responses.append(bytes(body))
        except (httpx.HTTPError, ValueError) as error:
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
        responses[2].decode("utf-8"),
        datetime.now(UTC),
    )
