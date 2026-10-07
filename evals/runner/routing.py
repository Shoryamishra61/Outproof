"""Live walking legs for public Chennai development points, not a feasible outing."""

import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

import httpx
from app.routing import ValhallaRoutingProvider
from ground_rule.models import CompilationFailure, Coordinates, PlaceCandidate


async def evaluate(discovery: Path, endpoint: str, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Preserve the earlier route observation; choose a new path")
    observations = json.loads(discovery.read_text(encoding="utf-8"))
    places = {
        place.place_id: place
        for place in (PlaceCandidate.model_validate(p) for p in observations["result"])
    }
    origin = Coordinates.model_validate(observations["origin"])
    eatery, park = "osm:node/12473051001", "osm:node/2270331348"
    locations = {
        "origin": origin,
        eatery: places[eatery].coordinates,
        park: places[park].coordinates,
    }
    routes = []
    started = perf_counter()
    async with httpx.AsyncClient(trust_env=False) as client:
        provider = ValhallaRoutingProvider(client, endpoint)
        for start, end in [
            ("origin", eatery),
            (eatery, "origin"),
            ("origin", park),
            (park, "origin"),
            (eatery, park),
        ]:
            step = perf_counter()
            result = await provider.route(start, end, locations[start], locations[end])
            routes.append(
                dict(
                    latency_ms=round((perf_counter() - step) * 1000, 2),
                    result=result.model_dump(mode="json"),
                )
            )
            if isinstance(result, CompilationFailure):
                break
    report = dict(
        evaluation="LIVE_ROUTING_NOT_AN_OUTING",
        discovery_report=str(discovery),
        endpoint=endpoint,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        routes=routes,
        passed=len(routes) == 5 and all(r["result"].get("reachable") is True for r in routes),
    )
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--endpoint", default="https://valhalla1.openstreetmap.de")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = asyncio.run(evaluate(args.discovery, args.endpoint, args.output))
    print(json.dumps({key: value for key, value in report.items() if key != "routes"}))
    raise SystemExit(0 if report["passed"] else 1)
