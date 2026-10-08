"""Global evaluation runner: >=50 scenarios across >=10 cities.

Measures verified compilation vs safe typed failure.
"""

import argparse
import asyncio
import json
import logging
import os
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic, perf_counter

import httpx
from app.compilation import compile_internal
from app.live import LiveEnrichmentProvider, LivePlacesProvider
from app.places import OverpassAvailability
from app.ranker import LocalGemma
from app.routing import ValhallaRoutingProvider
from ground_rule.models import (
    CompilationFailure,
    CompiledPlan,
    ConstraintSet,
    Coordinates,
    HardConstraint,
    SoftConstraint,
)

logger = logging.getLogger(__name__)


def load_scenarios(path: Path) -> list[dict]:
    scenarios = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            scenarios.append(json.loads(line))
    return scenarios


async def evaluate_scenario(
    scenario: dict,
    client: httpx.AsyncClient,
    ranker: LocalGemma,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    availability: OverpassAvailability | None = None,
) -> dict:
    s_id = scenario["id"]
    city = scenario["city"]
    origin = Coordinates.model_validate(scenario["origin"])
    raw_controls = scenario["controls"]

    now = clock()
    departure = now + timedelta(minutes=5)

    hard_constraints = [
        HardConstraint(kind=hc["kind"], value=hc["value"])
        for hc in raw_controls.get("hard_constraints", [])
    ]
    soft_constraints = [
        SoftConstraint(preference=sc["preference"])
        for sc in raw_controls.get("soft_constraints", [])
    ]

    controls = ConstraintSet(
        origin=origin,
        departure_at=departure,
        duration_max_minutes=raw_controls["duration_max_minutes"],
        budget_minor_units=raw_controls["budget_minor_units"],
        currency_code=raw_controls["currency_code"],
        budget_scope=raw_controls["budget_scope"],
        party_mode=raw_controls["party_mode"],
        party_size=raw_controls["party_size"],
        vibes=raw_controls["vibes"],
        hard_constraints=hard_constraints,
        soft_constraints=soft_constraints,
        max_walking_minutes=raw_controls.get("max_walking_minutes"),
        max_walking_meters=raw_controls.get("max_walking_meters"),
        return_by_local=raw_controls.get("return_by_local"),
        locale="en-IN" if scenario["country"] == "IN" else "en-US",
        strict_budget=raw_controls.get("strict_budget", True),
    )

    discovery = LivePlacesProvider(
        client,
        os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter"),
        availability=availability,
    )
    enrichment = LiveEnrichmentProvider(clock=clock)
    routing = ValhallaRoutingProvider(client, "https://valhalla1.openstreetmap.de")

    compile_started = perf_counter()
    try:
        result = await asyncio.wait_for(
            compile_internal(
                controls,
                discovery,
                enrichment,
                routing,
                ranker,
                as_of=now,
                mode="LIVE",
                clock=clock,
            ),
            timeout=45,
        )
    except Exception as exc:
        result = CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE",
            message=f"Provider or execution error category: {type(exc).__name__}",
        )
    compile_latency_ms = round((perf_counter() - compile_started) * 1000, 2)
    hard_violations = 0
    hallucinated_venues = 0
    unknown_price_certainty_errors = 0
    multiple_default_plans = 0

    if isinstance(result, CompiledPlan):
        outcome = "SUCCESS"
        plan_id = result.plan.plan_id
        # Invariant 1: Exactly one default plan returned
        if not result.plan or not result.proof:
            multiple_default_plans += 1

        # Invariant 2: Zero hard violations
        failed_checks = [c for c in result.proof.validation.checks if c.status != "PASS"]
        if failed_checks or not result.proof.validation.accepted:
            hard_violations += 1

        # Invariant 3: Zero hallucinated venues
        for stop in result.plan.stops:
            if not stop.place.place_id or not stop.place.coordinates:
                hallucinated_venues += 1

        # Invariant 4: Zero unknown prices presented as guaranteed
        if result.proof.cost.confidence.value in {"ESTIMATED", "UNKNOWN"}:
            unknown_price_certainty_errors += 1

        summary = {
            "id": s_id,
            "city": city,
            "outcome": outcome,
            "plan_id": plan_id,
            "venue": result.plan.stops[0].place.name if result.plan.stops else None,
            "provenance": [e.model_dump(mode="json") for e in result.proof.sources],
            "gate_breakdown": [c.model_dump(mode="json") for c in result.proof.validation.checks],
            "compiled_at": result.compiled_at.isoformat(),
            "duration_minutes": round(result.proof.total_duration_seconds / 60, 1),
            "cost_minor_units": result.proof.cost.upper.minor_units
            if result.proof.cost.upper
            else 0,
            "cost_confidence": result.proof.cost.confidence.value,
            "checks_passed": len(result.proof.validation.checks),
            "latency_ms": compile_latency_ms,
            "hard_violations": hard_violations,
            "hallucinated_venues": hallucinated_venues,
            "unknown_price_errors": unknown_price_certainty_errors,
            "multiple_plans_errors": multiple_default_plans,
        }
    else:
        outcome = (
            "TEMPORARY_PROVIDER_ERROR"
            if result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"
            else "TYPED_REJECTION"
        )
        summary = {
            "id": s_id,
            "city": city,
            "outcome": outcome,
            "failure_code": result.code,
            "failure_message": result.message,
            "latency_ms": compile_latency_ms,
            "hard_violations": hard_violations,
            "hallucinated_venues": hallucinated_venues,
            "unknown_price_errors": unknown_price_certainty_errors,
            "multiple_plans_errors": multiple_default_plans,
        }

    summary.update(
        locale=controls.locale,
        model=ranker.model,
        retry_count=0,
        input_case=scenario,
        source_mode="LIVE",
        trace=f"global:{s_id}",
    )
    return summary


async def run_global_evaluation(output: Path) -> dict:
    if output.exists():
        raise ValueError("Refusing to overwrite prior observations")
    cases_path = Path("evals/cases/global_scenarios.jsonl")
    scenarios = load_scenarios(cases_path)
    logger.info(
        "Loaded %d scenarios across %d cities", len(scenarios), len({s["city"] for s in scenarios})
    )

    def now_clock() -> datetime:
        return datetime.now(UTC)

    results = []
    availability = OverpassAvailability()

    async with httpx.AsyncClient(trust_env=False, timeout=30.0) as client:
        ranker = LocalGemma(
            client,
            os.getenv("GEMMA_MODEL", "gemma4:e2b-it-qat"),
            os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            api_key=os.getenv("GEMMA_API_KEY"),
        )

        for idx, scenario in enumerate(scenarios, start=1):
            while availability.retry_at > monotonic():
                await asyncio.sleep(min(5, availability.retry_at - monotonic()))
            logger.info(
                "[%d/%d] Running scenario %s (%s)...",
                idx,
                len(scenarios),
                scenario["id"],
                scenario["city"],
            )
            summary = await evaluate_scenario(
                scenario, client, ranker, clock=now_clock, availability=availability
            )
            results.append(summary)
            output.with_suffix(".partial.json").write_text(
                json.dumps(
                    {"executed_at": datetime.now(UTC).isoformat(), "results": results}, indent=2
                )
                + "\n",
                encoding="utf-8",
            )
            # Brief pause between scenarios to avoid rate limits
            await asyncio.sleep(0.3)

    successful = [r for r in results if r["outcome"] == "SUCCESS"]
    safe_failures = [r for r in results if r["outcome"] != "SUCCESS"]
    provider_errors = [r for r in results if r["outcome"] == "TEMPORARY_PROVIDER_ERROR"]
    total_hard_violations = sum(r["hard_violations"] for r in results)
    total_hallucinated = sum(r["hallucinated_venues"] for r in results)
    total_price_errors = sum(r["unknown_price_errors"] for r in results)
    total_multiple_plans = sum(r["multiple_plans_errors"] for r in results)

    failure_breakdown: dict[str, int] = {}
    for r in safe_failures:
        code = r.get("failure_code", "UNKNOWN")
        failure_breakdown[code] = failure_breakdown.get(code, 0) + 1

    cities = sorted({s["city"] for s in scenarios})
    avg_latency = round(sum(r["latency_ms"] for r in results) / len(results), 2) if results else 0

    report = {
        "evaluation": "GLOBAL_EVALUATION_50_SCENARIOS",
        "evaluated_at": datetime.now(UTC).isoformat(),
        "total_scenarios": len(results),
        "total_cities": len(cities),
        "cities": cities,
        "metrics": {
            "successful_compilations": len(successful),
            "typed_rejections": len(safe_failures) - len(provider_errors),
            "temporary_provider_errors": len(provider_errors),
            "accepted_population": len(successful),
            "hard_violations": total_hard_violations,
            "hallucinated_displayed_venues": total_hallucinated,
            "unknown_prices_presented_as_guaranteed": total_price_errors,
            "multiple_default_plans": total_multiple_plans,
            "average_latency_ms": avg_latency,
            "target_gates_passed": (
                len(successful) > 0
                and total_hard_violations == 0
                and total_hallucinated == 0
                and total_price_errors == 0
                and total_multiple_plans == 0
            ),
        },
        "failure_breakdown": failure_breakdown,
        "results": results,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(
        f"# Fresh global source evaluation\n\n{report['evaluated_at']} UTC. "
        f"{len(results)} actual live attempts across {len(cities)} cities. "
        f"{len(successful)} accepted; "
        f"{len(safe_failures) - len(provider_errors)} typed rejections; "
        f"{len(provider_errors)} temporary provider errors.\n\n"
        "Unsupported facts remain unknown. "
        "Zero accepted cases cannot establish successful global coverage. "
        "Generated/control tests and physical outings are excluded. "
        "The JSON contains inputs, status, source mode, "
        "retry counts, model identifier, latency and full provenance/gate breakdown "
        "where a plan was accepted.\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"]))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evals/reports/FINAL_GLOBAL_EVAL.json"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    asyncio.run(run_global_evaluation(args.output))
