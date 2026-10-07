"""Opt-in live, bounded development discovery; never an outing evaluation."""

import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

import httpx
from app.places import OverpassPlacesProvider
from ground_rule.models import CompilationFailure, Coordinates


async def evaluate(endpoint: str, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Preserve the earlier live observation; choose a new report path")
    # Public development area, not a user's recorded location. No canonical SRM origin exists.
    origin = Coordinates(latitude=13.0418, longitude=80.2341)
    started = perf_counter()
    async with httpx.AsyncClient(trust_env=False) as client:
        result = await OverpassPlacesProvider(client, endpoint).discover(origin, 1000)
    report = dict(
        evaluation="LIVE_PROVIDER_DISCOVERY_NOT_AN_OUTING",
        area="T Nagar, Chennai, India",
        origin=origin.model_dump(),
        radius_meters=1000,
        endpoint=endpoint,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        attribution="© OpenStreetMap contributors; ODbL 1.0",
        attribution_url="https://www.openstreetmap.org/copyright",
        result=result.model_dump(mode="json")
        if isinstance(result, CompilationFailure)
        else [place.model_dump(mode="json") for place in result],
        passed=not isinstance(result, CompilationFailure),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="https://overpass-api.de/api/interpreter")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = asyncio.run(evaluate(args.endpoint, args.output))
    print(json.dumps({key: value for key, value in report.items() if key != "result"}))
    raise SystemExit(0 if report["passed"] else 1)
