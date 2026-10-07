"""Build real-data candidate templates; report rejection without inventing missing facts."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from ground_rule.models import CompilationFailure, ConstraintSet, PlaceCandidate, RouteFact
from ground_rule.plans import build_candidates
from ground_rule.policy import validate_plan


def evaluate(discovery: Path, routing: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Keep the prior evaluation; choose another output")
    observed = json.loads(discovery.read_text(encoding="utf-8"))
    routed = json.loads(routing.read_text(encoding="utf-8"))
    now = datetime.now(UTC)
    controls = ConstraintSet(
        currency_code="INR",
        budget_minor_units=50000,
        budget_scope="PER_PERSON",
        duration_max_minutes=90,
        party_mode="FRIEND",
        party_size=2,
        vibes=("Food", "Talk"),
        hard_constraints=(
            dict(kind="DIETARY", value="vegetarian"),
            dict(kind="EXCLUDE_CATEGORY", value="mall"),
        ),
        soft_constraints=(dict(preference="quiet"),),
        max_walking_minutes=None,
        max_walking_meters=None,
        return_by_local=None,
        locale="en-IN",
        origin=observed["origin"],
        departure_at=now,
    )
    places = tuple(PlaceCandidate.model_validate(p) for p in observed["result"])
    routes = tuple(RouteFact.model_validate(item["result"]) for item in routed["routes"])
    result = build_candidates(places, routes, controls, as_of=now)
    candidates = [] if isinstance(result, CompilationFailure) else list(result)
    validations = [validate_plan(p, controls, as_of=now) for p in candidates]
    report = dict(
        evaluation="REAL_PROVIDER_CANDIDATE_TEMPLATES_NOT_COMPILED_OUTINGS",
        controls=controls.model_dump(mode="json"),
        evaluated_at=now.isoformat(),
        discovery_report=str(discovery),
        routing_report=str(routing),
        candidates=[p.model_dump(mode="json") for p in candidates],
        validations=[v.model_dump(mode="json") for v in validations],
        failure=result.model_dump(mode="json") if isinstance(result, CompilationFailure) else None,
        template_gate_passed=bool(candidates),
        accepted_plans=sum(v.accepted for v in validations),
    )
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--routing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.discovery, args.routing, args.output)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in {"controls", "candidates", "validations"}}
        )
    )
    raise SystemExit(0 if report["template_gate_passed"] else 1)
