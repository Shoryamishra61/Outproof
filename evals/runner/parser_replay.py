"""Replay preserved inference through current guards; no model or network calls."""

import argparse
import hashlib
import json
from pathlib import Path

from app.parser import ParserAdditions, parse_output, protected_requirements
from ground_rule.models import ConstraintSet

from evals.cases.parser import parser_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source, output = Path(args.input), Path(args.output)
    if output.exists():
        raise ValueError("Refusing to overwrite preserved replay")
    original = json.loads(source.read_text(encoding="utf-8"))
    cases = parser_cases()
    root = Path(__file__).resolve().parents[2]
    if (
        original["case_sha256"]
        != hashlib.sha256((root / "evals/cases/parser.py").read_bytes()).hexdigest()
    ):
        raise ValueError("Replay cases differ from measured inputs")
    originals = {row["id"]: row for row in original["results"]}
    rows = []
    for case in cases:
        controls = ConstraintSet.model_validate(case["controls"])
        result = parse_output(originals[case["id"]]["raw_output"], controls, case["text"])
        returned = isinstance(result, ConstraintSet)
        request_schema_valid = False
        try:
            additions = ParserAdditions.model_validate_json(originals[case["id"]]["raw_output"])
            request_schema_valid = all(
                getattr(controls, field) is None or getattr(additions, field) is None
                for field in (
                    "party_size",
                    "max_walking_minutes",
                    "max_walking_meters",
                    "return_by_local",
                )
            )
        except ValueError:
            pass
        preserved = returned and all(
            getattr(controls, field) == getattr(result, field)
            for field, value in controls.model_dump().items()
            if field not in {"hard_constraints", "soft_constraints"} and value is not None
        )
        expected = case["expected"]
        wanted = {("EXCLUDE_CATEGORY", value) for value in expected["exclusions"]}
        if expected["dietary"]:
            wanted.add(("DIETARY", expected["dietary"]))
        wanted.update(("UNSUPPORTED", value) for value in expected["unsupported"])
        actual = (
            {(item.kind, item.value) for item in result.hard_constraints} if returned else set()
        )
        missing = sorted(wanted - actual) if returned else []
        unsupported = protected_requirements(case["text"])
        source_retained = not unsupported or (
            any(case["text"] in item.value for item in result.hard_constraints)
            if returned
            else case["text"] in result.message
        )
        rows.append(
            {
                "id": case["id"],
                "returned": returned,
                "request_schema_valid": request_schema_valid,
                "controls_preserved": preserved,
                "corrupted": returned and not preserved,
                "missing_hard": missing,
                "unsupported_case": bool(unsupported),
                "unsupported_source_retained": source_retained,
                "output": result.model_dump(mode="json"),
            }
        )
    report = {
        "scope": "Offline replay of preserved raw outputs; zero new model/network calls",
        "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256(
            (root / "services/api/app/parser.py").read_bytes()
        ).hexdigest(),
        "cases": len(rows),
        "model": original["model"]["name"],
        "returned": sum(row["returned"] for row in rows),
        "request_schema_valid": sum(row["request_schema_valid"] for row in rows),
        "controls_preserved": sum(row["controls_preserved"] for row in rows),
        "corruptions": sum(row["corrupted"] for row in rows),
        "accepted_with_missing_hard": sum(bool(row["missing_hard"]) for row in rows),
        "unsupported_cases": sum(row["unsupported_case"] for row in rows),
        "unsupported_sources_retained": sum(
            row["unsupported_source_retained"] for row in rows if row["unsupported_case"]
        ),
        "results": rows,
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))


if __name__ == "__main__":
    main()
