"""Bounded cached factual rejection demo with actual local Gemma; not an offline outing."""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx
from app.enrichment import SerpApiEnrichmentProvider
from app.parser import parse_constraints
from ground_rule.models import CompilationFailure, ConstraintSet, PlaceCandidate, RouteFact
from ground_rule.plans import build_candidates
from ground_rule.policy import validate_plan


def evaluate(source: Path, routing: Path, template_report: Path, model: str, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Preserve earlier demo evidence; use another output path")
    discovery = json.loads(source.read_text(encoding="utf-8"))
    routed = json.loads(routing.read_text(encoding="utf-8"))
    controls = ConstraintSet.model_validate(
        json.loads(template_report.read_text(encoding="utf-8"))["controls"]
    )
    controls = ConstraintSet.model_validate(
        controls.model_copy(update={"departure_at": datetime.now(UTC)})
    )
    text = "vegetarian, no mall, somewhere quiet enough to talk"
    started = perf_counter()
    parsed = parse_constraints(controls, text, model=model)
    parser_ms = round((perf_counter() - started) * 1000, 2)
    places = tuple(PlaceCandidate.model_validate(p) for p in discovery["result"])
    routes = tuple(RouteFact.model_validate(r["result"]) for r in routed["routes"])
    validations = []
    candidate_failure = None
    now = datetime.now(UTC)
    if not isinstance(parsed, CompilationFailure):
        plans = build_candidates(places, routes, parsed, as_of=now)
        if isinstance(plans, CompilationFailure):
            candidate_failure = plans.model_dump(mode="json")
        else:
            validations = [validate_plan(p, parsed, as_of=now) for p in plans]

    # Prove the actual optional adapter's missing-credential path without external I/O.
    async def credential_check() -> dict:
        def forbid_external(request: httpx.Request) -> httpx.Response:
            raise AssertionError("Cached demo must not call external providers")

        async with httpx.AsyncClient(transport=httpx.MockTransport(forbid_external)) as client:
            failure = await SerpApiEnrichmentProvider(client, None).enrich(places[0])
            return failure.model_dump(mode="json")

    enrichment_failure = asyncio.run(credential_check())
    authoritative_fields = set(ConstraintSet.model_fields) - {
        "hard_constraints",
        "soft_constraints",
    }
    preserved = not isinstance(parsed, CompilationFailure) and all(
        getattr(controls, field) == getattr(parsed, field) for field in authoritative_fields
    )
    report = dict(
        evaluation="CACHED_COMPONENT_REJECTION_DEMO_NOT_AN_OFFLINE_OUTING",
        model=model,
        sentence=text,
        controls=controls.model_dump(mode="json"),
        evaluated_at=now.isoformat(),
        source_reports=[str(source), str(routing), str(template_report)],
        parser_latency_ms=parser_ms,
        parser_result=parsed.model_dump(mode="json"),
        authoritative_controls_preserved=preserved,
        validations=[v.model_dump(mode="json") for v in validations],
        candidate_failure=candidate_failure,
        enrichment_failure=enrichment_failure,
        accepted_outings=sum(v.accepted for v in validations),
        external_discovery_or_routing_requests=0,
        source_timestamps_refreshed=False,
    )
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--routing", type=Path, required=True)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.discovery, args.routing, args.templates, args.model, args.output)
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k
                in {
                    "evaluation",
                    "model",
                    "parser_latency_ms",
                    "authoritative_controls_preserved",
                    "accepted_outings",
                    "external_discovery_or_routing_requests",
                }
            }
        )
    )
    raise SystemExit(0 if report["authoritative_controls_preserved"] else 1)
